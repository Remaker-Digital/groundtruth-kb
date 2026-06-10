NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 1fdfef13-fddf-431a-b209-94b9301ef3b9
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3436

# GT-KB `gt backlog update` CLI - Slice 1 - Implementation Proposal - 001

bridge_kind: prime_proposal

Document: gtkb-backlog-update-cli-slice-1
Version: 001 (NEW)
Date: 2026-05-31 UTC

## Summary

Add a governed `gt backlog update` CLI subcommand (with `python -m groundtruth_kb backlog update` parity) that creates a new append-only version of an existing MemBase `work_items` row with changed fields — primarily `resolution_status`, `stage`, `related_bridge_threads`, and `priority` — via the already-implemented `KnowledgeDB.update_work_item()` API. Implements the cited work item.

**Why this advances the owner-burden-reduction objective (operating-model §1):** there is currently NO governed CLI to update a work item's lifecycle fields after creation. The `gt backlog` group exposes only `add`, `add-work-item`, `list`, `show`, `status`. Consequently, closing a completed work item, attaching a `related_bridge_threads` link so the post-VERIFIED reconciler (`bridge_verified_backlog_reconciler.py`, per `DELIB-S345`) can later auto-resolve it, or correcting any lifecycle field requires either a raw `db.update_work_item()` call (forbidden outside governed surfaces) or a bespoke per-item bridge proposal. This session (S379) demonstrated the cost: an attempt to close one stale work item required a full bridge proposal that was NO-GO'd partly because "the planned governed backlog update command does not exist" (`bridge/gtkb-stale-thread-closure-slice-3-impl-002.md` F1). The missing service converts routine bookkeeping into owner-decision-consuming ceremony. This proposal builds the service so future work-item-state bookkeeping is a single deterministic command, not a bridge round.

