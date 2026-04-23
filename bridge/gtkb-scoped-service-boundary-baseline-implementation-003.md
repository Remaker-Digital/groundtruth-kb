REVISED

# GTKB Scoped Service Boundary Baseline Implementation Revision 1

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md`
**Addresses:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-002.md` (NO-GO)

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-012]
target_paths: ["groundtruth.toml", "scripts/gtkb_scoped_client.py", "scripts/check_scoped_service_boundary.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_scoped_client.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_groundtruth_governance_adoption.py"]

## Requested Verdict

GO to implement the narrowed Phase 4 scoped-service baseline below, or NO-GO
with required revisions.

## Change From Revision 0 (-001)

Revision 0 was NO-GO'd in -002 for two blocking findings. This revision
applies scope-reducing fixes for both:

### F1 fix — Consolidate config contract on root `groundtruth.toml`

-001 scoped the new `[scoped_service]` section to
`tools/knowledge-db/groundtruth.toml`, but the live startup consumer
(`scripts/session_self_initialization.py:1095`) reads root `groundtruth.toml`.
That split-brain contract was the F1 blocker.

This revision makes root `groundtruth.toml` the sole authoritative home for
the `[scoped_service]` contract. `tools/knowledge-db/groundtruth.toml` is
removed from `target_paths`. All in-scope consumers (checker,
release-gate, startup) read the root file.

Path expressions in the `[scoped_service]` section are updated to resolve
from the repo root rather than from `tools/knowledge-db/`.

### F2 fix — Drop `dashboard.refresh.request` from the first-slice client contract

-001 claimed a `dashboard.refresh.request` operation without bringing the
live refresh surface (`scripts/gtkb_dashboard/refresh_service.py` +
`scripts/gtkb_dashboard/start_local_dashboard.ps1`) into scope. That
contract-vs-surface mismatch was the F2 blocker.

Per the NO-GO's Option 1, this revision removes `dashboard.refresh.request`
from the client contract and keeps the first slice strictly read-only.
Refresh-request typing is deferred to a later Phase 4 sub-slice that
explicitly includes the refresh surface.

## Claim (narrowed)

The correct first Phase 4 implementation slice is now:

1. define explicit scoped-service configuration in root `groundtruth.toml`
   (single authoritative config path),
2. add an app-scoped GT-KB client with a small typed operation surface
   limited to dashboard summary/history **reads only** (no request-class
   operations in this slice),
3. add a scoped-service boundary checker and release-gate wiring so raw
   combined-authority drift becomes visible early, and
4. switch one current read path in startup/dashboard generation to use the
   new scoped client rather than direct ad hoc config assumptions.

This slice does not implement Deliberation Archive mutation, MemBase
mutation, bridge writes, deployment queues, hosted-service tokens, dashboard
refresh request operations, or overlay promotion.

## Current Evidence (updated)

### Config Authority (F1 resolution)

- Root `groundtruth.toml` is the live active config consumed by
  `scripts/session_self_initialization.py:1095`. Evidence path preserved
  from `-002:43-44`.
- `tools/knowledge-db/groundtruth.toml` is not on the startup read path and
  is not the first-slice consumer. Per `-002` required action, this revision
  chooses root `groundtruth.toml` as the single authority.
- First-slice policy: all `[scoped_service]` authority resides in root
  `groundtruth.toml`. Any future migration of the contract to a different
  file must be a separate bridge proposal that also moves every consumer.

### Dashboard Surface Scope (F2 resolution)

- `scripts/gtkb_dashboard/refresh_service.py:70-75, :115, :150-166` handles
  token-gated `POST /refresh` and is the live refresh control surface.
- `scripts/gtkb_dashboard/start_local_dashboard.ps1:75-80, :122-127` sets
  `GTKB_DASHBOARD_DB`, `GTKB_DASHBOARD_PROJECT_ROOT`, and launches the
  refresh service.
- First-slice policy: those files remain **outside** this slice. No typed
  refresh-request operation is proposed, claimed, or approved by this
  proposal. A later Phase 4 sub-slice will handle refresh-surface typing
  after Phase 3 environment hardening lands.

### Remaining Evidence (carried forward from -001)

- `scripts/release_candidate_gate.py` does not yet run a dedicated
  scoped-service-boundary checker.
- `tests/scripts/test_groundtruth_governance_adoption.py` and
  `tests/scripts/test_session_self_initialization.py` verify config
  artifacts but do not yet assert a scoped-client or service-boundary
  contract.

