NEW

# Post-Implementation Report — Fix Init-Keyword Startup-Disclosure Relay Truncation (005)

**Status:** NEW (post-implementation report — awaiting VERIFIED)
**Author:** Prime Builder (claude / harness B)
**Date:** 2026-05-15 (S353)
**Thread:** gtkb-startup-relay-truncation-fix-refile
**Implements:** bridge/gtkb-startup-relay-truncation-fix-refile-003.md (GO at -004)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py"]

**Governing spec:** DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001

## Summary

The GO'd `-003` proposal is implemented. The init-keyword startup-disclosure
relay no longer inlines the ~15 KB owner-visible disclosure into the
UserPromptSubmit `additionalContext`. It now emits a bounded pointer to a
harness-scoped cache file; both SessionStart dispatchers write that cache; the
gate wording authorizes exactly one read-only recovery read; the shared
dashboard report is removed from the automatic relay fallback; and a
missing / inconsistent / wrong-harness cache fails visibly.

All work is within the seven GO'd `target_paths`. `scripts/session_self_initialization.py`
was not modified. No new helper file was added — helper logic is local
functions inside the listed source files.

## Implementation performed

1. `scripts/workstream_focus.py` — replaced `_extract_user_visible_startup` /
   `_cached_startup_disclosure` with `_startup_relay_cache_paths` and
   `_startup_relay_pointer` (reads the harness-scoped cache + metadata sidecar,
   computes sha256, returns a bounded pointer dict or None). Rewrote
   `_startup_gate_message` (explicit single read-only-read exception; no
   contradictory blanket tool prohibition; no shared-report reference). Rewrote
   `_startup_gate_response` to emit a bounded `additionalContext` (gate message
   + pointer block: cache path, byte length, sha256) or a visible
   `_startup_relay_failure_context` diagnostic when the cache is absent or
   inconsistent (sha / byte-length / harness-name mismatch).
2. `.claude/hooks/session_start_dispatch.py` and
   `.codex/gtkb-hooks/session_start_dispatch.py` — added the local
   `_write_startup_relay_cache` helper and called it on the validated
   NORMAL_STARTUP path only. It extracts the `## User-Visible Startup Message`
   content and writes `last-user-visible-startup.md` + a
   `last-user-visible-startup.meta.json` sidecar (harness name, harness id,
   generated timestamp, byte length, sha256) to the harness-scoped hooks
   directory. The bridge auto-dispatch path returns before this call, so bridge
   auto-dispatch payloads never populate the interactive relay cache.
3. Tests T1-T6 added/updated across the four `target_paths` test files.

## Files changed

- `scripts/workstream_focus.py` — bounded pointer relay, gate wording, relay-pointer helpers.
- `.claude/hooks/session_start_dispatch.py` — harness-scoped relay cache write.
- `.codex/gtkb-hooks/session_start_dispatch.py` — harness-scoped relay cache write.
- `platform_tests/hooks/test_workstream_focus.py` — T1/T2/T3/T5; updated 3 pre-existing startup-gate tests for the new gate-message text.
- `platform_tests/scripts/test_claude_session_start_dispatcher.py` — T4 (cache write + bridge-isolation).
- `platform_tests/scripts/test_codex_session_start_dispatcher.py` — T4 (cache write + bridge-isolation).
- `platform_tests/scripts/test_workstream_focus_hook_parity.py` — T6 (cross-harness cache-write parity).

All changes are within the GO'd `target_paths`.

## Specification Links

- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 — the governing constraint; this report implements its Required Behavior 1-6.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 — receiver-side role authority; the relay cache is harness-scoped.
- GOV-SESSION-SELF-INITIALIZATION-001 — fresh-session self-initialization disclosure.
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 — governance startup disclosure relay obligation.
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 — the bounded pointer cuts `additionalContext` from ~15 KB to a small pointer.
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 — the init-keyword that activates the relay path.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — both dispatchers write the cache symmetrically.
- GOV-RELIABILITY-FAST-LANE-001 — fast-lane defect-fix filing path.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — every relevant governing spec cited.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-to-test mapping below maps every behavior clause to an executed test.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact-oriented governance baseline.

## Spec-Derived Verification Evidence

Commands executed and observed results:

```
python -m pytest platform_tests/hooks/test_workstream_focus.py -q
  -> 51 passed, 3 skipped, 1 failed
     (the 1 failure is test_save_state_persists_topology_mode_default --
      pre-existing and unrelated; see Pre-Existing Failure Disclosure below)

python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py \
                 platform_tests/scripts/test_codex_session_start_dispatcher.py \
                 platform_tests/scripts/test_workstream_focus_hook_parity.py -q
  -> 36 passed

python -m ruff check <the 7 target_paths>
  -> All checks passed!

python -m ruff format --check <the 7 target_paths>
  -> scripts/workstream_focus.py and platform_tests/hooks/test_workstream_focus.py: clean.
     The other 5 files report "would reformat" for PRE-EXISTING formatting debt
     (see Pre-Existing Failure Disclosure). The implementation's own added code
     is ruff-format-clean (verified via `ruff format --diff` -- no hunk touches
     the relay-fix code).
```

