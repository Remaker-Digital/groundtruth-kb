NO-GO

# Loyal Opposition Review - GTKB-GOV AskUserQuestion Enforcement Stack Umbrella

**Status:** NO-GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md`

## Verdict

NO-GO.

The enforcement direction is coherent and appears worth pursuing, but the umbrella cannot receive GO as written. The mechanical applicability preflight fails with a missing required spec, and the proposal asks Codex to approve autonomous sub-slice filing authority without cited owner evidence for that authority.

## Applicability Preflight

Generated with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-2026-05-04
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:1314a86a59bccbc026a0ecfa767aeea38221c812001b68ccb5e0d940c7be1384`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-2026-05-04`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md`
- preflight_passed: `false`
- missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
- missing_advisory_specs: []
```

Relevant table row:

```text
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `no` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
```

## Prior Deliberations

Search command:

```text
python -m groundtruth_kb deliberations search "AskUserQuestion owner decision enforcement requirements collection bridge gate" --limit 10 --json
```

Relevant prior records:

- `DELIB-0880` confirms live `bridge/INDEX.md` authority and Loyal Opposition bridge repair/use authority.
- `DELIB-0872` is relevant precedent that Codex cannot convert defaults or review approval into owner decisions.
- `DELIB-0998` is relevant enforcement-design precedent: governance enforcement must attach to the actual bridge/hook hot path rather than a late or parallel surface.

## Findings

### F1 - Blocking: mandatory applicability preflight fails

**Claim:** The proposal cannot receive GO while the mechanical preflight reports a missing required spec.

**Evidence:**

- `.claude/rules/file-bridge-protocol.md` requires the bridge applicability preflight before GO and says GO is valid only when `missing_required_specs: []`; if required cross-cutting specs are missing, Loyal Opposition must issue NO-GO.
- `.claude/rules/codex-review-gate.md` repeats the same review obligation and requires NO-GO if any required applicable specification is missing.
- The live preflight for this bridge reports `preflight_passed: false` and `missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]`.
- The reviewed proposal discusses `applications/`, Agent Red, and project-root boundary material at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:37`, `:234`, and `:264`, but its Specification Links section does not cite `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

**Risk / impact:** Approving the proposal would bypass the mechanical cross-cutting spec gate and weaken the recent bridge hardening work that exists specifically to prevent incomplete specification linkage.

**Required action:** File a revision that cites `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, explains its applicability or non-applicability to the umbrella, and maps any resulting verification obligations in the spec-to-test mapping.

### F2 - Blocking: the proposal asks Codex to approve owner pre-approval it does not evidence

**Claim:** The acceptance criterion for "Owner pre-approval to file sub-slice bridges autonomously" is not supported by the owner decisions cited in the proposal.

**Evidence:**

- The proposal cites two S331 AskUserQuestion decisions: block ISOLATION-018 / enforcement first, and full 6-mechanism stack scope (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:269-273`).
- The umbrella acceptance criteria separately require "Owner pre-approval to file sub-slice bridges autonomously per work-list contract pattern" (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:215`).
- The "Open Questions" table says all scope decisions are resolved (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:240-248`), but it does not show an owner decision granting autonomous bridge-filing authority.
- `DELIB-0872` is relevant precedent: Codex review cannot ratify owner-only choices or convert proposed defaults into owner decisions.

**Risk / impact:** A GO could be misread as Codex granting owner authority for six follow-on bridge filings. That would blur the owner-decision channel this program is specifically trying to enforce.

**Required action:** Either remove that acceptance criterion and state that each sub-slice may be filed only under the ordinary standing-backlog / owner-priority rules, or obtain and cite an explicit AskUserQuestion owner decision authorizing autonomous filing of the six sub-slice bridge proposals.

### F3 - Blocking: release-metric enforcement is scoped ambiguously outside the umbrella

**Claim:** The proposal's end-state says release metrics are part of the enforcement stack, but the risk table says Sub-slice F's first run is informational-only and gate enforcement is enabled later in a separate metric-promotion step.

**Evidence:**

- The goal includes "release metrics gating" with three doctor checks (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:76`).
- Sub-slice F says the doctor checks are release metrics and that release-gate integration blocks the release-candidate gate (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:165-172`).
- Umbrella VERIFIED requires all three end-state tests PASS and fresh `gt project doctor` release-gate verification (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:216-222`).
- The risk/rollback table then says the first run is informational-only and gate enforcement is enabled in a separate metric-promotion step after the baseline is clean (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:232`).

**Risk / impact:** The umbrella could be marked complete while one of the promised mechanical enforcement mechanisms remains only observational. That contradicts the stated objective of replacing reminders with mechanical enforcement before resuming ISOLATION-018.

**Required action:** Revise Sub-slice F so the metric-promotion/enforcement step is either included in the umbrella's VERIFIED criteria or explicitly split into a named follow-on bridge that the umbrella does not claim to complete.

### F4 - Required revision: Agent Red / applications governance references need the current boundary framing

**Claim:** The proposal cites `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` and frames ISOLATION-018 as "Agent Red migration" context, but the current root-boundary guidance says Agent Red is a separate project and unqualified GT-KB work must not treat Agent Red files as live GT-KB artifacts.

**Evidence:**

- `.claude/rules/project-root-boundary.md` says Agent Red is a separate project, not a GT-KB file set, and no live GT-KB artifact may be created, read as a live dependency, updated, verified, or required from outside `E:\GT-KB`.
- `.claude/rules/canonical-terminology.md` records the 2026-05-04 owner correction that Agent Red is not part of GT-KB.
- The proposal cites `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` because it says the waiver governs ISOLATION-018 work blocked by this umbrella (`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-001.md:37`).

**Risk / impact:** The umbrella is governance work, not a migration slice, so stale Agent Red placement framing may leak into a broad enforcement program and confuse the current GT-KB / Agent Red separation.

**Required action:** In the revision, cite `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and the current project-root boundary rule. Clarify whether `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` is historical context, superseded context, or still an active constraint for the specific blocked ISOLATION-018 work; do not use it as a live GT-KB placement authority unless that status is current and evidenced.

## Accepted Portions

- The six-slice decomposition is directionally reasonable: hook re-enable/regex, rule declaration, bridge gate, durable evidence audit, requirements-collection hook, and release metrics are separable enough for bridge review.
- Sub-slice A correctly absorbs `memory/work_list.md` row 29 rather than leaving duplicate regex-tightening work open.
- The proposal includes an `Owner Decisions / Input` section, which is a useful shape for the proposed Sub-slice C gate.

## Required Conditions For Revision

1. Add and satisfy `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in Specification Links and test mapping, or revise content so the preflight no longer flags it.
2. Resolve the autonomous sub-slice filing authority issue with explicit owner evidence or remove the claim.
3. Make Sub-slice F's enforcement state unambiguous: either enforce within the umbrella or split promotion into a named follow-on that the umbrella does not claim as complete.
4. Update Agent Red / applications framing to match the current project-root boundary and canonical terminology records.

## Final Verdict

NO-GO.

File bridge scan: 1 entry processed.

