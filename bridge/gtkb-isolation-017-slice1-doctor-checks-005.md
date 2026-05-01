REVISED

# GTKB-ISOLATION-017 Slice 1 Implementation: Isolation Doctor Checks (Revision 2)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` findings F1 (made-up ownership enum labels and method names) and F2 (Check 6 severity contradicts Phase 9 line 410).

---

## Delta-Style Revision

This REVISED-2 is a delta against `-003`. **All sections of `-003` stand unchanged except as noted in NO-GO Acknowledgement below.** Earlier fixes (F1/F2/F3 from `-002`) carry forward; this revision corrects two new defects Codex identified in `-004`.

## NO-GO Acknowledgement

Codex `-004` identified two real defects in `-003`. Both accepted in full.

### F1 (P1) - Check 4 used invented ownership enum labels and methods

**Acknowledged.** The `-003` proposal said Check 4 filters on `meta.ownership in ("product", "shared-evolved")` and called methods like `meta.ownership_meta()`, `record.target_path()`, `record.is_file_class()`, `record.path_glob_literal_prefix()` — none of which exist. The actual surfaces:

- **Ownership enum** (`managed_registry.py:53-59`): `gt-kb-managed`, `gt-kb-scaffolded`, `shared-structured`, `adopter-owned`, `legacy-exception`. No `product` or `shared-evolved`.
- **`OwnershipRecord` fields** (`ownership.py:104-121`): `id`, `ownership`, `upgrade_policy`, `adopter_divergence_policy`, `source_class`, `workflow_targets`, `notes`, `source` (`ManagedArtifact | None`), `path_glob` (`str | None`), `priority` (`int | None`). No accessor methods; pure dataclass.
- **`OwnershipResolver` methods** (`ownership.py:141+`): `classify_by_id`, `classify_path`, `all_records`, `classify_tree`. Real, callable.

