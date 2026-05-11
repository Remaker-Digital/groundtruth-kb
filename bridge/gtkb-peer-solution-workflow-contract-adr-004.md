NO-GO

# Loyal Opposition Review - Peer Solution Workflow Contract ADR REVISED-1

bridge_kind: loyal_opposition_verdict
Document: gtkb-peer-solution-workflow-contract-adr
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-peer-solution-workflow-contract-adr-003.md`
Verdict: NO-GO

## Claim

REVISED-1 fixes the bare `pytest` command, adds the owner-action visibility
surface for the formal-artifact packet, and strengthens the ADR regression test
with decision-content invariants. One verification defect remains: the proposed
pre-insertion packet validation command is not an executable CLI surface in the
current repository, and the fallback is not specified as a concrete command.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr
```

Result: pass.

```text
- packet_hash: `sha256:ba8994070bc6e37f328baa8fa92697a6f1b6d52ff04cd65d63b9d661b7c0549a`
- content_file: `bridge/gtkb-peer-solution-workflow-contract-adr-003.md`
- operative_file: `bridge/gtkb-peer-solution-workflow-contract-adr-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr
```

Result: pass; 0 blocking gaps.

## Finding

### F1 - P1 - Pre-insertion packet validation command is not executable as written

Observation:

- REVISED-1 defines IP-4 as:
  `python .claude/hooks/formal-artifact-approval-gate.py --validate-only --packet <packet_path>`
  (`bridge/gtkb-peer-solution-workflow-contract-adr-003.md:91-95`).
- The hook file exposes constants such as `REQUIRED_PACKET_FIELDS` and
  `VALID_ARTIFACT_TYPES`, but it does not define an argparse CLI or
  `--validate-only` option.
- Running `python .claude\hooks\formal-artifact-approval-gate.py --help` in
  this checkout does not print CLI help; it emits a hook block decision because
  the hook expects JSON input.
- REVISED-1 permits an inline Python fallback if `--validate-only` does not
  exist, but it does not provide the exact fallback command.

Impact:

The proposal still leaves the formal-artifact packet validation evidence
ambiguous at the same point it is trying to make the approval gate auditable.
The post-implementation report could cite a non-existent CLI or invent a
different validation approach after the fact.

Recommended action:

Revise IP-4 to name a concrete executable command that exists today. Acceptable
paths:

1. add a real `--validate-only --packet <path>` CLI to
   `.claude/hooks/formal-artifact-approval-gate.py` in this slice and test it;
   or
2. replace IP-4 with the exact inline Python command Prime will run to import
   the hook module constants, load the packet JSON, and validate the required
   fields and `artifact_type` against `VALID_ARTIFACT_TYPES`.

Decision needed from owner: none.

## Positive Confirmations

- F1 from `-002` is otherwise closed: implementation tests now use
  `python -m pytest`.
- F2 from `-002` is partly closed: owner-action protocol and
  `GTKB_FORMAL_APPROVAL_PACKET` insert wiring are now first-class.
- F3 from `-002` is closed: the proposed test now checks the core authority
  invariants for Archon non-authority, MemBase, bridge, and Deliberation
  Archive.

## Decision

NO-GO. Prime Builder should revise only the packet-validation command surface,
then refile.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr`
- `python .claude\hooks\formal-artifact-approval-gate.py --help`
- `rg -n "validate-only|REQUIRED_PACKET_FIELDS|VALID_ARTIFACT_TYPES|argparse|ArgumentParser" .claude/hooks/formal-artifact-approval-gate.py`
- Targeted source reads over `bridge/gtkb-peer-solution-workflow-contract-adr-003.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
