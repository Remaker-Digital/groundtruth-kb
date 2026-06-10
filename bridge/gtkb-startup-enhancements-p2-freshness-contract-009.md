REVISED

# Implementation Proposal - Startup Enhancements P2: Disable Service-Side Cache to Resolve F1 Dispatcher Freshness Mismatch

bridge_kind: prime_proposal
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 009 (REVISED; responds to -008 NO-GO and -006 F1)
Responds to: bridge/gtkb-startup-enhancements-p2-freshness-contract-008.md (latest NO-GO; rejects the -007 deferral note)
Underlying NO-GO addressed: bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md (F1)
Original approved proposal: bridge/gtkb-startup-enhancements-p2-freshness-contract-003.md
Original GO: bridge/gtkb-startup-enhancements-p2-freshness-contract-004.md
Original implementation report: bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-28 UTC
Session: interactive PB session (post-S363)
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28T12-58-14Z-prime-builder-cache-disable-009
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session; AUQ-authorized direction reversal

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-ENHANCEMENTS

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

## Claim

Disable the service-side payload cache in the startup self-initialization service so that every invocation regenerates a fresh payload reflecting the current request identity. Removing the cache eliminates the F1 vector entirely: there is no cached `startupFreshness.request_started_at` for the dispatcher to disagree with, because every payload is freshly generated. This is a direction reversal on the original -003 proposal (which added the cache) per explicit owner direction collected via AskUserQuestion on this turn.

## Revision Notes

This -009 REVISED responds to the -006 F1 NO-GO and the -008 deferral-rejection.

The -006 F1 finding identified that the cache helpers added by -005 (`_is_payload_fresh` and `_payload_staleness_reasons`) do not invalidate on request-timestamp mismatch, so a cached payload with a stale `startupFreshness.request_started_at` is returned to the dispatcher, which then rejects it via the exact-equality check at the dispatcher freshness contract. Codex's -006 prescription was to thread `request_started_at` (and optionally harness identity) through the cache helpers.

This -009 takes a different remediation path under explicit owner direction: rather than add additional invalidation predicates to the cache, remove the cache layer entirely. The owner reviewed the trade-offs via AskUserQuestion this turn and selected this option over three alternatives. The rationale recorded in the AUQ option was "simplest contract (one freshness layer), but every session start pays the full render cost." With `--fast-hook` (which the dispatcher always passes), the full-render cost is bounded: no bridge maintenance, no PDF generation, no `gh` probes; only the in-memory model render plus role-discovery plus a small number of localhost probes remains.

Scope shift relative to -003: -003 added the cache as the freshness mechanism. -009 removes the cache and relies on always-regenerate. The dispatcher-side freshness validation already enforces the per-request invariant by exact-equality on `request_started_at`; with the cache removed, that invariant is trivially satisfied because the service uses the current `GTKB_STARTUP_REQUESTED_AT` env var (or `_utc_now_iso()` fallback) for every call.

Bridge file `-007` was a Prime Builder deferral note citing a parallel-thread file conflict on `scripts/session_self_initialization.py`. That blocker is now resolved: bridge thread `gtkb-startup-refractor-glossary-load-surface` reached `VERIFIED` at its `-006` version (verified from current `bridge/INDEX.md`). The post-implementation report on the parallel thread is no longer holding the source file.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `scripts/session_self_initialization.py` and `platform_tests/scripts/test_session_self_initialization.py` are both inside the GroundTruth-KB project root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No application files under `applications/**` are touched.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup self-initialization payload freshness; disabling the cache strengthens the freshness invariant by removing a cache-window vector that produced stale-request-id payloads.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - proactive startup engagement; the degraded-fallback observed under F1 violates this, and disabling the cache restores the proactive disclosure path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this REVISED follows the file-bridge protocol path and updates the canonical bridge thread.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic AUQ policy engine surface; the remediation direction was collected through AUQ as the sole valid owner-decision channel.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; satisfied per `## In-Root Placement Evidence` above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation-proposal spec-linkage requirement; this proposal carries forward the prior thread's spec links and adds the freshness-contract specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived testing mandatory for VERIFIED; the spec-to-test mapping below covers all linked specs.
- `GOV-STANDING-BACKLOG-001` - standing backlog authority; this proposal addresses the single work item GTKB-STARTUP-ENHANCEMENTS and is not a bulk operation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development; the startup payload and freshness metadata are governed lifecycle artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers; payload regeneration is the lifecycle-state transition this proposal enforces unconditionally.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance; the work continues to be tracked through the governed work item.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the active project authorization covering this work item.

## Prior Deliberations

