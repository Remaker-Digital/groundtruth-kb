NEW

# Implementation Proposal - Project VERIFIED-Completion Owner-Confirmed AUQ Trigger (WI-3316)

bridge_kind: prime_proposal
Document: gtkb-project-verified-completion-auq-trigger
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3316

target_paths: ["scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", "tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py", ".claude/settings.json", ".codex/hooks.json"]

This NEW proposal implements `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v1 specified 2026-05-14, Owner-confirmed-via-AUQ variant). When all constituent work items of an active project authorization reach VERIFIED status via their bridge threads, Prime Builder surfaces a completion AUQ to the owner. On approval, the project authorization transitions to `completed` and the project is retired. Auto-transition without owner confirmation is prohibited.

## Claim

Three components: (1) a read-only scanner script that computes per-project completion readiness from MemBase + bridge/INDEX.md; (2) a UserPromptSubmit-side surface that surfaces newly-completion-ready projects with one-at-a-time AUQ on owner prompts; (3) a `transition_project_authorization_to_completed()` DB method that, when called with proper AUQ-derived evidence in change_reason, transitions the authorization to status=`completed` and calls project retirement.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-project-verified-completion-auq-trigger-001.md`. Targets in `scripts/`, `.claude/hooks/`, `tests/scripts/`, `platform_tests/scripts/`, `groundtruth-kb/`, `.claude/settings.json`, `.codex/hooks.json`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - source spec; v1 specified 2026-05-14; Owner-confirmed-via-AUQ variant.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance for project authorizations.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema; `completed` status transition lives here.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved (AUQ + scanner do not bypass implementation_authorization gate).
- `SPEC-AUQ-POLICY-ENGINE-001` - AUQ-only enforcement applies; scanner uses AskUserQuestion.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - scanner uses deterministic VERIFIED detection, not LLM.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; scanner reads INDEX.md as canonical state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3316 is a tracked work_item.
- `GOV-ARTIFACT-APPROVAL-001` - project retirement is mutation; AUQ packet evidence required (this is the AUQ that creates it).
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14 establishing this WI; AUQ selecting Owner-confirmed variant over Auto-transition.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved 5-spec batch including GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001.
- 2026-05-14 UTC, S350+: owner AUQ "VERIFIED→COMPLETED transition: automatic or owner-confirmed?" answered "Owner-confirmed via AUQ" - explicit selection of this WI's variant.
- 2026-05-14 UTC, S350+: owner directive "Please proceed with parallel implementation proposals for as many backlog items as possible" - authorization to file this NEW.

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v1 fully specifies: detection trigger (all-VERIFIED), AUQ as confirmation channel, transition target (`completed` + project retirement), auto-transition prohibited.

## Clause Scope Clarification (Not a Bulk Operation)

NOT a bulk operation. One operative work item (WI-3316), active member of project GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (scanner) + IP-2 (hook surface) + IP-3 (DB method) + IP-4 (tests) + IP-5 (hook registration) scoped to a single thread file. No multi-project bulk operation.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-project-verified-completion-auq-trigger-001.md`; new top-of-file entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Read-only scanner `scripts/project_verified_completion_scanner.py`

CLI: `python scripts/project_verified_completion_scanner.py [--json]`

Logic:
1. Query `current_project_authorizations` for all `status='active'` rows.
2. For each authorization, parse `included_work_item_ids` JSON.
3. For each WI, look up corresponding bridge threads. Implementation-detection heuristic v1: scan `bridge/INDEX.md` for `Document:` entries that cite the WI in any bridge file's `Work Item:` line. Mark the thread VERIFIED iff its newest entry status is `VERIFIED`.
4. Authorization is completion-ready iff every included WI has at least one VERIFIED bridge thread.
5. Emit list of completion-ready authorizations (id, project_id, name).

Read-only: no DB writes, no bridge file writes. Idempotent.

### IP-2: UserPromptSubmit hook `.claude/hooks/project-completion-surface.py`

On UserPromptSubmit (Claude side):
1. Run the scanner (IP-1).
2. For each completion-ready authorization, if not yet surfaced this session (idempotency token in `.gtkb-state/project-completion-surface/`), emit `additionalContext` block: "Project <id> is completion-ready (all <N> WIs VERIFIED). Use AskUserQuestion to confirm completion."
3. One-at-a-time: only the oldest completion-ready authorization is surfaced per turn.
4. Codex parity: mirror at `.codex/gtkb-hooks/project-completion-surface.py`.

This is a SURFACE only (Axis-2 non-dispatchable per `.claude/rules/bridge-essential.md` two-axis model). Prime Builder uses AUQ when the surface fires.

### IP-3: DB method `transition_project_authorization_to_completed()`

In `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`:

```python
def transition_project_authorization_to_completed(
    self, authorization_id: str, owner_decision_deliberation_id: str,
    changed_by: str, change_reason: str
) -> dict[str, Any]:
    """Transition an active authorization to status=completed. Requires AUQ-derived owner decision."""
    # 1. Validate current status is 'active'
    # 2. Validate all included WIs have at least one VERIFIED bridge thread (re-run scanner)
    # 3. Insert new version with status='completed', preserving included_spec_ids and included_work_item_ids
    # 4. Optionally call retire_project(project_id) if the authorization was the sole active one
