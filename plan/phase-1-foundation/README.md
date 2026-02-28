# Phase 1 - Foundation: Screenshot to Plan

## Goal
Deliver end-to-end flow: image upload -> building detection -> normalized base JSON -> validated attack plan JSON.

## Member Tracks (Independent)

### Member A - Vision + API Skeleton
## Scope
- Implement detection runner interface.
- Implement normalized output processor.
- Provide fixture outputs for test images.
- Create FastAPI app skeleton and request/response models for analysis route.

## Deliverables
- `vision/detector.py` contract-compatible output.
- `vision/processor.py` normalized schema output.
- 3 sample JSON outputs from known TH3-TH5 images.
- API models for `POST /analyze-image`.

## Contract to Others
- Output JSON keys: `image_meta`, `buildings`, `zone_density`, `risk_map`.
- Building label set and confidence thresholds documented.
- Exposes typed base JSON payload consumed by planner flow.

## Acceptance
- Same input image returns deterministic normalized JSON.
- Invalid images return explicit error (no crash).
- API model validation works for valid/invalid upload payloads.

### Member B - Strategy + Integration/UI
## Scope
- Define plan schema and validator.
- Create prompt builder from base JSON + game data.
- Implement retry-once and fallback heuristic planner.
- Build `POST /analyze-image` integration and minimal upload UI.
- Add integration test for full flow.

## Deliverables
- Strategy schema file and validator.
- Planner function: `generate_plan(base_json)`.
- Fallback plan path with `source=fallback`.
- Wired endpoint returning `base_json` + `attack_plan`.
- UI page for upload and plan display.

## Contract to Others
- Input: normalized base JSON from Member A.
- Output: strict plan JSON with `entry_side`, `army_plan`, `deployment_order`, `contingencies`, `reasoning_summary`, `source`.
- Consumes Member A API model without changing vision contract keys.

## Acceptance
- Invalid LLM output never leaks to API response.
- All returned plans pass local validator.
- Uploading fixture image returns valid `base_json` + `attack_plan`.
- Error envelope is consistent for failures.

## Integration Checklist
1. Confirm JSON schema version used by all tracks.
2. Validate 3 common fixtures end-to-end.
3. Measure basic latency and log bottlenecks.

## Phase Exit Criteria
1. One-click upload returns validated plan.
2. No unhandled errors in happy/failure paths.
3. Contracts are documented and stable for Phase 2.