Spec-to-test mapping (`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`):

| Test | Behavior clause covered |
|---|---|
| T1 `test_startup_gate_emits_bounded_pointer_not_inlined_disclosure` (`test_workstream_focus.py`) | Finding 1 — relay `additionalContext` is a bounded pointer (< 4096 bytes; cache path + byte length + sha256; no inlined disclosure body). |
| T2 `test_startup_gate_message_authorizes_one_read_only_read` (`test_workstream_focus.py`) | Finding 2 / Required Behavior 2-4 — gate wording authorizes one read-only read, requires verbatim relay, prohibits acknowledgement substitution, and drops the contradictory blanket tool prohibition. |
| T3 `test_startup_gate_does_not_consult_shared_dashboard_report` (`test_workstream_focus.py`) | Finding 3 / Required Behavior 5 — the shared `docs/gtkb-dashboard/session-startup-report.md` is not consulted; an absent harness-scoped cache fails visibly. |
| T5 `test_startup_gate_fails_visibly_on_inconsistent_cache` (`test_workstream_focus.py`) | Fail-visibly constraint — an sha-inconsistent cache produces a visible diagnostic and does not mark startup satisfied. |
| T4 `test_startup_relay_cache_written_with_consistent_metadata` + `test_startup_relay_cache_not_written_by_bridge_dispatch_path` (both dispatcher test files) | Required Behavior 5 — SessionStart writes the harness-scoped cache + consistent metadata on the validated normal path; the bridge auto-dispatch path does not populate it. |
| T6 `test_startup_relay_cache_write_is_parity_across_dispatchers` (`test_workstream_focus_hook_parity.py`) | ADR-CODEX-HOOK-PARITY-FALLBACK-001 — both SessionStart dispatchers carry the cache-write implementation. |

Every behavior clause of `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` is
covered by an executed test; all relay-fix tests pass.

## Implementation Conditions Check (from the -004 GO)

1. Implementation only within the seven `target_paths` — PASS (`git diff --name-only` is confined to the seven files).
2. `scripts/session_self_initialization.py` not modified — PASS.
3. No new helper file or module — PASS (helpers are local functions in the listed source files).
4. Automatic relay fallback is the harness-scoped cache, not the shared dashboard report — PASS (`_startup_relay_pointer` reads only the harness-scoped cache; T3 verifies).
5. Missing / malformed / stale / wrong-harness / non-disclosure cache fails visibly and does not mark `startup_response_pending` satisfied — PASS (`_startup_gate_response` returns the `_startup_relay_failure_context` diagnostic; the wrong-harness case is covered by harness-scoped directory placement plus an explicit `harness_name` consistency check; T3 + T5 verify).

## Pre-Existing Failure Disclosure

- `test_save_state_persists_topology_mode_default` fails (`assert 'multi_harness' == 'single_harness'`). This is **pre-existing and unrelated** to the relay fix. Verified: stashing `scripts/workstream_focus.py` to HEAD and re-running the test reproduces the identical failure. The relay-fix diff does not touch `save_state` or topology code. The failure is environment-coupled (the install's role map is multi-harness while the test expects a single-harness default).
- `ruff format --check` reports "would reformat" for five files (the two dispatchers and three dispatcher/parity test files). Verified pre-existing: stashing the changes and re-running `ruff format --check` on the HEAD versions reports the identical five files. The implementation's own added code is ruff-format-clean. Pre-existing formatting debt was not reformatted, to keep this change scoped to the relay fix.
- The rewritten gate message no longer cites `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` / `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`; neither exists in MemBase (tracked separately as WI-3326). Two pre-existing tests that asserted that citation were updated to assert the stable `(init-keyword match)` substring instead.

## Owner Decisions / Input

This work was authorized by AskUserQuestion decisions captured this session
(2026-05-15, S353): owner selected "Draft bridge proposal now" and "Reliability
fast-lane" for the disposition; "Re-file as a new bridge thread" for the
blocked-thread resolution; and "Continue now" to implement under the `-004` GO.

## Recommended Commit Type

`fix:` — repairs the broken init-keyword startup-disclosure relay (a defect);
the harness-scoped cache is the mechanism of the repair, not a new
owner-facing capability surface.

## Risk / rollback

- Scope is startup hook transport and recovery only; startup content generation
  is untouched. Blast radius is the fresh-session relay turn.
- Rollback: revert the seven files to HEAD. The prior `last-session-start.json`
  diagnostic cache is unaffected and remains available.

## Verification Request

Loyal Opposition: please verify the implementation against
`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, confirm the spec-to-test
mapping and the implementation-conditions check, and re-run the listed
commands. Issue VERIFIED if the relay fix satisfies the linked specifications,
or NO-GO with specific findings.
