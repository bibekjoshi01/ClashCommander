"use client";

import Image from "next/image";
import { useState } from "react";
import { CheckCircle2, CircleAlert, ChevronDown, ChevronUp } from "lucide-react";
import MarkdownRenderer from "@/components/markdown/markdown-renderer";
import { Card } from "@/components/ui/card";
import { TraceStep } from "@/types/scan";

function StatusIcon({ status }: { status: TraceStep["status"] }) {
  if (status === "success") return <CheckCircle2 className="h-4 w-4 text-neon-green" />;
  return <CircleAlert className="h-4 w-4 text-neon-red" />;
}

function findingsFromOutput(step: TraceStep): string[] {
  const value = step.outputJson?.findings;
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string");
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string");
}

function summarizeToolCall(call: TraceStep["toolCalls"][number]) {
  const args = call.arguments ?? {};
  const snippets: string[] = [];
  const action = typeof args.action === "string" ? args.action : null;
  const text = typeof args.text === "string" ? args.text : null;
  const url = typeof args.url === "string" ? args.url : null;
  const limit = typeof args.limit === "number" ? args.limit : null;

  if (action) snippets.push(`action: ${action}`);
  if (text) snippets.push(`text: ${text}`);
  if (url) snippets.push(`url: ${url}`);
  if (limit !== null) snippets.push(`limit: ${limit}`);

  return snippets.length > 0 ? snippets.join(" | ") : "No notable arguments";
}

function extractEvidence(step: TraceStep): string[] {
  const evidence: string[] = [];
  const output = step.outputJson ?? {};
  const metadata = step.metadata ?? {};

  const requestFailures = stringList(output.request_failures);
  if (requestFailures.length > 0) {
    evidence.push(...requestFailures);
  }

  const missingHeaders = stringList(output.missing_headers);
  if (missingHeaders.length > 0) {
    evidence.push(`Missing headers: ${missingHeaders.join(", ")}`);
  }

  const consoleCount = typeof output.console_event_count === "number" ? output.console_event_count : undefined;
  if (typeof consoleCount === "number") {
    evidence.push(`Console events: ${consoleCount}`);
  }

  const failureCount = typeof output.request_failure_count === "number" ? output.request_failure_count : undefined;
  if (typeof failureCount === "number") {
    evidence.push(`Request failures: ${failureCount}`);
  }

  const status = typeof output.status === "number" ? output.status : typeof metadata.status === "number" ? metadata.status : undefined;
  if (typeof status === "number") {
    evidence.push(`HTTP status: ${status}`);
  }

  if (typeof metadata.url === "string") {
    evidence.push(`Target URL: ${metadata.url}`);
  }

  return evidence;
}

export function TraceVisualization({ trace }: { trace: TraceStep[] }) {
  const [open, setOpen] = useState<string | null>(trace[0]?.id ?? null);

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">Thinking</h3>
      <div className="space-y-3">
        {trace.map((step) => {
          const expanded = open === step.id;
          const findings = findingsFromOutput(step);
          const evidence = extractEvidence(step);

          return (
            <section key={step.id} className="overflow-hidden rounded-xl border border-white/10 bg-black/20">
              <button
                type="button"
                className="flex w-full items-start justify-between gap-3 px-4 py-3 text-left transition hover:bg-white/[0.03]"
                onClick={() => setOpen(expanded ? null : step.id)}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <StatusIcon status={step.status} />
                    <p className="text-sm font-medium text-slate-100">Step {step.step}</p>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">
                    {step.toolCalls.length} tool call{step.toolCalls.length === 1 ? "" : "s"}
                  </p>
                </div>
                {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
              </button>

              {expanded && (
                <div className="space-y-4 border-t border-white/10 px-4 py-4 text-sm">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">assistant_content</p>
                    <div className="mt-1 rounded-lg border border-white/10 bg-black/35 px-3 py-2 text-slate-200">
                      {step.assistantContent ? (
                        <MarkdownRenderer content={step.assistantContent} className="max-w-none px-0 text-slate-200" />
                      ) : (
                        <p>No assistant_content returned.</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Tool Calls</p>
                    <div className="mt-1 space-y-2">
                      {step.toolCalls.length === 0 && <p className="text-slate-400">No tool calls returned.</p>}
                      {step.toolCalls.map((call) => (
                        <div key={call.id} className="rounded-lg border border-white/10 bg-black/35 px-3 py-2">
                          <p className="text-slate-100">{call.name}</p>
                          <p className="text-xs text-slate-400">{summarizeToolCall(call)}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Error</p>
                    <p className="mt-1 text-slate-200">{step.error ?? "No error returned."}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Findings</p>
                    {findings.length === 0 && <p className="mt-1 text-slate-400">No findings returned for this step.</p>}
                    {findings.length > 0 && (
                      <ul className="mt-1 list-disc space-y-1 pl-5 text-slate-200">
                        {findings.map((finding, index) => (
                          <li key={`${step.id}-${index}`}>{finding}</li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Evidence</p>
                    {evidence.length === 0 && <p className="mt-1 text-slate-400">No evidence returned for this step.</p>}
                    {evidence.length > 0 && (
                      <ul className="mt-1 list-disc space-y-1 pl-5 text-slate-200">
                        {evidence.map((item, index) => (
                          <li key={`${step.id}-evidence-${index}`}>{item}</li>
                        ))}
                      </ul>
                    )}
                  </div>

                  {step.screenshotUrl && (
                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-500">Screenshot</p>
                      <Image
                        src={step.screenshotUrl}
                        alt={`Trace step ${step.step}`}
                        width={1000}
                        height={600}
                        className="mt-2 h-52 w-full rounded-lg border border-white/10 object-cover"
                      />
                    </div>
                  )}
                </div>
              )}
            </section>
          );
        })}
      </div>
    </Card>
  );
}
