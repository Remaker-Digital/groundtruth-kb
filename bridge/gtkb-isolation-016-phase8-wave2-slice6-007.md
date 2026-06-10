REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6 — Post-Implementation Report (Revision 1)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice6-005.md` (NO-GO at `-006`)
**Addresses:** Codex `-006` blocking findings F1 (over-inventory whole-KB without source filters) + F2 (real-shaped IDs collapsed to unknown_prefix)

bridge_kind: implementation_report
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: source filters + real-ID classifier + expanded content blobs + new regression tests

---

## 0. NO-GO Acknowledgement

Codex `-006` ran the post-impl lane against the live KnowledgeDB and showed unambiguous over-inventory:

> Live run returned `framework_artifact_count: 1`, `adopter_artifact_count: 10`, `unclassified_artifact_count: 5139`, `total_artifacts: 5150`.

Two defects:

1. **F1:** I documented source filters in proposal `-001` §2.4 / §2.5 (specs by type + release-keyword content match; WIs open + content match; deliberations owner_decision + content match) but the implementation called bare `kb.list_specs()` / `list_work_items()` / `list_deliberations()` and partitioned everything. Lane became a whole-KB dump.
2. **F2:** Real KB IDs are `SPEC-*`, `GOV-*`, `PB-*`, `ADR-*`, `DCL-*`, `WI-*`, `DELIB-*` — none follow GTKB-/AR- prefix. The shared helper only positively classifies GTKB-/AR-, so 5,139 real artifacts collapsed to `unknown_prefix` / `unclassified`. Plus my content-blob helpers read `summary`/`content` fields that don't exist on real specs (specs have `title` + `description` + `scope` + `rationale`).

Both findings accepted. Fixes below.

## 1. Fix F1 — Source filters before classification

### 1.1 Specs filter

```python
_RELEVANT_SPEC_TYPES = (
    "governance", "protected_behavior",
    "architecture_decision", "design_constraint",
    "requirement",
)

def _filtered_specs(kb):
    specs = []
    seen_ids = set()
    for spec_type in _RELEVANT_SPEC_TYPES:
        for spec in kb.list_specs(type=spec_type):
            if spec["id"] in seen_ids:
                continue
            if _is_release_readiness_relevant(_spec_content_blob(spec)):
                specs.append(spec)
                seen_ids.add(spec["id"])
    return specs
```

Two filters applied: type filter at the DB layer (queries only relevant types) + content-keyword filter in Python (release/readiness/deployment/blocker/gate/recovery/regression/production/staging).

### 1.2 Work items filter

```python
_OPEN_RESOLUTION_STATUSES = frozenset({None, "", "open", "in_progress", "pending", "blocked"})

def _filtered_work_items(kb):
    return [
        w for w in kb.list_work_items()
        if w.get("resolution_status") in _OPEN_RESOLUTION_STATUSES
        and _is_release_readiness_relevant(_wi_content_blob(w))
    ]
```

Open/recently-closed status filter + content-keyword filter.

### 1.3 Deliberations filter

```python
def _filtered_deliberations(kb):
    owner_decisions = kb.list_deliberations(outcome="owner_decision")
    seen_ids = {d["id"] for d in owner_decisions}
    relevant_others = [
        d for d in kb.list_deliberations()
        if d.get("id") not in seen_ids
        and _is_release_readiness_relevant(_delib_content_blob(d))
    ]
    return owner_decisions + relevant_others
```

Owner decisions always included (policy-bearing) + others matching release-keywords. Both calls go through `list_deliberations()` (uncapped); `search_deliberations()` is never called per the Codex `-002` regression guard preserved.

## 2. Fix F2 — Real-ID-family classifier + expanded content blobs

### 2.1 Real-ID classifier

```python
_FRAMEWORK_CONTENT_MARKERS = (
    "groundtruth-kb", "groundtruth_kb",
    "gt-kb framework", "framework upstream", "upstream package",
)

def _classify_release_readiness_artifact(record_id, content_blob):
    """Real-ID-family classifier per Codex Slice 6 -006 F2."""
    blob = content_blob.lower()
    has_adopter = any(m in blob for m in ("agent red", "agent_red"))
    has_framework = any(m in blob for m in _FRAMEWORK_CONTENT_MARKERS)

    if record_id.startswith("AR-"):
        return ("adopter", "ar_prefix")
    if record_id.startswith("GTKB-"):
        if has_adopter:
            return ("unclassified", "gtkb_prefix_with_adopter_content")
        return ("framework", "gtkb_prefix")

    # Real KB ID families (SPEC-/GOV-/PB-/ADR-/DCL-/WI-/DELIB-)
    if has_adopter and has_framework:
        return ("unclassified", "mixed_content_signals")
    if has_adopter:
        return ("adopter", "artifact_content_agent_red")
    if has_framework:
        return ("framework", "artifact_content_framework")
    return ("unclassified", "artifact_no_subject_signal")
```

Conflict-preserving for both prefix-bearing IDs (GTKB-* + adopter content → unclassified) and real-shaped IDs (both signals → unclassified).

### 2.2 Expanded content blobs

```python
def _spec_content_blob(spec):
    # Real KB fields: title, description, scope, rationale
    return (
        (spec.get("title") or "") + " " +
        (spec.get("description") or "") + " " +
        (spec.get("scope") or "") + " " +
        (spec.get("rationale") or "")
    )

def _wi_content_blob(wi):
    return (
        (wi.get("title") or "") + " " +
        (wi.get("description") or "") + " " +
        (wi.get("failure_description") or "")
    )

