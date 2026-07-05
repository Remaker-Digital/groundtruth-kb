NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; reasoning=xhigh; approval_policy=never; sandbox=danger-full-access

# GT-KB Bridge Implementation Report - WI-5020 Retire Event-Source Config - 005

bridge_kind: implementation_report
Document: gtkb-wi5020-retire-event-source-config
Version: 005 (NEW; post-implementation report)
Responds to: bridge/gtkb-wi5020-retire-event-source-config-004.md
Responds to GO: bridge/gtkb-wi5020-retire-event-source-config-004.md
Approved proposal: bridge/gtkb-wi5020-retire-event-source-config-003.md
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work item: WI-5020
Implementation authorization: sha256:e4541621de5e7e3925ccdfed8965a5d675b3a75170f087a11546e4f85e5d3ee4
Work-intent claim: rowid 30082, session 019f23f0-b16e-7481-8a18-9622ab564d50
Recommended commit type: fix:

## Implementation Claim

Implemented the approved Option B cleanup: harness-level event-source configuration is retired from current dispatcher configuration, generated harness-state projection, and declarative role inventory while preserving the schema/API fields and all dispatch-target semantics. The dispatcher daemon remains the only live event source; harnesses can still be selected as Prime Builder or Loyal Opposition dispatch receivers through `can_receive_dispatch`, role, score, and precedence metadata.

This report intentionally lists only the WI-5020 slice files below. The repository contains substantial unrelated dirty work from the recent bridge/harness outage recovery; those files were not claimed as WI-5020 implementation evidence.

## Files Changed

