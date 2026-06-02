NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019e87ff-698c-7002-beb1-0f5a8788e643
author_model: GPT-5
author_model_version: 2026-06-02
author_model_configuration: codex-desktop

# GT-KB Bridge Implementation Report - gtkb-bridge-index-chain-deviation-detector - 003

bridge_kind: implementation_report
Document: gtkb-bridge-index-chain-deviation-detector
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-bridge-index-chain-deviation-detector-002.md
Approved proposal: bridge/gtkb-bridge-index-chain-deviation-detector-001.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4235
Implementation-start packet: sha256:5bfd3a67f87882f165a51d33075b60106091fe8287a838595efcecaddc37c060
Recommended commit type: feat:

## Implementation Claim

Implemented the read-only WI-4235 bridge INDEX/file-chain deviation detector. The detector compares fresh `bridge/INDEX.md` with on-disk `bridge/*.md` files, classifies chain defects, and emits deterministic JSON/markdown output with candidate repair actions for later correction-packet work. It does not edit bridge files or `bridge/INDEX.md`.

## Requirement Sufficiency

Implementation proceeded under owner-deliberation sufficiency evidence `DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY`, recorded by implementation-start packet `sha256:5bfd3a67f87882f165a51d33075b60106091fe8287a838595efcecaddc37c060`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

## Owner Decisions / Input

- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` - owner authorized the bridge reconciliation project and WI-4234 through WI-4238 implementation proposal batch.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY` - owner sufficiency evidence used by the implementation-start packet because the approved proposal phrasing did not match the strict parser form.
- `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` - active project authorization for this work item.

## Prior Deliberations

- `bridge/gtkb-bridge-index-chain-deviation-detector-001.md` - approved implementation proposal.
- `bridge/gtkb-bridge-index-chain-deviation-detector-002.md` - Loyal Opposition GO verdict.
- `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP`
- `DELIB-2414`
- `DELIB-0870`
- `DELIB-2358`
- `DELIB-2421`

## Files Changed

- `scripts/bridge_index_chain_audit.py` - new shared read-only bridge INDEX/file-chain detector and script entrypoint.
- `platform_tests/scripts/test_bridge_index_chain_audit.py` - focused tests for missing files, unindexed files, duplicate rows, skipped versions, status mismatches, responds-to mismatches, read-only behavior, and CLI JSON.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - added `gt bridge reconcile index-chain`.

`scripts/bridge_reconciliation_audit.py` remains unchanged in this slice. The existing backlog reconciliation audit keeps its current schema while the new index-chain detector provides a bridge-artifact-specific companion command.

## Implemented Behavior

- Added deterministic parsing for live `bridge/INDEX.md` document blocks, status rows, line numbers, paths, and versions.
- Added on-disk bridge file scanning for first status token, `Document:` header, and `Responds to:` references.
- Added chain-deviation classifications:
  - `index_references_missing_file`
  - `index_status_body_mismatch`
  - `document_header_mismatch`
  - `duplicate_index_version`
  - `duplicate_index_path`
  - `missing_intermediate_versions`
  - `latest_index_not_highest_indexed_version`
  - `latest_index_omits_highest_file`
  - `responds_to_mismatch`
  - `versioned_bridge_file_unindexed`
