REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 1fdfef13-fddf-431a-b209-94b9301ef3b9
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3436

# GT-KB `gt backlog update` CLI - Slice 1 - Implementation Proposal - 003 (REVISED-1)

bridge_kind: implementation_proposal

Document: gtkb-backlog-update-cli-slice-1
Version: 003 (REVISED-1; responds to Codex NO-GO at -002)
Date: 2026-06-01 UTC
Responds to NO-GO: bridge/gtkb-backlog-update-cli-slice-1-002.md

## Claim

This REVISED-1 closes the single blocking finding from Codex NO-GO `-002` (P1-001: GOV-15 can be bypassed by status-only resolution). It makes no other scope change.

**The confirmed defect:** `KnowledgeDB.update_work_item()` enforces GOV-15 only through `_validate_stage_transition()`, which returns early when `new_stage == current_stage` (`groundtruth-kb/src/groundtruth_kb/db.py:3351`); the gate runs only when `new_stage == "resolved"` (`db.py:3374`). So `update_work_item(resolution_status="resolved", owner_approved=False)` on a `defect`/`regression` work item — with no stage change — reaches `resolution_status=resolved` while skipping the owner-approval gate. Codex's live probe confirmed: `NO_EXCEPTION resolved created 2`.

**The fix (CLI-layer, fail-closed):** the `gt backlog update` / `gt backlog resolve` CLI treats any transition of `resolution_status` to a terminal value (`resolved`, and the broader terminal set `verified/retired/wont_fix/not_a_defect` for completeness) on a work item whose `origin in {"defect","regression"}` as GOV-15-gated — **independent of whether `--stage` is supplied**. The CLI performs this check BEFORE delegating to `update_work_item()`; without `--owner-approved`, the command exits non-zero and writes no row. This binds terminal `resolution_status` semantics to the same approval requirement that currently sits behind `stage="resolved"`, per Codex's recommended minimal fix (option 1).

This fix is contained to the CLI layer (`cli_backlog_update.py`); `target_paths` are unchanged (no DB-layer modification needed). The DB-layer coupling gap is noted as a separate follow-on candidate (a deeper fix binding the gate to `resolution_status` inside `update_work_item()` itself), but is out of scope for this slice — the CLI is the governed surface this proposal introduces, and making it fail closed fully satisfies the GOV-15 requirement for this surface.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — standing backlog as the durable cross-session work authority surfaced via `gt backlog`. This proposal adds a governed mutation surface. Single-work-item, not bulk; see `## Clause Scope Clarification`.
- `GOV-08` — KB is truth: lifecycle-field corrections must be writable through a governed, append-only path.
- `GOV-12` — Work item creation triggers linked tests. The `update` command does not create work items; the proposal's own implementation carries spec-derived tests.
- `GOV-13` — Phase assignment. Not triggered by `update`.
- `GOV-15` — Test fix approval gate (THE central spec for this REVISED). The CLI enforces GOV-15 at the command layer for terminal `resolution_status` transitions on `defect`/`regression` work items, fail-closed, regardless of `--stage`. This corrects the bypass where the underlying `update_work_item()` runs GOV-15 only on a `stage` change to `resolved`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority; append-only INDEX update.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section; spec-to-test mapping in the verification plan.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Plan lists executable spec-derived tests, including the new GOV-15 negative/positive tests Codex required.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project Authorization` / `Project` / `Work Item` metadata at the header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the cited work item is explicitly included in the active `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` (owner-decision basis `DELIB-2546`); mutation classes `cli_extension` + `test_addition` within the envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — mutations within `allowed_mutation_classes`; no `forbidden_operations`.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — envelope includes `GOV-STANDING-BACKLOG-001` + `GOV-08`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — bridge GO, impl-start packet, target_paths, spec-derived tests, report, VERIFIED all preserved.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root: CLI under `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\`, tests under `E:\GT-KB\groundtruth-kb\tests\`, bridge under `E:\GT-KB\bridge\`. No `applications/` path touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — strengthens work-item ↔ bridge-thread linkage (`related_bridge_threads` update path).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — governed surface for `work_items` lifecycle-field transitions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented baseline.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the Deterministic Services Principle; this CLI is a direct application.
- `DELIB-2546` — the recorded S379 owner-decision chain (AskUserQuestion) authorizing this work; owner-decision basis for the implementation-authorization envelope.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` — owner-decision basis for the sibling PARALLEL-BATCH PAUTH on the same project; deterministic-services CLI extensions are an owner-authorized mutation class here.
- `DELIB-S345` — established `bridge_verified_backlog_reconciler.py` as the post-VERIFIED bookkeeping path; the motivating case for the `related_bridge_threads` update.
- `bridge/gtkb-backlog-add-cli-slice-1-003.md` (REVISED-1, Codex GO at `-004`) — the sibling `gt backlog add` command; this proposal mirrors its module structure, attribution discipline, and test pattern.
- `bridge/gtkb-kb-attribution-harness-aware-003.md` (Codex GO at `-004`) — the verified fail-closed attribution contract this command reuses.
- Codex NO-GO `bridge/gtkb-backlog-update-cli-slice-1-002.md` — the verified GOV-15 status-only-bypass finding this REVISED closes; the rejected approach (status/stage-split gate coupling) is documented here and not repeated.
- No prior deliberation rejected a `gt backlog update` CLI; the gap was an acknowledged absence.

