GO

# Loyal Opposition Review - Canonical Terms Production Seed And Doctor Elevation

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-001.md`
Verdict: GO

## Claim

The proposal is approved for implementation. The production database seed gap
is real, the doctor severity change is proportionate, and the proposed test
plan covers the failure mode that let a scratch-only seed be treated as
production-complete.

## Evidence Checked

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation` passed with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation` passed in mandatory mode with 5 clauses evaluated, 4 `must_apply`, and 0 blocking gaps.
- `python -m groundtruth_kb secrets scan --paths bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-001.md --json --fail-on=` returned `finding_count: 0`.
- Direct production DB count check against `groundtruth.db` returned `canonical_terms: 0` and `current_canonical_terms: 0`.
- `python -m groundtruth_kb canonical-terms seed --dry-run` planned `summary: insert=27` against `.claude/rules/canonical-terminology.md`.
- Current `_check_canonical_terms_registry()` returns `status="pass"` when the `canonical_terms` table exists but has no active rows.

## Review Notes

The requested production seed is a data mutation, but it is bounded and
owner-directed by the proposal's cited S337 prompt. Codex GO authorizes the
seed execution within this bridge item only, using the shipped
`canonical-terms seed --apply` command and the evidence sequence in the
proposal.

The proposed empty-table doctor status should be `warning`, not `fail`, for
this slice. That matches the existing soft-doctor compatibility stance while
making the schema-present, seed-missing state visible in aggregate health.

## GO Conditions

The implementation report must prove:

1. The production seed is run against `E:\GT-KB\groundtruth.db`, not a scratch
   database.
2. The first apply inserts 27 active `platform_core` canonical terms and the
   second apply reports all 27 as unchanged with no version-2 rows.
3. `.claude/rules/canonical-terminology.md` remains content-unchanged.
4. `_check_canonical_terms_registry()` reports `status="warning"` when the
   schema is present, markdown defines platform-core terms, and the table is
   empty.
5. After production seeding, `gt project doctor --json` or the equivalent
   module invocation reports the canonical terms registry as passing with 27
   active terms and clean parity.
6. The targeted doctor and canonical-term module tests pass.
7. Ruff check and format check cover the changed Python files.
8. The implementation report must be the next bridge file after this review,
   normally `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md`.
   Do not use `-002.md` for the implementation report because this GO review
   occupies that sequence number.

## Result

GO. Prime Builder may implement the production seed, doctor severity
correction, and regression test as described, constrained by the conditions
above.
