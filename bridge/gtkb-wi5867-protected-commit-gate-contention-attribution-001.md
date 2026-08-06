NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# WI-5867 Implementation Proposal — Attribute protected-commit gate elapsed time to work versus contention

bridge_kind: prime_proposal
Document: gtkb-wi5867-protected-commit-gate-contention-attribution
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5867

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_protected_commit_evaluation_bound.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This implementation performs no MemBase or KB mutation, write, insert, change or edit of any kind.

Source advisory: `bridge/gtkb-lo-protected-commit-gate-stall-finalization-advisory-001.md` (2026-07-29).

## Summary

The protected-commit authorization gate denies a commit when its evaluation exceeds a configured wall-clock bound. The bound is measured as pure elapsed time, so an evaluation that spent its budget **blocked behind another session's lock** is reported identically to one that spent its budget **doing work**. The denial text then recommends raising the bound, which is the wrong remedy for starvation and consumes a finite envelope that is nearly exhausted.

This proposal does not change the bound, the fail-closed semantics, or any configured value. It makes the gate report *why* it ran out of budget, so that the correct remedy is chosen and so that the follow-on contention work has data to act on.

## Scope Correction Against The Recorded Work Item

WI-5867's recorded description asks to "add a fail-closed wall-clock bound around the full evaluation (not only git subprocesses); emit phase/progress evidence to distinguish a slow snapshot from a stalled gate".

The bound and the phase evidence are **already implemented**. `_EvaluationBudget` in `scripts/check_protected_commit_authorization.py` is a monotonic wall-clock budget with phase tracking, `_EVALUATION_PHASES` enumerates seven phases, and `EvaluationBoundExceeded` already carries `phase`, `elapsed`, `bound` and `source`. That surface denied two terminal verdicts on 2026-08-06 and named its phase correctly.

What is **not** implemented is the discriminator the description actually asks for: distinguishing "a slow snapshot from a stalled gate". A phase name alone does not do that, because the phase in which the budget expires is the phase that happened to be running, not necessarily the phase that consumed the time. This proposal delivers that discriminator.

## Problem Evidence (fresh measurement, 2026-08-06)

### The denial

```text
FAIL protected-commit authorization
  - <evaluation-bound>: protected-commit evaluation exceeded its configured 700s
    wall-clock bound while executing phase 'per_path'
    evidence error: elapsed: 721.6s
    evidence error: configured bound: 700s
```

Recorded at `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-010.md`; a second finalization was blocked the same day at `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-014.md`.

### The same evaluation costs about four seconds of work

Direct read-only profiling of the gate's own functions against the live repository at HEAD `7d6b00f68`, with a five-path protected cohort and a bridge aggregate of 15,427 files:

| Gate function | Phase | Observed |
|---|---|---|
| `_load_live_go_evidence` | `live_go_evidence` | 0.40s |
| `_load_verified_evidence` | `verified_evidence` | 0.83s |
| `_index_snapshot` (enter) | `index_snapshot` | 0.77s |
| `_registry_commit_assessment` | `registry_assessment` | 0.75s |
| `_staged_index_content_digest` x5 | `per_path` | 0.39s |
| **total measured** | | **~4s** |

Roughly four seconds of work against a 721.6-second denial: a ratio of about 180x. Corpus size does not explain it — the profile ran against the full 15,427-file aggregate and stayed in the sub-second range per phase.

The remaining explanation is time spent waiting rather than working. The configuration file's own measurement note anticipates exactly this: "Run-to-run variance on the pathological corpus (59s -> 84s) comes from concurrent sessions contending for the control-plane lock." The 2026-08-06 finalizations ran while other harness sessions were actively publishing bridge artifacts.

**Disclosure on the measurement:** the profile above was taken under low or no concurrent load, and each function was timed individually rather than through one `evaluate()` call with a live staged set. It therefore establishes an approximate floor for the work term, not an exact reproduction of the failing run. It is sufficient to rule out corpus-bound work as the dominant term; it is not offered as a contention measurement. Producing that measurement is Acceptance Criterion 6.

