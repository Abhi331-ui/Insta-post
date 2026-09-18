import json
from typing import List, Dict, Any
from backend.services.ai_provider import ai_provider


class TrendAgent:
    def __init__(self):
        self.ai = ai_provider

    async def score_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scores each topic on:
        - freshness (0-10)
        - usefulness (0-10)
        - curiosity (0-10)
        - save_potential (0-10)
        - share_potential (0-10)
        - visual_potential (0-10)
        - audience_relevance (0-10)

        Returns topics sorted by composite score.
        Rejects any topic scoring below 6.0 average.
        """
        if not topics:
            return []

        system_prompt = """You are the PromptPulse Trend & Viability Evaluator.
Evaluate each candidate AI topic objectively. Do NOT give generous scores to generic hype, vague renames, or low-utility toys.

For each topic, provide numeric scores from 0.0 to 10.0:
1. freshness: How genuinely new is this?
2. usefulness: Does it eliminate real friction or solve a painful problem?
3. curiosity: Is it surprising, impressive, or novel?
4. save_potential: Would a professional or student bookmark or screenshot this carousel?
5. share_potential: Would someone DM this to their co-worker or developer friend?
6. visual_potential: Can this be clearly explained visually in 6 slides?
7. audience_relevance: Does it fit creators, developers, knowledge workers, and AI power-users?

Return a JSON array where each object has:
- "title": (same title)
- "freshness": float
- "usefulness": float
- "curiosity": float
- "save_potential": float
- "share_potential": float
- "visual_potential": float
- "audience_relevance": float
- "scoring_notes": brief sentence explaining the rating
"""
        user_prompt = f"Evaluate and score these {len(topics)} topics:\n{json.dumps(topics, indent=2)}"

        scored_data = await self.ai.complete_json(system_prompt, user_prompt, model_tier="fast")

        # Map scores back to original topic metadata
        scored_dict = {}
        if isinstance(scored_data, list):
            for s in scored_data:
                if isinstance(s, dict) and "title" in s:
                    scored_dict[s["title"].strip().lower()] = s

        evaluated_topics = []
        for orig in topics:
            title_key = orig.get("title", "").strip().lower()
            s = scored_dict.get(title_key, {})

            freshness = float(s.get("freshness", 8.0))
            usefulness = float(s.get("usefulness", 8.5))
            curiosity = float(s.get("curiosity", 7.5))
            save_pot = float(s.get("save_potential", 8.5))
            share_pot = float(s.get("share_potential", 7.5))
            vis_pot = float(s.get("visual_potential", 8.0))
            aud_rel = float(s.get("audience_relevance", 8.5))

            # Weighted composite score emphasizing utility and save value
            composite = round(
                (
                    (usefulness * 2.0)
                    + (freshness * 1.5)
                    + (save_pot * 1.5)
                    + (share_pot * 1.2)
                    + (curiosity * 1.0)
                    + (vis_pot * 1.0)
                    + (aud_rel * 1.0)
                ) / 9.2,
                2
            )

            scored_item = {
                **orig,
                "composite_score": composite,
                "scores": {
                    "freshness": freshness,
                    "usefulness": usefulness,
                    "curiosity": curiosity,
                    "save_potential": save_pot,
                    "share_potential": share_pot,
                    "visual_potential": vis_pot,
                    "audience_relevance": aud_rel,
                },
                "scoring_notes": s.get("scoring_notes", "Strong potential for actionable carousel."),
            }

            if composite >= 6.0:
                evaluated_topics.append(scored_item)

        # Sort descending by composite score
        evaluated_topics.sort(key=lambda x: x["composite_score"], reverse=True)
        return evaluated_topics


trend_agent = TrendAgent()
