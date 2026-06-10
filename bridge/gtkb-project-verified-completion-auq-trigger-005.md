REVISED

# Implementation Proposal - Project VERIFIED-Completion Owner-Confirmed AUQ Trigger - REVISED-2 (WI-3316)

bridge_kind: prime_proposal
Document: gtkb-project-verified-completion-auq-trigger
Version: 005
Responds to: bridge/gtkb-project-verified-completion-auq-trigger-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3316

target_paths: ["scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/hooks/test_project_completion_surface.py", "groundtruth-kb/tests/test_project_artifacts.py", ".claude/settings.json", ".codex/hooks.json"]

This REVISED-2 addresses the NO-GO at `bridge/gtkb-project-verified-completion-auq-trigger-004.md`:

- **F1 (P1)** - the owner-confirmation gate in IP-3 required only that the `owner_decision_deliberation_id` resolve to an existing deliberation; existence is not owner-confirmation -> **closed**: IP-3 now validates owner-decision *semantics* (`source_type='owner_conversation'`, `outcome='owner_decision'`, and the row records the project-completion context), with negative tests for non-owner deliberation types/outcomes and wrong-project owner-decisions.
- **F2 (P2)** - `check_codex_hook_parity.py` was named as an acceptance criterion but contains no check for the project-completion hook family, making it a "false floor" -> **closed**: `check_codex_hook_parity.py` is removed from the verification commands and acceptance criteria; Codex/Claude hook parity is instead proven by explicit dual-hook tests that exercise BOTH hook files.

IP-1, IP-2/IP-2b, IP-4, and IP-5 carry forward from REVISED-1 unchanged.

## Claim

Unchanged from REVISED-1 except the F1/F2 deltas: a read-only scanner computes per-authorization completion readiness; an Axis-2 surface hook (Claude + Codex parity) surfaces a completion-ready authorization for owner AUQ; and `ProjectLifecycleService.complete_project_authorization()` transitions the authorization to `completed` and conditionally retires the project. The owner-confirmation gate now requires a genuine owner-decision deliberation, not merely an existing deliberation id.

## In-Root Placement Evidence

All 9 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. Session idempotency state under `.gtkb-state/project-completion-surface/` is gitignored runtime state outside the implementation-start-gate's protected-path set; it is intentionally not a `target_path`.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - source spec; v1 specified 2026-05-14; Owner-confirmed-via-AUQ variant.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema; the `completed` status lives here.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved.
- `SPEC-AUQ-POLICY-ENGINE-001` - AUQ-only enforcement; the surface drives an AskUserQuestion.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - deterministic VERIFIED detection, no LLM.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Claude/Codex hook parity contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; the scanner reads `bridge/INDEX.md`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3316 is a tracked work item.
- `GOV-ARTIFACT-APPROVAL-001` - project completion/retirement is a governed mutation; the owner-decision deliberation is the approval evidence.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive; AUQ selecting the Owner-confirmed-via-AUQ variant.
- `bridge/gtkb-project-verified-completion-auq-trigger-002.md` - first NO-GO (omitted paths, layer inversion).
- `bridge/gtkb-project-verified-completion-auq-trigger-004.md` - second NO-GO (owner-confirmation semantics, parity-check false floor); closed by this REVISED-2.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch; owner AUQ "VERIFIED->COMPLETED transition: automatic or owner-confirmed?" answered "Owner-confirmed via AUQ".
- 2026-05-15 UTC, S350+: owner directive "Proceed with WI-3316 and WI-3317."

No new owner decision required; this REVISED-2 is a mechanical correction per the NO-GO.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v1 requires owner confirmation and prohibits auto-transition; REVISED-2 makes the mechanical owner-confirmation check faithful to that requirement.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3316), an active member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 + IP-2/IP-2b + IP-3 + IP-4 + IP-5 single thread; the scanner is read-only.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-project-verified-completion-auq-trigger-005.md`; `REVISED:` line prepended. Prior lines (`-004` NO-GO, `-003` REVISED-1, `-002` NO-GO, `-001` NEW) preserved.

## Proposed Scope

IP-1 (read-only scanner), IP-2/IP-2b (Claude + Codex parity surface hooks), IP-4 (hook registration in `.claude/settings.json` + `.codex/hooks.json`), and IP-5 (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` stays `specified` at proposal time) are **unchanged from REVISED-1** (`bridge/gtkb-project-verified-completion-auq-trigger-003.md`).

### IP-3 (REVISED in REVISED-2): `ProjectLifecycleService.complete_project_authorization()` with a true owner-confirmation gate

In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, the method state machine:

