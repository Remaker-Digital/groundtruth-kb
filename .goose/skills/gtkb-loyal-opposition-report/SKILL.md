---
name: gtkb-loyal-opposition-report
description: "Generate a Loyal Opposition report with required evidence structure. Files as an Advisory Proposal bridge entry or Deliberation Archive record."
argument-hint: "<report-slug>"
allowed-tools: Bash, Read, Write
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: groundtruth-kb
  category: loyal-opposition
  governance: report-depth-prime-builder-context
---
<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->

# Loyal Opposition Report Generator

Generate a Loyal Opposition report following the mandatory report quality standard.

**Arguments:** `$ARGUMENTS` = kebab-case slug for the report filename.

## Report Structure (Required)

Every report MUST include for each significant finding:

### 1. Observation
What was observed, with concrete detail.

### 2. Deficiency Rationale
Why the observation indicates a deficiency, risk, or control gap.

### 3. Proposed Solution/Enhancement
Specific remediation action with scope and minimal-risk implementation path.

### 4. Option Rationale
Why the proposed option was selected over alternatives.

## Prime Builder Implementation Context (Default)

Include for most reports:
- Objective and intended outcome
- Preconditions and constraints
- Exact evidence paths and line references
- Expected file touchpoints for implementation
- Ordered implementation sequence
- Verification/test steps
- Rollback or containment notes
- Open decisions required from owner

## Advisory Report Mode

When the report is an advisory rather than a bridge verdict, classify the
recommendation as `adopt`, `adapt`, `reject`, `defer`, or `monitor`. For
`adopt` or `adapt`, include a `Required Prime Builder Owner-Grilling Gate`
section before any implementation proposal exists. That section must name the
owner questions Prime Builder must resolve, practical options, tradeoffs, and
the durable artifact outcome expected from the decision.

## Output

`independent-progress-assessments/` is retired (contents deleted by owner
directive); do not write there. File the report as one of:

- An **Advisory Proposal** bridge entry (ADVISORY status; see
  `gtkb-bridge-advisory-status-001`, VERIFIED) when the report may create
  future Prime Builder work.
- A **Deliberation Archive** record (`gt deliberations record`) for
  process/review findings with no derived-work implication.

## Severity Levels

- **P0**: Blocks production or creates immediate security risk
- **P1**: Significant quality/governance gap requiring near-term fix
- **P2**: Important improvement that should be planned
- **P3**: Nice-to-have or future consideration

## Skills applied disclosure (report-only)

When completing this report, append a machine-parseable self-disclosure line listing skills you invoked during authoring. Use the shared emitter in `scripts/skill_disclosure.py`:

- Call `format_skills_applied([...])` or author the equivalent line using the same canonical format.
- Canonical format: `Skills applied: <comma-separated skill names>`; use `Skills applied: (none)` when none apply.
- Report-only: this line is advisory input for future `gt skills check` (WI-4810); it does not gate publishing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
