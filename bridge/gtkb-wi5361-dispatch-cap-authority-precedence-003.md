NEW

# WI-5361 implementation report: dispatcher cap authority precedence

bridge_kind: implementation_report
Document: gtkb-wi5361-dispatch-cap-authority-precedence
Version: 003
Responds to GO: bridge/gtkb-wi5361-dispatch-cap-authority-precedence-002.md
Approved proposal: bridge/gtkb-wi5361-dispatch-cap-authority-precedence-001.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5361-CAP-AUTHORITY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5361
Recommended commit type: fix:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; reasoning xhigh

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py"]

## Implementation Claim

Implemented the approved cap-authority precedence without mutating live
dispatcher configuration, eligibility, routing, workers, leases, TAFE, or
runtime state.

- `HarnessDispatchConfig` now reads and reports an explicit
  `max_items_override` policy marker and rejects non-positive cap values as
  invalid.
- `apply_dispatch_config_to_record()` now resolves one effective cap in this
  order: a valid marked dispatcher override, a valid canonical harness-registry
  `dispatch_max_items`, then a valid unmarked legacy dispatcher-config fallback.
- The effective candidate exposes `dispatch_max_items_source` as
  `dispatcher_config_override`, `harness_registry`, or
  `dispatcher_config_fallback`. The projection is idempotent across the status
  collector's second candidate-selection pass.
- Audited `set_caps()` and `add_harness(max_items=...)` transactions now write
  both `max_items` and `max_items_override=true`; existing unmarked rows remain
  backward-compatible fallbacks.
- Candidate summaries, status JSON, and report JSON carry the same cap source.
  The existing report ceiling continues to sum the selected effective caps.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `REQ-HARNESS-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-SOT-SINGLETON-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
bounded fleet-defect carrier while preserving exact GO, target, claim,
implementation-start, independent verification, and focused-commit gates. The
implementation does not change harness eligibility or target-selection rules.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded defect-repair authority.
- `DELIB-202666235` - established selected-target cap enforcement at the runtime capacity boundary.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-003.md` through `-010.md` - established canonical registry authority with policy-capable config.
- `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-001.md` through `-004.md` - established the downstream runtime cap boundary.
- `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` - preserved the observed A cap mismatch.
- `bridge/gtkb-wi5361-dispatch-cap-authority-precedence-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5361-dispatch-cap-authority-precedence-002.md` - independent Cursor E GO.

## Implementation Authorization Evidence

- `gt bridge show gtkb-wi5361-dispatch-cap-authority-precedence --json` read
  back latest status `GO` at version 002.
- `gt projects show-authorization
  PAUTH-DISPATCHER-BLACK-BOX-WI5361-CAP-AUTHORITY-20260716 --json` read back an
  active exact-scope PAUTH for WI-5361 and the three target paths.
- The three target paths were clean and unclaimed before implementation.
- Claim row 31678 was acquired as `go_implementation` by session
  `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, acting role `prime-builder`, for the
  exact black-box-hardening project.
- `python scripts/implementation_authorization.py begin --bridge-id
  gtkb-wi5361-dispatch-cap-authority-precedence --session-id
  019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` wrote a valid schema-v3 start packet.
  Packet hash:
  `sha256:d51bfaee9a70a310e727b102ee684374aef088f85e79aa53210b201ada491ba3`.
- `python scripts/implementation_authorization.py validate` authorized exactly
  the three declared target paths before protected edits.

## Specification-Derived Verification

| Governing requirements | Executed evidence and observed result |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, proposal/project linkage DCLs, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, operation-time enforcement, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Independent version-002 GO, active exact PAUTH, claim row 31678, schema-v3 implementation-start packet, and exact target validation all passed before edits. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `REQ-HARNESS-REGISTRY-001`, freshness, and singleton requirements | `test_bridge_dispatch_cap_authority.py` proves canonical 1 beats unmarked 4; absent, malformed, and non-positive canonical values fall back to 4; marked override 4 beats canonical 1; all cases preserve source and idempotence. Seven tests passed. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` and `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` | Focused transaction tests prove `set_caps()` and `add_harness(max_items=...)` serialize and round-trip `max_items_override=true` and append both audit records. Existing transaction CLI tests also pass. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and `DCL-DISPATCH-ENVELOPE-RULES-001` | Synthetic status/report tests prove the selected candidate and effective ceiling use the same cap and source. Adjacent dispatcher config, LO quality-floor, and config CLI tests pass. A live read-only report selected A at cap 1/source `harness_registry` and E at cap 3/source `harness_registry`, with health PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and artifact/backlog lifecycle requirements | TEST-11477 is the linked test; this report carries exact commands/results and remains NEW pending independent LO verification. No terminal or commit claim is made before VERIFIED. |

## Commands Run And Observed Results

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py -q --tb=short`
   - 7 passed in 0.24 seconds.
2. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short`
   - 31 passed in 2.99 seconds.
3. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short`
   - 87 passed in 3.51 seconds.
4. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py`
   - All checks passed.
5. `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py`
   - Three files already formatted.
6. `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch report --json`
   - Health PASS; Prime Builder A cap 1/source `harness_registry`; Loyal Opposition E cap 3/source `harness_registry`; effective ceilings PB 1 and LO 3.

Pytest emitted only the existing unknown `asyncio_mode` configuration warning.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`
- `platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py`

No other dirty worktree file is claimed, adopted, staged, reverted, or included.

## Acceptance Criteria Status

- [x] Marked audited config override wins over canonical registry cap.
- [x] Valid canonical registry cap wins over unmarked legacy config cap.
- [x] Missing, malformed, or non-positive canonical cap uses valid legacy fallback.
- [x] Every effective cap carries a deterministic source label.
- [x] `set-caps` and `add-harness --max-items` write and audit the override marker.
- [x] Status candidate and report ceiling use the same effective value.
- [x] No runtime-cap source, live config, eligibility, routing, worker, lease, or TAFE mutation occurred.
- [ ] Independent LO verification and focused commit remain pending.

## Risk And Rollback

Existing unmarked `max_items` rows now act only as backward-compatible fallback
when the canonical registry has no valid cap. Future explicit audited cap
transactions mark their policy override. Residual risk is limited to consumers
that expected an unmarked duplicate to override canonical metadata; the focused
regression set and live report cover the dispatcher status/report path. Rollback
is the eventual focused three-file commit; bridge audit files remain append-only.

## Loyal Opposition Asks

Verify the exact three-file diff, rerun the mapped tests, confirm the live
read-only cap/source evidence, and return VERIFIED only if the implementation
satisfies every linked requirement without adopting unrelated worktree changes.

## Recommended Commit Type

`fix:`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
