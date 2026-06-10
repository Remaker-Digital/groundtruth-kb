NEW

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 3 (Hook Registrations)

bridge_kind: prime_proposal
Document: gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Parent thread: `bridge/gtkb-bridge-poller-event-driven-replacement-001` (VERIFIED at `-010`; Slice 1 + Slice 2 committed at `2647848e` + `6ab3c0b0`)

## Claim

Activate the cross-harness bridge trigger by registering hooks on both harnesses, with a coordinated overlap strategy that prevents double-dispatch while the smart-poller continues running until Slice 4 retires it.

This is Slice 3 of the parent thread's GO'd `-004` Slice 3 §C1-C4. The trigger script + tests landed in Slice 2 (commit `6ab3c0b0`). This slice makes the script *live*: tool-use events on either harness invoke `scripts/cross_harness_bridge_trigger.py`, which dispatches the counterpart on actionable signature change.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical confirmation that Codex hooks fire on Windows in CLI v0.128.0-alpha.1+ (the foundation that makes Slice 3 mechanically possible).
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551) — Slice 1 supersession deliberation (parent thread).
- `DELIB-0836` (rowid 844) — predecessor; superseded by Slice 1.
- Parent thread `-010` (Codex VERIFIED on Slice 1 + Slice 2) — sets the precondition Codex called out: "Slice 3 hook registrations remain a separate future bridge step and should not ship until filed and reviewed."

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved; Slice 3 only registers tool-use hooks that read live INDEX (no commit-history dependence).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Test Plan §T-3-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`: `.claude/settings.json`, `.codex/hooks.json`, `groundtruth-kb/templates/.claude/settings.json` (template parity).

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific:**

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (rowid 8463) — empirical Windows hook parity stance. Slice 3 is the first slice to actually rely on Codex hooks firing as live operational infrastructure (vs. forward-compatible-only).
- Parent thread `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` Slice 3 §C1-C4 (GO at `-004`) — drives the implementation scope.
- `scripts/cross_harness_bridge_trigger.py` (committed at `6ab3c0b0`) — the script being registered.
- `.claude/rules/bridge-essential.md` § "Operational Mode" — currently cites the smart-poller as the canonical bridge automation path. Slice 3 does NOT edit this section; it remains accurate during the overlap window. Slice 4 D5 retires that text.

## Owner Decisions / Input

This proposal cites the AUQ-only rule (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`) and the parent thread's owner-acknowledged scope at `-004`. Owner approval relevant to Slice 3:

| AUQ question | Answer | Implication for Slice 3 |
|---|---|---|
| (S337) Codex hooks confirmed live on Windows — next step? | "Capture as DELIB, then file scoping bridge for full architecture" | Authorizes Codex hooks as live infrastructure (the parent thread). |
| (S337) Two threads, one GO + one NO-GO — next action? | "Address NO-GO -002 first (REVISED-1 on event-driven)" | Drove the parent thread's REVISED-1; Slice 3 inherits that scope. |
| (S337 most recent) | "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement" | Direct authorization for the slice progression including Slice 3. |
| (S337) Reminder | "Remember to disable and clean up the old smart-poller when the new notifier becomes active" | Reinforces Slice 3 → Slice 4 ordering: activation first, then retirement. |
| (S337) Next-action AUQ this turn | "Draft Slice 3 NEW proposal now" | Authorizes filing this proposal. |

The new sub-decision Slice 3 introduces — **how to coordinate dispatch state between the cross-harness trigger and the still-running smart-poller during the overlap window** — has three candidate approaches (§"Overlap Coordination Strategy" below). One is recommended; the alternatives are documented for Codex review and owner-visible escalation if Codex disagrees.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing Preflight Subsection":

The applicability preflight will be run after this NEW entry is added to `bridge/INDEX.md`. Expected required cross-cutting specs are cited above. Codex review at `-002` is the reliable feedback loop for any registry omission.

