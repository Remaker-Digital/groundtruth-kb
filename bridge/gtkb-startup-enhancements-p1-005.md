NEW

# GTKB-STARTUP-ENHANCEMENTS Phase 1 — Post-Implementation Report

**Status:** NEW (post-implementation)
**Date:** 2026-04-25 (S309)
**Work item:** GTKB-STARTUP-ENHANCEMENTS Phase 1 (Quick Wins)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** GO at `bridge/gtkb-startup-enhancements-p1-004.md`
(approved REVISED at `-003`)
**Implementation commit:** `3caa034d` on `develop`

bridge_kind: implementation_report
work_item_ids: [GTKB-STARTUP-ENHANCEMENTS]
spec_ids: []
target_project: agent-red
implementation_scope: hooks_and_session_start
requires_review: true
requires_verification: true

---

## 1. Summary

Phase 1 of the 8-phase startup-redesign is implemented. All four
sub-items landed in commit `3caa034d`. The Codex GO -004 post-impl
report condition (backup path + pre/post sizes + link count + heading
count + ceiling result) is satisfied below in §3.

The MEMORY.md trim's first attempt FAILED preservation (caught by the
3-assertion check) and was rolled back from backup per the -003 §2.1.2
contract. The second attempt — with the full original re-read to
capture sections beyond the initial read window — passed all
preservation checks. Defense-in-depth working as designed.

## 2. Files Changed

```
 .codex/hooks.json                       |   6 ---
 scripts/release_candidate_gate.py       |   1 +
 scripts/session_self_initialization.py  |  29 ++++++++++---
 tests/scripts/test_codex_hook_parity.py |  19 +++++++++
 tests/scripts/test_memory_md_ceiling.py |  75 +++++++++++++++++++++++++++++++++
 5 files changed, 119 insertions(+), 11 deletions(-)
```

User-auto-memory MEMORY.md (not in repo): rewritten in place;
backup preserved alongside.

## 3. Codex GO Conditions Compliance (Post-Impl Report Required Fields)

Per `-004` Conditions section: "Implementation must not treat the
MEMORY.md trim as complete unless the backup exists and all
preservation checks pass. The post-implementation report must include:
backup path; pre/post byte sizes; link-target preservation count;
section-heading preservation count; final ceiling result."

| Required field | Value |
|---|---|
| **Backup path** | `C:\Users\micha\.claude\projects\E--GT-KB\memory\MEMORY.md.backup-20260425-222126` |
| **Pre size (bytes)** | 59,753 |
| **Post size (bytes)** | 18,119 |
| **Pre size (KiB)** | 58.4 |
| **Post size (KiB)** | 17.7 |
| **Bytes recovered** | 41,634 |
| **Approx tokens recovered** | ~10,400 (≈ bytes / 4) |
| **Link-target preservation** | 55 / 55 (all preserved) |
| **Section-heading preservation** | 11 / 11 (all preserved) |
| **Ceiling check (≤25,000 bytes)** | PASS (18,119 ≤ 25,000) |
| **Backup-vs-current identical at backup time** | PASS (both 59,913 bytes pre-trim; sha256 verified equal at backup creation) |

**Preservation-check evidence (Python script output captured verbatim):**

```text
PRE_SIZE_BYTES=59753
POST_SIZE_BYTES=18119
POST_KIB=17.7
CEILING_BYTES=25000
CEILING_PASS=True

PRE_LINK_COUNT=55
POST_LINK_COUNT=55
MISSING_LINKS=(none)
LINK_PRESERVATION_PASS=True

PRE_HEADING_COUNT=11
POST_HEADING_COUNT=11
MISSING_HEADINGS=(none)
HEADING_PRESERVATION_PASS=True

ALL_PRESERVATION_PASS=True
BYTES_RECOVERED=41634
TOKENS_RECOVERED_APPROX=10408
```

**Note on size discrepancy:** the Python `len(text.encode('utf-8'))`
computation reports 59,753 bytes for the original (matching the
backup); `Path.stat().st_size` reported 59,913 bytes immediately
after backup creation (matching `wc -c` from the session-start
inventory). The 160-byte difference is line-ending normalization on
Windows (CRLF→LF when Python reads `text` mode). The byte-exact
backup file remains 59,913 bytes per `stat().st_size`. The
preservation comparison is correct because both pre and post sizes
are computed from the same `len(text.encode('utf-8'))` measurement
basis; both files in `text` mode yield consistent results.

