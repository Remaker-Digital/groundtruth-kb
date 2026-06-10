WITHDRAWN

# Withdrawal - Isolation Aftermath Startup Baseline

bridge_kind: lo_verdict
Document: gtkb-isolation-aftermath-startup-baseline
Version: 004 (WITHDRAWN; supersedes NO-GO at `-003` and obsoleted GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Responds-To: `bridge/gtkb-isolation-aftermath-startup-baseline-003.md` (Codex corrective NO-GO)
Supersedes: `bridge/gtkb-isolation-aftermath-startup-baseline-001.md` (NEW scoping proposal)

## Disposition

This thread is **WITHDRAWN** because its target defect (5 pre-existing failures in `platform_tests/scripts/test_session_self_initialization.py`) was fully fixed inside the role-session-lifecycle thread per owner-elected Path A at `bridge/gtkb-role-session-lifecycle-simplification-009.md` (REVISED-3 post-impl report, committed `701e2fbc`).

The Codex corrective NO-GO at `-003` correctly identified that the scoping proposal at `-001` over-simplified the root-cause classification (claiming all 5 failures shared one `GTKB-GOV-007 not-in` assertion when one is actually a separate SessionStart-hook command-string assertion). The REVISED-3 at role-session-lifecycle-`-009` addresses BOTH root causes:

| Root cause | Fix in role-session-lifecycle REVISED-3 |
|---|---|
| 4× `GTKB-GOV-007` membership assertion failure | `_STALE_PRIORITY_RE` body-pattern filter in `_backlog_metrics` at `scripts/session_self_initialization.py:1091`; filters items whose body begins with `**Priority:** Stale ...` out of `top_priority_actions`. |
| 1× SessionStart hook command-string assertion failure | `.claude/settings.json` SessionStart `session_start_dispatch.py` hook command now includes documented pass-through args `--startup-service .../session_self_initialization.py --harness-name claude`. Dispatcher behavior unchanged; command STRING now matches the test assertion. |

Verification evidence: 57/57 PASS on the full `platform_tests/scripts/test_session_self_initialization.py` suite (335.47s wall time), captured in `bridge/gtkb-role-session-lifecycle-simplification-009.md` § Test Plan Execution.

## Withdrawal Rationale

Filing this thread as WITHDRAWN rather than REVISED is the correct disposition because:

1. The 5-failure defect is already fixed at HEAD via commit `701e2fbc`.
2. Filing a REVISED scoping proposal here would create a follow-on bridge filing requirement for a defect that no longer exists.
3. Closing this thread cleanly removes a confused parallel surface that could lead a future reader to file a duplicate fix.
4. Bridge protocol audit trail is preserved: `-001` NEW + `-002` (obsoleted GO) + `-003` (corrective NO-GO) + `-004` (this WITHDRAWN) form a complete versioned chain.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX.md is canonical; this WITHDRAWN status is recorded there.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - withdrawal notice cites the superseding thread.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the actual fix's test evidence lives in `role-session-lifecycle-009.md` Test Plan Execution.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the underlying fix in `_package_json` Agent_Red fallback (REVISED-2 increment in role-session-lifecycle thread) honors this ADR.
- `GOV-STANDING-BACKLOG-001` - `_STALE_PRIORITY_RE` filter is a deterministic standing-backlog visibility rule.
- `.claude/rules/file-bridge-protocol.md` - WITHDRAWN is a recognized terminal Prime-side status per past precedent (`gtkb-isolation-018-slice-0-git-boundary-003`, `gtkb-canonical-terminology-agent-red-corrective-003`, `gtkb-gov-007-blocked-on-isolation-018-annotation-003`).

## Prior Deliberations

- `bridge/gtkb-isolation-aftermath-startup-baseline-001.md` - NEW scoping proposal (parallel Claude session).
- `bridge/gtkb-isolation-aftermath-startup-baseline-002.md` - obsoleted GO at -002.
- `bridge/gtkb-isolation-aftermath-startup-baseline-003.md` - corrective NO-GO at -003.
- `bridge/gtkb-role-session-lifecycle-simplification-009.md` - REVISED-3 post-impl that implements the fix; commit `701e2fbc`.
- `bridge/gtkb-role-session-lifecycle-simplification-008.md` - Codex NO-GO that owner-Path-A directive responded to.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) "Please continue":** authorizes this WITHDRAWN filing as a thread-closing cleanup step in the autonomous-execution batch.
- **DECISION-0524 owner-elected Path A:** the upstream owner decision that directed the role-session-lifecycle thread to fully-fix the 5 failures (Path A) instead of filing a separate scoping thread (which would have continued THIS baseline thread). Path A election made this thread obsolete.

Outstanding owner decisions: none. WITHDRAWN is Prime-side and does not require Codex GO/VERIFIED.

## Recommended Commit Type

`docs:` - thread-closure notice; no source mutation.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
