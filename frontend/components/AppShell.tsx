"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const protectedPaths = ["/dashboard", "/posts", "/queue", "/calendar", "/analytics", "/settings", "/inbox"];
    const token = localStorage.getItem("access_token");
    const isProtected = protectedPaths.includes(pathname);

    if (isProtected && !token) {
      router.replace("/login");
      return;
    }

    if (pathname === "/login" && token) {
      router.replace("/dashboard");
    }
  }, [pathname, router]);

  const showNav = pathname !== "/login" && !pathname.startsWith("/review/");

  return (
    <>
      {showNav && <Navbar />}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </>
  );
}
