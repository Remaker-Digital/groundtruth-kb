NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Prime Builder interactive; model GPT-5.5; reasoning effort Extra High

# Implementation Report - WI-4977 Headless Dispatch Stability

bridge_kind: implementation_report
Document: gtkb-wi4977-headless-dispatch-stability
Version: 007
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4977-headless-dispatch-stability-006.md (GO)

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4977-STABILITY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4977

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/ollama_harness.py", "scripts/bridge_thread_files.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_bridge_thread_files.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Implementation Summary

Implemented the WI-4977 stability repair within the approved target paths.

- Added `scripts/bridge_thread_files.py`, a shared exact bridge-thread helper that indexes only canonical `<slug>-NNN.md` files and ignores prefix siblings, drafts, and noncanonical markdown.
- Routed dispatcher latest-status reconciliation and dispatch-config terminal-status reconciliation through the exact helper.
- Hardened post-dispatch LO verdict reconciliation so timeout/nonzero exits count as success only after canonical exact thread advancement; when the selected top version is known, the verdict must be a later numbered version. `VERIFIED` reconciliation additionally requires git commit evidence for the exact verdict file.
- Added dispatcher-owned LO document leases for live runtime and daemon spawns, with release on failed launch and worker-exit reconciliation, so duplicated LO decisions suppress instead of spawning multiple workers on the same bridge document.
- Updated the Ollama LO system prompt to state the canonical advancement and atomic VERIFIED finalization rules it is judged against.

## Files Changed

