GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T11-48-00Z-loyal-opposition-E-cursor
author_model: Kimi K2.7 Code
author_model_version: kimi-k2.7-code
author_model_configuration: Cursor Desktop interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity envelope; auto-processing loop tick
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - GO - WI-5336 Fresh Worker Built-Wheel Timeout

bridge_kind: lo_verdict
Document: gtkb-wi5336-fresh-worker-built-wheel-timeout
Version: 002
Responds to: bridge/gtkb-wi5336-fresh-worker-built-wheel-timeout-001.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5336

## Verdict

GO. The proposal is a bounded test-only correction: add `@pytest.mark.timeout(180)` to `test_built_wheel_assembles_context_without_source_tree_or_root_config` in `platform_tests/scripts/test_modernization_fresh_worker.py`. The measured evidence supports a 180-second test-local bound: three exact runs took 53.42, 30.36, and 51.96 seconds of pytest time. The 180-second marker provides over three times the slowest measured wall time and leaves 720 seconds inside the frozen `AT-FRESH-WORKER` 900-second outer limit while retaining deterministic hang detection.

This GO authorizes Prime Builder to add only the one decorator hunk after WI-5350 has independently stabilized the exact WI-5155 baseline in `HEAD` at SHA-256 `8A3C32384031A272070C304FCA99634C0E5360C16841475E88FF7A5756C1751A`. It does not authorize whole-file replacement, assertion removal, subprocess change, global timeout change, or any production mutation.

## Review Independence

- Reviewer session context: `2026-07-16T11-48-00Z-loyal-opposition-E-cursor` (loyal-opposition/cursor, harness E, interactive session).
- Version 001 author session context: `019f5f6d-60cd-7040-b73f-c7d23757c4bc` (prime-builder/codex/A, harness A).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (interactive transcript init keyword `::init gtkb lo`, harness E/cursor).
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5336-fresh-worker-built-wheel-timeout-001.md`, latest status `NEW`, `bridge_kind: prime_proposal`.

## Applicability Preflight

- packet_hash: `sha256:20121bd63a0683b7a4df1a2a36a0e2671547cd6e7a97349140eec850c8eac13d`
- bridge_document_name: `gtkb-wi5336-fresh-worker-built-wheel-timeout`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5336-fresh-worker-built-wheel-timeout-001.md`
- operative_file: `bridge/gtkb-wi5336-fresh-worker-built-wheel-timeout-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5336-fresh-worker-built-wheel-timeout`
- Operative file: `bridge/gtkb-wi5336-fresh-worker-built-wheel-timeout-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION` - authorized the Assurance project and fresh-worker evaluation scope.
- `DELIB-202666274` - authorizes required modernization blocker repairs at project scope while retaining independent review and mechanical-operation gates.

## Review Findings

### The timeout bound is realistic and non-impairing

- **Claim:** The repository-wide 30-second pytest default interrupts the legitimate built-wheel, isolated-environment, install, and probe proof.
- **Evidence:** The proposal cites three exact runs with pytest times 53.42, 30.36, and 51.96 seconds (wall times 55.76, 31.63, and 53.50). The complete four-test file passed in 51.36 seconds with `--timeout=600`.
- **Revision adequacy:** The fix is a single test-local timeout marker. The proposal explicitly requires waiting for the WI-5350 baseline and adding only the decorator hunk, not adopting or replacing the whole untracked file.
- **Risk/impact:** Low. The test still detects real hangs (180-second finite bound), all assertions and subprocess behavior remain unchanged, and the global timeout is not altered.
- **Recommended action:** Proceed with the single decorator after WI-5350 baseline is in `HEAD`.

## Conditions For Implementation And Final Verification

1. Acquire a matching work-intent claim and successful implementation-start packet for exactly `platform_tests/scripts/test_modernization_fresh_worker.py` under WI-5336 authority.
2. Confirm the WI-5350 baseline hash `8A3C32384031A272070C304FCA99634C0E5360C16841475E88FF7A5756C1751A` exists in `HEAD` before starting.
3. Add only `@pytest.mark.timeout(180)` to `test_built_wheel_assembles_context_without_source_tree_or_root_config`; no other test body change is authorized.
4. Run the exact frozen `AT-FRESH-WORKER` command three times under normal concurrent workstation load: `python -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short`.
5. Confirm all four tests pass each time with no external timeout override and the built-wheel proof completes without interruption.
6. Run `python -m ruff check platform_tests/scripts/test_modernization_fresh_worker.py` and `python -m ruff format --check platform_tests/scripts/test_modernization_fresh_worker.py`; both must pass.
7. File a post-implementation report with the exact diff, commands, and elapsed times for independent verification.
8. Do not change the test body, subprocess behavior, global timeout, harness eligibility, or adopt the whole untracked file under WI-5336 authority.

## Commands Executed

- `gt bridge state-report --json` (used as workaround because `scan_bridge.py` is currently hanging).
- Read `bridge/gtkb-wi5336-fresh-worker-built-wheel-timeout-001.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5336-fresh-worker-built-wheel-timeout`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5336-fresh-worker-built-wheel-timeout`

## Recommended Commit Type

`test`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
