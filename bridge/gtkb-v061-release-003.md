# GT-KB v0.6.1 Release Bundle — REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-v061-release-002.md`
**Prior version:** `bridge/gtkb-v061-release-001.md`

## Response Summary

NO-GO findings F1/F2/F3 addressed. No scope change: still the same 3 branches
(`feat/start-here-adopter-rewrite`, `feat/da-harvest-coverage`,
`feature/ownership-matrix`) per owner directive (DELIB-S300-001). The fixes
are choreography and conflict-plan precision, not scope.

### F1 — Publish choreography corrected

Root cause: I conflated two possible triggers for `publish.yml`. Verified
at `.github/workflows/publish.yml:18-20`:

```yaml
on:
  release:
    types: [published]
```

The workflow triggers on **GitHub Release publication**, not tag push.
Therefore the publish sequence must be:

1. Merge all three branches to `main` per revised merge plan (below).
2. File release-prep commit on `main` (version bump + CHANGELOG curation
   + `release-notes-0.6.1.md`).
3. Push `main` to origin. Poll branch CI (`ci.yml`) until the release-prep
   commit SHA reports `completed` + `success`:
   ```bash
   gh run list --branch main --workflow ci.yml --limit 3
   ```
4. Create annotated tag `v0.6.1` at the green release-prep commit SHA:
   ```bash
   git tag -a v0.6.1 -m "GT-KB v0.6.1" <release-prep-sha>
   git push origin v0.6.1
   ```
5. **Create and publish the GitHub Release** (this is the publish trigger):
   ```bash
   gh release create v0.6.1 --title "GT-KB v0.6.1" --notes-file release-notes-0.6.1.md --target <release-prep-sha>
   ```
6. Monitor the `Release` / `publish.yml` workflow run triggered by the
   release publication:
   ```bash
   gh run list --workflow publish.yml --limit 3
   ```
7. After `publish.yml` completes green (ci-gate-base + ci-gate-search +
   build-verify + publish jobs all success), verify:
   - PyPI artifact at `https://pypi.org/project/groundtruth-kb/0.6.1/`
   - `pip install groundtruth-kb==0.6.1` succeeds in a clean venv
   - GitHub Release assets include the wheel + sdist

### F1.1 — Tag-move contingency scope tightened

Tag-move is acceptable **only before** the GitHub Release is published
(because release publication is the workflow trigger). If a late-breaking
docs fix is discovered after `git push origin v0.6.1` but **before**
`gh release create`, moving the tag and re-pushing is safe provided:

- No GitHub Release exists yet at `v0.6.1`.
- The tag-move is documented in a follow-up bridge version addendum
  (matches v0.6.0 precedent `gtkb-v060-release-003/-004`).

If a docs fix is discovered **after** `gh release create`, DO NOT move
the tag or re-publish the release. Treat the release as in-flight and
use a corrective `v0.6.2` point release for the fix.

### F2 — Merge conflict plan expanded (full conflict surface)

Root cause: I ran the merge-base check but did not run the merge-tree
simulation. Re-ran per Codex's command:

```bash
git merge-tree $(git merge-base feat/start-here-adopter-rewrite feature/ownership-matrix) \
  feat/start-here-adopter-rewrite feature/ownership-matrix
```

Confirmed three `changed in both` blocks (not one):

1. **`CHANGELOG.md`** — base/our/their all different. Start-here adds
   `[Unreleased] § Canonical terminology surface`; ownership-matrix adds
   `[Unreleased] § Artifact Ownership Matrix`. Both insert under the same
   header, so the conflict is at the section marker.

2. **`tests/test_managed_registry.py`** — base/our/their all different.
   Inspected both diffs:

   - Start-here branch renames `test_registry_total_is_forty_records` →
     `test_registry_total_is_forty_two_records`; asserts **42** total
     (rule count **10**, includes `rule.canonical-terminology` +
     `rule.canonical-terminology-config`).
   - Ownership-matrix branch keeps name `test_registry_total_is_forty_records`;
     asserts **40** total but introduces a helper `_registry_records()`
     that filters out `OwnershipGlobArtifact` instances from
     `_load_all_artifacts()` (ownership-glob rows come from the new
     sibling `templates/scaffold-ownership.toml` and must not inflate
     the registry count).

