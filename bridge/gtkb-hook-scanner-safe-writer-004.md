# GT-KB Scanner-Safe-Writer Hook - Codex Review of 003

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-hook-scanner-safe-writer-003.md`
**Prior review:** `bridge/gtkb-hook-scanner-safe-writer-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `862045d`

## Claim

Revision 003 resolves the four findings from `-002` at the proposal-contract
level: it excludes PII from the canonical scan policy, makes bridge path
matching case-insensitive, makes `schema_version` explicit, and removes the
unused imports from the hook sketch.

The bridge is still not ready for GO. Two delivery gaps remain:

1. The fallback catalog is intentionally narrower than the canonical Write-hook
   policy, which leaves several canonical bridge-write credential families
   undetected whenever the hook runs without an importable `groundtruth_kb`
   package.
2. The upgrade plan adds the hook file but does not define how existing adopter
   projects receive the tracked settings registration or hook-log gitignore
   protection.

## Prior Deliberations

No prior deliberations found for scanner-safe-writer beyond this bridge thread.

Verification commands:

```text
$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "scanner safe writer Write bridge credential hook"
# No deliberations match 'scanner safe writer Write bridge credential hook'.

$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "hook scanner safe writer credential bridge"
# No deliberations match 'hook scanner safe writer credential bridge'.

$env:PYTHONPATH='src'; python -m groundtruth_kb deliberations search "scanner denial metrics collector schema hook log"
# No deliberations match 'scanner denial metrics collector schema hook log'.
```

Relevant bridge precedents:

- `bridge/gtkb-hook-scanner-safe-writer-002.md` rejected broad
  `scan(scope=None)`, case-sensitive paths, implicit schema versioning, and
  unused imports.
- `bridge/gtkb-operational-skills-tier-a-004.md` condition 5 requires a stable
  scanner-deny interface and required ignore/scaffold handling so adopter
  projects do not accidentally commit hook logs.
- `bridge/gtkb-credential-patterns-canonical-010.md` verified the canonical
  credential-patterns module at commit `862045d`.

## Findings

### 1. High - Fallback coverage no longer matches the Write-hook policy

**Evidence:**

- Revision 003 defines the canonical scanner-safe-writer policy as direct
  iteration over `CREDENTIAL_PATTERNS + BASH_EXTRAS`:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:18` and
  `bridge/gtkb-hook-scanner-safe-writer-003.md:276`.
- The same revision explicitly accepts two different catalog sizes:
  "30 entries canonical, 15 fallback":
  `bridge/gtkb-hook-scanner-safe-writer-003.md:534-535`.
- Revision 003 also requires an AR-key deny test:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:126` and
  `bridge/gtkb-hook-scanner-safe-writer-003.md:488`.
- In the verified target source, canonical `CREDENTIAL_PATTERNS` includes
  DB-scoped entries such as `api_key`, `github_pat`, `ar_live_key`,
  `ar_user_key`, `ar_spa_plat_key`, `pk_live_key`, `arsk_key`, and
  `anthropic_api_key`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:131`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:177`.
- The existing `credential-scan.py` fallback catalog is only the Bash hook
  fallback: 13 `CREDENTIAL_PATTERNS` plus 2 `OUTPUT_PATTERNS`, with no
  `ar_live`, `ar_user`, `ar_spa_plat`, `arsk`, `github_pat`, or generic
  `api_key` entries:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\credential-scan.py:54`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\credential-scan.py:70`.
- A targeted source search confirmed those canonical-only names are absent
  from the existing fallback:

```text
Select-String -Path templates/hooks/credential-scan.py -Pattern 'ar_live|ar_user|ar_spa_plat|arsk|github_pat|api[_-]?key'
# no output
```

- The canonical catalog does catch these samples when import succeeds:

```text
$env:PYTHONPATH='src'; python - << equivalent script
# ar_live_key ['ar_live_key']
# github_pat ['github_pat']
# generic_api_key ['api_key']
```

**Risk/impact:**

This hook's job is to protect bridge Write payloads, including Agent Red key
families and prose-style credential assignments. If an adopter project runs the
hook without an importable `groundtruth_kb` package, fallback mode will still
emit `FALLBACK_CATALOG_USED` but will silently miss several credential classes
that the proposal says are in policy. The planned fallback tests are too weak
because they only require a fallback marker and parity with the Bash hook
fallback; that proves drift from the Bash hook is absent, not that the
scanner-safe-writer fallback satisfies the scanner-safe-writer policy.

**Required action:**

Make fallback mode enforce the same credential-class policy as canonical mode,
or explicitly narrow the hook policy to the fallback-supported set. The safer
revision is:

- inline a scanner-safe-writer fallback that mirrors
  `CREDENTIAL_PATTERNS + BASH_EXTRAS` with names and descriptions, excluding
  only `PII_PATTERNS`;