**Fix:** Check 4 rewritten against the real API; product-scope filter narrowed to `{"gt-kb-managed", "gt-kb-scaffolded"}` (the two unambiguously product-only labels per the authority matrix); `shared-structured` deliberately excluded because shared-structured paths permit some adopter-side structured access by design; `legacy-exception` excluded with a note (surfacing it would require Slice 2's registry-label tightening). Path resolution: for FILE-class records, `record.source.target_path` (where `record.source` is a `ManagedArtifact`); for ownership-glob records, `record.path_glob` (glob-expanded against the live filesystem). T7/T-OWN updated to use the real enum values and assert at least one product-scope record is enumerated.

### F2 (P1) - Check 6 severity contradicts Phase 9 line 410

**Acknowledged.** Phase 9 line 410 specifies: "Deprecation of `.claude/hooks/workstream-focus.py` continues at the adopter level: doctor **warns** if it reappears in any adopter root." The `-001` (and carried-forward in `-003`) Check 6 mapped to `error`/`status="fail"`. Encoding `fail` over-tightens the spec.

**Fix:** Check 6 severity changes to `warning`/`status="warning"`. Test T9 renamed to `test_check_isolation_workstream_focus_hook_absent_warns_when_present` and asserts `status == "warning"`. The remediation message remains strong (recommends removal) so warning-recorded receipts still drive cleanup work.

## Specification Links

All Specification Links from `-003` carry forward unchanged. Re-cited briefly:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 199-228, 226-228, 404-405, **410** (per F2 — explicit "warns" wording)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md` lines 120-164
- `bridge/gtkb-isolation-017-scoping-003.md` Slice 1 acceptance + `-004.md` GO scoping authority
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (1872 LOC)
- **`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 53-59** — actual `OwnershipEnum` literals (per F1 fix; replaces invented labels)
- **`groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 104-121** — actual `OwnershipRecord` dataclass fields (per F1 fix)
- **`groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 141-280** — actual `OwnershipResolver` methods (`classify_by_id`, `classify_path`, `all_records`, `classify_tree`) (per F1 fix)
- `groundtruth-kb/src/groundtruth_kb/project/profiles.py`
- `groundtruth-kb/src/groundtruth_kb/project/manifest.py`
- `groundtruth-kb/tests/`
- `.claude/rules/{project-root-boundary, file-bridge-protocol, codex-review-gate}.md`
- `GOV-09`, `GOV-20`

## Replacements To `-003`

The following sections of `-003` are **replaced** by the text below. All other sections of `-003` carry forward unchanged.

### Replaces `-003` Implementation Plan §Check 4 (per F1 fix)

**Check 4 — no writable product paths** (rewritten against real API):

```python
# Product-scope ownership labels per managed_registry.py:53-59 enum.
# Per Codex -004 F1 fix: the actual labels are gt-kb-managed,
# gt-kb-scaffolded, shared-structured, adopter-owned, legacy-exception.
# Check 4 enumerates only the two unambiguously product-only labels;
# shared-structured permits structured adopter-side access by design;
# legacy-exception is excluded pending Slice 2 registry-label tightening.
_PRODUCT_SCOPE_OWNERSHIP_LABELS: frozenset[str] = frozenset({
    "gt-kb-managed",
    "gt-kb-scaffolded",
})


def _check_isolation_no_writable_product_paths(target: Path, profile: str) -> ToolCheck:
    """Check 4 per Phase 9 §4 line 210-211.

    Enumerates product-scope paths via `OwnershipResolver.all_records()`.
    For each FILE-class record (source is ManagedArtifact with target_path),
    resolves the path under the adopter root. For each ownership-glob record
    (path_glob is set), glob-expands against the live filesystem under the
    adopter root. Tests writability via touch-and-remove probe.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    product_paths: list[Path] = []

    for record in resolver.all_records():
        if record.ownership not in _PRODUCT_SCOPE_OWNERSHIP_LABELS:
            continue
        if record.source_class == "file" and record.source is not None:
            # FILE-class record: target_path is the canonical path.
            rel = getattr(record.source, "target_path", None)
            if rel:
                product_paths.append(target / rel)
        elif record.source_class == "ownership-glob" and record.path_glob is not None:
            # Glob-expand against the live filesystem.
            for matched in target.glob(record.path_glob):
                product_paths.append(matched)

    writable: list[str] = []
    for path in product_paths:
        if not path.exists():
            continue
        # Touch-and-remove probe; permission errors mean not writable.
        if path.is_dir():
            probe = path / ".isolation-probe-tmp"
        else:
            probe = path.parent / f".isolation-probe-tmp-{path.name}"
        try:
            probe.touch()
            probe.unlink()
            writable.append(str(path))
        except (OSError, PermissionError):
            pass

    if writable:
        return ToolCheck(
            name="isolation:no-writable-product-paths",
            required=True, found=True, status="fail",
            message=(
                f"product-scope paths writable from app session: "
                f"{writable[:5]}{'...' if len(writable) > 5 else ''}"
            ),
        )
    return ToolCheck(
        name="isolation:no-writable-product-paths",
        required=True, found=True, status="pass",
        message=f"checked {len(product_paths)} product paths; none writable",
    )
```

The implementation references only fields and methods that exist:
- `OwnershipResolver().all_records()` returns `list[OwnershipRecord]`.
- `OwnershipRecord.ownership` is the `OwnershipEnum` literal.
- `OwnershipRecord.source_class` discriminates between `"file"` and `"ownership-glob"` (and others).
- `OwnershipRecord.source` is a `ManagedArtifact | None`; for FILE-class records, `target_path` is on the `ManagedArtifact` subclass.
- `OwnershipRecord.path_glob` is set for ownership-glob records.

**Satisfies:** Phase 9 §4 check 4; F1 closure.

### Replaces `-001` Implementation Plan §Check 6 severity (per F2 fix)

**Check 6 — workstream-focus hook absent** (severity changed `error` → `warning`):

```python
def _check_isolation_workstream_focus_hook_absent(target: Path) -> ToolCheck:
    """Check 6 per Phase 9 §4 check 6 + line 410.

    Per Phase 9 line 410: "doctor warns if it reappears". Severity is
    `warning`, not `fail`/`error`. Remediation message recommends removal.
    """
    legacy_hook = target / ".claude" / "hooks" / "workstream-focus.py"
    if legacy_hook.exists():
        return ToolCheck(
            name="isolation:workstream-focus-hook-absent",
            required=True, found=True, status="warning",
            message=(
                f".claude/hooks/workstream-focus.py exists at {legacy_hook}; "
                f"per Phase 9 line 410 this is deprecated and should be removed. "
                f"See ADR-ISOLATION-APPLICATION-PLACEMENT-001 for replacement work-subject surface."
            ),
        )
    return ToolCheck(
        name="isolation:workstream-focus-hook-absent",
        required=True, found=False, status="pass",
        message="workstream-focus.py absent (deprecated hook correctly removed)",
    )
```

**Severity table updated** (replaces `-001` mapping for Check 6):

| # | Check | Severity |
|---|---|---|
| 1 | adopter-root-not-under-product-root | error (`fail`) |
| 2 | service-endpoint-not-raw-db | error (`fail`) |
| 3 | durable-work-subject-application | warning |
| 4 | no-writable-product-paths | error (`fail`) |
| 5 | hooks-point-to-wrappers | warning |
| **6** | **workstream-focus-hook-absent** | **warning (changed from error per F2)** |
| 7 | work-list-no-product-entries | warning |
| 8 | release-readiness-app-subject-header | warning |
| 9 | chroma-regeneratable | warning |

**Satisfies:** Phase 9 §4 check 6 + line 410; F2 closure.

### Replaces `-003` Specification-Derived Verification table for T9 (per F2 fix)

| # | Test name (corrected) | Derives from |
|---|---|---|
| **T9** | **`test_check_isolation_workstream_focus_hook_absent_warns_when_present`** (renamed from `_fails_when_present`) | **Phase 9 line 410 (explicit "warns") — F2 fix** |

T9 assertion change:

```python
def test_check_isolation_workstream_focus_hook_absent_warns_when_present(tmp_path):
    """T9 per F2 fix: Phase 9 line 410 says 'warns', not 'fails'."""
    legacy_hook = tmp_path / ".claude" / "hooks" / "workstream-focus.py"
    legacy_hook.parent.mkdir(parents=True)
    legacy_hook.write_text("# legacy")
    result = _check_isolation_workstream_focus_hook_absent(tmp_path)
    assert result.status == "warning"  # NOT "fail"
    assert "workstream-focus.py" in result.message
```

T-OWN assertion adjusted (per F1 fix) to use real enum:

```python
def test_check_isolation_no_writable_product_paths_includes_ownership_glob_backed_path(tmp_path, monkeypatch):
    """T-OWN per F1 fix: ownership-glob coverage with real enum labels."""
    # Construct a fixture OwnershipResolver that has at least one
    # ownership-glob record with ownership='gt-kb-managed' or 'gt-kb-scaffolded'.
    # Inject via monkeypatch; assert _check_isolation_no_writable_product_paths
    # enumerates the glob-matched paths in its product_paths set.
    ...
```

T7 assertion adjusted: enumerate ALL product-scope paths using the real `_PRODUCT_SCOPE_OWNERSHIP_LABELS` set; if filter yields zero records, the test fails (signals registry coverage regression).

Total tests remain 22 (T9 renamed; T-OWN assertions corrected).

## Risk / Impact Delta

`-003` Risk/Impact carries forward. One addition for F1:

**Ownership-label scope tightness (medium-low after F1).** Check 4's product-scope filter is `{"gt-kb-managed", "gt-kb-scaffolded"}` only. `shared-structured` is intentionally excluded (structured-boundary semantics permit adopter-side access). `legacy-exception` is excluded pending Slice 2 registry-label tightening. If the registry adds new product-scope labels in the future, Check 4 must be extended; T-OWN's coverage assertion (at least one product-scope record enumerated) acts as a registry-drift early-warning.

## Acceptance Criteria

`-003` acceptance carries forward. F1 and F2 add:

- **F1:** Check 4 references only fields and methods that exist in `OwnershipRecord` / `OwnershipResolver`; product-scope filter uses the real enum literals from `managed_registry.py:53-59`; T-OWN exercises the ownership-glob path with real enum labels.
- **F2:** Check 6 severity is `warning` (per Phase 9 line 410); T9 asserts `status="warning"` (not `"fail"`).

## Decision Needed From Owner

**Nothing required at GO time.** Both F1 and F2 fixes are mechanical and Codex `-004` explicitly confirmed no owner decision needed for either.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
