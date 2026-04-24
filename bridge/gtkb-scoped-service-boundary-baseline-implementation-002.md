NO-GO

# GTKB Scoped Service Boundary Baseline Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md`

## Verdict

NO-GO on the proposal as written.

The intended first-slice boundary is reasonable: a read-only scoped client plus
explicit allowed operations is the right place to start Phase 4. The current
proposal misses two live integration surfaces that make the slice internally
inconsistent: it defines the contract in `tools/knowledge-db/groundtruth.toml`
even though the live startup path reads root `groundtruth.toml`, and it claims
`dashboard.refresh.request` in the client contract without bringing the actual
dashboard refresh surface into scope.

## Prior Deliberations

- `DELIB-0877`, `DELIB-0878`, and `DELIB-0879` are the current GTKB
  application-isolation planning records for this work.
- No exact prior deliberation for this specific baseline implementation thread
  was surfaced beyond that planning sequence.

## Blocking Findings

### F1 - The proposal creates a split-brain config contract

Severity: High

Evidence:

- The proposal scopes the new config contract to
  `tools/knowledge-db/groundtruth.toml` and shows the new `[scoped_service]`
  section only there:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md:88-114`
  and `:127-149`.
- The proposal's target paths do not include root `groundtruth.toml`:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md:8`.
- The live startup path currently reads root `groundtruth.toml`:
  `scripts/session_self_initialization.py:1095`.
- Root `groundtruth.toml` is a real active config surface in this repo:
  `groundtruth.toml:1-10`.

Risk/impact:

As written, the scoped-service contract would live in one config file while an
actual consumer named in the proposal still reads another. That makes the first
slice ambiguous at the exact point where it is supposed to reduce ambiguity.

Required action:

Revise the proposal so the first slice chooses one authoritative config path
for the scoped-service contract and brings every in-scope consumer onto that
same path. If root `groundtruth.toml` remains authoritative for startup, it
must be part of the proposal. If a different config becomes authoritative, the
proposal must explicitly move the startup consumer there.

### F2 - `dashboard.refresh.request` is proposed without the live refresh surface

Severity: Medium

Evidence:

- The proposal's client contract includes `dashboard.refresh.request`:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md:96-100`,
  `:141-146`, and `:157-166`.
- The target paths do not include
  `scripts/gtkb_dashboard/refresh_service.py` or
  `scripts/gtkb_dashboard/start_local_dashboard.ps1`:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md:8`.
- The live dashboard startup path sets `GTKB_DASHBOARD_DB`,
  `GTKB_DASHBOARD_PROJECT_ROOT`, and launches `refresh_service.py`:
  `scripts/gtkb_dashboard/start_local_dashboard.ps1:75-80` and `:122-127`.
- The live refresh surface reads those env vars and handles token-gated
  `POST /refresh` directly:
  `scripts/gtkb_dashboard/refresh_service.py:70-75`, `:115`, and `:150-166`.

Risk/impact:

The proposal claims a typed refresh-request operation, but the actual refresh
surface that exists today would remain outside the slice. That would leave the
first implementation with a contract that is not the real control surface.

Required action:

Revise the proposal so the first slice either:

1. removes `dashboard.refresh.request` and stays strictly read-only, or
2. explicitly brings the live refresh surface into scope and explains how the
   new typed contract will govern that path.

## Owner Decision Needed

None for this NO-GO.
