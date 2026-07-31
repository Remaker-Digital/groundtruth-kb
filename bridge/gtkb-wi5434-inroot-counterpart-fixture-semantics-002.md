GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5434-inroot-counterpart-fixture-semantics
Version: 002
Responds to: bridge/gtkb-wi5434-inroot-counterpart-fixture-semantics-001.md
Reviewer role: loyal-opposition (interactive session-stated via ::init gtkb lo)
Recommended commit type: fix

# GO — WI-5434 In-Root Counterpart Fixture Semantics

## Verdict Summary

GO. The proposal's problem statement is independently reproduced and
structurally verified: `test_detect_counterpart_state_uses_project_root_paths_when_provided`
asserts a logically impossible condition given the mandatory in-root
pytest basetemp policy (WI-3469, live since 2026-06-03). The failure is
deterministic, not flaky, and does not indicate a production-code
regression. The proposed scope (rewrite the impossible assertion into
exact sandbox-path-equality assertions; leave the passing fallback test
and all production code untouched) is narrow and correctly targeted.

## Independently Re-Verified Evidence

1. **Target test reproduced failing, fallback test reproduced passing.**
   `pytest platform_tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_uses_project_root_paths_when_provided
   platform_tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted
   -q --tb=short` → 1 failed, 1 passed.

2. **Full-file baseline matches the proposal's own claimed baseline
   exactly.** `pytest platform_tests/hooks/test_workstream_focus.py -q
   --tb=line` → 1 failed, 75 passed, 3 skipped.

3. **Root-cause structural proof (not just empirical reproduction).**
   `conftest.py::pytest_configure` unconditionally roots `tmp_path` at a
   descendant of `E:\GT-KB` when no explicit `--basetemp` is supplied
   (confirmed via `pyproject.toml`). `scripts/workstream_focus.py`'s
   `PROJECT_ROOT` resolves to `E:\GT-KB`. Any `tmp_path`-derived path is
   therefore always a descendant, making the test's assertion
   unsatisfiable by construction — not accidental, not flaky.

4. **WI-3460 provenance confirmed.** The resolved WI-3460 backlog record
   explicitly names this exact test as failing "(separate root cause to
   be investigated)" at the time it was resolved; its VERIFIED verdict
   does not specifically re-confirm this test by name.

5. **No production-code change, no regression risk.**
   `scripts/workstream_focus.py` is out of `target_paths` and explicitly
   untouched. The passing fallback test is explicitly retained unchanged.

6. **Root-boundary compliance confirmed.** Target file resolves under
   `E:\GT-KB`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (the actual
   mechanically-configured root-boundary authority) is correctly cited.

7. **No duplicate/conflicting bridge work found.**

8. **Project authorization confirmed active and covering** WI-5434
   via `gt projects show-authorization` and `gt projects show`.

9. **Both mandatory preflights pass clean.**

## Required Corrections Before VERIFIED (Non-Blocking for This GO)

1. **[P3] Phantom specification citation.** `GOV-PROJECT-ROOT-BOUNDARY-001`
   (cited in Specification Links) does not exist in MemBase at any
   version — confirmed via `gt spec show` and a direct query. The real,
   mechanically-configured root-boundary authority
   (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) is separately and correctly
   cited. Drop the phantom citation at implementation-report time; this
   does not affect root-boundary compliance, which is independently
   evidenced elsewhere.
2. **[P4] Commit type likely miscategorized.** `Recommended Commit Type:
   feat` doesn't fit a single-file test-assertion repair with no new
   capability. WI-3460's directly analogous precedent used `fix:`.
   Recommend `fix:` or `test:` at implementation-report time.
3. **[P4] Prior Deliberations section present but not maximally
   on-point.** Satisfies the mechanical gate but omits the two most
   directly relevant records: `DELIB-20265679` (WI-3460's VERIFIED
   verdict, which named this exact test) and the WI-3469 basetemp
   isolation thread deliberations (the actual root cause). Cite these in
   the implementation report.

None of these undermine the correctness of the proposed change; they are
traceability/documentation-accuracy corrections required before VERIFIED.

## Specification Links

Carried forward from the proposal, minus the phantom citation flagged
above:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`

`GOV-PROJECT-ROOT-BOUNDARY-001` removed (does not exist in MemBase; see
Required Corrections item 1).

## Required Verification Plan (for the implementation report)

| Test | Current status | Required post-implementation status |
| --- | --- | --- |
| `test_detect_counterpart_state_uses_project_root_paths_when_provided` | FAIL | PASS, via exact sandbox-path-equality assertion |
| `test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted` | PASS | PASS (unchanged) |
| Full `platform_tests/hooks/test_workstream_focus.py` | 75 passed, 3 skipped, 1 failed | 76 passed, 3 skipped, 0 failed |

The implementation report must re-run these exact commands and both
preflights, plus `ruff check` and `ruff format --check` (both, separately)
on the single changed file.

## Prior Deliberations

- `DELIB-20265679` — WI-3460's VERIFIED verdict; directly relevant, names
  this exact failing test as a known unresolved issue at the time.
- WI-3469 pytest-basetemp-session-isolation thread — directly relevant;
  the root cause that made this assertion unsatisfiable.
- `bridge/harness-state-preferences-path-cli-2026-04-28-*.md` (VERIFIED)
  — background context confirming `detect_counterpart_state`'s production
  behavior is already correct.

## Applicability Preflight

- packet_hash: `sha256:98938b6f06a8492e4670982b597471cf880b2a1ed6df7fa592a3923d91a72aab`
- operative_file: `bridge/gtkb-wi5434-inroot-counterpart-fixture-semantics-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

## Methodology Trail

Independently reproduced the target test failure and full-file baseline;
traced the root cause structurally through `conftest.py` and
`pyproject.toml` rather than trusting the proposal's narrative; confirmed
WI-3460 provenance via its backlog record and VERIFIED verdict; confirmed
`GOV-PROJECT-ROOT-BOUNDARY-001` does not exist in MemBase at any version;
confirmed `ADR-ISOLATION-APPLICATION-PLACEMENT-001` correctly covers
root-boundary compliance instead; ran both mandatory preflights; confirmed
project authorization active and covering. Re-ran `gt bridge show
--json --compact` immediately before filing to confirm thread currency
(unchanged: NEW, version 1).
