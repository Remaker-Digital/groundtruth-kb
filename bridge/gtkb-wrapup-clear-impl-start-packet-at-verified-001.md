NEW

# Wrap-Up Clears Stale Implementation-Start Packet At VERIFIED (WI-3328)

bridge_kind: implementation_proposal
Document: gtkb-wrapup-clear-impl-start-packet-at-verified
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001; PB-SESSION-WRAP-UP-PROACTIVE-001; WI-3328
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3328
target_paths: ["scripts/implementation_authorization.py", "scripts/wrap_clear_impl_start_packet.py", ".claude/skills/kb-session-wrap/SKILL.md", "platform_tests/scripts/**"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

The implementation-start authorization packet (`current.json`) survives across sessions because the session wrap-up procedure never clears or expires it when the associated bridge thread reaches VERIFIED. A stale active pointer then misleads the next session's implementation-start gate and packet-inspection surfaces.

Evidence for the packet-write site: `scripts/implementation_authorization.py:23` defines `DEFAULT_PACKET_RELATIVE_PATH = Path(".gtkb-state/implementation-authorizations/current.json")`; `write_packet()` at `scripts/implementation_authorization.py:787-791` writes that file; the CLI `begin` subcommand invokes `write_packet(root, packet)` at `scripts/implementation_authorization.py:1024`. This `current.json` is the single active pointer the implementation-start gate consults: `scripts/implementation_start_gate.py:608` calls `validate_targets(root, protected)`, which loads `current.json` via `load_packet()` (`scripts/implementation_authorization.py:983` → `878`).

Evidence that wrap-up never clears it: the `kb-session-wrap` procedure at `.claude/skills/kb-session-wrap/SKILL.md` (Phase 0 live inventory through Phase 5 handoff, plus the Knowledge Collection Matrix) makes zero reference to the implementation-start packet — a content scan for `implementation-start`, `current.json`, `impl-start`, and `implementation_authorization` over that SKILL.md returns no matches, and the matrix's "Bridge state" row only reconciles `bridge/INDEX.md` entries, not the packet. The CLI exposes exactly four subcommands — `begin`, `validate`, `activate`, `list` (`scripts/implementation_authorization.py:997,1004,1007,1013`) — with no `clear`/`end`/`close` and no `current.json` deletion (`.unlink`/`os.remove`) anywhere in the module. No Stop hook in `.claude/settings.json` clears it either.

The mechanism: when a thread is VERIFIED, `_validate_packet` (`scripts/implementation_authorization.py:809`) does fail-closed at `begin`-time on the terminal/expired packet (lines 817, 855-860), but `current.json` is never removed at wrap, so it persists as a leftover active pointer to a closed thread. Until the next `begin --bridge-id <new thread>` overwrites it, every inspection of "what is the active implementation scope?" — and the next session's mental model of an in-flight packet — sees a stale, completed-thread pointer. That is the reliability defect: a packet that looks active but is stale.

This proposal repairs the defect with a deterministic wrap step that clears (deletes) the active `current.json` pointer when the packet's associated bridge thread has reached VERIFIED, plus a `kb-session-wrap` procedure step that runs it. It is a small single-concern defect fix with no new dispatch behavior, filed under the reliability fast lane.

## Specification Links

- DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001 (verified) — governs wrap-up automation safety: "Safe automatic lifecycle hooks may generate startup reports... Mutating wrap-up operations... still require applicable approval, acknowledgement, or owner-authorized automation scope." Clearing the stale active pointer is a safe, owner-authorized-scope wrap step (reliability fast lane); the cleared `current.json` is regenerable runtime state, not canonical knowledge.
- PB-SESSION-WRAP-UP-PROACTIVE-001 (verified) — sessions proactively perform wrap-up procedures so the owner need not instruct each step; the missing packet-clear is exactly such a wrap step that should run proactively.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (specified) — the project/implementation-authorization envelope context within which the implementation-start packet operates; clearing the session-local `current.json` at VERIFIED keeps the authorization-evidence trail accurate.
- GOV-FILE-BRIDGE-AUTHORITY-001 (verified) — `bridge/INDEX.md` is canonical workflow state; the clear step reads INDEX latest-status (VERIFIED) as the trigger condition and does not mutate INDEX.
- GOV-RELIABILITY-FAST-LANE-001 (verified) — the reliability fast lane governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (verified) — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (verified) — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries it forward.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (verified) — durable artifact preservation across proposal, deliberation, and report (advisory).

## Fast-Lane Eligibility

This thread claims eligibility under `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers-by-membership: WI-3328 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`). The four eligibility criteria:

