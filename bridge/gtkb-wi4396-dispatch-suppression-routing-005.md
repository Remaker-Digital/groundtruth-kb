NEW

bridge_kind: implementation_report
Document: gtkb-wi4396-dispatch-suppression-routing
Version: 005
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T18-20-02Z-prime-builder-B-c23315
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch worker; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4396
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_suppression_routing.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4396 Implementation Report: route expected lease-contention suppressions out of `dispatch-failures.jsonl`

## Summary

Implements the GO'd design (`-003` REVISED-1, Codex GO at `-004`) that routes expected lease/contention suppressions out of the actionable `dispatch-failures.jsonl` log into a sibling `dispatch-suppressions.jsonl` audit surface. The fix is applied at the single shared writer `_record_dispatch_failure` and routes **by `reason`** (not by `launched`), so both dispatch substrates — the cross-harness trigger and the single-harness dispatcher (which reuses `trigger._record_dispatch_failure`) — are corrected with no call-site changes, and the real `WorkIntentRegistryError` (`launched: False`) record stays in the failure log.

All four changes are within the GO'd four-path `target_paths`. No source file outside scope, no formal-artifact / narrative-artifact / KB mutation.

## Changes On Disk

1. **`scripts/cross_harness_bridge_trigger.py`** (source):
   - New constants: `DISPATCH_SUPPRESSIONS_FILENAME = "dispatch-suppressions.jsonl"`, `DISPATCH_SUPPRESSIONS_MAX_BYTES_ENV_VAR`, `DEFAULT_DISPATCH_SUPPRESSIONS_MAX_BYTES`, and `EXPECTED_SUPPRESSION_REASONS = frozenset({"work_intent_already_held"})`.
   - `_record_dispatch_failure` now routes `payload["reason"] in EXPECTED_SUPPRESSION_REASONS` to `_record_dispatch_suppression(...)` and returns; otherwise unchanged. This is the single shared chokepoint reused by `single_harness_bridge_dispatcher`.
   - New `_record_dispatch_suppression` writer (mirrors the fire-and-forget try/except + rotation discipline of the failures writer).
   - New `_dispatch_suppressions_max_bytes` (mirrors `_dispatch_failures_max_bytes`) and `_rotate_dispatch_suppressions_if_needed` (mirrors `_rotate_dispatch_failures_if_needed`).
   - New `_read_dispatch_suppression_records` reader and an additive `== Expected suppressions ==` section in `_emit_diagnose_summary` (count + per-reason breakdown). The existing `== Recent failures ==` section now automatically excludes suppressions because they no longer land in the failures log.
2. **`platform_tests/scripts/test_dispatch_suppression_routing.py`** (new, 5 tests): routing root, real-failure no-route, shared-chokepoint reuse (both substrates), rotation discipline, fire-and-forget failsafe.
3. **`platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py`** (updated, +1 test): `test_diagnose_recent_failures_excludes_suppressions` seeds a mix THROUGH the shared writer and asserts the failures count excludes suppressions while the new section reports them.
4. **`platform_tests/scripts/test_cross_harness_bridge_trigger.py`** (updated): `test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug` now asserts the corrected routing (records land in `dispatch-suppressions.jsonl`, ABSENT from `dispatch-failures.jsonl`) while preserving the per-holder/per-slug dedupe coverage; added a `_suppression_records` helper.

Diff stat (source + updated tests): `scripts/cross_harness_bridge_trigger.py +109`, `test_cross_harness_bridge_trigger.py +19/-3`, `test_cross_harness_bridge_trigger_diagnose.py +39`; plus the net-new `test_dispatch_suppression_routing.py`.

## GO Constraint Compliance (`-004`)

| GO constraint (`-004` § Required Implementation Constraints) | How honored |
|---|---|
| Keep implementation within the revised `target_paths` | All 4 files are the GO'd `target_paths`; no out-of-scope file touched. |
| Route by explicit suppression reason (`work_intent_already_held`); not all `launched: false` | Routing keys on `payload["reason"] in EXPECTED_SUPPRESSION_REASONS`. `test_real_failure_stays_in_failures` proves a `launched: False` `work_intent_registry_error` stays in failures. |
| Preserve fire-and-forget logging for both logs | `_record_dispatch_suppression` mirrors the failures writer's `try/except OSError: pass`; `test_suppression_write_failsafe` proves no raise on an unwritable state-dir. |
| Preserve actionable failure logging for real reasons | `implementation_authorization_packet_failed` + registry errors still land in `dispatch-failures.jsonl` (`test_real_failure_stays_in_failures`). |
| Update the existing FAB10 assertion to read the corrected suppressions surface; preserve per-holder/per-slug dedupe | `test_fab10_…` updated to read `dispatch-suppressions.jsonl`, asserts absence from failures, keeps the 1-then-2 dedupe coverage. |
| Do not bundle the out-of-scope work-intent suite role-eligibility failure | `test_cross_harness_bridge_trigger_work_intent.py` is untouched and excluded from the pass criterion (§ Pre-existing Out-of-Scope Observation, `-003`). |

## Specification Links (carried forward from `-003`)

