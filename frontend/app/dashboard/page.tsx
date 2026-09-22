"use client";

import { useEffect, useState } from "react";
import AgentStatusBar from "@/components/AgentStatusBar";
import SlidePreview from "@/components/SlidePreview";
import WhyThisPost from "@/components/WhyThisPost";
import ApprovalPanel from "@/components/ApprovalPanel";
import CreateCarouselModal from "@/components/CreateCarouselModal";
import SixSlotStudioModal from "@/components/SixSlotStudioModal";
import { getPosts, getSettings, createManualPost, getAgentBrain, updateCustomDirectives } from "@/lib/api";
import { Sparkles, Clock, Compass, ShieldAlert, Play, Brain, Layers, Plus, Trash2, CheckCircle2 } from "lucide-react";

export default function DashboardPage() {
  const [latestPost, setLatestPost] = useState<any>(null);
  const [settings, setSettings] = useState<any>(null);
  const [agentBrain, setAgentBrain] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [quickTopic, setQuickTopic] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateMsg, setGenerateMsg] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSixSlotModalOpen, setIsSixSlotModalOpen] = useState(false);
  const [newDirective, setNewDirective] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [posts, settingsData, brainData] = await Promise.all([
        getPosts(),
        getSettings(),
        getAgentBrain().catch(() => null),
      ]);
      if (posts && posts.length > 0) {
        setLatestPost(posts[0]);
      } else {
        setLatestPost(null);
      }
      setSettings(settingsData);
      setAgentBrain(brainData);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleQuickGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickTopic.trim()) return;

    try {
      setIsGenerating(true);
      setGenerateMsg("");
      await createManualPost(quickTopic.trim());
      setGenerateMsg(`Autonomous pipeline started for "${quickTopic.trim()}". Follow live progress on the status bar below!`);
      setQuickTopic("");
      // Poll to reload post data after generation starts
      setTimeout(loadData, 3000);
      setTimeout(loadData, 8000);
    } catch (err: any) {
      setGenerateMsg(`Error: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
              Autonomous Content Engine
            </span>
            {settings?.auto_mode_enabled && (
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Auto Mode Active
              </span>
            )}
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Today's Discovery</h1>
          <p className="text-sm text-slate-400 mt-1">
            PromptPulse researches breaking AI developments and writes 6-slide carousels every morning.
          </p>
        </div>

        {settings && (
          <div className="flex items-center gap-4 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-blue-400" />
              <span>Post Time: <strong className="text-slate-200">{settings.posting_time}</strong> ({settings.timezone})</span>
            </div>
            <span className="text-slate-700">|</span>
            <div className="flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-purple-400" />
              <span>Niche: <strong className="text-slate-200">{settings.niche}</strong></span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Generate for Any Topic */}
      <div className="bg-[#090D16] border border-blue-500/30 rounded-3xl p-6 shadow-2xl shadow-blue-500/10 relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-purple-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-purple-400">
                Custom Topic Engine
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Generate Carousel for Any Topic
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Type any tool, framework, or idea to immediately create a 6-slide cosmic-neon carousel.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.1] text-xs font-semibold text-slate-300 hover:text-white transition-all whitespace-nowrap"
          >
            ✦ Custom Options & Audience
          </button>
        </div>

        {/* Input Bar */}
        <form onSubmit={handleQuickGenerate} className="flex flex-col sm:flex-row gap-3 relative z-10">
          <div className="relative flex-1">
            <input
              type="text"
              value={quickTopic}
              onChange={(e) => setQuickTopic(e.target.value)}
              placeholder="Enter any topic (e.g., Google Veo 3, Claude 3.5 Sonnet, Cursor Composer, Next.js 15)..."
              className="w-full bg-[#0F172A] border border-slate-700/80 focus:border-blue-500 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-500 outline-none transition-all shadow-inner"
              disabled={isGenerating}
            />
          </div>
          <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
            <button
              type="button"
              onClick={() => setIsSixSlotModalOpen(true)}
              className="flex items-center justify-center gap-1.5 px-4 py-3 rounded-xl bg-cyan-950/40 hover:bg-cyan-900/50 border border-cyan-500/40 text-cyan-300 hover:text-white text-xs font-bold active:scale-95 transition-all whitespace-nowrap shadow-lg shadow-cyan-950/30"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>✦ 6-Slot Slide Studio</span>
            </button>
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="flex items-center justify-center gap-1.5 px-4 py-3 rounded-xl bg-white/[0.05] hover:bg-white/[0.09] border border-white/[0.1] text-slate-300 hover:text-white text-xs font-semibold active:scale-95 transition-all whitespace-nowrap"
            >
              <span>✦ Add Notes</span>
            </button>
            <button
              type="submit"
              disabled={isGenerating || !quickTopic.trim()}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:opacity-95 text-white text-xs font-bold shadow-lg shadow-purple-600/25 active:scale-95 transition-all disabled:opacity-50 whitespace-nowrap"
            >
              <Sparkles className={`w-4 h-4 ${isGenerating ? "animate-spin" : ""}`} />
              {isGenerating ? "Generating..." : "✦ Instant Generate"}
            </button>
          </div>
        </form>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-1.5 mt-3 relative z-10">
          <span className="text-[11px] text-slate-500 mr-1">Trending:</span>
          {[
            { label: "Google Veo 3", icon: "⚡" },
            { label: "Claude 3.5 Sonnet", icon: "✦" },
            { label: "Cursor Composer", icon: "🚀" },
            { label: "OpenAI Canvas", icon: "💎" },
            { label: "Bolt.new Full-Stack", icon: "🔥" },
            { label: "v0 by Vercel", icon: "🛠️" },
          ].map((s) => (
            <button
              key={s.label}
              type="button"
              onClick={() => setQuickTopic(s.label)}
              className="px-2.5 py-1 rounded-lg text-xs bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.08] text-slate-300 hover:text-white transition-all active:scale-95 flex items-center gap-1"
            >
              <span>{s.icon}</span>
              <span>{s.label}</span>
            </button>
          ))}
        </div>

        {generateMsg && (
          <div className="mt-3 p-3 rounded-xl bg-purple-950/40 border border-purple-500/30 text-purple-200 text-xs font-medium">
            {generateMsg}
          </div>
        )}
      </div>

      {/* Live Agent Status Stream */}
      <AgentStatusBar />

      {/* Agent Brain & Everyday Learnings Card */}
      {agentBrain && (
        <div className="bg-[#090D16] border border-purple-500/30 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-white/[0.08]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-300">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-white">Agent Brain & Everyday Learnings</h3>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Self-Optimizing
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Learns from everyday posts, approvals, rejections, and your custom directives.
                </p>
              </div>
            </div>
            <a
              href="/settings"
              className="text-xs font-semibold text-purple-400 hover:text-purple-300 flex items-center gap-1 transition-colors self-start md:self-auto"
            >
              <span>Configure Carousel Blueprint</span>
              <span>→</span>
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {/* Winning Hooks */}
            <div className="p-3.5 rounded-2xl bg-[#0F172A] border border-slate-800">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Top Learned Hook Patterns</span>
              </div>
              <div className="flex flex-col gap-1.5">
                {(agentBrain.top_hook_patterns || []).slice(0, 3).map((h: string, idx: number) => (
                  <div key={idx} className="text-xs text-slate-300 bg-white/[0.03] border border-white/[0.06] rounded-lg px-2.5 py-1.5">
                    "{h}"
                  </div>
                ))}
              </div>
            </div>

            {/* Empirical Takeaways */}
            <div className="p-3.5 rounded-2xl bg-[#0F172A] border border-slate-800">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Empirical Content Takeaways</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {agentBrain.learning_notes || "Cosmic-neon carousels with 4-step workflow breakdowns drive highest save rates."}
              </p>
              <div className="mt-3 flex items-center gap-2">
                <span className="text-[11px] text-slate-500">Priority Pillar:</span>
                <span className="text-xs font-semibold text-purple-300 px-2 py-0.5 rounded bg-purple-500/20 border border-purple-500/30">
                  {agentBrain.increase_pillar || "AI Workflows & Automation"}
                </span>
              </div>
            </div>

            {/* Custom Directives / Rules */}
            <div className="p-3.5 rounded-2xl bg-[#0F172A] border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Active AI Directives</span>
                  <span className="text-[10px] text-slate-500 font-normal">{(agentBrain.custom_directives || []).length} rules</span>
                </div>
                <div className="flex flex-col gap-1.5 max-h-28 overflow-y-auto pr-1">
                  {(agentBrain.custom_directives || []).map((d: string, idx: number) => (
                    <div key={idx} className="text-[11px] text-slate-300 bg-white/[0.03] border border-white/[0.06] rounded-lg px-2.5 py-1 flex items-center justify-between">
                      <span className="truncate">• {d}</span>
                      <button
                        onClick={async () => {
                          const updated = (agentBrain.custom_directives || []).filter((_: any, i: number) => i !== idx);
                          await updateCustomDirectives(updated);
                          setAgentBrain({ ...agentBrain, custom_directives: updated });
                        }}
                        className="text-slate-500 hover:text-rose-400 ml-1.5 shrink-0"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Add Directive on the fly */}
              <div className="mt-2.5 flex items-center gap-1.5">
                <input
                  type="text"
                  value={newDirective}
                  onChange={(e) => setNewDirective(e.target.value)}
                  placeholder="Add custom rule (e.g. Keep headlines under 5 words)..."
                  className="flex-1 bg-[#080C16] border border-slate-700 rounded-lg px-2.5 py-1 text-[11px] text-white outline-none focus:border-purple-500"
                  onKeyDown={async (e) => {
                    if (e.key === "Enter" && newDirective.trim()) {
                      e.preventDefault();
                      const updated = [...(agentBrain.custom_directives || []), newDirective.trim()];
                      await updateCustomDirectives(updated);
                      setAgentBrain({ ...agentBrain, custom_directives: updated });
                      setNewDirective("");
                    }
                  }}
                />
                <button
                  onClick={async () => {
                    if (!newDirective.trim()) return;
                    const updated = [...(agentBrain.custom_directives || []), newDirective.trim()];
                    await updateCustomDirectives(updated);
                    setAgentBrain({ ...agentBrain, custom_directives: updated });
                    setNewDirective("");
                  }}
                  className="p-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white"
                >
                  <Plus className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <CreateCarouselModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadData}
        initialTopic={quickTopic}
      />

      <SixSlotStudioModal
        isOpen={isSixSlotModalOpen}
        onClose={() => setIsSixSlotModalOpen(false)}
        onSuccess={loadData}
        initialTopic={quickTopic}
      />

      {/* Main Content Area */}
      {loading ? (
        <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-medium">Loading content workspace...</p>
        </div>
      ) : latestPost ? (
        <div className="flex flex-col gap-8">
          {/* 2-Column: 6-Slide Preview (Left) & Why This Post (Right) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-5">
              <div className="sticky top-24">
                <SlidePreview
                  postId={latestPost.id}
                  slides={latestPost.slides || []}
                  onSlideUpdated={loadData}
                />
              </div>
            </div>

            <div className="lg:col-span-7 flex flex-col gap-6">
              <WhyThisPost post={latestPost} />
              <ApprovalPanel post={latestPost} onActionComplete={loadData} />
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#0F172A] border border-slate-800 rounded-3xl p-12 text-center flex flex-col items-center justify-center max-w-xl mx-auto shadow-2xl">
          <div className="w-16 h-16 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-5">
            <Sparkles className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">No Post Generated Yet</h2>
          <p className="text-sm text-slate-400 mb-6 leading-relaxed">
            PromptPulse follows the discovery rule: only publish when something is genuinely worth saving.
            Trigger an autonomous research scan now to find today's opportunity.
          </p>
          <button
            onClick={async () => {
              const { runAgentNow } = await import("@/lib/api");
              await runAgentNow();
              setTimeout(loadData, 2000);
            }}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold shadow-lg shadow-blue-600/25 transition-all"
          >
            <Play className="w-4 h-4 fill-white" />
            Launch First Discovery Run
          </button>
        </div>
      )}
    </div>
  );
}
