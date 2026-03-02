import { BackendScanResponse, BackendToolOutput, ScanIssue, ScanReport, Severity, TraceToolResult } from "@/types/scan";

function safeJsonParse(value: string | null): Record<string, unknown> | null {
  if (!value) return null;
  try {
    const parsed = JSON.parse(value) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
    return parsed as Record<string, unknown>;
  } catch {
    return null;
  }
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  return null;
}

function asString(value: unknown): string | null {
  if (typeof value === "string" && value.trim().length > 0) return value;
  return null;
}

function parseSeverity(value: unknown): Severity {
  const normalized = asString(value)?.toUpperCase();
  if (normalized === "P1" || normalized === "P2" || normalized === "P3") return normalized;
  return "Unknown";
}

function metricTarget(key: "FCP" | "DOM" | "TTFB" | "Resources"): number {
  if (key === "FCP") return 1800;
  if (key === "DOM") return 2000;
  if (key === "TTFB") return 600;
  return 80;
}

function extractScreenshotUrl(toolOutput: BackendToolOutput): string | undefined {
  const value = toolOutput.metadata?.screenshot_url;
  return typeof value === "string" ? value : undefined;
}

function mapBackendIssues(rawIssues: Array<Record<string, unknown>>): ScanIssue[] {
  return rawIssues.map((issue, idx) => {
    const steps = Array.isArray(issue.steps_to_reproduce)
      ? issue.steps_to_reproduce.filter((step): step is string => typeof step === "string")
      : [];

    return {
      id: asString(issue.id) ?? `ISSUE-${idx + 1}`,
      severity: parseSeverity(issue.severity),
      title: asString(issue.title) ?? "Untitled issue",
      category: asString(issue.category) ?? "uncategorized",
      description: asString(issue.description) ?? "",
      stepsToReproduce: steps,
      severityJustification: asString(issue.severity_justification) ?? ""
    };
  });
}

function buildPerformanceMetrics(parsedOutputs: Record<string, unknown>[]) {
  const perfPayload = parsedOutputs.find((item) => typeof item.metrics === "object");
  const perfMetrics = (perfPayload?.metrics as Record<string, unknown> | undefined) ?? {};
  const entries = [
    { key: "FCP" as const, raw: perfMetrics.fcp_ms, unit: "ms" as const },
    { key: "DOM" as const, raw: perfMetrics.dom_content_loaded_ms, unit: "ms" as const },
    { key: "TTFB" as const, raw: perfMetrics.ttfb_ms, unit: "ms" as const },
    { key: "Resources" as const, raw: perfMetrics.resource_count, unit: "count" as const }
  ];

  return entries
    .map((entry) => {
      const value = asNumber(entry.raw);
      if (value === null) return null;
      return {
        key: entry.key,
        value,
        unit: entry.unit,
        target: metricTarget(entry.key)
      };
    })
    .filter((entry): entry is NonNullable<(typeof entries)[number] & { value: number; target: number }> => entry !== null);
}

function buildSecurity(parsedOutputs: Record<string, unknown>[]) {
  const secPayload = parsedOutputs.find((item) => Array.isArray(item.missing_headers) || Array.isArray(item.weak_cookies));
  const missingHeaders = (secPayload?.missing_headers as unknown[]) ?? [];
  const weakCookies = (secPayload?.weak_cookies as unknown[]) ?? [];

  const security = missingHeaders
    .filter((value): value is string => typeof value === "string")
    .map((header) => ({
      header,
      missing: true,
      severity: "P1" as Severity
    }));

  const cookies = weakCookies.flatMap((item) => {
    const obj = item as Record<string, unknown>;
    const cookie = asString(obj.cookie) ?? "unknown-cookie";
    const cookieIssues = Array.isArray(obj.issues) ? obj.issues : [];
    return cookieIssues
      .filter((i): i is string => typeof i === "string")
      .map((issue) => ({
        name: cookie,
        issue,
        severity: "P1" as Severity
      }));
  });

  const status = asNumber(secPayload?.status);
  return { security, cookies, status };
}

