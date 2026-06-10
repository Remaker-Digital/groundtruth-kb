NEW

# GTKB Scoped Service Boundary Baseline Implementation Proposal

bridge_kind: prime_proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-004]
target_paths: ["tools/knowledge-db/groundtruth.toml", "scripts/gtkb_scoped_client.py", "scripts/check_scoped_service_boundary.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_scoped_client.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_groundtruth_governance_adoption.py"]

## Requested Verdict

GO to implement the narrow Phase 4 scoped-service baseline below, or NO-GO with
required revisions.

## Parent GO Inputs

This proposal is the first concrete implementation slice after the accepted
Phase 4 planning review:

- `bridge/gtkb-isolation-004-service-boundary-plan-review-002.md`

The Phase 4 plan accepted the scoped-service boundary design and required later
concrete implementation proposals before behavior changes.

## Claim

The correct first Phase 4 implementation slice is read-mostly, app-local, and
contract-first:

1. define explicit scoped-service configuration inside the application-local
   GT-KB config instead of leaving all authority implied by raw DB/root paths,
2. add an app-scoped GT-KB client with a small typed operation surface limited
   to dashboard summary/history reads and refresh requests, plus the shared
   subject/root validation that later mutating operations must reuse,
3. add a scoped-service boundary checker and release-gate wiring so raw
   combined-authority drift becomes visible early, and
4. switch one current read path in startup/dashboard generation to use the new
   scoped client rather than direct ad hoc config assumptions.

This slice should not yet implement Deliberation Archive mutation, MemBase
mutation, bridge writes, deployment queues, hosted-service tokens, or overlay
promotion.

## Current Evidence

### Existing Raw-Authority Shape

- `tools/knowledge-db/groundtruth.toml` currently points directly at
  `../../groundtruth.db`, `../..` as project root, and
  `../../.groundtruth-chroma` without any explicit scoped-service contract.
- `groundtruth.toml` still identifies a local `groundtruth.db`, which is valid
  for app-local governed state but does not by itself express which operations
  are allowed for ordinary application-subject sessions.

### Existing Dashboard And Startup Read Paths

- `scripts/gtkb_dashboard/start_local_dashboard.ps1` currently sets direct
  dashboard DB and project-root environment variables, then runs local refresh
  scripts.
- `scripts/session_self_initialization.py` currently reads app-local
  `groundtruth.db` and dashboard runtime artifacts directly when generating the
  startup/dashboard payload.

### Existing Enforcement Gap

- `scripts/release_candidate_gate.py` does not yet run a dedicated scoped
  service-boundary checker.
- `tests/scripts/test_groundtruth_governance_adoption.py` and
  `tests/scripts/test_session_self_initialization.py` currently verify
  dashboard/config artifacts, but they do not yet assert an explicit scoped
  client or service-boundary contract.

### Why This Slice Is First

- Phase 4 says ordinary application sessions should use typed scoped operations
  instead of raw parent-root, raw SQLite, or product-admin authority.
- The safest first proof point is read-only dashboard evidence, because the
  Phase 4 plan explicitly allows dashboard summary/action/history reads before
  mutation services are added.
- Phase 3 environment-boundary work remains necessary, but it does not by
  itself create typed scoped operations. This slice uses app-local contracts
  and release-gate checks without waiting for a hosted GT-KB service.

## Scope

Implement only:

1. A new scoped-service section in `tools/knowledge-db/groundtruth.toml`
   describing:
   - default subject
   - application identifier
   - project root
   - allowed read operations
   - refresh-request operation name
   - offline-cache/runtime roots
2. A new `scripts/gtkb_scoped_client.py` module that exposes a narrow typed
   client for:
   - `dashboard.summary.read`
   - `dashboard.history.read`
   - `dashboard.refresh.request`
3. Shared validation inside that client for:
   - subject label
   - project root confinement
   - allowed operation vocabulary
   - source freshness/provenance metadata in responses
4. A new `scripts/check_scoped_service_boundary.py` checker that fails when:
   - scoped-service config is missing required fields
   - raw combined-authority DB/root assumptions remain the only boundary
   - app-default config declares mutating operations not approved in this slice
