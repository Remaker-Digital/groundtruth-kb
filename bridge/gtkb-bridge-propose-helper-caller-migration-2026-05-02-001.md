NEW

# Implementation Proposal — Bridge-Propose Helper Caller Migration

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Migrate INDEX.md status-line writers (currently using direct `Edit` tool calls or unvalidated raw inserters) to delegate through `scripts/gtkb_bridge_writer.py`'s validation + live-snapshot-bound write path. Replaces the rejected "new helper" framing of the prior threads.

## Revision Rationale (relative to prior threads)

This is a **net-new scoping bridge** for the same work item, deliberately re-framed per the Codex `-006.md` Recommended Action ("delegate to, or refactor, `scripts/gtkb_bridge_writer.py` so validation and insertion are bound to the same live INDEX snapshot"). Both prior thread terminations are reconciled:

- **`gtkb-bridge-propose-helper-index-parity-2026-04-30-004.md` NO-GO** rejected the original raw all-status inserter on governance-bypass grounds.
- **`gtkb-bridge-propose-helper-index-parity-2026-05-02-006.md` NO-GO** rejected the dual-write `add_status_line` design as the same governance-bypass class plus a parity test that didn't prove the contract. Codex F1 explicitly directed the next attempt to either (a) add validation to a new helper, (b) scope to Prime-only statuses, or (c) **delegate to or refactor `gtkb_bridge_writer.py`**. This proposal takes path (c).

Path (c) is now feasible because the existing `scripts/gtkb_bridge_writer.py` already implements:
- Live-snapshot-bound `read_index(project_root)` (`scripts/gtkb_bridge_writer.py:76`).
- Full role/status/transition validation in `validate_transition(document_name, proposed_status, role_slot, project_root)` (lines 152–225).
- Status constants `VALID_STATUSES`, `PRIME_STATUSES`, `LOYAL_OPPOSITION_STATUSES`, role constants `PRIME_ROLE_SLOT`, `LOYAL_OPPOSITION_ROLE_SLOT` (lines 22–27).
- `BridgeTransitionError` for illegal moves (line 43).

## Specification Links