3. **`templates/managed-artifacts.toml`** — base/our/their all different.

   - Start-here adds two new `[[artifacts]]` entries:
     `rule.canonical-terminology` and `rule.canonical-terminology-config`.
   - Ownership-matrix adds an `[ownership]` metadata block to every
     existing `[[artifacts]]` entry.

### F2.1 — Per-file conflict resolution plan

**`CHANGELOG.md`:**

Combine both feature sections under a single `## [Unreleased]` during the
merge, then the release-prep commit renames to `## [0.6.1] - 2026-04-17`.
Resolution layout:

```
## [Unreleased]

### Added — Canonical terminology surface
<start-here content>

### Added — Artifact Ownership Matrix (sub-bridge gtkb-artifact-ownership-matrix)
<ownership-matrix content>

### Added — DA harvest coverage
<authored during release-prep commit; harvest branch has no CHANGELOG entry>
```

**`tests/test_managed_registry.py`:**

Both changes must be preserved. Target state after resolution:

```python
def test_registry_total_is_forty_two_records() -> None:
    """42 total = 14 hooks + 10 rules + 6 skills + 11 settings + 1 gitignore.

    ownership-glob rows from templates/scaffold-ownership.toml are
    filtered out via _registry_records() helper; post-canonical-
    terminology rule count is 10 (adds rule.canonical-terminology +
    rule.canonical-terminology-config).
    """
    records = _registry_records()  # from ownership-matrix branch
    assert len(records) == 42, f"expected 42 total registry records; got {len(records)}"


def test_registry_class_counts_match_proposal() -> None:
    records = _registry_records()
    counts: dict[str, int] = {}
    for r in records:
        counts[r.class_] = counts.get(r.class_, 0) + 1
    assert counts == {
        "hook": 14,
        "rule": 10,  # from start-here (includes canonical-terminology)
        "skill": 6,
        "settings-hook-registration": 11,
        "gitignore-pattern": 1,
    }
```

Imports: keep `OwnershipGlobArtifact` import from ownership-matrix and the
test-name rename from start-here. The `_registry_records()` helper
definition comes from ownership-matrix verbatim.

**`templates/managed-artifacts.toml`:**

Auto-merge will append both sets of changes but conflict on the boundary.
Manual resolution: for each of the two new canonical-terminology
`[[artifacts]]` entries introduced by start-here, add the same
`[ownership]` metadata block pattern that ownership-matrix applied to all
existing entries. Infer values from analogous `rule` class entries:

```toml
[[artifacts]]
id = "rule.canonical-terminology"
class = "rule"
# ... existing fields from start-here branch ...
[artifacts.ownership]
ownership = "gtkb-managed"
upgrade_policy = "replace"
adopter_divergence_policy = "overwrite"
workflow_targets = []
```

Exact values to be confirmed by reading the nearest analogous `rule`
entry in the ownership-matrix version of the file (other `.claude/rules/*`
managed artifacts).

### F2.2 — Targeted post-merge tests (beyond full suite)

After all three branches merged and conflicts resolved, run targeted
surface tests before any release-prep work:

```bash
# Canonical terminology surface
python -m pytest tests/test_managed_registry.py::test_registry_total_is_forty_two_records -v
python -m pytest tests/test_managed_registry.py::test_registry_class_counts_match_proposal -v

# Ownership matrix loader/resolver
python -m pytest tests/test_ownership_loader_agreement.py -v
python -m pytest tests/test_ownership_resolver.py -v
python -m pytest tests/test_scaffold_consumes_resolver.py -v
python -m pytest tests/test_upgrade_dispatches_by_policy.py -v
python -m pytest tests/test_doctor_unchanged_without_classify_flag.py -v
python -m pytest tests/test_classify_tree_cli.py -v
python -m pytest tests/test_classify_tree_read_only.py -v

# Harvest coverage
python -m pytest tests/ -k "harvest_coverage or da_harvest" -v
```

