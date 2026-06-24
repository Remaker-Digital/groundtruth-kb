NEW

# GT-KB Bridge Implementation Report - Agent Red WI-3213 WhatsApp Escalation Coverage - 003

bridge_kind: implementation_report
Document: agent-red-wi3213-whatsapp-escalation-coverage
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/agent-red-wi3213-whatsapp-escalation-coverage-002.md
Approved proposal: bridge/agent-red-wi3213-whatsapp-escalation-coverage-001.md
Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3213
target_paths: ["applications/Agent_Red/src/multi_tenant/cosmos_schema.py", "applications/Agent_Red/src/multi_tenant/config/field_mapping.py", "applications/Agent_Red/src/chat/pipeline/orchestrator.py", "applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py", "applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py", "applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx"]
implementation_packet_hash: sha256:c3d565c9f21f6bbaf4bda6d3b576bb050d234ee03fb128a3fd34c56111847e11
implementation_packet_created_at: 2026-06-24T04:43:22Z
implementation_packet_expires_at: 2026-06-24T06:43:22Z
work_intent_claim_rowid: 23795
recommended_commit_type: fix:
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

## Implementation Claim

Implemented the approved WI-3213 bounded `SPEC-1880` repair and coverage backfill.
The change makes `whatsapp_business_phone` a persisted tenant preference,
includes it in the config-preferences direct mapping, factors WhatsApp escalation
link construction into a production helper, and changes the streamed escalation
notice from a raw URL to a markdown link that the existing widget renderer turns
into a clickable anchor.

The new tests cover the live config mapping/model path, the production WhatsApp
link helper, and widget rendering of the markdown link. No ACS, Meta WhatsApp
Business API, webhook, template, provider onboarding, phone-identity linkage,
admin-inbox phone display, escalation state-machine expansion, formal artifact,
project membership, credential, deployment state, release tag, or new work item
was changed.

The Python formatter was applied only to the approved touched Python targets
after `ruff format --check` reported existing formatting drift in those files.
That produced mechanical formatting normalization in
`applications/Agent_Red/src/chat/pipeline/orchestrator.py` and two adjacent
approved Python targets while preserving the same behavioral scope.

## Specification Links

- `SPEC-1880` - Direct requirement for professional-plus WhatsApp escalation deep links to a merchant-configured WhatsApp number.
- `GOV-10` - Test artifacts must exercise exposed project paths; this implementation tests the live config mapping, production helper, and widget renderer rather than string-only evidence.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest and Vitest validate live source paths.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new tests create live spec-to-test evidence for the WI.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; this implementation uses targeted pytest, adjacent pytest, Vitest, widget typecheck, Ruff check, Ruff format check, and whitespace diff checks.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing AUQ-backed project authorization; no new owner decision was requested.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires proposal/report specification linkage to carry forward for review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this report uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses governed bridge helper paths and explicit preflight/packet evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation report as a lifecycle artifact for the work item.

## Owner Decisions / Input

- `DELIB-20265586` / `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23` authorize bounded implementation for the snapshot member set, including `WI-3213`.
- No new owner decision was needed for this implementation. The work stayed inside the approved GO target paths and approved mutation classes `source` and `test_addition`.

## Prior Deliberations

- `bridge/agent-red-wi3213-whatsapp-escalation-coverage-001.md` - NEW proposal defining the bounded WhatsApp persistence, production-helper, and widget-rendering scope.
- `bridge/agent-red-wi3213-whatsapp-escalation-coverage-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20265586` - Owner decision for the bounded project implementation authorization.
- `DELIB-0712` / `DELIB-0713` - Coverage-gap methodology and owner acceptance of behavioral remediation.
- `DELIB-0515` - SPEC-1880 proposal review recommending config mapping, post-response escalation rendering, widget click/button rendering, and production-path tests.
- `DELIB-0514` - SPEC-1880 implementation review identifying missing `whatsapp_business_phone` persistence and raw URL rendering gaps.
- `DELIB-0547` - WhatsApp integration/documentation evaluation recommending completing the v0 deep-link before future real-channel work.

## Implementation Authorization

