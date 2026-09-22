"use client";

import { useState, useEffect } from "react";
import { Sparkles, X, Wand2, Check, ArrowRight, Layers, FileText, Zap, Flame, Wrench, Lightbulb, ChevronDown, ChevronUp } from "lucide-react";
import { createManualPost } from "@/lib/api";

interface CreateCarouselModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  initialTopic?: string;
}

const PRESET_CATEGORIES = [
  { id: "all", label: "All Topics" },
  { id: "models", label: "🤖 AI Models" },
  { id: "dev", label: "💻 Dev Tools" },
  { id: "workflows", label: "⚙️ Workflows" },
  { id: "growth", label: "📈 Growth & SaaS" },
];

const TOPIC_PRESETS = [
  { label: "Google Veo 3", icon: "⚡", category: "models", defaultTone: "Viral Hype", defaultKw: "VEO" },
  { label: "Claude 3.5 Sonnet", icon: "✦", category: "models", defaultTone: "Technical Deep Dive", defaultKw: "CLAUDE" },
  { label: "OpenAI Canvas", icon: "💎", category: "models", defaultTone: "Step-by-Step Tutorial", defaultKw: "CANVAS" },
  { label: "Midjourney v6.1", icon: "🎨", category: "models", defaultTone: "Viral Hype", defaultKw: "PROMPT" },
  { label: "Cursor Composer", icon: "🚀", category: "dev", defaultTone: "Technical Deep Dive", defaultKw: "CURSOR" },
  { label: "Bolt.new Full-Stack", icon: "🔥", category: "dev", defaultTone: "Step-by-Step Tutorial", defaultKw: "BOLT" },
  { label: "v0 by Vercel", icon: "🛠️", category: "dev", defaultTone: "Technical Deep Dive", defaultKw: "VERCEL" },
  { label: "Claude Code CLI", icon: "💻", category: "dev", defaultTone: "Technical Deep Dive", defaultKw: "CLI" },
  { label: "Multi-Agent Systems", icon: "🤖", category: "workflows", defaultTone: "Creator Breakdown", defaultKw: "AGENTS" },
  { label: "Local LLMs with Ollama", icon: "🦙", category: "workflows", defaultTone: "Technical Deep Dive", defaultKw: "OLLAMA" },
  { label: "AI Video Production", icon: "🎬", category: "growth", defaultTone: "Viral Hype", defaultKw: "VIDEO" },
  { label: "Comment-to-DM Funnel", icon: "📈", category: "growth", defaultTone: "Creator Breakdown", defaultKw: "SCALE" },
];

const TONE_OPTIONS = [
  {
    id: "Technical Deep Dive",
    label: "Technical Deep Dive",
    desc: "Architecture, engineering, benchmarks & code",
    icon: Zap,
    color: "text-cyan-400 border-cyan-500/40 bg-cyan-950/20",
  },
  {
    id: "Viral Hype",
    label: "Viral Hype & Impact",
    desc: "Mindblowing capabilities & future of tech",
    icon: Flame,
    color: "text-rose-400 border-rose-500/40 bg-rose-950/20",
  },
  {
    id: "Step-by-Step Tutorial",
    label: "Step-by-Step Tutorial",
    desc: "Actionable how-to & practical prompt recipes",
    icon: Wrench,
    color: "text-amber-400 border-amber-500/40 bg-amber-950/20",
  },
  {
    id: "Creator Breakdown",
    label: "Creator Breakdown",
    desc: "ROI, workflows, efficiency & monetization",
    icon: Lightbulb,
    color: "text-purple-400 border-purple-500/40 bg-purple-950/20",
  },
];

const CONTENT_PILLARS = [
  "AI Workflows & Automation",
  "New Model & Tool Launches",
  "Developer & Engineering Tools",
  "Productivity Experiments",
];

const AUDIENCE_OPTIONS = [
  "Creators",
  "Developers",
  "Founders",
  "Marketers",
  "AI Power-Users",
];

