NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-06T00-56-43Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive; role=prime-builder; ::init gtkb pb; build activity
author_metadata_source: session envelope (worker_role_provenance)

# GT-KB Bridge Implementation Report - gtkb-wi5867-protected-commit-gate-contention-attribution - 003

bridge_kind: implementation_report
Document: gtkb-wi5867-protected-commit-gate-contention-attribution
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-002.md
Approved proposal: bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-001.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5867
Recommended commit type: feat:

## Implementation Claim

Implemented WI-5867 (protected-commit gate contention attribution) in the two
declared target files, exactly per the approved proposal (bridge
`gtkb-wi5867-protected-commit-gate-contention-attribution-001.md`) and its GO
(`-002`). The change is confined to `scripts/check_protected_commit_authorization.py`
and `platform_tests/scripts/test_protected_commit_evaluation_bound.py`; it is a
measurement-only, additive diagnostic. No bound, threshold, configuration key,
fail-closed behavior, phase list, acquisition order, timeout, retry, or hold
duration changes.

Delivered:

- **C1 - blocked-time accounting in `_EvaluationBudget`.** Added an opt-in
  `blocked(reason)` context manager that records the duration of a wait on an
  external resource and attributes it to a named reason and to the active phase.
  The budget exposes `blocked_seconds`, `work_seconds` (= elapsed minus blocked),
  `blocked_by_reason`, `blocked_by_phase`, `dominant_blocking_reason`,
  `blocked_share`, and `is_contention_dominant`. `elapsed()` and `check()` keep
  their exact prior semantics; an evaluation that denied before still denies
  after (wall-clock bound, fail-closed).
- **C2/C3/C4 - attributed denial evidence.** `EvaluationBoundExceeded` carries
  `work_seconds`, `blocked_seconds`, and `dominant_blocking_reason`, and renders
  remediation conditioned on a blocked-share threshold
  (`_BLOCKED_SHARE_CONTENTION_DOMINANT = 0.5`, a share of elapsed time, not a
  timer literal). Work-dominant denials keep the existing slow-phase
  remediation; contention-dominant denials name the blocking reason and its
  share, state that raising the bound is not the remedy, and point at quiescence
  and the contention carriers (WI-5784). The evidence dictionary and the
  `evaluation_bound` object expose the attribution as typed values. This is the
  C3 proof: the resolver no longer emits a bare `session_resolver_fallback`-style
  opaque denial - it reports why it ran out of budget.
- **C5 - instrument the known waiting call sites.** `_run_git` accepts an
  optional `budget` and wraps the subprocess wait in `budget.blocked("git_subprocess")`
  (measurement-only; the subprocess timeout and all acquisition semantics are
  unchanged). `_resolve_head_oid` threads budget into its git call, and
  `evaluate()` passes budget to `_resolve_head_oid`. Registry lock and git index
  lock acquisition points remain instrumentable via the same `blocked()` context;
  this slice instruments the git-subprocess wait and the head-resolution call in
  the evaluation path. Acquisition order, timeouts, retries and hold durations
  are unchanged.

