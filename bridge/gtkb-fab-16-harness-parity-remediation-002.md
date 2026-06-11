GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-16-harness-parity-remediation
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-16-harness-parity-remediation-001.md

# Loyal Opposition Review - FAB-16 Harness Parity Remediation

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-16-harness-parity-remediation-001.md`
for WI-4428 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, harness-parity
workflow inputs, and future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-16 couples to FAB-15's registry topology restore, but it does not perform role/status
transactions itself. The Antigravity adapter regeneration and Goose UI-client classification can be
implemented without changing durable role assignments. Any implementation evidence that relies on the
final Claude/Codex role topology should state whether FAB-15 has landed or should treat the role topology
as an external precondition.

## Harness-Parity Evidence

Following the harness-parity review workflow, this review checked the harness identity file and the
capability registry, then ran:

- `python scripts/check_harness_parity.py --harness antigravity --json`

Current result is `overall_status="FAIL"` with 22 `STALE`, 14 `MISSING`, and 1 `PASS`, matching the
proposal's HYG-061 evidence. This confirms the remediation target rather than introducing a blocker.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-16-harness-parity-remediation`
  passed with `missing_required_specs=[]` and no advisory omissions.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-16-harness-parity-remediation`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB16-REMEDIATION-20260610` confirms the owner classified Goose as the
  desktop UI client for OpenRouter interactive sessions, not an independent dispatch harness.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB16-20260610` for WI-4428, allowing registry/checker/adapter/doctor/test changes and
  forbidding Goose headless-harness buildout or Goose retirement.
- `gt backlog list --json --id WI-4428` confirms WI-4428 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Implementation Constraints

- Do not perform harness role/status transactions in FAB-16; FAB-15 owns topology restoration.
- Do not build a Goose headless wrapper and do not retire Goose. Record it as a UI client for
  OpenRouter interactive sessions.
- Do not mutate the external Agent Red repository.
- Verification must include Antigravity parity returning 0 stale and 0 missing adapters after regen,
  plus a degraded-projection test proving the checker reports projection failure rather than silently
  falling back to `("claude", "codex")`.

## Verdict

GO for implementation within the proposal's scoped paths and constraints above.
