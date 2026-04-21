GO

# GT-KB Project Boundary and Upgrade Hardening Implementation - Codex Review

**Verdict:** GO, structural only
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed revision:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md`
**Prior review:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `cf29738`
**Observed Agent Red HEAD:** `aa6a5fe5`

## Claim

The revised bridge is acceptable as a structural redirect. Codex GO is granted
only to close this oversized implementation thread and require the work to move
into protocol-visible sub-bridges. This GO does not approve any GT-KB source,
doc, registry, script, CI, KB, or Agent Red mutation from this parent thread.

The revised file fixes the prior protocol blocker by replacing unindexed
intra-bridge phase notes with separate sub-bridge lifecycles. The rollback
substance remains open: the new git-based rollback idea is allowed to be
proposed in `gtkb-rollback-receipts-001`, but is not approved here as
"restore-capable by construction."

## Evidence Summary

- The active file bridge protocol represents review gates only through
  versioned files and `bridge/INDEX.md` status lines; it does not define
  unindexed intra-bridge review notes (`.claude/rules/file-bridge-protocol.md`).
- `-003` replaces the rejected single 9-phase bridge with separate sub-bridges,
  each having its own scope -> GO -> implement -> post-impl -> VERIFIED
  lifecycle (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md:13`,
  `:17`, `:75`).
- `-003` defers detailed implementation content to those sub-bridges and says
  implementation risk lives there, not in this structural redirect
  (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md:53`,
  `:98`).
- Current GT-KB still has no rollback or retrofit command surface:
  `gt project upgrade` exposes only `--dry-run/--apply`, `--force`, and `--dir`
  (`src/groundtruth_kb/cli.py:683-686`).
- Current upgrade execution still mutates files directly with `.bak` backups and
  direct writes, not restore-capable receipts (`src/groundtruth_kb/project/upgrade.py:318-369`,
  `:423`, `:448`, `:453`).
- Current Agent Red remains a valid read-only dogfood target: `gt project
  upgrade --dry-run --dir "<Agent Red>"` returns a single skip for missing
  `groundtruth.toml`; `gt project doctor --dir "<Agent Red>"` fails on missing
  `groundtruth.toml`; Agent Red still tracks `groundtruth.db` and pins
  `groundtruth-kb.git@v0.2.1` in `requirements-local.txt:17` and
  `requirements-test.txt:49`.
- Regression smoke check in GT-KB passed:
  `python -m pytest tests/test_upgrade.py tests/test_managed_registry.py -q --tb=short`
  -> `49 passed, 1 warning in 0.62s`.

## Findings

### F1 - Protocol-visible sub-bridges resolve the prior phase-gate blocker

**Severity:** Resolved by `-003`, with conditions

The revised structure is the correct bridge-level fix. Each implementation
slice must now be filed as its own `Document:` entry and must receive its own
Codex GO before implementation begins. This replaces the rejected plan's
unindexed status notes with objects the automated bridge scan can actually
process.

**Conditions:**

- Do not implement GT-KB changes under this parent `GO`.
- File sub-bridges as separate bridge entries, not informal notes.
- Each sub-bridge must include its own proposed files, tests, dogfood evidence
  plan, and post-implementation verification criteria.
- This parent thread can close only after the sub-bridges it delegates are
  either VERIFIED or explicitly superseded by a later Codex-reviewed bridge.

### F2 - Git-based rollback is not approved here as restore-capable by construction

**Severity:** High, delegated to rollback sub-bridge

`-003` replaces durable receipt payloads with git-based rollback and asserts
that receipts are always restore-capable as long as git history is preserved
because reflog is available after branch pruning
(`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md:38-43`).
That assertion is too broad for implementation GO.

Git can be a useful rollback substrate, but it is not automatically equivalent
to a restore-capable receipt. It does not restore untracked or ignored files,
depends on object retention and repository health, can be defeated by history
rewrites or garbage collection, and `git reset --hard` is destructive unless
the tool has proven a clean tree and obtained explicit operator intent.

**Required in `gtkb-rollback-receipts-001`:**

- Treat git-based rollback as a candidate design, not a pre-approved answer.
- Define exact rollback modes and defaults. `git revert` may be the default
  history-preserving mode; `git reset --hard` must require explicit opt-in and
  clean-tree proof.
- Prove restore coverage for every touched artifact class. If any touched path
  can be untracked, ignored, newly created, deleted, or outside git tracking,
  the design needs receipt-owned payload storage for that class.
- Define object-retention and failure semantics. If git objects or receipt
  payloads are unavailable, rollback must fail loudly with a diagnostic that
  names the missing dependency.
- Add tests for large files, deleted files, new files, structured JSON merge,
  gitignore append, manifest updates, dirty-tree refusal, and rollback after
  unrelated adopter edits.

### F3 - Registry syntax correction is accepted but must be enforced in sub-bridges

**Severity:** Medium, delegated

`-003` correctly notes that the live registry uses `[[artifacts]]`, not
`[[managed]]` (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md:73`).
Current GT-KB evidence confirms `templates/managed-artifacts.toml` uses
`[[artifacts]]`, and the managed registry loader reads the artifact list from
that root.

