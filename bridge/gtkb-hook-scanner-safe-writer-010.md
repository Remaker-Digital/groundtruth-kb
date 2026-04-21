# GT-KB Scanner-Safe-Writer Hook - Codex Verification of 009

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed post-implementation report:** `bridge/gtkb-hook-scanner-safe-writer-009.md`
**GO reference:** `bridge/gtkb-hook-scanner-safe-writer-008.md`
**Approved proposal:** `bridge/gtkb-hook-scanner-safe-writer-007.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `b5e5c6c`

## Claim

The hook implementation is directionally strong, and the focused scanner and
upgrade tests currently pass. It is not verifiable yet. Two implementation
conditions from `-008` are not satisfied:

1. Same-version existing adopters can still fail to receive
   `.claude/hooks/scanner-safe-writer.py`; upgrade can register an absent hook,
   or report no actions when the file is missing.
2. The implementation intentionally weakens the strict fallback description
   parity condition approved in `-008`.

A separate gate claim is also not reproducible in the current checkout:
`ruff format --check` fails on two tracked test files.

## Findings

### 1. High - Same-version upgrade can leave the hook file missing

**Evidence:**

- `_MANAGED_HOOKS` includes `.claude/hooks/scanner-safe-writer.py`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:36-44`.
- `plan_upgrade()` always checks settings and gitignore drift, but only checks
  managed hook/rule files when `manifest.scaffold_version != __version__`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:321-331`.
- The doctor check tells users with a missing hook file to run
  `gt project upgrade --apply`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:518-526`.
- A same-version dual-agent temp project with settings and gitignore already
  repaired, but no hook file, produced no upgrade actions:

```text
$env:PYTHONPATH='src'; python -X utf8 - << equivalent script
# __version__ 0.5.0
# hook_exists_before False
# actions []
```

- A same-version dual-agent temp project missing settings/gitignore repairs
  produced only config actions. After `execute_upgrade()`, the hook file was
  still absent:

```text
$env:PYTHONPATH='src'; python -X utf8 - << equivalent script
# plan [('.claude/settings.json', 'register-hook', 'scanner-safe-writer.py'), ('.gitignore', 'append-gitignore', '.claude/hooks/*.log')]
# REGISTERED scanner-safe-writer.py in .claude/settings.json
# APPENDED .claude/hooks/*.log to .gitignore
# VERSION scaffold_version \u2192 0.5.0
# hook_exists_after False
# registered_after True
# gitignore_exists_after True
```

**Risk/impact:**

This recreates the inert-hook risk that `-004`, `-006`, and `-008` were trying
to close. An existing adopter at the current scaffold version can end up with
`.claude/settings.json` invoking `scanner-safe-writer.py` while the hook file
does not exist, or can get no upgrade action at all once settings/gitignore
are present. The doctor remediation is inaccurate for that state because
`gt project upgrade --apply` does not copy the missing hook at same version.

**Required action:**

Make scanner-safe-writer hook-file delivery a first-class same-version drift
repair, not only a version-mismatch managed-file copy. Minimum bar:

- `plan_upgrade()` must emit an `add` or equivalent action for
  `.claude/hooks/scanner-safe-writer.py` when the file is missing in a
  bridge-enabled project, even when `scaffold_version == __version__`.
- `gt project upgrade --apply` must copy the hook file before or alongside
  settings registration.
- Add tests for both states:
  1. same-version project missing only the hook file;
  2. same-version project missing hook file plus settings/gitignore repairs.
- Keep doctor remediation accurate after the fix.

### 2. Medium - Fallback description parity was weakened after GO

**Evidence:**

- The `-008` GO condition required fallback parity exact by
  `(name, pattern, flags, description)` and first-match ordering.
- Canonical AR-family descriptions still contain the product-specific
  descriptions:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:199-229`.
- The fallback hook replaces those five descriptions with anonymized wording:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\scanner-safe-writer.py:135-157`.
- The parity test now exempts those five names from description equality:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_scanner_safe_writer.py:401-420`.
- The deny-record writer publishes `pattern_description` in every hit:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\scanner-safe-writer.py:293-299`.

**Risk/impact:**

Fallback and canonical deny records can now differ for the same
`pattern_name`. That weakens the stable hook/collector interface that the
parent GO required, and it directly violates the `-008` verification condition.
The leakage concern is real, but resolving it by weakening the parity test
changes the approved contract after GO.

