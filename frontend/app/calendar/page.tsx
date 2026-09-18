"use client";

import { useEffect, useState } from "react";
import ContentCalendar from "@/components/ContentCalendar";
import { getCalendar, getPost } from "@/lib/api";
import SlidePreview from "@/components/SlidePreview";
import WhyThisPost from "@/components/WhyThisPost";
import { X, Calendar as CalendarIcon } from "lucide-react";

export default function CalendarPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadCalendar = async () => {
    try {
      setLoading(true);
      const data = await getCalendar();
      setEvents(data);
    } catch (err) {
      console.error("Error loading calendar:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCalendar();
  }, []);

  const handleSelectEvent = async (postId: number) => {
    try {
      const post = await getPost(postId);
      setSelectedPost(post);
    } catch (e: any) {
      alert("Error loading post: " + e.message);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <CalendarIcon className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Content Schedule</span>
        </div>
        <h1 className="text-3xl font-black text-white tracking-tight">Content Calendar</h1>
        <p className="text-sm text-slate-400 mt-1">
          Visual overview of published, scheduled, and pending 6-slide carousels across all content pillars.
        </p>
      </div>

      {loading ? (
        <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-medium">Loading content calendar...</p>
        </div>
      ) : (
        <ContentCalendar events={events} onSelectEvent={handleSelectEvent} />
      )}

      {/* Selected Post Modal / Drawer */}
      {selectedPost && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          <div className="bg-[#0F172A] border border-slate-800 rounded-3xl max-w-4xl w-full p-6 relative shadow-2xl max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedPost(null)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start mt-4">
              <SlidePreview postId={selectedPost.id} slides={selectedPost.slides || []} />
              <WhyThisPost post={selectedPost} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
