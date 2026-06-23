NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3a8-fefa-7382-a13c-c93e5ee51026
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; sandbox=danger-full-access; resolved Prime Builder by owner init keyword ::init gtkb pb

# Implementation Proposal - gt bridge dispatch report: comprehensive dispatcher reporting CLI

bridge_kind: prime_proposal
Document: gtkb-wi4765-dispatch-report-cli
Version: 001
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4765
Project: PROJECT-GTKB-DISPATCHER-CONTROL-CLI
Work Item: WI-4765

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

Implementation proposal for a bounded, read-only dispatcher reporting CLI. This thread does not authorize dispatcher scheduling, ranking, cap, harness role, or configuration behavior changes.

## Claim

Implement `gt bridge dispatch report` as a deterministic read/report surface over the existing dispatcher configuration, harness projection, runtime dispatch state, dispatch run evidence, failure logs, suppression logs, and starvation telemetry. The report must productionize the 2026-06-23 incident analysis for operators without requiring direct reads of `config/dispatcher/rules.toml` or `.gtkb-state/bridge-poller/*.json*`.

## Requirement Sufficiency

Existing requirements sufficient.

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` specifies the reporting capability: configuration, topology and eligibility, performance, reliability, live state, and history under `gt bridge dispatch`.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` constrains dispatcher configuration mutation to governed CLI transactions. This WI is read-only reporting, so it must not introduce config writes or behavior changes.
- `DELIB-20265795` is the owner AUQ-backed decision that created the dispatcher control project and requires the reporting/configuration surface.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4765` is active and bounds this WI to `cli_extension`, `source`, and `test_addition`, while forbidding production deployment and credential lifecycle work.

No new or revised requirement is needed before implementation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - primary owner requirement for all dispatcher reporting/configuration to live under the governed `gt bridge dispatch` CLI and skill surface.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - constrains dispatcher configuration mutation and keeps this WI read-only; reporting must not become a hidden mutation path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge files and role-specific status tokens are the canonical proposal/review chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH is the bounded owner-authorization envelope for this WI.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - active PAUTH and proposal scope must cite governing specifications.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge proposal, LO `GO`, implementation-start packet, implementation report, or verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the owner decision, requirement, DCL, project, WI, proposal, report, and verification evidence as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must cite all relevant specs and map tests back to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation report must carry spec-to-test mapping and executed evidence before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-targeting proposal must include PAUTH, project, work item, and target paths.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner approval evidence comes from AUQ-backed owner decision `DELIB-20265795`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all files and runtime evidence stay under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4765 is the MemBase work item authority for this slice.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use helper-mediated bridge filing and explicit fallback checks when hook parity matters.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation should reduce repeated incident-analysis work into a deterministic CLI/report artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner requirement, implementation plan, tests, report, and verification must stay lifecycle-visible.

## Prior Deliberations

- `DELIB-20265795` - owner AUQ-backed decision requiring a dispatcher reporting plus configuration skill/CLI surface and prohibiting file-mutation as an operating path.
- `DELIB-20265026` - prior LO GO on WI-4556, relevant precedent for dispatcher runtime failures, provider/output failure classes, fallback/backoff, and no-verdict evidence.
- `DELIB-S20260620-WI4703-DISPATCH-REPAIR-AUTH` - owner authorization for dispatcher fast-trip repair, relevant because WI-4765 must surface non-transient dispatch failure evidence rather than bury it in generic `launch_failed` rows.
- `DELIB-20263403` - prior GO on WI-4396 dispatch suppression routing, relevant to distinguishing expected suppressions from actionable dispatch failures.
- `DELIB-20265240` - prior malformed status token quarantine review surfaced by DA search, relevant to reporting quarantined thread evidence.
- `DELIB-20265484` - prior previous-launch-failure cooldown verdict surfaced by DA search, relevant to reporting launch cooldown/backoff evidence.

DA search command run before proposal drafting:

```text
gt deliberations search "WI-4765 dispatcher report CLI SPEC-DISPATCHER-CONTROL-SURFACE-001" --limit 8 --json
```

It returned `DELIB-20265795` plus adjacent dispatcher reliability precedents. `gt bridge threads --wi WI-4765 --json` returned `match_count: 0`, so no existing WI-metadata-linked bridge thread is duplicated by this proposal.

## Owner Decisions / Input

- `DELIB-20265795` - Owner AUQ `AUQ-2026-06-23-DISPATCHER-CONTROL-SURFACE`; owner selected full capture for a skill+CLI dispatcher reporting/configuration surface under `gt bridge dispatch`.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4765` - active project authorization created through `gt backlog authorize-implementation WI-4765` from `DELIB-20265795`; includes `WI-4765`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`; allows `cli_extension`, `source`, and `test_addition`; forbids `production-deploy` and `credential-lifecycle`.

## Proposed Scope

In scope:

- Add `gt bridge dispatch report` under the existing `bridge dispatch` command group.
- Add a read-only report builder, likely `groundtruth_kb.bridge_dispatch_report`, that composes existing config/status data with runtime evidence from `.gtkb-state/bridge-poller/`.
- Report configuration/topology by reusing `collect_bridge_dispatch_status()` rather than duplicating config parsing.
- Report performance and throughput from existing local evidence: dispatch run files, `dispatch-state.json`, `dispatch-failures.jsonl*`, `dispatch-suppressions.jsonl`, `trigger-diagnostic.jsonl*`, `starvation-telemetry.json`, and live dispatch-run files.
- Report failure taxonomy by concrete cause fields such as `reason`, `failure_class`, `last_result`, `last_launch.reason`, `last_launch.exit_failure_reason`, and suppressions, rather than collapsing to `launch_failed` or exit code 1.
- Report circuit-breaker state, pending/selected counts, live worker count/age, per-recipient caps where available, recent run history, and an effective per-cycle ceiling derived from selected candidates and per-harness `max_items`.
- Preserve JSON and human-readable output modes. JSON is the verification floor; the human output can be compact.
- Add focused tests for the report builder and CLI, with fixtures for runtime state, runs, failures, suppressions, and selected candidates.

Out of scope:

- No mutation of `config/dispatcher/rules.toml`.
- No transaction commands such as `set-eligibility`, `set-weights`, `set-caps`, `set-rule`, `add-harness`, or `remove-harness`; those are WI-4766.
- No PreToolUse edit prohibition guard or doctor check; those are WI-4767.
- No live-state reconciliation or rules.toml/registry consistency repair beyond accurately reporting current evidence; that is WI-4768.
- No skill creation/update; that is WI-4769.
- No credential lifecycle, production deployment, force-push, or external service action.
- No dispatcher behavior change to scheduling, ranking, cap enforcement, circuit-breaker thresholds, provider retry behavior, or bridge queue semantics.

## Specification-Derived Verification Plan

| Specification / requirement | Proposed verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` reporting surface | Add CLI tests proving `gt bridge dispatch report --json` emits configuration, topology/eligibility, performance, reliability, live state, and history without reading files manually. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` failure taxonomy by cause | Add report-builder fixture with launch failure, provider failure, no-verdict, suppression, and circuit-breaker rows; assert causes are preserved as separate counters/records. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` performance and throughput | Add tests for per-harness run counts, success/failure rates, latency derived from run evidence when timestamps are present, live worker counts, and effective per-cycle ceiling from candidate `max_items`. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` no hidden mutation path | Tests assert report command reads fixture state and leaves `rules.toml`, `harness-registry.json`, and runtime fixture files byte-identical. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge proposal carries PAUTH, Project, Work Item, and `target_paths` metadata; preflight and bridge-compliance helper must pass before filing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal links governing specs and this table maps tests to the linked requirements. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry this mapping forward and include executed pytest, ruff check, and ruff format evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests use temporary project roots under the pytest temp directory and target files remain under `E:\GT-KB`. |

Required verification commands after implementation:

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Acceptance Criteria

- `gt bridge dispatch report --json` exits 0 and returns a stable JSON object with top-level sections for `configuration`, `topology`, `performance`, `reliability`, `live_state`, `history`, and `summary`.
- The report includes current selected candidates per role and the configured harness overlays without requiring direct operator reads of `rules.toml`.
- The report includes per-harness or per-recipient success/failure counts, success rate when the denominator is nonzero, and latency fields when run evidence has enough timestamps.
- The report preserves failure causes separately: `last_result`, `failure_class`, `last_launch.reason`, `last_launch.exit_failure_reason`, dispatch failure JSONL reason, and suppression reason do not collapse into one generic category.
- The report includes circuit-breaker state, pending count, selected count, live worker count and age, recent run history, and effective per-cycle ceiling.
- The command is read-only in tests: config, harness registry, and runtime fixture files are byte-identical before and after command execution.
- Human-readable output is compact and points operators to the same evidence categories exposed by JSON.

## Risks / Rollback

- Risk: runtime evidence files are large or partially malformed. Mitigation: stream/tail bounded windows, tolerate JSONL decode failures as report warnings, and keep JSON schema stable.
- Risk: timestamp/latency evidence is incomplete. Mitigation: emit `null` or `unknown` for unavailable latency fields and still report counts/history.
- Risk: report builder grows too broad and overlaps WI-4768 reconcile work. Mitigation: report inconsistencies as observations only; do not repair or mutate state in this WI.
- Risk: CLI output becomes too verbose for operators. Mitigation: keep human output summarized and put complete details in JSON.
- Rollback: remove the `report` command wiring and the new report module/tests. No persistent dispatcher state or config is migrated by this WI.

## Pre-Filing Preflight

Applicability preflight command:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4765-dispatch-report-cli-001.md --json
```

Result:

- packet_hash: `sha256:42d42b860d8bdeae1cadaeb55144512055f2ff92e0190298298883cc52a1edcf`
- bridge_document_name: `gtkb-wi4765-dispatch-report-cli`
- content_source: pending content file `.gtkb-state/bridge-propose-drafts/gtkb-wi4765-dispatch-report-cli-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

Clause preflight command:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4765-dispatch-report-cli-001.md
```

Result:

- exit code: `0`
- clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- not_applicable: `0`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

`feat`
