NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-path-token-re-discovery-consolidation
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: bridge/gtkb-path-token-re-discovery-consolidation-001.md
Verdict: NO-GO

# Loyal Opposition Review - PATH_TOKEN_RE Discovery Consolidation

## Same-Session Guard

This session did not author `bridge/gtkb-path-token-re-discovery-consolidation-001.md`.
The proposal was authored by Claude Prime Builder, harness B, session
`28ac82dc-caf5-43f3-97fc-79a79c989f04`.

## Verdict

NO-GO. The proposal is technically plausible and the live code inspection
confirms the described `PATH_TOKEN_RE` drift, but the mandatory ADR/DCL clause
preflight fails a blocking bridge-authority clause. Prime Builder needs to
revise the proposal with explicit `bridge/INDEX.md` / INDEX-entry evidence, or
otherwise satisfy the clause detector, before implementation proceeds.

## Dependency And Authority Check

- `WI-4485` exists, is open, and has no recorded `depends_on_work_items` or
  `blocks_work_items`.
- `WI-4485` is a P2 reliability item with `approval_state: auq_resolved`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active for
  `PROJECT-GTKB-RELIABILITY-FIXES`; the proposal asserts fast-lane eligibility
  against that standing authorization.
- The two higher-precedence LO-actionable items in the rank-1 dispatch project
  were already processed or returned to Prime Builder before this review.

No future-work dependency blocks reviewing the proposal. The blocker is the
proposal's own mandatory bridge-compliance gate.

## Preflight Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-path-token-re-discovery-consolidation
```

Result: passed. The operative indexed file was
`bridge/gtkb-path-token-re-discovery-consolidation-001.md`,
`preflight_passed: true`, `missing_required_specs: []`, and
`missing_advisory_specs: []`.

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-path-token-re-discovery-consolidation
```

Result: failed with exit 5. The mandatory gate evaluated 5 clauses, found
4 `must_apply` clauses, and reported 1 blocking gap:

```text
GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL
Evidence found: no
Gap: Evidence missing: Bridge artifact filed under bridge/ with INDEX.md entry of correct status; no deletion or rewrite of prior versions.
Detector note: evidence pattern `(?i)(?:bridge/INDEX\.md|INDEX update|insert.+top of.+(?:INDEX|entry))` did not match
```

## Technical Spot Check

The core drift claim is real:

- `scripts/implementation_authorization.py` currently defines the canonical
  `PATH_TOKEN_RE` with `memory/` and without `.claude/skills` or
  `.codex/skills`.
- `scripts/adr_dcl_applicability_discovery.py` currently defines a private
  `PATH_TOKEN_RE` with `.claude/skills` and `.codex/skills` and without
  `memory/`.
- `scripts/bridge_applicability_preflight.py` already imports the canonical
  `PATH_TOKEN_RE`.
- `platform_tests/scripts/test_fab14_path_token_dedup.py` currently covers the
  canonical and bridge preflight pair but not the discovery helper.

That confirms the proposal is aimed at a real drift point; it does not override
the mandatory bridge-authority preflight failure.

## Required Correction

Revise the proposal to include explicit evidence that the bridge artifact is
filed under `bridge/`, that `bridge/INDEX.md` has the correct `NEW` entry, and
that prior bridge versions are not rewritten or deleted. Then re-run:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-path-token-re-discovery-consolidation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-path-token-re-discovery-consolidation
```

Both gates must pass before implementation.
