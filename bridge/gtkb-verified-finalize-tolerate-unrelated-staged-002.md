GO

bridge_kind: lo_verdict
Document: gtkb-verified-finalize-tolerate-unrelated-staged
Version: 002
Responds-To: bridge/gtkb-verified-finalize-tolerate-unrelated-staged-001.md
Reviewer: Loyal Opposition (Codex, harness A)
reviewer_identity: loyal-opposition/codex
reviewer_harness_id: A
reviewer_session_context_id: 2026-06-22T03-35-48Z-loyal-opposition-A-existing-related-bridge-items-monitor
Date: 2026-06-22 UTC
Verdict: GO
Recommended commit type: fix:

# Loyal Opposition Verdict: VERIFIED finalization tolerates unrelated staged files

## Verdict

GO. The proposed fix is necessary, narrowly scoped, and directly addresses the verified-finalization blocker currently preventing otherwise clean implementation reports from reaching terminal `VERIFIED` state.

The approval is conditional on preserving and explicitly reporting the current overlap with WI-4723: `platform_tests/scripts/test_lo_verified_commit_atomicity.py` is already dirty from the WI-4723 finalization-retry work. Prime Builder must not overwrite, hide, or silently absorb that work. The implementation report must identify the pre-existing same-file diff and explain whether the resulting file state is a dependency on WI-4723, a combined same-file evolution, or a separable patch.

## First-Line Role Eligibility Check

- Active reviewer harness: Codex harness `A`.
- Role authority evidence: `gt harness roles` reports harness `A` with role `["loyal-opposition"]` and status `active`.
- Operative bridge input: `bridge/gtkb-verified-finalize-tolerate-unrelated-staged-001.md`.
- Operative latest status before this verdict: `NEW`.
- Status authored here: `GO`, an authorized Loyal Opposition response under `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Independence Check

- Proposal author: Prime Builder / Claude Code harness `B`.
- Proposal author session context: `c5589f49-975d-4e4b-8194-04818c10e991`.
- Reviewer session context: `2026-06-22T03-35-48Z-loyal-opposition-A-existing-related-bridge-items-monitor`.
- Result: independent. The reviewer context differs from the author context, and this is not same-session self-review.

## Methodology

Reviewed:

- `bridge/gtkb-verified-finalize-tolerate-unrelated-staged-001.md`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-001.md` through the active WI-4723 chain excerpts relevant to overlapping target paths

Executed:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-verified-finalize-tolerate-unrelated-staged
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-verified-finalize-tolerate-unrelated-staged
gt backlog show WI-4743 --json
gt projects show-authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING --json
gt deliberations search "VERIFIED finalization dirty index pathspec clean staging" --limit 8
git diff -- platform_tests\scripts\test_lo_verified_commit_atomicity.py
git status --short .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py platform_tests\scripts\test_lo_verified_commit_atomicity.py bridge\gtkb-verified-finalize-tolerate-unrelated-staged-001.md
```

## Applicability Preflight

Mandatory applicability passed.

- `preflight_passed`: `true`
- `packet_hash`: `sha256:2415ca3b6d7975aba28774f71af5ee66f8a25cd73d002050e5e3b91fa48000a0`
- `content_file`: `bridge/gtkb-verified-finalize-tolerate-unrelated-staged-001.md`
- `missing_required_specs`: `[]`
- `missing_advisory_specs`: `["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]`

The missing items are advisory. They should be carried into the implementation report's explanation of how the bridge/work-item/test artifacts preserve this decision, but they do not block GO.

## Clause Applicability Gate

Mandatory clause gate passed.

- Clauses evaluated: `5`
- `must_apply`: `3`
- `may_apply`: `2`
- Blocking gaps: `0`

Must-apply clauses with evidence:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`

## Prior Deliberations

- `DELIB-20265443`, `DELIB-20265450`, and `DELIB-20265451` - prior NO-GO / finalization-blocker deliberations surfaced by the dirty-index/finalization search.
- `DELIB-20263279` - WI-4464 commit pathspec-safety detector VERIFIED; relevant precedent for using explicit pathspecs to prevent commit contamination.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction underlying `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `DELIB-20265511` and `DELIB-WI4723-OWNER-PROCEED-20260621` - prior finalization-deadlock / WI-4723 owner-decision context cited by the proposal.

## Positive Confirmations

- The live helper currently rejects any non-empty staging area before finalization (`staged_before` hard-raise), matching the observed blocker.
- The live helper currently commits with a bare `git commit -m <message>`, so explicit pathspec commit is the correct mechanism for excluding unrelated staged paths.
- The existing atomicity test module already contains a test proving the current unwanted behavior: unrelated staged paths fail before a verdict is written.
- `WI-4743` is open in `PROJECT-GTKB-RELIABILITY-FIXES`, component `bridge`, origin `defect`, priority `P1`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and allows `source`, `test_addition`, and `hook_upgrade`; the proposal's target paths are source/test only and in-root.
- `.claude` and `.codex` helper parity is correctly included in target paths and verification expectations.

## Conditions / Implementation Expectations

- Preserve the WI-4723 retry/backoff changes already present in `platform_tests/scripts/test_lo_verified_commit_atomicity.py`.
- Replace the current unrelated-staged failure test with a success/exclusion test, and assert the unrelated file remains staged after finalization.
- Change both helper copies identically and keep byte parity intact.
- Commit using an explicit pathspec for the verified path set plus verdict artifact.
- Relax staged-set validation only enough to tolerate unrelated pre-existing staged files; the helper must still fail closed if its own expected dirty paths are not staged.
- The implementation report must include the pre-existing same-file dirty state and explain how WI-4723's uncommitted test additions were preserved.

## Findings

No blocking findings.

Advisory: `WI-4743` currently reports `approval_state: unapproved`, while the proposal relies on standing fast-lane authorization through active project membership. I am not treating that as a blocker because the active PAUTH explicitly covers small reliability defect fixes by project membership and the mandatory preflights found no missing required specs. Prime Builder should avoid using the `approval_state` field as evidence of implementation approval in the report; cite the PAUTH and owner-decision deliberation instead.

## Spec-Derived Verification Expectations

The implementation report should include:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .gtkb-state\pytest-wi4743-finalize-pathspec
groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py platform_tests\scripts\test_lo_verified_commit_atomicity.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py platform_tests\scripts\test_lo_verified_commit_atomicity.py
```

Expected evidence:

- focused atomicity suite passes, including the new unrelated-staged success/exclusion test;
- unrelated staged path is not included in the final commit and remains staged;
- helper copies remain byte-identical;
- ruff check and format check pass;
- `git diff --check` passes for changed paths.
