NEW

# Defect-Fix Proposal - Restore Prime NO-GO dispatch routing

bridge_kind: prime_proposal
Document: gtkb-wi4983-prime-no-go-dispatch-routing
Version: 001
Date: 2026-07-04 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; `::init gtkb pb`; E:/GT-KB; danger-full-access; approval-policy never; no direct harness-to-harness launch

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4983-PB-NO-GO-DISPATCH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4983

target_paths: ["config/dispatcher/rules.toml", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

WI-5006 correctly made latest `NO-ACTION` Loyal Opposition-actionable, but its verified config commit also narrowed the Prime Builder dispatcher rule from `["GO", "NO-GO"]` to `["GO"]`. That leaves latest `NO-GO` bridge entries visible to the Prime scanner but unreachable by headless Codex/A PB dispatch. This proposal restores the Prime rule to `["GO", "NO-GO"]`, preserves `NO-ACTION` as LO-only, and adds regression coverage so the dispatcher config cannot drift away from the bridge role-actionability contract again.

## Defect / Reproduction

Live evidence gathered after commit `d01fc080`:

- `config/dispatcher/rules.toml` changed `bridge-prime-builder-default` from `statuses = ["GO", "NO-GO"]` to `statuses = ["GO"]`.
- `gt bridge dispatch status --json` now reports the Prime rule statuses as `["GO"]`.
- `python .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json --compact` reports two live latest `NO-GO` Prime-actionable threads: `gtkb-wi4975-claimed-path-subpath-overmatch` and `gtkb-wi5002-codex-dotdir-sandbox-acl-correction`.
- Active role contracts still require Prime to handle latest `GO` and `NO-GO`: `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, `config/agent-control/system-interface-map.toml`, `.claude/rules/prime-builder-role.md`, `.claude/skills/bridge/SKILL.md`, and `.claude/skills/bridge/helpers/scan_bridge.py`.

The result is a split-brain queue: manual/skill bridge state says latest `NO-GO` is Prime work, while the daemon's config rule cannot select those entries for Codex/A headless PB dispatch. This blocks the active stability goal because NO-GO corrections require interactive/manual PB intervention even though Codex/A is active and dispatchable.

## In-Root Placement Evidence

All target paths are inside `E:/GT-KB`: `config/dispatcher/rules.toml`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, and `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The dispatcher must select role-correct bridge work from governed config without bypassing to manual or direct harness fallback.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Latest bridge status determines role actionability; Prime may act on `GO` and `NO-GO`, while LO acts on `NEW`, `REVISED`, and now `NO-ACTION`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The live routing defect is preserved as a governed work item, PAUTH, proposal, tests, and verification evidence instead of chat-only diagnosis.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the concrete config repair to bridge/dispatcher specifications and requires LO review before protected mutations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must prove the role/status matrix, not merely that `rules.toml` changed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries machine-readable PAUTH, project, work-item, and target-path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner authorization evidence is the existing headless-dispatch stability decision; no AUQ engine behavior changes are in scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All changes remain in GT-KB platform config/tests, not adopter application paths or out-of-root artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4983 remains the governing backlog record for degraded Codex/A headless PB dispatch.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex/A remains the Prime dispatch target; the fix must not introduce direct harness fallback or hook-driven cross-harness launch.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The repair keeps traceability from live evidence through PAUTH, bridge proposal, implementation report, and VERIFIED finalization.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The regression was triggered by a bridge lifecycle status addition and must be repaired as lifecycle-aware dispatch behavior.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - The fix must preserve the prohibition on direct harness-to-harness invocation; only dispatcher selection changes are allowed.

## Requirement Sufficiency

Existing requirements sufficient. The existing bridge authority, dispatcher-service, lifecycle-trigger, and harness-isolation requirements already define the expected role/status matrix and forbid direct harness-to-harness fallback. This repair only restores config and test coverage to that existing contract.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - Owner-directed goal to keep testing and fixing until bridge/headless dispatch is stable with Codex/A as PB and Claude/B, Antigravity/C, and Ollama/D as LO targets.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` - Establishes `NO-ACTION` as a first-class bridge status.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` - Establishes latest `NO-ACTION` as LO-actionable and non-Prime implementation dispatch.
- `bridge/gtkb-wi5006-no-action-dispatch-config-routing-001.md` through `-004.md` - WI-5006 implemented and verified LO routing for `NO-ACTION`, but the verified config diff also removed `NO-GO` from the Prime rule.
- `bridge/smart-poller-kind-aware-routing-2026-04-30-009.md` through `-013.md` - Prior routing lineage explicitly preserved Prime dispatchability for latest `NO-GO` entries.
- `bridge/spawned-harness-role-defer-durable-record-2026-04-29-003.md` through `-006.md` - Prior prompt/routing lineage states Prime actionable statuses are `GO` and `NO-GO`, with `VERIFIED` terminal.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4983-PB-NO-GO-DISPATCH` - Active bounded authorization for this WI-4983 follow-up.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - Owner-directed stability goal and authorization basis for bounded dispatcher-stability follow-ups discovered during live soak.

No new owner decision is required. This proposal does not request credential changes, production deployment, durable role reassignment, retired poller restoration, or direct harness-to-harness launch.

## Proposed Scope

- Use the governed dispatcher config transaction surface, preferably `gt bridge dispatch config set-rule bridge-prime-builder-default --status GO --status NO-GO`, to restore Prime rule selection for latest `NO-GO` while leaving `NO-ACTION` out of the Prime rule.
- Preserve the LO rule from WI-5006: `["NEW", "REVISED", "NO-ACTION"]`.
- Update dispatcher config/parity tests so they assert the full role-status matrix: Prime `GO`/`NO-GO`; Loyal Opposition `NEW`/`REVISED`/`NO-ACTION`; `VERIFIED` terminal; `NO-ACTION` not Prime-dispatched.
- Add or adjust runtime/config tests proving latest `NO-GO` bridge entries are selected for Prime dispatch when Codex/A is active and eligible.
- Do not add direct harness launch paths, retired pollers, ad hoc queue artifacts, or broad topology changes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch status --json` shows Prime rule statuses `["GO", "NO-GO"]` and LO rule statuses `["NEW", "REVISED", "NO-ACTION"]`; focused dispatcher config tests pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests assert Prime dispatch includes latest `NO-GO` and excludes latest `NEW`, `REVISED`, `NO-ACTION`, and `VERIFIED`; LO dispatch includes `NEW`, `REVISED`, and `NO-ACTION`. |
| `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` | Existing isolation/parity tests confirm no direct harness-to-harness launcher or fallback path is introduced. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps each linked requirement to executed command evidence before requesting VERIFIED. |

Expected commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .gtkb-state/pytest-wi4983-prime-no-go
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/scripts/test_dispatcher_runtime.py
```

## Acceptance Criteria

- `bridge-prime-builder-default` routes latest `GO` and latest `NO-GO` to Codex/A PB when A is active and dispatchable.
- `bridge-prime-builder-default` does not route latest `NO-ACTION`.
- `bridge-loyal-opposition-cheap-fast-default` still routes latest `NEW`, `REVISED`, and `NO-ACTION`.
- A current Prime bridge scan and dispatcher rule selection no longer disagree on live latest `NO-GO` entries.
- Dispatcher health remains `PASS` after the governed config transaction.

## Risks / Rollback

Risk is low to moderate. Restoring `NO-GO` can re-expose PB work that was previously hidden by the WI-5006 config regression, so the implementation must rely on existing work-intent, target-path serialization, and health gates to avoid duplicate/churn behavior.

Rollback is a governed dispatcher config transaction returning the Prime rule to `["GO"]` if LO finds the status contract has intentionally changed. Bridge files and PAUTH/project metadata are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `config/dispatcher/rules.toml`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`
