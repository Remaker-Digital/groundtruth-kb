NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-11-regression-signal-revival
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-11-regression-signal-revival-001.md

# Loyal Opposition Review - FAB-11 Regression-Signal Revival

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-11-regression-signal-revival-001.md`
for WI-4423 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-11 is internally sequenced and should not be split casually: corpus repair must precede
sweep revival, and retention/VACUUM depends on the owner-classified telemetry disposition.
That sequencing is sound, but the proposal must be aligned to the latest owner authority
before implementation starts.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-11-regression-signal-revival`
  passed with `missing_required_specs=[]` and no advisory omissions.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-11-regression-signal-revival`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB11-REMEDIATION-20260610` returns the earlier v1 decision set.
- `gt deliberations get DELIB-FAB11-REMEDIATION-20260610B` returns a superseding owner decision
  that explicitly replaces two FAB-11 decisions.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB11-20260610` version 2, keyed to `DELIB-FAB11-REMEDIATION-20260610B`, and forbidding
  `off_root_telemetry_archive`.
- `gt backlog list --json --id WI-4423` confirms WI-4423 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Findings

### F1 - Proposal cites superseded owner authority

The proposal cites and implements `DELIB-FAB11-REMEDIATION-20260610`. The active project
authorization has since been re-keyed to `DELIB-FAB11-REMEDIATION-20260610B`.

The superseding decision record changes two load-bearing implementation choices:

- HYG-030 changes from a partial deterministic recorder into GOV-12/GOV-13 amendment to
  pytest-as-evidence and scoping the MemBase `tests` table to Agent Red history.
- HYG-014 changes from archive-then-prune to prune + retention.toml + VACUUM with no archive.

The current proposal still includes `scripts/fab11_spec_derived_test_recorder.py` and an
archive-then-prune workflow. That is no longer the owner-approved design.

### F2 - Target paths do not cover the revised formal-artifact work

Under `DELIB-FAB11-REMEDIATION-20260610B`, HYG-030 amends GOV-12/GOV-13 and changes governed
KPI/test-evidence surfaces. That requires formal artifact approval packets and concrete target
paths for the amended governance records and generated/derived surfaces. The current
`target_paths` omit `.groundtruth/formal-artifact-approvals/*.json` or concrete packet paths.

The proposal also includes a protected `CLAUDE.md` narrative edit but omits the matching packet
artifact path. This is independently blocking under the protected-narrative workflow.

### F3 - Telemetry archive language conflicts with active PAUTH

The active PAUTH forbids `off_root_telemetry_archive`. The proposal still preserves an
archive-first design and says a truly out-of-root archive is an owner option at implementation
time. That option is no longer available under the active PAUTH. The revised proposal must
remove archive-first/off-root archive behavior and match the v2 prune + retention + VACUUM
decision, including the cheap pre-VACUUM DB snapshot specified by the authorization.

## Required Revision

Submit a REVISED proposal that:

1. Cites `DELIB-FAB11-REMEDIATION-20260610B` as the operative owner decision and treats the
   earlier `DELIB-FAB11-REMEDIATION-20260610` as superseded history.
2. Replaces the partial spec-derived test recorder scope with the pytest-as-evidence GOV-12/GOV-13
   amendment and any required KPI/test-evidence surface updates.
3. Replaces archive-then-prune with prune + retention.toml + VACUUM, no off-root telemetry archive,
   and the required cheap file-level pre-VACUUM DB snapshot.
4. Adds concrete formal-artifact approval packet paths for protected narrative/spec-governance
   edits, including `CLAUDE.md` and GOV-12/GOV-13 amendment packets.
5. Preserves the valid sequencing constraint: assertion-corpus repair before sweep revival.

## Verdict

NO-GO until the proposal is revised to the current owner decision and project authorization.
