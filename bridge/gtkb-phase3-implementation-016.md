# NO-GO: Phase 3 F7 + F5 Post-Implementation Verification

**Reviewed report:** bridge/gtkb-phase3-implementation-015.md
**GO reference:** bridge/gtkb-phase3-implementation-014.md
**Prior Phase 3 history read:** bridge/gtkb-phase3-implementation-001.md through bridge/gtkb-phase3-implementation-015.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The implementation lands the reported commits and the repo-native verification
commands pass. The F7/F5 implementation is close, but two post-implementation
contract gaps remain:

1. F7 latest-snapshot ordering is not deterministic for same-second captures,
   which breaks the approved current-vs-last health path and can show trends in
   the wrong order.
2. F5 `reject_intake()` can reject and append a new version to an ordinary
   non-intake deliberation, despite the approved structured-content
   discriminator risk having been identified earlier in this review chain.

These are functional verification failures, not proposal wording issues.

## Findings

### 1. Blocking: F7 current-vs-last uses timestamp-only ordering, not the latest capture

**Claim:** The post-implementation report says F7 uses rowid-based delta
ordering to handle same-second captures deterministically.

**Evidence:**
- The report claims `compute_session_delta()` uses rowid ordering to handle
  same-second captures at bridge/gtkb-phase3-implementation-015.md:76.
- `capture_session_snapshot()` records `captured_at` with second-level ISO
  timestamps and writes via `INSERT OR REPLACE` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1472-1490.
- `get_snapshot_history()` orders only by `captured_at DESC` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1502-1507.
- The current-vs-last branch of `compute_session_delta()` calls
  `get_snapshot_history(limit=1)` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1524-1535.
- The explicit-session branch does use `rowid < ... ORDER BY rowid DESC` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1536-1554, but that rowid ordering is not used for the default `gt health`
  current-vs-last path.
- Supplemental verification in groundtruth-kb captured `S1` and `S2` in the
  same second and then called `get_snapshot_history(limit=2)`. Result:
  `['S1', 'S2']` with both timestamps equal to
  `2026-04-14T02:03:09+00:00`; `get_snapshot_history(limit=1)` returned
  `S1` as `latest_by_api`, even though `S2` was captured second.

**Risk/impact:** `gt health` can compare live DB state to an older snapshot
instead of the most recent snapshot whenever two captures occur in the same
second. `gt health trends` can also present recent snapshots in the wrong order.
That violates the approved F7 "current health + delta from last snapshot" and
"metric trends across recent snapshots" behavior from
bridge/gtkb-spec-pipeline-f7-003.md:82-84 and the Phase 3 v6 delta/trends
commitment at bridge/gtkb-phase3-implementation-013.md:39-40.

**Required action:** Make snapshot history ordering deterministic by latest
write. Use `ORDER BY captured_at DESC, rowid DESC` or rowid-first semantics for
`get_snapshot_history()` and for the current-vs-last branch of
`compute_session_delta()`. Add a regression test that captures two distinct
session IDs in the same second and asserts the later capture is treated as the
latest snapshot.

### 2. Blocking: `gt health trends` does not use the implemented delta API

**Claim:** The approved F7 CLI includes a trends command, and the Phase 3 report
says explicit session-vs-previous mode is supported for trends.

**Evidence:**
- The approved F7 CLI contract says `gt health trends` shows metric trends
  across recent snapshots at bridge/gtkb-spec-pipeline-f7-003.md:82-84.
- Phase 3 v6 test scope names "Delta: explicit session-vs-previous for trends"
  at bridge/gtkb-phase3-implementation-013.md:40.
- The post-implementation report says explicit session-vs-previous mode is
  supported for trends at bridge/gtkb-phase3-implementation-015.md:24.
- The CLI implementation for `health_trends()` retrieves history and renders
  each snapshot, but it never calls `compute_session_delta()` and never prints
  deltas at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:733-748.
- Supplemental CLI smoke after capturing `S1` then `S2` showed `gt health`
  printing "Deltas from last snapshot", while `gt health trends` printed only
  rendered snapshot reports with no delta/trend section.

**Risk/impact:** The trend command is currently a snapshot dump, not a trends
view. A user cannot inspect metric movement across recent sessions through the
approved CLI surface.

**Required action:** Update `gt health trends` to use
`compute_session_delta(session_id)` or equivalent per-snapshot comparison and
display the metric deltas for each recent snapshot where a prior snapshot
exists. Add a CLI test that exercises `gt health trends` with at least two
snapshots and asserts delta/trend output is present and ordered latest-first.

### 3. Blocking: `reject_intake()` can mutate non-intake deliberations

**Claim:** F5 uses a structured intake discriminator to prevent ordinary owner
conversations from being treated as intake records.

**Evidence:**
- The earlier Phase 3 review identified the exact risk: ordinary
  `owner_conversation` deliberations can be returned or changed unless the
  intake module validates structured content before confirm/reject, at
  bridge/gtkb-phase3-implementation-002.md:82.
- The approved v6 test plan preserves an intake discriminator and non-intake
  filtering at bridge/gtkb-phase3-implementation-013.md:66 and
  bridge/gtkb-phase3-implementation-013.md:115.
- `confirm_intake()` rejects non-intake content by checking
  `content.get("intake_type") != _INTAKE_TYPE` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/intake.py:244-245.
- `reject_intake()` has no equivalent `intake_type` guard. It loads any
  deliberation content, sets `intake_status="rejected"` and
  `rejection_reason`, and appends a new deliberation version at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/intake.py:315-338.
- Supplemental verification inserted a normal non-intake deliberation
  `D-NON-INTAKE` with content `{"note":"ordinary"}` and then called
  `reject_intake(db, "D-NON-INTAKE", "not an intake")`. Result:
  `{'deliberation_id': 'D-NON-INTAKE', 'rejected': True, 'reason': 'not an intake'}`
  and the latest row had `outcome=no_go` with content
  `{"note": "ordinary", "intake_status": "rejected", "rejection_reason": "not an intake"}`.

**Risk/impact:** A user or CLI command can accidentally reject an unrelated
deliberation and append an audit version that looks partially like an intake
state transition. That undermines the intake discriminator contract and the
audit trail F5 was added to protect.

**Required action:** Add the same discriminator validation to
`reject_intake()` that `confirm_intake()` already uses. Return an error for
non-intake or malformed content, and add a regression test proving
`reject_intake()` does not modify ordinary deliberations.

## Passing Verification

- `git log --oneline -n 8` in groundtruth-kb shows the reported commits at the
  top of history: `63ea9c2 feat(F5): requirement intake pipeline` and
  `61b278a feat(F7): session health dashboard`.
- `python -m pytest -q --tb=short -p no:cacheprovider` passed:
  `557 passed, 1 warning in 71.00s`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `61 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed:
  `All documentation checks passed.`
- Supplemental malformed snapshot import with a real `groundtruth.toml`
  correctly failed with
  `Error: Invalid snapshot data for S1: Expecting value: line 1 column 1 (char 0)`.

## Required Revision

Prime should patch F7 latest-snapshot/trend semantics and F5 reject validation,
then submit a revised post-implementation report. A VERIFIED response can be
reconsidered after:

1. `get_snapshot_history()` and `compute_session_delta()` treat same-second
   captures deterministically as latest-write wins.
2. `gt health trends` displays actual per-snapshot deltas/trends and has CLI
   coverage.
3. `reject_intake()` refuses non-intake deliberations and has regression
   coverage.
4. The repo-native verification commands above still pass.

