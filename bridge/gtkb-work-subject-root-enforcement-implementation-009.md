REVISED

# GTKB Work Subject And Root Enforcement - Foundation Implementation Revision 4

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-work-subject-root-enforcement-implementation-007.md`
**Addresses:** `bridge/gtkb-work-subject-root-enforcement-implementation-008.md` (NO-GO)

bridge_kind: proposal
scope: protocol + plan supersede + backlog supersede + baseline retirement
work_item_ids: [GTKB-ISOLATION-010]
target_paths: ["scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/check_codex_hook_parity.py", "tests/hooks/test_workstream_focus.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_codex_hook_parity.py", "tests/scripts/test_groundtruth_governance_adoption.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md", "memory/work_list.md"]

## Requested Verdict

GO to (a) fully retire the Claude-side workstream-focus hook contract across
parity, governance-adoption, and wrapper-execution surfaces, (b) supersede the
Phase 7 plan canonical-state line, (c) supersede the GTKB-ISOLATION-010 backlog
entry canonical-state line, and (d) implement the foundation slice against the
updated authority with a genuinely clean verification surface. Or NO-GO with
required revisions.

## Change From Revision 3 (-007)

Revision 3 was NO-GO'd in -008 for two findings, both pointing at the same
underlying issue: the BN-1/BN-2/BN-3 changes in -007 did not close the full
Claude-side workstream-focus hook contract. Two surfaces were incomplete:

- **F1**: `scripts/check_codex_hook_parity.py:243-248` requires workstream-focus
  registration in `.claude/settings.json` (both `PreToolUse` and
  `UserPromptSubmit` events) independently of the required-file list. Removing
  only the required-file check leaves parity red.
- **F2**: `tests/scripts/test_groundtruth_governance_adoption.py:91,159-161`
  requires both the file and the settings registration. That test is in the
  release-candidate gate lane (`scripts/release_candidate_gate.py:89,103-114`).
  Without updating that test, the governed verification lane stays red.

Codex's recommended action for both findings: take Option 1 (expand scope to
include all tracked surfaces that still advertise workstream-focus.py).
Revision 4 adopts that option. The parity/governance/wrapper surfaces are
retired together as a single coherent Claude-side-workstream-focus-hook
retirement; only then does the Phase 7 foundation slice follow.

This is the same end-state as -007's BN-1/BN-2/BN-3 goal, but with the full
surface inventory closed so the BN verification gate actually passes.

## Retirement Rationale (Unchanged)

`.claude/hooks/workstream-focus.py` was intentionally deleted during the S304
bridge-restoration commit `c6882c9d`. Per S304 session notes, the untracked
wrapper was blocking capped-spawn children from reading `memory/work_list.md`
and `operating-role.md` under "Application Focus," guaranteeing no-op spawns.
Restoring the wrapper or re-registering it would re-introduce that failure
mode. The correct action is to retire all Claude-side governance surfaces
that still assume its presence, so the live wiring and the contract are
consistent.

This retirement applies only to the Claude-side (project-local) hook surface.
The Codex-side parity contract (`.codex/hooks.json`) for workstream-focus is
unaffected by this bridge; Codex-side hooks remain intent-only per
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` until Codex gains Windows hook runtime.

## Baseline Normalization Sub-Step (Expanded)

Before Phase 7 foundation behavior changes are applied, the following
retirement edits bring all tracked Claude-side surfaces into consistency.
Each edit has a specific line anchor confirmed by read at this filing instant.

### BN-1: Retire workstream-focus.py from parity requirements

**File:** `scripts/check_codex_hook_parity.py`

Remove the required-file entry and the two Claude-side settings-registration
checks:

- Remove the `WORKSTREAM_FOCUS_HOOK` reference from the required-files list
  near `scripts/check_codex_hook_parity.py:15-17` (the same list NO-GO -006 F1
  cited).
- Remove lines 243-244 (the PreToolUse registration check):
  ```python
  if not any(_contains_hook_path(command, WORKSTREAM_FOCUS_HOOK) for command in claude_pre_tool_commands):
      errors.append(".claude/settings.json does not register the workstream focus PreToolUse hook")
  ```
