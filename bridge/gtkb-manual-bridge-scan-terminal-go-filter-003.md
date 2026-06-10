NEW

# Post-Implementation Report - Manual Bridge Scan Terminal-GO Filter

bridge_kind: implementation_report
Document: gtkb-manual-bridge-scan-terminal-go-filter
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-manual-bridge-scan-terminal-go-filter-002.md (GO)
Recommended commit type: fix
Work Item: WI-4278

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 9e37a40e-6b5a-44ff-8285-b3d48dbd25cf
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code keep-working-pb scheduled task, autonomous /loop, Windows workspace-write

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: helper_alignment plus regression_tests
kb_mutation_in_scope: false

## Summary

Implemented the GO'd proposal `-001`. The manual bridge scan helper
`.claude/skills/bridge/helpers/scan_bridge.py` previously marked every latest
`GO` as Prime-actionable, producing false Prime work for terminal-kind
governance-review threads whose GO is the deliverable (no implementation
follow-up). The helper now applies the canonical dispatchability rule for latest
`GO` entries — Prime-actionable only when the operative Prime proposal's
`bridge_kind` is not terminal — matching the AXIS 2 surface fix
(`gtkb-axis-2-dispatchable-filter`) and `groundtruth_kb.bridge.notify`.

The helper remains a standalone, dependency-free script. To honor the proposal's
"should not invent a new classifier" constraint without coupling the helper to
the `groundtruth_kb` package, the terminal-kind token set is **mirrored** from
`notify._KIND_TERMINAL_TOKENS` and the mirror is guarded against drift by an
explicit parity test (the proposal's sanctioned second option).

## Implemented Changes

`.claude/skills/bridge/helpers/scan_bridge.py`:
- Added `_KIND_TERMINAL_TOKENS` (mirror of `notify._KIND_TERMINAL_TOKENS`),
  `_PRIME_VERSION_STATUSES`, `_HEADER_READ_BUDGET_BYTES`, and `_BRIDGE_KIND_RE`.
- Added `_operative_prime_path(thread)` — walks the latest-first version chain to
  the operative Prime version (latest `NEW`/`REVISED`), which carries
  `bridge_kind`.
- Added `_is_terminal_kind_go(thread, project_root)` — reads `bridge_kind` from
  the operative file header, normalizes (lowercase + kebab→snake), and matches
  against the terminal tokens. **Fail-open**: missing operative version,
  unreadable file, or absent `bridge_kind` → `False` (keep the GO actionable),
  mirroring the canonical `ambiguous → dispatchable` GO rule in
  `notify._derive_dispatchable`.
- `_role_filter(threads, role, project_root)` now excludes a latest `GO` from
  the Prime actionable list when it is terminal-kind. `NO-GO` is never excluded
  (Prime must revise regardless of kind). Loyal Opposition filtering
  (`NEW`/`REVISED`) is unchanged.
- `scan()` derives `project_root` (from `index_path` when provided, else the
  module `PROJECT_ROOT`) so operative bridge files resolve correctly; inline
  `index_text` with no path fails open.
- Updated the module docstring filter-rules section.

`platform_tests/scripts/test_scan_bridge.py`:
- `test_terminal_kind_go_excluded_from_prime` — terminal-kind `GO` excluded;
  non-terminal `GO` and terminal-kind `NO-GO` preserved (temp-fixture bridge
  files).
- `test_terminal_kind_does_not_affect_lo` — LO `NEW`/`REVISED` unaffected.
- `test_unreadable_operative_go_stays_actionable` — fail-open behavior.
- `test_terminal_tokens_parity_with_canonical_notify` — asserts the mirrored
  token set equals `notify._KIND_TERMINAL_TOKENS` (drift guard).

No KB/schema/formal-artifact mutation. No changes outside `target_paths`.

## Specification Links

Carried forward from `-001`:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is the queue authority;
  consumers must not manufacture actionability beyond the protocol's
  terminal-kind routing rules.
- `GOV-RELIABILITY-FAST-LANE-001` — small reliability defect in a development
  helper, scoped to source + tests, no schema/formal-artifact mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal/report
  cite governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — header cites PAUTH,
  project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan below
  maps behavior to regression tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  — false-positive queue is a durable workflow-artifact problem.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — terminal-kind `GO` entries should not
  remain active Prime work.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner authority for the
  reliability fast-lane standing PAUTH.
- `smart-poller-kind-aware-routing-2026-04-30-009` (REVISED-4) — established the
  terminal-kind routing tokens and the `dispatchable` invariant that this helper
  now mirrors.
- `bridge/gtkb-axis-2-dispatchable-filter-003.md` / `-004.md` — the same
  defect class for the AXIS 2 surface; this report applies the equivalent rule
  to the manual scan helper.

## Specification-Derived Verification Plan

| Linked Spec | Verification Evidence |
|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_scan_bridge.py` — `test_terminal_kind_go_excluded_from_prime` (exclusion + preservation), `test_terminal_kind_does_not_affect_lo`, `test_unreadable_operative_go_stays_actionable`, `test_terminal_tokens_parity_with_canonical_notify`. Result: 15 passed (11 pre-existing + 4 new). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Live execution of `scan_bridge.py --role prime-builder` against the real `bridge/INDEX.md`: the six terminal-kind governance-review `GO` threads are excluded; the `NO-GO` init-keyword thread and the one non-terminal implementation_proposal `GO` are retained. Output snippet below. |

### Commands executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_scan_bridge.py -q
  -> 15 passed in 0.86s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check <both files>          -> All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <both files> -> 2 files already formatted

groundtruth-kb/.venv/Scripts/python.exe .claude/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json
```

### Live-index execution output (prime-builder actionable)

```text
prime actionable count: 2
  NO-GO  gtkb-envelope-init-keyword-amendment-slice-1
  GO     gtkb-manual-bridge-scan-terminal-go-filter

terminal-kind GO threads excluded:
  EXCLUDED  gtkb-session-wrap-procedure-001
  EXCLUDED  gtkb-work-envelope-router-slice-1-001
  EXCLUDED  gtkb-canonical-wrap-keyword-syntax-001
  EXCLUDED  gtkb-session-envelope-durability-001
  EXCLUDED  gtkb-envelope-dispatch-element-001
  EXCLUDED  gtkb-project-completion-drive-payload-001

NO-GO init-keyword still actionable: True
```

Before this fix the helper reported all 8 latest non-VERIFIED actionable
threads as Prime work (6 terminal-kind `GO` + 1 `NO-GO` + 1 real `GO`); after,
it reports only the 2 genuine items.

## Recommended Commit Type

`fix:` — repairs broken behavior (false-positive Prime actionability for
terminal-kind `GO`) in a development helper; no new capability surface, no new
CLI subcommand or flag. Consistent with the proposal header and the GO verdict's
`Recommended commit type: fix`.

## Same-Session Guard

The reviewed proposal `-001` was authored by Codex Prime Builder automation
(harness A, session `keep-working-2026-06-04T11-scan-helper`). This
implementation and report were produced by Claude Code Prime Builder (harness B,
session `9e37a40e-6b5a-44ff-8285-b3d48dbd25cf`) — a different harness implementing
a GO'd proposal, which is the normal forward path, not self-review. Verification
(`VERIFIED`/`NO-GO`) must be authored by a different (Loyal Opposition) session.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
