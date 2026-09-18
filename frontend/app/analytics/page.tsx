"use client";

import { useEffect, useState } from "react";
import AnalyticsChart from "@/components/AnalyticsChart";
import { getAnalytics, getPosts } from "@/lib/api";
import { BarChart3, TrendingUp, Sparkles } from "lucide-react";

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [analyticsData, postsData] = await Promise.all([getAnalytics(), getPosts()]);
        setData(analyticsData);
        setPosts(postsData);
      } catch (err) {
        console.error("Error loading analytics:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  return (
    <div className="flex flex-col gap-8">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Audience Growth</span>
        </div>
        <h1 className="text-3xl font-black text-white tracking-tight">Performance Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">
          Track bookmarks, shares, engagement, and discover which content pillars drive true retention.
        </p>
      </div>

      {loading ? (
        <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-medium">Synthesizing analytics insights...</p>
        </div>
      ) : data ? (
        <AnalyticsChart data={data} />
      ) : (
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-12 text-center text-slate-500">
          <p className="text-sm">No analytics records collected yet. Insights appear 24h after publication.</p>
        </div>
      )}
    </div>
  );
}