5. Release-gate wiring in `scripts/release_candidate_gate.py`.
6. A small integration in `scripts/session_self_initialization.py` so one
   dashboard/startup read path exercises the scoped client.
7. Focused tests for the client, checker, release-gate wiring, startup
   integration, and config contract.

Do not implement in this slice:

- Deliberation append/upsert,
- MemBase mutation,
- bridge write/read authority changes,
- deployment/release request queues,
- hosted service or auth token issuance,
- formal artifact mutation through the new client,
- dashboard control-plane registry,
- overlay storage or promotion behavior.

## Proposed Config Contract

Add an application-local section to `tools/knowledge-db/groundtruth.toml`
similar to:

```toml
[scoped_service]
default_subject = "application"
application_id = "agent-red"
project_root = "../.."
allowed_read_operations = [
  "dashboard.summary.read",
  "dashboard.history.read",
]
allowed_request_operations = [
  "dashboard.refresh.request",
]
runtime_root = "../../memory"
dashboard_db = "../../memory/gtkb-dashboard.sqlite"
dashboard_history = "../../memory/gtkb-dashboard-history.json"
```

This slice keeps the existing app-local DB path but makes the allowed operation
surface explicit and testable.

## Proposed Client Contract

Command examples:

```powershell
python scripts/gtkb_scoped_client.py dashboard.summary.read --json
python scripts/gtkb_scoped_client.py dashboard.history.read --json
python scripts/gtkb_scoped_client.py dashboard.refresh.request --json
```

Expected behavior:

- reads return subject/root/source/freshness metadata,
- refresh request returns a typed request acknowledgment and uses only the
  allowlisted local refresh path,
- unsupported or mutating operation names fail closed.

## Proposed First-Slice Guard Rules

1. The client must reject operations outside the allowlisted vocabulary.
2. The client must reject app-subject operations that try to target a different
   root than the configured application root.
3. The checker must fail if the config is still raw-path-only with no scoped
   operation declaration.
4. The checker must fail if app-default config advertises DA/MemBase mutation,
   bridge writes, or deployment/product operations in this first slice.
5. Startup/dashboard consumers using the client must surface source/freshness
   metadata instead of pretending the read model is canonical state.

## Proposed File Touchpoints

Primary code:

- `tools/knowledge-db/groundtruth.toml`
- `scripts/gtkb_scoped_client.py`
- `scripts/check_scoped_service_boundary.py`
- `scripts/release_candidate_gate.py`
- `scripts/session_self_initialization.py`

Tests:

- `tests/scripts/test_gtkb_scoped_client.py`
- `tests/scripts/test_release_candidate_gate.py`
- `tests/scripts/test_session_self_initialization.py`
- `tests/scripts/test_groundtruth_governance_adoption.py`

## Implementation Sequence

1. Add scoped-service config fields in `tools/knowledge-db/groundtruth.toml`.
2. Add the app-scoped client with operation and root validation.
3. Add the scoped-service boundary checker.
4. Wire the checker into the release gate before the pytest lane.
5. Route one startup/dashboard read path through the client.
6. Add focused tests for config, client responses, failure cases, and
   release-gate call ordering.

## Verification Commands

Required focused checks:

```powershell
python scripts/check_scoped_service_boundary.py --json
python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```

Recommended broader check after focused green:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

## Review Questions

1. Is the first Phase 4 slice narrow enough if it is limited to explicit
   scoped-service config, a read-only app-scoped client, and release-gate
   visibility?
2. Is switching one startup/dashboard read path to the new client the right
   first proof point, or should the client remain unintegrated until a later
   slice?
3. Is it acceptable to keep DA/MemBase mutation, bridge operations, and
   deployment requests out of this slice so the contract can stabilize around
   read-only operations first?

## Non-Scope Reminder

This proposal does not request DA/MemBase mutation APIs, bridge writes,
deployment queues, hosted-service credentials, dashboard control-plane
operations, overlay behavior, or migration work. Those remain later slices.