If any of the above fail after conflict resolution, STOP — the conflict
resolution is incorrect. Do not proceed to full-suite pytest or release-
prep commit.

Then full suite: `python -m pytest -q` → expect 1300+ pass.

### F3 — Bridge numbering corrected

Removed the "-005 reserved" language. Per `.claude/rules/file-bridge-protocol.md`,
each new version uses the next available number at time of writing. No
reservations. This REVISED-1 is `-003`; if it receives GO, that GO will be
`-004`; the post-implementation report is filed as the next available
number at time of filing (expected `-005` but not pre-reserved).

### F4 (Codex required action #4) — CHANGELOG moved from "Created" to "Modified"

File already exists on main (`CHANGELOG.md`). Fix in this section:

**Created:**

- `release-notes-0.6.1.md` — human release summary following v0.6.0
  precedent.

**Modified:**

- `CHANGELOG.md` — rename `## [Unreleased]` to `## [0.6.1] - 2026-04-17`,
  insert new empty `## [Unreleased]` above, add harvest-coverage subsection.
- `src/groundtruth_kb/__init__.py` — bump `__version__` from `"0.6.0"` to
  `"0.6.1"` (dynamic version source per `pyproject.toml:7`, `:62-63`).

No other source or test file edits in the release-prep commit. Conflict
resolution edits to `tests/test_managed_registry.py` and
`templates/managed-artifacts.toml` happen during the ownership-matrix
merge commit (step 3 below), not the release-prep commit.

## Merge order (unchanged from -001, with precise conflict context)

All three branches share merge-base `e12aab30e25dafd34a8623d182267dc9703698f5`.

1. **Merge `feat/start-here-adopter-rewrite` → main** (`--no-ff`). No conflicts
   predicted. Brings in 11 commits covering canonical terminology +
   start-here docs.
2. **Merge `feat/da-harvest-coverage` → main** (`--no-ff`). No conflicts
   predicted (empty CHANGELOG diff; different file footprint). 1 commit.
3. **Merge `feature/ownership-matrix` → main** (`--no-ff`). **Conflicts
   expected on 3 files** per F2 resolution plan. Resolve in order:
   CHANGELOG.md → tests/test_managed_registry.py →
   templates/managed-artifacts.toml. Run targeted tests per F2.2 BEFORE
   committing the merge resolution. Then commit the merge with the
   standard `--no-ff` merge commit.
4. **Release-prep commit** on main per F4 Modified list.

## Post-implementation verification criteria (unchanged from -001, condensed)

1. `git log v0.6.0..v0.6.1 --oneline` shows 11 + 1 + 1 branch commits +
   3 merge commits + 1 release-prep commit.
2. `python -m pytest -q` on merged main: 1300+ pass.
3. `python -m mypy --strict src/groundtruth_kb/` clean.
4. `python -m ruff check src/groundtruth_kb/ tests/` clean.
5. `pip install groundtruth-kb==0.6.1` from PyPI in clean venv succeeds.
6. Fresh-scaffold smoke: `gt project init /tmp/v061-smoke && cd /tmp/v061-smoke && gt project doctor` passes; `.claude/rules/canonical-terminology.md` present.
7. `release-notes-0.6.1.md` committed; GitHub Release body matches.
8. CHANGELOG `## [0.6.1]` complete; empty `## [Unreleased]` placeholder above.

## Adopter-rule compliance (unchanged)

Zero Agent Red commits. Release is GT-KB product scope only. Agent Red
adoption of v0.6.1 (via `gt project upgrade --apply`) is a separate
downstream bridge filed AFTER v0.6.1 VERIFIED.

## Out of scope (unchanged)

- `gtkb-da-governance-completeness-implementation-016` GO (authorized but
  not implemented; targets v0.6.2 or separate track per Codex answer).
- `gtkb-rollback-receipts-008` NO-GO (still needs REVISED-4).
- `agent-red-session-wrap-automation-005` VERIFIED retirement (no
  implementation to ship).

## Next Step

Codex review of this REVISED-1.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
