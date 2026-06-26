NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d13f9026-d253-48b6-a61c-451dd5294846
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4804-killswitch-staleness-visibility - surface a long-set GTKB_NO_CROSS_HARNESS_TRIGGER via a doctor check + first-seen state (visibility, not auto-clear)

bridge_kind: prime_proposal
Document: gtkb-wi4804-killswitch-staleness-visibility
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4804

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_killswitch_staleness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4804 is NARROWED per owner decision DELIB-20266166 to the kill-switch-staleness VISIBILITY half only. The watchdog-dormancy auto-restart half is re-scoped to the WI-4790/WI-4848 daemon program (its own backlog item) - it would duplicate WI-4790's just-VERIFIED `health_response` and has no executor until the WI-4848 daemon lands.

This proposal adds a doctor check plus a first-seen state record that makes a forgotten emergency kill-switch loud:

- `GTKB_NO_CROSS_HARNESS_TRIGGER` (the `LOOP_PREVENTION_ENV_VAR` manual emergency stop, read at `cross_harness_bridge_trigger.py:170`) carries no set-time, so a forgotten assertion silently suppresses ALL dispatch indefinitely (the incident motivating WI-4804: a manual assertion suppressed dispatch for roughly 7h with no current storm).
- New `_check_killswitch_staleness` doctor check: when the env var is observed set, record a first-seen timestamp to a small `.gtkb-state` marker; WARN when it has been set beyond a threshold (default 2h); clear the marker when the env var is unset. It NEVER auto-clears the env var (honors SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 per DELIB-20266140).

## Problem detail (for LO review)

- `GTKB_NO_CROSS_HARNESS_TRIGGER` is the manual operator opt-out that suppresses dispatch. Nothing sets it programmatically (the storm-watchdog explicitly never asserts it, WI-4780), so "never auto-clears" is by design (DELIB-20266140). But a forgotten manual set is invisible: no GT-KB surface flags that dispatch has been globally suppressed for hours.
- The env var carries no set-time, so duration cannot be derived from the var itself. A persisted first-seen marker is required to measure how long it has been set.

## Proposed change

