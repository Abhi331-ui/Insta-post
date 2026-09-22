"use client";

import { ExternalLink, Sparkles, CheckCircle2, Shield, Users, Target, Compass } from "lucide-react";

interface WhyThisPostProps {
  post: {
    topic: string;
    hook: string;
    angle?: string;
    freshness_category?: string;
    content_pillar?: string;
    why_today_reason?: string;
    target_audience?: string[];
    sources?: string[];
    scores?: Record<string, number>;
  };
}

export default function WhyThisPost({ post }: WhyThisPostProps) {
  const scores = post.scores || {};
  const sources = post.sources || [];
  const audience = post.target_audience || ["developers", "AI power-users"];

  const getFreshnessColor = (cat?: string) => {
    switch (cat) {
      case "BRAND_NEW":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "DEVELOPING":
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      case "RECENT":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
    }
  };

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col gap-6">
      {/* Header & Badges */}
      <div className="flex items-start justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[11px] font-bold tracking-wider uppercase text-blue-400">
              Strategy Inspection
            </span>
            <span className={`text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border ${getFreshnessColor(post.freshness_category)}`}>
              {post.freshness_category || "BRAND_NEW"}
            </span>
          </div>
          <h3 className="text-xl font-bold text-white tracking-tight leading-snug">
            {post.topic}
          </h3>
        </div>

        {scores.composite_score && (
          <div className="flex flex-col items-center bg-slate-900 border border-slate-700/80 px-3.5 py-2 rounded-xl">
            <span className="text-xs text-slate-400 font-medium">Viability</span>
            <span className="text-xl font-black text-blue-400">{scores.composite_score}</span>
          </div>
        )}
      </div>

      {/* WHY TODAY Reason */}
      <div className="flex items-start gap-3 bg-blue-950/25 border border-blue-900/40 rounded-xl p-4">
        <Sparkles className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-blue-300 mb-1">
            Why Today? (Discovery Rule)
          </h4>
          <p className="text-sm text-slate-300 leading-relaxed">
            {post.why_today_reason || "New breakthrough update released this week that eliminates local environment setup overhead."}
          </p>
        </div>
      </div>

      {/* Hook & Angle */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mb-1.5">
            <Target className="w-3.5 h-3.5 text-blue-400" />
            Selected Hook
          </div>
          <p className="text-sm font-semibold text-slate-200">
            "{post.hook}"
          </p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mb-1.5">
            <Compass className="w-3.5 h-3.5 text-purple-400" />
            Content Pillar
          </div>
          <p className="text-sm font-semibold text-slate-200">
            {post.content_pillar || "AI Workflows & Automation"}
          </p>
        </div>
      </div>

      {/* Viability Criteria Breakdown */}
      {Object.keys(scores).length > 1 && (
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            Evaluation Criteria (Threshold &gt;= 6.0)
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {Object.entries(scores).map(([key, val]) => {
              if (key === "composite_score" || key === "scoring_notes" || (typeof val !== "number" && isNaN(Number(val)))) return null;
              const numericVal = typeof val === "number" ? val : Number(val);
              return (
                <div key={key} className="bg-slate-900/50 border border-slate-800/80 rounded-lg p-2.5">
                  <div className="text-[11px] text-slate-400 capitalize">{key.replace("_", " ")}</div>
                  <div className="text-sm font-bold text-slate-200 mt-0.5">{numericVal} / 10</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Target Audience */}
      <div>
        <div className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5 text-blue-400" />
          Target Audience
        </div>
        <div className="flex flex-wrap gap-1.5">
          {audience.map((aud, i) => (
            <span key={i} className="text-xs px-2.5 py-1 rounded-md bg-slate-900 text-slate-300 border border-slate-800">
              {aud}
            </span>
          ))}
        </div>
      </div>

      {/* Verified Sources */}
      {sources.length > 0 && (
        <div className="border-t border-slate-800/80 pt-4">
          <div className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Fact-Checked Sources
          </div>
          <div className="flex flex-col gap-1.5">
            {sources.map((src, i) => (
              <a
                key={i}
                href={src}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-400 hover:text-blue-300 hover:underline truncate flex items-center gap-1"
              >
                <ExternalLink className="w-3 h-3 shrink-0" />
                {src}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
