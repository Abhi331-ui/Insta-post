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
  MessageSquare,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { runAgentNow, getNotifications, markAllNotificationsRead, markNotificationRead } from "@/lib/api";
import CreateCarouselModal from "@/components/CreateCarouselModal";

export default function Navbar() {
  const pathname = usePathname();
  const [isRunning, setIsRunning] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
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
    { name: "Inbox", href: "/inbox", icon: MessageSquare },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#030712]/80 backdrop-blur-xl border-b border-white/[0.08]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-purple-600/30 group-hover:scale-105 transition-transform">
              <span className="text-white font-black text-lg">P</span>
            </div>
            <div>
              <div className="text-white font-bold text-base tracking-tight flex items-center gap-2">
                PromptPulse
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[9px] font-bold tracking-wider uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Live
                </span>
              </div>
              <div className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">
                Autonomous Creator
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
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-white/[0.1] text-white border border-white/[0.15] shadow-sm shadow-black/40"
                      : "text-slate-400 hover:text-white hover:bg-white/[0.05]"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right action controls */}
        <div className="flex items-center gap-3">
          {runMessage && (
            <span className="text-xs text-purple-300 bg-purple-950/60 border border-purple-800/60 px-3 py-1 rounded-full animate-fade-in">
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
              className="relative p-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-300 hover:text-white transition-colors"
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
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-white/[0.1] rounded-2xl shadow-2xl overflow-hidden z-50 flex flex-col">
                <div className="p-3.5 border-b border-white/[0.08] flex items-center justify-between bg-black/40">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Notifications
                    </span>
                    {unreadCount > 0 && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        {unreadCount} new
                      </span>
                    )}
                  </div>
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      className="text-[11px] text-slate-400 hover:text-purple-400 font-medium transition-colors"
                    >
                      Mark all read
                    </button>
                  )}
                </div>

                <div className="max-h-80 overflow-y-auto divide-y divide-white/[0.05]">
                  {notifications.length === 0 ? (
                    <div className="p-6 text-center text-xs text-slate-500">
                      No notifications yet. You will be notified here immediately after each carousel publishes.
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        onClick={() => handleNotificationClick(n)}
                        className={`p-3.5 hover:bg-white/[0.04] transition-colors cursor-pointer flex flex-col gap-1.5 ${
                          !n.is_read ? "bg-purple-950/20" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="text-xs font-bold text-white leading-tight">
                            {n.title}
                          </span>
                          {!n.is_read && (
                            <span className="w-2 h-2 rounded-full bg-purple-500 shrink-0 mt-1" />
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
                            className="text-purple-400 hover:text-purple-300 font-bold flex items-center gap-1"
                          >
                            Make Ready Next 10 Ideas <ArrowRight className="w-3 h-3" />
                          </Link>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Dropdown Footer */}
                <div className="p-2.5 bg-black/40 border-t border-white/[0.08] text-center">
                  <Link
                    href="/queue"
                    onClick={() => setShowDropdown(false)}
                    className="text-xs font-semibold text-purple-400 hover:text-purple-300 inline-flex items-center gap-1"
                  >
                    Open Topic Queue & Refill Tracker →
                  </Link>
                </div>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-600/25 active:scale-95 transition-all whitespace-nowrap"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>✦ Create Carousel</span>
          </button>

          <button
            onClick={handleRunNow}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:opacity-95 text-white text-xs font-bold shadow-lg shadow-purple-600/25 active:scale-95 transition-all disabled:opacity-50 whitespace-nowrap"
          >
            <Play className={`w-3.5 h-3.5 ${isRunning ? "animate-spin" : "fill-white"}`} />
            {isRunning ? "Agent Running..." : "Run Discovery"}
          </button>

          <button
            type="button"
            onClick={handleLogout}
            className="px-3 py-2 rounded-xl border border-white/[0.08] bg-white/[0.04] text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/[0.08] transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      <CreateCarouselModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          if (window.location.pathname === "/dashboard" || window.location.pathname === "/posts") {
            window.location.reload();
          }
        }}
      />
    </header>
  );
}