This is Slice 1: the `update`/`resolve` CLI surface only. The WITHDRAWN-status writer/doc-parity cluster and the auto-retire multi-slice fix are deliberately scoped to separate follow-on threads to keep this slice a single clean, additive, improvement-origin change.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — standing backlog as the durable cross-session work authority surfaced via `gt backlog`. This proposal adds a governed mutation surface to that authority. The `gt backlog update` command does not itself perform bulk operations; it updates one work item per invocation. `## Clause Scope Clarification (Not a Bulk Operation)` below addresses the `CLAUSE-VISIBILITY-BULK-OPS` clause.
- `GOV-08` — KB is truth: lifecycle-field corrections must be writable to MemBase through a governed, append-only path, not parked in markdown or applied via ad-hoc raw DB writes.
- `GOV-12` — Work item creation triggers linked tests. This proposal mirrors the existing `gt backlog add-work-item` (GOV-12) pattern for its own test coverage; the `update` command does not create work items so it does not itself trigger GOV-12 test creation, but the proposal's own implementation carries spec-derived tests.
- `GOV-13` — Phase assignment. Not triggered by `update` (no new test artifacts created by the command); noted for completeness because the sibling `add-work-item` command enforces it.
- `GOV-15` — Test fix approval gate. The underlying `KnowledgeDB.update_work_item()` already enforces GOV-15 via its `owner_approved` parameter (required `True` to resolve `defect`/`regression` work items). The CLI surfaces an explicit `--owner-approved` flag that threads through to that parameter, preserving the gate. The cited work item is `origin=improvement`, so closing it does not require the flag.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority. This proposal is filed with a `NEW` entry at the top of `bridge/INDEX.md`; append-only; no prior versions rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section enumerates linkage; the Spec-Derived Verification Plan provides the spec-to-test mapping.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Plan below lists executable spec-derived tests; the post-implementation report will carry the spec-to-test mapping with executed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project Authorization` / `Project` / `Work Item` metadata lines at this file's header (lines 9-11).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the bounded-owner-authorization-envelope contract. The cited work item is explicitly included in the active `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` envelope (owner-decision basis `DELIB-2546`, the recorded S379 AUQ chain). The mutation classes `cli_extension` + `test_addition` are within the envelope's `allowed_mutation_classes`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the PAUTH was issued via `gt projects authorize` (envelope schema enforced); this proposal's mutations fall within `allowed_mutation_classes` (`cli_extension`, `test_addition`) and avoid `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — the authorization envelope includes the linked specifications `GOV-STANDING-BACKLOG-001` and `GOV-08`, satisfying the linked-specification requirement for an active authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project authorization does NOT bypass bridge GO, implementation-start packet, target_paths, spec-derived tests, post-implementation report, or VERIFIED. All preserved: implementation-start packet required after GO; `target_paths` bounded below; spec-derived tests in the verification plan; post-implementation report filed for separate VERIFIED review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement. All target paths reside under the GT-KB root `E:\GT-KB\` (in-root): the new CLI logic under `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\`, tests under `E:\GT-KB\groundtruth-kb\tests\`, and the bridge file under `E:\GT-KB\bridge\`. No `applications/` path is touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifact graph: the new command strengthens the work-item ↔ bridge-thread linkage that the artifact graph depends on (the `related_bridge_threads` update path).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle transitions: this command is the governed surface for `work_items` lifecycle-field transitions (`resolution_status`, `stage`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented governance baseline preserved.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the Deterministic Services Principle (repetitive AI plumbing is a defect; move it behind services). This proposal is a direct application: work-item-state bookkeeping is repetitive plumbing that belongs in a CLI, not in per-item bridge ceremony.
- `DELIB-2546` — the recorded S379 owner-decision chain (AskUserQuestion) authorizing this work; the owner-decision basis for the implementation-authorization envelope cited above.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` — the owner-decision basis for the sibling PARALLEL-BATCH PAUTH on the same project; establishes deterministic-services CLI extensions as an owner-authorized mutation class on this project.
- `DELIB-S345` — established `bridge_verified_backlog_reconciler.py` as the canonical post-VERIFIED bookkeeping path. The cited work item exists precisely because work items created without `related_bridge_threads` linkage become invisible to that reconciler; `gt backlog update` is the governed way to attach the linkage retroactively.
- `bridge/gtkb-backlog-add-cli-slice-1-003.md` (REVISED-1, Codex GO at `-004`) — the sibling `gt backlog add` command. This proposal mirrors its module structure, attribution discipline, and test pattern. Establishes that "capture is not implementation approval" and the fail-closed attribution contract this command reuses.
- `bridge/gtkb-kb-attribution-harness-aware-003.md` (Codex GO at `-004`) — the verified harness-aware attribution contract: mutating MemBase writers resolve `changed_by` exclusively via `scripts._kb_attribution.resolve_changed_by()`, which raises `RuntimeError` when no harness resolves. This command reuses that resolver; no `--changed-by` option, env override, or fallback literal may write a row.
- No prior deliberation rejected a `gt backlog update` CLI; the gap is an acknowledged absence, not a previously-considered-and-rejected design.

## Owner Decisions / Input

This proposal proceeds under owner authorization established through two channels:

1. **Project-scoped implementation authorization (durable):** the cited work item is explicitly included in the active `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` (owner-decision basis `DELIB-2546`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, this envelope authorizes bounded `cli_extension` + `test_addition` work without a fresh per-item owner approval, while preserving the full bridge protocol (this proposal + Codex GO + implementation-start packet + tests + report + VERIFIED).
2. **Session scope selection (AskUserQuestion, S379, 2026-05-31), recorded as `DELIB-2546`:** The owner selected the near-term objective "Cut the owner's operational load", then entry point "Tier 1 deterministic-services bundle", then — after discovery showed the work was already tracked — narrowed Slice 1 to "Just WI-3436 (gt backlog update) — cleanest first loop". All three answers were collected via the `AskUserQuestion` tool (`detected_via: ask_user_question`), no prose decision-asks.

These satisfy the AUQ-only enforcement contract and the project-authorization evidence path; no additional per-artifact owner approval is required for this `cli_extension` because it creates no canonical GOV/ADR/DCL/SPEC artifact (it adds CLI code + tests only).

## Requirement Sufficiency

Existing requirements sufficient. No new specification, ADR, DCL, GOV, or PB creation is needed. The cited work item is an already-tracked `improvement`-origin item; the underlying `KnowledgeDB.update_work_item()` API already exists and is governed. This proposal authorizes only a CLI surface (`cli_extension`) plus spec-derived tests (`test_addition`) over that existing API — both within the PAUTH envelope's `allowed_mutation_classes`.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a **single-work-item** mutation command (one `work_items` row updated per invocation), not a bulk standing-backlog operation. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause governs bulk transitions; it is satisfied here by the inventory-free, single-row design plus this proposal-as-review-packet plus the formal-artifact-approval evidence in the Owner Decisions / Input section. The command does not iterate over the backlog, does not perform batch state transitions, and does not change backlog ordering.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli.py` (add the `update` subcommand to the `backlog` group, mirroring `add-work-item` registration at line ~627; add a `resolve` convenience subcommand)
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` (new module: the governed update implementation, mirroring `cli_backlog_add.py` structure — request/error dataclasses, fail-closed attribution, delegation to `KnowledgeDB.update_work_item()`)
- `groundtruth-kb/tests/test_backlog_update_cli.py` (new: spec-derived tests)

No other files are authorized for mutation. `groundtruth.db` is NOT a target_path: this slice ships CLI code + tests only; it performs no canonical MemBase row mutation during implementation (the command is exercised against ephemeral test databases in the test suite, per the existing `add-work-item` test pattern).

## Implementation Plan

After Codex GO:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-backlog-update-cli-slice-1` to create the implementation-start packet from the GO (cites the WI-3436 PAUTH; validates coverage via explicit `included_work_item_ids` membership).
2. Create `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` mirroring `cli_backlog_add.py`:
   - `BacklogUpdateError(Exception)` and a `BacklogUpdateRequest` dataclass.
   - Resolve `changed_by` exclusively via `scripts._kb_attribution.resolve_changed_by()` (fail-closed; no `--changed-by`, no env override, no fallback literal).
   - Delegate to `KnowledgeDB.update_work_item(id, changed_by, change_reason, owner_approved=..., **fields)` with only the explicitly-supplied fields (so unsupplied fields carry forward per the API's merge semantics).
   - Validate `resolution_status` against the documented terminal/non-terminal vocabulary and `stage` against the API's `_VALID_STAGE_TRANSITIONS` graph BEFORE the write, surfacing a clear `BacklogUpdateError` on invalid input (the API also enforces stage transitions; the CLI validates early for a better error).
   - Support `--dry-run` (report the proposed new version + validate without writing) and `--json` output, mirroring `add-work-item`.
3. Register `gt backlog update` and a `gt backlog resolve` convenience wrapper (resolve = update with `--resolution-status resolved --stage resolved`) in `cli.py`'s `backlog` group. Options: `--id` (or positional work-item id), `--resolution-status`, `--stage`, `--priority`, `--related-bridge-threads`, `--status-detail`, `--owner-approved` (threads to the GOV-15 gate), `--change-reason` (required), `--dry-run`, `--json`.
4. Author `groundtruth-kb/tests/test_backlog_update_cli.py` with the spec-derived tests in the verification plan.
5. Run the verification plan; file the post-implementation report for Codex VERIFIED review.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, all spec-derived verification the implementation report will execute. Commands are repo-venv Python / pytest (Windows / PowerShell-valid).

| # | Verification | Spec Coverage | Command | Expected |
|---|---|---|---|---|
| T1 | `gt backlog update` exists + is registered | GOV-STANDING-BACKLOG-001, GOV-08 | `python -m groundtruth_kb backlog update --help` | exit 0; help text lists `--resolution-status`, `--stage`, `--change-reason`, `--dry-run`, `--json` |
| T2 | `gt backlog resolve` convenience exists | GOV-STANDING-BACKLOG-001 | `python -m groundtruth_kb backlog resolve --help` | exit 0; documents resolve = update to resolved |
| T3 | Update writes an append-only new version | GOV-08, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | pytest: create a work item in a temp DB, update its `resolution_status`, assert a new `version` row exists with the new value and the prior version unchanged | PASS |
| T4 | Unsupplied fields carry forward | GOV-08 | pytest: update only `priority`, assert `title`/`origin`/etc. unchanged in the new version | PASS |
| T5 | `related_bridge_threads` is updatable (the motivating case) | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | pytest: attach a `related_bridge_threads` value to a work item created without one; assert it persists | PASS |
| T6 | GOV-15 gate preserved for defect/regression resolution | GOV-15 | pytest: attempt to resolve a `defect`-origin work item without `--owner-approved`; assert it fails; with the flag, assert it succeeds | PASS (fails closed without flag) |
| T7 | Fail-closed attribution | GOV-08 (attribution contract) | pytest: with no resolvable harness, assert the command raises/exits non-zero before any write | PASS (no row written) |
| T8 | `--dry-run` writes nothing | GOV-08 | pytest: `--dry-run` update, assert DB version count unchanged | PASS |
| T9 | Invalid stage transition rejected | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | pytest: attempt an illegal stage transition; assert `BacklogUpdateError` (or API error surfaced) | PASS |
| T10 | Existing backlog tests still pass (non-regression) | GOV-08 | `python -m pytest groundtruth-kb/tests/test_backlog_update_cli.py groundtruth-kb/tests/test_doctor_standing_backlog.py -q` | all PASS |
| T11 | ruff lint + format on changed files | (code quality) | `ruff check <changed.py>` AND `ruff format --check <changed.py>` | both clean |

## Authorization Evidence

Live project-authorization coverage for the cited work item (captured 2026-05-31):

- Active PAUTH: `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` (status `active`, owner-decision `DELIB-2546`).
- `included_work_item_ids`: explicitly includes the cited work item (the Write-time gate `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP` requires explicit inclusion, not membership alone).
- `included_spec_ids`: `["GOV-STANDING-BACKLOG-001", "GOV-08"]` (satisfies `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`).
- `allowed_mutation_classes`: `["cli_extension", "test_addition"]` — this work is exactly those classes.
- `forbidden_operations`: `["deploy", "git_push_force", "spec_deletion"]` — none implicated.
- The implementation-start packet created post-GO will mechanically re-validate coverage and `target_paths`.

## Risk / Rollback

- **Risk: the update command could be used to bypass GOV-15 on defect/regression work items.** Mitigation: the `--owner-approved` flag threads directly to `update_work_item(owner_approved=...)`, which already enforces GOV-15; T6 verifies fail-closed behavior without the flag.
- **Risk: free-text `resolution_status` allows typos.** Mitigation: CLI validates against the documented vocabulary (terminal set `verified/resolved/retired/wont_fix/not_a_defect` plus known non-terminal values) before the write; invalid values surface `BacklogUpdateError`. (Schema-level enforcement is out of scope for this slice; noted as a candidate follow-on.)
- **Risk: attribution fallback writes an unattributed row.** Mitigation: reuse of the verified fail-closed `resolve_changed_by()` resolver; T7 verifies no row is written when attribution cannot resolve.
- **Rollback if NO-GO:** no canonical mutations occur pre-GO; the slice is additive code. If NO-GO post-implementation: `git restore` the two source files + remove the new test file; no MemBase rows are touched by the slice itself.

## Recommended Commit Type

**`feat:`** — adds a net-new governed CLI capability (`gt backlog update` / `gt backlog resolve`). Net-new command surface + new test module. Suggested message:

```
feat(cli): add `gt backlog update`/`resolve` for governed post-creation work-item field updates (Slice 1 of gtkb-backlog-update-cli)
```

## Owner Action Required

None for this NEW. Awaiting Codex GO at `-002` (or NO-GO with findings). After GO, implementation proceeds autonomously under the cited PAUTH per the Implementation Plan; the post-implementation report is filed for Codex VERIFIED review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
