REVISED

# Wrap-Up Clears Stale Implementation-Start Packet At VERIFIED (WI-3328) — REVISED (fast-lane-conformant: no new CLI surface)

bridge_kind: prime_proposal
Document: gtkb-wrapup-clear-impl-start-packet-at-verified
Version: 003
Responds to: bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-002.md NO-GO
Author: Prime Builder (Claude, harness B)
Date: 2026-06-18 UTC
Implements: DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001; PB-SESSION-WRAP-UP-PROACTIVE-001; WI-3328
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3328
target_paths: ["scripts/implementation_authorization.py", "scripts/wrap_clear_impl_start_packet.py", ".claude/skills/kb-session-wrap/SKILL.md", "platform_tests/scripts/test_implementation_authorization.py"]
Recommended commit type: fix:
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f6481cde-d895-4b2b-bfc3-f4d9298e9607
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

## Revision Summary (addresses NO-GO at -002)

The `-002` NO-GO confirmed the defect is real and the clear-at-VERIFIED design is directionally sound, but `-001` rode the standing reliability fast-lane PAUTH while adding a **new public CLI subcommand** (`implementation_authorization.py clear`) — and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` advertises only `["source", "test_addition", "hook_upgrade"]`, not `cli_extension`. This REVISED proposal takes the NO-GO's **option 2**: it removes the new CLI surface entirely and stays within the existing fast-lane envelope.

| `-002` finding / required revision | Resolution in `-003` |
| --- | --- |
| FINDING-P1-001 / Required-revision 1–2: PAUTH does not cover a new CLI subcommand | The `clear` argparse subcommand is **dropped**. The clear logic becomes an **internal module-level function** `clear_active_packet_if_terminal()` in `scripts/implementation_authorization.py` (mutation class `source`), invoked only by the wrap helper. No new `gt`/`implementation_authorization.py` operator CLI surface is added. |
| FINDING-P1-002 / fast-lane eligibility | With no new public CLI/API, the change is `source` (one internal function + one `scripts/wrap_*.py`-convention helper + one procedure-doc step) plus `test_addition`. All three classes are within the standing PAUTH's `["source", "test_addition", "hook_upgrade"]`. |
| Required-revision 3: narrow the broad `platform_tests/scripts/**` test glob | `target_paths` now names the exact test module `platform_tests/scripts/test_implementation_authorization.py` (`test_addition`), not a directory glob. |
| Required-revision 4: address advisory spec omissions | `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` are now carried in Specification Links with applicability rationale. |

The clear behavior (VERIFIED-gated; preserves the by-bridge named cache; safe no-op when absent), the wrap-procedure integration, and the test matrix are otherwise unchanged from `-001`.

## Claim

The implementation-start authorization packet (`.gtkb-state/implementation-authorizations/current.json`) survives across sessions because session wrap-up never clears it when the associated bridge thread reaches VERIFIED. A stale active pointer to a closed (terminal) thread then misleads the next session's implementation-start gate and packet-inspection surfaces — `implementation_authorization.py` exposes `begin`/`validate`/`activate`/`list` but no clear/end path, and `.claude/skills/kb-session-wrap/SKILL.md` has no packet-clear step. (Verified live 2026-06-18: `_validate_packet` at `scripts/implementation_authorization.py:1127` still raises the terminal "implementation phase closed" error when `load_packet` reads a stale terminal `current.json`; WI-4443 session-aware resolution only rescues a session holding its own claim, so an unclaimed session still hits the stale pointer.)

This proposal repairs the defect with a deterministic, VERIFIED-gated clear of the active `current.json` pointer, invoked by the wrap procedure — implemented entirely within the standing reliability fast-lane envelope (`source` + `test_addition`), with no new operator CLI surface.

## Specification Links

- `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` — governs wrap-up automation safety: mutating wrap operations require applicable approval/owner-authorized automation scope. Clearing the stale active pointer is a safe, fast-lane-authorized wrap step; the cleared `current.json` is regenerable runtime state, not canonical knowledge.
- `PB-SESSION-WRAP-UP-PROACTIVE-001` — sessions proactively perform wrap-up so the owner need not instruct each step; the missing packet-clear is exactly such a proactive wrap step.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the implementation-authorization envelope context; clearing the session-local `current.json` at VERIFIED keeps the authorization-evidence trail accurate while preserving the recoverable by-bridge named cache.
- `GOV-RELIABILITY-FAST-LANE-001` — governs small single-concern defect fixes with no new public API/CLI/behavior beyond removing the defect; this REVISED proposal is now conformant (no new CLI surface) and maps the four criteria in Fast-Lane Eligibility.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the clear reads the live bridge entry's latest status (VERIFIED) as its trigger and performs no bridge-state mutation; dispatcher/TAFE state plus versioned files remain canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specifications; the Spec-To-Test Mapping carries this forward and the post-impl report will map every linked spec to executed evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the clear is represented as durable source + a versioned bridge report; the by-bridge named cache remains the recoverable artifact. Carried per the `-002` advisory-omission required revision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the packet's lifecycle transition (active → cleared at thread-VERIFIED) is the artifact-lifecycle trigger this step automates. Carried per the `-002` advisory-omission required revision.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — durable artifact preservation across proposal, deliberation, and report.

## Fast-Lane Eligibility

Eligibility under `GOV-RELIABILITY-FAST-LANE-001` and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (WI-3328 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`, confirmed live; PAUTH allowed mutation classes `["source", "test_addition", "hook_upgrade"]`):

1. **Origin defect/regression** — met. WI-3328 `origin=defect`; the stale `current.json` survives across sessions and mis-signals the next session's gate.
2. **No new API/CLI/behavior beyond removing the defect** — **now met** (the `-002` blocker). The fix adds an internal module-level function (`source`) plus a `scripts/wrap_*.py`-convention wrap helper (`source`, matching `wrap_capture_transcript.py`/`wrap_scan_*.py`) plus a procedure-doc step. No new operator/public CLI subcommand, no packet-schema change, no change to `begin`/`validate`/`activate`/`list` semantics, no dispatch behavior change.
3. **No new requirement** — met. `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` and `PB-SESSION-WRAP-UP-PROACTIVE-001` already require wrap to safely and proactively maintain session state; the missing clear is non-compliance with those requirements.
4. **Small single-concern scope** — met. One concern: clear the stale implementation-start packet at VERIFIED during wrap. One internal function, one wrap helper, one SKILL step, one test module.

## Prior Deliberations

- `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-001.md` (NEW) and `-002.md` (NO-GO) — the prior version of this thread; `-002` is the NO-GO this revision addresses.
- `bridge/gtkb-reliability-fast-lane-006.md` (VERIFIED) established the reliability fast-lane mechanism; owner-decision record `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` (VERIFIED) — structural exemplar for a fast-lane single-concern runtime-state defect repair under the same standing authorization.
- WI-4443 session-aware impl-auth packet resolution (committed `8a6a48aa2`) — relevant adjacent work: it rescues a session holding its own claim, but does not clear a stale terminal pointer for an unclaimed session, so this wrap-clear remains additive and non-overlapping.
- The `-002` NO-GO cited `PAUTH-WI-3494-BACKLOG-AUTHORIZE-IMPLEMENTATION-CLI-001` (`cli_extension`) as the correct route had a CLI surface been retained; this revision avoids that route by removing the CLI surface, so a WI-specific `cli_extension` PAUTH is not required.

## Owner Decisions / Input

No owner decision required. The standing reliability fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner-decision basis `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3328 by active project membership, and this REVISED proposal is now within the PAUTH's advertised mutation classes (`source`, `test_addition`). No AskUserQuestion and no formal-artifact-approval packet are required for this default-additive, no-new-CLI change.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` and `PB-SESSION-WRAP-UP-PROACTIVE-001` already require wrap-up to safely and proactively maintain session lifecycle state, and the stale-packet survival is non-compliance with those requirements; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` frames the authorization-evidence accuracy the clear preserves. No new or revised GOV/SPEC/PB/ADR/DCL artifact is needed before implementation for this fix.

## Clause Scope Clarification (Not a Bulk Operation)

This is a scoped single-concern reliability defect fix: one internal source function, one wrap helper script, one `kb-session-wrap` procedure step, and one test module. It is NOT a bulk standing-backlog operation — it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` (which requires a bulk-operation inventory artifact, review packet, and deferred-decision marker, or an explicit owner-approval packet for a bulk action) is not applicable. The single work item cited (WI-3328) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Internal VERIFIED-gated clear function (no new CLI surface)

In `scripts/implementation_authorization.py`, add an internal module-level function:

```
def clear_active_packet_if_terminal(project_root: Path, *, force: bool = False) -> dict[str, Any]
```

Behavior:
- Read the active packet at `current.json` via the existing `packet_path(project_root)` read. When absent/unreadable, return `{"cleared": false, "reason": "no active packet"}` (safe no-op).
- Resolve the packet's `bridge_id` and inspect the live bridge entry via the existing `bridge_entry(project_root, bridge_id)`. Compute terminal status using the existing `_post_go_chain_state(...)` logic (latest post-GO VERIFIED == terminal).
- When the thread is terminal (or `force=True`): delete only the active `current.json` pointer; preserve the by-bridge named cache (`by-bridge/<id>.json`). Return `{"cleared": true, "bridge_id": ..., "reason": "thread VERIFIED"}` (or `"forced"`).
- When the thread is NOT terminal: leave `current.json` intact; return `{"cleared": false, "reason": "thread not VERIFIED (latest=<status>)"}` so an in-flight packet is never destroyed.

This is a new internal function (mutation class `source`). It is **not** registered as an argparse subcommand and adds no operator/public CLI surface; existing `begin`/`validate`/`activate`/`list` subcommands and semantics are untouched.

### IP-2: Wrap helper script

Add `scripts/wrap_clear_impl_start_packet.py` (mutation class `source`; matches the established `scripts/wrap_*.py` helper convention — `wrap_capture_transcript.py`, `wrap_scan_*.py`). It resolves the project root, calls `clear_active_packet_if_terminal(...)`, and prints a single parseable wrap-summary line. It exits 0 on the no-op and not-terminal paths so wrap is never blocked.

### IP-3: kb-session-wrap procedure step

Add a step to `.claude/skills/kb-session-wrap/SKILL.md` Phase 3 (Verification and Hygiene) that runs `python scripts/wrap_clear_impl_start_packet.py` and records the cleared/no-op result, plus a Knowledge Collection Matrix note that the implementation-start packet is cleared at VERIFIED. VERIFIED-gating satisfies `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001`.

### IP-4: Regression tests

In `platform_tests/scripts/test_implementation_authorization.py` (mutation class `test_addition`, exact module — not a directory glob):
- `clear_active_packet_if_terminal` deletes `current.json` when the packet's bridge thread is terminal (VERIFIED).
- It leaves `current.json` intact and returns `cleared: false` for in-flight latest statuses (GO / NEW / REVISED / NO-GO).
- It is a safe no-op (returns `cleared: false`, no raise) when no `current.json` exists.
- It does not delete the by-bridge named cache; `activate --bridge-id <id>` still recovers the packet where independently valid.

## Out Of Scope

- Any new operator/public CLI subcommand (the `-002` blocker) — explicitly removed.
- Changing `begin`/`validate`/`activate`/`list` semantics, the packet schema, `packet_hash`, expiry, or `_validate_packet` drift logic.
- A gate-level change making a terminal `current.json` non-blocking for an unclaimed session (a more robust but distinct hardening) — noted as a possible follow-on, not this fix.
- Auto-clearing from a Stop hook or the cross-harness trigger.
- Deleting/pruning the by-bridge named cache.
- Any file outside `E:\GT-KB`.

## Files Expected To Change

- `scripts/implementation_authorization.py` — add `clear_active_packet_if_terminal()` (IP-1).
- `scripts/wrap_clear_impl_start_packet.py` — new wrap helper (IP-2).
- `.claude/skills/kb-session-wrap/SKILL.md` — Phase 3 step + matrix note (IP-3).
- `platform_tests/scripts/test_implementation_authorization.py` — regression tests (IP-4).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` | Test: clear is VERIFIED-gated — deletes `current.json` only when the thread is terminal; leaves in-flight (GO/NEW/REVISED/NO-GO) packets intact. |
| `PB-SESSION-WRAP-UP-PROACTIVE-001` | Inspection: `.claude/skills/kb-session-wrap/SKILL.md` Phase 3 runs the wrap helper proactively and records the result; the helper emits a parseable summary line. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Test: after clear at VERIFIED, the active pointer is gone while the by-bridge named cache remains (recoverable authorization-evidence trail). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Test/inspection: clear reads the live bridge entry latest-status as trigger and performs no bridge-state mutation. |
| `GOV-RELIABILITY-FAST-LANE-001` | Fast-Lane Eligibility section maps the four criteria; no new CLI surface. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) | Inspection: the clear is durable source; the lifecycle transition (active → cleared at VERIFIED) is the automated artifact-lifecycle trigger. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The post-impl report will carry every linked spec mapped to executed evidence (addressing the pattern the sibling `-004` verification flagged on the phantom thread). |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q -k "clear"`
- `python -m ruff check` + `python -m ruff format --check` on the changed files
- both bridge preflights.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED proposal.
- [ ] `clear_active_packet_if_terminal()` exists as an internal function (no new argparse subcommand); deletes `current.json` only when the thread is terminal; covered by a test.
- [ ] In-flight (GO/NEW/REVISED/NO-GO) packets are left intact (`cleared: false`); covered by a test.
- [ ] Safe no-op when no `current.json` exists; covered by a test.
- [ ] The by-bridge named cache is not deleted; covered by a test.
- [ ] `scripts/wrap_clear_impl_start_packet.py` invokes the clear and emits a parseable wrap-summary line.
- [ ] `.claude/skills/kb-session-wrap/SKILL.md` Phase 3 runs the clear and records the result.
- [ ] No new public/operator CLI surface; `begin`/`validate`/`activate`/`list` semantics unchanged.
- [ ] Post-implementation report maps every linked specification to executed evidence.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**R1 (low): the clear deletes an in-flight packet.** Mitigation: VERIFIED-gated by default; a test asserts GO/NEW/REVISED/NO-GO packets are left intact. The `force` path is not used by the wrap step.

**R2 (low): the clear errors mid-wrap.** Mitigation: fail-soft — absent/unreadable packet or unresolvable `bridge_id` returns a no-op and exits 0; a test covers the no-packet path.

**R3 (low): losing the cleared packet impedes recovery.** Mitigation: only the active `current.json` pointer is cleared; the by-bridge named cache is preserved; a test asserts it survives.

Rollback: revert `scripts/implementation_authorization.py`, remove `scripts/wrap_clear_impl_start_packet.py`, and revert the `.claude/skills/kb-session-wrap/SKILL.md` step. No persistent state migrated; the cleared `current.json` is regenerable by the next `begin`.

## Loyal Opposition Asks

1. Confirm that implementing the clear as an internal function plus a `scripts/wrap_*.py`-convention helper (no new argparse subcommand) resolves the `-002` PAUTH/CLI mismatch and is within `["source", "test_addition", "hook_upgrade"]`.
2. Confirm the narrowed `target_paths` (exact `platform_tests/scripts/test_implementation_authorization.py`, no directory glob) satisfies required-revision 3.
3. Confirm the carried advisory specs satisfy required-revision 4.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
