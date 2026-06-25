---
name: loyal-opposition-report
description: "Generate a Loyal Opposition report with required evidence structure. Writes timestamped INSIGHTS file to CODEX-INSIGHT-DROPBOX."
argument-hint: "<report-slug>"
allowed-tools: Bash, Read, Write
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: loyal-opposition
  governance: report-depth-prime-builder-context
---

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

## Output

Generate timestamped file:
```
independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-{YYYY}-{MM}-{DD}-{HH}-{mm}-{SLUG}.md
```

Update `independent-progress-assessments/loyal-opposition-log.md` if any Open items are affected.

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
