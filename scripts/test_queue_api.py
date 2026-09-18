import urllib.request, json

req = urllib.request.Request("http://localhost:8000/api/queue")
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())

print(f"Total items in queue: {len(data['items'])}")
for it in data['items'][:15]:
    print(f"ID={it['id']} | Day={it['day_index']} | Topic='{it['topic']}' | PostID={it['post_id']} | Img={it.get('preview_image_url')}")
