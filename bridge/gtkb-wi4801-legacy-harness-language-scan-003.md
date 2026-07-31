NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f13b0-26e7-7ed2-930c-a637e952ba1c
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop automation; Prime Builder; autonomous auto-builder run
author_metadata_source: codex-auto-builder-explicit-runtime-envelope

bridge_kind: implementation_report
Document: gtkb-wi4801-legacy-harness-language-scan
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4801-legacy-harness-language-scan-002.md
Approved proposal: bridge/gtkb-wi4801-legacy-harness-language-scan-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4801
Recommended commit type: feat
Implementation commit: 3a626c9dd feat: add legacy harness language scanner

# Legacy Harness-Language Scan Implementation Report

## Implementation Claim

Implemented the first WI-4801 tranche as an advisory, read-only scanner plus hermetic tests.

The new `scripts/check_legacy_harness_language.py` scanner walks the approved load-bearing GT-KB surfaces, detects candidate legacy harness-name / reviewer-harness / hard-coded role-coupling language, and classifies findings as `STRIP`, `KEEP`, `QUARANTINE`, or `EXCLUDED`. It performs no source mutation and exits 0 in advisory mode.

The new `platform_tests/scripts/test_check_legacy_harness_language.py` test file covers deterministic phrase detection, excluded historical/runtime paths, `KEEP` / `STRIP` / `QUARANTINE` classification, out-of-root rejection, JSON/text CLI output shape, and a live read-only smoke check.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required. This implementation proceeds under `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25` and the GO verdict in `bridge/gtkb-wi4801-legacy-harness-language-scan-002.md`.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - owner directive authorizing obsolete-reference cleanup and the paired purge project.
- `bridge/gtkb-wi4801-legacy-harness-language-scan-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4801-legacy-harness-language-scan-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| WI-4801 cleanup family | `python -m pytest platform_tests/scripts/test_check_legacy_harness_language.py -q --tb=short` passed: 6 tests cover detection, path policy, classification, output contract, and live smoke. |
| PAUTH target-path bounds | Commit `3a626c9dd` contains only `scripts/check_legacy_harness_language.py` and `platform_tests/scripts/test_check_legacy_harness_language.py`, matching the GO-approved target paths. |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` inventory-first cleanup | Live smoke produced an advisory classified inventory with `files_scanned=1660`, `matches=147`, `unreadable=0`, and no mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps each linked requirement to executed pytest, live-smoke, lint, and commit evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed and reported files are under `E:\GT-KB`. |
| Python quality gate | `python -m ruff check ...` passed and `python -m ruff format --check ...` reported both files already formatted. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_check_legacy_harness_language.py -q --tb=short`
- `python scripts/check_legacy_harness_language.py --project-root . --json | python -c "import json, sys; data=json.load(sys.stdin); print(json.dumps({'status': data['status'], 'summary': data['summary']}, indent=2, sort_keys=True))"`
- `python -m ruff check scripts/check_legacy_harness_language.py platform_tests/scripts/test_check_legacy_harness_language.py`
- `python -m ruff format --check scripts/check_legacy_harness_language.py platform_tests/scripts/test_check_legacy_harness_language.py`
- `git diff --cached --check -- scripts/check_legacy_harness_language.py platform_tests/scripts/test_check_legacy_harness_language.py`
- `git commit -m "feat: add legacy harness language scanner"`

## Observed Results

- Focused pytest: 6 passed.
- Live smoke: `status=advisory`; summary `KEEP=4`, `QUARANTINE=31`, `STRIP=112`, `files_scanned=1660`, `matches=147`, `unreadable=0`.
- Ruff check: all checks passed.
- Ruff format check: 2 files already formatted.
- Cached diff check: no whitespace errors.
- Commit hook: secret scan passed, narrative-artifact evidence passed, ruff format passed, protected-commit authorization passed; material inventory drift was downgraded to warning because no staged path was an inventoried surface.

## Files Changed

- `scripts/check_legacy_harness_language.py`
- `platform_tests/scripts/test_check_legacy_harness_language.py`

## Recommended Commit Type

- Recommended commit type: `feat`
- Commit: `3a626c9dd feat: add legacy harness language scanner`

## Acceptance Criteria Status

- [x] Deterministic scanner detects legacy reviewer-harness and hard-coded harness-role coupling phrase families.
- [x] Explicit path policy includes approved load-bearing surfaces and excludes `bridge/`, `.claude/worktrees/`, `memory/`, `independent-progress-assessments/`, `.gtkb-state/`, and temporary/runtime paths.
- [x] Output classifies findings as `STRIP`, `KEEP`, `QUARANTINE`, or `EXCLUDED`.
- [x] CLI emits stable JSON/text summaries and exits 0 in advisory mode.
- [x] Focused tests, live smoke, ruff check, and ruff format check passed.
- [x] No source prose cleanup, bridge audit deletion, formal GOV/ADR/DCL/SPEC mutation, or state migration was performed.

## Risk And Rollback

Residual risk is limited to advisory false positives/false negatives in the scan inventory. The scanner does not mutate files, and later cleanup tranches still require their own bridge proposals and target paths.

Rollback is to revert commit `3a626c9dd`, removing the new script and test file. No database migration or bridge audit rewrite is involved.

## Loyal Opposition Asks

1. Verify that the committed scanner and tests satisfy the GO-approved WI-4801 scan/classification tranche.
2. Return `VERIFIED` if the implementation and evidence satisfy the approved proposal; otherwise return `NO-GO` with concrete findings.
