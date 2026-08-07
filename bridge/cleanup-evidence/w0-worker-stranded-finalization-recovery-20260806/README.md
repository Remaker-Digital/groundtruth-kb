# W0 worker-enablement plumbing — stranded file-only VERIFIED finalization (006)

Date: 2026-08-06 UTC
Actor: loyal-opposition/goose/G
Session: G-2026-08-06T20-01-18Z
Recovery route: WI-5825-class poisoned-row / aggregate-preimage recovery procedure

## Summary

The `--finalize-verified` atomic finalization for
`gtkb-w0-worker-enablement-plumbing` wrote and published the `-006` VERIFIED
verdict but failed at the durable-commit step with an aggregate-preimage
compensation error. This is the same stranding class as WI-5867 and the
WI-5825-class `recovery_required` / aggregate-preimage failure.

## Stranded state (verified 2026-08-06)

- **Bridge state:** thread latest status = **VERIFIED** at
  `bridge/gtkb-w0-worker-enablement-plumbing-006.md` (published), because the
  `-006` verdict was written via the governed writer.
- **Git state:** `-006` verdict untracked; the seven implementation files remain
  uncommitted; no finalization commit landed. (Predecessor chain `-001`..`-005`
  was committed as `64b43cdd0` + `12ed61c25` before finalization.)
- **Publication:** pending sidecar
  `.gtkb-state/bridge-publication-pending/gtkb-w0-worker-enablement-plumbing-006-29d10f75c49d85a1.json`.
  Finalize error: `BRIDGE_PUBLICATION_REPAIR_REQUIRED: compensation could not
  restore the aggregate preimage; file and claim are retained: bridge
  publication aggregate preimage cannot be restored exactly`.
- **Work-intent claim:** draft claim for the thread held (expired TTL).

## Implementation substance (verified before finalization)

All four live anchors verified present and stable before finalization: goose env
binding (cli_session_handoff.py:29), goose `G` in DEFAULT_HARNESS_IDS
(harness_identity.py:28), mint TTL SoT resolution (registry_control_plane.py:3356),
writer mint TTL pass-through (gtkb_bridge_writer.py:1245). Focused TTL-sizing
suite passed (5 passed). VERIFIED-eligible; blocked only by the broken atomic
finalization (aggregate preimage).

## Required recovery (WI-5825-class)

Reconcile the stranded `-006` file-only VERIFIED and the unrecoverable aggregate
preimage through the designated WI-5825-class poisoned-row / finalization
recovery procedure, then commit the verified implementation paths + verdict in
one atomic transaction.

No dispatcher, TAFE, source, test, Git index, commit, push, release,
deployment, credential, or external-system mutation was performed by this
evidence capture. The stranded `-006` file and its capability row were left
intact for the recovery procedure.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
