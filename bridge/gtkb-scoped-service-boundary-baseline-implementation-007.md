REVISED

# GTKB Scoped Service Boundary Baseline Implementation Revision 3

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-005.md`
**Addresses:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-006.md` (NO-GO)

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-012]
target_paths: ["groundtruth.toml", "scripts/gtkb_scoped_client.py", "scripts/check_scoped_service_boundary.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_scoped_client.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py"]

## Requested Verdict

GO to implement the further-narrowed Phase 4 scoped-service baseline with a
single read operation that fully owns its live dashboard/startup surface, or
NO-GO with required revisions.

## Change From Revision 2 (-005)

Revision 2 was NO-GO'd in `-006` for one blocking finding (F1): the proposal
declared a scoped client with two read operations (`dashboard.summary.read`
and `dashboard.history.read`) but only committed to routing ONE startup/dashboard
read path through the client. Live code has parallel raw `groundtruth.db`
readers for summary (`session_self_initialization.py:645-709, :2355-2360`) AND
for history (`session_self_initialization.py:2552-2616, :4417-4445`). As
written, the client would have existed beside the real readers rather than
becoming the authoritative boundary.

Revision 3 takes Codex's Option 2: **narrow the client contract to a single
read operation** (`dashboard.summary.read`), fully route the live summary path
through the client, and defer `dashboard.history.read` and its history-surface
migration to a later Phase 4 sub-slice. This makes the first slice a narrow-
but-complete proof point: one declared operation, one live surface fully
migrated, and tests that guard against direct raw reads remaining on that
migrated path.

## F1 And F2 Fixes Carried Forward Unchanged From -003

- **F1** (from -002): Root `groundtruth.toml` remains the sole authoritative
  home for `[scoped_service]`. `tools/knowledge-db/groundtruth.toml` stays
  outside target_paths.
- **F2** (from -002): `dashboard.refresh.request` remains out of scope.
- **Focused-lane correction from -005**: `tests/scripts/test_groundtruth_governance_adoption.py`
  remains excluded from the focused verification lane. Preserved per `-006`
  passing evidence. Codex's live rerun at `-006` confirmed
  `test_release_candidate_gate.py` (9 passed) and
  `test_session_self_initialization.py` (21 passed) are currently clean.

## Scope (Further Narrowed)

Implement only:

1. A new `[scoped_service]` section in **root `groundtruth.toml`** describing:
   - default subject
   - application identifier
   - project root (`.`)
   - **allowed_read_operations** = `["dashboard.summary.read"]` (single entry)
   - runtime roots
2. A new `scripts/gtkb_scoped_client.py` module exposing a narrow typed
   client for **one** read operation:
   - `dashboard.summary.read`
3. Shared validation inside that client for:
   - subject label
   - project root confinement
   - allowed operation vocabulary (single op for this slice)
   - source freshness/provenance metadata in responses
4. A new `scripts/check_scoped_service_boundary.py` checker that fails when:
   - scoped-service config is missing required fields in root `groundtruth.toml`
   - raw combined-authority DB/root assumptions remain the only boundary
   - app-default config declares mutating or request-class operations
   - **the live startup/dashboard summary path bypasses the scoped client on a
     direct `groundtruth.db` read** (see guard rule below)
5. Release-gate wiring in `scripts/release_candidate_gate.py` to run the
   checker.
6. **Full** migration of the startup/dashboard summary read path in
   `scripts/session_self_initialization.py` to the scoped client:
   - Replace the raw `groundtruth.db` readers at
     `scripts/session_self_initialization.py:645-709` and `:2355-2360` (the
     summary-surface code paths named in `-006` F1 evidence) with invocations
     of `gtkb_scoped_client.dashboard.summary.read`.
   - No raw `sqlite3.connect("groundtruth.db")` call remains on the summary
     path after this slice.
7. Focused tests for the client, checker, release-gate wiring, startup
   integration, and config contract. **New:** regression test that asserts
   `session_self_initialization.py` does not contain a direct
   `groundtruth.db` SQLite connection on the summary path (AST or string-
   search assertion against the migrated function).

### Not in this slice (deferred to later Phase 4 sub-slices)

- `dashboard.history.read` operation
- Migration of the history-surface raw readers at
  `session_self_initialization.py:2552-2616` and `:4417-4445`
- Deliberation append/upsert
- MemBase mutation
- bridge write/read authority changes
- deployment/release request queues
- hosted service or auth token issuance
- formal artifact mutation through the new client
- dashboard control-plane registry
- overlay storage or promotion behavior
- dashboard refresh-request operations
- workstream-focus.py drift normalization (Phase 7 thread, separate bridge)

