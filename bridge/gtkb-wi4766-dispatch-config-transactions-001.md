NEW

# Implementation Proposal - WI-4766 dispatcher config transaction CLI

bridge_kind: prime_proposal
Document: gtkb-wi4766-dispatch-config-transactions
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3a8-fefa-7382-a13c-c93e5ee51026
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; sandbox=danger-full-access; resolved Prime Builder by owner init keyword ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4766
Project: PROJECT-GTKB-DISPATCHER-CONTROL-CLI
Work Item: WI-4766

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4766 by adding governed dispatcher configuration transaction commands under the existing `gt bridge dispatch` CLI surface. The existing read command `gt bridge dispatch config` will remain usable; the implementation may convert it into an invoke-without-subcommand group so transaction commands can live below `gt bridge dispatch config ...` without breaking the read path.

The transaction surface will mutate only the selected project root's `config/dispatcher/rules.toml` when an operator explicitly invokes a transaction command. This implementation proposal itself does not authorize editing the live `config/dispatcher/rules.toml`; it authorizes source and test changes that create the governed transaction path. Tests must use temporary project roots and prove the commands validate inputs, write deterministic TOML for the known dispatcher schema, preserve unrelated fields, write append-only local audit evidence, and support `--defer-to-next-session` without changing live dispatcher behavior during implementation.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires dispatcher reporting and configuration control under the governed `gt bridge dispatch` CLI and skill surface.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - requires dispatcher configuration changes to be performed through governed CLI transactions rather than direct file edits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge files and role-specific status tokens are the canonical proposal, review, report, and verification chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH bounds implementation authority for the selected project/work item.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - active PAUTH and proposal scope must cite the governing specifications.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass the bridge `GO`, target paths, implementation-start packet, implementation report, or Loyal Opposition verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves owner decision, requirement, DCL, project, WI, proposal, report, verification, and audit evidence as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal must cite relevant specifications and map implementation tests to those specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must carry this spec-to-test mapping forward and report executed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation proposal must include PAUTH, project, work item, and target paths.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner approval evidence comes from AUQ-backed owner decision `DELIB-20265795`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation artifacts and tests must stay under `E:\GT-KB`; tests should use temp project roots.
- `GOV-STANDING-BACKLOG-001` - WI-4766 is the MemBase work item authority for this slice.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use helper-mediated bridge filing and explicit fallback checks when hook parity matters.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this turns repeated manual config-editing work into deterministic CLI operations with audit evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner requirement, implementation plan, test mapping, report, and verification remain lifecycle-visible.

## Prior Deliberations

- `DELIB-20265795` - owner AUQ-backed decision requiring a dispatcher reporting/configuration control surface under `gt bridge dispatch`.
- `DELIB-20265540` - prior NO-GO showing dispatcher config mutation must be covered by the cited authorization; this proposal avoids direct live `config/dispatcher/rules.toml` target mutation and authorizes the source/test transaction surface instead.
- `DELIB-20263376` - dispatch suppression routing precedent; relevant because transaction commands must preserve dispatch state semantics and avoid conflating configuration edits with runtime failure handling.
- `bridge/gtkb-wi4765-dispatch-report-cli-001.md` through `bridge/gtkb-wi4765-dispatch-report-cli-004.md` - predecessor project slice implementing and verifying the reporting half of the dispatcher control surface.

DA search command run before proposal drafting:

```text
gt deliberations search "WI-4766 dispatcher config transaction CLI SPEC-DISPATCHER-CONTROL-SURFACE-001 DCL-DISPATCHER-CONFIG-CLI-ONLY-001" --limit 10 --json
```

It returned dispatcher reliability and authorization precedents, including `DELIB-20265540` and `DELIB-20263376`. `gt bridge threads --wi WI-4766 --json` returned `match_count: 0`, so no existing WI-metadata-linked bridge thread is duplicated by this proposal.

## Owner Decisions / Input

- `DELIB-20265795` - owner AUQ-backed decision requiring the dispatcher control/reporting surface.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4766` - active project authorization for WI-4766, allowing `cli_extension`, `source`, and `test_addition` while forbidding production deployment and credential lifecycle work.

No new owner decision is required before implementation because WI-4766 is directly inside the captured dispatcher-control project and has a bounded PAUTH derived from `DELIB-20265795`.

## Requirement Sufficiency

Existing requirements sufficient.

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` specifies the dispatcher configuration transaction capability under `gt bridge dispatch`.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` specifies the direct-file-edit prohibition and the requirement for governed CLI transactions.
- `DELIB-20265795` is the AUQ-backed owner decision that created this workstream.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4766` is active and bounds this WI to CLI/source/test additions, while forbidding production deployment and credential lifecycle work.

