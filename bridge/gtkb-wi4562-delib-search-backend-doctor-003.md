NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB
Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-4562

# GT-KB Bridge Implementation Report - WI-4562 Deliberation Search Backend Doctor Check - 003

bridge_kind: implementation_report
Document: gtkb-wi4562-delib-search-backend-doctor
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4562-delib-search-backend-doctor-002.md
Approved proposal: bridge/gtkb-wi4562-delib-search-backend-doctor-001.md
Recommended commit type: fix:

## Implementation Claim

Implemented a bridge-profile `gt project doctor` health check for the deliberation-search backend.

- Added `KnowledgeDB.deliberation_search_backend_status()` as a read-only canonical-state probe for ChromaDB availability, canonical Chroma index path presence, collection availability, indexed chunk count, indexed deliberation-id coverage, and SQLite current deliberation count.
- Added `_check_deliberation_search_backend()` to `groundtruth_kb.project.doctor`, wired into bridge-profile `run_doctor()` after the service/SoT watchdog check.
- The doctor check is `required=True` in bridge profiles and fails loudly with a rebuild hint when ChromaDB is unavailable, the index path is missing, the collection cannot be opened, metadata cannot be read, or indexed deliberation IDs do not cover the current SQLite deliberation population.
- Added hermetic unit coverage for healthy, stale, and missing-Chroma states.
- Added platform test coverage proving a missing-index probe does not create the Chroma directory or open a Chroma client.
- Added a defensive fail-soft wrapper around dispatcher-complex health collection in `doctor.py`; the required full `test_doctor.py` slice exposed that synthetic dual-agent doctor fixtures could crash when dispatcher-complex scripts were absent. This keeps doctor behavior diagnostic instead of aborting.

Note: `groundtruth-kb/src/groundtruth_kb/db.py` also contains earlier uncommitted WI-4563 search-time fail-loud changes in the shared worktree. This WI-4562 report claims only the new read-only `deliberation_search_backend_status()` helper in that file.

## Specification Links

- `SPEC-2098`
- `ADR-0001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. This implements owner-authorized watchdog project scope under `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`.

## Prior Deliberations

- `DELIB-WI4561-CHROMADB-314-AUTHORIZE-20260614`
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`
- `bridge/gtkb-wi4562-delib-search-backend-doctor-001.md`
- `bridge/gtkb-wi4562-delib-search-backend-doctor-002.md`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-2098`, `ADR-0001` | The doctor check distinguishes healthy semantic backend state from ChromaDB unavailable, missing index, stale index, and probe-failure states. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The probe reads current SQLite deliberation rows and existing Chroma collection metadata directly; it does not rely on generated summaries. |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | The result is exposed through `gt project doctor` bridge-profile checks so the watchdog/service health surface can consume the same health signal. |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Degraded semantic-search state is a required doctor failure in bridge profiles and includes a concrete rebuild hint. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are under the approved GT-KB root target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / project-linkage DCL | Work ran after live claim and implementation authorization packet `sha256:9abd556c64a88b59b4ed808ac2c8f9f3f4b6a29a36ffb32f76806a0777e06439`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, and format checks passed; exact commands are below. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-wi4562-delib-search-backend-doctor --ttl-seconds 2400` - acquired live Prime Builder implementation claim.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4562-delib-search-backend-doctor` - passed; packet `sha256:9abd556c64a88b59b4ed808ac2c8f9f3f4b6a29a36ffb32f76806a0777e06439`.
- `python -m pytest platform_tests\scripts\test_deliberation_search_backend_doctor.py groundtruth-kb\tests\test_doctor.py -q --tb=short` - 48 passed.
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\tests\test_doctor.py platform_tests\scripts\test_deliberation_search_backend_doctor.py` - passed.
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\tests\test_doctor.py platform_tests\scripts\test_deliberation_search_backend_doctor.py` - passed.

## Observed Results

- Fresh Chroma metadata coverage returns a passing required doctor check.
- Stale metadata coverage returns a required doctor failure with `index_stale` and a rebuild command hint.
- `HAS_CHROMADB=False` returns a required doctor failure with `chromadb_unavailable`.
- A missing Chroma index path returns a required doctor failure without creating `.groundtruth-chroma` or opening a Chroma client.
- Synthetic `run_doctor(..., "dual-agent")` fixtures no longer crash when dispatcher-complex scripts are absent; they return diagnostic findings instead.

## Files Changed

Files changed by this WI:

- `groundtruth-kb/src/groundtruth_kb/db.py` - added `KnowledgeDB.deliberation_search_backend_status()` only; earlier WI-4563 uncommitted edits in this file are not claimed here.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor.py`
- `platform_tests/scripts/test_deliberation_search_backend_doctor.py`

Other dirty worktree files pre-existed or belong to concurrent bridge and project work and were not edited for this WI.

## Acceptance Criteria Status

- [x] Doctor check surfaces ChromaDB importability through the canonical `HAS_CHROMADB` path.
- [x] Doctor check reports canonical Chroma index path, collection availability, indexed chunks, indexed deliberation coverage, and current SQLite deliberation count.
- [x] Healthy semantic backend state is distinct from unavailable/degraded states.
- [x] Degraded backend state fails loudly in bridge-profile doctor runs.
- [x] Missing-index probing is read-only and does not create the Chroma directory.
- [x] Focused spec-derived tests, ruff check, and ruff format check pass.

## Risk And Rollback

Residual risk is low to moderate: the coverage comparison treats the Chroma metadata `delib_id` set as freshness evidence. That is stronger than chunk count alone, but it still does not validate embedding quality. Rollback is a revert of the four WI files above; bridge audit files remain append-only and must not be removed.

## Loyal Opposition Asks

1. Verify that bridge-profile doctor failure is appropriate for ChromaDB unavailable/missing/stale states while local-only profile remains unwired.
2. Verify that the read-only missing-index behavior satisfies `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.
3. Return `VERIFIED` if the implementation satisfies the approved proposal, otherwise return `NO-GO` with concrete target-path findings.
