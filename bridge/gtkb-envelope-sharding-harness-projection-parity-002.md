GO
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: 2026-07-01T08-47-50Z-loyal-opposition-F-f9f575
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

# Loyal Opposition Review — Cross-Harness Activity Projection And Result-Envelope Parity

bridge_kind: lo_verdict
Document: gtkb-envelope-sharding-harness-projection-parity
Reviewing: bridge/gtkb-envelope-sharding-harness-projection-parity-001.md (NEW)
Version: 002
Date: 2026-07-01 UTC

## Verdict

**GO** — The proposal is properly scoped, spec-linked, PAUTH-authorized, and passes all mandatory preflight gates. The session-context independence check passes (author session: `019f1bfe-9f4b-7bc2-805e-c051192b5a73` != reviewer session: `2026-07-01T08-47-50Z-loyal-opposition-F-f9f575`).

## Evidence

- All 11 `target_paths` exist in the worktree.
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py` already derives `can_fire_events` and `can_receive_dispatch` capability axes but has no activity-envelope or result-envelope dimension — the proposed extension is coherent with the existing schema.
- `config/agent-control/harness-capability-registry.toml` (parity_schema_version=1) defines per-capability harness surfaces with native/adapter/fallback status but no activity-envelope or result-envelope representation — this is the gap the proposal targets.
- `config/harness-parity/phase2-waivers.toml` has typed waivers (6 retired, 2 active for Ollama/OpenRouter event_source) following the PARITY-WAIVER-SCHEMA — the proposal preserves this semantics.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4950` authorizes mutation classes: docs, CLI, tests, skills, config — all target_paths fall within these classes.
- Both preflights pass cleanly (applicability + clause gates, exit 0).

## Applicability Preflight

- packet_hash: sha256:a7d9a8e3c924a6c5767a728239c6744eaaad48591941e937ec7dc8cc7a99133f
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- All blocking specs cited and matched.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: gtkb-envelope-sharding-harness-projection-parity
- Clauses evaluated: 5 (must_apply: 3, may_apply: 2)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Gate: PASS

## Concerns (non-blocking)

1. **Cross-Harness Disposition appears copy-pasted from WI-4949**: The disposition says "Claude: native `.claude` hook/skill surfaces listed in `target_paths` must preserve the canonical behavior for this slice." But this proposal's target_paths do not include any `.claude/` files — they are all config, scripts, and test files. The Prime Builder should either fix the disposition or confirm it applies to the actual target_paths.

2. **Provider lane result-envelope parity is underspecified**: The Claim says "compact result-envelope availability across ... Ollama, and OpenRouter" but provider harnesses (D, F) do not own native hook surfaces or envelope infrastructure. The proposal should clarify whether "result-envelope parity" for provider lanes means (a) documenting their inherent limitations as typed waivers, or (b) building infrastructure they cannot use. Option (a) aligns with existing phase2-waivers.toml semantics; option (b) would be a scope mismatch.

3. **Orthogonality to envelope sharding**: This WI is about harness capability representation, which is adjacent to but distinct from session/activity envelope sharding. The proposal should clarify the dependency relationship with WI-4949 — does WI-4950 depend on WI-4949 completing first, or can they proceed in parallel?

None of these concerns are blocking; they are advisory notes for the Prime Builder to address in the implementation-start packet.

## Prior Deliberations

- DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE — owner directive to complete all child work items and retire the project.
- DELIB-202665110 — umbrella program authorization.
- DELIB-20266631 — LO context for activity-envelope sharding.
- DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION — prior envelope refinement.
- DELIB-20265287 — single-active activity envelope and headless eligibility.
- DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME — context-load profile anatomy.
- DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE — existing harness parity waivers and active provider-lane limitations.