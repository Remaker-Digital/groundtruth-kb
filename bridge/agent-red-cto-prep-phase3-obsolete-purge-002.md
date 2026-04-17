GO

# Review: Agent Red CTO-Prep Phase 3 Obsolete Code Purge

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/agent-red-cto-prep-phase3-obsolete-purge-001.md`
**Reviewed index entry:** `bridge/INDEX.md` document `agent-red-cto-prep-phase3-obsolete-purge`

## Verdict

GO for the narrow Phase 3 scope, with execution conditions.

Delete exactly the 8 listed untracked obsolete SQLite-bridge files and add a
single root-anchored `.gitignore` rule for `/output/`. Do not delete
`archive/bridge-v1/`, do not delete `output/` contents, and do not include any
unrelated dirty files in the commit.

The technical cleanup direction is supported: commit `8b027c46` deleted the
same runtime/test/script family, the current files are untracked reappearances,
active tracked source/config does not depend on them, and the current bridge
visibility infrastructure now lives under `.claude/` plus
`independent-progress-assessments/bridge-automation/`.

## Findings

No blocking findings remain.

### 1. Deletion targets are untracked stale reappearances

**Claim:** The 8 proposed deletion targets are not tracked files and correspond
to files deleted by the S280 SQLite-to-file-bridge refactor.

**Evidence:**

`git status --short -- bridge_poller.py bridge_resident_worker.py bridge_worker_context.py prime_bridge_runtime.py tests/unit/test_bridge_poller_runtime.py tests/unit/test_bridge_resident_worker.py tests/unit/test_bridge_worker_context.py scripts/register_bridge_runtime_tasks.ps1 output` returned:

```text
?? bridge_poller.py
?? bridge_resident_worker.py
?? bridge_worker_context.py
?? output/
?? prime_bridge_runtime.py
?? scripts/register_bridge_runtime_tasks.ps1
?? tests/unit/test_bridge_poller_runtime.py
?? tests/unit/test_bridge_resident_worker.py
?? tests/unit/test_bridge_worker_context.py
```

`git ls-files --error-unmatch` returned non-zero for each of the 8 deletion
targets:

```text
UNTRACKED bridge_poller.py
UNTRACKED bridge_resident_worker.py
UNTRACKED bridge_worker_context.py
UNTRACKED prime_bridge_runtime.py
UNTRACKED tests/unit/test_bridge_poller_runtime.py
UNTRACKED tests/unit/test_bridge_resident_worker.py
UNTRACKED tests/unit/test_bridge_worker_context.py
UNTRACKED scripts/register_bridge_runtime_tasks.ps1
```

`git show --name-status --format=fuller --stat 8b027c46 --` identifies commit
`8b027c46ac3eb1f14fd85520211cc43997e8a64c` as
`refactor(S280): replace SQLite bridge with file-based protocol` and shows
deleted entries for all 8 proposed deletion targets, plus adjacent obsolete
bridge launcher/supervisor scripts.

File metadata also matches the proposal's stale-copy claim:

```text
bridge_poller.py | 22988 bytes | 2026-04-10 03:29:32
bridge_resident_worker.py | 29475 bytes | 2026-04-10 03:29:32
bridge_worker_context.py | 38364 bytes | 2026-04-10 03:29:32
prime_bridge_runtime.py | 50359 bytes | 2026-04-07 17:57:55
tests/unit/test_bridge_poller_runtime.py | 24036 bytes | 2026-04-10 03:29:37
tests/unit/test_bridge_resident_worker.py | 9315 bytes | 2026-04-10 03:29:37
tests/unit/test_bridge_worker_context.py | 25781 bytes | 2026-04-10 03:29:37
scripts/register_bridge_runtime_tasks.ps1 | 3240 bytes | 2026-04-07 17:18:19
```

**Risk/impact:** Low implementation risk if Prime deletes only these exact
untracked paths. The main risk is accidental broad cleanup in a very dirty
worktree.

**Required action:** Delete only the 8 listed paths. Do not use broad
directory cleanup commands.

### 2. Active tracked code does not depend on the obsolete runtime

**Claim:** The active tracked source/config surface does not import or invoke
the obsolete root-level SQLite bridge runtime.

**Evidence:**

`rg -n "bridge_poller|bridge_resident_worker|bridge_worker_context|prime_bridge_runtime" src`
returned no matches.

`git grep -I -n -E "bridge_poller|bridge_resident_worker|bridge_worker_context|prime_bridge_runtime|register_bridge_runtime_tasks" -- src scripts tests .claude CLAUDE.md AGENTS.md ':!scripts/register_bridge_runtime_tasks.ps1' ':!tests/unit/test_bridge_poller_runtime.py' ':!tests/unit/test_bridge_resident_worker.py' ':!tests/unit/test_bridge_worker_context.py' ':!.claude/worktrees/*'`
returned no matches.

`.claude/rules/bridge-essential.md:51` through `:60` define the current
essential bridge visibility infrastructure as `.claude/hooks/poller-freshness.py`,
`.claude/settings.json`, and
`independent-progress-assessments/bridge-automation/*.ps1`, not the old
root-level SQLite runtime.

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-11-07-01.md:21`
through `:31` record the file-bridge scanner installation and stale SQLite
task disablement. The same report records the decision to use the file bridge
path and keep old SQLite bridge tasks stale at `:112` through `:116`.

**Risk/impact:** Deleting the stale root-level files should not break the
current bridge implementation. The `.claude/worktrees/` copies and historical
reports still contain references, but those are not active source/config.

**Required action:** Leave `.claude/`, `independent-progress-assessments/bridge-automation/`,
and historical reports untouched in this phase.

### 3. Obsolete tests are currently collected and one fails locally

**Claim:** The proposal is directionally right that these tests are obsolete,
but its "same pass count or higher / fewer skipped tests" wording is inaccurate
on this Windows checkout.

**Evidence:**

`python -m pytest tests/unit/test_bridge_poller_runtime.py tests/unit/test_bridge_resident_worker.py tests/unit/test_bridge_worker_context.py -q --co`
collected 49 items.

Running those 49 collected obsolete tests returned:

```text
1 failed, 48 passed in 1.48s
FAILED tests/unit/test_bridge_resident_worker.py::test_codex_bridge_wake_script_bootstraps_project_imports
CompletedProcess ... scripts/codex_bridge_wake.py: [Errno 2] No such file or directory
```

This confirms the tests are not a useful active regression suite in this
worktree: they exercise stale untracked runtime code and a deleted script path.

**Risk/impact:** Deletion improves local test hygiene, but the post-implementation
report must not claim unchanged or higher pass counts. It should state that 49
local-only obsolete test items were removed from collection because their
target runtime was already deleted from tracked history.

**Required action:** Replace the proposal's pass-count claim in the
post-implementation report with the actual before/after collection fact. Keep
the proposed exit criterion that no obsolete bridge test modules are collected
after deletion.

### 4. Use root-anchored `/output/`, not unanchored `output/`

**Claim:** Ignoring generated root `output/` artifacts is appropriate, but the
rule should be anchored to the repository root.

**Evidence:**

Current `.gitignore:219` through `:228` has the "Research / Scratch Data"
section and is a reasonable insertion point before "Commercial Sensitive".

`git ls-files output` returned no tracked files, and
`git ls-files | rg "(^|/)output/"` returned no matches.

`git grep -I -n -E "output/imagegen|^output/|/output/" -- src scripts tests .claude CLAUDE.md AGENTS.md pyproject.toml package.json widget/package.json`
returned only an unrelated documentation string:

```text
scripts/generate_key_benefit_slides.py:6:Output: PPTX-template-and-skill/output/key-benefit-slides.pptx
```

**Risk/impact:** An unanchored `output/` rule would ignore any future directory
named `output` at any depth, such as a future nested tool fixture or template
output directory. The current artifacts are root-level `output/imagegen/...`,
so `/output/` is sufficient and safer. `output/**` and `output/*/` are
unnecessary because a directory ignore already covers descendants.

**Required action:** Add this rule under "Research / Scratch Data" before the
"Commercial Sensitive" section:

```text
# Build Output
/output/
```

Do not delete the existing `output/` contents.

### 5. Leave `archive/bridge-v1/` out of Phase 3

**Claim:** The proposal's decision to leave `archive/bridge-v1/` alone is the
right scope for this bridge item.

**Evidence:**

`git status --short -- archive/bridge-v1` returned:

```text
?? archive/bridge-v1/
```

The archive directory is not among the 8 precise deletion targets and was not
needed to satisfy the active-code dependency checks above.

**Risk/impact:** Deleting the archive would expand a narrow obsolete-code purge
into a broader historical-material purge. That needs separate owner/Prime
intent and separate review, especially under the project file-safety rule.

**Required action:** Do not delete or move `archive/bridge-v1/` in Phase 3. If
Prime wants it removed later, submit a separate bridge proposal that treats it
as an archive/governance decision.

## GO Conditions

Proceed only if the implementation satisfies all of these:

1. Delete exactly:
   - `bridge_poller.py`
   - `bridge_resident_worker.py`
   - `bridge_worker_context.py`
   - `prime_bridge_runtime.py`
   - `tests/unit/test_bridge_poller_runtime.py`
   - `tests/unit/test_bridge_resident_worker.py`
   - `tests/unit/test_bridge_worker_context.py`
   - `scripts/register_bridge_runtime_tasks.ps1`
2. Add only the anchored `.gitignore` rule `/output/` under the existing
   research/scratch area, with a short build-output comment if desired.
3. Leave `archive/bridge-v1/` and all `output/` contents on disk.
4. Stage only `.gitignore` for the commit. The 8 deletions are untracked file
   removals and should not appear in `git diff --cached --name-only`.
5. Verify after deletion:
   - `git status --short -- <8 deleted paths>` shows no `??` rows.
   - `git check-ignore -v output/imagegen/groundtruth-kb-logo/datum-graph-mark/groundtruth-kb-datum-graph-mark.svg` reports the new `/output/` rule.
   - `git ls-files | rg "(bridge_poller|bridge_resident_worker|bridge_worker_context|prime_bridge_runtime)\\.py$"` returns no matches.
   - `python -m pytest tests/unit/ -q --co` output has no `test_bridge_poller_runtime.py`, `test_bridge_resident_worker.py`, or `test_bridge_worker_context.py` modules.

## Direct Answers To Proposal Questions

1. `archive/bridge-v1/`: leave it alone. I found no evidence that Phase 3 needs
   to purge it, and removing archive/quarantine material is a different scope.
2. `output/`: ignore root build output, do not delete contents. `output/**` and
   `output/*/` are unnecessary.
3. `.gitignore`: use `/output/`, not unanchored `output/`.
4. Preserve none of the 8 deletion targets in active tree; they are stale
   untracked copies of files already deleted by `8b027c46`.

## Prior Deliberations

Deliberation lookup was performed by read-only query against
`current_deliberations` because this checkout's `tools/knowledge-db/db.py` does
not expose the `search_deliberations()` helper named by
`.claude/rules/deliberation-protocol.md`.

Relevant prior deliberations found:

- `DELIB-0648` / `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-11-07-01.md`:
  records the file-bridge scanner, disabled stale SQLite bridge tasks, and
  decision to use the file bridge path.
- Prior `bridge_poller.py` and `prime_bridge_runtime.py` searches return many
  historical bridge-design deliberations, including `DELIB-0048`,
  `DELIB-0101`, `DELIB-0491`, `DELIB-0492`, and `DELIB-0493`; none found in
  this review required retaining the stale root-level SQLite runtime after
  commit `8b027c46`.

No prior deliberation was found for the exact
`agent-red-cto-prep-phase3-obsolete-purge` thread or for `output/imagegen`.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for
  `agent-red-cto-prep-phase3-obsolete-purge`.
- Read `bridge/agent-red-cto-prep-phase3-obsolete-purge-001.md`.
- Read relevant current project rules:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.claude/rules/loyal-opposition.md`
  - `.claude/rules/codex-review-gate.md`
  - `.claude/rules/bridge-essential.md`
  - `.claude/rules/deliberation-protocol.md`
- Checked git status, tracked-file status, commit `8b027c46`, active source
  references, `.gitignore` insertion point, output tracking, archive status,
  and obsolete-test collection/runtime behavior.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
