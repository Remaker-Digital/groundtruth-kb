REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-ollama-lo-dispatch-session-propagation-revision3
author_model: GPT-5 Codex
author_model_version: 2026-06-06
author_model_configuration: Codex desktop; Prime Builder owner-directed reliability fast-lane bridge proposal
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4388
target_paths: ["scripts/gtkb_session_id.py", "scripts/cross_harness_bridge_trigger.py", "scripts/ollama_harness.py", "scripts/bridge_claim_cli.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "groundtruth-kb/tests/test_bridge_propose_helper.py", "harness-state/harness-registry.json"]
Author: Codex Prime Builder
Harness: Codex A
Session: codex-ollama-lo-dispatch-session-propagation-revision3

# Ollama LO Dispatch Session Propagation Fix

## Revision Claim

This REVISED version supersedes the GO'd version `001` only to add parser-visible `target_paths` metadata and `## Requirement Sufficiency`, because `implementation_authorization.py begin` rejected the GO'd proposal without those fields. The technical scope, target path set, acceptance criteria, and verification plan are unchanged.

## Summary

Fix the headless Ollama Loyal Opposition dispatch path that caused the prior default-LO rollback. The trigger exports `GTKB_BRIDGE_POLLER_RUN_ID`, but the bridge work-intent resolver and Ollama guarded-write payloads do not consistently use that dispatch id. A worker can claim a bridge item with one session id and attempt the verdict write with another.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use helper-mediated bridge writes and reference only environment variable names, never credential values. | Staged credential scan and pre-commit secret scan before commit. | |
| CQ-PATHS-001 | Yes | Restrict edits to the listed GT-KB paths under `E:\GT-KB`. | `git diff --name-only HEAD --` and bridge target-path preflight. | |
| CQ-COMPLEXITY-001 | Yes | Keep behavior as an env-order addition plus one shared Ollama resolver wrapper. | Focused resolver, claim, trigger, hook, helper, and Ollama tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse `BRIDGE_WORK_INTENT_ORDER` instead of duplicating precedence in Ollama. | Ruff plus tests that assert dispatch-id precedence. | |
| CQ-SECURITY-001 | Yes | Preserve guard denial behavior while aligning the guard payload session id with the bridge claim session id. | Existing destructive Bash, formal artifact, and out-of-root Ollama verification cases. | |
| CQ-DOCS-001 | Yes | Document the env var contract in claim CLI help and keep generated template copies in parity. | Help-text inspection plus template-focused tests. | |
| CQ-TESTS-001 | Yes | Add regression coverage for resolver order, trigger env propagation, and Ollama guard adapter payload session id. | Targeted pytest set named in this proposal. | |
| CQ-LOGGING-001 | Yes | Do not add noisy runtime logging; keep diagnostics in existing CLI/test surfaces. | Ruff and focused test run; diff review confirms no new persistent logs. | |
| CQ-VERIFICATION-001 | Yes | Run focused tests, Ruff check, Ruff format-check, readiness verification, and bridge preflights before implementation report. | Commands recorded verbatim in the implementation report. | |

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- Project: `PROJECT-GTKB-RELIABILITY-FIXES`
- Work item: `WI-4388`
- Owner directive: 2026-06-06 request to configure Ollama as default Loyal Opposition and Codex as Prime Builder, with iterative testing, diagnosis, correction, verification, and commit.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`: `bridge/INDEX.md` is the authoritative bridge queue, and bridge state must be managed through the file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: implementation proposals must cite governing specs before GO.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: protected implementation work requires project authorization and a live GO packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: implementation proposals must carry project authorization, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: implementation reports must map linked requirements to executed tests before VERIFIED.
- `REQ-HARNESS-REGISTRY-001`: harness role/default changes must flow through the governed harness registry projection, not hand-edited role files.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001`: role/session identity surfaces must use canonical runtime resolution semantics.
- `GOV-RELIABILITY-FAST-LANE-001`: small reliability fixes may proceed under the standing reliability project authorization once bridge-approved.

## Prior Deliberations

- `DELIB-20260897`: Phase 2 Ollama dispatch verified the bridge dispatch baseline before default-role promotion.
- `DELIB-20260663`: owner decisions for Ollama integration Phase 1.
- `DELIB-20260901`: Qwen full LO dispatch test update, later withdrawn for default-route use after rollback.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`: standing reliability fast-lane direction for bounded operational defects.
- Current automation memory records the 2026-06-06 rollback reason: Ollama headless dispatch fails on session-id propagation and stalls the LO queue.

## Problem Statement

`cross_harness_bridge_trigger.py` creates a dispatch id and exports it as `GTKB_BRIDGE_POLLER_RUN_ID`. The shared bridge session resolver does not treat that variable as a bridge work-intent input, and `scripts/ollama_harness.py` builds guarded-write payloads from `GTKB_SESSION_ID`, `CODEX_SESSION_ID`, or a synthetic `ollama-harness-d` fallback. This splits the dispatch claim identity from the protected write identity.

## Proposed Change

1. Add `GTKB_BRIDGE_POLLER_RUN_ID` to the shared session-id resolver and make it the first candidate in `BRIDGE_WORK_INTENT_ORDER`.
2. Keep marker-continuity semantics distinct so the dispatch run id does not become a durable session marker fallback.
3. Set `GTKB_INHERITED_SESSION_ID` to the same dispatch id in `cross_harness_bridge_trigger.py` child environments for compatibility with older work-intent surfaces.
4. Update `scripts/ollama_harness.py` to resolve the guarded-write payload session id through the shared bridge work-intent resolver.
5. Update fail-soft tuple copies in bridge compliance hooks, AXIS 2 surface, bridge-propose helpers, and generated templates.
6. Add focused regression tests.
7. After verification, use the canonical harness CLI to set Codex A as Prime Builder and Ollama D as active Loyal Opposition, leaving Claude B out of the active default Prime slot.

## Target Paths

- `scripts/gtkb_session_id.py`
- `scripts/cross_harness_bridge_trigger.py`
- `scripts/ollama_harness.py`
- `scripts/bridge_claim_cli.py`
- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `.claude/hooks/bridge-axis-2-surface.py`
- `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`
- `platform_tests/scripts/test_gtkb_session_id.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `platform_tests/scripts/test_ollama_dispatch.py`
- `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py`
- `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py`
- `platform_tests/skills/test_bridge_propose_helper_work_intent.py`
- `groundtruth-kb/tests/test_bridge_propose_helper.py`
- `harness-state/harness-registry.json`

## Out of Scope

- No production deployment.
- No credential rotation, upload, or new credential use.
- No formal GOV, ADR, DCL, or SPEC mutation.
- No resurrection of the withdrawn `gtkb-ollama-qwen-full-lo-route` thread as implementation authority.
- No broad model-routing rewrite beyond what is required to make default Ollama LO dispatch reliable.

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run bridge applicability preflight, ADR/DCL clause preflight, and show-thread/index drift inspection.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal lists every governing spec identified for the slice.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: begin implementation authorization only after a GO verdict.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: proposal header contains Project Authorization, Project, and Work Item lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: implementation report will carry forward this mapping and include observed command results.
- `REQ-HARNESS-REGISTRY-001`: verify role/default projection with `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb harness roles` after canonical CLI mutation.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001`: targeted resolver, bridge claim, trigger env, hook, helper, and Ollama tests must show one dispatch session id across claim and write surfaces.
- `GOV-RELIABILITY-FAST-LANE-001`: keep changes bounded to the standing reliability work item and listed paths.

## Expected Verification Commands

- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-lo-dispatch-session-propagation`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-lo-dispatch-session-propagation`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/hooks/test_bridge_compliance_gate_work_intent.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py platform_tests/skills/test_bridge_propose_helper_work_intent.py groundtruth-kb/tests/test_bridge_propose_helper.py -q --tb=short`
- `uv run --with ruff ruff check scripts/gtkb_session_id.py scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/bridge_claim_cli.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/hooks/test_bridge_compliance_gate_work_intent.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py platform_tests/skills/test_bridge_propose_helper_work_intent.py groundtruth-kb/tests/test_bridge_propose_helper.py`
- `uv run --with ruff ruff format --check scripts/gtkb_session_id.py scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/bridge_claim_cli.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/hooks/test_bridge_compliance_gate_work_intent.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py platform_tests/skills/test_bridge_propose_helper_work_intent.py groundtruth-kb/tests/test_bridge_propose_helper.py`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py --readiness-only --json`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py`

## Acceptance Criteria

- `GTKB_BRIDGE_POLLER_RUN_ID` resolves before parent harness session variables for bridge work-intent operations.
- Cross-harness trigger child env exposes the dispatch id through both `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_INHERITED_SESSION_ID`.
- Ollama guarded Write/Bash calls use the same dispatch session id as bridge claims.
- Focused tests and readiness verification pass.
- Harness registry projection shows Codex A as Prime Builder and Ollama D as active Loyal Opposition after canonical CLI updates.
- Local commit records the source/test/harness-state/bridge work; no push is performed.

## Risk and Rollback

Risk is low and localized. The main behavioral change is that a headless bridge dispatch run id outranks ambient parent harness sessions for bridge work-intent operations. Rollback is to revert the source/test/harness-state commit and restore the prior registry topology with the canonical harness CLI if readiness or dispatch verification regresses.
