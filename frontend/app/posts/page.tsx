"use client";

import { useEffect, useState } from "react";
import { getPosts, getPost } from "@/lib/api";
import SlidePreview from "@/components/SlidePreview";
import WhyThisPost from "@/components/WhyThisPost";
import ApprovalPanel from "@/components/ApprovalPanel";
import { LayoutGrid, Filter, Clock, X, ExternalLink } from "lucide-react";

export default function PostsPage() {
  const [posts, setPosts] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadPosts = async () => {
    try {
      setLoading(true);
      const data = await getPosts(statusFilter || undefined);
      setPosts(data);
    } catch (err) {
      console.error("Error loading posts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPosts();
  }, [statusFilter]);

  const handleSelectPost = async (id: number) => {
    try {
      const p = await getPost(id);
      setSelectedPost(p);
    } catch (e: any) {
      alert("Error loading post: " + e.message);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "published": return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "scheduled": return "bg-blue-500/15 text-blue-400 border-blue-500/30";
      case "pending_approval": return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "failed": return "bg-rose-500/15 text-rose-400 border-rose-500/30";
      default: return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <LayoutGrid className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Post Catalog</span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">All Carousels</h1>
          <p className="text-sm text-slate-400 mt-1">
            Browse, inspect, and manage every 6-slide carousel created by PromptPulse.
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {["", "pending_approval", "scheduled", "published", "failed"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize whitespace-nowrap transition-all ${
                statusFilter === st
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                  : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              {st === "" ? "All Posts" : st.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Posts Grid */}
      {loading ? (
        <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-medium">Loading posts...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-12 text-center text-slate-500">
          <p className="text-sm font-medium">No posts found matching filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <div
              key={post.id}
              onClick={() => handleSelectPost(post.id)}
              className="bg-[#0F172A] border border-slate-800 hover:border-blue-500/50 rounded-2xl p-5 shadow-xl cursor-pointer transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${getStatusBadge(post.status)}`}>
                    {post.status.replace("_", " ")}
                  </span>
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(post.created_at).toLocaleDateString()}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-2 mb-2">
                  {post.topic}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  "{post.hook}"
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                <span>{post.content_pillar || "AI Productivity"}</span>
                <span className="font-semibold text-slate-400">6 Slides →</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Post Inspection Drawer / Modal */}
      {selectedPost && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          <div className="bg-[#0F172A] border border-slate-800 rounded-3xl max-w-5xl w-full p-6 relative shadow-2xl max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedPost(null)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start mt-4">
              <div className="lg:col-span-5">
                <SlidePreview
                  postId={selectedPost.id}
                  slides={selectedPost.slides || []}
                  onSlideUpdated={() => handleSelectPost(selectedPost.id)}
                />
              </div>

              <div className="lg:col-span-7 flex flex-col gap-6">
                <WhyThisPost post={selectedPost} />
                <ApprovalPanel post={selectedPost} onActionComplete={() => { loadPosts(); handleSelectPost(selectedPost.id); }} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