### Why the current evidence misleads

`_EvaluationBudget.elapsed()` returns `clock() - start`. There is no blocked-time accounting anywhere in the class. Consequently:

- a starved gate and a slow gate produce identical denial evidence;
- the remediation text says "re-run the commit; if this recurs, the phase named above is the slow phase to investigate. Raise `evaluation_bound_seconds`...", which under contention points at a phase that was not slow and at a dial that cannot fix starvation; and
- each such denial consumes headroom in a finite envelope, because the bound must stay strictly below the paired capability TTL of 800s. After WI-5839 raised the bound to 790s, roughly 68s of margin remains in the config-only lane.

## Proposed Design

One slice, confined to two files, adding no configured value and changing no threshold.

### Change 1 — blocked-time accounting in `_EvaluationBudget`

Add an explicit, opt-in accounting context to the budget:

- `blocked(reason: str)` — a context manager that records the duration of a wait on an external resource and attributes it to a named reason (for example `registry_file_lock`, `git_index_lock`, `git_subprocess`). It accumulates into `blocked_seconds`, into a per-reason breakdown, and into a per-phase breakdown.
- `work_seconds` — a derived property equal to `elapsed() - blocked_seconds`.
- `elapsed()` and `check()` keep their current meaning exactly. The bound remains a wall-clock bound and the gate remains fail-closed on exhaustion. **No evaluation that denies today will pass after this change.**

The injected `clock` parameter the class already accepts is used for all new accounting, so the behavior is deterministically testable.

### Change 2 — attributed denial evidence

`EvaluationBoundExceeded` gains `work_seconds`, `blocked_seconds`, and the dominant blocking reason, and renders remediation conditioned on the attribution:

- **work-dominant** (blocked share below a stated threshold): current remediation preserved, naming the slow phase and the bound.
- **contention-dominant**: remediation names the blocking reason and its share, states that raising the bound is not the indicated remedy, and points at retry under quiescence and at the contention carriers (WI-5784 for claim-registry locks). The message must not recommend raising a bound that starvation will defeat.

The evidence dictionary the gate already emits gains the same fields so machine consumers and future measurement work can read the attribution without parsing prose.

### Change 3 — instrument the known waiting call sites

Wrap the acquisition points where the gate can block on another session in `budget.blocked(...)`: registry control-plane lock acquisition, git index lock acquisition, and git subprocess invocations. Instrumentation is measurement-only. It changes no acquisition order, no timeout, no retry behavior, and holds no lock for longer than it does today.

### Explicitly out of scope