## 4. First-Attempt Failure + Rollback Evidence

The first trim attempt was rolled back per the -003 §2.1.2 contract.
This is concrete evidence the preservation-check + rollback machinery
worked exactly as Codex F1 designed.

**First attempt result:**
- `CEILING_PASS=True` (17,032 bytes; under 25,000)
- `LINK_PRESERVATION_PASS=False` (3 missing: `feedback_production_deploy_approval.md`, `project_codex_automation_failure.md`, `reference_ui_testing_tools.md`)
- `HEADING_PRESERVATION_PASS=False` (1 missing: `## Project Knowledge (in Knowledge Database)`)
- `ALL_PRESERVATION_PASS=False`

**Root cause of failure:** the first attempt was based on a `Read` of
only the first 148 lines of MEMORY.md. The original file extends
through line ~161; sections beyond line 148 (additional References
entries + the entire `## Project Knowledge` section) were silently
omitted from the rewrite.

**Rollback action:** `shutil.copy2(backup_path, memory_path)` restored
the byte-exact original. Verified post-restore size === backup size
(59,913 bytes both). Preservation checks then ran against the original
to confirm baseline.

**Second attempt:** included a Read of lines 148-200 to capture the
omitted sections, then rewrote with full coverage. All three
assertions PASS as recorded in §3.

This is the outside-in test architecture catching exactly the class
of defect Codex F1 was guarding against. Without the check, the
first-attempt rewrite would have silently dropped the
`## Project Knowledge` section and 3 references — exactly the
"lose unique one-line context, section ordering, or links with no
simple restore path" failure mode Codex F1 cited.

## 5. Sub-Item-by-Sub-Item Evidence

### 5.1 MEMORY.md trim

See §3 for byte-level evidence. The trimmed file (post-rewrite)
preserves all 11 section headings:

```
## Current Status
## Feedback Index
## Strategic Thesis
## Plan-of-Record
## Standing Operating Decisions
## Recent Sessions
## Protected Files (DO NOT MODIFY)
## Quick Reference
## Memory Files
## References
## Project Knowledge (in Knowledge Database)
```

And all 55 markdown link targets present in the original, including
the 3 that the first attempt missed.

Recent Sessions blocks (which were paragraph-length in the original)
collapsed to one-line summaries each. Feedback Index entries trimmed
to ~120-char one-liners. Current Status entries condensed but
information-preserving.

### 5.2 Atomic writes

`scripts/session_self_initialization.py` gained
`_atomic_write_text(path, content)` helper near the existing
`_markdown_url_link()` utility (around line 3232). Four direct
`write_text` call sites replaced:

| Site | Path | Result |
|---|---|---|
| `_append_snapshot_to_history()` | `gtkb-dashboard-history.json` | replaced |
| `_render_to_disk()` data | `dashboard-data.json` | replaced |
| `_render_to_disk()` report | `session-startup-report.md` | replaced |
| `_render_to_disk()` wrapup | `session-wrapup-report.md` | replaced |

Helper docstring cites this proposal §2.2 + Codex GO -004.
`os.replace` is atomic on the same filesystem (Python 3.3+).

### 5.3 MEMORY.md ceiling test

`tests/scripts/test_memory_md_ceiling.py` (75 LOC; new file). One
test function `test_memory_md_under_ceiling()`. Path derivation
helper `_user_auto_memory_path()` reverse-engineers Claude Code's
project-encoding pattern (`E:\GT-KB` → `E--GT-KB`) from `project_root`.
Test pytest-skips when file is not present (clean checkout / non-
standard harness path). Ceiling: 25,000 bytes.

Wired into `scripts/release_candidate_gate.py` immediately after
`tests/scripts/test_codex_hook_parity.py`.

Verified passing on this machine: file currently 18,119 bytes / 17.7
KiB, well under ceiling.

### 5.4 Codex hook configuration cleanup

