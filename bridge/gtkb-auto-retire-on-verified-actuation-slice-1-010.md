REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef07d-dbf6-7083-bd4c-3c997d20f111
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-builder automation; approval_policy=never; workspace=E:\GT-KB; resolved_role=prime-builder
author_metadata_source: automation-prompt-live-state

# Auto-Retire on VERIFIED - WI-4741 (REVISED-5: preserve keep-open election)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4741
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "scripts/project_verified_completion_scanner.py", "platform_tests/scripts/test_auto_retire_on_verified.py"]

Document: gtkb-auto-retire-on-verified-actuation-slice-1

## Revision Claim

This revision resolves the `-009` NO-GO by carrying forward the v6 member-WI
terminal-resolution criterion while explicitly preserving the v5/v6 keep-open
caller election. The automatic retirement predicate, detector view, and
regression tests now include a durable-history keep-open guard, so a project
that was deliberately kept active by `retire_project=False` /
`--keep-project-open` is not later retired by a VERIFIED-finalization sweep.

## NO-GO Resolution (-009: keep-open election)

The `-009` NO-GO found that `-008` implemented the v6 member-WI criterion but
omitted one operative condition from `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
v6: automatic retirement fires only when no caller has taken the keep-open
election.

This revision corrects that omission:

1. `member_completion_ready(project_id)` includes a fourth condition:
   no active keep-open election is present for the project.
2. `scripts/project_verified_completion_scanner.py` reports the same
   keep-open exclusion used by the runtime predicate.
3. `platform_tests/scripts/test_auto_retire_on_verified.py` includes a negative
   regression that completes a project's sole authorization with
   `retire_project=False` / `--keep-project-open`, leaves all active member WIs
   terminal, triggers a later VERIFIED-finalization auto-retire pass, and
   asserts the project remains `active`.

## Keep-Open Detection

The current implementation surface does not store a separate boolean
`retire_project=False` field on `project_authorizations`; it records append-only
authorization status and project status history. The implementation therefore
uses a conservative durable-history predicate:

- a project is considered keep-open elected when the current project remains
  `active`, at least one current project authorization for that project has
  status `completed`, and no current authorization for that project remains
  `active`;
- this covers the explicit v5/v6 keep-open path because
  `complete_project_authorization(..., retire_project=False)` completes the sole
  authorization while leaving the project and its work-item memberships active;
- it also safely preserves owner/manual reactivation after an earlier
  completion, because an active project with completed authorization history is
  an explicit signal that the project should not be swept by a later unrelated
  VERIFIED event.

This is intentionally fail-safe by omission: an ambiguous keep-open signal
prevents automatic retirement and leaves a project visible for deterministic
review rather than risking spurious retirement.

## Design

1. **Predicate + retire routine** in `lifecycle.py`:
   `member_completion_ready(project_id)` returns true only when the project has
   at least one active member work item, every active member work item has a
   terminal `resolution_status`, no active `plan_incomplete` guard exists, and
   no keep-open election is detected from durable project/authorization history.
   `auto_retire_completed_projects(project_root, changed_by=...)` retires only
   projects satisfying that predicate, best-effort per project.
2. **Actuation seam - both verify-helper twins**:
   `.claude/skills/verify/helpers/write_verdict.py` and
   `.codex/skills/verify/helpers/write_verdict.py` both keep the same
   post-commit VERIFIED-finalization call to
   `auto_retire_completed_projects(...)`. The inserted helper blocks remain
   byte-identical and broad-exception-safe so actuation can never roll back the
   VERIFIED verdict/commit.
3. **Detector reconciliation**:
   `scripts/project_verified_completion_scanner.py` uses the same
   membership-based predicate over all active projects and surfaces keep-open
   exclusions distinctly, while retaining the existing implements-link view for
   authorization-completion diagnostics.

## Scope Clarifications

- This is still WI-4741. `WI-4750` and `WI-4755` remain related context only.
- No canonical KB mutation is part of implementation; tests use temporary
  databases. `groundtruth.db` is not a target path.
- The PAUTH still applies: it includes WI-4741, the project, source/script/skill
  and test mutation classes, and `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.
- The revision does not add a new owner decision requirement. It implements the
  owner-approved v6 text, including the keep-open condition already present in
  `DELIB-20265584` and `DELIB-20265228`.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6 - governing automatic
  retirement rule: active member WIs all terminal, no active `plan_incomplete`
  guard, and no keep-open election.
- `GOV-STANDING-BACKLOG-001` - project lifecycle state must remain accurate in
  MemBase and backlog surfaces.
