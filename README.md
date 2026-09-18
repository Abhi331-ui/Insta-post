# PromptPulse — Autonomous AI Instagram Content Agent

PromptPulse is a production-ready autonomous AI agent that discovers, strategizes, writes, designs, fact-checks, quality-assures, publishes, and analyzes high-retention 6-slide Instagram carousels every day.

### The Core Principle
> **DISCOVER something worth posting every day.  
> Do NOT just generate something every day.**  
> The agent is capable of stating: *"Nothing strong enough to post today. Continuing research."*

---

## System Architecture

```
promptpulse/
├── backend/
│   ├── main.py                    # FastAPI entrypoint, CORS, static media mount
│   ├── config.py                  # Pydantic settings & environment configuration
│   ├── database.py                # SQLAlchemy engine & session factory
│   ├── models/                    # PostgreSQL/SQLite models
│   │   ├── user.py                # User, InstagramAccount, BrandSetting, ContentPillar
│   │   ├── post.py                # Post, PostSlide, ScheduledPost, PublishingLog
│   │   ├── analytics.py           # Analytics metrics & engagement
│   │   ├── agent_run.py           # AgentRun & AIGeneration token audit
│   │   └── tool_database.py       # Verified AI tool catalog
│   ├── agents/                    # 10 Autonomous AI Agents
│   │   ├── research_agent.py      # Web search with Gemini Grounding
│   │   ├── trend_agent.py         # 7-criteria scoring & threshold filter
│   │   ├── strategy_agent.py      # Anti-repetition, 3 angles & 10 hooks
│   │   ├── content_agent.py       # 6-slide story narrative, caption & tags
│   │   ├── design_agent.py        # 1080x1350 PNG slide generator
│   │   ├── factcheck_agent.py     # Grounding claim verification & qualification
│   │   ├── qa_agent.py            # Dimensions, duplication, hook & CTA checks
│   │   ├── publishing_agent.py    # Meta Graph API carousel flow & idempotency
│   │   ├── analytics_agent.py     # 24h, 48h, 7d insights collection
│   │   └── learning_agent.py      # Weekly empirical strategy optimization
│   ├── pipeline/
│   │   └── daily_pipeline.py      # Sequential agent pipeline orchestrator
│   ├── services/
│   │   ├── ai_provider.py         # Gemini + OpenAI abstraction
│   │   ├── instagram.py           # Meta Graph API container publisher
│   │   ├── image_generator.py     # Jinja2 HTML → 1080x1350 PNG renderer
│   │   └── scheduler.py           # Post scheduling service
│   ├── api/                       # REST & SSE endpoints
│   │   ├── auth.py
│   │   ├── posts.py
│   │   ├── calendar.py
│   │   ├── analytics.py
│   │   ├── settings.py
│   │   └── agent.py
│   └── templates/slides/          # 6 HTML slide layouts (hero, tool_card, steps, comparison, workflow, cta)
├── frontend/                      # Next.js 14 + Tailwind CSS Dashboard
│   ├── app/
│   │   ├── dashboard/page.tsx     # Today's preview, Why-This-Post, Approval panel
│   │   ├── calendar/page.tsx      # Content calendar with pillar dots
│   │   ├── posts/page.tsx         # Filterable catalog & slide editor
│   │   ├── analytics/page.tsx     # Reach, saves, shares & learning recommendations
│   │   └── settings/page.tsx      # Meta OAuth, posting schedule & brand colors
│   └── components/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 10 Specialized AI Agents

1. **Research Agent**: Scans 5 daily categories (tool launches, new features, productivity workflows, model announcements, developer tools) using Gemini with Google Search Grounding.
2. **Trend Agent**: Evaluates 7 criteria (`freshness`, `usefulness`, `curiosity`, `save_potential`, `share_potential`, `visual_potential`, `audience_relevance`) and enforces a strict `>= 6.0` composite score threshold.
3. **Strategy Agent**: Enforces the *Why Today Test* and *One Big Idea Rule*, runs anti-repetition audits against the last 30 posts (tool recency, hook pattern, pillar run), generates 3 angles and 10 hook variations, with evergreen fallback.
4. **Content Agent**: Crafts an exact 6-slide story narrative:
   - Slide 1: Hook (`hero`)
   - Slide 2: Context (`tool_card`)
   - Slide 3: Discovery (`tool_card`)
   - Slide 4: How It Works (`steps`)
   - Slide 5: Value (`comparison` or `workflow`)
   - Slide 6: CTA (`cta`)
5. **Design Agent**: Renders each slide at high-resolution 1080×1350px PNG with PromptPulse cinematic dark brand identity (pure black `#000000`, purple→blue→pink gradient `linear-gradient(135deg, #7C3AED, #2563EB, #EC4899)`, white/gradient Inter 900 headlines, `#D1D5DB` body text, glassmorphism cards, neon cyan curves, slide counters, dot pagination, and faded atmospheric AI backgrounds).
6. **Fact-Check Agent**: Audits all claims against sources; removes unsubstantiated claims or softens with qualifiers ("reportedly", "according to [source]").
7. **QA Agent**: Enforces critical checks (exactly 6 slides, 1080×1350 dimensions, hook presence, CTA presence, duplication prevention) and triggers targeted single-slide regeneration on failures.
8. **Publishing Agent**: Official Meta Graph API 3-step carousel container flow with exponential backoff retry (30s, 60s, 120s) and strict idempotency guards.
9. **Analytics Agent**: Pulls post insights (reach, impressions, saves, shares, profile visits, follower growth) at 24h, 48h, and 7-day intervals.
10. **Learning Agent**: Weekly empirical synthesis of top-performing content pillars, hook patterns, and layouts to continually bias and refine future content strategy.

