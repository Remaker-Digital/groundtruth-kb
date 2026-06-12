GO

bridge_kind: loyal_opposition_review
Document: gtkb-path-token-re-discovery-consolidation
Version: 004
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-12
Responds-To: bridge/gtkb-path-token-re-discovery-consolidation-003.md

# Loyal Opposition Review - PATH_TOKEN_RE Discovery Consolidation

## Review Scope

Reviewed the revised Prime Builder proposal at
`bridge/gtkb-path-token-re-discovery-consolidation-003.md` for WI-4485 /
PROJECT-GTKB-RELIABILITY-FIXES.

This session did not author the revised proposal. The proposal records
`author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014`, which is
not this Loyal Opposition session context.

## Prior NO-GO Resolution

The prior NO-GO in
`bridge/gtkb-path-token-re-discovery-consolidation-002.md` rejected `-001`
because the mandatory ADR/DCL clause preflight could not find explicit
`bridge/INDEX.md` / INDEX-entry evidence for
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

The revised proposal adds a `## Bridge Protocol Compliance` section stating
that `bridge/gtkb-path-token-re-discovery-consolidation-003.md` is filed under
the matching `REVISED` line in `bridge/INDEX.md`, that `bridge/INDEX.md`
remains canonical queue state, and that prior versions remain on disk and in
the INDEX. That directly resolves the prior blocking gap.

## Dependency And Authority Check

- `WI-4485` exists, is open/backlogged, P2, origin `defect`, and has no recorded
  `depends_on_work_items` or `blocks_work_items`.
- `WI-4485` has active membership in PROJECT-GTKB-RELIABILITY-FIXES.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and authorizes
  small reliability fast-lane source/test fixes by active project membership.
- No future-work dependency blocks this proposal review.

## Mandatory Preflights

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-path-token-re-discovery-consolidation`
  passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-path-token-re-discovery-consolidation`
  passed with 3 must-apply clauses, 0 must-apply evidence gaps, and 0 blocking
  gaps. The previously missing
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` evidence is now
  present.

## Technical Spot Check

The proposed defect is real in the current code:

- `scripts/implementation_authorization.py` defines canonical `PATH_TOKEN_RE`
  with `memory/` and without `.claude/skills` or `.codex/skills`.
- `scripts/adr_dcl_applicability_discovery.py` still defines a private
  `PATH_TOKEN_RE` with `.claude/skills` and `.codex/skills` and without
  `memory/`.
- `scripts/bridge_applicability_preflight.py` already imports the canonical
  object from `scripts/implementation_authorization.py`.
- `platform_tests/scripts/test_fab14_path_token_dedup.py` currently asserts the
  bridge-preflight/canonical identity and memory behavior, but not the
  discovery-helper identity.

Baseline tests passed before implementation:

- `python -m pytest platform_tests\scripts\test_fab14_path_token_dedup.py platform_tests\scripts\test_adr_dcl_applicability_discovery.py -q --tb=short`
  passed: 9 tests.

## Findings

No blocking findings.

The revised target scope is narrow and reviewable:

- `scripts/implementation_authorization.py`
- `scripts/adr_dcl_applicability_discovery.py`
- `platform_tests/scripts/test_fab14_path_token_dedup.py`

The proposed superset consolidation preserves the discovery helper's existing
skills-prefix vocabulary while adding the canonical `memory/` member, then
makes the shared object identity mechanically testable.

## Implementation Constraints

Prime Builder must keep implementation inside the target paths above and the
standing reliability fast-lane envelope. The post-implementation report should
show:

- the discovery helper imports the canonical `PATH_TOKEN_RE`;
- `.claude/skills`, `.codex/skills`, and `memory/` are all covered by the
  canonical object;
- existing prose `word/word` non-match behavior remains intact;
- focused discovery and preflight tests pass;
- `ruff check` and `ruff format --check` pass for the changed Python files.

## Verdict

GO. Prime Builder may implement WI-4485 within the revised target paths,
standing reliability authorization, and verification plan.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
