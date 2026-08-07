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
Document: gtkb-wi5938-protected-commit-verified-evidence-memoization
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5938
Related Work Items: WI-5742, WI-5841, WI-5627, WI-5628

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: perf

# Implementation Proposal - Memoize verified-evidence bridge resolution in protected-commit checker

## Problem Statement

The protected-commit authorization gate
(`scripts/check_protected_commit_authorization.py`) can exceed its configured
`evaluation_bound_seconds` (480s) during atomic VERIFIED finalization, blocking
terminal publication for WI-5627, WI-5628, and WI-5841 (observed per-path
110-677s).

Independent profiling (Prime Builder, session G-2026-08-04T22-30-56Z) isolated
the dominant cost to `_load_verified_evidence`: it scans all by-bridge packets
(590 in the current repo), and for each packet that could authorize a protected
path (22 of 590 for a typical source path), it runs a **full
`_bridge_snapshot` + `_immutable_snapshot` + `resolve_bridge_lifecycle` +
`_approved_chain` + `_verify_snapshot_ledger`** (~0.35-0.66s each, re-reading
the entire bridge ledger ~2,657 opens / 1,268 read_bytes). There is **no
dedup/memoization cache across packets or protected paths**, so the same bridge
thread is re-resolved once per matching packet per path, compounding into the
multi-hundred-second blowup.

Measured: a 2-path check took 5.08s total, of which `_load_verified_evidence`
was 3.36s for a single protected path.

## Proposed Fix

Add an **invocation-scoped memoization cache** keyed by `bridge_id` inside
`_load_verified_evidence` (and, if needed, a matching scope guard in `evaluate`),
so each bridge thread's resolution result (the `_bridge_snapshot` +
`resolve_bridge_lifecycle` + `_approved_chain` output, or its failure) is
computed **once per invocation** and reused across all matching packets and
protected paths.

Design principles (mirroring the existing `registry_snapshot_cache_scope`
pattern from WI-5742):

- The cache is **invocation-scoped only**: it is created at the start of a
  single `evaluate()` run and discarded on exit. It is never process-global and
  never outlives the invocation, so no stale-authority window is opened for
  mutating callers (the exact property that rejected a global cache in
  WI-5742).
- The memoized value preserves the exact per-resolution semantics used by the
  downstream `_packet_binding_errors` check: the approved chain
  (`chain.target_paths`) and any per-resolution blocking diagnostics.
- A resolution that raised (`BridgeLifecycleResolutionError`, `GateError`,
  `OSError`, `ValueError`) is also memoized (as a typed failure) so the
  error-append path is not re-executed.
- All fail-closed behavior is unchanged: the same evidence routes, the same
  error messages, the same pass/fail verdict.

## Scope

- Modify `scripts/check_protected_commit_authorization.py`:
  `_load_verified_evidence` (add the bridge_id memo cache), and `evaluate`
  (establish/enter the invocation scope so the cache is created once and
  discarded).
- Add focused tests in
  `platform_tests/scripts/test_check_protected_commit_authorization.py`
  asserting: (a) a single invocation resolves each bridge_id exactly once
  (instrumentable via a counter on the resolution path), (b) the pass/fail
  verdict is identical to the unmemoized path, and (c) the cache does not leak
  across invocations.

## Out of Scope

- Changing `evaluation_bound_seconds` / `bridge_publication_capability_ttl_seconds`
  values (a separate timer-config decision; this fix makes the bound not be hit).
- Any change to `_registry_commit_assessment`, `_evaluate_protected_path`,
  `_verified_bridge_finalization_finding`, or other phases (already minor).
- Dispatcher/TAFE, MemBase, database, credential, deployment, release, push,
  history rewrite, or unrelated dirty-byte mutation.

## Requirement Sufficiency

Existing requirements sufficient. WI-5742 (bound + invocation cache pattern),
GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, and the current protected-commit
authorization spec fully specify this bounded performance correction. No new
owner decision, timer value, or dispatcher contract is needed.

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
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Invocation-scoped dedup | Instrumented resolution-counter test | Each bridge_id resolved exactly once per invocation |
| Verdict identity | Parallel unmemoized vs memoized run | Identical pass/fail and findings |
| Cache non-leak | Two sequential invocations | Second invocation does not reuse first's cache |
| Regression | `pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | All existing tests pass |
| Static quality | `ruff check` / `ruff format --check` on both targets | Clean |

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will acquire a fresh claim, pass schema-v3 implementation-start, implement the
invocation-scoped memoization, and file an implementation report requesting
VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
