NEW

# Implementation Report - GTKB-ISOLATION-017 Slice 5.5 Overlay Tests

**Author:** Prime Builder (Codex, harness A)
**Date:** 2026-05-06
**Type:** Post-implementation report
**Backlog item:** `GTKB-ISOLATION-017-SLICE-5.5`
**Proposal authority:** `bridge/gtkb-isolation-017-slice-5-5-overlay-tests-003.md`
**Review authority:** `bridge/gtkb-isolation-017-slice-5-5-overlay-tests-004.md` (`GO`)

---

## Claim

Slice 5.5 is implemented. GT-KB now exposes a bounded adopter-facing ChromaDB
regeneration API and CLI, plus clean-adopter coverage proving refresh,
disposability, stale-detection preservation, boundary refusal, and explicit
optional-dependency skip behavior.

## Implemented Changes

- Added `groundtruth_kb.project.chroma.regenerate(target, *, dry_run=False)`.
- Added `gt project chroma regenerate --dir <adopter> [--dry-run] [--json]`.
- Regeneration uses `groundtruth.db` as the source of truth through
  `KnowledgeDB.rebuild_deliberation_index()`.
- Source-checkout targets must live directly under
  `E:\GT-KB\applications\`; installed-wheel targets must live directly under
  an `applications/` directory.
- `groundtruth.db` and `chroma_path` must resolve inside the adopter target.
- Existing `.groundtruth-chroma/` files are replaced only when ChromaDB is
  available and the operation is not a dry run.
- Missing ChromaDB optional support returns `status="skipped"` and preserves
  existing cache files instead of silently claiming success.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/chroma.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/adopter/test_overlay_refresh.py`
- `groundtruth-kb/tests/adopter/test_overlay_disposability.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation report is filed under
  the active bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation is
  tied to the approved proposal and cited governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps
  tests to spec-derived obligations.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the deferred Slice 5.5 capability is
  preserved as a durable implementation report with explicit lifecycle state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - the API enforces adopter/root
  boundary placement and rejects out-of-bound targets.
- `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` -
  authorizes Slice 5.5 as the deferred refresh/disposability follow-on.

## Spec-To-Test Map

| Requirement | Evidence |
|---|---|
| Phase 6 overlay refresh behaves on demand | `tests/adopter/test_overlay_refresh.py::test_chroma_regenerate_replaces_stale_overlay` |
| Phase 6 overlay cache is disposable and rebuildable | `tests/adopter/test_overlay_disposability.py::test_chroma_overlay_can_be_deleted_and_regenerated` |
| Existing stale-detection behavior stays intact | `tests/adopter/test_overlay_stale_detection.py` |
| API is bounded to the adopter/root boundary | `tests/adopter/test_overlay_disposability.py::test_chroma_regenerate_rejects_non_adopter_target` |
| Optional ChromaDB dependency gaps are explicit | `tests/adopter/test_overlay_refresh.py::test_chroma_regenerate_reports_optional_dependency_skip` |
| Public CLI has a non-mutating planning surface | `tests/adopter/test_overlay_refresh.py::test_chroma_regenerate_dry_run_json_does_not_write` |
| No live dependency on archive paths | `rg -n "Claude-Playground|E:\\\\Claude-Playground" <touched files>` returned no matches |

## Verification

```powershell
cd E:\GT-KB\groundtruth-kb
python -m pytest tests/adopter/test_overlay_stale_detection.py tests/adopter/test_overlay_refresh.py tests/adopter/test_overlay_disposability.py -q --tb=short
# 7 passed, 1 warning

python -m pytest tests/test_doctor_isolation.py tests/adopter/test_doctor_detects_isolation_violations.py tests/adopter/test_overlay_stale_detection.py tests/adopter/test_overlay_refresh.py tests/adopter/test_overlay_disposability.py -q --tb=short
# 45 passed, 1 warning

python -m ruff check src/groundtruth_kb/project/chroma.py src/groundtruth_kb/cli.py tests/adopter/test_overlay_stale_detection.py tests/adopter/test_overlay_refresh.py tests/adopter/test_overlay_disposability.py
# All checks passed.

python -m ruff format --check src/groundtruth_kb/project/chroma.py src/groundtruth_kb/cli.py tests/adopter/test_overlay_stale_detection.py tests/adopter/test_overlay_refresh.py tests/adopter/test_overlay_disposability.py
# 5 files already formatted
```

The ChromaDB warning is an upstream deprecation warning from the installed
optional dependency:
`chromadb\telemetry\opentelemetry\__init__.py:128: DeprecationWarning:
'asyncio.iscoroutinefunction' is deprecated...`.

## Applicability Preflight

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-017-slice-5-5-overlay-tests
```

- operative_file: `bridge/gtkb-isolation-017-slice-5-5-overlay-tests-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Risk / Impact

- The new CLI mutates only `.groundtruth-chroma/` under the validated adopter
  target and never changes canonical SQLite records.
- In source checkouts, non-adopter and out-of-root paths are rejected before
  config or database mutation.
- On Windows, ChromaDB keeps SQLite handles open unless its client is closed
  and released; the implementation explicitly closes the client, drops the
  cached reference, and runs garbage collection after rebuild.
- Full `groundtruth-kb` format check still has pre-existing unrelated drift
  from other files; this item verified formatting only on touched files.

## Recommended Action

Loyal Opposition should verify the Slice 5.5 implementation and, if acceptable,
mark this bridge thread `VERIFIED`.

## Decision Needed From Owner

None.
