REVISED

# Revised Proposal - WI-5012 Dispatch Selection-Binding and SoT Consolidation

bridge_kind: prime_proposal
Document: gtkb-dispatch-selection-binding-sot-consolidation
Version: 003 (REVISED; metadata-validity correction after unusable GO)
Author: Prime Builder (Codex)
Date: 2026-07-05T07:34:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012
Project: PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION
Work Item: WI-5012

target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py", "groundtruth-kb/tests/test_harness_projection.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: source | config | kb | test | report
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

This revision carries forward the implementation scope from `bridge/gtkb-dispatch-selection-binding-sot-consolidation-001.md` unchanged.

Prime Builder attempted the required implementation-start gate after `bridge/gtkb-dispatch-selection-binding-sot-consolidation-002.md` recorded `GO` and before editing protected files:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation
```

Observed result: exit `1`, `authorized=false`.

```json
{
  "authorized": false,
  "error": "Self-review GO refused (author_session_context_missing): the GO verdict author session (None) and the proposal author session ('019f23f0-b16e-7481-8a18-9622ab564d50') must be present, distinct, and independent (WI-4829; GOV-DOCUMENT-AUTHOR-PROVENANCE-001)."
}
```

The `-002` verdict is substantively a GO, but it uses `reviewer_session_context_id` and does not include the machine-required `author_session_context_id`. The implementation-start gate therefore correctly fails closed. No protected implementation files have been modified under WI-5012.

## Requested Loyal Opposition Action

Please reissue the WI-5012 GO as the next bridge version if the substantive review still stands, with the same findings and a valid machine-readable `author_session_context_id` line for the LO verdict author session.

No implementation scope, target path, owner decision, requirement sufficiency, or verification plan change is requested in this revision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `REQ-HARNESS-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-SOT-SINGLETON-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202665442` - owner selected harness registry/MemBase as the single authoritative home for the five duplicated dispatch fields.
- `DELIB-202665446` - owner selected Claude/B as headless-eligible and first-class selectable for headless LO work.
- `DELIB-202665447` - owner selected the threshold-filter plus per-lane objective model.
- `DELIB-202665449` - owner selected weekly capability-adjust as GO-required proposal generation, never auto-apply.
- `DELIB-202665441`, `DELIB-202665444`, `DELIB-202665455` - SoT-singleton umbrella decisions.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-001.md` - original WI-5012 proposal, carried forward by this revision.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-002.md` - substantively positive GO verdict with missing machine-required verdict author-session metadata.

## Owner Decisions / Input

No new owner decision is required.

Carried-forward owner/project authority:

- `DELIB-202665442`
- `DELIB-202665446`
- `DELIB-202665447`
- `DELIB-202665449`
- `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012`

## Requirement Sufficiency

Existing requirements remain sufficient. This revision only repairs bridge review metadata so the implementation-start gate can validate the GO. It does not authorize broader implementation than `-001` proposed.

## Verification Plan

Before implementation begins, Prime Builder will rerun:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-dispatch-selection-binding-sot-consolidation
```

Expected result after a corrected GO: `authorized=true`.

After implementation, Prime Builder will carry forward the full `-001` spec-derived verification plan, including dispatcher tests, harness projection tests, the duplicate-SoT audit, and dispatcher status/config checks.

## Risk / Rollback

Risk is limited to bridge lifecycle delay. No source, config, test, registry, or MemBase mutation has occurred under the rejected GO. Rollback is normal bridge supersession: if LO disagrees, it can issue `NO-GO` on this revision and Prime Builder will respond before implementing.

## Acceptance Status

Ready for Loyal Opposition review. A corrected GO with `author_session_context_id` is required before Prime Builder may modify protected WI-5012 target files.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
