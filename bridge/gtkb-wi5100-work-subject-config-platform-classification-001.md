NEW

# Implementation Proposal - WI-5100 work-subject config/ platform-classification carve-out

bridge_kind: prime_proposal
Document: gtkb-wi5100-work-subject-config-platform-classification
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5100

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d97ced75-3b71-45cb-ae8d-88a0dd70e33c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Summary

The work-subject enforcement classifier `classify_root` in `scripts/workstream_focus.py`
misclassifies every GT-KB platform config path under `config/` as
`application_product`, because `APPLICATION_PREFIXES` carries a blanket `"config/"`
entry and no `config/` platform subdir is carved into
`CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`. Under the default GT-KB
(`gtkb_infrastructure`) work subject, the PreToolUse Edit/Write gate then BLOCKS
edits to core platform config (dispatcher rules, governance preflight configs,
SoT registry, agent-control config, harness-parity config, project templates).
This proposal adds the six existing `config/` platform subdirectories to the
governance-prefix list so they classify as `current_repo_bridge_or_governance`
(editable under the GT-KB subject), and adds a `classify_root` regression test.

## Requirement Sufficiency

Existing requirements sufficient. This is a bounded defect fix under the
reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) and `GOV-STANDING-BACKLOG-001`
(WI-5100). It corrects the classifier to match the established taxonomy intent
(platform governance surfaces are GT-KB-subject-editable); no new requirement
capture is needed.

## Problem / Context

`scripts/workstream_focus.py`:

- `APPLICATION_PREFIXES` (line ~218-229) contains a blanket `"config/"` entry.
- `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` (line ~232-244) carves out
  `.claude/`, `.codex/`, `bridge/`, `memory/`, etc., but NOT any `config/`
  platform subdir.
- `classify_root` (line ~2028-2053) checks governance prefixes (line 2047)
  BEFORE application prefixes (line 2050), so a governance-prefix match wins.

Empirical `classify_root` evidence (2026-07-09), all returning
`application_product`:

- `config/agent-control/harness-capability-registry.toml`
- `config/dispatcher/rules.toml`
- `config/governance/spec-applicability.toml`
- `config/registry/sot-artifacts.toml`
- `config/agent-control/SESSION-STARTUP-INDEX.md`

(`.claude/rules/operating-model.md` correctly returns
`current_repo_bridge_or_governance`.) The current `config/` subdirs are:
`agent-control`, `dispatcher`, `governance`, `harness-parity`,
`project-templates`, `registry` - all GT-KB platform infrastructure, none an
application product surface in the GT-KB repo.

Impact: under the default GT-KB work subject, the work-subject gate blocks
authorized platform edits to all `config/**` files. This blocked an authorized
WI-4841 registry edit (a live GO'd proposal with a valid impl-start packet) and
would block WI-5040/5041 dispatcher-config work.

## Proposed Scope

1. In `scripts/workstream_focus.py`, add the six `config/` platform subdir
   prefixes to `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`:
   `config/agent-control/`, `config/dispatcher/`, `config/governance/`,
   `config/harness-parity/`, `config/project-templates/`, `config/registry/`.
   Because governance prefixes are matched before `APPLICATION_PREFIXES`, these
   subdirs classify as `current_repo_bridge_or_governance`. Any future `config/`
   path outside these subdirs still falls through to the blanket `config/`
   application prefix (conservative; preserves the app-config fallback).
   `APPLICATION_PREFIXES` is not modified.
2. Add a `classify_root` regression test in
   `platform_tests/hooks/test_workstream_focus.py` asserting each of the six
   platform config subdirs (representative file per subdir) classifies as
   `ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE`, and that an out-of-carve-out
   `config/<other>` path still classifies as `ROOT_APPLICATION_PRODUCT`
   (guards the carve-out precision).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail / numbered-file filing authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete spec links required.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived test evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization / project / work item / target-path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH-backed implementation.
- `GOV-RELIABILITY-FAST-LANE-001` - reliability fast-lane for small defect fixes.
- `GOV-STANDING-BACKLOG-001` - WI-5100 backlog linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under E:/GT-KB.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact-oriented governance linkage (defect -> backlog WI -> bridge proposal -> test).

## Bridge Protocol Compliance

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi5100-work-subject-config-platform-classification-001.md`) under
`bridge/`. The numbered bridge file chain is the append-only canonical audit
trail; no prior bridge version is deleted or rewritten
(`GOV-FILE-BRIDGE-AUTHORITY-001`).

## Prior Deliberations

- `DELIB-1035` - GTKB Work Subject And Root Enforcement post-implementation verification (the subsystem this fix corrects).
- `DELIB-20264063` - First-Class Project Artifacts And Subject Workflow Model (the Phase 7 work-subject taxonomy).
- `DELIB-1855` - Active-Workspace Declaration Architecture (work-subject declaration lineage).
- WI-5100 (this session) - owner AUQ 2026-07-09 directed characterize + capture, then fix-via-bridge.
- _No prior deliberation adds or removes a `config/` platform carve-out; this is a novel corrective to the Phase 7 prefix taxonomy._

## Owner Decisions / Input

- Owner AUQ (2026-07-09, session d97ced75): after the work-subject gate blocked an authorized WI-4841 registry edit, the owner selected "Characterize + capture the work-subject gate defect" (filed as WI-5100), then "Fix WI-5100 first (via bridge)."
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: standing reliability fast-lane authorization covering bounded source + test defect fixes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run pytest over platform_tests/hooks/test_workstream_focus.py (incl. the new classify_root carve-out test) via the project venv python -> all pass. |
| Defect closure | Re-run classify_root over the six platform config subdirs -> all return current_repo_bridge_or_governance; an out-of-carve-out config/ path -> application_product. |
| Code quality | ruff check and ruff format --check on scripts/workstream_focus.py and platform_tests/hooks/test_workstream_focus.py (both gates). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability + clause preflights pass (missing_required_specs empty; 0 blocking gaps). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root under E:/GT-KB. |

## Acceptance Criteria

- `classify_root` returns `current_repo_bridge_or_governance` for files under the six `config/` platform subdirs.
- The work-subject gate no longer blocks GT-KB-subject Edit/Write to `config/agent-control|dispatcher|governance|harness-parity|project-templates|registry/`.
- A regression test asserts the carve-out and its precision (out-of-carve-out `config/` still `application_product`).
- ruff check + ruff format --check pass on both changed files.
