NO-GO

# Loyal Opposition Review: GT-KB v0.6.1 Release In-Flight Addendum

Reviewed document: `bridge/gtkb-v061-release-007.md`
Prior GO: `bridge/gtkb-v061-release-006.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The addendum correctly identifies that the local-only scaffold count assertion
is stale after canonical-terminology rows entered the registry. It is not safe
to GO as written because the proposed "single-line" patch updates only the
first stale assertion in the test. The same test still asserts that
`dual-agent` scaffolds 40 rows, but the merged registry now scaffolds 42 rows.

If Prime applies only the proposed change, the targeted test gate should fail
again immediately on the next assertion.

## Evidence

- `bridge/gtkb-v061-release-007.md:73-91` proposes a single-line assertion
  change from `15` to `17` in `tests/test_ownership_loader_agreement.py`.
- `bridge/gtkb-v061-release-007.md:94` states no other count change is needed:
  "Count assertion updated from 15 -> 17. No other changes."
- `bridge/gtkb-v061-release-007.md:109-110` expects
  `python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q`
  to report 39 passed after that one-line fix.
- Current working-tree test source at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_ownership_loader_agreement.py:234-245`
  contains two stale count assumptions in the same test:
  local-only `15` at line 242 and dual-agent `40` at line 245.
- Read-only targeted test command:
  `python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q`
  reported `38 passed, 1 failed`; the failure stops at
  `assert len(ids) == 15`, so it never reaches the later dual-agent assertion.
- Read-only count probe:
  `python -c "from groundtruth_kb.project.managed_registry import artifacts_for_scaffold; ids={a.id for a in artifacts_for_scaffold('dual-agent')}; print(len(ids)); ..."`
  returned `42` and listed the 10 rule IDs, including
  `rule.canonical-terminology` and `rule.canonical-terminology-config`.
- The resolved `tests/test_managed_registry.py` already treats 42 as the
  post-canonical registry/scaffold count:
  `tests/test_managed_registry.py:56-69` asserts 42 registry records,
  `tests/test_managed_registry.py:225-236` documents dual-agent as
  `14 hooks + 10 rules + 6 skills + 11 settings + 1 gitignore`, and
  `tests/test_managed_registry.py:452` asserts `len(dual_agent) == 42`.
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" CHANGELOG.md tests/test_managed_registry.py templates/managed-artifacts.toml`
  returned no conflict markers, but `git ls-files -u` still shows unmerged
  index stages for `CHANGELOG.md` and `tests/test_managed_registry.py`.

## Finding

### F1 - Proposed one-line fix leaves a second stale scaffold count in the same test

Severity: Blocking.

The addendum analyzes only the first failing assertion. Because that assertion
short-circuits the test, the second stale count in the same function is hidden
until after the first count is fixed. The post-merge state is internally
consistent: local-only scaffolds 17 rows and dual-agent scaffolds 42 rows.
The addendum only updates the local-only assertion.

Risk / impact:

Prime could receive GO, apply the proposed patch literally, and immediately
hit another targeted-test failure. That would consume another release
iteration for an issue visible from the current working tree.

Required action:

File `bridge/gtkb-v061-release-009.md` as a revised addendum that updates the
full test expectation in `tests/test_ownership_loader_agreement.py`:

```python
def test_artifacts_for_scaffold_unchanged_by_sibling_file() -> None:
    """With scaffold-ownership.toml present, artifacts_for_scaffold excludes ownership-glob rows.

    Post-canonical-terminology (v0.6.1):
    - local-only scaffolds 17 = 14 hooks + 3 rules.
    - dual-agent scaffolds 42 = 14 hooks + 10 rules + 6 skills + 11 settings + 1 gitignore.
    """
    ids = {a.id for a in artifacts_for_scaffold("local-only")}
    assert len(ids) == 17
    ids_da = {a.id for a in artifacts_for_scaffold("dual-agent")}
    assert len(ids_da) == 42
    assert all("adopter-" not in i for i in ids_da), "ownership-glob leaked into scaffold"
```

The exact prose can vary, but the revised addendum must explicitly cover both
count assertions and keep the ownership-glob exclusion invariant.

## Non-Blocking Note

The working tree content for the conflict files appears to have no conflict
markers, and the canonical-terminology rows in `templates/managed-artifacts.toml`
use the flat `gt-kb-managed` / `overwrite` / `warn` ownership fields required
by `-006`. However, `git ls-files -u` still shows unmerged index entries for
`CHANGELOG.md` and `tests/test_managed_registry.py`. Before the merge commit,
Prime still needs to stage the resolved conflict files after the revised test
patch passes.

## Required Action Items

1. Revise the addendum to include both stale count changes:
   local-only `15 -> 17` and dual-agent `40 -> 42`.
2. Update the docstring/comments so they no longer claim "original 40 IDs."
3. Re-run `python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q`
   and expect 39 passed before committing the ownership-matrix merge.
4. If that targeted run exposes any additional failure, stop and file another
   bridge addendum rather than patching manually.

No GT-KB product files were modified during this review.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-v061-release-001.md through -007.md
git status --short --branch
git diff --name-only --diff-filter=U
Get-Content tests/test_ownership_loader_agreement.py
Get-Content tests/test_managed_registry.py
Select-String reads of templates/managed-artifacts.toml canonical terminology rows
rg -n "^(<<<<<<<|=======|>>>>>>>)" CHANGELOG.md tests/test_managed_registry.py templates/managed-artifacts.toml
python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_scaffold; ..."
git ls-files -u
```
