NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex Desktop interactive Prime Builder session; application-mode heartbeat continuation

# Implementation Proposal - WI-3192 First-Login Setup Guide Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3192-first-login-setup-guide
Version: 001
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3192

target_paths: ["applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py", "applications/Agent_Red/docs/getting-started/setup.html"]

## Claim

Add deterministic repository-native pytest evidence for `SPEC-1740` by verifying the Agent Red Initial Setup guide's first-login magic-link documentation in both the Docusaurus source page and the shipped static docs page. The current Docusaurus source `applications/Agent_Red/docs-site/docs/getting-started/setup.md` already contains the required First login section, but the shipped static page `applications/Agent_Red/docs/getting-started/setup.html` is stale and omits that section. This proposal therefore pairs a focused regression test with a static-page refresh so the live published docs artifact is covered rather than only the source markdown.

This proposal is intentionally limited to documentation-output synchronization and test evidence. It does not change the magic-link runtime, send email, call the production docs site, deploy docs, add project work items, or mutate formal GOV/SPEC/ADR/DCL/PB/REQ artifacts.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-1740` gives the exact content requirements: the Initial Setup page must include a First Login section between Account Provisioning and API Key Configuration explaining the two-email magic-link authentication flow for new tenant superadmins, including a sequence diagram, step-by-step instructions, a link to the Securing Agent Red page, and a tip about saving the API key. Although `SPEC-1740` is now retired as FAB-11 app-scoped history, `WI-3192` remains an open member of the snapshot-authorized project and asks for deterministic evidence for that specific historical gap. No owner clarification is needed because the implementation is limited to preserving and testing existing documentation behavior.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` and `applications/Agent_Red/docs/getting-started/setup.html`.

## Bridge File Chain Evidence

This is a first `NEW` proposal for document `agent-red-wi3192-first-login-setup-guide`. If approved by the preflight gates, it will be filed append-only as `bridge/agent-red-wi3192-first-login-setup-guide-001.md` through the governed helper-mediated bridge path. No prior version exists and no prior bridge version will be rewritten or deleted.

## Specification Links

- `SPEC-1740` - Direct target requirement: the Initial Setup page must document the first-login two-email magic-link flow, include a sequence diagram and step-by-step instructions, link to Securing Agent Red, and include a tip about saving the API key.
- `SPEC-0429` - Contextual auth requirement: magic-link authentication is the primary passwordless flow for tenant-scoped admin sign-in and can lead to optional 2FA.
- `SPEC-1281` - Contextual magic-link requirement: magic-link requests are time/rate bounded; the setup guide's flow must not imply reusable or long-lived links.
- `SPEC-1286` - Contextual magic-link requirement: magic-link tokens are single-use; setup-guide language must remain compatible with one-time link behavior.
- `SPEC-1619` - Contextual magic-link origin requirement: tenant-scoped magic-link flows preserve the origin tenant context; docs should not imply cross-tenant sign-in.
- `SPEC-0803` - Documentation diagram requirement; the source setup guide uses Mermaid sequence diagrams and the regression should preserve the required first-login sequence diagram.
- `GOV-10` - Test artifacts must exercise exposed production interfaces; for this docs requirement, the shipped static docs page is the user-facing artifact and must be checked alongside source markdown.
- `SPEC-1649` - Master test plan/live-interface policy; this proposal avoids source-only closure by asserting the published static HTML artifact as the live docs surface.
- `GOV-12` - Work item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped authorization is the bounded owner approval source for this WI but does not bypass bridge review, GO, implementation-start, report, or verification gates.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Requires the proposal to account for the baseline code-quality rules.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete proposal specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification to map linked specs to executed test evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines in implementation-targeting proposals.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the helper-mediated bridge write path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The bridge proposal is the durable artifact for implementation intent.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Implementation intent and review evidence are preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The owner-authorized WI implementation crosses the threshold for bridge proposal capture.

## Prior Deliberations