## Owner Decisions / Input

This proposal proceeds under owner authorization established through two channels:

1. **Project-scoped implementation authorization (durable):** the cited work item is explicitly included in the active `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` (owner-decision basis `DELIB-2546`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, this authorizes bounded `cli_extension` + `test_addition` work without a fresh per-item owner approval, while preserving the full bridge protocol. Per Codex NO-GO `-002` "Implementation Context", no new owner decision is needed for this NO-GO because the mutation classes and target paths are unchanged.
2. **Session scope selection (AskUserQuestion, S379), recorded as `DELIB-2546`:** owner selected objective "Cut the owner's operational load" → "Tier 1 deterministic-services bundle" → "Just WI-3436 (gt backlog update) — cleanest first loop". All via the `AskUserQuestion` tool (`detected_via: ask_user_question`).

No additional per-artifact owner approval is required for this `cli_extension` (it creates no canonical GOV/ADR/DCL/SPEC artifact).

## Requirement Sufficiency

Existing requirements sufficient. No new specification needed. The fix tightens the CLI to honor the existing `GOV-15` requirement; it does not create or change a requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a **single-work-item** mutation command (one `work_items` row updated per invocation), not a bulk standing-backlog operation. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause is satisfied by the inventory-free, single-row design plus this proposal-as-review-packet plus the Owner Decisions / Input evidence. The command does not iterate the backlog, batch-transition state, or change ordering.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli.py` (add `update` + `resolve` subcommands to the `backlog` group)
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` (new module: governed update implementation with the CLI-layer GOV-15 fail-closed check)
- `groundtruth-kb/tests/test_backlog_update_cli.py` (new: spec-derived tests, including the GOV-15 status-only negative test and the owner-approved coherent-terminal-state positive test)

Unchanged from `-001`. The fix is contained to `cli_backlog_update.py`; no DB-layer file is modified, so `groundtruth.db` and `db.py` are NOT in `target_paths`. (Per Codex `-002` Implementation Context: target_paths stay unchanged unless the correction requires a DB-layer change; it does not — the CLI-layer fail-closed check is sufficient for this governed surface.)

## Implementation Plan

After Codex GO:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-backlog-update-cli-slice-1` to create the implementation-start packet.
2. Create `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` mirroring `cli_backlog_add.py`:
   - `BacklogUpdateError(Exception)` and a `BacklogUpdateRequest` dataclass.
   - Resolve `changed_by` exclusively via `scripts._kb_attribution.resolve_changed_by()` (fail-closed; no `--changed-by`, no env override, no fallback literal).
   - **GOV-15 CLI-layer gate (the `-002` fix):** before any write, fetch the target work item. If the requested `resolution_status` is in the terminal set (`{resolved, verified, retired, wont_fix, not_a_defect}`) AND the work item's `origin in {defect, regression}` AND `--owner-approved` was not supplied, raise `BacklogUpdateError` and exit non-zero with NO write. This check is independent of `--stage`. (Defense in depth: the call to `update_work_item(owner_approved=...)` still passes the flag through, but the CLI no longer relies on a stage change to trigger the gate.)
   - Delegate to `KnowledgeDB.update_work_item(id, changed_by, change_reason, owner_approved=..., **fields)` with only the explicitly-supplied fields (unsupplied fields carry forward).
   - Validate `resolution_status` against the documented vocabulary and `stage` against `_VALID_STAGE_TRANSITIONS` before the write; surface a clear `BacklogUpdateError` on invalid input.
   - Support `--dry-run` (which also runs the GOV-15 check and reports the would-be refusal) and `--json`.
3. Register `gt backlog update` and `gt backlog resolve` in `cli.py`'s `backlog` group. `resolve` = update with `--resolution-status resolved --stage resolved` (so the convenience path always reaches a coherent terminal state). Options: `--id` (or positional), `--resolution-status`, `--stage`, `--priority`, `--related-bridge-threads`, `--status-detail`, `--owner-approved`, `--change-reason` (required), `--dry-run`, `--json`.
4. Author `groundtruth-kb/tests/test_backlog_update_cli.py` with the verification-plan tests, including the new GOV-15 tests T6a/T6b.
5. Run the verification plan; file the post-implementation report for Codex VERIFIED review.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Commands are repo-venv Python / pytest (Windows / PowerShell-valid).

| # | Verification | Spec Coverage | Command | Expected |
|---|---|---|---|---|
| T1 | `gt backlog update` exists + registered | GOV-STANDING-BACKLOG-001, GOV-08 | `python -m groundtruth_kb backlog update --help` | exit 0; lists `--resolution-status`, `--stage`, `--owner-approved`, `--change-reason`, `--dry-run`, `--json` |
| T2 | `gt backlog resolve` convenience exists | GOV-STANDING-BACKLOG-001 | `python -m groundtruth_kb backlog resolve --help` | exit 0; documents resolve = update to resolved (stage + status) |
| T3 | Update writes an append-only new version | GOV-08, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | pytest: create WI in temp DB, update `resolution_status`, assert new `version` row with new value + prior version unchanged | PASS |
| T4 | Unsupplied fields carry forward | GOV-08 | pytest: update only `priority`, assert other fields unchanged | PASS |
| T5 | `related_bridge_threads` is updatable (motivating case) | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | pytest: attach `related_bridge_threads` to a WI created without one; assert persisted | PASS |
| **T6a** | **GOV-15 status-only bypass CLOSED (the `-002` fix; negative test)** | **GOV-15** | pytest: on a `defect`-origin WI, run the CLI update path equivalent to `update WI-X --resolution-status resolved --change-reason ...` with NO `--stage` and NO `--owner-approved` | **non-zero exit; NO new row written; resolution_status stays non-terminal** |
| **T6b** | **GOV-15 positive: owner-approved coherent terminal state** | **GOV-15** | pytest: same WI with `--owner-approved` (and `resolve` semantics or explicit `--stage resolved`); assert success | **PASS; final state resolution_status="resolved" AND stage="resolved"** |
| T6c | GOV-15 not over-applied to non-defect | GOV-15 | pytest: resolve an `improvement`-origin WI without `--owner-approved` | PASS (improvement is not gated; succeeds) |
| T7 | Fail-closed attribution | GOV-08 (attribution contract) | pytest: with no resolvable harness, assert raise/exit non-zero before any write | PASS (no row) |
| T8 | `--dry-run` writes nothing (and reports the GOV-15 refusal when applicable) | GOV-08, GOV-15 | pytest: `--dry-run` on a gated defect resolution without `--owner-approved`; assert DB unchanged + refusal reported | PASS |
| T9 | Invalid stage transition rejected | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | pytest: illegal stage transition; assert `BacklogUpdateError` | PASS |
| T10 | Existing backlog tests still pass (non-regression) | GOV-08 | `python -m pytest groundtruth-kb/tests/test_backlog_update_cli.py groundtruth-kb/tests/test_doctor_standing_backlog.py -q` | all PASS |
| T11 | ruff lint + format on changed files | (code quality) | `ruff check <changed.py>` AND `ruff format --check <changed.py>` | both clean |

The new **T6a** is the exact status-only defect/regression negative test Codex required (no `--stage`, no `--owner-approved` → non-zero exit, no row). **T6b** is the owner-approved positive counterpart proving a coherent terminal state. **T6c** guards against over-applying the gate to non-defect origins.

## Authorization Evidence

(Unchanged from `-001`.) Active PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` (status `active`, owner-decision `DELIB-2546`); explicitly `included_work_item_ids=["WI-3436"]`; `included_spec_ids=["GOV-STANDING-BACKLOG-001","GOV-08"]`; `allowed_mutation_classes=["cli_extension","test_addition"]`; `forbidden_operations=["deploy","git_push_force","spec_deletion"]`. Codex `-002` independently confirmed this PAUTH is active and in-scope.

## Risk / Rollback

- **Risk (the `-002` finding): GOV-15 bypass via status-only resolution.** CLOSED by the CLI-layer fail-closed gate (Implementation Plan step 2); verified by T6a (negative) + T6b (positive) + T6c (no over-application).
- **Risk: the DB-layer `update_work_item()` retains the underlying coupling.** Acknowledged: the DB-layer gate still keys on stage. This proposal's CLI is fail-closed regardless, so the *governed surface* is safe. A deeper DB-layer fix (bind the gate to `resolution_status` inside `update_work_item()`) is a separate candidate captured as a follow-on; it is out of this slice's scope and target_paths.
- **Risk: free-text `resolution_status` typos.** CLI validates against the documented vocabulary before write.
- **Risk: attribution fallback writes an unattributed row.** Reuse of the verified fail-closed resolver; T7 verifies.
- **Rollback if NO-GO:** no canonical mutations pre-GO; additive code. If NO-GO post-implementation: `git restore` the two source files + remove the new test file.

## Recommended Commit Type

**`feat:`** — net-new governed CLI capability. Suggested message:

```
feat(cli): add `gt backlog update`/`resolve` with fail-closed GOV-15 gate for governed post-creation work-item field updates (Slice 1 of gtkb-backlog-update-cli)
```

## Owner Action Required

None for this REVISED. Awaiting Codex GO at `-004` (or NO-GO). After GO, implementation proceeds autonomously under the cited PAUTH; the post-implementation report is filed for Codex VERIFIED review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
