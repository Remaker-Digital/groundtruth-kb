WITHDRAWN
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 07b18076-9dbc-4aab-9e85-b8a6e89aca07
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (::init gtkb pb); harness B; workspace=E:/GT-KB

# Supersession Notice - GT-KB Project Boundary and Upgrade Hardening (proposal)

bridge_kind: lo_verdict
Document: gtkb-project-boundary-and-upgrade-hardening
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds-To: `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md`

## Disposition

Prime Builder withdraws this GO'd proposal thread as a current implementation
target, per owner AskUserQuestion decision 2026-06-25 ("Withdraw both";
session 07b18076).

The `-002` GO verdict (2026-04-17) was produced against the archived repository
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` ("Target checkout
inspected" line, observed HEAD `cf29738`). The mandatory project-root boundary
designates that location archive-only and forbids treating it as a live GT-KB
dependency; the file-bridge protocol's Mandatory Root Boundary Gate makes a
thread whose GO depends on a path outside `E:\GT-KB` invalid until revised. The
scope has been independently realized/redirected in canonical `E:\GT-KB`, so
this orphaned transport thread is superseded rather than abandoned. `WITHDRAWN`
is the append-only audit-trail closure; it retires no spec or ADR.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this
  terminal-status reconciliation write.
- `.claude/rules/project-root-boundary.md` - mandatory root boundary; basis for
  the root-boundary-invalid GO finding (archive `E:\Claude-Playground`) and the
  canonical realization of the project-boundary scope.
- `.claude/rules/file-bridge-protocol.md` - Mandatory Root Boundary Gate.

## Owner Decisions / Input

- AskUserQuestion (2026-06-25): "Disposition for the project-boundary-hardening
  threads?" -> owner selected **"Withdraw both"**
  (`gtkb-project-boundary-and-upgrade-hardening-002` +
  `gtkb-project-boundary-and-upgrade-hardening-implementation-004`).

## Supersession Evidence

- Project-root-boundary scope is realized in canonical by
  `.claude/rules/project-root-boundary.md` plus the boundary doctor checks
  (`_check_harness_local_scratchpad_boundary`, `_check_external_harness_exec_boundary`,
  `_check_db_snapshot_output_allowlist`).
- Upgrade-hardening scope is realized by the verified upgrade pre-flight work
  (`bridge/gtkb-upgrade-pre-flight-checks-implementation` reached VERIFIED) and
  the dry-run upgrade plan surfaced at session start.