**Required in `gtkb-artifact-ownership-matrix-001`:**

- Extend the existing `[[artifacts]]` records; do not introduce a parallel
  root.
- State whether ownership metadata is loaded through the existing managed
  registry dataclasses or a raw-TOML ownership resolver.
- Add tests proving the registry loader and ownership resolver agree on record
  IDs and target paths.

### F4 - Agent Red dogfood must not disappear into dispersed evidence

**Severity:** Medium, condition

`-003` says Phase 8 Agent Red dogfood is "subsumed into each sub-bridge's
VERIFIED evidence" (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md:27`,
`:66`). That is acceptable only if the original Condition 4 remains visible:
Agent Red is read-only, and the classification artifact is written to GT-KB,
not Agent Red.

**Condition:**

At least one sub-bridge, probably preflight/retrofit or docs parity, must own
the generated Agent Red classification report as an explicit deliverable. Other
sub-bridges may add read-only dogfood checks, but they do not replace the
classification report requirement.

## Required Action Items

1. File `gtkb-artifact-ownership-matrix-001` and
   `gtkb-rollback-receipts-001` as separate bridge entries before any
   implementation.
2. In `gtkb-rollback-receipts-001`, present git rollback as a design subject to
   review and satisfy the restore-capability requirements above.
3. In every sub-bridge, state the exact Agent Red dogfood boundary and confirm
   no Agent Red writes.
4. Keep this parent thread as a coordination/supersession record only.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-project-boundary-and-upgrade-hardening-implementation' -Context 4,20
Get-ChildItem bridge | Where-Object { $_.Name -like 'gtkb-project-boundary-and-upgrade-hardening-implementation-*' } | Sort-Object Name | Select-Object -ExpandProperty Name
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md
rg -n "sub-bridges|git-based rollback|git history|reflog|reset --hard|merge commit|No implementation risk|Next Steps|\[\[artifacts\]\]|\[\[managed\]\]" bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md
git rev-parse --short HEAD
git status --short --branch
git ls-files groundtruth.db requirements-local.txt requirements-test.txt
rg -n "groundtruth-kb|groundtruth\.db|groundtruth\.toml" requirements-local.txt requirements-test.txt .gitignore
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
rg -n "project upgrade|rollback|retrofit|force|dry-run|dir" src/groundtruth_kb/cli.py
rg -n "manifest is None|\.bak|copy2|write_text|append-gitignore|scaffold_version" src/groundtruth_kb/project/upgrade.py
rg -n "\[\[artifacts\]\]|ownership|upgrade_policy|adopter_divergence_policy|workflow_targets|\[\[managed\]\]" templates/managed-artifacts.toml src/groundtruth_kb/project/managed_registry.py
python -m groundtruth_kb project upgrade --dry-run --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m groundtruth_kb project doctor --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m pytest tests/test_upgrade.py tests/test_managed_registry.py -q --tb=short
```

Observed command results:

```text
GT-KB HEAD: cf29738
Agent Red HEAD: aa6a5fe5
GT-KB targeted tests: 49 passed, 1 warning in 0.62s
Agent Red upgrade dry-run: [SKIP] groundtruth.toml - No [project] manifest found - run `gt project init` first
Agent Red doctor: FAIL on missing groundtruth.toml
```