1. **Origin defect/regression** — met. WI-3328 targets a wrap-up defect: a stale implementation-start packet (`current.json`) survives across sessions because wrap-up never clears it at VERIFIED, mis-signaling the next session's impl-start gate and inspection surfaces.
2. **No new API/CLI/behavior beyond removing the defect** — met. The fix adds one deterministic clear step (a small `clear` subcommand on the existing `implementation_authorization.py` CLI, invoked by a thin wrap helper, and a `kb-session-wrap` procedure step that runs it). It changes no dispatch behavior, no packet schema, no `begin`/`validate`/`activate`/`list` semantics, and no bridge state. The cleared file is regenerable runtime state.
3. **No new requirement** — met. `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` and `PB-SESSION-WRAP-UP-PROACTIVE-001` already require wrap-up to safely and proactively maintain session state; the missing packet-clear is non-compliance with those requirements. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. **Small single-concern scope** — met. One concern: clear the stale implementation-start packet at VERIFIED during wrap-up. One CLI-module change, one thin wrap helper, one SKILL.md step, plus tests; no cross-cutting change.

## Prior Deliberations

- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` (VERIFIED) — the structural exemplar for a reliability-fast-lane single-concern defect repair of session/bridge runtime state under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; this proposal mirrors its section structure and fast-lane framing.
- The reliability fast lane (`GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) was established at `bridge/gtkb-reliability-fast-lane-006.md` (VERIFIED) with owner-decision record `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`; this proposal uses that standing authorization.
- _No prior deliberations: a content scan of `.claude/skills/kb-session-wrap/SKILL.md` and a bridge scan for "clear packet"/"expire packet"/"current.json" found no thread that makes session-wrap clear or expire the implementation-start packet at VERIFIED. The "clear packet" bridge hits all concern formal-artifact approval packets clearing protected files (a distinct concept), not the implementation-start authorization pointer. This is the first thread on this exact defect._

## Owner Decisions / Input

No owner decision required — standing fast-lane authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this by active project membership; no AskUserQuestion needed.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` and `PB-SESSION-WRAP-UP-PROACTIVE-001` already require wrap-up to safely and proactively maintain session lifecycle state; the stale-packet survival is non-compliance with those requirements. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` frames the authorization-evidence accuracy that the clear step preserves. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix: one CLI-module change, one thin wrap helper, one `kb-session-wrap` procedure step, and regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3328) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Clear the stale implementation-start packet at VERIFIED

Add a deterministic clear path so that, when the bridge thread associated with the active `current.json` packet has reached VERIFIED, the active pointer is removed:

1. Add a `clear` subcommand to `scripts/implementation_authorization.py` (alongside the existing `begin`/`validate`/`activate`/`list` subparsers). Behavior: read the active packet at `current.json` (via `packet_path(project_root)` / `load_packet`-style read). Resolve the packet's `bridge_id` and inspect the live bridge entry (`bridge_entry(project_root, bridge_id)`). When the thread's latest status is VERIFIED (terminal), delete `current.json` and report `{"cleared": true, "bridge_id": ..., "reason": "thread VERIFIED"}`. When the thread is NOT VERIFIED, leave `current.json` intact and report `{"cleared": false, "reason": "thread not VERIFIED (latest=<status>)"}` so an in-flight packet is never destroyed. When `current.json` is absent or unreadable, report a no-op `{"cleared": false, "reason": "no active packet"}` and exit 0. A `--force` flag MAY clear regardless of status for explicit owner-directed cleanup; default is VERIFIED-gated. The by-bridge named cache (`by-bridge/<id>.json`) is NOT deleted — it remains the recoverable record per the existing `activate` contract; only the active `current.json` pointer is cleared. The implementation will confirm the exact reuse points (`packet_path`, `load_packet`, `bridge_entry`) at implementation time; the change is additive and does not alter existing subcommand semantics.

2. Add a thin wrap helper `scripts/wrap_clear_impl_start_packet.py` that invokes the VERIFIED-gated clear for the current project root and prints a one-line wrap-summary result. This gives the wrap procedure a single deterministic command to run (consistent with the other `scripts/wrap_*.py` helpers referenced in the SKILL).

3. Add a step to `.claude/skills/kb-session-wrap/SKILL.md` Phase 3 (Verification And Hygiene) that runs `python scripts/wrap_clear_impl_start_packet.py` and records the cleared/no-op result in the wrap summary, plus a Knowledge Collection Matrix note that the implementation-start packet is cleared at VERIFIED. The step is non-destructive for in-flight packets (VERIFIED-gated), satisfying `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001`.

### IP-2: Regression tests

Add tests under `platform_tests/scripts/`:
- `clear` deletes `current.json` when the packet's bridge thread is VERIFIED in a synthetic `bridge/INDEX.md`.
- `clear` leaves `current.json` intact (and reports `cleared: false`) when the thread's latest status is GO / NEW / REVISED / NO-GO (in-flight).
- `clear` is a safe no-op (exit 0) when no `current.json` exists.
- `clear` does not delete the by-bridge named cache (`by-bridge/<id>.json`) — `activate --bridge-id <id>` still recovers the packet afterward (only when its own validity allows).
- The `wrap_clear_impl_start_packet.py` helper invokes the VERIFIED-gated clear and emits a parseable wrap-summary line.

## Out Of Scope

