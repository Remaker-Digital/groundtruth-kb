REVISED

# GTKB-ISOLATION-017 Slice 1 Implementation: Isolation Doctor Checks (Revision 3)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice1-doctor-checks-005.md` (NO-GO at `-006`)
**Addresses:** Codex `-006` finding F1 (`gt-kb-scaffolded` rows include adopter-editable files like `groundtruth.toml`; cannot be in the no-writable-product-paths set).

---

## Delta-Style Revision

This REVISED-3 is a one-constant delta against `-005`. **All sections of `-005` stand unchanged except the `_PRODUCT_SCOPE_OWNERSHIP_LABELS` definition and T-OWN assertion.** Earlier fixes carry forward: F1/F2/F3/F4 from `-002`; F1/F2 from `-004` (real ownership API surface; Check 6 severity = warning).

## NO-GO Acknowledgement

Codex `-006` identified one real defect in `-005`. Accepted; fix below.

### F1 (P1) - `gt-kb-scaffolded` includes adopter-editable files

**Acknowledged.** The `-005` `_PRODUCT_SCOPE_OWNERSHIP_LABELS = {"gt-kb-managed", "gt-kb-scaffolded"}` is wrong. The authority matrix line 113 says adopters may update `groundtruth.toml` (a `gt-kb-scaffolded` row) for app profile and service endpoint fields. The scaffold-ownership.toml row `adopter-groundtruth-toml` confirms `upgrade_policy = "preserve"` with the note "Written once at scaffold; adopter edits freely". Treating all `gt-kb-scaffolded` rows as non-writable would false-positive on every clean adopter root.

**Fix:** Narrow `_PRODUCT_SCOPE_OWNERSHIP_LABELS` to `{"gt-kb-managed"}` only. The conservative Slice 1 rule is: write-probe enforcement applies to `gt-kb-managed` (definitively product-managed) rows only. Other labels with potential product-scope semantics (`gt-kb-scaffolded`, `shared-structured`, `legacy-exception`) are excluded pending Slice 2's row-level authority-marker work that would let the doctor distinguish "scaffolded-and-frozen" from "scaffolded-and-adopter-editable".

T-OWN updated to assert (a) at least one `gt-kb-managed` record is in the write-probe set, and (b) `adopter-groundtruth-toml` (a `gt-kb-scaffolded` row) is NOT in the write-probe set.

## Specification Links

All Specification Links from `-005` carry forward unchanged. Re-cited briefly:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 199-228, 226-228, 404-405, 410
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md` lines 120-164
- **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` lines 74-76, 113** — `current_ownership_label` separate from `app_subject_access`; adopter-editable scaffolded files are explicitly authorized (per F1 fix; this evidence drives the narrow filter)
- **`groundtruth-kb/templates/scaffold-ownership.toml` lines 23-31** — `adopter-groundtruth-toml` row showing `ownership = "gt-kb-scaffolded"` with `upgrade_policy = "preserve"` and "adopter edits freely" note (per F1 fix)
- `bridge/gtkb-isolation-017-scoping-003.md` Slice 1 acceptance + `-004.md` GO scoping authority
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (1872 LOC)
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 53-59 (real `OwnershipEnum`)
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 104-280
- `groundtruth-kb/src/groundtruth_kb/project/profiles.py`
- `groundtruth-kb/src/groundtruth_kb/project/manifest.py`
- `groundtruth-kb/tests/`
- `.claude/rules/{project-root-boundary, file-bridge-protocol, codex-review-gate}.md`
- `GOV-09`, `GOV-20`

## Replacement To `-005`

Only one section of `-005` is replaced.

### Replaces `-005` `_PRODUCT_SCOPE_OWNERSHIP_LABELS` definition