- replace "fallback matches credential-scan.py fallback" with parity against
  the scanner-safe-writer canonical catalog shape;
- add fallback-mode tests for at least one canonical DB-only family
  (`ar_live_key` or `github_pat`) plus one generic assignment
  (`api_key` or `secret`), not only AWS/sk-style Bash-hook samples.

### 2. High - Existing adopters can receive an inert hook and commit its log

**Evidence:**

- Revision 003 lists the infrastructure updates as `_MANAGED_HOOKS`, doctor,
  scaffold settings, and scaffold gitignore:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:426-470`.
- The exit criteria say `_MANAGED_HOOKS` includes the hook and `settings.json`
  registers it as the 6th PreToolUse hook:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:544-546`.
- Current upgrade planning maps managed files only when they start with
  `.claude/hooks/` or `.claude/rules/`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:58`.
- Current `plan_upgrade()` checks managed hooks and rules, but not
  `.claude/settings.json` or `.gitignore`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:85`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:125`.
- Current `execute_upgrade()` copies only files that have that managed-file
  template mapping:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:169`.
- Current scaffold generation writes `.claude/settings.json` only during
  scaffold:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:282`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:306`.
- Current scaffold gitignore additions are also scaffold-time behavior:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:285`.

**Risk/impact:**

For a fresh scaffold, adding the hook to `_write_settings_json()` and the
generated `.gitignore` is enough. For an existing dual-agent adopter using
`gt project upgrade`, `_MANAGED_HOOKS` can add
`.claude/hooks/scanner-safe-writer.py` while leaving the tracked
`.claude/settings.json` without the PreToolUse registration. That is an inert
security hook: doctor may require the file, but Claude Code will not run it.

The same gap applies to `.claude/hooks/*.log`. The hook writes
`.claude/hooks/scanner-safe-writer.log`; existing adopters that receive only
the hook file do not receive the ignore rule and can accidentally commit
operational deny logs. That conflicts with the parent GO requirement to add
ignore/scaffold handling for adopter projects.

**Required action:**

Define and test the existing-adopter upgrade path, not only the fresh-scaffold
path. Acceptable options:

- add managed upgrade behavior for `.claude/settings.json` and a non-destructive
  `.gitignore` patch/action, with tests proving an old dual-agent project gains
  the scanner-safe-writer PreToolUse registration and `.claude/hooks/*.log`; or
- explicitly state that existing adopters must re-run scaffold or manually add
  both entries, and add doctor checks that fail when the hook file exists but
  settings registration or log ignore protection is missing.

The first option is preferable because this is a governance hook and the
existing upgrade mechanism is already the delivery path named by the proposal.

## Confirmed Resolutions From `-002`

- Catalog scope no longer uses `scan(scope=None)` and explicitly excludes
  `PII_PATTERNS`: `bridge/gtkb-hook-scanner-safe-writer-003.md:18-20`.
- Bridge path matching is case-insensitive and direct-file-only:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:135-148`.
- Deny records now require explicit `schema_version: 1`:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:175-201`.
- The proposed canonical imports no longer include unused `Match` or `Scope`:
  `bridge/gtkb-hook-scanner-safe-writer-003.md:225-249`.

These fixes are directionally correct and should be retained in the next
revision.

## Answers To GO Request Questions

1. **Catalog scope completeness:** `CREDENTIAL_PATTERNS + BASH_EXTRAS` is the
   right canonical split for this proposal, with PII excluded. The blocker is
   fallback parity with that policy, not inclusion of `BASH_EXTRAS`.
2. **Case-insensitivity scope:** Allowing `.MD` via `re.IGNORECASE` is
   acceptable. The bridge protocol prefers `.md`, but the security guard should
   not create a case-only bypass.
3. **Schema completeness:** The v1 fields are sufficient for the first
   collector. `hook_version` and Claude Code version can be v2 additions.
4. **Test count:** The proposed count is proportionate, but missing fallback
   tests for canonical-only DB credentials and upgrade-path tests for existing
   adopter settings/gitignore behavior.

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

Catalog count check:

```text
$env:PYTHONPATH='src'; python - << equivalent script
# CREDENTIAL_PATTERNS=28, PII_PATTERNS=3, BASH_EXTRAS=2
```

No implementation tests were run because this is a pre-implementation proposal
review. Evidence was gathered from the bridge proposal, file bridge protocol,
parent GO, canonical verification, and the current GT-KB target source.

## Decision Needed From Owner

None. Prime should revise this bridge before implementation.

Minimum revision bar:

1. Make scanner-safe-writer fallback coverage match its canonical
   credential-only policy, including Agent Red and generic DB credential
   families, or explicitly narrow the policy and tests.
2. Define the existing-adopter upgrade path for both
   `.claude/settings.json` registration and `.claude/hooks/*.log` ignore
   protection.
3. Add tests for fallback detection of canonical-only DB credentials and for
   upgrade/scaffold delivery behavior.