- `config/dispatcher/rules.toml`
- `config/agent-control/declarative-agent-role-manifest.yaml`
- `harness-state/harness-registry.json`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth-kb/tests/test_agent_role_manifest.py`
- `groundtruth-kb/tests/test_harness_projection.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`

## Implementation Details

- Removed `event-source` tags from dispatcher overlays for A, B, and E through the governed dispatcher transaction CLI, not by direct editing.
- Changed the harness projection generator so `can_fire_events` and deprecated `event_driven_hooks` project as `false` for all current harness records, even when legacy MemBase invocation metadata still contains event-source hints.
- Scrubbed generated projection `invocation_surfaces` metadata so the hot-path JSON does not retain nested `event-source`, `can_fire_events: true`, or `event_driven_hooks: true` state.
- Regenerated `harness-state/harness-registry.json` from MemBase through `groundtruth_kb.harness_projection.generate_harness_projection`.
- Updated the declarative role manifest so Codex and Cursor are dispatch targets, not event sources.
- Updated regression coverage for manifest parsing, projection neutralization, cross-harness parity, and bridge state-report output.

## Architecture Alignment Ledger

| Alignment surface | Evidence |
| --- | --- |
| OPS consolidation | Keeps dispatch control in the consolidated dispatcher daemon instead of harness-local event hooks. |
| Dispatcher daemon architecture | `can_fire_events` and `event_driven_hooks` are retained as compatibility fields but no current harness advertises event-firing authority. |
| Lifecycle-first / scoring-last precedence | Dispatch receiver eligibility and role lifecycle remain intact; quality/cost/availability scoring is unchanged and still applies after lifecycle/role selection. |
| Portfolio reconciliation findings | Scope stayed inside WI-5020 and did not revive retired poller/smart-poller paths, duplicate project-family records, or stale overlapping dispatcher specs. |

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `gt bridge dispatch health --json` reported `routing_config.health_status == PASS` and selected records show `can_fire_events: false` / `event_driven_hooks: false` for selected PB and LO harnesses. |
| `DELIB-20265888` | `rg -n "event-source" config/dispatcher/rules.toml harness-state/harness-registry.json config/agent-control/declarative-agent-role-manifest.yaml` returned no matches. |
| `DELIB-202665470` | `rg -n '"can_fire_events": true|"event_driven_hooks": true' harness-state/harness-registry.json` returned no matches; `test_build_projection_neutralizes_legacy_event_source_metadata` now covers legacy metadata scrubbing. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge status was `GO`; work-intent claim rowid 30082 was live; `implementation_authorization.py validate --target ...` accepted representative protected targets before mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Implementation stayed within the approved WI-5020 target-path envelope; no protected source/config/test mutations were made outside the approved slice. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest and ruff checks below passed after implementation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report links the approved proposal, GO verdict, project, work item, authorization hash, and work-intent claim. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex hook inventory remains present, but the manifest and projection no longer treat hook surfaces as dispatcher event sources. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changes are confined to GT-KB platform dispatcher/harness-control surfaces; no adopter application paths were touched. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi5020-retire-event-source-config`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target config/dispatcher/rules.toml`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config remove-harness A --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config add-harness A --description Codex --max-items 4 --tag loyal-opposition --tag prime-builder --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config remove-harness B --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config add-harness B --description "Claude Code" --max-items 4 --tag loyal-opposition --tag prime-builder --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config remove-harness E --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config add-harness E --description Cursor --max-items 4 --tag loyal-opposition --tag prime-builder --json`
- `groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from groundtruth_kb.config import GTConfig; from groundtruth_kb.db import KnowledgeDB; from groundtruth_kb.harness_projection import generate_harness_projection; root=Path(r'E:\GT-KB'); config=GTConfig.load(root / 'groundtruth.toml'); db=KnowledgeDB(config.db_path); print(generate_harness_projection(db, config.project_root))"`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py groundtruth-kb/tests/test_agent_role_manifest.py groundtruth-kb/tests/test_harness_projection.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/tests/test_agent_role_manifest.py groundtruth-kb/tests/test_harness_projection.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/tests/test_agent_role_manifest.py groundtruth-kb/tests/test_harness_projection.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch health --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config --json`
- `rg -n "event-source" config/dispatcher/rules.toml harness-state/harness-registry.json config/agent-control/declarative-agent-role-manifest.yaml`
- `rg -n "dispatch_mode: event_source|can_fire_events: true" config/agent-control/declarative-agent-role-manifest.yaml`
- `rg -n '"can_fire_events": true|"event_driven_hooks": true' harness-state/harness-registry.json`

## Observed Results

- Targeted pytest: `105 passed, 1 warning in 6.45s`; warning was existing `PytestConfigWarning: Unknown config option: asyncio_mode`.
- Ruff check: `All checks passed!`.
- Ruff format check: `5 files already formatted`.
- Event-source scans: all three `rg` scans returned no matches.
- Dispatcher config transaction output: A, B, and E overlays now have tags `["loyal-opposition", "prime-builder"]` with no `event-source`.
- Dispatcher config health: `routing_config.health_status == PASS`; overall health was `WARN` only because the storm watchdog heartbeat was stale at the check instant (`55.0s > 15.0s`), while daemon and routing config were healthy.
- Work-intent claim status after implementation: `expired: false`, latest bridge status `GO`, implementation deadline `2026-07-05T14:20:25Z`, grace expires `2026-07-05T14:30:25Z`.

## Acceptance Criteria Status

- No currently configured harness has an `event-source` tag in dispatcher rules, generated registry projection, or declarative manifest.
- No current generated harness registry record has `can_fire_events: true` or `event_driven_hooks: true`.
- Manifest event sources are empty while dispatch targets remain explicit.
- Dispatch receiver selection remains intact for current PB/LO harnesses through `can_receive_dispatch`, role, score, and precedence.
- State-report output presents event firing as `no` while preserving dispatchability and model/config display.

## Risk And Rollback

Residual risk is compatibility-related: any untested consumer that incorrectly reads nested `invocation_surfaces.dispatch.can_fire_events` directly from the generated projection will now see the corrected `false` value. That is intended by WI-5020 and aligns with the no-index/daemon-owned dispatcher architecture.

Rollback is straightforward: revert the eight files listed above, then regenerate `harness-state/harness-registry.json` from the reverted projection generator. The dispatcher config edits were made through audited `gt bridge dispatch config` transactions; the audit remains append-only.

## Loyal Opposition Asks

1. Verify that the implementation satisfies the approved WI-5020 Option B scope.
2. Confirm that event-source retirement did not damage dispatch receiver selection or score/precedence behavior.
3. Return `VERIFIED` if accepted, otherwise return `NO-GO` with concrete findings.
