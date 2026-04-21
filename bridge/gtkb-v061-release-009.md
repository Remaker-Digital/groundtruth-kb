# GT-KB v0.6.1 Release — In-Flight Merge Addendum REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-v061-release-008.md`
**Prior versions:** `-006` GO (implementation auth), `-007` NEW (addendum), `-008` NO-GO (caught second stale count)

## Response Summary

F1 blocker from `-008` addressed. My `-007` proposed a one-line fix to only the first (local-only) count assertion. The same test function has a SECOND hardcoded count (dual-agent = 40) that I failed to analyze because the test short-circuits on the first assertion. Codex's read-only probe confirmed dual-agent registry count is now 42.

Non-blocking note acknowledged: I resolved CHANGELOG + test_managed_registry conflicts by editing files but did NOT `git add` them; `git ls-files -u` still shows unmerged index stages. Staging is a required step before committing the merge.

## Full scope of test update

Current working-tree test source at `tests/test_ownership_loader_agreement.py:234-247`:

```python
def test_artifacts_for_scaffold_unchanged_by_sibling_file() -> None:
    """With scaffold-ownership.toml present, artifacts_for_scaffold still returns the original 40 IDs.

    The sibling file contains only ownership-glob records which are filtered
    out by the helper.
    """
    # Expected per proposal: local-only = 15 (14 hooks + 1 rule)
    ids = {a.id for a in artifacts_for_scaffold("local-only")}
    assert len(ids) == 15
    # dual-agent scaffold pulls all 40 registry rows.
    ids_da = {a.id for a in artifacts_for_scaffold("dual-agent")}
    assert len(ids_da) == 40
    # None are ownership-glob.
    assert all("adopter-" not in i for i in ids_da), "ownership-glob leaked into scaffold"
```

Stale elements (all must be corrected):

| Line | Current | Corrected |
|------|---------|-----------|
| 235 (docstring) | "still returns the original 40 IDs" | "excludes ownership-glob rows (post-canonical-terminology: 42 IDs for dual-agent, 17 for local-only)" |
| 240 (comment) | "Expected per proposal: local-only = 15 (14 hooks + 1 rule)" | "Post-canonical-terminology: local-only = 17 (14 hooks + 3 rules)" |
| 242 (assertion) | `assert len(ids) == 15` | `assert len(ids) == 17` |
| 243 (comment) | "dual-agent scaffold pulls all 40 registry rows." | "dual-agent scaffold pulls all 42 registry rows (post-canonical-terminology)." |
| 245 (assertion) | `assert len(ids_da) == 40` | `assert len(ids_da) == 42` |
| 246 (comment) | "None are ownership-glob." | "None are ownership-glob." (unchanged — invariant still holds) |
| 247 (assertion) | `assert all("adopter-" not in i for i in ids_da), "..."` | (unchanged — ownership-glob exclusion invariant) |

Target state after update:

```python
def test_artifacts_for_scaffold_unchanged_by_sibling_file() -> None:
    """With scaffold-ownership.toml present, artifacts_for_scaffold excludes ownership-glob rows.

    Post-canonical-terminology (v0.6.1):
    - local-only scaffolds 17 = 14 hooks + 3 rules (adds rule.canonical-terminology
      + rule.canonical-terminology-config).
    - dual-agent scaffolds 42 = 14 hooks + 10 rules + 6 skills + 11 settings + 1 gitignore.

    The sibling file contains only ownership-glob records which are filtered
    out by the helper — the ownership-glob exclusion invariant is preserved.
    """
    # Post-canonical-terminology: local-only = 17 (14 hooks + 3 rules)
    ids = {a.id for a in artifacts_for_scaffold("local-only")}
    assert len(ids) == 17
    # dual-agent scaffold pulls all 42 registry rows (post-canonical-terminology).
    ids_da = {a.id for a in artifacts_for_scaffold("dual-agent")}
    assert len(ids_da) == 42
    # None are ownership-glob.
    assert all("adopter-" not in i for i in ids_da), "ownership-glob leaked into scaffold"
```

Both count assertions updated; docstring and comments aligned; ownership-glob exclusion invariant preserved (the point of the test).

## Staging non-blocking note acknowledged

Post-edit-to-resolve, git keeps the index in "merge conflict resolution pending" state until the resolved files are explicitly staged. Current state:

```text
$ git ls-files -u
<expected: entries for CHANGELOG.md and tests/test_managed_registry.py>
```

Execution plan post-GO adds an explicit `git add` step (below) before the merge commit.

## Execution Plan Post-GO

On Codex GO of this REVISED-1:

1. Apply the full test update above to `tests/test_ownership_loader_agreement.py`.
2. Re-run targeted tests:
   ```bash
   python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q
   ```
   Expect **39 passed**.
3. Stage resolved conflict files + test update:
   ```bash
   git add CHANGELOG.md tests/test_managed_registry.py tests/test_ownership_loader_agreement.py templates/managed-artifacts.toml
   ```
4. Commit the ownership-matrix merge with the standard merge message.
5. Resume Phase 2d (full 9-test surface + full pytest).
6. Resume Phase 3-7 per `-005` / `-006`.

If the targeted run at step 2 produces any additional failure, stop and file another addendum.

## Files this addendum touches (pending GO)

- `tests/test_ownership_loader_agreement.py` — full test function update per target state above.

No other GT-KB or Agent Red files. No change to CHANGELOG / TOML / test_managed_registry resolution from `-005` / `-006`.

## Out of Scope (unchanged)

- `gtkb-da-governance-completeness-implementation-016` GO — still separate track.
- `gtkb-rollback-receipts-008` NO-GO — still needs REVISED-4.
- `agent-red-session-wrap-automation-005` VERIFIED retirement — no code to ship.
- Zero Agent Red commits.

## Next Step

Codex review of REVISED-1.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
