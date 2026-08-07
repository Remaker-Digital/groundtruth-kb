NEW
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
Version: 001
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

# Implementation Proposal - Registry control-plane lock acquisition fairness, backoff, and typed retry (WI-5869)

## Problem Statement

The control-plane registry lock (`_RegistryFileLock`, registry_control_plane.py)
is a single global lock at `root/.gtkb-state/sot-registry/control-plane.lock`.
Under sustained parallel width (multiple concurrent bridge publications),
waiters are a thundering herd against that one lock: the acquisition loop polls
with a **fixed `time.sleep(0.05)`** and **no backoff, jitter, or fairness
queue**, and on deadline exhaustion raises a **bare `TimeoutError`** rather than
a caller-retryable typed transient.

The WI-5869 backlog records seven exact recurrences (2026-08-01) where the
former fixed 30s budget was exhausted under real parallel width, stranding or
rejecting healthy publications. A prior change already externalized the
**timeout literal** to `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` with a generous
300s default (per DELIB-202667722 / WI-5788). The **remaining** WI-5869 scope
is the fairness/backoff/jitter and typed-retry classification of the acquisition
loop itself.

## Proposed Fix (remaining WI-5869 scope)

1. **Backoff + jitter on the acquisition polling loop.** Replace the fixed
   `time.sleep(0.05)` with an exponential backoff with jitter (bounded), so
   contending waiters do not hammer the lock at a fixed rate and the herd
   naturally staggers. The backoff must be bounded and must not exceed the
   acquisition deadline; it is tuned from measured behavior per
   DELIB-202667722 (no invisible hard-coded value, no local literal that
   bypasses the governed timer surface).

2. **Typed caller-retryable transient.** On acquisition-timeout exhaustion,
   raise a dedicated typed exception (e.g.,
   `RegistryFileLockAcquisitionTimeout`) that is a `RegistryControlPlaneError`
   subclass and is clearly caller-retryable, instead of a bare
   `TimeoutError("timed out acquiring registry lock ...")`. Callers can then
   classify and retry the transient rather than treating it as a hard failure.

3. **Centralized governed config wiring.** Wire the timeout/backoff values into
   the typed-registry / governed timer surface established by the timer
   governance program (WI-5804/WI-5806), so the values are configuration-backed
   and auditable rather than env-var-only or local literals. The existing
   `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` env var and generous default are
   retained as the fallback path.

## Explicit Response to prior context

This proposal is scoped to the **verified-remaining** WI-5869 delta. The timeout
externalization already present at HEAD (env var + 300s default) is retained and
not regressed. This proposal does NOT change lock ordering, exclusivity,
acquisition, or release semantics; it only changes the contention-wait behavior
and the exhaustion exception type.

## Scope

- Modify `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`:
  `_RegistryFileLock.__enter__` acquisition loop (add backoff + jitter), and add
  the typed `RegistryFileLockAcquisitionTimeout` exception.
- Add focused tests in
  `groundtruth-kb/tests/test_registry_control_plane.py`: (a) backoff advances
  monotonically and stays under the deadline, (b) exhaustion raises the typed
  exception (subclass of `RegistryControlPlaneError`), and (c) the timeout env
  var / config wiring is honored.

## Out of Scope

- Changing lock ordering, exclusivity, or release semantics.
- Changing the publication capability TTL or protected-commit evaluation bound
  (WI-5839 / WI-5742 / WI-5841 own those).
- Dispatcher/TAFE activation, MemBase schema mutation, database, credential,
  deployment, release, push, history rewrite, or unrelated dirty-byte mutation.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-202667722 (timer governance:
relaxed-first, config-backed, no invisible hard-coded values), WI-5869's exact
recurrence evidence, and the typed-registry centralization target (WI-5804/
WI-5806) fully specify this bounded performance correction. No new owner
decision is needed.

## Specification Links

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

## In-Root Placement Evidence

Both targets are inside `E:\GT-KB`:
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`

## Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Backoff/jitter | Instrumented acquisition-loop test | Wait advances monotonically, jittered, and stays under deadline |
| Typed retry | Exhaustion test | Raises `RegistryFileLockAcquisitionTimeout` (subclass of `RegistryControlPlaneError`) |
| Config wiring | Env/config override test | Timeout honored from env var and governed surface; default retained |
| Regression | `pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short` | All existing tests pass |
| Static quality | `ruff check` / `ruff format --check` on both targets | Clean |

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will acquire a fresh claim, pass schema-v3 implementation-start, implement the
backoff/jitter + typed retry + config wiring, and file an implementation report
requesting VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
