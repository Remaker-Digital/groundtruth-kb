# Report Depth and Prime Builder Context Standard

This rule defines mandatory report quality for Loyal Opposition outputs.

## Required Depth in Every Report

For each significant finding, include all of the following:

1. Observation
- What was observed, with concrete detail.

2. Deficiency Rationale
- Why the observation indicates a deficiency, risk, or control gap.
- Include threat/impact mechanics where relevant (not just conclusions).

3. Proposed Solution/Enhancement
- Specific remediation action.
- Scope and minimal-risk implementation path.

4. Option Rationale
- Why the proposed option was selected over alternatives.
- Note rejected alternatives when they were considered.

## Prime Builder Implementation Context (Default)

In most reports, include a dedicated implementation-context section for Prime Builder with:

- Objective and intended outcome
- Preconditions and constraints
- Exact evidence paths and line references
- Expected file touchpoints for implementation
- Ordered implementation sequence
- Verification/test steps
- Rollback or containment notes
- Open decisions required from owner

## Exceptions

- If disclosing full detail would increase sensitive exposure risk, redact sensitive values while preserving implementation usefulness.
- If the owner explicitly asks for a short summary-only report, comply but still include evidence.

## Quality Bar

- Evidence-first, inference-second.
- Avoid generic recommendations; recommendations must be operationally actionable.
- Prefer minimal-risk, reversible remediation ordering.
