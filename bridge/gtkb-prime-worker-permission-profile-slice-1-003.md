REVISED

# Implementation Proposal — Prime Worker Permission Profile (Slice 1 of 4) — REVISED-1

bridge_kind: prime_proposal
Document: gtkb-prime-worker-permission-profile-slice-1
Version: 003
Responds to: bridge/gtkb-prime-worker-permission-profile-slice-1-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Claim

REVISED-1 closes both `-002` Codex findings:

- **F1 (P1) closed**: `Specification Links` now cites the missing required spec (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) plus the three missing advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`). Applicability preflight now returns `preflight_passed: true` after INDEX update.
- **F2 (P2) closed**: the test plan now asserts the allow-list contract directly. Non-empty-string assertions removed; replaced with set-superset / set-disjoint assertions over a parsed allow-list. Two new tests added: (a) `test_harness_command_claude_allowed_tools_includes_required_authoring_tools` asserts the parsed set is a superset of `{Read, Edit, Write, Glob, Grep, Bash, TodoWrite, NotebookEdit}`; (b) `test_harness_command_claude_allowed_tools_excludes_interactive_and_network_tools` asserts the set is disjoint from `{AskUserQuestion, WebFetch, WebSearch}` and contains no `mcp__` prefix.

The implementation substance from `-001` is preserved unchanged: add `--permission-mode acceptEdits` and `--allowed-tools "Read Edit Write Glob Grep Bash TodoWrite NotebookEdit"` to the spawned-Claude command in `_harness_command`. Codex branch unaltered.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — the dispatch script (the `_harness_command` modification).
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py` — existing test module; the 6 new tests will live here.
- `E:\GT-KB\bridge\gtkb-prime-worker-permission-profile-slice-1-003.md` — this proposal.
- Runtime spawned-worker dispatch logs at `E:\GT-KB\.gtkb-state\cross-harness-trigger\dispatch-runs\*.log`.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, both target paths are within the GT-KB platform root and do not touch any application tree. Spawned workers inherit the same in-root constraint via `--add-dir <project_root>` (the existing flag; unchanged by this slice).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge as canonical workflow state; dispatch automation preserves protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement boundary; all target paths and runtime artifacts in-root under `E:\GT-KB`; no `applications/` paths touched (closes F1 of `-002`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every governing spec cited in this flat list.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; each linked spec maps to at least one named test.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — dispatch substrate change preserves bridge-thread, dispatch-state, and dispatch-failures audit artifacts (closes F1 advisory from `-002`).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved across bridge thread, sibling slices 2-4, and test artifacts (closes F1 advisory from `-002`).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — proposal lifecycle is NEW → (GO/NO-GO) → VERIFIED per the file-bridge-protocol contract (closes F1 advisory from `-002`).
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — first-line `::init gtkb <mode>` invariant preserved; permission flags do not alter prompt content.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — emitter authority on dispatched prompts; first-line invariant tested.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval discipline; this slice mutates only operational dispatch substrate, not formal artifacts.
- `GOV-STANDING-BACKLOG-001` — no work_item is required for this single-function plumbing change; the fix is operational hygiene, not backlog work.
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — cross-harness trigger is opt-out; this slice does not change opt-in/opt-out, only the dispatched harness's permission posture.
- `.claude/rules/prime-builder-role.md` — Prime Builder operating role; spawned workers operate under Prime Builder authority with explicit allowed-tools surface.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants observed.
- `.claude/rules/codex-review-gate.md` — review gate honored; spec-derived test mapping below.

## Prior Deliberations

- `DELIB-1498` — cross-harness trigger Windows rename-race and liveness-diagnostics review context.
- `DELIB-1513` / `DELIB-1514` — canonical init-keyword syntax reviews; first-line invariant preserved.
- `DELIB-1546` — smart-poller retirement review context establishing the event-driven trigger substrate this slice modifies.
- `DELIB-1717` — AUQ enforcement stack Prime rule context.
- `DELIB-0919` / `DELIB-1109` — ADR isolation/application-placement and project-root-boundary context (cited per F1 closure).
- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO at `-004` (Slice 2) — establishes the cross-harness trigger as canonical bridge automation.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` Codex GO at `-008` — init-keyword first-line invariant documentation.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` VERIFIED — suppression contract (unchanged by this slice).

## Owner Decisions / Input

Two AskUserQuestion answers in S350 (2026-05-14) authorize this work:

1. Question: "Which slicing strategy for the Prime-worker-delivery fix?"
   Answer: **4-slice sequence (recommended)** — Slice 1 = permission-mode + allowed-tools.
2. Question: "Permission-mode choice for spawned Prime workers?"
   Answer: **acceptEdits + explicit allowed-tools (recommended)** — `--permission-mode acceptEdits` + explicit `--allowed-tools` list. PreToolUse governance hooks (`scanner-safe-writer`, `bridge-compliance-gate`, `formal-artifact-approval-gate`, `narrative-artifact-approval-gate`, `implementation_start_gate`, `owner-decision-tracker`) remain active.

Owner directive in S350 (2026-05-14): "Please continue" — interpreted as authorization to address the `-002` NO-GO findings via REVISED-1 in this session rather than waiting for a spawned worker (counterpart-active suppression would otherwise indefinitely defer Prime dispatch while the interactive session is foregrounded).

## Requirement Sufficiency

Existing requirements sufficient. The dispatch behavior contract at `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (prompt syntax) and `GOV-FILE-BRIDGE-AUTHORITY-001` (workflow authority) are unchanged. The new permission-mode behavior is operational scaffolding within the existing contract.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is not a bulk operation against the standing backlog. The fix is a single-function source edit (`_harness_command` in `scripts/cross_harness_bridge_trigger.py`) plus 6 new tests in the existing test module `platform_tests/scripts/test_cross_harness_bridge_trigger.py`. No MemBase insert; no formal-artifact-approval packet required (no protected narrative artifact edited; no governed canonical artifact inserted). `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` does not require bulk-operation evidence here.

## Implementation Plan (Strengthened per F2)

1. **Modify `_harness_command`** in `scripts/cross_harness_bridge_trigger.py:380-403`. The Claude branch returns:
   ```python
   return [
       "claude",
       "-p",
       prompt,
       "--add-dir",
       str(project_root),
       "--output-format",
       "json",
       "--permission-mode",
       "acceptEdits",
       "--allowed-tools",
       "Read Edit Write Glob Grep Bash TodoWrite NotebookEdit",
   ]
   ```
   The `command_handle == "codex"` branch is unchanged.

2. **Update the docstring** at lines 380-390 to document: (a) `acceptEdits` allows Edit/Write without interactive prompts, (b) PreToolUse governance hooks remain the safety floor, (c) the explicit allow-list intentionally excludes `AskUserQuestion`, `WebFetch`, `WebSearch`, and all `mcp__*` tools.

3. **Add 6 regression tests** in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`:
   - `test_harness_command_claude_has_acceptedits_permission_mode`: assert `--permission-mode` appears immediately before `acceptEdits` in the returned list.
   - `test_harness_command_claude_allowed_tools_includes_required_authoring_tools`: split the `--allowed-tools` value by whitespace; assert the resulting set is a superset of `{Read, Edit, Write, Glob, Grep, Bash, TodoWrite, NotebookEdit}`.
   - `test_harness_command_claude_allowed_tools_excludes_interactive_and_network_tools`: assert the resulting set is disjoint from `{AskUserQuestion, WebFetch, WebSearch}` AND contains no string starting with `mcp__`.
   - `test_harness_command_codex_unchanged`: assert codex target returns exactly `["codex", "exec", prompt, "--cd", str(project_root)]`.
   - `test_harness_command_preserves_init_keyword_first_line`: assert the prompt's first line matches the regex `^::init gtkb (pb|lo)$` regardless of permission flag additions.
   - `test_harness_command_permission_flags_only_in_claude_branch`: explicit cross-check — for `target.command_handle == "codex"`, assert `--permission-mode` and `--allowed-tools` are NOT in the returned list.

## Spec-to-Test Mapping

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` → `test_harness_command_preserves_init_keyword_first_line` (first-line invariant).
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` → same test plus `test_harness_command_codex_unchanged` (emitter authority unaltered for non-Claude target).
- `GOV-FILE-BRIDGE-AUTHORITY-001` → `test_harness_command_codex_unchanged` and `test_harness_command_permission_flags_only_in_claude_branch` (dispatch decision and prompt content unchanged for the protocol surface).
- `.claude/rules/prime-builder-role.md` → `test_harness_command_claude_allowed_tools_includes_required_authoring_tools` (worker can act as Prime Builder for normal authoring) and `test_harness_command_claude_allowed_tools_excludes_interactive_and_network_tools` (worker cannot call AUQ or unsolicited network tools; AUQ semantics are owner-context-only).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` → all target paths and runtime artifacts confirmed in-root in the In-Root Placement Evidence section; the existing `--add-dir str(project_root)` flag (unchanged) scopes worker filesystem reads.

## Risks

- **`acceptEdits` is broader than `--add-dir` scope**: the flag accepts Edit/Write on any path the worker tries. *Mitigation:* PreToolUse hooks gate dangerous patterns (`scanner-safe-writer`, `bridge-compliance-gate`, `formal-artifact-approval-gate`, `narrative-artifact-approval-gate`, `implementation_start_gate`). `--add-dir` continues to scope filesystem reads.
- **Tool allow-list too restrictive**: if the worker needs a tool not on the list, it blocks. *Mitigation:* the allow-list covers all tools exercised in normal bridge implementation work observed in current Prime sessions; Slice 4 regression coverage observes worker behavior empirically; missing tools are added in follow-up proposals.
- **Cross-platform behavior**: tested on Windows. *Mitigation:* Slice 4 will catch host-specific divergence; this slice's unit tests assert command shape independent of platform.
- **Worker still hangs on AskUserQuestion call attempt**: with AUQ excluded from allow-list, a worker that tries to call it gets a tool-availability error rather than a permission prompt. *Mitigation:* Slice 2 adds positive enforcement via worker-context-aware tracker; until then, the allow-list exclusion is the floor.

## Rollback

Revert `scripts/cross_harness_bridge_trigger.py:380-403` to remove the two new flags. Remove the 6 new tests. No state migration required.

## Verification Procedure

1. Run `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` — all existing tests must continue to pass; the 6 new tests must pass.
2. Run `python scripts/cross_harness_bridge_trigger.py --diagnose` — liveness summary remains HEALTHY.
3. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1` — `preflight_passed: true`, no missing required or advisory specs.
4. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1` — no blocking clause gaps.
5. Manual end-to-end smoke: file a NEW Prime-actionable bridge entry, observe the cross-harness trigger dispatches a Prime worker, inspect `.gtkb-state/cross-harness-trigger/dispatch-runs/*.stdout.log` to confirm at least one Edit/Write completes without permission denial.

## Acceptance Criteria

- `_harness_command` returns the new flags for Claude targets (6 regression tests pass).
- Codex branch unchanged.
- All preflights pass (applicability + clause).
- Existing test suite continues to pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
