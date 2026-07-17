VERIFIED
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5407-installed-wheel-source-exclusion
Version: 004
Date: 2026-07-17 UTC
Reviewed: bridge/gtkb-wi5407-installed-wheel-source-exclusion-003.md
Responds to: bridge/gtkb-wi5407-installed-wheel-source-exclusion-003.md
Approved proposal: bridge/gtkb-wi5407-installed-wheel-source-exclusion-001.md
GO: bridge/gtkb-wi5407-installed-wheel-source-exclusion-002.md
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5407
Recommended commit type: fix

# VERIFIED — WI-5407 Installed Wheel Source Exclusion

## Verdict Summary

VERIFIED. The approved one-assertion repair in
`platform_tests/scripts/test_modernization_fresh_worker.py` is implemented
exactly as proposed and GO'd: the invalid `not module.is_relative_to(REPO_ROOT)`
lexical check (which false-positives whenever the governed in-root pytest
basetemp places the isolated venv under `E:/GT-KB`) is replaced with a venv
positive-containment assertion plus an exact `BUILD_PROJECT / "src"`
checkout-source exclusion. All claims in the implementation report were
independently reproduced against live repository state. Two material items
were discovered during independent verification and are disclosed below;
neither is a defect in this thread's own implementation.

## Material Findings (Non-Blocking For This Verdict)

### Finding 1 (P1) — Live duplicate bridge authorization on the identical assertion

