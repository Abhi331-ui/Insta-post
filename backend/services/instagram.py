import asyncio
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from backend.config import settings


class InstagramService:
    def __init__(
        self,
        access_token: Optional[str] = None,
        instagram_user_id: Optional[str] = None,
    ):
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.instagram_user_id = instagram_user_id or settings.INSTAGRAM_USER_ID
        self.graph_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.graph_version}"

    def is_configured(self) -> bool:
        return bool(self.access_token and self.instagram_user_id)

    def get_auth_url(self) -> str:
        """Generate Meta OAuth authorization URL."""
        client_id = settings.META_APP_ID
        redirect_uri = settings.INSTAGRAM_REDIRECT_URI
        scopes = "instagram_basic,instagram_content_publish,instagram_manage_insights,pages_show_list,pages_read_engagement"
        return (
            f"https://www.facebook.com/{self.graph_version}/dialog/oauth?"
            f"client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&response_type=code"
        )

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange temporary code for short-lived token, then upgrade to 60-day long-lived token."""
        # 1. Short lived token
        token_url = f"https://graph.facebook.com/{self.graph_version}/oauth/access_token"
        params = {
            "client_id": settings.META_APP_ID,
            "client_secret": settings.META_APP_SECRET,
            "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
            "code": code,
        }
        res = requests.get(token_url, params=params)
        data = res.json()
        if "access_token" not in data:
            raise Exception(f"Failed to retrieve access token: {data}")

        short_token = data["access_token"]

        # 2. Upgrade to long-lived 60-day token
        long_token_params = {
            "grant_type": "fb_exchange_token",
            "client_id": settings.META_APP_ID,
            "client_secret": settings.META_APP_SECRET,
            "fb_exchange_token": short_token,
        }
        long_res = requests.get(token_url, params=long_token_params)
        long_data = long_res.json()
        long_token = long_data.get("access_token", short_token)
        expires_in = long_data.get("expires_in", 5184000)  # default 60 days in seconds

        return {
            "access_token": long_token,
            "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
        }

    def refresh_long_lived_token(self, current_token: str) -> Dict[str, Any]:
        """Refresh long-lived access token before 60-day expiration."""
        url = f"https://graph.facebook.com/{self.graph_version}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": settings.META_APP_ID,
            "client_secret": settings.META_APP_SECRET,
            "fb_exchange_token": current_token,
        }
        res = requests.get(url, params=params)
        data = res.json()
        return data

    async def publish_carousel(
        self,
        image_urls: List[str],
        caption: str,
        max_retries: int = 3,
        backoff_delays: List[int] = None,
    ) -> Dict[str, Any]:
        """
        Executes Meta Graph API Official Carousel flow:
        Step 1: Upload each image as media container
        Step 2: Create carousel container
        Step 3: Publish carousel
        Includes exponential backoff retry logic.
        """
        backoff_delays = backoff_delays or [30, 60, 120]

        if not self.is_configured():
            # If running in simulation / dev without live Meta credentials
            return {
                "success": True,
                "simulated": True,
                "instagram_post_id": f"ig_sim_{int(time.time())}",
                "permalink": f"https://instagram.com/p/sim_{int(time.time())}",
                "message": "Simulated publication successful (Meta credentials not configured in .env).",
                "attempt_count": 1,
            }

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                # Step 1: Upload each image as carousel child container
                child_container_ids = []
                for img_url in image_urls:
                    item_res = requests.post(
                        f"{self.base_url}/{self.instagram_user_id}/media",
                        data={
                            "image_url": img_url,
                            "is_carousel_item": "true",
                            "access_token": self.access_token,
                        },
                        timeout=30,
                    )
                    item_data = item_res.json()
                    if "id" not in item_data:
                        raise Exception(f"Failed to create child media container: {item_data}")
                    child_container_ids.append(item_data["id"])

                # Wait 5 seconds for containers to be processed by Meta
                await asyncio.sleep(5)

                # Step 2: Create carousel container
                carousel_res = requests.post(
                    f"{self.base_url}/{self.instagram_user_id}/media",
                    data={
                        "media_type": "CAROUSEL",
                        "children": ",".join(child_container_ids),
                        "caption": caption,
                        "access_token": self.access_token,
                    },
                    timeout=30,
                )
                carousel_data = carousel_res.json()
                if "id" not in carousel_data:
                    raise Exception(f"Failed to create carousel container: {carousel_data}")

                carousel_container_id = carousel_data["id"]

                # Wait 5 seconds for carousel container status
                await asyncio.sleep(5)

                # Step 3: Publish carousel
                publish_res = requests.post(
                    f"{self.base_url}/{self.instagram_user_id}/media_publish",
                    data={
                        "creation_id": carousel_container_id,
                        "access_token": self.access_token,
                    },
                    timeout=30,
                )
                publish_data = publish_res.json()
                if "id" not in publish_data:
                    raise Exception(f"Failed to publish carousel: {publish_data}")

                return {
                    "success": True,
                    "simulated": False,
                    "instagram_post_id": publish_data["id"],
                    "attempt_count": attempt,
                    "response": publish_data,
                }

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    delay = backoff_delays[attempt - 1] if attempt - 1 < len(backoff_delays) else 60
                    await asyncio.sleep(delay)
                else:
                    break

        return {
            "success": False,
            "simulated": False,
            "error": last_error,
            "attempt_count": max_retries,
        }

    def get_post_insights(self, instagram_post_id: str) -> Dict[str, Any]:
        """Fetch reach, impressions, saves, shares, likes, comments for a published post."""
        if not self.is_configured() or instagram_post_id.startswith("ig_sim_"):
            # Return realistic simulated analytics
            import random
            reach = random.randint(3500, 12000)
            impressions = int(reach * random.uniform(1.2, 1.6))
            likes = random.randint(240, 890)
            comments = random.randint(18, 75)
            shares = random.randint(60, 280)
            saves = random.randint(140, 620)
            profile_visits = random.randint(45, 190)
            follows = random.randint(12, 55)
            engagement_rate = round(((likes + comments + shares + saves) / max(reach, 1)) * 100, 2)
            return {
                "reach": reach,
                "impressions": impressions,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": saves,
                "profile_visits": profile_visits,
                "follows": follows,
                "engagement_rate": engagement_rate,
            }

        url = f"{self.base_url}/{instagram_post_id}/insights"
        params = {
            "metric": "reach,impressions,saved,shares,likes,comments,total_interactions",
            "access_token": self.access_token,
        }
        res = requests.get(url, params=params)
        data = res.json()
        metrics = {}
        for item in data.get("data", []):
            metrics[item["name"]] = item.get("values", [{}])[0].get("value", 0)

        reach = metrics.get("reach", 0)
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0)
        saves = metrics.get("saved", 0)
        engagement_rate = round(((likes + comments + shares + saves) / max(reach, 1)) * 100, 2) if reach else 0.0

        return {
            "reach": reach,
            "impressions": metrics.get("impressions", 0),
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "profile_visits": metrics.get("profile_activity", 0),
            "follows": metrics.get("follows", 0),
            "engagement_rate": engagement_rate,
        }


instagram_service = InstagramService()