export function backendToScanReport(data: BackendScanResponse, forcedId?: string): ScanReport {
  const parsedOutputs = data.tool_outputs
    .map((item) => safeJsonParse(item.output))
    .filter((item): item is Record<string, unknown> => item !== null);

  const issues = mapBackendIssues(data.issues);
  const performance = buildPerformanceMetrics(parsedOutputs);
  const { security, cookies, status } = buildSecurity(parsedOutputs);

  const fcp = performance.find((m) => m.key === "FCP")?.value ?? 0;
  const dom = performance.find((m) => m.key === "DOM")?.value ?? 0;
  const ttfb = performance.find((m) => m.key === "TTFB")?.value ?? 0;
  const perfPenalty = Math.max(0, (fcp - 1800) / 60) + Math.max(0, (dom - 2000) / 90) + Math.max(0, (ttfb - 600) / 40);
  const performanceScore = Math.max(0, Math.min(100, Math.round(100 - perfPenalty)));

  const severity = {
    p1: issues.filter((item) => item.severity === "P1").length,
    p2: issues.filter((item) => item.severity === "P2").length,
    p3: issues.filter((item) => item.severity === "P3").length,
    unknown: issues.filter((item) => item.severity === "Unknown").length
  };
  const riskScore = Math.max(0, Math.min(100, Math.round(severity.p1 * 12 + severity.p2 * 7 + severity.p3 * 3 + severity.unknown * 2)));

  const screenshotSet = new Set<string>();
  data.screenshots.forEach((url) => screenshotSet.add(url));
  data.tool_outputs.forEach((item) => {
    const url = extractScreenshotUrl(item);
    if (url) screenshotSet.add(url);
  });
  const screenshots = Array.from(screenshotSet).map((url, idx) => ({
    id: `shot-${idx + 1}`,
    label: `Screenshot ${idx + 1}`,
    url,
    failed: false
  }));

  let outputCursor = 0;
  const oneToOneStepOutput = data.trace.length === data.tool_outputs.length;

  const trace = data.trace.map((step, idx) => {
    const callCount = step.tool_calls.length;
    let stepOutputs: BackendToolOutput[] = [];

    if (callCount > 0) {
      stepOutputs = data.tool_outputs.slice(outputCursor, outputCursor + callCount);
      outputCursor += callCount;
    } else if (oneToOneStepOutput && data.tool_outputs[idx]) {
      stepOutputs = [data.tool_outputs[idx]];
      if (outputCursor <= idx) outputCursor = idx + 1;
    }

    const toolResults: TraceToolResult[] =
      callCount > 0
        ? step.tool_calls.map((call, callIdx) => {
            const output = stepOutputs[callIdx];
            return {
              toolCallId: call.id,
              toolName: call.name,
              success: output?.success ?? true,
              output: output?.output ?? null,
              outputJson: safeJsonParse(output?.output ?? null),
              error: output?.error ?? null,
              metadata: (output?.metadata as Record<string, unknown>) ?? {},
              screenshotUrl: output ? extractScreenshotUrl(output) : undefined
            };
          })
        : stepOutputs.map((output, outputIdx) => ({
            toolCallId: `step-${step.step}-output-${outputIdx + 1}`,
            toolName: "step_output",
            success: output.success,
            output: output.output ?? null,
            outputJson: safeJsonParse(output.output ?? null),
            error: output.error ?? null,
            metadata: (output.metadata as Record<string, unknown>) ?? {},
            screenshotUrl: extractScreenshotUrl(output)
          }));

    const firstResult = toolResults[0];
    const stepFailed = toolResults.some((item) => !item.success);

    return {
      id: `trace-${step.step}`,
      step: step.step,
      status: stepFailed ? ("failed" as const) : ("success" as const),
      assistantContent: step.assistant_content ?? "",
      toolCalls: step.tool_calls,
      toolResults,
      output: firstResult?.output ?? null,
      outputJson: firstResult?.outputJson ?? null,
      error: firstResult?.error ?? null,
      metadata: firstResult?.metadata ?? {},
      screenshotUrl: firstResult?.screenshotUrl
    };
  });

  const hasFailures = data.tool_outputs.some((item) => !item.success);
  const logs = data.tool_outputs.map((item, idx) => {
    if (item.success) return `Step ${idx + 1}: success`;
    return `Step ${idx + 1}: failed - ${item.error ?? "unknown error"}`;
  });

  return {
    id: forcedId ?? `scan_${Math.random().toString(36).slice(2, 10)}`,
    targetUrl: data.url,
    httpStatus: status ?? null,
    riskScore,
    performanceScore,
    runStatus: hasFailures ? "Failed" : "Completed",
    severity,
    issues,
    performance,
    security,
    cookies,
    screenshots,
    trace,
    toolOutputs: data.tool_outputs,
    rawModelOutput: data.raw_model_output,
    rawJson: data as unknown as Record<string, unknown>,
    logs
  };
}
