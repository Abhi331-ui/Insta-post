"use client";

import { useState, useEffect } from "react";
import { Sparkles, X, Wand2, Check, ArrowRight, Layers, RefreshCw, ChevronRight, Zap, Flame, Wrench, Lightbulb, Copy } from "lucide-react";
import { draftSixSlots, createCustomSlidesPost } from "@/lib/api";

interface SixSlotStudioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  initialTopic?: string;
}

const HERO_VARIANTS = [
  { id: "hero_editorial", label: "Hero Editorial (Mockup + Pills)" },
  { id: "hero_terminal", label: "Hero Terminal (Dev CLI Matrix)" },
  { id: "hero_blueprint", label: "Hero Blueprint (Architectural)" },
  { id: "hero_badge", label: "Hero Badge (Breakthrough Stamp)" },
  { id: "hero_minimal_bold", label: "Hero Minimal (High Contrast)" },
  { id: "hero_grid_matrix", label: "Hero Matrix (Tech Grid)" },
];

const TONE_OPTIONS = [
  { id: "Technical Deep Dive", label: "⚡ Technical Deep Dive" },
  { id: "Viral Hype", label: "🔥 Viral Hype & Impact" },
  { id: "Step-by-Step Tutorial", label: "🛠️ Step-by-Step Tutorial" },
  { id: "Creator Breakdown", label: "💡 Creator Breakdown" },
];

const SLOT_META = [
  { num: 1, name: "Hero Hook", type: "Hero Discovery", desc: "Kicker, glowing highlight, 4 capability pills & mockup" },
  { num: 2, name: "Tool Concept", type: "Tool Card", desc: "Tool name, breakthrough badge & 4 capability points" },
  { num: 3, name: "Possibilities", type: "2x2 Showcase", desc: "4 visual cards with prompt quotes & flow bar" },
  { num: 4, name: "How It Works", type: "Steps & Mockup", desc: "4 actionable steps + workspace monitor mockup" },
  { num: 5, name: "Real Examples", type: "Comparison Rows", desc: "4 prompt-to-result rows with 0:08 play buttons" },
  { num: 6, name: "Lead Magnet", type: "Viral CTA", desc: "Resource pack card, 4 benefits & comment-to-DM trigger" },
];