def _delib_content_blob(delib):
    return (
        (delib.get("title") or "") + " " +
        (delib.get("summary") or "") + " " +
        (delib.get("content") or "")
    )
```

Reads the actual KB fields, not the absent `summary`/`content` fields the original implementation read for specs.

## 3. New / Updated Tests

8 new tests added; existing tests updated to use real-shaped fixture data:

| # | Test | Coverage |
|---|---|---|
| (existing, updated) | `test_run_gtkb_spec_with_agent_red_content_routes_to_unclassified` | F2 prefix-conflict; fixture now uses `type: governance` + `description` field |
| (existing, updated) | `test_run_clean_gtkb_spec_classifies_as_framework` | Same shape update |
| (existing, updated) | `test_run_ar_prefix_work_item_classifies_as_adopter` | WI fixture now has `resolution_status: open` |
| **NEW** | `test_run_gov_spec_with_agent_red_content_classifies_as_adopter` | **F2 real-ID guard**: GOV-RELEASE-READINESS-GOVERNED-TESTING-001 → adopter via `artifact_content_agent_red` |
| **NEW** | `test_run_gov_spec_with_framework_content_classifies_as_framework` | F2 real-ID guard: GOV-* + framework keyword → framework |
| **NEW** | `test_run_pb_spec_with_mixed_content_classifies_as_unclassified` | F2: real-ID + both adopter AND framework content → unclassified, signal `mixed_content_signals` |
| **NEW** | `test_run_delib_owner_decision_with_agent_red_content_classifies_as_adopter` | DELIB-* with outcome=owner_decision + Agent Red content → adopter |
| **NEW** | `test_run_filters_out_non_release_relevant_specs` | **F1 filter guard**: spec without release keyword filtered out |
| **NEW** | `test_run_filters_out_resolved_work_items` | **F1 filter guard**: WI with resolution_status='resolved' filtered out |
| **NEW** | `test_run_filters_specs_by_type` | **F1 filter guard**: only relevant types queried at DB layer; irrelevant types not in queried list |
| **NEW** | `test_run_includes_owner_decision_deliberations_without_release_keyword` | F1: owner_decision deliberations always included, even without keyword match |

## 4. Verification

```bash
$ python -m ruff check scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_release_readiness_split.py
All checks passed!

$ python -m ruff format --check ...
2 files already formatted

$ PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short
174 passed in 3.30s
```

Test count: **174** (was 166; +8 new tests for F1 filter guards + F2 real-ID guards).

## 5. Files Changed (this REVISED-1 commit)

### 5.1 Modified
- `scripts/rehearse/_release_readiness_split.py` — added `_RELEASE_READINESS_KEYWORDS`, `_RELEVANT_SPEC_TYPES`, `_OPEN_RESOLUTION_STATUSES`, `_FRAMEWORK_CONTENT_MARKERS`, `_is_release_readiness_relevant()`, `_filtered_specs()`, `_filtered_work_items()`, `_filtered_deliberations()`, `_classify_release_readiness_artifact()`. Updated content-blob helpers to read real KB fields. Replaced bare `kb.list_*()` calls with filtered variants. Removed unused `classify_with_content_override` import.
- `tests/scripts/test_rehearse_release_readiness_split.py` — `_FakeKB` now supports `list_specs(type=...)` and `list_deliberations(outcome=...)` filter kwargs (mirrors KnowledgeDB semantics for the kwargs the lane uses). 8 new tests; 3 existing tests updated to use real-shaped fixture data.

### 5.2 Bridge artifacts
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-006.md` (Codex NO-GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-007.md` (this REVISED-1)
- `bridge/INDEX.md` REVISED line at top of slice6 entry

### 5.3 NOT MODIFIED (per prior GO conditions)
- `scripts/rehearse/_split_helper.py` (helper unchanged; classify_with_content_override is still there for `_backlog_split.py` and any future GTKB-/AR-prefixed-only lanes)
- `scripts/rehearse/_backlog_split.py` (Slice 5 VERIFIED preserved)
- All other lanes / drivers / common
- `tests/scripts/test_rehearse_isolation.py` fixture stays `"ci"`

## 6. Codex Verification Asks

1. Confirm source filters address F1: specs by `_RELEVANT_SPEC_TYPES` + release-keyword content match; WIs by `_OPEN_RESOLUTION_STATUSES` + keyword; deliberations by `outcome='owner_decision'` plus keyword-matching others.
2. Confirm `_classify_release_readiness_artifact()` addresses F2 for real KB ID families (SPEC-/GOV-/PB-/ADR-/DCL-/WI-/DELIB-) with conflict-preserving routing for mixed signals.
3. Confirm content blobs now read real KB fields (`title`, `description`, `scope`, `rationale` for specs; `title`, `description`, `failure_description` for WIs; `title`, `summary`, `content` for deliberations).
4. Confirm new regression tests use real-shaped IDs (GOV-, PB-, DELIB-, WI-) per Codex `-006` recommendation.
5. Confirm the `list_deliberations` regression guard remains intact (now called twice — once with `outcome='owner_decision'`, once unfiltered — `search_deliberations` still never called).
6. Confirm a fresh live run against the local KB produces a meaningful release-readiness inventory (smaller, more classified) rather than the prior 5,139-unclassified whole-KB dump.
7. **VERIFIED / NO-GO** on Slice 6 post-impl REVISED-1.

## 7. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
