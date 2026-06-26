NEW

# GT-KB Bridge Implementation Report — gtkb-wi3350-parent-project-pauth-covers-subproject — 003

bridge_kind: implementation_report
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f95c6f19-b1a8-4602-8d22-43886dcdf659
author_model: claude-opus-4-8
author_model_version: opus-4.8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)
Document: gtkb-wi3350-parent-project-pauth-covers-subproject
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi3350-parent-project-pauth-covers-subproject-002.md
Approved proposal: bridge/gtkb-wi3350-parent-project-pauth-covers-subproject-001.md
Project: PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001
Work Item: WI-3350
Recommended commit type: fix

## Implementation Claim

The GO'd `-001` scope is implemented exactly as approved and committed in `9008ca135`
(`fix(impl-auth): accept a parent-project PAUTH for a sub-project proposal (WI-3350)`).
`validate_project_authorization_row` now honors the backlog → projects → sub-projects
taxonomy: a proposal scoped to a sub-project validates under a PAUTH attached to an
ancestor project.

- `scripts/implementation_authorization.py` — three read-only helpers added after
  `_work_item_in_project`:
  - `_project_parent(project_root, project_id)` — reads `current_projects.parent_project_id`.
  - `_is_descendant_project(project_root, candidate, ancestor, *, max_depth=32)` — walks the
    `parent_project_id` chain upward; depth-bounded + visited-set cycle guard; fail-closes
    (returns False) on cycle / missing row / depth exceeded.
  - `_work_item_in_project_or_descendant(project_root, project_id, work_item_id)` — active
    membership in the project or any descendant sub-project.
  The two reject-points are relaxed: the exact `proposal_project_id != project_id` check now
  also accepts a descendant via `_is_descendant_project`; the empty-included-list membership
  check now uses `_work_item_in_project_or_descendant`. The DELIB-20266083 restrictive
  included-list branch and the active/expired/excluded/spec-exclusion checks are untouched.
- `platform_tests/scripts/test_implementation_authorization.py` — a parent/sub-project
  hierarchy fixture (`_seed_project_hierarchy`) + 5 spec-derived tests.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization; a sub-project proposal inside an authorized parent project is within that authorization's intent.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — envelope fields explicit + append-only; this change reads the envelope and hierarchy, mutating neither.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — unaffected (spec-link checks unchanged).
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — preserved: only PAUTH↔proposal project matching changed; the bridge-GO + implementation-start packet requirement is intact (this work itself went through GO + a validated packet).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed through the append-only numbered bridge-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied (spec-to-test mapping below).
- `GOV-STANDING-BACKLOG-001` — WI-3350 is the governing backlog item.

## Owner Decisions / Input

Carried forward from the approved proposal `-001`:

- `DELIB-20265586` (owner decision authorizing PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001
  implementation; the PAUTH's `owner_decision_deliberation_id`). The covering
  `PAUTH-...-BOUNDED-IMPLEMENTATION-2026-06-23` lists `WI-3350` in `included_work_item_ids` and
  grants `allowed_mutation_classes` including `source` + `test_addition` — exactly the change
  classes here. The implementation-start packet (`packet_hash sha256:c2c89449…`) validated this
  authorization before any source edit.

No new owner decision is required by this report.

## Prior Deliberations

- `bridge/gtkb-wi3350-parent-project-pauth-covers-subproject-001.md` — approved proposal carried forward.
- `bridge/gtkb-wi3350-parent-project-pauth-covers-subproject-002.md` — LO GO verdict (Cursor, harness E, session `cursor-e-20260626-lo-autoproc-2`).
- `DELIB-20266083` — restrictive `included_work_item_ids` semantics; the included-list branch was deliberately left untouched (verified by `test_validate_included_list_still_authoritative_for_subproject`).
- `DELIB-20265586` — the authorizing owner decision.

## Specification-Derived Verification Plan

| Requirement clause (linked spec) | Test | Result |
| --- | --- | --- |
| Parent PAUTH covers sub-project proposal (`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`) | `test_validate_accepts_subproject_proposal_under_parent_pauth` | PASS |
| WI membership in a sub-project honored under parent PAUTH | `test_validate_accepts_work_item_in_subproject_under_parent_pauth` | PASS |
| Unrelated (non-descendant) project still rejected — no over-acceptance | `test_validate_rejects_unrelated_project_proposal` | PASS |
| Restrictive `included_work_item_ids` preserved (`DELIB-20266083`) | `test_validate_included_list_still_authoritative_for_subproject` | PASS |
| Cycle / depth guard fail-closed (no hang) + genuine descendant resolves True | `test_is_descendant_project_handles_cycle` | PASS |
| No regression in the validator + packet flow | full `test_implementation_authorization.py` suite | PASS (107 passed) |

## Commands Run

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe` (Python 3.14.0).

- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -k "subproject or descendant or unrelated_project or included_list_still" -q --tb=short`
- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short`
- `python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py`
- `python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py`

## Observed Results

- New WI-3350 tests: `5 passed, 102 deselected`.
- Full `test_implementation_authorization.py` suite: `107 passed` (102 pre-existing + 5 new; no regression).
- `ruff check`: `All checks passed!`
- `ruff format --check`: `2 files already formatted`.

## Files Changed

Scoped to the GO'd `target_paths`; committed in `9008ca135` (2 files changed, +196 / -4):

- `scripts/implementation_authorization.py` — 3 read-only hierarchy helpers + 2 relaxed reject-points in `validate_project_authorization_row`.
- `platform_tests/scripts/test_implementation_authorization.py` — `_seed_project_hierarchy` fixture + 5 spec-derived tests.

No other files were changed by this work.

## Recommended Commit Type

- Recommended commit type: `fix:` — repairs the project-auth validator to honor the project/sub-project hierarchy for PAUTH↔proposal matching. No new capability surface beyond closing the hierarchy gap; no change to bridge controls or owner-facing behavior. (The change landed under this exact `fix:` commit `9008ca135`.)

## Acceptance Criteria Status

1. Sub-project proposal accepted under an ancestor-project PAUTH (exact-match + membership honor `parent_project_id`). — MET (`*_accepts_subproject_*` + `*_accepts_work_item_in_subproject_*`).
2. `included_work_item_ids` restrictive semantics unchanged (DELIB-20266083). — MET (`*_included_list_still_authoritative_*`).
3. Unrelated (non-descendant) projects still rejected; ancestor walk cycle- and depth-guarded (fail-closed). — MET (`*_rejects_unrelated_project_*`, `*_handles_cycle`).
4. No change to active/expired/excluded/spec-exclusion checks, the bridge-GO requirement, or the implementation-start packet. — MET (only the 2 reject-points changed; 107-pass no-regression; this work itself flowed through GO + a validated packet).
5. `ruff check` + `ruff format --check` pass; existing suite green. — MET.

## Risk And Rollback

- Risk: over-acceptance (a parent PAUTH wrongly authorizing an unrelated project). Mitigation: acceptance requires a concrete `parent_project_id` ancestry link to the PAUTH's project; `test_validate_rejects_unrelated_project_proposal` locks rejection of non-descendants; the walk is depth-bounded + cycle-guarded.
- Risk: weakening the restrictive included-list gate. Mitigation: the included-list branch was left untouched; `test_validate_included_list_still_authoritative_for_subproject` locks this.
- Rollback: revert commit `9008ca135` (the 3 helpers + 2 relaxed conditionals + 5 tests); prior exact-match behavior returns. No schema change; append-only KB untouched; read-only hierarchy queries only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence above. Report author session: `f95c6f19-b1a8-4602-8d22-43886dcdf659` (independent of the eventual verifier; the GO author was the Cursor LO session `cursor-e-20260626-lo-autoproc-2`).
2. Return VERIFIED if the report and implementation (commit `9008ca135`) satisfy the approved proposal `-001`; otherwise NO-GO with findings.
