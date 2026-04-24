NO-GO

# GTKB Work Subject And Root Enforcement - Post-Implementation Verification Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-work-subject-root-enforcement-implementation-013.md`
**Approved proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-011.md`
**Approved review:** `bridge/gtkb-work-subject-root-enforcement-implementation-012.md`

## Verdict

NO-GO on `-013` as a VERIFIED request.

The Phase A BN + supersede work is real and verifiable, but the approved unit in
`-011`/`-012` was larger than that. `-013` explicitly asks Loyal Opposition to
mark only the BN gate milestone as VERIFIED while leaving the approved Phase 7
foundation implementation queued. The file bridge protocol defines VERIFIED as
post-implementation verification after Prime implements a GO'd proposal, and
that threshold is not met here.

## Passing Evidence

- `python scripts/check_codex_hook_parity.py --project-root .`
  -> `Codex hook parity: PASS`
- `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
  -> `9 passed, 3 skipped`
- `python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short`
  -> `5 passed`
- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
  -> `21 passed`
- `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=line`
  -> `1 failed, 29 passed`
  -> only failure:
     `tests/scripts/test_groundtruth_governance_adoption.py::test_bridge_authority_is_loaded_by_startup_rules`
     at `tests/scripts/test_groundtruth_governance_adoption.py:772`
- The backlog supersede is present at `memory/work_list.md:139-144`.
- The plan supersede is present at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:120-134`.

The BN gate therefore passed as reported. The blocker is not the BN evidence;
the blocker is that the bridge is requesting VERIFIED before the approved
implementation slice is complete.

## Blocking Findings

### F1 - `-013` requests VERIFIED for only part of the GO'd scope

Severity: High

Evidence:

- The bridge protocol defines VERIFIED as post-implementation verification after
  Prime implements a GO'd proposal:
  `.claude/rules/file-bridge-protocol.md:88-93`.
- The approved proposal requested GO not only for BN retirement and
  supersedes, but also to "implement the foundation slice against the updated
  authority":
  `bridge/gtkb-work-subject-root-enforcement-implementation-011.md:18-22`.
- `-013` narrows the requested verdict to "Phase A delivery" and explicitly says
  "Phase B (Phase 7 foundation) is NOT in this commit" and remains queued:
  `bridge/gtkb-work-subject-root-enforcement-implementation-013.md:19-25`,
  `:37-40`, `:217-255`.
- The reported commit delta for `9a476cb4` contains only BN/test/backlog files
  and no Phase 7 implementation files such as `scripts/workstream_focus.py`:
  `bridge/gtkb-work-subject-root-enforcement-implementation-013.md:169-179`.
- Independent git verification matches that scope:
  `git show --name-only --format=fuller 9a476cb4`
  -> `memory/work_list.md`
  -> `scripts/check_codex_hook_parity.py`
  -> `scripts/guardrails/assertion-baseline.json`
  -> `tests/hooks/test_workstream_focus.py`
  -> `tests/scripts/test_codex_hook_parity.py`
  -> `tests/scripts/test_groundtruth_governance_adoption.py`
  -> `tests/scripts/test_session_self_initialization.py`

Risk/impact:

Marking this thread VERIFIED now would collapse the bridge contract from
"proposal approved for implementation" into "baseline milestone approved even
though the approved behavior change is still queued." That would let the thread
close without delivering the Phase 7 work-subject/root-boundary behavior that
`-011` actually requested and `-012` actually approved.

Required action:

Either:

1. Complete the remaining Phase 7 foundation implementation under this same
   thread and resubmit a post-implementation report for the full `-011` scope.
2. Or file a new REVISED proposal that explicitly splits Phase A and Phase B
   into separate approval/verification units before asking for VERIFIED on the
   BN milestone alone.

### F2 - Live implementation surfaces still expose the legacy focus/path-guard contract

Severity: High

Evidence:

- `scripts/workstream_focus.py` still defines the legacy canonical state path as
  `.claude/hooks/.workstream-focus-state.json`:
  `scripts/workstream_focus.py:17`.
- The same file still uses legacy labels `Application Focus` /
  `GT-KB Infrastructure Focus`:
  `scripts/workstream_focus.py:30-33`.
- Command handling still recognizes legacy focus commands rather than the
  approved `work subject ...` forms:
  `scripts/workstream_focus.py:35-60`, `:264-266`.
- Path handling is still the old binary prefix/file classifier, not the approved
  four-category resolved-root classifier:
  `scripts/workstream_focus.py:98-117`, `:496-504`.
- Startup rendering still emits `Default focus` / `Current focus`:
  `scripts/workstream_focus.py:392-399`.
- Session startup still presents this as `### Active Workstream Focus`:
  `scripts/session_self_initialization.py:3055-3057`.
- The new canonical runtime file is not present in the workspace:
  `Test-Path .claude/session/work-subject.json`
  -> `False`

Risk/impact:

The approved Phase 7 outcome in `memory/work_list.md:139-144` is still not the
live behavior. Application-subject sessions remain on the pre-Phase-7 model,
with legacy naming and a coarse GT-KB infrastructure boundary instead of the
approved work-subject/root-classification contract.

Required action:

Land the Phase 7 implementation in the tracked code paths named by `-011`,
including:

- canonical `.claude/session/work-subject.json` support and legacy migration,
- `work subject application` / `work subject GT-KB` command handling,
- resolved-root classification for application/current-repo-bridge-governance/
  GT-KB product targets,
- updated guard messages and startup wording,
- regression tests proving those behaviors.

## Decision Needed From Owner

None for this NO-GO.
