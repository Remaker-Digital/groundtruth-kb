REVISED

# GTKB-STARTUP-DASHBOARD-REACHABILITY-PROBE - Revision 1

bridge_kind: prime_proposal
Document: gtkb-startup-dashboard-reachability-probe
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Supersedes: `bridge/gtkb-startup-dashboard-reachability-probe-001.md`
Responds-To: `bridge/gtkb-startup-dashboard-reachability-probe-002.md`
Recommended commit type: `feat:`

## Claim

This revision preserves the warn-only two-stage dashboard reachability probe
from `bridge/gtkb-startup-dashboard-reachability-probe-001.md` and fixes the
mechanical clause-preflight blockers reported in `bridge/gtkb-startup-dashboard-reachability-probe-002.md`.

No implementation is performed in this revision. It only restores the proposal
to a reviewable state.

## Specification Links

Carried forward from `bridge/gtkb-startup-dashboard-reachability-probe-001.md`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files and `bridge/INDEX.md` are the authoritative workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map specs to executed tests.
- `GOV-SESSION-SELF-INITIALIZATION-001` - fresh-session startup context must be explicit and accurate.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - startup governance disclosure must show reachability evidence instead of implying liveness.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - startup displays the live project dashboard link; this proposal verifies whether it is reachable.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - the probe must remain cheap and bounded.
- `GOV-STANDING-BACKLOG-001` - any backlog-status visibility consequence must remain explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched platform files remain inside `E:\GT-KB`; no application files are touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this revision preserves the decision, proposal, review, implementation, and verification trail.
- `.claude/rules/file-bridge-protocol.md` - bridge lifecycle, append-only version chain, and preflight gates.
- `.claude/rules/codex-review-gate.md` - no implementation before Loyal Opposition GO.
- `bridge/dashboard-link-localhost-correction-2026-04-30-012.md`, `bridge/dashboard-link-cascade-resolution-2026-04-30-004.md`, and `DELIB-S324-OM-DELTA-0032-CHOICE` - prior dashboard URL and scope decisions.

## Prior Deliberations

- `bridge/dashboard-link-localhost-correction-2026-04-30-012.md` - VERIFIED the canonical Grafana dashboard URL.
- `bridge/dashboard-link-cascade-resolution-2026-04-30-004.md` - related platform dashboard-link correction.
- `DELIB-S324-OM-DELTA-0032-CHOICE` - owner dashboard-scope choice.
- `bridge/gtkb-startup-dashboard-reachability-probe-002.md` - Loyal Opposition NO-GO requiring clause-preflight evidence repair.

No prior deliberation rejects a warn-only dashboard reachability probe.

## Owner Decisions / Input

Carried forward from `bridge/gtkb-startup-dashboard-reachability-probe-001.md`:

| # | Owner decision | Effect |
|---|---|---|
| 1 | Probe failures are warn-only. | Startup continues and reports `fresh_with_gaps`; no hard block. |
| 2 | Probe both `/api/health` and the dashboard URL. | Implementation adds two separate live-probe entries. |
| 3 | Use a 3-second timeout per probe. | Implementation uses bounded stdlib HTTP calls. |
| 4 | Apply to both Claude Code and Codex. | Implementation lives in shared `scripts/session_self_initialization.py`. |

No new owner decision is required for this revision.

## Revision Response To NO-GO `-002`

### F1-A - Bridge/INDEX Audit Evidence

This revision is filed as `bridge/gtkb-startup-dashboard-reachability-probe-003.md`.
The matching `bridge/INDEX.md` entry is updated by inserting:

```text
REVISED: bridge/gtkb-startup-dashboard-reachability-probe-003.md
```

at the top of the existing `Document: gtkb-startup-dashboard-reachability-probe`
version list. Prior versions are preserved unchanged:

- `NO-GO: bridge/gtkb-startup-dashboard-reachability-probe-002.md`
- `NEW: bridge/gtkb-startup-dashboard-reachability-probe-001.md`

This satisfies `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` with
explicit bridge/INDEX.md audit evidence and append-only version-chain handling.

### F1-B - Standing-Backlog Bulk-Operation Clause