- **No change to any bound or configured value**, and **no new configuration key**. This keeps the proposal's cohort disjoint from WI-5839's declared targets (`config/governance/protected-commit-timers.toml`, `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`, `registry_control_plane.py`), which are contended at the time of filing. Any future bound sourced from configuration must come from the centralized timer surface per WI-5806 and `DELIB-202667722`; none is introduced here.
- **No reduction of lock hold time and no change to lock acquisition strategy.** Making contention visible is a prerequisite for fixing it; the fix belongs with WI-5784 and a follow-on slice informed by the data this change produces.
- **No change to fail-closed behavior**, phase list, or the paired bound/TTL invariant.
- No dispatcher or TAFE activation, configuration, or mutation.
- No repair of `test_capability_ttl_ceiling_matches_mint_time_rejection`, which fails today because it asserts a 300s capability TTL ceiling while the live ceiling is 800s. That test lives in a declared target file, but it is a distinct defect tracked as **WI-5946** and is deliberately left alone here so this cohort stays exclusive to WI-5867. Its failure is disclosed in the verification plan below so it is not mistaken for a regression.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the finalization path this gate protects; the gate's denials are what leave terminal VERIFIED uncommitted.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the gate is a mechanical fail-closed enforcement surface; this change preserves that property while improving its evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing links cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed spec-derived evidence required before VERIFIED; mapping below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active list-free PAUTH cited in this header, operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current project authorization controls at operation time.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item and exact target linkage.
- `GOV-17` — automation script modification approval gate; `scripts/check_protected_commit_authorization.py` is governance automation modified under this thread's future GO.
- `GOV-10` — tests exercise the exposed gate interfaces (`_resolve_evaluation_budget`, `_EvaluationBudget`, `EvaluationBoundExceeded`), not private re-implementations.
- `SPEC-1830` and `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — diagnosis belongs in deterministic instrumentation rather than in per-incident session investigation; this change moves a recurring manual diagnosis into the gate itself.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every measurement above derives from a fresh read this session.
- `GOV-STANDING-BACKLOG-001` — WI-5784 remains the separate carrier for claim-registry lock hardening and WI-5946 for the stale ceiling test; no duplicate carrier is created here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable traceability of the advisory-to-proposal conversion.

## Prior Deliberations

- `DELIB-202667722` — timer and throttle governance as a first-class concern with a single resolution path; no new hard-coded or configured timer is introduced here.
- `DELIB-20260801-GENEROUS-TIMER-THRESHOLD-INTERIM-DIRECTIVE` — use generous waits and track evidenced timer or cap miscalibration; this change supplies the evidence that distinguishes miscalibration from starvation.
- `DELIB-20260803084763` — the owner decision that raised the bound to 700 and the TTL to 800.
- `DELIB-20260803084759` — WI-5580 VERIFIED finalization held pending WI-5742 Layer C timer remediation; the same stall class.
- `bridge/gtkb-lo-protected-commit-gate-stall-finalization-advisory-001.md` — the source advisory this proposal converts.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-010.md` and `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-014.md` — the two 2026-08-06 denials.
- `bridge/gtkb-wi5839-capability-ttl-sizing-007.md` — the configured-value raise to 790s and its disclosure that the config-only lane is nearly exhausted.

## Owner Decisions / Input

1. **AskUserQuestion, 2026-08-06, timer deadlock.** Owner answer: **"Config-only bound raise now, then propose WI-5867"** — the authority for filing this proposal as the durable follow-on to the interim bound raise.
2. **Standing owner directive on concurrency** — concurrency and parallelism problems receive a durable platform-wide fix rather than a work-around, with quiescence used only while repairing. This proposal is deliberately the diagnostic half of that durable fix; it does not attempt a work-around, and it does not claim to resolve the contention itself.
3. **Standing owner directive on timers** — be generous with timers and file a correction work item for evidenced undersizing unless already tracked. The bound is tracked by WI-5839 and the lock contention by WI-5784; no duplicate carrier is created.
4. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This proposal does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5867's defect record, the source advisory, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`, `SPEC-1830`, `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and the timer-governance deliberations fully determine this change. The scope correction recorded above narrows the recorded description to the part that is not already implemented; it does not add a new requirement. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan

All tests use the budget's existing injected `clock`, so timing is deterministic and no test sleeps for a real bound.

| Requirement | Behavior under test | Planned coverage |
|---|---|---|
| Bound semantics unchanged | An evaluation whose elapsed time exceeds the bound still raises `EvaluationBoundExceeded`, with identical phase and bound fields; no path passes on timeout | `test_protected_commit_evaluation_bound.py` — existing cases must stay green unmodified |
| Work-dominant attribution | With no blocked intervals recorded, `blocked_seconds` is 0, `work_seconds` equals elapsed, and the denial renders the existing slow-phase remediation | new case |
| Contention-dominant attribution | With a blocked interval covering most of the elapsed budget, the denial reports the blocking reason and its share, and its remediation does **not** recommend raising the bound | new case |
| Per-reason and per-phase breakdown | Blocked intervals recorded under different reasons and phases are attributed to the correct buckets and sum to `blocked_seconds` | new case |
| Nested and abandoned waits | A `blocked` context exited by exception still records its interval and does not corrupt the accounting | new case |
| Evidence is machine-readable | The emitted evidence mapping carries `work_seconds`, `blocked_seconds` and the dominant reason as typed values, not only in prose | new case |
| Instrumentation is measurement-only | Lock acquisition order, timeouts, retry behavior and hold durations are unchanged; verified by diff inspection plus the existing gate suites staying green | `test_protected_commit_evaluation_bound.py`, `test_bridge_publication_finalization_atomicity.py` |
| No new timer literal or configuration key | Diff introduces no timeout, TTL, interval, retry, throttle or concurrency literal and no new config key | diff inspection |

