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
        if not self.access_token or not self.instagram_user_id:
            return False
        if self.access_token.startswith(("TEST_", "MOCK_", "test_", "mock_")):
            return False
        return True

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

        # 3. Automatically discover linked Instagram Business Account ID and Profile
        instagram_user_id = None
        page_name = "Instagram Business Account"
        username = None
        profile_picture_url = None

        try:
            accounts_res = requests.get(
                f"{self.base_url}/me/accounts",
                params={
                    "fields": "id,name,instagram_business_account{id,name,username,profile_picture_url}",
                    "access_token": long_token,
                },
                timeout=15,
            )
            accounts_data = accounts_res.json()
            for page in accounts_data.get("data", []):
                ig_biz = page.get("instagram_business_account")
                if ig_biz and "id" in ig_biz:
                    instagram_user_id = ig_biz["id"]
                    page_name = ig_biz.get("name") or page.get("name")
                    username = ig_biz.get("username")
                    profile_picture_url = ig_biz.get("profile_picture_url")
                    break
        except Exception:
            pass

        # Fallback query directly to /me if accounts didn't return business account
        if not instagram_user_id:
            try:
                me_res = requests.get(
                    f"{self.base_url}/me",
                    params={"fields": "id,name,username", "access_token": long_token},
                    timeout=10,
                )
                me_data = me_res.json()
                if "id" in me_data:
                    instagram_user_id = me_data["id"]
                    username = me_data.get("username")
                    page_name = me_data.get("name") or page_name
            except Exception:
                pass

        return {
            "access_token": long_token,
            "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
            "instagram_user_id": instagram_user_id,
            "page_name": page_name,
            "username": username,
            "profile_picture_url": profile_picture_url,
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

    def get_account_profile(
        self,
        access_token: Optional[str] = None,
        instagram_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch Instagram account profile info (username, name, profile_picture_url)."""
        token = access_token or self.access_token
        user_id = instagram_user_id or self.instagram_user_id

        if not token or not user_id or user_id.startswith("test_"):
            return {
                "username": "promptpulse.ai",
                "name": "PromptPulse AI",
                "profile_picture_url": None,
            }

        try:
            url = f"{self.base_url}/{user_id}"
            params = {
                "fields": "username,name,profile_picture_url",
                "access_token": token,
            }
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if "username" in data:
                return {
                    "username": data.get("username"),
                    "name": data.get("name") or data.get("username"),
                    "profile_picture_url": data.get("profile_picture_url"),
                }
        except Exception:
            pass

        return {
            "username": None,
            "name": None,
            "profile_picture_url": None,
        }

    def get_post_comments(
        self,
        instagram_post_id: str,
        access_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch comments for a published Instagram post."""
        token = access_token or self.access_token

        if not token or instagram_post_id.startswith("ig_sim_"):
            # Simulated comments for dev/test mode
            import random
            sim_users = [
                {"username": "tech_founder", "text": "TOOLKIT please! Great breakdown."},
                {"username": "alex_creator", "text": "Can you send the guide? Looking to implement this."},
                {"username": "sarah_ai", "text": "TOOLKIT - awesome slides as always!"},
                {"username": "growth_marketer", "text": "Really insightful comparison on slide 5."},
            ]
            sample = random.sample(sim_users, k=min(len(sim_users), 2))
            return [
                {
                    "id": f"sim_cmt_{int(time.time())}_{idx}",
                    "text": item["text"],
                    "from": {"id": f"sim_user_{idx}", "username": item["username"]},
                    "timestamp": datetime.utcnow().isoformat(),
                }
                for idx, item in enumerate(sample)
            ]

        try:
            url = f"{self.base_url}/{instagram_post_id}/comments"
            params = {
                "fields": "id,text,from{id,username},timestamp",
                "access_token": token,
                "limit": 50,
            }
            res = requests.get(url, params=params, timeout=12)
            data = res.json()
            return data.get("data", [])
        except Exception:
            return []

    def reply_to_comment(
        self,
        comment_id: str,
        message: str,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post a public reply to a comment."""
        token = access_token or self.access_token

        if not token or token.startswith(("TEST_", "MOCK_", "test_", "mock_")) or comment_id.startswith(("sim_", "test_")):
            return {
                "success": True,
                "simulated": True,
                "id": f"sim_reply_{int(time.time())}",
                "message": "Simulated reply sent.",
            }

        try:
            url = f"{self.base_url}/{comment_id}/replies"
            res = requests.post(url, data={"message": message, "access_token": token}, timeout=15)
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def send_private_reply(
        self,
        comment_id: str,
        message: str,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an automated private DM response to a commenter using Meta's Private Replies API."""
        token = access_token or self.access_token

        if not token or token.startswith(("TEST_", "MOCK_", "test_", "mock_")) or comment_id.startswith(("sim_", "test_")):
            return {
                "success": True,
                "simulated": True,
                "message": "Simulated private reply DM sent.",
            }

        try:
            url = f"{self.base_url}/me/messages"
            payload = {
                "recipient": {"comment_id": comment_id},
                "message": {"text": message},
            }
            res = requests.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                timeout=15,
            )
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def get_direct_messages(
        self,
        access_token: Optional[str] = None,
        instagram_user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch incoming direct messages and conversation threads."""
        token = access_token or self.access_token
        user_id = instagram_user_id or self.instagram_user_id

        if not token or not user_id or user_id.startswith("test_"):
            return [
                {
                    "id": f"sim_conv_1",
                    "sender_username": "sarah_ai",
                    "sender_id": "sim_user_1",
                    "message": "Hey! Could you share the prompt cheat sheet from today's post?",
                    "created_time": datetime.utcnow().isoformat(),
                },
                {
                    "id": f"sim_conv_2",
                    "sender_username": "tech_founder",
                    "sender_id": "sim_user_2",
                    "message": "Love your content! How often do you post?",
                    "created_time": datetime.utcnow().isoformat(),
                },
            ]

        try:
            url = f"{self.base_url}/{user_id}/conversations"
            params = {
                "fields": "messages{id,message,from{id,username},created_time}",
                "access_token": token,
                "limit": 20,
            }
            res = requests.get(url, params=params, timeout=12)
            data = res.json()
            conversations = []
            for item in data.get("data", []):
                for msg in item.get("messages", {}).get("data", []):
                    conversations.append({
                        "id": msg.get("id"),
                        "sender_username": msg.get("from", {}).get("username", "user"),
                        "sender_id": msg.get("from", {}).get("id"),
                        "message": msg.get("message"),
                        "created_time": msg.get("created_time"),
                    })
            return conversations
        except Exception:
            return []

    def send_direct_message(
        self,
        recipient_id: str,
        message: str,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a direct message to a user."""
        token = access_token or self.access_token

        if not token or token.startswith(("TEST_", "MOCK_", "test_", "mock_")) or recipient_id.startswith(("sim_", "test_")):
            return {
                "success": True,
                "simulated": True,
                "message": "Simulated DM sent.",
            }

        try:
            url = f"{self.base_url}/me/messages"
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
            }
            res = requests.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                timeout=15,
            )
            return res.json()
        except Exception as e:
            return {"error": str(e)}


instagram_service = InstagramService()

