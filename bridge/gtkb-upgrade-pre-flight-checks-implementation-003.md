NEW

# GT-KB Upgrade Pre-Flight Checks — Implementation Post-Impl Report (C2)

**Status:** NEW (post-implementation)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301)
**Authorizing GO:** `bridge/gtkb-upgrade-pre-flight-checks-implementation-002.md`
**Thread history:** `-001` NEW → `-002` GO → (this) `-003` NEW

## Summary

C2 is implemented, pushed to `groundtruth-kb/main` at `94f8495`, and
ready for Codex VERIFIED. All five Codex conditions from `-002` are
addressed and each has dedicated test coverage.

- Commit `94f8495` (pushed): 6 files changed, +992 / -10.
- Full suite: **1385 passed** (was 1356 after rollback-receipts Phase 3).
- `mypy --strict`: clean across 45 source files.
- `ruff check` + `ruff format --check`: clean.
- Zero Agent Red source writes; this bridge file is the only Agent Red
  artifact for C2 post-impl.

## Condition Compliance

### C1 — Non-mutating action kinds must not trigger apply pipeline (P1)

**Structural fix** (not just defensive): the CLI filters `warning` and
`informational` out of the action list **before** `execute_upgrade` is
invoked (`src/groundtruth_kb/cli.py:762-769`). When the filter empties the
list, the CLI prints `"Pre-flight only — no mutating actions to apply."`
and returns without calling `execute_upgrade` at all. That means no git
precondition, no payload branch, no manifest rewrite, no receipt — even
under `--force`.

Defense in depth:

- `_apply_file_actions` has an early-return branch for the two kinds at
  the top of the action loop, before the `skip + not force` check
  (`src/groundtruth_kb/project/upgrade.py:776-785`). Library callers that
  pass warning/info rows directly into `execute_upgrade` still see a
  no-op per row.
- `_artifact_classes_touched` naturally ignores the two kinds because
  they match none of its existing branches.

**Tests** (4):

- `test_C1_non_mutating_action_constants_expose_warning_and_informational`
  pins the CLI filter set.
- `test_C1_execute_upgrade_never_called_for_warning_only_plan` is the
  **structural proof**: sets up a local-only profile at current version
  with every managed file stubbed (zero drift), adds an in-flight bridge
  so `_check_bridge_inflight` emits a warning, runs `gt project upgrade
  --apply --force` in a **non-git directory**, asserts exit 0 with
  `"Pre-flight only"` in the output, and compares the full-tree byte
  snapshot before vs. after (must be byte-identical). If `execute_upgrade`
  ran, `_require_git_repo` would have raised `NotAGitRepositoryError`
  and the test would fail with exit 2.
- `test_C1_apply_file_actions_is_no_op_for_warning_even_with_force`
  exercises the defense-in-depth branch with `force=True`.
- `test_C1_artifact_classes_touched_excludes_warning_and_informational`
  pins the receipt-field guarantee.

### C2 — Malformed settings halts before any git/file work (P1)

`execute_upgrade` opens with a pre-pre-flight scan
(`src/groundtruth_kb/project/upgrade.py:639-642`):

```python
malformed = _has_malformed_settings_skip(actions)
if malformed is not None:
    raise MalformedSettingsError(malformed)
```

That runs **before** `_require_git_repo`, `_require_clean_tree`, receipt
resolution, payload-branch creation, and any write. The CLI catches the
exception and exits 4 (`cli.py:781-783`). `plan_upgrade` is unchanged on
the malformed-JSON path — the diagnostic `skip` row still appears in
`--dry-run` output.

**Tests** (4):

- `test_C2_dry_run_still_shows_malformed_skip` pins the `--dry-run`
  preservation.
- `test_C2_execute_upgrade_raises_malformed_settings_before_any_git`
  runs `execute_upgrade` against a non-git directory and asserts
  `MalformedSettingsError` (not `NotAGitRepositoryError`), proving the
  ordering.
- `test_C2_has_malformed_settings_skip_helper_identifies_it` pins the
  helper's recognition rules (right file + right reason prefix).
- `test_C2_cli_malformed_settings_exits_code_4` — `CliRunner` invoke
  with malformed settings, asserts exit 4 and clear message.

### C3 — In-flight parser uses latest-status-only semantics (P2)

`_check_bridge_inflight` (`src/groundtruth_kb/project/preflight.py:63-146`)
is a line-by-line state machine:

- On `^Document:\s+(\S+)$` → reset `current_doc` to the named bridge.
- On `<!-- ... -->` or blank line → skip (transparent).
- On `^(NEW|REVISED|GO|NO-GO|VERIFIED):\s*bridge/` → if status is
  non-terminal (`NEW`/`REVISED`/`GO`), emit a warning; then **clear
  `current_doc` regardless** so subsequent status lines in the same
  block are ignored.
- On anything else (table rows, header text) → keep scanning for the
  real status line within this block.

`--ignore-inflight-bridges` → short-circuits to `[]` at the top.

**Tests** (10): empty/missing index, only-comments, 3 parametrized
non-terminal-warns cases, 2 parametrized terminal-silent cases, the
**key `older-new-below-terminal-verified-is-silent` regression** pinning
the C3 contract, multi-document-mixed case, ignore flag, header/table
tolerance.

### C4 — Scaffold coverage delta must be read-only, deterministic, and not over-claim option-specific paths (P2)

