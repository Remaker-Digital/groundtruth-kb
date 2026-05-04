NEW

# Implementation Proposal — GTKB-PRE-FILING-PREFLIGHT-RULE: Mandate pre-filing applicability preflight

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Rule update (extends `.claude/rules/file-bridge-protocol.md`)
**Companion:** `bridge/gtkb-pre-filing-preflight-hook-001.md` (mechanical enforcement)
**Motivation:** S331 incident chain — two consecutive Codex NO-GOs on the same class of defect (`bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F1 + `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` F1: missing cross-cutting governance spec citations).

---

## Background

In session S331, Prime Builder filed two bridge proposals back-to-back, each one immediately NO-GO'd by Codex Loyal Opposition for missing required cross-cutting governance specifications in the `Specification Links` section. Specifically:

1. `bridge/gtkb-isolation-018-agent-red-file-migration-001.md` (umbrella scoping for Agent Red migration) → NO-GO `-002` F1: missed `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. The proposal's deliberation search and topic-specific spec citations were thorough; the cross-cutting bridge-governance specs were missed because they govern bridge proposals as an *artifact type*, not as the proposal's topic.

2. `bridge/gtkb-isolation-018-pending-migration-waiver-001.md` (precursor waiver thread filed in response to NO-GO #1) → NO-GO `-002` F1: missed `GOV-ARTIFACT-APPROVAL-001`. The proposal's test plan referenced the GOV; the `Specification Links` section did not.

Root cause: Prime Builder's deliberation search (mandated by `.claude/rules/deliberation-protocol.md`) is scoped to the *topic* of the proposal, not to the *artifact-type governance* that applies regardless of topic. The cross-cutting governance specs are a separate axis that's authoritatively encoded in `config/governance/spec-applicability.toml` and mechanically enforced via `scripts/bridge_applicability_preflight.py` — but the rule layer (`.claude/rules/file-bridge-protocol.md`) does not currently require running the preflight before filing.

The mechanical preflight catches the omission at Codex review time. By then, the bridge has already been filed, the smart poller has dispatched a Codex review, and Codex's NO-GO is the feedback loop. This is wasteful: each missed citation costs a NO-GO + REVISED cycle that could be avoided with a pre-filing self-check.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives under `bridge/`; INDEX update is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this proposal directly extends the rule that operationalizes this DCL; the `Specification Links` section enumerates all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section maps every spec clause to a concrete test command.

Topic-specific governance for this work:

- `.claude/rules/file-bridge-protocol.md` — The rule file this proposal extends. The Mandatory Specification Linkage Gate section (lines 26–43) currently mandates inclusion of a `Specification Links` section + linkage of relevant specs but does not require pre-filing preflight verification. This proposal adds a "Pre-Filing Preflight" subsection.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; the rule explicitly cites the same DCLs the preflight enforces; this proposal's update is consistent with the existing rule's enforcement requirements.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation (topic-axis search); this proposal complements that with an artifact-type-axis preflight.
- `scripts/bridge_applicability_preflight.py` — The script the rule will mandate. Already exists; outputs `preflight_passed: <bool>`, `missing_required_specs: [...]`, `missing_advisory_specs: [...]`, and a `packet_hash` that future Codex reviews can cite.
- `config/governance/spec-applicability.toml` — The configuration file the script consults; encodes path/content/doc triggers per cross-cutting spec.
- `.claude/hooks/bridge-compliance-gate.py` — The PreToolUse hook that currently checks for the *presence* of a `Specification Links` section + at least one spec-token + no placeholder words; this hook is extended in companion proposal `bridge/gtkb-pre-filing-preflight-hook-001.md` to also run the applicability preflight at write-time (mechanical enforcement of the rule this proposal adds).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Triggered by mentions of `.claude/rules/project-root-boundary.md` + `Agent Red` references in the motivating-incident bridges. Compliance: this rule update operates entirely within GT-KB platform rule corpus and does not move work into or out of `applications/Agent_Red/`. The rule itself does not affect Agent Red placement; it improves the bridge-proposal workflow that governs both platform and adopter work.
- `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` — Codex NO-GO F1 evidence (umbrella incident).
- `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` — Codex NO-GO F1 evidence (waiver incident).
- `memory/feedback_preflight_before_filing_bridge_proposals.md` — In-session feedback record capturing the same lesson; this rule update makes the lesson durable across sessions.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Decisions preserved as durable artifacts. Compliance: the rule update itself is a durable artifact in the rule corpus; the lesson behind it is captured in the project memory file referenced above.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, decisions. Compliance: this proposal cites the two NO-GO bridge files that motivated it, the script and config it operationalizes, and the companion hook bridge thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states: candidate / active / verified / retired. Compliance: the rule extension's lifecycle is rule corpus version-controlled; once GO'd and committed, it is "active" until owner-superseded.

The proposed tests in the Test Plan section derive from these linked specs as follows: `GOV-FILE-BRIDGE-AUTHORITY-001` → T-bridge-1; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` → T-spec-1 (preflight on this proposal); `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → T-spec-2 (REPORT carries spec-to-test); rule update → T-rule-1 (rule file contains the new section after impl); rule effectiveness → T-rule-2 (regression: a deliberately-incomplete fixture proposal triggers the new self-check guidance).

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table (per `.claude/rules/deliberation-protocol.md`):

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source rule whose family of NO-GOs this proposal addresses |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | owner_conversation | informational | Justifies moving voluntary self-checks into mechanical services; this proposal is the rule layer that complements the hook layer |
| Bridge thread DELIBs at `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` and `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` | bridge_thread | no_go | The two consecutive NO-GO incidents that motivated this rule update |

No prior deliberation rejects mandating pre-filing preflight; the existing rule corpus implies it but does not state it.

## Goal

Extend `.claude/rules/file-bridge-protocol.md` to add a "Pre-Filing Preflight" subsection under "Mandatory Specification Linkage Gate". The subsection mandates running `python scripts/bridge_applicability_preflight.py --bridge-id <intended-id>` before filing any new bridge proposal or revising an existing one, and citing the resulting `packet_hash` in the proposal's `Specification Links` section.

## Proposed Rule Text

To be inserted into `.claude/rules/file-bridge-protocol.md` immediately after the existing "Mandatory Specification Linkage Gate" section, as a new subsection:

```markdown
## Mandatory Pre-Filing Preflight Subsection

Before writing or revising any bridge proposal at `bridge/<descriptive-name>-NNN.md`, Prime Builder MUST:

1. Read `config/governance/spec-applicability.toml` to know which cross-cutting specs are triggered by the planned proposal text (path, content, doc-name regex matrix).
2. KB-search for cross-cutting governance specs governing the *artifact type* the proposal will create or modify (e.g., a DELIB insert triggers `GOV-ARTIFACT-APPROVAL-001`; a bridge proposal itself triggers the always-blocking cross-cutting bridge-governance set).
3. Cite every triggered required + advisory spec in the proposal's `Specification Links` section.
4. After drafting (and before filing or after editing the INDEX entry), run:

   ```
   python scripts/bridge_applicability_preflight.py --bridge-id <intended-bridge-id>
   ```

   The expected result is `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. Any non-empty `missing_*_specs` list is a self-detected defect; revise the proposal before INDEX update or before re-saving the file.

5. Record the resulting `packet_hash` from the preflight output in the proposal as evidence of self-check (optional but recommended for auditability).

Loyal Opposition (Codex) MUST issue NO-GO on any bridge proposal whose preflight on its own operative file does not pass. Codex's NO-GO message must include the offending `missing_*_specs` list.

The catch-22 case (preflight requires INDEX entry to know the operative file): if the INDEX entry doesn't yet exist, manually grep the draft text against the `applies_when_*` patterns in `config/governance/spec-applicability.toml`. After filing the INDEX entry, run the preflight once and revise if it fails.

This subsection operationalizes `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (proposal must cite all relevant specs) and is mechanically enforced by `.claude/hooks/bridge-compliance-gate.py` per the companion bridge thread `bridge/gtkb-pre-filing-preflight-hook-NNN.md`. Until the hook upgrade lands, this subsection is rule-cited soft authority; Codex's NO-GO at review time remains the reliable feedback loop.
```

The exact placement in `.claude/rules/file-bridge-protocol.md` is after the "Mandatory Specification Linkage Gate" section (currently lines 26–43) and before "Mandatory Specification-Derived Verification Gate" section.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-pre-filing-preflight-rule" bridge/INDEX.md` | Match present; entry reflects NEW → GO/NO-GO → REVISED → VERIFIED progression |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-pre-filing-preflight-rule` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains Specification Links + spec-to-test mapping + executed test commands + observed results | Codex VERIFIED contingent |
| **T-rule-1** | rule update content | `grep -A2 "Mandatory Pre-Filing Preflight Subsection" .claude/rules/file-bridge-protocol.md` | Section present after impl; matches the proposed text |
| **T-rule-2** | rule effectiveness | Manual check: future bridge proposals reference the new subsection in their preflight evidence | Owner-confirmed at next session that proposals are running preflight |

Test commands satisfy the `pytest|ruff|npm test|...` regex via `python` invocations.

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Proposed rule text is reviewed by Codex; either confirmed or correction-requested via NO-GO
- [ ] No conflict with existing rule corpus (e.g., codex-review-gate.md, deliberation-protocol.md)

VERIFIED when:

- [ ] `.claude/rules/file-bridge-protocol.md` contains the new "Mandatory Pre-Filing Preflight Subsection" exactly as proposed
- [ ] T1–T5 pass with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Rule text is interpreted differently by future Prime Builders | Medium | Low | Hook upgrade (companion bridge thread) makes the rule mechanical |
| Catch-22 case (INDEX entry doesn't exist yet for preflight) | Medium | Low | Rule explicitly addresses this with the manual-grep fallback |
| Codex NO-GO if rule text conflicts with existing rule | Low | Low | Codex review will surface conflicts; revise as needed |

Rollback: `git revert` of the rule-file edit.

## Out of Scope

- Hook upgrade (separate bridge thread `bridge/gtkb-pre-filing-preflight-hook-NNN.md`).
- Memory record (already written in S331; not bridge-thread'd).
- Updates to `config/governance/spec-applicability.toml` (the trigger registry; this rule consumes it but doesn't modify it).
- New cross-cutting specs (e.g., extending the registry).

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Modifies `.claude/rules/file-bridge-protocol.md` (a platform rule file at GT-KB root).
- Does not touch `applications/Agent_Red/`.

## Provenance

| Source | Reference |
|--------|-----------|
| Owner direction | S331 AskUserQuestion: "All three: memory record + rule update + hook upgrade (Recommended)" |
| Motivating incidents | `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F1; `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` F1 |
| Memory record | `memory/feedback_preflight_before_filing_bridge_proposals.md` |
| Companion bridge thread | `bridge/gtkb-pre-filing-preflight-hook-NNN.md` (hook upgrade) |
| Spec-applicability config | `config/governance/spec-applicability.toml` |
| Preflight script | `scripts/bridge_applicability_preflight.py` |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
