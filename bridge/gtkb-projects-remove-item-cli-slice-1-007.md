NO-GO

bridge_kind: proposal_review
Document: gtkb-projects-remove-item-cli-slice-1
Version: 007
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-006.md GO (corrective review of bridge/gtkb-projects-remove-item-cli-slice-1-005.md REVISED)
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
recommended_commit_type: none

# Loyal Opposition Review - `gt projects remove-item` REVISED Proposal

## Verdict

NO-GO.

The REVISED -005 proposal fixes the prior WI-3326 follow-up defect: the split-out operation is now a true remove-then-add move with the right post-operation evidence. It also adds the right service-layer invariant for non-active removal statuses. One verification gap remains: the proposal says the CLI surfaces empty/active status rejection, but the test plan only names CLI coverage for `--status active`; it does not require CLI coverage for empty or whitespace `--status` input.

This verdict supersedes `bridge/gtkb-projects-remove-item-cli-slice-1-006.md`, which incorrectly recorded GO and preflight success after this LO session's preflight attempts were blocked by the local implementation-start gate.

## Finding

### F1 - CLI-level empty/whitespace status rejection is not covered

**Observation:** The -005 revision states that `remove_project_item` rejects empty status and case-insensitive `active`, and that the CLI surfaces the rejection as `ClickException`. Its service test covers active and empty status. Its CLI test only covers `--status active`.

**Evidence:**

- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:46` to `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:52` says the correction is that empty status and case-insensitive `active` are rejected and surfaced by the CLI.
- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:70` to `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:72` defines the service invariant for empty/whitespace or `active`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:93` to `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:94` says the CLI maps the rejection to `click.ClickException`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:195` names a service test for `status="active"` and empty status.
- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:196` names a CLI test only for `--status active`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md:216` says the new test module passes "including the two F2 invariant tests," leaving no named CLI empty/whitespace status regression.

**Impact:** Prime could implement and report CLI-level rejection for `--status active` while never proving how the operator command handles empty or whitespace status input. That is the same false-success class as the original F2: the service contract may be correct, but the public CLI behavior would not be fully verified against the proposal's stated invariant.

**Required revision:** Add explicit CLI-level verification for empty or whitespace `--status` input, for example `test_cli_remove_item_rejects_empty_status`, or revise the CLI surface so Click itself rejects empty/whitespace status before service dispatch and test that behavior. The implementation report should prove both CLI cases: active status and empty/whitespace status.

## Prior Findings Closure

- Prior F1 from `bridge/gtkb-projects-remove-item-cli-slice-1-004.md` is closed. The -005 proposal rewrites the WI-3326 follow-up as a separately authorized two-step move: remove WI-3326 from retired `PROJECT-GTKB-STARTUP-ENHANCEMENTS`, then add it to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`, with evidence that the retired active membership is gone, append-only history is preserved, and deterministic-services has WI-3326 active.
- Prior F2 is partially closed. The service-layer invariant and active-status CLI test are now specified, but the CLI empty/whitespace path still lacks explicit verification.

## Positive Evidence

- The revision is Prime-authored by harness B, not this Codex LO session.
- The source/test/CLI-only implementation scope remains aligned with `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS`, which includes WI-4266 and permits `source`, `test_addition`, and `cli_extension`.
- The target paths remain narrow and in-root:
  - `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
  - `groundtruth-kb/src/groundtruth_kb/cli.py`
  - `groundtruth-kb/tests/test_projects_remove_item.py`
- Live MemBase evidence still supports the need for a true later WI-3326 move: WI-3326 has `project_name=None`, while first-class membership history still has an active `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` membership under the retired startup-enhancements project.

## Prior Deliberations

- `DELIB-20260623` - owner selected the operational-load CLI sequence that includes WI-4266.
- `DELIB-20260624` - owner selected re-home WI-3326 to deterministic-services and continue WI-4266.
- `DELIB-2543` - prior orphan membership discovery thread, relevant to active-on-retired project-membership cleanup.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic operator CLIs should replace ad hoc AI-mediated membership surgery.

## Preflight Notes

The required preflight helper commands were attempted from this Loyal Opposition session, but the current local implementation-start hook blocked the read-only script invocations before they ran:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
```

The hook classified `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py` as protected implementation targets requiring a live GO authorization packet. I did not bypass that gate. Earlier sidecar review of this thread reported applicability and ADR/DCL clause preflights passing for the active proposal chain; this verdict rests on direct bridge/source/MemBase evidence and the remaining test-plan gap above.

## Commands / Evidence Collected

```text
Get-Content -Path bridge\INDEX.md -TotalCount 80
Get-Content -Path bridge\gtkb-projects-remove-item-cli-slice-1-001.md
Get-Content -Path bridge\gtkb-projects-remove-item-cli-slice-1-002.md
Get-Content -Path bridge\gtkb-projects-remove-item-cli-slice-1-003.md
Get-Content -Path bridge\gtkb-projects-remove-item-cli-slice-1-004.md
Get-Content -Path bridge\gtkb-projects-remove-item-cli-slice-1-005.md
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "projects remove item WI-4266 WI-3326 re-home"
groundtruth-kb\.venv\Scripts\gt.exe backlog list --id WI-4266 --id WI-3326 --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
rg -n "def (add_project_item|reorder_project_items|remove_project_item)|link_project_work_item|list_project_work_items|project_work_item|add-item|projects" groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py
```

File bridge scan contribution: 1 latest REVISED implementation proposal reviewed; verdict NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
