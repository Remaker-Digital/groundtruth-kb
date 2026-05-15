REVISED

# Operating-Mode Transaction Component — Slice 1 (REVISED-3)

bridge_kind: implementation_proposal
Document: gtkb-operating-mode-transaction-001
Version: 008
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350 (continuation; concurrent-window parallel-session safe scope)
Addresses: NO-GO at `bridge/gtkb-operating-mode-transaction-001-007.md` — F1 proposed bridge-artifact validation rejects the live authoritative bridge index (omits `WITHDRAWN` from status vocabulary; requires file-existence of every status-line reference, which the live INDEX cannot satisfy without unrelated historical hygiene).

## Claim

REVISED-3 closes the single remaining Codex finding by aligning `validate_bridge_artifact()` with the canonical bridge parser's vocabulary and removing the file-existence requirement that turned unrelated historical hygiene into a hard mode-switch precondition.

- **F1 fix (live-INDEX compatibility):** `validate_bridge_artifact()` now mirrors the canonical parser's status vocabulary from `scripts/bridge_applicability_preflight.py:32`: `{NEW, REVISED, GO, NO-GO, VERIFIED, WITHDRAWN, ADVISORY}`. The validator no longer requires every status-line referenced bridge file to exist on disk — historical references can legitimately persist after VERIFIED/WITHDRAWN closure or after bridge file relocations, and that hygiene is a separate concern from mode-switch safety. Two new regression tests pin the live-compatibility behavior: a fixture containing `WITHDRAWN` rows and a fixture containing status lines whose referenced files are absent (matching the current `gtkb-isolation-018-slice-d-non-functional-content-001/002` historical pattern).

All other content from REVISED-2 (`-006`) carries forward unchanged: F1 dispatch-ordering correction (four call sites for `apply_pending`), F3 MemBase scope removal, F4 `.gtkb-state/.gitkeep` removal, the validation module's role-artifact and session-state artifact validators (which Codex did not flag), the seven-deliverable Slice 1 scope, and the spec-to-test mapping for all six SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria.

Both mandatory mechanical preflights are expected to pass against this `-008` operative file (verified post-filing).

## target_paths

Unchanged from REVISED-2 (`-006`):

- `groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (MODIFY)
- `scripts/session_self_initialization.py` (MODIFY)
- `scripts/workstream_focus.py` (MODIFY)
- `scripts/single_harness_bridge_dispatcher.py` (MODIFY)
- `scripts/cross_harness_bridge_trigger.py` (MODIFY — F1 fix from `-006`)
- `.codex/gtkb-hooks/session_start_dispatch.py` (MODIFY — F1 fix from `-006`)
- `.claude/hooks/session_start_dispatch.py` (MODIFY — F1 fix from `-006`)
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (NEW)
- `platform_tests/groundtruth_kb/test_mode_switch_pending.py` (NEW)
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py` (NEW — F2 fix; expanded with REVISED-3 live-compatibility regression tests)
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (NEW)
- `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` (NEW)
- `platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py` (NEW — F1 fix from `-006`)
- `platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` (NEW — F1 fix from `-006`)
- `.claude/rules/operating-role.md` (MODIFY)

