NEW

# GTKB-STARTUP-ENHANCEMENTS Phase 1 (Quick Wins) — Implementation Proposal

**Status:** NEW (implementation; ready for code on Codex GO)
**Date:** 2026-04-25 (S309)
**Work item:** GTKB-STARTUP-ENHANCEMENTS (filed 2026-04-25 S309 at commit `c8e7c525`; revised with redesign architecture at `bcfa1e7f`)
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Routing:** Agent Red-local. Phase 1 is the lowest-risk slice of the
8-phase startup-redesign plan; subsequent phases (P2 freshness contract,
P3 primer registry, P4 rule consolidation, P5 active-ADR primer, P6
action tray, P7 FP-guard tightening, P8 primer cache) follow as separate
bridges.

bridge_kind: prime_proposal
work_item_ids: [GTKB-STARTUP-ENHANCEMENTS]
spec_ids: []
target_project: agent-red
implementation_scope: hooks_and_session_start
requires_review: true
requires_verification: true

---

## 0. What This Proposal Is

Phase 1 ("Quick Wins") of the GTKB-STARTUP-ENHANCEMENTS redesign. Four
independent sub-items, all low-risk:

1. **Trim user-auto-memory `MEMORY.md`** from ~60KB to ≤25KB by
   consolidating index entries to one line each per the format
   documented in CLAUDE.md.
2. **Atomic writes** for the four session-start output files
   (`dashboard-data.json`, `session-startup-report.md`,
   `session-wrapup-report.md`, `gtkb-dashboard-history.json`) using
   write-to-`.tmp` + `os.replace`.
3. **Release-gate test** that fails when `MEMORY.md` exceeds the
   documented 24.4 KiB ceiling.
4. **Codex hook configuration cleanup**: remove the unreferenced
   `owner-decision-tracker-ups.cmd` entry from `.codex/hooks.json`.
   The wrapper file does not exist on disk, will not be created in
   Phase 1 scope, and the parity verifier in the release-candidate
   gate already covers Codex/Windows. Update
   `tests/scripts/test_codex_hook_parity.py` to assert this
   wrapper-cleanup state.