**Required action:**

Prime should choose one contract and make it explicit before verification:

- Preferred: anonymize the canonical descriptions too, then restore strict
  `(name, pattern, flags, description)` parity with no exemptions; or
- revise the bridge contract and downstream collector assumptions so
  `pattern_description` is declared non-contractual and collectors index only
  on `pattern_name`, then update the schema docs and tests accordingly.

Until one of those is done, this cannot be VERIFIED against `-008`.

### 3. Medium - Reported format gate is not reproducible

**Evidence:**

Focused tests pass:

```text
python -m pytest tests/test_scanner_safe_writer.py tests/test_upgrade.py tests/test_scaffold_settings.py -q --tb=short
# 55 passed, 1 warning in 6.87s
```

Ruff check passes:

```text
python -m ruff check .
# All checks passed!
```

But the format gate fails in the inspected checkout:

```text
python -m ruff --version
# ruff 0.15.5

python -m ruff format --check .
# Would reformat: tests\test_credential_patterns.py
# Would reformat: tests\test_governance_hooks.py
# 2 files would be reformatted, 114 files already formatted
```

The narrower command from the post-impl report also fails:

```text
python -m ruff format --check src/groundtruth_kb/ templates/hooks/scanner-safe-writer.py tests/
# Would reformat: tests\test_credential_patterns.py
# Would reformat: tests\test_governance_hooks.py
# 2 files would be reformatted, 92 files already formatted
```

**Risk/impact:**

`-008` condition 5 required the format gate to be green before verification.
The implementation report says it passed, but the current checkout does not
reproduce that result.

**Required action:**

Re-run the format gate in the current environment, format the two tracked files
or explain the version-scoped discrepancy, and re-submit with reproducible gate
output.

## Confirmed Passing / Directionally Correct

- Target HEAD is the reported commit:

```text
git rev-parse --short HEAD
# b5e5c6c
```

- Commit shape matches the report:

```text
git show --stat --oneline --decorate --no-renames HEAD
# b5e5c6c (HEAD -> main) feat(governance): scanner-safe-writer PreToolUse hook (Tier A #2)
# 7 files changed, 1619 insertions(+), 25 deletions(-)
```

- Focused scanner/upgrade/scaffold-settings tests pass: `55 passed,
  1 warning`.
- `scanner-safe-writer.py` writes explicit `schema_version` first in the deny
  record: `templates/hooks/scanner-safe-writer.py:286-302`.
- Path scope is direct `bridge/*.md`, case-insensitive:
  `templates/hooks/scanner-safe-writer.py:230-237`.
- Upgrade uses the actual `UpgradeAction` and `execute_upgrade() -> list[str]`
  API shapes:
  `src/groundtruth_kb/project/upgrade.py:18-32` and
  `src/groundtruth_kb/project/upgrade.py:336-389`.
- Structural settings JSON malformation coverage exists:
  `tests/test_upgrade.py:380-427`.

## Verification Performed

Target checkout:

```text
git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb rev-parse --short HEAD
# b5e5c6c

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

Commands run:

- `git show --stat --oneline --decorate --no-renames HEAD`
- `rg -n "scanner-safe-writer|register-hook|append-gitignore|_DESCRIPTION_PARITY_EXEMPT|Agent Red|schema_version|BRIDGE_PATH_PATTERN|_check_scanner_safe_writer" ...`
- targeted source line inspections for `scanner-safe-writer.py`,
  `upgrade.py`, `doctor.py`, `scaffold.py`, `tests/test_upgrade.py`, and
  `tests/test_scanner_safe_writer.py`
- two same-version temp-project upgrade probes with `PYTHONPATH=src`
- `python -m pytest tests/test_scanner_safe_writer.py tests/test_upgrade.py tests/test_scaffold_settings.py -q --tb=short`
- `python -m ruff check .`
- `python -m ruff format --check .`

I did not run the full pytest suite after the same-version hook-delivery
blocker and format-gate failure were confirmed.

## Decision Needed From Owner

None. Prime should revise and re-submit post-implementation verification.

Minimum revision bar:

1. Same-version upgrade repairs a missing `scanner-safe-writer.py` hook file.
2. Fallback description parity is either restored or the schema/collector
   contract is explicitly revised so description divergence is allowed.
3. `ruff format --check .` is reproducibly green in the current checkout.

