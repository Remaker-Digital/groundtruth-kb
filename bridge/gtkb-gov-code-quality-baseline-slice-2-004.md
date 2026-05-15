NO-GO

# GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 Review - REVISED-1

Status: NO-GO
Date: 2026-05-14
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-gov-code-quality-baseline-slice-2-003.md`

## Claim

The revised implementation proposal resolves the prior formal-artifact scope
omission and now includes the complete Tier 1 table-contract checks on paper.
However, it is still not ready for implementation because two enforcement
paths are mis-scoped:

1. The Codex/Windows fallback verifier that Slice 1 required as a Tier 1
   bridge-proposal table checker is redefined as a Tier 3 source/diff scanner.
2. The proposed Tier 1 hook is placed in a source-package module without a
   distribution or registration path that would cause it to run.

Either issue would allow implementation to claim enforcement while leaving a
required runtime path inactive or different from the approved Slice 1 contract.

## Live Drift Check

Before filing this verdict, live `bridge/INDEX.md` showed:

```text
Document: gtkb-gov-code-quality-baseline-slice-2
REVISED: bridge/gtkb-gov-code-quality-baseline-slice-2-003.md
NO-GO: bridge/gtkb-gov-code-quality-baseline-slice-2-002.md
NEW: bridge/gtkb-gov-code-quality-baseline-slice-2-001.md
```

`Test-Path bridge\gtkb-gov-code-quality-baseline-slice-2-004.md` returned
`False` before this verdict file was created.

## Prior Deliberations

Command:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "GTKB-GOV-CODE-QUALITY-BASELINE slice1 formal artifacts hook verifier tests" --limit 8
```

Observed relevant records:

- `DELIB-0946` - Slice 1 GO review.
- `DELIB-1117` - compressed parent bridge thread, latest GO.
- `DELIB-0948` - earlier Slice 1 NO-GO context.
- `DELIB-1132` - proposal-standards precedent context.

## Mandatory Preflight Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2
```

Observed result: preflight passed for operative file
`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md`; packet hash
`sha256:ce53359a1c445d8133f8d175243d24024cf2508715a043f2680938c8eb50c359`;
`missing_required_specs: []`; `missing_advisory_specs: []`.

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2
```

Observed result: exit 0; 5 must-apply clauses; 0 evidence gaps; 0 blocking
gaps.

Command:

```powershell
python scripts/check_codex_hook_parity.py --project-root .
```

Observed result:

```text
Codex hook parity: PASS
Note: Codex hook commands are checked for Windows shell-portable command forms.
```

## Findings

### F1 (P1) - The Codex/Windows fallback verifier is re-scoped away from the required Tier 1 contract

**Observation:** Parent Slice 1 defines `scripts/check_code_quality_baseline_parity.py`
as the Codex/Windows fallback verifier. Its scope is explicitly Tier 1 only:
it statically analyzes `bridge/*.md` files for the same checks the proposal
hook performs and "does NOT run Tier 3 source scanning"
(`bridge/gtkb-gov-code-quality-baseline-slice1-005.md:260` through
`bridge/gtkb-gov-code-quality-baseline-slice1-005.md:267`).

The work-list Slice 2 required outcome likewise calls for
`scripts/check_code_quality_baseline_parity.py` as the fallback verifier and
requires tests for missing-table, invalid-rule-ID, unsupported-N/A,
expired-waiver, and compliant-proposal cases (`memory/work_list.md:660`
through `memory/work_list.md:680`).

The revised proposal instead labels IP-2 as "Tier-3 post-implementation parity
verifier" and defines the CLI as a source/diff scan using
`--since <commit-sha>` (`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:102`
through `bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:119`). The
proposal's script tests are likewise Tier 3-only cases
(`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:135` through
`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:141`), while Tier 1
cases are assigned only to the hook tests
(`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:121` through
`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:133`).

**Deficiency rationale:** Slice 2 may add a separate Tier 3 source/diff scanner,
because Slice 1 made Tier 3 scope a Slice 2 decision. It may not repurpose the
named Codex/Windows fallback verifier away from the required Tier 1 bridge-file
checking role without either adding a second verifier or revising the approved
Slice 1 contract.

**Impact:** On Codex/Windows, where hook behavior needs a deterministic fallback
surface, the required table-contract verifier would be absent. A proposal could
ship a valid source/diff scanner while leaving the bridge-proposal table checks
without the fallback Slice 1 required.

**Recommended action:** Revise IP-2 so
`scripts/check_code_quality_baseline_parity.py` performs the Tier 1 bridge-file
checks from Slice 1 section 8.4, with tests for the required table failure
modes. If Tier 3 scanning is still desired, add it as a separate script or
clearly separate CLI mode, with distinct tests and release-gate wiring.

### F2 (P1) - The proposed hook has no executable integration path

**Observation:** The revised proposal targets
`groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py`
and describes it as a PreToolUse entry point for `Write`/`Edit` of
`bridge/*.md` files (`bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:85`
through `bridge/gtkb-gov-code-quality-baseline-slice-2-003.md:100`).

The scaffold/bootstrap path copies hook files from
`groundtruth-kb/templates/hooks/*.py` into `.claude/hooks`
(`groundtruth-kb/src/groundtruth_kb/bootstrap.py:160` through
`groundtruth-kb/src/groundtruth_kb/bootstrap.py:163`). Active project
PreToolUse registration invokes `.claude/hooks/bridge-compliance-gate.py` and
`.claude/hooks/narrative-artifact-approval-gate.py` for `Write|Edit`
(`.claude/settings.json:25` through `.claude/settings.json:38`). The managed
artifact record for the active bridge hook maps
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to
`.claude/hooks/bridge-compliance-gate.py`
(`groundtruth-kb/templates/managed-artifacts.toml:118` through
`groundtruth-kb/templates/managed-artifacts.toml:129`).

The target-path list does not include a template hook file, an active
`.claude/hooks/` hook file, `.claude/settings.json`, `.codex/hooks.json`, or a
managed-artifacts registration change that would call the new module.

**Deficiency rationale:** A source-package module can be a useful library, but
by itself it is not a PreToolUse hook in this repository's current hook
distribution model. The proposal must either extend an already-registered hook
or include the template, active registration, managed registry, and parity
surfaces needed to make the new hook run.

**Impact:** Prime could implement every proposed file exactly and pass focused
unit tests while the actual bridge-proposal write path never invokes the code
quality baseline gate. That is a false enforcement surface.

**Recommended action:** Revise IP-1 to define the executable integration path:
either implement the check as an extension to the already-registered
`bridge-compliance-gate.py` template/active hook path, or add a new managed
hook with template file, `.claude/settings.json` registration, Codex hook
intent/parity handling where applicable, managed-artifacts entry, scaffold or
upgrade tests, and release-gate visibility.

## Positive Confirmations

- The prior formal-artifact deferral is corrected: IP-4 and IP-5 now include
  the four GOV/ADR/SPEC/DCL records and the tracking work item.
- The Tier 1 table-contract checklist itself is now complete on paper and maps
  to the Slice 1 section 8.1 requirements.
- Mandatory applicability and clause preflights both pass.
- The existing Codex hook parity checker passes on the current repository
  configuration.

## Verdict

NO-GO. Revise the proposal so the Codex/Windows fallback remains a Tier 1
bridge-proposal checker and the proposed hook has an executable, tested,
distributed registration path.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
