# Harness Envelope Equivalence Evidence

- evidence_id: `harness_envelope_equivalence`
- status: `WARN`
- baseline: `WI-4950` - Add cross-harness activity-envelope projection and result-envelope parity
- generated_at: `2026-07-06T01:37:24.603820+00:00`

## Summary

- harness_count: `6`
- typed_waiver_count: `4`
- missing_evidence_harnesses: `ollama, cursor, openrouter`

| Harness | Classification | Activity | Result | Session | Session evidence | Typed waivers |
| --- | --- | --- | --- | --- | --- | --- |
| `codex` (`A`) | `equivalent` | `equivalent`/native | `equivalent`/native | `equivalent`/native | `equivalent` | - |
| `claude` (`B`) | `equivalent` | `equivalent`/native | `equivalent`/native | `equivalent`/native | `equivalent` | - |
| `antigravity` (`C`) | `equivalent` | `equivalent`/native | `equivalent`/native | `equivalent`/native | `equivalent` | - |
| `ollama` (`D`) | `missing-evidence` | `equivalent-with-limits`/compact-provider | `equivalent-with-limits`/compact-provider | `equivalent-with-limits`/compact-provider | `missing-evidence` | WAIVER-P2-OLLAMA-EVENT-SOURCE, WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE |
| `cursor` (`E`) | `missing-evidence` | `equivalent`/native | `equivalent`/native | `equivalent`/native | `missing-evidence` | - |
| `openrouter` (`F`) | `missing-evidence` | `equivalent-with-limits`/compact-provider | `equivalent-with-limits`/compact-provider | `equivalent-with-limits`/compact-provider | `missing-evidence` | WAIVER-P2-OPENROUTER-EVENT-SOURCE, WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE |

## Typed Waivers

- `ollama` `WAIVER-P2-OLLAMA-EVENT-SOURCE` (event_source): Ollama is a receive-only Loyal Opposition provider harness in Phase 2 and has no native event-firing hook surface.
- `ollama` `WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE` (full_transcript_archive): Ollama is an API/provider harness and does not own a full interactive transcript archive equivalent to desktop harnesses; parity is assessed through compact dispatch/result/session envelopes.
- `openrouter` `WAIVER-P2-OPENROUTER-EVENT-SOURCE` (event_source): OpenRouter is a receive-only Loyal Opposition provider harness in Phase 2 and has no native event-firing hook surface.
- `openrouter` `WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE` (full_transcript_archive): OpenRouter is an API/provider harness and does not own a full interactive transcript archive equivalent to desktop harnesses; parity is assessed through compact dispatch/result/session envelopes.

## Verified Sharding Boundary

Existing envelope-sharding implementation is treated as verified coverage and is not reopened by WI-4968.
- `bridge/gtkb-session-activity-envelope-sharding-umbrella-004.md`
- `bridge/gtkb-envelope-sharding-taxonomy-baseline-006.md`
- `bridge/gtkb-envelope-sharding-harness-projection-parity-004.md`
- `bridge/gtkb-envelope-sharding-compact-query-modes-004.md`

## Evidence Gaps

- `ollama`: `missing-evidence`; session evidence: no session-envelope file found
- `cursor`: `missing-evidence`; session evidence: no session-envelope file found
- `openrouter`: `missing-evidence`; session evidence: no session-envelope file found
