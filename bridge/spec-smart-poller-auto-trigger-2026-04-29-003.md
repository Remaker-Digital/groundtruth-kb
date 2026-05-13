WITHDRAWN

# Supersession Notice - Smart-Poller Auto-Trigger Spec + Incident Remediation

bridge_kind: prime_supersession_notice
Document: spec-smart-poller-auto-trigger-2026-04-29
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds-To: `bridge/spec-smart-poller-auto-trigger-2026-04-29-002.md`
Recommended commit type: `docs:`

## Disposition

Prime Builder withdraws this old smart-poller-specific implementation target.
The incident lesson is not withdrawn: bridge dispatch must be automatic when
work waits and must not rely on owner prompts. The implementation substrate,
however, has changed since this GO.

The smart-poller runtime was retired by the verified event-driven replacement
and smart-poller retirement threads. Current bridge dispatch authority is split
between the cross-harness event-driven trigger and the single-harness bridge
dispatcher. Re-implementing this thread as written would revive checks and
release-gate wiring for a retired runtime.

`WITHDRAWN` closes only this obsolete queue entry. It preserves the prior GO
and the S321 incident evidence while preventing the single-harness dispatcher
from repeatedly selecting a stale smart-poller work item.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`

## Superseding Evidence

- `bridge/gtkb-bridge-poller-event-driven-replacement-010.md` verified the
  event-driven bridge replacement foundation.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`
  verified hook registrations for the cross-harness trigger.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md`
  verified smart-poller retirement.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` verified the
  single-harness dispatcher runtime path for single-harness topology.
- `.claude/rules/bridge-essential.md` now describes the retired pollers as
  disabled and identifies the cross-harness event-driven trigger plus
  single-harness dispatcher as the active substrates.

## Standing Backlog / Bulk-Operation Visibility

This closure does not perform a MemBase standing-backlog bulk operation. The
inventory for this withdrawal is the live bridge chain listed in this document
and the superseding bridge evidence above; no work-item state is changed here.

## Specification-Derived Verification

| Specification / rule | Verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This notice is filed as `bridge/spec-smart-poller-auto-trigger-2026-04-29-003.md`; `bridge/INDEX.md` is updated append-only above the prior `GO`. | Prior versions remain preserved; live latest state becomes terminal. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Superseding event-driven and single-harness dispatcher threads are cited. | The obsolete smart-poller lifecycle state is explicit. |
| `.claude/rules/bridge-essential.md` | Current bridge rules identify retired pollers and active replacement substrates. | This closure aligns queue state with current bridge architecture. |

## Owner Decisions / Input

No new owner decision is required. This closure follows verified retirement of
the smart-poller runtime and does not approve or implement new behavior.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md
Get-Content bridge/spec-smart-poller-auto-trigger-2026-04-29-002.md
rg -n "smart-poller retirement|single-harness dispatcher|cross-harness event-driven" bridge .claude/rules
```

Observed result: the live INDEX showed this document latest at `GO`, the
proposal targets smart-poller remediation, and successor bridge/rule evidence
identifies non-smart-poller substrates as current.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