- Work-intent claim acquired:
  `python scripts\bridge_claim_cli.py claim agent-red-wi3213-whatsapp-escalation-coverage`
  returned `claim_kind: go_implementation`, `rowid: 23795`,
  `ttl_expires_at: 2026-06-24T05:23:13Z`.
- Implementation-start packet acquired:
  `python scripts\implementation_authorization.py begin --bridge-id agent-red-wi3213-whatsapp-escalation-coverage`
  returned latest status `GO`, proposal file
  `bridge/agent-red-wi3213-whatsapp-escalation-coverage-001.md`, GO file
  `bridge/agent-red-wi3213-whatsapp-escalation-coverage-002.md`, packet hash
  `sha256:c3d565c9f21f6bbaf4bda6d3b576bb050d234ee03fb128a3fd34c56111847e11`,
  and all six approved target path globs.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-1880` | `python -m pytest applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py -q --tb=short` passed `6 passed`; `npm --prefix applications/Agent_Red/widget test -- whatsapp-escalation-link.test.tsx` passed `1 passed`. Coverage verifies persisted `whatsapp_business_phone`, config round trip, professional/enterprise markdown `wa.me` link generation with encoded context, starter/missing-phone suppression, and clickable widget rendering. |
| `GOV-10` | Tests import live `PreferencesDocument`, `_PREFS_DIRECT_FIELDS`, `_config_to_preferences()`, `_preferences_to_config()`, `_build_whatsapp_escalation_markdown_link()`, and `MessageBubble`, with no mirrored implementation. |
| `SPEC-1649` | Repository-native pytest and Vitest executed against live Agent Red paths plus adjacent legacy/config coverage. |
| `GOV-12` | `WI-3213` now has concrete repository test artifacts at the approved target paths. |
| `GOV-13` | The report maps the test artifacts and commands to the linked spec/governance surfaces for verification review. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet was acquired after GO and carried the project authorization, project id, work item, packet hash, and target paths. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Focused pytest, adjacent pytest, Vitest, widget typecheck, Ruff check, Ruff format check, and `git diff --check` all passed on the touched target set. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No new owner input was requested; the implementation relies only on the existing AUQ-backed PAUTH/DELIB authorization. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This status-bearing report is filed by Prime Builder as `NEW` after an LO `GO`; no LO status token is authored by Prime Builder. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specifications and governing surfaces. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked surface to executed evidence for LO verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project authorization, project id, work item, and `target_paths` metadata are included near the top of this report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation targets are under `applications/Agent_Red/`. |
| `GOV-STANDING-BACKLOG-001` | No new work item or project membership change was made. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Work used explicit bridge thread checks, preflights, work-intent claim, implementation-start packet, and helper-mediated report filing. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The bridge proposal, GO, source/test artifacts, command evidence, and this report preserve the lifecycle trail. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation intent and verification evidence are captured in bridge artifacts for independent review. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This report is the post-implementation lifecycle artifact for `WI-3213`. |

## Commands Run

- `gt projects show PROJECT-AGENT-RED-TEST-COVERAGE-GAPS --json` - confirmed `WI-3213` remains an open member of the active project and is covered by the active PAUTH snapshot.
- `gt bridge threads --wi WI-3213 --json` - confirmed thread
  `agent-red-wi3213-whatsapp-escalation-coverage`, latest path
  `bridge/agent-red-wi3213-whatsapp-escalation-coverage-002.md`, latest status `GO`.
- `python scripts\bridge_applicability_preflight.py --bridge-id agent-red-wi3213-whatsapp-escalation-coverage --json` - passed before implementation.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id agent-red-wi3213-whatsapp-escalation-coverage` - passed before implementation.
- `python scripts\bridge_claim_cli.py claim agent-red-wi3213-whatsapp-escalation-coverage` - acquired go-implementation claim, rowid `23795`.
- `python scripts\implementation_authorization.py begin --bridge-id agent-red-wi3213-whatsapp-escalation-coverage` - acquired implementation-start packet, packet hash `sha256:c3d565c9f21f6bbaf4bda6d3b576bb050d234ee03fb128a3fd34c56111847e11`.
- `python -m pytest applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py -q --tb=short` - passed.
- `python -m pytest applications/Agent_Red/tests/chat/test_whatsapp_escalation.py applications/Agent_Red/tests/multi_tenant/test_config_yaml_schema.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py -q --tb=short` - passed.
- `npm --prefix applications/Agent_Red/widget test -- whatsapp-escalation-link.test.tsx` - passed.
- `npm --prefix applications/Agent_Red/widget run typecheck` - passed.
- `python -m ruff check applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py` - passed.
- `python -m ruff format applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py` - applied mechanical formatting to approved touched Python targets.
- `python -m ruff format --check applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py` - passed.
- `git diff --check -- applications/Agent_Red/src/multi_tenant/cosmos_schema.py applications/Agent_Red/src/multi_tenant/config/field_mapping.py applications/Agent_Red/src/chat/pipeline/orchestrator.py applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx` - passed with no output.

