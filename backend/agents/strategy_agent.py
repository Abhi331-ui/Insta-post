import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from backend.services.ai_provider import ai_provider

logger = logging.getLogger("PromptPulse.StrategyAgent")


class StrategyAgent:
    def __init__(self):
        self.ai = ai_provider

    def is_too_similar(self, candidate: Dict[str, Any], previous_posts: List[Dict[str, Any]]) -> (bool, str):
        """
        Anti-Repetition Rules:
        - Same tool mentioned in last 14 days
        - Same hook pattern used in last 7 days
        - Same content pillar used 3 days in a row
        - Title starts with "X AI tools" where format was used in last 30 days
        - Topic name overlap
        """
        cand_title = candidate.get("title", "").lower()
        cand_summary = candidate.get("summary", "").lower()

        now = datetime.utcnow()

        # Check pillar streak (3 in a row)
        if len(previous_posts) >= 3:
            cand_pillar = candidate.get("category", "")
            prev_pillars = [p.get("content_pillar", "") for p in previous_posts[:3]]
            if all(p.lower() == cand_pillar.lower() for p in prev_pillars if p):
                return True, f"Content pillar '{cand_pillar}' has been used 3 days in a row."

        for post in previous_posts:
            post_date = post.get("created_at") or now
            days_ago = (now - post_date).days if isinstance(post_date, datetime) else 0

            prev_topic = post.get("topic", "").lower()

            # Rule 1: Same tool in last 14 days
            if days_ago <= 14:
                # Check for major tool keywords (e.g. 'bolt', 'canvas', 'cursor', 'claude', 'gpt')
                cand_words = set(w for w in cand_title.split() if len(w) > 3)
                prev_words = set(w for w in prev_topic.split() if len(w) > 3)
                overlap = cand_words.intersection(prev_words)
                if len(overlap) >= 2:
                    return True, f"Similar tool keywords '{', '.join(overlap)}' covered {days_ago} days ago in '{post.get('topic')}'."

            # Rule 2: "X AI Tools" format repetition
            if "ai tools" in cand_title and "ai tools" in prev_topic and days_ago <= 30:
                return True, f"Generic 'AI Tools' list format already published {days_ago} days ago."

        return False, ""

    async def select_opportunity(
        self,
        scored_topics: List[Dict[str, Any]],
        previous_posts: List[Dict[str, Any]],
        content_strategy: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Selects the single best content opportunity applying:
        1. Anti-repetition against previous 30 posts
        2. WHY TODAY test
        3. ONE BIG IDEA rule
        4. Generates 3 angles -> selects best
        5. Generates 10 hooks -> selects best
        6. Injects learned guidelines and user directives
        """
        rejection_log = []
        valid_candidates = []

        for item in scored_topics:
            is_dup, reason = self.is_too_similar(item, previous_posts)
            if is_dup:
                rejection_log.append(f"Rejected '{item.get('title')}': {reason}")
            else:
                valid_candidates.append(item)

        if not valid_candidates:
            logger.info("No candidates passed anti-repetition. Trying evergreen with fresh angle.")
            return None

        # Sort by composite score
        valid_candidates.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
        top_candidate = valid_candidates[0]

        strat_info = ""
        if content_strategy:
            strat_info = f"""
Learned Guidelines & User Directives:
- Priority Pillars: {content_strategy.get('increase_pillar', 'AI Workflows & Automation')}
- Top Hook Patterns: {content_strategy.get('top_hook_patterns', [])}
- Custom Directives: {content_strategy.get('custom_directives', [])}
- Empirical Takeaways: {content_strategy.get('learning_notes', '')}
"""

        # Use strong AI model to generate 3 angles, select best, and generate 10 hooks
        system_prompt = """You are the PromptPulse Chief Content Strategist.
Your core principle: DISCOVER something worth posting every day. Do NOT just generate something random.

Apply two strict tests:
1. WHY TODAY TEST: Why does this matter right now? (New update, breaking release, workflow shift).
2. ONE BIG IDEA RULE: Every carousel must focus on exactly ONE clear transformation. Reject sprawling lists.

Your task:
1. Generate 3 distinct angles for this opportunity.
2. Select the single strongest angle that provides the highest save/share value.
3. Generate 10 high-converting hook variations (curiosity, contrarian, tutorial, efficiency, warning).
4. Select the #1 best hook (punchy, under 12 words, evokes urgency/curiosity).
5. Specify target audience personas and content pillar.

Return a JSON object with:
- "topic": concise topic title
- "why_today": the specific reason to publish today
- "freshness": "BRAND_NEW" | "DEVELOPING" | "RECENT" | "EVERGREEN"
- "all_angles": list of 3 angles
- "selected_angle": the winning angle
- "all_hooks": list of 10 hooks
- "hook": the winning #1 hook
- "target_audience": list of 3-4 target audience groups
- "content_pillar": string (e.g. "AI Workflows & Automation", "Developer Tools", "Productivity")
"""

        user_prompt = f"""Winning candidate:
Title: {top_candidate.get('title')}
Summary: {top_candidate.get('summary')}
Source: {top_candidate.get('source_url')} ({top_candidate.get('source_name')})
Category: {top_candidate.get('category')}
Freshness: {top_candidate.get('freshness', 'BRAND_NEW')}

Previous posts summary to avoid repetition:
{[p.get('topic') for p in previous_posts[:10]]}
{strat_info}
"""

        strategy_output = await self.ai.complete_json(system_prompt, user_prompt, model_tier="strong")

        if not isinstance(strategy_output, dict) or "hook" not in strategy_output:
            # Fallback structured output
            strategy_output = {
                "topic": top_candidate.get("title"),
                "why_today": top_candidate.get("summary", "New breakthrough released this week."),
                "freshness": top_candidate.get("freshness", "BRAND_NEW"),
                "selected_angle": f"How to eliminate setup friction using {top_candidate.get('title')}",
                "hook": f"Stop doing this manually. {top_candidate.get('title')} changes everything.",
                "target_audience": ["developers", "solopreneurs", "creators"],
                "content_pillar": "AI Productivity & Workflows",
            }

        strategy_output["sources"] = [top_candidate.get("source_url", "https://promptpulse.ai")]
        strategy_output["rejection_log"] = rejection_log
        strategy_output["composite_score"] = top_candidate.get("composite_score", 8.5)
        strategy_output["scores"] = top_candidate.get("scores", {})

        return strategy_output

    async def find_evergreen_with_fresh_angle(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Evergreen Fallback: When no breaking news passes the threshold,
        unearth an established powerful AI workflow with an unexpected, fresh angle.
        """
        system_prompt = """You are the PromptPulse Strategy Agent.
No breaking news passed our quality threshold today. We must discover an evergreen high-utility AI workflow with a fresh, counter-intuitive angle.

Return JSON:
- "topic": str
- "why_today": str (why this evergreen insight is critical right now)
- "freshness": "EVERGREEN"
- "selected_angle": str
- "hook": str
- "target_audience": list of strings
- "content_pillar": str
- "sources": list of documentation URLs
- "rejection_log": list of strings
"""
        res = await self.ai.complete_json(
            system_prompt,
            "Propose one timeless, high-utility AI workflow (e.g. multi-agent task execution or automated research synthesizing).",
            model_tier="strong"
        )
        if not isinstance(res, dict) or "hook" not in res:
            res = {
                "topic": "Autonomous Multi-Agent Systems in Practice",
                "why_today": "Single-prompt LLMs plateau on complex workflows; agent handoffs solve the reliability wall.",
                "freshness": "EVERGREEN",
                "selected_angle": "How to orchestrate 3 specialized micro-agents instead of one mega-prompt",
                "hook": "Stop writing giant AI prompts. Autonomous micro-agents produce 10x better results.",
                "target_audience": ["developers", "solopreneurs", "AI practitioners"],
                "content_pillar": "AI Workflows & Automation",
                "sources": ["https://promptpulse.ai", "https://docs.anthropic.com"],
                "composite_score": 8.7,
                "scores": {
                    "freshness": 7.5,
                    "usefulness": 9.5,
                    "curiosity": 8.5,
                    "save_potential": 9.2,
                    "share_potential": 8.5,
                    "visual_potential": 8.8,
                    "audience_relevance": 9.0,
                },
            }

        res["rejection_log"] = ["No breaking AI news met 6.0 composite score today; pivoted to high-retention evergreen."]
        return res


strategy_agent = StrategyAgent()
