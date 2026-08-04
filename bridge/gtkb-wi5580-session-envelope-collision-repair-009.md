NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T06-29-16Z
author_model: goose-deepseek-v4-pro
author_model_version: goose-deepseek-v4-pro
author_model_configuration: harness=goose-desktop; role=prime-builder
author_metadata_source: goose-session-envelope

bridge_kind: implementation_report

# Implementation Report — gtkb-wi5580-session-envelope-collision-repair (v009)
Document: gtkb-wi5580-session-envelope-collision-repair
Version: 009
Date: 2026-08-03 UTC
Responds to: bridge/gtkb-wi5580-session-envelope-collision-repair-008.md (GO on v007)
Work Item: WI-5580
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Implementation-start packet: sha256:a7688959d902a3ce93a77545c80465d6b79d05427f47c2360770dd906a5b7727 (expires 2026-08-03T08:51:38Z)
Work-intent claim: gtkb-wi5580-session-envelope-collision-repair @ G-2026-08-03T06-29-16Z (acquired 2026-08-03T06:49:40Z, go_implementation)

## Summary

This implementation performs no MemBase mutation and does not write
groundtruth.db; it changes only the in-scope source and test paths.

WI-5580 repairs the empty-environ fallback defect in the session-envelope
acting-harness selector and the modernization semantic-evidence collector. The
prior code used `dict(environ or os.environ)`, which silently re-inherited the
process ambient environment whenever a caller passed an explicit empty mapping
(`environ={}`). That made a caller's explicit "no environment" signal fall back
to ambient host-family markers (e.g. a live `CODEX_THREAD_ID`), defeating the
fail-closed contract for provenance resolution. This report covers the fix at
exactly the three semantic sites named in v007 IP-R1/IP-R2, plus the v007 IP-R3
regression tests. No other hunks were introduced.

## Scope Implemented (v007 IP-R1 / IP-R2 — exactly 3 semantic sites)

1. `groundtruth-kb/src/groundtruth_kb/session/envelope.py` —
   `resolve_acting_harness_identity()` (line 227):
   `env = dict(environ or os.environ)` →
   `env = dict(os.environ if environ is None else environ)`.
2. `scripts/collect_modernization_semantic_evidence.py` —
   `resolve_runtime_provenance()` (line 496): same None-only fallback.
3. `scripts/collect_modernization_semantic_evidence.py` —
   `Collector.__init__()` (line 524): same None-only fallback.

The change narrows the ambient-environment fallback to trigger only when the
caller passes `environ=None` (the "use the process environment" signal). An
explicit empty mapping is now honored as "no environment", so ambient
host-family markers (e.g. a live `CODEX_THREAD_ID`) are no longer inherited and
provenance resolution fails closed as specified.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement is required
before implementation; the governing scope is v007 REVISED as approved by GO
v008.

## Regression Tests Added (v007 IP-R3)

`platform_tests/scripts/test_kb_attribution_session_role.py` (2 new tests):
- `test_empty_environ_does_not_fall_back_to_ambient_markers` — ambient Codex
  marker seeded via monkeypatch; `resolve_acting_harness_identity(..., environ={})`
  raises `EnvelopeError("Acting harness identity is unavailable")` (fail-closed,
  no ambient selection).
- `test_explicit_producer_beats_ambient_marker` — ambient Codex marker seeded;
  `resolve_acting_harness_identity(..., environ={}, harness_name='claude',
  harness_id='B')` returns exactly `('claude', 'B')` despite the ambient Codex
  marker.

`platform_tests/scripts/test_collect_modernization_semantic_evidence.py` (2 new
tests):
- `test_empty_environ_does_not_consume_ambient_session` — ambient Codex/session
  markers seeded; `resolve_runtime_provenance(..., environ={})` raises
  `CollectionError` (ambient session NOT consumed); evidence dir not created.
- `test_collector_empty_environ_stays_empty_and_fails_closed` —
  `Collector(environ={})` stores an exactly-empty `self.environ == {}`, issuer
  resolution fails closed (`issuer is None`, `issuer_error` set), and no
  evidence state is mutated (evidence dir not created).

No new hunks were added to `.claude/hooks/workstream-focus.py` or
`platform_tests/hooks/test_workstream_focus.py` (verification-only rerun).

## Specification Links

Carried from v007; `GOV-SESSION-ROLE-AUTHORITY-001` removed as RETIRED per v008
NO-GO F4 / WI-5723; `DCL-SESSION-ROLE-RESOLUTION-001` v7 and
`DELIB-202667524` / `DELIB-202667530` substituted.

- DCL-SESSION-ROLE-RESOLUTION-001 (v7)
- DCL-SESSION-ENVELOPE-DURABILITY-001
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001
- DCL-PROJECT-DEPENDENCY-ORDERING-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DELIB-202667524
- DELIB-202667530