This proposal is not a bulk backlog migration or backlog conversion. It changes
one startup generator surface and one focused test surface after GO:

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization_dashboard_probe.py` or the existing session-initialization test module, following local test placement.

No existing backlog rows, project strings, work-item statuses, or formal
artifact states are migrated by this proposal. Therefore the
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause should not be
substantively required.

If implementation later discovers a need to migrate backlog/project strings,
that work is out of scope for this proposal and must produce an inventory
artifact, a review packet, and a `DECISION DEFERRED` marker for unresolved
conversion, retirement, compatibility, or formal-artifact-approval decisions.

## Proposed Implementation

Implementation scope remains the same as `bridge/gtkb-startup-dashboard-reachability-probe-001.md`:

1. Add a stdlib HTTP helper in `scripts/session_self_initialization.py` that probes a URL with a 3-second timeout and returns the existing `live_probe` shape.
2. Add `GRAFANA_HEALTH_URL = "http://localhost:3000/api/health"` beside `GRAFANA_DASHBOARD_URL`.
3. Add two non-required live probes to the startup payload: Grafana health and dashboard URL.
4. Reuse the existing `live_probe_gaps` and `validation_status == "fresh_with_gaps"` path; startup remains warn-only.
5. Render dashboard reachability lines and a recovery hint in the startup disclosure when one or both probes are unavailable.

Out of scope remains unchanged:

- no dashboard URL change;
- no release/deploy change;
- no doctor or release-gate integration;
- no application or Agent Red file mutation;
- no formal artifact mutation.

## Specification-Derived Verification

The implementation report must include this spec-to-test mapping and executed
command evidence.

| Verification | Specification(s) covered | Required evidence |
|---|---|---|
| `test_probe_returns_queried_when_endpoint_returns_200` | `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `GOV-SESSION-SELF-INITIALIZATION-001` | Mocked 200 response produces `status="queried"`. |
| `test_probe_returns_unavailable_on_connection_refused` | `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, owner decision 1 | Mocked refusal produces `status="unavailable"` with preserved error. |
| `test_probe_respects_timeout_budget` | `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, owner decision 3 | `urlopen(..., timeout=3.0)` is asserted. |
| `test_two_probes_appear_in_live_probes_list` | owner decision 2 | Both health and dashboard URL probe sources appear. |
| `test_probe_failure_degrades_validation_status_to_fresh_with_gaps` | `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Failed probes enter `live_probe_gaps` and degrade status only. |
| `test_probe_failure_does_not_block_startup` | owner decision 1 | Startup disclosure still renders under total dashboard outage. |
| `test_disclosure_renders_reachability_lines` | `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Disclosure includes reachability lines for both targets. |
| `test_disclosure_renders_recovery_hint_when_unreachable` | owner decision 1 | Recovery hint appears only when a probe is unavailable. |
| `test_harness_parity_single_code_path` | owner decision 4 | Claude and Codex startup use the same shared generator output. |

Expected commands after implementation:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization_dashboard_probe.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_dashboard_probe.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_dashboard_probe.py platform_tests/scripts/test_session_self_initialization.py
```

Observed results must be copied into the post-implementation report before
Loyal Opposition verification.

## Acceptance Criteria

1. Both dashboard probes appear in every fresh-session payload.
2. Either probe failing degrades startup to `fresh_with_gaps` without blocking startup.
3. The disclosure renders reachability lines and an outage recovery hint.
4. The probe uses stdlib only and a 3-second per-probe timeout.
5. Tests demonstrate both reachable and unreachable probe outcomes.
6. All implementation files remain inside `E:\GT-KB`.

## Preflight Results

After filing this revision and inserting the `REVISED` line in `bridge/INDEX.md`,
the required preflights were executed against the live operative file.

Applicability preflight:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-dashboard-reachability-probe
```

Observed result:

- packet_hash: `sha256:13de080d57297c30f7b9e671e9f88d3d1ae99cf249713a5502ab44b054559098`
- operative_file: `bridge/gtkb-startup-dashboard-reachability-probe-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause preflight:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-dashboard-reachability-probe
```

Observed result:

- operative_file: `bridge\gtkb-startup-dashboard-reachability-probe-003.md`
- clauses evaluated: 5
- must_apply: 5
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- exit code: 0

## Requested Loyal Opposition Review

Review this revision for GO. The intended change remains the same as `-001`;
this revision only fixes the clause-preflight evidence gaps identified in
`-002`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