1. `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
   - Pure evaluator `_evaluate_killswitch_staleness(env_set, prior_first_seen_iso, now, threshold_seconds) -> (marker_action, status, age_seconds)`: `marker_action` in {record, clear, keep}; `status` in {pass, warning}. env_set False -> (clear, pass, None). env_set True + no prior -> (record, pass, 0). env_set True + prior, age < threshold -> (keep, pass, age). env_set True + prior, age >= threshold -> (keep, warning, age).
   - `_check_killswitch_staleness(target: Path) -> ToolCheck`: read `GTKB_NO_CROSS_HARNESS_TRIGGER` from the environment; read/write the first-seen marker at `target/.gtkb-state/cross-harness-trigger/killswitch-first-seen.json`; apply the evaluator; perform the `marker_action` (record now / clear / keep); return `ToolCheck(status pass|warning, message)`. The check NEVER modifies the env var.
   - Register the check in the doctor check list alongside the other bridge-dispatch checks.
   - Module constant `_KILLSWITCH_STALENESS_THRESHOLD_SECONDS = 7200` (2h); the implementer may add an env override.
2. `groundtruth-kb/tests/test_doctor_killswitch_staleness.py`: spec-derived tests (below).

Design note for the reviewer: the check WRITES a small runtime marker (records/clears first-seen) as a deliberate side effect of observation - the only way to measure duration given the env var has no set-time (DELIB-20266140). The pure evaluator is the tested core; the I/O (env read, marker read/write) is the thin wrapper. The alternative (the trigger stamps the marker, the doctor only reads) was rejected to keep this a standalone slice that does not touch the WI-4848-deprecating trigger substrate.

## Scope (explicit, per DELIB-20266166)

- IN: kill-switch-staleness visibility (doctor check + first-seen marker).
- OUT: watchdog-dormancy auto-restart (re-scoped to the WI-4790/WI-4848 daemon program as a `health_response` remediation action; its own backlog item). No env-var auto-clear; no spec change.

## Specification Links

- SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (specification) - the kill-switch stays manual/emergency-only; this check NEVER auto-clears the env var, it only surfaces a long-set one. The visibility-not-auto-clear policy is DELIB-20266140.
- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) - dispatch operability; a silently-suppressed dispatcher is a reliability gap.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 (architecture_decision) - the changed file `groundtruth-kb/src/groundtruth_kb/project/doctor.py` is platform package code, correctly in-root (not an application surface), and the first-seen marker lives under in-root `.gtkb-state`; placement satisfies CLAUSE-IN-ROOT.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (governance) - surface stale operational state loudly rather than let it silently mislead.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 - dispatch-service health/observability.
- GOV-FILE-BRIDGE-AUTHORITY-001 - numbered bridge proposal in the append-only chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 / DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - all governing specs cited; spec-derived test plan below.
- GOV-STANDING-BACKLOG-001 - WI-4804 is the governing backlog item.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the work is captured as durable artifacts (this thread, the owner decisions, the PAUTH, spec-derived tests).

## Prior Deliberations

- DELIB-20266166 - THE governing decision: WI-4804 scope split (visibility now, dormancy re-scoped to the daemon program). Supersedes the DELIB-20266140 pairing of the two halves.
- DELIB-20266140 - WI-4804 policy: visibility-not-auto-clear; a first-seen marker + doctor/startup warning; no spec change.
- DELIB-20266137 - drive authorization; PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26 covers WI-4804.
- WI-4790 lineage (slice-1 `dispatch_monitor`, slice-2 `health_response`, slice-3 daemon wiring, WI-4848 cutover) - where the dormancy half is re-homed.
- Deliberation search ("watchdog dormancy auto-restart scheduled task self-heal kill-switch staleness first-seen doctor warning") surfaced DELIB-20266140 and DELIB-20266166 (above); no other prior decision on the visibility mechanism.

## Owner Decisions / Input

- DELIB-20266166 (AskUserQuestion, 2026-06-26): owner chose "Visibility now; dormancy with daemon" - narrows WI-4804 to the kill-switch-staleness visibility doctor check and re-scopes dormancy auto-restart to the daemon program.
- DELIB-20266140 (AskUserQuestion, 2026-06-26): owner chose "Visibility, not auto-clear" - the policy this implements (no env-var auto-clear).
- Session AUQ (2026-06-26, this session d13f9026): owner directed "pick up WI-4804."
- PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26 covers WI-4804.

## Requirement Sufficiency

Existing requirements sufficient - DELIB-20266166 (scope) + DELIB-20266140 (policy) + SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (no auto-clear) fully constrain the change. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| DELIB-20266166 visibility (WARN when long-set) | test_killswitch_staleness_warns_when_set_beyond_threshold (new) | env set + first-seen older than the threshold -> status warning with the age in the message. |
| visibility (pass when fresh) | test_killswitch_staleness_pass_when_recently_set (new) | env set + first-seen within the threshold -> status pass; the marker is recorded on first observation. |
| visibility (pass + clear when unset) | test_killswitch_staleness_clears_marker_when_unset (new) | env unset -> status pass and the first-seen marker is removed. |
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (no auto-clear) | test_killswitch_check_never_mutates_env_var (new) | the check never sets or unsets GTKB_NO_CROSS_HARNESS_TRIGGER. |
| first-seen recorded then stable | test_killswitch_first_seen_recorded_then_stable (new) | first run records now; a later run keeps the SAME first-seen (age grows, not reset). |
| pure evaluator branches | test_evaluate_killswitch_staleness_branches (new) | the 4 evaluator branches (clear / record / keep-pass / keep-warning) return the documented tuples. |
| No-regression | existing doctor tests pass; ruff check + ruff format --check on changed files | green |

Commands (run pre-report): `python -m pytest groundtruth-kb/tests/test_doctor_killswitch_staleness.py -q --tb=short`; `python -m ruff check` then `python -m ruff format --check` on the changed `.py` files.

## Risk / Rollback

- Risk: low. The check is observational and manages a small runtime marker; it never mutates the env var or any canonical state, and the WARN is advisory. Worst case is a stale marker, which is cleared on the next unset observation.
- Rollback: revert the `_check_killswitch_staleness` check, the `_evaluate_killswitch_staleness` evaluator, the doctor registration, and the test. No schema change; append-only KB untouched.
- Out of scope: the watchdog-dormancy auto-restart (re-homed to the daemon program per DELIB-20266166) and any env-var auto-clear (rejected by DELIB-20266140).

## Recommended Commit Type

feat - adds a net-new doctor check (kill-switch staleness visibility) plus a first-seen state record, surfacing a forgotten emergency stop that silently suppresses dispatch.
