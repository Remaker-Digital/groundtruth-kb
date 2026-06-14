NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4396-dispatch-suppression-routing
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4396
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_suppression_routing.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4396: Route expected lease-contention suppressions out of `dispatch-failures.jsonl`

## Summary

WI-4396 (P2, `bridge-dispatch`, origin=defect): a last-24h analysis found 1,997 `work_intent_already_held` rows in `dispatch-failures.jsonl` versus 233 `implementation_authorization_packet_failed` rows. The `work_intent_already_held` rows are EXPECTED lease/contention suppressions (`launched: false`, with `holder_session_id` + `holder_ttl_expires_at`); recording them in the failure log makes the dispatch `diagnose` output report normal concurrency as "Recent failures" and buries the real, actionable hook/GOV failures. The fix routes expected lease contention to a separate non-failure audit/metrics surface so the failure log contains only actionable dispatch failures.

**Cycle-16 triage (this session) confirms WI-4396 is genuinely OPEN and localizes the fix to a single chokepoint:**

- `scripts/cross_harness_bridge_trigger.py:692-706` records `work_intent_already_held` (`launched: False`) to `dispatch-failures.jsonl` via `_record_dispatch_failure` (`:556`).
- `scripts/single_harness_bridge_dispatcher.py` does NOT duplicate the writer — it REUSES `trigger._record_dispatch_failure` (`:474/581/674/739/758`, and records `work_intent_already_held` at `:859`). So **both dispatch substrates funnel through the one `_record_dispatch_failure` function**.
- The `diagnose` "Recent failures" reporter is in the trigger itself (`:992` `"== Recent failures =="`, reading `dispatch-failures.jsonl`).
- Critically, NOT all `launched: False` records are expected — `:725` records a real `WorkIntentRegistryError`. So the fix must route by REASON, not by `launched`.

