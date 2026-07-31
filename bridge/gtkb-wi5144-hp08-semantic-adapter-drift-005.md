NEW

# WI-5144 HP08 Semantic Adapter Drift - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5144-hp08-semantic-adapter-drift
Version: 005
Responds to GO: bridge/gtkb-wi5144-hp08-semantic-adapter-drift-004.md
Approved proposal: bridge/gtkb-wi5144-hp08-semantic-adapter-drift-003.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5144
target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py"]
Recommended commit type: feat:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder

## Implementation Claim

The parity checker now renders the expected Codex, Antigravity, or API adapter
through the corresponding canonical generator and compares the generated
semantic body with the live adapter body after removing only volatile marker
metadata. Existing path, source-hash, marker, and loadability checks remain in
front of the new comparison. A hash-current adapter whose executable text
contradicts its canonical source is therefore `STALE` instead of `PASS`.

The Codex test fixture now models the real generator shape, and a negative test
mutates only the adapter body while preserving current source-path and hash
metadata. Both target files were clean against HEAD before implementation; this
scope owns their complete current HEAD-relative diffs. No dispatcher, TAFE,
harness, eligibility, source registry, generated adapter, Git index, commit,
push, release, deployment, or credential state was changed.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Owner Decisions / Input

`DELIB-202666274` authorizes the modernization implementation program while
preserving independent GO, implementation-start, verification, and mechanical
finalization gates. No new owner decision is required for this report. The
owner's dispatchability correction is preserved: this implementation performs
no harness eligibility or routing operation.

## Prior Deliberations

- `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-003.md` - approved bounded
  two-file proposal.
- `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-004.md` - independent GO.
- `DELIB-202666274` - controlling project-level modernization authority.

## Specification-Derived Verification Plan

| Specification | Executed evidence and result |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Canonical generators define expected adapter behavior; live Codex, Antigravity, Ollama, and OpenRouter checks emitted zero semantic findings. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Positive current-adapter and negative source/hash/body cases execute through the production `_status_for_surface` path. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Unsupported/fallback classifications remain unchanged; only `status = "adapter"` receives the new fail-closed semantic check. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Frozen `MOD-HP08` negative test passes and rejects a hash-current contradiction. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | 24 focused parity tests pass; Ruff, formatting, diff checks, and four live harness reports pass without semantic false positives. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | HEAD-relative files have recorded Git blob IDs and SHA-256 values; generator-derived comparison is deterministic. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | GO, live claim, and implementation-start preceded both edits; packet hashes are recorded below. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All nineteen approved specification links are carried forward and mapped here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Positive, stale-source, stale-semantic, frozen-clause, live-harness, lint, format, and diff evidence was executed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header binds the PAUTH, project, WI-5144, and exact two target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Operation-time evaluator allowed source plus test mutation under Harness Parity PAUTH v2. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Pre-start packet `sha256:1ad283a832d094c286cdf433ebc19e17802141e33999c920906975eb05c23710`; implementation packet `sha256:20cb3f8f8664d0fd6367ea94e06239dfda306c03caa1136030894df285b0470a`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5144, proposal, GO, exact implementation, report, and pending independent verdict form one traceable chain. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The semantic defect is represented by production logic plus an executable negative regression artifact. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This NEW report requests independent verification and does not claim terminal closure. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changes remain inside the GT-KB platform checker/test boundary and do not touch Agent Red. |
| `GOV-STANDING-BACKLOG-001` | Work remains linked to WI-5144 until independent VERIFIED reconciliation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex adapter semantics are checked through the canonical Codex generator rather than assumed from metadata. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No owner question or AUQ-dependent behavior was added or changed. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_harness_parity.py::test_generated_adapter_passes_when_hash_matches platform_tests/scripts/test_check_harness_parity.py::test_generated_adapter_reports_stale_when_source_hash_changes platform_tests/scripts/test_check_harness_parity.py::test_generated_adapter_reports_stale_when_semantics_conflict_with_current_hash platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py::test_mod_hp08_semantic_skill_drift_is_rejected_even_when_adapter_hash_metadata_is_current -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short -k 'not repository_registry_has_no_unclassified_missing_rows'`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/check_harness_parity.py --harness <codex|antigravity|ollama|openrouter> --all --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py`
- `git diff --check HEAD -- scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py`
- In-memory baseline: pipe `git show HEAD:scripts/check_harness_parity.py` to Python, load that exact HEAD source, and run `check_harness_parity(Path.cwd(), include_all=True)` without writing a file.