```

### IP-4: Hook registration

In `.claude/settings.json`, add UserPromptSubmit hook entry pointing at `.claude/hooks/project-completion-surface.py`. In `.codex/hooks.json`, mirror.

### IP-5: Spec status promotion

Promote `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` from `specified` to `implemented` after IP-1..IP-4 land and tests pass.

## Specification-Derived Verification Plan

Tests in `tests/scripts/test_project_verified_completion_scanner.py` + `tests/hooks/test_project_completion_surface.py` + `groundtruth-kb/tests/test_db.py`:

| Spec requirement | Test |
|---|---|
| "all constituent WIs VERIFIED → completion-ready" | `test_scanner_marks_all_verified_authorization_completion_ready` |
| "some WI non-VERIFIED → not ready" | `test_scanner_skips_authorization_with_one_non_verified_wi` |
| "Auto-transition without owner confirmation prohibited" | `test_transition_requires_auq_derived_change_reason_pattern` (DB method rejects when change_reason lacks AUQ-evidence marker) |
| Hook surfaces one-at-a-time | `test_hook_surfaces_one_authorization_per_prompt` |
| Hook idempotency per session | `test_hook_does_not_resurface_same_authorization_same_session` |
| "Projects retired via explicit owner direction follow standard retirement (bypass this gate)" | `test_explicit_retire_command_does_not_require_all_verified` |
| Transition correctness | `test_transition_inserts_new_version_with_completed_status` (DB method check) |
| Read-only scanner | `test_scanner_makes_no_db_writes` (DB integrity assertion) |

Test execution: `python -m pytest tests/scripts/test_project_verified_completion_scanner.py tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_db.py -v`.

## Acceptance Criteria

- IP-1 scanner landed; 4 scanner tests PASS.
- IP-2 hook surfaces correctly; 2 hook tests PASS.
- IP-3 DB method landed; 2 DB tests PASS.
- IP-4 hook registered in both Claude + Codex settings.
- IP-5 spec promoted to `implemented`.
- No regression in existing test suites.
- Both preflights PASS for this bridge ID.

## Risks / Rollback

- Risk: bridge/INDEX.md parsing for VERIFIED detection is regex-fragile. Mitigation: use the existing bridge-index parser (`groundtruth_kb.bridge.*` modules) rather than ad-hoc regex.
- Risk: hook adds latency to every UserPromptSubmit. Mitigation: cache scanner result for ~30s; only re-run when bridge/INDEX.md mtime changes.
- Risk: project retirement may interfere with in-flight follow-on work. Mitigation: AUQ surfaces only completion-ready state; owner has final decision before any DB write.
- Rollback: disable hook registration in settings.json; remove scanner script; revert DB method.

## Recommended Commit Type

`feat` - adds new mechanical governance surface for project completion. ~150 LOC net (scanner + hook + DB method + tests).
