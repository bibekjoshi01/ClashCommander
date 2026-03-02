import { backendToScanReport } from "@/lib/report-adapter";
import { BackendScanResponse, ScanPayload, ScanReport } from "@/types/scan";

const QA_API_URL = process.env.NEXT_PUBLIC_QA_API_URL ?? "http://localhost:8000/api/qa";

function looksLikeBackendResponse(value: unknown): value is BackendScanResponse {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return typeof record.url === "string" && Array.isArray(record.tool_outputs) && Array.isArray(record.trace);
}

function parseContext(contextJson?: string): Record<string, unknown> | undefined {
  if (!contextJson?.trim()) return undefined;
  try {
    const parsed = JSON.parse(contextJson) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return undefined;
    return parsed as Record<string, unknown>;
  } catch {
    return undefined;
  }
}

export async function runScan(payload: ScanPayload): Promise<ScanReport> {
  const context = parseContext(payload.contextJson) ?? {};
  const backendPayload: Record<string, unknown> = {
    url: payload.targetUrl,
    context,
    device_profile: payload.deviceProfile,
    network_profile: payload.networkProfile,
    selected_tools: payload.selectedTools ?? []
  };

  const res = await fetch(QA_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": process.env.NEXT_PUBLIC_QA_API_KEY ?? ""
    },
    body: JSON.stringify(backendPayload),
    cache: "no-store"
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "");
    throw new Error(`Scan failed (${res.status}): ${errorBody || "Unknown backend error"}`);
  }

  const data = (await res.json()) as unknown;
  if (!looksLikeBackendResponse(data)) {
    throw new Error("Invalid backend response shape");
  }

  return backendToScanReport(data);
}