## Observed Results

- Focused pytest result after final formatting: `collected 6 items`, `6 passed in 1.51s`.
- Adjacent Python bundle result after final formatting: `collected 64 items`, `64 passed in 6.84s`.
- Widget Vitest result after final formatting: `Test Files 1 passed (1)`, `Tests 1 passed (1)`.
- Widget typecheck result: `tsc --noEmit` exited 0.
- Ruff check result: `All checks passed!`
- Ruff format check result: `5 files already formatted`.
- Whitespace diff check result: exited 0 with no output.

## Files Changed

- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` - added `PreferencesDocument.whatsapp_business_phone`.
- `applications/Agent_Red/src/multi_tenant/config/field_mapping.py` - added `whatsapp_business_phone` to `_PREFS_DIRECT_FIELDS` and accepted formatter normalization.
- `applications/Agent_Red/src/chat/pipeline/orchestrator.py` - added `_build_whatsapp_escalation_markdown_link()`, used it from post-response escalation, emitted markdown-link WhatsApp text, and accepted formatter normalization in the approved target file.
- `applications/Agent_Red/tests/multi_tenant/test_whatsapp_config_spec1880.py` - new SPEC-1880 config/model persistence coverage.
- `applications/Agent_Red/tests/chat/test_whatsapp_escalation_spec1880.py` - new SPEC-1880 production-helper coverage.
- `applications/Agent_Red/widget/tests/whatsapp-escalation-link.test.tsx` - new widget markdown-link rendering coverage.

The shared worktree contains unrelated dirty/untracked bridge and project files from other workstreams. They are not part of this WI-3213 implementation claim.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this implementation includes narrow source fixes plus tests to make the already-specified deep-link feature reachable and verified.

## Acceptance Criteria Status

- PASS: `whatsapp_business_phone` is declared on `PreferencesDocument`.
- PASS: `whatsapp_business_phone` is in `_PREFS_DIRECT_FIELDS`.
- PASS: Config-to-preferences and preferences-to-config round-trip coverage preserves the field.
- PASS: The production WhatsApp helper emits a markdown link to `https://wa.me/...` with URL-encoded conversation context for professional and enterprise tenants with a configured phone.
- PASS: Starter tenants and missing phone configurations do not receive a WhatsApp link.
- PASS: The widget `MessageBubble` renders the WhatsApp markdown notice as a clickable anchor with the expected `href` and `_top` target.
- PASS: Targeted pytest, adjacent pytest, Vitest, widget typecheck, Ruff check, Ruff format check, and diff whitespace checks all pass.
- PASS: No formal artifacts, project membership, new work items, credentials, deployment state, release tags, provider integrations, phone identity features, full WhatsApp channel surfaces, webhooks, templates, or ACS/Meta API work were changed.

## Risk And Rollback

Residual risk is moderate-low because this touches the live tenant preference
model and the customer-visible escalation notice. The tests cover the intended
persistence, helper, and widget rendering contracts, and the source behavior is
limited to professional/enterprise tenants with a configured phone.

Rollback is to remove `whatsapp_business_phone` from `PreferencesDocument` and
`_PREFS_DIRECT_FIELDS`, restore the previous raw-URL escalation notice behavior
in `orchestrator.py`, and delete the three new SPEC-1880 test files. Bridge
audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