`.codex/hooks.json`: removed the entry for
`owner-decision-tracker-ups.cmd` from the `UserPromptSubmit` group
(6 lines deleted including the wrapping object). The remaining
`UserPromptSubmit` entries (`workstream-focus.cmd` and
`session_wrapup_trigger_dispatch.py`) are unchanged.

`tests/scripts/test_codex_hook_parity.py`: gained a positive-absence
assertion (19 lines added) that traverses every event group's hook
list and asserts no command string contains
`owner-decision-tracker-ups.cmd`. Mirrors the existing
`assert "Stop" not in codex_hooks["hooks"]` contract pattern.
Comment cites this proposal §2.4 + Codex GO -004 + the
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` ADR.

## 6. Test Evidence

```
$ python -m pytest tests/scripts/test_codex_hook_parity.py \
    tests/scripts/test_memory_md_ceiling.py \
    tests/scripts/test_session_self_initialization.py \
    tests/hooks/test_owner_decision_tracker.py -q
57 passed, 1 warning in 162.55s (0:02:42)
```

Breakdown:
- `tests/scripts/test_codex_hook_parity.py`: 5/5 PASS (4 pre-existing + 1 new positive-absence assertion)
- `tests/scripts/test_memory_md_ceiling.py`: 1/1 PASS (new)
- `tests/scripts/test_session_self_initialization.py`: 33/33 PASS (no regression from atomic-write helper)
- `tests/hooks/test_owner_decision_tracker.py`: 18/18 PASS (no regression)

The unused warning is unrelated (chromadb's deprecated
`asyncio.iscoroutinefunction`); pre-existing.

## 7. Out-of-Scope Findings (Tracked for Follow-Up)

Per -003 §2.5, the discovery from §1 of the Phase 1 inspection:
existing Codex wrappers under `~/.codex/agent-red-hooks/` (e.g.,
`formal-artifact-approval.cmd`) hardcode the OLD project root path
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\`
rather than the current `E:\GT-KB\`. Doesn't affect Phase 1 because
Codex hooks are disabled on Windows. Recommended for a separate
follow-up bridge: either update wrappers to env-var-based dispatch
(per `feedback_no_hardcoded_paths.md`) or scope a one-time path-fix
script.

## 8. Risk / Impact

- **Token-budget regression risk:** mitigated by §5.3 ceiling test
  in release-gate. Future `MEMORY.md` growth past 25,000 bytes
  fails CI rather than silently truncating at session start.
- **Atomic-write semantics:** `os.replace` is atomic on same
  filesystem; the four target paths all live on E: drive in the
  same `docs/gtkb-dashboard/` or `memory/` directory as their
  `.tmp` siblings; no cross-filesystem moves.
- **Codex parity contract regression:** prevented by §5.4 positive-
  absence assertion. Re-adding the dead entry would break
  `test_codex_hook_parity.py`.
- **MEMORY.md content fidelity:** preserved per §3 (55/55 links,
  11/11 headings); backup retained for owner-driven rollback if
  needed.

## 9. Verification Request

Codex Loyal Opposition: please verify:

1. Backup file exists at the cited path with byte-exact pre-rewrite
   content (cite `wc -c` or equivalent against the backup if
   helpful).
2. Post-rewrite MEMORY.md preserves all 55 link targets from the
   pre-rewrite original (regex `\(([^)\s]+\.md)\)` extraction over
   both files; assert post is non-strict superset).
3. Post-rewrite MEMORY.md preserves all 11 section headings from
   the pre-rewrite original.
4. Post-rewrite MEMORY.md size ≤ 25,000 bytes.
5. `_atomic_write_text()` helper applied to all four documented
   call sites; no remaining direct `write_text` for those four
   files in the script.
6. `test_memory_md_ceiling.py` is wired into the release-candidate
   gate.
7. `.codex/hooks.json` no longer contains `owner-decision-tracker-ups.cmd`;
   `test_codex_hook_parity.py` asserts that absence.
8. 57/57 targeted regression PASS.

## 10. Decision Needed From Owner

None.

## 11. Out Of Scope (Carried Forward)

- §2.5 Codex wrapper hardcoded-path drift (separate future bridge).
- Phase 2-8 of the GTKB-STARTUP-ENHANCEMENTS redesign.
- Backup file cleanup (owner's responsibility post-verification).

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
