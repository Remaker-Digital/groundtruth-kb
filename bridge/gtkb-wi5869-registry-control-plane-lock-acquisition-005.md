REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

bridge_kind: prime_proposal
Document: gtkb-wi5869-registry-control-plane-lock-acquisition
Version: 005 (REVISED; exact verification heading for implementation-start)
Responds to: bridge/gtkb-wi5869-registry-control-plane-lock-acquisition-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5869
Related Work Items: WI-5742, WI-5804, WI-5806, WI-5839, WI-5788

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: perf

# REVISED Implementation Proposal - Registry control-plane lock acquisition backoff + typed retry (WI-5869)

## Revision Claim

This REVISED proposal responds to NO-GO v002 and resolves all four findings:

- **F1 (P0):** Added the missing required spec citation
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and re-presented in-root evidence.
- **F2 (P0):** Added explicit numbered-file-chain prose for the
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` clause.
- **F3 (P0):** **Narrowed the config-wiring claim to env-var-only wiring that is
  already present and in-cohort**, removing the out-of-cohort timer/config TOML
  mutation claim. The existing `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` env var and
  `_DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS` default are retained; the backoff/
  poll/jitter parameters introduced by this proposal are **in-memory module
  constants** in the declared source target (no timer/config TOML file is
  mutated), so the declared `target_paths` fully cover the implementation.
- **F4 (P1):** **Explicitly deferred the fairness queue** to a follow-on WI. This
  proposal scopes to backoff + jitter + typed retry only; fairness-queue design
  is recorded as deferred, not silently dropped.

## Problem Statement

The control-plane registry lock (`_RegistryFileLock`) is a single global lock
at `root/.gtkb-state/sot-registry/control-plane.lock`. Under sustained parallel
width, waiters are a thundering herd: the acquisition loop polls with a fixed
`time.sleep(0.05)` and no backoff/jitter, and on deadline exhaustion raises a
bare `TimeoutError` rather than a caller-retryable typed transient.

The WI-5869 backlog records seven exact recurrences (2026-08-01) of the former
fixed 30s budget being exhausted under real parallel width. A prior change
already externalized the **timeout literal** to
`GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` with a generous 300s default (per
DELIB-202667722 / WI-5788). The remaining WI-5869 scope is the acquisition-loop
**backoff + jitter** and **typed-retry classification**.

## Proposed Fix (remaining WI-5869 scope, in-cohort)

1. **Backoff + jitter on the acquisition polling loop.** Replace the fixed
   `time.sleep(0.05)` with a bounded exponential backoff with jitter (capped so
   it never exceeds the acquisition deadline), so contending waiters stagger
   naturally instead of hammering the lock at a fixed rate. The backoff values
   are **in-memory module constants** in `registry_control_plane.py` (the
   declared source target), tuned per DELIB-202667722, and do NOT require any
   timer/config TOML mutation.

2. **Typed caller-retryable transient.** On acquisition-timeout exhaustion,
   raise a dedicated typed exception `RegistryFileLockAcquisitionTimeout`
   (subclass of `RegistryControlPlaneError`), replacing the bare
   `TimeoutError("timed out acquiring registry lock ...")`. Callers can then
   classify and retry the transient.

3. **Retain env-var config wiring (already present, in-cohort).** The existing
   `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` env var and
   `_DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS` default remain the config surface
   for the acquisition deadline. This proposal does NOT add or mutate any
   timer/config TOML file; it only refactors the acquisition loop and exception
   type in the declared source target.

## Explicit Fairness-Queue Deferral (F4)

A fairness queue / ticket mechanism for the registry lock is **explicitly
deferred** to a follow-on work item. This proposal does not claim to implement
fairness; it scopes to backoff + jitter + typed retry only. The residual
fairness gap remains a recorded open concern for a later governed cycle.

## Numbered-File-Chain Prose (F2)

This work appends the next numbered bridge file under `bridge/` (e.g.
`bridge/gtkb-wi5869-registry-control-plane-lock-acquisition-NNN.md`) with the
correct status token and does not delete or rewrite any prior version. The
append-only numbered-file chain is preserved per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`.

## In-Root Placement Evidence (F1)

Both declared targets are inside `E:\GT-KB` per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`:
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`

## Scope

- Modify `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`:
  `_RegistryFileLock.__enter__` acquisition loop (bounded backoff + jitter), and
  add the typed `RegistryFileLockAcquisitionTimeout` exception.
- Add focused tests in `groundtruth-kb/tests/test_registry_control_plane.py`:
  (a) backoff advances monotonically and stays under the deadline, (b) jitter is
  bounded, (c) exhaustion raises the typed exception (subclass of
  `RegistryControlPlaneError`), and (d) the `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS`
  env var wiring is honored.

## Out of Scope

- Fairness queue / ticket mechanism (deferred to follow-on WI).
- Changing lock ordering, exclusivity, or release semantics.
- Timer/config TOML mutation (timer-inventory, protected-commit-timers, or any
  other config file).
- Changing the publication capability TTL or protected-commit evaluation bound
  (WI-5839 / WI-5742 / WI-5841 own those).
- Dispatcher/TAFE activation, MemBase schema mutation, database, credential,
  deployment, release, push, history rewrite, or unrelated dirty-byte mutation.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-202667722 (timer governance:
relaxed-first, config-backed, no invisible hard-coded values), WI-5869's exact
recurrence evidence, and the in-memory module-constant approach fully specify
this bounded performance correction. No new owner decision is needed.

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Backoff/jitter | Instrumented acquisition-loop test | Wait advances monotonically, jittered, bounded, and stays under deadline |
| Typed retry | Exhaustion test | Raises `RegistryFileLockAcquisitionTimeout` (subclass of `RegistryControlPlaneError`) |
| Env config wiring | Env override test | `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` honored; default retained |
| Regression | `pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short` | All existing tests pass |
| Static quality | `ruff check` / `ruff format --check` on both targets | Clean |

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will acquire a fresh claim, pass schema-v3 implementation-start, implement the
backoff/jitter + typed retry, and file an implementation report requesting
VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