- Added correction-packet-ready finding fields: `candidate_repair_actions`, `risk_notes`, `evidence`, `severity`, and `recommended_action`.
- Added JSON and markdown/operator summary output.
- Added CLI surface: `gt bridge reconcile index-chain --json`.
- Preserved read-only behavior; no command path performs bridge or MemBase mutation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused tests prove fresh INDEX/file-chain reads and no alternate queue; live smoke read used `E:\GT-KB\bridge\INDEX.md`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | JSON findings include durable evidence, recommended action, risk notes, and candidate repair actions. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_index_chain_audit_reports_requested_deviation_types` covers chain defects that change bridge artifact lifecycle state. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passed for the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, adjacent reconciliation pytest, ruff lint, ruff format, and live CLI smoke commands were executed and passed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation report carries Project Authorization, Project, and Work Item metadata. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Detector emits correction candidates only; it does not batch owner decisions or apply correction packets. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All modified target paths are under `E:\GT-KB`. |
| `GOV-STANDING-BACKLOG-001` | Detector is bridge-artifact-only and does not inspect or mutate backlog rows. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Command is exposed through deterministic repo CLI usable by Codex or Claude. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Findings are structured artifacts suitable for follow-on WI-4236 correction packets. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-bridge-index-chain-deviation-detector --owner-sufficiency-deliberation-id DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_index_chain_audit.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-bridge-index-chain-0602b`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_reconciliation_audit.py platform_tests\scripts\test_bridge_index_chain_audit.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-bridge-reconcile-combined-0602`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\bridge_reconciliation_audit.py scripts\bridge_backlog_terminal_reconciliation.py scripts\bridge_index_chain_audit.py platform_tests\scripts\test_bridge_reconciliation_audit.py platform_tests\scripts\test_bridge_index_chain_audit.py groundtruth-kb\src\groundtruth_kb\cli.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\bridge_reconciliation_audit.py scripts\bridge_backlog_terminal_reconciliation.py scripts\bridge_index_chain_audit.py platform_tests\scripts\test_bridge_reconciliation_audit.py platform_tests\scripts\test_bridge_index_chain_audit.py groundtruth-kb\src\groundtruth_kb\cli.py`
- `groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.cli import main; main()" bridge reconcile index-chain --json`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-chain-deviation-detector`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-chain-deviation-detector`
- `groundtruth-kb\.venv\Scripts\gt.exe deliberations search "bridge index chain deviation detector WI-4235"`

## Observed Results

- Implementation-start packet succeeded with `latest_status: GO`, `project_authorization.status: active`, and target path globs limited to `scripts/bridge_index_chain_audit.py`, `scripts/bridge_reconciliation_audit.py`, `platform_tests/scripts/test_bridge_index_chain_audit.py`, and `groundtruth-kb/src/groundtruth_kb/cli.py`.
- Focused pytest: `3 passed, 1 warning in 0.82s`. Warning was an existing `.pytest_cache` cache-path warning.
- Combined adjacent pytest: `7 passed, 1 warning in 1.68s`. Warning was the same cache-path warning.
- Ruff check: `All checks passed!`
- Ruff format check: `6 files already formatted`.
- Live CLI smoke exited 0 and produced bounded summary from JSON: `bridge_document_count=184`, `bridge_file_count=4925`, `issue_count=3896`, with counts by type:
  - `document_header_mismatch: 17`
  - `index_status_body_mismatch: 1`
  - `latest_index_omits_highest_file: 2`
  - `missing_intermediate_versions: 1`
  - `responds_to_mismatch: 13`
  - `versioned_bridge_file_unindexed: 3862`
- Applicability preflight passed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- ADR/DCL clause preflight exited 0 with `Evidence gaps in must_apply clauses: 0`, `Blocking gaps (gate-failing): 0`.
- Deliberation search returned 5 related deliberations, including `DELIB-2358` and `DELIB-2421`.

## Acceptance Criteria Status

- [x] Command detects absent files referenced by INDEX.
- [x] Command detects bridge files not referenced by INDEX.
- [x] Command detects duplicate INDEX version/path rows.
- [x] Command detects missing intermediate versions.
- [x] Command detects latest INDEX/file-chain disagreements.
- [x] Command detects `Responds to:` chain mismatches.
- [x] Command emits correction-packet-ready JSON with candidate repair actions, evidence paths, and risk notes.
- [x] Command does not edit `bridge/INDEX.md`, bridge documents, MemBase, projects, or deliberations.

## Residual Risk / Follow-Up

The live detector currently reports heavy historical bridge noise, especially `versioned_bridge_file_unindexed`. This is expected because many old versioned bridge files are no longer present in live `bridge/INDEX.md`. WI-4236 should classify historical pruned files, parked drafts, and true live drift before any correction packet proposes edits.

## Risk And Rollback

Risk is limited to false-positive reporting because the detector is read-only. Rollback is to remove the CLI registration, `scripts/bridge_index_chain_audit.py`, and `platform_tests/scripts/test_bridge_index_chain_audit.py`. No data rollback is required.

## Recommended Commit Type

`feat:` - this adds a net-new deterministic bridge chain audit service and CLI surface.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the read-only detector and report satisfy the approved proposal, otherwise return NO-GO with findings.
