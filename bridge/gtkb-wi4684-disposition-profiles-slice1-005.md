NEW

# WI-4684 Slice 1: Activity-Disposition Profile Schema, Data & Loader — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4684-disposition-profiles-slice1
Version: 005
Responds-To: bridge/gtkb-wi4684-disposition-profiles-slice1-004.md (GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-22 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-22T07-14-43Z-prime-builder-B-7bc82a
author_model: Claude Sonnet 4.6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code CLI, auto-dispatched Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4684

target_paths: ["config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/activity/__init__.py", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "platform_tests/scripts/test_activity_disposition_profiles.py"]

---

## Implementation Summary

All four target files exist in the working tree as net-new, uncommitted files. The implementation was produced by a prior dispatch session; this report records the verified state for Loyal Opposition review.

**Files implemented (all net-new, untracked):**

1. `config/agent-control/activity-disposition-profiles.toml` — TOML config with `schema_version = 1` and six canonical activity profile records (`ops`, `deliberation`, `build`, `test`, `spec`, `project`), each carrying all four payload classes plus `headless_eligibility` values per DELIB-20265287 D4.
2. `groundtruth-kb/src/groundtruth_kb/activity/__init__.py` — Package init with single-line module docstring.
3. `groundtruth-kb/src/groundtruth_kb/activity/profiles.py` — Canonical reader entrypoint `load_activity_profiles()` with `ActivityProfile` frozen dataclass, `ActivityProfileError` typed exception, `CANONICAL_ACTIVITIES` frozenset, `_D4_ELIGIBILITY` mapping, and fail-closed A1/A2/A3 validation.
4. `platform_tests/scripts/test_activity_disposition_profiles.py` — 12-test pytest suite with full spec-to-test mapping for DCL A1–A3 and all loader fail-closed paths.

**Out of scope (deferred per proposal):** `::open <activity>` interception hook (Slice 2 / DCL A4), soft-reminder gate (Slice 3 / DCL A5), per-activity content refinement (WI-4730 owner-driven AUQ), `topic_router.py` 5→6 vocabulary reconciliation (WI-4683).

## Specification Links

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` — normative schema; assertions A1/A2/A3 are this slice's acceptance criteria.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` — architecture decision implemented.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/WI/PAUTH linkage metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — tests derived from linked DCL assertions.
- `GOV-STANDING-BACKLOG-001` — WI-4684 is the governing backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — (advisory) config is a schema-versioned, git-tracked governed artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — (advisory) TOML+loader are new durable artifact-graph nodes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — (advisory) `headless_eligibility` is an artifact lifecycle trigger signal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — confirms all implementation files land within `E:\GT-KB` (not Agent Red or any out-of-root path); the four target paths are platform-root GT-KB artifacts only.

## Spec-to-Test Mapping

| DCL Clause | Test(s) | Result |
|---|---|---|
| A1: six canonical activities present | `test_all_six_activities_present`, `test_default_path_loads_shipped_config` | PASS |
| A2: four classes per profile | `test_each_profile_defines_four_classes`, `test_skills_and_terminology_are_lists`, `test_history_state_and_direction_are_dicts` | PASS |
| A3: `headless_eligibility` valid and D4-consistent | `test_headless_eligibility_valid_and_d4_consistent` | PASS |
| Loader fail-closed / A1 violation | `test_loader_rejects_missing_activity` | PASS |
| Loader fail-closed / A2 violation | `test_loader_rejects_missing_class` | PASS |
| Loader fail-closed / A3 violation | `test_loader_rejects_invalid_eligibility`, `test_loader_rejects_d4_inconsistent_eligibility` | PASS |
| Default path resolution | `test_default_path_loads_shipped_config` | PASS |
| Error paths: missing file | `test_loader_raises_on_missing_file` | PASS |
| Error paths: invalid TOML | `test_loader_raises_on_invalid_toml` | PASS |

DCL assertions A4/A5 remain out of scope; the DCL stays at `status=specified` until Slices 2–3 land the consuming runtime.

## Verification Evidence

### pytest (12/12 passed)

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: E:\GT-KB
configfile: pyproject.toml
...
collected 12 items

platform_tests\scripts\test_activity_disposition_profiles.py ............ [100%]

======================== 12 passed, 1 warning in 8.83s ========================
```

### ruff check

```
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py
All checks passed!
```

### ruff format --check

```
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py
2 files already formatted
```

## Implementation-Start Authorization Evidence

```json
{
  "bridge_id": "gtkb-wi4684-disposition-profiles-slice1",
  "created_at": "2026-06-22T07:25:48Z",
  "expires_at": "2026-06-22T09:25:48Z",
  "go_file": "bridge/gtkb-wi4684-disposition-profiles-slice1-004.md",
  "latest_status": "GO",
  "packet_hash": "sha256:19a2c155dc3e2f958e421f6519793d3c2d59a4bf531782c893094940302555ac",
  "project_authorization": "PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-...",
  "work_item_id": "WI-4684"
}
```

## Scope Confirmation

- A4/A5 wiring (interception hook, soft-reminder gate): **NOT implemented** — Slices 2/3.
- `topic_router.py` vocabulary reconciliation: **NOT implemented** — WI-4683.
- Per-activity profile content refinement: **NOT implemented** — WI-4730 (owner-driven AUQ).
- Agent Red / out-of-root mutations: **none**.

## Prior Deliberations

- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — DEC-2/DEC-3/DEC-4; the 4-class context-load profile and six-member vocabulary encoded in this slice.
- `DELIB-20265287` — D2 (named versioned profiles), D4 (per-activity headless-eligibility), F2 (profile enriches intent_hint leg).

## Recommended Commit Type

- Recommended commit type: `feat` — net-new capability surface (`activity` package + config + test suite); no existing behavior modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
