Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-4415, WI-4416, WI-4417, WI-4418, WI-4419

# Fable P1 Verified-Open Disposition Gap

Role: Loyal Opposition
Harness: Codex A
Automation: keep-working-lo
Date: 2026-06-13

## Claim

Five P1 Fable Investigation work items are still live as open/backlogged
MemBase rows even though their corresponding bridge implementation threads are
latest `VERIFIED` and have no INDEX drift:

| Work item | Bridge thread | Latest verified file |
|---|---|---|
| WI-4415 FAB-03 MemBase backup | `gtkb-fab-03-membase-backup` | `bridge/gtkb-fab-03-membase-backup-011.md` |
| WI-4416 FAB-04 storage reclamation | `gtkb-fab-04-storage-reclamation` | `bridge/gtkb-fab-04-storage-reclamation-015.md` |
| WI-4417 FAB-05 rule-file retirement | `gtkb-fab-05-rule-file-retirement` | `bridge/gtkb-fab-05-rule-file-retirement-006.md` |
| WI-4418 FAB-06 narrative corrections | `gtkb-fab-06-narrative-corrections` | `bridge/gtkb-fab-06-narrative-corrections-010.md` |
| WI-4419 FAB-07 doctor false signals | `gtkb-fab-07-doctor-false-signals` | `bridge/gtkb-fab-07-doctor-false-signals-008.md` |

The right next action is a governed backlog disposition pass, not another
implementation proposal for these same clusters.

## Evidence

- Live bridge scan: `python .claude\skills\bridge\helpers\scan_bridge.py --role
  loyal-opposition --format json` reports zero LO-actionable latest `NEW` or
  `REVISED` entries.
- Thread checks:
  - `show_thread_bridge.py gtkb-fab-03-membase-backup --format json
    --preview-lines 0` reports latest `VERIFIED` and `drift: []`.
  - `show_thread_bridge.py gtkb-fab-04-storage-reclamation --format json
    --preview-lines 0` reports latest `VERIFIED` and `drift: []`.
  - `show_thread_bridge.py gtkb-fab-05-rule-file-retirement --format json
    --preview-lines 0` reports latest `VERIFIED` and `drift: []`.
  - `show_thread_bridge.py gtkb-fab-06-narrative-corrections --format json
    --preview-lines 0` reports latest `VERIFIED` and `drift: []`.
  - `show_thread_bridge.py gtkb-fab-07-doctor-false-signals --format json
    --preview-lines 0` reports latest `VERIFIED` and `drift: []`.
- Canonical INDEX evidence:
  - `bridge/INDEX.md:488` through `:499` list FAB-03 with latest `VERIFIED`.
  - `bridge/INDEX.md:507` through `:522` list FAB-04 with latest `VERIFIED`.
  - `bridge/INDEX.md:474` through `:480` list FAB-05 with latest `VERIFIED`.
  - `bridge/INDEX.md:462` through `:472` list FAB-06 with latest `VERIFIED`.
  - `bridge/INDEX.md:452` through `:460` list FAB-07 with latest `VERIFIED`.
- Backlog evidence: `python -m groundtruth_kb.cli backlog list --id WI-4415
  --id WI-4416 --id WI-4417 --id WI-4418 --id WI-4419 --json` reports all five
  rows with `resolution_status: open`, `stage: backlogged`, `approval_state:
  unapproved`, and `completion_evidence: null`.
- Applicability evidence: `python scripts\bridge_applicability_preflight.py
  --bridge-id <thread>` reports `preflight_passed: true` and
  `missing_required_specs: []` for all five threads.

## Finding

Severity: P1 governance/backlog drift.

The project queue is over-reporting high-priority implementation work. The
bridge has already completed the required independent review cycle for these
Fable clusters, but the backlog still exposes them as unfinished P1 rows. This
can cause autonomous workers to keep rediscovering solved work, distract Prime
Builder from genuinely open Fable follow-ups, and blur the distinction between
verified implementation evidence and pending work.

This is not a request for Loyal Opposition to mutate MemBase. Closing or
superseding the rows is a formal backlog disposition and should use the normal
governed path.

## Recommended Action

Prime Builder should run a governed Fable disposition pass for WI-4415 through
WI-4419:

1. Resolve each row whose verified bridge thread fully satisfies the work item,
   with completion evidence pointing to the terminal `VERIFIED` file and the
   implementation report's verification commands.
2. If any row intentionally carries residual scope beyond the verified bridge
   thread, split that remainder into a new work item or rewrite the current
   row's title/acceptance so it no longer duplicates the completed Fable slice.
3. Update related bridge-thread metadata on the rows from the umbrella advisory
   reference to the concrete terminal bridge thread where applicable.
4. Re-run `gt backlog list --priority P1 --resolution-status open --json` after
   disposition so the high-priority queue stops surfacing completed Fable work.

## Owner Decision Needed

No owner decision is required for this Loyal Opposition report. Any actual
MemBase close, supersede, or rewrite operation should carry the required
approval evidence for governed backlog mutation.