- `scripts/bridge_thread_files.py`
- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/ollama_harness.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_thread_files.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the numbered bridge chain, role-correct authoring, and this Prime-authored implementation report following an LO `GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governs preserving concrete proposal/report links to the relevant specs and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - governs the spec-to-test mapping and executed command evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - governs the PAUTH/project/work-item metadata preserved in this report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governs preserving the owner-discovered dispatch-stability defect as bridge/work-item evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs durable source, test, bridge, and verification artifacts for this repair.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs treating the dispatch storm and stalled headless-worker behavior as formal artifact lifecycle triggers.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - governs keeping the repair in GT-KB platform paths rather than adopter application paths.
- `GOV-STANDING-BACKLOG-001` - governs keeping WI-4977 visible until LO verification and governed closure.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - governs preserving cross-harness bridge dispatch parity while Codex remains PB and Claude/Ollama are LO targets.

## Spec-to-Test Mapping

| Spec / Requirement | Executed | Evidence |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct bridge processing and LO verdict boundaries | yes | Runtime/daemon tests assert LO duplicate suppression, exact thread advancement, and post-verdict reconciliation without Prime authoring LO verdicts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | yes | Implementation stayed within the `-006` GO target paths and active WI-4977 PAUTH packet. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | yes | This report maps each implemented behavior to focused and full test commands below. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | yes | Report preserves PAUTH, Project, Work Item, Document, Version, and target path metadata. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | yes | Defect repair is preserved as WI-4977 bridge artifact plus source/test evidence; no scratchpad-only closure. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | yes | Changes are confined to GT-KB platform dispatcher/harness paths and platform tests; no adopter application paths changed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | yes | Codex remains selected PB dispatch target A; LO B/D remain quiesced pending VERIFIED/re-enable transaction. |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4977-headless-dispatch-stability
# PASS: packet_hash sha256:4546cc79f3092e7bbce200737c39db61b98bcd88d61dc7a403659daa2320a192; proposal_file bridge/gtkb-wi4977-headless-dispatch-stability-005.md; go_file bridge/gtkb-wi4977-headless-dispatch-stability-006.md; PAUTH WI-4977 active.

groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\bridge_thread_files.py scripts\dispatcher_runtime.py scripts\gtkb_dispatcher_daemon.py scripts\ollama_harness.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_bridge_thread_files.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_ollama_harness.py
# PASS: All checks passed.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\bridge_thread_files.py scripts\dispatcher_runtime.py scripts\gtkb_dispatcher_daemon.py scripts\ollama_harness.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_bridge_thread_files.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_ollama_harness.py
# PASS: 9 files already formatted.

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_thread_files.py platform_tests\scripts\test_dispatcher_runtime.py::test_latest_bridge_status_ignores_draft_and_prefix_sibling_files platform_tests\scripts\test_dispatcher_runtime.py::test_find_dispatch_verdict_ignores_draft_and_prefix_sibling_files platform_tests\scripts\test_dispatcher_runtime.py::test_find_dispatch_verdict_requires_canonical_version_advancement platform_tests\scripts\test_dispatcher_runtime.py::test_lo_nonzero_exit_with_post_launch_verdict_reconciles_success platform_tests\scripts\test_dispatcher_runtime.py::test_lo_nonzero_exit_with_fatal_marker_does_not_reconcile_noncanonical_verdict platform_tests\scripts\test_dispatcher_runtime.py::test_lo_max_turn_exit_with_canonical_verdict_reconciles_success platform_tests\scripts\test_dispatcher_runtime.py::test_verified_verdict_without_atomic_commit_remains_failure platform_tests\scripts\test_dispatcher_runtime.py::test_verified_verdict_with_atomic_commit_reconciles_success platform_tests\scripts\test_dispatcher_runtime.py::test_lo_live_spawn_acquires_document_lease_or_suppresses_duplicate platform_tests\scripts\test_gtkb_dispatcher_daemon.py::test_daemon_live_spawns_do_not_duplicate_lo_documents_across_targets platform_tests\scripts\test_ollama_harness.py::test_tool_loop_reconciles_success_only_after_canonical_bridge_advancement -q --tb=short
# PASS: 13 passed, 1 warning.

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_thread_files.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_ollama_harness.py -q --tb=short
# PASS: 235 passed, 1 warning.

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py -q --tb=short
# PASS: 56 passed, 1 warning.

gt bridge show gtkb-wi4977-headless-dispatch-stability --json
# PASS before report write: latest_status GO at bridge/gtkb-wi4977-headless-dispatch-stability-006.md.

gt bridge show gtkb-wi4977-headless-dispatch-stability --json
# PASS after report write: latest_status NEW at bridge/gtkb-wi4977-headless-dispatch-stability-007.md.

groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4977-headless-dispatch-stability
# PASS: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4977-headless-dispatch-stability
# PASS: exit 0; must_apply 3; evidence gaps 0; blocking gaps 0.

gt bridge dispatch status --json
# OBSERVED: health_status FAIL because LO dispatch remains owner-quiesced (B/D can_receive_dispatch=false) and pre-fix stale failure evidence remains in runtime state. Re-enable is intentionally not performed in this implementation report.
```

## Live-State Notes

- This implementation does not re-enable B or D. Per `-006`, B/D LO dispatch should remain quiesced until WI-4977 is VERIFIED and a separate governed dispatcher-config transaction re-enables them for soak.
- Fresh dispatch status before filing this report still shows Codex A as the selected Prime Builder target with `gpt-5.5`, Claude B pinned to `claude-opus-4-8`, and Ollama D pinned to `deepseek-v4-pro-cloud`.
- The status remains `FAIL` for expected current-state reasons: no active dispatchable LO target while quiesced, plus stale pre-fix runtime failure evidence.

## Rollback

Revert the nine changed source/test files listed above. No dispatcher eligibility or model-routing config was changed by this implementation.

## Verification Request

Loyal Opposition should verify:

1. The exact helper excludes prefix siblings, drafts, and edited current-top files.
2. Dispatcher/runtime and dispatch-config status reconciliation use the shared exact helper.
3. Live LO duplicate decisions suppress through document leases instead of double-spawning.
4. Ollama timeout/nonzero reconciliation requires canonical thread advancement and `VERIFIED` commit evidence.
5. The remaining live dispatch `FAIL` is due to the intentionally quiesced B/D state and pre-existing stale evidence, not a new regression from this implementation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
