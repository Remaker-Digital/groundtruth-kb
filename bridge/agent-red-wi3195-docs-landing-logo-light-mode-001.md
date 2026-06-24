NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: harness-state registry plus current Codex runtime

# Implementation Proposal - WI-3195 Docs Landing Logo Light/Dark Variant Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3195-docs-landing-logo-light-mode
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3195

target_paths: ["applications/Agent_Red/docs-site/docs/intro.md", "applications/Agent_Red/docs-site/static/img/primary-logo-no-wordmark_white_text.svg", "applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py"]

## Claim

WI-3195 should be implemented as a narrow source-and-test correction for `SPEC-1743`.

MemBase currently shows `SPEC-1743` as `retired` because FAB-11 retired stale assertion history after Agent Red isolation moved the referenced docs under `applications/Agent_Red/`; the open WI remains the active project work item for replacing assertion-only evidence with deterministic tests. The live docs source already uses the required black-text SVG variant for light mode:

- `applications/Agent_Red/docs-site/docs/intro.md` references `/img/primary-logo-no-wordmark_black_text.svg` for the `ThemedImage` light source.

The same source currently references `/img/agent-red-logo.svg` for the dark source. That asset appears to be the white-text logo variant, but `SPEC-1743` names the required dark-mode file as `primary-logo-no-wordmark_white_text.svg`. To make the implementation match the spec text and keep the test deterministic, this proposal authorizes only:

- update `applications/Agent_Red/docs-site/docs/intro.md` so its `ThemedImage` dark source uses `/img/primary-logo-no-wordmark_white_text.svg`;
- add `applications/Agent_Red/docs-site/static/img/primary-logo-no-wordmark_white_text.svg` as the spec-named white-text docs-site asset, using the current white-text logo SVG content already present in `agent-red-logo.svg`;
- add `applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py` to assert the exact Docusaurus `ThemedImage` source switch and asset characteristics.

This proposal does not authorize runtime application code, generated static HTML, navbar configuration, credentials, deployment state, formal GT-KB artifact mutation, project membership changes, or new work items.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1743` and `WI-3195` together state the testable target: the docs landing page (`intro.md`) must render the Agent Red logo through Docusaurus `ThemedImage`, use `primary-logo-no-wordmark_black_text.svg` in light mode, and use the white-text variant in dark mode. `WI-3195` explicitly exists because previous assertion-only evidence was insufficient per `DELIB-0712` and `DELIB-0713`. No owner clarification is needed to align the filename with the requirement and add deterministic tests for that behavior.

## In-Root Placement Evidence

The implementation targets are under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\docs-site\docs\intro.md`
- `E:\GT-KB\applications\Agent_Red\docs-site\static\img\primary-logo-no-wordmark_white_text.svg`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_docs_landing_logo_spec1743.py`

Read-only evidence surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\docs-site\static\img\primary-logo-no-wordmark_black_text.svg`
- `E:\GT-KB\applications\Agent_Red\docs-site\static\img\agent-red-logo.svg`

## Specification Links

- `SPEC-1743` - Direct target documentation requirement for docs landing page logo source switching: black-text SVG in light mode and white-text SVG in dark mode.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live Docusaurus markdown source and docs-site SVG assets are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate the documentation artifact rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies the baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the governed bridge helper path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside the snapshot-bound project member `WI-3195`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3195 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- MemBase `SPEC-1743` title: "Docs site landing page logo must use black text variant in light mode".
- MemBase `SPEC-1743` description requires the docs landing page (`intro.md`) to use the black-text SVG variant in light mode and the white-text variant in dark mode through Docusaurus `ThemedImage`.
- MemBase `get_tests_for_spec("SPEC-1743")` returned `[]`, confirming no current linked test evidence.
- `applications/Agent_Red/docs-site/docs/intro.md` currently imports `ThemedImage` from `@theme/ThemedImage`.
- The current `ThemedImage` light source is `/img/primary-logo-no-wordmark_black_text.svg`.
- The current dark source is `/img/agent-red-logo.svg`, while the exact spec-named `primary-logo-no-wordmark_white_text.svg` asset is absent from `applications/Agent_Red/docs-site/static/img/`.
- `applications/Agent_Red/docs-site/static/img/agent-red-logo.svg` uses white fills for the wordmark paths and is suitable as the source content for the spec-named dark-mode asset alias.

## Pre-Filing Preflight Evidence

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3195-docs-landing-logo-light-mode-001.md --json
```

Observed:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:2afd1c7c3791f66962b729a3b0cdb6d668c2e80dc3986cef19ce5de301912751`
- warning only: parser harvested bare `tests/multi_tenant/test_docs_landing_logo_spec1743.py` strings from command/prose text; declared target paths remain in-root under `applications/Agent_Red/`.

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3195-docs-landing-logo-light-mode-001.md
```

Observed:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1743` | New pytest parses `docs-site/docs/intro.md` and asserts the docs landing page imports/uses Docusaurus `ThemedImage`, has an `alt` value for the Agent Red logo, maps `light` to `/img/primary-logo-no-wordmark_black_text.svg`, and maps `dark` to `/img/primary-logo-no-wordmark_white_text.svg`. |
| `SPEC-1743` | New pytest verifies both referenced SVG assets exist under `docs-site/static/img/`; verifies the light asset contains black wordmark fill evidence; verifies the dark asset contains white wordmark fill evidence. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic docs-source test file. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3195-docs-landing-logo-light-mode`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py
```

## Acceptance Criteria

- PASS when `intro.md` uses `ThemedImage` for the landing-page Agent Red logo.
- PASS when the light-mode source is exactly `/img/primary-logo-no-wordmark_black_text.svg`.
- PASS when the dark-mode source is exactly `/img/primary-logo-no-wordmark_white_text.svg`.
- PASS when both referenced SVG assets exist under `docs-site/static/img/`.
- PASS when the deterministic pytest verifies black-text evidence for the light asset and white-text evidence for the dark asset.
- PASS when the targeted pytest and ruff commands all pass.
- PASS when no runtime application code, generated static HTML, navbar configuration, credentials, deployment state, formal artifacts, project membership, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal changes only the Docusaurus landing-page source, adds one docs-site SVG asset alias using current white-text logo content, and adds one source-level regression test. The main risk is asset duplication drift if future branding changes update only one logo file. The new pytest mitigates that risk by checking the docs landing page references the spec-named assets and that those assets have the expected wordmark color evidence.

Rollback is to revert `applications/Agent_Red/docs-site/docs/intro.md`, delete `applications/Agent_Red/docs-site/static/img/primary-logo-no-wordmark_white_text.svg`, and delete `applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/docs-site/docs/intro.md`
- `applications/Agent_Red/docs-site/static/img/primary-logo-no-wordmark_white_text.svg`
- `applications/Agent_Red/tests/multi_tenant/test_docs_landing_logo_spec1743.py`

## Recommended Commit Type

`test:`
