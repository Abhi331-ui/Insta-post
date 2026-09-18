"use client";

import { useState } from "react";
import { Check, X, RefreshCw, Send, Clock, Calendar, Edit3 } from "lucide-react";
import { approvePost, rejectPost, regeneratePost, publishNow, updateCaption } from "@/lib/api";

interface ApprovalPanelProps {
  post: {
    id: number;
    status: string;
    scheduled_at?: string;
    caption?: string;
    hashtags?: string;
    alt_text?: string;
  };
  onActionComplete: () => void;
}

export default function ApprovalPanel({ post, onActionComplete }: ApprovalPanelProps) {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [editingCaption, setEditingCaption] = useState(false);
  const [captionText, setCaptionText] = useState(post.caption || "");
  const [hashtagsText, setHashtagsText] = useState(post.hashtags || "");

  const handleApprove = async () => {
    try {
      setLoadingAction("approve");
      await approvePost(post.id);
      onActionComplete();
    } catch (e: any) {
      alert("Approval error: " + e.message);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleReject = async () => {
    if (!confirm("Reject this post and trigger autonomous discovery for a fresh opportunity?")) return;
    try {
      setLoadingAction("reject");
      await rejectPost(post.id);
      onActionComplete();
    } catch (e: any) {
      alert("Rejection error: " + e.message);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleRegenerate = async () => {
    if (!confirm("Regenerate entire carousel with fresh angles and visuals?")) return;
    try {
      setLoadingAction("regenerate");
      await regeneratePost(post.id);
      onActionComplete();
    } catch (e: any) {
      alert("Regeneration error: " + e.message);
    } finally {
      setLoadingAction(null);
    }
  };

  const handlePublishNow = async () => {
    if (!confirm("Publish this carousel to Instagram immediately via Meta Graph API?")) return;
    try {
      setLoadingAction("publish");
      const res = await publishNow(post.id);
      alert(res.simulated ? "Simulated publication successful!" : "Published live to Instagram!");
      onActionComplete();
    } catch (e: any) {
      alert("Publishing error: " + e.message);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleSaveCaption = async () => {
    try {
      await updateCaption(post.id, { caption: captionText, hashtags: hashtagsText });
      setEditingCaption(false);
      onActionComplete();
    } catch (e: any) {
      alert("Error saving caption: " + e.message);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "published":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "scheduled":
        return "bg-blue-500/15 text-blue-400 border-blue-500/30";
      case "pending_approval":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "failed":
        return "bg-rose-500/15 text-rose-400 border-rose-500/30";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col gap-5">
      {/* Top Status and Time */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Status:</span>
          <span className={`text-xs font-bold px-3 py-1 rounded-full border capitalize ${getStatusBadge(post.status)}`}>
            {post.status.replace("_", " ")}
          </span>
        </div>

        {post.scheduled_at && (
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Scheduled: {new Date(post.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button
          onClick={handleApprove}
          disabled={loadingAction !== null || post.status === "scheduled" || post.status === "published"}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-bold shadow-lg shadow-emerald-600/20 active:scale-95 transition-all disabled:opacity-40"
        >
          <Check className="w-4 h-4" />
          {loadingAction === "approve" ? "Approving..." : "Approve"}
        </button>

        <button
          onClick={handleReject}
          disabled={loadingAction !== null}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/30 text-sm font-bold active:scale-95 transition-all disabled:opacity-40"
        >
          <X className="w-4 h-4" />
          {loadingAction === "reject" ? "Rejecting..." : "Reject"}
        </button>

        <button
          onClick={handleRegenerate}
          disabled={loadingAction !== null}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-semibold active:scale-95 transition-all disabled:opacity-40"
        >
          <RefreshCw className={`w-4 h-4 ${loadingAction === "regenerate" ? "animate-spin text-blue-400" : ""}`} />
          {loadingAction === "regenerate" ? "Regenerating..." : "Regen All"}
        </button>

        <button
          onClick={handlePublishNow}
          disabled={loadingAction !== null || post.status === "published"}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold shadow-lg shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-40"
        >
          <Send className="w-4 h-4" />
          {loadingAction === "publish" ? "Publishing..." : "Publish Now"}
        </button>
      </div>

      {/* Caption Preview & Inline Editor */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 mt-2">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Instagram Caption & Tags
          </span>
          <button
            onClick={() => setEditingCaption(!editingCaption)}
            className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-medium"
          >
            <Edit3 className="w-3.5 h-3.5" />
            {editingCaption ? "Cancel" : "Edit Copy"}
          </button>
        </div>

        {editingCaption ? (
          <div className="flex flex-col gap-3 mt-2">
            <textarea
              rows={4}
              value={captionText}
              onChange={(e) => setCaptionText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-slate-200 font-sans focus:outline-none focus:border-blue-500"
              placeholder="Caption copy..."
            />
            <input
              type="text"
              value={hashtagsText}
              onChange={(e) => setHashtagsText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
              placeholder="#hashtags"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setEditingCaption(false)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCaption}
                className="px-4 py-1.5 rounded-lg bg-blue-600 text-xs font-bold text-white hover:bg-blue-500"
              >
                Save Caption
              </button>
            </div>
          </div>
        ) : (
          <div>
            <p className="text-xs text-slate-300 whitespace-pre-line line-clamp-3 leading-relaxed">
              {post.caption || "No caption generated."}
            </p>
            {post.hashtags && (
              <p className="text-[11px] text-blue-400/80 mt-2 truncate">
                {post.hashtags}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
