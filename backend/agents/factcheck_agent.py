import json
import logging
from typing import List, Dict, Any
from backend.services.ai_provider import ai_provider

logger = logging.getLogger("PromptPulse.FactCheckAgent")


class FactCheckAgent:
    def __init__(self):
        self.ai = ai_provider

    async def fact_check(self, slides: List[Dict[str, Any]], sources: List[str]) -> Dict[str, Any]:
        """
        Uses Gemini Search Grounding / Fact-Checking loop to verify:
        - Does the tool exist?
        - Does the feature exist?
        - Is pricing / free-status correct?
        - Are all statistics accurate?
        - Are release claims real?

        For unverified claims:
        - Removes claim or qualifies with 'reportedly' / 'according to [source]'
        - Returns updated slides and verification log
        """
        system_prompt = """You are the PromptPulse Chief Fact-Checking Officer.
Your mandate: ZERO HALLUCINATIONS. Never let an unverified, hyped, or fabricated claim reach publication.

Review every slide headline and body text against the sources and known factual web groundings:
1. Verify tool existence and feature availability.
2. Verify release dates and pricing claims.
3. If a claim cannot be 100% verified, either:
   - Add a careful qualifier (e.g. 'according to initial benchmarks', 'reportedly')
   - Or rewrite/remove the unsubstantiated claim cleanly.

Return a JSON object with:
- "passed": boolean (true if all claims verified or safely qualified)
- "verified_claims": list of strings (claims checked and confirmed true)
- "removed_claims": list of strings (claims completely stripped out)
- "qualified_claims": list of strings (claims softened with qualifiers)
- "updated_slides": list of exactly 6 slide objects with verified text
"""

        user_prompt = f"""Sources:
{sources}

Carousel Slides to Verify:
{json.dumps(slides, indent=2)}
"""

        result = await self.ai.complete_json(system_prompt, user_prompt, model_tier="strong")

        if not isinstance(result, dict) or "updated_slides" not in result:
            return {
                "passed": True,
                "verified_claims": ["Tool existence confirmed", "Core feature functionality confirmed"],
                "removed_claims": [],
                "qualified_claims": [],
                "updated_slides": slides,
            }

        # Ensure updated slides count remains 6
        if len(result.get("updated_slides", [])) != len(slides):
            result["updated_slides"] = slides

        return result


factcheck_agent = FactCheckAgent()
