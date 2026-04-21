# NO-GO: F5 Requirement Intake Pipeline Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The capture-confirm-record shape matches the GroundTruth vision, but the proposal is not ready because its dependencies are incomplete/unresolved and the candidate buffer is intentionally non-persistent even though traceability is the point of the feature.

## Findings

### 1. Blocking: Dependencies are incomplete and unresolved

**Evidence:** F5 declares dependencies on F1 and F2 at bridge/gtkb-spec-pipeline-f5-001.md:7. Stage 3 also depends on F3 for assertion tiering and F4 for constraints at bridge/gtkb-spec-pipeline-f5-001.md:88. F1 remains NO-GO in bridge/gtkb-spec-pipeline-f1-004.md; F2, F3, and F4 are also NO-GO in their bridge review files.

**Risk/impact:** The proposal cannot be implemented as written until the schema, impact report, quality scoring, and constraint lookup contracts are stable.

**Required action:** Add explicit dependencies on F3/F4 or decouple Stage 3 from them for the first implementation phase.

### 2. Blocking: In-memory candidate buffer conflicts with traceability and recovery

**Evidence:** The proposal defines candidate records with raw owner text at bridge/gtkb-spec-pipeline-f5-001.md:31 and says the raw text is ground truth at bridge/gtkb-spec-pipeline-f5-001.md:54. Implementation step 3 makes the candidate buffer in-memory and not persisted at bridge/gtkb-spec-pipeline-f5-001.md:179. The risk table acknowledges session-loss and punts to a session-recovery file at bridge/gtkb-spec-pipeline-f5-001.md:193.

**Risk/impact:** The most important evidence, the owner's exact words and the AI classification, can disappear before confirmation or audit. That weakens the protection against chat misinterpretation.

**Required action:** Persist candidates before confirmation, either as a GT-KB table or as deliberation records with candidate status. If a recovery file is used, include it in the implementation sequence, tests, and cleanup/retention policy.

### 3. Major: GOV-09 hook integration is an open design question

**Evidence:** F5 asks whether to replace or layer on the existing GOV-09 hook at bridge/gtkb-spec-pipeline-f5-001.md:199. Current `templates/hooks/spec-classifier.py` is a mechanical UserPromptSubmit hook with regex patterns at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/spec-classifier.py:30 and emits only a static reminder at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/spec-classifier.py:69.

**Risk/impact:** Two independent classifiers can produce inconsistent guidance: one says "record/verify specs now" while the intake pipeline says "capture candidate and wait for confirmation."

**Required action:** Define whether F5 replaces, wraps, or configures the current spec-classifier hook, and update templates/tests accordingly.

### 4. Major: Target ownership is blurred

**Evidence:** F5 target repo is `groundtruth-kb`, but implementation step 8 creates a `/confirm-requirements` skill for Agent Red at bridge/gtkb-spec-pipeline-f5-001.md:184.

**Risk/impact:** A package feature and a project-specific skill can diverge, leaving GT-KB without a reusable integration point.

**Required action:** Specify the GT-KB-owned artifact first, such as CLI command, hook template, or library API. Agent Red skill wiring should be a downstream adoption step.

## Conditions For GO

1. Resolve/decompose dependencies on F1-F4.
2. Persist candidate records or explicitly document why losing them is acceptable.
3. Define GOV-09 hook interaction.
4. Keep GT-KB implementation separate from Agent Red adoption wiring.

