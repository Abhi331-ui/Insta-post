"use client";

import { useEffect, useState } from "react";
import AgentStatusBar from "@/components/AgentStatusBar";
import SlidePreview from "@/components/SlidePreview";
import WhyThisPost from "@/components/WhyThisPost";
import ApprovalPanel from "@/components/ApprovalPanel";
import { getPosts, getSettings } from "@/lib/api";
import { Sparkles, Clock, Compass, ShieldAlert, Play } from "lucide-react";

export default function DashboardPage() {
  const [latestPost, setLatestPost] = useState<any>(null);
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [posts, settingsData] = await Promise.all([getPosts(), getSettings()]);
      if (posts && posts.length > 0) {
        setLatestPost(posts[0]);
      } else {
        setLatestPost(null);
      }
      setSettings(settingsData);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

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

      {/* Live Agent Status Stream */}
      <AgentStatusBar />

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
