# Phase 4 - Replanning: Dynamic Adjustments

## Goal
Detect meaningful battle changes and issue focused, delta-only updated strategy instructions.

## Member Tracks (Independent)

### Member A - State Diff + Replan API
## Scope
- Implement battle snapshot storage and diff logic.
- Detect critical events (defense destroyed, CC revealed, tank loss).
- Integrate replan route contracts and state persistence hooks.

## Deliverables
- Event detector with confidence thresholds.
- Event payload schema and severity levels.
- Replan request/response models and storage interface.

## Contract to Others
- Input: sequential state snapshots.
- Output: event list `{type, confidence, timestamp, context}`.
- Provides stable event payload schema for replanner.

## Acceptance
- No false-trigger flood on minor visual changes.
- Critical events detected reliably in fixtures.
- Replan route handles malformed state deltas safely.

### Member B - Replan Engine + Voice/UI/QA
## Scope
- Implement `generate_adjustment(state_update)`.
- Produce plan deltas with versioning and minimal instruction churn.
- Speak only updated instructions, not full-plan replay.
- Add UI event timeline and guardrails (cooldown, max replans/minute).
- Add end-to-end tests for trigger/cooldown/voice-delta behavior.

## Deliverables
- Replanning engine consuming events.
- Plan versioning model and delta format.
- Voice delta playback integration.
- UI change summary components.
- End-to-end safety and stability tests.

## Contract to Others
- Input: prior plan + event list.
- Output: `plan_version`, `changes[]`, `updated_instructions[]`.
- Consumes Member A payload schema without bespoke event formats.

## Acceptance
- Replan only on high-confidence events.
- Delta instructions are short and actionable.
- Replanning improves guidance clarity, not noise.
- Guardrails prevent oscillation and instruction spam.

## Integration Checklist
1. Validate event -> delta-plan -> voice chain.
2. Verify cooldown and max-replan limits.
3. Run scenario tests with multiple event sequences.

## Phase Exit Criteria
1. Dynamic replanning works on meaningful state changes.
2. User receives only relevant incremental instructions.
3. System remains stable under repeated event bursts.