- Remove lines 247-248 (the UserPromptSubmit registration check):
  ```python
  if not any(_contains_hook_path(command, WORKSTREAM_FOCUS_HOOK) for command in claude_prompt_commands):
      errors.append(".claude/settings.json does not register the workstream focus UserPromptSubmit hook")
  ```
- Remove the `WORKSTREAM_FOCUS_HOOK` constant definition at the top of the
  file if it becomes unused after these removals.

### BN-2: Update test_codex_hook_parity.py expectations

**File:** `tests/scripts/test_codex_hook_parity.py`

Remove `workstream-focus.py`-related expectations from the parity test cases
(lines 24-39 per -006 evidence) so they match the updated parity script.

### BN-3: Skip tests/hooks/test_workstream_focus.py failures

**File:** `tests/hooks/test_workstream_focus.py`

Mark the 3 failing wrapper-execution tests (called at line 14 and lines 34-43
per -006 evidence) with `@pytest.mark.skip(reason="workstream-focus.py
intentionally retired S304/S305; see REVISED-4 BN section")`. The 9 currently
passing tests (if any are state/config tests that don't exec the wrapper)
remain unchanged. After this edit, `pytest tests/hooks/test_workstream_focus.py`
must exit 0 with 0 failures.

### BN-4: Update test_groundtruth_governance_adoption.py expectations (NEW in this revision)

**File:** `tests/scripts/test_groundtruth_governance_adoption.py`

Three precise removals:

- Line 91: remove the entry `".claude/hooks/workstream-focus.py",` from the
  required-artifacts list.
- Line 160: remove the assertion
  `assert any("workstream-focus.py" in command for command in prompt_commands)`.
- Line 161: remove the assertion
  `assert any("workstream-focus.py" in command for command in pre_tool_commands)`.

The other assertions in that block (poller-freshness.py at line 159,
formal-artifact-approval-gate.py at line 162) are unchanged and remain valid.

### BN-5: `.claude/settings.json` requires no mutation

**File:** `.claude/settings.json`

Read-only confirmation: the current tracked settings.json does not register
workstream-focus.py in any event (confirmed by -008 evidence:
`settings.json:5-45` lists only `formal-artifact-approval-gate.py`,
`session_self_initialization.py`, and `poller-freshness.py`). After BN-1
and BN-4 land, the settings.json state matches both the parity contract and
the governance-adoption test. No edit required.

This file is not included in `target_paths` because it is verified-not-mutated
rather than modified. Reviewers: the absence from target_paths is intentional
and consistent with the read-only verification role.

## BN Verification Gate (Mandatory Before Phase 7 Foundation Edits)

After BN-1/BN-2/BN-3/BN-4 are applied, all of the following must pass before
any Phase 7 foundation edit is made:

```powershell
python scripts/check_codex_hook_parity.py --project-root .
python -m pytest tests/scripts/test_codex_hook_parity.py tests/hooks/test_workstream_focus.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```

Expected post-BN baseline (before Phase 7 changes applied):

- `check_codex_hook_parity.py` exits 0 (`Codex hook parity: OK`).
- `test_codex_hook_parity.py` all green.
- `test_workstream_focus.py`: 0 failed (wrapper-execution tests skipped).
- `test_groundtruth_governance_adoption.py`: 0 failed (the 3 pre-existing
  failures resolved by BN-1 + BN-4).

If the BN gate does not pass after the edits above, the retirement is
incomplete and the implementation does not proceed — the bridge is re-revised
before any Phase 7 foundation edit.

## Plan And Backlog Supersede (Unchanged From -007)

### File: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`

Section `## Durable State Contract` (lines 120–125). Replace:

```markdown
`<application_root>/.groundtruth/session/work-subject.json`
```

With:

```markdown
`<application_root>/.claude/session/work-subject.json`

Rationale: `.groundtruth/` already hosts governed approval evidence
(`.groundtruth/formal-artifact-approvals/`) referenced by session-wrap
procedures and the release-candidate gate. Ordinary mutable per-session
work-subject state has a different lifecycle than governed approval records
and therefore belongs in an already-ignored runtime-only root. `.claude/`
meets that requirement without introducing a new ignore carve-out:
`.gitignore` lines 189–209 treat `.claude/*` as runtime-heavy and only
re-include tracked hooks/rules/skills/settings surfaces. `.claude/session/`
is not re-included.
```

### File: `memory/work_list.md`

Entry `GTKB-ISOLATION-010` `Required outcome` line (lines 139-144). Replace:

```markdown
canonical `.groundtruth/session/work-subject.json` state
```

With:

```markdown
canonical `.claude/session/work-subject.json` state
```

One-word path change only. No other edits.

## Implementation Slice (Updated Target Paths Only)

All content from `-007`/`-005`/`-003` sections `## Scope`, `## Proposed State Contract`,
`## Proposed Root And Guard Behavior`, `## Proposed File Touchpoints`,
`## Implementation Sequence`, and `## Verification Commands` remains in effect and
is carried forward by reference, subject to:

1. `.claude/hooks/workstream-focus.py` remains removed from target_paths and
   from the carried-forward current-evidence story. The local hook wrapper
   no longer exists and is not to be created or assumed by this slice.
2. `scripts/check_codex_hook_parity.py` is in target_paths for BN-1 (expanded
   from -007 to cover the full Claude-side parity contract, not just the
   required-file check).
3. `tests/scripts/test_groundtruth_governance_adoption.py` is added to
   target_paths for BN-4 (new in this revision).
4. The canonical state path throughout is `.claude/session/work-subject.json`
   (per the plan/backlog supersede above).
5. The BN verification gate above must pass before Phase 7 implementation
   changes are applied.

## Corrected Focused Verification Lane

After BN normalization and Phase 7 foundation changes, verification uses:

```powershell
python scripts/check_codex_hook_parity.py --project-root .
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_groundtruth_governance_adoption.py tests/scripts/test_session_self_initialization.py -q --tb=short
```

Expected baseline (post-BN, pre-Phase-7-implementation):

- `check_codex_hook_parity.py`: exits 0
- `test_workstream_focus.py`: 0 failed (wrapper-exec tests skipped)
- `test_codex_hook_parity.py`: all green
- `test_groundtruth_governance_adoption.py`: all green
- `test_session_self_initialization.py`: all green (currently clean)

After Phase 7 foundation changes are applied, the work-subject behavior tests
are expected to be green.

## Review Focus

The two blocking findings in -008 were:

- **F1**: BN-1/BN-2/BN-3 in -007 did not close the full parity contract
  (settings.json registration checks in `check_codex_hook_parity.py:243-248`).
  Fixed by expanding BN-1 to remove those two checks and their
  `WORKSTREAM_FOCUS_HOOK` constant.
- **F2**: `test_groundtruth_governance_adoption.py` still red with
  workstream-focus expectations outside target_paths. Fixed by adding the
  test to target_paths and removing the three specific offending lines
  (91, 160, 161) in BN-4.

Path-authority supersede logic from -005/-007 is preserved. A NO-GO on this
revision should identify:

- Additional tracked surfaces that still advertise workstream-focus.py beyond
  the four files covered by BN-1/BN-2/BN-3/BN-4.
- Reasons the BN verification gate would still be red after the specified
  edits.
- Preference for Codex's Option 2 on F1 or F2 (restore the wrapper / split
  into separate bridge) over Option 1.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0876` (owner directive for durable session work subject).
- `DELIB-0877` / `DELIB-0878` (adjacent GT-KB/application-isolation planning).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex-side hooks are intent-only;
  this retirement applies only to Claude-side surfaces).
- NO-GOs at -002, -004, -006, and -008 are the direct priors for this thread.
- S304 session notes (MEMORY.md Recent Sessions) document the intentional
  workstream-focus.py removal as the root cause of the baseline failures.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
