NO-GO

# GT-KB Bridge Verdict - gtkb-wi5055-advisory-proposal-skill - 004

bridge_kind: verification_verdict
Document: gtkb-wi5055-advisory-proposal-skill
Version: 004 (NO-GO)
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-07-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5055-advisory-proposal-skill-003.md

## Applicability Preflight

- packet_hash: `sha256:31a9af15711a3b2448da3deb1d137bf75a59cf8e158712b3837adb2e4c8fe9ee`
- bridge_document_name: `gtkb-wi5055-advisory-proposal-skill`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5055-advisory-proposal-skill-003.md`
- operative_file: `bridge/gtkb-wi5055-advisory-proposal-skill-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5055-advisory-proposal-skill`
- Operative file: `bridge\gtkb-wi5055-advisory-proposal-skill-003.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-202665870` - owner approved filing all six child implementation proposals for WI-5054 through WI-5059.
- `DELIB-202665484` - owner authorized the deliberation-side advisory-proposal skill child item.
- `bridge/gtkb-wi5055-advisory-proposal-skill-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5055-advisory-proposal-skill-002.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-wi5055-advisory-proposal-skill-003.md` - Prime Builder post-implementation report.

## Specifications Carried Forward

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

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Manual verification of `.claude/skills/advisory-proposal/SKILL.md` contents for owner confirmation guidelines | yes | pass |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Manual verification of `.claude/skills/advisory-proposal/SKILL.md` contents for owner confirmation guidelines | yes | pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/skills/test_advisory_proposal_skill.py -q --tb=short` | yes | pass |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5055-advisory-proposal-skill` | yes | pass |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5055-advisory-proposal-skill` | yes | pass |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Manual verification of implementation path constraints and preflights | yes | pass |
| `GOV-STANDING-BACKLOG-001` | Manual verification of MemBase project linkage | yes | pass |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verification of metadata links in the filed implementation report | yes | pass |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Verification of metadata links in the filed implementation report | yes | pass |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verification of version chain advancement in the bridge INDEX | yes | pass |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5055-advisory-proposal-skill` | yes | pass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5055-advisory-proposal-skill` | yes | pass |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Manual verification of target-path containment in GroundTruth-KB | yes | pass |

## Positive Confirmations

- Verified that `.claude/skills/advisory-proposal/SKILL.md` defines the draft-first Loyal Opposition ADVISORY capture workflow correctly, ensuring it is not treated as implementation approval and explicitly requires owner confirmation evidence.
- Verified that the Codex adapter was correctly generated and registered in `.codex/skills/MANIFEST.json`.
- Verified that the focused tests in `platform_tests/skills/test_advisory_proposal_skill.py` pass.

## Findings

### Finding 1: Broken capability registry test due to missing ollama and openrouter configurations

- **Observation**: The implementation of `skill.advisory-proposal` registration in `config/agent-control/harness-capability-registry.toml` lacks entries for the `ollama` and `openrouter` harnesses. This causes the pre-existing test suite `test_repository_registry_has_no_unclassified_missing_rows` in `platform_tests/scripts/test_check_harness_parity.py` to fail with an `AssertionError`.
- **Deficiency Rationale**: Since `skill.advisory-proposal` has `required_for_roles = ["loyal-opposition"]`, and both `ollama` and `openrouter` harnesses are registered with the `loyal-opposition` role, the capability parity scanner checks for their configurations. By failing to specify `status = "unsupported"` for these harnesses (similar to how `antigravity` and `cursor` are specified), the test suite breaks.
- **Proposed Solution**: Add configurations for `ollama` and `openrouter` to the `skill.advisory-proposal` section in `config/agent-control/harness-capability-registry.toml` declaring them as `status = "unsupported"` with appropriate justification.
- **Option Rationale**: This is the standard pattern used for all other skills that are unsupported on specific harnesses. Adding these declarations satisfies the parity test requirements.
- **Prime Builder Implementation Context**: Mutate the `skill.advisory-proposal` section in `config/agent-control/harness-capability-registry.toml` to include `status = "unsupported"` for `ollama` and `openrouter` to resolve the test failure.

## Required Revisions

1. Add `capabilities.ollama` and `capabilities.openrouter` entries declaring `status = "unsupported"` under `skill.advisory-proposal` in `config/agent-control/harness-capability-registry.toml`.
2. Ensure that `python -m pytest platform_tests/scripts/test_check_harness_parity.py` passes successfully on the worktree before resubmitting the implementation report.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5055-advisory-proposal-skill`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5055-advisory-proposal-skill`
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -v` (FAILED on missing harness rows)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
