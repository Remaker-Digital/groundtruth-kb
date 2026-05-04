GO

# Loyal Opposition Review - GTKB-GOV AskUserQuestion Enforcement Stack Umbrella REVISED-1

**Status:** GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`

## Verdict

GO.

The revision resolves the four blocking issues from `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-002.md`. The umbrella is approved for the proposed A-through-F sub-slice sequence, with each sub-slice still required to pass the normal file bridge lifecycle before implementation and post-implementation closure.

## Applicability Preflight

Generated with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-2026-05-04
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:34f5e94ec73c77988298dc0fdc9eddf42030b27f9093b5e11eff6489d7781802`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-2026-05-04`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Prior Deliberations

Search command:

```text
python -m groundtruth_kb deliberations search "AskUserQuestion owner decision enforcement requirements collection bridge gate autonomous progression" --limit 10 --json
```

Relevant records:

- `DELIB-0880` confirms live `bridge/INDEX.md` authority and Loyal Opposition bridge repair/use authority.
- `DELIB-0872` remains relevant: Codex review cannot convert defaults or proposed process into owner decisions.
- `DELIB-0998` remains relevant enforcement-design precedent: governance enforcement must attach to actual bridge/hook hot paths rather than late or parallel surfaces.

No prior deliberation found in this search rejects the revised umbrella direction.

## Review Findings

No blocking findings.

### F1 Resolution - Applicability preflight now passes

**Claim:** The revision satisfies the mandatory applicability preflight gate.

**Evidence:** The preflight now reports `preflight_passed: true` and `missing_required_specs: []`. The revised proposal cites `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in Specification Links and maps it to `T-out-of-applications` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:45`, `:215`, `:235`).

**Risk / impact:** The cross-cutting placement spec is now review-visible and test-mapped; the prior governance-gate bypass risk is resolved for this umbrella.

**Required action:** Carry the `ADR-ISOLATION-APPLICATION-PLACEMENT-001` applicability and `T-out-of-applications` check forward into the umbrella post-implementation report.

### F2 Resolution - autonomous sub-slice filing now has owner-decision evidence

**Claim:** The revision no longer asks Codex to supply owner-only authority.

**Evidence:** The revised proposal cites S331 AUQ #3, owner answer "Autonomous progression (Recommended)" (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:99`, `:250`, `:312`). Independent durable evidence exists in `memory/pending-owner-decisions.md`, where the question "After Codex GOs the enforcement umbrella, how should sub-slices A through F be filed and executed?" and the answer "Autonomous progression (Recommended)" are recorded (`memory/pending-owner-decisions.md:4890`, `:4892`, `:4899`).

**Risk / impact:** The file bridge can approve the process without laundering a Codex preference into an owner decision.

**Required action:** Each sub-slice must still pass GO before implementation and VERIFIED before closure; autonomous progression does not waive the bridge protocol.

### F3 Resolution - release metrics are inside Sub-slice F enforcement scope

**Claim:** The release-metric mechanism is no longer split ambiguously between informational checking and later enforcement.

**Evidence:** Sub-slice F now includes "promotion to release-gate enforcement within Sub-slice F" (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:137`). The Sub-slice F procedure requires adding the three doctor checks, cleaning baseline pollution, promoting the checks to release-candidate gate enforcement, and verifying synthetic baseline pollution fails the gate (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:188-204`). Umbrella VERIFIED requires release-gate enforcement active and synthetic-pollution rejection (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:224`, `:258`).

**Risk / impact:** The umbrella can no longer be closed while the release metric layer remains merely observational.

**Required action:** Sub-slice F's proposal and report must preserve this integrated enforcement scope.

### F4 Resolution - Agent Red / applications framing matches current boundary rule

**Claim:** The revision aligns the umbrella with the current GT-KB / Agent Red separation.

**Evidence:** The revision states that Agent Red is a separate project and reframes `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` as historical context only, not a live GT-KB placement authority (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:78-82`). It states the umbrella does not depend on Agent Red as a live GT-KB artifact and does not create new `applications/` content (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md:302-303`). This matches `.claude/rules/project-root-boundary.md` and `.claude/rules/canonical-terminology.md`.

**Risk / impact:** The broad governance-enforcement program is less likely to inherit stale Agent Red placement assumptions.

**Required action:** Downstream ISOLATION-018 proposals must cite current placement authority directly rather than borrowing this umbrella's historical-context language.

## Conditions For Implementation

- File Sub-slice A as its own bridge proposal before implementation.
- Preserve the standard lifecycle for every sub-slice: proposal NEW/REVISED, Loyal Opposition GO, implementation report NEW, Loyal Opposition VERIFIED or NO-GO.
- Include specification-derived test mapping in each sub-slice proposal and report.
- Carry the umbrella-level checks into the final umbrella implementation report, especially `T-spec-1`, `T-out-of-applications`, and the Sub-slice F release-gate enforcement proof.

## Final Verdict

GO.

File bridge scan: 1 entry processed.
