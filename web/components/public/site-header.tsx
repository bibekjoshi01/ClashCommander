"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

const SiteHeader = () => {
  const pathname = usePathname();
  const [hasPastRuns, setHasPastRuns] = useState(false);

  useEffect(() => {
    const readHistoryPresence = () => {
      if (typeof window === "undefined") return;
      const raw = window.localStorage.getItem("qa-agent-history");
      if (!raw) {
        setHasPastRuns(false);
        return;
      }
      try {
        const parsed = JSON.parse(raw);
        setHasPastRuns(Array.isArray(parsed) && parsed.length > 0);
      } catch {
        setHasPastRuns(false);
      }
    };

    readHistoryPresence();
    window.addEventListener("storage", readHistoryPresence);
    return () => window.removeEventListener("storage", readHistoryPresence);
  }, [pathname]);

  return (
    <header className="z-[10] mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-8">
      <Link href="/" className="text-xl font-semibold tracking-tight">
        QA agent
      </Link>
      <nav className="flex items-center gap-6 text-sm">
        {hasPastRuns && (
          <Link href="/qa/history" className="font-medium text-surface-muted hover:text-surface-fg">
            past runs
          </Link>
        )}
        <Link href="/qa" className="font-medium text-surface-fg">
          try now
        </Link>
      </nav>
    </header>
  );
};

export default SiteHeader;
