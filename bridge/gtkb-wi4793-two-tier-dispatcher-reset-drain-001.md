NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d13f9026-d253-48b6-a61c-451dd5294846
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4793-two-tier-dispatcher-reset-drain - two-tier dispatcher reset (soft / owner-gated hard) plus graceful drain

bridge_kind: prime_proposal
Document: gtkb-wi4793-two-tier-dispatcher-reset-drain
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4793

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/tests/test_bridge_dispatch_reset.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4793 (Phase 6) adds a two-tier dispatcher reset plus a graceful-drain command as governed `gt bridge dispatch` subcommands. Today the only reset surface is `cross_harness_bridge_trigger.py --reset-recipient <key>` (per-recipient circuit-breaker / clean-slate, hardened in WI-4805). There is no global reset, no soft/hard distinction, and no graceful drain. This proposal adds:

- `gt bridge dispatch reset --soft`: clear ALL transient dispatcher runtime state (circuit breakers, failure counts, last-launch/signature state, quiesce records, stale guard/lease locks, the pid-provenance ledger, spawn-throttle cooldown stamps), PRESERVING the audit trail and any learned-quality KPI.
- `gt bridge dispatch reset --hard --confirm`: owner-gated factory reset = soft reset PLUS wiping computed/learned quality (see the Computed-quality scoping section; that surface is not yet persisted, so the wipe is a reserved, forward-compatible extension point today).
- `gt bridge dispatch drain [--timeout SECONDS]`: graceful drain - set a dedicated drain marker that stops NEW dispatches (without asserting the emergency kill-switch), wait for in-flight lease-holders to finish within the timeout, then force-terminate stragglers.

Placement in the governed `gt bridge dispatch` CLI (not the `cross_harness_bridge_trigger.py` flag surface) is deliberate: the reset/drain operate on dispatcher STATE directories, so they are substrate-agnostic and survive the WI-4848 trigger-to-daemon cutover, and they are exempt-by-construction from the WI-4788 black-box config/state gate (a governed CLI mutates via Python file I/O, not a direct agent Write/Edit).

## Problem detail (for LO review)

