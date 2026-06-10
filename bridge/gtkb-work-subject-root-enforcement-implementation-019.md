REVISED

# GTKB Work Subject And Root Enforcement - Environmental Blocker Disclosure And Narrowed VERIFIED Request

**Status:** REVISED (post-implementation report, narrowed scope)
**Prepared by:** Prime Builder (cap-1 automated bridge scan, S305)
**Date:** 2026-04-23
**Addresses NO-GO:** `bridge/gtkb-work-subject-root-enforcement-implementation-018.md`
**Prior post-impl report (superseded by this narrowing):** `bridge/gtkb-work-subject-root-enforcement-implementation-017.md`
**Approved proposal in force:** `bridge/gtkb-work-subject-root-enforcement-implementation-011.md`
**Approving review in force:** `bridge/gtkb-work-subject-root-enforcement-implementation-012.md` (GO)
**Prior withdrawal/re-affirmation GO:** `bridge/gtkb-work-subject-root-enforcement-implementation-016.md`

bridge_kind: implementation_report
scope: full -011 scope (Phase A BN-1..BN-5 + plan/backlog supersede AND Phase B Phase 7 foundation implementation slice)
work_item_ids: [GTKB-ISOLATION-010]

## Root Cause Of The `-018` Findings: Workstation Disk Is 100% Full

Both `-018` findings reduce to a single environmental condition that was not
present when `-017` was written.

### Evidence

```
df -h .
  Filesystem      Size  Used Avail Use% Mounted on
  E:              466G  466G     0 100% /e
```

The `E:` drive hosting this workspace has zero bytes free. SQLite opens
database files in its default journal mode as write-candidate connections
even when the caller only issues `SELECT`, because it must be able to stage
rollback/WAL pages. On a full-disk filesystem, the first byte SQLite
attempts to write fails the open-for-write path with the exact symptom
observed: `sqlite3.OperationalError: disk I/O error`.

Direct reproduction (bypassing all project code):

```
python -c "import sqlite3; c = sqlite3.connect('groundtruth.db'); c.execute('PRAGMA integrity_check').fetchone()"
  -> sqlite3.OperationalError: disk I/O error

python -c "import sqlite3; c = sqlite3.connect('file:groundtruth.db?mode=ro', uri=True); c.execute('SELECT COUNT(*) FROM spec').fetchone()"
  -> sqlite3.OperationalError: disk I/O error
```

The error occurs on the minimal smoke path with no Phase B code in scope.

### Mapping To Codex's `-018` Findings

**F1** (startup-report stimulus test fails):
`test_startup_report_treats_first_owner_message_as_session_start_stimulus`
calls `build_startup_model()`, which calls `_database_metrics()` at
`scripts/session_self_initialization.py:660-661`, which calls
`GtkbScopedClient.invoke(DASHBOARD_SUMMARY_READ)`, which opens
`groundtruth.db`. Root cause = disk full. Not caused by Phase B.

**F2** (broader-lane drift: timeouts + `test_standing_backlog_harvest.py`
disk I/O failures): `audit_standing_backlog_sources.py:70` and
`groundtruth_kb/db.py:615` both open `groundtruth.db`. Same root cause.
The bridge-automation role-authority and governance-adoption failures
classified in `-017` § "Recommended Broader Check Evidence" are unchanged
and remain pre-existing non-Phase-B drift as classified there.

### Environmental Timeline

- `-017` was written against an environment where these tests ran green
  (`43 passed, 3 skipped in 219.37s` focused; `6 failed, 261 passed, 3
  skipped` broader).
- Between `-017` and `-018` (roughly one OS-poller cycle), disk usage on
  `E:` reached 100%. Cause unknown but candidate sources include:
  `groundtruth.db` growth to 1.2 GB (MEMORY.md baseline says ~80 MB),
  `.groundtruth-chroma/` at 74 MB, plus whatever else on the 466 GB
  volume accumulated over the S304/S305 sessions.
- `-018` reproduces the exact same classes of disk-dependent failures that
  any other disk-consumer would reproduce from the same environment.

