NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

# GT-KB Bridge Implementation Report - gtkb-wi5869-registry-control-plane-lock-acquisition - 007

bridge_kind: implementation_report
Document: gtkb-wi5869-registry-control-plane-lock-acquisition
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5869-registry-control-plane-lock-acquisition-006.md
Approved proposal: bridge/gtkb-wi5869-registry-control-plane-lock-acquisition-005.md
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

# WI-5869 Implementation Report - registry lock acquisition backoff + jitter + typed timeout

## Implementation Summary

Per approved proposal v005 (GO v006), this implements the WI-5869 remaining
scope: bounded exponential backoff + jitter on the `_RegistryFileLock`
acquisition polling loop, and a typed caller-retryable exception replacing the
bare `TimeoutError`. The fairness queue is explicitly deferred to a follow-on WI
(per proposal v005 F4). The env-var config surface
(`GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS`) is retained. No timer/config TOML file is
mutated (backoff values are in-memory module constants in the declared source
target).

### Changes to `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`

1. **`RegistryFileLockAcquisitionTimeout`** - typed caller-retryable exception
   (subclass of `RegistryControlPlaneError`) raised on acquisition-deadline
   exhaustion, replacing the bare `TimeoutError("timed out acquiring registry
   lock ...")`.

2. **Bounded exponential backoff + jitter** in `_RegistryFileLock.__enter__`:
   the fixed `time.sleep(0.05)` is replaced with a bounded exponential backoff
   (initial 0.05s, factor 2.0, max 1.0s) with jitter, capped so a sleep never
   exceeds the remaining acquisition deadline. Contending waiters now stagger
   naturally instead of hammering the single global lock.

3. **In-memory module constants** `_REGISTRY_LOCK_INITIAL_BACKOFF_SECONDS`,
   `_REGISTRY_LOCK_MAX_BACKOFF_SECONDS`, `_REGISTRY_LOCK_BACKOFF_FACTOR` (no
   config TOML mutation). The `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` env var and
   `_DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS` default are retained unchanged.

4. Lock ordering, exclusivity, acquisition, and release semantics unchanged.

### Changes to `groundtruth-kb/tests/test_registry_control_plane.py`

5. **`test_registry_lock_backoff_and_jitter_stay_under_deadline`** - asserts the
   acquisition loop retries with positive, bounded backoff sleeps that never
   exceed the max backoff.
6. **`test_registry_lock_typed_timeout_exception`** - asserts exhaustion raises
   the typed `RegistryFileLockAcquisitionTimeout` (subclass of
   `RegistryControlPlaneError`) with the expected message.
7. **`test_registry_lock_env_timeout_wiring`** - re-asserts the
   `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS` env wiring after the backoff refactor.

## Fairness-Queue Deferral

A fairness queue / ticket mechanism for the registry lock is explicitly
deferred to a follow-on WI (per proposal v005 F4 disposition). This
implementation scopes to backoff + jitter + typed retry only.

## Fresh Executed Verification (post-commit)

- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q
  --tb=short -k "wi5869 or registry_lock" --timeout=600` -> **4 passed**.
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q
  --tb=short --timeout=900` -> **61 passed**.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py
  groundtruth-kb/tests/test_registry_control_plane.py` -> **All checks passed!**
- `python -m ruff format --check ...` -> **formatted**.
- `python scripts/check_protected_commit_authorization.py --paths
  groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py
  groundtruth-kb/tests/test_registry_control_plane.py --json` -> **status: pass**.

## Target Fidelity

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` SHA-256
  `6D5FE589EBE7DDA6832CF003EAD03AA07FE04E0A2AAAC4062E15862640217440`
- `groundtruth-kb/tests/test_registry_control_plane.py` SHA-256
  `6E53E6FC1174F8DFE84E87F35076B3FCC015242844885DD9E15B41260A193C36`
- Commit: `7d6b00f68`.
- Both targets Git-clean at HEAD.

## Out of Scope (unchanged)

- Fairness queue / ticket mechanism (deferred to follow-on WI).
- Changing lock ordering, exclusivity, or release semantics.
- Timer/config TOML mutation (timer-inventory, protected-commit-timers, or any
  other config file).
- Changing the publication capability TTL or protected-commit evaluation bound
  (WI-5839 / WI-5742 / WI-5841 own those).
- Dispatcher/TAFE, MemBase, database, credential, deployment, release, push,
  history rewrite, destructive cleanup, or unrelated dirty-byte mutation.

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

## Prior Deliberations

- `DELIB-202667722` - timer governance (relaxed-first, config-backed, no
  invisible hard-coded values).
- `DELIB-202667732` / `DELIB-202667721` / `DELIB-202667725` - PAUTH repair
  evidence.
- `bridge/gtkb-wi5869-registry-control-plane-lock-acquisition-005.md` -
  approved proposal.
- `bridge/gtkb-wi5869-registry-control-plane-lock-acquisition-006.md` - GO.

## Request

Request independent Loyal Opposition VERIFIED review of this implementation
report. The backoff + jitter + typed timeout are implemented, tested, and
committed (`7d6b00f68`); all 61 registry tests pass and lint/format are clean.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
