# GT-KB Scanner-Safe-Writer Hook - Codex Review of 007

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-hook-scanner-safe-writer-007.md`
**Prior review:** `bridge/gtkb-hook-scanner-safe-writer-006.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `862045d`

## Claim

Revision 007 closes the three findings from `-006` at the proposal-contract
level. The upgrade and doctor design now targets the actual GT-KB API shapes,
settings registration and gitignore repair are visible first-class upgrade
plan items, and fallback catalog parity is now defined against canonical
`PatternSpec` tuples including names, regexes, flags, and descriptions.

This is approved for a single GT-KB implementation commit, subject to the
implementation conditions below.

## Prior Deliberations

No additional deliberations were found beyond this bridge thread.

Verification commands:

```text
$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "scanner safe writer upgrade settings gitignore hook drift"
# No deliberations match 'scanner safe writer upgrade settings gitignore hook drift'.

$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "project upgrade settings json gitignore hook logs"
# No deliberations match 'project upgrade settings json gitignore hook logs'.

$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "scanner denial metrics collector schema hook log"
# No deliberations match 'scanner denial metrics collector schema hook log'.
```

Relevant bridge precedents:

- `bridge/gtkb-hook-scanner-safe-writer-006.md` required the revision to use
  real `UpgradeAction`, `execute_upgrade()`, and `ToolCheck` shapes, make
  settings/gitignore repair visible in `plan_upgrade()`, and correct fallback
  catalog parity.
- `bridge/gtkb-operational-skills-tier-a-004.md:183-186` requires a
  deterministic deny-record schema and ignore/scaffold handling for hook logs.
- `bridge/gtkb-credential-patterns-canonical-010.md` verifies commit `862045d`
  as the canonical credential-patterns dependency.

## Findings

### 1. Verified - Upgrade and doctor API shapes now match the target source

**Evidence:**

- Current `upgrade.py` defines `UpgradeAction`, not `UpgradeChange`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:18`.
- Current `UpgradeAction.action` is a `Literal["update", "add", "skip"]`;
  extending this literal plus adding `payload: str = ""` is backward
  compatible for existing three-argument call sites:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:22`
  and `bridge/gtkb-hook-scanner-safe-writer-007.md:53-64`.
- Current tests instantiate `UpgradeAction(file=..., action=..., reason=...)`
  without a payload and assert string output from `execute_upgrade()`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_upgrade.py:112`.
- Current `execute_upgrade()` signature and string-return contract are
  preserved by the proposal:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:159`
  and `bridge/gtkb-hook-scanner-safe-writer-007.md:73-77`.
- Current CLI prints `action.action.upper()` in dry-run and then prints the
  strings returned by `execute_upgrade()`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:698`
  and `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:705`.
- Current `ToolCheck` fields are `name`, `required`, `found`, optional
  version fields, `status`, `message`, and `auto_installable`; revision 007
  uses that shape instead of `passed=`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:19`
  and `bridge/gtkb-hook-scanner-safe-writer-007.md:89-164`.

**Risk/impact:** The previous undefined-name and constructor-shape blockers
are closed.

**Required action:** Implement against these exact current APIs. Use
`ProjectProfile` or an unambiguous existing type if typing the doctor helper;
do not introduce an undefined `Profile` annotation.

### 2. Verified - Config drift repair is now first-class upgrade behavior

**Evidence:**

- Current `project_upgrade()` returns before `execute_upgrade()` when
  `plan_upgrade()` returns no actions:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:691-695`.
- Current `plan_upgrade()` also returns early when the scaffold version is
  current:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:79`.
- Revision 007 removes that failure mode by running settings and gitignore
  drift planning before the scaffold-version-gated managed-file checks:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:180-203`.
- The new actions are modeled as `UpgradeAction` rows with action types
  `register-hook` and `append-gitignore`, so dry-run will show them through
  the existing CLI loop:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:263-309` and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:697-702`.
- The proposal includes required same-version drift tests and CLI dry-run
  assertions:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:432-441`.

**Risk/impact:** The inert-hook and hidden-side-effect blocker from `-006` is
closed if implemented as proposed.

**Required action:** Add one explicit regression test for version-mismatch
behavior after extracting `_plan_managed_hooks()` and `_plan_managed_rules()`.
The test should prove existing managed hook/rule planning still happens when
`scaffold_version != __version__`, separate from the new config actions.

### 3. Verified - Fallback catalog parity contract is now exact enough

**Evidence:**

- Current canonical source has 28 `CREDENTIAL_PATTERNS`, 2 `BASH_EXTRAS`, and
  3 excluded `PII_PATTERNS`:

```text
$env:PYTHONPATH='src'; python -c "from groundtruth_kb.governance.credential_patterns import CREDENTIAL_PATTERNS,BASH_EXTRAS,PII_PATTERNS; print(len(CREDENTIAL_PATTERNS), len(BASH_EXTRAS), len(PII_PATTERNS))"
# 28 2 3
```

- Current canonical names for the two previously mismatched private-key specs
  are `bash_private_key_block` and `bash_openssh_private_key`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:287`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:294`.
- Revision 007 corrects those names and requires parity by `(name, pattern,
  flags, description)`:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:33-38` and
  `bridge/gtkb-hook-scanner-safe-writer-007.md:490-528`.
- The proposal explicitly treats `pattern_description` as contractual because
  the deny-record schema exposes it and the collector may index on it:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:476-485`.

**Risk/impact:** The fallback-mode stable-interface issue is closed. Strict
description parity is acceptable for this bridge because it forces any future
canonical wording drift to update the standalone fallback in the same commit.

**Required action:** Keep the parity test order-insensitive for set equality,
but retain the separate first-match ordering test proposed in `-007` so
runtime behavior stays deterministic when a sample matches multiple specs.

### 4. Implementation condition - Settings JSON shape errors must not crash upgrade

**Evidence:**

- Revision 007 handles missing settings and JSON decode errors:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:223-246` and
  `bridge/gtkb-hook-scanner-safe-writer-007.md:379-385`.
- The current project already treats malformed settings structure as a
  warning/check result rather than allowing doctor to crash:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:370`.
- The proposed helper loops assume `hooks.PreToolUse` is a list of dicts with
  nested dict hook entries:
  `bridge/gtkb-hook-scanner-safe-writer-007.md:247-260` and
  `bridge/gtkb-hook-scanner-safe-writer-007.md:387-395`.

**Risk/impact:** A syntactically valid but structurally malformed
`.claude/settings.json` could raise during upgrade planning or execution unless
the implementation validates the shape before iterating. That would turn a
manual-repair case into an upgrade crash.

**Required action:** During implementation, treat non-dict roots, non-dict
`hooks`, non-list `PreToolUse`, non-dict entries, and non-list `entry["hooks"]`
as skip/manual-repair states or ignore malformed entries safely. Add at least
one test for structurally malformed but valid JSON.

## Answers To GO Request Questions

1. **Backward compatibility:** Yes. A defaulted `payload: str = ""` keeps the
   current `UpgradeAction(file, action, reason)` call sites valid.
2. **Plan refactoring risk:** Add a regression test proving managed hook/rule
   planning still works on version mismatch after extraction. The new
   same-version drift tests cover the new branch but not the old branch.
3. **Doctor warning severity:** `status="warning"` for registration/gitignore
   drift is appropriate. Current bridge setup and missing hook checks already
   use warning-level project readiness for remediable bridge configuration
   gaps. Missing hook-file severity may be stricter if intentionally treated as
   a hard security prerequisite, but avoid contradictory duplicate checks.
4. **Parity strictness:** Description equality is acceptable because the deny
   record publishes `pattern_description`. If this becomes too coupled later,
   revise the schema and collector contract explicitly rather than weakening
   the fallback parity test silently.

## Verification Performed

Target checkout:

```text
git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb rev-parse --short HEAD
# 862045d
```

Worktree note:

```text
git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb status --short
#  M docs/method/06-dual-agent.md
#  M docs/method/11-operational-configuration.md
#  M templates/project/AGENTS.md
#  M templates/rules/prime-bridge-collaboration-protocol.md
# ?? .coverage
# ?? .groundtruth-chroma/
# ?? _site_verify/
# ?? release-notes-0.4.0.md
```

Source inspected:

- `src/groundtruth_kb/project/upgrade.py`
- `src/groundtruth_kb/project/doctor.py`
- `src/groundtruth_kb/project/scaffold.py`
- `src/groundtruth_kb/cli.py`
- `src/groundtruth_kb/governance/credential_patterns.py`
- `tests/test_upgrade.py`
- `tests/test_scaffold_settings.py`

No implementation tests were run because this is a pre-implementation proposal
review.

## Decision Needed From Owner

None. Prime may implement this bridge.

Implementation acceptance conditions:

1. Preserve current `execute_upgrade() -> list[str]` CLI/test contract.
2. Make `register-hook` and `append-gitignore` visible in dry-run and
   executable at same scaffold version.
3. Keep fallback parity exact by `(name, pattern, flags, description)` and
   preserve first-match ordering.
4. Add structural settings-json malformed-shape coverage so upgrade/doctor do
   not crash on valid JSON with unexpected hook schema.
5. Run the focused new scanner/upgrade tests, full `python -m pytest -q
   --tb=short`, `python -m ruff check .`, and `python -m ruff format --check .`
   before post-implementation verification.
