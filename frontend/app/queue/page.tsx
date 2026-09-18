"use client";

import { useEffect, useState } from "react";
import { getQueue, submitTopicBatch, deleteQueueItem, getPost } from "@/lib/api";
import SlidePreview from "@/components/SlidePreview";
import WhyThisPost from "@/components/WhyThisPost";
import {
  ListOrdered,
  Calendar,
  Sparkles,
  Clock,
  Trash2,
  RefreshCw,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Send,
  X,
  Layers,
  ArrowRight,
  ShieldCheck,
  Film,
  Zap,
} from "lucide-react";

const SAMPLE_TRENDING_TOPICS = [
  "1. Bolt.new In-Browser Runtime Breakthrough",
  "2. OpenAI Canvas Interface vs Traditional Editors",
  "3. Cursor Composer 20-File Orchestration",
  "4. v0.dev Next.js Component Generation",
  "5. Claude 3.5 Sonnet Artifacts for Productivity",
  "6. Perplexity Pro Computer Interaction Workflows",
  "7. NotebookLM Dual-Host Audio Synthesis",
  "8. Devin AI Autonomous Software Engineering Review",
  "9. Replit Agent Full-Stack Autonomous Deployments",
  "10. Supabase AI Auto-Migrate Vector Search",
];

const PILLAR_STYLES: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  "AI Workflows & Automation": {
    bg: "bg-blue-500/15",
    text: "text-blue-400",
    border: "border-blue-500/30",
    dot: "bg-blue-400",
  },
  "New Model & Tool Launches": {
    bg: "bg-purple-500/15",
    text: "text-purple-400",
    border: "border-purple-500/30",
    dot: "bg-purple-400",
  },
  "Developer & Engineering Tools": {
    bg: "bg-emerald-500/15",
    text: "text-emerald-400",
    border: "border-emerald-500/30",
    dot: "bg-emerald-400",
  },
  "Productivity Experiments": {
    bg: "bg-amber-500/15",
    text: "text-amber-400",
    border: "border-amber-500/30",
    dot: "bg-amber-400",
  },
};

const SLIDE_NAMES = [
  { num: 1, name: "Hero Hook", type: "hero" },
  { num: 2, name: "Meet Tool", type: "tool_card" },
  { num: 3, name: "Showcase", type: "showcase" },
  { num: 4, name: "4 Steps", type: "steps" },
  { num: 5, name: "Real Demo", type: "comparison" },
  { num: 6, name: "CTA", type: "cta" },
];

