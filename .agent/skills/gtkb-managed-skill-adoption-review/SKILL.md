---
name: gtkb-managed-skill-adoption-review
description: Structural review of managed-artifact proposals (skill, template, or adopter). Use when a bridge thread proposes a new or revised managed-artifact so a Prime Builder structural review is required before proposal filing or as part of the bridge review checklist.
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: implementation
  activity-envelope: build, ops
---
<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project antigravity`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Activity Envelope Requirement

This is an **activity-envelope-only** skill. Use it only after the current worker has opened the respective activity-envelope(s) (e.g., 'ops', 'deliberation', or 'build') specified earlier in this document. If a request for this skill arrives outside `::open <activity-envelope>`, do not act on this skill request and inform the user that this skill is only availablewithin the specified activity envelope.


# Managed Skill Adoption Review

## When To Use

- A bridge thread proposes creating or updating a managed skill, managed template,
  or managed adopter artifact.
- A Prime Builder must perform a structural review of a managed-artifact proposal
  before filing the bridge proposal, or a Loyal Opposition reviewer needs a
  structured checklist for the proposal verdict.
- Reviewer must verify that the proposal satisfies managed-artifact registry
  authority, target-path completeness, and avoids stale Tier A registry
  assumptions.

## When Not To Use

- Do not use to review non-managed artifacts (standard skills, templates,
  adopters that are not managed by a central registry).
- Do not substitute for a bridge proposal review verdict; the output of this
  skill is input evidence for the verdict, not the verdict itself.
- Do not use to author the managed artifact; this skill is for review only.

## Required Context

- The managed-artifact proposal bridge file (NEW or REVISED).
- The relevant managed-artifact registry entry (if any exists).
- The `target_paths` declared in the proposal.
- The parent project record and its current `activation-status` field.
- Recent bridge history for the same artifact class to detect stale assumptions.

## Structural Review Checklist

### 1. Registry Authority

- [ ] Is the registry that governs this artifact class clearly identified?
- [ ] Does the proposal cite the registry entry that authorizes (or will
  authorize) the artifact?
- [ ] Is there a competing or duplicate registration?
- [ ] Does the parent project's current `activation-status` permit dispatch of
  this work, without inventing a separate authorization carrier?

### 2. Target-Path Completeness

- [ ] Are all target paths declared in the proposal?
- [ ] Do the target paths include:
  - Canonical source path (for skills: `.harness-baseline-configuration/skills/...`)
  - Generated adapter paths (for skills: `.harness-baseline-configuration/skills/...`, manifest)
  - Registry update paths (capability registry, manifests)
  - Platform test paths
- [ ] Is every target path inside the GT-KB project root?
- [ ] Are there cross-harness parity obligations, and are the adapter paths
  covered?

### 3. Stale-Assumption Detection

- [ ] Does the proposal assume a Tier A registry that may have been deprecated or
  replaced?
- [ ] Does the proposal reference a bridge thread, DELIB, or authorization that
  has been superseded?
- [ ] Does the proposal assume a harness deployment (e.g., Codex, Cursor) that
  may not yet have the artifact class enabled?
- [ ] Does the proposal conflict with a newer owner decision or governing
  specification?

### 4. Specification Linkage

- [ ] Are all required specifications linked?
- [ ] Does the proposal satisfy DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  (concrete spec links)?
- [ ] Are verification commands identified for each linked specification per
  DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001?

### 5. Lifecycle Compliance

- [ ] Is the proposal at the correct bridge stage (NEW for a first proposal,
  REVISED for re-attempts)?
- [ ] Is the status token correct on the first line?
- [ ] Are prior deliberations and owner decisions cited?
- [ ] Is the bridge chain unbroken?

### 6. Artifact Quality

- [ ] Does the skill have a clear purpose statement?
- [ ] Are the When To Use / When Not To Use sections present and non-trivial?
- [ ] Are required inputs and constraints documented?
- [ ] Is the skill body free of placeholder or TODO-only sections?

## Output

Produce a structured review report with:

1. **Registry Authority Assessment**: pass, fail, or needs-owner-decision.
2. **Target-Path Completeness Assessment**: pass with n paths, or a list of
   missing paths.
3. **Stale-Assumption Warnings**: list any detected stale assumptions.
4. **Specification Linkage Gap Report**: list any missing spec links.
5. **Lifecycle Compliance Status**: pass or list of violations.
6. **Overall Recommendation**: `GO` (proposal is structurally sound), `NO-GO`
   (proposal has blocking structural issues), or `OWNER-DECISION-NEEDED` (proposal
   requires owner input before structural review can complete).

The output is advisory evidence for the bridge verdict; it does not replace the
bridge verdict file.

## Artifact Routing

If the structural review detects issues:

- **Registry authority gap**: route to specification intake or an owner-directed
  project `activation-status` update (see `advisory-disposition` skill decision tree).
- **Missing target paths**: require the Prime Builder to amend the proposal with
  complete target paths before re-filing.
- **Stale assumptions**: require the Prime Builder to address each stale
  assumption in a REVISED proposal.
- **Specification linkage gap**: require the Prime Builder to add the missing
  specification link(s).
- **Owner decision needed**: record as a bridge blocker and escalate through the
  AskUserQuestion path if interactive, or document the blocker in the headless
  bridge artifact.

## Adopted From

- WI-4841, motivated by repeated bridge NO-GOs around managed-artifact registry
  authority, target_paths omission, and stale Tier A registry assumptions.
- DELIB-20265883, DELIB-20266596

<!--
GTKB-ANTIGRAVITY-SKILL-ADAPTER-BEGIN
Generated by: scripts/harness_projection/project_harness.py
Generated at: content-addressed 7d7bc19a030d
Canonical source: .harness-baseline-configuration/skills/gtkb-managed-skill-adoption-review/SKILL.md
Canonical source sha256: 7d7bc19a030dac7fb7a20d05485f38bec17c21c4cd2eb5c63aee08dac58050d3
GTKB-ANTIGRAVITY-SKILL-ADAPTER-END
-->
