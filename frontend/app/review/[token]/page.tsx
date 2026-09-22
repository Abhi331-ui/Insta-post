"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getPublicReview, submitReviewAction, getPublicExportPdfUrl } from "@/lib/api";
import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  MessageSquare,
  Sparkles,
  Calendar,
  Share2,
  Copy,
  Check,
  Clock,
  Send,
  AlertCircle,
  Loader2,
} from "lucide-react";

export default function ClientReviewPage() {
  const params = useParams();
  const token = params?.token as string;

  const [post, setPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeSlide, setActiveSlide] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState("");
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [copiedCaption, setCopiedCaption] = useState(false);

  useEffect(() => {
    if (token) {
      loadReview();
    }
  }, [token]);

  const loadReview = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getPublicReview(token);
      setPost(data);
    } catch (e: any) {
      setError(e.message || "This review link is invalid or has expired.");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      setSubmitting(true);
      const res = await submitReviewAction(token, "approve");
      setActionSuccess(res.message || "Carousel approved! It will be published as scheduled.");
      await loadReview();
    } catch (e: any) {
      alert("Error approving carousel: " + e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRequestChanges = async () => {
    if (!feedbackText.trim()) {
      alert("Please provide some feedback on what you would like changed.");
      return;
    }
    try {
      setSubmitting(true);
      const res = await submitReviewAction(token, "request_changes", feedbackText);
      setShowFeedbackModal(false);
      setActionSuccess(res.message || "Feedback submitted! The team will update the carousel.");
      await loadReview();
    } catch (e: any) {
      alert("Error submitting feedback: " + e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const copyCaption = () => {
    if (!post?.caption) return;
    const fullText = `${post.caption}\n\n${post.hashtags || ""}`.trim();
    navigator.clipboard.writeText(fullText);
    setCopiedCaption(true);
    setTimeout(() => setCopiedCaption(false), 2500);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090D16] text-white flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-slate-400 text-sm font-medium">Loading carousel preview...</p>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-[#090D16] text-white flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-2xl bg-rose-950/40 border border-rose-900/50 flex items-center justify-center text-rose-400 mb-4">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">Link Expired or Not Found</h1>
        <p className="text-slate-400 text-sm max-w-md mb-6">{error}</p>
        <p className="text-xs text-slate-500">Please contact the creator who shared this link with you.</p>
      </div>
    );
  }

  const slides = post.slides || [];
  const currentSlide = slides[activeSlide] || null;
  const isApproved = post.status === "approved" || post.status === "scheduled" || post.status === "published";
  const needsChanges = post.status === "needs_changes";

  return (
    <div className="min-h-screen bg-[#090D16] text-white flex flex-col">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-30 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center text-white font-black text-sm shadow-md">
              P
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Content Review</span>
              <h1 className="text-sm font-bold text-slate-200 line-clamp-1">{post.topic}</h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href={getPublicExportPdfUrl(token)}
              download
              className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors border border-slate-700"
            >
              <Download className="w-3.5 h-3.5" />
              Download PDF
            </a>

            {isApproved ? (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Approved
              </span>
            ) : needsChanges ? (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                Changes Requested
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-500/15 text-blue-400 border border-blue-500/30 flex items-center gap-1.5">
                Pending Your Review
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto w-full px-4 sm:px-6 py-8 flex-1 flex flex-col lg:flex-row gap-8 items-start">
        {/* Left: Interactive Carousel Preview */}
        <div className="w-full lg:w-[480px] flex flex-col items-center shrink-0">
          <div className="relative w-full max-w-[420px] aspect-[4/5] bg-black rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex items-center justify-center group">
            {currentSlide?.image_url ? (
              <img
                src={currentSlide.image_url}
                alt={`Slide ${activeSlide + 1}`}
                className="w-full h-full object-cover select-none"
              />
            ) : (
              <div className="p-8 text-center text-slate-400 flex flex-col items-center gap-2">
                <Sparkles className="w-8 h-8 text-blue-400 animate-pulse" />
                <p className="text-sm font-semibold">{currentSlide?.headline || `Slide ${activeSlide + 1}`}</p>
                <p className="text-xs text-slate-500">{currentSlide?.body_text}</p>
              </div>
            )}

            {/* Navigation Arrows */}
            {activeSlide > 0 && (
              <button
                onClick={() => setActiveSlide((prev) => prev - 1)}
                className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/60 hover:bg-black/80 text-white backdrop-blur-md flex items-center justify-center border border-white/10 transition-all opacity-80 hover:opacity-100 shadow-lg"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
            )}
            {activeSlide < slides.length - 1 && (
              <button
                onClick={() => setActiveSlide((prev) => prev + 1)}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/60 hover:bg-black/80 text-white backdrop-blur-md flex items-center justify-center border border-white/10 transition-all opacity-80 hover:opacity-100 shadow-lg"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            )}

            {/* Slide Counter Overlay */}
            <div className="absolute top-4 right-4 px-2.5 py-1 rounded-full bg-black/70 backdrop-blur-md text-[11px] font-mono font-bold text-slate-300 border border-white/10">
              {activeSlide + 1} / {slides.length}
            </div>
          </div>

          {/* Slide Pagination Dots */}
          <div className="flex items-center gap-2 mt-4">
            {slides.map((_: any, idx: number) => (
              <button
                key={idx}
                onClick={() => setActiveSlide(idx)}
                className={`h-2 rounded-full transition-all ${
                  idx === activeSlide ? "w-8 bg-blue-500" : "w-2 bg-slate-700 hover:bg-slate-600"
                }`}
                title={`Go to slide ${idx + 1}`}
              />
            ))}
          </div>

          {/* Slide Thumbnail Strip */}
          <div className="grid grid-cols-6 gap-2 w-full max-w-[420px] mt-4">
            {slides.map((s: any, idx: number) => (
              <button
                key={idx}
                onClick={() => setActiveSlide(idx)}
                className={`aspect-[4/5] rounded-lg overflow-hidden border-2 transition-all ${
                  idx === activeSlide
                    ? "border-blue-500 scale-105 shadow-md"
                    : "border-slate-800 opacity-60 hover:opacity-100"
                }`}
              >
                {s.image_url ? (
                  <img src={s.image_url} alt="" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full bg-slate-900 flex items-center justify-center text-[10px] font-bold text-slate-400">
                    {idx + 1}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Right: Review Details & Actions */}
        <div className="flex-1 w-full space-y-6">
          {/* Status Feedback Banner */}
          {actionSuccess && (
            <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-900/50 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-bold text-emerald-300">{actionSuccess}</p>
                <p className="text-xs text-emerald-400/80 mt-0.5">Thank you for reviewing your content.</p>
              </div>
            </div>
          )}

          {post.client_feedback && (
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3">
              <MessageSquare className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Client Feedback</p>
                <p className="text-sm text-slate-200 mt-1">{post.client_feedback}</p>
              </div>
            </div>
          )}

          {/* Action Card for Client */}
          <div className="p-6 rounded-2xl bg-[#0F172A] border border-slate-800 shadow-xl space-y-4">
            <div>
              <h2 className="text-lg font-bold text-white">Approve this Carousel</h2>
              <p className="text-xs text-slate-400 mt-1">
                Review the slides and caption. Once approved, this post will be scheduled for auto-publishing.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
              <button
                onClick={handleApprove}
                disabled={submitting || isApproved}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white text-sm font-bold shadow-lg shadow-emerald-600/25 active:scale-95 transition-all disabled:opacity-60"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                {isApproved ? "Already Approved" : "Approve Carousel"}
              </button>

              <button
                onClick={() => setShowFeedbackModal(true)}
                disabled={submitting}
                className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold border border-slate-700 transition-colors"
              >
                <MessageSquare className="w-4 h-4" />
                Request Changes
              </button>
            </div>
          </div>

          {/* Monetization / Comment-to-DM Highlight */}
          {post.dm_keyword && (
            <div className="p-5 rounded-2xl bg-gradient-to-r from-purple-950/40 via-indigo-950/30 to-blue-950/40 border border-purple-800/40 space-y-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-bold text-white">Comment-to-DM Lead Magnet Active</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                When viewers comment <span className="font-mono font-bold text-purple-300 bg-purple-900/50 px-1.5 py-0.5 rounded">"{post.dm_keyword}"</span> on Instagram, they receive this automated resource message:
              </p>
              {post.dm_message && (
                <div className="p-3 rounded-xl bg-slate-950/60 border border-purple-900/30 text-xs font-mono text-purple-200">
                  {post.dm_message}
                </div>
              )}
            </div>
          )}

          {/* Post Caption & Details */}
          <div className="p-6 rounded-2xl bg-[#0F172A] border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-blue-400" />
                Caption & Copy
              </h3>
              <button
                onClick={copyCaption}
                className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors font-medium"
              >
                {copiedCaption ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copiedCaption ? "Copied!" : "Copy Full Caption"}
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto font-sans">
              {post.caption || "No caption generated."}
            </div>

            {post.hashtags && (
              <div className="text-xs text-blue-400 font-mono leading-relaxed break-words">
                {post.hashtags}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">Request Changes</h3>
            <p className="text-xs text-slate-400">
              Let the creator know what adjustments you would like (e.g., change slide 3 headline, adjust caption tone).
            </p>

            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="e.g. Please update slide 4 to focus more on our pricing structure..."
              className="w-full h-32 bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none"
            />

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowFeedbackModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleRequestChanges}
                disabled={submitting}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                Submit Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
