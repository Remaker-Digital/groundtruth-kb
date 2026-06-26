NEW

# gtkb-wi4858-excise-active-session-dispatch-suppression — Make the dispatcher session/UI-unaware: complete excision of active-session suppression

bridge_kind: prime_proposal
Document: gtkb-wi4858-excise-active-session-dispatch-suppression
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI4858-EXCISE-ACTIVE-SESSION-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4858

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/single_harness_bridge_automation.py", "scripts/active_session_heartbeat.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_active_session_heartbeat.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_dispatch_session_unaware_guard.py", ".claude/rules/bridge-essential.md", "groundtruth-kb/templates/rules/bridge-essential.md", ".claude/settings.json", ".codex/hooks.json", ".cursor/hooks.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner directive (2026-06-26, DELIB-20266195): the dispatcher MUST NOT be aware of any interactive session or harness UI; active-session dispatch suppression must be removed completely from code, tests, AND directives. Prior work (`gtkb-disable-active-session-dispatch-suppression` VERIFIED at -010) only *disabled* the suppression in the trigger; the machinery, tests, and directives persist across many layers — which is why it has survived many removal attempts. This proposal is the complete, multi-layer excision plus a regression guard so it cannot return. `SPEC-INTAKE-ca9165` already supersedes binary same-role active-session suppression in favor of bounded parallel claim-gated dispatch; this completes that supersession. No spec/DCL/PB mandates the suppression (verified by MemBase query).

## Surgical scope (what is and is NOT removed)

REMOVE (active-session / harness-UI awareness only):
- The active-session heartbeat read + `HEARTBEAT_LOCK_TEMPLATE` + the `active_session_suppressed` classification/branch in `scripts/cross_harness_bridge_trigger.py`.
- The equivalent active-session machinery in `scripts/single_harness_bridge_dispatcher.py` and `scripts/single_harness_bridge_automation.py`.
- `scripts/active_session_heartbeat.py` (the dispatcher was its only reader) and its session-hook writer registrations in `.claude/settings.json`, `.codex/hooks.json`, `.cursor/hooks.json`.
- The suppression test suite (`test_cross_harness_trigger_suppression.py`, `test_active_session_heartbeat.py`) and active-session-suppression assertions in `test_cross_harness_bridge_trigger.py` / `test_single_harness_bridge_dispatcher.py`.
- The active-session-suppression "contract" sections in `.claude/rules/bridge-essential.md` AND `groundtruth-kb/templates/rules/bridge-essential.md` (the template is the re-propagation source).

PRESERVE (NOT session/UI awareness — out of scope):
- `_application_subject_dispatch_suppression` (work-subject suppression).
- Lease/contention suppression (`EXPECTED_SUPPRESSION_REASONS`, `dispatch-suppressions.jsonl`) — these are claim/lease arbitration, not interactive-session awareness.

## Regression guard (the keystone — why it sticks this time)

Add `platform_tests/scripts/test_dispatch_session_unaware_guard.py`: a `grep_absent`-style assertion that the dispatch code (`cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`, `single_harness_bridge_automation.py`) contains no active-session/heartbeat awareness (no `active_session_heartbeat`, `active-{role}-session.lock`, `active_session_suppressed`, or interactive-session reads). If any reappears — via a future edit or a template re-scaffold — this test fails. This converts "removed" into a durable invariant, directly addressing the many-session recurrence.

## Specification Links

- `SPEC-INTAKE-ca9165` — supersedes binary same-role active-session suppression with bounded parallel claim-gated dispatch; this completes the supersession.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher is a GT-KB-owned service triggered by artifact deposit + ownership-release, NOT by harness/session state; removing session-awareness aligns the implementation to the ADR (`DELIB-20265888`: harnesses do not trigger or influence dispatch).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4858-excise-active-session-dispatch-suppression-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001` — satisfied (WI-4858 governs; PAUTH-WI4858-EXCISE-ACTIVE-SESSION-SUPPRESSION authorizes).
- `GOV-ARTIFACT-APPROVAL-001` — the edits to `.claude/rules/bridge-essential.md` (protected narrative artifact) require a formal/narrative approval packet; the owner directive authorizes the content change and the packet will be presented before the protected-file write.

## Prior Deliberations

- `DELIB-20266195` — owner directive (this session): complete excision, dispatcher session/UI-unaware; authorizes WI-4858.
- `gtkb-disable-active-session-dispatch-suppression` (-010 VERIFIED) — the disable-only predecessor; this excises what it left behind.
- `SPEC-INTAKE-ca9165` deliberation chain (DELIB-2512, DELIB-2745, DELIB-20265472, DELIB-20265511) — bounded parallel dispatch superseding active-session suppression.

## Owner Decisions / Input

- Owner directive (2026-06-26, captured as DELIB-20266195): "halt all work in the dispatcher until active-session-suppression is removed completely from all tests, directives, and code. I do not want this. The dispatcher should not be aware of any interactive session or any harness UI." Owner AUQ (2026-06-26): "Mint PAUTH + start the excision now." Authorized under PAUTH-WI4858-EXCISE-ACTIVE-SESSION-SUPPRESSION. The protected-directive edit (`bridge-essential.md`) will carry its own formal-artifact-approval packet at write time per `GOV-ARTIFACT-APPROVAL-001`.

## Requirement Sufficiency

Existing requirements sufficient — `SPEC-INTAKE-ca9165` already specifies superseding active-session suppression; the owner directive confirms complete removal. No new requirement; this completes a specified supersession.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| Owner directive + SPEC-INTAKE-ca9165 (dispatcher session-unaware) | `test_dispatch_session_unaware_guard` (new) | dispatch code contains no active-session/heartbeat awareness tokens (grep_absent). |
| ADR-DISPATCHER-ARCHITECTURE-001 (dispatch unchanged otherwise) | existing dispatch suites (trigger, single-harness, per-role cap, lease) | PASS — non-session dispatch behavior (lease, application-subject, caps, dedup) unchanged. |
| Clean removal | full `platform_tests/scripts` dispatch suites + `ruff check`/`ruff format --check` on changed files | green; suppression suite removed; no dangling references. |

Commands (pre-report): targeted `pytest` over the dispatch suites + the new guard; `ruff check`/`ruff format --check`; a repo grep confirming no live (non-bridge-history) reference to active-session suppression remains.

## Risk / Rollback

- Risk: moderate breadth (many files) but low behavioral risk — the suppression is already disabled, so removing the machinery changes no live dispatch behavior; the guard prevents regression. Surgical scope preserves lease + application-subject suppression. All paths in-root under `E:\GT-KB`.
- Rollback: revert the excision commit; the disabled-but-present machinery returns. Append-only KB + bridge history untouched (`kb_mutation_in_scope: false`).
- Note: `bridge/*.md` historical references to active-session suppression are the audit trail and are intentionally NOT modified.
