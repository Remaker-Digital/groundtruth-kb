REVISED

bridge_kind: implementation_proposal
Document: gtkb-wi4527-go-claim-auto-extend
Version: 003
Responds-To: bridge/gtkb-wi4527-go-claim-auto-extend-002.md
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4527
target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_work_intent_auto_extend.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4527: Auto-extend go-implementation claims while the holder is actively editing (prevent mid-build claim loss)

## Revision Scope

This REVISED-003 addresses the single P1-blocker finding in Codex's NO-GO at `-002` (Finding 1 "Unresolved Draft Template Placeholder"): the `propose_bridge` helper's `pre_populate_prior_deliberations` auto-injected a `Helper-suggested candidates` sub-section with an unresolved fill-in-reason scaffold line BELOW the substantive Prior Deliberations citations I authored in `-001` (lines 62-64 of the filed `-001`). That placeholder is removed in this revision. All substantive Prior Deliberations citations from `-001` are preserved verbatim. No other section is changed: design, target_paths, PAUTH/spec citations, verification plan, risk/rollback, and recommended commit type are identical to `-001`. Codex's "Positive Confirmations" in `-002` already validated the proposal's design as sound; this revision corrects only the surfaced authoring-helper artifact.

## Summary

WI-4527 (P2, `bridge-protocol`, origin=improvement): the go-implementation work-intent claim window (30 min deadline + 10 min grace) is too short for large source-scope builds. On 2026-06-13 harness B's claim on `gtkb-tafe-dispatch-tick-health` (WI-4499) expired mid-build during a multi-module TAFE integration; session `019ec000` re-claimed it and the claim-gated implementation-start gate (`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`) then blocked harness B from finishing its edits, forcing a stand-down. The claim system worked as designed; the default window does not accommodate long active builds.

**Owner cycle-7 AskUserQuestion decision: "Auto-extend while holder is active."** This proposal seeds exactly that: a go-implementation claim is automatically extended while its holder is actively making authorized edits, bounded by the existing 2-hour max-hold cap. Active builds keep their claim; abandoned claims still expire at the cap (auto-extend only rescues live work).

The fix is low-risk by construction because both primitives already exist:
- `bridge_work_intent_registry.extend()` (`:437`) is the proven extension primitive — it advances the deadline by `GO_IMPLEMENTATION_EXTENSION_SECONDS`, increments `extensions_used`, and **raises when the new deadline would exceed `acquired_at + GO_IMPLEMENTATION_MAX_HOLD_SECONDS` (2 h)**. Nothing new is unbounded.
- `implementation_start_gate.py` (`:1020-1024`) already resolves the holder's `session_id` and validates the claim (`work_intent_claim_block_reason`) on **every** protected edit — the natural per-edit activity signal.

So the slice is: on an authorized edit, when the deadline is near, best-effort call the existing capped `extend()`. It is fail-soft (cannot block an edit) and does NOT change the gate's allow/deny verdict.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4527 is the backlog authority for this fix (P2 bridge-protocol reliability improvement).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4527; allows `source` + `test_addition`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the work-intent claim system + implementation-start gate are bridge-coordination infrastructure; this fix keeps active GO-implementation claims alive without altering `bridge/INDEX.md`, the GO/NO-GO discipline, or bridge authority.
- **PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001** — the claim-gated implementation-start gate that blocked the WI-4499 stand-down. This fix PRESERVES that gate's enforcement: auto-extend is a fail-soft side-effect layered AFTER the gate has already authorized an edit; it never changes the gate's allow/deny verdict and never lets an unauthorized session extend or edit.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including the max-hold-cap bound and the gate-verdict-unchanged guard.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked enhancement to a coordination surface; the bounded behavior and owner-chosen scope are recorded.

## Requirement Sufficiency

