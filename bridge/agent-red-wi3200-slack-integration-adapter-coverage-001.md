NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3200 Slack Integration Adapter Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3200-slack-integration-adapter-coverage
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3200

target_paths: ["applications/Agent_Red/tests/integrations/test_slack_spec1776.py"]

## Claim

WI-3200 should be implemented as a narrow test-only backfill for `SPEC-1776`.

Current Agent Red source already contains a Slack channel adapter under `applications/Agent_Red/src/integrations/slack/`, plus an existing general-purpose `test_slack_adapter.py`. The open work item exists because prior assertion-only coverage was rejected under `DELIB-0712` and `DELIB-0713`; this proposal adds deterministic, spec-mapped coverage with explicit `SPEC-1776` clause assertions without changing runtime code.

This proposal does not authorize source edits, existing-test rewrites, generated artifacts, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items. If the new test exposes a current source gap, Prime Builder should stop and return through the bridge with a revised source+test proposal rather than broadening target paths under this NEW proposal.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1776` directly states the target Slack adapter behavior: OAuth2 auth; required bot scopes; destination reply capability using Block Kit; Events API webhook receive; @mention-triggered threaded responses with source citations and escalation; HMAC-SHA256 signature verification through `x-slack-signature` plus timestamp; and Connect -> OAuth -> bot appears -> channel configuration setup flow. `WI-3200` asks for deterministic test evidence for that existing requirement; no owner clarification is needed to add a mapped regression test.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_slack_spec1776.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\integrations\slack\adapter.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\slack\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\models.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_slack_adapter.py`

## Specification Links

- `SPEC-1776` - Direct historical requirement text and source spec for the Slack channel adapter for the AI bot.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live Slack adapter and manifest surfaces are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3200`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3200 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.
- `gt deliberations search "WI-3200 SPEC-1776 Slack Integration Channel Adapter AI Bot"` returned broad project/review records (`DELIB-2026-06-21-WI4237-OPTION-B-DELIVER-ALL-HARNESSES`, `DELIB-2192`, `DELIB-20261050`, `DELIB-20265467`, `DELIB-20265802`) but no WI-3200-specific blocking prior decision.

## Current-State Evidence

- MemBase `SPEC-1776` title: "Slack Integration - Channel Adapter for AI Bot".
- MemBase `SPEC-1776` description requires OAuth2; scopes `chat:write`, `channels:history/read`, `groups:read`, `im:read/write`, `app_mentions:read`, and `users:read`; `dest.reply` with Block Kit; `webhook.receive` through Events API; @mention trigger, threaded responses, source citations, escalation, and Block Kit formatting; webhook events `app_mention` and `message.channels`; HMAC-SHA256 `x-slack-signature` plus timestamp; and Connect -> OAuth -> bot appears -> admin configures channels setup.
- `gt bridge threads --wi WI-3200 --json` currently returns `match_count: 0`.
- `applications/Agent_Red/tests/integrations/test_slack_spec1776.py` does not currently exist.
- `applications/Agent_Red/src/integrations/slack/manifest.py` declares OAuth2, the required Slack scopes, channel category, destination reply and webhook receive capabilities, webhook sync strategy, signature header `x-slack-signature`, HMAC-SHA256 signature algorithm, and professional tier gate.
- `applications/Agent_Red/src/integrations/slack/adapter.py` declares Slack Web API request handling, `chat.postMessage` replies, threaded reply metadata, conversation history reads, Events API registration guidance, timestamped HMAC verification, Block Kit text/citation/escalation helpers, rich message formatting, and Slack user lookup.
- `applications/Agent_Red/tests/integrations/test_slack_adapter.py` already covers many behaviors, but it is not a WI-3200/SPEC-1776 named mapping file and does not explicitly bind every SPEC-1776 clause into one deterministic coverage artifact.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3200-slack-integration-adapter-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3200-slack-integration-adapter-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/integrations/test_slack_spec1776.py`.
2. In the new pytest, import live Slack manifest, adapter helpers, normalized models, and action-executor action types where useful.
3. Assert manifest evidence for OAuth2, required Slack scopes, channel category, destination reply capability, webhook receive capability, webhook sync strategy, signature header, HMAC-SHA256 signature algorithm, and setup-relevant OAuth URLs/env keys.
4. Assert Block Kit helper evidence for text, source citation, and escalation action blocks.
5. Assert adapter request behavior for `chat.postMessage`, fallback text, Block Kit payloads, threaded replies, citation blocks, escalation blocks, and normalized Slack outbound messages.
6. Assert channel history receive behavior for inbound normalized Slack messages and cursor pagination.
7. Assert Events API registration guidance includes the requested events and required scopes for app mentions/channel messages.
8. Assert webhook verification uses `x-slack-signature`, timestamp replay protection, and HMAC-SHA256 semantics.
9. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1776` | New pytest imports live Slack adapter/manifest surfaces and asserts OAuth2/scopes, `dest.reply` Block Kit payloads, webhook receive metadata, Events API registration, @mention/threaded response support through threaded replies, source citations, escalation blocks, HMAC-SHA256 `x-slack-signature` verification with timestamp replay protection, and setup-relevant OAuth configuration. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic Slack spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3200-slack-integration-adapter-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/integrations/test_slack_spec1776.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/integrations/test_slack_spec1776.py
python -m ruff format --check applications/Agent_Red/tests/integrations/test_slack_spec1776.py
```

## Acceptance Criteria

- PASS when the new pytest verifies OAuth2 auth and required Slack OAuth scopes.
- PASS when the new pytest verifies channel category, destination reply, and webhook receive capabilities.
- PASS when the new pytest verifies Block Kit text, citation, and escalation formatting.
- PASS when the new pytest verifies threaded response payloads and normalized outbound Slack messages.
- PASS when the new pytest verifies channel history receive behavior and cursor pagination.
- PASS when the new pytest verifies Events API registration guidance for app mention/channel message events and required scopes.
- PASS when the new pytest verifies HMAC-SHA256 `x-slack-signature` validation plus timestamp replay protection.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal adds one deterministic test module and does not alter runtime behavior. The main risk is that the test may reveal a real source gap in the historical Slack adapter; if that happens, Prime Builder will stop and revise rather than widening this proposal.

Rollback is to delete `applications/Agent_Red/tests/integrations/test_slack_spec1776.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/integrations/test_slack_spec1776.py`

## Recommended Commit Type

`test:`
