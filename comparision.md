# Spur QA Agent vs QABot Engine (Architecture Breakdown)

Date: 2026-03-02  
Scope: Public Spur product pages + your current codebase

## 1) What Spur appears to do (from public messaging)

Based on Spur's site and docs, their QA system is positioned as:

1. Flow-first test authoring
- Tests are described as real user journeys (not selector-level scripts).
- You can run one-off tests, scheduled runs, and scenario/table-based variants.

2. Browser-native autonomous execution
- Agent interacts with pages in a human-like way.
- Messaging emphasizes stability beyond brittle CSS/XPath coupling.

3. Built-in reporting and alerting loop
- Reports are generated automatically with issue context.
- Integrations/notifications are first-class (e.g., ticketing + chat workflows).

4. Replay-centric debugging UX
- A core differentiator is run playback (video/replay) plus step-level reasoning.
- The product narrative is "see exactly what happened, where, and why."

5. Operational QA platform features
- Docs/navigation indicate scheduling, parallel runs, scenario tables, and "video-to-test" workflows.

Important note: This is an inference from public product/docs messaging, not internal implementation details.

## 2) What QABot does today (actual code behavior)

1. Single LLM orchestration loop
- One loop runs tool calls until model stops or max iterations ([agent_loop.py](d:/opensource/QABot/engine/core/agent_loop.py#L30)).
- Issues are parsed only from final model text JSON ([parsing.py](d:/opensource/QABot/engine/core/parsing.py#L30)).

2. Browser control is low-level and coordinate/action based
- `computer` tool exposes clicks, typing, scroll, keypress, wait ([playwright.py](d:/opensource/QABot/engine/tools/playwright.py#L147)).
- Actions are mostly primitive input events, not semantic "intent" actions.

3. Audits are heuristic snapshots
- You run page/console/perf/security audits with fixed checks ([audit_tools.py](d:/opensource/QABot/engine/tools/audit_tools.py)).
- Good baseline coverage, but limited flow intelligence.

4. Evidence model is screenshot-first, not replay-first
- You persist screenshot URLs and trace/tool outputs ([server/api.py](d:/opensource/QABot/server/api.py#L34), [schemas.py](d:/opensource/QABot/server/schemas.py#L16)).
- No run video artifact in response schema or pipeline.

5. Tasking is generic and shallow by default
- Default objective is broad and single-pass ([constants.py](d:/opensource/QABot/server/constants.py#L1)).
- Prompt asks "test systematically" but without explicit flow graph/planner ([qa_prompts.py](d:/opensource/QABot/engine/prompts/qa_prompts.py#L16)).

## 3) Direct gap analysis (why Spur feels stronger)

| Capability | Spur (publicly positioned) | QABot now | Gap impact |
|---|---|---|---|
| User-flow modeling | Scenario/journey-driven | Generic objective string | Agent can miss critical business flows |
| DOM interaction robustness | "Not tied to CSS/XPath" messaging | Coordinate + key/mouse primitives | Fragile behavior on dynamic UIs |
| Reporting clarity | One-click bug reports + rich context | Raw issues + screenshots + trace JSON | Harder triage for product/QA teams |
| Replay/debugging | Video playback emphasized | No video output artifact | Slower root-cause analysis |
| Step diagnostics | In-depth per-step analysis | Step text + tool outputs only | Weak explainability of failures |
| Test operations | Scheduling, parallel runs, tables | Single run endpoint | Limited CI/load regression readiness |
| Integrations loop | Native ticket/notification positioning | Not part of engine contract | Bugs can be missed operationally |

## 4) What you are missing in the engine (priority order)

## P0 (core quality jump)

1. Flow planner + checkpoints
- Add a pre-execution plan phase that expands objective into ordered journeys/checkpoints.
- Persist plan nodes and completion/failure reason per node.

2. Semantic interaction layer (on top of Playwright)
- Add tools like `click_element_by_text`, `fill_field(label=...)`, `submit_form`, `wait_for_text`.
- Keep coordinate tool as fallback only.

3. Replay artifact pipeline
- Persist Playwright trace/video/HAR per run.
- Return `video_url`, `trace_zip_url`, and step-to-artifact index in API response.

## P1 (reporting + trust)

1. Step-level issue extraction
- Generate findings per step/tool-output, not only final JSON parse.
- Attach `evidence_refs` (screenshot/video timestamp/network event IDs) for each issue.

2. Stronger failure taxonomy
- Distinguish infra/tooling failure vs product bug vs likely false positive.
- Right now blocker fallback is a single generic issue ([agent_loop.py](d:/opensource/QABot/engine/core/agent_loop.py#L130)).

3. Scenario matrix execution
- Support table-driven runs (device x locale x auth-state x network).
- Aggregate regressions and deduplicate repeated issues.

## P2 (platform maturity)

1. Scheduling + retry policy + flake scoring
2. Notification/ticket adapters (Jira/Slack/GitHub)
3. Historical trend analysis (new vs existing issue tracking)

## 5) Suggested architecture evolution for QABot

1. `Planner`
- Input: target URL + context
- Output: flow graph (`landing`, `signup`, `checkout`, etc.) with success assertions

2. `Executor`
- Runs each flow node using semantic tools first, coordinate fallback second
- Captures screenshot + video segment + network/console timeline

3. `Analyzer`
- Merges audit outputs + execution events into evidence-backed findings
- Produces deterministic issue IDs and severity rationale

4. `Reporter`
- Builds human report, machine JSON, and replay links
- Emits notifications/integrations

## 6) Bottom line

Your current engine has a solid baseline (LLM + Playwright + audits), but it is still "single-agent + primitive actions + screenshot evidence."  
Spur's perceived quality advantage is mostly product architecture around flow modeling, replay-quality evidence, and operational reporting loop, not just model intelligence.

## Sources

- Spur homepage: https://www.spurtest.com/
- Spur docs home/navigation: https://docs.spurtest.com/
- Spur FAQ page: https://docs.spurtest.com/introduction/faq
- Spur public roadmap: https://roadmap.spurtest.com/
- Spur YC profile: https://www.ycombinator.com/companies/spur
