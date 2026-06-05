REVISED
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE
Work Item: WI-4355

# Post-Implementation Report REVISED — Verb-Aware Path Extraction (F1 fix)

bridge_kind: implementation_report
Document: gtkb-impl-start-gate-verb-aware-path-extraction
Version: 007
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-impl-start-gate-verb-aware-path-extraction-006.md (Codex NO-GO)

## Summary

REVISED -007 addresses Codex NO-GO `-006` finding F1: the prior implementation correctly added verb-aware path extraction for `git add`, `git rm`, and `git restore`, but did NOT update the mutating-command predicate. As a result, `_is_mutating_command("git add scripts/protected.py")` returned False and the gate allowed these commands without an implementation authorization packet.

The F1 fix landed in commit `96c07db5`. Single-line regex extension to `MUTATING_COMMAND_RE` adds `add|rm|restore` to the git-verb alternation. 4 new tests cover the protected verbs (True) plus a `git status` regression guard (False).

## Specification Links

Carried forward from prior cycles unchanged:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the table below.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility under standing PAUTH for this defect-class fix.
- `GOV-STANDING-BACKLOG-001` — governance contract for standing backlog.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.
- `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` — the design constraint motivating this work, including the F1 acceptance assertion.

## Revision Notes (REVISED -007 vs -005)

Changes addressing Codex NO-GO `-006` finding F1 (`_is_mutating_command` not firing on protected git verbs):

1. **Source change in `scripts/implementation_start_gate.py`:** extended `MUTATING_COMMAND_RE`'s git-verb alternation from `commit|reset|checkout|merge|rebase|tag|push` to `add|rm|restore|commit|reset|checkout|merge|rebase|tag|push`. The added verbs match the path-extraction surface that the prior implementation already added.

2. **4 new anti-regression tests in `platform_tests/scripts/test_implementation_start_gate_verb_aware.py`:**
   - `test_is_mutating_git_add_returns_true` — `git add scripts/protected.py`, `git add -A`, `git add .` all return True.
   - `test_is_mutating_git_rm_returns_true` — `git rm <path>`, `git rm --cached <path>` return True.
   - `test_is_mutating_git_restore_returns_true` — `git restore --staged <path>` and `git restore <path>` return True.
   - `test_is_mutating_git_status_remains_false` — `git status` + `git status --short` remain False (regression guard against over-broad regex changes).

3. **No changes to the verb-aware path extraction surface itself** (`_paths_from_shell`, the `_extract_git_*` helpers, `MUTATING_VERB_TABLE`). The prior implementation correctly extracted paths for these verbs; the only missing piece was the `_is_mutating_command` predicate firing on them.

## Spec-to-Test Mapping (executed)

| Spec / Acceptance Item | Test | Result |
|---|---|---|
| `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` — `git add <path>` extracts the path AND fires the gate | `test_is_mutating_git_add_returns_true` (predicate side) + existing extraction tests | **PASS** |
| Same — `git rm <path>` fires the gate | `test_is_mutating_git_rm_returns_true` + extraction tests | **PASS** |
| Same — `git restore --staged <path>` fires the gate | `test_is_mutating_git_restore_returns_true` + extraction tests | **PASS** |
| Regression guard — `git status` remains a safe read | `test_is_mutating_git_status_remains_false` | **PASS** |
| Full module regression | `pytest test_implementation_start_gate_verb_aware.py` | **46 passed (42 prior + 4 new)** |
| Ruff lint + format | `ruff check + ruff format --check` on the 2 changed files | **CLEAN** |

## Verification Commands (observed)

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate_verb_aware.py
46 passed in 0.84s

python -m pytest platform_tests/scripts/test_implementation_start_gate_verb_aware.py -k "is_mutating"
4 passed, 42 deselected in 0.50s

python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate_verb_aware.py
All checks passed!

python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate_verb_aware.py
2 files already formatted
```

## Files Changed (cumulative across thread)

This REVISED cycle's commit:

- `scripts/implementation_start_gate.py` — 6-character regex extension on `MUTATING_COMMAND_RE`.
- `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` — 4 new test functions.

Cumulative thread history:

- Prior cycles landed the verb-aware path extraction surface (`_paths_from_shell` + `_extract_git_*` helpers + `MUTATING_VERB_TABLE`).
- Commit `96c07db5 fix(gate)` — F1 fix (this REVISED cycle's load-bearing commit).

## Implementation Authorization

- Packet: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-impl-start-gate-verb-aware-path-extraction.json`
- GO file: `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-004.md`
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE` (active)
- Owner-decision authority: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing fast-lane direction for defect-class fixes.

## Owner Decisions / Input

No new owner decision required. The fix is a within-protocol mechanical defect repair (Codex NO-GO -006 F1) covered by the project authorization. WI origin: defect; covered by the standing reliability fast-lane authorization per `GOV-RELIABILITY-FAST-LANE-001`.

## Risk and Rollback

**Risk after merge:** Minimal. The regex extension is purely additive — `git add`, `git rm`, and `git restore` now trip the predicate, but `_paths_from_shell` already extracted paths for them, so the gate fires with the correct target path context. Existing protected-path enforcement gains coverage without behavior change for previously-mutating verbs. The `git status` regression guard catches over-broad regex drift in future changes.

**Rollback:** Revert commit `96c07db5`. The path-extraction surface (committed in prior cycles) remains intact.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing fast-lane direction.
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-001..006` — prior thread history including the GO-4 acceptance + the NO-GO-6 finding.

No retrieved deliberation rejects the regex extension approach.

## Notes for Loyal Opposition

The fix is minimal-surface: a single-line regex extension plus 4 anti-regression tests. The `git status` regression guard explicitly anchors the test surface against future over-broad changes. The fix preserves the prior implementation's path-extraction surface unchanged — the only delta is making `_is_mutating_command` return True for the protected verbs whose paths were already being extracted.

The substantive guarantee Codex called for in -006 F1 ("`git add scripts/protected.py` extracts a path AND the gate fires") is now satisfied by the combination of the pre-existing `_paths_from_shell` extraction and the post-fix `_is_mutating_command` predicate.

## Recommended Commit Type

`docs(bridge):` — this REVISED report adds bridge documentation only; the substantive F1 fix is already in HEAD as commit `96c07db5`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
