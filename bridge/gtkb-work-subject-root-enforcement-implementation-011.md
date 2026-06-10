REVISED

# GTKB Work Subject And Root Enforcement - Foundation Implementation Revision 5

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-work-subject-root-enforcement-implementation-009.md`
**Addresses:** `bridge/gtkb-work-subject-root-enforcement-implementation-010.md` (NO-GO)

bridge_kind: prime_proposal
scope: protocol + plan supersede + backlog supersede + workstream-focus retirement
work_item_ids: [GTKB-ISOLATION-010]
target_paths: ["scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/check_codex_hook_parity.py", "tests/hooks/test_workstream_focus.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_codex_hook_parity.py", "tests/scripts/test_groundtruth_governance_adoption.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md", "memory/work_list.md"]

## Requested Verdict

GO to (a) complete the Claude-side workstream-focus retirement across parity,
governance-adoption, session-init, and wrapper-exec surfaces; (b) supersede the
Phase 7 plan canonical-state line; (c) supersede the GTKB-ISOLATION-010 backlog
entry canonical-state line; and (d) implement the foundation slice against the
updated authority. Or NO-GO with required revisions.

## Change From Revision 4 (-009)

Revision 4 was NO-GO'd in -010 for two findings:

- **F1** (High): `test_groundtruth_governance_adoption.py` has a third failure
  at line 775 on `.claude/rules/file-bridge-protocol.md` (missing "Startup
  reports" language), unrelated to workstream-focus retirement. Revision 4's
  clean-baseline claim overstated what BN would achieve.
- **F2** (High): `tests/scripts/test_session_self_initialization.py:93` asserts
  `"workstream-focus.py" in model["directives"]["hook_files"]`, which fails
  because the file was retired. Revision 4 claimed that module was "currently
  clean" but it is not.

Revision 5 takes:

- **F1 Option 2**: narrow the clean-baseline claim. The `Startup reports`
  failure at line 775 is an unrelated documentation-governance gap. It is
  explicitly scoped out of this bridge and will be tracked separately. The BN
  gate is redefined to target the **three specific assertions affected by
  workstream-focus retirement** (lines 91, 160, 161), not the test module as
  a whole.
- **F2 Option 1**: add **BN-5** (replacing the previous read-only BN-5) to
  explicitly update `test_session_self_initialization.py:93` as part of this
  retirement bridge.

## Scoping Statement (Explicit)

This bridge retires the Claude-side `workstream-focus.py` hook contract. It
does NOT repair:

- Documentation-governance completeness gaps in the five governance docs
  tested by `test_bridge_authority_is_loaded_by_startup_rules` (requires
  "Startup reports", "cached", "downstream", "permanent" / "standing owner
  authority" language in `AGENTS.md`, `file-bridge-protocol.md`,
  `loyal-opposition.md`, `CODEX-SESSION-BOOTSTRAP.md`, `CODEX-WAY-OF-WORKING.md`).
  That is a separate documentation-sync concern affecting language in
  governance rule files and will be filed as a separate bridge
  (`gtkb-governance-startup-reports-docs-sync` or similar) against the
  existing live failure.

After this bridge lands, `test_groundtruth_governance_adoption.py::test_bridge_authority_is_loaded_by_startup_rules`
is expected to **still fail** on the `Startup reports` assertion at line 775
until that separate documentation-sync bridge lands. The BN gate for this
Phase 7 slice does NOT require that test to pass; it requires the three
specific workstream-focus assertions (lines 91, 160, 161) to pass.

## Retirement Rationale (Unchanged)

Per S304 session notes, `.claude/hooks/workstream-focus.py` was intentionally
deleted in restoration commit `c6882c9d` because the untracked wrapper was
blocking capped-spawn children from reading `memory/work_list.md` and
`operating-role.md`. Restoring or re-registering it would re-introduce that
failure mode. The correct action is to retire all Claude-side surfaces that
still assume its presence.

## Baseline Normalization Sub-Step (Expanded)

### BN-1: Retire workstream-focus.py from parity requirements

**File:** `scripts/check_codex_hook_parity.py`

Remove:
- `WORKSTREAM_FOCUS_HOOK` from the required-files list near lines 15-17.
- Lines 243-244 (the PreToolUse registration check).
- Lines 247-248 (the UserPromptSubmit registration check).
- The `WORKSTREAM_FOCUS_HOOK` constant definition if unused after removal.

### BN-2: Update test_codex_hook_parity.py expectations

**File:** `tests/scripts/test_codex_hook_parity.py`

Remove `workstream-focus.py`-related expectations from parity test cases
(lines 24-39 per -006 evidence).

### BN-3: Skip test_workstream_focus.py failing tests

**File:** `tests/hooks/test_workstream_focus.py`

Mark the 3 failing wrapper-execution tests with
`@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN section")`.
After this edit, `pytest tests/hooks/test_workstream_focus.py` exits 0.

### BN-4: Update test_groundtruth_governance_adoption.py (workstream-focus-only)

**File:** `tests/scripts/test_groundtruth_governance_adoption.py`

Three precise removals (targeting **only** workstream-focus retirement; not
the line-775 Startup reports gap):

- Line 91: remove `".claude/hooks/workstream-focus.py",` from the
  required-artifacts list.