---

## Quickstart Guide

### Option 1: Local Development

#### 1. Backend Setup
```bash
# Clone and enter directory
cd "promptpulse"

# Install Python requirements
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY (optional for local testing; intelligent fallback included)

# Start FastAPI server
uvicorn backend.main:app --reload --port 8000
```
Backend API will be live at: `http://localhost:8000` (Interactive docs at `/docs`).

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be live at: `http://localhost:3000`.

---

### Option 2: Docker Compose (Full Stack with PostgreSQL & Redis)

```bash
docker compose up --build
```
Spins up:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Celery worker
- Celery beat scheduler
- Next.js frontend (port 3000)

---

## Meta Graph API / Instagram OAuth Setup

1. Navigate to [developers.facebook.com](https://developers.facebook.com) and create a **Business** app.
2. Add the **Instagram Graph API** product.
3. Configure the following permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_insights`
   - `pages_show_list`
   - `pages_read_engagement`
4. Set OAuth Redirect URI: `http://localhost:3000/settings/instagram/callback`.
5. Enter your `META_APP_ID` and `META_APP_SECRET` in `.env`.
6. Visit `/settings` on the PromptPulse dashboard and click **Connect Instagram via Meta**.
7. The app automatically exchanges the authorization code for a long-lived 60-day access token and enables automatic token refreshing.

---

## Slide Layout HTML Templates

All slide templates are located in `backend/templates/slides/`:
- `hero.html` — Full-bleed headline, accent pill, subtext
- `tool_card.html` — Tool specs, verification badges, feature list
- `steps.html` — Numbered 3-step process cards
- `comparison.html` — Two-column Before vs After breakdown
- `workflow.html` — Arrow-connected pipeline nodes
- `cta.html` — High-impact Save, Share, and Follow banner

---

## Verification & Testing

To run the automated test suite verifying all 6 slide layouts, QA checks, database initialization, and end-to-end pipeline execution:

```bash
python -m pytest backend/tests/test_pipeline.py -v
```
Output:
```
backend/tests/test_pipeline.py::test_database_init PASSED
backend/tests/test_pipeline.py::test_ai_provider_completion PASSED
backend/tests/test_pipeline.py::test_image_generation_all_layouts PASSED
backend/tests/test_pipeline.py::test_trend_scoring PASSED
backend/tests/test_pipeline.py::test_qa_agent PASSED
backend/tests/test_pipeline.py::test_full_pipeline_run PASSED
======================= 6 passed in 27s =======================
```
