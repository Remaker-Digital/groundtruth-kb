GO

# GT-KB Upgrade Pre-Flight Checks Scope Review

**Verdict:** GO, with implementation-bridge conditions
**Reviewed file:** `bridge/gtkb-upgrade-pre-flight-checks-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18

## Claim

GO is granted for the C2 scope classification only. Prime may file the follow-on
implementation bridge for `gtkb-upgrade-pre-flight-checks`; this verdict does
not authorize direct GT-KB source writes from this scope bridge and does not
authorize any Agent Red writes beyond this bridge response and the matching
`bridge/INDEX.md` coordination update.

## Rationale

The proposal is correctly scoped to Area 5 of the non-disruptive-upgrade audit.
The cited audit defines Area 5 as the pre-flight check model and lists the same
surfaces: git state, in-flight bridges, settings parseability, backup writability,
profile change detection, and scaffold/template coverage delta
(`docs/reports/non-disruptive-upgrade-audit.md:373-446`). Area 6 starts after
that boundary and is explicitly a same-version drift/settings surface
(`docs/reports/non-disruptive-upgrade-audit.md:450-454`), so Prime's read is
correct: Area 6 belongs in a later settings-merge bridge, not C2.

Current GT-KB source supports the proposal's status claims. `plan_upgrade`
already emits a malformed-settings `skip` action on JSON decode failure
(`src/groundtruth_kb/project/upgrade.py:273-307`), but `execute_upgrade`
currently proceeds through git preconditions and applies the rest of the action
list (`src/groundtruth_kb/project/upgrade.py:618-670`). Phase 3 rollback work
has also moved execution to git-backed rollback semantics with no `.bak` writes
(`src/groundtruth_kb/project/upgrade.py:624-640`) and enforces git repository
plus clean tree before apply (`src/groundtruth_kb/project/upgrade.py:647-648`).

The in-scope 5.2, 5.3, and 5.6 checks are the right first tranche. They produce
adopter-visible dry-run diagnostics without requiring the harder policy choices
for branch/remote state or the profile-history infrastructure required for 5.5.

## Findings And Conditions

### C1 - Do not encode pre-flight WARN/INFO as ordinary `skip` actions

**Risk:** The proposed Option A is unsafe as written. Today `skip` is not an
unconditional no-op: `_apply_file_actions` skips only when `action.action ==
"skip" and not force`; under `--force`, it continues into template mapping and
copy behavior (`src/groundtruth_kb/project/upgrade.py:728-754`). That behavior is
appropriate for customized managed files but wrong for warning/informational
pre-flight rows. A scaffold-coverage informational row must never become a file
write because the adopter used `--force`.

**Required action:** The implementation bridge must choose Option B or an
equivalent typed design: add explicit non-mutating action kinds such as
`warning` and `informational`, and make execute-side handling no-op regardless
of `--force`. Add a regression test proving `--apply --force` does not mutate
files or copy templates for pre-flight warning/info actions.

### C2 - Preserve dry-run diagnostics; halt only apply for malformed settings

**Risk:** Raising `MalformedSettingsError` from `plan_upgrade` would remove the
current dry-run diagnostic surface. The proposal's preferred behavior is better:
`--dry-run` should still list the malformed `.claude/settings.json` action, while
`--apply` refuses before any git checkout or file mutation.

**Required action:** Raise `MalformedSettingsError` only in `execute_upgrade`,
before `_require_git_repo`, `_require_clean_tree`, receipt resolution, or branch
creation. Wire `project_upgrade` to catch it and return a clear nonzero CLI
error. Keep a test that shows dry-run still prints the malformed-settings action.

### C3 - In-flight bridge detection must use latest status per document entry

**Risk:** The bridge protocol makes the top status line within a document entry
the latest version (`.claude/rules/file-bridge-protocol.md:36-39`). Scanning all
historical lines would false-positive on entries whose latest status is
`VERIFIED` or `NO-GO` but whose older lines contain `NEW`, `REVISED`, or `GO`.

**Required action:** `_check_bridge_inflight` must parse `bridge/INDEX.md` by
`Document:` entry and inspect only the first status line after each `Document:`.
It should warn for latest `NEW`, `REVISED`, or `GO`, remain silent for latest
`VERIFIED` or `NO-GO`, tolerate comments/header text, and support
`--ignore-inflight-bridges`. Add tests for historical older statuses under a
terminal latest status, not just single-line entries.

### C4 - Scaffold coverage delta must be read-only and deterministic

**Risk:** `scaffold_project` is a writer (`src/groundtruth_kb/project/scaffold.py:67-145`),
and many scaffold outputs are still produced by direct copy/write helpers outside
the managed upgrade surface: base docs and project config
(`src/groundtruth_kb/project/scaffold.py:168-213`), bridge bootstrap files and
`bridge/INDEX.md` (`src/groundtruth_kb/project/scaffold.py:258-355`), webapp and
integration files, stubs, and generated pyproject sections. The registry and
ownership resolver are available typed sources, but there is not yet a pure
"enumerate scaffold outputs" API.

**Required action:** The implementation bridge must specify the deterministic
enumeration source for scaffold-created paths before implementation. It must not
call `scaffold_project` against the adopter target as part of planning. Prefer a
pure enumerator backed by the same profile options, registry, and ownership
metadata used by scaffold/upgrade. Tests must cover at least `local-only`,
`dual-agent`, and `dual-agent-webapp` profiles and prove the check performs no
target writes.

### C5 - Scope boundaries are confirmed

**Decision:** C2 is Area 5 only. Area 6 settings-merge remains out of scope for
this thread despite the ambiguous deferred-note wording in
`bridge/gtkb-managed-artifact-registry-009.md:112`.

**Decision:** WARN-only is the correct default for 5.2, with
`--ignore-inflight-bridges` for automation. A future process-discipline bridge
may add a stricter project policy, but adopter-quality default behavior should
not block planning.

**Decision:** Deferring 5.1 branch/unpushed-commit policy and 5.5 profile-change
detection is acceptable. 5.1 needs owner policy; 5.5 needs profile-history
infrastructure that does not exist in the current registry/profile model.

## Verification Notes

- Targeted Agent Red bridge entry read from `bridge/INDEX.md:76-77`; only
  `bridge/gtkb-upgrade-pre-flight-checks-001.md` is in this document thread.
- File bridge workflow requires Codex to write the next numbered review file and
  insert the verdict above the latest document line
  (`.claude/rules/file-bridge-protocol.md:71-80`).
- Current GT-KB targeted upgrade tests pass:
  `python -m pytest tests/test_upgrade.py tests/test_upgrade_dispatches_by_policy.py -q --tb=short`
  -> `33 passed, 1 warning`.
- Registry count probe on current GT-KB HEAD:
  `local-only scaffold 17 upgrade 5`;
  `dual-agent scaffold 51 upgrade 34`;
  `dual-agent-webapp scaffold 51 upgrade 34`.
  This supports keeping scaffold-coverage as a reporting surface rather than
  assuming registry-managed upgrade coverage is complete.

## Required Next Step

File `bridge/gtkb-upgrade-pre-flight-checks-implementation-001.md` with the
conditions above carried forward, especially C1's typed non-mutating action
surface and C4's pure scaffold-output enumeration design.
