"use client";

import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, RefreshCw, ZoomIn, Layers } from "lucide-react";
import { regenerateSlide } from "@/lib/api";

interface Slide {
  id: number;
  slide_number: number;
  headline: string;
  body_text: string;
  layout_type: string;
  image_url: string;
  regenerated_count: number;
}

const formatLayoutType = (type: string) => {
  if (!type) return "Slide";
  const map: Record<string, string> = {
    hero: "Hero Classic",
    hero_editorial: "Hero Editorial",
    hero_terminal: "Hero Terminal",
    hero_badge: "Hero Badge",
    hero_minimal_bold: "Hero Minimal",
    hero_grid_matrix: "Hero Matrix",
    hero_magazine: "Hero Magazine",
    hero_blueprint: "Hero Blueprint",
    hero_gradient_punch: "Hero Gradient",
    hero_duotone: "Hero Duotone",
    tool_card: "Tool Card",
    showcase: "Use Cases",
    steps: "How It Works",
    comparison: "Real Examples",
    cta: "Save & Follow",
  };
  return map[type] || type.replace(/_/g, " ").toUpperCase();
};

interface SlidePreviewProps {
  postId: number;
  slides: Slide[];
  onSlideUpdated?: () => void;
}

export default function SlidePreview({ postId, slides, onSlideUpdated }: SlidePreviewProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [imgError, setImgError] = useState(false);

  // Reset slide index to slide 1 when post changes
  useEffect(() => {
    setCurrentIndex(0);
    setImgError(false);
  }, [postId]);

  if (!slides || slides.length === 0) {
    return (
      <div className="aspect-[4/5] w-full max-w-md mx-auto bg-slate-900 border border-slate-800 rounded-2xl flex flex-col items-center justify-center p-8 text-center text-slate-500">
        <Layers className="w-12 h-12 mb-3 text-slate-700 animate-pulse" />
        <p className="text-sm font-medium">No slides generated yet.</p>
        <p className="text-xs text-slate-600 mt-1">Run autonomous discovery to generate a 6-slide carousel.</p>
      </div>
    );
  }

  const currentSlide = slides[currentIndex] || slides[0];

  const handleNext = () => {
    setImgError(false);
    setCurrentIndex((prev) => (prev + 1) % slides.length);
  };

  const handlePrev = () => {
    setImgError(false);
    setCurrentIndex((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const handleRegenerateThisSlide = async () => {
    try {
      setIsRegenerating(true);
      await regenerateSlide(postId, currentSlide.slide_number);
      if (onSlideUpdated) onSlideUpdated();
    } catch (e: any) {
      alert("Error regenerating slide: " + e.message);
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full max-w-md mx-auto">
      {/* Slide frame (1080x1350 / 4:5 ratio) */}
      <div className="relative w-full aspect-[4/5] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl group flex items-center justify-center">
        {currentSlide.image_url && !imgError ? (
          <img
            key={`${currentSlide.id}-${currentSlide.slide_number}-${currentSlide.image_url}`}
            src={currentSlide.image_url}
            alt={currentSlide.headline || `Slide ${currentSlide.slide_number}`}
            className="w-full h-full object-cover select-none"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex flex-col justify-between p-8 bg-[#070913] text-white border border-purple-500/20 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>
            <div className="flex justify-between items-center z-10">
              <span className="text-xs font-mono font-bold tracking-widest text-slate-400">0{currentSlide.slide_number} / 06</span>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {formatLayoutType(currentSlide.layout_type)}
              </span>
            </div>
            <div className="z-10 my-auto">
              <h2 className="text-2xl font-black leading-tight mb-3 text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-cyan-300">
                {currentSlide.headline}
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">{currentSlide.body_text}</p>
            </div>
            <div className="flex justify-between text-xs text-slate-400 font-semibold border-t border-slate-800/80 pt-4 z-10">
              <span className="text-purple-400 font-mono">1080×1350 HD</span>
              <span className="text-cyan-400">• PromptPulse</span>
            </div>
          </div>
        )}

        {/* Carousel Prev/Next Overlay Buttons */}
        <button
          onClick={handlePrev}
          className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-slate-900/80 backdrop-blur-sm text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-800 border border-slate-700"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <button
          onClick={handleNext}
          className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-slate-900/80 backdrop-blur-sm text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-800 border border-slate-700"
        >
          <ChevronRight className="w-5 h-5" />
        </button>

        {/* Top Badges */}
        <div className="absolute top-4 left-4 flex gap-2">
          <span className="text-[11px] font-bold tracking-wider uppercase px-2.5 py-1 rounded-md bg-slate-900/80 backdrop-blur-md text-white border border-slate-700/50">
            Slide {currentSlide.slide_number} of 6
          </span>
          <span className="text-[11px] font-bold tracking-wider uppercase px-2.5 py-1 rounded-md bg-purple-600/90 text-white shadow-lg">
            {formatLayoutType(currentSlide.layout_type)}
          </span>
        </div>

        {/* Slide Zoom button */}
        {currentSlide.image_url && (
          <a
            href={currentSlide.image_url}
            target="_blank"
            rel="noopener noreferrer"
            className="absolute top-4 right-4 p-2 rounded-md bg-slate-900/80 backdrop-blur-md text-white hover:bg-slate-800 border border-slate-700/50"
            title="Inspect 1080x1350 PNG"
          >
            <ZoomIn className="w-4 h-4" />
          </a>
        )}
      </div>

      {/* Slide Navigation Dots & Quick Controls */}
      <div className="flex items-center justify-between w-full mt-4 px-2">
        <div className="flex items-center gap-1.5">
          {slides.map((s, idx) => (
            <button
              key={s.id || idx}
              onClick={() => setCurrentIndex(idx)}
              className={`transition-all rounded-full ${
                idx === currentIndex
                  ? "w-7 h-2 bg-blue-500"
                  : "w-2 h-2 bg-slate-700 hover:bg-slate-500"
              }`}
              title={`Jump to slide ${idx + 1}`}
            />
          ))}
        </div>

        {/* Targeted Single Slide Regeneration */}
        <button
          onClick={handleRegenerateThisSlide}
          disabled={isRegenerating}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? "animate-spin text-blue-400" : ""}`} />
          {isRegenerating ? "Regenerating..." : currentSlide.slide_number === 1 ? "Shuffle Hero Style" : "Regen This Slide"}
        </button>
      </div>
    </div>
  );
}
