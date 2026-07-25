NEW
::init gtkb pb
::open build

# gtkb-wi5671-startup-relay-fail-open — Slice B: startup-relay fail-open on stale-but-valid cache + detached background refresh

bridge_kind: prime_proposal
Document: gtkb-wi5671-startup-relay-fail-open
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-24 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 302c4543-bd90-4fe9-b169-e90390e528b1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (durable registry role is loyal-opposition; session-stated override per DCL-SESSION-ROLE-RESOLUTION-001)

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5671

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The Prime Builder startup-disclosure relay in `scripts/workstream_focus.py` fails closed with `GTKB STARTUP RELAY FAILURE` whenever the harness-scoped cache (`last-user-visible-startup-pb.md`) is stale but otherwise identity-valid. This was diagnosed under WI-5650 (Slice A, observability): the sole prompt-time recovery, `_refresh_startup_relay_cache_bounded`, re-runs the full `_render_role_startup_report` (measured 35–39s) under `STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS = 5.0` — a **hard ceiling** (`_startup_relay_refresh_timeout_seconds()` clamps any env override to `min(value, 5.0)`). The render cannot complete in 5s, so the self-heal is *deterministically* abandoned and the relay fails closed, consuming the first PB turn with an owner-facing failure diagnostic. WI-5650 was authorized only for observability/diagnostics (Slice A), so it correctly resolved without fixing the structural defect. This proposal is the fix (Slice B).

**Change (two edits in the prompt-time relay path only):**
1. **Fail *open* on mere staleness.** In `_startup_gate_response`, when the pointer is `consistent_except_freshness` (identity-intact, content-consistent, only stale), relay the cached disclosure prefixed with an explicit **staleness banner** (naming `generated_at` + the TTL, and directing the reader to derive current state from fresh canonical reads / `::open <activity>`) instead of emitting the `_startup_relay_failure_context` block. Keep fail-*closed* only for genuinely unusable caches: `pointer is None` (missing/empty/malformed) and the content-mismatch case (sha/byte/identity/wrong-role).
2. **Replace the joined 5s synchronous self-heal with a detached background refresh.** Instead of `_refresh_startup_relay_cache_bounded` running the ~35s render in a joined thread capped at 5s (always abandoned, leaving a churning daemon thread), dispatch a fire-and-forget detached refresh that updates the cache for the *next* prompt without blocking the current one.

**Out of scope (explicitly):** reducing the ~35s `_render_role_startup_report` cost is a *separate* lane already owned by WI-4564 (startup-service timeout + inner-cost alignment) and FAB21 (startup load-cost reduction). This proposal is the relay-*reliability* fix only.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — the fresh-session self-initialization disclosure requirement. The defect **violates** it: on every PB interactive session with a stale cache, the required startup disclosure is never delivered. This fix restores delivery. (Source spec of WI-5650 and WI-5671.)
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — the init-keyword relay contract governing the exact `_startup_gate_response` / `_startup_relay_pointer` behavior being modified. The fix changes the stale-cache branch from fail-closed to fail-open-with-banner while preserving the contract for unusable caches.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — state-claims-from-fresh-reads. The staleness banner operationalizes this: rather than silently relaying stale project-state numbers, the banner names the staleness and directs the reader to fresh canonical reads.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `scripts/workstream_focus.py` relay/cache helpers are parity-checked across harness surfaces (`scripts/check_codex_hook_parity.py`). Edits must preserve cross-harness parity; the verification plan runs the parity check.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail/GO-NO-GO discipline; this proposal is filed and verified through the governed bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandates this Specification Links section citing all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — mandates the Project/PAUTH/Work-Item linkage present in the metadata block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandates the spec-to-test mapping in the verification plan below; VERIFIED requires executed spec-derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-5671 is the MemBase backlog authority for this work; the fix is scoped to that WI under project `…SESSION-STARTUP-LATENCY`.

## Prior Deliberations

