NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4804-kill-switch-staleness-visibility — surface a long-standing dispatch kill-switch via a doctor check (visibility, not auto-clear)

bridge_kind: prime_proposal
Document: gtkb-wi4804-kill-switch-staleness-visibility
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4804

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_kill_switch_staleness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Scope Note (WI-4804 narrowed per DELIB-20266166)

WI-4804 originally paired two halves (DELIB-20266140): a stale-kill-switch visibility warning AND a watchdog-dormancy auto-restart. Per the owner scope-split (DELIB-20266166), the **dormancy auto-restart is re-scoped to the WI-4790/WI-4848 daemon program** (tracked as WI-4852) because it overlaps WI-4790's `health_response` framework and needs the WI-4848 daemon as the executor. THIS proposal implements only the cleanly-standalone half: kill-switch-staleness visibility. No auto-clear of the env var (honors SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001, per DELIB-20266140).

## Summary

`GTKB_NO_CROSS_HARNESS_TRIGGER=1` is the manual operator kill-switch: the cross-harness trigger no-ops immediately when it is set (`cross_harness_bridge_trigger.py:30,153,170`). It is emergency-only/manual by design (`SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`, WI-4780) — nothing sets or clears it programmatically. The gap: a kill-switch left set (a forgotten emergency stop) silently disables cross-harness dispatch indefinitely with no surfaced signal. This proposal adds a doctor check that records a first-seen timestamp when the kill-switch is observed set, WARNs when it has been set beyond a threshold, and clears the record when the env var is unset — making a long-standing emergency-stop loud instead of silent. It never auto-clears the env var.

## Problem detail (for LO review)

- `cross_harness_bridge_trigger.py:170` — `LOOP_PREVENTION_ENV_VAR = "GTKB_NO_CROSS_HARNESS_TRIGGER"`; the trigger no-ops when it is set (comment at `:30,153`). Per `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`, the watchdog never asserts it; there is no programmatic set or clear (confirmed: no `SetEnvironmentVariable` for it anywhere in `scripts/`).
- Because an env var carries no set-time, "has it been set a long time?" requires a recorded first-seen timestamp. The doctor (run at SessionStart and via `gt project doctor`) is the natural always-available, kill-switch-agnostic surface to record/observe it — the doctor is not gated by the kill-switch (only the trigger is), so it still runs and warns while dispatch is disabled.
- Existing dispatch-health doctor checks are registered together at `doctor.py:5691-5693` (`_check_bridge_dispatch_liveness` x2 + `_check_cross_harness_trigger`); the new check joins them.

## Proposed change

