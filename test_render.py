import json
from pathlib import Path
from backend.services.image_generator import image_generator
from backend.services.ai_provider import ai_provider

# Test rendering all 6 slides
content = json.loads(ai_provider._fallback_completion("write_carousel", "Topic: Google Veo 3\nHook: THIS AI TURNS YOUR IDEAS INTO STUNNING VIDEOS"))
print("Slides content count:", len(content))

for idx, slide in enumerate(content):
    layout_type = slide.get("layout_type", "hero")
    slide_num = slide.get("slide_number", idx + 1)
    print(f"Rendering slide {slide_num} ({layout_type})...")
    path = image_generator.generate_slide_image(
        post_id=100,
        slide_number=slide_num,
        layout_type=layout_type,
        content=slide
    )
    print(f"Slide {slide_num} rendered to: {path} (exists: {Path(path).exists()})")
