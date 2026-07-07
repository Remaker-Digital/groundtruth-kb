NEW

# GT-KB Bridge Implementation Report - gtkb-wi5058-advisory-intake-profile-surfacing - 003

bridge_kind: implementation_report
Document: gtkb-wi5058-advisory-intake-profile-surfacing
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex)
Date: 2026-07-07T20:28:15Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; approval_policy=never

Responds to GO: bridge/gtkb-wi5058-advisory-intake-profile-surfacing-002.md
Approved proposal: bridge/gtkb-wi5058-advisory-intake-profile-surfacing-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5058-ACTIVITY-PROFILE-20260707
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW
Work Item: WI-5058
Recommended commit type: feat

## Implementation Claim

Implemented the WI-5058 activity-profile surfacing slice for advisory-intake workflows.

`config/agent-control/activity-disposition-profiles.toml` now surfaces `advisory-proposal` only in the `deliberation` activity profile and `advisory-intake` only in the `build` activity profile. This preserves the intended role separation: advisory authoring belongs to deliberation/advisory review context, while Prime Builder intake belongs to build context, and neither skill is exposed in unrelated activity profiles.

The canonical skill sources, generated Codex adapters, manifest entries, and registry entries were already created by the immediately preceding WI-5055 and WI-5056 slices. WI-5058 verifies those surfaces together with the profile routing and does not make ADVISORY entries implementation-dispatchable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision was required. Owner approval is carried by `DELIB-202665870` and PAUTH `PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5058-ACTIVITY-PROFILE-20260707`.

## Prior Deliberations

- `DELIB-202665870` - owner approved filing all six child implementation proposals for WI-5054 through WI-5059.
- `DELIB-202665487` - owner authorized the activity-profile surfacing and parity-test child items.
- `bridge/gtkb-wi5058-advisory-intake-profile-surfacing-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5058-advisory-intake-profile-surfacing-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5055-advisory-proposal-skill-003.md` - implementation report for the advisory-proposal skill surface.
- `bridge/gtkb-wi5056-prime-advisory-intake-skill-003.md` - implementation report for the advisory-intake skill surface.

## Specification-Derived Verification Plan

| Requirement | Executed verification evidence |
| --- | --- |
| Advisory authoring and Prime Builder intake must surface in intended contexts | Profile test passed, proving `advisory-proposal` is in `deliberation` and `advisory-intake` is in `build`. |
| Advisory skills must be absent from unrelated contexts | Profile test passed, proving no unrelated activity profile exposes either advisory skill. |
| Managed skill/adapter/catalog parity remains intact | Focused skill tests, catalog-contract test, and generator check passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposed WI-5058 test command passed and maps to `TEST-11296`. |
| Bridge/project authorization specs | Work-intent claim, applicability preflight, clause preflight, and implementation-start authorization all succeeded before report filing. |

## Commands Run

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5058-advisory-intake-profile-surfacing --json`
- `python scripts/bridge_claim_cli.py claim gtkb-wi5058-advisory-intake-profile-surfacing --session-id 019f3d79-c37d-7432-8c82-a66b675a389a --ttl-seconds 7200`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5058-advisory-intake-profile-surfacing --expires-minutes 120 --session-id 019f3d79-c37d-7432-8c82-a66b675a389a`
- `python -m pytest platform_tests/skills/test_advisory_intake_profile_surfacing.py platform_tests/skills/test_advisory_proposal_skill.py platform_tests/skills/test_advisory_intake_skill.py platform_tests/skills/test_skill_catalog_contract.py -q --tb=short`
- `python scripts/generate_codex_skill_adapters.py --update-registry --check`
- `python -m ruff check platform_tests/skills/test_advisory_intake_profile_surfacing.py platform_tests/skills/test_advisory_proposal_skill.py platform_tests/skills/test_advisory_intake_skill.py`
- `python -m ruff format --check platform_tests/skills/test_advisory_intake_profile_surfacing.py platform_tests/skills/test_advisory_proposal_skill.py platform_tests/skills/test_advisory_intake_skill.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5058-advisory-intake-profile-surfacing --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5058-advisory-intake-profile-surfacing`

## Observed Results

- Applicability preflight passed with packet hash `sha256:f05cff8283b26a3ee4a491008d934f1b97c693d44bee4e6e36d7faec7afa0073`; no missing required or advisory specs and no missing parent directories.
- Work-intent claim acquired for session `019f3d79-c37d-7432-8c82-a66b675a389a`; implementation deadline `2026-07-07T20:57:24Z`, grace through `2026-07-07T21:07:24Z`.
- Implementation-start authorization succeeded with packet hash `sha256:2fcf013fbca6b7921e60d7d656f3cfe8fdfb5f60aa101baeff8549616e7adcde`.
- Focused pytest command passed: `10 passed`.
- Generator post-check passed: `Codex skill adapters: PASS (42 adapters current)`.
- Ruff check passed.
- Ruff format check passed: `3 files already formatted`.
- ADR/DCL clause preflight passed; `Blocking gaps (gate-failing): 0`.

## Files Changed

- `config/agent-control/activity-disposition-profiles.toml`
- `groundtruth.db`

The skill, adapter, manifest, and registry surfaces were verified under WI-5058 but were created by WI-5055 and WI-5056. `platform_tests/skills/test_advisory_intake_profile_surfacing.py` was verified but did not require source edits.

## Acceptance Criteria Status

- [x] Skill surfacing is precise enough to avoid confusing ordinary bridge proposal or implementation flows with advisory intake.
- [x] TEST-11296 is satisfied by test output and this implementation-report evidence.
- [x] `advisory-proposal` is discoverable in the `deliberation` profile.
- [x] `advisory-intake` is discoverable in the `build` profile.
- [x] Neither advisory skill is surfaced in unrelated activity profiles.
- [x] Bridge lifecycle evidence is present: GO, work-intent claim, implementation-start authorization, preflight pass, and this report.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
