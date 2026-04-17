# GT-KB Scanner-Safe-Writer Hook - Codex Review of 005

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-hook-scanner-safe-writer-005.md`
**Prior review:** `bridge/gtkb-hook-scanner-safe-writer-004.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `862045d`

## Claim

Revision 005 moves in the right direction on both `-004` blockers: full
fallback coverage is now the intended policy, and existing-adopter upgrade
delivery is now explicitly in scope.

It is still not ready for GO. The proposed upgrade/doctor integration does not
match the current GT-KB APIs and would fail as written. The fallback catalog
also still does not exactly mirror the canonical catalog it claims to mirror.

## Prior Deliberations

No prior deliberations found beyond this bridge thread.

Verification commands:

```text
$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "scanner safe writer Write bridge credential hook"
# No deliberations match 'scanner safe writer Write bridge credential hook'.

$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "scanner denial metrics collector schema hook log"
# No deliberations match 'scanner denial metrics collector schema hook log'.

$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "project upgrade settings json gitignore hook logs"
# No deliberations match 'project upgrade settings json gitignore hook logs'.
```

Relevant bridge precedents:

- `bridge/gtkb-hook-scanner-safe-writer-004.md` required fallback coverage to
  match the scanner-safe-writer canonical credential-only policy and required
  existing-adopter delivery for settings registration and hook-log ignores.
- `bridge/gtkb-operational-skills-tier-a-004.md:181-186` requires a
  deterministic scanner-deny schema and ignore/scaffold handling so adopter
  projects do not commit operational hook logs.
- `bridge/gtkb-credential-patterns-canonical-010.md` verified the canonical
  credential-patterns module at commit `862045d`.

## Findings

### 1. High - The proposed upgrade and doctor code does not match the current APIs

**Evidence:**

- Revision 005 claims existing adopters running `gt project upgrade` will
  receive the hook file, `.claude/settings.json` registration, and the
  `.gitignore` hook-log pattern:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:25-31`.
- The new settings helper uses `json.loads()` and `json.dumps()`:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:217-235`.
- Current `upgrade.py` does not import `json`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:4-10`.
- The proposed `execute_upgrade()` integration branches on
  `profile.includes_bridge`: `bridge/gtkb-hook-scanner-safe-writer-005.md:267`.
  Current `execute_upgrade()` has no `profile` in scope and its signature is
  only `(target, actions, *, force=False)`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:159-167`.
  The only local `profile` variable is inside `plan_upgrade()`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:82`.
- The proposed integration appends `UpgradeChange(...)` objects:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:271-287`.
  Current `upgrade.py` defines `UpgradeAction`, not `UpgradeChange`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:17-24`.
  Current `execute_upgrade()` returns `list[str]` status messages:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:159-165`,
  and the CLI prints those strings directly:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:705-707`.
- Current upgrade tests assert string status results from `execute_upgrade()`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_upgrade.py:112-133`.
- The proposed doctor check constructs `ToolCheck(..., passed=True/False)`:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:321-364`.
  Current `ToolCheck` has `required`, `found`, `status`, and `message` fields;
  it has no `passed` field:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:18-29`.

**Risk/impact:**

A literal implementation will fail with undefined names or invalid constructor
arguments before it can deliver the security hook. More importantly, the
existing-adopter delivery guarantee from `-005` is still not an implementation
contract that fits the current project.

**Required action:**

Revise the upgrade/doctor design against the actual local APIs:

1. Add the needed `json` import or avoid JSON handling in `upgrade.py`.
2. Derive the project profile inside `execute_upgrade()` from the manifest,
   pass it explicitly, or move the settings/gitignore actions into
   `plan_upgrade()` with executable `UpgradeAction` entries.
3. Preserve the current `execute_upgrade() -> list[str]` contract unless the
   CLI and tests are intentionally changed in the same bridge.
4. Implement the doctor drift check using the existing `ToolCheck` fields and
   add the check to the bridge-profile path in `run_doctor()`.
5. Include tests that would fail on the current sketch: missing `json`,
   missing `profile`, undefined `UpgradeChange`, and invalid `ToolCheck`
   constructor shape.

### 2. High - The proposed upgrade path can still hide or skip settings/gitignore repairs

**Evidence:**

- Revision 005 places settings and gitignore repair only in the
  `execute_upgrade()` integration snippet:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:262-287`.
- The CLI returns before calling `execute_upgrade()` when `plan_upgrade()`
  returns no actions:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:691-695`.
- Current `plan_upgrade()` also returns an empty list immediately when the
  scaffold version equals the package version:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:79-80`.
- Current `plan_upgrade()` only plans managed hook/rule file actions:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:85-156`.
  It has no settings or `.gitignore` action model.

**Risk/impact:**

The `-004` blocker was not just that the hook file could be absent; it was that
existing adopters could have an inert hook or commit its log. If settings and
gitignore repairs are hidden execute-time side effects, `--dry-run` will not
show them. If `plan_upgrade()` returns no managed-file action, the CLI will not
run the repair code at all. That makes the proposed doctor instruction to "run
`gt project upgrade`" unreliable for same-version or partially repaired drift.

**Required action:**

Make settings registration and `.gitignore` protection first-class upgrade
plan items, or otherwise guarantee that `gt project upgrade --apply` executes
those repairs even when no managed hook/rule file changes are pending. Add tests
for:

1. dry-run reports settings and `.gitignore` repairs;
2. same-version drift is either repaired by upgrade or reported with a different
   exact remediation path;
3. a project with the hook file already present but missing settings/gitignore
   is repaired.

### 3. Medium - The fallback catalog is still not an exact canonical mirror

**Evidence:**

- Revision 005 says the inline fallback mirrors all 30 canonical
  credential-class entries:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:44-46` and
  `bridge/gtkb-hook-scanner-safe-writer-005.md:123-125`.
- The proposed fallback uses the names `bash_private_key` and
  `bash_openssh_key`: `bridge/gtkb-hook-scanner-safe-writer-005.md:96-99`.
- The verified canonical names are `bash_private_key_block` and
  `bash_openssh_private_key`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:287-295`.
- A direct canonical-name check confirmed the 30-entry policy and those exact
  names:

```text
$env:PYTHONPATH='src'; python -c "from groundtruth_kb.governance.credential_patterns import CREDENTIAL_PATTERNS,BASH_EXTRAS,PII_PATTERNS; print(len(CREDENTIAL_PATTERNS), len(BASH_EXTRAS), len(PII_PATTERNS)); print([s.name for s in CREDENTIAL_PATTERNS if 'private' in s.name or 'openssh' in s.name]); print([s.name for s in list(CREDENTIAL_PATTERNS)+list(BASH_EXTRAS)])"
# 28 2 3
# ['bash_private_key_block', 'bash_openssh_private_key']
# ['api_key', 'bearer_header', 'token', 'secret', 'connection_string', 'azure_sas_key', 'github_pat', 'service_key', 'aws_key', 'ar_live_key', 'ar_user_key', 'ar_spa_plat_key', 'pk_live_key', 'arsk_key', 'anthropic_api_key', 'bash_aws_key', 'bash_anthropic_api_key', 'bash_secret_key', 'bash_stripe_live', 'bash_stripe_test', 'bash_stripe_restricted', 'bash_private_key_block', 'bash_openssh_private_key', 'bash_connection_string', 'bash_azure_account_key', 'bash_jwt_token', 'bash_password_arg', 'bash_password_flag_p', 'bash_credential_piped_output', 'bash_credential_exported_env_var']
```

- The proposed parity test checks names, patterns, and flags:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:142-166`. As written, the
  fallback code block in the same proposal would fail that test because the two
  canonical names above are missing.
- The proposal says the fallback mirrors canonical names and descriptions:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:44-46`, but the parity sketch
  does not compare descriptions:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:160-166`. Several proposed
  descriptions differ from canonical, for example `api_key`:
  `bridge/gtkb-hook-scanner-safe-writer-005.md:52-53` versus
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:136-140`.

**Risk/impact:**

Fallback mode would emit non-canonical `pattern_name` and
`pattern_description` values for some deny records, or the proposed parity test
would fail. Either result undermines the stable hook/collector interface this
bridge exists to define.

**Required action:**

Make the fallback catalog mechanically exact before implementation:

1. Correct the fallback names to match `CREDENTIAL_PATTERNS + BASH_EXTRAS`.
2. Either compare descriptions in the parity test or explicitly declare that
   only `pattern_name`, regex, and flags are stable while descriptions are
   human-readable and non-contractual.
3. Prefer a helper in the test that builds canonical `(name, pattern, flags,
   description)` tuples from `PatternSpec` and compares the parsed inline
   fallback against that tuple set.

## Confirmed Directional Resolutions From `-004`

- Full fallback coverage is the right policy. A code-generation step is not
  required for this bridge if the inline fallback is exact and parity-tested
  against canonical names, patterns, flags, and the chosen description contract.
- Boolean "changed" helper returns are acceptable internally, but public
  `execute_upgrade()` output should remain compatible with the current
  `list[str]` CLI/test contract unless deliberately changed.
- `.claude/hooks/*.log` is an acceptable gitignore pattern.
- Appending scanner-safe-writer last in `PreToolUse` is acceptable for write
  protection. If scanner-denial metrics need to count all credential-bearing
  attempts even when earlier PreToolUse hooks would deny for another reason,
  place scanner-safe-writer before content-validating bridge hooks and test the
  ordering.

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

- `src/groundtruth_kb/governance/credential_patterns.py`
- `templates/hooks/credential-scan.py`
- `src/groundtruth_kb/project/upgrade.py`
- `src/groundtruth_kb/project/doctor.py`
- `src/groundtruth_kb/project/scaffold.py`
- `src/groundtruth_kb/cli.py`
- `tests/test_upgrade.py`

No implementation tests were run because this is still a pre-implementation
proposal review. Evidence was gathered from the bridge proposal, prior bridge
reviews, parent GO, canonical verification, and the current GT-KB target
source.

## Decision Needed From Owner

None. Prime should revise this bridge before implementation.

Minimum revision bar:

1. Rewrite the upgrade and doctor integration against the actual GT-KB APIs.
2. Make settings registration and `.gitignore` repair visible and executable in
   the upgrade flow, including same-version or partial-drift cases.
3. Correct fallback catalog parity so the inline fallback exactly matches the
   canonical scanner-safe-writer policy.
