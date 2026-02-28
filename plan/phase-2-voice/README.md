# Phase 2 - Voice: Plan to Audio

## Goal
Convert structured plan into low-latency, playable voice instructions while preserving text fallback.

## Member Tracks (Independent)

### Member A - Text Formatter + Voice API
## Scope
- Transform plan JSON into short imperative steps.
- Chunk instructions for TTS streaming.
- Build `POST /generate-voice` contract and route wiring.

## Deliverables
- Formatter utility: `plan_to_voice_steps(plan)`.
- Rules for chunk size, numbering, and tone.
- API request/response model for voice generation.

## Contract to Others
- Input: validated strategy plan JSON.
- Output: ordered `steps[]` text list, each chunk TTS-ready.
- Exposes stable API contract consumed by UI.

## Acceptance
- Steps are concise and in deployment order.
- No chunk exceeds configured max length.
- API returns text fallback payload shape consistently.

### Member B - TTS + UI/QA
## Scope
- Integrate ElevenLabs streaming client.
- Implement resilient audio generation with retries/timeouts.
- Add UI controls (play, pause, replay).
- Add integration tests for success, timeout, and fallback.

## Deliverables
- `generate_audio(steps)` service with streaming mode.
- Fallback handling for provider timeout or rate-limit.
- UI controls tied to returned audio stream/URL.
- QA coverage for fallback behavior.

## Contract to Others
- Input: `steps[]` from Member A.
- Output: stream handle or audio URL + metadata.
- Uses Member A route contract without custom payload variants.

## Acceptance
- Voice starts quickly on normal network.
- Failures are mapped to standard error envelope.
- User can hear instructions after plan generation.
- Text fallback always available.

## Integration Checklist
1. Verify step ordering matches deployment sequence.
2. Verify TTS fallback path without breaking user flow.
3. Confirm logs capture provider latency and failures.

## Phase Exit Criteria
1. Voice playback works end-to-end.
2. Failures degrade gracefully to text mode.
3. APIs and UI remain backward compatible with Phase 1.