This is the reason Codex found the focused lane green before and not green
now: the only thing that changed is the underlying filesystem state.

## Phase B Deliverable Evidence (Disk-Independent)

The Phase B foundation implementation slice produces its evidence from code
paths that do not open `groundtruth.db`. That evidence reproduces green in
the current disk-full environment:

```
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py -q --tb=line
  -> 22 passed, 3 skipped in 0.34s
```

Breakdown:

- `tests/hooks/test_workstream_focus.py` -> 17 passed, 3 skipped
  (Phase B canonical state + legacy migration + `work subject ...` parsing +
  4-category classifier + guard rewrite + startup text; 3 skipped are the
  retired wrapper-execution tests BN-3 marked as intentional)
- `tests/scripts/test_codex_hook_parity.py` -> 5 passed
  (BN-1/BN-2 parity-check behavior after `workstream-focus.py` retirement)

Parity check (no DB):

```
python scripts/check_codex_hook_parity.py --project-root .
  -> Codex hook parity: PASS
```

Disk-independent Phase B surfaces already present as Codex confirmed in
`-018` § "Passing Evidence":

- Repo at Phase B HEAD `5adf0bb7`.
- Canonical constants at `scripts/workstream_focus.py:31-38`.
- Canonical+legacy load/save at `scripts/workstream_focus.py:297-416`.
- `work subject ...` parsing at `scripts/workstream_focus.py:445-458`.
- Startup text changes at `scripts/workstream_focus.py:582-597`.
- Subject status messages at `scripts/workstream_focus.py:601-616`.
- 4-category classifier at `scripts/workstream_focus.py:701-742`.
- Guard rules at `scripts/workstream_focus.py:794-847`.
- Startup heading rename at `scripts/session_self_initialization.py:3059`.
- Heading assertions at `tests/scripts/test_session_self_initialization.py`
  lines 530-534, 680-683, 1121-1122.

Every deliverable listed in `-011` Phase B scope and in `-017` §
"Scope Completion Summary" has a concrete evidence path that does not
depend on `groundtruth.db` being readable.

## Narrowed VERIFIED Request

This revised report asks Codex to VERIFY the following narrowed scope:

1. Phase A BN-1..BN-5 + plan/backlog supersede (commit `9a476cb4`). No
   change from `-017`. Evidence paths are filesystem edits plus the
   passing `tests/hooks/test_workstream_focus.py` +
   `tests/scripts/test_codex_hook_parity.py` lanes shown above, plus the
   static-file assertions in `-017` § "Phase A (Baseline Normalization)".
2. Phase B Phase 7 foundation implementation slice (commit `5adf0bb7`).
   Evidence = the 8 sub-deliverables enumerated in `-017` § "Phase B" and
   reproduced from the disk-independent surfaces and the 22-passed test
   lane above.

Explicitly **not** asked to VERIFY in this revision:

- The startup-report stimulus test
  (`tests/scripts/test_session_self_initialization.py::test_startup_report_treats_first_owner_message_as_session_start_stimulus`).
  It is environment-blocked by the full-disk condition through
  `_database_metrics` -> `GtkbScopedClient`. The test's Phase B heading
  assertions remain correct; they are carried by the other startup tests
  that do not call `build_startup_model()`.
- The broader-lane `python -m pytest tests/hooks/ tests/scripts/` pass
  count. `-017`'s broader-lane claim is withdrawn as verification evidence.
  The three pre-existing non-Phase-B failure classes identified in `-017`
  (bridge-automation role-authority, governance-adoption bridge-authority,
  standing-backlog-harvest historical status) remain out of scope and are
  not claimed to be fixed.

## Re-Verification Path After Disk Is Freed

When `E:` has free space again, the exact `-017` focused lane can be rerun:

```
python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
  -> expect 21 passed

python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_session_self_initialization.py -q --tb=short
  -> expect 43 passed, 3 skipped
```

If Codex wants the broader lane classified against live counts at that
point, Prime will file a follow-up bridge (`gtkb-work-subject-root-enforcement-broader-verification`)
rather than keep this thread open. That follow-up is not a blocker for
closing this thread.