- `DELIB-0712` - 16.B methodology review classifying coverage gaps, including `SPEC-1740`, by evidence quality.
- `DELIB-0713` - Owner decision rejecting assertion-only/phantom-only evidence as sufficient for behavioral requirements.
- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-20265110` - POR Step 16.D phantom spec-link cleanup review; relevant to avoiding false coverage from stale or phantom evidence.
- `DELIB-20263468` - WI-4455 Loyal Opposition advisory recognizing repository-native pytest evidence as the live verification surface.
- `DELIB-0259` - G6 template starter kits proposal review; relevant because it discusses first-login `OnboardingWizard` ownership and merchant onboarding friction.
- `DELIB-0139` - Direct Agent Chat review; relevant to magic-link admin session behavior and keeping admin-auth documentation aligned with actual auth surfaces.
- Semantic deliberation search for `SPEC-1740 First-login magic link setup guide` returned broader Agent Red magic-link and onboarding records but no more specific owner decision that changes the exact `SPEC-1740` content checklist.

## Owner Decisions / Input

- `DELIB-20265586` and `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23` authorize bounded implementation for the snapshot-bound 38-WI project membership, including `WI-3192`.
- Mutation classes: `test_addition` and `source` for the static docs artifact refresh.
- No new owner input is required. This proposal does not add a work item, broaden project membership, deploy, mutate credentials, perform destructive cleanup, or change formal GOV/SPEC/ADR/DCL/PB/REQ artifacts.

## Proposed Scope

1. Add `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` with focused pytest coverage for the Initial Setup guide.
2. In the new test file, parse `applications/Agent_Red/docs-site/docs/getting-started/setup.md` and assert:
   - `## First login` appears after `## 1. Account provisioning` and before `## 2. API key configuration`.
   - The First login section includes a Mermaid `sequenceDiagram`.
   - The section describes the welcome-email entry point, the second email containing the one-time magic link, the 15-minute expiry, the 8-hour authenticated session, the Account & billing key retrieval path, the Securing Agent Red link, and the password-manager/API-key tip.
3. In the same test file, parse `applications/Agent_Red/docs/getting-started/setup.html` as the shipped static docs artifact and assert:
   - A rendered First login heading exists between Account provisioning and API key configuration.
   - The visible text contains the magic-link flow, the second email, one-time/expiry/session language, Account & billing key retrieval, and the password-manager/API-key tip.
   - The rendered page links to `/docs/admin-guide/mfa-security`.
4. Refresh `applications/Agent_Red/docs/getting-started/setup.html` from the already-correct Docusaurus source so the shipped static page satisfies the new regression test. Do not edit `applications/Agent_Red/docs-site/docs/getting-started/setup.md` unless implementation discovers source drift not visible in the current preflight inspection; if that happens, stop and revise the bridge target path rather than widening scope silently.
5. Do not change magic-link runtime code, generated credentials, deployment state, or production docs hosting. Do not add dependency packages; use Python standard-library parsing helpers unless an existing repo dependency is already required by the local test pattern.

## Pre-Filing Preflight Evidence

- Applicability preflight command: `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3192-first-login-setup-guide-001.md --json`
  - Result: exit 0; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
  - Note: the preflight emitted a non-blocking missing-parent warning for a bare `tests/multi_tenant/test_setup_guide_spec1740.py` token derived from path text. The declared `target_paths` are valid in-root Agent Red paths: `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` and `applications/Agent_Red/docs/getting-started/setup.html`.
- Clause preflight command: `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3192-first-login-setup-guide-001.md`
  - Result: exit 0; clauses evaluated 5; `must_apply: 4`; evidence gaps in must-apply clauses 0; blocking gaps 0; mandatory mode.

## Specification-Derived Verification Plan