- Changing the `begin`/`validate`/`activate`/`list` subcommand semantics, the packet schema, `packet_hash`, expiry, or the `_validate_packet` drift logic — this proposal only adds a VERIFIED-gated clear of the active pointer.
- Changing the implementation-start gate (`scripts/implementation_start_gate.py`) decision logic — the gate already fails closed on a terminal packet; this proposal removes the stale pointer at wrap so the gate is not even reached with a stale active scope.
- Auto-clearing the packet from a Stop hook or the cross-harness trigger — this proposal scopes the clear to the wrap-up procedure (and the explicit CLI subcommand). A hook-driven auto-clear is a possible later follow-on, not this defect fix.
- Deleting or pruning the by-bridge named cache — left intact as the recoverable record.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root; the cleared `current.json` lives under the in-root `.gtkb-state/implementation-authorizations/` directory.

## Files Expected To Change

- `scripts/implementation_authorization.py` — add the VERIFIED-gated `clear` subcommand and its handler (IP-1.1).
- `scripts/wrap_clear_impl_start_packet.py` — new thin wrap helper invoking the clear (IP-1.2).
- `.claude/skills/kb-session-wrap/SKILL.md` — add the Phase 3 clear step and the matrix note (IP-1.3).
- `platform_tests/scripts/**` — regression coverage for IP-1 (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001 | Test: `clear` is VERIFIED-gated — it deletes `current.json` only when the bridge thread is VERIFIED and leaves an in-flight (GO/NEW/REVISED/NO-GO) packet intact, so the wrap step never destroys live authorization scope. |
| PB-SESSION-WRAP-UP-PROACTIVE-001 | Test/inspection: `.claude/skills/kb-session-wrap/SKILL.md` Phase 3 runs `python scripts/wrap_clear_impl_start_packet.py` proactively and records the result, so the owner need not instruct the clear. The wrap helper emits a parseable summary line. |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Test: after `clear` at VERIFIED the active pointer is gone while the by-bridge named cache remains, preserving the recoverable authorization-evidence trail (`activate --bridge-id <id>` behavior is unchanged). |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Test: `clear` reads `bridge/INDEX.md` latest-status as the trigger and performs no INDEX mutation; INDEX remains canonical. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/ -q -k "impl_start_packet or clear or wrap_clear"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wrapup-clear-impl-start-packet-at-verified`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wrapup-clear-impl-start-packet-at-verified`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] A VERIFIED-gated `clear` subcommand exists on `scripts/implementation_authorization.py`; it deletes `current.json` when the packet's bridge thread is VERIFIED; covered by a test.
- [ ] `clear` leaves `current.json` intact and reports `cleared: false` when the thread's latest status is GO / NEW / REVISED / NO-GO; covered by a test.
- [ ] `clear` is a safe no-op (exit 0) when no `current.json` exists; covered by a test.
- [ ] `clear` does not delete the by-bridge named cache; covered by a test.
- [ ] `scripts/wrap_clear_impl_start_packet.py` exists and invokes the VERIFIED-gated clear, emitting a parseable wrap-summary line.
- [ ] `.claude/skills/kb-session-wrap/SKILL.md` includes a Phase 3 step that runs the clear and records the result, plus the matrix note.
- [ ] No change to `begin`/`validate`/`activate`/`list` semantics, the packet schema, or the implementation-start gate decision logic.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): the clear deletes an in-flight packet.** Mitigation: the clear is VERIFIED-gated by default — it only removes `current.json` when the associated bridge thread's latest status is VERIFIED; a test asserts that GO/NEW/REVISED/NO-GO packets are left intact. The `--force` path is explicit and not used by the wrap step.

**Risk R2 (low): the clear cannot resolve the thread status and errors mid-wrap.** Mitigation: the clear fails soft — when `current.json` is absent, unreadable, or its `bridge_id` is not in the INDEX, it reports a no-op and exits 0 rather than raising, so wrap-up is never blocked by the clear step. A test covers the no-packet no-op path.

**Risk R3 (low): losing the cleared packet impedes recovery.** Mitigation: only the active `current.json` pointer is cleared; the by-bridge named cache (`by-bridge/<id>.json`) is preserved, and `activate --bridge-id <id>` still recovers it where the packet is independently valid. A test asserts the named cache survives a clear.

Rollback: each IP is independently revertible. Reverting `scripts/implementation_authorization.py`, removing `scripts/wrap_clear_impl_start_packet.py`, and reverting the `.claude/skills/kb-session-wrap/SKILL.md` step restore prior behavior. No persistent state is migrated; the cleared `current.json` is regenerable by the next `begin`.

## Loyal Opposition Asks

1. Confirm that VERIFIED-gated clearing of only the active `current.json` pointer (preserving the by-bridge named cache) is the correct minimal scope for this defect, versus also pruning the named cache.
2. Confirm that scoping the clear to the wrap-up procedure plus an explicit CLI subcommand (rather than a Stop-hook auto-clear) is the right boundary for a fast-lane fix.
3. Confirm the spec linkage — `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` + `PB-SESSION-WRAP-UP-PROACTIVE-001` as the governing wrap-up requirements, with `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` as the authorization-envelope context — is complete for this surface.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
