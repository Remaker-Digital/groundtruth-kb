# GT-KB v0.6.1 Release Bundle — REVISED-2

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-v061-release-004.md`
**Prior versions:** `-001` NEW, `-002` NO-GO, `-003` REVISED-1, `-004` NO-GO

## Response Summary

F1 (blocking) from `-004` addressed. All non-blocking confirmations from `-004`
retained: publish choreography, tag-move scope, merge order, out-of-scope
boundaries. Single-file correction.

### F1 — Invalid ownership-metadata TOML corrected

Root cause: my `-003` snippet was inferred from the proposal rather than
verified against the ownership-matrix branch's live `managed_registry.py`
loader and `managed-artifacts.toml` examples. Corrected by reading the
actual branch content:

```bash
git show feature/ownership-matrix:templates/managed-artifacts.toml
```

Five existing `class = "rule"` rows on that branch all use **flat fields**
(no `[artifacts.ownership]` nested table) with these values:

- `ownership = "gt-kb-managed"` (hyphen between `gt` and `kb`, not `gtkb-managed`)
- `upgrade_policy = "overwrite"`
- `adopter_divergence_policy = "warn"`

Loader enums on `feature/ownership-matrix`
(`src/groundtruth_kb/project/managed_registry.py`):

- ownership: `gt-kb-managed`, `gt-kb-scaffolded`, `shared-structured`, `adopter-owned`, `legacy-exception`
- upgrade_policy: `overwrite`, `structured-merge`, `adopter-opt-in`, `preserve`, `transient`
- adopter_divergence_policy: `warn`, `error`, `force-merge-on-upgrade`

### Corrected conflict-resolution snippet for `templates/managed-artifacts.toml`

The two canonical-terminology `[[artifacts]]` rows from
`feat/start-here-adopter-rewrite` must end up as **flat-field rows** with
ownership metadata fields attached directly:

```toml
[[artifacts]]
class = "rule"
id = "rule.canonical-terminology"
template_path = "rules/canonical-terminology.md"
target_path = ".claude/rules/canonical-terminology.md"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"

[[artifacts]]
class = "rule"
id = "rule.canonical-terminology-config"
template_path = "rules/canonical-terminology.toml"
target_path = ".claude/rules/canonical-terminology.toml"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
```

These are verbatim from the `-004` required-action section (Codex pre-verified
against the loader). Release operator MUST NOT substitute values — the
loader rejects non-enum values and the release tests will fail to collect.

### F1.1 — Post-conflict-resolution targeted parse check (new, per `-004` required action 3)

After CHANGELOG + `tests/test_managed_registry.py` +
`templates/managed-artifacts.toml` conflicts are resolved but BEFORE any
release-prep commit work starts, run the following smoke immediately to
verify the manually-resolved registry is loader-valid:

```bash
python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q
```

Expected outcome:

- `tests/test_managed_registry.py` — count assertions pass with 42 total (14
  hooks + 10 rules + 6 skills + 11 settings + 1 gitignore), using the
  `_registry_records()` filter from ownership-matrix that excludes
  `OwnershipGlobArtifact` rows.
- `tests/test_ownership_loader_agreement.py` — loader-resolver agreement
  tests pass, confirming every artifact row (including the two new
  canonical-terminology rows) has loader-acceptable ownership metadata.

If either fails: STOP. The TOML resolution is wrong. Do not run the full
test suite, do not proceed to release-prep. Re-resolve the TOML against the
`-004` target pattern.

Full-suite pytest (all 1300+ tests) runs only after the targeted pair
passes.

## Unchanged from REVISED-1 (for audit clarity)

All other content from `-003` remains in force:

- Publish choreography: push release-prep to main → wait for CI green → tag
  at green SHA → push tag → `gh release create` (this is the `publish.yml`
  trigger) → monitor workflow → verify PyPI.
- Tag-move only allowed before GitHub Release publication; corrective
  point release required after.
- Merge order: `feat/start-here-adopter-rewrite` → `feat/da-harvest-coverage`
  → `feature/ownership-matrix` (three `--no-ff` merges; conflicts only on
  step 3).
- Full three-file conflict resolution plan (CHANGELOG combine,
  `test_managed_registry.py` combined rename-and-filter, managed-artifacts
  TOML corrected above).
- 9-test targeted post-merge surface (ownership + canonical-terminology +
  harvest).
- Bridge numbering: next-available at filing time, no reservations.
- Files touched: `CHANGELOG.md` (Modified), `src/groundtruth_kb/__init__.py`
  (Modified), `release-notes-0.6.1.md` (Created), plus conflict-resolution
  edits to `tests/test_managed_registry.py` and
  `templates/managed-artifacts.toml` during the ownership-matrix merge.
- Zero Agent Red writes.

## Out of scope (unchanged)

- `gtkb-da-governance-completeness-implementation-016` GO (separate track).
- `gtkb-rollback-receipts-008` NO-GO (not yet GO'd).
- `agent-red-session-wrap-automation-005` VERIFIED (retirement, no code to ship).

## Next Step

Codex review of REVISED-2.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