Note: `GOV-SESSION-ROLE-AUTHORITY-001` was carried in v007 but is RETIRED
(flagged by v008 NO-GO F4 on WI-5723); it is removed here and replaced by
DCL-SESSION-ROLE-RESOLUTION-001 v7 plus DELIB-202667524 / DELIB-202667530.

## Specification-Derived Verification Plan → Test Mapping

| Specification clause / acceptance criterion | Verification (test / command) | Result |
| --- | --- | --- |
| Empty-environ must fail closed (no ambient inherit) — envelope selector | `test_empty_environ_does_not_fall_back_to_ambient_markers` | PASS |
| Explicit producer beats ambient marker — envelope selector | `test_explicit_producer_beats_ambient_marker` | PASS |
| Empty-environ must not consume ambient session — collector provenance | `test_empty_environ_does_not_consume_ambient_session` | PASS |
| Collector empty-environ stays empty, fails closed, no evidence mutation | `test_collector_empty_environ_stays_empty_and_fails_closed` | PASS |
| No regression in existing collision/envelope/receipt tests | existing tests in the 3 primary files | PASS (111 prior + 4 new = 115) |
| No nonimpairment regression across modernization suites | scope_semantics / hard_invariants / harness_parity / fresh_worker suites | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | spec-to-test mapping above + executed commands below | PASS |

## Verification Commands and Observed Results

Primary suite (3 files) — expect prior 111 pass + new regressions, only the 2
pre-disclosed failures remain:
- `python -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --timeout=600`
  → **2 failed, 115 passed, 3 skipped** (prior 111 + 4 new regressions pass; the
  only 2 failures are the pre-existing failures disclosed in v007: duplicate
  modernization memberships WI-5292/WI-5541/WI-5580/WI-5086, and absent
  historical corpus manifest — both outside WI-5580 scope).

- `python -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short --timeout=600 -k "not mod_ad09_proves_query_quarantine_and_no_historical_worker_dependency"` → **14 passed, 1 deselected**.
- `python -m pytest platform_tests/scripts/test_modernization_hard_invariants.py platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short --timeout=600` → **9 passed**.
- `python -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=600 -k "not fresh_worker_bootstraps_from_only_copied_product_assets"` → **3 passed, 1 deselected**.

Code-quality gates (all 6 target paths):
- `ruff check <6 paths>` → **All checks passed!**
- `ruff format --check <6 paths>` → **6 files already formatted**.
- `py_compile` (3 source paths) → **PY_COMPILE_OK**.
- `git diff --check <6 paths>` → **DIFF_CHECK_OK** (only LF→CRLF working-copy
  warnings; no whitespace errors).

Sidecar integrity (WI-5825-owned, read-only):
- `.gtkb-state/bridge-publication-pending/gtkb-wi5580-session-envelope-collision-repair-005-7079b5644cd1966e.json`
  SHA-256 re-read post-test = `1e35532fa6e53f982a938fe9e1f8a4ce1a94e31a8221e024eed2a8c14dab70bd`
  — **unchanged** (WI-5825-owned recovery artifact, read-only preserved).

## Files Changed (exactly the in-scope set)

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` — 1 line (L227).
- `scripts/collect_modernization_semantic_evidence.py` — 2 lines (L496, L524).
- `platform_tests/scripts/test_kb_attribution_session_role.py` — +24 lines (2 tests).
- `platform_tests/scripts/test_collect_modernization_semantic_evidence.py` — +44 lines (2 tests).

Diff stat: 4 files changed, 71 insertions(+), 3 deletions(-). The two
verification-only paths (`.claude/hooks/workstream-focus.py`,
`platform_tests/hooks/test_workstream_focus.py`) have zero hunks.

## Recommended Commit Type

Recommended commit type: `fix:` — repairs broken behavior (empty-environ
ambient fallback) with no new capability surface; the test additions are
regressions covering the repair.

## Disclosed Pre-Existing Failures (NOT WI-5580 scope)

The 2 failures in the primary suite are pre-existing and disclosed in v007; they
are outside WI-5580 scope and left failing:
1. `test_live_program_reconciliation_is_executable_and_duplicate_free` — duplicate
   modernization memberships WI-5292/WI-5541/WI-5580/WI-5086.
2. `test_pre_modernization_baseline_binds_historical_observations_and_explicit_gaps`
   — absent historical corpus manifest
   (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CORPUS-MANIFEST-2026-07-04.md`).

## Owner Decisions / Input

None required for this implementation. Work proceeded under live GO v008,
implementation-start packet sha256:a7688959d902a3ce93a77545c80465d6b79d05427f47c2360770dd906a5b7727,
PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE v5
(owner decision DELIB-202667714), and work-intent claim at
G-2026-08-03T06-29-16Z. No owner-approval scope is claimed by this report.

## VERIFIED Status

VERIFIED is an external Loyal Opposition outcome via the commit-finalization
helper. This report does not self-assert VERIFIED.
