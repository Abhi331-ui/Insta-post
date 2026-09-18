"use client";

import { useEffect, useState } from "react";
import { getSettings, updateSettings, connectInstagram } from "@/lib/api";
import { Settings, Instagram, Sparkles, Clock, Palette, Sliders, Check, AlertCircle } from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await getSettings();
      setSettings(data);
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
      const res = await connectInstagram();
      if (res.auth_url) {
        window.location.href = res.auth_url;
      }
    } catch (e: any) {
      alert("Error initiating Instagram OAuth: " + e.message);
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
          <h1 className="text-3xl font-black text-white tracking-tight">Settings & Integrations</h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage your Meta Graph API credentials, autonomous posting schedule, and brand identity.
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
        {/* Instagram Account Connection */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 flex items-center justify-center text-white shadow-lg">
                <Instagram className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Instagram Professional Account</h3>
                <p className="text-xs text-slate-400">Meta Graph API official publishing & analytics</p>
              </div>
            </div>

            {settings.instagram?.connected ? (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                Connected
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                Not Connected (Simulation Active)
              </span>
            )}
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="text-xs text-slate-300">
              {settings.instagram?.connected ? (
                <div>
                  <p className="font-semibold text-slate-100">{settings.instagram.page_name}</p>
                  <p className="text-slate-500 mt-0.5">Token active until {new Date(settings.instagram.token_expires_at).toLocaleDateString()}</p>
                </div>
              ) : (
                <p>
                  Connect your Instagram Business account to enable automatic 3-step carousel container publishing.
                </p>
              )}
            </div>

            <button
              onClick={handleConnectInstagram}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-rose-600 to-purple-600 hover:from-rose-500 hover:to-purple-500 text-white text-xs font-bold shadow-md shadow-purple-600/20 whitespace-nowrap active:scale-95 transition-all"
            >
              {settings.instagram?.connected ? "Reconnect Meta" : "Connect Instagram via Meta"}
            </button>
          </div>
        </div>

        {/* Autonomous Mode & Scheduling */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Autonomous Automation & Timing</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Auto Mode Switch */}
            <div className="flex items-start justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div>
                <div className="text-sm font-bold text-white mb-1">Autonomous Auto-Publish Mode</div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  When enabled, verified QA-passed carousels publish directly to Instagram without waiting for manual approval.
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

            {/* Posting Time */}
            <div className="flex flex-col gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Target Daily Posting Time
                </label>
                <span className="text-xs text-slate-500 font-mono">{settings.timezone}</span>
              </div>
              <input
                type="time"
                value={settings.posting_time}
                onChange={(e) => setSettings({ ...settings, posting_time: e.target.value })}
                className="bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-sm text-white font-mono focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Daily Post-Publish Reminder & Webhook */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
              <h3 className="text-base font-bold text-white">Daily Post-Publish Notifications</h3>
            </div>
            <button
              type="button"
              onClick={async () => {
                try {
                  const { triggerTestReminder } = await import("@/lib/api");
                  const res = await triggerTestReminder();
                  alert(`Test notification triggered! Look at the bell in the top navbar.\n\n"${res.title}"`);
                } catch (e: any) {
                  alert("Error triggering test reminder: " + e.message);
                }
              }}
              className="px-3 py-1.5 rounded-lg bg-blue-600/15 hover:bg-blue-600/25 border border-blue-500/30 text-xs font-semibold text-blue-400 transition-colors"
            >
              Send Test Reminder Notification
            </button>
          </div>

          <p className="text-xs text-slate-400 mb-4 leading-relaxed">
            Every day immediately after posting your carousel, PromptPulse calculates your remaining queue coverage and sends you a reminder to make ready the next 10 trending ideas.
          </p>

          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
              External Webhook URL (Discord / Slack / Telegram) <span className="text-slate-500 lowercase">(optional)</span>
            </label>
            <input
              type="url"
              value={settings.webhook_url || ""}
              onChange={(e) => setSettings({ ...settings, webhook_url: e.target.value })}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white font-mono placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
              placeholder="https://discord.com/api/webhooks/... or https://hooks.slack.com/services/..."
            />
            <p className="text-[11px] text-slate-500 mt-1.5">
              Leave blank to receive in-app notifications only (via the navbar bell icon).
            </p>
          </div>
        </div>

        {/* AI Provider Settings */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">AI Provider Abstraction</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Active Provider
              </label>
              <select
                value={settings.ai_provider}
                onChange={(e) => setSettings({ ...settings, ai_provider: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value="gemini">Google Gemini (Search Grounded 1.5 Pro & Flash)</option>
                <option value="openai">OpenAI (GPT-4o & GPT-4o-mini)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Content Niche
              </label>
              <input
                type="text"
                value={settings.niche}
                onChange={(e) => setSettings({ ...settings, niche: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                placeholder="AI Tools, Productivity & Developers"
              />
            </div>
          </div>
        </div>

        {/* Brand Palette Customization */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Palette className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Brand Identity (1080x1350 Visual System)</h3>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Primary Blue</label>
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
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Primary Text</label>
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
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Secondary Slate</label>
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

        {/* Content Pillars Editor */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Sliders className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">Content Pillar Distribution</h3>
          </div>

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
