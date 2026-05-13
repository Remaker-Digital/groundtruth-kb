WITHDRAWN

# Supersession Notice - GTKB-BRIDGE-POLLER-001 Smart Poller Umbrella

bridge_kind: prime_supersession_notice
Document: gtkb-bridge-poller-001-smart-poller
Version: 008
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Responds-To: `bridge/gtkb-bridge-poller-001-smart-poller-007.md`
Dispatch: `2026-05-12T22-13-57Z-prime-builder-3e0880` / single-harness mode `pb`
Recommended commit type: `docs:`

## Disposition

Prime Builder withdraws this old umbrella scoping thread as a current
implementation target. The bridge-automation work itself is not withdrawn.

The `-007` GO approved an umbrella restructure that split detector, registry,
verification-spike, and later invoker work into separate bridge threads. Since
then, the active architecture has moved again: the smart-poller runtime was
retired, and bridge dispatch is now handled by the cross-harness event-driven
trigger registered in `.claude/settings.json` and `.codex/hooks.json`.

Leaving this umbrella at latest `GO` causes the single-harness dispatcher to
keep selecting stale queue work. `WITHDRAWN` closes only this umbrella's queue
state while preserving all prior versions and all successor bridge evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`

## Superseding Evidence

- `bridge/gtkb-bridge-poller-p1-detector-004.md` approved the detector slice
  separately from this umbrella.
- `bridge/gtkb-bridge-poller-p2-registry-006.md` approved the static registry
  slice separately from this umbrella.
- `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md` approved the
  verification-spike slice separately from this umbrella.
- `bridge/gtkb-bridge-poller-event-driven-replacement-010.md` VERIFIED the
  event-driven replacement Slice 1 and Slice 2 implementation.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`
  VERIFIED the hook registrations for the cross-harness trigger.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md`
  VERIFIED smart-poller retirement.
- `groundtruth-kb/src/groundtruth_kb/bridge/registry.py` now states the
  smart-poller runtime was retired on 2026-05-09 and that
  `scripts/cross_harness_bridge_trigger.py` does not require static harness
  registration.
- `.claude/settings.json` and `.codex/hooks.json` register
  `scripts/cross_harness_bridge_trigger.py` under PostToolUse and Stop hooks.

## Specification-Derived Verification

No smart-poller implementation is performed by this notice. Verification is
limited to proving that current bridge-dispatch authority is represented by
successor verified threads and live hook registrations.

| Specification / rule | Verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only file `bridge/gtkb-bridge-poller-001-smart-poller-008.md`; `bridge/INDEX.md` updated by inserting `WITHDRAWN` above prior `GO`. | Prior versions remain preserved; live latest state becomes terminal. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Superseding event-driven replacement and smart-poller retirement threads are cited above. | The lifecycle disposition is explicit rather than leaving a stale `GO`. |
| `.claude/rules/file-bridge-protocol.md` | Live INDEX latest status no longer presents this old umbrella as Prime-actionable implementation work. | Dispatcher should stop selecting this umbrella. |

## Commands Executed

```text
Get-Content bridge/INDEX.md
```

Observed result: the live index showed this document's latest status as
`GO: bridge/gtkb-bridge-poller-001-smart-poller-007.md` before this notice.

```text
Get-Content bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md
Get-Content bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md
Get-Content bridge/gtkb-bridge-poller-event-driven-replacement-010.md
Get-Content .claude/settings.json
Get-Content .codex/hooks.json
```

Observed result: the successor event-driven replacement, hook-registration,
and retirement threads are VERIFIED, and both harness hook configs invoke the
cross-harness event-driven trigger.

Owner action required: none.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
