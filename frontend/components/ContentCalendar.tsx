"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, Layers } from "lucide-react";

interface CalendarEvent {
  id: number;
  topic: string;
  hook: string;
  content_pillar: string;
  pillar_color: string;
  status: string;
  date: string; // YYYY-MM-DD
  time: string; // HH:MM
  slides_count: number;
}

interface ContentCalendarProps {
  events: CalendarEvent[];
  onSelectEvent?: (eventId: number) => void;
}

export default function ContentCalendar({ events, onSelectEvent }: ContentCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const daysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = (year: number, month: number) => new Date(year, month, 1).getDay();

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const totalDays = daysInMonth(year, month);
  const startDay = firstDayOfMonth(year, month);

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  // Group events by day
  const eventsByDate: Record<string, CalendarEvent[]> = {};
  events.forEach((ev) => {
    if (!eventsByDate[ev.date]) eventsByDate[ev.date] = [];
    eventsByDate[ev.date].push(ev);
  });

  const getStatusColor = (st: string) => {
    switch (st) {
      case "published": return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
      case "scheduled": return "bg-blue-500/20 text-blue-400 border-blue-500/40";
      case "pending_approval": return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      case "failed": return "bg-rose-500/20 text-rose-400 border-rose-500/40";
      default: return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <CalendarIcon className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            {monthNames[month]} {year}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevMonth}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={handleNextMonth}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Weekday Names */}
      <div className="grid grid-cols-7 gap-2 mb-2 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div key={day} className="py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Days Grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Empty padding cells for start of month */}
        {Array.from({ length: startDay }).map((_, i) => (
          <div key={`empty-${i}`} className="min-h-[110px] rounded-xl bg-slate-950/40 border border-slate-900/60 p-2 opacity-30" />
        ))}

        {/* Day cells */}
        {Array.from({ length: totalDays }).map((_, i) => {
          const dayNum = i + 1;
          const formattedDate = `${year}-${String(month + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
          const dayEvents = eventsByDate[formattedDate] || [];
          const isToday = new Date().toISOString().slice(0, 10) === formattedDate;

          return (
            <div
              key={dayNum}
              className={`min-h-[110px] rounded-xl border p-2 flex flex-col justify-between transition-all ${
                isToday
                  ? "bg-blue-950/20 border-blue-500/50"
                  : "bg-slate-900/50 border-slate-800/80 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-bold ${isToday ? "text-blue-400" : "text-slate-400"}`}>
                  {dayNum}
                </span>
                {dayEvents.length > 0 && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                    {dayEvents.length}
                  </span>
                )}
              </div>

              {/* Event cards */}
              <div className="flex flex-col gap-1.5 overflow-y-auto max-h-[80px]">
                {dayEvents.map((ev) => (
                  <div
                    key={ev.id}
                    onClick={() => onSelectEvent && onSelectEvent(ev.id)}
                    className="p-1.5 rounded-lg bg-slate-950/80 border border-slate-800 hover:border-blue-500/50 cursor-pointer transition-all text-left group"
                  >
                    <div className="flex items-center gap-1.5 mb-1">
                      <span
                        className="w-2 h-2 rounded-full shrink-0"
                        style={{ backgroundColor: ev.pillar_color || "#2563EB" }}
                      />
                      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border uppercase tracking-wider ${getStatusColor(ev.status)}`}>
                        {ev.status.replace("_", " ")}
                      </span>
                    </div>
                    <p className="text-[11px] font-medium text-slate-200 line-clamp-1 group-hover:text-blue-400">
                      {ev.topic}
                    </p>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                      <span className="flex items-center gap-0.5">
                        <Clock className="w-2.5 h-2.5" />
                        {ev.time}
                      </span>
                      <span>• 6 slides</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