Routing the expected-suppression reasons out of the failure log at the shared `_record_dispatch_failure` chokepoint fixes both substrates at once, preserves the dual-substrate fire-and-forget audit discipline (`.claude/rules/bridge-essential.md` § Dual-Substrate Coexistence), and requires NO change to the `diagnose` reader (it simply reads a now-clean failure log).

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4396 is the backlog authority for this fix (P2 dispatch-diagnostics defect). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one source file + tests), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (owner AUQ 2026-06-14, DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION; includes WI-4396; allows `source`, `test_addition`, `hook_upgrade`, `config`).
- **`.claude/rules/bridge-essential.md`** § "Dual-Substrate Coexistence" — both the cross-harness trigger and the single-harness dispatcher honor the same fire-and-forget audit-log discipline (`dispatch-failures.jsonl`). This fix keeps that invariant: it adds a sibling audit surface (`dispatch-suppressions.jsonl`) and routes at the shared chokepoint, so both substrates stay consistent.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the dispatch substrate is bridge-coordination infrastructure; this fix improves its diagnostics without altering `bridge/INDEX.md`, the GO/NO-GO discipline, or any dispatch decision (records are routed, never dropped).
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root under `E:\GT-KB`; the new `dispatch-suppressions.jsonl` lives in the same in-root dispatch state-dir as `dispatch-failures.jsonl`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked diagnostics fix with explicit test coverage.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4396 + the 1,997-vs-233 measurement), cycle-16 triage confirmed it open and localized the chokepoint, the bounded PAUTH authorizes the `source` + `test_addition` work, and `bridge-essential.md` defines the dual-substrate audit invariant the fix preserves. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-4396 (and siblings 3439/3448/3384) under the bounded PAUTH.
- **`.claude/rules/bridge-essential.md`** § "Dual-Substrate Coexistence" — establishes that both substrates share the `dispatch-failures.jsonl` audit discipline; this fix extends that to a sibling suppressions surface at the shared chokepoint.
- **The shared `_record_dispatch_failure` design** (`single_harness_bridge_dispatcher` reusing `trigger._record_dispatch_failure`) — the existing single-source-of-truth pattern this fix leverages so one branch covers both substrates without divergence.
- **WI-4480 (this session's dispatch-starvation detector seed; GO/in-flight)** — adjacent dispatch-observability work; WI-4396 (failure-log signal quality) and WI-4480 (per-entry starvation telemetry) are complementary diagnostics improvements that do not overlap (different surfaces, different record classes).
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live dispatch source instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-4396 under `PAUTH-…-COMPLIANCE-DISPATCH-BATCH-001` (allowed: `source`, `test_addition`, `hook_upgrade`, `config`; forbids formal-artifact + narrative-artifact mutation). This fix stays within that scope: it edits one dispatch source file + tests. No formal-artifact or narrative-artifact mutation, no KB mutation.

## Design

In `scripts/cross_harness_bridge_trigger.py`:

1. **New module constants:**
   - `EXPECTED_SUPPRESSION_REASONS = frozenset({"work_intent_already_held"})` — the set of expected, non-actionable lease/contention suppression reasons (extensible; documented as "records that are normal concurrency outcomes, not actionable failures").
   - `DISPATCH_SUPPRESSIONS_FILENAME = "dispatch-suppressions.jsonl"` — the sibling audit surface in the same state-dir, with the same rotation env-var / max-bytes discipline as `dispatch-failures.jsonl`.
2. **Route at the shared chokepoint `_record_dispatch_failure(state_dir, payload)` (`:556`):** when `payload.get("reason") in EXPECTED_SUPPRESSION_REASONS`, append the record to `dispatch-suppressions.jsonl` (same fire-and-forget try/except + rotation) instead of `dispatch-failures.jsonl`; otherwise append to `dispatch-failures.jsonl` exactly as today. (A thin `_record_dispatch_suppression` helper may hold the suppressions-file write; the routing decision lives in `_record_dispatch_failure` so all existing call sites — in both the trigger and the single-harness dispatcher, which reuses this function — are covered with no call-site changes.)
3. **No change to the `diagnose` reader.** Because the suppression records no longer land in `dispatch-failures.jsonl`, the existing "Recent failures" section (`:992`) automatically reports only actionable failures. (Optional, additive, low-risk: a one-line `== Expected suppressions ==` count read from `dispatch-suppressions.jsonl` may be added so the data remains visible; if added, the existing diagnose test is updated accordingly. The core fix does not require it.)
4. **Records are routed, never dropped:** every suppression remains durably recorded for audit/metrics in the sibling file. No dispatch decision, lease behavior, or signature computation is changed — this is purely a record-destination change.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_dispatch_suppression_routing.py`) | Method |
|---|---|---|
| `work_intent_already_held` is routed to `dispatch-suppressions.jsonl`, NOT `dispatch-failures.jsonl` (WI-4396 root) | `test_work_intent_held_routed_to_suppressions` | call `_record_dispatch_failure` with `reason="work_intent_already_held"` → assert the row appears in `dispatch-suppressions.jsonl` and is ABSENT from `dispatch-failures.jsonl` |
| A real failure reason still goes to `dispatch-failures.jsonl` (no false routing) | `test_real_failure_stays_in_failures` | call with `reason="implementation_authorization_packet_failed"` (and a registry-error reason) → assert it lands in `dispatch-failures.jsonl`, absent from suppressions |
| Both substrates covered via the shared chokepoint | `test_single_harness_dispatcher_uses_shared_chokepoint` | assert `single_harness_bridge_dispatcher` calls `trigger._record_dispatch_failure` (no independent writer), so routing applies to both |
| Suppressions file honors rotation discipline | `test_suppressions_file_rotates` | exceed the max-bytes threshold → assert `dispatch-suppressions.jsonl` rotates like the failures log |
| `diagnose` "Recent failures" excludes suppressions | `test_diagnose_recent_failures_excludes_suppressions` (in `test_cross_harness_bridge_trigger_diagnose.py`) | seed a mix of suppression + real-failure records → diagnose "Recent failures" count/listing reflects only the real failures |
| Fire-and-forget: a suppressions-write error never breaks dispatch | `test_suppression_write_failsafe` | unwritable state-dir → `_record_dispatch_failure` returns without raising |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on all changed files; `python -m pytest platform_tests/scripts/test_dispatch_suppression_routing.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py -q --tb=short` (new + existing diagnose + work-intent suites must pass).

## Risk / Rollback

- **Risk: low.** One routing branch added to a single chokepoint function + a sibling JSONL file + tests. No dispatch decision, lease/work-intent behavior, signature computation, or selection logic is changed — only the destination of an audit record. Suppression records are routed (still durably recorded), never dropped, so no audit data is lost. The fire-and-forget try/except discipline is preserved for both files.
- **Existing-test impact:** any existing test that asserted `work_intent_already_held` appears in `dispatch-failures.jsonl` was asserting the buggy behavior and is updated to assert the corrected routing (test maintenance accompanying the fix; both files are in `target_paths`).
- **Rollback:** revert the routing branch + constants + the suppressions helper, and delete the new test. The sibling file simply stops being written. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (the failure log polluted by expected concurrency, burying actionable failures in `diagnose`), restoring the failure log's signal. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
