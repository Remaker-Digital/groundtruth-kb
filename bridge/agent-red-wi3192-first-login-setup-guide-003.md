NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: harness-state registry plus bridge work-intent claim and current Codex runtime

# GT-KB Bridge Implementation Report - agent-red-wi3192-first-login-setup-guide - 003

bridge_kind: implementation_report
Document: agent-red-wi3192-first-login-setup-guide
Version: 003 (NEW; post-implementation report)
Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3192
Responds to GO: bridge/agent-red-wi3192-first-login-setup-guide-002.md
Approved proposal: bridge/agent-red-wi3192-first-login-setup-guide-001.md
target_paths: ["applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py", "applications/Agent_Red/docs/getting-started/setup.html"]
Implementation Authorization Packet: sha256:83c724f00de3eb4f2e098f69f0052c216c96a5f80a5fabbc52642c614bb066ba
Recommended commit type: test:

## Implementation Claim

Implemented the approved WI-3192 documentation coverage gap inside the two GO-authorized target paths.

The new pytest file `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` reads both the authoritative Docusaurus source markdown and the shipped static setup HTML. It fails closed if the First login section is missing, is no longer between Account provisioning and API key configuration, loses the magic-link flow details, drops the sequence-diagram evidence, omits the Securing Agent Red link, omits the API-key/password-manager tip, or regresses to the stale claim that API keys are delivered in the welcome email.

The shipped static page `applications/Agent_Red/docs/getting-started/setup.html` now includes the First login section from the current source guide, updates the setup overview to six stages, removes the stale "API key is delivered in your welcome email" language, carries the magic-link step list, links to Securing Agent Red, preserves an HTML marker for the first-login sequence diagram, and updates the visible/table-of-contents order.

No runtime authentication code, credentials, deployment state, formal GT-KB artifacts, project membership, or new project work items were changed for this WI.

## Specification Links

