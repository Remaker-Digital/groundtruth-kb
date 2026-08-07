NEW
::init gtkb pb
::open build

# Config-back and relax the work-intent write-contention retry deadline (WI-5971)

bridge_kind: prime_proposal
Document: gtkb-wi5971-work-intent-write-deadline-config-relax
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-08-06 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 235a0cb7-2d12-4241-9951-a54c73c301f8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5971

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source + focused test (timer-governance config-backing; no lock-semantics change)
kb_mutation_in_scope: false
requires_review: true
requires_verification: true

**No KB mutation.** This proposal performs no MemBase write beyond the WI-5971
backlog candidate already captured; the implementation it proposes touches only
the two declared source/test paths. `groundtruth.db` is deliberately NOT in
target_paths.

## Summary

The work-intent claim/finalization write path in
`scripts/bridge_work_intent_registry.py` bounds its SQLite `BEGIN IMMEDIATE`
retry loop with a hard-coded module constant:

```python
WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS: Final[float] = 10.0
```

There is **no environment override** for this deadline. Under sustained
concurrent write load — e.g., the current multi-harness bulk bridge-drain
automation — a claim or an LO atomic-VERIFIED finalization write that cannot win
the single-writer lock within 10 seconds hard-fails with
`WorkIntentWriteContentionError` (`reason=contention_exhausted`,
`phase=begin_immediate`).

This 10s deadline is asymmetric with the analogous **registry control-plane**
lock (`_resolve_registry_lock_timeout` in
`groundtruth_kb/project/registry_control_plane.py`), which resolves a
**generous 300s default that is env-overridable**
(`GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS`) precisely so "sustained concurrent
registry writers wait through … contention instead of hard-failing at the
retired 30s deadline" (per DELIB-202667722 timer governance and WI-5788). The
work-intent deadline was never brought into line with that principle, so it
remains an **invisible hard-coded timer value** — the exact anti-pattern
DELIB-202667722 governs.

Operational impact (observed this session): repeated `contention_exhausted`
failures acquiring work-intent claims, and a cluster of finalization-contention
bridge NO-GOs (`gtkb-wi5939-*`, `gtkb-wi5941-*`, `gtkb-wi5825-*`) where the
implementation substance is green but Loyal Opposition cannot complete the
atomic VERIFIED commit because the write times out. Re-presenting REVISED
reports does not resolve these; the retry budget does.

## Proposed Scope

1. Make `WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS` config-backed via a new
   environment variable `GTKB_WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS`,
   resolved through a helper that mirrors `_resolve_registry_lock_timeout`
   (explicit caller value wins; else env var when present and a positive float;
   else the default), fail-open to the default on unset/malformed input.
2. Raise the **default** from `10.0` to a generous, relaxed-first value aligned
   with the registry-control-plane precedent (proposed default `300.0`), so
   concurrent claim/finalization writers wait through contention bursts instead
   of hard-failing.
3. Keep lock ordering, exclusivity, per-attempt timeout
   (`WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS`), backoff/jitter, and release
   semantics **unchanged**. Only the total-deadline value and its resolution
   path change.
4. Add focused tests asserting: (a) the default is the generous relaxed-first
   value; (b) a valid `GTKB_WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS`
   env value overrides it; (c) unset/malformed env fails open to the default;
   (d) an explicit caller argument still wins.

Out of scope: any change to SQLite `journal_mode` (already WAL), `synchronous`,
lock ordering, the registry-control-plane lock, or the git-commit finalization
sequence. Those are separate levers not required by this bounded fix.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-202667722 (timer governance:
relaxed-first, config-backed, no invisible hard-coded values) and the WI-5788 /
WI-5869 registry-lock precedent already define the contract this change brings
the work-intent deadline into compliance with. No new or revised requirement is
needed; this is a conformance fix, not a new capability.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge-state authority whose atomic VERIFIED finalization writes are blocked by the current deadline; the fix preserves its append-only / fail-closed guarantees.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing specs linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the focused tests below derive from this change and are executed before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-5971 bound to PROJECT-GTKB-HOUSEKEEPING-HARDENING via the whole-project PAUTH.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-5971 recorded as the governed backlog authority for this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact lifecycle preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — no lifecycle transition triggered by this proposal.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; artifact-first delivery.

