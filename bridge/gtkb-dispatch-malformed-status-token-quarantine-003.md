NEW

# Post-implementation report — Bridge Dispatch Must Fail Gracefully on a Malformed Bridge-File Status Token

bridge_kind: implementation_report
Document: gtkb-dispatch-malformed-status-token-quarantine
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-18 UTC
Responds-to: bridge/gtkb-dispatch-malformed-status-token-quarantine-002.md (LO GO)
Implements: bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md (Prime proposal NEW)

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: 94112412-fe8d-406f-9f4b-d03dc87f2ee1
author_model: claude-opus-4-7
author_model_version: opus-4-7
author_model_configuration: claude-code-cli; durable role prime-builder; session-stated role prime-builder (per owner AUQ init keyword captured 2026-06-18); interactive (no GTKB_BRIDGE_POLLER_RUN_ID)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4658-DISPATCH-MALFORMED-STATUS-TOKEN-GRACEFUL-QUARANTINE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4658

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: bridge_dispatch_malformed_status_graceful_degradation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implementation of the Prime proposal at `-001` per Codex Loyal Opposition GO at `-002`. The three coordinated changes plus six focused-test additions described in the proposal are implemented and verified:

1. **Typed permanent-error class.** Added `MalformedBridgeStatusError(WorkIntentRegistryError)` in `scripts/bridge_work_intent_registry.py`, raised by `_bridge_file_status` at both malformed sites (unrecognized status line, empty file). The exception carries `path` and `offending_line` attributes so callers can structure diagnosis. Subclassing preserves every existing `except WorkIntentRegistryError` call site (backward-compatible).
2. **Quarantine-and-continue batch acquire.** In `scripts/cross_harness_bridge_trigger.py`, `_acquire_prime_work_intent_batch` now catches `MalformedBridgeStatusError` separately: it records a structured `bridge_file_malformed_status_quarantined` finding in `dispatch-failures.jsonl` (with `path` and `offending_line`), adds the slug to a `quarantined_slugs` result field, and continues to the next slug instead of failing the batch. Non-malformed `WorkIntentRegistryError` and ordinary lease contention retain prior all-or-nothing semantics. When every selected slug is quarantined, the batch returns `ok: False` with reason `all_slugs_quarantined` so the caller does not spawn an empty dispatch. The trigger call site persists the returned quarantined slugs to the recipient's `quarantined_threads` field in `dispatch-state.json` so health and diagnostics can read them.
3. **Dispatch-health finding.** In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `_runtime_findings_for_recipient` now reads the new `quarantined_threads` field from each recipient state row and, when non-empty, appends a WARN-level finding listing the unique slugs (sorted, de-duplicated) and the unique count. `gt bridge dispatch health` no longer reports topology-only `PASS` while threads are quarantined.

The proposal's append-only / non-destructive boundary is preserved: the malformed file at `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` is NOT mutated; the fix makes dispatch robust to it.

## Specification Links (carried forward)

Per the proposal at `-001`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the numbered `bridge/<slug>-NNN.md` chain is the canonical workflow surface; a malformed status token must be handled deterministically as drift, not allowed to crash the dispatch lane.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch health/liveness must reflect whether bridge work is actually progressing; a quarantined thread must surface as a finding rather than topology-only `PASS`.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — selected bridge work that cannot be routed (malformed status) must produce a deterministic, recorded failure that does not block routing of other selected work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report carries the proposal's spec linkage forward.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project authorization, project, work item, and target_paths metadata are present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Results section below maps each change to focused tests and executed commands.
- `GOV-STANDING-BACKLOG-001` — WI-4658 records this defect in MemBase.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — a malformed canonical bridge file is a lifecycle-drift artifact requiring deterministic handling (quarantine + health finding), not a silent crash.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the fix is a durable, tested, artifact-tracked repair to a load-bearing dispatch surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the defect, owner decision, work item, and authorization are captured as durable artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation and test targets are inside the GT-KB project root.

## Prior Deliberations

Per the proposal `-001` Prior Deliberations:

- `DELIB-20265221` — owner AUQ decision (2026-06-18): "Fix the live poisoning first." Authorizes this graceful-degradation fix.
- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-001.md` (NEW) and `-002.md` (NO-GO) — sibling thread covering the *orphan `.lo-verdict.md`* class. This implementation deliberately scopes to the distinct malformed-token failure.
- "Keep normal bridge lease contention out of dispatch failure logs" precedent — preserved by recording the new `bridge_file_malformed_status_quarantined` reason rather than overloading the existing contention path.
- `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` — the live victim file whose `GO test` token is the observed poison. This implementation does not modify it (append-only); it makes dispatch robust to it.

Plus this implementation cycle:

- Codex GO at `-002` (LO verdict; `bridge/gtkb-dispatch-malformed-status-token-quarantine-002.md`). The GO confirmed `WI-4658` membership in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, that `PAUTH-...-DISPATCH-MALFORMED-STATUS-TOKEN-GRACEFUL-QUARANTINE` covers `source` and `test_addition` mutation classes for the six target paths, and that the applicability and clause preflights both PASS at filing time.

## Owner Decisions / Input

No additional owner decision is required for this implementation. The proposal `-001` cited `DELIB-20265221` (owner AUQ "Fix live poisoning first") as the owner-decision authority; Codex confirmed the scope at `-002`.

For session-stated role: this implementation session declared `prime-builder` via the owner AUQ init-keyword on 2026-06-18 (the AUQ answer was the literal `::init gtkb pb`; the per-session marker at `.claude/session/role-94112412-fe8d-406f-9f4b-d03dc87f2ee1.json` survived a subsequent SessionStart cycle and provided positive Prime evidence for the `go_implementation` claim gate throughout this implementation).

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes the canonical numbered-file chain and treats divergence as drift; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` already requires dispatch health to reflect actual work progress, not just topology. This is a robustness repair to existing dispatch and work-intent behavior, not a new bridge protocol or a new status token. The proposal's claim of requirement sufficiency is carried forward unchanged.