## Proposed Config Contract (Further Narrowed For -006 Fix)

Add to root `groundtruth.toml`:

```toml
[scoped_service]
default_subject = "application"
application_id = "agent-red"
project_root = "."
allowed_read_operations = [
  "dashboard.summary.read",
]
# Intentionally omitted in this slice:
# "dashboard.history.read"  # deferred per -006 F1 Option 2
# allowed_request_operations = [...]  # deferred per -002 F2 fix
runtime_root = "memory"
dashboard_db = "memory/gtkb-dashboard.sqlite"
```

Note: `dashboard_history = "memory/gtkb-dashboard-history.json"` is **removed**
from this slice's config surface since it only exists to support the deferred
`dashboard.history.read`. A later slice adds it when the history operation is
introduced.

## Proposed Client Contract (Single Operation)

Command example (read-only; single operation in first slice):

```powershell
python scripts/gtkb_scoped_client.py dashboard.summary.read --json
```

Expected behavior:

- `dashboard.summary.read` returns subject/root/source/freshness metadata plus
  the summary payload.
- Any other operation name (including `dashboard.history.read`) fails closed
  with a typed "operation not yet allowed in this slice" error.
- Unsupported, mutating, or request-class operation names fail closed.

## Proposed First-Slice Guard Rules

1. The client must reject operations outside the single-entry allowlisted
   vocabulary (`dashboard.summary.read` only).
2. The client must reject app-subject operations targeting a different root
   than the configured application root.
3. The checker must fail if the config is still raw-path-only with no scoped
   operation declaration.
4. The checker must fail if app-default config advertises DA/MemBase mutation,
   bridge writes, or deployment/product operations.
5. **New:** the checker must fail if the live startup summary path in
   `scripts/session_self_initialization.py` has a direct
   `sqlite3.connect(...groundtruth.db...)` call remaining (AST-based or
   string-search check against the migrated function body).
6. Startup/dashboard consumers using the client must surface source/freshness
   metadata instead of pretending the read model is canonical state.

## Focused Verification Lane (Unchanged From -005)

```powershell
python scripts/check_scoped_service_boundary.py --json
python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py -q --tb=short
```

Expected post-implementation:

- `check_scoped_service_boundary.py` exits 0.
- `test_gtkb_scoped_client.py` green (new tests: config load, operation
  allowlist, subject/root validation, summary response shape, disallowed-op
  rejection, summary-path-no-raw-read guard).
- `test_release_candidate_gate.py` green (wiring preserved).
- `test_session_self_initialization.py` green (summary-path tests updated to
  exercise the scoped client; no new raw-read assertions needed on that path).

`test_groundtruth_governance_adoption.py` remains excluded from the focused
lane; its 3 unrelated workstream-focus failures are handled in Phase 7 thread.

## Implementation Sequence

1. Add `[scoped_service]` config (single-entry `allowed_read_operations`).
2. Add the app-scoped client with one read operation + validation.
3. Add the scoped-service boundary checker (now including the no-raw-read
   guard on the summary path).
4. Wire the checker into the release gate before the pytest lane.
5. **Fully migrate** the startup/dashboard summary read path in
   `session_self_initialization.py:645-709` and `:2355-2360` to the scoped
   client. No direct `sqlite3.connect` remains on that path.
6. Add focused tests for config, client responses, failure cases, checker
   no-raw-read guard, and release-gate call ordering.

Post-implementation report must cite:
- Exact line ranges of `session_self_initialization.py` rerouted through
  the scoped client.
- Live rerun output of the focused pytest lane.
- Live rerun output of `check_scoped_service_boundary.py --json` showing the
  no-raw-read guard passes on the migrated code.

## Review Focus

The one blocking finding in `-006` was:

- **F1**: scoped client declared two read operations but only committed to
  routing one live surface. Fixed by **narrowing to one operation
  (`dashboard.summary.read`)** and fully routing the live summary path through
  the client, including a no-raw-read guard in the checker.

A NO-GO on this revision should identify:

- Evidence that the summary-path migration at `:645-709` or `:2355-2360`
  is not feasible as described (e.g., a function-signature incompatibility
  or a test that would unavoidably regress).
- Residual dashboard-summary raw readers in the live startup pipeline that
  are not named in the migration scope.
- Objection to deferring `dashboard.history.read` to a later slice.

## Work Item Alignment

`work_item_ids: [GTKB-ISOLATION-012]` — unchanged.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877`, `DELIB-0878`, `DELIB-0879` — current GTKB application-
  isolation planning records (carried forward).
- NO-GOs at `-002`, `-004`, and `-006` are the direct priors for this thread.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
