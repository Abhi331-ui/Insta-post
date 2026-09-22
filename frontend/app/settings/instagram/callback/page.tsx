"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { exchangeInstagramCode } from "@/lib/api";
import { Instagram, AlertCircle, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const error = searchParams.get("error");
    const errorDescription = searchParams.get("error_description");

    if (error || errorDescription) {
      setStatus("error");
      setErrorMessage(errorDescription || error || "Meta authorization was declined or failed.");
      return;
    }

    if (!code) {
      setStatus("error");
      setErrorMessage("No authorization code found in callback URL.");
      return;
    }

    const exchange = async () => {
      try {
        await exchangeInstagramCode(code);
        setStatus("success");
        setTimeout(() => {
          router.replace("/settings?instagram=connected");
        }, 1500);
      } catch (err: any) {
        setStatus("error");
        setErrorMessage(err.message || "Failed to exchange authorization code.");
      }
    };

    exchange();
  }, [searchParams, router]);

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-[#0F172A] border border-slate-800 rounded-3xl p-8 shadow-2xl text-center flex flex-col items-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 flex items-center justify-center text-white shadow-xl mb-6">
          <Instagram className="w-8 h-8" />
        </div>

        {status === "loading" && (
          <>
            <h2 className="text-2xl font-bold text-white mb-2">Connecting Instagram...</h2>
            <p className="text-xs text-slate-400 mb-6">
              Exchanging your Meta authorization code for a long-lived 60-day publishing token.
            </p>
            <div className="w-8 h-8 border-3 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          </>
        )}

        {status === "success" && (
          <>
            <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Connected Successfully!</h2>
            <p className="text-xs text-slate-400 mb-6">
              Your Instagram Professional Account is linked. Redirecting to settings...
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mb-4">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Connection Failed</h2>
            <p className="text-xs text-rose-300/90 bg-rose-950/40 border border-rose-900/50 rounded-xl p-3 mb-6 text-left font-mono">
              {errorMessage}
            </p>
            <Link
              href="/settings"
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold transition-all"
            >
              <span>Back to Settings</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default function InstagramCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[70vh] flex items-center justify-center p-4">
          <div className="w-8 h-8 border-3 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
