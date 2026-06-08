NO-GO

# Loyal Opposition Review: gtkb-ollama-dispatch-state-recovery-001

**Verdict:** NO-GO
**Reviewer:** Claude (harness B, session-scoped LO override, manual session 2026-06-08)
**Date:** 2026-06-08

---

## Applicability Preflight

```
preflight_passed: false
missing_required_specs:
  - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  - GOV-FILE-BRIDGE-AUTHORITY-001
packet_hash: sha256:fb1e307f0763da3b01ca82a4be65371b7fffb3f6beac7ee0da70b120c594f036
```

Preflight FAILED. Three blocking specs are missing.

---

## Findings

### FINDING-P0-001 — Missing mandatory cross-cutting Specification Links

The proposal has no `Specification Links` section. The following blocking specs are required:

1. **`GOV-FILE-BRIDGE-AUTHORITY-001`** — Required for all bridge proposals.
2. **`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`** — Mandates spec citation before GO.
3. **`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`** — Mandates spec-to-test mapping.

Additionally, the proposal references the cross-harness trigger behavior spec and the dispatch state loop-prevention contract. Relevant specs from the `gtkb-cross-harness-trigger` family (e.g. `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `REQ-HARNESS-REGISTRY-001`) should be cited.

### FINDING-P0-002 — No Requirement Sufficiency declaration

Missing the mandatory subsection. The proposal should state whether existing specifications are sufficient or whether new specs are required for the retry/circuit-breaker behavior.

### FINDING-P0-003 — No `target_paths` metadata

The proposal modifies `scripts/cross_harness_bridge_trigger.py` but does not list `target_paths`.

### FINDING-P1-001 — Dry-run signature behavior is more nuanced than described

The proposal states "dry-run must never update signature." However, examining the trigger code: the current dry-run behavior writes the dedup signature to prevent spurious re-dispatches within the same trigger invocation cycle. Removing dry-run signature writes may cause dry-runs to trigger real dispatches in some edge cases. The proposal needs to address how dry-run signature tracking is handled post-change, or confirm that suppressing dry-run writes is safe given the current signature-comparison logic.

### FINDING-P1-002 — `exit_code` field not present in current launch dict

The proposal gates on `launch.get("exit_code") == 0` for loyal-opposition but the current `_spawn_recipient()` return dict does not include `exit_code` — it includes `launched` (bool) and PID. The proposal needs to either add `exit_code` tracking (a new field to populate after process completion) or use a different liveness signal. This is a significant implementation gap since the trigger is fire-and-forget and doesn't currently wait for or record the worker exit code.

### FINDING-P2-001 — OLLAMA_RETRY_DELAY_SECONDS not wired to dispatch logic

The env var is defined but the retry logic pseudocode (`should_dispatch = True`) doesn't implement a delay. Either the delay is handled by natural signature-change timing (and should be documented as such) or explicit delay logic is needed.

---

## Required Changes for REVISED

1. Add `Specification Links` table citing:
   - `GOV-FILE-BRIDGE-AUTHORITY-001`
   - `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
   - `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
   - Applicable trigger/dispatch specs
2. Add `Requirement Sufficiency` declaration
3. Add `target_paths: [scripts/cross_harness_bridge_trigger.py]` and test files
4. Address the `exit_code` tracking gap — propose how worker exit codes are captured for the signature-write gate
5. Clarify or remove the dry-run signature suppression edge-case concern
6. Clarify retry delay mechanism

---

## Disposition

The root cause analysis is accurate and the proposed changes address the correct failure modes. The `exit_code`-gating issue is the substantive blocker — the current trigger does not capture worker exit codes at all (it's fire-and-forget). The proposal must resolve this architectural gap. Consider whether the exit-code gate is the right mechanism, or whether the dispatch log (stderr content) should be the success signal instead.

**Priority:** High. Revise and resubmit alongside the prompt-hardening proposal.

---

*Loyal Opposition: Claude harness B, session-scoped LO override*
*Manual LO session 2026-06-08 — gtkb-ollama-dispatch-state-recovery*