- `GOV-08` - MemBase is the source of truth for project/work-item state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority and latest status
  chain discipline.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - cross-harness verify-helper parity.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - project-retirement decisions and
  lifecycle transitions remain durable artifact-backed records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact state, deliberations, and
  tests drive implementation rather than session-only memory.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB
  platform files.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal work-item/project lifecycle
  triggers are explicit and durable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  the governing specs and rules.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each
  governing condition to executable tests.
- `.claude/rules/bridge-essential.md` - VERIFIED finalization is bridge-critical
  infrastructure.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
v6 already states the keep-open condition, and `DELIB-20265228` records the
owner-approved `retire_project=False` / `--keep-project-open` election. This
revision implements that existing condition; no new or revised requirement is
introduced.

## Prior Deliberations

- `DELIB-20265584` - owner reconcile-to-member-WI decision and v6 approval; v6
  explicitly preserves the keep-open election.
- `DELIB-20265228` - owner approval of the keep-open caller election and its
  implementation surface.
- `DELIB-20265569` - owner decision to build WI-4741 auto-retire-on-VERIFIED
  automation now.
- `DELIB-20265581` - prior NO-GO on this thread for missing Codex verify-helper
  parity, resolved by the current target path set.
- `bridge/gtkb-auto-retire-on-verified-actuation-slice-1-009.md` - latest NO-GO,
  requiring keep-open detection in predicate, detector, and tests.
- `WI-4750` - helper parity context, addressed by including both helper twins.
- `WI-4755` - governing-spec drift context, resolved by v6.

## Owner Decisions / Input

- `DELIB-20265569` - owner AUQ approval to build WI-4741 auto-retire automation
  now through the standard bridge path.
- `DELIB-20265584` - owner AUQ decisions to reconcile to member-WI terminal
  resolution, formalize it as v6, and approve the v6 text.
- `DELIB-20265228` - owner AUQ decisions approving the keep-open caller election
  and v5 text; preserved by v6 and implemented by this revision.

## Spec-Derived Verification

`platform_tests/scripts/test_auto_retire_on_verified.py` will cover:

| Governing condition | Derived test |
|---|---|
| v6 all-active-member-WIs-terminal criterion | all active member WIs terminal -> VERIFIED finalization -> project retired |
| v6 open WI fail-safe | one active member WI non-terminal -> project remains active |
| v6 zero-member fail-safe | zero active member WIs -> project remains active |
| v6 `plan_incomplete` guard | active completion guard -> project remains active |
| v6 keep-open election | sole authorization completed with `retire_project=False` / `--keep-project-open`, all member WIs terminal, later auto-retire sweep -> project remains active |
| Membership-scoped detector | detector membership view reports the same ready/excluded projects as `member_completion_ready` |
| Cross-harness parity | both verify-helper twins are byte-identical or contain byte-identical actuation blocks |
| Best-effort safety | actuation failure does not roll back the VERIFIED verdict/commit |

Verification commands:

```text
python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py scripts/project_verified_completion_scanner.py platform_tests/scripts/test_auto_retire_on_verified.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py scripts/project_verified_completion_scanner.py platform_tests/scripts/test_auto_retire_on_verified.py
```

## Pre-Filing Preflight Subsection

Prime Builder will file this REVISED artifact only through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which runs both candidate
preflights against the completed content before publishing live dispatcher/TAFE
state:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-auto-retire-on-verified-actuation-slice-1 --content-file <candidate> --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-auto-retire-on-verified-actuation-slice-1 --content-file <candidate>
```

Expected result: no missing required specs and zero blocking clause gaps.

## Acceptance Criteria

1. `member_completion_ready(project_id)` refuses to auto-retire projects with
   active member WIs missing terminal statuses, zero active members, active
   `plan_incomplete` guards, or detected keep-open elections.
2. A project whose sole authorization was completed with `retire_project=False`
   remains active after a later VERIFIED-finalization auto-retire pass.
3. The scanner membership view uses the same ready/excluded classification as
   the runtime predicate and surfaces keep-open exclusions.
4. Both verify-helper twins retain parity for the actuation seam.
5. Focused tests plus ruff lint/format checks pass.

## Risk / Rollback

- Risk: durable-history keep-open detection may under-retire an ambiguous
  project. This is the intended fail-safe direction; the project remains visible
  and can be retired manually or by a later governed clarification.
- Risk: helper twin drift. Mitigation: include both twins in target paths and
  assert parity in tests.
- Risk: actuation error during VERIFIED finalization. Mitigation: broad
  best-effort wrapper; retirement failure never rolls back the verdict/commit.
- Rollback: revert lifecycle/scanner predicate changes, remove the helper
  actuation blocks, and remove the tests. Append-only project history preserves
  any auto-retirement decisions for manual repair.

## Recommended Commit Type

`feat:` - new event-driven auto-retirement capability implementing
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6, including the preserved
keep-open election.
