import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client


# Ensure the project .env is loaded before reading Supabase configuration.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class SupabaseStorage:
    def __init__(self):
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "slides")

        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured"
            )

        self.client: Client = create_client(url, key)

    def upload_file(self, file_path: str, destination: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

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


storage = SupabaseStorage()