---
name: gtkb-assertion-triage
description: "Investigate assertion failures against current canonical requirements and actual executable behavior."
argument-hint: "<specification-id>"
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
metadata:
  project: groundtruth-kb
  category: governance
---
# Investigate assertion results

Use the assigned scope and current canonical definition:

```text
gt spec show <specification-id> --json
gt assert --spec <specification-id> --json
```

The assertion command is read-only. Its observations concern the returned source version and structural checks; they do not prove full behavioral qualification or work completion. Read the current requirement and implementation, then run the applicable executable tests. Capture the actual process exit code and inspect what the tests exercise.

Distinguish an implementation defect, an incorrect assertion, missing behavioral coverage, and a requirement that the owner has changed or retired. Repeated failures alone establish none of those conclusions. Do not call a failure harmless, accept it as expected, retire a valid requirement, or weaken a test merely to improve a score. A change of requirement belongs directly in its canonical formal record under the owner's direction.

Correct the affected implementation or test through the assigned work. Reuse existing corrective work where it covers the defect; otherwise use the canonical intake with a linked executable test. Preserve coherent project scope and the actual unresolved obligation. Report unsupported or missing evaluation as UNASSESSED, or PARTIAL alongside evaluated checks.

Use current CLI domain writers for resulting formal or work-item amendments, then read back the current state. Owner decisions are applied directly to authoritative state; their conversational history remains in session logs. Do not produce approval packets, decision files, retained triage snapshots or a second authority store.

Assertion evaluation is an assigned investigation, not an automatic SessionStart corpus scan. There is no requirement to grow assertion-run history to make a failure threshold reachable. Historical run frequency cannot replace current canonical scope, actual behavioral testing or independent review.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
