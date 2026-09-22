import os
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image

from backend.config import settings


class QAAgent:
    def __init__(self):
        self.expected_width = settings.SLIDE_WIDTH    # 1080
        self.expected_height = settings.SLIDE_HEIGHT  # 1350
        self.expected_count = settings.TOTAL_SLIDES   # 6

    async def quality_check(
        self,
        post_data: Dict[str, Any],
        slide_images: List[str],
        slides_content: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Runs comprehensive QA checks:
        CRITICAL (fail if violated):
        - Exactly 6 slides exist
        - All 6 images are 1080x1350px
        - No slide is a duplicate of another
        - Hook exists on slide 1
        - CTA exists on slide 6

        IMPORTANT (warnings & auto-fixes):
        - Caption exists
        - Hashtags exist
        - Alt text exists
        """
        critical_failures: List[str] = []
        warnings: List[str] = []
        auto_fix_applied: List[str] = []
        failed_slide_indices: List[int] = []

        # 1. Slide Count Check
        if len(slide_images) != self.expected_count or len(slides_content) != self.expected_count:
            critical_failures.append(
                f"Carousel must have exactly {self.expected_count} slides. Found {len(slide_images)} images and {len(slides_content)} content items."
            )

        # 2. Image Dimension and Integrity Checks
        for idx, img_path in enumerate(slide_images):
            p = Path(img_path)
            if not p.exists():
                critical_failures.append(f"Slide image {idx + 1} file not found: {img_path}")
                failed_slide_indices.append(idx + 1)
                continue

            try:
                with Image.open(p) as img:
                    w, h = img.size
                    if w != self.expected_width or h != self.expected_height:
                        critical_failures.append(
                            f"Slide {idx + 1} resolution mismatch: expected {self.expected_width}x{self.expected_height}, got {w}x{h}"
                        )
                        failed_slide_indices.append(idx + 1)
            except Exception as e:
                critical_failures.append(f"Failed to verify slide {idx + 1} image data: {e}")
                failed_slide_indices.append(idx + 1)

        # 3. Duplicate Slide Detection
        headlines = [s.get("headline", "").strip().lower() for s in slides_content if isinstance(s, dict)]
        if len(headlines) != len(set(headlines)):
            critical_failures.append("Duplicate slide headline detected in carousel.")

        # 4. Slide 1 Hook Check
        if slides_content:
            s1 = slides_content[0]
            if not s1.get("headline") or len(s1.get("headline", "").split()) < 3:
                critical_failures.append("Slide 1 hook is missing or insufficiently compelling.")
                failed_slide_indices.append(1)

        # 5. Slide 6 CTA Check
        if len(slides_content) >= 6:
            s6 = slides_content[5]
            s6_text = (
                s6.get("headline", "") + " " +
                s6.get("body_text", "") + " " +
                s6.get("cta_title", "") + " " +
                s6.get("cta_subtitle", "") + " " +
                s6.get("headline_prefix", "") + " " +
                s6.get("headline_highlight", "")
            ).lower()
            if not any(k in s6_text for k in ["save", "follow", "share", "promptpulse", "bookmark", "explore"]):
                critical_failures.append("Slide 6 does not contain a clear call to action (Save/Follow/Share).")
                failed_slide_indices.append(6)

        # 6. Metadata checks
        if not post_data.get("caption"):
            warnings.append("Post caption is empty.")
        if not post_data.get("hashtags"):
            warnings.append("Post hashtags are empty.")
        if not post_data.get("alt_text"):
            warnings.append("Accessibility alt text is missing.")

        passed = len(critical_failures) == 0

        return {
            "passed": passed,
            "critical_failures": critical_failures,
            "warnings": warnings,
            "auto_fix_applied": auto_fix_applied,
            "failed_slide_indices": list(set(failed_slide_indices)),
        }


qa_agent = QAAgent()
