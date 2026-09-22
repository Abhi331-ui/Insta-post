"use client";

import { useState, useEffect } from "react";
import {
  MessageSquare,
  Send,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  MessageCircle,
  Inbox as InboxIcon,
  Search,
  Filter,
  ArrowRight,
  ExternalLink,
  ShieldCheck,
  Zap,
  CornerDownRight,
  Clock,
  UserCheck,
} from "lucide-react";
import {
  getInteractions,
  getInteractionStats,
  checkInteractionsNow,
  replyToInteraction,
  ignoreInteraction,
} from "@/lib/api";

interface Interaction {
  id: number;
  user_id: number;
  post_id?: number;
  type: "comment" | "dm";
  external_id?: string;
  sender_id?: string;
  sender_username?: string;
  content: string;
  is_keyword_match: boolean;
  matched_keyword?: string;
  status: "pending" | "replied" | "ignored";
  reply_content?: string;
  dm_sent: boolean;
  created_at?: string;
  replied_at?: string;
}

interface Stats {
  total_interactions: number;
  total_comments: number;
  total_dms: number;
  keyword_matches: number;
  auto_dms_sent: number;
  pending_count: number;
}

export default function InboxPage() {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [stats, setStats] = useState<Stats>({
    total_interactions: 0,
    total_comments: 0,
    total_dms: 0,
    keyword_matches: 0,
    auto_dms_sent: 0,
    pending_count: 0,
  });
  const [loading, setLoading] = useState(true);
  const [isChecking, setIsChecking] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [replyingToId, setReplyingToId] = useState<number | null>(null);
  const [replyMessage, setReplyMessage] = useState("");
  const [replyAsDm, setReplyAsDm] = useState(false);
  const [sendingReply, setSendingReply] = useState(false);
  const [notificationMsg, setNotificationMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [items, statsData] = await Promise.all([
        getInteractions(),
        getInteractionStats().catch(() => ({
          total_interactions: 0,
          total_comments: 0,
          total_dms: 0,
          keyword_matches: 0,
          auto_dms_sent: 0,
          pending_count: 0,
        })),
      ]);
      setInteractions(items || []);
      setStats(statsData);
    } catch (err: any) {
      console.error("Failed to load interactions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000); // Auto-refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const handleCheckNow = async () => {
    try {
      setIsChecking(true);
      const res = await checkInteractionsNow();
      setNotificationMsg({
        type: "success",
        text: `Checked! Processed ${res.data?.comments_checked || 0} comments and ${res.data?.dms_checked || 0} DMs.`,
      });
      await fetchData();
      setTimeout(() => setNotificationMsg(null), 4000);
    } catch (err: any) {
      setNotificationMsg({ type: "error", text: err.message || "Failed to check Instagram interactions." });
      setTimeout(() => setNotificationMsg(null), 4000);
    } finally {
      setIsChecking(false);
    }
  };

  const handleSendReply = async (id: number) => {
    if (!replyMessage.trim()) return;
    try {
      setSendingReply(true);
      await replyToInteraction(id, replyMessage.trim(), replyAsDm);
      setNotificationMsg({ type: "success", text: "Reply sent successfully!" });
      setReplyingToId(null);
      setReplyMessage("");
      await fetchData();
      setTimeout(() => setNotificationMsg(null), 3000);
    } catch (err: any) {
      setNotificationMsg({ type: "error", text: err.message || "Failed to send reply." });
      setTimeout(() => setNotificationMsg(null), 3000);
    } finally {
      setSendingReply(false);
    }
  };

  const handleIgnore = async (id: number) => {
    try {
      await ignoreInteraction(id);
      setInteractions((prev) =>
        prev.map((item) => (item.id === id ? { ...item, status: "ignored" } : item))
      );
    } catch (err: any) {
      console.error("Failed to ignore interaction:", err);
    }
  };

  // Filtered interactions
  const filteredInteractions = interactions.filter((item) => {
    if (typeFilter === "comment" && item.type !== "comment") return false;
    if (typeFilter === "dm" && item.type !== "dm") return false;
    if (typeFilter === "keyword" && !item.is_keyword_match) return false;
    if (statusFilter !== "all" && item.status !== statusFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchSender = (item.sender_username || "").toLowerCase().includes(q);
      const matchContent = item.content.toLowerCase().includes(q);
      const matchKeyword = (item.matched_keyword || "").toLowerCase().includes(q);
      if (!matchSender && !matchContent && !matchKeyword) return false;
    }
    return true;
  });

  return (
    <div className="space-y-8">
        {/* Toast Notification */}
        {notificationMsg && (
          <div
            className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3 rounded-xl backdrop-blur-xl border shadow-2xl transition-all duration-300 ${
              notificationMsg.type === "success"
                ? "bg-emerald-950/80 border-emerald-500/30 text-emerald-300 shadow-emerald-950/50"
                : "bg-rose-950/80 border-rose-500/30 text-rose-300 shadow-rose-950/50"
            }`}
          >
            {notificationMsg.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            )}
            <span className="text-sm font-medium">{notificationMsg.text}</span>
          </div>
        )}

        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-purple-500/15 text-purple-300 border border-purple-500/30">
                Autonomous Engagement
              </span>
              <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Checking Active
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Inbox & Auto-DM Hub
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl">
              Monitor Instagram comments and direct messages in real time. Whenever a user comments with your CTA keyword, your AI automatically delivers the lead-magnet via Private DM.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleCheckNow}
              disabled={isChecking}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-semibold shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${isChecking ? "animate-spin" : ""}`} />
              {isChecking ? "Checking Instagram..." : "Check Now"}
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5 sm:gap-4">
          <div className="glass-card p-4 sm:p-5 rounded-2xl border border-white/[0.08]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">Total Checked</span>
              <div className="w-8 h-8 rounded-xl bg-slate-800/80 border border-white/[0.08] flex items-center justify-center">
                <InboxIcon className="w-4 h-4 text-slate-300" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white">{stats.total_interactions}</div>
            <div className="text-[11px] text-slate-500 mt-1">Comments & DMs stored</div>
          </div>

          <div className="glass-card p-4 sm:p-5 rounded-2xl border border-white/[0.08]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">Post Comments</span>
              <div className="w-8 h-8 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                <MessageCircle className="w-4 h-4 text-blue-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white">{stats.total_comments}</div>
            <div className="text-[11px] text-blue-400/80 mt-1">Public interactions</div>
          </div>

          <div className="glass-card p-4 sm:p-5 rounded-2xl border border-white/[0.08]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">Direct Messages</span>
              <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                <MessageSquare className="w-4 h-4 text-cyan-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white">{stats.total_dms}</div>
            <div className="text-[11px] text-cyan-400/80 mt-1">Private messages</div>
          </div>

          <div className="glass-card p-4 sm:p-5 rounded-2xl border border-purple-500/20 bg-gradient-to-b from-purple-950/20 to-transparent">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-purple-300">Keyword Triggers</span>
              <div className="w-8 h-8 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                <Zap className="w-4 h-4 text-purple-300" />
              </div>
            </div>
            <div className="text-2xl font-bold text-purple-200">{stats.keyword_matches}</div>
            <div className="text-[11px] text-purple-400 mt-1">Matched CTA prompts</div>
          </div>

          <div className="glass-card p-4 sm:p-5 rounded-2xl border border-emerald-500/20 bg-gradient-to-b from-emerald-950/20 to-transparent col-span-2 lg:col-span-1">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-emerald-300">Auto-DMs Sent</span>
              <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-emerald-300" />
              </div>
            </div>
            <div className="text-2xl font-bold text-emerald-300">{stats.auto_dms_sent}</div>
            <div className="text-[11px] text-emerald-400 mt-1">Lead magnets delivered</div>
          </div>
        </div>

        {/* Filters & Search Bar */}
        <div className="glass-panel p-4 rounded-2xl border border-white/[0.08] flex flex-col sm:flex-row gap-3 items-center justify-between">
          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => setTypeFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                typeFilter === "all"
                  ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                  : "bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setTypeFilter("comment")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                typeFilter === "comment"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                  : "bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]"
              }`}
            >
              <MessageCircle className="w-3.5 h-3.5" />
              Comments
            </button>
            <button
              onClick={() => setTypeFilter("dm")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                typeFilter === "dm"
                  ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/30"
                  : "bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]"
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Direct Messages
            </button>
            <button
              onClick={() => setTypeFilter("keyword")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                typeFilter === "keyword"
                  ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md shadow-purple-600/30"
                  : "bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]"
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              Keyword Triggers 🎯
            </button>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search handle or text..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-slate-300 focus:outline-none focus:border-purple-500/50 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="replied">Replied</option>
              <option value="ignored">Ignored</option>
            </select>
          </div>
        </div>

        {/* Feed of Interactions */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-500">
            <RefreshCw className="w-8 h-8 animate-spin text-purple-400" />
            <p className="text-sm font-medium">Syncing Instagram interactions...</p>
          </div>
        ) : filteredInteractions.length === 0 ? (
          <div className="glass-card rounded-2xl p-12 text-center border border-white/[0.08] max-w-2xl mx-auto space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto text-purple-400">
              <MessageSquare className="w-7 h-7" />
            </div>
            <h3 className="text-lg font-bold text-white">No interactions found</h3>
            <p className="text-sm text-slate-400">
              {typeFilter !== "all" || statusFilter !== "all" || searchQuery
                ? "No interactions match your active filter criteria."
                : "When your Instagram audience comments on your carousels or sends DMs, they will appear here. The AI continuously checks every 5 minutes and automatically delivers your lead magnets!"}
            </p>
            <div className="pt-2">
              <button
                onClick={handleCheckNow}
                disabled={isChecking}
                className="px-4 py-2 rounded-xl bg-white/[0.08] hover:bg-white/[0.12] text-sm text-slate-200 font-medium transition-colors cursor-pointer"
              >
                {isChecking ? "Checking now..." : "Run Manual Check Now"}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-3.5">
            {filteredInteractions.map((item) => (
              <div
                key={item.id}
                className={`glass-card rounded-2xl p-5 border transition-all duration-200 ${
                  item.is_keyword_match
                    ? "border-purple-500/30 bg-purple-950/[0.08] hover:border-purple-500/50"
                    : "border-white/[0.08] hover:border-white/[0.15]"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  {/* Left: Avatar, Username, Badges */}
                  <div className="flex items-start gap-3.5">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 ${
                        item.type === "comment"
                          ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                          : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                      }`}
                    >
                      {item.type === "comment" ? (
                        <MessageCircle className="w-5 h-5" />
                      ) : (
                        <MessageSquare className="w-5 h-5" />
                      )}
                    </div>

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-white text-sm">
                          @{item.sender_username || "instagram_user"}
                        </span>

                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                            item.type === "comment"
                              ? "bg-blue-500/15 text-blue-400 border border-blue-500/25"
                              : "bg-cyan-500/15 text-cyan-400 border border-cyan-500/25"
                          }`}
                        >
                          {item.type === "comment" ? "Post Comment" : "Direct Message"}
                        </span>

                        {item.is_keyword_match && (
                          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/35">
                            <Zap className="w-3 h-3 text-amber-400 fill-amber-400" />
                            Trigger: &ldquo;{item.matched_keyword}&rdquo;
                          </span>
                        )}

                        {item.dm_sent && (
                          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                            <CheckCircle2 className="w-3 h-3" />
                            Auto-DM Delivered
                          </span>
                        )}

                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            item.status === "replied"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : item.status === "ignored"
                              ? "bg-slate-800 text-slate-400 border border-white/[0.08]"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}
                        >
                          {item.status.toUpperCase()}
                        </span>
                      </div>

                      {/* Content */}
                      <p className="text-sm text-slate-200 mt-1 leading-relaxed bg-black/30 p-3 rounded-xl border border-white/[0.04]">
                        {item.content}
                      </p>

                      {/* Replied content preview */}
                      {item.reply_content && (
                        <div className="flex items-start gap-2 text-xs text-slate-300 mt-2 bg-purple-950/20 border border-purple-500/20 rounded-xl p-3">
                          <CornerDownRight className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                          <div className="space-y-0.5">
                            <div className="font-semibold text-purple-300">
                              {item.dm_sent ? "Automated Private Reply DM:" : "Public Comment Reply:"}
                            </div>
                            <p className="text-slate-300">{item.reply_content}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right: Actions */}
                  <div className="flex items-center gap-2 shrink-0 sm:self-start">
                    {item.status !== "replied" && (
                      <button
                        onClick={() => {
                          setReplyingToId(replyingToId === item.id ? null : item.id);
                          setReplyAsDm(item.type === "comment");
                        }}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 border border-purple-500/30 text-xs font-semibold transition-all cursor-pointer"
                      >
                        <Send className="w-3.5 h-3.5" />
                        Reply
                      </button>
                    )}

                    {item.status === "pending" && (
                      <button
                        onClick={() => handleIgnore(item.id)}
                        className="px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-slate-200 text-xs font-semibold transition-colors cursor-pointer"
                      >
                        Dismiss
                      </button>
                    )}
                  </div>
                </div>

                {/* Inline Reply Composer */}
                {replyingToId === item.id && (
                  <div className="mt-4 pt-4 border-t border-white/[0.08] space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                        <Send className="w-3.5 h-3.5 text-purple-400" />
                        Reply to @{item.sender_username}
                      </span>

                      {item.type === "comment" && (
                        <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={replyAsDm}
                            onChange={(e) => setReplyAsDm(e.target.checked)}
                            className="rounded border-slate-700 text-purple-600 focus:ring-purple-500"
                          />
                          <span>Send as Private Reply DM</span>
                        </label>
                      )}
                    </div>

                    <textarea
                      rows={2}
                      value={replyMessage}
                      onChange={(e) => setReplyMessage(e.target.value)}
                      placeholder={
                        replyAsDm
                          ? "Type private DM message (e.g., 'Hey! Here is the free toolkit link...')"
                          : "Type public comment reply..."
                      }
                      className="w-full p-3 rounded-xl bg-black/40 border border-white/[0.12] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
                    />

                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => {
                          setReplyingToId(null);
                          setReplyMessage("");
                        }}
                        className="px-3 py-1.5 rounded-lg bg-white/[0.04] text-slate-400 text-xs font-semibold hover:bg-white/[0.08]"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleSendReply(item.id)}
                        disabled={sendingReply || !replyMessage.trim()}
                        className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-semibold shadow-md shadow-purple-600/30"
                      >
                        <Send className="w-3.5 h-3.5" />
                        {sendingReply ? "Sending..." : "Send Reply"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
    </div>
  );
}
