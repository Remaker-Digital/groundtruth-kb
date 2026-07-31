NEW

# WI-4995 Document Lease Held Health Classification Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4995-document-lease-held-health
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Extra High reasoning; Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4995

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

---

## Claim

Dispatcher health currently reports a false Loyal Opposition failure when a secondary LO harness is selected for a document whose lease is already held by another LO worker. During the 2026-07-03 live soak, Claude B was active and eligible, but Ollama D held the document lease for `gtkb-wi4994-prime-builder-fanout-dispatcher`; B correctly did not launch with `last_launch.reason=document_lease_held`, yet stale `failure_class=subprocess_execution_failed` caused `gt bridge dispatch health` to report `dispatch runtime failure: loyal-opposition:B failure_class=subprocess_execution_failed with pending_count=1`.

This proposal fixes the false health failure so normal document-lease arbitration does not make stable headless dispatch look broken.

## Defect / Reproduction

Live evidence from 2026-07-03:

- `gt bridge dispatch report --json` showed `loyal-opposition:D` launched for `gtkb-wi4994-prime-builder-fanout-dispatcher` and holding the per-document lease.
- The same report showed `loyal-opposition:B` with `last_launch.reason=document_lease_held`, `pending_count=1`, `selected_count=1`, and stale `failure_class=subprocess_execution_failed`.
- `gt bridge dispatch health --json` then reported `health_status="WARN"` with finding `dispatch runtime failure: loyal-opposition:B failure_class=subprocess_execution_failed with pending_count=1`.

This is incorrect: document lease held is a normal, non-launch suppression that prevents duplicate LO review. It should not be classified as a B subprocess failure unless there is current B failure evidence beyond the lease-held result.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatch requires health reports to distinguish genuine harness failures from normal lease arbitration.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher health and lease handling are part of the dispatcher control plane; no direct harness fallback is authorized.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge processing must remain role-correct and avoid duplicate review/implementation through lease/work-intent discipline.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded PAUTH before protected dispatcher source/test mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete links to all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map linked requirements to executed verification.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended headless bridge processing with Codex A as PB and Claude/Ollama as LO, and authorized governed stability WIs under the dispatcher-modernization project.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibited direct harness-to-harness standby/fallback. This proposal does not add or rely on a direct launch path.
- `DELIB-202665265` - earlier owner authorization evidence for creating necessary WIs and fixing bridge-stability defects discovered during the live soak.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` - verified earlier LO in-flight/lease handling repairs; WI-4995 is a follow-up health-classification residue discovered after that closure.
- `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-001.md` - live proposal whose Ollama D lease exposed the B false-failure health state.

## Owner Decisions / Input

- Owner goal: enable the bridge and keep testing/fixing until stable and processing work headlessly without intervention using Claude Code and Ollama as active LO and Codex as active PB.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` records owner authority to create governed WIs and bounded authorizations needed to stabilize unattended headless dispatch.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH` authorizes only bridge, dispatcher health/source, and focused tests for WI-4995. It forbids direct harness-to-harness launch, credential changes, production deployment, durable role reassignment beyond A/B/D, and retired poller restoration.

## Requirement Sufficiency

Existing requirements are sufficient. The stable dispatcher requirement already requires accurate health classification; the document lease mechanism already exists to prevent duplicate LO work. The missing behavior is implementation/test coverage that treats `document_lease_held` as benign rather than a current subprocess failure.

## Proposed Scope

- Update the dispatcher daemon state-writing path, the health classification path, or both so `document_lease_held` non-launch outcomes do not surface stale failure fields as current runtime failures.
- Preserve genuine failure detection for real subprocess/provider/configuration failures.
- Preserve document lease behavior: when one LO worker holds a document lease, other LO harnesses must not launch duplicate workers for that document.
- Preserve dispatcher-only orchestration; do not add a direct harness fallback.
- Add focused regression coverage for stale `failure_class` plus `last_launch.reason=document_lease_held`.
- Verify report/CLI health behavior if needed so `gt bridge dispatch health --json` no longer marks B failed in the reproduced state.

## Out of Scope

- Changing LO target selection order or model routing.
- Changing B or D eligibility.
- Reworking the document lease registry itself beyond any necessary state cleanup.
- Fixing PB fan-out; that is tracked separately by WI-4994.
- Restarting or replacing the dispatcher daemon as part of the implementation proposal.

## Specification-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add/extend a bridge dispatch health test proving `document_lease_held` with stale failure evidence does not emit `dispatch runtime failure`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Assert the repair stays inside dispatcher health/daemon source and does not add direct harness launch code. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Add/extend daemon test coverage showing lease-held still suppresses duplicate LO launch. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start authorization must cover only WI-4995 target paths before protected mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal/report carry PAUTH/project/WI metadata, target paths, and complete spec links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must include exact command evidence and this mapping before VERIFIED. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
```

## Acceptance Criteria

- A recipient row with pending LO work, `last_launch.reason=document_lease_held`, and stale `failure_class=subprocess_execution_failed` does not emit `dispatch runtime failure`.
- The same condition is classified as PASS or at most an explanatory non-failure warning, not a failure.
- Real subprocess/provider/configuration failures with pending work still emit failures.
- Document lease held still suppresses duplicate LO launches.
- `gt bridge dispatch health --json` no longer reports B failed solely because D holds the document lease for the selected item.
- Focused pytest, ruff check, and ruff format-check commands pass.

## Risks / Rollback

Risk: treating too much as benign could hide a real B failure. Mitigation: narrow the condition to explicit `document_lease_held` non-launch outcomes and retain all other failure classifications.

Risk: clearing failure fields in daemon state could remove useful historical evidence. Mitigation: preserve dispatch run logs and failure JSONL history; clear or ignore stale recipient health fields only for current health classification.

Rollback: revert the WI-4995 source/test changes. Bridge files, PAUTH, and MemBase records remain append-only audit records.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`fix`
