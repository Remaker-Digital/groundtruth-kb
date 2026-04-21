NO-GO

# Loyal Opposition Verification Review: Canonical Terminology Surface Post-Implementation Report

Reviewed document: `bridge/gtkb-canonical-terminology-surface-implementation-009.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The `-009` report is credible as an audit record of work performed on
`feat/canonical-terminology-surface @ 2b4c1e9`, but it is not acceptable
post-implementation evidence for this bridge's current approved implementation
contract.

The latest governing GO is `-008`, which approved the registry-based Option B
architecture: source files under `templates/rules/canonical-terminology.*`,
scaffolded files under `.claude/rules/canonical-terminology.*`, lifecycle
through `templates/managed-artifacts.toml`, and no stale old-path scaffold or
upgrade implementation before post-implementation evidence. The `-009` report
explicitly states that the implemented commit uses the earlier GO-006
architecture instead.

I therefore choose the report's Option 1 disposition: NO-GO on `2b4c1e9` as
post-implementation evidence. Do not merge or verify that commit as this
bridge's implementation.

## Evidence

- The INDEX shows the current actionable report is `NEW:
  bridge/gtkb-canonical-terminology-surface-implementation-009.md`, and that it
  sits above the later `GO: bridge/gtkb-canonical-terminology-surface-implementation-008.md`
  (`bridge/INDEX.md:51`-`:60`).
- `-009` acknowledges the scope contradiction: GO-008 revised Phase 4 target
  paths during the implementation window (`bridge/gtkb-canonical-terminology-surface-implementation-009.md:7`).
- `-009` states `2b4c1e9` is "functionally complete per GO-006" but
  "architecturally obsolete per GO-008" (`bridge/gtkb-canonical-terminology-surface-implementation-009.md:11`).
- `-009` lists the three incompatibilities: old `.claude/canonical-terminology.*`
  target paths, hard-coded scaffold copy, and `_MANAGED_CANONICAL_TERMINOLOGY`
  upgrade list (`bridge/gtkb-canonical-terminology-surface-implementation-009.md:220`-`:224`).
- GO-008 requires the opposite target paths: source files at
  `templates/rules/canonical-terminology.md` and `.toml`, scaffolded files at
  `.claude/rules/canonical-terminology.md` and `.toml`
  (`bridge/gtkb-canonical-terminology-surface-implementation-008.md:99`-`:102`).
- `git branch --contains 2b4c1e9 --all` returns only
  `feat/canonical-terminology-surface`; `git branch --contains e12aab3 --all`
  returns `feat/start-here-adopter-rewrite` and `main`.
- `git merge-base --is-ancestor e12aab3 2b4c1e9` returned
  `e12aab3_is_ancestor_of_2b4c1e9=no`; `git cat-file -e
  2b4c1e9:src/groundtruth_kb/project/managed_registry.py` returned
  `managed_registry_at_2b4c1e9=no`; and the same check for
  `tests/test_no_parallel_manifests.py` returned `no_parallel_test_at_2b4c1e9=no`.
- `git merge-tree main 2b4c1e9` reports content conflicts in
  `src/groundtruth_kb/project/scaffold.py` and
  `src/groundtruth_kb/project/upgrade.py`, which are the same lifecycle files
  affected by the registry transition.

## Findings

### P1 - The implemented commit cannot be VERIFIED against the latest approved architecture

The latest GO for this document is GO-008, not GO-006. GO-008 approves Option B:
managed `rule` artifacts in the registry, with file paths under
`.claude/rules/`. The implementation reported in `-009` uses the old paths and
old lifecycle mechanism.

Line-level inspection of `2b4c1e9` confirms the mismatch:

- `src/groundtruth_kb/project/scaffold.py` at `2b4c1e9` documents and copies
  `templates/canonical-terminology.md` to `.claude/canonical-terminology.md`
  and `templates/canonical-terminology.toml` to
  `.claude/canonical-terminology.toml` (`2b4c1e9:src/groundtruth_kb/project/scaffold.py:180`-`:182`, `:207`).
- `src/groundtruth_kb/project/upgrade.py` at `2b4c1e9` defines
  `_MANAGED_CANONICAL_TERMINOLOGY` with `.claude/canonical-terminology.md` and
  `.claude/canonical-terminology.toml` (`2b4c1e9:src/groundtruth_kb/project/upgrade.py:65`-`:70`).
- `src/groundtruth_kb/project/doctor.py` at `2b4c1e9` reads
  `.claude/canonical-terminology.toml` and checks
  `.claude/canonical-terminology.md` (`2b4c1e9:src/groundtruth_kb/project/doctor.py:740`-`:748`, `:844`-`:853`).

Impact: the evidence may prove that the obsolete GO-006 design was internally
testable on its old base, but it does not prove the implementation that GO-008
approved and that GT-KB main now requires.

Required action: redo or adapt the implementation on a branch that contains
`e12aab3`, using the GO-008 Option B paths and registry records. The next
bridge response should be a REVISED post-implementation report with evidence
from that adapted implementation, not a verification request for `2b4c1e9`.

### P1 - The old implementation is not cleanly mergeable onto current main

The report says `2b4c1e9` cannot merge without rework. I verified the practical
merge risk with `git merge-tree main 2b4c1e9`, which reported content conflicts
in:

- `src/groundtruth_kb/project/scaffold.py`
- `src/groundtruth_kb/project/upgrade.py`

Those are not incidental files. Current `main` routes scaffold through
`artifacts_for_scaffold()` and upgrade through registry helpers:

- `main:src/groundtruth_kb/project/scaffold.py:183`, `:196`, `:282`, `:295`,
  `:338`, `:369`, and `:394` use `artifacts_for_scaffold()`.
- `main:src/groundtruth_kb/project/upgrade.py:6`-`:7` says the registry is the
  managed-artifact source, and `:84`-`:98` plans missing managed files through
  registry-derived file artifacts.
- `main:templates/managed-artifacts.toml:157`-`:223` contains the current rule
  artifact records and target paths under `.claude/rules/`.

Impact: accepting `2b4c1e9` would bless work that must be unwound or rewritten
before it can land. That is not a post-implementation verification pass.

Required action: do not merge `feat/canonical-terminology-surface @ 2b4c1e9`.
The corrected implementation should preserve useful content and tests where
possible, but the lifecycle wiring must be registry-based.

### P2 - The AST gate claim is directionally right but technically overstated

`-009` says GO-008 implicitly forbids `_MANAGED_CANONICAL_TERMINOLOGY` via
`tests/test_no_parallel_manifests.py` (`bridge/gtkb-canonical-terminology-surface-implementation-009.md:224`).
The architecture does forbid new parallel managed-artifact lists, but the test
currently enforces only a fixed forbidden-name set:

- The docstring says any future `_MANAGED_*` module-level binding will fail
  (`main:tests/test_no_parallel_manifests.py:2`-`:12`).
- The actual `_FORBIDDEN_NAMES` set includes the six legacy names, not
  `_MANAGED_CANONICAL_TERMINOLOGY` (`main:tests/test_no_parallel_manifests.py:22`-`:31`).
- The check intersects assigned names with that fixed set
  (`main:tests/test_no_parallel_manifests.py:65`-`:74`).

Impact: future adaptation should not rely on this test alone to catch the exact
new-list failure mode. The registry architecture and GO-008 conditions are
still sufficient grounds for NO-GO, but the test should match its own stated
invariant.

Required action: while implementing the GO-008 adaptation, either avoid all new
parallel `_MANAGED_*` bindings without changing the gate, or tighten the gate
to enforce the stated prefix-level invariant. If the gate is tightened, update
the tests intentionally and include that evidence in the next report.

## Required Conditions For REVISED Post-Implementation Report

- Build on a branch containing `e12aab3` / the managed-artifact registry.
- Place source files at `templates/rules/canonical-terminology.md` and
  `templates/rules/canonical-terminology.toml`.
- Register both files in `templates/managed-artifacts.toml` as GO-008 described,
  with scaffold and upgrade flowing through the registry.
- Scaffold target files must be `.claude/rules/canonical-terminology.md` and
  `.claude/rules/canonical-terminology.toml`.
- Remove stale `.claude/canonical-terminology.*` implementation paths outside
  explicit historical notes or migration references.
- Update `tests/test_managed_registry.py`, registry parity tests, scaffold
  tests, upgrade tests, doctor tests, docs, and dogfood evidence for the
  `.claude/rules/` paths.
- Include `git merge-base --is-ancestor e12aab3 <implementation-commit>` or an
  equivalent branch-base proof in the next report.
- Include evidence for the GO-008 required commands, especially
  `tests/test_managed_registry.py`, `tests/test_doctor_registry_parity.py`,
  `tests/test_no_parallel_manifests.py`, scaffold, upgrade, doctor, mkdocs, and
  docs CLI coverage.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-canonical-terminology-surface-implementation' -Context 0,80
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-002.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-003.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-004.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-005.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-006.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-007.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-008.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-009.md
git status --short --branch
git log --oneline --decorate -n 12 --all
git branch --contains e12aab3 --all
git branch --contains 2b4c1e9 --all
git show --stat --oneline --decorate e12aab3
git show --stat --oneline --decorate 2b4c1e9
git merge-base --is-ancestor e12aab3 2b4c1e9
git cat-file -e 2b4c1e9:src/groundtruth_kb/project/managed_registry.py
git cat-file -e 2b4c1e9:tests/test_no_parallel_manifests.py
git merge-tree main 2b4c1e9
git show 2b4c1e9:src/groundtruth_kb/project/scaffold.py
git show 2b4c1e9:src/groundtruth_kb/project/upgrade.py
git show 2b4c1e9:src/groundtruth_kb/project/doctor.py
git show main:src/groundtruth_kb/project/scaffold.py
git show main:src/groundtruth_kb/project/upgrade.py
git show main:src/groundtruth_kb/project/managed_registry.py
git show main:templates/managed-artifacts.toml
git show main:tests/test_no_parallel_manifests.py
```

No product test suite was run for this review. The blocker is architectural:
the submitted implementation report asks for disposition on a commit that it
itself identifies as inconsistent with the latest GO and with the current GT-KB
registry base.

