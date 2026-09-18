import sys
from pathlib import Path
import sqlite3

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.image_generator import image_generator

def update_slide_2():
    conn = sqlite3.connect("promptpulse.db", timeout=60)
    c = conn.cursor()

    items = [
        {
            "post_id": 25,
            "slide_content": {
                "layout_type": "tool_card",
                "eyebrow": "M E E T",
                "tool_name_prefix": "STACKBLITZ",
                "tool_name": "BOLT.NEW",
                "tool_badge": "BOLT.NEW",
                "headline": "Meet Bolt.new",
                "body_text": "Complete in-browser Node.js runtime powered by WebContainers.",
                "annotation": "Zero configuration required.",
                "features": [
                    {"icon": "⚡", "label": "Instant Live Server"},
                    {"icon": "📦", "label": "Full NPM Ecosystem"},
                    {"icon": "🔄", "label": "Self-Healing Errors"},
                    {"icon": "🚀", "label": "1-Click Netlify Deploy"},
                ],
            }
        },
        {
            "post_id": 26,
            "slide_content": {
                "layout_type": "tool_card",
                "eyebrow": "M E E T",
                "tool_name_prefix": "OPENAI",
                "tool_name": "CANVAS",
                "tool_badge": "CANVAS",
                "headline": "Meet Canvas",
                "body_text": "Direct inline editing and targeted line-by-line AI refactoring.",
                "annotation": "No more copy-pasting.",
                "features": [
                    {"icon": "✍️", "label": "Inline Targeted Edits"},
                    {"icon": "🔍", "label": "Code Review Shortcuts"},
                    {"icon": "🌐", "label": "Multi-Language Porting"},
                    {"icon": "📐", "label": "Reading Level Slider"},
                ],
            }
        }
    ]

    for item in items:
        pid = item["post_id"]
        sc = item["slide_content"]
        img_path = image_generator.generate_slide_image(
            post_id=pid,
            slide_number=2,
            layout_type="tool_card",
            content=sc,
            brand={"primary_color": "#7C3AED", "background_color": "#000000"}
        )
        c.execute("UPDATE post_slides SET image_path = ?, headline = ?, body_text = ? WHERE post_id = ? AND slide_number = 2",
                  (img_path, sc["headline"], sc["body_text"], pid))
        print(f"Updated Post {pid} Slide 2 -> {Path(img_path).name}")

    conn.commit()
    conn.close()
    print("Done updating slide 2 for post 25 and 26.")

if __name__ == "__main__":
    update_slide_2()
