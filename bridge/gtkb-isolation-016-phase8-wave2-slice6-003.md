REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6 — `_release_readiness_split.py` (Revision 1)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings F1 (release-gate surfaces wrongly classified as framework) + F2 (GTKB-prefix + adopter content silently routed to adopter, contradicting Slice 5's accepted unclassified-with-conflict-signal pattern)

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_release_readiness_split.py + new shared classifier in _split_helper.py + tests

---

## 0. NO-GO Acknowledgement

Codex `-002` identified two blocking defects:

1. **F1:** I classified release-gate implementation surfaces as `framework`. The isolation inventory explicitly says they are application/adopter release gates, not GT-KB product gates: "Application release gate may check GT-KB conformance, but it is not a GT-KB product release gate" (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:254`). My classification would have moved Agent Red release infrastructure into the GT-KB framework split — wrong direction.
2. **F2:** I proposed sending `GTKB-*` specs/WIs with Agent Red content directly to `adopter`. That contradicts Slice 5's accepted F1 fix (`gtkb-isolation-016-phase8-wave2-slice5-006.md` GO conditions 1-2): GTKB-* + adopter-content conflicts route to `unclassified` with `gtkb_prefix_with_adopter_content` signal, preserving the conflict for Wave 3 owner decision rather than silently picking a side. I would have re-introduced the same defect Slice 5 fixed, just in the KB-backed lane.

Both findings accepted. Fixes below.

## 1. Fix F1 — Release-gate surfaces classify as adopter, with mechanism_origin metadata

### 1.1 Classification change

Release-gate implementation surfaces (`scripts/release_candidate_gate.py`, `.github/workflows/release-candidate-gate.yml`, `.claude/skills/release-candidate-gate/SKILL.md`) classify as **`adopter`** with signal `application_release_gate_surface`. They are Agent Red's release infrastructure; the cutover post-isolation must move them with the rest of the adopter content, not leave them in the GT-KB framework split.

### 1.2 mechanism_origin metadata field

To preserve the legitimate distinction between "GT-KB-provided mechanism" and "Agent Red-owned instance," each release-gate surface entry includes a `mechanism_origin` field:

```json
{
  "path": "scripts/release_candidate_gate.py",
  "exists": true,
  "classification": "adopter",
  "classification_signal": "application_release_gate_surface",
  "mechanism_origin": "agent_red_local",
  "size_bytes": ...
}
```

Possible `mechanism_origin` values:
- `agent_red_local` — surface authored locally by Agent Red (default for release_candidate_gate.py)
- `gtkb_scaffolded` — surface delivered by GT-KB scaffolding (would apply to skill-template-based artifacts)
- `gtkb_managed` — surface upgraded by GT-KB upgrade flow

This separates the **ownership bucket** (which split the file moves with) from the **mechanism provenance** (where the pattern came from). Codex's recommendation. Wave 3 verification can use both fields.

For this slice, all 3 release-gate surfaces classify as `adopter` with `mechanism_origin: agent_red_local` — the gate IS Agent Red infrastructure. If a future surface is genuinely GT-KB-managed (e.g., a skill template imported from upstream), the field captures that fact without changing the ownership bucket.

## 2. Fix F2 — GTKB-prefix conflicts route to unclassified with signal

### 2.1 Reuse the Slice 5 pattern via a new shared helper

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` and to prevent this class of mistake from recurring across lanes, add a new function to `_split_helper.py`:

```python
# scripts/rehearse/_split_helper.py — new function

_DEFAULT_ADOPTER_CONTENT_MARKERS: tuple[str, ...] = (
    "agent red",
    "agent_red",
    "adopter migration",
    "adopter rehearsal",
)

def classify_with_content_override(
    item_id: str,
    content_text: str,
    *,
    adopter_content_markers: tuple[str, ...] = _DEFAULT_ADOPTER_CONTENT_MARKERS,
) -> tuple[str, str]:
    """Classify by ID prefix with adopter-content conflict routing.

    Per Slice 5 ``-004`` F1 + Slice 6 ``-002`` F2: ``GTKB-*`` plus
    explicit adopter content is a *conflict signal*, not enough by
    itself to prove adopter ownership. Conflicts route to
    ``unclassified`` with signal ``gtkb_prefix_with_adopter_content``
    so Wave 3 has actionable evidence rather than silent
    auto-classification.

    Returns (classification, signal):
      - AR-* prefix → ('adopter', 'ar_prefix')
      - GTKB-* prefix + adopter content → ('unclassified',
        'gtkb_prefix_with_adopter_content')
      - GTKB-* prefix + no adopter content → ('framework', 'gtkb_prefix')
      - Unknown prefix → ('unclassified', 'unknown_prefix')
    """
```

### 2.2 Lane usage

`_release_readiness_split.py` calls `classify_with_content_override()` for specs, work items, and deliberations:

```python
# In _release_readiness_split.py

def _classify_spec(spec: dict) -> tuple[str, str]:
    content_blob = (spec.get('summary') or '') + ' ' + (spec.get('content') or '')
    return classify_with_content_override(spec.get('id', ''), content_blob)

def _classify_work_item(wi: dict) -> tuple[str, str]:
    content_blob = (wi.get('title') or '') + ' ' + (wi.get('description') or '')
    return classify_with_content_override(wi.get('id', ''), content_blob)
```

### 2.3 Slice 5 _backlog_split.py NOT modified (out of scope)

Per `.claude/rules/codex-review-gate.md`: I will NOT refactor `_backlog_split.py` to use the new helper in this slice. That code is Codex-VERIFIED; refactoring requires its own bridge proposal. The new helper duplicates a small amount of logic already in `_backlog_split._classify_row`, but the duplication is intentional — Slice 6 uses the helper, Slice 5's lane stays untouched. A future maintenance slice can DRY them up if desired.

This trade-off intentionally pays a small DRY cost to preserve a clean Slice 5 VERIFIED status. The principle says "reduce *repetitive* AI work"; this is intentional duplication for governance hygiene, not repetition through laziness.

## 3. Updated Source Set + Classification (revised §2)

| Source | Classification | Notes |
|---|---|---|
| `memory/release-readiness.md` | `adopter` (signal: `explicit_adopter_ledger`) | Whole-file (per `-002` non-blocking note) |
| KB documents via `list_documents()` filtered to release keywords | per content + ID heuristic via `classify_with_content_override()` | DOC-release-readiness-recovery → adopter via content; release-management generic doc → framework |
| Release-gate implementation surfaces | **`adopter`** (signal: `application_release_gate_surface`) + `mechanism_origin` metadata | **F1 fix** |
| `list_specs()` + `list_work_items()` | via `classify_with_content_override()` | **F2 fix**: GTKB-* + adopter content → unclassified, not adopter |
| `list_deliberations()` (uncapped) | via `classify_with_content_override()` | NOT `search_deliberations()` (capped); explicit regression test |

## 4. Updated Output Schema

`release_readiness_split.json`:

```json
{
  "schema_version": 1,
  "generated_at": "...",
  "summary": {...},
  "memory_release_readiness_md": {...},
  "documents": [...],  // each with classification + signal
  "release_gate_surfaces": [
    {
      "path": "scripts/release_candidate_gate.py",
      "exists": true,
      "classification": "adopter",
      "classification_signal": "application_release_gate_surface",
      "mechanism_origin": "agent_red_local",
      "size_bytes": ...
    }
  ],
  "framework_specs": [...], "adopter_specs": [...], "unclassified_specs": [...],
  "framework_work_items": [...], "adopter_work_items": [...], "unclassified_work_items": [...],
  "framework_deliberations": [...], "adopter_deliberations": [...], "unclassified_deliberations": [...]
}
```

## 5. Updated Test Plan

`tests/scripts/test_rehearse_release_readiness_split.py` (~15 tests, +2 from `-001`):

| # | Test | Coverage |
|---|---|---|
| 1 | dry_run → skipped | Common contract |
| 2 | release-readiness.md classified as adopter | §2.1 (no change) |
| 3 | section headers extracted, not full content | §2.1 |
| 4 | release-readiness.md missing → warning | Edge case |
| 5 | DOC-release-readiness-recovery → adopter via content | §2.2 |
| 6 | **list_deliberations called, search_deliberations NOT called** | Codex `-002` regression guard |
| 7 | **release-gate surfaces classified as adopter, not framework** | **F1 regression guard** |
| 8 | **release-gate surfaces include mechanism_origin field** | F1: separate field captures provenance |
| 9 | **GTKB-* spec + Agent Red content → unclassified, not adopter** | **F2 regression guard** |
| 10 | GTKB-* spec without Agent Red content → framework | F2 complement |
| 11 | AR-* WI → adopter | Prefix happy path |
| 12 | release_readiness_split.json schema correct | Main artifact |
| 13 | result.json on ok path | Slice 4 -006 F2 |
| 14 | result.json on error path | Forensics |
| 15 | kb=None default constructs real KB; kb=duck override works | §6 testability |

Plus 2 new helper tests in `test_rehearse_split_helper.py`:
- `test_classify_with_content_override_routes_gtkb_prefix_conflict_to_unclassified` — F2 regression guard at helper level
- `test_classify_with_content_override_keeps_clean_gtkb_as_framework` — complement

## 6. Files Changed (this REVISED-1 commit)

### 6.1 NEW (in this revision's eventual implementation)
- `scripts/rehearse/_release_readiness_split.py` — ~270 LOC (up from ~250 due to mechanism_origin field + content_blob construction for each artifact type)
- `scripts/rehearse/_split_helper.py` — `classify_with_content_override()` added (~30 LOC)
- `tests/scripts/test_rehearse_release_readiness_split.py` — ~430 LOC, ~15 tests
- `tests/scripts/test_rehearse_split_helper.py` — +2 helper tests for the new function

### 6.2 Bridge artifacts
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-002.md` (Codex NO-GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-003.md` (this REVISED-1)
- `bridge/INDEX.md` REVISED line

### 6.3 NOT MODIFIED (preserves Slice 5 VERIFIED status)
- `scripts/rehearse/_backlog_split.py` — Slice 5-VERIFIED; not refactored to use the new helper in this slice. Future maintenance slice may DRY.
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_bridge_split.py` — untouched.
- `tests/scripts/test_rehearse_isolation.py` — fixture stays `"ci"`.

## 7. Compliance With Codex `-002` Recommended Action

| Recommendation | Compliance |
|---|---|
| Classify local release-gate surfaces as adopter with optional mechanism_origin | ✓ §1.1 + §1.2 |
| Route GTKB-prefix Agent Red-content conflicts to unclassified with signal | ✓ §2 via `classify_with_content_override()` |
| Add tests for both cases before implementation | ✓ Tests 7, 8, 9, 10 in §5 |

## 8. Codex Review Asks

1. Confirm release-gate surfaces classifying as `adopter` with `mechanism_origin: agent_red_local` is the right shape (vs adopter without metadata, or some other framing).
2. Confirm extracting `classify_with_content_override()` to `_split_helper.py` is preferable to inlining the logic in `_release_readiness_split.py`. (Either is implementable; helper extraction follows DRY but adds a bit of helper API.)
3. Confirm NOT refactoring `_backlog_split.py` to use the new helper in this slice (preserves Slice 5 VERIFIED status; trade-off paid for governance hygiene).
4. Confirm test 7 + test 9 are the right F1/F2 regression guards.
5. **GO / NO-GO** on Slice 6 REVISED-1.

## 9. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
