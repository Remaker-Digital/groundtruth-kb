NEW

# WI-5029 Dispatch Cap Reconciliation - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5029-dispatch-cap-reconciliation
Version: 003
Responds to GO: bridge/gtkb-wi5029-dispatch-cap-reconciliation-002.md
Approved proposal: bridge/gtkb-wi5029-dispatch-cap-reconciliation-001.md
Date: 2026-07-05T09:39:07Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-05T09-28-32Z-prime-builder-A-44ac7b
author_model: GPT-5.5 via Codex
author_model_version: current Codex runtime
author_model_configuration: dispatcher auto-dispatch Prime Builder worker; approval_policy=never; sandbox=workspace-write

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5029-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5029
target_paths: ["scripts/dispatcher_runtime.py", "scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py", "platform_tests/scripts/test_bridge_dispatch_concurrency.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Implemented `WI-5029` by reconciling the live dispatcher per-role cap with the standalone WI-3375 dispatch-concurrency module.

The live dispatcher still uses the existing PID-sidecar live-worker accounting in `scripts/dispatcher_runtime.py`; that remains the least-risk live enforcement path because worker lifetime is already tracked by `run_with_status.py` sidecars. The reconciliation makes `scripts/bridge_dispatch_concurrency.py` the single source for role-specific limit defaults and per-role environment overrides:

- `loyal-opposition` default remains `3`.
- `prime-builder` default is now `2`, matching the WI-3375/S350 intended Prime range.
- `GTKB_DISPATCH_CONCURRENCY_LOYAL_OPPOSITION` and `GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER` are now live for the dispatcher because `dispatcher_runtime.py` calls `bridge_dispatch_concurrency.role_limit(...)`.
- Legacy `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE` remains supported as a positive-integer flat override for backward-compatible operator tuning.

The slot-file bounded-pool functions in `scripts/bridge_dispatch_concurrency.py` were not wired as the live dispatch gate. Its module docstring now explicitly says the live dispatcher imports the role-limit contract only, while live counting/enforcement remains PID-sidecar based. This prevents maintainers from mistaking `.gtkb-state/.../workers/<role>/slot-*.lock` files for live dispatcher capacity evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge review, latest `GO`, work-intent claim, and implementation-start authorization before protected source/test edits.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires implementation evidence to preserve the decision and verification trail in durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires proposal/report linkage to the governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires tests or verification mapped to the linked specifications before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - linked by the approved proposal as governance context for owner-authorized automation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - constrains the work to in-root GT-KB platform files.
- `GOV-STANDING-BACKLOG-001` - governs `WI-5029` as a MemBase work item and bridge-scoped backlog execution unit.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - preserves Codex hook/dispatch behavior while retaining explicit self-enforcement and deterministic command paths.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires durable artifacts and tests for the reconciled behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs the transition from approved proposal to implementation-report evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires dispatch behavior to remain centralized and deterministic in the dispatcher service.
- `ADR-DISPATCHER-ARCHITECTURE-001` - requires dispatcher-owned dispatch control without reintroducing harness-triggered runtime control.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - favors cheap deterministic dispatch gating over launching workers to discover saturation.

## Owner Decisions / Input

Owner approval is carried by `DELIB-20260705-WI5029-5031-IMPLEMENT-AUTHORIZATION` and active project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5029-IMPLEMENTATION-PROPOSAL-FILING`. No new owner decision was required or requested in this auto-dispatch worker.

## Prior Deliberations

- `DELIB-20260705-WI5029-5031-IMPLEMENT-AUTHORIZATION` - owner decision authorizing implementation of `WI-5029`, `WI-5030`, and `WI-5031`.
- `bridge/gtkb-wi5029-dispatch-cap-reconciliation-001.md` - approved implementation proposal for this work.
- `bridge/gtkb-wi5029-dispatch-cap-reconciliation-002.md` - Loyal Opposition `GO` verdict authorizing implementation.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-001.md` - CA9165 live per-role cap lineage.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md` - WI-3375 slot-module lineage.

## Specification-Derived Verification

| Specification | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5029-dispatch-cap-reconciliation --json --compact` returned latest `GO` at `-002`; `bridge_claim_cli.py status gtkb-wi5029-dispatch-cap-reconciliation` returned active `go_implementation` claim rowid `30049` for this dispatch session; `implementation_authorization.py begin --bridge-id gtkb-wi5029-dispatch-cap-reconciliation` produced packet `sha256:d8db8b93852f78400bdc52f6a91ee4028af4273d86fc60c63d0e5dbbc81d7736`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This implementation report records the chosen reconciliation, the retained legacy override, the non-wired slot-pool decision, and command evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The report carries forward all linked specifications from the approved proposal; `bridge_applicability_preflight.py --bridge-id gtkb-wi5029-dispatch-cap-reconciliation` passed with `missing_required_specs: []` and `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest` executed the focused dispatcher cap and slot-module test suites: `29 passed, 1 warning`; this table maps linked specs to executed evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation authorization packet includes PAUTH, project, work item, and `target_path_globs` for the approved source/test files. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No new owner decision was taken; existing owner authorization and PAUTH are cited in the report instead of prose approval. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed files are in root-contained GT-KB platform paths under `scripts/` and `platform_tests/`; no Agent Red or external path was touched. |
| `GOV-STANDING-BACKLOG-001` | `WI-5029` is implemented through the selected bridge thread and this post-implementation report, preserving backlog-to-bridge traceability. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The worker used explicit self-enforcement: durable role read, live bridge scan, work-intent status, and implementation-start packet before edits. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Behavior is covered by committed source/test changes plus this bridge report rather than a session-only note. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This `NEW` implementation report moves the approved `GO` thread to Loyal Opposition verification without deleting or rewriting prior bridge files. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Runtime cap resolution remains in `scripts/dispatcher_runtime.py`; tests verify the centralized live gate suppresses at cap, allows below cap, and keeps global-cap precedence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The slot-file pool was not wired into worker lifecycle from the harness side; live enforcement remains dispatcher-owned PID-sidecar logic. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Runtime still performs a cheap pre-spawn cap check using sidecar counts and role-limit config; no worker launch is needed to discover role saturation. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json`
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5029-dispatch-cap-reconciliation --json --compact`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5029-dispatch-cap-reconciliation`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi5029-dispatch-cap-reconciliation`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check --fix scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py -q --tb=short --basetemp .gtkb-state/pytest-wi5029-dispatch-cap-reconciliation-20260705T0935` with pytest cacheprovider disabled.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py -q --tb=short --basetemp .gtkb-state/pytest-wi5029-dispatch-cap-reconciliation-20260705T0942` with pytest cacheprovider disabled.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_bridge_dispatch_concurrency.py`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5029-dispatch-cap-reconciliation`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5029-dispatch-cap-reconciliation`

## Observed Results

- Durable role check: harness `A` / `codex` is assigned `prime-builder`.
- Live bridge state before mutation: `latest_status: GO`, `latest_path: bridge/gtkb-wi5029-dispatch-cap-reconciliation-002.md`.
- Work-intent claim: rowid `30049`, `claim_kind: go_implementation`, session `2026-07-05T09-28-32Z-prime-builder-A-44ac7b`, not expired.
- Implementation-start packet: `packet_hash: sha256:d8db8b93852f78400bdc52f6a91ee4028af4273d86fc60c63d0e5dbbc81d7736`, `target_path_globs` limited to the approved four files.
- First pytest attempt using the default temp root failed before assertions with `PermissionError: [WinError 5] Access is denied: 'C:\Users\micha\AppData\Local\Temp\pytest-of-micha'`.
- Final focused pytest run with repo-local basetemp: `29 passed, 1 warning in 0.72s`. The warning is the repository's existing `PytestConfigWarning: Unknown config option: asyncio_mode`.
- Ruff lint: `All checks passed!`.
- Ruff format check: `4 files already formatted`.
- Applicability preflight: passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- Clause preflight: exit 0, clauses evaluated `5`, must-apply evidence gaps `0`, blocking gaps `0`.
- Diff-line-ending cleanup: `scripts/bridge_dispatch_concurrency.py` was normalized back to LF after formatter output produced CRLF noise; final `git ls-files --eol` showed `w/lf` for changed files.

## Files Changed

- `scripts/dispatcher_runtime.py` - imports `bridge_dispatch_concurrency.role_limit`, resolves live per-role caps through the shared role-specific contract, preserves legacy flat `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`, and passes the target role into the cap resolver.
- `scripts/bridge_dispatch_concurrency.py` - clarifies that `role_limit()` is live-wired for defaults/overrides while the slot-file pool remains a standalone primitive and not live capacity evidence.
- `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py` - covers LO=3 and Prime=2 defaults, per-role env override, legacy flat override, Prime at-cap suppression, LO at-cap suppression, below-cap spawn, role-scoped counts, and global-cap precedence.

Approved target left intentionally unchanged:

- `platform_tests/scripts/test_bridge_dispatch_concurrency.py` - retained as the slot-module regression suite and rerun successfully.

## Recommended Commit Type

Recommended commit type: `feat:`

Justification: this changes live dispatcher runtime behavior by making role-specific Prime/LO caps authoritative, while preserving the legacy flat override and adding focused regression coverage.

## Acceptance Criteria Status

- [x] One authoritative per-role default contract is used by live dispatch: `bridge_dispatch_concurrency.DEFAULT_ROLE_LIMITS` / `role_limit()`.
- [x] Live enforcement remains dispatcher-owned and deterministic through PID-sidecar counts.
- [x] Role-scoped defaults are reconciled: LO default `3`, Prime default `2`.
- [x] Legacy flat override remains available for backward-compatible operator tuning.
- [x] Tests prove at-cap suppression, below-cap spawning, role-scoped counts, role-specific defaults, per-role env override, legacy flat override, and global-cap precedence.
- [x] The slot module is documented so maintainers do not mistake slot files for live dispatcher worker evidence.

## Risk And Rollback

Residual risk: the Prime Builder default live cap is now lower (`2`) unless an operator sets either `GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER` or legacy `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`. This matches the WI-3375/S350 Prime range cited by the approved proposal and reduces Prime-side saturation risk.

Rollback is a revert of the three changed files. Bridge files remain append-only and must not be deleted.

## Loyal Opposition Asks

Verify that the implementation satisfies the approved reconciliation: live dispatch uses the shared role-limit contract, the slot-file pool is not misrepresented as live capacity evidence, and the focused tests provide sufficient coverage for the linked specifications.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
