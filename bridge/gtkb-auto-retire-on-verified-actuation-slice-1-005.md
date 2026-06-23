REVISED

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Auto-Retire on VERIFIED - WI-4741 (REVISED-2: cross-harness verify-helper parity)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4741
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "scripts/project_verified_completion_scanner.py", "platform_tests/scripts/test_auto_retire_on_verified.py"]

Document: gtkb-auto-retire-on-verified-actuation-slice-1

## NO-GO Resolution (-004 P1: Codex verify-helper parity)

The `-004` NO-GO correctly found that `-003` wired actuation into
`.claude/skills/verify/helpers/write_verdict.py` but omitted its Codex twin
`.codex/skills/verify/helpers/write_verdict.py`, which would make auto-retirement
harness-dependent (Codex VERIFIED finalizations would skip it) - the exact defect
class tracked as `WI-4750`. This revision resolves it:

1. **Both verify-helper twins are now in `target_paths`** and receive the *identical*
   actuation call-site.
2. **Shared implementation, not duplicated logic.** The actuation routine lives in
   `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (one implementation). Each
   twin's `finalize_verified_commit` adds the same small lazy-import best-effort call to
   it - so there is no logic to drift, only an identical invocation.
3. **Parity is regression-locked.** The two twins are currently byte-identical
   (both 18,777 bytes; `diff` clean). The new test asserts they remain byte-identical,
   so any future divergence of the auto-retire seam (or anything else) fails CI.

This proposal subsumes `WI-4750`; on VERIFIED it should be cross-linked/closed as
addressed by WI-4741.

## Reconciled Completion Criterion (carried forward from -003)

New additive predicate in `ProjectLifecycleService`,
`member_completion_ready(project_id) -> bool`: the project has >= 1 active member
work item; every active member work item is in a terminal resolution status
`{verified, resolved, retired, wont_fix, not_a_defect}`; and the project has no
active `plan_incomplete` completion guard. Project-scoped by construction (no
cross-project false-positive class). Additive: the existing implements-link
authorization-completion machinery is left intact for its own consumers.

## Design

1. **Predicate + retire routine** (`lifecycle.py`):
   `auto_retire_completed_projects(project_root, changed_by=...) -> list[str]` - iterate
   active projects; retire each `member_completion_ready` project via `retire_project(...)`
   with a clear `change_reason`. Best-effort: per-project try/except, log + skip, never raise.
2. **Actuation seam - BOTH twins, identical call-site**: in
   `.claude/skills/verify/helpers/write_verdict.py` AND
   `.codex/skills/verify/helpers/write_verdict.py`, after a successful VERIFIED
   finalization (post-commit), lazily import the lifecycle service (try/except `ImportError`)
   and call `auto_retire_completed_projects(...)`. The call re-evaluates active projects'
   current member-WI state (not the just-VERIFIED thread's WIs), so it is correct
   regardless of when WIs reach terminal resolution. Wrapped in a broad try/except that
   logs and swallows: a VERIFIED verdict/commit is never rolled back by an actuation failure.
   The inserted block is byte-identical in both twins.
3. **Detector reconciliation** (`scripts/project_verified_completion_scanner.py`): add a
   membership-based completion view using `member_completion_ready` over ALL active
   projects (not only authorized ones); the existing authorization/implements-link view is
   retained (additive).

## Scope Clarifications (governance checkpoints)

- **Cited WIs are references, not the declared work item.** This proposal declares
  `Work Item: WI-4741`. `WI-4750` (the Codex verify-helper parity defect this revision
  resolves) and `WI-3481` (premature-retirement risk precedent) are cited as related
  context only, not as additional declared work items.
- **No canonical KB mutation during implementation; `groundtruth.db` is intentionally
  NOT a target_path.** The change is source-only. The auto-retirement `retire_project()`
  call is a RUNTIME effect of the deployed code (it mutates MemBase only when a real
  VERIFIED finalization later fires), not an implementation step. The new tests exercise
  the seam against temporary databases, never the canonical `E:\GT-KB\groundtruth.db`.

## In-Root Placement Evidence (ADR-ISOLATION-APPLICATION-PLACEMENT-001 / CLAUSE-IN-ROOT)

All target paths are in-root under `E:\GT-KB`
(`groundtruth-kb/src/...`, `.claude/skills/...`, `.codex/skills/...`, `scripts/...`,
`platform_tests/...`). No out-of-root path is created or required.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governing spec (automatic VERIFIED-driven retirement) on the owner-reconciled criterion.
- `GOV-STANDING-BACKLOG-001` - project authority reflects real lifecycle state.
- `GOV-08` - KB single source of truth.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - cross-harness behavior parity (both verify-helper twins must behave identically).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/bridge-essential.md`

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
requires automatic VERIFIED-driven retirement; owner AUQ (`DELIB-20265569` build-now;
2026-06-22 reconcile-to-member-WI; `DELIB-20265228` decoupling authorization-completion
from retirement) clarifies the criterion. Cross-harness parity is an existing
expectation (`GOV-HARNESS-ROLE-PORTABILITY-001`), not a new requirement. No new requirement.