All paths in-root under `E:\GT-KB\`. No `applications/**` paths touched, no Agent Red files referenced as live artifacts, no `groundtruth.db` MemBase mutation in scope, no `.gtkb-state/**` tracked-file placeholders.

Out-of-scope for Slice 1 (unchanged from `-006`):

- Future Slice 2: wrap existing imperative role-management call sites to invoke the transaction component.
- Future Slice 3: migrate `topology_mode` storage out of `work-subject.json` entirely.
- Future tracking slice (separate bridge thread): MemBase project + WI creation.
- Bridge-index file-existence hygiene (e.g., the `gtkb-isolation-018-slice-d-non-functional-content` historical references): explicitly NOT in this slice's scope; would be a separate bridge thread for INDEX hygiene if/when the owner directs.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this REVISED-3 follows the standard lifecycle. `bridge/INDEX.md` will be updated with `REVISED: bridge/gtkb-operating-mode-transaction-001-008.md` at the top of the document's version list.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - target paths inside `E:\GT-KB`; no Agent Red commingling.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - topology decision; defines role-set cardinality determines topology.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - single-harness dispatcher contract.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - wake-substrate constraint.
- GOV-HARNESS-ROLE-PORTABILITY-001 - roles attach to harness IDs, not vendor names.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - GT-KB installs prepare capable harnesses for either role regardless of topology.
- GOV-ACTING-PRIME-BUILDER-001 - legacy `acting-prime-builder` READ-accepted, SET-rejected.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - every implementation proposal cites governing specs.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification executes spec-derived tests against implementation; F2 fix expands the test surface.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - audit records are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lifecycle visibility; pending → applied transition is an explicit lifecycle trigger.
- GOV-STANDING-BACKLOG-001 - cross-cutting; F3 disposition still defers the standing-backlog entry to a separate project-authorization-scoped bridge thread.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec being implemented (approved 2026-05-13 via owner AUQ; packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`; `full_content_sha256` `f5311c8844a89b17e906cc022415aa39fd1b48eeaa9f7ea774bd068f736c99b5`). REVISED-3 still implements all six acceptance criteria; F1 fix this turn strengthens criterion #2 enforcement against the live bridge index rather than against an idealized strict-validation surface.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the validator design tightens deterministic governance plumbing.
- `.claude/rules/operating-role.md` - durable operating-role assignment; role-set schema honored.
- `.claude/rules/operating-model.md` - operating model §1 and §2.
- `.claude/rules/canonical-terminology.md` - load-bearing topology terms.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming + mandatory subsections; the canonical bridge vocabulary used by F2 fix lives in this rule's invariants.
- `.claude/rules/codex-review-gate.md` - review gate.
- `.claude/rules/project-root-boundary.md` - root boundary rule.
- `scripts/bridge_applicability_preflight.py` - the canonical bridge parser whose status vocabulary at line 32 is the authoritative reference for F2's parse-clean rule.
- `bridge/gtkb-operating-mode-transaction-001-007.md` - Codex NO-GO addressed by this REVISED-3.
- `bridge/gtkb-operating-mode-transaction-001-006.md` - REVISED-2 whose substantive scope is retained with the F2 live-INDEX compatibility correction.
- `bridge/gtkb-operating-mode-transaction-001-005.md` - earlier Codex NO-GO addressed by REVISED-2.

Advisory / cross-cutting:

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` - the approval packet authorizing the underlying spec.

## Prior Deliberations

- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION (S347, 2026-05-13) - project-scoped implementation authorization model.
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION (S346, 2026-05-13) - SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 was approved under that scope.
- DELIB-0877 (2026-04-22) - owner directive establishing harness topology awareness as first-class.
- DELIB-1511 [no_go, S310] - Loyal Opposition Review history for the single-harness bridge dispatcher work; informs the test surface.
- DELIB-1405 / DELIB-1406 (VERIFIED operating-model slice-0 and slice-1).
- DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (S330) - project root boundary.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` (2026-05-13) - records the role switch producing the current drifted state.
- `bridge/gtkb-operating-mode-transaction-001-001.md` through `-007.md` - complete version chain. `-007` (the Codex NO-GO addressed by this REVISED-3) flagged the live-INDEX compatibility gap; `-006` (REVISED-2) substantively addressed dispatch ordering, MemBase scope, and runtime-state policy.

No prior deliberation authorizes treating historical bridge-index file-existence defects as a hard precondition for role/mode changes; this REVISED-3 reflects that by aligning validator strictness with the canonical bridge parser rather than imposing a stricter rule unilaterally.

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - approval packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`. Standing authority for implementing the spec.
- 2026-05-14 owner AUQ - "How should I proceed with the topology-misreport flaw and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 implementation?" answered "Project + impl proposal now (Recommended)". Authorizes the original proposal chain.
- 2026-05-14 owner AUQ (post-NO-GO at -002) - "Slice 4 hygiene first (Recommended)" then "REVISED-1 with next-session in Slice 1 (Recommended)". Authorizes REVISED-1 scope and, by continuation, this REVISED-3.
- 2026-05-14 owner direction (this session): "Continue with priority items from the backlog. Please parallelize work whenever possible and work independently for as long as possible." Standing autonomous-work direction extending the `memory/work_list.md` pre-approval clause "Proceed through this list autonomously... Do not wait for owner approval between items. Continue unsupervised." Authorizes filing this REVISED-3 without an additional decision-class AUQ; the F2 fix is a mechanical mechanism correction within previously-approved scope.

No new owner decision is required before review. The F2 fix is a scope-bounded validator strictness reduction (from "strict vocabulary + file existence" to "canonical vocabulary parity"), not a scope expansion.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-3 implements `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` under its existing six-criterion acceptance contract. The F2 validator design now interprets criterion #2 ("validates the requested switch against the authoritative role, bridge, and session-state artifacts before writing durable state") through the lens of "compatible with the live authoritative artifact" rather than "stricter than the canonical bridge parser already enforces." No requirement change.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. The clause-preflight rule `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may flag the proposal because the content mentions `work item` and `backlog` while explaining the F3 disposition. The actual scope:

- Zero MemBase mutations in this slice.
- Zero bulk standing-backlog operations.
- One bridge thread filed (this `-008`).
- One protected-artifact mutation under formal-artifact-approval gate (`.claude/rules/operating-role.md`) — collected at implementation time, not at proposal review time.
- Owner-approval evidence: `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` plus the in-session 2026-05-14 AUQs and the standing autonomous-work direction.

## Changes from -006 (REVISED-2)

### F1 fix from -007: validate_bridge_artifact aligned with canonical parser

**Removed from -006:**

- The strict status vocabulary `{NEW, REVISED, GO, NO-GO, VERIFIED, ADVISORY}` (omitting `WITHDRAWN`).
- The requirement that "status-line referenced files exist on disk."

**Added in REVISED-3:**

- Canonical vocabulary `{NEW, REVISED, GO, NO-GO, VERIFIED, WITHDRAWN, ADVISORY}` mirroring the regex at `scripts/bridge_applicability_preflight.py:32`. The validator imports or references this set rather than redefining it, so future bridge-protocol vocabulary changes propagate.
- The new parse-clean rule:
  1. `bridge/INDEX.md` exists and is readable.
  2. The file contains at least one `Document: <name>` entry (signal that the bridge protocol is alive).
  3. Every status line that matches the bridge-status pattern uses a token from the canonical set.
  4. Status lines that do NOT match the canonical bridge-status pattern are ignored (treated as commentary/HTML comments/etc.) — same forgiveness pattern as the canonical preflight script.
- The validator no longer requires file existence of any bridge file referenced by INDEX. Historical references to relocated, renamed, or removed files are a separate hygiene concern out of scope for mode-switch safety.
- Two new regression tests pin the corrected behavior:
  1. `test_validate_bridge_artifact_accepts_withdrawn_status_rows` — fixture INDEX contains `WITHDRAWN: bridge/<name>.md` rows; validator returns `is_valid=True`.
  2. `test_validate_bridge_artifact_tolerates_missing_referenced_bridge_files` — fixture INDEX contains a status line whose referenced bridge file is absent on disk (matching the live `gtkb-isolation-018-slice-d-non-functional-content-001/002` pattern); validator still returns `is_valid=True`.
- The existing fail-closed tests (missing INDEX, unparseable INDEX, unknown status token) retain their expected behavior.

### Substantive scope retained from -006 (no changes this turn)

- F1 dispatch-ordering correction: pending-transaction drain at four call sites (`.codex/gtkb-hooks/session_start_dispatch.py`, `.claude/hooks/session_start_dispatch.py`, `scripts/cross_harness_bridge_trigger.py`, `scripts/session_self_initialization.py`), each fail-soft.
- F2 validation module's role-artifact + session-state artifact validators (Codex did not flag these in `-007`).
- F3 disposition: MemBase mutation deferred to a separate project-authorization-scoped bridge.
- F4 disposition: `.gtkb-state/.gitkeep` removed; directories runtime-created.
- Seven-deliverable Slice 1 scope.
- Spec-to-test mapping for all six SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria.

## Slice 1 Scope (REVISED-3)

Unchanged from REVISED-2's seven deliverables:

1. Pure derivation function at `groundtruth_kb.mode_switch.derive.topology_from_role_map(role_map: dict) -> str`.
2. **Validation module** at `groundtruth_kb.mode_switch.validation`. Three validator functions. `ValidationResult` dataclass: `is_valid: bool`, `axis: str` ("role" / "bridge" / "session-state"), `errors: tuple[str, ...]`. **F2 fix: `validate_bridge_artifact` uses the canonical bridge vocabulary `{NEW, REVISED, GO, NO-GO, VERIFIED, WITHDRAWN, ADVISORY}` and does not require referenced-file existence.**
3. Transaction component at `groundtruth_kb.mode_switch.transaction.apply_role_switch(...)`. Calls all three validators first; raises `TransactionValidationError` on any failure.
4. Pending-transaction queue at `groundtruth_kb.mode_switch.pending`.
5. Click CLI at `gt mode set-role` + `gt mode list-pending` + `gt mode apply-pending`.
6. Pre-role-resolution apply-pending call sites at four files (both SessionStart hooks + cross-harness trigger + session_self_initialization).
7. Topology derivation at startup in `scripts/session_self_initialization.py`; plus `workstream_focus.save_state` writes derived topology.

## Implementation Plan

Unchanged from REVISED-2 ordering. The only change is Step 2, which now reflects the canonical vocabulary alignment:

1. Create `groundtruth-kb/src/groundtruth_kb/mode_switch/` package with six submodules; unit-test `derive.topology_from_role_map` against fixtures.
2. Implement `validation.validate_role_artifact`, `validation.validate_bridge_artifact`, `validation.validate_session_state_artifact`. **`validate_bridge_artifact` uses the canonical status vocabulary `{NEW, REVISED, GO, NO-GO, VERIFIED, WITHDRAWN, ADVISORY}` (mirrored from `scripts/bridge_applicability_preflight.py:32`) and does NOT require referenced-file existence.** Tests cover: valid INDEX → pass; missing INDEX → fail; unreadable → fail; unparseable structurally → fail; INDEX with WITHDRAWN rows → pass; INDEX with missing referenced files → pass; INDEX with unknown-token status line → fail.
3. Implement `audit.write_transaction_record`. Runtime-creates `.gtkb-state/mode-switches/` via `mkdir(parents=True, exist_ok=True)`.
4. Implement `transaction.apply_role_switch`. Validators called FIRST.
5. Implement `pending.defer_role_switch`, `pending.list_pending`, `pending.apply_pending`. Runtime-create `pending/` and `applied/` dirs.
6. Add `gt mode set-role`, `gt mode list-pending`, `gt mode apply-pending` Click subcommands.
7. Refactor `scripts/single_harness_bridge_dispatcher.py:_is_single_harness_topology_applicable` to call `derive.topology_from_role_map`.
8. Add try-wrapped `apply_pending(project_root)` to `.codex/gtkb-hooks/session_start_dispatch.py` before role resolution.
9. Add try-wrapped `apply_pending(project_root)` to `.claude/hooks/session_start_dispatch.py` before role resolution.
10. Add try-wrapped `apply_pending(project_root)` to `scripts/cross_harness_bridge_trigger.py` before recipient resolution.
11. Add `apply_pending(project_root)` to `scripts/session_self_initialization.py` before topology derivation.
12. Modify `scripts/workstream_focus.save_state` to write derived topology.
13. Update `.claude/rules/operating-role.md` to document `gt mode set-role`. Protected narrative artifact — formal-artifact-approval packet collected at implementation time per `GOV-ARTIFACT-APPROVAL-001`.
14. File implementation report; Codex VERIFIES against the full six-criterion spec-to-test mapping below.

(Steps from REVISED-1's "create project / link WI" remain REMOVED per the F3 disposition.)

## Specification-Derived Test Plan

Mapping from `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` six acceptance criteria to executable tests (all paths under `platform_tests/**`). Updates from REVISED-2 are in criterion #2's row to reflect the new live-INDEX regression tests:

| Acceptance criterion | Test file | Test function | Command |
|---|---|---|---|
| "There is a deterministic component or service API for bridge-configuration and operating-mode switch requests." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_apply_role_switch_returns_transaction_result` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_apply_role_switch_returns_transaction_result -v` |
| "The component validates the requested switch against the authoritative role, bridge, and session-state artifacts before writing durable state." | `platform_tests/groundtruth_kb/test_mode_switch_validation.py` + `test_mode_switch_transaction.py` | `test_apply_role_switch_refuses_when_bridge_index_missing`, `test_apply_role_switch_refuses_when_bridge_index_unparseable`, `test_apply_role_switch_refuses_when_bridge_index_has_unknown_status_token`, **`test_validate_bridge_artifact_accepts_withdrawn_status_rows` (NEW REVISED-3)**, **`test_validate_bridge_artifact_tolerates_missing_referenced_bridge_files` (NEW REVISED-3)**, `test_apply_role_switch_refuses_when_role_artifact_unparseable`, `test_apply_role_switch_refuses_when_session_state_artifact_unparseable`, `test_apply_role_switch_rejects_acting_prime_builder`, `test_apply_role_switch_rejects_unknown_role`, `test_apply_role_switch_rejects_unknown_harness` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py -v` |
| "The component records enough transaction evidence to audit who requested the switch, what changed, when it was requested, and when it becomes effective." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_audit_record_contains_required_fields` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_audit_record_contains_required_fields -v` |
| "Agent instructions direct agents to use the transaction component or service, not ad hoc direct edits, when switching bridge configurations or operating modes." | `platform_tests/scripts/test_operating_role_rule.py` | `test_operating_role_md_documents_gt_mode_set_role` | `python -m pytest platform_tests/scripts/test_operating_role_rule.py::test_operating_role_md_documents_gt_mode_set_role -v` |
| "Session initialization reads the authoritative transaction result or current configuration artifact and applies the effective bridge/operating-mode state." | `platform_tests/scripts/test_session_self_initialization_topology_derive.py` + `test_session_self_initialization_applies_pending_mode_switches.py` + `test_session_start_dispatch_drains_pending_before_role_resolution.py` + `test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` | `test_startup_derives_topology_from_role_map`, `test_startup_overrides_stale_stored_topology_with_corrective_note`, `test_startup_applies_pending_transactions_before_topology_read`, `test_codex_session_start_dispatch_drains_pending_before_role_resolution`, `test_claude_session_start_dispatch_drains_pending_before_role_resolution`, `test_cross_harness_trigger_drains_pending_before_recipient_resolution` | `python -m pytest platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py -v` |
| "The implementation explicitly supports next-session effectiveness; immediate mid-session state replacement is optional unless separately specified." | `platform_tests/groundtruth_kb/test_mode_switch_pending.py` + `test_session_self_initialization_applies_pending_mode_switches.py` + `test_session_start_dispatch_drains_pending_before_role_resolution.py` | `test_defer_role_switch_writes_pending_file`, `test_apply_pending_drains_queue_in_chronological_order`, `test_apply_pending_moves_applied_to_applied_subdir`, `test_apply_pending_leaves_failed_in_pending_with_logged_error`, `test_cli_defer_to_next_session_writes_pending_not_current`, `test_next_session_initialization_applies_pending_and_state_matches_deferred_request` | (same as criterion #5 command + the pending-specific tests) |

Additional regression coverage (unchanged from -006):

| Risk | Test |
|---|---|
| Refactored `_is_single_harness_topology_applicable` changes dispatcher behavior | `python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -v` |
| Topology derivation breaks `single_harness_bridge_automation` | `python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py -v` |
| `workstream_focus.save_state` regression | `python -m pytest platform_tests/hooks/test_workstream_focus.py -v` |
| `session_self_initialization` startup-payload golden tests | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -v` |

Final full-bank regression at implementation-report time:

```
python -m pytest platform_tests -q --tb=short
```

## Risk and Rollback

Carried forward from REVISED-2 with one risk updated:

- R1 (P1, carried): Refactoring `_is_single_harness_topology_applicable` to call the new derivation function changes single-harness applicability under malformed role-map. Mitigation: byte-identical fixture parity test.
- R2 (P1, carried): The F1 fix adds I/O at hook startup. Mitigation: fail-soft per-call-site; failed files remain in `pending/` with logged error.
- R3 (P2, carried): Startup payload corrective note. Mitigation: notes as bullets under existing sections.
- R4 (P2, carried): `workstream_focus.save_state` writing derived topology. Mitigation: documented in module docstring.
- **R5 (P2, REVISED-3 update):** The F2 fix uses the canonical bridge vocabulary and does not require file existence of referenced bridge files. This is more permissive than `-006`'s validator but matches what the live bridge tooling already accepts. Mitigation: the regression tests pin the live-compatibility behavior; if a future bridge-protocol vocabulary change adds a status token, the validator's `STATUS_TOKENS` constant should be updated to mirror the canonical regex (or imported from the canonical parser module).
- R6 (P3, carried): Audit-record directory growth.

**Rollback procedure:** unchanged from REVISED-2. All Slice 1 changes are reversible by reverting the corresponding modules + the shared-script refactor + the rule-file documentation update. Audit records under `.gtkb-state/mode-switches/` are runtime-created and append-only; rollback does not delete them.

## Applicability Preflight

Required-spec citations expected per `config/governance/spec-applicability.toml` (same as REVISED-2 plus the new explicit citation of `scripts/bridge_applicability_preflight.py` as the F2 vocabulary source):

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001` (clause-scope clarification per § Clause Scope Clarification)

Expected advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Preflight will be re-run after INDEX update; updated `packet_hash` captured in the review.

## Recommended Commit Type

`feat:` - net-new deterministic mode-switch CLI + pending-queue + multi-call-site SessionStart application + canonical-vocabulary bridge-artifact validation. The diff stat is dominated by new module files and new test files. `feat:` matches.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with plain heading, flat bullets, no `###` sub-headings inside, no parenthetical heading qualifier.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the prior AUQs plus this turn's standing direction.
- `target_paths` consistent with all planned writes; F3 + F4 + F1 fixes from `-006` retained; F2 vocabulary correction this turn.
- `## Requirement Sufficiency` exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- explicit `## Changes from -006 (REVISED-2)` section with the F2 fix.
- All paths under `E:\GT-KB\`.
- F2 fix: `validate_bridge_artifact` aligned with canonical bridge parser vocabulary; file-existence requirement dropped; two new regression tests pin live-compatibility behavior (closes Codex `-007` F1).
- All F1 (dispatch ordering), F3 (MemBase scope), F4 (.gitkeep) fixes from REVISED-2 retained unchanged.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
