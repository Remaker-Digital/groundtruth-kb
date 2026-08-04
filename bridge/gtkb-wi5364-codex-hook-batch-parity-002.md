GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: 6c8b300-ddc8-4f79-b47c-e0da3ca6a55f
author_model: Fireworks kimi-k2p7-code
author_model_configuration: Cursor interactive Loyal Opposition; transcript-defined LO role
author_metadata_source: bridge_function_provenance_repair_from_legacy_reviewer_identity
reviewer_identity: loyal-opposition/cursor/E
reviewer_harness_id: E
reviewer_session_context_id: 6c8b300-ddc8-4f79-b47c-e0da3ca6a55f
reviewer_model: Fireworks kimi-k2p7-code
reviewer_model_configuration: Cursor interactive Loyal Opposition; transcript-defined LO role

# Loyal Opposition Verdict - Restore Live Codex Hook Parity Without Duplicate Execution

bridge_kind: lo_verdict
Document: gtkb-wi5364-codex-hook-batch-parity
Version: 002
Responds to: bridge/gtkb-wi5364-codex-hook-batch-parity-001.md
Work Item: WI-5364
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE

## Verdict

GO

## Summary

The proposal restores the live Codex hook surface on Windows by enabling the existing no-window batch topology, removing the wrap-up adapter's explicit `--role-profile` override, and updating the parity checker/tests to recognize declarative batch fan-out. The scope is bounded to four declared targets, and the proposal explicitly preserves the unrelated `sandbox_mode` pre-start hunk in `.codex/config.toml`.

## Preflight Checks

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5364-codex-hook-batch-parity` - **passed** (prelight_passed: true; no missing required specs)
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5364-codex-hook-batch-parity` - **passed** (0 blocking gaps)

## Assessment

- The approach avoids duplicate handler registration by teaching the parity checker to expand declarative batches rather than re-registering handlers.
- Key requirements are linked: ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-HARNESS-ROLE-PORTABILITY-001, DCL-SESSION-ROLE-RESOLUTION-001, and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001.
- The expected baseline shows the current checker reports 8 findings; the proposal aims to reduce that to 0 while adding focused fixtures for batch validity, missing surfaces, and direct-wrapper compatibility.
- The rollback plan preserves the foreign config hunk and all existing batch registrations.

## Recommendation

Approved to proceed with implementation. Verification must confirm the parity checker passes with zero findings, the no-window batch tests remain green, and the `sandbox_mode` hunk is byte-preserved. Atomic finalization of this verdict is deferred due to the current uncommitted predecessor bridge chain.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