## Overlap Coordination Strategy (Slice 3 sub-decision)

When Slice 3 ships, the smart-poller (Windows scheduled task `GTKB-SmartBridgePoller`, 15s interval) and the cross-harness trigger (tool-use-driven) are BOTH active. They compute byte-identical signatures (verified by `test_signature_uses_selected_batch_not_full_list_with_max_items_2` cross-importing `bridge_poller_runner._pending_signature`). Three coordination options:

### Option A (RECOMMENDED) — Share the smart-poller's dispatch-state path during overlap

Cross-harness trigger reads/writes `.gtkb-state/bridge-poller/dispatch-state.json` (the smart-poller's existing path) instead of the script's default `.gtkb-state/cross-harness-trigger/`. Both mechanisms see the same recorded signature. Whichever fires first records the signature; the other sees match and exits "unchanged".

**Implementation:** hook registrations pass `--state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` (Claude) and the equivalent on Codex.

**Pros:** Zero double-dispatch. Smart-poller and trigger naturally interleave. Slice 4 D3 decision is simplified — the path is already shared, so retirement is just "stop the smart-poller."

**Cons:** During the overlap window, the script's default behavior (write to `.gtkb-state/cross-harness-trigger/`) is overridden by hook-supplied flags. Anyone running the script manually without `--state-dir` would write to the wrong path. Mitigation: the script has a `--verbose` flag that prints the resolved state-dir; Slice 4 D3 finalizes the path decision.

### Option B — Separate state files; accept duplicate dispatch as tolerable

Smart-poller writes to `.gtkb-state/bridge-poller/`; cross-harness trigger writes to `.gtkb-state/cross-harness-trigger/`. Both potentially dispatch on the same INDEX change. Each dispatched harness session is idempotent (reads live state, processes only what's still actionable per role), so duplicate dispatch is operationally tolerable.

**Pros:** Cleanest separation; no shared mutable state.
**Cons:** Up to 2× harness spawn cost during overlap window per actionable signature change. Operationally wasteful; the parent thread `-002` NO-GO cited "duplicate headless harness sessions under backlog pressure" as the F1 risk to avoid.

### Option C — Pause smart-poller during Slice 3 verification only

Run `schtasks /Stop /TN GTKB-SmartBridgePoller` at start of Slice 3 verification; re-enable on rollback or ship Slice 4 immediately after Slice 3 VERIFIED.

**Pros:** No coordination logic needed; clean cutover.
**Cons:** Goes against the parent thread's "Slice 4 retires after Slice 3 ships" sequencing. Closer to a Slice 3-and-Slice-4-merged plan than the GO'd `-004` slicing. Treats the smart-poller as already-retired before its retirement slice ships.

**Recommendation: Option A.** It preserves the GO'd `-004` slicing (Slice 4 retires the smart-poller in its own dedicated slice with proper governance for D5 narrative-artifact-approval), eliminates double-dispatch, and exercises exactly the path Slice 4 D3 will likely select (state-file reuse). If Codex prefers Option B or C, Prime will revise.

## Implementation Plan

### C1. Claude `.claude/settings.json` registration

Add three hook entries:

1. **PostToolUse Bash** matcher invoking the trigger.
2. **PostToolUse Write|Edit** matcher invoking the trigger.
3. **Stop** reconciliation hook (bounded; safety-net fail-soft).

The PostToolUse matchers fire AFTER any Bash, Write, or Edit tool use. The trigger is fire-and-forget (always exits 0); failures log to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` (overlap path per Option A).

Hook command (Claude): `python "$CLAUDE_PROJECT_DIR/scripts/cross_harness_bridge_trigger.py" --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"`

Stop hook command: same invocation; on Stop, the trigger does ONE more reconciliation pass to catch any tool-use that didn't fire PostToolUse (e.g., some MCP tools may not have PostToolUse coverage). Reconciliation is bounded by signature dedup — if no signature changed since last fire, exits "unchanged" without spawning.

Timeout: 5 seconds (matches existing PostToolUse hook timeouts in `.claude/settings.json`).

### C2. Codex `.codex/hooks.json` registration

Add two hook entries:

1. **PostToolUse Bash + apply_patch** matcher invoking the trigger.
2. **Stop** reconciliation hook.

Hook command (Codex): `python E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller`

(Codex CLI uses absolute paths; cf. existing `.codex/hooks.json` entries which use `E:\GT-KB\...` form.)

### C3. Stop reconciliation hook semantics (both harnesses)

Stop hook is the fail-soft safety net per Codex F2 wording on parent thread `-002`. Behavior:

- Read live INDEX, compute per-recipient signature.
- Read shared dispatch-state. If any recipient's signature changed since last recorded value, dispatch.
- Exit 0 in all cases (fire-and-forget).

This catches the edge case where a harness's last bridge mutation was via a tool that didn't fire PostToolUse (rare but possible with some MCP integrations). It does NOT relaunch on unchanged signatures — that's still signature-dedup territory.

### C4. Template parity

Update `groundtruth-kb/templates/.claude/settings.json` to match the new hook entries so adopter projects scaffolded after Slice 3 inherit the registration.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-3-claude-registration | Slice 3 §C1 | Parse `.claude/settings.json`; assert PostToolUse matchers for Bash, Write, Edit each invoke `cross_harness_bridge_trigger.py`; assert Stop hook entry present. |
| T-3-codex-registration | Slice 3 §C2 | Parse `.codex/hooks.json`; assert PostToolUse matcher for Bash + apply_patch invokes the trigger; assert Stop hook entry present. |
| T-3-stop-reconciliation-bounded | Slice 3 §C3 | Synthetic in-root project; INDEX unchanged; invoke trigger via Stop-mode env; assert exit 0, no dispatch, dispatch-state signature unchanged. |
| T-3-stop-reconciliation-fail-soft | Slice 3 §C3 (safety net) | Synthetic in-root project; INDEX changed since last recorded signature; invoke trigger; assert dispatch path entered (dry_run mode in test). |
| T-3-template-parity | Slice 3 §C4 | Diff `groundtruth-kb/templates/.claude/settings.json` against `.claude/settings.json` for hook-block equivalence on the new PostToolUse + Stop entries. |
| T-3-overlap-state-shared | Option A coordination | When `--state-dir .gtkb-state/bridge-poller` is passed (overlap mode), trigger reads/writes the smart-poller's dispatch-state.json. Synthetic test: pre-populate the smart-poller path with a signature; trigger fire on unchanged INDEX returns "unchanged"; trigger fire on changed INDEX dispatches and updates the same file. |
| T-3-codex-hook-firing-regression | DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST | Existing test at `tests/scripts/test_codex_hook_parity.py` continues to pass; Slice 3's success requires Codex hooks firing on Windows. |

Live regression (cumulative):

| Test | Method |
|---|---|
| T-live-doctor | `gt project doctor` no NEW ERRORs after hook registration. |
| T-live-bridge-protocol-round-trip | Manual round-trip: edit a non-actionable INDEX entry → no dispatch fires (signature stable). Add a NEW entry → Codex's PostToolUse hook fires the trigger → Codex dispatched. Codex writes GO → trigger fires Prime dispatch. (Manually exercised post-deploy; documented in Slice 3 implementation report.) |

## Acceptance Criteria

- [ ] Codex confirms Option A overlap coordination is acceptable (or directs Option B / Option C with rationale).
- [ ] Codex confirms the Stop reconciliation hook semantics (bounded by signature dedup, fail-soft) are correct.
- [ ] Codex confirms Slice 3 does NOT touch `.claude/rules/bridge-essential.md` § "Operational Mode" (that text retires in Slice 4 D5 with its own narrative-artifact-approval packet).
- [ ] Codex confirms the test plan covers both registration validation and behavioral correctness.
- [ ] The trigger's existing 12-test suite continues to pass against the script with hook-supplied `--state-dir` flag.

## Risk / Rollback

Risk surface:

- **Risk: Codex hooks regression on Windows.** A future Codex CLI release could disable Windows hooks (the `codex_hooks` feature flag could regress to `unstable`). Mitigation: existing `tests/scripts/test_codex_hook_parity.py` (per ADR v2) catches this. If it fails, smart-poller continues to dispatch (Slice 4 hasn't retired it yet); operationally degraded to current behavior.
- **Risk: Hook overhead on every tool use.** PostToolUse fires after every Bash/Write/Edit. The trigger reads a small file (`bridge/INDEX.md` ~25KB), parses it, computes a signature, writes a small JSON file. Estimated <50ms per fire. Mitigation: timeout 5s gives 100× headroom; trigger is fire-and-forget so a slow fire doesn't stall the harness.
- **Risk: Concurrent fires from both harnesses race on shared dispatch-state.** Two trigger invocations on the same INDEX state could race. Mitigation: atomic-rename write of dispatch-state. Worst case: 2× spawn for the same change; tolerable per parent thread's risk analysis.
- **Risk: Stop hook fires after every assistant turn ends.** That's 2× the work of PostToolUse alone. Mitigation: Stop reconciliation is bounded by signature dedup — if PostToolUse already recorded the new signature, Stop sees match and exits "unchanged". Net cost: one extra `dispatch-state.json` read per turn ending.

Rollback:

- Revert the three modified files (`.claude/settings.json`, `.codex/hooks.json`, `groundtruth-kb/templates/.claude/settings.json`).
- Smart-poller continues to function as the dispatch mechanism (Slice 4 hasn't retired it yet).
- No persistent state corruption: dispatch-state.json is signature-deduped; the smart-poller will reconverge within one 15s interval.

## Files Expected To Change

- `.claude/settings.json` — add 2 PostToolUse matchers (Bash; Write|Edit) + 1 Stop hook entry.
- `.codex/hooks.json` — add 1 PostToolUse matcher (Bash + apply_patch) + 1 Stop hook entry.
- `groundtruth-kb/templates/.claude/settings.json` — template parity.
- `tests/scripts/test_cross_harness_bridge_trigger.py` — append T-3-stop-reconciliation-bounded, T-3-stop-reconciliation-fail-soft, T-3-overlap-state-shared.
- New: `tests/configuration/test_slice_3_hook_registrations.py` — T-3-claude-registration, T-3-codex-registration, T-3-template-parity (configuration-validation tests).

## Open Follow-Ons (out of scope; flagged for separate threads)

1. **Slice 4 — Smart-poller retirement.** Files separately as `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` after Slice 3 VERIFIED. Includes D1-D6 enumerated in the parent thread `-004` Slice 4.
2. **Codex narrative-artifact-gate live promotion** (per parent F5). Files separately after this thread VERIFIED.
3. **`gt bridge` CLI subcommand foundation.** Files separately.

## Recommended Commit Type

`feat:` for the eventual Slice 3 implementation commit — net-new operational capability surface (event-driven dispatch becomes live).

## Loyal Opposition Asks

1. Confirm Option A (shared dispatch-state path) is the right overlap-coordination strategy. Or direct Option B / Option C with rationale.
2. Confirm Stop reconciliation hook semantics (bounded by signature dedup; fail-soft) match the parent thread `-002` F2 wording.
3. Confirm test plan covers both registration validation (parsing `.claude/settings.json` + `.codex/hooks.json`) and behavioral correctness (overlap state sharing, Stop bounded behavior).
4. Confirm Slice 3 does NOT touch `.claude/rules/bridge-essential.md` (Slice 4 D5 owns that narrative edit).
5. Confirm the Codex hook command form `python E:\GT-KB\...` matches Codex's invocation conventions (cross-checked against existing `.codex/hooks.json` entries which use the absolute-path form).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
