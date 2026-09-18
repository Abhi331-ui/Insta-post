import json
from typing import List, Dict, Any
from backend.services.ai_provider import ai_provider


class ContentAgent:
    def __init__(self):
        self.ai = ai_provider

    async def write_carousel(self, opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Writes structured content for exactly 6 slides following the PromptPulse narrative arc:
        Slide 1 — HOOK: Large headline (max 8 words), minimal text, curiosity-driven
        Slide 2 — CONTEXT: What is happening and why it matters
        Slide 3 — DISCOVERY: Introduce the tool / feature / workflow card
        Slide 4 — HOW IT WORKS: 3 practical steps
        Slide 5 — VALUE: Comparison or workflow diagram
        Slide 6 — CTA: Save / Share / Follow
        """
        system_prompt = """You are the PromptPulse Master Content Creator.
Write a high-converting, 6-slide Instagram carousel based on the selected opportunity.
The carousel MUST strictly match the exact 6-slide aesthetic and narrative arc of the PromptPulse visual system:

SLIDE 1 — HOOK (layout_type: "hero"):
- "headline_prefix": Uppercase prefix (e.g. "THIS AI TURNS YOUR IDEAS INTO")
- "headline_highlight": Radiant punchline words (e.g. "STUNNING VIDEOS")
- "body_text": Subtitle (max 15 words, e.g. "Just a text prompt. No camera. No editing. Pure imagination.")
- "annotation": Handwritten cursive thought (max 8 words, e.g. "From thoughts to visuals. In minutes.")
- "prompt_preview": Sample realistic prompt (e.g. "A cinematic scene of a lone traveler on a mountain...")

SLIDE 2 — MEET THE TOOL (layout_type: "tool_card"):
- "eyebrow": "M E E T"
- "tool_name_prefix": Brand/Company (e.g. "Google")
- "tool_name": Tool or Model name (e.g. "Veo 3")
- "tool_badge": Short badge text (e.g. "Veo 3")
- "body_text": Punchy tagline (e.g. "The most advanced AI video model yet.")
- "annotation": Handwritten reaction (e.g. "Not just videos. Realistic videos.")
- "features": Exactly 4 capabilities with short labels:
  [{"icon": "camera", "label": "Cinematic quality"}, {"icon": "audio", "label": "Native audio & dialogue"}, {"icon": "resolution", "label": "4K High resolution"}, {"icon": "style", "label": "Multiple styles"}]

SLIDE 3 — USE CASES / SHOWCASE (layout_type: "showcase"):
- "headline_prefix": "WHAT CAN YOU"
- "headline_highlight": "CREATE?"
- "body_text": "From imagination to reality — here are some examples."
- "annotation": "Same tool. Endless possibilities."
- "showcase_items": Exactly 4 use cases with title and tag:
  [{"title": "Cinematic scenes", "tag": "4K Ultra-Real"}, {"title": "Animated stories", "tag": "Anime & 3D"}, {"title": "Product videos", "tag": "Commercial CGI"}, {"title": "Nature & travel visuals", "tag": "Cinematic 8K"}]

SLIDE 4 — HOW IT WORKS (layout_type: "steps"):
- "headline_prefix": "HOW IT"
- "headline_highlight": "WORKS"
- "body_text": "Turn your idea into a video in 4 simple steps."
- "annotation": "Ideas -> Videos That Simple."
- "steps": Exactly 4 numbered steps:
  [{"title": "Enter your prompt", "desc": "Describe what you want to see."},
   {"title": "AI generates", "desc": "AI creates the video with audio."},
   {"title": "Customize", "desc": "Adjust style, length or details."},
   {"title": "Download & share", "desc": "Use for personal or commercial projects."}]

SLIDE 5 — REAL EXAMPLES (layout_type: "comparison"):
- "headline_prefix": "REAL"
- "headline_highlight": "EXAMPLES"
- "body_text": "Same prompt. Different worlds."
- "annotation": "Text in. This out."
- "examples": Exactly 3 prompt examples:
  [{"prompt": "A futuristic city at sunset with flying cars", "tag": "Futuristic City"},
   {"prompt": "A close up of a lion in the wild", "tag": "Wildlife 4K"},
   {"prompt": "A cozy room during rain, with a cat", "tag": "Cozy Interior"}]
- "quote": "It literally feels like bringing your imagination to life."

SLIDE 6 — A NEW ERA FOR CREATORS / CTA (layout_type: "cta"):
- "headline_prefix": "A NEW ERA FOR"
- "headline_highlight": "CREATORS"
- "body_text": "Better tools. Bigger ideas. A more creative you."
- "annotation": "Create what doesn't exist yet."
- "benefits": Exactly 4 creator benefits:
  [{"icon": "bolt", "text": "Create faster"},
   {"icon": "infinity", "text": "More possibilities"},
   {"icon": "users", "text": "For everyone"},
   {"icon": "rocket", "text": "The future is visual"}]
- "cta_title": "Save this post"
- "cta_subtitle": "And start exploring the future."

Return a JSON array of EXACTLY 6 slide objects. Every object must include "slide_number": int (1 to 6), "headline" (or "headline_prefix" and "headline_highlight"), "body_text", and "layout_type".
"""

        user_prompt = f"""Opportunity Details:
Topic: {opportunity.get('topic')}
Selected Angle: {opportunity.get('selected_angle')}
Hook: {opportunity.get('hook')}
Why Today: {opportunity.get('why_today')}
Pillar: {opportunity.get('content_pillar')}
Target Audience: {opportunity.get('target_audience')}
Sources: {opportunity.get('sources')}
"""

        slides = await self.ai.complete_json(system_prompt, user_prompt, model_tier="strong")

        # Validation: ensure exactly 6 slides
        if not isinstance(slides, list) or len(slides) != 6:
            slides = self._fallback_slides(opportunity)

        # Force slide numbers 1..6 and layout types
        expected_layouts = ["hero", "tool_card", "showcase", "steps", "comparison", "cta"]
        for idx, s in enumerate(slides):
            s["slide_number"] = idx + 1
            if not s.get("layout_type"):
                s["layout_type"] = expected_layouts[idx]
            if "headline" not in s or not s["headline"]:
                prefix = s.get("headline_prefix", "")
                highlight = s.get("headline_highlight", "")
                s["headline"] = f"{prefix} {highlight}".strip() or f"Key Insight {idx + 1}"

        return slides

    async def generate_caption(self, opportunity: Dict[str, Any], slides: List[Dict[str, Any]]) -> str:
        """Generate high-retention Instagram caption."""
        system_prompt = """You are the PromptPulse Social Copywriter.
Write an engaging Instagram caption for this 6-slide carousel.
Structure:
- Line 1: Strong hook matching slide 1
- Blank line
- 3-4 bullet points highlighting the discovery and practical takeaway
- Blank line
- "Swipe through for the full 6-step breakdown."
- Blank line
- CTA: "📌 Save this for when you need it. Follow @promptpulse for daily verified AI breakthroughs."
Do NOT include hashtags in the caption body.
"""
        user_prompt = f"Topic: {opportunity.get('topic')}\nHook: {opportunity.get('hook')}\nSlides: {json.dumps(slides)}"
        caption = await self.ai.complete(system_prompt, user_prompt, model_tier="strong")
        return caption.strip()

    async def generate_hashtags(self, opportunity: Dict[str, Any]) -> str:
        """Generate targeted niche hashtags."""
        tags = [
            "#aitools",
            "#artificialintelligence",
            "#productivityhacks",
            "#techupdates",
            "#promptengineering",
            "#developerlife",
            "#softwareengineer",
            "#aiagents",
            "#futureofwork",
            "#automation",
            "#generativeai",
            "#workflow",
        ]
        return " ".join(tags)

    async def generate_alt_text(self, slides: List[Dict[str, Any]]) -> str:
        """Generate accessibility alt-text for screen readers."""
        alt_lines = []
        for s in slides:
            alt_lines.append(f"Slide {s.get('slide_number')}: {s.get('headline')}. {s.get('body_text')}")
        return " | ".join(alt_lines)

    def _fallback_slides(self, opp: Dict[str, Any]) -> List[Dict[str, Any]]:
        topic = opp.get("topic", "Google Veo 3")
        hook = opp.get("hook", "THIS AI TURNS YOUR IDEAS INTO STUNNING VIDEOS")
        return [
            {
                "slide_number": 1,
                "headline_prefix": "THIS AI TURNS YOUR IDEAS INTO",
                "headline_highlight": "STUNNING VIDEOS",
                "headline": hook,
                "body_text": "Just a text prompt. No camera. No editing. Pure imagination.",
                "annotation": "From thoughts to visuals. In minutes.",
                "prompt_preview": f"A cinematic scene of {topic} generating realistic visuals...",
                "layout_type": "hero",
            },
            {
                "slide_number": 2,
                "eyebrow": "M E E T",
                "tool_name_prefix": "Google",
                "tool_name": topic if " " not in topic else topic.split(" ", 1)[1],
                "tool_badge": topic,
                "headline": f"Meet {topic}",
                "body_text": "The most advanced generative AI model yet.",
                "annotation": "Not just videos. Realistic videos.",
                "features": [
                    {"icon": "camera", "label": "Cinematic quality"},
                    {"icon": "audio", "label": "Native audio & dialogue"},
                    {"icon": "resolution", "label": "4K High resolution"},
                    {"icon": "style", "label": "Multiple styles"},
                ],
                "layout_type": "tool_card",
            },
            {
                "slide_number": 3,
                "headline_prefix": "WHAT CAN YOU",
                "headline_highlight": "CREATE?",
                "headline": "WHAT CAN YOU CREATE?",
                "body_text": "From imagination to reality — here are some examples.",
                "annotation": "Same tool. Endless possibilities.",
                "showcase_items": [
                    {"title": "Cinematic scenes", "tag": "4K Ultra-Real"},
                    {"title": "Animated stories", "tag": "Anime & 3D"},
                    {"title": "Product videos", "tag": "Commercial CGI"},
                    {"title": "Nature & travel visuals", "tag": "Cinematic 8K"},
                ],
                "layout_type": "showcase",
            },
            {
                "slide_number": 4,
                "headline_prefix": "HOW IT",
                "headline_highlight": "WORKS",
                "headline": "HOW IT WORKS",
                "body_text": "Turn your idea into a video in 4 simple steps.",
                "annotation": "Ideas -> Videos That Simple.",
                "steps": [
                    {"title": "Enter your prompt", "desc": "Describe what you want to see."},
                    {"title": f"{topic} generates", "desc": "AI creates the output with full context."},
                    {"title": "Customize", "desc": "Adjust style, length or details."},
                    {"title": "Download & share", "desc": "Use for personal or commercial projects."},
                ],
                "layout_type": "steps",
            },
            {
                "slide_number": 5,
                "headline_prefix": "REAL",
                "headline_highlight": "EXAMPLES",
                "headline": "REAL EXAMPLES",
                "body_text": "Same prompt. Different worlds.",
                "annotation": "Text in. This out.",
                "examples": [
                    {"prompt": "A futuristic city at sunset with flying cars", "tag": "Futuristic City"},
                    {"prompt": "A close up of a lion in the wild", "tag": "Wildlife 4K"},
                    {"prompt": "A cozy room during rain, with a cat", "tag": "Cozy Interior"},
                ],
                "quote": "It literally feels like bringing your imagination to life.",
                "layout_type": "comparison",
            },
            {
                "slide_number": 6,
                "headline_prefix": "A NEW ERA FOR",
                "headline_highlight": "CREATORS",
                "headline": "A NEW ERA FOR CREATORS",
                "body_text": "Better tools. Bigger ideas. A more creative you.",
                "annotation": "Create what doesn't exist yet.",
                "benefits": [
                    {"icon": "bolt", "text": "Create faster"},
                    {"icon": "infinity", "text": "More possibilities"},
                    {"icon": "users", "text": "For everyone"},
                    {"icon": "rocket", "text": "The future is visual"},
                ],
                "cta_title": "Save this post",
                "cta_subtitle": "And start exploring the future.",
                "layout_type": "cta",
            },
        ]


content_agent = ContentAgent()
