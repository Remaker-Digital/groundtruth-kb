NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-project-completion-scanner-addressing-thread-fix-post-impl-revised5
author_model: claude-opus-4-8
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report: Project-Completion Scanner Addressing-Thread Fix (project-scoped D4; F1+F2 closed) (015)

bridge_kind: implementation_report
Document: gtkb-project-completion-scanner-addressing-thread-fix
Version: 015 (NEW post-impl, requesting VERIFIED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Implements: WI-3365
Work Item: WI-3365
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
target_paths: ["scripts/project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/hooks/test_project_completion_surface.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json"]
Implements GO: bridge/gtkb-project-completion-scanner-addressing-thread-fix-014.md
Recommended commit type: feat:

## Summary

Implemented the project-scoped D4 discriminator per the GO'd REVISED-5 proposal (-013, GO at -014), closing both findings from NO-GO -012:

- **F1 (P0) closed** — coverage is now computed project-scoped as `dict[project_id, set[work_item_id]]`. A work item WI-X is VERIFIED *for project P* iff P itself holds an active `relationship='implements'` link to a VERIFIED-topped thread citing WI-X. The prior global-slug union (which let a PROJECT-A link complete a PROJECT-B authorization) is removed entirely. Two new cross-project regression tests reproduce and prevent the exact false positive.
- **F2 (P1) closed** — `platform_tests/hooks/test_project_completion_surface.py` is now within the authorized `target_paths`; its fixture seed update (project-scoped `implements` link) is bridge-authorized.

The v4 GOV spec row and the owner-approved formal-artifact packet are UNCHANGED (the v4 text was already project-scoped at criterion 1; only the -011 code was wrong). No re-insertion, no new packet.

## Owner Decisions / Input

- **S372 AUQ #1** = "Supersede v3 (Recommended)" — authorizes superseding `gtkb-s358-w1-retirement-machinery-correction`.
- **S372 AUQ #2** = "Approve as shown" on the v4 spec text + sha256 `bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f`. The v4 text is UNCHANGED by REVISED-5, so this approval remains valid and no new owner approval was required for this revision.
- **S358 owner-decision** (`DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`): standing PAUTH covering WI-3365.
- No NEW owner decision was required: F1 is a code-correctness fix and F2 is a target-path scope correction; neither changes owner-facing governance semantics.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 — the spec whose project-scoped criterion 1 the implementation now honors; text UNCHANGED, row current at version 4.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec links carried forward from -013.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; the cross-project regression is the F1 evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + PAUTH header present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project-scoped authorization respected.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the v4 packet (already generated + owner-approved; unchanged).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook source files byte-unchanged; only the hook test fixture (now in target_paths) carries the project-scoped seed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable code changes + regression tests; full traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-3365 lifecycle advance on this report.
- `GOV-STANDING-BACKLOG-001` — WI-3365 active under PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — project-scoped discriminator is deterministic SQLite (no LLM).
- `SPEC-AUQ-POLICY-ENGINE-001` — owner authorization via AskUserQuestion.

## Requirement Sufficiency

Existing requirements sufficient. The v4 spec text (project-scoped at criterion 1) is already inserted and UNCHANGED; this revision brought the implementation into conformance with it. No new GOV/SPEC/ADR/DCL required.

## WI Citation Disclosure

Declares work for **WI-3365** only. WI-3438 (v3-misfire evidence) and WI-3442 (sibling classifier-fix WI) are context only. WI-8002 / WI-8001 are synthetic test-fixture ids (not MemBase work items).

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — S358 owner-decision authorizing the governance-correction work.
- `DELIB-2502` — the v3 misfire context this v4 fix closes.
- `DELIB-2503` — owner AUQ chain for the D3+D4+v4 scanner-fix vehicle.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic project-linkage discriminator.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-014.md` (Codex GO of REVISED-5) — the GO this report implements.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-013.md` (Prime REVISED-5) — the project-scoped design this report executes.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-012.md` (Codex NO-GO) — the F1 + F2 findings now closed.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-011.md` (prior post-impl, NO-GO'd) — produced the v4 row + packet, which remain valid and unchanged.

## What Changed Since the -011 Implementation

The -011 implementation (global-slug) is fully replaced by the project-scoped design. Concretely:

**Scanner (`scripts/project_verified_completion_scanner.py`):**
- `_implements_linked_slugs() -> set[str]` (global) → `_implements_links_by_project() -> dict[str, set[str]]` (the SELECT now carries `project_id`, grouped in Python).
- `verified_work_items() -> set[str]` (global decision fn) REMOVED → `_verified_thread_work_items() -> dict[slug, set[wi]]` (VERIFIED threads' WIs) + `verified_work_items_by_project() -> dict[project_id, set[wi]]` (the project-scoped decision view).
- `scan()` looks up `verified_by_project.get(project_id, set())` per authorization.

**Lifecycle (`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`):**
- `_implements_linked_slugs()` → `_implements_links_by_project()` (project-scoped).
- `_verified_work_items(apply_implements_gate=...)` REMOVED → `_verified_thread_work_items()` (staticmethod) + `_verified_work_items_by_project()` (decision view) + `_all_verified_work_items()` (global v3 baseline, confined to the fail-safe diagnostic).
- `_authorization_completion_ready(authorization, verified_for_project)` now receives the project's OWN verified set (caller looks it up by `project_id`).
- `complete_project_authorization()` Step 2 uses `_verified_work_items_by_project().get(project_id, set())`.
- `auto_complete_ready_authorizations()` decides with the project-scoped map; the `include_fail_safe_pauses` diagnostic compares against the global v3 baseline to compute `covered_under_v3` / `missing_under_v4`.

**Tests:** the 6 v4 tests updated to the project-scoped API; 2 NEW cross-project regression tests added (scanner + lifecycle); hook-test fixture seed retained (now authorized via target_paths).

## Spec-to-Test Mapping (Actual Results)

| Specification / Behavior | Test | Result |
|---|---|---|
| v4 F1 — cross-project implements link does NOT satisfy another project (scanner) | `test_cross_project_implements_link_does_not_satisfy_other_project` | PASS |
| v4 F1 — cross-project auto-complete does NOT retire another project (lifecycle) | `test_auto_complete_does_not_cross_project_retire` | PASS |
| v4 — incidental citation excluded (project-scoped) | `test_incidental_citation_thread_does_not_complete_wi`, `test_lifecycle_verified_work_items_implements_gate` | PASS |
| v4 — implements-linked thread completes WI (positive) | `test_implements_linked_thread_completes_wi` | PASS |
| v4 — D3 regression: scan is NOT top-version-only | `test_top_verdict_has_no_work_item_line_but_report_does` | PASS |
| v4 fail-safe — silent pause + manual-review record | `test_fail_safe_no_implements_link_no_completion`, `test_auto_complete_fail_safe_emits_manual_review` | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook parity | `platform_tests/hooks/test_project_completion_surface.py` (4 tests) + byte-identical hook source | PASS |
| no-regression on all existing scanner/lifecycle/hook tests | full targeted pytest (3 files) | PASS (39/39) |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic project-scoped discriminator | inspection: SELECT carries project_id, no LLM | PASS |

## Verification Evidence

### V1. Implementation-start packet (from GO@-014)

```
$ python scripts/implementation_authorization.py begin --bridge-id gtkb-project-completion-scanner-addressing-thread-fix
latest_status: GO
go_file: bridge/gtkb-project-completion-scanner-addressing-thread-fix-014.md
proposal_file: bridge/gtkb-project-completion-scanner-addressing-thread-fix-013.md
requirement_sufficiency: sufficient
expires_at: 2026-05-30T06:08:04Z
target_paths: (7 paths, incl. platform_tests/hooks/test_project_completion_surface.py)
```

### V2. Pre-implementation validation (project-scoped algorithm, synthetic two-project)

Read-only scratch validation BEFORE editing confirmed the corrected query distinguishes projects:

```text
BUGGY global-slug:  implements_slugs = {'thread-a'}  -> WI-8002 leaks globally -> PROJECT-B false positive
CORRECTED scoped:   {PROJECT-A: {thread-a}, PROJECT-B: {}}  -> PROJECT-B not ready  [F1 fixed]
```

### V3. Live-DB smoke of the implemented functions

```
scanner: implements-links-by-project count: 0
scanner: verified-by-project count: 0
lifecycle: links-by-project count: 0
lifecycle: verified-by-project count: 0
lifecycle: global v3 baseline count: 56
auto_complete (default): 0 records (expect 0; no implements links)
```

Confirms: 0 implements links platform-wide → 0 project-scoped coverage → 0 auto-completions (silent-pause fail-safe holds). The global v3 baseline (56) exists but feeds only the fail-safe diagnostic.

### V4. Full targeted pytest suite (39/39 PASS)

```
$ python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py -q --tb=short
collected 39 items
.....                                                                    [ 12%]
....                                                                     [ 23%]
.........................                                               [ 87%]
.                                                                        [ 89%]
....                                                                     [100%]
======================= 39 passed, 1 warning in 35.27s ========================
```

Breakdown: 9 scanner (4 pre-existing + 4 updated v4 + 1 new cross-project), 26 lifecycle (23 pre-existing + 2 updated v4 + 1 new cross-project), 4 hook. +2 net new tests vs the -011 suite (the two cross-project regressions). The 1 warning is upstream chromadb, not from changed code.

### V5. Ruff (all 5 changed files)

```
$ python -m ruff check scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py
All checks passed!
```

### V6. Hook smoke (fail-safe silence)

```
$ python .claude/hooks/project-completion-surface.py < /dev/null
(empty stdout; exit 0)
```

The production hook is silent: zero active `implements` links → no project auto-completes → no spurious retirement. This is the fail-safe direction.

### V7. v4 row unchanged (no re-insertion)

```
$ python -c "...get_spec('GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001')..."
v4 row still current: version 4 | status specified | type governance
```

The v4 row is the same one inserted under -011; this revision did NOT re-insert it and did NOT regenerate the packet (Codex Required Revision #5 condition not triggered — v4 text unchanged).

## Files Changed

| Path | Kind | In target_paths? |
|---|---|---|
| `scripts/project_verified_completion_scanner.py` | edit (project-scoped D4) | YES |
| `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` | edit (project-scoped D4 + fail-safe) | YES |
| `platform_tests/scripts/test_project_verified_completion_scanner.py` | edit (4 updated + 1 new cross-project test) | YES |
| `groundtruth-kb/tests/test_project_artifacts.py` | edit (2 updated + 1 new cross-project test) | YES |
| `platform_tests/hooks/test_project_completion_surface.py` | edit (fixture seed; now authorized per F2) | YES |
| `groundtruth.db` | NOT re-mutated (v4 already current) | YES (authorized-but-unused) |
| `.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json` | NOT changed (existing packet) | YES (authorized-but-unused) |

All seven changed/touched paths are within the GO@-014 target_paths. F2 is fully resolved: no out-of-envelope edit remains.

## Acceptance Criteria Check

| Criterion (from -013) | Status | Evidence |
|---|---|---|
| Codex GO on REVISED-5 | DONE | -014 |
| Fresh impl-start packet from -014 GO | DONE | V1 |
| IP-1 + IP-2 landed: project-scoped `dict[project_id, set[wi]]`; global `verified_work_items()` removed | DONE | code; V3 |
| IP-5: 2 cross-project regression tests PASS; 6 updated v4 tests PASS; all pre-existing PASS | DONE | V4 (39/39) |
| ruff clean on all 5 files | DONE | V5 |
| hook smoke does NOT auto-retire absent implements link | DONE | V6 |
| v4 row current (version 4); no re-insertion; packet unchanged | DONE | V7 |
| F2 resolved: hook test within authorized target_paths | DONE | Files Changed table |
| Codex VERIFIED on this report | PENDING | this report |
| Phase-2 implements-link backfill bridge filed as follow-on | DEFERRED | follow-on after VERIFIED |

## Loyal Opposition Asks

1. Confirm F1 is closed: the cross-project regression tests (`test_cross_project_implements_link_does_not_satisfy_other_project` scanner + `test_auto_complete_does_not_cross_project_retire` lifecycle) prove a PROJECT-A implements link cannot complete/retire PROJECT-B. V2 pre-validation + V3 live smoke corroborate.
2. Confirm the global `verified_work_items()` removal from the scanner and the confinement of the lifecycle `_all_verified_work_items()` to the fail-safe diagnostic match the REVISED-5 design.
3. Confirm F2 is closed: all seven touched paths are within GO@-014 target_paths; no out-of-envelope edit remains.
4. Confirm the v4 row + packet are correctly left unchanged (V7).
5. Confirm `Recommended commit type: feat:` matches the diff (project-scoped D4 + fail-safe + 2 net-new regression tests).
6. Confirm Phase-2 backfill as a separate follow-on is the right next step.

## Risk and Rollback

- **Project-scoped is strictly narrower than -011's global behavior**: it can only remove cross-project false-positive completions, never add completions. Proven by the unchanged positive tests + the new cross-project regressions.
- **Auto-completion paused until Phase-2 backfill**: unchanged; zero implements links at landing → no auto-completion.
- **Hook parity**: source byte-unchanged; 4 hook tests green.
- **v4 row / packet**: unchanged; no drift.

Rollback: `git restore` the 5 source/test files (restores the conservative paused behavior); the v4 spec row is append-only and already landed (no spec rollback); the packet JSON is unchanged.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
