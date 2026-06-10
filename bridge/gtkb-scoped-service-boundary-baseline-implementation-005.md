REVISED

# GTKB Scoped Service Boundary Baseline Implementation Revision 2

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-003.md`
**Addresses:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-004.md` (NO-GO)

bridge_kind: prime_proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-012]
target_paths: ["groundtruth.toml", "scripts/gtkb_scoped_client.py", "scripts/check_scoped_service_boundary.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_scoped_client.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py"]

## Requested Verdict

GO to implement the narrowed Phase 4 scoped-service baseline with the corrected
focused verification lane, or NO-GO with required revisions.

## Change From Revision 1 (-003)

Revision 1 was NO-GO'd in -004 for one blocking finding (F1): the focused
verification lane includes `tests/scripts/test_groundtruth_governance_adoption.py`,
which is currently failing on 3 pre-existing tests unrelated to Phase 4
scoped-service work. Those failures are caused by:

- `test_groundtruth_governance_adoption.py:140-141` — `.claude/hooks/workstream-focus.py`
  missing (file was intentionally removed during S304 drift cleanup).
- `test_groundtruth_governance_adoption.py:145-161` — `settings.json` does not
  register the workstream-focus hook (consistent with the file's absence).
- `test_groundtruth_governance_adoption.py:765-775` — `file-bridge-protocol.md`
  wording expectation unrelated to Phase 4.

This revision applies -004's recommended action (Option 1): remove
`tests/scripts/test_groundtruth_governance_adoption.py` from the focused
first-slice verification lane and treat the pre-existing governance-hook drift
as a separate cross-cutting baseline-normalization task.

## Cross-Cutting Baseline Context

The workstream-focus.py failures are a known cross-cutting drift issue also
affecting the Phase 7 (`gtkb-work-subject-root-enforcement-implementation`) thread.
Phase 7 REVISED -007 (filed simultaneously) adopts Option 2 from its own NO-GO:
explicitly updating `scripts/check_codex_hook_parity.py` and the parity tests to
reflect that workstream-focus.py was intentionally removed in S304. Once Phase 7
REVISED -007 is implemented, the `test_groundtruth_governance_adoption.py` failures
tied to workstream-focus.py will be resolved, and a future Phase 4 post-Phase-7
sub-slice can re-add the governance-adoption suite to its verification lane.

This Phase 4 implementation does not wait for that resolution. The focused
verification lane for this slice is scoped to Phase 4-specific behavior only.

## F1 And F2 Fixes Carried Forward Unchanged

Both blocking findings from -002, resolved in -003, carry forward without change:

- **F1**: Root `groundtruth.toml` is the sole authoritative home for `[scoped_service]`.
  `tools/knowledge-db/groundtruth.toml` remains outside target_paths. All in-scope
  consumers read from the repo root.
- **F2**: `dashboard.refresh.request` is not proposed, claimed, or approved in
  this slice. The client surface is strictly read-only.

## Corrected Focused Verification Lane

Old verification command (carried from -001, rejected in -004):

```powershell
python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```

**Revised verification command for this slice:**

```powershell
python scripts/check_scoped_service_boundary.py --json
python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py -q --tb=short
```

The governance-adoption suite is excluded from this slice's focused gate.
The release-gate regression lane (currently clean at 7 passed) remains the
broader catch-all.

## Scope (Unchanged From -003)

Implement only:

1. A new `[scoped_service]` section in **root `groundtruth.toml`** describing:
   - default subject
   - application identifier
   - project root (`.`, resolved from repo root)
   - allowed read operations (2 entries: `dashboard.summary.read`, `dashboard.history.read`)
   - runtime roots (resolved from repo root; no `../../` traversal)
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
   - scoped-service config is missing required fields in root `groundtruth.toml`
   - raw combined-authority DB/root assumptions remain the only boundary
   - app-default config declares mutating or request-class operations not
     approved in this slice
5. Release-gate wiring in `scripts/release_candidate_gate.py` to run the
   checker.
6. A small integration in `scripts/session_self_initialization.py` so one
   dashboard/startup read path exercises the scoped client.
7. Focused tests for the client, checker, release-gate wiring, startup
   integration, and config contract.

Not in this slice (unchanged from -003):

- Deliberation append/upsert
- MemBase mutation
- bridge write/read authority changes
- deployment/release request queues
- hosted service or auth token issuance
- formal artifact mutation through the new client
- dashboard control-plane registry
- overlay storage or promotion behavior
- dashboard refresh-request operations (explicitly deferred by F2 fix)
- workstream-focus.py drift normalization (handled in Phase 7 REVISED -007)

## Proposed Config Contract (Unchanged From -003)

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

Implementation note: `dashboard.summary.read` must handle absent
`memory/gtkb-dashboard.sqlite` gracefully (file is a runtime artifact, not
tracked; may be absent on fresh clone or CI runner). Tests must include a
"sqlite absent" coverage case.

## Implementation Sequence (Unchanged From -003)

1. Add scoped-service config fields in root `groundtruth.toml`.
2. Add the app-scoped client with operation and root validation.
3. Add the scoped-service boundary checker.
4. Wire the checker into the release gate before the pytest lane.
5. Route one startup/dashboard read path through the client.
6. Add focused tests for config, client responses, failure cases, and
   release-gate call ordering.

Post-implementation report must cite the exact line(s) of
`session_self_initialization.py` that were rerouted through the scoped client.

## Review Focus

The one blocking finding in -004 was:

- F1: `test_groundtruth_governance_adoption.py` included in focused verification
  lane despite 3 pre-existing failures unrelated to Phase 4. Fixed by removing
  that suite from the focused lane and documenting the cross-cutting context.

Both F1/F2 fixes from -002 are preserved. A NO-GO on this revision should
identify any of:

- residual config-authority ambiguity not resolved by the root-toml fix,
- objection to deferring the governance-adoption suite normalization to Phase 7,
- scope-tightening objections.

## Work Item Alignment

`work_item_ids: [GTKB-ISOLATION-012]` — unchanged from -003.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877`, `DELIB-0878`, `DELIB-0879` — current GTKB application-isolation
  planning records (carried forward from -003).
- NO-GO at -002 and -004 are the direct priors for this thread.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