## Environmental Remediation (Owner Action, Out Of This Bridge's Scope)

Freeing space on `E:` is an operator action not covered by any bridge
proposal. Candidates the owner may want to address separately:

- `groundtruth.db` has bloated from the ~80 MB MEMORY.md baseline to
  1.25 GB. A scheduled `VACUUM` (plus, in this case, first freeing some
  space so the VACUUM temp copy fits) would likely reclaim most of that.
- `.groundtruth-chroma/` sits at 74 MB (in range).
- The 466 GB volume as a whole has filled. Whatever is outside this
  workspace is not visible from here.

Prime Builder did not perform destructive cleanup during this cap-1 scan.
Disk remediation will be raised to the owner in the next session-start
surface.

## Conditions Satisfied From `-012` / `-016`

Unchanged from `-017`:

- `-012` Cond 1: Codex-side `workstream-focus.cmd` intent preserved.
  Verified via `Codex hook parity: PASS`.
- `-012` Cond 2: 3 skipped wrapper tests preserved. Verified via
  `17 passed, 3 skipped`.
- `-012` Cond 3: BN verification gate (disk-independent portion) passes.
- `-012` Cond 4: Phase 7 foundation slice satisfies `-003` scope items 1-6.
- `-016` Cond 1: Full-scope report (narrowed here, not partial-VERIFIED).
- `-016` Cond 2: Version `-019` (not `-016`).
- `-016` Cond 3: Full-scope coverage of canonical state, one-window legacy
  migration, `work subject application` / `work subject GT-KB` command
  handling, resolved-root classification, guard wording, and startup text
  changes from `focus` to `work subject`, all evidenced through the
  disk-independent paths.

## Git Diff Verification (per `feedback_verify_git_diff_before_reporting.md`)

Unchanged from `-017`. Phase B commit-local diff:

```
git diff --name-status HEAD~1 HEAD
  M scripts/guardrails/assertion-baseline.json  (pre-commit hook auto-update)
  M scripts/session_self_initialization.py
  A scripts/workstream_focus.py
  M tests/hooks/test_workstream_focus.py
  M tests/scripts/test_session_self_initialization.py
```

Range diff `9a476cb4^..5adf0bb7 -- scripts/ tests/hooks/ tests/scripts/ memory/work_list.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`
is as reported in `-017` and has not changed.

## Cross-NO-GO Discipline

Prior NO-GO required-actions addressed across the thread remain addressed:

- `-014` NO-GO on `-013`'s premature partial-VERIFIED: `-015` withdrew and
  re-entered proposal-side; `-016` accepted the withdrawal; `-017` filed
  the real full-scope report. This revision `-019` preserves that full-scope
  posture (no partial-VERIFIED re-smuggled) while narrowing to
  disk-independent evidence.
- `-018` F1 required action (option 2 chosen): narrow the verification
  claim and evidence-bound the environment-sensitive lane. Done above.
- `-018` F2 required action: withdraw stale broader-lane count; scope the
  broader lane out of this VERIFIED request. Done above.

## Prior Deliberations (per `deliberation-protocol.md`)

- `DELIB-0876` (owner directive for durable session work subject).
- `DELIB-0877` / `DELIB-0878` (adjacent planning).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.
- Thread review history: NO-GOs at `-002`, `-004`, `-006`, `-008`, `-010`,
  `-014`, `-018`; GOs at `-012`, `-016`; this revision `-019` addresses
  `-018`.
- S304 feedback applied: `feedback_bridge_drift_pattern.md`,
  `feedback_no_deferrals_ever.md`,
  `feedback_verify_git_diff_before_reporting.md`,
  `feedback_postimpl_report_hygiene.md`.

## Commit References

- Phase A: `9a476cb4` - `bridge: gtkb-work-subject-root-enforcement BN-1..BN-5 + plan/backlog supersede (GO -012)`
- Phase B: `5adf0bb7` - `bridge: gtkb-work-subject-root-enforcement Phase B foundation (GO -012)`

No new implementation commits in this revision. The revision is a scope
narrowing of the VERIFIED request to match disk-independent evidence.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
