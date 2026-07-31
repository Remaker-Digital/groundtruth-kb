GO

reviewer_identity: loyal-opposition/cursor/E
reviewer_harness_id: E
reviewer_session_context_id: 6c8b300-ddc8-4f79-b47c-e0da3ca6a55f
reviewer_model: Fireworks kimi-k2p7-code
reviewer_model_configuration: Cursor interactive Loyal Opposition; transcript-defined LO role

# Loyal Opposition Verdict - Extend Codex Snapshot-Window Containment to All Internal Git-Manager Commands

bridge_kind: lo_verdict
Document: gtkb-wi5368-codex-git-window-command-family
Version: 002
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-001.md
Work Item: WI-5368
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY

## Verdict

GO

## Summary

The proposal completes the hide-only WI-5298 containment by replacing the single exact-argv matcher with a deterministic parser for the full Codex Desktop internal Git-manager command family. The parser requires `git.exe`, exactly one `core.hooksPath=NUL` override, exactly one empty `core.fsmonitor=` override, a non-empty subcommand, `conhost.exe` relationship, and `ChatGPT.exe` ancestry. The only side effect remains `ShowWindowAsync(SW_HIDE)`; no process lifetime, Git execution, dispatcher, or eligibility mutation is introduced.

## Preflight Checks

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5368-codex-git-window-command-family` - **passed** (prelight_passed: true; no missing required specs)
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5368-codex-git-window-command-family` - **passed** (0 blocking gaps)

## Assessment

- The change is bounded to the two declared targets: `scripts/ops/codex_snapshot_window_hider.py` and `platform_tests/scripts/test_codex_snapshot_window_hider.py`.
- The parser is fail-open on ambiguity and fail-closed on marker near-misses, satisfying the nonimpairment requirement.
- Live trace evidence (write-tree, read-tree, diff, status, ls-files, add --pathspec-from-file) is explicitly addressed.
- Cross-harness disposition is neutral: no harness-specific routing or role changes.

## Recommendation

Approved to proceed with implementation. Verification must include the expanded focused tests and, where practical, a live observer that confirms qualifying windows are hidden and every command completes naturally. Atomic finalization of this verdict is deferred due to the current uncommitted predecessor bridge chain.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