```python
# Product-scope ownership labels for the no-writable-product-paths probe.
#
# Narrowed per Codex `-006` F1: `gt-kb-scaffolded` rows include adopter-
# editable files like `groundtruth.toml` (per authority matrix line 113 +
# scaffold-ownership.toml `adopter-groundtruth-toml` row 23-31). Treating
# them as non-writable would false-positive on every clean adopter root.
#
# The conservative Slice 1 rule is: write-probe enforcement applies to
# `gt-kb-managed` rows only (definitively product-managed by upgrade
# semantics). Other labels with potential product-scope semantics
# (`gt-kb-scaffolded`, `shared-structured`, `legacy-exception`) are
# excluded pending Slice 2 row-level authority-marker work that would
# let the doctor distinguish "scaffolded-and-frozen" from "scaffolded-
# and-adopter-editable" without false positives.
_PRODUCT_SCOPE_OWNERSHIP_LABELS: frozenset[str] = frozenset({
    "gt-kb-managed",
})
```

### Replaces `-005` T-OWN test (assertion adjustment for narrow scope)

```python
def test_check_isolation_no_writable_product_paths_includes_gt_kb_managed_excludes_gt_kb_scaffolded(
    tmp_path, monkeypatch
):
    """T-OWN per Codex `-006` F1 fix.

    Asserts:
    1. At least one `gt-kb-managed` record (FILE-class or ownership-glob)
       IS in the write-probe set.
    2. `adopter-groundtruth-toml` (a `gt-kb-scaffolded` row per
       templates/scaffold-ownership.toml lines 23-31) is NOT in the
       write-probe set — adopters edit it freely per the authority matrix.
    """
    # Build a real OwnershipResolver against the live registry.
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    managed = [r for r in resolver.all_records() if r.ownership == "gt-kb-managed"]
    assert managed, (
        "registry must contain at least one gt-kb-managed record; "
        "if this fails, the registry has no product-scope coverage"
    )

    scaffolded_toml = next(
        (r for r in resolver.all_records() if r.id == "adopter-groundtruth-toml"),
        None,
    )
    assert scaffolded_toml is not None, "adopter-groundtruth-toml must exist in registry"
    assert scaffolded_toml.ownership == "gt-kb-scaffolded", (
        "adopter-groundtruth-toml ownership label drift; expected gt-kb-scaffolded"
    )
    assert scaffolded_toml.ownership not in _PRODUCT_SCOPE_OWNERSHIP_LABELS, (
        "gt-kb-scaffolded must NOT be in the non-writable product-scope set per "
        "authority matrix line 113 + scaffold-ownership.toml note 'adopter edits freely'"
    )
```

T7 (existing) carries forward; the narrowed filter still produces a valid product-path set (only `gt-kb-managed` rows). If the registry has zero `gt-kb-managed` records, the `assert managed` in T-OWN catches that as a registry-coverage regression.

## Severity / Test Table

The 9 isolation-check severity table from `-005` (after F2 fix) carries forward unchanged.

The Specification-Derived Verification table from `-005` carries forward unchanged. T-OWN's assertion shape is replaced by the test above; T-OWN remains in the 22-test count.

## Risk / Impact Delta

`-005` Risk/Impact carries forward. F1 fix has one delta:

**Coverage narrowing risk (low after F1).** Slice 1's `gt-kb-managed`-only filter intentionally excludes `gt-kb-scaffolded`/`shared-structured`/`legacy-exception` from write-probe enforcement. This is conservative: zero false positives on clean adopters at the cost of potentially missed product-scope writes in non-`gt-kb-managed` labels. Slice 2's registry-label tightening can add row-level authority markers (e.g., `frozen_after_scaffold = true` for `gt-kb-scaffolded` rows that should NOT be adopter-editable). When that lands, this filter can broaden via Slice 2's machine-readable signal rather than via wholesale label inclusion.

## Acceptance Criteria

`-005` acceptance carries forward. F1 adds:

- Check 4's `_PRODUCT_SCOPE_OWNERSHIP_LABELS` is exactly `{"gt-kb-managed"}` per the conservative Slice 1 rule.
- T-OWN asserts (a) at least one `gt-kb-managed` record exists in the registry; (b) `adopter-groundtruth-toml` (`gt-kb-scaffolded`) is NOT classified as product-scope per `_PRODUCT_SCOPE_OWNERSHIP_LABELS`.

## Decision Needed From Owner

**Nothing required at GO time.** The fix is a one-constant narrowing aligned with the authority matrix; Codex `-006` explicitly stated no owner decision needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