export default function CreateCarouselModal({
  isOpen,
  onClose,
  onSuccess,
  initialTopic = "",
}: CreateCarouselModalProps) {
  const [topic, setTopic] = useState(initialTopic);
  const [hook, setHook] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedTone, setSelectedTone] = useState("Technical Deep Dive");
  const [dmKeyword, setDmKeyword] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [selectedPillar, setSelectedPillar] = useState(CONTENT_PILLARS[0]);
  const [selectedAudiences, setSelectedAudiences] = useState<string[]>([
    "Creators",
    "AI Power-Users",
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    if (initialTopic) {
      setTopic(initialTopic);
    }
  }, [initialTopic]);

  if (!isOpen) return null;

  const toggleAudience = (aud: string) => {
    setSelectedAudiences((prev) =>
      prev.includes(aud) ? prev.filter((a) => a !== aud) : [...prev, aud]
    );
  };

  const selectPreset = (preset: typeof TOPIC_PRESETS[0]) => {
    setTopic(preset.label);
    setSelectedTone(preset.defaultTone);
    if (!dmKeyword || dmKeyword === "VEO") {
      setDmKeyword(preset.defaultKw);
    }
  };

  const filteredPresets = activeCategory === "all"
    ? TOPIC_PRESETS
    : TOPIC_PRESETS.filter((p) => p.category === activeCategory);

  const effectiveDmKeyword = dmKeyword.trim().toUpperCase() || (
    topic ? topic.split(" ").filter(w => !/^\d+$/.test(w)).pop()?.toUpperCase() || "GUIDE" : "GUIDE"
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      setErrorMsg("Please enter a topic or select one of the presets.");
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMsg("");
      setSuccessMsg("");

      await createManualPost(
        topic.trim(),
        selectedPillar,
        selectedAudiences.length > 0 ? selectedAudiences : undefined,
        {
          notes: notes.trim() || undefined,
          hook: hook.trim() || undefined,
          tone: selectedTone,
          dm_keyword: dmKeyword.trim().toUpperCase() || undefined,
        }
      );

      setSuccessMsg(
        `Autonomous pipeline initiated for "${topic.trim()}". Generating 6-slide cosmic-neon carousel...`
      );

      setTimeout(() => {
        setIsSubmitting(false);
        onClose();
        if (onSuccess) onSuccess();
      }, 1500);
    } catch (err: any) {
      setIsSubmitting(false);
      setErrorMsg(err.message || "Failed to trigger carousel generation.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in overflow-y-auto">
      <div className="relative w-full max-w-2xl bg-[#090D16] border border-blue-500/30 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-blue-500/10 overflow-hidden my-8 max-h-[90vh] flex flex-col">
        {/* Ambient background glows */}
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] relative z-10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-600/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-black text-white tracking-tight">
                Carousel Creation Studio
              </h2>
              <p className="text-xs text-slate-400">
                Generate a 6-slide cosmic-neon carousel customized to your exact requirements.
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

        {/* Form Body - Scrollable */}
        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5 relative z-10 overflow-y-auto pr-1">
          {/* Topic Presets Categories */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Topic Presets & Inspiration
              </label>
              <span className="text-[11px] text-slate-500">1-click select</span>
            </div>

            <div className="flex gap-1.5 overflow-x-auto pb-1.5 scrollbar-none">
              {PRESET_CATEGORIES.map((cat) => (
                <button
                  type="button"
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                    activeCategory === cat.id
                      ? "bg-purple-600/30 text-purple-300 border border-purple-500/50"
                      : "bg-white/[0.03] text-slate-400 hover:text-white border border-white/[0.06]"
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            <div className="flex flex-wrap gap-1.5 mt-2">
              {filteredPresets.map((s) => (
                <button
                  type="button"
                  key={s.label}
                  onClick={() => selectPreset(s)}
                  className={`px-2.5 py-1 rounded-lg text-xs border transition-all flex items-center gap-1.5 active:scale-95 ${
                    topic === s.label
                      ? "bg-blue-600/30 border-blue-500 text-white shadow-md shadow-blue-600/20"
                      : "bg-white/[0.03] hover:bg-white/[0.08] border-white/[0.08] text-slate-300 hover:text-white"
                  }`}
                >
                  <span>{s.icon}</span>
                  <span>{s.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Topic Input */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Topic or Tool Name <span className="text-purple-400">*</span>
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Cursor Composer, Google Veo 3, Claude 3.5 Sonnet, Bolt.new..."
              className="w-full bg-[#0F172A] border border-slate-700/80 focus:border-blue-500 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-500 outline-none transition-all shadow-inner"
              disabled={isSubmitting}
              autoFocus
            />
          </div>

          {/* Tone Selector */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              Carousel Tone & Style
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {TONE_OPTIONS.map((t) => {
                const Icon = t.icon;
                const isSelected = selectedTone === t.id;
                return (
                  <button
                    type="button"
                    key={t.id}
                    onClick={() => setSelectedTone(t.id)}
                    className={`p-3 rounded-xl border text-left transition-all flex items-start gap-2.5 ${
                      isSelected
                        ? `${t.color} shadow-lg`
                        : "bg-[#0F172A] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                    }`}
                  >
                    <Icon className="w-4 h-4 mt-0.5 shrink-0" />
                    <div>
                      <div className="text-xs font-bold text-white flex items-center justify-between">
                        <span>{t.label}</span>
                        {isSelected && <Check className="w-3.5 h-3.5 text-current" />}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{t.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Toggle Advanced / Detailed Mode */}
          <div className="border border-white/[0.08] rounded-2xl bg-[#0F172A]/60 overflow-hidden">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full px-4 py-3 flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-300 hover:text-white transition-colors"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-purple-400" />
                <span>Custom Notes, Hook & Lead Magnet Keyword</span>
                <span className="text-[10px] lowercase font-normal px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {showAdvanced ? "hide" : "expand for exact control"}
                </span>
              </div>
              {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showAdvanced && (
              <div className="p-4 pt-2 border-t border-white/[0.06] flex flex-col gap-4">
                {/* Notes / Must-Include Features */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Key Features / Notes to Highlight <span className="text-slate-500 text-[11px]">(Optional)</span>
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={3}
                    placeholder="e.g. Highlight multi-file editing, custom .cursorrules, index codebase speed, and compare against Copilot..."
                    className="w-full bg-[#090D16] border border-slate-700/80 focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder:text-slate-500 outline-none transition-all resize-none shadow-inner"
                    disabled={isSubmitting}
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    The agent will extract and inject these points into the 4 features, steps, and examples across the slides.
                  </p>
                </div>

                {/* Custom Hook */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Custom Hook / Headline Angle <span className="text-slate-500 text-[11px]">(Optional)</span>
                  </label>
                  <input
                    type="text"
                    value={hook}
                    onChange={(e) => setHook(e.target.value)}
                    placeholder="e.g. The IDE feature nobody is talking about..."
                    className="w-full bg-[#090D16] border border-slate-700/80 focus:border-purple-500 rounded-xl px-3.5 py-2 text-xs text-white placeholder:text-slate-500 outline-none transition-all shadow-inner"
                    disabled={isSubmitting}
                  />
                </div>

                {/* Custom DM Keyword */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-semibold text-slate-300">
                      Lead Magnet Trigger Keyword <span className="text-slate-500 text-[11px]">(Slide 6 CTA)</span>
                    </label>
                    <span className="text-[11px] text-cyan-400 font-mono">
                      Preview: COMMENT "{effectiveDmKeyword}" TO GET IT
                    </span>
                  </div>
                  <input
                    type="text"
                    value={dmKeyword}
                    onChange={(e) => setDmKeyword(e.target.value.toUpperCase())}
                    placeholder={effectiveDmKeyword}
                    className="w-full bg-[#090D16] border border-slate-700/80 focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-white placeholder:text-slate-500 outline-none uppercase font-mono tracking-wider transition-all shadow-inner"
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Content Pillar & Audience */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Content Pillar
              </label>
              <select
                value={selectedPillar}
                onChange={(e) => setSelectedPillar(e.target.value)}
                className="w-full bg-[#0F172A] border border-slate-700/80 rounded-xl px-3 py-2.5 text-xs text-white outline-none focus:border-blue-500"
              >
                {CONTENT_PILLARS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Target Audience
              </label>
              <div className="flex flex-wrap gap-1.5">
                {AUDIENCE_OPTIONS.map((aud) => {
                  const isSelected = selectedAudiences.includes(aud);
                  return (
                    <button
                      type="button"
                      key={aud}
                      onClick={() => toggleAudience(aud)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all ${
                        isSelected
                          ? "bg-blue-600/20 border-blue-500/60 text-blue-300"
                          : "bg-white/[0.03] border-white/[0.08] text-slate-400 hover:text-white"
                      }`}
                    >
                      {aud}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* 6-Slide Architecture Preview */}
          <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex flex-col gap-2">
            <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>6-Slide Cosmic-Neon Story Arc</span>
              <span className="text-cyan-400 font-mono">1080×1350 HD</span>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 text-center">
              {[
                { num: "01", name: "Hook", type: "Hero Discovery" },
                { num: "02", name: "Tool", type: "Concept Card" },
                { num: "03", name: "Showcase", type: "2x2 Possibilities" },
                { num: "04", name: "Steps", type: "Workspace UI" },
                { num: "05", name: "Examples", type: "Prompt Rows" },
                { num: "06", name: "CTA", type: "Lead Magnet" },
              ].map((s) => (
                <div key={s.num} className="bg-[#0F172A] border border-slate-800 rounded-lg p-1.5">
                  <div className="text-[10px] font-mono text-purple-400 font-bold">{s.num}</div>
                  <div className="text-[11px] font-bold text-white truncate">{s.name}</div>
                  <div className="text-[9px] text-slate-500 truncate">{s.type}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Messages */}
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-medium">
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium flex items-center gap-2">
              <Check className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/[0.08] shrink-0">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/[0.04] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:opacity-95 text-white text-xs font-bold shadow-lg shadow-purple-600/25 active:scale-95 transition-all disabled:opacity-50"
            >
              <Wand2 className={`w-3.5 h-3.5 ${isSubmitting ? "animate-spin" : ""}`} />
              {isSubmitting ? "Generating Carousel..." : "✦ Generate 6-Slide Carousel"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
