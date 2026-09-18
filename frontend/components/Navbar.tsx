"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sparkles,
  Calendar,
  LayoutGrid,
  BarChart3,
  Settings,
  Play,
  ListOrdered,
  Bell,
  Check,
  ArrowRight,
  X,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { runAgentNow, getNotifications, markAllNotificationsRead, markNotificationRead } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [isRunning, setIsRunning] = useState(false);
  const [runMessage, setRunMessage] = useState("");
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchNotifs = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (_) {}
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 10000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleRunNow = async () => {
    try {
      setIsRunning(true);
      await runAgentNow();
      setRunMessage("Agent triggered!");
      setTimeout(() => setRunMessage(""), 4000);
    } catch (e: any) {
      setRunMessage("Error: " + e.message);
      setTimeout(() => setRunMessage(""), 4000);
    } finally {
      setIsRunning(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    window.location.href = "/login";
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setUnreadCount(0);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (_) {}
  };

  const handleNotificationClick = async (notif: any) => {
    try {
      if (!notif.is_read) {
        await markNotificationRead(notif.id);
        setUnreadCount((c) => Math.max(0, c - 1));
        setNotifications((prev) =>
          prev.map((n) => (n.id === notif.id ? { ...n, is_read: true } : n))
        );
      }
      setShowDropdown(false);
    } catch (_) {}
  };

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: Sparkles },
    { name: "Topic Queue", href: "/queue", icon: ListOrdered },
    { name: "Calendar", href: "/calendar", icon: Calendar },
    { name: "Posts", href: "/posts", icon: LayoutGrid },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#0F172A]/95 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-transform">
              <span className="text-white font-black text-lg">P</span>
            </div>
            <div>
              <div className="text-white font-bold text-lg tracking-tight flex items-center gap-1.5">
                PromptPulse
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
              </div>
              <div className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">
                Autonomous Agent
              </div>
            </div>
          </Link>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-blue-600/15 text-blue-400 border border-blue-500/30"
                      : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right action controls */}
        <div className="flex items-center gap-3">
          {runMessage && (
            <span className="text-xs text-blue-400 bg-blue-950/60 border border-blue-800/60 px-3 py-1 rounded-full animate-fade-in">
              {runMessage}
            </span>
          )}

          {/* Notification Bell with Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => {
                setShowDropdown(!showDropdown);
                fetchNotifs();
              }}
              className="relative p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-colors"
              title="Daily reminders & publish alerts"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 bg-rose-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center shadow-lg shadow-rose-500/40 animate-pulse">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notification Dropdown Menu */}
            {showDropdown && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-[#0F172A] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden z-50 flex flex-col">
                <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Notifications
                    </span>
                    {unreadCount > 0 && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                        {unreadCount} new
                      </span>
                    )}
                  </div>
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      className="text-[11px] text-slate-400 hover:text-blue-400 font-medium transition-colors"
                    >
                      Mark all read
                    </button>
                  )}
                </div>

                <div className="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
                  {notifications.length === 0 ? (
                    <div className="p-6 text-center text-xs text-slate-500">
                      No notifications yet. You will be notified here immediately after each carousel publishes.
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        onClick={() => handleNotificationClick(n)}
                        className={`p-3.5 hover:bg-slate-900/80 transition-colors cursor-pointer flex flex-col gap-1.5 ${
                          !n.is_read ? "bg-blue-950/15" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="text-xs font-bold text-white leading-tight">
                            {n.title}
                          </span>
                          {!n.is_read && (
                            <span className="w-2 h-2 rounded-full bg-blue-500 shrink-0 mt-1" />
                          )}
                        </div>

                        <p className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-line">
                          {n.message}
                        </p>

                        <div className="flex items-center justify-between pt-1 mt-1 text-[10px] text-slate-500">
                          <span>{n.time_display}</span>
                          <Link
                            href={n.link || "/queue"}
                            onClick={() => setShowDropdown(false)}
                            className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1"
                          >
                            Make Ready Next 10 Ideas <ArrowRight className="w-3 h-3" />
                          </Link>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Dropdown Footer */}
                <div className="p-2.5 bg-slate-950/80 border-t border-slate-800 text-center">
                  <Link
                    href="/queue"
                    onClick={() => setShowDropdown(false)}
                    className="text-xs font-semibold text-blue-400 hover:text-blue-300 inline-flex items-center gap-1"
                  >
                    Open Topic Queue & Refill Tracker →
                  </Link>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleRunNow}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${isRunning ? "animate-spin" : "fill-white"}`} />
            {isRunning ? "Agent Running..." : "Run Discovery"}
          </button>

          <button
            type="button"
            onClick={handleLogout}
            className="px-3 py-2 rounded-lg border border-slate-700 bg-slate-900 text-sm text-slate-200 hover:bg-slate-800 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