## Prior Deliberations

- `DELIB-20265569` - owner build-now decision (WI-4741).
- 2026-06-22 AUQ "Reconcile to member-WI criterion" (recorded via owner-decision tracker).
- `DELIB-20265228` - decoupling authorization completion from automatic retirement.
- `WI-4750` - "Auto-retire VERIFIED actuation omits Codex verify helper parity" (this revision resolves it).
- `-001`..`-004` of this thread: original implements-link proposal, GO, the member-WI REVISED, and the parity NO-GO this revision addresses.
- `DELIB-2276` (GO) / `DELIB-20264096` (NO-GO) - W1 Retirement-Machinery history.
- `WI-3481` - premature multi-slice retirement risk (the member-WI predicate uses the active membership set; unfiled future members cannot trigger premature retirement).

## Spec-Derived Verification

New `platform_tests/scripts/test_auto_retire_on_verified.py`:

| Behavior | Test |
|---|---|
| Auto-retire fires (member-WI) | all active member WIs terminal -> VERIFIED finalization -> project `status='retired'` |
| Open WI / guard / no-members block | non-terminal member, active `plan_incomplete` guard, or zero members -> NOT retired |
| Membership-scoped (no auth needed) | project with NO active authorization but all member WIs terminal -> detected/retired |
| Best-effort safety | actuation raising does NOT roll back the VERIFIED verdict/commit |
| **Cross-harness parity (NO-GO -004 fix)** | assert `.claude/skills/verify/helpers/write_verdict.py` and `.codex/skills/verify/helpers/write_verdict.py` are byte-identical AND both contain the auto-retire actuation call |
| Detector parity | scanner's membership view lists the same projects the predicate retires |

Commands: `python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py -q`;
`python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q` (regression of the
untouched authorization-completion machinery); `ruff check` + `ruff format --check` on
all changed files (both twins included).

## Risk / Rollback

- Risk: looser criterion (WI terminal-state vs bridge-VERIFIED coverage) retires more
  projects. Accepted per owner reconciliation; mitigated by guards + append-only
  reversibility (`gt projects update <ID> --status active`).
- Risk: twin drift. Mitigated by the byte-identity parity test (fails on any divergence).
- Risk: actuation error corrupts the verdict transaction. Mitigated by best-effort
  swallow + lazy-import degradation in both twins.

## Owner Decisions / Input

- AUQ 2026-06-22 "Build the auto-retire automation now" (`DELIB-20265569`).
- AUQ 2026-06-22 "Re-scope Slice 2" -> **Reconcile to member-WI criterion**.
- The `-004` NO-GO required no owner decision ("Owner Action Required: None"); this is a
  Prime Builder revision addressing the cross-harness parity finding.

## Recommended Commit Type

`feat:` - new event-driven auto-retirement capability (member-WI criterion) wired into
both verify-helper twins with regression-locked parity.
