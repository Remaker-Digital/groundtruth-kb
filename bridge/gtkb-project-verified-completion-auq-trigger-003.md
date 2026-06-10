REVISED

# Implementation Proposal - Project VERIFIED-Completion Owner-Confirmed AUQ Trigger - REVISED-1 (WI-3316)

bridge_kind: prime_proposal
Document: gtkb-project-verified-completion-auq-trigger
Version: 003
Responds to: bridge/gtkb-project-verified-completion-auq-trigger-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3316

target_paths: ["scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/hooks/test_project_completion_surface.py", "groundtruth-kb/tests/test_project_artifacts.py", ".claude/settings.json", ".codex/hooks.json"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-project-verified-completion-auq-trigger-002.md`:

- **F1 (P1)** - `target_paths` omitted required parity/test paths -> **closed**: the Codex parity hook `.codex/gtkb-hooks/project-completion-surface.py` and the hook test file (relocated to the existing `platform_tests/hooks/` tree) are now in `target_paths`; the scanner/service test files are explicit. (The session idempotency state under `.gtkb-state/project-completion-surface/` is gitignored runtime state outside the implementation-start-gate's protected-path set; it is intentionally NOT a `target_path` because `target_paths` authorize source mutations, not regenerable runtime state.)
- **F2 (P1)** - completion/retirement semantics and the layer boundary were underspecified -> **closed**: the transition orchestration is moved OUT of a `KnowledgeDB` method INTO a `ProjectLifecycleService` method (no layer inversion), and the completion/retirement state machine is made explicit below.

## Claim

Three components: (1) a read-only scanner that computes per-project-authorization completion readiness from MemBase + `bridge/INDEX.md`; (2) an Axis-2 surface hook (Claude + Codex parity) that surfaces a newly completion-ready authorization for owner AUQ confirmation, one at a time; (3) a `ProjectLifecycleService.complete_project_authorization()` method that, given an owner-decision deliberation id, transitions the authorization to `completed` and conditionally retires the project. Auto-transition without owner confirmation is prohibited: the service method requires an `owner_decision_deliberation_id` that resolves to a real archived deliberation.

## In-Root Placement Evidence

All 9 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - source spec; v1 specified 2026-05-14; Owner-confirmed-via-AUQ variant.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance for project authorizations.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema; the `completed` status lives here.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved; the scanner and surface do not bypass the implementation-authorization gate.
- `SPEC-AUQ-POLICY-ENGINE-001` - AUQ-only enforcement; the surface drives an AskUserQuestion.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - the scanner uses deterministic VERIFIED detection, not an LLM.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Claude/Codex hook parity contract (governs IP-2b).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; the scanner reads `bridge/INDEX.md` as canonical state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3316 is a tracked work item.
- `GOV-ARTIFACT-APPROVAL-001` - project completion/retirement is a governed mutation; the owner-decision deliberation is the approval evidence.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14; AUQ selecting the Owner-confirmed-via-AUQ variant over Auto-transition.
- `bridge/gtkb-project-verified-completion-auq-trigger-002.md` - NO-GO under remediation by this REVISED-1.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`; owner AUQ "VERIFIED->COMPLETED transition: automatic or owner-confirmed?" answered "Owner-confirmed via AUQ".
- 2026-05-15 UTC, S350+: owner directive "Proceed with WI-3316 and WI-3317."

No new owner decision required; this REVISED-1 corrects scope and design per the NO-GO.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v1 specifies the detection trigger (all constituent WIs VERIFIED), AUQ as the confirmation channel, the transition target (`completed` + project retirement), and the prohibition on auto-transition. This REVISED-1 makes the multi-authorization retirement rule explicit (see IP-3); it is a clarifying refinement within the existing requirement, not a new requirement.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3316), an active member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (scanner) + IP-2/IP-2b (surface hooks) + IP-3 (service method) + IP-4 (hook registration) + IP-5 (tests) single thread. The scanner is read-only and surfaces completion-ready authorizations one at a time; no multi-project bulk mutation occurs.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-project-verified-completion-auq-trigger-003.md`; `REVISED:` line prepended. Prior `NO-GO: -002` and `NEW: -001` lines preserved.

## Proposed Scope

### IP-1: Read-only scanner `scripts/project_verified_completion_scanner.py`

CLI `python scripts/project_verified_completion_scanner.py [--json]`. Logic: query `current_project_authorizations` for `status='active'` rows; for each, parse `included_work_item_ids`; for each WI, determine whether a bridge thread citing that WI has a latest status of `VERIFIED` (using the existing bridge-index parser in `groundtruth_kb.bridge`, not ad-hoc regex). An authorization is completion-ready iff every included WI has a VERIFIED bridge thread. Emit the completion-ready authorizations (id, project_id, name). Read-only, idempotent, no DB or bridge-file writes.

### IP-2 / IP-2b: Axis-2 surface hooks (Claude + Codex parity)

`.claude/hooks/project-completion-surface.py` (Claude `UserPromptSubmit`) and `.codex/gtkb-hooks/project-completion-surface.py` (Codex parity). On the event: run the scanner; for the oldest completion-ready authorization not yet surfaced this session, emit an `additionalContext` block instructing the agent to confirm completion via AskUserQuestion. One-at-a-time; per-session idempotency via a token under `.gtkb-state/project-completion-surface/` (gitignored runtime state). This is a SURFACE only (Axis-2 non-dispatchable per `.claude/rules/bridge-essential.md`); it never mutates state itself.

### IP-3: `ProjectLifecycleService.complete_project_authorization()` (lifecycle layer)

In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (NOT `db.py` - this is the layer-boundary correction for F2):

```python
def complete_project_authorization(
    self, authorization_id, owner_decision_deliberation_id, changed_by, change_reason
) -> dict[str, Any]:
```

State machine (explicit per F2):

1. Load the authorization; raise `ProjectLifecycleError` if it is not `status='active'`.
2. Require `owner_decision_deliberation_id` to resolve via `self.db.get_deliberation()`; absent/unknown -> `ProjectLifecycleError` ("auto-transition prohibited; owner-decision deliberation required"). This is the mechanical owner-confirmation gate.
3. Re-run the IP-1 readiness check for this authorization; raise `ProjectLifecycleError` if any included WI lacks a VERIFIED bridge thread.
4. Call the existing DB primitive `self.db.update_project_authorization(authorization_id, status="completed", ...)`. (A status-only change with the spec set unchanged passes the WI-3312 and WI-3313 gates cleanly.)
5. Query the project's other authorizations. **Project-retirement rule:** if NO other `status='active'` authorization exists for `project_id`, call the existing `self.retire_project(project_id, ...)`. If one or more other active authorizations remain, the project stays `active` and is NOT retired.
6. Return `{"authorization": <completed row>, "project_retired": <bool>}`.

The DB layer exposes only primitive writes (`update_project_authorization`); the `ProjectLifecycleService` owns the orchestration and the conditional `retire_project` call. No `KnowledgeDB` method "calls project retirement".

### IP-4: Hook registration

Register `project-completion-surface.py` as a `UserPromptSubmit` hook in `.claude/settings.json` and `.codex/hooks.json`.

### IP-5: Spec status

`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` remains `specified` at proposal-filing time. Promotion to `implemented` is proposed in the post-implementation report only after IP-1..IP-4 land and all tests pass.

## Specification-Derived Verification Plan

| Spec requirement | Test | File |
|---|---|---|
| all constituent WIs VERIFIED -> completion-ready | `test_scanner_marks_all_verified_authorization_completion_ready` | `platform_tests/scripts/test_project_verified_completion_scanner.py` |
| one WI non-VERIFIED -> not ready | `test_scanner_skips_authorization_with_one_non_verified_wi` | scanner test |
| scanner is read-only | `test_scanner_makes_no_db_writes` | scanner test |
| surface is one-at-a-time | `test_hook_surfaces_one_authorization_per_prompt` | `platform_tests/hooks/test_project_completion_surface.py` |
| surface idempotent per session | `test_hook_does_not_resurface_same_authorization_same_session` | hook test |
| auto-transition prohibited (no owner deliberation) | `test_complete_requires_owner_decision_deliberation` | `groundtruth-kb/tests/test_project_artifacts.py` |
| transition rejected when authorization not active | `test_complete_rejects_non_active_authorization` | service test |
| transition rejected when not all WIs VERIFIED | `test_complete_rejects_when_a_wi_not_verified` | service test |
| sole active authorization -> project retired | `test_complete_sole_active_authorization_retires_project` | service test |
| other active authorizations remain -> project NOT retired | `test_complete_with_other_active_authorization_keeps_project_active` | service test |
| authorization transitions to `completed` | `test_complete_transitions_authorization_to_completed` | service test |

Verification commands:

```text
python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py -v
python scripts/check_codex_hook_parity.py
```

## Acceptance Criteria

- IP-1 scanner lands; 3 scanner tests PASS.
- IP-2/IP-2b surface hooks land (Claude + Codex parity); 2 hook tests PASS; `check_codex_hook_parity.py` reports parity.
- IP-3 `ProjectLifecycleService.complete_project_authorization()` lands in `lifecycle.py` (not `db.py`); 6 service tests PASS, covering both the sole-active and the other-active-authorization retirement cases.
- IP-4 hook registered in both `.claude/settings.json` and `.codex/hooks.json`.
- IP-5 `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` remains `specified` at proposal time.
- No regression in existing suites.
- Both preflights PASS.

## Risks / Rollback

- Risk: `bridge/INDEX.md` VERIFIED detection could be fragile. Mitigation: use the existing `groundtruth_kb.bridge` index parser, not ad-hoc regex.
- Risk: the surface hook adds latency to every `UserPromptSubmit`. Mitigation: cache the scanner result; re-run only when `bridge/INDEX.md` mtime changes.
- Risk: retiring a project while another authorization is active. Mitigation: the IP-3 state machine retires the project ONLY when the completed authorization was the sole active one; covered by `test_complete_with_other_active_authorization_keeps_project_active`.
- Rollback: unregister the hook in both settings files; delete the scanner, hooks, and service method; the new test files stay as behavior documentation or are deleted with the feature.

## Recommended Commit Type

`feat` - new mechanical governance surface for owner-confirmed project completion + retirement, across a read-only scanner, Axis-2 parity hooks, and a project-lifecycle service method. No spec status promotion in this slice.