## Prior Deliberations

- `DELIB-202667722` — timer governance (relaxed-first, config-backed, no invisible hard-coded values); the governing principle this fix conforms to.
- WI-5788 / WI-5869 — the registry control-plane lock precedent: env-backed `GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS`, generous 300s default, bounded backoff + jitter. This proposal applies the same pattern to the work-intent write deadline.
- WI-5784 — introduced the current bounded work-intent write retry (the 10.0s deadline this proposal relaxes).
- WI-5881 — reservation claim-fence CAS primitive (adjacent contention hardening; unchanged here).
- Finalization-contention NO-GO cluster: `bridge/gtkb-wi5939-false-terminal-finalization-recovery-004.md`, `bridge/gtkb-wi5941-deterministic-release-deadline-test-008.md` — green substance, VERIFIED finalization blocked by this contention class.

## Owner Decisions / Input

This proposal is authorized by an owner AskUserQuestion decision on 2026-08-06:
presented with the finding that the recent NO-GO queue is dominated by a
finalization-contention loop cluster, the owner selected **"Fix the root
cause"** — propose reducing Loyal Opposition's atomic-VERIFIED `groundtruth.db`
lock contention (building on the WI-5869 lock-backoff / WI-5881 claim-fence
work) so the cluster can drain. No further owner decision is required to file
this proposal for review. Implementation remains gated on independent Loyal
Opposition `GO`, a matching claim, and an implementation-start packet.

## Specification-Derived Verification Plan

| Spec / requirement | Verification (command) |
| --- | --- |
| Config-backed deadline (default relaxed-first) | `pytest platform_tests/scripts/test_bridge_work_intent_registry.py -k deadline` — asserts default == generous value |
| Env override respected | same suite — sets `GTKB_WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS` and asserts resolution |
| Fail-open on unset/malformed env | same suite — unset and non-float env both resolve to default |
| Explicit caller argument wins | same suite — explicit value overrides env + default |
| No-regression (`GOV-GTKB-...`) | full `pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q` stays green |
| Code-quality gates | `ruff check` AND `ruff format --check` on both target paths |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | clause preflight; both paths under `E:\GT-KB` |

## Acceptance Criteria

- `WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS` is resolved through an
  env-overridable helper (`GTKB_WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS`) with
  a generous relaxed-first default, fail-open on unset/malformed input.
- Lock ordering, exclusivity, per-attempt timeout, backoff/jitter, and release
  semantics are unchanged (diff confined to the deadline constant + its
  resolver + tests).
- The focused suite passes, including the four resolution-precedence tests, and
  the existing work-intent registry tests continue to pass.

## Risk / Rollback

Low risk. The change only lengthens how long a contended writer waits before
giving up; it introduces no new lock, changes no lock ordering, and cannot
deadlock (the per-attempt timeout and bounded backoff are unchanged, and the
total deadline still terminates). The relaxed-first default matches an existing
reviewed precedent. Rollback is reverting the resolver + default to the prior
hard-coded `10.0` and removing the tests. A pathologically long real deadlock
would now surface as a slow wait rather than a fast `contention_exhausted`; this
is the same tradeoff already accepted for the registry-control-plane lock, and
the env var allows an operator to tighten the deadline if needed.

## Recommended Commit Type

`fix:` — repairs a latent defect (an invisible hard-coded 10s timer that
hard-fails legitimate concurrent writers and blocks atomic VERIFIED
finalization), bringing the work-intent write deadline into compliance with the
DELIB-202667722 timer-governance contract already applied to the registry lock.
Diff stat: one constant + one small resolver helper + focused tests; no new
capability surface, no lock-semantics change.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