- **GOV-STANDING-BACKLOG-001** — WI-4396 backlog authority (P2 `bridge-dispatch` defect). Single-WI scope; `CLAUSE-VISIBILITY-BULK-OPS` not_applicable.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeded under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (allows `source`, `test_addition`, `hook_upgrade`, `config`). Implementation-start packet `sha256:801eee7a4eee30c08730fb6641348718fa823274e406be39dfa133bf86a36907` issued from the GO `-004` (latest_status GO).
- **`.claude/rules/bridge-essential.md`** § "Dual-Substrate Coexistence" — the fire-and-forget audit-log discipline is preserved for both `dispatch-failures.jsonl` and the new `dispatch-suppressions.jsonl`; routing at the shared chokepoint keeps both substrates consistent.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — dispatch substrate is bridge infrastructure; the fix changes only an audit-record destination, never `bridge/INDEX.md`, the GO/NO-GO discipline, or any dispatch/lease/signature decision (records routed, never dropped).
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / WI / target-path metadata + governing specs concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` in-root under `E:\GT-KB`; `dispatch-suppressions.jsonl` lives in the same in-root dispatch state-dir as `dispatch-failures.jsonl`.

## Spec-to-Test Mapping

| Acceptance criterion | Test | Result |
|---|---|---|
| `work_intent_already_held` routed to `dispatch-suppressions.jsonl`, ABSENT from `dispatch-failures.jsonl` (WI-4396 root) | `test_work_intent_held_routed_to_suppressions` | PASS |
| Real failure reasons (incl. a `launched: False` registry error) still go to `dispatch-failures.jsonl` | `test_real_failure_stays_in_failures` | PASS |
| Both substrates covered via the shared chokepoint (no independent writer) | `test_single_harness_dispatcher_uses_shared_chokepoint` | PASS |
| Suppressions file honors rotation discipline | `test_suppressions_file_rotates` | PASS |
| Fire-and-forget: a suppressions-write error never breaks dispatch | `test_suppression_write_failsafe` | PASS |
| `diagnose` "Recent failures" excludes suppressions; new section reports them | `test_diagnose_recent_failures_excludes_suppressions` | PASS |
| Existing-test maintenance: `_record_prime_work_intent_held` routes to suppressions, dedupe preserved | `test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug` (updated) | PASS |

## Verification Evidence (exact commands + fresh results, this session 2026-06-14T18:5xZ)

- WI-4396 focused suites (proposal pre-file gate):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= \
  platform_tests/scripts/test_dispatch_suppression_routing.py \
  platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py \
  platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug \
  -q --tb=short
12 passed, 1 warning in 1.86s
```

- Full cross-harness trigger suite (regression check):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
78 passed, 1 warning in 6.43s
```

- Ruff lint (all four changed files):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_suppression_routing.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
All checks passed!
```

- Ruff format gate (separate from lint):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same four files>
4 files already formatted
```

### Pre-existing out-of-scope failure (NOT this change)

`platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py::test_prime_dispatch_filters_held_work_intent_and_signs_unheld_batch` is red at HEAD for an unrelated `WorkIntentRegistryError` (harness-role eligibility at the `run_trigger` step), documented in `-003` § Pre-existing Out-of-Scope Observation. It is intentionally NOT in `target_paths`, NOT modified, and excluded from this fix's pass criterion.

## Risk / Rollback

- **Risk: low.** One reason-based routing branch at a single chokepoint + a sibling JSONL writer/rotation + an additive diagnose section + tests. No dispatch decision, lease/work-intent behavior, signature computation, or selection logic changed — only an audit-record destination. Suppression records are routed (still durably recorded), never dropped; fire-and-forget try/except preserved for both files.
- **Rollback:** revert the routing branch + constants + suppression writer/rotation/reader + diagnose section, restore the original `test_fab10` assertion, delete `test_dispatch_suppression_routing.py` and the diagnose test. The sibling file simply stops being written. No migration, schema change, or KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (the failure log polluted by expected concurrency, burying actionable failures in `diagnose`), restoring the failure log's signal. The new suppressions file + diagnose section are the *mechanism* of the repair (records are re-homed, not a standalone feature surface), consistent with the GO'd `-003` proposal's `fix:` classification.

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new AskUserQuestion required to file or verify.

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14) authorizing WI-4396 under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (allows `source`, `test_addition`, `hook_upgrade`, `config`; forbids formal-artifact + narrative-artifact mutation). This fix edits one dispatch source file + tests only. No formal-artifact, narrative-artifact, or KB mutation.

## Prior Deliberations

- **GO verdict `-004`** (Codex, harness A) — the GO on the REVISED-1 proposal `-003`; its six Required Implementation Constraints are honored (table above) and its scope review confirmed adding `test_cross_harness_bridge_trigger.py` is necessary test maintenance.
- **REVISED proposal `-003`** (Prime, harness B) — the GO'd design + four-path `target_paths` this report implements; § Pre-existing Out-of-Scope Observation carried forward.
- **GO verdict `-002`** (Codex, harness A) — original GO on `-001`; design unchanged through the revision.
- **Proposal `-001`** (Prime, harness B) — original design (shared-chokepoint reason-based routing).
- _Live semantic deliberation search not run during authoring (headless bridge auto-dispatch worker); prior-decision context gathered from the live bridge thread (`-001`…`-004`), the live dispatch source, and the existing test suites._

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
