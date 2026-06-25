WITHDRAWN
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 07b18076-9dbc-4aab-9e85-b8a6e89aca07
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (::init gtkb pb); harness B; workspace=E:/GT-KB

# Supersession Notice - Spec-Pipeline F4 (Cross-Cutting Constraint Propagation)

bridge_kind: lo_verdict
Document: gtkb-spec-pipeline-f4
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds-To: `bridge/gtkb-spec-pipeline-f4-004.md`

## Disposition

Prime Builder withdraws this GO'd spec-pipeline thread as a current
implementation target, per owner AskUserQuestion decision 2026-06-25
("Withdraw all 9"; session 07b18076).

The `-004` GO verdict was produced against the archived repository
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` (see the verdict's
"Target repo inspected" line and its evidence citations). The mandatory
project-root boundary designates that location archive-only and forbids
treating it as a live GT-KB dependency, and the file-bridge protocol's
Mandatory Root Boundary Gate makes a thread whose GO depends on a path outside
`E:\GT-KB` invalid until revised. Re-executing this thread as written would
reintroduce the prohibited outside-root dependency.

The feature's capability has been independently realized in canonical
`E:\GT-KB` under native threads, so this orphaned transport thread is
superseded rather than abandoned. `WITHDRAWN` is the narrow audit-trail
closure: it makes the live bridge state terminal for this thread while
preserving all prior versions (append-only). It retires no spec or ADR.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this
  terminal-status reconciliation write.
- `.claude/rules/project-root-boundary.md` - mandatory root boundary; basis for
  the root-boundary-invalid GO finding (archive `E:\Claude-Playground`).
- `.claude/rules/file-bridge-protocol.md` - Mandatory Root Boundary Gate; an
  out-of-root-dependent GO is invalid until revised.

## Owner Decisions / Input

- AskUserQuestion (2026-06-25): "Reconciliation review packet - withdraw the
  superseded spec-pipeline cluster?" -> owner selected **"Withdraw all 9"**
  (`gtkb-spec-pipeline-f1`...`f8` + `gtkb-f1f8-cross-check`), on the evidence
  that all nine carry root-boundary-invalid GOs and the F1-F7 capabilities
  exist in canonical `E:\GT-KB`.

## Supersession Evidence

- F4 Cross-Cutting Constraint Propagation is realized in canonical by the
  applicability/clause-propagation surface: `config/governance/spec-applicability.toml`
  (cross-cutting spec triggers) plus the constraint-check path consumed by
  `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py`.
- The `affected_by` constraint column the F4 Phase-B write path depended on is
  present in the canonical `specifications` schema (F1 landed).