1. **`.claude/rules/file-bridge-protocol.md`** lines 87–93 — assigns `NEW`/`REVISED` to Prime, `GO`/`NO-GO`/`VERIFIED` to LO. Caller migration enforces this contract mechanically at every status-line write.
2. **Live writer** `scripts/gtkb_bridge_writer.py` lines 22–225 — the validation surface this proposal migrates callers onto.
3. **Phase 7 plan** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md` — referenced in `gtkb_bridge_writer.py` module docstring as the contract source.
4. **Prior threads (reconciled, not superseded as audit records)**:
   - `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-{001..004}.md` (4 versions; terminal NO-GO).
   - `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-{001..006}.md` (6 versions; terminal NO-GO).
   These are bridge-history evidence; this thread is the substantive successor.
5. **GOV-19-A1** (Outside-in testing) — primary tests exercise the migrated callers (the actual file-edit surfaces) plus the validator's rejection paths.
6. **Owner pre-approval** — work_list row 24 carries program-level owner pre-approval ("This should be tracked and completed at the next opportunity," S324 owner directive).
7. **Prior Deliberations search**: pending probe (will run as the first implementation step). Active prior context is the bridge-thread audit per item 4 above.

## Scope

### In-scope

Files modified:
- **`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`** — refactor existing `propose_bridge()` to validate via `gtkb_bridge_writer.validate_transition(...)` before INDEX write. Add new `add_status_line(document_name, status, version, *, role_slot, project_root)` function that also delegates to validate_transition then performs the atomic write through the writer's API.
- **`.claude/skills/bridge-propose/helpers/write_bridge.py`** — mirror the refactor (this is the live editable copy that S327 actually invokes).
- **Caller migration** — identify Prime-side direct `Edit` calls on `bridge/INDEX.md` (likely zero non-skill callers in the repo, but probe will confirm) and route them through the helper. Out-of-skill callers (scripts that hand-edit INDEX) are reported in post-impl with a list; they are migrated in this commit if any exist.

Files created (tests):
- **`groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py`** — primary tests proving the migrated callers go through `validate_transition` + tests proving illegal transitions raise `BridgeTransitionError` via the helper.
- Existing `groundtruth-kb/tests/test_bridge_propose_helper.py` — extended where necessary (probe at impl start).

Documents (per GOV-20):
- `IPR-BRIDGE-PROPOSE-HELPER-MIGRATION-001`, `CVR-BRIDGE-PROPOSE-HELPER-MIGRATION-001` — KB document rows.

### Out-of-scope

- Refactor of `gtkb_bridge_writer.py` itself (already passes its contract; only callers change).
- LO-side writers (Codex's smart-poller-runner has its own atomic write path; not a Prime caller).
- Helper API design beyond `propose_bridge()` and `add_status_line()` — additional helpers (e.g., bulk INDEX rewrite) deferred to follow-on bridges.
- Mechanical hook-level enforcement that rejects raw `Edit` calls on `bridge/INDEX.md` — separate hardening work; this slice migrates known callers.

## Implementation Plan

1. Probe direct INDEX writers across repo (`grep -r "INDEX.md" --include="*.py"` plus tool-history audit). Report list in post-impl.
2. Probe `propose_bridge()` current implementation in both helper copies (live `.claude/...` and templated `groundtruth-kb/templates/...`).
3. Refactor `propose_bridge()` to:
   - Compute next version via `gtkb_bridge_writer.next_version(document_name, project_root)` (existing).
   - Validate via `validate_transition(document_name, "NEW", role_slot=PRIME_ROLE_SLOT, project_root)`.
   - Write the response file first, then update INDEX through the writer's API (preserves the file-first-then-INDEX ordering).
4. Add `add_status_line(document_name, status, version, *, role_slot, project_root)`:
   - Validate via `validate_transition(...)`.
   - Compute next-state INDEX content via the writer's helpers.
   - Atomic write via the writer's INDEX-write helper.
5. Mirror in both helper copies. The packaged template (`groundtruth-kb/templates/skills/...`) and the live shadow copy (`.claude/skills/...`) must stay byte-equal; T-PARITY (in-test bytecmp) enforces this.
6. Migrate any direct Prime `Edit` calls on INDEX to `add_status_line()`.
7. IPR + CVR documents.

## Spec-to-test mapping

### Primary tests — outside-in (validator + helper surfaces)

| # | Test | Behavior |
|---|---|---|
| TP-MIG-1 | `test_propose_bridge_calls_validate_transition_before_writing` | mock the writer; assert `propose_bridge()` calls `validate_transition` with role_slot=PRIME_ROLE_SLOT, status='NEW' |
| TP-MIG-2 | `test_propose_bridge_refuses_when_validate_transition_raises` | inject a `BridgeTransitionError`; assert `propose_bridge()` propagates it without writing INDEX |
| TP-MIG-3 | `test_add_status_line_validates_role_slot_against_status` | call `add_status_line(... status='GO', role_slot=PRIME_ROLE_SLOT)`; assert raises BridgeTransitionError (Prime not authorized for GO) |
| TP-MIG-4 | `test_add_status_line_refuses_illegal_transition` | fixture INDEX with latest=VERIFIED; call `add_status_line(... status='REVISED', role_slot=PRIME_ROLE_SLOT)`; assert raises BridgeTransitionError (no transitions after VERIFIED) |
| TP-MIG-5 | `test_add_status_line_succeeds_for_valid_revised_after_no_go` | fixture INDEX with latest=NO-GO; `add_status_line(... status='REVISED', role_slot=PRIME_ROLE_SLOT)` writes the new line atomically |
| TP-MIG-6 | `test_add_status_line_succeeds_for_valid_post_impl_NEW_after_GO` | fixture INDEX with latest=GO; `add_status_line(... status='NEW', role_slot=PRIME_ROLE_SLOT)` writes the post-impl NEW line |
| TP-MIG-7 | `test_helper_template_and_live_copies_byte_equal` | T-PARITY: assert `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` and `.claude/skills/bridge-propose/helpers/write_bridge.py` are byte-equal |

### Supplemental helper-level tests

| # | Test | Behavior |
|---|---|---|
| TS1 | `test_validate_transition_imported_from_writer_not_redefined` | static check that the helper module imports `validate_transition` from `scripts.gtkb_bridge_writer`, not redefining it locally |

## Verification Commands

```
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py groundtruth-kb/tests/test_bridge_propose_helper.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/ -k bridge -v
$ uv run --project groundtruth-kb ruff check groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py
```

## Risk and Rollback

- **Risk: import-path breakage.** The helper modules don't currently import from `scripts.gtkb_bridge_writer`. Mitigation: implementation establishes the import path with a small guard (sys.path manipulation only if needed) and a smoke test on import.
- **Risk: T-PARITY churn.** The two helper copies must stay byte-equal. Mitigation: T-PARITY test catches drift on every CI run; documented in CONTRIBUTING-style note in both files.
- **Rollback:** revert the implementation commit; helpers return to their pre-migration state. The writer module is untouched.

## Acceptance Criteria

- TP-MIG-1 through TP-MIG-7 pass.
- TS1 passes.
- Existing `test_bridge_propose_helper.py` tests pass after the refactor.
- Ruff clean on modified and new files.
- `IPR-BRIDGE-PROPOSE-HELPER-MIGRATION-001` and `CVR-BRIDGE-PROPOSE-HELPER-MIGRATION-001` inserted as KB document rows with explicit owner-approval evidence in change-reason.
- Both helper copies (`groundtruth-kb/templates/...` and `.claude/...`) byte-equal.
- Probe report in post-impl lists every Prime-side INDEX writer found and confirms each is migrated or out-of-scope.

## Open Items (probed during implementation)

- Exact list of Prime-side INDEX writers across the repo.
- Whether `gtkb_bridge_writer.py` exposes a public atomic-INDEX-write helper, or whether `propose_bridge()` continues to do its own write while delegating only validation.
- Result of `python -m groundtruth_kb.cli deliberations search --query "bridge propose helper INDEX parity caller migration" --limit 5`.

## Deliberation Capture

This proposal + IPR/CVR pair capture the substantive design. No pre-implementation owner decisions are required.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
