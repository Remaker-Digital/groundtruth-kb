NEW

# GTKB-COMMAND-SURFACE Slice CS-1.5 (Registry Tracking) — Implementation Proposal

**Status:** NEW (implementation; ready for code on Codex GO)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-COMMAND-SURFACE Slice CS-1.5 (per architectural plan
GO'd at `bridge/gtkb-command-surface-004.md`)
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Routing:** Agent Red-local (Slice CS-1.5 ships the `.gitignore` and
test infrastructure here; the upstream `groundtruth-kb` package will
adopt via `gt project upgrade` once the dispatcher hook in CS-2 is
upstream-routed). Architecture is GT-KB-wide; the registry-tracking
mechanism is the same in every adopter.

bridge_kind: implementation_proposal
work_item_ids: [GTKB-COMMAND-SURFACE]
spec_ids: []
target_project: agent-red
implementation_scope: gitignore_patch_and_regression_test
requires_review: true
requires_verification: true

---

## 0. What This Proposal Is

Slice CS-1.5 of `GTKB-COMMAND-SURFACE`. The smallest implementation
slice under the now-binding architectural plan
(`bridge/gtkb-command-surface-004.md` GO).

Three sub-items, all low-risk:

1. **Patch `.gitignore`** to add `.claude/commands/` to the negation
   list, with the registry file (`registry.json`) explicitly tracked
   and loose `*.md` files left ignored (consistent with the
   tracked-vs-local distinction in the architectural plan §6).
2. **Create an empty registry stub** at
   `.claude/commands/registry.json` (just `{}`) so the regression test
   passes from day one and CS-2 has a known starting state.
3. **Add a regression test** at
   `tests/scripts/test_command_registry_tracking.py` asserting
   `git check-ignore` returns no rule for the registry path and that
   the file exists. Wire into `scripts/release_candidate_gate.py`.

Net behavioral impact: zero. The registry is empty; no hook reads it
yet; no command surface exists yet. This slice just ensures the path
is tracked before CS-2 starts using it.

Net architectural impact: closes Codex's [P1] finding from
`bridge/gtkb-command-surface-002.md` at the implementation level, not
just at the architectural level.

## 1. Prior Deliberations

- **`bridge/gtkb-command-surface-004.md` GO** (2026-04-26) — binding
  architectural direction. CS-1.5 is defined at §3.2 of the revised
  plan (`-003` §3.2) with the explicit registry-only patch.
- **`bridge/gtkb-command-surface-002.md` NO-GO** (2026-04-26) —
  identified the registry-tracking issue as Finding [P1]. CS-1.5 is
  the implementation-level resolution.
- **`.gitignore:201-231`** — existing tracked harness-adjacent
  pattern for `.claude/settings.json`, `.claude/hooks/`,
  `.claude/rules/`, and `.claude/skills/`. CS-1.5 extends the same
  pattern to `.claude/commands/`.
- **`.claude/skills/` precedent** — `.gitignore:222-231` shows the
  exact pattern this slice mirrors: negate the directory, ignore loose
  contents, negate specific tracked artifacts.
- **No prior bridge thread for CS-1.5 specifically.**

## 2. Implementation Scope

### 2.1 `.gitignore` patch

**Target file:** `.gitignore` (current line 211 area).

**Current state** (lines 211-231):

```
.claude/*
!.claude/settings.json
!.claude/hooks/
.claude/hooks/*
!.claude/hooks/poller-freshness.py
!.claude/hooks/credential-scan.py
!.claude/hooks/*.py
!.claude/rules/
.claude/rules/*
!.claude/rules/bridge-essential.md
!.claude/rules/*.md
!.claude/skills/
.claude/skills/*
!.claude/skills/*/
!.claude/skills/*/SKILL.md
!.claude/skills/*/references/
!.claude/skills/*/references/*.md
!.claude/skills/*/scripts/
!.claude/skills/*/scripts/*.py
!.claude/skills/*/helpers/
!.claude/skills/*/helpers/*.py
```

**Patch** (insert after the `.claude/skills/` block; keep section
ordering analogous):

```
!.claude/commands/
.claude/commands/*
!.claude/commands/registry.json
```

Pattern semantics:

- `!.claude/commands/` — negate the directory (re-include from the
  blanket `.claude/*` ignore one line earlier)
- `.claude/commands/*` — ignore directory contents by default
- `!.claude/commands/registry.json` — explicitly track the registry
  file

The 6 existing local-only `.md` files in `.claude/commands/` (per
architectural plan §6) remain ignored because no `*.md` negation is
added. This preserves the tracked-vs-local distinction.

### 2.2 Empty registry stub

**New file:** `.claude/commands/registry.json`.

```json
{
  "schema_version": 1,
  "commands": {}
}
```

Two-field structure (not just `{}`) so CS-2's registry-loader has a
predictable shape from day one. `schema_version` is the migration-
compat field; `commands` is the empty object that CS-3 will populate.

CS-2 will define and document the full schema. CS-1.5 just establishes
the file's existence and tracked status.

### 2.3 Regression test

**New file:** `tests/scripts/test_command_registry_tracking.py`.

```python
"""Release-gate test: the GT-KB command registry path must be tracked
in git, not gitignored.

Per the GT-KB command-surface architectural plan (GO'd at
bridge/gtkb-command-surface-004.md), the dispatcher hook (CS-2) reads
the command registry from .claude/commands/registry.json. The
.claude/* blanket ignore in .gitignore would normally hide that path
from fresh checkouts and adopter scaffolding. CS-1.5 patches the
ignore list to track the registry; this test ensures the patch
remains in effect.

A regression here means: a fresh clone or `gt project upgrade` adopter
would not receive the command registry. The dispatcher hook would
either fail to load or fall back to default behavior, breaking the
::cmd surface silently.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


REGISTRY_PATH = ".claude/commands/registry.json"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_registry_path_exists() -> None:
    """The registry file must exist in the working tree."""
    path = _project_root() / REGISTRY_PATH
    assert path.exists(), (
        f"Command registry not present at {REGISTRY_PATH}. "
        "CS-1.5 must commit an empty stub so CS-2's dispatcher has "
        "a known starting state."
    )


def test_registry_path_is_not_gitignored() -> None:
    """`git check-ignore` must report no ignore rule for the registry path.

    A non-zero exit from `git check-ignore` means the path is NOT
    ignored, which is what we want.
    """
    result = subprocess.run(
        ["git", "check-ignore", "-v", REGISTRY_PATH],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )
    assert result.returncode != 0, (
        f"Command registry at {REGISTRY_PATH} is gitignored: "
        f"{result.stdout.strip()}. "
        "Adopter scaffolding and fresh checkouts will not receive the "
        "registry. Patch .gitignore to add a negation rule for "
        "`.claude/commands/registry.json` (see "
        "bridge/gtkb-command-surface-003.md §3.2)."
    )


def test_registry_path_is_tracked_in_git() -> None:
    """`git ls-files` must include the registry path.

    Even if check-ignore reports no rule, the file must actually be
    tracked (added + committed) for fresh checkouts to receive it.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", REGISTRY_PATH],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )
    assert result.returncode == 0, (
        f"Command registry at {REGISTRY_PATH} is not tracked in git: "
        f"{result.stderr.strip()}. "
        "CS-1.5 must `git add` the registry stub after patching "
        ".gitignore."
    )


def test_registry_loose_md_files_remain_local() -> None:
    """Defense in depth: loose *.md files under .claude/commands/ must
    remain ignored (the tracked-vs-local distinction per architectural
    plan §6).

    If a future change broadens the negation pattern to `*.md`, the
    six existing local-only command files would become tracked,
    surprising both the developer and adopters. This test catches that.
    """
    test_path = ".claude/commands/__cs1-5-test-loose-md__.md"
    project_root = _project_root()
    full_path = project_root / test_path
    full_path.write_text("# CS-1.5 test artifact; safe to delete\n")
    try:
        result = subprocess.run(
            ["git", "check-ignore", test_path],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        assert result.returncode == 0, (
            f"Loose .md files under .claude/commands/ are no longer ignored. "
            "The tracked-vs-local distinction per architectural plan "
            "§6 has been broken. If this is intentional, update the "
            "architectural plan and CS-7 disposition; if not, narrow "
            "the negation pattern."
        )
    finally:
        full_path.unlink(missing_ok=True)
```

Four assertions:

1. The registry file exists in the working tree.
2. `git check-ignore` reports no ignore rule (the negation works).
3. `git ls-files` confirms the file is actually tracked (added +
   committed, not just present on disk).
4. Defense in depth: loose `*.md` files remain ignored, catching any
   future change that accidentally broadens the negation pattern.

### 2.4 Release-gate wiring

**Target file:** `scripts/release_candidate_gate.py`.

Add `tests/scripts/test_command_registry_tracking.py` to the existing
pytest invocation list. Pattern matches the S309 P1 ceiling-test
addition.

### 2.5 Files NOT modified

- `.claude/hooks/*` (no hook code in CS-1.5; CS-2 introduces the
  dispatcher)
- `.claude/settings.json` (no hook registration in CS-1.5)
- `.claude/skills/*` (no skill changes)
- `groundtruth.db` (no KB changes)
- The 6 existing `.claude/commands/*.md` files (remain local-only;
  CS-7 disposition is out of scope here)
- `CLAUDE.md` / `AGENTS.md` (no canonical-rule changes)

## 3. Owner-Decision Sequencing

No owner decisions block CS-1.5 implementation. The architectural-
plan GO at `bridge/gtkb-command-surface-004.md` already covers the
registry-tracking decision.

## 4. Implementation Order

Single wave (sub-items independent):

1. Patch `.gitignore` per §2.1.
2. Create `.claude/commands/registry.json` per §2.2.
3. Create `tests/scripts/test_command_registry_tracking.py` per §2.3.
4. Wire test into `scripts/release_candidate_gate.py` per §2.4.
5. Run targeted regression locally:
   ```
   pytest tests/scripts/test_command_registry_tracking.py -v
   ```
   All four assertions PASS.
6. Run full release-candidate pytest lane locally to confirm no
   broader regression.
7. Verify `git check-ignore -v .claude/commands/registry.json` returns
   non-zero exit (path is tracked).
8. Verify `git ls-files .claude/commands/registry.json` returns the
   file (path is tracked).
9. Commit with scoped message.
10. File post-implementation report citing commit hash + test results
    + the two manual `git` verifications.

## 5. Risk Analysis

### 5.1 Failure modes for the change itself

- **Negation pattern syntax error in `.gitignore` breaks all
  `.claude/` tracking.** Mitigated by: minimal, additive patch (three
  lines, all `!`/path/wildcard); existing pattern at `.claude/skills/`
  proves the syntax. The release-gate runs the test on every
  release-candidate build.
- **Registry stub committed without negation patch first.** Mitigated
  by: implementation order above puts the patch first; the test
  assertion for "is tracked in git" catches this if the order is
  violated.
- **Defense-in-depth loose-`*.md` test creates and deletes a file mid-
  test, racing with another test or developer.** Mitigated by: unique
  filename `__cs1-5-test-loose-md__.md` (double-underscore prefix);
  `try/finally` cleanup; missing_ok unlink.
- **Adopter scaffolding diverges.** This is the very risk CS-1.5
  closes. The patch lands in `agent-red` first; once verified, the
  upstream `groundtruth-kb` adopter scaffold gains the same patch in
  a future upstream-routing slice. Until that lands, adopters need
  to apply the same negation manually — flagged in §6 below.

### 5.2 Failure modes the change prevents

- **Silent registry invisibility on fresh checkouts.** Without
  CS-1.5, a fresh `git clone` would not contain the registry. CS-2's
  dispatcher would fall back to default behavior or fail to load.
- **Adopter project upgrade missing the registry.** Same class for
  `gt project upgrade` consumers.
- **Pattern broadening accidentally tracking the 6 local files.**
  The defense-in-depth test catches this.

### 5.3 Rollback

- `.gitignore` patch: revert the three added lines; the registry stub
  becomes ignored again.
- Registry stub: `git rm .claude/commands/registry.json`.
- Test: delete the test file; remove from release-gate.
- All steps mechanical and reversible. No persisted state to clean.

## 6. Codex Review Asks

1. Confirm the §2.1 negation pattern is correct and consistent with
   the existing `.claude/skills/` precedent. Flag any edge case.
2. Confirm the §2.2 registry stub structure (`schema_version: 1`,
   empty `commands: {}`) is the right starting shape for CS-2 to
   extend.
3. Confirm the §2.3 four assertions cover the tracking guarantee
   exhaustively. The defense-in-depth assertion is novel; flag any
   concern about the create-and-delete dance.
4. **Upstream-routing flag for §5.1**: agent-red lands CS-1.5 first,
   but the same patch belongs in the upstream `groundtruth-kb`
   adopter scaffold. Should CS-1.5 include filing the upstream patch
   as a follow-up bridge note, or is that a separate slice (call it
   CS-1.5-upstream)? This proposal flags it for follow-up; a separate
   slice is cleaner.
5. **GO / NO-GO** on Slice CS-1.5 implementation.

## 7. Decision Needed From Owner

None for CS-1.5 implementation.

## 8. Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | No secrets in registry stub or test; the registry contains command-routing metadata, never credentials | Source review | n/a |
| CQ-PATHS-001 | Yes | All paths derived from `Path(__file__).resolve().parents[2]`; relative path constants for `git` invocations; no hardcoded `E:\GT-KB\` | Source review | n/a |
| CQ-CONSTANTS-001 | Yes | `REGISTRY_PATH = ".claude/commands/registry.json"` is module-level with rationale comment citing the architectural plan | Source review | n/a |
| CQ-DOCS-001 | Yes | Module docstring explains why-registry-must-be-tracked with architectural-plan citation; each test docstring explains the specific failure mode | Source review | n/a |
| CQ-COMPLEXITY-001 | Yes | Each test ≤ 30 LOC; module ≤ 130 LOC including docstrings | Source review | n/a |
| CQ-TESTS-001 | Yes | The proposal IS the test addition; four assertions cover the tracking guarantee from four angles (existence, not-ignored, in-git-index, defense-in-depth) | Source review + release-gate inclusion | n/a |
| CQ-LOGGING-001 | Yes | Tests produce clear failure messages with remediation pointers (citing the architectural plan §3.2 for the patch); no swallowed exceptions; finally-cleanup defensive | Source review | n/a |
| CQ-SECURITY-001 | n/a | n/a | n/a | No auth/network/external-interface changes; only local file I/O via subprocess git invocations |
| CQ-VERIFICATION-001 | Yes | Level 1 (automated tests in §2.3); Level 2 (release-gate inclusion in §2.4); Level 3 (manual `git check-ignore` + `git ls-files` verifications in §4 step 7-8) end-to-end | §2.3 + §2.4 + §4 | n/a |

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:**
- `.gitignore` (three lines added per §2.1)
- `.claude/commands/registry.json` (new; empty stub per §2.2)
- `tests/scripts/test_command_registry_tracking.py` (new per §2.3)
- `scripts/release_candidate_gate.py` (one new test file in pytest list)

**Implementation NOT yet authorized** until Codex GO on this proposal.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
