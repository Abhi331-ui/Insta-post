import json
import re
from typing import List, Dict, Any
from backend.services.ai_provider import ai_provider


class ContentAgent:
    def __init__(self):
        self.ai = ai_provider

    async def write_carousel(self, opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Writes structured content for exactly 6 slides following the PromptPulse Cosmic-Neon UI design system:
        Slide 1 — HOOK (hero): Category header, headline prefix & glowing highlight, 4 capability pills, UI search mockup
        Slide 2 — THE CONCEPT / TOOL (tool_card): Deep dive on the tool/concept with 4 capability badges
        Slide 3 — REAL POSSIBILITIES (showcase): 2x2 grid of 4 cards with tags, prompts, play button thumbnails, flow bar
        Slide 4 — HOW IT WORKS (steps): Split layout: 4 progressive steps on left, glowing UI workspace monitor on right
        Slide 5 — REAL EXAMPLES (comparison): 4 horizontal rows with prompt, arrow, video thumbnail (play button + 0:08), category tag
        Slide 6 — LEAD MAGNET CTA (cta): Full resource pack card with 4 benefits, comment-to-DM keyword badge, glowing CTA pill
        """
        system_prompt = """You are an elite Instagram Carousel Strategist & Viral Copywriter.
Your goal is to write a high-converting, visually stunning 6-slide carousel for ANY topic given by users (e.g. AI models, tech breakthroughs, productivity frameworks, developer tools, design systems, etc.).
Every slide must have crisp, punchy copy formatted for a 1080x1350 dark-mode cosmic neon presentation.

NARRATIVE ARC ACROSS 6 SLIDES:

SLIDE 1 — THE HOOK (layout_type: "hero"):
- "category": Short uppercase category (e.g. "AI DISCOVERY", "NEW LAUNCH", "WORKFLOW UNLOCKED")
- "headline_prefix": Short uppercase kicker (1-2 lines, e.g. "THE AI TOOL YOU'LL WISH", "THE UNFAIR ADVANTAGE TO")
- "headline_highlight": Radiant punchline words (1 line, e.g. "YOU KNEW EARLIER", "SCALING FAST")
- "body_text": High-curiosity subheadline (max 15 words) explaining the core promise.
- "annotation": Handwritten cursive note (max 6 words, e.g. "Same Prompt Infinite Possibilities", "Save this immediately.")
- "feature_pills": Exactly 4 capability pills:
  [{"icon": "⚡", "title": "IDEA", "desc": "Just a prompt"},
   {"icon": "✦", "title": "CREATE", "desc": "In seconds"},
   {"icon": "ılı", "title": "ITERATE", "desc": "Make it better"},
   {"icon": "↗", "title": "SHARE", "desc": "Bring it to life"}]
- "prompt_preview": Provocative search prompt teaser (max 12 words, e.g. "Describe what you want to create...")
- "cta_button_text": "DISCOVER WHAT'S NEXT"
- "tagline_right": "BETTER TOOLS<br>BRIGHTER IDEAS<br>A MORE CREATIVE YOU"

SLIDE 2 — THE CONCEPT / TOOL (layout_type: "tool_card"):
- "category": "DEEP DIVE"
- "eyebrow": "M E E T" or "T H E  S H I F T" or "T H E  F R A M E W O R K"
- "tool_name_prefix": Brand, Context, or Category (e.g. "Introducing", "The Architecture:")
- "tool_name": The Core Tool, Model, or Principle (e.g. "Google Veo 3", "Claude Artifacts", "Cursor Composer")
- "tool_badge": Short badge (e.g. "Gamechanger", "Next-Gen 3.0", "Core Shift")
- "body_text": Punchy 1-2 sentence explanation of why this changes everything.
- "annotation": Handwritten observation (e.g. "Not just fast. Superhuman.")
- "features": Exactly 4 capabilities or key realities:
  [{"icon": "bolt", "label": "10x Speed & Power"},
   {"icon": "target", "label": "Hyper-Precise Control"},
   {"icon": "shield", "label": "Production-Ready Quality"},
   {"icon": "sparkles", "label": "Instant Iteration"}]
- "cta_button_text": "EXPLORE POSSIBILITIES"
- "tagline_left": "FUTURE READY.<br>BUILT FOR SPEED."

SLIDE 3 — REAL POSSIBILITIES (layout_type: "showcase"):
- "category": "REAL POSSIBILITIES"
- "headline_prefix": "ONE PROMPT."
- "headline_highlight": "ENDLESS POSSIBILITIES."
- "body_text": "From ideas to stunning results — here's what you can create with [Topic]."
- "annotation": "Same tool. Different worlds."
- "grid_cards": Exactly 4 showcase cards (tailored to the topic):
  [{"tag": "CINEMATIC", "title": "Epic Landscapes", "prompt": "\"A cinematic drone shot over a futuristic city at sunset...\""},
   {"tag": "CHARACTERS", "title": "Lifelike People", "prompt": "\"A close-up of a traveler in a neon-lit Tokyo street, cinematic style...\""},
   {"tag": "PRODUCTS", "title": "Stunning Ads", "prompt": "\"A cinematic product ad for a sleek coffee machine, with steam and dramatic lighting...\""},
   {"tag": "ANIMATION", "title": "Animated Worlds", "prompt": "\"A cozy animated short of a little robot exploring a magical forest at night...\""}]
- "flow_steps": Exactly 3 progressive step labels (e.g. ["TEXT", "VIDEO", "REALITY"] or ["PROMPT", "AI", "OUTPUT"])
- "cta_button_text": "WHAT WILL YOU CREATE?"
- "tagline_left": "BIGGER IDEAS.<br>BRIGHTER REALITIES."

SLIDE 4 — HOW IT WORKS (layout_type: "steps"):
- "category": "HOW IT WORKS"
- "headline_prefix": "FROM PROMPT"
- "headline_highlight": "TO MASTERPIECE."
- "body_text": "Create stunning results in just a few simple steps."
- "annotation": "Simple steps. Incredible results."
- "steps": Exactly 4 sequential actionable steps:
  [{"title": "Write Your Prompt", "desc": "Describe what you want in simple text.", "example": "e.g. \"A serene mountain lake at sunset, cinematic style\""},
   {"title": "Customize (Optional)", "desc": "Choose style, aspect ratio and other settings."},
   {"title": "Generate", "desc": "Let AI do the magic. It creates high-quality output."},
   {"title": "Download & Share", "desc": "Preview, download and share your masterpiece."}]
- "mockup_prompt": Sample prompt matching the topic (e.g. "A peaceful mountain lake at sunset, cinematic, with soft music")
- "cta_button_text": "NEXT: SEE REAL EXAMPLES"
- "tagline_left": "SAME IDEA.<br>A BIGGER WORLD."

SLIDE 5 — REAL EXAMPLES (layout_type: "comparison"):
- "category": "REAL EXAMPLES"
- "headline_prefix": "SAME PROMPT."
- "headline_highlight": "INCREDIBLE RESULTS."
- "body_text": "Real prompts. Real results. Made with [Topic]."
- "annotation": "Just a prompt. Look at the result."
- "rows": Exactly 4 horizontal prompt-to-result rows:
  [{"number": "01", "tag": "CINEMATIC", "tag_desc": "Futuristic worlds", "prompt": "\"A cinematic drone shot over a futuristic city at sunrise, with flying cars and low clouds, ultra realistic, 8k.\"", "duration": "0:08"},
   {"number": "02", "tag": "CHARACTERS", "tag_desc": "Bring stories to life", "prompt": "\"A close-up of a traveler in a spacesuit standing on an alien planet, looking at a giant ringed planet in the sky, cinematic lighting, ultra realistic.\"", "duration": "0:08"},
   {"number": "03", "tag": "ANIMATION", "tag_desc": "Animated worlds", "prompt": "\"A cozy animated short of a little robot sitting in a forest, with glowing fireflies, Pixar style, warm lighting.\"", "duration": "0:08"},
   {"number": "04", "tag": "PRODUCTS", "tag_desc": "Stunning product ads", "prompt": "\"A close-up product shot of a premium sneaker, rotating slowly, with dramatic studio lighting, black background, cinematic style.\"", "duration": "0:08"}]
- "cta_button_text": "NEXT: A NEW ERA FOR CREATORS"
- "tagline_left": "IDEAS TO VIDEOS.<br>FASTER THAN EVER."

SLIDE 6 — LEAD MAGNET CTA (layout_type: "cta"):
- "category": "A NEW ERA"
- "headline_prefix": "WANT THE FULL"
- "headline_highlight": "RESOURCE PACK?"
- "body_text": "I put together the complete free checklist, prompts & templates for you."
- "annotation": "Free for the community."
- "benefits": Exactly 4 takeaways:
  [{"icon": "⚡", "text": "Instant Actionable Prompts"},
   {"icon": "∞", "text": "Save 10+ Hours of Trial & Error"},
   {"icon": "👥", "text": "Tested by Top Creators"},
   {"icon": "🚀", "text": "Immediate Real Results"}]
- "dm_keyword": A single, memorable uppercase viral keyword (e.g. "VEO", "PROMPT", "TOOLKIT", "BLUEPRINT")
- "dm_message": Pre-written DM message with placeholder link (e.g. "Hey! Here is your free resource pack: https://promptpulse.ai/toolkit - let me know what you think!")
- "cta_button_text": "COMMENT \"[KEYWORD]\" TO GET IT"
- "tagline_left": "BETTER TOOLS.<br>BRIGHTER IDEAS."

Return a JSON array of EXACTLY 6 slide objects. Every object must include "slide_number": int (1 to 6), "headline" (or "headline_prefix" and "headline_highlight"), "body_text", and "layout_type".
"""

        user_prompt = f"""Opportunity Details:
Topic: {opportunity.get('topic')}
Selected Angle: {opportunity.get('selected_angle')}
Hook: {opportunity.get('hook')}
Tone / Style: {opportunity.get('tone', 'Practical & High-Impact')}
Key Notes / Must-Include Details: {opportunity.get('notes', 'None provided')}
Custom Lead Magnet Keyword: {opportunity.get('dm_keyword', 'Auto-generate a punchy 1-word keyword')}
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
        """Generate high-retention Instagram caption with Comment-to-DM conversion trigger."""
        dm_keyword = "VEO"
        if slides and len(slides) >= 6:
            dm_keyword = slides[5].get("dm_keyword", "VEO")

        system_prompt = f"""You are an elite Instagram Social Copywriter.
Write an engaging, high-retention Instagram caption for this 6-slide carousel.
Structure:
- Line 1: Strong hook matching slide 1 (captivates in the feed before the "more" button)
- Blank line
- 3-4 bullet points summarizing the core insights and why this matters right now
- Blank line
- "Swipe through for the complete 6-step breakdown 👉"
- Blank line
- High-Converting CTA:
  "💬 Comment '{dm_keyword}' below and I'll DM you the free resource pack & checklist!"
- Blank line
- "📌 Save this post for reference & follow for daily insights."
Do NOT include hashtags in the caption body.
"""
        user_prompt = f"Topic: {opportunity.get('topic')}\nHook: {opportunity.get('hook')}\nSlides: {json.dumps(slides)}"
        caption = await self.ai.complete(system_prompt, user_prompt, model_tier="strong")
        return caption.strip()

    async def generate_hashtags(self, opportunity: Dict[str, Any]) -> str:
        """Generate targeted niche hashtags dynamically based on topic."""
        topic = opportunity.get("topic", "productivity")
        system_prompt = "Generate 12-15 highly relevant, high-traffic Instagram hashtags for the given topic. Return ONLY the hashtags separated by spaces."
        try:
            res = await self.ai.complete(system_prompt, f"Topic: {topic}", model_tier="fast")
            if res and "#" in res:
                return res.strip()
        except Exception:
            pass

        # Fallback tags
        tags = [
            "#aitools",
            "#growthhacking",
            "#productivityhacks",
            "#entrepreneurship",
            "#businesstips",
            "#techupdates",
            "#contentcreation",
            "#creatorsecrets",
            "#workflow",
            "#marketingstrategy",
            "#automation",
            "#digitalproducts",
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
        hook = opp.get("hook") or f"THE AI TOOL YOU'LL WISH YOU KNEW EARLIER"
        notes = opp.get("notes") or ""
        tone = opp.get("tone") or "Practical Deep Dive"
        custom_kw = opp.get("dm_keyword")
        if custom_kw and custom_kw.strip():
            keyword = custom_kw.strip().upper()
        else:
            words = [w for w in topic.split() if not w.isdigit()]
            keyword = words[-1].upper() if words else "VEO"

        words = [w for w in topic.split() if not w.isdigit()]
        tool_prefix = words[0] if len(words) > 1 else "The"
        tool_name = " ".join(words[1:]) if len(words) > 1 else topic

        # Category based on tone
        cat_map = {
            "Technical Deep Dive": "ENGINEERING DEEP DIVE",
            "Viral Hype": "BREAKTHROUGH LAUNCH",
            "Step-by-Step Tutorial": "STEP-BY-STEP GUIDE",
            "Creator Breakdown": "CREATOR BLUEPRINT",
        }
        category_header = cat_map.get(tone, "AI DISCOVERY")

        # Dynamic features from user notes if present
        features = [
            {"icon": "bolt", "label": "10x Speed & Power"},
            {"icon": "target", "label": "Hyper-Precise Control"},
            {"icon": "shield", "label": "Production-Ready Quality"},
            {"icon": "sparkles", "label": "Instant Iteration"},
        ]
        if notes:
            note_lines = [n.strip() for n in re.split(r"[\n,;•\.-]+", notes) if n.strip() and len(n.strip()) > 3]
            if len(note_lines) >= 1:
                features[0] = {"icon": "bolt", "label": note_lines[0][:26]}
            if len(note_lines) >= 2:
                features[1] = {"icon": "target", "label": note_lines[1][:26]}
            if len(note_lines) >= 3:
                features[2] = {"icon": "shield", "label": note_lines[2][:26]}
            if len(note_lines) >= 4:
                features[3] = {"icon": "sparkles", "label": note_lines[3][:26]}

        return [
            {
                "slide_number": 1,
                "category": category_header,
                "headline_prefix": "THE AI TOOL\nYOU'LL WISH",
                "headline_highlight": "YOU KNEW EARLIER",
                "headline": hook,
                "body_text": f"A new way to turn ideas into reality with {topic}.",
                "annotation": "Same Prompt Infinite Possibilities",
                "feature_pills": [
                    {"icon": "⚡", "title": "IDEA", "desc": "Just a prompt"},
                    {"icon": "✦", "title": "CREATE", "desc": "In seconds"},
                    {"icon": "ılı", "title": "ITERATE", "desc": "Make it better"},
                    {"icon": "↗", "title": "SHARE", "desc": "Bring it to life"}
                ],
                "prompt_preview": f"Describe what you want to create with {topic}...",
                "cta_button_text": "DISCOVER WHAT'S NEXT",
                "tagline_right": "BETTER TOOLS<br>BRIGHTER IDEAS<br>A MORE CREATIVE YOU",
                "layout_type": "hero",
            },
            {
                "slide_number": 2,
                "category": "DEEP DIVE",
                "eyebrow": "M E E T",
                "tool_name_prefix": tool_prefix,
                "tool_name": tool_name,
                "tool_badge": "Breakthrough",
                "headline": f"Meet {topic}",
                "body_text": f"The most advanced system yet to turn imagination into reality.",
                "annotation": "Not just fast. Superhuman.",
                "features": features,
                "cta_button_text": "EXPLORE POSSIBILITIES",
                "tagline_left": "FUTURE READY.<br>BUILT FOR SPEED.",
                "layout_type": "tool_card",
            },
            {
                "slide_number": 3,
                "category": "REAL POSSIBILITIES",
                "headline_prefix": "ONE PROMPT.",
                "headline_highlight": "ENDLESS POSSIBILITIES.",
                "headline": "ONE PROMPT. ENDLESS POSSIBILITIES.",
                "body_text": f"From ideas to stunning results — here's what you can create with {topic}.",
                "annotation": "Same tool. Different worlds.",
                "grid_cards": [
                    {"tag": "CINEMATIC", "title": "Epic Landscapes", "prompt": '"A cinematic drone shot over a futuristic city at sunset..."'},
                    {"tag": "CHARACTERS", "title": "Lifelike People", "prompt": '"A close-up of a traveler in a neon-lit Tokyo street, cinematic style..."'},
                    {"tag": "PRODUCTS", "title": "Stunning Ads", "prompt": '"A cinematic product ad for a sleek coffee machine, with steam and dramatic lighting..."'},
                    {"tag": "ANIMATION", "title": "Animated Worlds", "prompt": '"A cozy animated short of a little robot exploring a magical forest at night..."'}
                ],
                "flow_steps": ["TEXT", "VIDEO", "REALITY"],
                "cta_button_text": "WHAT WILL YOU CREATE?",
                "tagline_left": "BIGGER IDEAS.<br>BRIGHTER REALITIES.",
                "layout_type": "showcase",
            },
            {
                "slide_number": 4,
                "category": "HOW IT WORKS",
                "headline_prefix": "FROM PROMPT",
                "headline_highlight": "TO MASTERPIECE.",
                "headline": "FROM PROMPT TO MASTERPIECE.",
                "body_text": "Create stunning videos in just a few simple steps.",
                "annotation": "Simple steps. Incredible results.",
                "steps": [
                    {"title": "Write Your Prompt", "desc": "Describe the video you want in simple text.", "example": 'e.g. "A serene mountain lake at sunset, cinematic style"'},
                    {"title": "Customize (Optional)", "desc": "Choose style, aspect ratio and other settings."},
                    {"title": "Generate", "desc": f"Let {topic} do the magic. It creates high-quality output."},
                    {"title": "Download & Share", "desc": "Preview, download and share your masterpiece."}
                ],
                "mockup_prompt": "A peaceful mountain lake at sunset, cinematic, with soft music",
                "cta_button_text": "NEXT: SEE REAL EXAMPLES",
                "tagline_left": "SAME IDEA.<br>A BIGGER WORLD.",
                "layout_type": "steps",
            },
            {
                "slide_number": 5,
                "category": "REAL EXAMPLES",
                "headline_prefix": "SAME PROMPT.",
                "headline_highlight": "INCREDIBLE RESULTS.",
                "headline": "SAME PROMPT. INCREDIBLE RESULTS.",
                "body_text": f"Real prompts. Real videos. Made with {topic}.",
                "annotation": "Just a prompt. Look at the result.",
                "rows": [
                    {"number": "01", "tag": "CINEMATIC", "tag_desc": "Futuristic worlds", "prompt": '"A cinematic drone shot over a futuristic city at sunrise, with flying cars and low clouds, ultra realistic, 8k."', "duration": "0:08"},
                    {"number": "02", "tag": "CHARACTERS", "tag_desc": "Bring stories to life", "prompt": '"A close-up of a traveler in a spacesuit standing on an alien planet, looking at a giant ringed planet in the sky, cinematic lighting, ultra realistic."', "duration": "0:08"},
                    {"number": "03", "tag": "ANIMATION", "tag_desc": "Animated worlds", "prompt": '"A cozy animated short of a little robot sitting in a forest, with glowing fireflies, Pixar style, warm lighting."', "duration": "0:08"},
                    {"number": "04", "tag": "PRODUCTS", "tag_desc": "Stunning product ads", "prompt": '"A close-up product shot of a premium sneaker, rotating slowly, with dramatic studio lighting, black background, cinematic style."', "duration": "0:08"}
                ],
                "cta_button_text": "NEXT: A NEW ERA FOR CREATORS",
                "tagline_left": "IDEAS TO VIDEOS.<br>FASTER THAN EVER.",
                "layout_type": "comparison",
            },
            {
                "slide_number": 6,
                "category": "A NEW ERA",
                "headline_prefix": "WANT THE FULL",
                "headline_highlight": "RESOURCE PACK?",
                "headline": "WANT THE FULL RESOURCE PACK?",
                "body_text": f"I put together the complete free checklist, prompts & templates for {topic}.",
                "annotation": "Free for the community.",
                "benefits": [
                    {"icon": "⚡", "text": "Instant Actionable Prompts"},
                    {"icon": "∞", "text": "Save 10+ Hours of Trial & Error"},
                    {"icon": "👥", "text": "Tested by Top Creators"},
                    {"icon": "🚀", "text": "Immediate Real Results"}
                ],
                "dm_keyword": keyword,
                "dm_message": f"Hey! Here is your free {topic} resource pack: https://promptpulse.ai/toolkit - enjoy!",
                "cta_button_text": f"COMMENT \"{keyword}\" TO GET IT",
                "tagline_left": "BETTER TOOLS.<br>BRIGHTER IDEAS.",
                "layout_type": "cta",
            },
        ]


content_agent = ContentAgent()
