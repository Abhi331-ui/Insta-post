"use client";

import { Bookmark, Share2, Eye, Heart, UserPlus, TrendingUp, Lightbulb, Compass } from "lucide-react";

interface AnalyticsData {
  total_reach: number;
  total_impressions: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_saves: number;
  total_profile_visits: number;
  total_follows: number;
  avg_engagement_rate: number;
  pillar_breakdown: Array<{ name: string; saves: number; shares: number; reach: number }>;
  learning_recommendations?: {
    increase_pillar?: string;
    reduce_pillar?: string;
    best_posting_time?: string;
    top_hook_patterns?: string[];
    top_layouts?: string[];
    learning_notes?: string;
  };
}

interface AnalyticsChartProps {
  data: AnalyticsData;
}

export default function AnalyticsChart({ data }: AnalyticsChartProps) {
  const kpis = [
    { label: "Total Reach", value: data.total_reach.toLocaleString(), icon: Eye, change: "+24% vs last week", color: "text-blue-400" },
    { label: "Total Saves", value: data.total_saves.toLocaleString(), icon: Bookmark, change: "+38% vs last week", color: "text-emerald-400" },
    { label: "Total Shares", value: data.total_shares.toLocaleString(), icon: Share2, change: "+19% vs last week", color: "text-purple-400" },
    { label: "Avg Engagement", value: `${data.avg_engagement_rate}%`, icon: TrendingUp, change: "Industry avg: 2.1%", color: "text-amber-400" },
    { label: "Profile Visits", value: data.total_profile_visits.toLocaleString(), icon: UserPlus, change: "+15% vs last week", color: "text-cyan-400" },
    { label: "Total Likes", value: data.total_likes.toLocaleString(), icon: Heart, change: "+12% vs last week", color: "text-rose-400" },
  ];

  const maxSaves = Math.max(...data.pillar_breakdown.map((p) => p.saves), 1);

  return (
    <div className="flex flex-col gap-6">
      {/* Top 6 KPI Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="bg-[#0F172A] border border-slate-800 rounded-2xl p-4 flex flex-col justify-between shadow-lg"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">{kpi.label}</span>
                <Icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
              <div>
                <div className="text-2xl font-black text-white tracking-tight">{kpi.value}</div>
                <div className="text-[11px] text-slate-500 font-medium mt-1">{kpi.change}</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Content Pillar Performance */}
        <div className="lg:col-span-2 bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <Compass className="w-5 h-5 text-blue-400" />
                Content Pillar Performance (Saves & Retention)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Which pillars drive the highest bookmark and share velocity</p>
            </div>
          </div>

          <div className="flex flex-col gap-5">
            {data.pillar_breakdown.map((pillar) => {
              const pct = Math.round((pillar.saves / maxSaves) * 100);
              return (
                <div key={pillar.name} className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-200">{pillar.name}</span>
                    <div className="flex items-center gap-3 text-slate-400 font-mono">
                      <span>{pillar.saves} saves</span>
                      <span>•</span>
                      <span>{pillar.shares} shares</span>
                    </div>
                  </div>
                  <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="h-full bg-gradient-to-r from-blue-600 to-indigo-500 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Learning Agent Recommendations */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-white tracking-tight">Learning Agent</h3>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Autonomous weekly pattern synthesis over the last 30 posts.
            </p>

            {data.learning_recommendations && (
              <div className="flex flex-col gap-3">
                <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block mb-1">
                    Prioritize Pillar
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {data.learning_recommendations.increase_pillar || "AI Workflows & Automation"}
                  </span>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-rose-400 uppercase tracking-wider block mb-1">
                    Deprioritize Format
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {data.learning_recommendations.reduce_pillar || "Generic Prompt Lists"}
                  </span>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-blue-400 uppercase tracking-wider block mb-1">
                    Optimal Posting Time
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {data.learning_recommendations.best_posting_time || "09:00 UTC"}
                  </span>
                </div>

                <div className="bg-blue-950/20 border border-blue-900/30 rounded-xl p-3 mt-1">
                  <p className="text-xs text-slate-300 italic leading-relaxed">
                    "{data.learning_recommendations.learning_notes || "Carousels featuring practical containerized workflows drive 3.4x higher bookmark rates than surface-level listicles."}"
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