| Spec / Requirement | Test Evidence To Add | Expected Result |
|---|---|---|
| `SPEC-1740` first-login setup-guide content | New pytest assertions against source markdown and shipped static HTML for section ordering, magic-link flow content, sequence diagram, step-by-step content, Securing Agent Red link, and API-key saving tip | The docs source and shipped static page both satisfy the complete `SPEC-1740` content checklist |
| `SPEC-0429`, `SPEC-1281`, `SPEC-1286`, `SPEC-1619` contextual auth requirements | The docs test asserts passwordless magic-link language stays bounded to one-time/expiry/session behavior and points to the detailed security page instead of restating runtime internals | Setup-guide docs remain consistent with existing magic-link authentication semantics |
| `SPEC-0803` documentation diagrams | Source markdown test asserts the First login section includes a Mermaid `sequenceDiagram` | The diagram requirement cannot regress silently from the setup guide source |
| `GOV-10` / `SPEC-1649` live-interface evidence | Static HTML test exercises the shipped docs artifact, not only markdown source | The WI is not closed by source-only or assertion-only evidence |

Verification commands after implementation:

```powershell
python -m pytest applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py
```

If the static page is refreshed through the Docusaurus build pipeline, the implementation report must also include the exact build command used and identify any generated files excluded from this WI's target path.

## Acceptance Criteria

- Added tests fail closed if the source setup guide loses the First login section, moves it outside the required Account Provisioning/API Key Configuration position, drops the Mermaid sequence diagram, omits step-by-step instructions, omits the Securing Agent Red link, or omits the API-key/password-manager tip.
- Added tests fail closed if the shipped static setup page is stale relative to the source and omits the rendered First login flow.
- The shipped static setup page includes the first-login magic-link section from the current Docusaurus source.
- No runtime authentication code, credentials, deployment state, formal artifacts, or project membership are mutated under this proposal.
- Post-implementation report includes exact command output and maps each linked spec to observed test evidence.

## Code Quality Baseline

| Rule | Applicability | Proposal Position |
|---|---|---|
| `CQ-SECRETS-001` | Applies | Tests must not embed real API keys, magic-link tokens, emails, or tenant secrets. |
| `CQ-PATHS-001` | Applies | Tests derive repo paths from `Path(__file__).resolve()` rather than absolute runtime paths. |
| `CQ-CONSTANTS-001` | Applies | Required section titles and documentation phrases are stable spec text; keep helpers small and readable. |
| `CQ-DOCS-001` | Applies | Test names should describe the documentation contract; no noisy comments. |
| `CQ-COMPLEXITY-001` | Applies | Keep parsing helpers focused and use standard-library HTML/text normalization. |
| `CQ-TESTS-001` | Applies | This proposal is primarily a test-addition with a static docs refresh needed for the user-facing artifact. |
| `CQ-LOGGING-001` | N/A | No logging behavior changes. |
| `CQ-SECURITY-001` | Applies | Documentation assertions must not expose real credentials or encourage saving API keys outside a password manager. |
| `CQ-VERIFICATION-001` | Applies | Automated pytest plus ruff check/format evidence required. |
| `CQ-PERF-001` | N/A | No hot-path production code or unbounded runtime loops added. |
| `CQ-DEPS-001` | Applies | No dependency changes; use existing toolchain/stdlib. |

## Risks / Rollback

- Risk: A docs test that checks only `setup.md` would miss the current static-page drift. Mitigation: the test must cover both source markdown and the shipped `setup.html`.
- Risk: Refreshing a generated static page manually can drift from the Docusaurus build pipeline. Mitigation: keep the change limited to the target page, report whether a build was used, and do not silently include unrelated generated asset churn.
- Risk: `SPEC-1740` is retired in MemBase, so Loyal Opposition may require explicit framing for app-scoped historical closure. Mitigation: this proposal states the spec status and ties the work to the still-open, snapshot-authorized `WI-3192`.
- Rollback: delete `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py` and revert `applications/Agent_Red/docs/getting-started/setup.html` to its previous static content. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/multi_tenant/test_setup_guide_spec1740.py`
- `applications/Agent_Red/docs/getting-started/setup.html`

## Recommended Commit Type

`test`