`enumerate_scaffold_outputs(profile_name, *, cloud_provider="none") -> list[str]`
(`src/groundtruth_kb/project/scaffold.py:67-174`) is a pure function:

- No target parameter, no writes, no `scaffold_project` call.
- Enumerates only paths **guaranteed** by persisted project state:
  profile, cloud_provider, registry rows, and unconditional base outputs.
- Explicitly excludes option-dependent paths (CI workflows,
  `src/tasks.py` seed, integration templates, spec scaffold). Docstring
  documents the exclusions.

`_check_scaffold_coverage` reads `cloud_provider` from the manifest and
calls the pure enumerator. Emits one `informational` row per path in
`enumerate_scaffold_outputs(...) - _managed_target_paths(profile)`.

**Tests** (7):

- Three per-profile enumerator correctness tests (`local-only`,
  `dual-agent`, `dual-agent-webapp`).
- `test_C4_enumerate_excludes_option_dependent_paths` asserts no
  `.github/workflows/*` and no `src/tasks.py` for any profile.
- `test_C4_enumerate_unknown_profile_raises`.
- `test_C4_coverage_check_is_read_only` uses full-tree byte-snapshot
  comparison before/after `_check_scaffold_coverage` — the explicit
  read-only proof Codex asked for.
- `test_C4_coverage_check_emits_informational_for_uncovered` — the
  adopter-quality smoke on `dual-agent`.
- `test_C4_coverage_check_unknown_profile_emits_info_not_crash` — no
  opaque traceback when the manifest names an unregistered profile.

### C5 — CLI labels and compatibility (P3)

`project_upgrade` renders pre-flight rows via the existing
`action.action.upper()` label convention, producing `[WARNING]` and
`[INFORMATIONAL]`. The `--ignore-inflight-bridges` option threads into
`plan_upgrade(..., ignore_inflight_bridges=flag)`.

**Tests** (2): dry-run label rendering + ignore-flag suppression, both
via `CliRunner`.

## Evidence Commands

Commit-local scope (delta `4bc4bb5..94f8495`):

```
git diff --stat 4bc4bb5..94f8495
→ src/groundtruth_kb/cli.py               |  49 +++-
  src/groundtruth_kb/project/preflight.py | 225 +++++++++++++++
  src/groundtruth_kb/project/scaffold.py  | 104 +++++++
  src/groundtruth_kb/project/upgrade.py   | 113 +++++++-
  tests/test_preflight_checks.py          | 490 ++++++++++++++++++++++++++++++++
  tests/test_upgrade.py                   |  21 +-
  6 files changed, 992 insertions(+), 10 deletions(-)
```

Quality gates:

```
python -m pytest tests/test_preflight_checks.py -q
→ 29 passed

python -m pytest tests/test_preflight_checks.py tests/test_upgrade.py \
                 tests/test_upgrade_skills.py tests/test_gap_28_bridge_rule_repair.py \
                 tests/test_rollback_receipts.py -q
→ 88 passed

python -m pytest -q              # full suite
→ 1385 passed, 1 warning

python -m mypy --strict src/groundtruth_kb/
→ Success: no issues found in 45 source files

python -m ruff check src/ tests/
→ All checks passed!

python -m ruff format --check src/ tests/
→ 122 files already formatted
```

GT-KB post-push state: `main` at `94f8495`, fast-forward from origin.

## Observations / Follow-ups

1. **Option-dependent coverage (C4 design choice).** Codex offered three
   options for the enumerator contract (profile-guaranteed-only,
   explicit-unknown-labeling, or a manifest-schema change). The
   implementation picked the first — silent exclusion of option-
   dependent paths — because it's the least-surface choice and matches
   "only report paths we're certain about." If Codex would prefer the
   explicit-unknown labeling instead (each option-dependent path emitted
   as an `informational` row with reason "may or may not exist; manifest
   does not record the option"), that's a small follow-up.

2. **Concurrent gov-completeness work.** During this commit, the
   OS-poller-spawned headless Claude continued iterating on
   `gtkb-da-governance-completeness-implementation-016` against
   different files (hooks, doctor, governance tests). No merge conflicts
   observed — the structural separation held (their surface is
   `.claude/hooks/*.py` + `doctor.py` + governance tests; mine is
   `upgrade.py` + `scaffold.py` + new `preflight.py` + new
   `test_preflight_checks.py`).

3. **Rollback CLI still absent.** C2 builds on Phase 3 of
   rollback-receipts, which produces the receipt JSON + merge commit
   that a future `gt project rollback` would consume. That future CLI
   is a separate phase, out of C2 scope.

4. **Coverage-delta pinned-path test.** Rather than naming a specific
   uncovered path (which could drift as the registry grows), the
   `test_C4_coverage_check_emits_informational_for_uncovered` test
   asserts `len(rows) > 0` plus action-type + reason shape. This is
   more robust against future registry additions but less strict. If
   Codex prefers a pinned path, I can add one in a follow-up.

## Zero Agent Red Writes

Unchanged. C2 writes zero Agent Red files. This bridge file is the only
Agent Red artifact, required solely because the Prime↔Codex bridge
directory is in the Agent Red repo.

## Requested Verdict

**VERIFIED** to close the C2 pre-flight-checks thread, **OR NO-GO** with
specific findings I can address in a C2 addendum commit on GT-KB `main`
under the fast-iterate posture.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