Sibling thread `bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-008.md`
carries a still-live, unimplemented `GO` verdict authorizing a fix to the
exact same assertion in the exact same test
(`test_built_wheel_assembles_context_without_source_tree_or_root_config`)
in the exact same file, via a different mechanism (exact single-file-path
inequality vs. this thread's directory-containment exclusion).

Evidence this is a genuine duplicate: both threads' original proposals
share the same underlying Codex session ID
(`019f5f6d-60cd-7040-b73f-c7d23757c4bc`); both GOs were authored by the
same LO session (`cursor-20260716-lo-auto-process`) with identical
timestamps; neither proposal cross-references the other's slug or work
item. Because this thread's fix has landed, WI-5350/5155's outstanding GO
now targets stale content (its cited baseline SHA-256 no longer matches
the current file).

This does not block VERIFIED for WI-5407: its own diff is independently
confirmed correct, isolated, and technically preferable (directory
containment catches any file imported from within the checkout source
tree, vs. the sibling's exact single-file match). Declining to finalize
correct, verified work would not un-stale the sibling thread. Recommend
owner-directed reconciliation of the sibling thread (withdraw/defer,
citing this thread as the superseding fix) as separate follow-on work.

### Finding 2 (Advisory) — separately-tracked timeout flakiness disclosed in MemBase

`gt backlog show WI-5407` discloses a 2026-07-17 rerun that hit pytest's
30-second watchdog during the isolated wheel pip-install subprocess,
explicitly attributed to a separate, already-tracked issue (WI-5443 /
TEST-11549), not to this thread's assertion change. This reviewer's own
independent full-module rerun completed cleanly (4 passed in 34.28s, no
timeout). Disclosed for completeness; not a blocker.

## Independently Re-Verified Evidence

- `git diff -- platform_tests/scripts/test_modernization_fresh_worker.py`
  reproduces exactly the claimed 3-insertion/2-deletion hunk.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --basetemp=E:/GT-KB/.pytest-tmp/lo-review-wi5407`
  → 4 passed, 1 warning in 34.28s.
- `ruff check` on the changed file → all checks passed.
- `ruff format --check` on the changed file → 1 file already formatted.
- `git diff --check` → clean (exit 0).
- `Get-FileHash -Algorithm SHA256` on the live file →
  `137745CC34FDF7B310D14BC0013E8E1F01CA1C5798D24B9AEBFFAB361E32EE5E` —
  exact match to the report's claimed final hash.
- `git status --porcelain` on the target path → only the one declared
  target is dirty; isolated from the ~970+ unrelated dirty paths currently
  in this working tree.
- `git show HEAD:<path>` confirms the pre-change committed baseline
  carried the invalid assertion, matching the report's stated "before" state.
- Exclusion-mechanism live-risk confirmed real, not hypothetical:
  `pip show groundtruth-kb` → `Editable project location:
  E:\GT-KB\groundtruth-kb` — the dev venv used to spawn the test's nested
  venv genuinely has an editable install that would resolve to
  `groundtruth-kb/src/groundtruth_kb/__init__.py` on leak.
- Review independence confirmed: this reviewer's session context differs
  from both the `-003` report author session
  (`019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`) and the `-002` GO author session
  (`cursor-20260716-lo-auto-process`).
- Both mandatory preflights PASS against the current operative file (see
  sections below).

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test | Executed | Result |
| --- | --- | --- | --- |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | Full 4-test module (in-root basetemp) | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Same in-root rerun + git status path-isolation check | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Both mandatory preflights + gt bridge show | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight (missing_required_specs: []) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent full pytest rerun, in-root basetemp | yes | PASS (4/4) |
| `GOV-STANDING-BACKLOG-001` | gt backlog show WI-5407, WI-5350, WI-5155 | yes | PASS with disclosed caveat (Finding 1) |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Full 4-test module + ruff check + ruff format --check + git diff --check | yes | PASS |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Get-FileHash SHA256 vs report-claimed hash | yes | PASS (exact match) |

## Commands Executed

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --basetemp=E:/GT-KB/.pytest-tmp/lo-review-wi5407`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests/scripts/test_modernization_fresh_worker.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests/scripts/test_modernization_fresh_worker.py`
- `git diff --check -- platform_tests/scripts/test_modernization_fresh_worker.py`
- `git diff -- platform_tests/scripts/test_modernization_fresh_worker.py`
- `git status --porcelain -- platform_tests/scripts/test_modernization_fresh_worker.py`
- `git show HEAD:platform_tests/scripts/test_modernization_fresh_worker.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5407-installed-wheel-source-exclusion --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5407-installed-wheel-source-exclusion`
- `groundtruth-kb\.venv\Scripts\python.exe -m pip show groundtruth-kb`
- `gt deliberations search "installed wheel source exclusion package"`
- `gt bridge show gtkb-wi5407-installed-wheel-source-exclusion --json --compact` (run at start and end of review)
- `gt bridge show gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline --json --compact`
- `gt backlog show WI-5407`, `gt backlog show WI-5350`, `gt backlog show WI-5155`

## Prior Deliberations

- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-001.md` — approved proposal, carried forward.
- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-002.md` — GO verdict authorizing implementation.
- `DELIB-20260710-GTKB-MODERNIZATION-ASSURANCE-CHARTER` — owner-approved charter for `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`; this thread's acceptance-test repair fits directly within the charter's non-impairment guardrail scope.
- No prior deliberation found specifically about this exact assertion defect — consistent with `-001`'s own "No prior deliberations" claim.
- Newly discovered and not previously captured: the sibling duplicate-proposal relationship with `gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline` (Finding 1) — should be captured as a Deliberation Archive record once the sibling thread is reconciled.

## Applicability Preflight

- packet_hash: `sha256:eb023261e9dd302e2ad219cd0b7495d4283504227cce939dd68947c6f0d07a18`
- operative_file: `bridge/gtkb-wi5407-installed-wheel-source-exclusion-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

## Methodology Trail

Read full thread chain (`-001` through `-003`) plus the sibling thread
`gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline` (all versions) for
the duplicate-authorization finding. Ran both mandatory preflights against
the current operative file. Independently reproduced the pytest run
(4/4 pass), both ruff gates, `git diff --check`, and a fresh SHA-256 hash
computation — all matching the report's claims exactly. Verified the
exclusion mechanism guards a real (not hypothetical) risk via `pip show`.
Searched deliberations. Cross-checked `gt backlog show` for WI-5407,
WI-5350, and WI-5155 to surface the duplicate-authorization and
separately-tracked-flakiness findings, neither of which appears anywhere
in the bridge file chain itself. Re-ran `gt bridge show --json --compact`
at start and immediately before filing to confirm thread currency
(unchanged: NEW, version 3, both times).

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(bridge): WI-5407 installed wheel source exclusion VERIFIED`
- Same-transaction path set:
- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-001.md`
- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-002.md`
- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-003.md`
- `platform_tests/scripts/test_modernization_fresh_worker.py`
- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
