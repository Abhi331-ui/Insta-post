import logging
from typing import List, Dict, Any, Optional
from backend.services.image_generator import image_generator

logger = logging.getLogger("PromptPulse.DesignAgent")


class DesignAgent:
    def __init__(self):
        self.generator = image_generator

    async def generate_slides(
        self,
        slides_content: List[Dict[str, Any]],
        post_id: int = 1,
        brand_settings: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Renders all 6 carousel slides into 1080x1350 PNGs following PromptPulse updated design system:
        - Pure black background: #000000
        - Primary gradient: linear-gradient(135deg, #7C3AED, #2563EB, #EC4899)
        - Headline color: White #FFFFFF (base) + gradient accent on key words
        - Body text: #D1D5DB (light gray)
        - Glassmorphism cards: rgba(255,255,255,0.05) with border rgba(255,255,255,0.1)
        - Accent glow: #7C3AED with blur shadow
        - Neon accent lines: #06B6D4 (cyan)
        - Typography: Inter (900 headlines, 600 subheadings, 400 body)
        - Slide counter top-right ("01 / 06"), 6-dot pagination bottom-center, white arrow bottom-right.
        - Cinematic atmospheric AI background image on every slide (20-35% opacity).

        Returns list of image file paths.
        """
        slide_image_paths = []

        for idx, slide in enumerate(slides_content):
            slide_num = slide.get("slide_number", idx + 1)
            layout_type = slide.get("layout_type", "hero")

            try:
                img_path = self.generator.generate_slide_image(
                    post_id=post_id,
                    slide_number=slide_num,
                    layout_type=layout_type,
                    content=slide,
                    brand=brand_settings,
                )
                slide_image_paths.append(img_path)
            except Exception as e:
                logger.error(f"Error rendering slide {slide_num}: {e}")
                raise e

        return slide_image_paths

    async def regenerate_single_slide(
        self,
        slide_content: Dict[str, Any],
        post_id: int,
        slide_number: int,
        brand_settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Regenerate a single slide PNG without re-rendering the whole carousel."""
        layout_type = slide_content.get("layout_type", "hero")
        return self.generator.generate_slide_image(
            post_id=post_id,
            slide_number=slide_number,
            layout_type=layout_type,
            content=slide_content,
            brand=brand_settings,
        )


design_agent = DesignAgent()
