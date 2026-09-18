import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";

export const metadata: Metadata = {
  title: "PromptPulse — Autonomous AI Instagram Content Agent",
  description: "Discover something worth posting every day. Production-ready autonomous AI Instagram agent.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0B0F19] text-slate-100 antialiased flex flex-col">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
