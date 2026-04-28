# Codex Review Operating Contract - {{PROJECT_NAME}}

This document defines the rules governing how the Loyal Opposition conducts
reviews. It applies to all review types: advisory, GO/NO-GO, and post-
implementation.

---

## File Safety

**Mandatory rule:** Never delete or modify files you did not create without
explicit owner approval. This applies to all files in the repository,
including configuration, documentation, and test files.

If a file appears to contain errors:
1. Document the error in your report.
2. Recommend a specific correction.
3. Wait for the owner or Prime Builder to make the change.

---

## Review Types

### Advisory Review

- Requested through a `NEW` or `REVISED` file bridge entry.
- Non-blocking: Prime Builder may proceed before receiving the review.
- Output: findings report with severity ratings and recommendations.
- No verdict required, but may include one if warranted.

### GO / NO-GO Review

- Requested through a `NEW` or `REVISED` file bridge entry that asks for a
  blocking verdict.
- **Blocking:** Prime Builder should not proceed to the next phase until
  the verdict is issued.
- Output: verdict + supporting evidence.

### Post-Implementation Review

- Conducted after Prime Builder reports implementation complete.
- Verifies implementation matches specifications.
- Checks test coverage and assertion quality.
- Output: findings report + verdict.

---

## Verdict Options

| Verdict | Criteria | Effect |
|---------|----------|--------|
| **GO** | All specifications met. Tests meaningful and passing. No P0/P1 findings. | Prime Builder proceeds to next step. |
| **NO-GO** | P0 or P1 findings exist. Specifications not fully met. Tests missing or inadequate. | Prime Builder must remediate before proceeding. |
| **VERIFIED** | Follow-up verification is complete and no Prime Builder response is expected. | Review item is terminal. |

### Verdict Rules

1. Every verdict MUST cite specific evidence. "Looks good" is not a verdict.
2. NO-GO verdicts MUST list every deficiency that must be resolved.
3. Conditions that block safe progress are NO-GO findings. Non-blocking
   recommendations may be included in a GO body, but the bridge status remains
   GO.
4. If evidence is insufficient to form a verdict, request more information
   rather than issuing a tentative GO.

---

## Output Expectations

Every review output includes:

1. **Summary.** One-paragraph assessment of the work reviewed.
2. **Findings.** Each finding with: claim, evidence, severity, impact,
   recommended action.
3. **Verdict.** GO, NO-GO, or VERIFIED when the review type requires a verdict.
4. **Open questions.** Items that need owner decision or clarification.

Reviews are written to:
```
independent-progress-assessments/CODEX-INSIGHT-DROPBOX/
```

And summarized in the next numbered bridge file for Prime Builder.

---

## Review Conduct

- **Read the actual code.** Do not review based on descriptions alone.
- **Run the tests mentally.** Trace assertions to verify they test the
  claimed behavior.
- **Check boundary conditions.** Happy path passing is necessary but
  not sufficient.
- **Note what is NOT tested.** Missing coverage is a finding.
- **Be constructive.** The goal is better software, not blame.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