1. Load the authorization; raise `ProjectLifecycleError` if not `status='active'`.
2. **Owner-confirmation gate (F1 strengthened):** resolve `owner_decision_deliberation_id` via `self.db.get_deliberation()`. Raise `ProjectLifecycleError` unless ALL hold:
   - the deliberation row exists;
   - `source_type == 'owner_conversation'`;
   - `outcome == 'owner_decision'`;
   - the row records the project-completion context for THIS transition - i.e. the deliberation's `content`, `source_ref`, or `change_reason` text mentions the `project_id` or the `authorization_id` being completed.
   Existence alone is insufficient; an LO review, an informational deliberation, a no-go deliberation, or an owner-decision recorded for a different project is rejected.
3. Re-run the IP-1 readiness check; raise `ProjectLifecycleError` if any included WI lacks a VERIFIED bridge thread.
4. `self.db.update_project_authorization(authorization_id, status="completed", ...)` (DB primitive).
5. Project-retirement rule: if NO other `status='active'` authorization exists for `project_id`, call `self.retire_project(project_id, ...)`; otherwise leave the project `active`.
6. Return `{"authorization": <completed row>, "project_retired": <bool>}`.

The DB layer exposes only primitive writes; `ProjectLifecycleService` owns the orchestration.

## Specification-Derived Verification Plan

| Spec requirement | Test | File |
|---|---|---|
| all constituent WIs VERIFIED -> completion-ready | `test_scanner_marks_all_verified_authorization_completion_ready` | `platform_tests/scripts/test_project_verified_completion_scanner.py` |
| one WI non-VERIFIED -> not ready | `test_scanner_skips_authorization_with_one_non_verified_wi` | scanner test |
| scanner is read-only | `test_scanner_makes_no_db_writes` | scanner test |
| surface one-at-a-time | `test_hook_surfaces_one_authorization_per_prompt` | `platform_tests/hooks/test_project_completion_surface.py` |
| surface idempotent per session | `test_hook_does_not_resurface_same_authorization_same_session` | hook test |
| Claude + Codex hooks both exercised (F2 - parity by explicit dual-hook tests) | `test_claude_hook_surfaces_completion_ready_authorization`, `test_codex_hook_surfaces_completion_ready_authorization` | hook test |
| owner-confirmation: missing deliberation rejected | `test_complete_rejects_missing_deliberation` | `groundtruth-kb/tests/test_project_artifacts.py` |
| owner-confirmation: LO-review deliberation rejected | `test_complete_rejects_lo_review_deliberation` | service test |
| owner-confirmation: informational deliberation rejected | `test_complete_rejects_informational_deliberation` | service test |
| owner-confirmation: no-go deliberation rejected | `test_complete_rejects_no_go_deliberation` | service test |
| owner-confirmation: owner-decision for the wrong project rejected | `test_complete_rejects_owner_decision_for_other_project` | service test |
| owner-confirmation: valid owner-decision deliberation accepted | `test_complete_accepts_valid_owner_decision_deliberation` | service test |
| transition rejected when authorization not active | `test_complete_rejects_non_active_authorization` | service test |
| transition rejected when not all WIs VERIFIED | `test_complete_rejects_when_a_wi_not_verified` | service test |
| sole active authorization -> project retired | `test_complete_sole_active_authorization_retires_project` | service test |
| other active authorizations remain -> project NOT retired | `test_complete_with_other_active_authorization_keeps_project_active` | service test |

Verification command (F2 - `check_codex_hook_parity.py` removed; parity proven by the dual-hook tests above):

```text
python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py -v
```

## Acceptance Criteria

- IP-1 scanner lands; 3 scanner tests PASS.
- IP-2/IP-2b surface hooks land (Claude + Codex parity); the hook test file exercises BOTH hook files and all hook tests PASS.
- IP-3 `ProjectLifecycleService.complete_project_authorization()` lands in `lifecycle.py`; the owner-confirmation gate validates owner-decision semantics; all service tests PASS, including the 4 owner-confirmation negative tests and both retirement-rule cases.
- IP-4 hook registered in both `.claude/settings.json` and `.codex/hooks.json`.
- IP-5 `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` remains `specified` at proposal time.
- No regression in existing suites.
- Both preflights PASS.

## Risks / Rollback

- Risk: the project-completion context check (deliberation text mentions project/authorization id) could false-negative if an owner-decision deliberation uses different phrasing. Mitigation: the surface hook instructs the agent to archive the owner-decision deliberation with the project/authorization id in content; tests document the expected phrasing.
- Risk: the surface hook adds latency to every `UserPromptSubmit`. Mitigation: cache the scanner result; re-run only on `bridge/INDEX.md` mtime change.
- Rollback: unregister the hook in both settings files; delete the scanner, hooks, and service method.

## Recommended Commit Type

`feat` - new owner-confirmed project-completion + retirement governance surface across a read-only scanner, Axis-2 parity hooks, and a project-lifecycle service method. No spec status promotion in this slice.
