GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5392 Make Rehearsal Outside-Legacy Fixture Root-Relative

bridge_kind: loyal_opposition_review
Document: gtkb-wi5392-rehearse-outside-root-fixture
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5392
Reviewed: bridge/gtkb-wi5392-rehearse-outside-root-fixture-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5392-rehearse-outside-root-fixture` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5392-rehearse-outside-root-fixture` → 0 blocking gaps

Independent verification of the current baseline:
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=600` → **67 passed, 1 failed, 1 warning in 1.32s**
- The single failure is `test_target_root_allowed_outside_legacy_root`, exactly as the proposal states.
- The failure reason matches the proposal: `tmp_path` is under the GT-KB root, so the production validator correctly rejects it.

The proposal is a one-fixture correction that uses `monkeypatch` to create a synthetic legacy boundary under `tmp_path` while keeping all scratch paths inside the GT-KB root. Production code and refusal cases remain unchanged.

## Conditions

- Only `platform_tests/scripts/test_rehearse_isolation.py` may be edited.
- The fix must use `monkeypatch` to patch only the imported rehearsal module constants, not production constants.
- All existing refusal cases must remain green.
- The separately owned WI-5381 relocation failure must not be masked or waived.
- Independent VERIFIED must precede any mechanical finalization.
