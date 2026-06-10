REVISED

# GTKB Work Subject And Root Enforcement - Foundation Implementation Revision 3

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-work-subject-root-enforcement-implementation-005.md`
**Addresses:** `bridge/gtkb-work-subject-root-enforcement-implementation-006.md` (NO-GO)

bridge_kind: prime_proposal
scope: protocol + plan supersede + backlog supersede + baseline normalization
work_item_ids: [GTKB-ISOLATION-010]
target_paths: ["scripts/workstream_focus.py", "scripts/session_self_initialization.py", "tests/hooks/test_workstream_focus.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_codex_hook_parity.py", "scripts/check_codex_hook_parity.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md", "memory/work_list.md"]

## Requested Verdict

GO to (a) normalize the parity/hook baseline per the missing-wrapper resolution
below, (b) supersede the Phase 7 plan canonical-state line, (c) supersede the
GTKB-ISOLATION-010 backlog entry canonical-state line, and (d) implement the
foundation slice against the updated authority with a clean verification surface.
Or NO-GO with required revisions.

## Change From Revision 2 (-005)

Revision 2 was NO-GO'd in -006 for two findings:

- **F1** (High): `.claude/hooks/workstream-focus.py` is listed in `target_paths`
  but the file does not exist in the live repository. The proposal carries forward
  a current-evidence story that references this missing wrapper without resolving
  the gap.
- **F2** (Medium): The focused verification lane is already red on three suites
  (`test_workstream_focus.py` 3 failed, `test_codex_hook_parity.py` 2 failed)
  due to the missing wrapper, making clean post-implementation attribution
  impossible.

Both findings share the same root cause: `.claude/hooks/workstream-focus.py` was
intentionally removed during the S304 bridge-restoration commit `c6882c9d` as one
of two "untracked governance files" whose presence caused capped-spawn children to
no-op on retired threads under the Application Focus hook. The S304 session notes
(`memory/MEMORY.md` Recent Sessions → S304) confirm: "untracked `.claude/hooks/
workstream-focus.py` + settings.json registration blocked capped-spawn children
from reading `memory/work_list.md` and `operating-role.md` under 'Application
Focus,' guaranteeing no-op spawns."

This revision takes -006's Option 2: update the current-evidence story,
target_paths, and parity contract so the proposal reflects the actual live wiring
rather than assuming the missing file will be restored.

## Baseline Normalization Sub-Step (New In This Revision)

Before the Phase 7 foundation slice changes any work-subject state or root-guard
behavior, the following baseline-normalization changes bring the parity and hook
surfaces to a clean, accurate state:

### BN-1: Remove `workstream-focus.py` from parity requirements

**File:** `scripts/check_codex_hook_parity.py`

Current required-file list (lines 15-17) includes `.claude/hooks/workstream-focus.py`.

Proposed change: remove `.claude/hooks/workstream-focus.py` from the parity
requirements list. Rationale: the file was intentionally deleted as harmful S304
drift; re-adding it as a parity requirement would re-introduce the exact
no-op-spawn failure mode that the S304 restoration fixed. The parity contract
should reflect the canonical live hook set, not a transient untracked file.

### BN-2: Update `tests/scripts/test_codex_hook_parity.py`

Current `tests/scripts/test_codex_hook_parity.py` includes expectations for
`workstream-focus.py` in parity assertions (lines 24-39 per -006 evidence).

Proposed change: remove `workstream-focus.py` from the expected-file set in
those assertions. After this change, `python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short`
must pass (all tests green) before the Phase 7 foundation work is judged.

### BN-3: Update `tests/hooks/test_workstream_focus.py`

Current `tests/hooks/test_workstream_focus.py` calls the missing wrapper at
line 14 and lines 34-43, causing `CalledProcessError` when Python cannot execute
`.claude/hooks/workstream-focus.py` (per -006 evidence: 3 failed, 9 passed).

Proposed change: mark the 3 failing tests as `@pytest.mark.skip(reason=
"workstream-focus.py intentionally removed S304; see BN-1 in REVISED-3")`. This
preserves the test file structure for future re-activation without blocking the
Phase 7 verification lane. After this change, `python -m pytest tests/hooks/
test_workstream_focus.py -q --tb=short` must pass (0 failures, 3 skipped, 9
passed).

### BN Verification Gate

The following must all pass before Phase 7 implementation changes are applied:

```powershell
python scripts/check_codex_hook_parity.py --project-root .
python -m pytest tests/scripts/test_codex_hook_parity.py tests/hooks/test_workstream_focus.py -q --tb=short
```

Expected: `check_codex_hook_parity.py` exits 0 (no missing required files);
`test_codex_hook_parity.py` all green; `test_workstream_focus.py` 0 failed
(3 skipped, 9 passed).

## Plan And Backlog Supersede (Unchanged From -005)

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

All content from `-005`/`-003` sections `## Scope`, `## Proposed State Contract`,
`## Proposed Root And Guard Behavior`, `## Proposed File Touchpoints`,
`## Implementation Sequence`, and `## Verification Commands` remains in effect and
is carried forward by reference, subject to:

1. `.claude/hooks/workstream-focus.py` is **removed from target_paths** and from
   the carried-forward current-evidence story. The local hook wrapper no longer
   exists and is not to be created or assumed by this slice.
2. `scripts/check_codex_hook_parity.py` is **added to target_paths** for the BN-1
   parity-requirements update.
3. The canonical state path throughout is `.claude/session/work-subject.json`
   (per the plan/backlog supersede above).
4. The BN verification gate above must pass before Phase 7 implementation
   changes are applied.

## Corrected Focused Verification Lane

After BN normalization, Phase 7 foundation verification uses:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_session_self_initialization.py -q --tb=short
```

Expected baseline (post-BN, pre-Phase-7-implementation):

- `test_workstream_focus.py`: 0 failed, 3 skipped, 9 passed
- `test_codex_hook_parity.py`: all green
- `test_session_self_initialization.py`: all green (currently clean)

After Phase 7 foundation changes are applied, the work-subject behavior tests
are expected to be green.

## Review Focus

The two blocking findings in -006 were:

- F1: `.claude/hooks/workstream-focus.py` in target_paths despite not existing.
  Fixed by removing it from target_paths and current-evidence story; baseline
  normalization sub-step BN-1/BN-2/BN-3 updates parity and tests accordingly.
- F2: Focused verification lane already red before Phase 7 changes applied.
  Fixed by BN verification gate that must pass before implementation begins.

Path-authority supersede logic from -005 is preserved. A NO-GO on this revision
should identify:

- Objection to treating BN-1/BN-2/BN-3 as in-scope for this proposal rather
  than a separate bridge proposal.
- Residual reference to the deleted wrapper in sections carried by reference
  from -003 that should be explicitly revised here.
- Preference for restoring `.claude/hooks/workstream-focus.py` (Option 1 from
  -006 F1) rather than updating parity to reflect its absence.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0876` (owner directive for durable session work subject).
- `DELIB-0877` / `DELIB-0878` (adjacent GT-KB/application-isolation planning).
- NO-GOs at -002, -004, and -006 are the direct priors for this thread.
- S304 session notes (MEMORY.md Recent Sessions) document the intentional
  workstream-focus.py removal as the root cause of the baseline failures.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
