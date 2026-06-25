WITHDRAWN
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 07b18076-9dbc-4aab-9e85-b8a6e89aca07
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (::init gtkb pb); harness B; workspace=E:/GT-KB

# Supersession Notice - GT-KB Project Boundary and Upgrade Hardening (implementation parent)

bridge_kind: lo_verdict
Document: gtkb-project-boundary-and-upgrade-hardening-implementation
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds-To: `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`

## Disposition

Prime Builder withdraws this implementation-parent thread as a current
implementation target, per owner AskUserQuestion decision 2026-06-25
("Withdraw both"; session 07b18076).

This withdrawal makes the live bridge state match what the thread's own GO
already declared. The `-004` GO (2026-04-17) was "structural only... granted
only to close this oversized implementation thread and require the work to move
into protocol-visible sub-bridges. This GO does not approve any GT-KB source,
doc, registry, script, CI, KB, or Agent Red mutation from this parent thread."
The parent was therefore self-described-terminal, with real work redirected to
sub-bridges (e.g., `gtkb-rollback-receipts-001`). The `-004` GO additionally
inspected the archived repository `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`,
which the mandatory project-root boundary forbids as a live GT-KB dependency.
`WITHDRAWN` is the append-only audit-trail closure; it retires no spec or ADR
and does not affect the downstream sub-bridges.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this
  terminal-status reconciliation write.
- `.claude/rules/project-root-boundary.md` - mandatory root boundary; basis for
  the root-boundary-invalid GO finding (archive `E:\Claude-Playground`).
- `.claude/rules/file-bridge-protocol.md` - Mandatory Root Boundary Gate.

## Owner Decisions / Input

- AskUserQuestion (2026-06-25): "Disposition for the project-boundary-hardening
  threads?" -> owner selected **"Withdraw both"**
  (`gtkb-project-boundary-and-upgrade-hardening-002` +
  `gtkb-project-boundary-and-upgrade-hardening-implementation-004`).

## Supersession Evidence

- The `-004` GO text itself closes this parent thread as a "structural redirect"
  and forbids parent-thread mutation; the implementation work moved to
  protocol-visible sub-bridges (rollback to `gtkb-rollback-receipts-001`).
- The project-boundary and upgrade-hardening capabilities are realized in
  canonical (see the sibling proposal-thread supersession notice
  `gtkb-project-boundary-and-upgrade-hardening-003`).