## Proposed Scope

In scope:

- Preserve `gt bridge dispatch config` as the read-only configuration report.
- Add transaction subcommands under `gt bridge dispatch config`, covering at minimum:
  - `set-eligibility` for `can_receive_dispatch` and `can_fire_events`;
  - `set-weights` for `dispatch_quality`, `dispatch_cost`, and `dispatch_availability`;
  - `set-caps` for `max_items`;
  - `set-rule` for rule status/role/prefer selector fields;
  - `add-harness` and `remove-harness` for dispatcher overlay entries.
- Add validation for harness ids, boolean fields, numeric ranges, max item values, role/status selector names, and rule ids.
- Add a deterministic writer for the known dispatcher `rules.toml` schema without adding a new dependency.
- Preserve unrelated dispatcher config fields and comments only where the current schema-aware writer can do so deterministically; if comments cannot be preserved safely, the implementation must state the limitation and keep output stable.
- Add append-only local audit evidence for transaction attempts and applied/deferred changes.
- Add `--dry-run` and `--defer-to-next-session` behavior. `--dry-run` reports without writing. `--defer-to-next-session` records a pending transaction artifact and does not alter the live config immediately.
- Keep implementation tests on temporary project roots; no test may mutate the live `E:\GT-KB\config\dispatcher\rules.toml`.

Out of scope:

- No direct live edit to `config/dispatcher/rules.toml` during implementation.
- No PreToolUse guard or doctor check for direct rules.toml edits; that is WI-4767.
- No live-state reconciliation between `rules.toml` and the harness registry; that is WI-4768.
- No dispatcher-control skill work; that is WI-4769.
- No dispatcher scheduling, ranking, runtime worker, provider retry, circuit-breaker, bridge queue, or harness registry role behavior change beyond the transaction helpers' explicit config-file output.
- No credential lifecycle, production deployment, force-push, or external service action.

## Spec-Derived Verification Plan

| Specification / requirement | Proposed verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` transaction surface | Add CLI tests proving `gt bridge dispatch config` still reports the config and that transaction subcommands are discoverable and executable against a temp project root. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` config transaction commands | Add tests for `set-eligibility`, `set-weights`, `set-caps`, `set-rule`, `add-harness`, and `remove-harness` on fixture dispatcher TOML. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` governed mutation path | Tests prove direct implementation does not modify live `config/dispatcher/rules.toml`; transaction tests mutate only temp fixture config files through CLI/helper calls. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` validation and audit | Tests assert invalid harness ids, invalid booleans/numbers, unknown rule ids, and invalid selector fields fail closed without writing; applied/deferred transaction audit records are append-only and machine-readable. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` defer behavior | Tests assert `--defer-to-next-session` records a pending transaction and leaves the immediate `rules.toml` bytes unchanged. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This proposal carries PAUTH, project, work item, and inline JSON `target_paths` metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal links governing specs and maps tests back to the linked requirements. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry this mapping forward and include executed pytest, ruff check, and ruff format evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests use pytest temp roots and all implementation target paths remain under `E:\GT-KB`. |

Required verification commands after implementation:

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Pre-Filing Preflight

Applicability preflight run before filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4766-dispatch-config-transactions-001.md --bridge-id gtkb-wi4766-dispatch-config-transactions
```

Observed result: exit 0; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet hash `sha256:3b4366b51189827db3f0b48aa7e3f5b9f7f7cb6732a176086b0247bb3280947b`.

Clause preflight run before filing:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4766-dispatch-config-transactions-001.md --bridge-id gtkb-wi4766-dispatch-config-transactions
```

Observed result: exit 0; clauses evaluated: 5; must_apply: 4; may_apply: 1; evidence gaps in must_apply clauses: 0; blocking gaps: 0.

## Risk / Rollback

Primary risk: a schema-aware TOML writer could accidentally drop a dispatcher config field. The implementation must test preservation of unrelated known fields and fail closed on unsupported shapes rather than silently rewriting unknown data incorrectly.

Secondary risk: exposing mutation commands before the WI-4767 direct-edit guard exists could create a partially protected operating surface. This is acceptable because WI-4766 creates the governed path first; WI-4767 then mechanically blocks bypass edits.

Rollback: remove the transaction module, remove the transaction subcommand wiring while keeping the existing read command, and remove the focused transaction tests. No live dispatcher config migration is proposed or required by this implementation.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4766-dispatch-config-transactions`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `feat:`. The implementation adds a net-new governed dispatcher configuration transaction capability under the `gt bridge dispatch` CLI.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
