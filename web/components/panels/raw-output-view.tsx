"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Card } from "@/components/ui/card";
import MarkdownRenderer from "@/components/markdown/markdown-renderer";
import { ScanReport } from "@/types/scan";

export function RawOutputView({ report }: { report: ScanReport }) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const jsonPayload = JSON.stringify(report.rawJson, null, 2);
  const tracePayload = JSON.stringify(report.trace, null, 2);
  const toolOutputsPayload = JSON.stringify(report.toolOutputs, null, 2);

  const copy = async (key: string, text: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 1200);
  };

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Backend Narrative</h3>
            <p className="text-xs text-slate-500">Rendered directly from backend markdown output.</p>
          </div>
          <button
            className="inline-flex items-center gap-2 rounded-md border border-white/10 px-2 py-1 text-xs"
            type="button"
            onClick={() => copy("model", report.rawModelOutput)}
          >
            {copiedKey === "model" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />} Copy
          </button>
        </div>
        <div className="rounded-lg border border-white/10 bg-black/35 py-3">
          <MarkdownRenderer content={report.rawModelOutput} className="max-w-none px-4" />
        </div>
      </Card>

      <Card className="p-4">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Raw Backend Data</h3>
        <p className="mt-1 text-xs text-slate-500">
          Structured payloads from backend. Kept collapsed to reduce clutter.
        </p>

        <details className="mt-3 rounded-lg border border-white/10 bg-black/35 p-3">
          <summary className="cursor-pointer text-xs uppercase tracking-wide text-slate-400">Full JSON Response</summary>
          <div className="mt-3 flex justify-end">
            <button
              className="inline-flex items-center gap-2 rounded-md border border-white/10 px-2 py-1 text-xs"
              type="button"
              onClick={() => copy("json", jsonPayload)}
            >
              {copiedKey === "json" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />} Copy
            </button>
          </div>
          <pre className="mt-2 max-h-72 overflow-auto rounded-md border border-white/10 bg-black/30 p-3 font-mono text-xs text-slate-300">
            {jsonPayload}
          </pre>
        </details>

        <details className="mt-3 rounded-lg border border-white/10 bg-black/35 p-3">
          <summary className="cursor-pointer text-xs uppercase tracking-wide text-slate-400">Trace JSON</summary>
          <div className="mt-3 flex justify-end">
            <button
              className="inline-flex items-center gap-2 rounded-md border border-white/10 px-2 py-1 text-xs"
              type="button"
              onClick={() => copy("trace", tracePayload)}
            >
              {copiedKey === "trace" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />} Copy
            </button>
          </div>
          <pre className="mt-2 max-h-72 overflow-auto rounded-md border border-white/10 bg-black/30 p-3 font-mono text-xs text-slate-300">
            {tracePayload}
          </pre>
        </details>

        <details className="mt-3 rounded-lg border border-white/10 bg-black/35 p-3">
          <summary className="cursor-pointer text-xs uppercase tracking-wide text-slate-400">Tool Outputs JSON</summary>
          <div className="mt-3 flex justify-end">
            <button
              className="inline-flex items-center gap-2 rounded-md border border-white/10 px-2 py-1 text-xs"
              type="button"
              onClick={() => copy("tool-outputs", toolOutputsPayload)}
            >
              {copiedKey === "tool-outputs" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />} Copy
            </button>
          </div>
          <pre className="mt-2 max-h-72 overflow-auto rounded-md border border-white/10 bg-black/30 p-3 font-mono text-xs text-slate-300">
            {toolOutputsPayload}
          </pre>
        </details>
      </Card>
    </div>
  );
}