Existing requirements sufficient. The gap is documented (WI-4527 + the WI-4499 incident), the owner's cycle-7 AUQ chose the auto-extend approach, the bounded PAUTH authorizes the `source` + `test_addition` work, and the existing `MAX_HOLD` cap + `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` define the invariants the fix preserves. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4527 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **Cycle-7 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Auto-extend while holder is active" over "bump the default deadline" and "detector-first", scoping this slice as the root-cause auto-extend (reuse the capped `extend()` on holder activity).
- **`bridge/gtkb-go-impl-claim-timebox` thread** (the go-implementation deadline/grace/extension timebox that this fix builds on) — the existing `extend()` + `MAX_HOLD` machinery is the proven foundation; this slice automates invocation on activity rather than changing the timebox values.
- **`bridge/gtkb-claim-gated-implementation-start` thread** (VERIFIED predecessor for protected-edit claim-holder enforcement, as cited by Codex's `-002` Evidence Reviewed) — the enforcement layer this slice extends with a fail-soft activity hook on the already-authorized edit path; the gate's allow/deny verdict is preserved unchanged.
- _Live semantic deliberation search was not run during authoring of `-001` or this `-003` revision (the `gt deliberations search` ChromaDB freshness/hang caution active this session — itself the subject of WI-4453/WI-4519); prior-decision context gathered from the claim-system code + the incident record + Codex's `-002` Evidence Reviewed citations instead._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4527 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-7 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Auto-extend while holder is active"**, authorizing this auto-extend scope (reuse `extend()` on holder activity, bounded by the 2 h max-hold cap) over the TTL-bump and detector-first alternatives. The fix stays within `source` + `test_addition` and changes no formal artifact, the GO/NO-GO discipline, or the impl-start gate's allow/deny verdict.

## Design

1. **New registry helper `maybe_auto_extend(thread_slug, session_id, *, project_root=None, now=None) -> dict | None`** in `scripts/bridge_work_intent_registry.py` (additive; reuses `extend()`):
   - No-op (returns `None`) unless ALL hold: a claim exists for `thread_slug`; it is held by `session_id`; `claim_kind == go_implementation`; latest bridge status is `GO`; the claim is not lapsed-past-grace.
   - Threshold-gated: only proceeds when the **remaining time to `implementation_deadline` is below a new constant** `GO_IMPLEMENTATION_AUTO_EXTEND_THRESHOLD_SECONDS` (default `GO_IMPLEMENTATION_GRACE_SECONDS`, i.e. 10 min) — so it does NOT extend on every edit, only as the deadline nears.
   - When eligible, calls the existing `extend(thread_slug, session_id, ...)`. On `WorkIntentRegistryError` (e.g. the 2 h cap reached, or a race) it returns `None` (fail-soft) — the existing cap/lapse behavior then governs (the build genuinely exceeded the max hold and must re-claim).
   - Pure reuse of the proven `extend()` ⇒ inherits its `MAX_HOLD` cap and `extensions_used` accounting.
2. **Activity hook in `scripts/implementation_start_gate.py`**: after the gate has resolved `session_id` and confirmed the edit is authorized (`work_intent_claim_block_reason(...)` returns no block, ≈ `:1020-1024`), invoke `maybe_auto_extend(bridge_id, session_id, project_root=root)` inside a `try/except Exception: pass`. This is a **side-effect of an already-authorized edit**: it runs only on the allow path, swallows all errors, and does NOT alter the gate's allow/deny decision or any block reason.

No change to `extend()`'s cap logic, to claim acquisition, to the GO/NO-GO discipline, or to the gate's authorization verdict.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_work_intent_auto_extend.py`) | Method |
|---|---|---|
| Auto-extend fires for an active holder near the deadline (WI-4527 root cause) | `test_auto_extend_when_deadline_near` | claim go-impl, advance time to within threshold, `maybe_auto_extend(holder)` → deadline advanced, `extensions_used` incremented |
| No-op when the deadline is NOT near (no per-edit runaway) | `test_no_extend_when_deadline_far` | fresh claim, `maybe_auto_extend` → record unchanged |
| No-op for a non-holder session (no unauthorized extension) | `test_no_extend_for_non_holder` | `maybe_auto_extend(other_session)` → unchanged, no raise |
| No-op for a draft (non-GO-implementation) claim | `test_no_extend_for_draft_claim` | draft claim → `maybe_auto_extend` returns None, unchanged |
| Fail-soft at the 2 h cap (GOV bound preserved) | `test_auto_extend_fail_soft_at_cap` | near deadline but extend would exceed MAX_HOLD → returns None, no raise; `extension_capped` reflects the cap |
| Bounded by MAX_HOLD (abandoned claims still expire) | `test_repeated_auto_extend_bounded_by_max_hold` | repeated near-deadline auto-extends never push the deadline past `acquired_at + MAX_HOLD` |
| Gate verdict unchanged by auto-extend (PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 preserved) | `test_gate_verdict_unchanged_when_auto_extend_raises` | monkeypatch `maybe_auto_extend` to raise → the impl-start gate's allow/deny result on an authorized edit is identical to baseline (error swallowed, edit not blocked) |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on all changed files; `python -m pytest platform_tests/scripts/test_work_intent_auto_extend.py -q --tb=short`; plus the existing work-intent / implementation-start-gate regression suites must still pass (claim acquisition, extend cap, gate authorization unchanged).

## Risk / Rollback

- **Risk: low (bounded + fail-soft).** Auto-extend reuses the already-VERIFIED `extend()` primitive, which is hard-capped at `MAX_HOLD` (2 h). The new registry helper is additive; the impl-start-gate change is a single `try/except`-wrapped side-effect on the already-authorized edit path. It CANNOT block an edit, change the gate's allow/deny verdict, let a non-holder extend, or push a claim past the 2 h cap. Abandoned claims still expire (auto-extend only rescues active holders).
- **Concurrency:** `extend()` already uses `BEGIN IMMEDIATE` + holder-match + lapse checks; `maybe_auto_extend` adds no new write path beyond that proven transaction.
- **Rollback:** delete `maybe_auto_extend` + the new constant + the gate hook line + the test. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`feat:` — net-new capability (automatic activity-driven claim extension), built on the existing `extend()` primitive; it adds behavior rather than repairing broken behavior (the claim system "worked as designed"). Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