Net token impact: ~9K tokens recovered (mostly from #1).
Net reliability impact: 3 latent bugs closed (atomic write, ceiling
drift, dead config entry).

## 1. Prior Deliberations

- **`memory/work_list.md`** GTKB-STARTUP-ENHANCEMENTS Active Items entry
  (revised at `bcfa1e7f`) — captures the 6 owner priming objectives and
  the Six Primers + Project Snapshot + Action Tray architecture.
- **`memory/work_list.md`** Next Actionable Items table row 9 — current
  P1 status pointer.
- **Owner decisions captured 2026-04-25 S309 via AskUserQuestion:** full
  rule-file consolidation in P4 (8 → 3 files); P1 quick wins as the
  starting phase. Both decisions are recorded in the work_list entry
  and in commit message of `bcfa1e7f`.
- **`bridge/gtkb-gov-owner-decision-surfacing-slice1-005.md`** —
  post-implementation report for the S309 owner-decision-tracker. Sub-item
  #4 of this Phase 1 cleans up the `.codex/hooks.json` entry that
  was added by that implementation (it was Codex hook intent that
  doesn't fire on Windows + has no on-disk wrapper).
- **`scripts/check_pending_owner_decisions_parity.py`** — the active
  Codex/Windows fallback for owner-decision surfacing. The
  Phase 1 cleanup of the `.codex/hooks.json` entry removes the dead
  entry without changing any operationally-active mechanism.
- **No prior bridge thread for Phase 1 specifically.**

## 2. Implementation Scope

### 2.1 Trim `MEMORY.md`

**Target file:** `~/.claude/projects/E--GT-KB/memory/MEMORY.md` (user
auto-memory; not in the repo). Current size: 59,913 bytes (~58.5 KiB).
Target: ≤25,000 bytes (≤24.4 KiB).

Per CLAUDE.md, MEMORY.md is an index, not a content store. Each entry
should be one line under ~150 chars: `- [Title](file.md) — one-line hook`.
Current state has many multi-line entries with detailed bullets that
should be in their topic file (`feedback_*.md` / `project_*.md`),
not in the index.

**Approach:**
- Walk each section ("Feedback Index", "Strategic Thesis",
  "Plan-of-Record", "Recent Sessions", etc.).
- For each multi-line entry, collapse to one line: `- [Title](file.md) —
  <hook-summary-under-100-chars>`.
- Topic file content stays intact (it's the per-file detail; index just
  points at it).
- Recent Sessions: trim each session block to one line summarizing
  outcome + commits; full session detail belongs in commit messages and
  bridge files, not in MEMORY.md.
- Preserve every entry's pointer; do not delete entries.

**Out of scope for Phase 1:** rewriting topic file content; deleting
historical entries; reorganizing sections. This is a mechanical trim,
not a content audit.

### 2.2 Atomic writes for session-start output files

**Target file:** `scripts/session_self_initialization.py` lines around
2745, 4867, 4872, 4873.

Add a helper near the existing file-I/O utilities:

```python
def _atomic_write_text(path: Path, content: str) -> None:
    """Write text to `path` atomically via write-to-.tmp + os.replace.

    Prevents partial writes from corrupting downstream consumers (the
    Grafana dashboard reading dashboard-data.json; Claude Code reading
    session-startup-report.md as additionalContext) when a process
    crashes or the system loses power mid-write.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
```

Replace the four direct `path.write_text(...)` calls with
`_atomic_write_text(path, ...)`:

| Site | Path | Current call |
|---|---|---|
| `_append_snapshot_to_history()` ~line 2745 | `gtkb-dashboard-history.json` | `history_path.write_text(...)` |
| `_render_to_disk()` ~line 4867 | `dashboard-data.json` | `data_path.write_text(...)` |
| `_render_to_disk()` ~line 4872 | `session-startup-report.md` | `report_path.write_text(...)` |
| `_render_to_disk()` ~line 4873 | `session-wrapup-report.md` | `wrapup_path.write_text(...)` |

**Out of scope for Phase 1:** atomic writes for the lifecycle-guard
JSON, the Codex `last-session-start.json`, and the durable
`memory/pending-owner-decisions.md` (the latter already uses
write-to-`.tmp` + `os.replace` per the S309 owner-decision-tracker
implementation; the others are session-state files where partial-write
risk is lower).

### 2.3 `MEMORY.md` size ceiling test

**New test:** `tests/scripts/test_memory_md_ceiling.py`.

```python
"""Release-gate test: user-auto-memory MEMORY.md must stay below the
documented harness loading ceiling.

Per CLAUDE.md ("MEMORY.md is always loaded into your conversation
context — lines after 200 will be truncated, so keep the index
concise"), the file is silently truncated when it exceeds the harness's
load budget. The owner has observed this at session start with a banner:
"WARNING: MEMORY.md is 58.2KB (limit: 24.4KB) — index entries are too
long." This test fails when the file size exceeds 25,000 bytes (24.4
KiB rounded up) so growth is caught at release time, not at session
start as silent truncation.

The test is skipped when the file is not present on the running
machine (clean checkout, fresh dev environment). It does not enforce
that user-auto-memory exists; it only enforces a ceiling when it does.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 24.4 KiB rounded up. Banner and CLAUDE.md document 24.4KB; binary
# KiB matches the observed banner format (58.5 KiB displayed as 58.2KB).
MEMORY_MD_CEILING_BYTES = 25_000

# User-auto-memory path is reliably derivable from the project root:
# ~/.claude/projects/<encoded-path>/memory/MEMORY.md
# where encoded-path replaces path separators with `--`.
def _user_auto_memory_path(project_root: Path) -> Path:
    parts = project_root.resolve().parts
    drive = parts[0].rstrip(":\\/")
    rest = "-".join(p for p in parts[1:] if p)
    encoded = f"{drive}--{rest}" if drive and rest else (drive or rest)
    return Path.home() / ".claude" / "projects" / encoded / "memory" / "MEMORY.md"


def test_memory_md_under_ceiling() -> None:
    project_root = Path(__file__).resolve().parents[2]
    memory_path = _user_auto_memory_path(project_root)
    if not memory_path.exists():
        pytest.skip(f"User-auto-memory not present at {memory_path}; skip ceiling check.")
    size = memory_path.stat().st_size
    assert size <= MEMORY_MD_CEILING_BYTES, (
        f"MEMORY.md is {size} bytes (~{size / 1024:.1f} KiB), exceeds the "
        f"documented {MEMORY_MD_CEILING_BYTES}-byte (~24.4 KiB) ceiling. "
        "Trim multi-line entries to one line each per the format documented "
        "in CLAUDE.md (`- [Title](file.md) — one-line hook`)."
    )
```

Wired into `scripts/release_candidate_gate.py` pytest list.

### 2.4 Codex hook configuration cleanup

**Target files:** `.codex/hooks.json` + `tests/scripts/test_codex_hook_parity.py`.

Remove the dead Codex UserPromptSubmit hook entry that references the
non-existent wrapper:

```json
{
  "type": "command",
  "command": "cmd /d /s /c C:\\Users\\micha\\.codex\\agent-red-hooks\\owner-decision-tracker-ups.cmd",
  "statusMessage": "Checking pending owner decisions",
  "timeout": 5
}
```

Reason for removal (not creation):
- The wrapper file is not on disk and will not be created in Phase 1.
- Codex hooks are disabled on Windows per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; this entry never fires.
- The active Codex/Windows mechanism for surfacing pending owner
  decisions is `scripts/check_pending_owner_decisions_parity.py` running
  in the release-candidate gate. That mechanism is unchanged.
- A follow-up phase (or separate cleanup bridge) can restore the entry
  + create the wrapper if/when Codex Windows hooks activate.

Update `tests/scripts/test_codex_hook_parity.py` to assert the entry is
absent (mirroring the existing `assert "Stop" not in codex_hooks["hooks"]`
contract). Add a single positive assertion: the
`owner-decision-tracker-ups.cmd` command string is not present in any
Codex hook list.

### 2.5 Out-of-scope discovery (informational; separate follow-up bridge)

While inspecting `.codex/hooks.json` and the existing wrappers, the
Codex wrappers under `~/.codex/agent-red-hooks/` (e.g.,
`formal-artifact-approval.cmd`) hardcode the OLD project root path
(`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\`)
rather than the current `E:\GT-KB\`. This is a configuration-drift bug
unrelated to Phase 1 scope. It does not affect Phase 1's outcome
(Codex hooks are disabled on Windows; wrappers don't fire). Recommend
filing as a separate bridge: either update wrappers to point at
current `E:\GT-KB\` (still hardcoded; bad per
`feedback_no_hardcoded_paths.md`) or replace wrappers with env-var-
based dispatch. Out of Phase 1 scope.

### 2.6 Files NOT modified

- `CLAUDE.md`, `AGENTS.md` (Phase 4 territory; redundant content stays
  for now).
- `.claude/rules/*` (Phase 4 territory; full consolidation comes later).
- `.claude/hooks/*` (no behavior change; only Codex-side config cleanup).
- `scripts/session_self_initialization.py` core logic (only the four
  write-call sites; collectors and rendering unchanged).
- `groundtruth.db` schema (no KB changes in Phase 1).

## 3. Owner-Decision Sequencing

No owner decisions block Phase 1 implementation. The two architectural
decisions (full consolidation; P1 first) are already captured.

The pending DECISION-0001, DECISION-0002, and DECISION-0005 in
`memory/pending-owner-decisions.md` are all doc-paragraph false
positives motivating Phase 7 (FP-guard tightening); they intentionally
remain in pending as live test data and are not touched by Phase 1.

## 4. Implementation Order

Single wave (sub-items independent):

1. Trim `MEMORY.md` to ≤25KB (mechanical; entry-by-entry pass).
2. Add `_atomic_write_text()` helper + replace 4 write-call sites.
3. Create `tests/scripts/test_memory_md_ceiling.py`.
4. Edit `.codex/hooks.json` to remove the dead entry.
5. Update `tests/scripts/test_codex_hook_parity.py` to assert the
   absence (one new assertion).
6. Wire `tests/scripts/test_memory_md_ceiling.py` into
   `scripts/release_candidate_gate.py`.
7. Run targeted regression: `pytest tests/scripts/test_codex_hook_parity.py
   tests/scripts/test_memory_md_ceiling.py
   tests/scripts/test_session_self_initialization.py
   tests/hooks/test_owner_decision_tracker.py -q` — all PASS.
8. Run full release-candidate pytest lane locally to confirm no
   broader regression.
9. Commit with scoped message.
10. File post-implementation report citing commit hash + test results.

## 5. Risk Analysis

### 5.1 Failure modes for the change itself

- **MEMORY.md trim loses information.** Mitigated by: not deleting
  entries, only collapsing to one line; topic files (`feedback_*.md`,
  `project_*.md`) preserve detail; if a one-line summary turns out to
  be insufficient, the topic file is still readable.
- **Atomic write breaks on Windows path semantics.** `os.replace` is
  atomic on the same filesystem on Windows since Python 3.3; the four
  target paths all live on the same drive as their `.tmp` siblings;
  no cross-filesystem moves. Helper handles directory creation
  defensively.
- **Ceiling test fires false-positive in CI without user-auto-memory.**
  Mitigated by: `pytest.skip()` when the file is not present.
- **`.codex/hooks.json` cleanup breaks parity test.** Mitigated by:
  test update lands in same commit; release-candidate gate exercises
  the test before merge.
- **Path encoding for user-auto-memory mismatches harness convention
  on Windows.** The existing path on this machine
  (`C:\Users\micha\.claude\projects\E--GT-KB\memory\MEMORY.md`) confirms
  the encoding pattern. The test's `_user_auto_memory_path()` helper
  would mis-derive on a non-Windows machine but those don't have
  user-auto-memory in the same shape; the `pytest.skip()` covers it.

### 5.2 Failure modes the change prevents

- Silent MEMORY.md truncation past the harness load ceiling (currently
  active; trim closes it; ceiling test prevents recurrence).
- Partial JSON / Markdown writes corrupting Grafana / Claude additional-
  Context (currently latent; atomic write closes).
- Dead Codex hook config drift (currently dormant; cleanup closes).
- Token-budget regression as MEMORY.md grows (ceiling test catches at
  release time).

### 5.3 Rollback

- MEMORY.md trim: `git checkout` is not applicable (file is in user
  auto-memory, not in repo). Restoration requires re-deriving from
  topic files. Mitigation: trim is mechanical; redoing is straightforward.
  The diff is large but each entry's transformation is independent.
- Atomic-write helper: revert to direct `write_text()`; no schema or
  format change.
- Ceiling test: remove the test file + remove the release-gate entry.
- `.codex/hooks.json` cleanup: re-add the entry (one JSON block).

## 6. Codex Review Asks

1. Confirm §2.1 trim approach (mechanical entry-collapse, no content
   deletion, topic files preserved) is acceptable for user-auto-memory
   under the existing memory-management conventions.
2. Confirm §2.2 `_atomic_write_text()` helper signature + the four
   target sites cover the right scope; flag any other write sites in
   `session_self_initialization.py` that should be atomic in Phase 1.
3. Confirm §2.3 ceiling value (25,000 bytes / 24.4 KiB) and the
   path-derivation heuristic in `_user_auto_memory_path()` match the
   harness convention; flag any encoding edge case.
4. Confirm §2.4 cleanup-not-create choice for the dead Codex entry; the
   alternative would be to create the wrapper (creating + tracking
   another machine-local file). Either is defensible; this proposal
   takes the cleanup path.
5. Confirm §2.5 out-of-scope finding (Codex wrapper hardcoded to old
   project path) belongs in a separate bridge; not absorbed here.
6. **GO / NO-GO** on Phase 1 implementation.

## 7. Decision Needed From Owner

None for Phase 1 implementation. Both architectural decisions (full
consolidation, P1 starting point) were captured 2026-04-25 (S309).

## 8. Code Quality Baseline

(Per `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` REVISED;
voluntary pre-emptive compliance demonstrating the format. Baseline is
not yet GO'd; this section is illustrative.)

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | No secrets in any sub-item; MEMORY.md trim never touches credential paths | Source review | n/a |
| CQ-PATHS-001 | Yes | `_user_auto_memory_path()` derives from project_root; `_atomic_write_text()` works on any Path. The §2.5 finding about hardcoded wrapper paths is explicitly out of scope and tracked for follow-up | Source review + §2.5 disclosure | n/a |
| CQ-CONSTANTS-001 | Yes | `MEMORY_MD_CEILING_BYTES = 25_000` is module-level with rationale comment citing the banner format | Source review | n/a |
| CQ-DOCS-001 | Yes | Helper docstrings explain why-atomic; ceiling test docstring cites CLAUDE.md and banner | Source review | n/a |
| CQ-COMPLEXITY-001 | Yes | Helper is ~10 LOC; test is ~20 LOC; both well under §4.1 thresholds | Source review | n/a |
| CQ-TESTS-001 | Yes | Ceiling test covers the new ceiling; existing test_codex_hook_parity gains one positive-absence assertion; no test for the atomic-write helper itself (its correctness is the `os.replace` documented contract) | Source review | n/a |
| CQ-LOGGING-001 | Yes | Trim writes no logs; atomic helper raises on failure (no swallowed errors); ceiling test produces a clear failure message with bytes-and-KiB output | Source review | n/a |
| CQ-SECURITY-001 | N/A | n/a | n/a | No auth/network/external-interface changes; only local file I/O |
| CQ-VERIFICATION-001 | Yes | Level 1 (automated tests) for ceiling; Level 2 (release-gate inclusion) for ceiling test runtime; Level 3 (`pytest` command transcript in §4.7) end-to-end | §2.3 + §4.7 + release-gate wiring | n/a |

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:**
- User-auto-memory `~/.claude/projects/E--GT-KB/memory/MEMORY.md`
  (trim; not in repo)
- `scripts/session_self_initialization.py` (helper + 4 call sites)
- `tests/scripts/test_memory_md_ceiling.py` (new)
- `.codex/hooks.json` (one entry removed)
- `tests/scripts/test_codex_hook_parity.py` (one assertion added)
- `scripts/release_candidate_gate.py` (one new test file in pytest list)

**Implementation NOT yet authorized** until Codex GO on this proposal.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
