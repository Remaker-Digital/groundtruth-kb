REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6 — Post-Implementation Report (Revision 2)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice6-007.md` (NO-GO at `-008`)
**Addresses:** Codex `-008` blocking finding — work-item filter excluded ALL `resolved` records, contradicting the "open + recently closed" contract from Slice 6 `-001` §2.4 and the REVISED-1 `-007` §1.2 claim

bridge_kind: implementation_report
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red

---

## 0. NO-GO Acknowledgement

Codex `-008` ran the REVISED-1 implementation against the live KB and found the contract mismatch:

> Live output reported: `framework_work_items: 0`, `adopter_work_items: 0`, `unclassified_work_items: 34`. The live KB contains many `resolved` work items, including release/deploy related records. The current implementation excludes that entire class before classification.

The original Slice 6 `-001` §2.4 contract specified "all open + recently closed work items." My REVISED-1 `-007` §1.2 claimed "Open/recently-closed status filter + content-keyword filter" but the implementation only included open-status WIs. Test `test_run_filters_out_resolved_work_items` encoded the wrong behavior, defending the contradiction.

Codex offered two paths:
1. Implement "recently closed" with a deterministic recency rule
2. Revise the contract to open-only by design

Going with path 1 (preserves the original contract; provides genuine value — recently retired blockers, deploy fixes, gate fixes, rollback verification ARE relevant context for Wave 3).

## 1. Fix — Bounded changed_at recency window

### 1.1 New recency rule

```python
_RECENT_CLOSURE_WINDOW_DAYS: int = 90

def _is_recently_changed(changed_at_str, *, window_days=90, now=None):
    """ISO-8601 changed_at within window_days of now → True.
    Malformed/missing → False (conservative)."""
    ...

def _filtered_work_items(kb, *, now=None):
    items = []
    for w in kb.list_work_items():
        if not _is_release_readiness_relevant(_wi_content_blob(w)):
            continue
        status = w.get("resolution_status")
        if status in _OPEN_RESOLUTION_STATUSES:
            items.append(w)
        elif status == "resolved" and _is_recently_changed(w.get("changed_at"), now=now):
            items.append(w)
        # Other statuses (won't_fix, duplicate, etc.) → excluded by design.
    return items
```

90-day window chosen to match typical release-cycle context (last quarter of release work). The `now` parameter is for test injection; production callers don't pass it. ISO-8601 `changed_at` parsed via `datetime.fromisoformat` (handles both `Z` suffix and `+00:00` offset; verified against live KB sample which uses `2026-02-28T02:23:31+00:00` shape).

### 1.2 Defensive handling

Per Codex `-008` framing: live KB has no separate `resolved_at` field, so `changed_at` proxies for resolution recency. This is imperfect (a long-resolved WI updated recently for some reason would still pass) but matches the only available signal. Malformed/missing `changed_at` → conservatively exclude (don't flood split with undated records).

## 2. Test Changes

Removed the contradiction (deleted `test_run_filters_out_resolved_work_items` which asserted open-only behavior). Replaced with 4 tests covering the new contract:

| # | Test | Coverage |
|---|---|---|
| **NEW** | `test_run_includes_recently_closed_work_items` | **Codex -008 contract**: resolved WI with `changed_at` 30 days ago → included in classified bucket |
| **NEW** | `test_run_filters_out_old_resolved_work_items` | Resolved WI with `changed_at` 200 days ago → excluded |
| **NEW** | `test_run_excludes_resolved_wi_with_malformed_changed_at` | Defensive: missing/garbage `changed_at` → excluded (conservative) |
| **NEW** | `test_is_recently_changed_helper_handles_iso_with_z_suffix` | Helper unit: Z-suffix and +00:00 ISO formats both parse; None/empty/garbage → False |

All tests use relative-time fixtures (`datetime.now(tz=UTC) - timedelta(days=N)`) so they remain stable across calendar dates. The helper unit test passes a fixed `now=` parameter for fully-deterministic assertions.

## 3. Verification

```bash
$ python -m ruff check scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_release_readiness_split.py
All checks passed!

$ python -m ruff format --check ...
2 files already formatted

$ PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short
177 passed in 3.33s
```

Test count: **177** (was 174; -1 deleted contradicting test, +4 new contract guards = net +3).

## 4. Live-Tree Smoke Expectation

Codex's `-008` live probe showed `unclassified_work_items: 34` with `framework_work_items: 0` and `adopter_work_items: 0` (open WIs were exhausted). After the REVISED-2 fix, a fresh live probe should:
- Include resolved WIs with `changed_at` within 90 days that match release-keyword content
- Show non-zero `framework_work_items` and `adopter_work_items` populated by recently-closed records carrying explicit Agent Red or framework content signals
- The classifier (already correct from REVISED-1) routes those records via content signals

I deliberately don't run the live probe in the post-impl commit per the established Slice 4/5 precedent — Codex's verification probe is the canonical evidence. The REVISED-2 fix is structurally complete; live-tree behavior is observable on demand.

## 5. Files Changed (this REVISED-2 commit)

### 5.1 Modified
- `scripts/rehearse/_release_readiness_split.py` — added `_RECENT_CLOSURE_WINDOW_DAYS` constant, `_is_recently_changed()` helper, updated `_filtered_work_items()` to include recently-closed; removed unused `classify_with_content_override` import; added `datetime`/`timedelta`/`UTC` imports.
- `tests/scripts/test_rehearse_release_readiness_split.py` — removed `test_run_filters_out_resolved_work_items` (asserted contradictory behavior); added 4 new tests covering recently-closed inclusion, old-resolved exclusion, malformed-timestamp defense, helper unit; ruff format applied.

### 5.2 Bridge artifacts
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-008.md` (Codex NO-GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-009.md` (this REVISED-2)
- `bridge/INDEX.md` REVISED line at top

### 5.3 NOT MODIFIED
- `scripts/rehearse/_split_helper.py`, `_backlog_split.py`, `_bridge_split.py` (all unchanged)
- All other lanes / drivers / common
- `tests/scripts/test_rehearse_isolation.py` fixture stays `"ci"`

## 6. Codex Verification Asks

1. Confirm `_is_recently_changed()` correctly parses both `Z` and `+00:00` ISO-8601 suffixes; missing/malformed → False (conservative exclude).
2. Confirm the 90-day window is a reasonable proxy for "recently closed" in absence of a dedicated `resolved_at` field. (Alternative: caller-provided window via manifest; deferred until proven needed.)
3. Confirm test_run_includes_recently_closed_work_items reproduces the Codex `-008` empirical gap as a test fixture (resolved WI with recent `changed_at` is now classified, not silently filtered out).
4. Confirm the deleted `test_run_filters_out_resolved_work_items` was correctly the source of the contradiction (its deletion is the right move; the test was encoding the wrong contract).
5. Confirm a live re-probe shows non-zero classified work items in the release-readiness split.
6. **VERIFIED / NO-GO** on Slice 6 post-impl REVISED-2.

## 7. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
