NO-GO

# Loyal Opposition Review - Requirements Collection Hook Implementation Proposal

**Document:** `gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04`
**Reviewed file:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-04
**Verdict:** NO-GO

## Claim

The implementation direction is plausible and the mechanical applicability preflight passes, but the proposal is not ready for GO because its formal specification linkage is inaccurate against live MemBase. The proposal cites a non-existent governing specification for chat-derived spec approval, omits the live governing transparency spec that the requirements-hook GOV itself names, and describes creating an IPR record that already exists.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

The mechanical preflight is a floor, not a ceiling. It does not resolve the live MemBase defects below.

## Evidence Reviewed

- `bridge/INDEX.md` live latest status: `NEW` for this document.
- Proposal: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-001.md`.
- File bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Project root boundary rule: `.claude/rules/project-root-boundary.md`.
- Live MemBase reads from `groundtruth.db`.
- Deliberation search:
  - `python -m groundtruth_kb deliberations search "requirements collection hook DELIB-S330 DELIB-S331 DELIB-S332" --limit 10 --json`

## Prior Deliberations

Relevant prior records found:

- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` is cited by current memory as the source for the requirements-collection hook governance work.
- `DELIB-S331-AUQ-1/2/3` and `DELIB-S332-CONTINUE-WITH-SUBSLICE-E` are cited by the proposal as authorization for the umbrella and continuation.

No prior NO-GO was found for this exact Sub-slice E proposal.

## Findings

### F1 - Blocking - Specification Links cite a non-existent spec and omit the live governing transparency spec

**Evidence:** The proposal lists `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` as a blocking specification at line 27 and maps it to indirect output-rendering coverage at line 140. A live MemBase query against `groundtruth.db` returned `NOT FOUND` for `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

The same live query confirms `GOV-SPEC-CAPTURE-TRANSPARENCY-001` exists as a `specified` governance record. The live `GOV-REQUIREMENTS-COLLECTION-HOOK-001` text explicitly references `GOV-SPEC-CAPTURE-TRANSPARENCY-001` in its `REQUIREMENT_CANDIDATE PATH` Step 1 and in the `decision` / `chat` classification handling. The proposal does not include `GOV-SPEC-CAPTURE-TRANSPARENCY-001` in `Specification Links` or in the spec-to-test mapping.

**Risk / impact:** The proposal's formal linkage is not reviewable as written. If Prime implements against `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, the implementation may target a phantom or obsolete requirement while missing the actual owner-visible positive/negative capture-event transparency rule. That violates `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate and `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.

**Required action:** Revise the proposal to remove or justify the nonexistent `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` reference. Add `GOV-SPEC-CAPTURE-TRANSPARENCY-001` to `Specification Links` and provide a concrete test mapping for the owner-visible positive and negative capture-event behavior it requires, or document a specific waiver if Prime believes it is not applicable.

### F2 - Blocking - IPR creation plan contradicts live MemBase state

**Evidence:** The proposal says Step 3 will "Create `IPR-REQUIREMENTS-COLLECTION-HOOK-001` in MemBase via the formal-artifact-approval gate" at lines 98-105. Live MemBase already contains document `IPR-REQUIREMENTS-COLLECTION-HOOK-001` version 1 with category `implementation_proposal` and status `proposed`. Current `memory/MEMORY.md` also states that the S330 spawned artifacts already included `IPR-REQUIREMENTS-COLLECTION-HOOK-001` and that it was approved and inserted.

**Risk / impact:** A plan to create an already-existing formal artifact is ambiguous under append-only MemBase governance. Prime might attempt a duplicate insert, silently create an unnecessary version, or misstate post-implementation evidence by treating the IPR as absent. Since formal artifact mutation is governed by `GOV-ARTIFACT-APPROVAL-001`, the bridge proposal must be precise about whether it is creating, updating, linking, or promoting the existing record.

**Required action:** Revise Step 3 and acceptance criteria to reflect the live IPR state. Either link the existing `IPR-REQUIREMENTS-COLLECTION-HOOK-001` as the pre-approved implementation proposal record, or explicitly propose an append-only update/promote action with the required formal-artifact-approval evidence.

## Passing Evidence

- The proposal is root-contained: planned file paths remain under `E:\GT-KB`, and it explicitly excludes `applications/` content.
- The DCL-derived hook implementation tests cover the main binding categories: classifier labels, retrieval sources, escape hatch, output schema, cost, timeout, subprocess smoke, and hook registration.
- The required mechanical applicability preflight passes with `missing_required_specs: []`.

## Required Revision

Submit `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-003.md` that:

1. Corrects the Specification Links and spec-to-test mapping for the live transparency governance spec.
2. Resolves the phantom or obsolete `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` citation.
3. Rewrites the IPR step around the already-existing `IPR-REQUIREMENTS-COLLECTION-HOOK-001` record.
4. Re-runs and includes the applicability preflight output.

## Decision Needed From Owner

None for this NO-GO.
