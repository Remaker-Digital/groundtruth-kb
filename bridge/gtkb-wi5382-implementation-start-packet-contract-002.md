GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5382 Implementation Start Packet Contract

bridge_kind: loyal_opposition_review
Document: gtkb-wi5382-implementation-start-packet-contract
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5382
Reviewed: bridge/gtkb-wi5382-implementation-start-packet-contract-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5382-implementation-start-packet-contract` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5382-implementation-start-packet-contract` → 0 blocking gaps

This proposal directly addresses the systemic implementation-start failure observed across multiple threads (WI-5230, WI-5287, WI-5299, WI-5316, WI-5318, WI-5354, WI-5355, WI-5359, WI-5360, WI-5364, WI-5365, WI-5366), where `implementation_authorization.py begin` reportedly produced no named schema-v3 packet and no actionable diagnostic.

The scope is bounded to `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`. It requires the CLI to either emit the exact schema-v3 packet JSON and durably write the bridge-named cache before `current.json`, or exit nonzero with deterministic JSON denial and create no packet state.

## Conditions

- `--no-write` must remain a diagnostic-only mode that prints the pre-start packet and writes no files.
- Denied attempts must be side-effect-free for packet state.
- Shared-path conflict, PAUTH operation-time, target-path bounds, latest bridge status, worker-role provenance, and current named-packet fallback semantics must be preserved.
- Any pre-existing dirty target bytes must be hunk-attributed in the implementation report.
