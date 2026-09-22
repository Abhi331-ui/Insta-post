"use client";

import { useEffect, useState } from "react";
import {
  getSettings,
  updateSettings,
  connectInstagram,
  disconnectInstagram,
  connectTelegram,
  disconnectTelegram,
  testTelegram,
} from "@/lib/api";
import {
  Settings,
  Instagram,
  Sparkles,
  Clock,
  Palette,
  Sliders,
  Check,
  AlertCircle,
  Unlink,
  Shield,
  Loader2,
  CheckCircle2,
  Target,
  Send,
  MessageSquare,
  ExternalLink,
  BellRing,
} from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [connectError, setConnectError] = useState("");

  // Telegram states
  const [telegramChatId, setTelegramChatId] = useState("");
  const [telegramBotToken, setTelegramBotToken] = useState("");
  const [showAdvancedTelegram, setShowAdvancedTelegram] = useState(false);
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [telegramTesting, setTelegramTesting] = useState(false);
  const [telegramError, setTelegramError] = useState("");
  const [telegramSuccess, setTelegramSuccess] = useState("");

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await getSettings();

      // Ensure posting_times is an array
      let postingTimes = data.posting_times;
      if (typeof postingTimes === "string") {
        try {
          postingTimes = JSON.parse(postingTimes);
        } catch (_) {
          postingTimes = [data.posting_time || "09:00"];
        }
      }
      if (!Array.isArray(postingTimes)) {
        postingTimes = [data.posting_time || "09:00"];
      }
      data.posting_times = postingTimes;

      // Ensure active_days is an array
      let activeDays = data.active_days;
      if (typeof activeDays === "string") {
        try {
          activeDays = JSON.parse(activeDays);
        } catch (_) {
          activeDays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
        }
      }
      if (!Array.isArray(activeDays)) {
        activeDays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
      }
      data.active_days = activeDays;

      setSettings(data);
      if (data.telegram?.chat_id) {
        setTelegramChatId(data.telegram.chat_id);
      }
    } catch (e: any) {
      console.error("Error loading settings:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateSettings(settings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (e: any) {
      alert("Error saving settings: " + e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleConnectInstagram = async () => {
    try {
      setActionLoading(true);
      setConnectError("");
      const res = await connectInstagram();
      if (res.auth_url) {
        window.location.href = res.auth_url;
      }
    } catch (e: any) {
      setConnectError("Unable to connect Instagram right now. Please try again later or contact support.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm("Are you sure you want to disconnect your Instagram account? Your scheduled posts will stop publishing.")) return;
    try {
      setActionLoading(true);
      await disconnectInstagram();
      await loadSettings();
    } catch (e: any) {
      alert("Error disconnecting Instagram: " + e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleConnectTelegram = async () => {
    if (!telegramChatId.trim()) {
      setTelegramError("Please enter your Telegram Chat ID.");
      return;
    }
    try {
      setTelegramLoading(true);
      setTelegramError("");
      setTelegramSuccess("");
      await connectTelegram(telegramChatId.trim(), telegramBotToken.trim() || undefined);
      setTelegramSuccess("Connected! A welcome message has been sent to your Telegram.");
      await loadSettings();
    } catch (e: any) {
      setTelegramError(e.message || "Failed to connect Telegram. Please make sure you sent /start to the bot.");
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleDisconnectTelegram = async () => {
    if (!confirm("Are you sure you want to disconnect Telegram notifications?")) return;
    try {
      setTelegramLoading(true);
      setTelegramError("");
      setTelegramSuccess("");
      await disconnectTelegram();
      setTelegramChatId("");
      await loadSettings();
    } catch (e: any) {
      setTelegramError(e.message || "Failed to disconnect Telegram.");
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleTestTelegram = async () => {
    try {
      setTelegramTesting(true);
      setTelegramError("");
      setTelegramSuccess("");
      await testTelegram();
      setTelegramSuccess("Test notification sent! Check your Telegram.");
      setTimeout(() => setTelegramSuccess(""), 4000);
    } catch (e: any) {
      setTelegramError(e.message || "Failed to send test message.");
    } finally {
      setTelegramTesting(false);
    }
  };

  if (loading || !settings) {
    return (
      <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-3">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-medium">Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Settings className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Configuration</span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Settings</h1>
          <p className="text-sm text-slate-400 mt-1">
            Connect your Instagram, set your posting schedule, and customize your brand.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold shadow-lg shadow-blue-600/25 active:scale-95 transition-all disabled:opacity-50"
        >
          {saveSuccess ? <Check className="w-4 h-4" /> : null}
          {saving ? "Saving..." : saveSuccess ? "Saved!" : "Save Changes"}
        </button>
      </div>

      <div className="flex flex-col gap-6">
        {/* Instagram Account Connection — Simplified */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 flex items-center justify-center text-white shadow-lg">
                <Instagram className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Instagram Account</h3>
                <p className="text-xs text-slate-400">Connect to auto-publish carousels to your feed</p>
              </div>
            </div>

            {settings.instagram?.connected ? (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-3 h-3" />
                Connected
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                Not Connected
              </span>
            )}
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="text-xs text-slate-300">
              {settings.instagram?.connected ? (
                <div className="flex items-center gap-3">
                  {settings.instagram.profile_picture_url ? (
                    <img
                      src={settings.instagram.profile_picture_url}
                      alt="Profile"
                      className="w-10 h-10 rounded-full border border-slate-700 object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                      {(settings.instagram.username || settings.instagram.page_name || "IG").charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-bold text-slate-100 text-sm">{settings.instagram.page_name || "Instagram Account"}</p>
                      {settings.instagram.username && (
                        <span className="text-xs text-purple-400 font-semibold">@{settings.instagram.username}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
                        <Shield className="w-3 h-3" />
                        Verified & connected
                      </span>
                      {settings.instagram.token_expires_at && (
                        <span className="text-slate-500 text-[11px]">
                          · Renews {new Date(settings.instagram.token_expires_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <p className="font-semibold text-slate-200">Connect your Instagram to get started</p>
                  <p className="text-slate-400 mt-1 leading-relaxed">
                    Link your Instagram Professional account so the AI can automatically generate and publish carousels for you.
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2.5 shrink-0">
              {settings.instagram?.connected ? (
                <button
                  onClick={handleDisconnect}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-950/60 text-rose-300 border border-rose-900/50 text-xs font-semibold transition-colors disabled:opacity-50"
                >
                  <Unlink className="w-3.5 h-3.5" />
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={handleConnectInstagram}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 via-purple-600 to-indigo-600 hover:opacity-90 text-white text-sm font-bold shadow-lg shadow-purple-600/20 active:scale-95 transition-all disabled:opacity-60"
                >
                  {actionLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Instagram className="w-4 h-4" />
                  )}
                  {actionLoading ? "Connecting..." : "Connect Instagram"}
                </button>
              )}
            </div>
          </div>

          {/* Connection error */}
          {connectError && (
            <div className="flex items-center gap-2 mt-3 p-3 rounded-xl bg-rose-950/30 border border-rose-900/40">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span className="text-xs text-rose-300">{connectError}</span>
            </div>
          )}

          {/* What happens when connected */}
          {!settings.instagram?.connected && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
              {[
                { icon: "\u{1F916}", title: "AI generates carousels", desc: "Content created automatically from trending topics" },
                { icon: "\u{1F4CA}", title: "Virality scoring", desc: "Every post is scored before publishing" },
                { icon: "\u{1F4F1}", title: "Auto-publish", desc: "Posts go live at your scheduled times" },
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60">
                  <span className="text-lg">{item.icon}</span>
                  <div>
                    <p className="text-xs font-semibold text-slate-200">{item.title}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Telegram Notifications & Reminders */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center text-white shadow-lg">
                <Send className="w-5 h-5 -translate-x-0.5 translate-y-0.5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Telegram Reminders & Alerts</h3>
                <p className="text-xs text-slate-400">Get queue refill reminders and live post notifications on Telegram</p>
              </div>
            </div>

            {settings.telegram?.connected ? (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-3 h-3" />
                Connected
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                Not Connected
              </span>
            )}
          </div>

          {settings.telegram?.connected ? (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-bold text-slate-100 text-sm">Telegram Alerts Active</p>
                  <span className="text-xs text-sky-400 bg-sky-950/40 px-2 py-0.5 rounded border border-sky-800/50 font-mono">
                    Chat ID: {settings.telegram.chat_id}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  You will receive smart refill reminders (5-day & 2-day queue warnings) and instant post confirmations.
                </p>
              </div>

              <div className="flex items-center gap-2.5 shrink-0">
                <button
                  onClick={handleTestTelegram}
                  disabled={telegramTesting}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-sky-600/20 hover:bg-sky-600/30 text-sky-300 border border-sky-500/30 text-xs font-semibold transition-colors disabled:opacity-50"
                >
                  {telegramTesting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <BellRing className="w-3.5 h-3.5" />}
                  {telegramTesting ? "Sending..." : "Send Test Alert"}
                </button>
                <button
                  onClick={handleDisconnectTelegram}
                  disabled={telegramLoading}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-950/60 text-rose-300 border border-rose-900/50 text-xs font-semibold transition-colors disabled:opacity-50"
                >
                  <Unlink className="w-3.5 h-3.5" />
                  Disconnect
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5">
                <p className="font-semibold text-slate-200 text-sm mb-2">Connect your Telegram in 2 simple steps:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-400 mb-4">
                  <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                    <span className="w-5 h-5 rounded-full bg-sky-500/20 text-sky-400 font-bold flex items-center justify-center shrink-0">1</span>
                    <div>
                      <p className="text-slate-200 font-medium">Open Telegram & message the bot</p>
                      <p className="mt-0.5">
                        Search for{" "}
                        <a
                          href={`https://t.me/${settings.telegram?.bot_username || "PromptPulseBot"}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-sky-400 hover:underline font-semibold inline-flex items-center gap-1"
                        >
                          @{settings.telegram?.bot_username || "PromptPulseBot"}
                          <ExternalLink className="w-3 h-3" />
                        </a>{" "}
                        and click <b>Start</b> (or send <code className="bg-slate-800 px-1 py-0.5 rounded text-[11px]">/start</code>).
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                    <span className="w-5 h-5 rounded-full bg-sky-500/20 text-sky-400 font-bold flex items-center justify-center shrink-0">2</span>
                    <div>
                      <p className="text-slate-200 font-medium">Enter your Chat ID below</p>
                      <p className="mt-0.5">
                        Get your Chat ID by messaging{" "}
                        <a
                          href="https://t.me/userinfobot"
                          target="_blank"
                          rel="noreferrer"
                          className="text-sky-400 hover:underline font-semibold inline-flex items-center gap-1"
                        >
                          @userinfobot
                          <ExternalLink className="w-3 h-3" />
                        </a>{" "}
                        or check the bot's response.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                  <input
                    type="text"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    placeholder="Enter your Telegram Chat ID (e.g. 123456789)"
                    className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 font-mono"
                  />
                  <button
                    onClick={handleConnectTelegram}
                    disabled={telegramLoading}
                    className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-sm font-bold shadow-lg shadow-sky-600/20 active:scale-95 transition-all disabled:opacity-60"
                  >
                    {telegramLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    {telegramLoading ? "Connecting..." : "Connect Telegram"}
                  </button>
                </div>

                {/* Optional custom bot token */}
                <div className="mt-3">
                  <button
                    type="button"
                    onClick={() => setShowAdvancedTelegram(!showAdvancedTelegram)}
                    className="text-[11px] text-slate-500 hover:text-slate-400 underline"
                  >
                    {showAdvancedTelegram ? "Hide Custom Bot Token (Optional)" : "+ Use Custom Bot Token (Optional)"}
                  </button>
                  {showAdvancedTelegram && (
                    <div className="mt-2 p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                      <label className="text-xs text-slate-400 block mb-1">Custom Telegram Bot Token (from @BotFather)</label>
                      <input
                        type="password"
                        value={telegramBotToken}
                        onChange={(e) => setTelegramBotToken(e.target.value)}
                        placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 font-mono"
                      />
                      <p className="text-[10px] text-slate-500 mt-1">Leave blank to use the platform's default bot.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Telegram Success / Error Feedback */}
          {telegramSuccess && (
            <div className="flex items-center gap-2 mt-3 p-3 rounded-xl bg-emerald-950/30 border border-emerald-900/40">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="text-xs text-emerald-300">{telegramSuccess}</span>
            </div>
          )}
          {telegramError && (
            <div className="flex items-center gap-2 mt-3 p-3 rounded-xl bg-rose-950/30 border border-rose-900/40">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span className="text-xs text-rose-300">{telegramError}</span>
            </div>
          )}
        </div>

        {/* Posting Schedule */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-5">
            <Clock className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Posting Schedule</h3>
          </div>

          <div className="flex flex-col gap-6">
            {/* Auto Mode Switch */}
            <div className="flex items-start justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div>
                <div className="text-sm font-bold text-white mb-1">Auto-Publish</div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  When enabled, carousels publish directly to Instagram at your scheduled times without needing your approval first.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer shrink-0 ml-4">
                <input
                  type="checkbox"
                  checked={settings.auto_mode_enabled}
                  onChange={(e) => setSettings({ ...settings, auto_mode_enabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Posts Per Day Selector */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-3">
                Posts Per Day
              </label>
              <div className="flex gap-3">
                {[1, 2, 3].map((count) => (
                  <button
                    key={count}
                    type="button"
                    onClick={() => {
                      const currentTimes = Array.isArray(settings.posting_times)
                        ? settings.posting_times
                        : [settings.posting_time || "09:00"];
                      let newTimes = [...currentTimes];
                      if (count > newTimes.length) {
                        const defaults = ["09:00", "18:00", "20:00"];
                        while (newTimes.length < count) {
                          const nextDefault = defaults.find((d) => !newTimes.includes(d)) || `${12 + newTimes.length}:00`;
                          newTimes.push(nextDefault);
                        }
                      }
                      if (count < newTimes.length) {
                        newTimes = newTimes.slice(0, count);
                      }
                      setSettings({
                        ...settings,
                        posts_per_day: count,
                        posting_times: newTimes,
                        posting_time: newTimes[0],
                      });
                    }}
                    className={`flex-1 py-3 px-4 rounded-xl text-sm font-bold transition-all duration-200 border ${
                      settings.posts_per_day === count
                        ? "bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-600/25 scale-[1.02]"
                        : "bg-slate-950 text-slate-400 border-slate-700 hover:border-slate-600 hover:text-slate-200"
                    }`}
                  >
                    <div className="text-2xl mb-0.5">{count}</div>
                    <div className="text-[10px] opacity-80">
                      {count === 1 ? "Post / Day" : "Posts / Day"}
                    </div>
                  </button>
                ))}
              </div>
              <p className="text-[11px] text-slate-500 mt-2.5">
                {settings.posts_per_day === 1
                  ? "One carousel per day — ideal for quality-focused accounts."
                  : settings.posts_per_day === 2
                  ? "Two carousels per day — morning & evening prime reach."
                  : "Three carousels per day — maximum visibility and algorithm boost."}
              </p>
            </div>

            {/* Dynamic Time Slot Pickers */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Posting Time{(settings.posts_per_day || 1) > 1 ? "s" : ""}
                </label>
                <span className="text-xs text-slate-500 font-mono">{settings.timezone || "UTC"}</span>
              </div>

              <div className="flex flex-col gap-3">
                {Array.from({ length: settings.posts_per_day || 1 }).map((_, slotIdx) => {
                  const times = Array.isArray(settings.posting_times)
                    ? settings.posting_times
                    : [settings.posting_time || "09:00"];
                  const slotValue = times[slotIdx] || "09:00";
                  const isDuplicate =
                    Array.isArray(times) && times.filter((t: string) => t === slotValue).length > 1;

                  return (
                    <div key={slotIdx} className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0 ${
                          slotIdx === 0
                            ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                            : slotIdx === 1
                            ? "bg-purple-600/20 text-purple-400 border border-purple-500/30"
                            : "bg-emerald-600/20 text-emerald-400 border border-emerald-500/30"
                        }`}
                      >
                        {slotIdx + 1}
                      </div>
                      <div className="flex-1">
                        <input
                          type="time"
                          value={slotValue}
                          onChange={(e) => {
                            const timesList = Array.isArray(settings.posting_times)
                              ? settings.posting_times
                              : [settings.posting_time || "09:00"];
                            const newTimes = [...timesList];
                            newTimes[slotIdx] = e.target.value;
                            setSettings({
                              ...settings,
                              posting_times: newTimes,
                              posting_time: newTimes[0],
                            });
                          }}
                          className={`w-full bg-slate-950 border rounded-lg p-2.5 text-sm text-white font-mono focus:outline-none transition-colors ${
                            isDuplicate
                              ? "border-rose-500 focus:border-rose-400"
                              : "border-slate-700 focus:border-blue-500"
                          }`}
                        />
                      </div>
                      <span className="text-[11px] text-slate-500 w-28 shrink-0">
                        {slotIdx === 0
                          ? "Morning slot"
                          : slotIdx === 1
                          ? "Afternoon / Evening"
                          : "Night slot"}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Duplicate time warning */}
              {(() => {
                const times = Array.isArray(settings.posting_times) ? settings.posting_times : [];
                const hasDuplicates = times.length !== new Set(times).size;
                if (!hasDuplicates) return null;
                return (
                  <div className="flex items-center gap-2 mt-3 p-2.5 rounded-lg bg-rose-950/30 border border-rose-900/40">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                    <span className="text-xs text-rose-300 font-medium">
                      Each posting time must be different. Please adjust the duplicate slots.
                    </span>
                  </div>
                );
              })()}
            </div>

            {/* Active Days Chips */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-3">
                Active Posting Days
              </label>
              <div className="flex flex-wrap gap-2">
                {["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"].map((day) => {
                  const daysList = Array.isArray(settings.active_days) ? settings.active_days : [];
                  const active = daysList.includes(day);
                  const dayLabels: Record<string, string> = {
                    MON: "Mon",
                    TUE: "Tue",
                    WED: "Wed",
                    THU: "Thu",
                    FRI: "Fri",
                    SAT: "Sat",
                    SUN: "Sun",
                  };
                  return (
                    <button
                      key={day}
                      type="button"
                      onClick={() => {
                        const current = Array.isArray(settings.active_days) ? settings.active_days : [];
                        const updated = active
                          ? current.filter((d: string) => d !== day)
                          : [...current, day];
                        setSettings({ ...settings, active_days: updated });
                      }}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-200 border ${
                        active
                          ? "bg-blue-600/15 text-blue-400 border-blue-500/40 shadow-sm"
                          : "bg-slate-950 text-slate-500 border-slate-700 hover:border-slate-600 hover:text-slate-300"
                      }`}
                    >
                      {dayLabels[day]}
                    </button>
                  );
                })}
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                Carousels will only be created and posted on selected days.
              </p>
            </div>

            {/* Timezone Selector */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Timezone
              </label>
              <select
                value={settings.timezone || "UTC"}
                onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value="UTC">UTC (Coordinated Universal Time)</option>
                <option value="America/New_York">Eastern Time (US — New York)</option>
                <option value="America/Chicago">Central Time (US — Chicago)</option>
                <option value="America/Denver">Mountain Time (US — Denver)</option>
                <option value="America/Los_Angeles">Pacific Time (US — Los Angeles)</option>
                <option value="America/Toronto">Eastern Time (Canada — Toronto)</option>
                <option value="America/Sao_Paulo">Bras\u00edlia Time (S\u00e3o Paulo)</option>
                <option value="Europe/London">GMT / BST (London)</option>
                <option value="Europe/Paris">Central European (Paris)</option>
                <option value="Europe/Berlin">Central European (Berlin)</option>
                <option value="Europe/Istanbul">Turkey Time (Istanbul)</option>
                <option value="Asia/Dubai">Gulf Standard (Dubai)</option>
                <option value="Asia/Kolkata">India Standard (IST — Kolkata)</option>
                <option value="Asia/Singapore">Singapore / HKT (Singapore)</option>
                <option value="Asia/Tokyo">Japan Standard (Tokyo)</option>
                <option value="Asia/Shanghai">China Standard (Shanghai)</option>
                <option value="Australia/Sydney">Australian Eastern (Sydney)</option>
                <option value="Pacific/Auckland">New Zealand (Auckland)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Content Niche */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">Content Niche</h3>
          </div>

          <p className="text-xs text-slate-400 mb-4 leading-relaxed">
            Tell us what your account is about. The AI will research trending topics, generate carousels, and write captions tailored to your niche.
          </p>

          <input
            type="text"
            value={settings.niche}
            onChange={(e) => setSettings({ ...settings, niche: e.target.value })}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
            placeholder="e.g. AI Tools & Productivity, Fitness, Crypto, Fashion..."
          />
        </div>

        {/* Brand Palette Customization */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-2">
            <Palette className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Brand Colors</h3>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            These colors are used in your auto-generated carousel slides.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Primary</label>
              <div className="flex items-center gap-2 bg-slate-950 border border-slate-700 rounded-lg p-2">
                <input
                  type="color"
                  value={settings.primary_color}
                  onChange={(e) => setSettings({ ...settings, primary_color: e.target.value })}
                  className="w-8 h-8 rounded border-none bg-transparent cursor-pointer"
                />
                <span className="text-xs font-mono text-slate-300">{settings.primary_color}</span>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Background</label>
              <div className="flex items-center gap-2 bg-slate-950 border border-slate-700 rounded-lg p-2">
                <input
                  type="color"
                  value={settings.background_color}
                  onChange={(e) => setSettings({ ...settings, background_color: e.target.value })}
                  className="w-8 h-8 rounded border-none bg-transparent cursor-pointer"
                />
                <span className="text-xs font-mono text-slate-300">{settings.background_color}</span>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Text</label>
              <div className="flex items-center gap-2 bg-slate-950 border border-slate-700 rounded-lg p-2">
                <input
                  type="color"
                  value={settings.text_color}
                  onChange={(e) => setSettings({ ...settings, text_color: e.target.value })}
                  className="w-8 h-8 rounded border-none bg-transparent cursor-pointer"
                />
                <span className="text-xs font-mono text-slate-300">{settings.text_color}</span>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Secondary</label>
              <div className="flex items-center gap-2 bg-slate-950 border border-slate-700 rounded-lg p-2">
                <input
                  type="color"
                  value={settings.secondary_color}
                  onChange={(e) => setSettings({ ...settings, secondary_color: e.target.value })}
                  className="w-8 h-8 rounded border-none bg-transparent cursor-pointer"
                />
                <span className="text-xs font-mono text-slate-300">{settings.secondary_color}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Brand Identity */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">Brand Identity</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Brand Name
              </label>
              <input
                type="text"
                value={settings.brand_name}
                onChange={(e) => setSettings({ ...settings, brand_name: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                placeholder="Your brand or page name"
              />
            </div>

            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Tagline
              </label>
              <input
                type="text"
                value={settings.tagline}
                onChange={(e) => setSettings({ ...settings, tagline: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                placeholder="Your brand's short tagline"
              />
            </div>
          </div>
        </div>

        {/* Carousel Blueprint & Style Preferences */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white">Carousel Blueprint & Preferences</h3>
          </div>
          <p className="text-xs text-slate-400 mb-4 leading-relaxed">
            Define what kind of carousels you want the AI to generate automatically every morning.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Default Tone & Angle
              </label>
              <select
                value={settings.content_strategy?.default_tone || "Technical Deep Dive"}
                onChange={(e) => {
                  const strat = { ...(settings.content_strategy || {}), default_tone: e.target.value };
                  setSettings({ ...settings, content_strategy: strat });
                }}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="Technical Deep Dive">⚡ Technical Deep Dive (Code, Architecture, Benchmarks)</option>
                <option value="Viral Hype">🔥 Viral Hype & Impact (Mindblowing Tech, Future of Work)</option>
                <option value="Step-by-Step Tutorial">🛠️ Step-by-Step Tutorial (Actionable How-To)</option>
                <option value="Creator Breakdown">💡 Creator Breakdown (ROI, Monetization, Scaling)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Default Comment-to-DM Keyword (Slide 6 CTA)
              </label>
              <input
                type="text"
                value={settings.content_strategy?.default_dm_keyword || "VEO"}
                onChange={(e) => {
                  const strat = { ...(settings.content_strategy || {}), default_dm_keyword: e.target.value.toUpperCase() };
                  setSettings({ ...settings, content_strategy: strat });
                }}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs font-mono font-bold text-cyan-300 uppercase focus:outline-none focus:border-cyan-500"
                placeholder="e.g. CURSOR, VEO, CHEAT"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
              Preferred Hero Slide 1 Layout
            </label>
            <select
              value={settings.content_strategy?.preferred_hero || "hero_editorial"}
              onChange={(e) => {
                const strat = { ...(settings.content_strategy || {}), preferred_hero: e.target.value };
                setSettings({ ...settings, content_strategy: strat });
              }}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="hero_editorial">Hero Editorial (Cosmic Workspace Mockup + 4 Capability Pills)</option>
              <option value="hero_terminal">Hero Terminal (Dev CLI Matrix & Glow Command Bar)</option>
              <option value="hero_blueprint">Hero Blueprint (Architectural Schematics)</option>
              <option value="hero_badge">Hero Badge (Breakthrough Stamp & Metric Focus)</option>
              <option value="hero_minimal_bold">Hero Minimal (High Contrast Typography)</option>
              <option value="hero_grid_matrix">Hero Matrix (Tech Grid & Accent Lines)</option>
            </select>
          </div>
        </div>

        {/* Content Pillars Editor */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-2">
            <Sliders className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">Content Topics</h3>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            Set the mix of content types the AI should create. Adjust percentages to control how often each topic appears.
          </p>

          <div className="flex flex-col gap-3">
            {(settings.pillars || []).map((pillar: any, index: number) => (
              <div
                key={pillar.id || index}
                className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 gap-4"
              >
                <div className="flex-grow">
                  <div className="text-sm font-semibold text-white">{pillar.name}</div>
                  <div className="text-xs text-slate-400">{pillar.description}</div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={pillar.percentage}
                    onChange={(e) => {
                      const updated = [...settings.pillars];
                      updated[index].percentage = parseInt(e.target.value) || 0;
                      setSettings({ ...settings, pillars: updated });
                    }}
                    className="w-16 bg-slate-950 border border-slate-700 rounded-lg p-1.5 text-center text-xs font-mono text-white"
                  />
                  <span className="text-xs text-slate-400 font-bold">%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
