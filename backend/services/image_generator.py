import os
import uuid
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from backend.config import settings
from backend.services.storage import storage

# Setup Jinja2 environment for HTML templates
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "slides"
ASSETS_DIR = TEMPLATES_DIR / "assets"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


class ImageGenerator:
    _asset_cache: Dict[str, str] = {}
    _public_url_cache: Dict[tuple[int, int], str] = {}

    def __init__(self):
        self.output_dir = settings.SLIDES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.width = settings.SLIDE_WIDTH    # 1080
        self.height = settings.SLIDE_HEIGHT  # 1350

    def get_public_url(self, post_id: int, slide_number: int) -> Optional[str]:
        return self._public_url_cache.get((post_id, slide_number))

    @classmethod
    def get_asset_base64(cls, filename: str) -> str:
        """Returns base64 data URI for an asset in slides/assets."""
        if filename not in cls._asset_cache:
            p = ASSETS_DIR / filename
            if p.exists():
                mime = "image/jpeg" if filename.endswith((".jpg", ".jpeg")) else "image/png"
                b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
                cls._asset_cache[filename] = f"data:{mime};base64,{b64}"
            else:
                cls._asset_cache[filename] = ""
        return cls._asset_cache[filename]

    def get_background_base64(self, slide_number: int, custom_url: Optional[str] = None, post_id: int = 1) -> str:
        """
        Returns a base64 data URI for a dark, atmospheric cinematic background image.
        Rotates through 10 curated dark backgrounds so no two consecutive slides or posts share the same one.
        """
        if custom_url:
            # If it's already a data URI or http URL, return it
            if custom_url.startswith("data:") or custom_url.startswith("http"):
                return custom_url
            # If it's a local file path
            local_p = Path(custom_url)
            if local_p.exists():
                mime = "image/jpeg" if local_p.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
                b64 = base64.b64encode(local_p.read_bytes()).decode("utf-8")
                return f"data:{mime};base64,{b64}"

        # Rotate through curated 10 backgrounds based on post_id and slide_number
        bg_num = (((post_id * 3) + (slide_number - 1)) % 10) + 1
        bg_name = f"bg_{bg_num}.jpg"
        bg_path = BACKGROUNDS_DIR / bg_name
        if bg_path.exists():
            return self.get_asset_base64(f"backgrounds/{bg_name}")

        return ""

    def render_html_content(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render slide HTML template with given context variables."""
        if not template_name.endswith(".html"):
            template_name = f"{template_name}.html"
        template = jinja_env.get_template(template_name)
        return template.render(**context)

    def generate_slide_image(
        self,
        post_id: int,
        slide_number: int,
        layout_type: str,
        content: Dict[str, Any],
        brand: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Renders a 1080x1350 PNG for a carousel slide according to the PromptPulse
        updated dark/cinematic design system specs.
        Attempts HTML headless rendering first; cleanly falls back to high-res Pillow rendering.
        Returns the absolute file path to the generated PNG.
        """
        brand = brand or {}
        filename = f"post_{post_id}_slide_{slide_number}_{uuid.uuid4().hex[:8]}.png"
        output_path = self.output_dir / filename

        # Smart headline splitting for gradient highlight
        headline = content.get("headline", "")
        headline_prefix = content.get("headline_prefix")
        headline_highlight = content.get("headline_highlight")
        headline_suffix = content.get("headline_suffix", "")
        if not headline_prefix and not headline_highlight and headline:
            words = headline.split()
            if len(words) <= 2:
                headline_prefix = ""
                headline_highlight = headline
            elif len(words) in (3, 4):
                headline_prefix = " ".join(words[:-1])
                headline_highlight = words[-1]
            else:
                headline_prefix = " ".join(words[:-2])
                headline_highlight = " ".join(words[-2:])

        # Smart tool name splitting for Slide 2
        tool_name = content.get("tool_name", headline)
        tool_name_prefix = content.get("tool_name_prefix", "")
        if not tool_name_prefix and " " in tool_name:
            t_parts = tool_name.split(" ", 1)
            tool_name_prefix = t_parts[0]
            tool_name = t_parts[1]

        prompt_preview = content.get("prompt_preview", content.get("prompt", ""))
        if prompt_preview.startswith('"') and prompt_preview.endswith('"'):
            prompt_preview = prompt_preview[1:-1]

        # Slide 1 Cover Design Variation (10 distinct styles so every post looks unique)
        actual_layout = layout_type
        hero_variants = [
            "hero",
            "hero_editorial",
            "hero_terminal",
            "hero_badge",
            "hero_minimal_bold",
            "hero_grid_matrix",
            "hero_magazine",
            "hero_blueprint",
            "hero_gradient_punch",
            "hero_duotone",
        ]
        if slide_number == 1:
            # If an explicit specific hero variant was provided (e.g. hero_terminal), use it directly
            if layout_type in hero_variants and layout_type != "hero":
                actual_layout = layout_type
            elif content.get("layout_variant") in hero_variants:
                actual_layout = content["layout_variant"]
            else:
                # Generic "hero" requested: cycle across all 10 distinct hero styles
                # using post_id so each consecutive post gets a completely unique hero
                variant_idx = max(0, post_id - 1) % len(hero_variants)
                actual_layout = hero_variants[variant_idx]

        # Background image with rotation across 10 distinct atmospheric AI textures
        custom_bg = content.get("background_image_url") or content.get("bg_image")
        background_image_url = self.get_background_base64(slide_number, custom_bg, post_id=post_id)

        # Slide counter string (e.g. "01 / 06")
        slide_counter = f"{slide_number:02d} / {settings.TOTAL_SLIDES:02d}"

        # Subtext fallback
        subtext = content.get("subtext") or content.get("body_text", "")

        context = {
            "post_id": post_id,
            "layout_variant": actual_layout,
            "slide_number": slide_number,
            "total_slides": settings.TOTAL_SLIDES,
            "slide_counter": slide_counter,
            "active_slide_index": slide_number,
            "background_image_url": background_image_url,
            "headline": headline,
            "headline_prefix": headline_prefix,
            "headline_highlight": headline_highlight,
            "headline_suffix": headline_suffix,
            "line1": content.get("line1"),
            "line2": content.get("line2"),
            "line3": content.get("line3"),
            "gradient_word": content.get("gradient_word", headline_highlight),
            "line5": content.get("line5"),
            "body_text": content.get("body_text", ""),
            "subtext": subtext,
            "eyebrow": content.get("eyebrow", "MEET"),
            "category": content.get("category", "AI DISCOVERY"),
            "tool_name_prefix": tool_name_prefix,
            "tool_name": tool_name,
            "tool_badge": content.get("tool_badge", tool_name),
            "annotation": content.get("annotation") or content.get("annotation_text", ""),
            "annotation_text": content.get("annotation_text") or content.get("annotation", ""),
            "prompt_preview": prompt_preview,
            "features": content.get("features", []),
            "showcase_items": content.get("showcase_items", []),
            "steps": content.get("steps", []),
            "examples": content.get("examples", []),
            "quote": content.get("quote", ""),
            "benefits": content.get("benefits", []),
            "cta_title": content.get("cta_title", "Save this post"),
            "cta_subtitle": content.get("cta_subtitle", "And start exploring the future."),
            "comparison_left_title": content.get("comparison_left_title", "Traditional Way"),
            "comparison_left_items": content.get("comparison_left_items", []),
            "comparison_right_title": content.get("comparison_right_title", "PromptPulse Way"),
            "comparison_right_items": content.get("comparison_right_items", []),
            "workflow_nodes": content.get("workflow_nodes", []),
            "primary_color": brand.get("primary_color", settings.PRIMARY_COLOR),
            "background_color": brand.get("background_color", settings.BACKGROUND_COLOR),
            "text_color": brand.get("text_color", settings.TEXT_COLOR),
            "secondary_color": brand.get("secondary_color", settings.SECONDARY_COLOR),
            "brand_name": brand.get("brand_name", settings.BRAND_NAME),
            "brand_handle": brand.get("brand_name", settings.BRAND_NAME).lower().replace(" ", ""),
        }

        # Embedded high-res visual assets matching the reference collage
        if actual_layout in hero_variants:
            context["asset_slide1_portal"] = self.get_asset_base64("slide1_portal.png")
        elif actual_layout == "tool_card":
            context["asset_slide2_tile"] = self.get_asset_base64("slide2_tile.png")
        elif actual_layout == "showcase":
            context["asset_thumb_cinematic"] = self.get_asset_base64("s3_thumb_cinematic.png")
            context["asset_thumb_anime"] = self.get_asset_base64("s3_thumb_anime.png")
            context["asset_thumb_sneaker"] = self.get_asset_base64("s3_thumb_sneaker.png")
            context["asset_thumb_nature"] = self.get_asset_base64("s3_thumb_nature.png")
        elif actual_layout == "steps":
            context["asset_slide4_wave"] = self.get_asset_base64("slide4_wave.png")
        elif actual_layout == "comparison":
            context["asset_s5_city"] = self.get_asset_base64("s5_thumb_city.png")
            context["asset_s5_lion"] = self.get_asset_base64("s5_thumb_lion.png")
            context["asset_s5_cat"] = self.get_asset_base64("s5_thumb_cat.png")
        elif actual_layout == "cta":
            context["asset_slide6_helmet"] = self.get_asset_base64("slide6_helmet.png")

        template_map = {
            "hero": "hero.html",
            "hero_editorial": "hero_editorial.html",
            "hero_terminal": "hero_terminal.html",
            "hero_badge": "hero_badge.html",
            "hero_minimal_bold": "hero_minimal_bold.html",
            "hero_grid_matrix": "hero_grid_matrix.html",
            "hero_magazine": "hero_magazine.html",
            "hero_blueprint": "hero_blueprint.html",
            "hero_gradient_punch": "hero_gradient_punch.html",
            "hero_duotone": "hero_duotone.html",
            "tool_card": "tool_card.html",
            "showcase": "showcase.html",
            "steps": "steps.html",
            "comparison": "comparison.html",
            "workflow": "workflow.html",
            "cta": "cta.html",
        }
        template_name = template_map.get(actual_layout, "hero.html")

        # Attempt Playwright / html2image rendering first
        rendered = False
        try:
            rendered = self._render_via_headless(template_name, context, str(output_path))
        except Exception:
            rendered = False

        if not rendered:
            # High quality Pillow vector/text fallback renderer at exact 1080x1350
            self._render_via_pillow(actual_layout, context, str(output_path))

        # Upload generated slide to Supabase Storage while preserving the local file path for QA/testing.
        storage_path = f"posts/{post_id}/{filename}"
        public_url = storage.upload_file(
            str(output_path),
            storage_path,
        )
        self._public_url_cache[(post_id, slide_number)] = public_url
        return str(output_path)

    def _render_via_headless(self, template_name: str, context: dict, output_path: str) -> bool:
        """Render using Html2Image with Chromium flags."""
        try:
            from html2image import Html2Image
            if not hasattr(self, "_hti") or self._hti is None:
                self._hti = Html2Image(
                    output_path=str(self.output_dir),
                    size=(self.width, self.height),
                    custom_flags=[
                        "--headless=new",
                        "--no-sandbox",
                        "--disable-gpu",
                        "--hide-scrollbars",
                        "--default-background-color=000000",
                        "--force-device-scale-factor=1",
                    ],
                )
            html_content = self.render_html_content(template_name, context)
            self._hti.screenshot(html_str=html_content, save_as=Path(output_path).name)
            return Path(output_path).exists()
        except Exception:
            return False

    def _render_via_pillow(self, layout_type: str, ctx: dict, output_path: str):
        """
        High fidelity typography and layout renderer using Pillow.
        Adheres strictly to the PromptPulse updated dark/cinematic brand specifications:
        1080x1350, #000000 pure black, #7C3AED accent glow, #FFFFFF headline, #D1D5DB body text,
        6-dot pagination, top-right counter ("01 / 06"), and right arrow.
        """
        width, height = self.width, self.height
        bg_color = "#000000"
        primary_color = "#7C3AED"
        text_color = "#FFFFFF"
        secondary_color = "#D1D5DB"
        cyan_accent = "#06B6D4"

        image = Image.new("RGBA", (width, height), bg_color)

        # Draw subtle atmospheric nebula glow
        slide_num = ctx.get("slide_number", 1)
        post_id = ctx.get("post_id", 1)
        bg_num = (((post_id * 3) + (slide_num - 1)) % 10) + 1
        bg_file = BACKGROUNDS_DIR / f"bg_{bg_num}.jpg"
        if bg_file.exists():
            try:
                bg_img = Image.open(bg_file).convert("RGBA").resize((width, height))
                # Apply 40% opacity
                bg_img.putalpha(int(255 * 0.40))
                image.paste(bg_img, (0, 0), bg_img)
            except Exception:
                pass

        draw = ImageDraw.Draw(image)

        # Load system fonts with fallback to Inter or Windows standard bold fonts
        def get_font(size: int, bold: bool = False):
            font_names = [
                "Inter-Bold.ttf" if bold else "Inter-Regular.ttf",
                "arialbd.ttf" if bold else "arial.ttf",
                "segoeuib.ttf" if bold else "segoeui.ttf",
                "calibrib.ttf" if bold else "calibri.ttf",
            ]
            for fn in font_names:
                try:
                    return ImageFont.truetype(fn, size)
                except IOError:
                    continue
            return ImageFont.load_default()

        font_headline = get_font(96, bold=True)
        font_sub = get_font(34, bold=False)
        font_meta = get_font(26, bold=True)
        font_card_title = get_font(34, bold=True)
        font_card_body = get_font(28, bold=False)

        margin = 70

        # 1. Slide Counter Top-Right ("01 / 06")
        counter_str = ctx.get("slide_counter", f"{slide_num:02d} / 06")
        draw.text((width - margin - 130, 60), counter_str, fill="#9CA3AF", font=font_meta)

        # Hero layout-specific styling for Slide 1 in Pillow renderer
        if slide_num == 1:
            if layout_type == "hero_terminal":
                draw.rounded_rectangle([margin, 50, margin + 400, 96], radius=10, fill="#0F172A", outline="#334155")
                draw.ellipse([margin + 16, 66, margin + 28, 78], fill="#EF4444")
                draw.ellipse([margin + 36, 66, margin + 48, 78], fill="#EAB308")
                draw.ellipse([margin + 56, 66, margin + 68, 78], fill="#10B981")
                draw.text((margin + 80, 60), "~/promptpulse/engine", fill="#94A3B8", font=get_font(20, bold=True))
            elif layout_type == "hero_blueprint":
                draw.line([30, 30, 70, 30], fill=cyan_accent, width=3)
                draw.line([30, 30, 30, 70], fill=cyan_accent, width=3)
                draw.line([width - 70, 30, width - 30, 30], fill=cyan_accent, width=3)
                draw.line([width - 30, 30, width - 30, 70], fill=cyan_accent, width=3)
                draw.text((margin, 60), "SPEC: ARCHITECTURE // 01", fill=cyan_accent, font=get_font(22, bold=True))
            elif layout_type == "hero_badge":
                draw.rounded_rectangle([margin, 55, margin + 270, 102], radius=25, fill="#831843", outline="#F472B6")
                draw.text((margin + 20, 66), "✦ BREAKTHROUGH", fill="#F472B6", font=get_font(20, bold=True))
            elif layout_type == "hero_editorial":
                draw.rounded_rectangle([margin, 55, margin + 260, 102], radius=25, fill="#312E81", outline="#818CF8")
                draw.text((margin + 20, 66), "• EDITORIAL REPORT", fill="#C7D2FE", font=get_font(20, bold=True))
            elif layout_type == "hero_magazine":
                draw.text((margin, 60), "PROMPTPULSE MAGAZINE // VOL. 2026", fill="#FBBF24", font=get_font(22, bold=True))
            elif layout_type == "hero_grid_matrix":
                draw.text((margin, 60), "[SYS.MATRIX // LAT: 01.448]", fill="#2DD4BF", font=get_font(22, bold=True))
            elif layout_type == "hero_gradient_punch":
                draw.rounded_rectangle([margin, 55, margin + 250, 102], radius=25, fill="#7C2D12", outline="#FB923C")
                draw.text((margin + 20, 66), "🔥 BREAKTHROUGH", fill="#FDBA74", font=get_font(20, bold=True))
            elif layout_type == "hero_duotone":
                draw.text((margin, 60), "// DUOTONE SPEC 01", fill="#A5B4FC", font=get_font(22, bold=True))
            elif layout_type == "hero_minimal_bold":
                draw.line([margin - 20, 60, margin - 20, 300], fill="#10B981", width=4)

        # 2. Headline with text wrap
        headline = ctx.get("headline", "")
        y_cursor = 140

        if layout_type == "tool_card":
            # Eyebrow
            draw.text((margin, y_cursor), ctx.get("eyebrow", "MEET"), fill="#9CA3AF", font=get_font(28, bold=True))
            y_cursor += 50
            # Tool name
            tool_name = f"{ctx.get('tool_name_prefix', '')} {ctx.get('tool_name', headline)}".strip()
            draw.text((margin, y_cursor), tool_name, fill=text_color, font=get_font(108, bold=True))
            y_cursor += 120
        else:
            headline_lines = self._wrap_text(headline, font_headline, width - (margin * 2))
            for idx, line in enumerate(headline_lines[:3]):
                # Highlight last line with purple accent
                color = primary_color if idx == len(headline_lines[:3]) - 1 else text_color
                draw.text((margin, y_cursor), line, fill=color, font=font_headline)
                y_cursor += 105

        y_cursor += 20

        # Subtext
        subtext = ctx.get("subtext") or ctx.get("body_text", "")
        if subtext:
            sub_lines = self._wrap_text(subtext, font_sub, width - (margin * 2))
            for line in sub_lines[:3]:
                draw.text((margin, y_cursor), line, fill=secondary_color, font=font_sub)
                y_cursor += 46

        # Annotation for Slide 1
        if slide_num == 1:
            annotation = ctx.get("annotation")
            if annotation:
                y_cursor += 10
                draw.text((margin, y_cursor), f"↳ {annotation}", fill="#C084FC", font=get_font(28, bold=False))
                y_cursor += 40

        y_cursor += 30

        # 3. Middle Content based on layout_type
        if layout_type == "tool_card":
            # 4 bottom feature badges
            features = ctx.get("features", [
                {"label": "Cinematic quality"}, {"label": "Native audio"},
                {"label": "High resolution"}, {"label": "Multiple styles"}
            ])
            badge_w = (width - (margin * 2) - (16 * 3)) // 4
            bx = margin
            by = height - 280
            for feat in features[:4]:
                flabel = feat.get("label", feat.get("title", "Feature")) if isinstance(feat, dict) else str(feat)
                draw.rounded_rectangle([bx, by, bx + badge_w, by + 120], radius=18, fill="#111827", outline="#374151", width=1)
                draw.text((bx + 16, by + 45), flabel[:16], fill=secondary_color, font=get_font(22, bold=True))
                bx += badge_w + 16

        elif layout_type == "showcase":
            # 4 use case cards
            items = ctx.get("showcase_items", [
                {"title": "Cinematic scenes", "tag": "4K Ultra-Real"},
                {"title": "Animated stories", "tag": "Anime & 3D"},
                {"title": "Product videos", "tag": "Commercial CGI"},
                {"title": "Nature & travel visuals", "tag": "Cinematic 8K"}
            ])
            cy = y_cursor + 20
            for itm in items[:4]:
                title = itm.get("title", "Use Case") if isinstance(itm, dict) else str(itm)
                draw.rounded_rectangle([margin, cy, width - margin, cy + 90], radius=16, fill="#111827", outline="#374151", width=1)
                draw.text((margin + 24, cy + 26), title, fill=text_color, font=font_card_title)
                # Play button
                draw.rounded_rectangle([width - margin - 110, cy + 18, width - margin - 20, cy + 72], radius=10, fill="#1F2937")
                draw.text((width - margin - 72, cy + 24), "▶", fill="#FFFFFF", font=get_font(22, bold=True))
                cy += 110

        elif layout_type == "steps":
            steps = ctx.get("steps", [
                {"title": "Enter your prompt", "desc": "Describe what you want to see."},
                {"title": "AI generates", "desc": "AI creates the video with audio."},
                {"title": "Customize", "desc": "Adjust style, length or details."},
                {"title": "Download & share", "desc": "Use for personal or commercial projects."}
            ])
            sy = y_cursor + 15
            for idx, s in enumerate(steps[:4]):
                step_title = s.get("title", f"Step {idx + 1}") if isinstance(s, dict) else str(s)
                step_desc = s.get("desc", "") if isinstance(s, dict) else ""
                # Box
                draw.rounded_rectangle([margin, sy, width - margin, sy + 100], radius=16, fill="#111827", outline="#374151", width=1)
                # Purple Circle badge #5B21B6
                draw.ellipse([margin + 16, sy + 16, margin + 84, sy + 84], fill="#5B21B6")
                draw.text((margin + 36, sy + 30), f"0{idx + 1}", fill="#FFFFFF", font=get_font(24, bold=True))
                # Text
                draw.text((margin + 105, sy + 20), step_title, fill=text_color, font=get_font(28, bold=True))
                if step_desc:
                    draw.text((margin + 105, sy + 56), step_desc, fill="#9CA3AF", font=get_font(22, bold=False))
                sy += 120

            # Neon wave cyan line
            draw.line([margin, height - 170, width - margin, height - 170], fill=cyan_accent, width=3)

        elif layout_type == "comparison":
            examples = ctx.get("examples", [
                {"prompt": "A futuristic city at sunset with flying cars", "tag": "Futuristic City"},
                {"prompt": "A close up of a lion in the wild", "tag": "Wildlife 4K"},
                {"prompt": "A cozy room during rain, with a cat", "tag": "Cozy Interior"}
            ])
            ey = y_cursor + 15
            for ex in examples[:3]:
                ptag = ex.get("tag", "PROMPT") if isinstance(ex, dict) else "PROMPT"
                ptext = ex.get("prompt", "") if isinstance(ex, dict) else str(ex)
                draw.rounded_rectangle([margin, ey, width - margin, ey + 110], radius=16, fill="#111827", outline="#374151", width=1)
                draw.text((margin + 20, ey + 16), ptag.upper(), fill=primary_color, font=get_font(20, bold=True))
                draw.text((margin + 20, ey + 48), f'"{ptext[:45]}..."', fill="#F3F4F6", font=get_font(22, bold=False))
                # Thumbnail box
                draw.rounded_rectangle([width - margin - 150, ey + 15, width - margin - 20, ey + 95], radius=12, fill="#1F2937")
                draw.text((width - margin - 92, ey + 40), "▶", fill="#FFFFFF", font=get_font(24, bold=True))
                ey += 135

        elif layout_type == "cta":
            # 4 creator benefits
            benefits = ctx.get("benefits", [
                {"text": "Create faster"}, {"text": "More possibilities"},
                {"text": "For everyone"}, {"text": "The future is visual"}
            ])
            by = y_cursor + 15
            for b in benefits[:4]:
                btext = b.get("text", "Benefit") if isinstance(b, dict) else str(b)
                draw.rounded_rectangle([margin, by, width - margin, by + 80], radius=16, fill="#111827", outline="#374151", width=1)
                draw.ellipse([margin + 16, by + 16, margin + 64, by + 64], fill=primary_color)
                draw.text((margin + 30, by + 24), "⚡", fill="#FFFFFF", font=get_font(22, bold=True))
                draw.text((margin + 85, by + 24), btext, fill=text_color, font=get_font(28, bold=True))
                by += 98

            # Full-width CTA button #5B21B6 to #2563EB
            btn_top = height - 250
            draw.rounded_rectangle([margin, btn_top, width - margin, btn_top + 110], radius=55, fill="#5B21B6", outline="#2563EB", width=2)
            draw.text((margin + 36, btn_top + 34), "📌", fill="#FFFFFF", font=get_font(32, bold=True))
            draw.text((margin + 90, btn_top + 24), ctx.get("cta_title", "Save this post"), fill="#FFFFFF", font=get_font(32, bold=True))
            draw.text((margin + 90, btn_top + 64), ctx.get("cta_subtitle", "And start exploring the future."), fill="#D1D5DB", font=get_font(20, bold=False))
            draw.ellipse([width - margin - 80, btn_top + 25, width - margin - 20, btn_top + 85], fill="#2563EB")
            draw.text((width - margin - 58, btn_top + 36), "→", fill="#FFFFFF", font=get_font(28, bold=True))

        # 4. Dot Pagination Bottom-Center
        dot_y = height - 70
        dot_spacing = 20
        total_dots = 6
        active_dot = max(1, min(6, slide_num))
        # Total dots width: 5 * 12 + 32 + 5 * 8 = 132
        start_x = (width - 140) // 2
        curr_x = start_x
        for i in range(1, total_dots + 1):
            if i == active_dot:
                draw.rounded_rectangle([curr_x, dot_y - 4, curr_x + 32, dot_y + 8], radius=6, fill=primary_color)
                curr_x += 32 + 8
            else:
                draw.ellipse([curr_x, dot_y - 2, curr_x + 12, dot_y + 10], fill="#4B5563")
                curr_x += 12 + 8

        # 5. Right Arrow Bottom-Right
        draw.text((width - margin - 40, height - 85), "→", fill="#FFFFFF", font=get_font(36, bold=True))

        # Save temporarily to local disk
        image.save(output_path, "PNG", optimize=True)

    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text cleanly into lines respecting maximum pixel width."""
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = []

        dummy_img = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_w = bbox[2] - bbox[0]
            if line_w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))
        return lines


image_generator = ImageGenerator()
