NEW

# GT-KB Bridge Implementation Report - gtkb-wi4735-clause-preflight-user-profile-disclosure-guard - 003

bridge_kind: implementation_report
Document: gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4735-clause-preflight-user-profile-disclosure-guard-002.md
Approved proposal: bridge/gtkb-wi4735-clause-preflight-user-profile-disclosure-guard-001.md
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T10-10-37Z-prime-builder-A-148048
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex headless auto-dispatch; resolved_role=prime-builder

## Implementation Claim

Implemented the WI-4735 CLAUSE-IN-ROOT false-positive guard in `scripts/adr_dcl_clause_preflight.py`.

The detector still removes explicit `<!-- in-root-disclosure -->` blocks only for failure-pattern scanning and still appends raw `target_paths` declarations back into the scanned text. The new behavior additionally removes only diagnostic/disclosure prose lines from CLAUSE-IN-ROOT failure scanning when the clause has `failure_pattern_disclosure_exempt = true`.

The guard preserves failure detection for out-of-root `target_paths`, file-list entries, artifact/output sections, and unmarked artifact/output claims. This keeps genuine out-of-root implementation declarations blocking while allowing report-safe harness-local diagnostic examples.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision is required. This implementation stays inside the approved `WI-4735` target paths and uses project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23` carried forward from the approved proposal.

## Prior Deliberations

- `DELIB-20263398` - GO review for WI-3384, which introduced the explicit disclosure-block exemption that this work preserves.
- `DELIB-20263484` - Loyal Opposition advisory verifying WI-3384 disclosure-exemption regression coverage.
- `DELIB-20263832` - bridge preflight path-warning GO; relevant precedent for narrowing path-token collection instead of broad document-wide path scanning.
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-006.md` - incident evidence where CLAUSE-IN-ROOT failed because report text quoted a harness-local user-profile path while implementation targets remained in-root.
- `bridge/gtkb-wi4735-clause-preflight-user-profile-disclosure-guard-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4735-clause-preflight-user-profile-disclosure-guard-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; WI-4735 false-positive requirement | Added `test_harness_local_observed_result_path_not_refuted` and `test_harness_local_diagnostic_disclosure_line_not_refuted`; direct content-file preflight against the prior WI-4723 report shape now reports zero CLAUSE-IN-ROOT gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; strict artifact enforcement | Preserved `target_paths` enforcement and added/updated negative coverage for out-of-root `target_paths`, file-list entries, and artifact/output claims. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Ran the bridge applicability and clause preflights for `gtkb-wi4735-clause-preflight-user-profile-disclosure-guard`; both passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ran the focused clause-preflight regression modules with 32 passing tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserved traceability across WI-4735, the approved bridge thread, detector source, regression tests, and this implementation report. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_adr_dcl_clause_preflight.py platform_tests\scripts\test_clause_in_root_disclosure_exempt.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_adr_dcl_clause_preflight.py platform_tests\scripts\test_clause_in_root_disclosure_exempt.py -q --tb=short --basetemp .gtkb-state\tmp\pytest-wi4735-clause-disclosure-final2
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\adr_dcl_clause_preflight.py platform_tests\scripts\test_adr_dcl_clause_preflight.py platform_tests\scripts\test_clause_in_root_disclosure_exempt.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\adr_dcl_clause_preflight.py platform_tests\scripts\test_adr_dcl_clause_preflight.py platform_tests\scripts\test_clause_in_root_disclosure_exempt.py
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file bridge\gtkb-wi4723-verified-finalize-index-lock-retry-005.md
```

## Observed Results

- Implementation authorization succeeded: latest status `GO`, packet hash `sha256:f2b5b16b1a34bc0ed5adfb257bc164d5ba53faf53d969f63803918a60e96d0da`, active project authorization for `WI-4735`.
- Work-intent claim succeeded for session `2026-06-23T10-10-37Z-prime-builder-A-148048`.
- Initial pytest run without `--basetemp` failed before fixture setup because the default Windows temp directory was inaccessible; this is the known environment issue from the WI-4723 incident family, not a test assertion failure.
- Repo-local `--basetemp` pytest rerun: `32 passed, 2 warnings in 9.57s`.
- Ruff lint: `All checks passed!`.
- Ruff format check: `3 files already formatted`.
- WI-4735 applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- WI-4735 clause preflight: `Evidence gaps in must_apply clauses: 0`, `Blocking gaps (gate-failing): 0`.
- Direct WI-4723 incident-shape content-file clause preflight: `Evidence gaps in must_apply clauses: 0`, `Blocking gaps (gate-failing): 0`.

## Files Changed

- `scripts/adr_dcl_clause_preflight.py`
- `platform_tests/scripts/test_clause_in_root_disclosure_exempt.py`

Unrelated dirty worktree paths were present before this dispatch and are not part of this implementation report.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this repairs a false-positive blocking gate in an existing mandatory preflight surface.

```text
 platform_tests/scripts/test_clause_in_root_disclosure_exempt.py | 56 +++++++++++++++++--
 scripts/adr_dcl_clause_preflight.py                            | 62 ++++++++++++++++++++++
 2 files changed, 115 insertions(+), 3 deletions(-)
```

## Acceptance Criteria Status

- [x] Report-safe harness-local user-profile disclosures in diagnostic/observed-result prose no longer refute CLAUSE-IN-ROOT evidence.
- [x] Raw out-of-root `target_paths` continue to refute CLAUSE-IN-ROOT evidence even inside explicit disclosure blocks.
- [x] Out-of-root file-list entries continue to refute CLAUSE-IN-ROOT evidence.
- [x] Unmarked artifact/output claims continue to refute CLAUSE-IN-ROOT evidence.
- [x] Focused regression tests, lint, format check, bridge applicability preflight, and clause preflight pass.

## Risk And Rollback

Residual risk is classifier calibration: a future report could use ambiguous prose that looks diagnostic but is actually declaring an artifact/output. The implementation mitigates this by preserving artifact-heading, file-list, `target_paths`, and artifact/output verb checks in the failure scan.

Rollback is a single-source/test revert of `scripts/adr_dcl_clause_preflight.py` and `platform_tests/scripts/test_clause_in_root_disclosure_exempt.py`; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the line-level disclosure guard does not broaden CLAUSE-IN-ROOT beyond report-safe harness-local diagnostics.
2. Verify the positive and negative tests map to the linked specifications and WI-4735 acceptance criteria.
3. Return VERIFIED if the implementation and report satisfy the approved proposal; otherwise return NO-GO with specific detector-boundary findings.
