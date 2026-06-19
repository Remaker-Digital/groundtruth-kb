NEW

# gtkb-show-thread-bridge-windows-unicode — Show Thread Bridge Windows Unicode encoding crash fix

bridge_kind: prime_proposal
Document: gtkb-show-thread-bridge-windows-unicode
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-19 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: antigravity-session-76223e81
author_model: Gemini 3.5 Flash
author_model_version: gemini-3.5-flash
author_model_configuration: Antigravity desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4633

target_paths: [".claude/skills/bridge/helpers/show_thread_bridge.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves a Windows-specific crash in `show_thread_bridge.py` when formatting a bridge thread's history as markdown. When the console output page uses a non-UTF-8 encoding (such as cp1252 on standard Windows systems), writing non-ASCII characters (e.g. right-arrow `→` / U+2192) to `sys.stdout` throws a `UnicodeEncodeError`.

The fix configures `sys.stdout` to use `utf-8` encoding when running the tool, ensuring unicode characters are encoded correctly regardless of the host console's default code page.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The helper script `.claude/skills/bridge/helpers/show_thread_bridge.py` is the key tool used to view bridge thread history and verify the lack of drift before actions are taken. Fixing the Unicode crash ensures this tool is reliable on Windows systems.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Compliant specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Bounded to project `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification plan executed below.
- `GOV-STANDING-BACKLOG-001` — Bounded to single work item `WI-4633`.

## Prior Deliberations

None.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20261527` — seed=search; bridge_thread; Loyal Opposition Verification - Platform Tests Ruff Cleanup
- DA: `DELIB-2696` — seed=search; bridge_thread; Loyal Opposition Verification - Platform Tests Ruff Cleanup
- DA: `DELIB-2783` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-02T00:23:25Z
- DA: `DELIB-20261955` — seed=search; bridge_thread; Bridge thread: gtkb-claude-code-bridge-status-thread-automation-001 (4 versions,
- DA: `DELIB-20261633` — seed=search; bridge_thread; Loyal Opposition Review - GT-KB Discoverability CLI Slice 1 REVISED

## Owner Decisions / Input

No owner decisions are required. The standing reliability fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this work stream.

## Requirement Sufficiency

Existing requirements sufficient.

## Spec-Derived Verification Plan

### Automated Tests
- Run the tool with markdown output and verify it does not crash when outputting unicode:
  `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-startup-relay-cache-ttl-self-heal --format markdown`

### Manual Verification
- Verify the tool is executable and outputs valid markdown.

## Risk / Rollback

No risk. Reverting the import and reconfiguration of `sys.stdout` in `show_thread_bridge.py` restores the original behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-show-thread-bridge-windows-unicode`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