- `DELIB-20262426` — bridge thread `gtkb-startup-relay-cache-ttl-self-heal` (introduced the 1800s TTL + bounded self-heal mechanism, marked ORPHAN). This proposal amends that mechanism's recovery path; the TTL constant itself is unchanged.
- `DELIB-20264935` — `GO — Startup Relay Cache TTL Self-Heal`. The fail-closed design and the bounded self-heal were deliberate; this proposal preserves the *honesty* intent (via the banner) while fixing the *recovery* path, which the 5s budget made structurally impossible.
- `DELIB-202665935` — owner authorized a *derived repair after the Codex startup relay failed closed on a stale cache*. This is a prior recurrence of exactly this failure class; the present fix is the durable remedy for the PB side.
- `DELIB-202667181` — WI-5650 Slice A owner decision (observability & diagnostic accuracy). Slice A measured the defect (39s render vs 5s budget) but was scoped to diagnostics only; this proposal is the fix Slice A pointed to.
- `DELIB-WI5671-SLICE-B-AUTHORIZATION` — this proposal's authorizing owner decision (see Owner Decisions / Input).

_No previously-rejected approach is being revisited; the fail-open + detached-refresh direction was owner-selected over "raise the cap" (rejected as structurally unworkable) and "capture to backlog" / "broaden to render-cost" (deferred to other lanes)._

## Owner Decisions / Input

This proposal depends on owner approval, captured as `DELIB-WI5671-SLICE-B-AUTHORIZATION` (`source_type=owner_conversation`, `outcome=owner_decision`). AskUserQuestion evidence:

- **AUQ 1 — defect disposition:** "How should I dispose of the startup-relay 5s-budget defect?" → owner chose **"Draft bridge proposal (Recommended)"** (over "Investigate options first" / "Capture to backlog only").
- **AUQ 2 — scope authorization** (after discovering WI-5650 authorized only Slice A observability): "The structural fix is unscoped Slice B work … How do you want to proceed?" → owner chose **"Authorize Slice B fix now (Recommended)"** (over "Capture Slice B to backlog only" / "Broaden to reliability + render-cost"), authorizing creation of WI-5671 + the bounded PAUTH + this proposal, scoped to relay reliability only.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed. The governing requirements already exist and the current implementation *fails* them: `GOV-SESSION-SELF-INITIALIZATION-001` (disclosure must be delivered at fresh-session start), `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (the relay contract), and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (state honesty). This proposal makes the relay actually satisfy those requirements for the stale-but-valid case; it introduces no new capability requiring specification.

## Spec-Derived Verification Plan

Tests added/updated in `platform_tests/hooks/test_workstream_focus.py`, mapped to each linked specification:

| Spec | Test assertion | Expected |
|------|----------------|----------|
| `GOV-SESSION-SELF-INITIALIZATION-001` + `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `_startup_gate_response` on a `consistent_except_freshness` pointer relays the disclosure body (contains `## Startup Disclosure`) and does NOT emit `GTKB STARTUP RELAY FAILURE` | PASS — disclosure delivered |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (fail-closed preserved) | `_startup_gate_response` on `pointer is None` and on a content-mismatch/wrong-role pointer still emits the failure context | PASS — fail-closed only for unusable caches |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | the fail-open relay body contains an explicit staleness banner naming `generated_at` + the TTL and directing to fresh reads | PASS — staleness surfaced, not silent |
| relay-reliability (no synchronous block) | the stale-cache path dispatches a detached refresh and returns without invoking the joined 5s-capped synchronous render | PASS — current prompt not blocked |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `scripts/check_codex_hook_parity.py` passes after the edits | PASS — cross-harness parity preserved |

Execution command (repo venv, reproducible):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py
```

Also run `ruff check` and `ruff format --check` on the changed `.py` files before filing the post-implementation report (separate gates; format is CI-enforced).

## Risk / Rollback

**Risk surface.** (1) Relaying a stale disclosure could present outdated project-state numbers — mitigated by the explicit staleness banner, the disclosure's own "state requires fresh reads" framing, and retaining fail-closed for genuinely unusable caches. (2) Cross-harness parity: `workstream_focus.py` has a parity-checked counterpart — mitigated by applying parity-preserving edits and running `check_codex_hook_parity.py` in verification. (3) Detached refresh must be truly fire-and-forget (no zombie/lock retention) — mitigated by the existing dispatcher fire-and-forget pattern and by asserting the current prompt returns immediately.

**Rollback.** Single-commit revert of `scripts/workstream_focus.py` (+ the test file). No schema, data, or KB mutation (`kb_mutation_in_scope: false`); the TTL constant and cache format are unchanged, so no migration or state cleanup is required on rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5671-startup-relay-fail-open`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs broken relay behavior (fail-closed-on-stale that never recovers) and restores `GOV-SESSION-SELF-INITIALIZATION-001` disclosure delivery. No new capability surface (that would be `feat:`); the detached-refresh mechanism replaces an existing, non-functioning recovery path rather than adding a new one.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