## Scope (narrowed)

Implement only:

1. A new `[scoped_service]` section in **root `groundtruth.toml`** describing:
   - default subject
   - application identifier
   - project root (resolved from repo root, not `tools/knowledge-db/`)
   - allowed read operations (2 entries, no request-class operations)
   - offline-cache/runtime roots (resolved from repo root)
2. A new `scripts/gtkb_scoped_client.py` module exposing a narrow typed
   client for **read-only** operations:
   - `dashboard.summary.read`
   - `dashboard.history.read`
3. Shared validation inside that client for:
   - subject label
   - project root confinement
   - allowed operation vocabulary
   - source freshness/provenance metadata in responses
4. A new `scripts/check_scoped_service_boundary.py` checker that fails when:
   - scoped-service config is missing required fields in root
     `groundtruth.toml`
   - raw combined-authority DB/root assumptions remain the only boundary
   - app-default config declares mutating or request-class operations not
     approved in this slice
5. Release-gate wiring in `scripts/release_candidate_gate.py` to run the
   checker.
6. A small integration in `scripts/session_self_initialization.py` so one
   dashboard/startup read path exercises the scoped client.
7. Focused tests for the client, checker, release-gate wiring, startup
   integration, and config contract.

Not in this slice (unchanged from -001):

- Deliberation append/upsert
- MemBase mutation
- bridge write/read authority changes
- deployment/release request queues
- hosted service or auth token issuance
- formal artifact mutation through the new client
- dashboard control-plane registry
- overlay storage or promotion behavior
- **dashboard refresh-request operations (explicitly deferred by F2 fix)**

## Proposed Config Contract (revised for F1)

Add an application-local section to **root `groundtruth.toml`**:

```toml
[scoped_service]
default_subject = "application"
application_id = "agent-red"
project_root = "."
allowed_read_operations = [
  "dashboard.summary.read",
  "dashboard.history.read",
]
# Intentionally omitted in this slice:
# allowed_request_operations = [...]  # deferred per F2 fix
runtime_root = "memory"
dashboard_db = "memory/gtkb-dashboard.sqlite"
dashboard_history = "memory/gtkb-dashboard-history.json"
```

Path expressions resolve from the repo root. No `../../` traversal is used
because root `groundtruth.toml` is at the repo root.

## Proposed Client Contract (revised for F2)

Command examples (read-only; no request-class operations in first slice):

```powershell
python scripts/gtkb_scoped_client.py dashboard.summary.read --json
python scripts/gtkb_scoped_client.py dashboard.history.read --json
```

Expected behavior:

- reads return subject/root/source/freshness metadata,
- unsupported, mutating, or request-class operation names fail closed.

## Proposed First-Slice Guard Rules (unchanged from -001)

The guard rules and remaining sections from `-001` (beyond the two fixes
above) carry forward by reference. No other changes from `-001` are proposed
in this revision.

## Review Focus

The blocking findings in `-002` were:

- F1: config split-brain between `tools/knowledge-db/groundtruth.toml` and
  root `groundtruth.toml`. Fixed by choosing root `groundtruth.toml` as the
  sole authority.
- F2: `dashboard.refresh.request` claimed without bringing the refresh
  surface into scope. Fixed by dropping that operation from the first-slice
  client contract (Option 1 from the NO-GO).

Both fixes reduce first-slice scope. A NO-GO on this revision should
identify any of:

- residual config-authority ambiguity,
- read-only operations that still imply request-class authority,
- scope-tightening objections (e.g., preferring Option 2 of F2 — include
  the refresh surface rather than drop the operation).

## Work Item Alignment

`work_item_ids` updated from `GTKB-ISOLATION-004` (planning item) to
`GTKB-ISOLATION-012` (execution item in `memory/work_list.md`), matching the
pattern established by `GTKB-ISOLATION-010` in the Phase 7 thread.

## Non-Blocking Acknowledgement From -002

The proposal's original claim that read-mostly app-local contract-first is
the right first-slice boundary was not disputed by `-002`. The Prior
Deliberations (DELIB-0877, DELIB-0878, DELIB-0879) continue to apply.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877`, `DELIB-0878`, `DELIB-0879` — current GTKB application-
  isolation planning records (cited in `-002`).
- No earlier NO-GOs exist for this thread beyond `-002`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
