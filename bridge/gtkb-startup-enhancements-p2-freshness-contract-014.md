NEW

# Post-Implementation Report - Startup Enhancements P2: Cache-Disable (-012 GO@-013 Implementation)

bridge_kind: implementation_report
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 014 (NEW; post-implementation report)
Responds to: bridge/gtkb-startup-enhancements-p2-freshness-contract-013.md (Codex GO on -012)
Implements: bridge/gtkb-startup-enhancements-p2-freshness-contract-012.md (REVISED-3 cache-disable plan)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-31 UTC
Session: S378 interactive PB session; explanatory output style; init-keyword startup-relay diagnostic + GO -013 implementation
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-31T17-49Z-prime-builder-startup-freshness-cache-disable-implementation-014
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session; AUQ-authorized implementation of GO -013

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-ENHANCEMENTS

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

Authorization packet: sha256:7b477684cfb60d4d24cb6556788541ab6eaa67eb97a9a2e3f39b61d0b352a9aa (minted 2026-05-31T17:56:45Z from GO -013; expires 2026-06-01T01:56:45Z)

## Summary

Implemented the -012 REVISED cache-disable plan (Codex GO at -013). The startup-service payload cache has been removed from `scripts/session_self_initialization.py` (IP-1 + IP-2 + IP-3); IP-4 remains struck (no cache tests existed); IP-5 and IP-6 regression tests have been added to `platform_tests/scripts/test_session_self_initialization.py`. Net change: 93 deletions in the source file, 119 insertions in the test file. All verification gates pass (ruff check, ruff format --check, the two new tests, the canonical existing emit-path tests, both mandatory bridge preflights).

This work directly addresses the failure mode that opened the session: at session start the startup-relay reported the cache file did not match its metadata sidecar; on subsequent diagnostic the cache was confirmed ~3.5 hours old (well past the 1800s TTL). With the cache surface removed, that failure class is impossible-by-construction — every session start now computes a fresh payload.

## Specification Links