- The only reset is per-recipient (`--reset-recipient`). An operator who needs to clear the whole dispatcher (post-incident, post-storm, after a config change) has no single command and would otherwise hand-edit `.gtkb-state` JSON - which the WI-4788 black-box gate now blocks, leaving no governed path.
- There is no graceful drain. Resetting while workers are in-flight orphans their leases and can cause double-dispatch (the reset clears the signature/lease state the live worker still owns). A drain-then-reset sequence is required for a safe full reset.
- The transient surfaces are spread across several files under `.gtkb-state/bridge-poller/` and `.gtkb-state/cross-harness-trigger/` (dispatch-state.json, quiesce-state.json, leases/*.lock, the reset guard, `.gtkb-state/ops/dispatch-provenance/`). An ad hoc reset risks clearing some and missing others; a single governed command makes the surface set explicit and testable.

## Proposed change

1. NEW `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py` - substrate-agnostic core (pure-ish; clock and terminate callable injected for unit testing):
   - `soft_reset(state_dirs, *, dry_run=False) -> ResetResult`: enumerate and clear the transient surfaces - per-recipient circuit_breaker/failure_count/last_launch/signature state in dispatch-state.json, quiesce-state.json records, stale reset-guard and lease `*.lock` files, the pid-provenance ledger (`.gtkb-state/ops/dispatch-provenance`), and spawn-throttle cooldown stamps. PRESERVE dispatch-failures.jsonl (+ .1 rotation), dispatch-diagnostic-post.jsonl, and any learned-quality state. Returns a structured count of what was cleared.
   - `hard_reset(state_dirs, *, dry_run=False) -> ResetResult`: `soft_reset` PLUS clearing computed/learned quality state (reserved; see scoping note). Returns the soft result plus the quality surfaces cleared (zero today).
   - `drain(state_dirs, *, timeout_seconds, now_fn, terminate_fn) -> DrainResult`: write a dedicated drain marker that the dispatch path checks to stop NEW dispatches; poll `read_leases` until no live lease-holder remains or the timeout elapses; then `terminate_fn` the straggler lease pids. Returns drained-vs-terminated pid sets. The default `terminate_fn` is a shared pid-tree terminator factored from the WI-4805 `_terminate_pid_tree` helper (the implementer extracts it to a shared module so both the trigger and this command use one implementation).
2. `groundtruth-kb/src/groundtruth_kb/cli.py` - register `bridge dispatch reset` (`--soft` | `--hard`, `--confirm`, `--dry-run`, `--state-dir`) and `bridge dispatch drain` (`--timeout`, `--state-dir`). `--hard` without `--confirm` is refused with explicit guidance (the owner-gate at the CLI boundary; the destructive factory reset only runs when the operator confirms).
3. `groundtruth-kb/tests/test_bridge_dispatch_reset.py` - spec-derived tests (below).

The implementer MAY slice this (soft + drain first, hard tier second) given the computed-quality dependency; the design is presented whole so the reviewer can judge the full shape.

## Computed-quality scoping (flagged for the reviewer)

Verified against canonical state: there is NO persisted learned/computed-quality surface today. `config/dispatcher/rules.toml` carries STATIC `dispatch_quality` weights (config, not learned), and the only outcome surface is `scripts/ops/dispatch_monitor.py` (the WI-4790 read-only detector, no persisted quality state). So WI-4793's "soft preserves vs hard wipes quality" distinction has no quality state to act on yet. This proposal therefore implements soft reset + drain concretely now and structures `--hard` (owner-gated) as soft + a reserved computed-quality wipe that is a no-op until a learned-quality surface (for example a future dispatch-outcome-tracker, peer-tracked under sp1b) lands. The reviewer should decide: (A) accept the reserved-extension-point design (recommended - the owner-gated factory-reset CLI shape and the soft/drain value are worth landing now, and the quality-wipe becomes a small addition when the surface exists), or (B) NO-GO and defer the hard tier until the outcome-tracker exists.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) - reset/drain are dispatcher operational-control surfaces; placing them in the governed CLI keeps them substrate-agnostic across the trigger-to-daemon cutover.
- SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (specification) - the drain stop-new MUST use a dedicated drain marker and MUST NOT assert `GTKB_NO_CROSS_HARNESS_TRIGGER` (the manual emergency-only kill-switch; reaffirmed by DELIB-20266140).
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 - dispatch-service reliability and operability.
- DCL-DISPATCH-ENVELOPE-RULES-001 - dispatch lifecycle/state rules the reset enumerates.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed as a numbered bridge proposal in the append-only chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - all governing specs cited.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-derived test plan below.
- GOV-STANDING-BACKLOG-001 - WI-4793 is the governing backlog item.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the work is captured as durable artifacts (this thread, the PAUTH, the session AUQ, spec-derived tests).

## Prior Deliberations

- DELIB-20266137 - owner authorization for this dispatcher-reliability drive (Fixes-then-Phases); source authority for WI-4793 under PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26.
- DELIB-20266140 - WI-4804 owner decision; reaffirms the kill-switch stays manual/emergency-only, which constrains the drain stop-new mechanism (dedicated marker, not the kill-switch). The drain pairs naturally with WI-4804's watchdog-dormancy work.
- DELIB-20266104 - watchdog liveness slice (WI-4828); the lease registry the drain polls is the same liveness substrate.
- bridge/gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap-* - the per-recipient clean-slate + `_terminate_pid_tree` helper this generalizes (global soft reset) and reuses (drain force-terminate).
- Deliberation search ("two-tier dispatcher reset soft hard factory graceful drain") surfaced no prior decision on the two-tier reset design itself.

## Owner Decisions / Input

- AskUserQuestion (2026-06-26, this session d13f9026): owner selected "Propose WI-4793 (clean lane)" as the next focus and endorsed scoping the computed-quality surface around the peer's dispatch-outcome-tracker and flagging it for the reviewer. PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26 covers WI-4793.
- The owner-gated hard reset is enforced at runtime by the `--confirm` CLI flag: the destructive factory-reset OPERATION is the operator's explicit confirmed action at invocation time. This proposal authorizes building the CLI; it does not itself execute any reset.

## Requirement Sufficiency

Existing requirements sufficient - WI-4793 (the backlog requirement) + ADR-DISPATCHER-ARCHITECTURE-001 (operational control surface) + SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (drain must not assert the kill-switch) constrain the design. The computed-quality surface is an implementation-pinning detail (a reserved extension point), not a new requirement. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4793 soft reset (clear transient, preserve audit/quality) | test_soft_reset_clears_transient_preserves_audit (new) | After soft_reset on a seeded state set, dispatch-state recipients are clean (no circuit_breaker, no last_launch, signatures None), quiesce records empty, provenance ledger gone; dispatch-failures.jsonl and any quality state are untouched. |
| WI-4793 hard reset = soft + quality wipe (reserved) | test_hard_reset_is_soft_plus_quality_surface (new) | hard_reset performs the soft clear AND invokes the computed-quality wipe path (asserted via the injected/observed quality-surface clear; zero surfaces today, but the path runs). |
| Owner-gate | test_hard_reset_without_confirm_is_refused (new) | `reset --hard` without `--confirm` exits non-zero with guidance and mutates nothing. |
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (drain stop-new) | test_drain_does_not_assert_kill_switch (new) | drain sets the dedicated drain marker and never sets `GTKB_NO_CROSS_HARNESS_TRIGGER`. |
| WI-4793 graceful drain (wait then force-terminate) | test_drain_waits_then_terminates_stragglers (new) | With a seeded live lease past the timeout, drain calls terminate_fn for the straggler pid; with leases that clear before timeout, terminate_fn is not called. |
| dry-run safety | test_reset_dry_run_mutates_nothing (new) | `--dry-run` reports the would-clear set without mutating any file. |
| No-regression | existing dispatcher tests unaffected; ruff check + ruff format --check on changed files | green |

Commands (run pre-report): `python -m pytest groundtruth-kb/tests/test_bridge_dispatch_reset.py -q --tb=short`; `python -m ruff check` then `python -m ruff format --check` on the changed `.py` files.

## Risk / Rollback

- Risk: moderate. Reset is intentionally destructive of TRANSIENT state; mitigations are the drain-first guidance, `--dry-run`, the `--confirm` owner-gate on the hard tier, and explicit preservation of the audit trail. The drain force-terminate reuses the WI-4805 gated pid-tree terminator (best-effort, swallows errors). The computed-quality wipe is a reserved no-op today, so the hard tier cannot accidentally destroy learned state that does not exist.
- Rollback: revert the new `bridge_dispatch_reset.py` module, the `cli.py` subcommand registration, and the new test file; the only prior reset surface (`--reset-recipient`) is untouched. No schema change; append-only KB untouched.
- Out of scope: the WI-4804 watchdog-dormancy/kill-switch-visibility work (separate thread), the WI-4848 daemon cutover, and the learned-quality outcome-tracker itself (the hard-reset quality-wipe consumes it once it exists).

## Recommended Commit Type

feat - adds net-new governed `gt bridge dispatch reset`/`drain` CLI subcommands and the substrate-agnostic reset/drain module.
