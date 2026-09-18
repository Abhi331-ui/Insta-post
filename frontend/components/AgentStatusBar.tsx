"use client";

import { useEffect, useState } from "react";
import { Search, BarChart2, Compass, PenTool, FileText, CheckCircle2, Image as ImageIcon, ShieldCheck, AlertCircle } from "lucide-react";

interface PipelineState {
  status: string;
  current_step: string;
  step_index: number;
  total_steps: number;
  message: string;
  updated_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

export default function AgentStatusBar() {
  const [state, setState] = useState<PipelineState>({
    status: "idle",
    current_step: "Idle",
    step_index: 0,
    total_steps: 10,
    message: "PromptPulse autonomous engine is ready. Next discovery scheduled for 09:00 UTC.",
    updated_at: new Date().toISOString(),
  });

  useEffect(() => {
    const eventSource = new EventSource(`${API_BASE}/agent-status`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setState(data);
      } catch (err) {
        console.error("Failed to parse SSE pipeline state:", err);
      }
    };

    eventSource.onerror = () => {
      // EventSource reconnects automatically
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const steps = [
    { name: "Research", icon: Search, index: 1 },
    { name: "Score", icon: BarChart2, index: 2 },
    { name: "Strategy", icon: Compass, index: 3 },
    { name: "Content", icon: PenTool, index: 4 },
    { name: "Copy", icon: FileText, index: 5 },
    { name: "FactCheck", icon: CheckCircle2, index: 6 },
    { name: "Design", icon: ImageIcon, index: 7 },
    { name: "QA", icon: ShieldCheck, index: 8 },
  ];

  const isRunning = state.status === "running";
  const isNoOpp = state.status === "no_opportunity";
  const isError = state.status === "failed";

  return (
    <div className="w-full bg-[#0F172A] border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <span
              className={`w-3.5 h-3.5 rounded-full block ${
                isRunning
                  ? "bg-blue-500 animate-ping"
                  : isNoOpp
                  ? "bg-amber-500"
                  : isError
                  ? "bg-rose-500"
                  : "bg-emerald-500"
              }`}
            />
            <span
              className={`w-3.5 h-3.5 rounded-full absolute top-0 left-0 ${
                isRunning
                  ? "bg-blue-500"
                  : isNoOpp
                  ? "bg-amber-500"
                  : isError
                  ? "bg-rose-500"
                  : "bg-emerald-500"
              }`}
            />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider font-bold text-slate-400">
              Autonomous Pipeline Status
            </div>
            <div className="text-white text-sm font-semibold flex items-center gap-2">
              {state.current_step ? state.current_step : "Ready"}
              {isRunning && <span className="text-xs text-blue-400 font-normal">({state.step_index}/10)</span>}
            </div>
          </div>
        </div>

        <div className="text-xs text-slate-400 bg-slate-900/90 border border-slate-800 px-3.5 py-1.5 rounded-lg max-w-xl truncate">
          <span className="text-slate-500 font-mono mr-2">LOG:</span>
          {state.message}
        </div>
      </div>

      {/* Visual step pipeline tracker */}
      <div className="grid grid-cols-4 sm:grid-cols-8 gap-2 pt-2 border-t border-slate-800/80">
        {steps.map((step) => {
          const Icon = step.icon;
          const isDone = state.step_index > step.index;
          const isCurrent = state.step_index === step.index && isRunning;

          return (
            <div
              key={step.name}
              className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all ${
                isCurrent
                  ? "bg-blue-600/20 border border-blue-500 text-blue-400"
                  : isDone
                  ? "bg-slate-900 border border-slate-800 text-slate-300"
                  : "bg-slate-950/40 border border-slate-900 text-slate-600"
              }`}
            >
              <Icon className={`w-4 h-4 mb-1 ${isCurrent ? "animate-bounce" : ""}`} />
              <span className="text-[11px] font-medium tracking-tight">{step.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
