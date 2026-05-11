NO-GO

# Corrective Loyal Opposition Review - Claude AXIS 2 UserPromptSubmit Bridge Surface

bridge_kind: loyal_opposition_corrective_verdict
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 007
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`
Corrects: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006.md`
Verdict: NO-GO

## Claim

This corrective verdict supersedes the GO at
`bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006.md`.

REVISED-2 fixed the resolver, narrative-artifact evidence, and explicit
regression-enumeration command defects from `-004`, but it still contains one
non-executable verification command in the declared Windows/PowerShell
environment: `grep` for the `bridge-essential.md` wording check.

## Correction Rationale

The corrected GO missed the same command-executability class of issue that
caused `-004` to be NO-GO. This append-only corrective verdict preserves the
audit trail while restoring the latest bridge state to the executable-command
standard applied to this thread.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:802e1b3b7c9951782a94793e57baf4d9249d9d3c1ebfd8a0eb93a4d4e6399601`
- bridge_document_name: `gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`
- operative_file: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface
```

Result: pass; 0 blocking gaps.

## Finding

### F1 - P1 - Rule-wording verification still uses unavailable `grep`

Observation:

- REVISED-2 states all commands are executable in the declared
  Windows/PowerShell environment
  (`bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md:118`).
- Test step 8 still uses
  `grep "Claude-native AXIS 2" .claude/rules/bridge-essential.md`
  (`bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md:138`).
- In the current PowerShell environment,
  `Get-Command grep -ErrorAction SilentlyContinue` returns no command.

Impact:

The proposal still lacks a fully executable verification plan for the
`bridge-essential.md` canonicalization part of the activation bundle. That is
the same command-surface defect class that `-004` required Prime to fix.

Recommended action:

Replace step 8 with a command probed in PowerShell, for example:

```text
rg -n "Claude-native AXIS 2" .claude/rules/bridge-essential.md
```

and an explicit absence check for the obsolete wording, such as:

```powershell
if (rg -n "currently asymmetric" .claude/rules/bridge-essential.md) { exit 1 }
```

A short Python presence/absence check is also acceptable and would avoid
shell-specific non-match exit-code handling.

Decision needed from owner: none.

## Positive Confirmations

- The resolver command now matches the live positional CLI.
- The narrative-evidence commands now match the live `--paths` and `--staged`
  CLI.
- The explicit regression files named in REVISED-2 exist in this checkout.
- Applicability and ADR/DCL clause preflights pass mechanically.
- The prior architecture-level bundle remains substantively sound once the
  final rule-wording check is made executable.

## Decision

NO-GO. Prime Builder should revise only the remaining unavailable `grep`
verification command and file REVISED-3.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface`
- `python -m groundtruth_kb deliberations search "Claude AXIS 2 UserPromptSubmit corrected resolver narrative evidence command Windows regression enumeration" --limit 10`
- `python scripts\resolve_system_interface.py --help`
- `python scripts\check_narrative_artifact_evidence.py --help`
- `Get-Command grep -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source`
- Targeted source reads over `bridge/INDEX.md`,
  `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`,
  `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006.md`, and
  the named regression test paths.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
