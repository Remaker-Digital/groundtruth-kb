NO-GO

# Codex Review - GTKB-ISOLATION-018 Agent Red File Migration

**Status:** NO-GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-isolation-018-agent-red-file-migration-001.md`

## Claim

The scoping direction is broadly aligned with the owner-approved topology
decision, but this proposal cannot receive `GO` in its current form because the
mandatory bridge applicability preflight failed and the proposal relies on a
future waiver DELIB before that waiver exists.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-agent-red-file-migration
```

Observed result:

```text
preflight_passed: false
missing_required_specs: ["DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001", "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001", "GOV-FILE-BRIDGE-AUTHORITY-001"]
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

Per `.claude/rules/file-bridge-protocol.md` lines 55-66, `GO` is valid only
when `missing_required_specs: []`. This is therefore a blocking defect.

## Prior Deliberations

I searched the deliberations table for:

- `GTKB-ISOLATION-018`
- `Agent Red file migration`
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`

Relevant result found:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` v1, owner decision:
  source authority for Agent Red nested under `applications/Agent_Red/`.

No deliberation entry was found for
`DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`.

## Findings

### F1 - Missing required cross-cutting specs block GO

Evidence:

- Proposal `bridge/gtkb-isolation-018-agent-red-file-migration-001.md` has a
  `Specification Links` section starting at line 23.
- Mechanical preflight reports the required specs above as missing.
- `.claude/rules/file-bridge-protocol.md` requires a `NO-GO` unless required
  applicability specs are cited and satisfied.

Risk / impact:

The proposal is a large umbrella migration that governs 13 follow-on bridge
threads, repo separation, formal artifact work, and verification. If the
cross-cutting bridge authority and specification-derived-testing requirements
are omitted at this level, later sub-slices can inherit an incomplete
governance surface.

Recommended action:

Revise the proposal to cite and satisfy:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

Also consider citing the advisory specs reported by preflight, or explicitly
explain why they do not apply.

### F2 - The proposal relies on a future waiver as if it were already active

Evidence:

- The proposal states that Agent-Red-related root work operates under a
  documented exception until ISOLATION-018 is verified, but says that exception
  will be formalized in sub-slice 18.B
  (`bridge/gtkb-isolation-018-agent-red-file-migration-001.md` lines 15-19 and
  46).
- The DCL formal approval packet names
  `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` as the exception DELIB, but
  the deliberations table search found no such DELIB.
- The proposal makes 18.B dependent on 18.A `VERIFIED`
  (`bridge/gtkb-isolation-018-agent-red-file-migration-001.md` line 302), so
  the waiver cannot exist before this umbrella proposal proceeds unless the
  sequence is changed.

Risk / impact:

This creates a bootstrap problem: the migration plan needs a waiver to govern
the in-flight root-state violation, but the waiver is deferred until after the
umbrella thread is approved and verified. That leaves the current exception
state asserted but not backed by the owner-approved DELIB required by the DCL's
exception mechanism.

Recommended action:

Revise the sequencing so the pending-migration waiver is created before any
proposal or implementation relies on it, or narrow 18.A so it does not claim an
active waiver. The revised proposal should state the exact blocking state: no
Agent Red root-file implementation work proceeds until the waiver DELIB exists
or the work is otherwise compliant without relying on a waiver.

### F3 - Acceptance criteria require OQ-1 to be decided, but the plan defers it

Evidence:

- The 18.A acceptance criteria include "Repo-history preservation strategy is
  decided by owner" (`bridge/gtkb-isolation-018-agent-red-file-migration-001.md`
  line 280).
- The open questions table defers OQ-1 to the start of sub-slice 18.K
  (`bridge/gtkb-isolation-018-agent-red-file-migration-001.md` line 347).

Risk / impact:

18.A cannot be accepted under its own criteria if a required owner decision is
intentionally delayed until 18.K. This will make verification ambiguous: either
18.A is not complete, or the acceptance criteria are overstated.

Recommended action:

Choose one of two clear paths:

- Decide OQ-1 before 18.A is accepted.
- Revise 18.A acceptance criteria to say OQ-1 may be deferred until 18.K, and
  make 18.K explicitly blocked on that owner decision.

## Positive Evidence

The proposal correctly cites the source topology decision
`DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` and the companion GOV/DCL
formal approval packets. Its destination path
`E:/GT-KB/applications/Agent_Red/` is aligned with
`.claude/rules/project-root-boundary.md` and the owner-approved Agent Red
canonical repository identity.

## Decision

NO-GO.

Revise the proposal to clear the applicability preflight, resolve the waiver
bootstrap problem, and make the 18.A acceptance criteria internally consistent.
