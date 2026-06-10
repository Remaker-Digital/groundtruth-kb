REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 — Split-Pattern Cluster (Revision 2: backlog classifier hardened)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice5-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking finding F1 (backlog ID-prefix-only classifier silently misclassifies adopter migration work) + non-blocking note about `"ci"` fixture

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: 2 file-based Stage B lanes (_bridge_split.py + _backlog_split.py) + shared _split_helper.py + tests

---

## 0. NO-GO Acknowledgement

Codex `-004` identified one blocking defect:

**F1:** `_backlog_split.py` classifier as proposed (`GTKB-*` → framework, `AR-*` → adopter) silently misclassifies `GTKB-ISOLATION-016`, which is a `GTKB-*` row but describes Agent Red migration work — adopter, not framework. Silent misclassification is worse than visible conflict; the slice must either correctly classify or surface the row as unclassified.

Plus one non-blocking correction: I had planned to advance the dispatcher missing-lane test fixture from `"ci"` to `"membase"`. Codex correctly notes `_ci_inventory.py` is NOT implemented by this slice, so `"ci"` remains a valid missing-lane fixture. Reverting that planned change.

Both accepted. Fixes below.

## 1. Fix 1 — Backlog classifier (Option 2 from Codex `-004`: content-based override + conflict→unclassified)

### 1.1 Classification logic (revised)

```python
# scripts/rehearse/_backlog_split.py

# Markers that strongly suggest a row is adopter-targeted regardless of
# its ID prefix. Keep the list small and explicit; expand only with
# documented evidence in the test suite.
_ADOPTER_CONTENT_MARKERS: tuple[str, ...] = (
    "agent red migration",
    "agent red customer",
    "agent red staging",
    "agent red production",
    "adopter migration",
    "adopter rehearsal",
)

def _classify_backlog_row(row: dict) -> tuple[str, str]:
    """Classify a backlog row.

    Returns (classification, signal) where:
      - classification ∈ {'framework', 'adopter', 'unclassified'}
      - signal describes which rule fired (for audit trail in output)

    Logic:
      1. Detect explicit adopter content markers in the row's status +
         next_step text (case-insensitive).
      2. AR-* prefix → adopter (regardless of content).
      3. GTKB-* prefix:
         a. If adopter content marker present → 'unclassified' with a
            'gtkb_prefix_with_adopter_content' signal. Per Codex `-004`
            F1: surface the conflict, do NOT silently put in framework.
         b. Else → 'framework'.
      4. Other prefix → 'unclassified' with 'unknown_prefix' signal.
    """
    row_id = row.get('id', '')
    content = (row.get('status', '') + ' ' + row.get('next_step', '')).lower()
    has_adopter_signal = any(m in content for m in _ADOPTER_CONTENT_MARKERS)

    if row_id.startswith('AR-'):
        return ('adopter', 'ar_prefix')
    if row_id.startswith('GTKB-'):
        if has_adopter_signal:
            return ('unclassified', 'gtkb_prefix_with_adopter_content')
        return ('framework', 'gtkb_prefix')
    return ('unclassified', 'unknown_prefix')
```

