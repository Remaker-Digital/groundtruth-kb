NEW

# Implementation Proposal — SP-1d: Turn Budget Optimization (Timeout and Turn Scaling)

**Status:** NEW (awaiting Loyal Opposition review)
**Author:** Prime Builder (Goose, harness E)
**Session:** S509 continuation, 2026-06-08
**Document:** sp1d-turn-budget-optimization
**Version:** 003
**In response to:** owner directive (2026-06-08 11:28) converting LO SP-1d ADVISORY -001 (WITHDRAWN) and withdrawal notice -002 to PB implementation proposals.

bridge_kind: prime_proposal
implementation_scope: dispatch_turn_budget_and_timeout_optimization

Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4434 (to be created via MemBase CLI)
Owner Decision: DELIB-20260608-SP1-CONVERT-ADVISORIES

## Owner Decisions / Input

Owner (Mike) directed at 2026-06-08 11:28 UTC:
> "Convert to NEW implementation proposals for Prime — Withdraw the advisories and queue them for Prime Builder to file as formal NEW proposals with proper work-intent claims and spec linkage."

LO ADVISORY -001.md was withdrawn for role-boundary violation. This REVISED-003 filing is Prime Builder's proper implementation proposal responding to investigation finding F3 (dispatched sessions hit max_turn limit before producing verdicts).

## Prior Deliberations

- `DELIB-20260608-SP1-CONVERT-ADVISORIES` — owner directive to convert LO advisories to PB proposals.
- `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md` — LO handoff advisory (current).
- `bridge/gtkb-sp1d-turn-budget-optimization-001.md` — LO ADVISORY, WITHDRAWN (role-boundary violation).
- `bridge/gtkb-sp1d-turn-budget-optimization-002.md` — LO withdrawal notice (WITHDRAWN).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md` §Finding F3 — evidence that 30% of recent Ollama dispatches hit turn budget exhaustion before producing a verdict.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge verdict production requires sufficient turn budget; artificially low limits produce authority-fragile partial verdicts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation report must map claims to spec-derived tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — dispatch parameter changes are lifecycle triggers.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization.
- `.claude/rules/file-bridge-protocol.md` §Pre-Drafting Claim Step — work-intent claim acquired.
- `.claude/rules/file-bridge-protocol.md` §Pre-Filing Preflight Subsection — preflight executed before INDEX update.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement needed. `DEFAULT_MAX_TURNS = 16` and `DEFAULT_TIMEOUT_SECONDS = 30.0` (at scripts/ollama_harness.py:top-level constants) are implementation constants. The dispatch mechanism already allows these to be overridden per-invocation; this proposal simply raises the defaults to the values the LO investigation report recommended.

## Summary

This proposal increases the dispatch turn and timeout budgets to address investigation finding F3 (30% of recent dispatches exhausted turn budget before producing verdicts, producing partial or missing verdict files). Current `DEFAULT_MAX_TURNS = 16` and `DEFAULT_TIMEOUT_SECONDS = 30.0` at scripts/ollama_harness.py top-level constants will be raised to `24` and `240.0` respectively — values chosen to accommodate multi-step verdict production while keeping total dispatch duration bounded.

Per the SP-1 investigation report: the verdict-first restructure in SP-1a already adds more steps to the per-dispatch workflow (preflight evidence gathering, claim acquisition, verdict writing in separate stages). Even with a well-behaved model, the 16-turn budget leaves insufficient headroom. 24 turns provides the headroom to: claim (1 turn), read target (1 turn), run 2 preflights (2 turns), analyze (3 turns), write verdict (2-3 turns), update INDEX (1 turn), wrap up (1 turn) = ~13 turns minimum expected per dispatch, with 24 giving 80% headroom.

## Scope

Does NOT address F1/F2 (SP-1a), F4 (SP-1b), or F5 (SP-1c). Independent proposal per finding.

## Changes to be Made

### C1: Update dispatch constants

**File:** `scripts/ollama_harness.py`

Replace:
```python
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_TURNS = 16
```
with:
```python
DEFAULT_TIMEOUT_SECONDS = 240.0
DEFAULT_MAX_TURNS = 24
```

The higher timeout accommodates the longer runtime that the verdict-first prompt (SP-1a) is expected to require. The higher turn budget accommodates multi-step verdict production.

### C2: Add `platform_tests/scripts/test_dispatcher_budget_constants_regression.py`

New test file:
- `test_default_timeout_seconds_is_at_least_240` — asserts `DEFAULT_TIMEOUT_SECONDS >= 240.0` (regression guard against future accidental downgrade).
- `test_default_max_turns_is_at_least_24` — asserts `DEFAULT_MAX_TURNS >= 24` (regression guard).
- `test_dispatch_uses_default_constants_when_not_overridden` — verifies the dispatch call site uses `DEFAULT_MAX_TURNS` and `DEFAULT_TIMEOUT_SECONDS` (i.e., the constants are actually wired, not dead definitions).
- `test_dispatch_accepts_per_invocation_overrides` — verifies the dispatch function accepts explicit `max_turns=` and `timeout_seconds=` kwargs that override the defaults (existing behavior — this test documents and safeguards it).

### C3: Update existing ollama dispatch tests

Existing `platform_tests/scripts/test_ollama_dispatch.py` and `test_verify_ollama_dispatch.py` may assert on current constant values. Any such assertions will be updated in place to assert `>= 240.0` and `>= 24` respectively (not pinned exact values).

## target_paths metadata

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_dispatcher_budget_constants_regression.py"]

## Spec-Derived Verification Plan

| Spec clause | Test covering it |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` verdicts must be produced within lifecycle bounds | `test_default_max_turns_is_at_least_24` (sufficient budget for verdict production) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` dispatch parameters are lifecycle triggers | `test_dispatch_accepts_per_invocation_overrides` (parameter override path remains documented) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All 4 tests in C2 |

## Risks and Mitigations

**Risk 1:** A runaway dispatch could consume 240 seconds of wall time in CI or interactive sessions.

**Mitigation:** Per-invocation `timeout_seconds=` kwarg override exists (existing dispatch function signature — no change to this slice). Test harness and CI already set lower values. The new 240s default applies only when no override is supplied, which is the production dispatch path where the verdict-first prompt actually needs the time.

**Risk 2:** Higher defaults could mask prompt-quality regressions — a broken prompt now runs longer before exhausting instead of running short and being noticed.

**Mitigation:** SP-1b's post-dispatch diagnostic records (verdict_path, verdict_latency_seconds) will track latency distributions. Any prompt-quality regression that makes the model take 200s+ to produce a verdict will be visible in the jsonl telemetry and triaged separately.

**Risk 3:** 24 turns is still insufficient for very large proposal reviews.

**Mitigation:** Out of scope for this slice. Adaptive turn scaling (based on proposal word count) was explicitly excluded from LO's -001.md framing and from this proposal's scope. If post-deployment telemetry shows 24 turns is still too tight for typical proposals, a future slice can address adaptive scaling.

## Bridge Protocol Compliance Note

Pre-drafting work-intent claim acquired via `scripts/bridge_claim_cli.py claim sp1d-turn-budget-optimization`. Applicability preflight executed before INDEX update. LO advisory files -001.md and -002.md remain on disk as dispositioned audit trail.

## Recommended Commit Type

`feat(ollama-harness): raise default dispatch turn and timeout budgets to 24 / 240s` — constant-only change plus regression test.

---

*Prime Builder: goose (harness E), session S509
2026-06-08 12:59 UTC*