- Line 160: remove
  `assert any("workstream-focus.py" in command for command in prompt_commands)`.
- Line 161: remove
  `assert any("workstream-focus.py" in command for command in pre_tool_commands)`.

Line 775 (`Startup reports` assertion on file-bridge-protocol.md) is **NOT**
modified by this bridge.

### BN-5: Update test_session_self_initialization.py startup-model contract (NEW in this revision)

**File:** `tests/scripts/test_session_self_initialization.py`

Remove line 93:

```python
assert "workstream-focus.py" in model["directives"]["hook_files"]
```

Rationale: `scripts/session_self_initialization.py:2364-2365,2441-2444`
populates `model["directives"]["hook_files"]` from a live glob of
`.claude/hooks/*.py`. Since `workstream-focus.py` was retired, the glob does
not include it, and the assertion fails. The startup-model contract must
reflect the actual live hook set, not a retired file.

Lines 94-96 (workstream_focus label assertions) are **preserved**. The
`workstream_focus` dict is populated from config/session state independent
of the hook file; the "Application Focus" label concept persists even
without the hook-enforcement wrapper. If those lines also turn out to fail
at implementation time, an addendum to this bridge will update them with
evidence.

## BN Verification Gate (Mandatory Before Phase 7 Foundation Edits)

After BN-1/BN-2/BN-3/BN-4/BN-5 are applied, the following must pass:

```powershell
python scripts/check_codex_hook_parity.py --project-root .
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_session_self_initialization.py -q --tb=short
```

Expected (post-BN, pre-Phase-7-implementation):

- `check_codex_hook_parity.py`: exits 0 (`Codex hook parity: OK`).
- `test_workstream_focus.py`: 0 failed (3 skipped, others passing).
- `test_codex_hook_parity.py`: all green.
- `test_session_self_initialization.py`: all green (after BN-5).

Additional targeted-assertion verification for `test_groundtruth_governance_adoption.py`:

```powershell
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```

Expected (post-BN): `2 failed, 28 passed` OR `1 failed, 29 passed`. The
remaining failure(s) are the pre-existing `Startup reports` gap at line 775
(and possibly the duplicate line-774 `bridge/INDEX.md` assertion pattern
in that same test if it fires first). Both are tracked in the separate
governance-docs-sync bridge and are **not** in scope for this retirement.

A release-gate green state on `test_groundtruth_governance_adoption.py`
requires the separate documentation-sync bridge to land. This Phase 7
foundation bridge does not claim release-gate green.

## Plan And Backlog Supersede (Unchanged From -009)

### File: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`

Section `## Durable State Contract` (lines 120-125). Replace
`<application_root>/.groundtruth/session/work-subject.json` with
`<application_root>/.claude/session/work-subject.json` plus the lifecycle-
boundary rationale (unchanged text from -009).

### File: `memory/work_list.md`

Entry `GTKB-ISOLATION-010` `Required outcome` line (lines 139-144). Replace
`.groundtruth/session/work-subject.json` with `.claude/session/work-subject.json`.
One-word path change.

## Implementation Slice (Carried Forward From -009)

Phase 7 foundation content from `-003`/`-005`/`-007`/`-009` sections
`## Scope`, `## Proposed State Contract`, `## Proposed Root And Guard Behavior`,
`## Proposed File Touchpoints`, `## Implementation Sequence`, and
`## Verification Commands` remains in effect, subject to:

1. `.claude/hooks/workstream-focus.py` remains removed from target_paths.
2. `scripts/check_codex_hook_parity.py` is in target_paths for BN-1.
3. `tests/scripts/test_groundtruth_governance_adoption.py` is in target_paths
   for BN-4 only (three specific line removals; not the Startup reports fix).
4. `tests/scripts/test_session_self_initialization.py` is in target_paths for
   BN-5 (line 93 removal).
5. The canonical state path throughout is `.claude/session/work-subject.json`.
6. The BN verification gate above must pass before Phase 7 implementation
   changes are applied.

## Review Focus

The two blocking findings in -010 were:

- **F1**: `test_groundtruth_governance_adoption.py` had a third failure
  unrelated to workstream-focus retirement (line 775 Startup reports).
  Resolved by Option 2: explicitly scoping that failure out and tracking it
  in a separate bridge.
- **F2**: `test_session_self_initialization.py:93` asserts workstream-focus.py
  in hook_files. Resolved by Option 1: BN-5 updates that assertion.

Path-authority supersede from -005/-007/-009 is preserved. A NO-GO on this
revision should identify:

- Additional tracked surfaces advertising workstream-focus.py beyond the
  five files covered by BN-1/BN-2/BN-3/BN-4/BN-5.
- Objection to scoping the `Startup reports` repair into a separate bridge.
- Evidence that lines 94-96 of test_session_self_initialization.py also
  fail after BN-5 (requiring an expanded BN-5).

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0876` (owner directive for durable session work subject).
- `DELIB-0877` / `DELIB-0878` (adjacent GT-KB/application-isolation planning).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex-side hooks intent-only).
- NO-GOs at -002, -004, -006, -008, -010 are the direct priors.
- S304 session notes document the intentional workstream-focus.py removal.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
