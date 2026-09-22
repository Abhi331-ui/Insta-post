import os
from pathlib import Path

from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client


# Ensure the project .env is loaded before reading Supabase configuration.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


import logging

logger = logging.getLogger("PromptPulse.Storage")


class SupabaseStorage:
    def __init__(self):
        self.storage_type = os.getenv("STORAGE_TYPE", "supabase").lower()
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "slides")
        self.client: Optional[Client] = None

        if self.storage_type == "supabase" and url and key:
            try:
                self.client = create_client(url, key)
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}. Falling back to local storage.")
                self.client = None
        else:
            logger.info("Operating in local media storage mode.")

    def upload_file(self, file_path: str, destination: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        from backend.config import settings
        local_url = f"{settings.PUBLIC_MEDIA_BASE_URL}/slides/{path.name}"

        if not self.client:
            return local_url

        try:
            with path.open("rb") as file:
                self.client.storage.from_(self.bucket).upload(
                    destination,
                    file,
                    {
                        "content-type": "image/png",
                        "upsert": "true",
                    },
                )
            return self.client.storage.from_(self.bucket).get_public_url(destination)
        except Exception as e:
            logger.warning(f"Supabase upload failed for {destination}: {e}. Falling back to local URL.")
            return local_url


storage = SupabaseStorage()