Planned commands after implementation:

```text
python -m pytest platform_tests/scripts/test_protected_commit_evaluation_bound.py platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_timer_inventory.py -q --tb=short
python -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py
python -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py
python -m py_compile scripts/check_protected_commit_authorization.py
git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py
```

**Disclosed pre-existing failure.** `test_protected_commit_evaluation_bound.py::test_capability_ttl_ceiling_matches_mint_time_rejection` fails today and will continue to fail after this change. It asserts a 300s capability TTL ceiling while `_CAPABILITY_TTL_CEILING_SECONDS` is 800; the test is hermetic, so repository configuration cannot influence it. It is tracked as WI-5946 and is deliberately not repaired here. The implementation report will record the suite result as "N passed, 1 pre-existing failure" with that attribution rather than claiming a fully green module.

## Acceptance Criteria

1. `_EvaluationBudget` records blocked intervals with a named reason and exposes `blocked_seconds`, `work_seconds`, a per-reason breakdown and a per-phase breakdown.
2. `elapsed()` and `check()` retain their current semantics; every evaluation that denies before this change still denies after it.
3. `EvaluationBoundExceeded` carries the attribution, and its rendered remediation differs between the work-dominant and contention-dominant cases, with the contention case not recommending a bound raise.
4. The emitted evidence mapping exposes the attribution as typed values.
5. Registry-lock, index-lock and git-subprocess waits are instrumented, with acquisition order, timeouts, retries and hold durations unchanged.
6. The implementation report records a fresh profile of the gate's phases against the live corpus, and states plainly whether the work term or the blocked term dominates, including the load conditions under which the profile was taken.
7. All new cases pass; the existing cases in both named suites remain green; the single pre-existing WI-5946 failure is disclosed and unchanged.
8. `ruff check`, `ruff format --check`, `py_compile` and `git diff --check` pass on both declared paths.
9. No new timeout, TTL, interval, retry, throttle or concurrency literal, and no new configuration key.
10. Only the two declared paths change, and the cohort stays disjoint from WI-5839's declared targets; at implementation-start, fresh readback confirms both paths clean with matching hashes and no live GO from another thread overlapping them.

## Risks And Rollback

- **Risk: instrumentation perturbs the thing it measures.** Mitigated: accounting is arithmetic over the already-injected clock inside context managers around waits that already occur; no new I/O, no new lock, and no change to acquisition order.
- **Risk: attribution is read as a fix.** Mitigated: the proposal states in scope, in the report, and in the remediation text that this makes contention visible and does not reduce it. WI-5784 and a follow-on slice own the reduction.
- **Risk: a mis-tuned dominance threshold mislabels a denial.** Mitigated: the threshold is expressed as a share of elapsed time rather than an absolute duration, so it introduces no timer literal, and both branches are covered by deterministic tests.
- **Risk: cohort collision with WI-5839.** Mitigated: this cohort deliberately excludes the timer configuration file, `timer_config.py` and `registry_control_plane.py`. Criterion 10 re-checks overlap at implementation-start.
- **Rollback:** revert the two file diffs. All changes are additive accounting and message rendering; the pre-change bound behavior is preserved underneath and re-emerges on revert. No configuration, capability row, bridge artifact or committed history is touched.

## Recommended Commit Type

Recommended later implementation type: `feat` — adds diagnostic attribution and typed evidence that the gate does not currently produce. It is defect-motivated, but it introduces a new evidence surface rather than repairing an existing behavior, and no current behavior changes.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
