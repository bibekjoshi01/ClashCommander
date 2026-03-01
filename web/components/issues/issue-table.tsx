"use client";

import { Fragment, useMemo, useState } from "react";
import { ArrowUpDown, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TBody, TD, TH, THead } from "@/components/ui/table";
import { ScanIssue } from "@/types/scan";

function severityTone(severity: ScanIssue["severity"]) {
  if (severity === "P1") return "critical" as const;
  if (severity === "P2") return "warn" as const;
  return "info" as const;
}

function severityRank(severity: ScanIssue["severity"]) {
  if (severity === "P1") return 0;
  if (severity === "P2") return 1;
  if (severity === "P3") return 2;
  return 3;
}

export function IssueTable({ issues }: { issues: ScanIssue[] }) {
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("All");
  const [category, setCategory] = useState("All");
  const [sortBy, setSortBy] = useState<"id" | "severity" | "title">("severity");
  const [expanded, setExpanded] = useState<string | null>(null);

  const categories = useMemo(() => {
    const values = Array.from(new Set(issues.map((item) => item.category)));
    return values.sort((a, b) => a.localeCompare(b));
  }, [issues]);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().trim();
    return [...issues]
      .filter((item) => (severity === "All" ? true : item.severity === severity))
      .filter((item) => (category === "All" ? true : item.category === category))
      .filter((item) => {
        if (!q) return true;
        const haystack = [item.id, item.title, item.category, item.description, item.severityJustification].join(" ").toLowerCase();
        return haystack.includes(q);
      })
      .sort((a, b) => {
        if (sortBy === "severity") return severityRank(a.severity) - severityRank(b.severity);
        return a[sortBy].localeCompare(b[sortBy]);
      });
  }, [issues, severity, category, query, sortBy]);

  return (
    <Card className="p-4">
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-500" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search issues" className="pl-9" />
        </div>
        <Select className="w-36" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option>All</option>
          <option>P1</option>
          <option>P2</option>
          <option>P3</option>
          <option>Unknown</option>
        </Select>
        <Select className="w-52" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option>All</option>
          {categories.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </Select>
      </div>

      <div className="overflow-x-auto">
        <Table>
          <THead>
            <tr>
              <TH>
                <button className="inline-flex items-center gap-1" type="button" onClick={() => setSortBy("id")}>
                  ID <ArrowUpDown className="h-3 w-3" />
                </button>
              </TH>
              <TH>
                <button className="inline-flex items-center gap-1" type="button" onClick={() => setSortBy("severity")}>
                  Severity <ArrowUpDown className="h-3 w-3" />
                </button>
              </TH>
              <TH>Category</TH>
              <TH>
                <button className="inline-flex items-center gap-1" type="button" onClick={() => setSortBy("title")}>
                  Title <ArrowUpDown className="h-3 w-3" />
                </button>
              </TH>
            </tr>
          </THead>
          <TBody>
            {filtered.length === 0 && (
              <tr>
                <TD colSpan={4} className="py-10 text-center text-slate-500">
                  No matching issues for current filters.
                </TD>
              </tr>
            )}

            {filtered.map((item) => (
              <Fragment key={item.id}>
                <tr className="cursor-pointer hover:bg-white/[0.03]" onClick={() => setExpanded(expanded === item.id ? null : item.id)}>
                  <TD>{item.id}</TD>
                  <TD>
                    <Badge tone={severityTone(item.severity)}>{item.severity}</Badge>
                  </TD>
                  <TD>{item.category}</TD>
                  <TD>{item.title}</TD>
                </tr>

                {expanded === item.id && (
                  <tr>
                    <TD colSpan={4} className="bg-black/25">
                      <div className="space-y-3 text-sm">
                        <div>
                          <p className="text-[11px] uppercase tracking-wide text-slate-500">Description</p>
                          <p className="mt-1 text-slate-300">{item.description || "Not provided"}</p>
                        </div>
                        <div>
                          <p className="text-[11px] uppercase tracking-wide text-slate-500">Severity Justification</p>
                          <p className="mt-1 text-slate-300">{item.severityJustification || "Not provided"}</p>
                        </div>
                        <div>
                          <p className="text-[11px] uppercase tracking-wide text-slate-500">Steps To Reproduce</p>
                          {item.stepsToReproduce.length === 0 && <p className="mt-1 text-slate-400">Not provided</p>}
                          {item.stepsToReproduce.length > 0 && (
                            <ol className="mt-1 list-decimal space-y-1 pl-5 text-slate-300">
                              {item.stepsToReproduce.map((step, index) => (
                                <li key={`${item.id}-${index}`}>{step}</li>
                              ))}
                            </ol>
                          )}
                        </div>
                      </div>
                    </TD>
                  </tr>
                )}
              </Fragment>
            ))}
          </TBody>
        </Table>
      </div>
    </Card>
  );
}
