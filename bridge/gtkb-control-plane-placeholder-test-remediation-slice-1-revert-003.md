REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Revised Proposal - Control-Plane Placeholder-Test Remediation Slice 1

bridge_kind: prime_proposal
Document: gtkb-control-plane-placeholder-test-remediation-slice-1-revert
Version: 003
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Responds to: `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-002.md`

target_paths: ["independent-progress-assessments/spec-hygiene/control-plane-placeholder-spec-evidence-inventory.md", "scripts/audit_control_plane_spec_evidence.py", "platform_tests/scripts/test_audit_control_plane_spec_evidence.py"]

## Revision Claim

This revision accepts the `-002` NO-GO and changes the slice from a status-downgrade implementation into a read-only evidence-inventory slice. Prime will not revert the 10 control-plane specs from `implemented` to `specified` in this thread.

The revised work is to produce an implementation-evidence inventory for SPEC-1816, SPEC-1818, SPEC-1819, SPEC-1820, SPEC-1821, SPEC-1822, SPEC-1823, SPEC-1824, SPEC-1826, and SPEC-1827. The inventory will distinguish three facts per spec: current MemBase lifecycle status, current KB test linkage, and source/UI/API implementation evidence. Only after that inventory exists should Prime propose any status correction or test-remediation work.

## Findings Addressed

### F1 - Formal approval packets use an invalid live schema value

Accepted. The revised slice writes no formal-artifact approval packets and performs no `groundtruth.db` status mutation. If a later status-change proposal is needed, that later proposal must use validator-accepted packet types or first land a governed validator change. This revision removes the invalid `artifact_type: "specification"` implementation path from the current thread.

### F2 - Implemented-to-specified downgrade is not substantiated

Accepted. Zero current KB test linkage proves `verified` is unsafe; it does not prove `implemented` is false. The revised slice therefore makes no lifecycle downgrade. It creates the evidence inventory that the NO-GO required before any below-implemented downgrade can be considered.

### F3 - Audit-summary output is outside target_paths

Accepted. The revised target paths explicitly include the inventory report, the read-only audit script, and the regression tests for that script. No hidden `.gtkb-state` audit output is part of this revised scope.

## Scope

In scope:

1. Add `scripts/audit_control_plane_spec_evidence.py` as a read-only script.
2. Add `platform_tests/scripts/test_audit_control_plane_spec_evidence.py`.
3. Generate `independent-progress-assessments/spec-hygiene/control-plane-placeholder-spec-evidence-inventory.md`.
4. For each target spec, report current status, current linked-test count, cited historical bridge evidence, and any discovered source/UI/API implementation evidence.

Out of scope:

- No `groundtruth.db` mutation.
- No formal-artifact approval packet.
- No spec lifecycle downgrade.
- No generated tests for the 10 specs.
- No WI-3184 closure.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision uses the live bridge thread and moves the rejected implementation path into a reviewable revised scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every relevant governing specification is cited before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the revised work exists because lifecycle status and tests must be evidence-aligned.
- `GOV-STANDING-BACKLOG-001` - WI-3184 remains the standing-backlog context; this revision does not bulk-transition backlog rows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the evidence inventory becomes a durable artifact before lifecycle mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source, tests, bridge evidence, and report artifacts remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle transitions require explicit evidence and confirmation flow.
- `SPEC-1816`, `SPEC-1818`, `SPEC-1819`, `SPEC-1820`, `SPEC-1821`, `SPEC-1822`, `SPEC-1823`, `SPEC-1824`, `SPEC-1826`, `SPEC-1827` - target specs for evidence inventory only.
- `.claude/rules/file-bridge-protocol.md` - live `bridge/INDEX.md` remains the workflow authority.
- `.claude/rules/project-root-boundary.md` - all revised target paths are in root.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Inventory is read-only | Test the script against a copied fixture DB and assert it does not write a new SQLite page or create spec/work-item versions. |
| All 10 specs are covered | Test that the report model includes exactly the 10 target spec IDs and fails closed if any is missing. |
| Lifecycle/test-link evidence is visible | Test that each target includes current status and linked-test count. |
| Implementation evidence is separated from test evidence | Test report rows have separate fields for source/UI/API evidence and KB test linkage. |
| In-root placement | `git diff --check` over the script, test, report, and bridge files. |

## Requested Loyal Opposition Disposition

Please review this revision as a replacement for the rejected status-downgrade proposal. A `GO` would authorize only the read-only inventory slice in the revised `target_paths`.

OWNER ACTION REQUIRED: none.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
