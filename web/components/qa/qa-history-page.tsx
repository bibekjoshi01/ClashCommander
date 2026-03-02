"use client";

import Link from "next/link";
import { useMemo } from "react";
import { ArrowRight } from "lucide-react";
import { useLocalStorage } from "@/hooks/use-local-storage";
import { ScanReport } from "@/types/scan";

function formatDate(value?: string) {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

export function QAHistoryPage() {
  const [history] = useLocalStorage<ScanReport[]>("qa-agent-history", []);

  const runs = useMemo(() => [...history], [history]);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 pb-20">
      <section className="rounded-2xl border border-surface-border bg-surface-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Past Runs</h1>
            <p className="mt-1 text-sm text-surface-muted">Choose a previous run to open its full results.</p>
          </div>
          <Link href="/qa" className="inline-flex items-center gap-1 text-sm font-medium text-surface-muted hover:text-surface-fg">
            Run new scan <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {runs.length === 0 && (
          <div className="mt-6 rounded-xl border border-surface-border p-6 text-sm text-surface-muted">
            No past runs found in local storage.
          </div>
        )}

        {runs.length > 0 && (
          <div className="mt-6 space-y-3">
            {runs.map((report) => (
              <Link
                key={report.id}
                href={`/qa/results?scanId=${encodeURIComponent(report.id)}`}
                className="block rounded-xl border border-surface-border p-4 transition hover:bg-slate-50 dark:hover:bg-slate-900"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{report.targetUrl}</p>
                    <p className="mt-1 text-xs text-surface-muted">{report.id}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs uppercase tracking-wide text-surface-muted">Completed</p>
                    <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">{formatDate(report.completedAt ?? report.startedAt)}</p>
                  </div>
                </div>

                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-surface-border px-3 py-2">
                    <p className="text-xs uppercase tracking-wide text-surface-muted">Risk</p>
                    <p className="mt-1 text-base font-semibold">{report.riskScore}</p>
                  </div>
                  <div className="rounded-lg border border-surface-border px-3 py-2">
                    <p className="text-xs uppercase tracking-wide text-surface-muted">Performance</p>
                    <p className="mt-1 text-base font-semibold">{report.performanceScore}</p>
                  </div>
                  <div className="rounded-lg border border-surface-border px-3 py-2">
                    <p className="text-xs uppercase tracking-wide text-surface-muted">Findings</p>
                    <p className="mt-1 text-base font-semibold">{report.issues.length}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
