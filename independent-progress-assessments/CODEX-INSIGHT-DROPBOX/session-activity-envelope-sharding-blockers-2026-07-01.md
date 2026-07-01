# Session/Activity Envelope Sharding Blocker Disposition Inventory

Date: 2026-07-01
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4952
Bridge: gtkb-envelope-sharding-blocker-repairs
Implementation packet: sha256:ad09ddc64fa9246c2e00341abe6fd430364630e194efe4addfd4f4ac6ec6af4b

## Purpose

This inventory satisfies the WI-4952 inventory-first requirement before claiming
any additional source repairs. It classifies the concrete transcript/CLI
blockers that caused agents to waste tokens on raw state or fall back to direct
artifact manipulation.

## Dispositions

| ID | Blocker | Disposition | Evidence / route |
| --- | --- | --- | --- |
| B1 | Bridge scan raw JSON included terminal VERIFIED and archived/nonterminal payloads during routine checks. | Fixed by WI-4947 compact scan mode. | `.claude/.codex/skills/bridge/helpers/scan_bridge.py --compact`; `platform_tests/scripts/test_scan_bridge.py::test_compact_scan_omits_terminal_payloads_and_version_chains`. |
| B2 | Implementation authorization `list` output dumped hundreds of expired named packets, making the SoT unwieldy. | Fixed by WI-4947 compact list mode; compact output reports counts plus valid/current packets only. | `scripts/implementation_authorization.py list --compact`; observed 918 packets summarized into 742 bytes with 916 invalid packets omitted. |
| B3 | Implementation-report planning output included broad dirty-worktree file and version-chain payloads when agents needed only current GO/report metadata. | Fixed by WI-4947 compact plan mode. | `.codex/skills/bridge/helpers/impl_report_bridge.py plan <slug> --compact`; `platform_tests/skills/test_bridge_impl_report_helper.py::test_latest_go_thread_produces_compact_plan_summary`. |
| B4 | Handoff/session marker drift and archived-envelope mis-resolution could cause agents to use the wrong archived session state. | Existing handoff service already resolves explicit session IDs across registered archives and fails closed on ambiguity; add a lightweight compatibility regression at the WI-4952-authorized test path. | `groundtruth-kb/src/groundtruth_kb/session/handoff.py`; existing `platform_tests/scripts/test_session_handoff_service.py`; new `platform_tests/scripts/test_session_handoff.py`. |
| B5 | Broad generated/cache searches can hit `.pytest-*`, generated adapter, and runtime-cache artifacts, wasting tokens and producing access-denied noise. | Deferred/routed: this is a structural hygiene/search-surface policy issue outside the narrow WI-4952 target paths. Use deterministic inventory/hygiene commands instead of ad hoc recursive grep. | Route to existing work-tree hygiene/generated-cache cleanup program; do not repair via this slice. |
| B6 | Startup glossary/terminology loading risked loading the full glossary into the base session envelope. | Already mitigated: startup loads a bounded core term profile and resolves activity terms only on demand. | `scripts/startup_glossary_load.py`; no source change needed in this slice. |
| B7 | Provider harnesses lack full transcript/session archives, creating temptation to rely on synthetic state. | Fixed/covered by WI-4950 provider compact-provider projection and typed transcript-archive waivers. | `bridge/gtkb-envelope-sharding-harness-projection-parity-003.md` and VERIFIED `-004.md`. |

## Follow-On Routing

- B5 should be handled by the active work-tree hygiene/generated-cache cleanup
  program rather than this envelope-sharding blocker repair slice. The desired
  repair is a deterministic search/query surface and default ignore policy for
  generated/cache/runtime artifacts, not another ad hoc grep wrapper.
- Any future handoff/session-envelope drift that is not covered by the explicit
  session-id archive-selection tests should be filed as a handoff-service
  proposal with `groundtruth-kb/src/groundtruth_kb/session/handoff.py` and the
  canonical `test_session_handoff_service.py` in scope.

## Current WI-4952 Repair Plan

1. Preserve this inventory as the durable blocker disposition artifact.
2. Add the authorized `platform_tests/scripts/test_session_handoff.py` wrapper
   regression for explicit session-id archive selection.
3. Re-run the compact bridge/helper tests and the handoff regression.
4. File the implementation report with repaired/deferred/routed mapping.