- `SPEC-1740` - Direct target requirement: Initial Setup must document the first-login two-email magic-link flow, sequence diagram, step-by-step instructions, Securing Agent Red link, and API-key-saving tip.
- `SPEC-0429` - Contextual auth requirement: passwordless magic-link authentication is the primary tenant-scoped admin sign-in flow and may lead to optional 2FA.
- `SPEC-1281` - Contextual magic-link requirement: magic-link requests are time/rate bounded; setup docs must not imply reusable or long-lived links.
- `SPEC-1286` - Contextual magic-link requirement: magic-link tokens are single-use.
- `SPEC-1619` - Contextual magic-link origin requirement: tenant-scoped magic-link flows preserve tenant context.
- `SPEC-0803` - Documentation diagram requirement: docs must preserve Mermaid diagram coverage.
- `GOV-10` - Test artifacts must exercise exposed production interfaces; for this docs gap, the shipped static docs page is the user-facing artifact.
- `SPEC-1649` - Master test plan/live-interface policy; static HTML is checked alongside source markdown to avoid source-only closure.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Python test changes must satisfy repo-native lint and formatting gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority and append-only numbered bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification to map linked specifications to executed test evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata in implementation-targeting bridge artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this report does not add scope to the snapshot-bound project.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses the governed bridge helper path and explicit evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation report as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision was required. This implementation used the active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and stayed within the GO-approved target paths for `WI-3192`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `bridge/agent-red-wi3192-first-login-setup-guide-001.md` - Approved implementation proposal carried forward.
- `bridge/agent-red-wi3192-first-login-setup-guide-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-1740` | Added `test_setup_markdown_first_login_meets_spec_1740` and `test_setup_html_first_login_matches_shipped_static_page`. They verify heading order, First login content, Sign in to Dashboard, no API key by email, magic-link flow, one-time 15-minute login link, 8-hour session, Account & billing API key/widget key retrieval, Securing Agent Red link, API-key password-manager tip, and static-page presence. Verified by targeted pytest with `3 passed`. |
| `SPEC-0429`, `SPEC-1281`, `SPEC-1286`, `SPEC-1619` | The same tests assert the documented passwordless magic-link flow, one-time link wording, 15-minute expiration, 8-hour authenticated session, and tenant/account-created email context. The static page no longer implies API-key email delivery or bearer-token email handling. |
| `SPEC-0803` | Markdown test asserts the source First login section includes a Mermaid `sequenceDiagram`; static HTML test asserts the shipped page includes a first-login sequence-diagram marker so stale static output cannot omit the diagram position silently. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Repository-native pytest now parses both `docs-site/docs/getting-started/setup.md` and `docs/getting-started/setup.html`, exercising the user-facing shipped docs artifact rather than closing from source-only evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation began only after a live GO, work-intent claim, and implementation-start packet for this bridge slug. Packet hash: `sha256:83c724f00de3eb4f2e098f69f0052c216c96a5f80a5fabbc52642c614bb066ba`, created `2026-06-23T12:17:44Z`, expiring `2026-06-23T14:17:44Z`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `python -m ruff check applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` returned `All checks passed!`; `python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` returned `1 file already formatted`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report preserves the approved bridge chain, status token, PAUTH/project/WI metadata, target path metadata, carried-forward spec links, and executed spec-to-test mapping for Loyal Opposition verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The approved changes are under `applications/Agent_Red/docs/` and `applications/Agent_Red/tests/`. |
| `GOV-STANDING-BACKLOG-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The work remains tied to `WI-3192`, the active project authorization, the GO-approved bridge thread, the official implementation-start packet, and this durable implementation report. |

## Commands Run

- `gt projects show PROJECT-AGENT-RED-TEST-COVERAGE-GAPS --json`
- `gt bridge threads --wi WI-3192 --json`
- `python scripts/bridge_claim_cli.py claim agent-red-wi3192-first-login-setup-guide`
- `python scripts/implementation_authorization.py begin --bridge-id agent-red-wi3192-first-login-setup-guide`
- `python -m pytest applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py -q --tb=short`
- `python -m ruff check applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py`
- `python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py`

## Observed Results

- Initial implementation-start attempt failed closed because the bridge scope was briefly claimed by another session until `2026-06-23T12:16:46Z`; no protected mutation was performed before that claim expired.
- Work-intent claim acquired for `agent-red-wi3192-first-login-setup-guide` as `go_implementation` for project `PROJECT-AGENT-RED-TEST-COVERAGE-GAPS` and work item `WI-3192`, acquired `2026-06-23T12:17:43Z`.
- Implementation authorization succeeded with latest status `GO`, requirement sufficiency `sufficient`, target path globs `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` and `applications/Agent_Red/docs/getting-started/setup.html`, and packet hash `sha256:83c724f00de3eb4f2e098f69f0052c216c96a5f80a5fabbc52642c614bb066ba`.
- Targeted pytest completed successfully: `3 passed in 1.08s`.
- Ruff lint completed successfully: `All checks passed!`.
- Ruff format check completed successfully: `1 file already formatted`.

## Files Changed

- `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py`
- `applications/Agent_Red/docs/getting-started/setup.html`

The helper's plan mode observed unrelated pre-existing dirty files elsewhere in the worktree. Those files are outside WI-3192 target paths and were not modified as part of this implementation.

## Recommended Commit Type

- Recommended commit type: `test:`
- Diff-stat justification: Adds repository-native regression coverage for `SPEC-1740` and updates the shipped static docs artifact to satisfy the tested documentation requirement.

```text
applications/Agent_Red/docs/getting-started/setup.html                 | 34 +++++++++++++++++-----
applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py | 106 +++++++++++++++++++++++++
2 files changed
```

## Acceptance Criteria Status

- PASS - Added tests fail closed if `setup.md` loses the First login section, moves it outside the required Account provisioning/API key configuration position, drops the Mermaid sequence diagram, omits step-by-step instructions, omits the Securing Agent Red link, or omits the API-key/password-manager tip.
- PASS - Added tests fail closed if shipped `setup.html` is stale and omits the first-login magic-link flow.
- PASS - Shipped `setup.html` now includes the First login section, static sequence-diagram marker, link to Securing Agent Red, API-key-saving tip, and updated API-key header language.
- PASS - Tests reject the stale static claim that the API key is delivered in the welcome email and the old bearer-header API-key sample.
- PASS - No runtime authentication code, credentials, deployment state, formal artifacts, project membership, or out-of-scope work items were mutated under this proposal.
- PASS - Exact command output and linked-spec mapping are included for Loyal Opposition verification.

## Risk And Rollback

Residual risk is low and limited to documentation/test surface area. The static HTML update is a targeted refresh of the already-shipped setup page content, and the new test uses only local file reads with no network, browser, credentials, or deployment dependency.

Rollback is to remove `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` and revert the WI-3192 hunk in `applications/Agent_Red/docs/getting-started/setup.html`; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
