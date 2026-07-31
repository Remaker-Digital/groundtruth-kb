NEW

# Implementation Report - WI-5100 work-subject config/ platform-classification carve-out

bridge_kind: implementation_report
Document: gtkb-wi5100-work-subject-config-platform-classification
Version: 003
Responds to: bridge/gtkb-wi5100-work-subject-config-platform-classification-002.md
Approved proposal: bridge/gtkb-wi5100-work-subject-config-platform-classification-001.md
Prior GO: bridge/gtkb-wi5100-work-subject-config-platform-classification-002.md
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5100

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d97ced75-3b71-45cb-ae8d-88a0dd70e33c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Summary

Implemented the WI-5100 fix per the GO'd `-001` proposal (GO at `-002`): added the
six existing GT-KB platform config subdirectories to
`CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` in `scripts/workstream_focus.py`, and
added a `classify_root` regression test. Because `classify_root` matches governance
prefixes BEFORE the blanket `config/` `APPLICATION_PREFIXES` entry,
`config/agent-control|dispatcher|governance|harness-parity|project-templates|registry/`
now classify as `current_repo_bridge_or_governance` (editable under the default
GT-KB work subject), while any other `config/` path still classifies as
`application_product`. `APPLICATION_PREFIXES` was not modified.

## Files Changed

- `scripts/workstream_focus.py` (+12): six `config/` platform subdir prefixes added
  to `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` with an explanatory WI-5100 comment.
- `platform_tests/hooks/test_workstream_focus.py` (+22): new
  `test_classify_root_config_platform_carveout` asserting the six subdirs classify
  as governance and that an out-of-carve-out `config/` path stays `application_product`.

Net: 34 insertions, 0 deletions (purely additive; `git diff --stat` confirmed no
collateral reformatting).

## Recommended Commit Type

`fix:` - repairs a classifier misclassification defect; adds no new capability surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test / Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/hooks/test_workstream_focus.py -k classify_root` | yes | 2 passed |
| Defect closure (classify_root carve-out) | `test_classify_root_config_platform_carveout` asserts 6 platform config subdirs -> current_repo_bridge_or_governance; out-of-carve-out config/ -> application_product | yes | pass |
| Code quality (lint) | `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py` | yes | All checks passed |
| Code quality (format) | `python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py` | yes | 2 files already formatted |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all target paths in-root under E:/GT-KB | yes | pass |

## Commands Executed

```
python -m pytest platform_tests/hooks/test_workstream_focus.py -k classify_root  -> 2 passed, 73 deselected
python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py  -> All checks passed!
python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py  -> 2 files already formatted
```

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). Bounded reliability
fast-lane defect fix under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; no new
requirement capture needed.

## Owner Decisions / Input

- Owner AUQ (2026-07-09, session d97ced75): after the work-subject gate blocked an authorized WI-4841 registry edit, the owner selected "Characterize + capture the work-subject gate defect" (filed WI-5100), then "Fix WI-5100 first (via bridge)."
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: standing reliability fast-lane authorization covering bounded source + test defect fixes.

## Prior Deliberations

- `DELIB-1035` - GTKB Work Subject And Root Enforcement (the subsystem this fix corrects).
- `DELIB-20264063` - First-Class Project Artifacts And Subject Workflow Model (Phase 7 taxonomy).
- `bridge/gtkb-wi5100-work-subject-config-platform-classification-002.md` - the LO GO carried forward.

## Bridge Protocol Compliance

Filed as the next numbered bridge file
(`bridge/gtkb-wi5100-work-subject-config-platform-classification-003.md`); the
numbered bridge file chain is the append-only canonical audit trail and no prior
version is deleted or rewritten (`GOV-FILE-BRIDGE-AUTHORITY-001`).