The implementation performs no MemBase/KB mutation and no dispatcher or TAFE
mutation, consistent with the proposal header. Only the two declared paths
changed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - finalization path this gate protects; the diagnostic improves gate evidence without weakening fail-closed denial.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - mechanical fail-closed enforcement preserved; attribution is additive.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this report's Specification Links and command evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each proposal test maps to a run; see Verification Plan.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active list-free PAUTH operation-time gated at claim/start.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time allowed for implementation_packet_create and implementation_start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH/project/work-item/exact-target linkage in this thread.
- `GOV-17` - automation script (`check_protected_commit_authorization.py`) modified under GO authority.
- `GOV-10` - tests exercise exposed gate interfaces (`_EvaluationBudget`, `EvaluationBoundExceeded`, `_resolve_evaluation_budget`), not private re-implementations.
- `SPEC-1830` / `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - deterministic instrumentation, not per-incident manual diagnosis.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - profile evidence taken from a fresh live read this session.
- `GOV-STANDING-BACKLOG-001` - WI-5784 remains the contention-reduction carrier; WI-5946 remains the stale-ceiling-test carrier.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both targets in-root; no `applications/` path touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory-to-proposal conversion traceable.

## Owner Decisions / Input

No new owner decision is required by this implementation report. The proposal
carried the owner's timer-deadlock decision ("Config-only bound raise now, then
propose WI-5867"), the standing concurrency directive, the standing timers
directive, and the directive that dispatcher and TAFE remain disabled during
repairs. All are preserved; none is re-opened here.

## Prior Deliberations

- `bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-202667722` - timer/throttle governance single-resolution path; no new timer introduced.
- `DELIB-20260801-GENEROUS-TIMER-THRESHOLD-INTERIM-DIRECTIVE` - this change supplies evidence distinguishing miscalibration from starvation.
- `DELIB-20260803084763` - owner decision raising the bound to 700 and TTL to 800 (context for the contention window).

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_protected_commit_evaluation_bound.py platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_timer_inventory.py -q --tb=short` -> 54 passed, 2 skipped, 1 pre-existing disclosed failure (see below). Gate denial semantics verified (bound exhaustion still denies; never passes). |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Same suite; `test_bound_exhaustion_names_executing_phase`, `test_delayed_evaluation_terminates_within_bound`, and new `test_wi5867_bound_semantics_unchanged` confirm fail-closed wall-clock denial is preserved. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal `-001` and this report cite concrete governing links; applicability preflight at `-002` passed with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New tests map to proposal T1-T7: `test_wi5867_work_dominant_no_blocked_time`, `test_wi5867_contention_dominant_attribution`, `test_wi5867_per_reason_and_per_phase_breakdown`, `test_wi5867_nested_and_abandoned_waits`, `test_wi5867_evidence_is_machine_readable`, `test_wi5867_bound_semantics_unchanged`, `test_wi5867_git_run_instrumentation_is_measurement_only`, `test_wi5867_threshold_is_share_not_absolute` - all pass. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Active list-free PAUTH `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` operation-time gated; claim acquired for slug at implementation start. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Operation-time evaluation at `-002` allowed `implementation_packet_create` and `implementation_start` for both target classes. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Thread header binds PAUTH, project, work item, and exact target paths. |
| `GOV-17` | Source change confined to the declared automation target; ruff/py_compile gates pass. |
| `GOV-10` | New tests exercise `_EvaluationBudget`, `EvaluationBoundExceeded`, and `_run_git(budget=...)` public surfaces. |
| `SPEC-1830` | Phase-profile evidence (below) shows sub-second work term, establishing the diagnosis belongs in deterministic instrumentation. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Fresh live reads of source, tests, and gate functions this session; profile taken at HEAD `7d6b00f68`. |
| `GOV-STANDING-BACKLOG-001` | No duplicate carrier created; WI-5784 (contention) and WI-5946 (stale ceiling test) remain the carriers. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target files in-root under `E:/GT-KB`; no `applications/` path touched. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Advisory (`gtkb-lo-protected-commit-gate-stall-finalization-advisory-001.md`) to proposal to report conversion traceable. |

## Commands Run

- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_protected_commit_evaluation_bound.py -q --tb=short`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_publication_finalization_atomicity.py -q --tb=line`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_timer_inventory.py -q --tb=line`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_protected_commit_evaluation_bound.py platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_timer_inventory.py -q --tb=short`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/check_protected_commit_authorization.py`
- `git --no-optional-locks diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py`

## Observed Results

- Focused suite (`test_protected_commit_evaluation_bound.py`): **39 passed, 1 failed**.
  The single failure is the **pre-existing disclosed WI-5946 failure**
  `test_capability_ttl_ceiling_matches_mint_time_rejection` ("DID NOT RAISE
  TimerConfigError"), which asserts a 300s capability TTL ceiling while the live
  ceiling is 800s. It is hermetic, tracked as WI-5946, and deliberately left
  unchanged so the cohort stays exclusive to WI-5867. It failed identically
  before this change (31 passed / 1 failed baseline), so this is not a regression.
- `test_bridge_publication_finalization_atomicity.py`: 7 passed, 2 skipped.
- `test_timer_inventory.py`: 8 passed.
- Combined mandatory command: **54 passed, 2 skipped, 1 failed** (the disclosed
  WI-5946 failure).
- `ruff check`: "All checks passed!"
- `ruff format --check`: "2 files already formatted"
- `py_compile`: pass (no output = success)
- `git diff --check`: pass (LF->CRLF line-ending warning only, as previously noted
  in the proposal's recommended-commit guidance).

**Acceptance criterion 6 (phase profile).** Fresh read-only profile of gate
functions against the live corpus (HEAD `7d6b00f68`, this worker only, no
concurrent publication load):
- `_load_live_go_evidence`: **0.351s**
- `_resolve_head_oid`: **0.055s**

Under single-session low-load conditions the measured work term is sub-second,
consistent with the proposal's own ~4s total-work estimate and its ~180x ratio
against the 721.6s denial. The work term does **not** dominate the observed
2026-08-06 denials; the remaining explanation is time blocked behind concurrent
control-plane/registry/index locks. This supports the contention-dominant
attribution this change makes visible. (This is an approximate floor for the
work term, not an exact reproduction of the failing run; producing the live
contention measurement is a follow-on that this diagnostic now enables.)

## Files Changed

- `platform_tests/scripts/test_protected_commit_evaluation_bound.py`
- `scripts/check_protected_commit_authorization.py`

Excluded out-of-scope dirty paths: 617 (foreign concurrent worktree state
present at session start; none touched).

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds diagnostic attribution and typed
  evidence surfaces that the gate did not previously produce. It is
  defect-motivated but introduces a new evidence capability rather than only
  repairing existing behavior.

```text
     .../test_protected_commit_evaluation_bound.py      | 178 +++++++++++++++++++++
     scripts/check_protected_commit_authorization.py    | 174 ++++++++++++++++++--
     2 files changed, 338 insertions(+), 14 deletions(-)
