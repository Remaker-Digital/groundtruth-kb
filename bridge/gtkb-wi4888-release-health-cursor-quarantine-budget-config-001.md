NEW
author_identity: codex-prime-builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop; restarted Prime Builder dispatcher release-health session

# gtkb-wi4888-release-health-cursor-quarantine-budget-config - Budget-aware dispatcher config transactions and Cursor quarantine

bridge_kind: prime_proposal
Document: gtkb-wi4888-release-health-cursor-quarantine-budget-config
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4888

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "config/dispatcher/rules.toml", "harness-state/harness-registry.json"]

implementation_scope: dispatcher config transaction source/test repair plus governed temporary dispatcher eligibility change
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The dispatcher cannot be release-healthy while Cursor E is selected as a dispatch target on this host. The WI-4888 Cursor code-side launcher fix is already terminal VERIFIED, but its own implementation report records the remaining environmental blocker: there is no standalone `agent` executable on PATH, and this installed Cursor desktop CLI does not expose a usable headless `cursor agent --print --output-format` surface. Live `gt bridge dispatch health --json` therefore reports `prime-builder:E` with `cursor_headless_cli_unavailable`.

The correct release posture is to quarantine Cursor E from automated dispatch until a real headless Cursor Agent runtime exists. However, the governed dispatcher-control surface currently cannot apply the quarantine because `gt bridge dispatch config set-eligibility E --no-can-receive-dispatch --dry-run --json` fails with `unsupported top-level table: budget`. The status parser accepts the new `[budget]` table, but the transaction renderer rejects it.

This proposal authorizes a narrow fix: make dispatcher config transactions preserve and render the `[budget]` table, then use the governed CLI to disable Cursor E receive/event eligibility. It does not install Cursor, change credentials, reactivate Antigravity, restore the retired poller, or hand-edit dispatcher config.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source, tests, config, and harness-state mutation require bridge GO, implementation-start authorization, report, and independent verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing dispatcher and release-readiness specifications before work begins.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project authorization, project, work item, and parseable target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map transaction rendering and topology evidence to executed commands.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher routing changes must go through the dispatcher control surface, not manual config edits.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected dispatcher targets must be runnable and observable.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher control commands must remain usable after config schema growth.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires real health evidence, not a selected known-unavailable target.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - the existing budget table is a governed cost-control surface and must survive dispatcher transactions.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues must be diagnosed and resolved before release.
- `bridge/gtkb-wi4888-cursor-agent-cli-subcommand-no-window-004.md` - VERIFIED code-side Cursor harness fix; records external headless Cursor Agent runtime still missing.
- `bridge/gtkb-wi4895-claude-token-outage-dispatch-topology-004.md` - VERIFIED temporary topology that selected Cursor E before the host-level headless Cursor runtime blocker was proven release-blocking.
- `bridge/gtkb-wi4550-dispatch-cost-budget-policy-003.md` - GO for budget-table dispatcher work; the current transaction renderer bug is a schema-growth integration gap exposed by that work.
- Current owner directive in this release session: continue until the dispatcher is release-healthy and do whatever is necessary to diagnose and correct the issue before release.

## Owner Decisions / Input

No new owner input is required before Loyal Opposition review. The owner has made release health the top priority, called the console/dispatcher instability a showstopper, and asked whether Cursor should be switched if necessary. This proposal chooses the narrower and reversible option: do not switch Cursor roles; remove Cursor E from automated dispatcher receive/event eligibility until the external headless Cursor Agent runtime exists.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4888 is still open for full-topology go-live acceptance and real-harness smoke, `DELIB-20266276` authorizes dispatcher resilience source/test/config work, and the current release directive requires a truthful healthy dashboard. A new product requirement is not needed because this is a bounded release-health correction and temporary eligibility quarantine.

## Implementation Plan

1. Update `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` so `_render_dispatch_config` accepts and preserves the dispatcher `[budget]` table and its `[budget.harnesses.<id>]` children while continuing to reject genuinely unsupported top-level tables.
2. Add regression coverage in `platform_tests/scripts/test_bridge_dispatch_transactions.py` using a rules fixture with `[budget]` and `[budget.harnesses.D]`; assert `set_eligibility(..., dry_run=True)` and applied `set_eligibility` no longer fail and preserve the budget section.
3. Run focused tests and ruff checks for the transaction source/test files.
4. Use the governed CLI, after implementation authorization, to run:

```text
gt bridge dispatch config set-eligibility E --no-can-receive-dispatch --no-can-fire-events --json
```

5. Run `gt bridge dispatch reset --soft --json` to clear stale runtime recipient state without wiping quality history.
6. Verify `gt bridge dispatch status --json`, `health --json`, and `report --json` no longer select Cursor E and no longer report `cursor_headless_cli_unavailable`.

## Spec-Derived Verification Plan

| Specification | Required verification evidence |
|---|---|
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config set-eligibility E --no-can-receive-dispatch --dry-run --json` succeeds after the renderer fix and includes the unchanged budget table in returned config. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | `platform_tests/scripts/test_bridge_dispatch_transactions.py` proves budget config is preserved by dry-run and applied transactions. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Actual Cursor quarantine is applied only through `gt bridge dispatch config set-eligibility`, not by direct editing. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Dispatcher status/health/report show Cursor E absent from selected dispatch targets and no `cursor_headless_cli_unavailable` runtime finding after stale state reset. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact commands and observed outputs. |

## Acceptance Criteria

- Config transaction dry-run and apply paths accept the current budget-enabled `config/dispatcher/rules.toml`.
- Cursor E has `can_receive_dispatch=false` and `can_fire_events=false` in dispatcher config and regenerated harness projection.
- Dispatcher selected Prime Builder targets no longer include Cursor E until a working headless Cursor Agent runtime is installed.
- Health no longer reports `cursor_headless_cli_unavailable` after stale runtime state is reset.
- All changes are scoped to the approved target paths and are reversible by the inverse governed CLI transaction after Cursor Agent readiness is proven.

## Risk / Rollback

Risk is temporarily reducing Prime Builder dispatch capacity from two targets to one. That is preferable to repeatedly spawning a known-unavailable headless Cursor target during release. Rollback is the inverse governed CLI transaction after a fresh Cursor Agent smoke succeeds:

```text
gt bridge dispatch config set-eligibility E --can-receive-dispatch --can-fire-events --json
```

## Recommended Commit Type

fix - this repairs the dispatcher control surface and quarantines a selected but unavailable release target.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
