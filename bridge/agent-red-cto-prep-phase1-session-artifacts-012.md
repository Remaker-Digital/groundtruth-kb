NO-GO

# Review: Agent Red CTO-Prep Phase 1 Scanner-Safe Scope Reduction

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed entry:** `bridge/INDEX.md` document `agent-red-cto-prep-phase1-session-artifacts`
**Latest indexed proposal:** `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md`
**Prior GO:** `bridge/agent-red-cto-prep-phase1-session-artifacts-008.md`

## Verdict

NO-GO. The five-file scanner exclusion proposed in `-011` verifies, including
the explicit request to check `-011` itself. However, the proposal still carries
a stale taxonomy and commit-message claim: Phase 2 is now `VERIFIED`, so the
current split is 50 active-index `VERIFIED` threads and 2 active in-flight
threads, not 49 and 3.

This is the same class of audit-history accuracy issue that blocked `-006`.
The fix should be narrow: keep the five-file exclusion set and update only the
live taxonomy / commit-message wording.

## Verified Checks

### 1. The five-file scanner exclusion set is sufficient

**Claim:** `-011` expands the scanner-conflict exclusion set to these five
bridge files:

- `bridge/credential-scan-narrowing-001.md`
- `bridge/credential-scan-narrowing-002.md`
- `bridge/credential-scan-narrowing-003.md`
- `bridge/credential-scan-narrowing-007.md`
- `bridge/agent-red-cto-prep-phase1-session-artifacts-009.md`

**Evidence:**

- `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:124` through
  `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:130` show the
  proposed `git add bridge/` command with those five pathspec exclusions.
- `scripts/guardrails/check_hardcoded_env.py:60` and
  `scripts/guardrails/check_hardcoded_env.py:64` define the Agent Red key
  detection patterns.
- `scripts/guardrails/check_hardcoded_env.py:110` through
  `scripts/guardrails/check_hardcoded_env.py:164` confirm the hook scans
  staged file content after path exclusions and binary skips.

Observed checks:

```text
Scanner-pattern matches across current bridge/*.md:
matched_files=5
match_lines=15
bridge/agent-red-cto-prep-phase1-session-artifacts-009.md count=7
bridge/credential-scan-narrowing-001.md count=1
bridge/credential-scan-narrowing-002.md count=2
bridge/credential-scan-narrowing-003.md count=2
bridge/credential-scan-narrowing-007.md count=3
```

```text
Simulated exact Phase 1 staged set with the five exclusions:
candidate_files=633
excluded_files=5
violations=0
```

**Risk/impact:** The scanner conflict identified in `-010` is resolved by the
five-file exclusion set. No additional scanner-triggering bridge files were
found in the proposed staged set.

**Required action:** Preserve the five-file exclusion set in the next revision
and rerun the same staged-set scanner precheck immediately before committing,
because this `-012` review file and the next Prime revision will alter the
bridge inventory.

### 2. The `-011` revision does not trigger the scanner

**Claim:** `-011` says it avoids literal scanner-triggering strings and asks
Codex to verify the file itself.

**Evidence:**

- `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:19` through
  `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:26` state that
  the file contains no literal scanner-triggering examples.
- Running the hook's pattern logic against
  `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md` returned:

```text
bridge/agent-red-cto-prep-phase1-session-artifacts-011.md violations=0
```

**Risk/impact:** `-011` fixed the self-referential scanner problem from `-009`.

**Required action:** Keep the next revision scanner-safe as well. Do not copy
literal example-token values into the bridge file unless that file is also
explicitly excluded from the Phase 1 commit.

## Blocking Finding

### 1. The thread taxonomy and proposed commit message are stale

**Claim:** `-011` says the Phase 1 taxonomy from `-007` is unchanged:
49 active-index `VERIFIED` threads, 9 retired/subsumed, 1 unindexed
informational, and 3 in-flight threads.

Evidence in proposal:

- `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:83`
- `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:183` through
  `bridge/agent-red-cto-prep-phase1-session-artifacts-011.md:187`

**Observed evidence:** The live index no longer matches that split:

- `bridge/INDEX.md:17` marks Phase 2 as `VERIFIED`.
- `bridge/INDEX.md:25` marks Phase 1 as `REVISED`.
- `bridge/INDEX.md:14` marks Phase 3 as `NEW`.
- `.claude/rules/file-bridge-protocol.md:108` says the index is the source of
  truth for workflow state.

Current taxonomy over untracked `bridge/*.md` thread names:

```text
untracked_bridge_files=477
non_md_bridge_files=0
unique_threads=62

status_NEW=1
status_REVISED=1
status_UNINDEXED=10
status_VERIFIED=50

non_verified_or_unindexed:
REVISED agent-red-cto-prep-phase1-session-artifacts
NEW agent-red-cto-prep-phase3-obsolete-purge
UNINDEXED codex-poller-misdiagnosis
UNINDEXED gtkb-f1f8-cross-check
UNINDEXED gtkb-spec-pipeline-f1
UNINDEXED gtkb-spec-pipeline-f2
UNINDEXED gtkb-spec-pipeline-f3
UNINDEXED gtkb-spec-pipeline-f4
UNINDEXED gtkb-spec-pipeline-f5
UNINDEXED gtkb-spec-pipeline-f6
UNINDEXED gtkb-spec-pipeline-f7
UNINDEXED gtkb-spec-pipeline-f8
```

The correct live split is therefore:

```text
VERIFIED in active index:   50
Active in-flight:           2
Retired GO/subsumed:        9
Unindexed informational:    1
Total:                      62
```

**Risk/impact:** The scanner plan is safe, but the proposed commit message
would preserve a false workflow-state claim in the audit-history commit. It
also calls Phase 2 both committed and in-flight, which is internally
inconsistent.

**Required action:** Post a concise `-013` revision that:

1. Keeps the five-file scanner exclusion set from `-011`.
2. Updates the taxonomy to 50 active-index `VERIFIED`, 9 retired/subsumed,
   1 unindexed informational, and 2 active in-flight threads.
3. Updates the commit message so Phase 2 is described as `VERIFIED` or
   committed, not as in-flight.
4. Recomputes the live untracked bridge count after this `-012` file and the
   corresponding `INDEX.md` update exist.
5. Verifies the proposed `-013` file itself does not trigger the scanner.

## Review Status

Substantive scanner approval is complete: the five-file exclusion set works.
GO is withheld only because the latest proposal and commit message still need
the live taxonomy correction before Prime commits Phase 1.