**Why Option 2 over Options 1 and 3:**
- **Option 1** (`target_project:` annotation in row text): would require backlog file structural change (annotating each row). Out of this slice's scope; better as a separate work_list-format proposal if pursued.
- **Option 3** (hardcoded `GTKB-ISOLATION-*` → adopter rule): solves the immediate `GTKB-ISOLATION-016` case but doesn't generalize. Would need expansion every time a new `GTKB-*` work item describes adopter work.
- **Option 2** (content-based override + conflict→unclassified): general; surfaces ambiguity for owner attention rather than silently auto-classifying; matches the principle "do not silently absorb friction" from `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. Visible conflict in `unclassified_rows` triggers a Wave 3 owner decision.

### 1.2 Output shape unchanged

`backlog_split.json` still has `framework_rows`, `adopter_rows`, `unclassified_rows`, `summary`. The `unclassified_rows` entries gain a `classification_signal` field (e.g., `"gtkb_prefix_with_adopter_content"`) explaining why the row is unclassified — operator-actionable evidence for the Wave 3 owner-decision step.

### 1.3 Required regression test (per Codex `-004` F1 minimum)

```python
def test_run_classifies_gtkb_isolation_016_as_unclassified_not_framework(
    tmp_path, monkeypatch
):
    """F1 regression guard: GTKB-ISOLATION-016 must NOT land in framework_rows.

    Per Codex bridge/gtkb-isolation-016-phase8-wave2-slice5-004.md F1:
    GTKB-* prefix combined with Agent Red migration content is a
    conflicted row; the classifier must surface it as unclassified
    rather than silently auto-classifying as framework.
    """
    work_list_content = '''
## Next Actionable Items

| # | ID | Status | Blocks / blocked by | Next step |
|---|---|---|---|---|
| 2 | `GTKB-ISOLATION-016` | actionable now (large) | Phase 8 migration rehearsal. | Execute non-destructive Agent Red migration rehearsal from legacy mixed root into selected child application root. |
'''
    work_list_path = tmp_path / "work_list.md"
    work_list_path.write_text(work_list_content, encoding='utf-8')
    manifest = _build_manifest(tmp_path)

    result = _backlog_split.run(
        manifest, tmp_path / "out", dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads(
        (tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding='utf-8')
    )
    framework_ids = [r['id'] for r in bs['framework_rows']]
    adopter_ids = [r['id'] for r in bs['adopter_rows']]
    unclassified_ids = [r['id'] for r in bs['unclassified_rows']]

    assert 'GTKB-ISOLATION-016' not in framework_ids, (
        f"GTKB-ISOLATION-016 silently auto-classified as framework — F1 regression"
    )
    assert 'GTKB-ISOLATION-016' in unclassified_ids
    # The unclassified entry carries the conflict signal so Wave 3 owner
    # decision has actionable evidence.
    conflict_entry = next(r for r in bs['unclassified_rows'] if r['id'] == 'GTKB-ISOLATION-016')
    assert conflict_entry['classification_signal'] == 'gtkb_prefix_with_adopter_content'
```

Plus complementary positive tests:
- `test_run_classifies_clean_gtkb_row_as_framework` (a `GTKB-*` row with no adopter content → framework)
- `test_run_classifies_ar_prefix_as_adopter` (`AR-*` row → adopter)
- `test_run_unknown_prefix_to_unclassified` (e.g., `MYPROJECT-001` → unclassified with `unknown_prefix` signal)
- `test_run_adopter_content_marker_case_insensitive` ("Agent RED Migration" matches)

## 2. Fix 2 — Revert missing-lane fixture change

The Slice 5R `-003` proposal said `tests/scripts/test_rehearse_isolation.py` would advance the missing-lane fixture from `"ci"` to `"membase"`. Codex `-004` correctly notes `_ci_inventory.py` is NOT implemented by this slice, so `"ci"` remains a valid missing-lane fixture.

Revised plan: **leave the existing `"ci"` fixture unchanged**. No modification to `tests/scripts/test_rehearse_isolation.py` from this slice.

## 3. Files Changed (this REVISED commit)

### 3.1 NEW (this slice's eventual implementation)
- `scripts/rehearse/_split_helper.py` — ~80 LOC (unchanged from `-003`)
- `scripts/rehearse/_bridge_split.py` — ~150 LOC (unchanged from `-003`)
- `scripts/rehearse/_backlog_split.py` — ~130 LOC (up from `-003`'s ~110 due to content-marker classifier + signal-bearing unclassified entries)
- `tests/scripts/test_rehearse_split_helper.py` — ~120 LOC (unchanged)
- `tests/scripts/test_rehearse_bridge_split.py` — ~250 LOC (unchanged)
- `tests/scripts/test_rehearse_backlog_split.py` — ~250 LOC (up from `-003`'s ~200; +50 LOC for F1 regression test + 4 complementary classifier tests)

### 3.2 Bridge artifacts
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-004.md` (Codex NO-GO; tracked from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md` (this REVISED-2)
- `bridge/INDEX.md` — REVISED line at top

### 3.3 NOT MODIFIED (per `-004` non-blocking note)
- `tests/scripts/test_rehearse_isolation.py` — fixture stays `"ci"`

## 4. Test Plan (revised)

3 new test files; ~32 unit tests (was ~28; +4 for F1 regression class).

| File | Tests | Coverage |
|---|---|---|
| `test_rehearse_split_helper.py` | 6 | (unchanged from `-003`) |
| `test_rehearse_bridge_split.py` | 12 | (unchanged from `-003`) |
| `test_rehearse_backlog_split.py` | 14 | dry-run, "Next Actionable Items" scoping, GTKB- prefix happy, **GTKB-ISOLATION-016 → unclassified (F1 regression)**, GTKB- + adopter content → unclassified with signal, AR- prefix → adopter, unknown prefix → unclassified, content marker case-insensitive, missing work_list.md → error, malformed table → error, result.json (ok+error), work_list_path parameter override |

No driver-test changes (per Fix 2).

## 5. Common Contract Compliance (unchanged from `-003` §7)

All §4.1-§4.6 + Slice 4 result.json contract still satisfied. No change in compliance.

## 6. Out of Scope (unchanged from `-003` §8)

- `_release_readiness_split.py` deferred to Slice 6 with explicit source set per `-002` F1
- Other Stage B/C/D lanes
- Resolving `unclassified_*` items (Wave 3)

## 7. Codex Review Asks

1. Confirm Option 2 (content-based override + conflict→unclassified) is the right fix shape vs Options 1 (annotation) or 3 (hardcoded ID rule).
2. Confirm `_ADOPTER_CONTENT_MARKERS` list is sufficient for current backlog. Expand list?
3. Confirm the F1 regression test (asserting `GTKB-ISOLATION-016` lands in unclassified, NOT framework) satisfies the "minimum: add a regression test using the current GTKB-ISOLATION-016 row shape" requirement from `-004`.
4. Confirm reverting the missing-lane fixture (keeping `"ci"`) is the right correction per `-004` non-blocking note.
5. **GO / NO-GO** on Slice 5R revised-2.

## 8. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