export default function QueuePage() {
  const [topicsText, setTopicsText] = useState("");
  const [startDate, setStartDate] = useState("");
  const [queueData, setQueueData] = useState<any>({ items: [], stats: {} });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [postsPerDay, setPostsPerDay] = useState<number>(1);
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [activeSlideIdx, setActiveSlideIdx] = useState(0);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const data = await getQueue();
      setQueueData(data);
    } catch (e: any) {
      console.error("Error loading topic queue:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Default start date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setStartDate(tomorrow.toISOString().slice(0, 10));
    loadQueue();
  }, []);

  const handleSubmitBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    const lines = topicsText
      .split("\n")
      .map((l) => l.replace(/^\d+[\.\)]\s*/, "").trim())
      .filter((l) => l.length > 0);

    if (lines.length === 0) {
      alert("Please enter at least 1 topic.");
      return;
    }

    try {
      setSubmitting(true);
      const res = await submitTopicBatch(lines, startDate || undefined, postsPerDay);
      alert(res.message || `Queued ${lines.length} topics across consecutive days!`);
      setTopicsText("");
      loadQueue();
    } catch (e: any) {
      alert("Error submitting batch: " + e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePasteSample = () => {
    setTopicsText(SAMPLE_TRENDING_TOPICS.join("\n"));
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Remove this topic from the consecutive queue?")) return;
    try {
      await deleteQueueItem(id);
      loadQueue();
    } catch (e: any) {
      alert("Error deleting item: " + e.message);
    }
  };

  const handleInspectPost = async (postId: number, slideNum: number = 1) => {
    try {
      const post = await getPost(postId);
      setSelectedPost(post);
      setActiveSlideIdx(slideNum - 1);
    } catch (e: any) {
      alert("Error loading post: " + e.message);
    }
  };

  const stats = queueData.stats || {};
  const items = queueData.items || [];

  const getStatusBadge = (st: string) => {
    switch (st) {
      case "ready":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "generating":
        return "bg-blue-500/15 text-blue-400 border-blue-500/30 animate-pulse";
      case "published":
        return "bg-purple-500/15 text-purple-400 border-purple-500/30";
      case "pending":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  return (
    <div className="flex flex-col gap-8 pb-16 max-w-6xl mx-auto">
      {/* Header Banner with Cyberpunk Gradient Accent */}
      <div className="relative rounded-3xl p-8 bg-gradient-to-br from-[#0B0F19] via-[#0F172A] to-[#1E1B4B] border border-purple-500/20 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/15 border border-purple-500/30 text-purple-300 text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                Cinematic Content Queue
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-mono">
                1080×1350 HD
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
              Topic Queue & Consecutive Days Scheduler
            </h1>
            <p className="text-sm text-slate-300 mt-2 max-w-2xl leading-relaxed">
              Every topic is scheduled across consecutive calendar days with a full, verified 6-slide story carousel rendered in the <strong className="text-white">Cinematic Dark Design System</strong>.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
            <div className="px-4 py-3 rounded-2xl bg-slate-900/80 border border-slate-700/60 backdrop-blur-md flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs text-slate-400 font-medium">Consecutive Streak</div>
                <div className="text-lg font-black text-white">{items.length} Days Active</div>
              </div>
            </div>

            <div className="px-4 py-3 rounded-2xl bg-slate-900/80 border border-slate-700/60 backdrop-blur-md flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
                <Film className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs text-slate-400 font-medium">Carousels Ready</div>
                <div className="text-lg font-black text-white">{items.length * 6} HD Slides</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5-Day Refill Status Bar */}
      <div
        className={`p-5 rounded-2xl border backdrop-blur-md flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all shadow-lg ${
          stats.refill_recommended
            ? "bg-amber-950/30 border-amber-500/40 text-amber-200 shadow-amber-950/20"
            : "bg-emerald-950/25 border-emerald-500/30 text-emerald-200 shadow-emerald-950/20"
        }`}
      >
        <div className="flex items-center gap-3.5">
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
              stats.refill_recommended ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500/20 text-emerald-400"
            }`}
          >
            {stats.refill_recommended ? (
              <AlertTriangle className="w-5 h-5" />
            ) : (
              <CheckCircle2 className="w-5 h-5" />
            )}
          </div>
          <div>
            <div className="text-sm font-bold flex items-center gap-2">
              <span>{stats.refill_recommended ? "Refill Due: Queue coverage is low" : "10-Day Consecutive Queue Ready"}</span>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
                100% Brand Unified
              </span>
            </div>
            <div className="text-xs opacity-80 mt-0.5">
              Coverage: <strong>{stats.days_covered || items.length} consecutive calendar days scheduled</strong>.
              All carousels share the exact same high-contrast, pure black aesthetic with zero layout crashes.
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={loadQueue}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
            Refresh Queue
          </button>
        </div>
      </div>

      {/* Input Section: 10 Topics Form */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col gap-6 relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              Schedule 10 Consecutive Trending Topics
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Paste up to 10 topics. PromptPulse maps each topic across consecutive calendar days and renders complete 6-slide carousels.
            </p>
          </div>

          <button
            type="button"
            onClick={handlePasteSample}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600/20 to-blue-600/20 hover:from-purple-600/30 hover:to-blue-600/30 border border-purple-500/30 text-xs font-semibold text-purple-300 transition-all shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            Paste 10 Real AI Topics
          </button>
        </div>

        <form onSubmit={handleSubmitBatch} className="flex flex-col gap-4">
          <textarea
            rows={5}
            value={topicsText}
            onChange={(e) => setTopicsText(e.target.value)}
            placeholder={`1. Bolt.new In-Browser Runtime Breakthrough\n2. OpenAI Canvas Interface vs Traditional Editors\n3. Cursor Composer 20-File Orchestration\n4. v0.dev Next.js Component Generation\n5. Claude 3.5 Sonnet Artifacts for Productivity\n... paste 10 trending topics (one per line)`}
            className="w-full bg-slate-950/90 border border-slate-800 rounded-2xl p-4 text-xs font-mono text-slate-200 focus:outline-none focus:border-purple-500/80 focus:ring-1 focus:ring-purple-500/40 leading-relaxed shadow-inner"
          />

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Calendar className="w-4 h-4 text-blue-400" />
                <span>Start Date:</span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex items-center gap-1.5 text-xs text-slate-400 pl-3 border-l border-slate-800">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>Interval: <strong className="text-white">1 post / day</strong></span>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting || !topicsText.trim()}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 hover:opacity-90 text-white text-xs font-bold shadow-lg shadow-purple-600/30 active:scale-95 transition-all disabled:opacity-40"
            >
              <Send className={`w-3.5 h-3.5 ${submitting ? "animate-spin" : ""}`} />
              {submitting ? "Generating 10 Carousels..." : "Schedule 10 Consecutive Days"}
            </button>
          </div>
        </form>
      </div>

      {/* Visual Consecutive Schedule Timeline List */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-3xl p-6 sm:p-8 shadow-xl flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Calendar className="w-5 h-5 text-purple-400" />
              Scheduled Consecutive Timeline
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Active 10-day content pipeline. Click on any slide preview or thumbnail to inspect the full 6-slide carousel.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 font-mono">
              {items.length} Consecutive Days Active
            </span>
          </div>
        </div>

        {loading ? (
          <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-3">
            <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs font-medium">Loading consecutive timeline & slides...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-16 text-slate-500 flex flex-col items-center">
            <Layers className="w-12 h-12 mb-3 text-slate-700 animate-pulse" />
            <p className="text-sm font-medium text-slate-400">Queue is currently empty.</p>
            <p className="text-xs text-slate-600 mt-1">
              Click &quot;Paste 10 Real AI Topics&quot; above to schedule your 10-day streak.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {items.map((item: any, idx: number) => {
              const pillarStyle = PILLAR_STYLES[item.content_pillar] || PILLAR_STYLES["AI Workflows & Automation"];

              return (
                <div
                  key={item.id}
                  className="relative rounded-2xl bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/80 border border-slate-800/80 hover:border-purple-500/50 p-5 transition-all shadow-xl hover:shadow-purple-950/20 group"
                >
                  <div className="flex flex-col md:flex-row items-start md:items-center gap-6 justify-between">
                    {/* Left: Thumbnail & Day Badge */}
                    <div className="flex items-start gap-4 shrink-0 w-full md:w-auto">
                      {/* Day Pill Badge */}
                      <div className="w-12 h-16 rounded-2xl bg-gradient-to-b from-purple-600/20 to-blue-600/10 border border-purple-500/30 text-purple-300 flex flex-col items-center justify-center shrink-0 shadow-lg">
                        <span className="text-[9px] uppercase font-bold tracking-widest text-slate-400">DAY</span>
                        <span className="text-xl font-black text-white">{String(item.day_index || idx + 1).padStart(2, "0")}</span>
                      </div>

                      {/* Mini 4:5 Slide 1 Thumbnail */}
                      {item.preview_image_url ? (
                        <div
                          onClick={() => item.post_id && handleInspectPost(item.post_id, 1)}
                          className="relative w-20 aspect-[4/5] rounded-xl overflow-hidden border border-purple-500/40 shadow-lg cursor-pointer group-hover:scale-105 transition-transform shrink-0 bg-black"
                          title="Click to inspect this 6-slide carousel"
                        >
                          <img
                            src={item.preview_image_url}
                            alt={item.topic}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors"></div>
                          <div className="absolute bottom-1 right-1 px-1 py-0.2 rounded bg-black/80 text-[8px] font-mono text-purple-300 font-bold border border-purple-500/30">
                            01/06
                          </div>
                        </div>
                      ) : (
                        <div className="w-20 aspect-[4/5] rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-600 shrink-0">
                          <Layers className="w-6 h-6" />
                        </div>
                      )}

                      {/* Title & Metadata for Mobile */}
                      <div className="md:hidden flex-1 min-w-0">
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border inline-flex items-center gap-1.5 mb-1.5 ${pillarStyle.bg} ${pillarStyle.text} ${pillarStyle.border}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${pillarStyle.dot}`}></span>
                          {item.content_pillar}
                        </span>
                        <h4 className="text-sm font-bold text-white line-clamp-2">{item.topic}</h4>
                        <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-2">
                          <span>{item.date_display}</span>
                          <span>•</span>
                          <span className="text-purple-400 font-semibold">6 Slides Ready</span>
                        </div>
                      </div>
                    </div>

                    {/* Center: Detailed Info (Desktop) */}
                    <div className="hidden md:flex flex-col flex-1 min-w-0 gap-1.5">
                      <div className="flex items-center gap-3">
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md border inline-flex items-center gap-1.5 ${pillarStyle.bg} ${pillarStyle.text} ${pillarStyle.border}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${pillarStyle.dot}`}></span>
                          {item.content_pillar}
                        </span>

                        <span className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5 text-blue-400" />
                          {item.date_display}
                        </span>

                        <span className="text-xs text-slate-500">• {item.time_display}</span>

                        <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.2 rounded-full border ${getStatusBadge(item.status)}`}>
                          {item.status}
                        </span>
                      </div>

                      <h4 className="text-base font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:via-purple-200 group-hover:to-pink-300 transition-all truncate">
                        {item.topic}
                      </h4>

                      {/* Hook Quote Line */}
                      {item.hook && (
                        <p className="text-xs text-slate-400 line-clamp-1 italic">
                          &ldquo;{item.hook}&rdquo;
                        </p>
                      )}

                      {/* 6-Slide Story Arc Filmstrip Navigator */}
                      <div className="flex items-center gap-1.5 mt-2">
                        {SLIDE_NAMES.map((sl) => (
                          <button
                            key={sl.num}
                            onClick={() => item.post_id && handleInspectPost(item.post_id, sl.num)}
                            className="px-2 py-0.5 rounded-md bg-slate-950/80 hover:bg-purple-600/20 border border-slate-800 hover:border-purple-500/40 text-[10px] text-slate-400 hover:text-white transition-all flex items-center gap-1"
                            title={`Inspect Slide ${sl.num}: ${sl.name}`}
                          >
                            <span className="text-purple-400 font-bold font-mono">0{sl.num}</span>
                            <span>{sl.name}</span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center gap-3 self-end md:self-center shrink-0 w-full md:w-auto justify-end pt-3 md:pt-0 border-t md:border-t-0 border-slate-800/80">
                      {item.post_id && (
                        <button
                          onClick={() => handleInspectPost(item.post_id, 1)}
                          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-purple-600/25 hover:shadow-purple-600/40 active:scale-95 transition-all"
                        >
                          <Eye className="w-4 h-4" />
                          <span>View 6 Slides</span>
                          <ArrowRight className="w-3.5 h-3.5 opacity-70" />
                        </button>
                      )}

                      <button
                        onClick={() => handleDelete(item.id)}
                        className="p-2.5 rounded-xl bg-slate-950 hover:bg-rose-950/40 text-slate-500 hover:text-rose-400 border border-slate-800 hover:border-rose-900/60 transition-colors"
                        title="Remove from queue"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Slide Inspection Modal */}
      {selectedPost && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          <div className="bg-[#0B0F19] border border-purple-500/30 rounded-3xl max-w-5xl w-full p-6 sm:p-8 relative shadow-2xl max-h-[92vh] overflow-y-auto">
            <button
              onClick={() => setSelectedPost(null)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-purple-400">
                Active Carousel Inspection
              </span>
              <h2 className="text-xl sm:text-2xl font-black text-white mt-1">
                {selectedPost.topic}
              </h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              <div className="lg:col-span-5">
                <SlidePreview postId={selectedPost.id} slides={selectedPost.slides || []} />
              </div>
              <div className="lg:col-span-7">
                <WhyThisPost post={selectedPost} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
