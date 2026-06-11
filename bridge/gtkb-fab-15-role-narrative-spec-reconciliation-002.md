NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-15-role-narrative-spec-reconciliation
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-15-role-narrative-spec-reconciliation-001.md

# Loyal Opposition Review - FAB-15 Role Narrative Spec Reconciliation

## Review Scope

Reviewed the operative Prime Builder proposal
`bridge/gtkb-fab-15-role-narrative-spec-reconciliation-001.md` for WI-4427 /
PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory bridge preflights,
owner-decision evidence, project authorization, backlog state, and future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-15 should not absorb the vendor-de-binding narrative sweep; both the proposal and active PAUTH
correctly defer that work to a separate follow-on. This review is limited to the registry posture,
Codex config posture, canonical_terms sync, and startup-spec carve-out.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-15-role-narrative-spec-reconciliation`
  passed with `missing_required_specs=[]` and no advisory omissions.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-15-role-narrative-spec-reconciliation`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB15-REMEDIATION-20260610` confirms the owner selected registry
  restoration, split Codex posture, markdown-glossary SoT with deterministic canonical_terms sync,
  and the startup-relay declared-TTL carve-out.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB15-20260610` for WI-4427, including `kb_canonical_terms_regeneration_with_packet` and
  `formal_spec_amendment_with_packet`.
- `gt backlog list --json --id WI-4427` confirms WI-4427 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Findings

### F1 - Formal artifact approval packet paths are missing

The proposal mutates formal/governed artifacts:

- `canonical_terms` regeneration, described by the PAUTH as `kb_canonical_terms_regeneration_with_packet`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` amendment, described as `formal_spec_amendment_with_packet`.

The current `target_paths` include `groundtruth.db`, but omit `.groundtruth/formal-artifact-approvals/*.json`
or concrete packet paths. Implementation-start authority is path-scoped; Prime Builder cannot safely
create the required packet artifacts unless the revised proposal includes them.

### F2 - Session-wrap wiring target is not concrete

Area 3 says the deterministic canonical_terms sync is "wired into session wrap", but the target set
does not include any session-wrap hook, skill, rule, template, or config surface that performs that
runtime wiring. `config/governance/canonical-terms-sync.toml` may be the intended control file, but the
proposal does not explain how existing session-wrap code will consume it without additional target paths.

The revised proposal must either name the exact wrap/runtime surface being changed, or limit this slice
to adding the script, config, doctor check, and one-time regeneration while deferring wrap integration.

## Required Revision

Submit a REVISED proposal that:

1. Adds concrete formal-artifact approval packet path(s) under `.groundtruth/formal-artifact-approvals/`
   for canonical_terms regeneration and the GOV-SOURCE-OF-TRUTH-FRESHNESS-001 amendment.
2. Names the exact session-wrap integration target path(s), or removes/defer the "wire it into session
   wrap" claim.
3. Keeps the existing owner constraints: no vendor-de-binding narrative sweep, no external Agent Red
   mutation, and no hard deletion of canonical specification rows.

## Verdict

NO-GO until formal packet artifacts and the session-wrap integration surface are concrete.
