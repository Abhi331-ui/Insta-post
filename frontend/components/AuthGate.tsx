"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const protectedPaths = ["/dashboard", "/posts", "/queue", "/calendar", "/analytics", "/settings"];
    const isProtected = protectedPaths.includes(pathname);
    const token = localStorage.getItem("access_token");

    if (isProtected && !token) {
      router.replace("/login");
      return;
    }

    if (pathname === "/login" && token) {
      router.replace("/dashboard");
    }
  }, [pathname, router]);

  return <>{children}</>;
}