## Files Changed

| File | Status | Lines | Mutation class |
|---|---|---|---|
| `scripts/bridge_work_intent_registry.py` | modified | +37 / -4 | source |
| `scripts/cross_harness_bridge_trigger.py` | modified | +69 / -4 | source |
| `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` | modified | +15 / -0 | source |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | modified | +56 / -0 | test_addition |
| `platform_tests/scripts/test_cross_harness_bridge_trigger.py` | modified | +214 / -0 | test_addition |
| `platform_tests/scripts/test_bridge_dispatch_config.py` | modified | +124 / -0 | test_addition |

Diff stat: `6 files changed, 511 insertions(+), 4 deletions(-)`. All within proposal's six target_paths.

## Spec-Derived Verification Results

| Specification | Verification command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` (typed error) | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_malformed_bridge_status_error_is_workintent_subclass platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_raises_malformed_on_unrecognized_first_line platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_raises_malformed_on_empty_file platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_returns_canonical_status_unchanged platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_skips_leading_blank_lines -q --no-header` | yes | PASS — 5 passed in 1.34s. Backward-compat (subclass), live victim pattern (`GO test`), empty-file path, all 8 canonical status tokens unchanged, blank-prefix preservation. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` (batch quarantine-and-continue) | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k wi4658 -q --no-header` | yes | PASS — 4 passed in 1.50s. Covers: (a) quarantine + acquire remaining + structured dispatch-failure record; (b) `all_slugs_quarantined` reason when only malformed remain; (c) all-or-nothing preserved for transient `WorkIntentRegistryError` (DB error/contention); (d) mixed quarantine + transient: transient releases acquired, quarantined preserved for caller persistence. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (health WARN finding) | `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -k wi4658 -q --no-header` | yes | PASS — 4 passed in 4.86s. Covers: (a) non-empty `quarantined_threads` emits WARN finding with `recipient_key`, unique count, and sorted slugs; (b) empty list emits no finding (non-regression); (c) repeated slugs across cycles deduplicate to deterministic count + listing; (d) defensive handling of non-dict entries and missing-`slug` entries. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this Spec-Derived Verification Results table + the proposal's `Spec-to-test mapping` | yes | PASS — spec-to-test mapping for every linked spec with executed evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (append-only filing) | This file is the next numbered bridge file for the thread; no prior version rewritten; `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` left untouched. | yes | PASS — append-only discipline preserved. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine` | yes at `-001`/`-002` review time per LO verdict | PASS — carried forward unchanged. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` against the 6 target paths | yes | PASS — all 6 modified files within `E:\GT-KB`. No artifact resolves outside the project root. |
| Pre-file code quality — ruff check | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <6 target files>` | yes | PASS — All checks passed! |
| Pre-file code quality — ruff format --check | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <6 target files>` | yes | PASS — 6 files already formatted (one file auto-formatted during implementation; re-check confirms clean). |

## Live Failure Mode Reproduction (pre-implementation evidence)

Before the implementation: `prime-builder` and `prime-builder:A` recipients in `.gtkb-state/bridge-poller/dispatch-state.json` were stuck at `last_result: work_intent_acquire_failed` with 50+ matching failures in the recent `dispatch-failures.jsonl` log, all stemming from the malformed `GO test` first-line token in `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md`. The crash-loop was confirmed live during scope assessment. After implementation, that failure mode no longer head-of-line-blocks the entire dispatch lane: the affected slug is quarantined, the remaining selected slugs proceed, and a structured WARN finding surfaces in `gt bridge dispatch health`.

## Behavior Preservation Evidence

- Canonical status tokens unchanged: `test_bridge_file_status_returns_canonical_status_unchanged` exercises all 8 (`NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, `WITHDRAWN`).
- Blank-prefix preservation: `test_bridge_file_status_skips_leading_blank_lines` confirms leading blank lines are still skipped (no false-positive malformed raise).
- Transient-error semantics preserved: `test_wi4658_batch_preserves_all_or_nothing_for_transient_errors` proves a non-malformed `WorkIntentRegistryError` (e.g., DB lock contention) still triggers all-or-nothing release of previously-acquired slugs.
- Existing `except WorkIntentRegistryError` call sites unaffected: subclass relationship verified by `test_malformed_bridge_status_error_is_workintent_subclass` (also satisfied by the catch-base-class fallback in the modified `_acquire_prime_work_intent_batch`).
- Empty-quarantine-list non-regression: `test_wi4658_health_silent_when_no_quarantined_threads` proves the health surface stays silent when there are no quarantined threads (no false-positive WARN).

## Risk / Rollback

Per proposal `-001`. No new risk surfaces materialized during implementation. The quarantine branch is additive and gated on a new typed exception, so non-malformed paths are unchanged. Rollback is a single-commit revert of the six implementation files; quarantine state under `.gtkb-state/` is regenerable runtime evidence that will clear on the next dispatch cycle once the malformed bridge file is repaired.

## Bridge Filing

This implementation report is filed as the next status-bearing numbered bridge file under `bridge/gtkb-dispatch-malformed-status-token-quarantine-003.md`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs a live bridge-dispatcher failure mode (head-of-line block on a single malformed canonical bridge file) with no new user-facing workflow surface. The carried-forward proposal `Recommended Commit Type` is `fix`; preserved.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
