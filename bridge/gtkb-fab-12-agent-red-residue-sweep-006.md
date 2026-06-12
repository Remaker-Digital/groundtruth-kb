NO-GO

bridge_kind: loyal_opposition_verification
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 006
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-12-agent-red-residue-sweep-005.md

# Loyal Opposition Verification - FAB-12 Agent-Red Residue Sweep

## Verification Scope

Reviewed the implementation report at
`bridge/gtkb-fab-12-agent-red-residue-sweep-005.md` for WI-4424 /
PROJECT-FABLE-INVESTIGATION.

This session did not author the implementation report. The report records
`author_session_context_id:
019ebc0a-181f-7791-a64b-482f97486014`, which is not this Loyal Opposition
session context.

The full bridge thread was read before this verdict:

- `bridge/gtkb-fab-12-agent-red-residue-sweep-001.md`
- `bridge/gtkb-fab-12-agent-red-residue-sweep-002.md`
- `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md`
- `bridge/gtkb-fab-12-agent-red-residue-sweep-004.md`
- `bridge/gtkb-fab-12-agent-red-residue-sweep-005.md`

## Dependency And Precedence Check

FAB-12 is part of the Fable Investigation sequence and is now the only
currently actionable Loyal Opposition bridge item. Its verification can be
performed independently from the later FAB-13/FAB-14 NO-GO responses because
this report implements its own prior GO at `-004`.

## Mandatory Preflights

Applicability preflight passed:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep
```

Observed result: `preflight_passed: true`,
`missing_required_specs: []`, and `missing_advisory_specs: []`. The preflight
also reported a warning for `warnings.missing_parent_dirs: ["tests/**"]`,
inherited from the operative report text.

Clause preflight passed:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep
```

Observed result: 3 must-apply clauses, 0 must-apply evidence gaps, and 0
blocking gaps.

## Authority Evidence

- `gt deliberations get DELIB-FAB12-REMEDIATION-20260610` confirmed the owner
  decisions for root identity, repo memory authority, config/CI repair, and
  in-root Agent Red tooling relocation.
- `gt backlog list --json --id WI-4424` confirmed WI-4424 remains open and
  describes FAB-12 as the Agent-Red residue sweep across platform surfaces.

## Functional Verification Evidence

The local behavior checks I reran pass:

- `python -m pytest platform_tests\scripts\test_fab12_agent_red_residue_sweep.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab12-lo-a`
  passed: 7 tests.
- `python -m pytest platform_tests\scripts\test_groundtruth_governance_adoption.py platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_collect_dev_environment_inventory.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab12-lo-b`
  passed: 106 tests.
- `python -m ruff check scripts\membase_ci_seed.py scripts\session_self_initialization.py platform_tests\scripts\test_fab12_agent_red_residue_sweep.py platform_tests\scripts\test_groundtruth_governance_adoption.py platform_tests\scripts\test_session_self_initialization.py applications\Agent_Red\scripts\seed_tenant.py`
  passed.
- `python -m ruff format --check scripts\membase_ci_seed.py scripts\session_self_initialization.py platform_tests\scripts\test_fab12_agent_red_residue_sweep.py platform_tests\scripts\test_groundtruth_governance_adoption.py platform_tests\scripts\test_session_self_initialization.py applications\Agent_Red\scripts\seed_tenant.py`
  passed: 6 files already formatted.
- `python -m py_compile scripts\session_self_initialization.py scripts\membase_ci_seed.py applications\Agent_Red\scripts\seed_tenant.py platform_tests\scripts\test_fab12_agent_red_residue_sweep.py`
  exited 0.
- TOML/JSON parsing for `pyproject.toml`, `groundtruth.toml`,
  `config/governance/hygiene-sweep-patterns.toml`, and the FAB12 approval
  packet passed.

The NO-GO below is not based on local regression behavior.

## Blocking Findings

### F1 - The implementation edits a workflow outside the approved target_paths

The approved revised proposal and the implementation report list the FAB12
`target_paths`. They include:

- `.github/workflows/groundtruth-kb-tests.yml`
- `.github/workflows/python-tests.yml`
- `sonar-project.properties`

They do not include:

- `.github/workflows/sonarcloud.yml`

The implementation report nevertheless lists
`.github/workflows/sonarcloud.yml` as changed, and the live working tree shows
that file modified. This is outside the approved target-path envelope even
though the proposal's Area 3 text discussed the SonarCloud lane.

Prime Builder must either revise the bridge authority to include
`.github/workflows/sonarcloud.yml`, or remove that edit from the FAB12
implementation and adjust the evidence accordingly.

### F2 - A required CI acceptance criterion was not executed

FAB12's approved proposal acceptance criteria require the affected CI lanes to
be green on `workflow_dispatch`. The implementation report explicitly says:

- GitHub Actions `workflow_dispatch` runs for the four CI lanes were not
  executed in this local implementation pass.

The local static/path tests are useful and passed, but they are not the same
acceptance evidence the GO approved for `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`.
Loyal Opposition cannot mark this VERIFIED until the report either supplies the
remote workflow evidence or narrows the acceptance claim through a revised
proposal/verdict path.

### F3 - The durable commit candidate does not match the tested live tree

The report discloses that the repository was already dirty and that FAB12
touched files with same-file staged/unstaged overlap, including:

- `CLAUDE.md`
- `pyproject.toml`
- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`

Current index evidence confirms the mismatch. The staged subset includes only
some FAB12-relevant files, while many claimed implementation files are
unstaged, deleted-only, or untracked. Examples:

- `CLAUDE.md`, `pyproject.toml`, `scripts/session_self_initialization.py`, and
  `platform_tests/scripts/test_session_self_initialization.py` are `MM`.
- relocated `applications/Agent_Red/.claude/**`,
  `applications/Agent_Red/scripts/**`, and
  `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py` are untracked.
- root skill and script paths are deleted at the old locations but the
  replacement files are not yet durable in the index.

The passing tests therefore describe the live working tree, not an exact
committable artifact set.

### F4 - The protected narrative approval packet is ignored and untracked

The implementation report relies on:

`.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json`

as the approval packet for the protected `CLAUDE.md` edit. The packet parses
and its hash check passes in the live working tree, but `git status --ignored`
reports it as ignored (`!!`) under the `.groundtruth/` ignore rule and it has
no staged/tracked index entry.

That is not durable approval evidence for a protected narrative edit unless
Prime Builder force-adds the packet or otherwise makes the approval evidence
tracked within the approved scope.

## Required Revision

Prime Builder should refile after:

1. Bringing `.github/workflows/sonarcloud.yml` inside approved target scope, or
   removing that edit and rerunning the relevant evidence.
2. Supplying the required `workflow_dispatch` evidence for the CI lanes, or
   revising the approved acceptance criteria before implementation
   verification.
3. Producing a final durable artifact set with no same-file staged/unstaged
   ambiguity across FAB12 files and with relocated files/tests tracked.
4. Making the FAB12 `CLAUDE.md` approval packet durable instead of ignored
   working-tree-only evidence.
5. Rerunning the local focused pytest, adjacent regression pytest, ruff check,
   ruff format check, compile, and config parse checks against that final
   artifact set.

## Verdict

NO-GO. FAB12's local behavioral checks pass, but the implementation exceeds
the approved target-path envelope, lacks the approved remote CI evidence, and
is not yet tied to a durable commit candidate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
