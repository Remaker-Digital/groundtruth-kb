REVISED

bridge_kind: prime_proposal
Document: gtkb-wi4396-dispatch-suppression-routing
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T16-57-48Z-prime-builder-B-82b7c9
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code headless bridge auto-dispatch session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4396
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_suppression_routing.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4396: Route expected lease-contention suppressions out of `dispatch-failures.jsonl` (REVISED-1)

## Revision Scope

REVISED-1 corrects a `target_paths` scope gap discovered during implementation
prep of the GO'd `-001` proposal (Codex GO at `-002`). The gap is purely a
metadata correction — **the approved design is unchanged**.

**What changed in this revision:**

- **`target_paths` adds `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.**
  The GO'd writer-level routing design (acceptance criterion #1: "`work_intent_already_held`
  is routed to `dispatch-suppressions.jsonl`, NOT `dispatch-failures.jsonl`")
  necessarily moves `work_intent_already_held` records out of `dispatch-failures.jsonl`.
  This breaks a **currently-green** existing test that asserts the *old* (buggy)
  behavior:
  - `platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug`
    (lines 282–285) calls `_record_prime_work_intent_held(...)` directly and then
    asserts via `_failure_records(state_dir)` (which reads `dispatch-failures.jsonl`)
    that the record's `reason == "work_intent_already_held"`. After the fix that
    record lands in `dispatch-suppressions.jsonl`, so the assertion fails.

  The `-001` proposal's Risk/Rollback section already committed to updating "any
  existing test that asserted `work_intent_already_held` appears in
  `dispatch-failures.jsonl` … (both files are in `target_paths`)", but the file
  holding that test was omitted from the `target_paths` metadata. Because the
  implementation-start gate binds to `target_paths` (and `platform_tests/` is a
  protected prefix), the omission is a hard block, not a soft note. This revision
  closes that gap so the existing test can be updated to assert the corrected
  routing.

**Verified baseline at HEAD (this session):**

- `test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug` —
  **PASS** today; **will break** under the fix → must be updated (now in scope).
- `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py::test_prime_dispatch_filters_held_work_intent_and_signs_unheld_batch` —
  **already FAILS at HEAD** for an *unrelated, pre-existing* reason
  (`WorkIntentRegistryError: go_implementation claim requires a prime-builder
  harness; session 'foreground-session' resolves to … role None`) — it fails at
  the trigger-run step, before reaching its line 110–116 routing assertion. This
  is **out of WI-4396 scope** (work-intent registry role-eligibility hardening,
  not failure-log routing). It is therefore intentionally **NOT** added to
  `target_paths` and **NOT** modified here; see § Pre-existing Out-of-Scope
  Observation. Its line 110–116 routing assertion is also semantically stale and
  should be refreshed when that separate failure is addressed.

Everything below carries forward from `-001` unchanged except the Verification
Plan (updated to cover the existing-test maintenance) and the new
§ Pre-existing Out-of-Scope Observation.

## Summary

WI-4396 (P2, `bridge-dispatch`, origin=defect): a last-24h analysis found 1,997 `work_intent_already_held` rows in `dispatch-failures.jsonl` versus 233 `implementation_authorization_packet_failed` rows. The `work_intent_already_held` rows are EXPECTED lease/contention suppressions (`launched: false`, with `holder_session_id` + `holder_ttl_expires_at`); recording them in the failure log makes the dispatch `diagnose` output report normal concurrency as "Recent failures" and buries the real, actionable hook/GOV failures. The fix routes expected lease contention to a separate non-failure audit/metrics surface so the failure log contains only actionable dispatch failures.

- `scripts/cross_harness_bridge_trigger.py` records `work_intent_already_held` (`launched: False`) to `dispatch-failures.jsonl` via the shared `_record_dispatch_failure` writer (`:556`).
- `scripts/single_harness_bridge_dispatcher.py` does NOT duplicate the writer — it REUSES `trigger._record_dispatch_failure`. So **both dispatch substrates funnel through the one `_record_dispatch_failure` function**.
- Critically, NOT all `launched: False` records are expected — `:725` records a real `WorkIntentRegistryError`. So the fix routes by REASON, not by `launched`.

Routing the expected-suppression reasons out of the failure log at the shared `_record_dispatch_failure` chokepoint fixes both substrates at once, preserves the dual-substrate fire-and-forget audit discipline (`.claude/rules/bridge-essential.md` § Dual-Substrate Coexistence), and requires NO change to the `diagnose` reader (it simply reads a now-clean failure log).

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4396 is the backlog authority for this fix (P2 dispatch-diagnostics defect). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one source file + tests), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (owner AUQ 2026-06-14, DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION; includes WI-4396; allows `source`, `test_addition`, `hook_upgrade`, `config`). Updating an existing test to track corrected behavior is `test_addition`-class test maintenance within this bounded authorization.
- **`.claude/rules/bridge-essential.md`** § "Dual-Substrate Coexistence" — both the cross-harness trigger and the single-harness dispatcher honor the same fire-and-forget audit-log discipline (`dispatch-failures.jsonl`). This fix keeps that invariant: it adds a sibling audit surface (`dispatch-suppressions.jsonl`) and routes at the shared chokepoint, so both substrates stay consistent.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the dispatch substrate is bridge-coordination infrastructure; this fix improves its diagnostics without altering `bridge/INDEX.md`, the GO/NO-GO discipline, or any dispatch decision (records are routed, never dropped).
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root under `E:\GT-KB`; the new `dispatch-suppressions.jsonl` lives in the same in-root dispatch state-dir as `dispatch-failures.jsonl`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked diagnostics fix with explicit test coverage.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4396 + the 1,997-vs-233 measurement), triage confirmed it open and localized the chokepoint, the bounded PAUTH authorizes the `source` + `test_addition` work, and `bridge-essential.md` defines the dual-substrate audit invariant the fix preserves. No new or revised formal specification is required. This revision is a `target_paths` metadata correction only and does not change the requirement basis.

## Prior Deliberations

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-4396 (and siblings 3439/3448/3384) under the bounded PAUTH.
- **`bridge/gtkb-wi4396-dispatch-suppression-routing-002.md` (Codex GO)** — the GO this revision builds on; the design is unchanged, only `target_paths` is corrected to cover an existing test the design breaks.
- **`.claude/rules/bridge-essential.md`** § "Dual-Substrate Coexistence" — establishes that both substrates share the `dispatch-failures.jsonl` audit discipline; this fix extends that to a sibling suppressions surface at the shared chokepoint.
- **The shared `_record_dispatch_failure` design** (`single_harness_bridge_dispatcher` reusing `trigger._record_dispatch_failure`) — the existing single-source-of-truth pattern this fix leverages so one branch covers both substrates without divergence.
- _Live semantic deliberation search was not run during authoring (headless dispatch session); prior-decision context was gathered from the GO verdict, the live dispatch source, and the existing test suite instead._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it. The revision is a `target_paths` metadata correction within the existing bounded authorization (it does not expand the authorized mutation classes — `test` work was already authorized).

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-4396 under `PAUTH-…-COMPLIANCE-DISPATCH-BATCH-001` (allowed: `source`, `test_addition`, `hook_upgrade`, `config`; forbids formal-artifact + narrative-artifact mutation). This fix stays within that scope: it edits dispatch source + tests. No formal-artifact or narrative-artifact mutation, no KB mutation.

## Design

In `scripts/cross_harness_bridge_trigger.py`:

1. **New module constants:**
   - `EXPECTED_SUPPRESSION_REASONS = frozenset({"work_intent_already_held"})` — the set of expected, non-actionable lease/contention suppression reasons (extensible; documented as "records that are normal concurrency outcomes, not actionable failures").
   - `DISPATCH_SUPPRESSIONS_FILENAME = "dispatch-suppressions.jsonl"` — the sibling audit surface in the same state-dir, with the same rotation env-var / max-bytes discipline as `dispatch-failures.jsonl`.
2. **Route at the shared chokepoint `_record_dispatch_failure(state_dir, payload)` (`:556`):** when `payload.get("reason") in EXPECTED_SUPPRESSION_REASONS`, append the record to `dispatch-suppressions.jsonl` (same fire-and-forget try/except + rotation) via a thin `_record_dispatch_suppression` helper; otherwise append to `dispatch-failures.jsonl` exactly as today. The routing decision lives in `_record_dispatch_failure` so all existing call sites — in both the trigger and the single-harness dispatcher, which reuses this function — are covered with no call-site changes.
3. **Additive (low-risk) `diagnose` visibility:** add a small `== Expected suppressions ==` section to `_emit_diagnose_summary` that reports a count read from `dispatch-suppressions.jsonl`, keeping the data visible (per Codex `-002` review note: "keep the suppressions file visibly auditable"). The existing "Recent failures" section automatically excludes suppressions because they no longer land in `dispatch-failures.jsonl`.
4. **Records are routed, never dropped:** every suppression remains durably recorded for audit/metrics in the sibling file. No dispatch decision, lease behavior, or signature computation is changed — this is purely a record-destination change.

## Pre-existing Out-of-Scope Observation

`platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py::test_prime_dispatch_filters_held_work_intent_and_signs_unheld_batch`
is **already red at HEAD** with
`WorkIntentRegistryError: go_implementation claim requires a prime-builder harness; session 'foreground-session' resolves to interactive session marker role None (not prime-eligible)`.
This failure occurs at the `run_trigger` step (work-intent acquisition role
eligibility), unrelated to failure-log routing, and is therefore **out of
WI-4396 scope**. Per scoped-change discipline it is NOT bundled into this fix.
Its line 110–116 routing assertion (`work_intent_already_held` in
`dispatch-failures.jsonl`) is also semantically stale and will need refreshing
when the underlying registry-role failure is addressed. **Recommendation:** a
separate work item to (a) repair the work-intent suite fixture's harness-role
eligibility and (b) update its routing assertion to the corrected destination.
This proposal records the observation so it is not silently lost; it does not
implement it.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test | Method |
|---|---|---|
| `work_intent_already_held` is routed to `dispatch-suppressions.jsonl`, NOT `dispatch-failures.jsonl` (WI-4396 root) | `test_work_intent_held_routed_to_suppressions` (new, `test_dispatch_suppression_routing.py`) | call `_record_dispatch_failure` with `reason="work_intent_already_held"` → assert the row appears in `dispatch-suppressions.jsonl` and is ABSENT from `dispatch-failures.jsonl` |
| A real failure reason still goes to `dispatch-failures.jsonl` (no false routing) | `test_real_failure_stays_in_failures` (new) | call with `reason="implementation_authorization_packet_failed"` and a registry-error reason → assert it lands in `dispatch-failures.jsonl`, absent from suppressions |
| Both substrates covered via the shared chokepoint | `test_single_harness_dispatcher_uses_shared_chokepoint` (new) | assert `single_harness_bridge_dispatcher` calls `trigger._record_dispatch_failure` (no independent writer), so routing applies to both |
| Suppressions file honors rotation discipline | `test_suppressions_file_rotates` (new) | exceed the max-bytes threshold → assert `dispatch-suppressions.jsonl` rotates like the failures log |
| `diagnose` "Recent failures" excludes suppressions | `test_diagnose_recent_failures_excludes_suppressions` (new, `test_cross_harness_bridge_trigger_diagnose.py`) | seed a mix of suppression + real-failure records → diagnose "Recent failures" reflects only real failures; `== Expected suppressions ==` reports the suppression count |
| Fire-and-forget: a suppressions-write error never breaks dispatch | `test_suppression_write_failsafe` (new) | unwritable state-dir → `_record_dispatch_failure` returns without raising |
| **Existing-test maintenance:** `_record_prime_work_intent_held` routes to suppressions, not failures | `test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug` (UPDATED, `test_cross_harness_bridge_trigger.py`) | update the existing assertions to read `dispatch-suppressions.jsonl` and assert the dedupe semantics there (preserving the per-holder/per-slug dedupe coverage); confirm the records are ABSENT from `dispatch-failures.jsonl` |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on all changed files; `python -m pytest platform_tests/scripts/test_dispatch_suppression_routing.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` (new + updated suites must pass). The pre-existing unrelated failure in `test_cross_harness_bridge_trigger_work_intent.py` (§ Pre-existing Out-of-Scope Observation) is documented and excluded from this fix's pass criterion.

## Risk / Rollback

- **Risk: low.** One routing branch added to a single chokepoint function + a sibling JSONL file + an additive diagnose section + tests. No dispatch decision, lease/work-intent behavior, signature computation, or selection logic is changed — only the destination of an audit record. Suppression records are routed (still durably recorded), never dropped. The fire-and-forget try/except discipline is preserved for both files.
- **Existing-test impact:** `test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug` asserted the buggy behavior and is updated to assert the corrected routing (now in `target_paths`). The work-intent suite test is a pre-existing unrelated failure, documented and left untouched (§ Pre-existing Out-of-Scope Observation).
- **Rollback:** revert the routing branch + constants + the suppressions helper + the diagnose section, restore the original `test_fab10` assertion, and delete the new test file. The sibling file simply stops being written. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (the failure log polluted by expected concurrency, burying actionable failures in `diagnose`), restoring the failure log's signal. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