1. `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
   - New `_check_kill_switch_staleness(target: Path) -> ToolCheck` (and a module constant `_KILL_SWITCH_STALE_SECONDS = 7200` = 2h, and a `_KILL_SWITCH_FIRST_SEEN_PATH = ".gtkb-state/ops/kill-switch-first-seen.json"`):
     - Reads `GTKB_NO_CROSS_HARNESS_TRIGGER` using the SAME predicate the trigger uses to no-op (set == value `"1"`).
     - **Not set:** if the first-seen record exists, delete it (clears stale state); return `status="pass"` ("cross-harness trigger kill-switch not set").
     - **Set:** read the first-seen record; if absent, create it with the current UTC timestamp (first observation). Compute age. `age >= _KILL_SWITCH_STALE_SECONDS` → `status="warning"` with a message naming the first-seen timestamp and approximate duration, stating dispatch is disabled and that the operator should clear `GTKB_NO_CROSS_HARNESS_TRIGGER` if the emergency has passed (and that this check never auto-clears it, per `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`). `age < threshold` → `status="pass"` ("kill-switch set recently; deliberate manual stop"). The record read/write is fail-soft (a corrupt/unwritable record degrades to recording-now / no crash).
   - Register it: `checks.append(_check_kill_switch_staleness(target))` alongside the dispatch-health checks at `doctor.py:5693`.
2. `platform_tests/scripts/test_doctor_kill_switch_staleness.py` (new, dedicated — matching the per-check doctor-test convention): tests below. The first-seen timestamp is written directly to the state file (past/now) so the threshold branch is deterministic without a clock dependency.

No change to the trigger, the kill-switch semantics, or any auto-clear behavior; the env var stays purely manual.

## Specification Links

- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — the kill-switch is emergency-only/manual; this check surfaces staleness for visibility and explicitly never auto-clears it (per the owner decision).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture; a silently-disabled dispatch lane is a reliability/observability gap this closes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the change stays within the in-root `groundtruth-kb` package (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`) and the in-root test tree; no out-of-root or misplaced artifacts (CLAUSE-IN-ROOT satisfied), and the first-seen bookkeeping file is under the in-root `.gtkb-state/ops/`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — surfacing a stale operational state (a long-set kill-switch) rather than letting it silently persist.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4804 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266140` — owner policy decision for WI-4804: visibility-not-auto-clear (honor SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001).
- `DELIB-20266166` — owner scope-split: kill-switch visibility now (this proposal); watchdog-dormancy auto-restart re-scoped to the WI-4790/WI-4848 daemon program (WI-4852).
- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive.
- Deliberation search ("storm watchdog ... kill switch ...") surfaced the WI-4670/WI-4828 watchdog lineage but no prior decision on a kill-switch-staleness visibility check.

## Owner Decisions / Input

- Authorized by `DELIB-20266140` (policy) + `DELIB-20266166` (scope: visibility-half now), both owner AUQ this session (2026-06-26); `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` covers WI-4804. No further owner decision is required: the check is read-and-surface only (plus its own first-seen bookkeeping); it never auto-clears the kill-switch and changes no dispatch behavior.
- Topology this session: Claude (B) = Prime Builder; Cursor (E) = Loyal Opposition reviewer.

## Requirement Sufficiency

Existing requirements sufficient — `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` (manual/emergency-only) + the owner decisions fully constrain the change (surface staleness; never auto-clear). No new or revised requirement is needed.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (visibility, no auto-clear) | `test_warns_when_kill_switch_set_beyond_threshold` (new) | env set + first-seen older than threshold → `status="warning"`; the env var is NOT modified (no auto-clear). |
| visibility threshold (no nag for a recent deliberate stop) | `test_pass_when_kill_switch_set_recently` (new) | env set + first-seen within threshold → `status="pass"`. |
| clear on unset | `test_clears_first_seen_when_kill_switch_unset` (new) | env unset → first-seen record removed; `status="pass"`. |
| first observation records first-seen | `test_records_first_seen_on_first_observation` (new) | env set + no prior record → record created with a timestamp; `status="pass"` on the first (recent) observation. |
| No-regression | existing doctor checks unaffected; `ruff check` / `ruff format --check` on the changed files | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_doctor_kill_switch_staleness.py -q --tb=short`; `ruff check` then `ruff format --check` on the changed files.

## Risk / Rollback

- Risk: low. The check is observe-and-warn; its only mutation is its own first-seen bookkeeping file under `.gtkb-state`, which is fail-soft and regenerable. It never touches the env var, dispatch state, or dispatch behavior. A WARN (not FAIL) keeps it non-blocking.
- Rollback: remove `_check_kill_switch_staleness`, its registration, the constants, and the test file. No schema change; append-only KB untouched.
- Out of scope: the watchdog-dormancy auto-restart (re-scoped to WI-4852 under the WI-4790/WI-4848 daemon program); any auto-clear of the kill-switch (explicitly rejected by DELIB-20266140); the trigger's no-op behavior (unchanged).

## Recommended Commit Type

`fix:` — closes the silent-disabled-dispatch observability gap (a forgotten kill-switch had no surfaced signal). Adds a non-blocking doctor WARN + fail-soft first-seen bookkeeping; no dispatch-behavior change and no kill-switch auto-clear.