## Observed Results

- Four specification-derived tests: `4 passed`; one pre-existing unknown
  `asyncio_mode` warning.
- Focused parity module: `24 passed, 1 deselected`; the deselected repository
  inventory assertion currently fails only because concurrent Goose adoption
  exposes 67 missing Goose capability rows.
- HEAD-baseline execution proves the same unrelated condition: the exact HEAD
  checker reports `HEAD_MISSING_COUNT=67`, `HEAD_MISSING_HARNESSES=goose`.
- A broader exploratory run produced `37 passed, 12 failed`; MOD-HP08 passed.
  Eleven failures are other open modernization clauses, and the twelfth is the
  same HEAD-existing Goose inventory gap. None is attributed to WI-5144.
- Live Codex: `DEGRADED=3, PASS=57, UNSUPPORTED=11`, zero semantic findings.
- Live Antigravity, Ollama, and OpenRouter: each `PASS=43,
  UNSUPPORTED=28`, zero semantic findings.
- Ruff check: `All checks passed!`.
- Ruff format: `2 files already formatted`.
- Diff check: exit 0; only the existing Windows LF/CRLF warning appeared.

## Exact Candidate Identity

- `scripts/check_harness_parity.py`
  - Git blob: `81da2f5682bf1ecd2d36de4d7b61c976c11ea8e8`
  - SHA-256: `7C86B29EBD326C5323D2F500A9B822801B4CFBA9295B901C5F695FE6EC529A7F`
- `platform_tests/scripts/test_check_harness_parity.py`
  - Git blob: `bdc7d15b7303a1e098be83f86cb14b00b466af84`
  - SHA-256: `0F8DA85C7AC4F7F2B05C11435443B9F98E12CBBEE2070FEA68505C59BDFA53B8`
- Diffstat: `2 files changed, 132 insertions(+), 23 deletions(-)`.

## Files Changed

- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity.py`

## Acceptance Criteria Status

- PASS: a hash-current contradictory Codex adapter is classified `STALE`.
- PASS: expected semantics come from the canonical Codex, Antigravity, and API
  generators, not from duplicated hash declarations.
- PASS: positive current adapters and existing stale-source behavior remain
  covered and passing.
- PASS: live applicable harnesses show no semantic false positives.
- PASS: no routing, dispatchability, registry, generated adapter, or Git-index
  mutation occurred.
- PENDING: independent VERIFIED and atomic exact-path finalization.

## Risk And Rollback

The checker now imports the three canonical generator modules, so future
generator changes immediately become the semantic standard. That coupling is
intentional and removes a second hand-maintained equivalence definition. The
remaining worktree-capture risk is mechanical: LO must finalize only these two
clean-pre-start files through an isolated index or equivalent atomic exact-path
finalizer, never the broad real index. Rollback is the inverse of their exact
HEAD-relative patch.

## Loyal Opposition Asks

1. Reconstruct only the two target files from HEAD and the exact current diff.
2. Rerun the four specification-derived tests, focused 24-test slice, four live
   harness checks, Ruff check/format, and diff check.
3. Confirm the HEAD-baseline Goose inventory gap is unrelated and unchanged.
4. Return VERIFIED only through an atomic exact-path finalizer that cannot
   absorb unrelated staged or unstaged worktree changes.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
