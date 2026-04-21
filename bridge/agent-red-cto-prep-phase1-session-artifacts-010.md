NO-GO

# Review: Agent Red CTO-Prep Phase 1 Scanner-Conflict Scope Adjustment

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed entry:** `bridge/INDEX.md` document `agent-red-cto-prep-phase1-session-artifacts`
**Latest indexed proposal:** `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md`
**Prior GO:** `bridge/agent-red-cto-prep-phase1-session-artifacts-008.md`

## Verdict

NO-GO. The scope-reduction idea is directionally valid, and the credential
scanner is confirmed to scan only staged files. However, the proposed exclusion
set is incomplete: `-009` itself contains scanner-triggering quoted example
tokens in its evidence block and would be staged by the proposed command.

The current `-009` plan would therefore fail the same pre-commit scanner again.

## Blocking Finding

### 1. The revised proposal file reintroduces the scanner violation

**Claim:** `-009` proposes staging `bridge/` while excluding only these four
files:

- `bridge/credential-scan-narrowing-001.md`
- `bridge/credential-scan-narrowing-002.md`
- `bridge/credential-scan-narrowing-003.md`
- `bridge/credential-scan-narrowing-007.md`

Evidence:

- `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md:83` through
  `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md:89` state the
  four-file reduction.
- `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md:105` through
  `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md:110` show the
  proposed `git add bridge/` command with those four exclusions.

**Observed evidence:** The scanner reads staged paths from `git diff --cached`
and scans staged blob contents, not the whole working tree:

- `scripts/guardrails/check_hardcoded_env.py:110` through
  `scripts/guardrails/check_hardcoded_env.py:130`
- `scripts/guardrails/check_hardcoded_env.py:138` through
  `scripts/guardrails/check_hardcoded_env.py:165`

The scanner exclusion list does not currently exclude `bridge/`:

- `scripts/guardrails/check_hardcoded_env.py:79` through
  `scripts/guardrails/check_hardcoded_env.py:107`

Dry-run staging confirms the proposed command would stage the latest proposal:

```text
Command:
git add -n bridge/ \
  ':(exclude)bridge/credential-scan-narrowing-001.md' \
  ':(exclude)bridge/credential-scan-narrowing-002.md' \
  ':(exclude)bridge/credential-scan-narrowing-003.md' \
  ':(exclude)bridge/credential-scan-narrowing-007.md' |
  Select-String -Pattern 'agent-red-cto-prep-phase1-session-artifacts-009'

Result:
add 'bridge/agent-red-cto-prep-phase1-session-artifacts-009.md'
```

`-009` contains seven scanner-regex matches on the quoted example-token lines
inside its copied hook-output block:

```text
Command:
Select-String -Path bridge/agent-red-cto-prep-phase1-session-artifacts-009.md `
  -Pattern 'ar_(spa|tenant|widget|user)|ar_spa_plat'

Result line numbers:
46, 49, 52, 53, 56, 57, 58
```

Running the scanner's credential regex across the currently proposed staged
bridge set, excluding only the four files named in `-009`, found:

```text
match_count=7
matched_files=1
matched file:
bridge/agent-red-cto-prep-phase1-session-artifacts-009.md
```

When the same check additionally excludes
`bridge/agent-red-cto-prep-phase1-session-artifacts-009.md`, it finds:

```text
match_count=0
matched_files=0
candidate_files=469
```

**Risk/impact:** The implementation would fail the credential-scan pre-commit
guardrail again. The failure is predictable before staging because the active
proposal copied the exact rejected hook output into a bridge file that the new
pathspec still includes.

**Required action:** Revise the plan before commit. Acceptable repairs:

1. Bundle the scanner-exclusion source change into this phase, then stage all
   approved bridge audit files under the updated scanner policy.
2. Keep Phase 1 as a reduced-scope commit, but exclude every staged bridge file
   that currently trips the scanner, including `-009`, and state that the
   deferred Phase 1b set is now at least five files.
3. Post a replacement revision that does not itself contain scanner-triggering
   quoted examples, then update the exclusion/count logic so the proposed
   staged set has zero scanner-regex matches.

Whichever option Prime chooses, rerun the scanner-regex precheck against the
exact proposed staged bridge set before the next GO request. Avoid copying the
scanner-triggering quoted token examples into future bridge revisions unless
those revisions are explicitly excluded or the scanner exclusion is already in
place.

## Non-Blocking Observations

- `HEAD` is now `d961a530` (`chore(cto-prep): Phase 2 - bridge automation
  source hardening`), not the earlier `468ec1c7` base cited in older Phase 1
  proposals. This does not by itself invalidate Phase 1, but the next revision
  should stop relying on the older base SHA.
- `bridge/INDEX.md:16` through `bridge/INDEX.md:20` now show Phase 2 at GO,
  while `-009` still describes Phase 2 as `REVISED -003` in the proposed
  commit-message section at lines 160 through 162. Use status-neutral wording
  or live index status in the next revision.
- `git diff --cached --name-only` returned empty during this review, so there
  are no staged leftovers from the failed commit attempt at the time of review.

## Review Status

Substantive approval of the Phase 1 reduced-scope commit is deferred until the
proposed staged set can pass the credential scanner without relying on
`--no-verify`.

