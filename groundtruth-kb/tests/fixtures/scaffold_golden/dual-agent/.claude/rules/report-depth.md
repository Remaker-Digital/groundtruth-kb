# Report Depth and Prime Builder Context Standard

This rule defines mandatory report quality for Loyal Opposition outputs.
Every report must meet this standard to be actionable.

## Required Depth in Every Report

For each significant finding, include all of the following:

### 1. Observation

What was observed, with concrete detail. Include file paths, line numbers,
or command output. Vague observations are not findings.

### 2. Deficiency Rationale

Why the observation indicates a deficiency, risk, or control gap. Include
threat/impact mechanics where relevant -- not just conclusions, but the
reasoning chain.

### 3. Proposed Solution / Enhancement

Specific remediation action with:
- Scope of the change (which files, which components).
- Minimal-risk implementation path (prefer reversible, incremental changes).
- Expected outcome after remediation.

### 4. Option Rationale

Why the proposed option was selected over alternatives. Note rejected
alternatives and why they were rejected. This prevents revisiting
already-considered approaches.

## Prime Builder Implementation Context

In most reports, include a dedicated section for Prime Builder with:

| Element | Description |
|---------|-------------|
| **Objective** | What the implementation should achieve. |
| **Preconditions** | What must be true before starting. |
| **Evidence paths** | Exact file paths and line references to inspect. |
| **File touchpoints** | Expected files to create or modify. |
| **Implementation sequence** | Ordered steps for the implementation. |
| **Verification steps** | How to confirm the implementation is correct. |
| **Rollback notes** | How to revert if the implementation fails. |
| **Open decisions** | Items requiring owner input before proceeding. |

## Exceptions

- If disclosing full detail would increase sensitive exposure risk, redact
  sensitive values while preserving implementation usefulness.
- If the owner explicitly asks for a summary-only report, comply but still
  include evidence references.

## Quality Bar

- **Evidence-first, inference-second.** Every claim must be grounded in
  something observable.
- **Avoid generic recommendations.** "Improve test coverage" is not
  actionable. "Add assertion for X in test_Y.py line Z" is actionable.
- **Prefer minimal-risk, reversible remediation ordering.** Address the
  safest fixes first; save high-risk changes for last.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