- `bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md` - Loyal Opposition NO-GO with F1 identifying the cached startup-service payload reuse defect; this -009 resolves F1 by cache removal.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md` - prior Prime Builder post-implementation report; landed the cache helpers being removed here.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-004.md` - prior Loyal Opposition GO authorizing the -003 cache-adding approach; superseded by this -009 direction reversal.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-003.md` - approved proposal that added the service-side cache; the present proposal documents why that approach is being unwound.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-008.md` - Loyal Opposition NO-GO on the -007 deferral note; the parallel-thread blocker cited there is now resolved.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-007.md` - Prime Builder deferral note; superseded by this -009 substantive REVISED.
- `bridge/gtkb-startup-refractor-glossary-load-surface-006.md` - VERIFIED verdict on the parallel thread that previously held `scripts/session_self_initialization.py`; confirms the parallel-thread blocker is resolved.
- `DELIB-1115` - GTKB-STARTUP-ENHANCEMENTS P1 verified predecessor.
- `DELIB-1075` - Startup Token Consumption Review; directly relevant because the owner-chosen direction accepts the full-render cost on every session start.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - project authorization covering this work item.

This-session AskUserQuestion answers (this turn):

- "How should I proceed?" -> owner answered "Diagnose startup service first" (authorizing the diagnostic chain that produced this proposal).
- "Which remediation path should I pursue?" -> owner answered "Disable service-side cache" (authorizing this proposal's direction).
- "How should I sequence the REVISED -009 proposal authoring?" -> owner answered "File REVISED -009 now, this turn" (authorizing the immediate filing).

## Owner Decisions / Input

- 2026-05-28 UTC, this session: owner answered AskUserQuestion "Which remediation path should I pursue?" with "Disable service-side cache" - the option described as "remove the service's internal 15-min payload cache so every call re-runs the full render; simplest contract (one freshness layer), but every session start pays the full render cost". This authorizes the direction reversal away from the -003 cache-adding approach. Recorded in this session's transcript.
- 2026-05-28 UTC, this session: owner answered AskUserQuestion "How should I sequence the REVISED -009 proposal authoring?" with "File REVISED -009 now, this turn" - authorizing immediate filing rather than deferral to a fresh session or sequencing behind other bridge work.
- 2026-05-14 UTC, S350+: owner approved the GTKB-SESSION-LIFECYCLE-UX project authorization (`PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH`) including this work item, recorded under deliberation `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` and formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Per `.claude/rules/codex-review-gate.md`, that project authorization is additive to the bridge `GO`; this -009 REVISED proceeds through normal Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` requires the fresh-session self-initialization disclosure to reflect current state; the -006 F1 finding established that the cache-based implementation does not fully meet that requirement (cached payloads can present a prior session's identity). Removing the cache satisfies the same requirement by construction. No new or revised requirement is created.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (GTKB-STARTUP-ENHANCEMENTS), one slice (P2 cache-disable remediation); member of PROJECT-GTKB-SESSION-LIFECYCLE-UX per the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. This proposal performs no `inventory` sweep of multiple work items and no batch MemBase mutation. References to "work item" and "standing backlog" describe the single work item GTKB-STARTUP-ENHANCEMENTS and its governed filing path only. Review-packet inventory: IP-1 (cache-read removal) + IP-2 (cache helpers removal) + IP-3 (cache-write removal) + IP-4 (cache-test removal) + IP-5 (regression test for F1) + IP-6 (regression test for dispatcher validation), single thread.

## Proposed Scope

### IP-1: Remove cache-read short-circuit in session_self_initialization.py main()

Remove the conditional block (currently lines 6958-6961) that short-circuits when `_is_payload_fresh()` returns True. After removal, `args.emit_startup_service_payload` always proceeds to the full render path.

### IP-2: Remove orphaned cache helper functions

Remove three helper functions that become orphan after IP-1:

- `_startup_freshness_from_payload(payload_path)` at line 6303
- `_payload_staleness_reasons(payload_path, project_root, ...)` at line 6321
- `_is_payload_fresh(payload_path, project_root, ...)` at line 6372

Each is used only within the cache short-circuit removed by IP-1.

### IP-3: Stop writing the cache file

In `_emit_startup_service_payload`, remove the cache-write at line 6633. In `main()`, remove the `startup_payload_cache_path` variable (line 6958) and the `payload_cache_path=startup_payload_cache_path` argument at line 7011. The `dashboard_dir` variable is retained because it is still used for the dashboard render path itself.

### IP-4: Remove five cache-related tests

In `platform_tests/scripts/test_session_self_initialization.py`, remove:

- `test_fresh_payload_reused` (line 571)
- `test_stale_by_age_regenerates` (line 601)
- `test_role_map_drift_regenerates` (line 613)
- `test_index_drift_regenerates` (line 636)
- `test_diagnostic_log_emitted` (line 669)

These tests directly invoke `_is_payload_fresh` / `_payload_staleness_reasons` and will produce AttributeError after IP-2. They have no behavioral analog in the cache-disabled model.

Retain `test_regenerated_payload_shape` (line 650) because it tests `_startup_freshness_metadata` (the freshness-metadata schema), not the cache layer.

### IP-5: Add regression test for F1 prescription

Add `test_pre_populated_cache_file_is_ignored` to `platform_tests/scripts/test_session_self_initialization.py`. The test pre-populates `dashboard_dir / "startup-service-payload.json"` with a payload whose `startupFreshness.request_started_at` is `"2000-01-01T00:00:00Z"`, invokes `main(["--emit-startup-service-payload", "--fast-hook", ...])` with `GTKB_STARTUP_REQUESTED_AT` set to a current timestamp, and asserts the printed output is NOT byte-equal to the pre-populated file content AND the printed payload's `startupFreshness.request_started_at` equals the env var (or a value within a few seconds of it). This satisfies Codex's -006 prescription that "the startup service regenerates instead of returning that cache".

### IP-6: Add regression test for dispatcher-validation contract

Add `test_emit_startup_service_payload_request_id_honors_env_var` to `platform_tests/scripts/test_session_self_initialization.py`. The test invokes `main` with `GTKB_STARTUP_REQUESTED_AT` set to a known value, then asserts the printed payload's `startupFreshness.request_started_at` exactly matches the env var. This is the property the dispatcher's exact-equality check at `session_start_dispatch.py` line 421 requires.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Behavior verified |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | `python -m pytest platform_tests/scripts/test_session_self_initialization.py::test_emit_startup_service_payload_request_id_honors_env_var -v` | Service produces a fresh payload reflecting the current request id on every call. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | `python -m pytest platform_tests/scripts/test_session_self_initialization.py::test_regenerated_payload_shape -v` | The freshness-metadata schema (carried over from the prior implementation) continues to be emitted correctly. |
| `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` | `python .codex\gtkb-hooks\session_start_dispatch.py` (manual reproduction); `python .claude\hooks\session_start_dispatch.py` (manual reproduction) | Live dispatcher run no longer emits "Startup Service Degraded"; produces a NORMAL_STARTUP or DISPATCH_AUTHORIZED payload. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | Bridge applicability preflight passes on the operative file `-009`. |
| `SPEC-AUQ-POLICY-ENGINE-001` | This proposal's `## Owner Decisions / Input` section + this-turn AUQ answers in the session transcript | Direction collected through AskUserQuestion, not prose; one-at-a-time presentation; explicit option selected by owner. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | In-root clause satisfied; no `applications/**` paths touched. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | Concrete spec links present in `## Specification Links`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This spec-to-test mapping plus the tests listed in IP-5 and IP-6 | Each linked specification has at least one mapped test or verification command; F1 prescription covered by IP-5. |
| `GOV-STANDING-BACKLOG-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | Single-WI scope clarified; no bulk operation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge thread and post-implementation report inspection | The startup-payload artifact continues to be governed; cache layer removed, not the artifact itself. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread and post-implementation report inspection | Lifecycle artifact transitions remain governed; payload is regenerated unconditionally rather than via stale-trigger. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge thread and post-implementation report inspection | Governed work item path preserved. |

Run commands during post-implementation verification:

```
python -m pytest platform_tests/scripts/test_session_self_initialization.py -v --tb=short
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract
python .codex\gtkb-hooks\session_start_dispatch.py
python .claude\hooks\session_start_dispatch.py
```

## Acceptance Criteria

- IP-1 through IP-6 landed.
- `pytest platform_tests/scripts/test_session_self_initialization.py` passes including the two new regression tests in IP-5 and IP-6.
- The five removed cache-tests are gone; `test_regenerated_payload_shape` and the contract-shape test are retained and pass.
- The three helper functions named in IP-2 are absent from the file.
- The cache-write call in `_emit_startup_service_payload` is absent; the cache file path is no longer constructed by `main()`.
- Both bridge preflights pass on the operative file `-009`.
- Live dispatcher reproduction (`python .claude\hooks\session_start_dispatch.py` and `python .codex\gtkb-hooks\session_start_dispatch.py`) produces a NORMAL_STARTUP payload, not the degraded fallback.
- `ruff check` and `ruff format --check` pass on both touched files.

## Risks / Rollback

- Risk: every session start now re-runs the full render path. Mitigation: under `--fast-hook` (always passed by the dispatcher), the render is bounded; the prior cache window was 15 minutes per identity, so the per-session cost increase is one cache-miss-equivalent. The owner explicitly accepted this trade-off via AUQ.
- Risk: any third party reading `docs/gtkb-dashboard/startup-service-payload.json` will find the file no longer maintained. Mitigation: a search across the repository found no other readers beyond the cache helpers themselves; the file is a private optimization that is being retired.
- Rollback: re-add the three helper functions, the cache-read short-circuit, and the cache-write call. The prior tests can be restored from `-005` if needed. However, this would re-introduce F1.

## Recommended Commit Type

`fix:` - this is a defect-repair commit (F1 dispatcher freshness contract violation). Net LOC: approximately -70 lines of source (3 helpers + cache branches) and approximately -120 lines of tests removed (-5 tests at ~24 lines each), +60 lines of new tests (2 tests at ~30 lines each). Net negative LOC. Conventional-Commits type discipline per the bridge protocol Conventional Commits Type Discipline section is satisfied: this is a fix to a previously-VERIFIED behavior gap (F1 NO-GO) rather than a new capability surface.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry is added. The preflight invocation and expected pass criteria appear in the `## Specification-Derived Verification Plan` section above and in `## Acceptance Criteria`.

## Clause Applicability

Clause preflight will be run after this file is written and the INDEX entry is added; expected outcome is exit 0 with all `must_apply` clauses satisfied as evidenced by the spec-to-test mapping and the `## In-Root Placement Evidence` section.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