export default function SixSlotStudioModal({
  isOpen,
  onClose,
  onSuccess,
  initialTopic = "",
}: SixSlotStudioModalProps) {
  const [topic, setTopic] = useState(initialTopic || "Cursor Composer");
  const [tone, setTone] = useState("Technical Deep Dive");
  const [activeSlot, setActiveSlot] = useState(1);
  const [isDrafting, setIsDrafting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // 6 Slots State
  const [slot1, setSlot1] = useState<any>({
    slide_number: 1,
    layout_type: "hero_editorial",
    category: "AI DISCOVERY",
    headline_prefix: "THE AI TOOL\nYOU'LL WISH",
    headline_highlight: "YOU KNEW EARLIER",
    body_text: "A new way to turn ideas into reality.",
    annotation: "Same Prompt Infinite Possibilities",
    feature_pills: [
      { icon: "⚡", title: "IDEA", desc: "Just a prompt" },
      { icon: "✦", title: "CREATE", desc: "In seconds" },
      { icon: "ılı", title: "ITERATE", desc: "Make it better" },
      { icon: "↗", title: "SHARE", desc: "Bring it to life" },
    ],
    prompt_preview: "Describe what you want to create...",
    cta_button_text: "DISCOVER WHAT'S NEXT",
  });

  const [slot2, setSlot2] = useState<any>({
    slide_number: 2,
    layout_type: "tool_card",
    category: "DEEP DIVE",
    eyebrow: "M E E T",
    tool_name_prefix: "Introducing",
    tool_name: "Cursor Composer",
    tool_badge: "Breakthrough",
    headline: "Meet Cursor Composer",
    body_text: "The most advanced system yet to turn imagination into reality.",
    annotation: "Not just fast. Superhuman.",
    features: [
      { icon: "bolt", label: "Multi-file Editing" },
      { icon: "target", label: "Codebase Indexing" },
      { icon: "shield", label: "Terminal Execution" },
      { icon: "sparkles", label: "Instant Iteration" },
    ],
    cta_button_text: "EXPLORE POSSIBILITIES",
  });

  const [slot3, setSlot3] = useState<any>({
    slide_number: 3,
    layout_type: "showcase",
    category: "REAL POSSIBILITIES",
    headline_prefix: "ONE PROMPT.",
    headline_highlight: "ENDLESS POSSIBILITIES.",
    body_text: "From ideas to stunning results — here's what you can create.",
    annotation: "Same tool. Different worlds.",
    grid_cards: [
      { tag: "CINEMATIC", title: "Full Stack Apps", prompt: '"Build a real-time multiplayer whiteboard with Next.js..."' },
      { tag: "WORKFLOW", title: "Agent Automations", prompt: '"Create a script that scrapes and summarizes tech news..."' },
      { tag: "REFACTOR", title: "Codebase Migrations", prompt: '"Refactor this Express backend to modern Fastify in TypeScript..."' },
      { tag: "UI/UX", title: "Glassmorphic UI", prompt: '"Build a dark-mode dashboard with glowing charts and metrics..."' },
    ],
    flow_steps: ["PROMPT", "CODE", "DEPLOY"],
    cta_button_text: "WHAT WILL YOU CREATE?",
  });

  const [slot4, setSlot4] = useState<any>({
    slide_number: 4,
    layout_type: "steps",
    category: "HOW IT WORKS",
    headline_prefix: "FROM PROMPT",
    headline_highlight: "TO MASTERPIECE.",
    body_text: "Create stunning results in just a few simple steps.",
    annotation: "Simple steps. Incredible results.",
    steps: [
      { title: "Define Your Goal", desc: "Describe the feature in plain English with context." },
      { title: "Review Multi-File Diffs", desc: "Inspect live changes across your entire repository." },
      { title: "Run & Validate", desc: "Execute terminal commands and automated checks." },
      { title: "Ship with Confidence", desc: "Deploy your tested production code in minutes." },
    ],
    mockup_prompt: "Build an autonomous AI agent with real-time SSE streaming",
    cta_button_text: "NEXT: SEE REAL EXAMPLES",
  });

  const [slot5, setSlot5] = useState<any>({
    slide_number: 5,
    layout_type: "comparison",
    category: "REAL EXAMPLES",
    headline_prefix: "SAME PROMPT.",
    headline_highlight: "INCREDIBLE RESULTS.",
    body_text: "Real prompts. Real results.",
    annotation: "Just a prompt. Look at the result.",
    rows: [
      { number: "01", tag: "FRONTEND", tag_desc: "Modern React", prompt: '"Build a full responsive navigation bar with glassmorphism."', duration: "0:08" },
      { number: "02", tag: "BACKEND", tag_desc: "FastAPI Pipeline", prompt: '"Create a background task runner with SSE progress streaming."', duration: "0:08" },
      { number: "03", tag: "DATABASE", tag_desc: "Schema & Migrations", prompt: '"Generate SQLAlchemy models with cascade deletes and indexes."', duration: "0:08" },
      { number: "04", tag: "DEPLOYMENT", tag_desc: "Production Ready", prompt: '"Configure Dockerfile with multi-stage build and caching."', duration: "0:08" },
    ],
    cta_button_text: "NEXT: A NEW ERA FOR CREATORS",
  });

  const [slot6, setSlot6] = useState<any>({
    slide_number: 6,
    layout_type: "cta",
    category: "A NEW ERA",
    headline_prefix: "WANT THE FULL",
    headline_highlight: "RESOURCE PACK?",
    body_text: "I put together the complete free checklist, prompts & templates for you.",
    annotation: "Free for the community.",
    benefits: [
      { icon: "⚡", text: "Instant Actionable Prompts & Rules" },
      { icon: "∞", text: "Save 10+ Hours of Trial & Error" },
      { icon: "👥", text: "Tested by Top Creators & Engineers" },
      { icon: "🚀", text: "Immediate Production Results" },
    ],
    dm_keyword: "CURSOR",
    dm_message: "Hey! Here is your free resource pack: https://promptpulse.ai/toolkit - enjoy!",
    cta_button_text: 'COMMENT "CURSOR" TO GET IT',
  });

  useEffect(() => {
    if (initialTopic) {
      setTopic(initialTopic);
      setSlot2((prev: any) => ({
        ...prev,
        tool_name: initialTopic,
        headline: `Meet ${initialTopic}`,
      }));
    }
  }, [initialTopic]);

  if (!isOpen) return null;

  const handleDraftAllWithAi = async () => {
    if (!topic.trim()) {
      setErrorMsg("Please enter a topic first.");
      return;
    }
    try {
      setIsDrafting(true);
      setErrorMsg("");
      const res = await draftSixSlots(topic.trim(), tone);
      if (res && res.slides && res.slides.length === 6) {
        setSlot1(res.slides[0]);
        setSlot2(res.slides[1]);
        setSlot3(res.slides[2]);
        setSlot4(res.slides[3]);
        setSlot5(res.slides[4]);
        setSlot6(res.slides[5]);
        setSuccessMsg(`AI successfully drafted all 6 slots for "${topic.trim()}"!`);
      }
    } catch (err: any) {
      setErrorMsg("AI Drafting failed: " + err.message);
    } finally {
      setIsDrafting(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setIsSubmitting(true);
      setErrorMsg("");
      setSuccessMsg("");

      const allSlides = [slot1, slot2, slot3, slot4, slot5, slot6];
      await createCustomSlidesPost({
        topic: topic.trim(),
        tone,
        slides: allSlides,
      });

      setSuccessMsg(`Custom 6-slot carousel created! Renders in background...`);
      setTimeout(() => {
        setIsSubmitting(false);
        onClose();
        if (onSuccess) onSuccess();
      }, 1500);
    } catch (err: any) {
      setIsSubmitting(false);
      setErrorMsg("Generation error: " + err.message);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/90 backdrop-blur-lg animate-fade-in overflow-y-auto">
      <div className="relative w-full max-w-4xl bg-[#080C16] border border-blue-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-blue-500/15 overflow-hidden my-6 max-h-[92vh] flex flex-col">
        {/* Glow ambient */}
        <div className="absolute -top-32 -right-32 w-80 h-80 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-80 h-80 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] relative z-10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-white tracking-tight">
                  6-Slot Slide Studio
                </h2>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  Granular Control
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Give prompts & define content for each of the 6 slides individually, or let AI draft them first.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Top Control Bar */}
        <div className="mt-4 p-4 rounded-2xl bg-[#0E1526] border border-slate-800 flex flex-col md:flex-row items-center gap-3 relative z-10 shrink-0">
          <div className="flex-1 w-full">
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
              Overall Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Cursor Composer, DeepSeek V3, Claude 3.5 Sonnet..."
              className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white placeholder:text-slate-500 outline-none focus:border-cyan-500"
            />
          </div>

          <div className="w-full md:w-52">
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
              Tone Style
            </label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-cyan-500"
            >
              {TONE_OPTIONS.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div className="w-full md:w-auto self-end">
            <button
              type="button"
              onClick={handleDraftAllWithAi}
              disabled={isDrafting || !topic.trim()}
              className="w-full md:w-auto flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:opacity-95 text-white text-xs font-bold shadow-md shadow-purple-600/30 active:scale-95 transition-all disabled:opacity-50 whitespace-nowrap"
            >
              <Wand2 className={`w-3.5 h-3.5 ${isDrafting ? "animate-spin" : ""}`} />
              {isDrafting ? "AI Drafting 6 Slots..." : "✦ AI Draft All 6 Slots"}
            </button>
          </div>
        </div>

        {/* Slot Selector Tabs */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 mt-4 relative z-10 shrink-0">
          {SLOT_META.map((s) => {
            const isActive = activeSlot === s.num;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => setActiveSlot(s.num)}
                className={`p-2.5 rounded-xl border text-left transition-all relative ${
                  isActive
                    ? "bg-cyan-950/40 border-cyan-500/70 text-cyan-200 shadow-lg shadow-cyan-950/50 scale-[1.02]"
                    : "bg-[#0E1526] border-slate-800 text-slate-400 hover:text-white hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono font-bold">
                  <span className={isActive ? "text-cyan-400" : "text-slate-500"}>0{s.num}</span>
                  <span className="text-[10px] text-slate-500">{s.type.split(" ")[0]}</span>
                </div>
                <div className="text-xs font-bold text-white mt-1 truncate">{s.name}</div>
              </button>
            );
          })}
        </div>

        {/* Active Slot Editor Area - Scrollable */}
        <div className="mt-4 p-5 rounded-2xl bg-[#0E1526] border border-slate-800 relative z-10 flex-1 overflow-y-auto pr-2">
          {/* SLOT 1: HERO HOOK */}
          {activeSlot === 1 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
                <div>
                  <h3 className="text-sm font-black text-white">Slot 1: The Hook (Hero Slide)</h3>
                  <p className="text-xs text-slate-400">Captivates users in feed with punchy headline, 4 pills, and search mockup.</p>
                </div>
                <div className="w-48">
                  <select
                    value={slot1.layout_type}
                    onChange={(e) => setSlot1({ ...slot1, layout_type: e.target.value })}
                    className="w-full bg-[#080C16] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-cyan-300 font-semibold"
                  >
                    {HERO_VARIANTS.map((h) => (
                      <option key={h.id} value={h.id}>{h.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Headline Prefix (Kicker)</label>
                  <input
                    type="text"
                    value={slot1.headline_prefix || ""}
                    onChange={(e) => setSlot1({ ...slot1, headline_prefix: e.target.value })}
                    placeholder="THE AI TOOL YOU'LL WISH"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Headline Highlight (Glowing Text)</label>
                  <input
                    type="text"
                    value={slot1.headline_highlight || ""}
                    onChange={(e) => setSlot1({ ...slot1, headline_highlight: e.target.value })}
                    placeholder="YOU KNEW EARLIER"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-cyan-300 font-bold"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Subheadline / Body Text</label>
                  <input
                    type="text"
                    value={slot1.body_text || ""}
                    onChange={(e) => setSlot1({ ...slot1, body_text: e.target.value })}
                    placeholder="A new way to turn ideas into reality."
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Cursive Annotation</label>
                  <input
                    type="text"
                    value={slot1.annotation || ""}
                    onChange={(e) => setSlot1({ ...slot1, annotation: e.target.value })}
                    placeholder="Same Prompt Infinite Possibilities"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-purple-300 italic"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">4 Capability Pills</label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {(slot1.feature_pills || []).map((p: any, idx: number) => (
                    <div key={idx} className="p-2 rounded-xl bg-[#080C16] border border-slate-800 flex flex-col gap-1">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs">{p.icon}</span>
                        <input
                          type="text"
                          value={p.title}
                          onChange={(e) => {
                            const newPills = [...slot1.feature_pills];
                            newPills[idx].title = e.target.value;
                            setSlot1({ ...slot1, feature_pills: newPills });
                          }}
                          className="w-full bg-transparent text-[11px] font-bold text-white outline-none"
                        />
                      </div>
                      <input
                        type="text"
                        value={p.desc}
                        onChange={(e) => {
                          const newPills = [...slot1.feature_pills];
                          newPills[idx].desc = e.target.value;
                          setSlot1({ ...slot1, feature_pills: newPills });
                        }}
                        className="w-full bg-transparent text-[10px] text-slate-400 outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SLOT 2: TOOL CARD */}
          {activeSlot === 2 && (
            <div className="flex flex-col gap-4">
              <div className="pb-2 border-b border-white/[0.06]">
                <h3 className="text-sm font-black text-white">Slot 2: The Tool Concept (Tool Card)</h3>
                <p className="text-xs text-slate-400">Deep dive on the core tool/concept with 4 capability badges.</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Prefix / Brand</label>
                  <input
                    type="text"
                    value={slot2.tool_name_prefix || ""}
                    onChange={(e) => setSlot2({ ...slot2, tool_name_prefix: e.target.value })}
                    placeholder="Introducing"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Core Tool Name</label>
                  <input
                    type="text"
                    value={slot2.tool_name || ""}
                    onChange={(e) => setSlot2({ ...slot2, tool_name: e.target.value, headline: `Meet ${e.target.value}` })}
                    placeholder="Cursor Composer"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-purple-300 font-bold"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Breakthrough Badge</label>
                  <input
                    type="text"
                    value={slot2.tool_badge || ""}
                    onChange={(e) => setSlot2({ ...slot2, tool_badge: e.target.value })}
                    placeholder="Breakthrough"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">Body Text Explanation</label>
                <input
                  type="text"
                  value={slot2.body_text || ""}
                  onChange={(e) => setSlot2({ ...slot2, body_text: e.target.value })}
                  placeholder="The most advanced system yet to turn imagination into reality."
                  className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">4 Feature Badges</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(slot2.features || []).map((f: any, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-[#080C16] border border-slate-800 flex items-center gap-2">
                      <span className="text-purple-400 font-bold">⚡</span>
                      <input
                        type="text"
                        value={f.label}
                        onChange={(e) => {
                          const newFeatures = [...slot2.features];
                          newFeatures[idx].label = e.target.value;
                          setSlot2({ ...slot2, features: newFeatures });
                        }}
                        className="w-full bg-transparent text-xs text-white outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SLOT 3: 2x2 SHOWCASE */}
          {activeSlot === 3 && (
            <div className="flex flex-col gap-4">
              <div className="pb-2 border-b border-white/[0.06]">
                <h3 className="text-sm font-black text-white">Slot 3: Real Possibilities (2x2 Grid)</h3>
                <p className="text-xs text-slate-400">4 diverse showcase cards with prompt quotes and 3-step flow bar.</p>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">4 Showcase Cards</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {(slot3.grid_cards || []).map((card: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-xl bg-[#080C16] border border-slate-800 flex flex-col gap-1.5">
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={card.tag}
                          onChange={(e) => {
                            const newCards = [...slot3.grid_cards];
                            newCards[idx].tag = e.target.value.toUpperCase();
                            setSlot3({ ...slot3, grid_cards: newCards });
                          }}
                          className="w-24 px-2 py-0.5 rounded bg-white/[0.05] text-[10px] font-bold text-cyan-300 uppercase outline-none"
                        />
                        <input
                          type="text"
                          value={card.title}
                          onChange={(e) => {
                            const newCards = [...slot3.grid_cards];
                            newCards[idx].title = e.target.value;
                            setSlot3({ ...slot3, grid_cards: newCards });
                          }}
                          className="w-full text-xs font-bold text-white bg-transparent outline-none"
                        />
                      </div>
                      <textarea
                        value={card.prompt}
                        rows={2}
                        onChange={(e) => {
                          const newCards = [...slot3.grid_cards];
                          newCards[idx].prompt = e.target.value;
                          setSlot3({ ...slot3, grid_cards: newCards });
                        }}
                        className="w-full bg-[#0E1526] border border-slate-800 rounded-lg p-1.5 text-[11px] text-slate-300 outline-none resize-none"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SLOT 4: HOW IT WORKS */}
          {activeSlot === 4 && (
            <div className="flex flex-col gap-4">
              <div className="pb-2 border-b border-white/[0.06]">
                <h3 className="text-sm font-black text-white">Slot 4: How It Works (Steps & Mockup)</h3>
                <p className="text-xs text-slate-400">4 progressive actionable steps + mockup prompt in workspace monitor.</p>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">4 Sequential Steps</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {(slot4.steps || []).map((st: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-xl bg-[#080C16] border border-slate-800 flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-purple-600/30 text-purple-300 text-[10px] font-bold flex items-center justify-center">
                          0{idx + 1}
                        </span>
                        <input
                          type="text"
                          value={st.title}
                          onChange={(e) => {
                            const newSteps = [...slot4.steps];
                            newSteps[idx].title = e.target.value;
                            setSlot4({ ...slot4, steps: newSteps });
                          }}
                          className="w-full text-xs font-bold text-white bg-transparent outline-none"
                        />
                      </div>
                      <input
                        type="text"
                        value={st.desc}
                        onChange={(e) => {
                          const newSteps = [...slot4.steps];
                          newSteps[idx].desc = e.target.value;
                          setSlot4({ ...slot4, steps: newSteps });
                        }}
                        className="w-full text-[11px] text-slate-400 bg-transparent outline-none pl-7"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Workspace Mockup Prompt <span className="text-slate-500 text-[10px]">(Text displayed inside glowing monitor)</span>
                </label>
                <input
                  type="text"
                  value={slot4.mockup_prompt || ""}
                  onChange={(e) => setSlot4({ ...slot4, mockup_prompt: e.target.value })}
                  placeholder="A peaceful workspace utilizing Cursor Composer for high productivity"
                  className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-cyan-300 font-mono"
                />
              </div>
            </div>
          )}

          {/* SLOT 5: REAL EXAMPLES */}
          {activeSlot === 5 && (
            <div className="flex flex-col gap-4">
              <div className="pb-2 border-b border-white/[0.06]">
                <h3 className="text-sm font-black text-white">Slot 5: Real Examples (Prompt Rows)</h3>
                <p className="text-xs text-slate-400">4 horizontal prompt-to-result rows with 0:08 video play buttons.</p>
              </div>

              <div className="flex flex-col gap-2.5">
                {(slot5.rows || []).map((r: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#080C16] border border-slate-800 flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-purple-400 shrink-0">{r.number}</span>
                    <input
                      type="text"
                      value={r.tag}
                      onChange={(e) => {
                        const newRows = [...slot5.rows];
                        newRows[idx].tag = e.target.value.toUpperCase();
                        setSlot5({ ...slot5, rows: newRows });
                      }}
                      className="w-24 px-2 py-0.5 rounded bg-white/[0.05] text-[10px] font-bold text-cyan-300 uppercase outline-none shrink-0"
                    />
                    <input
                      type="text"
                      value={r.prompt}
                      onChange={(e) => {
                        const newRows = [...slot5.rows];
                        newRows[idx].prompt = e.target.value;
                        setSlot5({ ...slot5, rows: newRows });
                      }}
                      className="w-full text-xs text-slate-200 bg-transparent outline-none"
                    />
                    <span className="text-[10px] font-mono text-slate-500 shrink-0">0:08</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SLOT 6: LEAD MAGNET CTA */}
          {activeSlot === 6 && (
            <div className="flex flex-col gap-4">
              <div className="pb-2 border-b border-white/[0.06]">
                <h3 className="text-sm font-black text-white">Slot 6: Lead Magnet CTA (Comment-to-DM)</h3>
                <p className="text-xs text-slate-400">Full resource pack card, 4 benefits, and comment trigger keyword.</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                    Comment-to-DM Trigger Keyword
                  </label>
                  <input
                    type="text"
                    value={slot6.dm_keyword || ""}
                    onChange={(e) => {
                      const kw = e.target.value.toUpperCase();
                      setSlot6({
                        ...slot6,
                        dm_keyword: kw,
                        cta_button_text: `COMMENT "${kw}" TO GET IT`,
                      });
                    }}
                    placeholder="CURSOR"
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono font-bold text-cyan-300 uppercase"
                  />
                  <p className="text-[10px] text-cyan-400 mt-1">CTA: {slot6.cta_button_text}</p>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                    Subheadline / Offer Copy
                  </label>
                  <input
                    type="text"
                    value={slot6.body_text || ""}
                    onChange={(e) => setSlot6({ ...slot6, body_text: e.target.value })}
                    placeholder="I put together the complete free checklist, prompts & templates for you."
                    className="w-full bg-[#080C16] border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">4 Resource Pack Benefits</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(slot6.benefits || []).map((b: any, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-[#080C16] border border-slate-800 flex items-center gap-2">
                      <span className="text-purple-400 font-bold">{b.icon || "✦"}</span>
                      <input
                        type="text"
                        value={b.text}
                        onChange={(e) => {
                          const newB = [...slot6.benefits];
                          newB[idx].text = e.target.value;
                          setSlot6({ ...slot6, benefits: newB });
                        }}
                        className="w-full bg-transparent text-xs text-white outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        {errorMsg && (
          <div className="mt-3 p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-medium shrink-0">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="mt-3 p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium flex items-center gap-2 shrink-0">
            <Check className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-white/[0.08] mt-3 relative z-10 shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-500">Currently Editing:</span>
            <span className="text-xs font-bold text-cyan-300">
              Slide 0{activeSlot} ({SLOT_META[activeSlot - 1].name})
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isSubmitting || !topic.trim()}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 hover:opacity-95 text-white text-xs font-bold shadow-lg shadow-cyan-500/25 active:scale-95 transition-all disabled:opacity-50"
            >
              <Wand2 className={`w-3.5 h-3.5 ${isSubmitting ? "animate-spin" : ""}`} />
              {isSubmitting ? "Generating All 6 Slides..." : "✦ Generate 6-Slide Carousel"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
