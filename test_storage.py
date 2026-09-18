from dotenv import load_dotenv

load_dotenv()

from backend.services.storage import storage

url = storage.upload_file(
    "test.png",
    "test/test.png"
)

print("UPLOAD SUCCESS")
print(url)