WITHDRAWN
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 07b18076-9dbc-4aab-9e85-b8a6e89aca07
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (::init gtkb pb); harness B; workspace=E:/GT-KB

# Supersession Notice - Spec-Pipeline F8 (Provenance Reconciliation)

bridge_kind: lo_verdict
Document: gtkb-spec-pipeline-f8
Version: 015
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds-To: `bridge/gtkb-spec-pipeline-f8-014.md`

## Disposition

Prime Builder withdraws this GO'd spec-pipeline thread as a current
implementation target, per owner AskUserQuestion decision 2026-06-25
("Withdraw all 9"; session 07b18076).

The `-014` GO verdict was produced against the archived repository
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`. The mandatory
project-root boundary designates that location archive-only and forbids
treating it as a live GT-KB dependency; the file-bridge protocol's Mandatory
Root Boundary Gate makes a thread whose GO depends on a path outside `E:\GT-KB`
invalid until revised. The capability has been independently realized in
canonical `E:\GT-KB` (under different naming), so this orphaned transport
thread is superseded rather than abandoned. `WITHDRAWN` is the append-only
audit-trail closure; it retires no spec or ADR.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this
  terminal-status reconciliation write.
- `.claude/rules/project-root-boundary.md` - mandatory root boundary; basis for
  the root-boundary-invalid GO finding (archive `E:\Claude-Playground`).
- `.claude/rules/file-bridge-protocol.md` - Mandatory Root Boundary Gate.

## Owner Decisions / Input

- AskUserQuestion (2026-06-25): "Reconciliation review packet - withdraw the
  superseded spec-pipeline cluster?" -> owner selected **"Withdraw all 9"**
  (`gtkb-spec-pipeline-f1`...`f8` + `gtkb-f1f8-cross-check`). Owner was advised
  F8 carried the weakest direct code signal; the root-boundary-invalid GO basis
  applies regardless of naming.

## Supersession Evidence

- F8 Provenance Reconciliation is realized in canonical under different naming:
  `scripts/bridge_verified_backlog_reconciler.py` (verified-backlog/parent-evidence
  reconciliation) plus the WI-4230-class `related_bridge_threads` linkage
  correction packets (WI-4230 / WI-4231 / WI-4233) provide the provenance
  reconciliation capability the F8 proposal scoped under `provenance_reconcile*`
  symbols.