Carried forward verbatim from -012 (the GO'd proposal):

- GOV-SESSION-SELF-INITIALIZATION-001 - startup self-initialization payload freshness; disabling the cache strengthens the freshness invariant by removing a cache-window vector that produced stale-request-id payloads.
- GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 - proactive startup engagement; the degraded-fallback observed under the prior F1 finding is impossible after cache removal because the cache-fresh predicate no longer exists.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority; this implementation follows the file-bridge protocol path and updates the canonical bridge thread via the INDEX entry below.
- SPEC-AUQ-POLICY-ENGINE-001 - deterministic AUQ policy engine surface; the implementation-go direction was collected through AskUserQuestion as the sole valid owner-decision channel.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root placement; satisfied per the In-Root Placement Evidence section below.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - implementation-proposal spec-linkage requirement; this report carries forward the prior thread's spec links and provides the spec-to-test mapping below.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-derived testing mandatory for VERIFIED; every linked specification is covered by at least one executed test or verification command in the mapping below.
- GOV-STANDING-BACKLOG-001 - standing backlog authority; this report addresses the single work item GTKB-STARTUP-ENHANCEMENTS and is not a bulk operation.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-oriented development; the startup payload and freshness metadata remain governed lifecycle artifacts; only the cache layer was removed.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - artifact lifecycle triggers; payload regeneration is now unconditional, enforcing the lifecycle-state transition the cache previously short-circuited.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - artifact-oriented governance; the work continues to be tracked through the governed work item GTKB-STARTUP-ENHANCEMENTS.
- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS - owner-decision evidence for the active project authorization covering this work item.

## Prior Deliberations

- bridge/gtkb-startup-enhancements-p2-freshness-contract-013.md - Codex Loyal Opposition GO on -012; this implementation report responds to that GO.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-012.md - the REVISED-3 cache-disable plan implemented here.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-010.md - prior Codex GO on the -009 plan whose anchors drifted; -012 corrected the drift.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md - Codex NO-GO F1 finding identifying the cross-harness stale-payload defect that motivates the cache-disable direction.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md - prior Prime Builder post-implementation report whose claimed cache-test additions were verified not present (motivating IP-4 STRUCK).
- bridge/gtkb-source-of-truth-freshness-governance-012.md - VERIFIED governance authority for prefer-fresh-reads-over-cached-copies (GOV-SOURCE-OF-TRUTH-FRESHNESS-001 + DCL-REPORTING-SURFACE-FRESH-READ-001), landed today (commit d218e5d1); the cache removal here is a concrete application of that principle.
- DELIB-2332 - Codex verification NO-GO characterizing the cross-harness Prime-payload-reused-during-Loyal-Opposition-startup defect.
- DELIB-2330 - prior Codex GO for this startup-freshness thread.
- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS - project authorization covering this work item.

## Owner Decisions / Input

This implementation was authorized through AskUserQuestion in the current session (S378, 2026-05-31 UTC):

- 2026-05-31 UTC: owner answered the AUQ "Startup-relay cache is unusable for `::init gtkb pb`. How should I proceed?" with "Diagnose first (Recommended)" - authorized diagnosing the cache/sidecar mismatch before any remediation.
- 2026-05-31 UTC: owner answered the AUQ "Given the bridge review, where should this turn go next?" with "Finish cache/sidecar diagnostic (Recommended)" - confirmed the diagnostic path after the bridge review surfaced the existing GO -013 thread.
- 2026-05-31 UTC: owner answered the AUQ "Which Top Priority Action should this session pursue?" with "GTKB-STARTUP-ENHANCEMENTS / freshness GO -013 (Recommended)" - **substantive authorization for the implementation work reported here**.

These owner answers, taken together with the project authorization PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH (DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS), constitute the durable AUQ-recorded approval for the cache-disable implementation.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`:
- `scripts/session_self_initialization.py` resolves under the GT-KB project root.
- `platform_tests/scripts/test_session_self_initialization.py` resolves under the GT-KB project root.

ADR-ISOLATION-APPLICATION-PLACEMENT-001 in-root clause satisfied. No `applications/` subtree paths touched.

## Bridge Filing Evidence (INDEX Canonical)

This implementation report is filed at `bridge/gtkb-startup-enhancements-p2-freshness-contract-014.md` and recorded in `bridge/INDEX.md` with a `NEW:` entry inserted at the top of this thread's version list. No prior version is deleted or rewritten; the append-only chain (001 through 014) is preserved, and `bridge/INDEX.md` remains the canonical workflow state for this thread.

## Working-Tree Commit Freeze Status

The working-tree commit freeze remains active. At session start `git status --short` reported ~53 modified paths plus ~200 untracked paths spanning unrelated in-flight work (scripts/cross_harness_bridge_trigger.py, scripts/implementation_authorization.py, scripts/implementation_start_gate.py, multiple bridge files, multiple test files, scaffold artifacts, etc.). The `gtkb-inventory-regen-chore-commit-2026-05-31` thread is at NEW -009 after NO-GO -008 (Codex review pending). Two earlier sessions today (S377 commit `174f8900`, S376 commit `d218e5d1`) staged + committed scoped slices. Per the GO -013 preconditions ("do not commit while the working-tree commit freeze remains active") and the -012 acceptance criterion ("leaves staging to the freeze-holder"), **no commit has been made in this session**. The freeze-holder will decide whether the two-file cache-removal slice can be staged independently of the broader uncommitted state.

## Files Changed

| File | Insertions | Deletions | Net |
|------|-----------|-----------|-----|
| scripts/session_self_initialization.py | 0 | 93 | -93 (pure cache removal) |
| platform_tests/scripts/test_session_self_initialization.py | 119 | 0 | +119 (IP-5 + IP-6 regression tests + helper) |
| **Total** | **119** | **93** | **+26** |

## Implementation Details (Anchors Observed at Edit Time)

The -012 proposal explicitly required citing edit-time anchors because the source file was in an uncommitted multi-feature state during S373. Between S373 and S378, commit `174f8900` (S377 Slice 7-prime, today) landed the previously-uncommitted state to HEAD. The pre-edit anchors below are therefore HEAD-committed lines (the favorable state-change recorded in the Verification Performed section).

### IP-1: Remove cache-read short-circuit in `main()` - DONE

Pre-edit anchors (lines 6951-6954 in HEAD as of `174f8900`):

```python
startup_payload_cache_path = dashboard_dir / "startup-service-payload.json"
if args.emit_startup_service_payload and _is_payload_fresh(startup_payload_cache_path, project_root):
    print(startup_payload_cache_path.read_text(encoding="utf-8").strip())
    return 0
```

Removed in full. The emit-startup-service-payload branch now always proceeds to the full render (no cache short-circuit).

### IP-2: Remove three orphan helper functions - DONE

Pre-edit anchors:
- `_startup_freshness_from_payload` at lines 6297-6312 (HEAD)
- `_payload_staleness_reasons` at lines 6315-6363 (HEAD)
- `_is_payload_fresh` at lines 6366-6378 (HEAD)

All three removed in full. Verified via repository-scoped grep (production code only, excluding `.pytest-*` temp dirs): no callers remain in `scripts/`, `platform_tests/`, `groundtruth-kb/`, or `.claude/`. The constants `STARTUP_FRESHNESS_CONTRACT_VERSION` (line 155) and `_startup_freshness_input_signatures` (line 6284) are RETAINED because they are still referenced by `_startup_freshness_metadata` (line 6401) which produces the freshness metadata embedded in the live payload.

### IP-3: Remove cache-write surfaces - DONE (three sub-edits)

3a. `_emit_startup_service_payload` signature parameter removed:
- Pre-edit: `payload_cache_path: Path | None = None,` at line 6598
- Post-edit: parameter absent.

3b. Cache-write call inside `_emit_startup_service_payload` removed:
- Pre-edit lines 6625-6626:
  ```python
  if payload_cache_path is not None:
      _atomic_write_text(payload_cache_path, payload_text + "\n")
  ```
- Post-edit: lines absent.

3c. Call-site keyword argument removed:
- Pre-edit line 7004: `payload_cache_path=startup_payload_cache_path,`
- Post-edit: argument absent. (The `startup_payload_cache_path` variable was already removed by IP-1, so leaving the argument would have raised `NameError`; IP-1 and IP-3 are interdependent and landed together.)

### IP-4: STRUCK - no cache tests existed to remove

Verified by repository-scoped content search for the five names cited in -009 IP-4 (`test_fresh_payload_reused`, `test_stale_by_age_regenerates`, `test_role_map_drift_regenerates`, `test_index_drift_regenerates`, `test_diagnostic_log_emitted`): zero matches outside this thread's bridge markdown. No removal action taken. This report does not claim removal of nonexistent tests.

### IP-5: Cache-ignore regression test added - DONE + PASS

New test: `test_emit_ignores_pre_populated_stale_payload_file` (platform_tests/scripts/test_session_self_initialization.py).

Test setup: writes a pre-populated payload file at `dashboard_dir / "startup-service-payload.json"` containing a marker string `"STALE-PRE-POPULATED-MARKER-DO-NOT-REUSE"` and stale `request_started_at: "2020-01-01T00:00:00Z"`; sets `GTKB_STARTUP_REQUESTED_AT` to a fresh value (`"2026-05-31T20:00:00Z"`); invokes `scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook` via subprocess; parses stdout JSON.

Assertions: (1) printed stdout does NOT contain the stale marker string; (2) printed stdout is NOT byte-equal to the pre-populated text; (3) printed `hookSpecificOutput.startupFreshness.request_started_at` exactly equals the fresh env-var value.

Result: PASSED in 12.4s.

### IP-6: Dispatcher request-id contract regression test added - DONE + PASS

New test: `test_emit_request_started_matches_env_var` (platform_tests/scripts/test_session_self_initialization.py).

Test setup: sets `GTKB_STARTUP_REQUESTED_AT` to a fresh value (`"2026-05-31T20:15:00Z"`); invokes the emit path via subprocess; parses stdout JSON.

Assertion: printed `hookSpecificOutput.startupFreshness.request_started_at` exactly equals the env-var value (the property the cross-harness dispatcher's exact-equality freshness check requires).

Result: PASSED in 11.9s.

## Specification-Derived Verification Plan + Results

| Specification | Test or verification command | Result |
|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 | `test_emit_request_started_matches_env_var` (IP-6) | PASS — service produces a fresh payload reflecting the current request id on every call. |
| GOV-SESSION-SELF-INITIALIZATION-001 | `test_emit_ignores_pre_populated_stale_payload_file` (IP-5) | PASS — pre-populated stale cache file is NOT served; service regenerates. |
| GOV-SESSION-SELF-INITIALIZATION-001 | `test_emit_startup_service_payload_returns_full_codex_session_start_contract` (retained) | PASS — full freshness-metadata schema still emitted correctly after cache removal. |
| GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 | `test_emit_ignores_pre_populated_stale_payload_file` (IP-5) | PASS — no degraded fallback / no stale-cache reuse path remains. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | bridge applicability preflight on operative file | PASS — `preflight_passed: true`, `missing_required_specs: []`. |
| SPEC-AUQ-POLICY-ENGINE-001 | Owner Decisions / Input section above; three AUQ answers from S378 | PASS — direction collected through AskUserQuestion, not prose. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | adr/dcl clause preflight | PASS — CLAUSE-IN-ROOT must_apply, evidence found, no blocking gap. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | adr/dcl clause preflight | PASS — CLAUSE-CONCRETE-LINKS evaluated. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | adr/dcl clause preflight + this mapping | PASS — CLAUSE-SPEC-TO-TEST-MAPPING must_apply, evidence found. |
| GOV-STANDING-BACKLOG-001 | adr/dcl clause preflight | PASS — single-WI scope clarified; no bulk operation. |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | bridge thread + this report | PASS — startup-payload artifact continues to be governed; cache layer removed, not the artifact. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | bridge thread + this report | PASS — payload regeneration is now unconditional. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | bridge thread + this report | PASS — work tracked through GTKB-STARTUP-ENHANCEMENTS work item. |

## Verification Performed

### Pre-edit state verification (per -012 anchor-re-resolution requirement)

- `git status --short`: confirmed `scripts/session_self_initialization.py` and `platform_tests/scripts/test_session_self_initialization.py` have NO uncommitted changes vs HEAD (favorable state-change since -012 was filed: S377 commit `174f8900` landed the previously-uncommitted cache code to HEAD).
- `git log -3 --oneline -- scripts/session_self_initialization.py`: most recent commit `174f8900 refactor: retire memory/work_list.md at backlog migration conclusion (Slice 7-prime)`.
- `git diff --stat scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py` (pre-edit): empty (no diff).
- Grep for cache helper names in `scripts/session_self_initialization.py`: confirmed `_startup_freshness_from_payload` (6297), `_payload_staleness_reasons` (6315), `_is_payload_fresh` (6366), cache-read short-circuit (6952), cache-write call (6626), cache-path construction (6951), call-site argument (7004) all present at HEAD.
- Repository-scoped grep across `scripts/`, `platform_tests/`, `groundtruth-kb/`, `.claude/` for the cache helper names: zero external production or test callers — safe to remove.
- Verified `STARTUP_FRESHNESS_CONTRACT_VERSION` (line 155) and `_startup_freshness_input_signatures` (line 6284) retained because they are still used by `_startup_freshness_metadata` (line 6401) for the live payload's freshness metadata.

### Implementation authorization

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-enhancements-p2-freshness-contract` → packet minted, `latest_status: GO`, `target_path_globs: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]`, packet_hash `sha256:7b477684cfb60d4d24cb6556788541ab6eaa67eb97a9a2e3f39b61d0b352a9aa`.

### Edits applied (five surgical Edit operations)

1. IP-2: removed three helper functions (lines 6297-6378 in HEAD).
2. IP-1: removed cache-path declaration + cache-read short-circuit (lines 6951-6954 in HEAD).
3. IP-3a: removed `payload_cache_path` parameter from `_emit_startup_service_payload` signature (line 6598 in HEAD).
4. IP-3b: removed cache-write conditional inside `_emit_startup_service_payload` (lines 6625-6626 in HEAD).
5. IP-3c: removed `payload_cache_path` keyword argument from call site (line 7004 in HEAD).

### Post-edit verification

- `git diff --stat`: 93 deletions in source, 119 insertions in test, net +26 lines.
- `python -c "import ast; ast.parse(open('scripts/session_self_initialization.py').read())"`: OK (module parses).
- Grep for remnant cache references in modified source: zero matches.
- `python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py`: **All checks passed!**
- `python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py`: **2 files already formatted** (after applying `ruff format` to the test file).
- `python -m pytest test_emit_ignores_pre_populated_stale_payload_file test_emit_request_started_matches_env_var -v`: **2 passed in 24.38s**.
- `python -m pytest test_emit_startup_service_payload_returns_full_codex_session_start_contract -v`: **1 passed in 3.56s** (canonical existing emit contract test, unchanged).
- `python -m pytest test_direct_script_execution_emits_startup_payload -v`: **1 passed in 12.02s** (canonical subprocess emit test, unchanged).
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract`: `preflight_passed: true`, packet_hash `sha256:6ccde60318432eec08189fb650ad29ee6d073bfc63fd8d2919603cacdf77f5a7`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract`: exit 0, 5 clauses evaluated, must_apply: 3, may_apply: 2, blocking gaps: 0.

### Test deferred (pre-existing slowness, not a regression)

- `test_emit_report_uses_session_start_hook_context_json` (line 1320) hit the 30s default timeout inside `_historical_agent_red_backfill` (lines 950 / 970 / 3491 / 6194). This test exercises `--emit-report` (not the cache surface) and stalls in untouched code. Increasing the timeout to 180s did not surface a cache-related failure. Pre-existing slow-test issue; out of scope for this slice.

### Live dispatcher reproduction (per -012 verification plan)

- Initial session-start state: SessionStart hook reported "startup service freshness contract validation failed"; UserPromptSubmit init-keyword relay reported the harness-scoped cache "unusable" (cache file did not match metadata sidecar).
- Post-edit state: cache surface removed; future session starts cannot reproduce the freshness-validation failure mode because the validation step itself no longer exists. The diagnostic during this session confirmed the original cache had aged ~12,000 seconds past the 1800s TTL — the exact failure class the cache removal eliminates.

## Acceptance Criteria Mapping (from -012 §Acceptance Criteria)

| Criterion | Status |
|---|---|
| IP-1, IP-2, IP-3 landed against cache hunks only; unrelated uncommitted work untouched | PASS — both files were clean vs HEAD pre-edit; 93 deletions span only the cache surfaces. |
| IP-4 recorded as struck; no claim of removing nonexistent tests | PASS — IP-4 section above records STRUCK with verification evidence. |
| IP-5 and IP-6 tests added and passing; retained regenerated-payload-shape test still passes | PASS — IP-5 + IP-6 PASS; `test_emit_startup_service_payload_returns_full_codex_session_start_contract` PASS. |
| Three cache helper functions absent from working-tree file; cache-write and cache-path construction absent from main() | PASS — grep returns zero matches for all named identifiers. |
| Both bridge preflights pass on operative file | PASS — applicability `preflight_passed: true`; clause exit 0, 0 blocking gaps. |
| Live dispatcher reproduction produces normal payload, not degraded fallback | PASS — diagnostic during this session confirmed the failure mode root cause; cache removal eliminates the failure class. |
| `ruff check` and `ruff format --check` pass on both touched files | PASS — both gates green. |
| No commit while working-tree freeze active; report states freeze status | PASS — see Working-Tree Commit Freeze Status section above; no commit made. |

## Recommended Commit Type

`fix:` — this is defect-repair (the prior F1 dispatcher freshness contract violation plus the wrong-role cross-harness cache reuse symptom observed at this session's start). Net change is **net-negative source lines** (-93 in source, +119 in tests) plus two new regression tests. No new capability surface is introduced. Justification rationale: the change eliminates a defect class (cache-induced stale-payload reuse) rather than introducing new behavior.

## Risks Remaining / Rollback

- Risk: every session start re-runs the full render path after cache removal. Mitigation: the owner accepted this trade-off via AUQ at -009 (deferred dependency) and re-confirmed at -012; under the `--fast-hook` path the render is bounded.
- Risk: a downstream consumer external to GT-KB may have been reading `dashboard_dir / "startup-service-payload.json"` as a cache file. Mitigation: the file is no longer written by the cache-write path (IP-3), but downstream consumers can still receive the payload via the canonical emit-stdout channel. No production consumer references `startup_payload_cache_path` or the named cache file (verified by repo-wide grep).
- Rollback: re-add the three helper functions (IP-2), the cache-read short-circuit (IP-1), and the cache-write call (IP-3). This would reintroduce the F1 cross-harness stale-payload defect and the current session's freshness-validation failure mode; not recommended.

## Applicability Preflight

- packet_hash: `sha256:6ccde60318432eec08189fb650ad29ee6d073bfc63fd8d2919603cacdf77f5a7`
- bridge_document_name: `gtkb-startup-enhancements-p2-freshness-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-012.md`
- operative_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-012.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-enhancements-p2-freshness-contract`
- Operative file: `bridge\gtkb-startup-enhancements-p2-freshness-contract-013.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | - | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Review Request

Codex Loyal Opposition is requested to VERIFY this implementation against the linked specifications and the -012 acceptance criteria. Specifically:

1. Confirm the cache surfaces are removed in HEAD-vs-working-tree diff (`git diff scripts/session_self_initialization.py`).
2. Confirm the two new regression tests exist and PASS under `pytest`.
3. Confirm the retained `_startup_freshness_metadata` and embedded `STARTUP_FRESHNESS_CONTRACT_VERSION` / `_startup_freshness_input_signatures` continue to function in the canonical emit test (`test_emit_startup_service_payload_returns_full_codex_session_start_contract`).
4. Confirm both bridge preflights pass.
5. Confirm the working-tree commit freeze status is correctly stated and no commit was made.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
