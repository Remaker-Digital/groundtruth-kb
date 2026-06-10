NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 2026-06-07T01-02-49Z-prime-builder-transcript-scan-p1
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder; owner-directed PROJECT-GTKB-RELIABILITY-FIXES P1 chase-through
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Startup Role-Slot Labels Disambiguate Active Harness And Work Subject (WI-4391)

bridge_kind: prime_proposal
Document: gtkb-startup-role-slot-label-disambiguation
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Codex Prime Builder
Date: 2026-06-07 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4391
target_paths: ["scripts/session_self_initialization.py", "scripts/workstream_focus.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/hooks/test_workstream_focus.py"]
Recommended commit type: fix:

## Claim

The generated startup disclosure can show two lines with the same visible label, Bridge role slot, but different values in the same message: one from Current Project State for the active harness role slot, and one from Active Work Subject for the work-subject bridge slot. The last-24h transcript scan found 21 Codex startup records with both prime-builder and shared under that same label.

The fix is display-only: keep the underlying state fields intact, but rename the visible labels so the two dimensions are unambiguous.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-RELIABILITY-FAST-LANE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- GOV-SESSION-ROLE-AUTHORITY-001
- DCL-SESSION-ROLE-RESOLUTION-001
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001
- GOV-SESSION-SELF-INITIALIZATION-001
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001

## Reliability Fast-Lane Eligibility

1. Origin defect/regression: met. WI-4391 is a transcript-observed startup disclosure ambiguity.
2. No new public API/CLI: met. The implementation changes display labels and tests only.
3. No forbidden operations: met. No deploy, force-push, spec deletion, or data migration.
4. Small single-concern scope: met. One startup-label concern across the two renderers and focused tests.

## Prior Deliberations

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: standing reliability fast-lane direction and PAUTH basis.
- The startup payload canonical-state drift thread established that startup role/topology fields must derive from canonical helpers rather than stale defaults; this proposal preserves that derivation and fixes only the visible label collision.
- WI-4391 transcript-scan evidence: owner-requested scan on 2026-06-06 captured the duplicate-label startup records.

## Owner Decisions / Input

No new owner decision required. Mike explicitly directed this session to elevate these PROJECT-GTKB-RELIABILITY-FIXES items and chase them through to completion. The standing PAUTH covers small source/test reliability fixes by active project membership.

## Scope

IP-1: Rename the Current Project State role-slot line in scripts/session_self_initialization.py to identify it as the active harness role slot while preserving the canonical derivation from harness-state/harness-registry.json.

IP-2: Rename the Active Work Subject role-slot line in scripts/workstream_focus.py to identify it as the work-subject bridge role slot while preserving the existing state field and semantics.

IP-3: Update focused startup/workstream tests so the generated disclosure cannot contain duplicate ambiguous Bridge role slot labels with conflicting values.

## Out Of Scope

- Changing role derivation, work-subject state schema, harness registry data, or bridge dispatch behavior.
- Changing startup focus selection behavior or the init-keyword contract.
- Editing generated dashboard JSON except if a normal startup regeneration updates generated startup report artifacts as a consequence of the source fix.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 / GOV-SESSION-SELF-INITIALIZATION-001 | Startup report/disclosure tests assert the role/governance disclosure remains present and label dimensions are distinct. |
| GOV-SESSION-ROLE-AUTHORITY-001 / DCL-SESSION-ROLE-RESOLUTION-001 | Current Project State continues to derive active harness role slot from canonical role helpers; tests assert the visible label no longer collides with work-subject state. |
| GOV-RELIABILITY-FAST-LANE-001 | Manual target-path inspection confirms source + test-only, one-concern fast-lane scope. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Post-implementation report will carry executed pytest/ruff evidence. |

Implementation verification will run:

- python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py -q -k "role_slot or startup_focus_lines or active_work_subject or current_project_state" --tb=short
- python -m ruff check scripts/session_self_initialization.py scripts/workstream_focus.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py
- python -m ruff format --check scripts/session_self_initialization.py scripts/workstream_focus.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py

## Acceptance Criteria

- [ ] Loyal Opposition returns GO.
- [ ] Startup disclosure/report no longer emits two identical Bridge role slot labels with different values.
- [ ] Current Project State labels the active harness role-slot dimension explicitly.
- [ ] Active Work Subject labels the work-subject bridge role-slot dimension explicitly.
- [ ] Focused tests fail before and pass after the fix.
- [ ] Post-implementation report carries observed verification commands and results.
- [ ] Loyal Opposition returns VERIFIED before WI-4391 is closed.

## Risk And Rollback

Risk is low: this is display-label wording only. Rollback is file-level revert of the label changes and tests. The role map, work-subject state, and startup routing behavior remain unchanged.
