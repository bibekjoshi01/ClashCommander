# Phase 3 - Live Screen: Frame Ingestion

## Goal
Replace static screenshot input with live frame ingestion while controlling analysis frequency and cost.

## Member Tracks (Independent)

### Member A - Frame Capture + Live API
## Scope
- Implement frame ingestion endpoint or stream adapter.
- Standardize frame resizing, format conversion, and timestamping.
- Build live analysis route contracts and input validation.

## Deliverables
- Frame intake module with validated frame payload.
- Preprocessing pipeline with deterministic output shape.
- Route models for live frame requests/responses.

## Contract to Others
- Output: processed frame packet `{frame_id, ts, image_bytes, meta}`.
- Guarantees consistent dimensions and color format.
- Exposes stable live payload for orchestration layer.

## Acceptance
- Frame packets are valid under sustained input.
- Corrupt frames are dropped with explicit warnings.
- Live endpoint validation rejects malformed frames safely.

### Member B - Orchestration + UI/Observability
## Scope
- Implement throttling/debouncing policy.
- Trigger analysis only on user action or configured interval.
- Add UI controls for start/analyze/stop.
- Add metrics for fps, queue depth, call rate, and latency.

## Deliverables
- Scheduler logic for controlled vision/strategy calls.
- Cache policy for duplicate/similar frames.
- Live mode UI controls and states.
- Integration tests for trigger behavior and throttling.

## Contract to Others
- Input: frame packets from Member A.
- Output: same plan schema as Phase 1.
- Consumes Member A route contract without changing payload shape.

## Acceptance
- No unbounded model calls under high frame rate.
- Repeated similar frames do not trigger duplicate planning.
- User can run live mode without API instability.
- Metrics clearly show model call rate and latency.

## Integration Checklist
1. Validate policy: no analysis on every frame.
2. Verify response schema parity with Phase 1.
3. Validate performance under representative frame rates.

## Phase Exit Criteria
1. Live frame mode works with controlled analysis.
2. Cost/latency remains bounded under test load.
3. Plan output remains contract-compatible.
