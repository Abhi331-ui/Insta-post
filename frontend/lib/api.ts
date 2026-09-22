const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

function clearAuthState() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    window.location.href = "/login";
  }
}

export async function fetchJson(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.method && options.method.toUpperCase() === "GET")) {
    headers.set("Content-Type", "application/json");
  }

  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401 && typeof window !== "undefined") {
      clearAuthState();
      throw new Error("Authentication expired or invalid.");
    }

    let errMessage = `API request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data.detail) errMessage = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch (_) {}
    throw new Error(errMessage);
  }

  return res.json();
}

// Posts
export const getPosts = (status?: string, pillar?: string) => {
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  if (pillar) params.append("pillar", pillar);
  return fetchJson(`/posts?${params.toString()}`);
};

export const getPost = (id: number | string) => fetchJson(`/posts/${id}`);
export const approvePost = (id: number | string) => fetchJson(`/posts/${id}/approve`, { method: "POST" });
export const rejectPost = (id: number | string) => fetchJson(`/posts/${id}/reject`, { method: "POST" });
export const regeneratePost = (id: number | string) => fetchJson(`/posts/${id}/regenerate`, { method: "POST" });
export const regenerateSlide = (id: number | string, slideNumber: number) =>
  fetchJson(`/posts/${id}/slides/${slideNumber}/regenerate`, { method: "POST" });
export const publishNow = (id: number | string) => fetchJson(`/posts/${id}/publish-now`, { method: "POST" });
export const reschedulePost = (id: number | string, scheduledTime: string) =>
  fetchJson(`/posts/${id}/reschedule`, {
    method: "POST",
    body: JSON.stringify({ scheduled_time: scheduledTime }),
  });
export const updateCaption = (id: number | string, data: { caption: string; hashtags?: string; alt_text?: string }) =>
  fetchJson(`/posts/${id}/caption`, { method: "PATCH", body: JSON.stringify(data) });
export const updateSlideText = (id: number | string, slideNumber: number, data: { headline?: string; body_text?: string }) =>
  fetchJson(`/posts/${id}/slides/${slideNumber}`, { method: "PATCH", body: JSON.stringify(data) });
export const createManualPost = (
  topic: string,
  contentPillar?: string,
  targetAudience?: string[],
  options?: {
    notes?: string;
    hook?: string;
    tone?: string;
    dm_keyword?: string;
  }
) =>
  fetchJson(`/create-post`, {
    method: "POST",
    body: JSON.stringify({
      topic,
      content_pillar: contentPillar,
      target_audience: targetAudience,
      notes: options?.notes,
      hook: options?.hook,
      tone: options?.tone,
      dm_keyword: options?.dm_keyword,
    }),
  });

// Calendar
export const getCalendar = () => fetchJson(`/calendar`);

// Analytics
export const getAnalytics = () => fetchJson(`/analytics`);
export const getPostAnalytics = (postId: number | string) => fetchJson(`/analytics/${postId}`);

// Settings
export const getSettings = () => fetchJson(`/settings`);
export const updateSettings = (data: any) =>
  fetchJson(`/settings`, { method: "PUT", body: JSON.stringify(data) });
export const connectInstagram = () => fetchJson(`/settings/instagram/connect`, { method: "POST" });
export const connectInstagramManual = (data: { instagram_user_id: string; access_token: string; page_name?: string }) =>
  fetchJson(`/settings/instagram/manual`, { method: "POST", body: JSON.stringify(data) });
export const connectInstagramTest = () =>
  fetchJson(`/settings/instagram/test-connect`, { method: "POST" });
export const disconnectInstagram = () =>
  fetchJson(`/settings/instagram/disconnect`, { method: "POST" });
export const exchangeInstagramCode = (code: string) =>
  fetchJson(`/settings/instagram/exchange-code`, { method: "POST", body: JSON.stringify({ code }) });

// Telegram
export const connectTelegram = (chatId: string, botToken?: string) =>
  fetchJson(`/settings/telegram/connect`, {
    method: "POST",
    body: JSON.stringify({ chat_id: chatId, bot_token: botToken || undefined }),
  });
export const disconnectTelegram = () =>
  fetchJson(`/settings/telegram/disconnect`, { method: "POST" });
export const testTelegram = () =>
  fetchJson(`/settings/telegram/test`, { method: "POST" });

// Agent Trigger & Status
export const getAgentStatus = () => fetchJson(`/agent/status-json`);
export const runAgentNow = () => fetchJson(`/agent/run-now`, { method: "POST" });

// Curated Topic Queue & Batch Scheduler
export const getQueue = () => fetchJson(`/queue`);
export const submitTopicBatch = (topics: string[], startDate?: string, postsPerDay?: number) =>
  fetchJson(`/queue/batch`, {
    method: "POST",
    body: JSON.stringify({ topics, start_date: startDate, posts_per_day: postsPerDay || 1 }),
  });
export const deleteQueueItem = (id: number | string) =>
  fetchJson(`/queue/${id}`, { method: "DELETE" });
export const generateQueueItem = (id: number | string) =>
  fetchJson(`/queue/${id}/generate`, { method: "POST" });

// Notifications
export const getNotifications = () => fetchJson(`/notifications`);
export const markNotificationRead = (id: number | string) =>
  fetchJson(`/notifications/${id}/read`, { method: "POST" });
export const markAllNotificationsRead = () =>
  fetchJson(`/notifications/read-all`, { method: "POST" });
export const triggerTestReminder = () =>
  fetchJson(`/notifications/test-reminder`, { method: "POST" });

// Client Magic Review & Monetization
export const getShareLink = (postId: number | string) =>
  fetchJson(`/posts/${postId}/share-link`, { method: "POST" });

export const getPublicReview = (token: string) =>
  fetchJson(`/posts/public/review/${token}`);

export const submitReviewAction = (token: string, action: "approve" | "request_changes", feedback?: string) =>
  fetchJson(`/posts/public/review/${token}/action`, {
    method: "POST",
    body: JSON.stringify({ action, feedback }),
  });

export const getExportPdfUrl = (postId: number | string) =>
  `${process.env.NEXT_PUBLIC_API_URL || "/api"}/posts/${postId}/export-pdf`;

export const getPublicExportPdfUrl = (token: string) =>
  `${process.env.NEXT_PUBLIC_API_URL || "/api"}/posts/public/review/${token}/export-pdf`;

// Interactions & Engagement (Comments & DMs)
export const getInteractions = (type?: string, status?: string, limit = 50, offset = 0) => {
  const params = new URLSearchParams();
  if (type) params.append("type", type);
  if (status) params.append("status", status);
  params.append("limit", limit.toString());
  params.append("offset", offset.toString());
  return fetchJson(`/interactions?${params.toString()}`);
};

export const getInteractionStats = () => fetchJson(`/interactions/stats`);

export const checkInteractionsNow = () =>
  fetchJson(`/interactions/check-now`, { method: "POST" });

export const replyToInteraction = (id: number | string, replyMessage: string, sendDm = false) =>
  fetchJson(`/interactions/${id}/reply`, {
    method: "POST",
    body: JSON.stringify({ reply_message: replyMessage, send_dm: sendDm }),
  });

export const ignoreInteraction = (id: number | string) =>
  fetchJson(`/interactions/${id}/ignore`, { method: "POST" });

// Agent Brain & Learning Engine
export const getAgentBrain = () => fetchJson(`/agent/brain`);
export const updateCustomDirectives = (directives: string[]) =>
  fetchJson(`/agent/directives`, { method: "POST", body: JSON.stringify({ directives }) });

// 6-Slot Slide Studio
export const draftSixSlots = (topic: string, tone?: string, notes?: string, dmKeyword?: string) =>
  fetchJson(`/draft-6-slots`, {
    method: "POST",
    body: JSON.stringify({
      topic,
      tone,
      notes,
      dm_keyword: dmKeyword,
    }),
  });

export const createCustomSlidesPost = (data: {
  topic: string;
  content_pillar?: string;
  target_audience?: string[];
  tone?: string;
  slides: any[];
}) =>
  fetchJson(`/create-custom-slides-post`, {
    method: "POST",
    body: JSON.stringify(data),
  });