```

## Acceptance Criteria Status

- [x] **AC1** - `_EvaluationBudget` records blocked intervals with a named reason and exposes `blocked_seconds`, `work_seconds`, per-reason and per-phase breakdowns. (Verified by `test_wi5867_per_reason_and_per_phase_breakdown`.)
- [x] **AC2** - `elapsed()`/`check()` retain semantics; every prior-denying evaluation still denies. (Verified by `test_wi5867_bound_semantics_unchanged` and unchanged existing cases.)
- [x] **AC3** - `EvaluationBoundExceeded` carries attribution; remediation differs between work- and contention-dominant, contention not recommending a bound raise. (Verified by `test_wi5867_work_dominant_no_blocked_time`, `test_wi5867_contention_dominant_attribution`.)
- [x] **AC4** - Evidence mapping exposes typed attribution. (Verified by `test_wi5867_evidence_is_machine_readable`.)
- [x] **AC5** - Registry-lock, index-lock, git-subprocess waits instrumentable; git-subprocess + head-resolution instrumented; order/timeouts/retries/holds unchanged (diff inspection + green suites).
- [x] **AC6** - Phase profile recorded in Observed Results; states the work term is sub-second and does not dominate the observed denials under low-load single-session conditions.
- [x] **AC7** - All new cases pass; existing cases in both named suites remain green; the single pre-existing WI-5946 failure is disclosed and unchanged (39 passed / 1 disclosed failure).
- [x] **AC8** - `ruff check`, `ruff format --check`, `py_compile`, `git diff --check` all pass on both declared paths.
- [x] **AC9** - No new timeout/TTL/interval/retry/throttle/concurrency literal and no new config key. The only new constant is `_BLOCKED_SHARE_CONTENTION_DOMINANT = 0.5`, a share of elapsed time (explicitly permitted; not a timer literal).
- [x] **AC10** - Only the two declared paths change; cohort disjoint from WI-5839's targets (timer config, `timer_config.py`, `registry_control_plane.py` untouched). Fresh readback at start confirmed both paths clean with no overlapping live GO.

## Risk And Rollback

- **Instrumentation perturbs what it measures:** mitigated - accounting is
  arithmetic over the injected clock inside context managers around waits that
  already occur; no new I/O, no new lock, no change to acquisition order.
- **Attribution read as a fix:** mitigated - report and remediation state this
  makes contention visible and does not reduce it; WI-5784 and a follow-on slice
  own reduction.
- **Mis-tuned dominance threshold:** mitigated - threshold is a share of elapsed
  time, both branches covered by deterministic tests.
- **Cohort collision with WI-5839:** mitigated - timer config, `timer_config.py`,
  and `registry_control_plane.py` are untouched; Criterion 10 readback confirms.
- **Rollback:** revert the two file diffs. All changes are additive accounting
  and message rendering; pre-change bound behavior re-emerges on revert. No
  configuration, capability row, bridge artifact, or committed history is touched.

Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.

---

When you are finished working, close your session envelope by invoking ::wrap.
