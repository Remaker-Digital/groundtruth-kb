# OPERATING MODEL — DRAFT (NOT CANONICAL)

**Status:** DRAFT.

**Authority:** none. This file is NOT cited by any rule, hook, test, or canonical governance artifact. It exists only as a tracked draft to inform the `GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION` program (Slice 0 deliverable §3.1 per `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` REVISED-1 GO at `-004`).

**Promotion path:** an owner-approved Slice 1 proposal designates a canonical operating-model artifact and authority level (potentially at `.claude/rules/operating-model.md` or a managed-template path). At promotion time, this draft is either elevated, modified, or retired based on the Slice 0 inventory findings and any owner direction given in the Slice 1 deliberation.

**Slice 0 status (2026-04-30 S324):**
- §A below contains the owner's verbatim operating-model text. This is the canonical Slice 0 baseline; drift findings in the Slice 0 inventory measure against §A.
- §B below contains Codex Loyal Opposition's revised text from `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPERATING-MODEL-ALIGNMENT-REMEDIATION-ADVISORY-2026-04-30.md` §"Revised Operating-Model Text". §B is **annotated proposed clarifications**, NOT canonical.
- §C below contains the start of the §3.5 owner-vs-Codex revision-delta annotations (one initial NARROW delta spot-checked at proposal time; full delta inventory is a Slice 0 deliverable in progress).

---

## §A. Owner verbatim text (canonical Slice 0 baseline)

Captured from S324 owner conversation (2026-04-30). Verbatim quote; no edits.

> "Application development progresses when the user and the Prime Builder agent select work items, which are usually within projects, from the backlog. The backlog is a roughly chronological stack of highest-to-lowest priority engineering work. Projects often contain multiple distinct work items which have interdependencies and whose implementation requires specific knowledge in context, which affects their place in the order. Some projects and their respective work items are interleaved with other projects which are progressing in parallel, and some work items are stand-alone, high priority or urgent work items. Reordering of the backlog is interactive and typically happens when the application has changed substantially and prior work items and their respective priorities need reassessment before the next batch of prioritized work begins. Projects are a response to the introduction of new requirement specifications or changes to existing related specifications. The identification of requirements in user chat is guided by the Prime Builder agent, and the formalization of new requirements specifications is performed via a mechanically enforced dialog with the owner in the interactive session. Formulation of new projects is interactive with the owner, beginning with establishment of a core set of related requirements for that project. Once the requirements specifications which articulate the objective of the project have been identified or created, the owner and the Prime Builder agent agree on the definition and relative priority of work items within the scope of that project. In some cases, work items are dependent on completion of work items logically within other projects, leading to interleaving of projects in the backlog. Prime Builder reviews and investigates the implementation options for meeting the project's requirements and creates a detailed implementation proposal. The implementation proposal is conveyed to the Loyal Opposition agent for review. The Loyal Opposition agent investigates, evaluates and critiques the Implementation Proposal and questions the cited requirements to disambiguate the owner's intent in order to substantiate requests for changes and corrections. The Loyal Opposition agent responds to the Prime Builder agent with the annotated Implementation Proposal, either affirming that it is ready to implement (GO) or requires another revision and resubmission (NO-GO). When the Prime Builder receives a GO to implement a proposal, it proceeds as specified, first by creating tests which will show that the implementation meets the specification, then by implementing the specified work, and finally creates an Implementation Report which is conveyed to the Loyal Opposition agent for verification. If Prime Builder receives a NO-GO, it makes changes and re-submits to Loyal Opposition. The loyal opposition investigates the Implementation Report conveyed by the Prime Builder, evaluates the tests which were created, and provides the Prime Builder with a report detailing errors or omissions in the tests and the implementation, if any. When Prime Builder receives a response to an Implementation Report, it addresses the issues in the report and re-submits an updated Implementation Report to the Loyal Opposition and the cycle continues until the Loyal Opposition is satisfied and records the final Implementation Report as VERIFIED. Topical chat exchanges between Prime Builder and the owner, Implementation Reports and Proposals, advisory reports, Prime Builder insights, and Loyal Opposition insights are recorded in the Deliberation Archive. The Deliberation Archive is used to disambiguate owner expectations and requirement specification wording, phrasing and intent. Requirement specifications, both functional and non-functional, are recorded in the MemBase append-only database. MemBase also contains details of the tests which are used to confirm that the implementation of each specification is correct and has not inadvertently been changed because of ongoing development work. The system is strongly biased toward artifact creation and maintenance, implementation modularity, and extensive version control over interfaces and objects. The progress of application implementation is tracked using comprehensive system contents inventory records, which include version information, test results, reports on requirements specifications, references to implementation reports and originating deliberations. The system provides commands which may be entered by the owner during interactive sessions which disambiguate owner decisions and directives. The system also provides a Command Line Interface which allows the owner to manage aspects of the GroundTruth-KB system, including assignment of Loyal Opposition and Prime Builder roles, configuration management, health checks and operating state reports. The system includes automations which integrate with external 3rd party services which provide testing, publication and deployment capabilities. GroundTruth-KB includes a graphical dashboard with an underlying database that provides the owner with centralized access to information about the state of the project, including display of current configuration, operating state, the status of 3rd party services, computed project KPI, reports and interactive access to MemBase, test results, and GT-KB inventory, including directory structure and contents, artifact version numbers, and details of historical releases. GT-KB includes capabilities which assist the user in executing application lifecycle operations, such as deployment, upgrades, and testing/ GT-KB also includes capabilities which harvest information about the environment and state of the application, such as log files, reports and test results, for use during remediation, root cause diagnosis, triage and correction of applications which experience outages or defects while in service. GT-KB is distributed as an installable bundle which may be used to create fresh installs or to upgrade existing GT-KB installs to the latest release. Upgrafing GT-KB does not force existing applications to make changes in order to continue operating in service."

This text is also captured in the bridge audit trail at `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` §10.

DA archival as `DELIB-S324-OPERATING-MODEL-OWNER-VERBATIM` is pending session-wrap or earlier follow-on bridge requirement.

---

## §B. Codex proposed revision (annotated; NOT canonical)

Captured from `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPERATING-MODEL-ALIGNMENT-REMEDIATION-ADVISORY-2026-04-30.md` §"Revised Operating-Model Text". Verbatim quote; no edits.

> GT-KB (GroundTruth-KB) is an Internal Developer Platform for AI-assisted software development. It exists to reduce the owner's routine role to specifications, clarifications, and decisions, while the platform and AI agents preserve durable artifacts, create tests, implement approved work, verify outcomes, and maintain release-readiness evidence.
>
> In GT-KB terminology, an **application** is the lifecycle object managed by GT-KB. A **project** is scoped implementation work inside the active application or GT-KB platform, such as a subsystem, feature area, remediation effort, governance improvement, or cross-cutting change. A project is not the hosted application itself. In the current work, GT-KB is both the platform and the active application, but the same application/project distinction applies.
>
> Application development progresses through backlog selection. The backlog is an ordered set of active and candidate work, shaped by priority, dependencies, readiness, owner decisions, and current system state. Chronology is preserved in the audit trail, but backlog order is not merely chronological. Projects often contain multiple work items whose dependencies and required context affect execution order. Work items from different projects may be interleaved when dependencies, urgency, or readiness require it. Reordering is interactive and typically occurs when substantial implementation progress, new requirements, defects, or changed owner priorities make the previous ordering stale.
>
> Projects normally arise from new requirements, changed requirements, defects, governance needs, architectural decisions, operational findings, or discovered drift. Project formulation is interactive with the owner. It begins by identifying the related requirements and decisions that define the objective. The owner and Prime Builder then identify work items within that scope and place them in the backlog according to priority, dependency, and readiness.
>
> Requirement identification in owner chat is assisted by Prime Builder and by GT-KB's artifact-oriented governance. Candidate requirements must not silently become formal requirements. Formal specification creation or update requires an owner-visible confirmation path and the applicable approval evidence. Functional requirements, non-functional requirements, architecture decisions, design constraints, protected behaviors, and governance rules are specification surfaces when they constrain implementation or verification.
>
> Prime Builder investigates implementation options for approved or selected work and prepares an implementation proposal. The proposal must cite the governing specifications, decisions, constraints, and prior deliberations that shape the work. It must also identify the tests or verification procedures that will show whether the implementation satisfies those specifications.
>
> The implementation proposal is conveyed to Loyal Opposition through the file bridge. Loyal Opposition investigates, critiques, and evaluates the proposal. It checks specification linkage, ambiguity, omitted constraints, test adequacy, operational risk, and consistency with owner intent. Loyal Opposition does not change owner intent. It identifies ambiguity or defects and requests clarification, correction, or revision when needed.
>
> Loyal Opposition responds with a numbered bridge verdict. `GO` means the proposal is ready for Prime Builder implementation within the approved scope. `NO-GO` means the proposal requires revision before implementation. If Prime Builder receives `NO-GO`, it revises and resubmits. If Prime Builder receives `GO`, it proceeds according to the approved proposal.
>
> Implementation begins with test or verification creation where the approved proposal requires it. Tests must be derived from the linked specifications and must be capable of showing whether the implementation satisfies the requirements. Prime Builder then implements the work and files an implementation report through the bridge. The report must carry forward the specification links, describe the implemented changes, identify the tests run, and report observed results.
>
> Loyal Opposition reviews the implementation report, inspects the relevant code, tests, artifacts, and evidence, and responds with findings. If errors, omissions, inadequate tests, or implementation gaps remain, Loyal Opposition issues `NO-GO` and Prime Builder corrects and resubmits. The cycle continues until Loyal Opposition can record `VERIFIED`. `VERIFIED` is the dated evidence that the implementation has been verified; it is not a mere assertion that a specification exists or has been claimed.
>
> Topical owner exchanges, implementation proposals, implementation reports, advisory reports, Prime Builder insights, Loyal Opposition insights, decisions, trade-offs, and rationale should be preserved in the Deliberation Archive when they cross the capture threshold from brainstorming into requirements, decisions, plans, risks, procedures, review findings, or accepted future work. The Deliberation Archive is used to disambiguate owner expectations, specification wording, phrasing, and intent.
>
> MemBase is the authoritative append-only/versioned knowledge database for governed records such as specifications, tests, work items, procedures, documents, environment configuration, test coverage, and backlog snapshots. Derived semantic indexes may assist retrieval, but they are not authoritative stores. MemBase records must distinguish current state from historical versions and must avoid fields that encode misleading lifecycle concepts.
>
> GT-KB is strongly biased toward durable artifacts, traceability, modular implementation, versioned interfaces, automated checks, and release evidence. It should maintain inventories and reports that connect requirements, deliberations, work items, implementation reports, tests, configuration, artifact versions, releases, and operating state. Where current implementation does not yet provide that coverage, artifacts should state the gap plainly rather than implying the capability is complete.
>
> The owner may enter interactive commands that clarify decisions, directives, active workspace, role assignment, project focus, or operating state. GT-KB also provides CLI surfaces for platform lifecycle operations such as project initialization, upgrade, health checks, configuration inspection, role-support surfaces, and operating-state reports.
>
> GT-KB may integrate with third-party services for testing, publication, deployment, observability, and release evidence. Those integrations should be governed as platform capabilities with explicit configuration, health checks, evidence capture, and failure modes.
>
> GT-KB includes dashboard and reporting surfaces that should give the owner centralized visibility into the state of the active application and platform: current configuration, operating state, bridge queue, release blockers, requirements and test status, implementation evidence, inventory, historical release data, and relevant KPIs. Claims about dashboard capabilities must distinguish implemented surfaces from intended surfaces.
>
> GT-KB should assist with application lifecycle operations such as testing, deployment, upgrades, rollback, release readiness, remediation, root-cause diagnosis, and triage. It should harvest relevant environment and application state, such as logs, reports, test results, release evidence, and operational artifacts, when doing so improves diagnosis or reduces owner burden.
>
> GT-KB is distributed as an installable and upgradeable platform bundle. It should support fresh installs and upgrades of existing GT-KB installations. Upgrading GT-KB should preserve application lifecycle independence: an upgrade to the platform should not force the active application to change merely to continue operating, except where the owner explicitly accepts a migration, compatibility break, or governed remediation.

---

## §C. Owner-vs-Codex revision-delta annotations (Slice 0 §3.5 deliverable)

Complete delta inventory comparing §A (owner verbatim) against §B (Codex revision). 37 deltas identified across 5 types: 10 ADD, 13 EXPAND, 4 REMOVE, 2 REPHRASE, 8 NARROW. Aggregate observation: Codex's revision encodes existing GT-KB governance conventions (`GOV-ARTIFACT-APPROVAL-001`, `DCL-VERIFIED-BRIDGE-HISTORY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, current-vs-target-state discipline) that are not in the owner's prose. Most are reasonable refinements but several are substantive interpretive additions or narrowings that should be owner-reviewed before any Slice 1+ proposal designates a canonical operating-model artifact.

### Highest-risk deltas (NARROW + REMOVE)

#### `OM-DELTA-0001` — NARROW (Loyal Opposition authority over requirements)

- **owner_text** (§A): "The Loyal Opposition agent investigates, evaluates and critiques the Implementation Proposal **and questions the cited requirements to disambiguate the owner's intent in order to substantiate requests for changes and corrections**."
- **codex_text** (§B P7): "Loyal Opposition does not change owner intent. It identifies ambiguity or defects and requests clarification, correction, or revision when needed."
- **delta:** Codex drops owner-stated authority for LO to "question the cited requirements to disambiguate the owner's intent" and replaces it with the narrower "LO does not change owner intent." Owner grants LO active-investigation authority over requirements; Codex restricts LO to reactive defect-flagging.
- **owner_action_recommended:** revisit-in-slice-1.
- **risk_if_accepted_silently:** would restrict LO from challenging requirement framings in subsequent reviews even when ambiguous or internally inconsistent.

#### `OM-DELTA-0004` — NARROW (backlog chronology)

- **owner_text** (§A): "The backlog is a roughly chronological stack of highest-to-lowest priority engineering work."
- **codex_text** (§B P3): "The backlog is an ordered set... shaped by priority, dependencies, readiness, owner decisions, and current system state. Chronology is preserved in the audit trail, but backlog order is not merely chronological."
- **delta:** Owner's text treats chronology as primary structure with priority as modifier ("roughly chronological stack"); Codex's revision treats chronology as audit-trail metadata only and emphasizes order is "not merely chronological."
- **owner_action_recommended:** revisit-in-slice-1.
- **risk_if_accepted_silently:** would shift backlog-ordering behavior away from owner-stated chronological-with-priority semantics; existing artifacts that assume rough chronological order may diverge silently.

#### `OM-DELTA-0006` — REMOVE (stand-alone urgent work items)

- **owner_text** (§A): "...some work items are stand-alone, high priority or urgent work items."
- **codex_text** (§B P3): (no equivalent — concept dropped).
- **delta:** Owner explicitly recognizes a class of stand-alone urgent work items separate from project-grouped work. Codex's revision implicitly assumes all work items are within projects.
- **owner_action_recommended:** accept-with-modification (restore the stand-alone urgent class explicitly in any canonical artifact).
- **risk_if_accepted_silently:** stand-alone urgent items might be forced into synthetic projects, adding governance overhead to fast-path work.

#### `OM-DELTA-0007` — NARROW (reordering triggers)

- **owner_text** (§A): "Reordering of the backlog is interactive and typically happens when the application has changed substantially and prior work items and their respective priorities need reassessment."
- **codex_text** (§B P3): "Reordering is interactive and typically occurs when substantial implementation progress, new requirements, defects, or changed owner priorities make the previous ordering stale."
- **delta:** Codex enumerates specific triggers; owner just says "the application has changed substantially." Enumeration may exclude triggers the owner had in mind (e.g., environment changes, third-party integration changes).
- **owner_action_recommended:** accept-with-modification (preserve owner's broader "application has changed substantially" framing alongside Codex's enumerated examples).
- **risk_if_accepted_silently:** reordering might be denied for triggers outside Codex's enumeration.

#### `OM-DELTA-0031` — REMOVE (3rd party service status in dashboard)

- **owner_text** (§A): "...display of current configuration, operating state, the status of 3rd party services, computed project KPI..."
- **codex_text** (§B P17): "...current configuration, operating state, bridge queue, release blockers, requirements and test status..."
- **delta:** Owner explicitly lists "the status of 3rd party services" as a dashboard surface. Codex omits.
- **owner_action_recommended:** accept (likely just streamlining; restore in canonical artifact if 3rd-party-service status remains a dashboard requirement).
- **risk_if_accepted_silently:** dashboard implementation might deprioritize 3rd-party-service status surface.

#### `OM-DELTA-0032` — REMOVE (interactive MemBase access in dashboard)

- **owner_text** (§A): "...interactive access to MemBase, test results, and GT-KB inventory..."
- **codex_text** (§B P17): "...requirements and test status, implementation evidence, inventory, historical release data, and relevant KPIs."
- **delta:** Owner explicitly lists "interactive access to MemBase" as a dashboard capability. Codex omits the interactive framing.
- **owner_action_recommended:** revisit-in-slice-1 (interactive MemBase access vs. read-only is a substantive capability question).
- **risk_if_accepted_silently:** dashboard might be implemented as read-only views without interactive MemBase write paths the owner intended.

#### `OM-DELTA-0035` — REMOVE (outage/defect framing for harvest)

- **owner_text** (§A): "...for use during remediation, root cause diagnosis, triage and correction of applications which experience outages or defects while in service."
- **codex_text** (§B P18): "...when doing so improves diagnosis or reduces owner burden."
- **delta:** Codex removes the specific in-service outage/defect framing and replaces with general "improves diagnosis or reduces owner burden."
- **owner_action_recommended:** accept-with-modification (preserve owner's explicit in-service-outage framing in canonical artifact; harvest is specifically an in-service-incident capability per owner intent).
- **risk_if_accepted_silently:** harvest capability might be invoked outside the in-service-incident context the owner specified, creating unnecessary load.

### ADD deltas (Codex introduced content not in owner text)

| ID | Codex addition (§B paragraph) | Risk class | Owner action |
|---|---|---|---|
| `OM-DELTA-0002` | Opening framing: "GT-KB is an Internal Developer Platform for AI-assisted software development. It exists to reduce the owner's routine role to specifications, clarifications, and decisions" (§B P1) | Low (helpful summary) | accept-with-modification (verify alignment with owner intent for "reduce owner's routine role" framing) |
| `OM-DELTA-0003` | Application/project terminology distinction with examples (§B P2) | Medium (terminology choice ripples across artifacts) | revisit-in-slice-1 |
| `OM-DELTA-0010` | "Candidate requirements must not silently become formal requirements" (§B P5) | Low (consistent with `GOV-ARTIFACT-APPROVAL-001`) | accept |
| `OM-DELTA-0012` | "approval evidence" requirement for spec creation (§B P5) | Low (encodes `GOV-ARTIFACT-APPROVAL-001`) | accept |
| `OM-DELTA-0013` | Implementation-proposal content requirements: cite governing specs/decisions/constraints/prior deliberations + identify tests (§B P6) | Low (encodes existing bridge gates) | accept |
| `OM-DELTA-0014` | LO review checklist: spec linkage, ambiguity, omitted constraints, test adequacy, operational risk, consistency with owner intent (§B P7) | Low (encodes bridge protocol) | accept |
| `OM-DELTA-0016` | "Tests must be derived from the linked specifications" (§B P9) | Low (encodes `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) | accept |
| `OM-DELTA-0017` | Implementation-report content requirements: carry forward spec links, describe changes, identify tests run, report results (§B P9) | Low (encodes `DCL-VERIFIED-BRIDGE-HISTORY-001`) | accept |
| `OM-DELTA-0018` | "VERIFIED is the dated evidence... not a mere assertion that a specification exists or has been claimed" (§B P10) | Low (response to phantom-VERIFIED incidents; consistent with owner intent) | accept |
| `OM-DELTA-0023` | "MemBase records must distinguish current state from historical versions and must avoid fields that encode misleading lifecycle concepts" (§B P12) | Low (encodes existing schema-discipline concerns) | accept |
| `OM-DELTA-0025` | Current-vs-target-state discipline: "artifacts should state the gap plainly rather than implying the capability is complete" (§B P13) | Low (substantive governance addition; aligns with `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) | accept |
| `OM-DELTA-0030` | "Claims about dashboard capabilities must distinguish implemented surfaces from intended surfaces" (§B P17) | Low (consistent with delta 0025) | accept |

### EXPAND deltas (Codex broadened stated capability/actor scope)

| ID | Owner text (§A) | Codex expansion (§B) | Owner action |
|---|---|---|---|
| `OM-DELTA-0005` | backlog "highest-to-lowest priority engineering work" | adds "active and candidate" + "owner decisions, and current system state" (§B P3) | accept |
| `OM-DELTA-0008` | projects respond to "new requirement specifications or changes" | adds "defects, governance needs, architectural decisions, operational findings, or discovered drift" (§B P4) | accept |
| `OM-DELTA-0009` | project formulation begins with "core set of related requirements" | adds "and decisions" as project-defining input (§B P4) | accept |
| `OM-DELTA-0011` | "functional and non-functional" specifications | adds "architecture decisions, design constraints, protected behaviors, and governance rules" as specification surfaces (§B P5) | accept (matches existing GT-KB types) |
| `OM-DELTA-0015` | "annotated Implementation Proposal, either affirming that it is ready to implement (GO) or requires another revision and resubmission (NO-GO)" | adds "numbered bridge verdict" framing and "within the approved scope" qualifier (§B P8) | accept |
| `OM-DELTA-0019` | LO "evaluates the tests which were created" | broadens to "inspects the relevant code, tests, artifacts, and evidence" (§B P10) | accept |
| `OM-DELTA-0020` | DA captures "chat exchanges, Implementation Reports and Proposals, advisory reports, Prime Builder insights, and Loyal Opposition insights" | adds "decisions, trade-offs, and rationale" + "capture threshold" concept from `DELIB-0874` (§B P11) | accept |
| `OM-DELTA-0021` | MemBase contains "requirement specifications" + "tests" | adds "work items, procedures, documents, environment configuration, test coverage, and backlog snapshots" (§B P12) | accept (matches existing GT-KB usage) |
| `OM-DELTA-0024` | bias toward "artifact creation and maintenance, implementation modularity, and extensive version control" | adds "traceability, versioned interfaces, automated checks, and release evidence" (§B P13) | accept |
| `OM-DELTA-0026` | owner commands disambiguate "decisions and directives" | adds "active workspace, role assignment, project focus, or operating state" (§B P14) | accept |
| `OM-DELTA-0027` | CLI surfaces include "assignment of Loyal Opposition and Prime Builder roles, configuration management, health checks and operating state reports" | adds "project initialization, upgrade, configuration inspection, role-support surfaces" (§B P14) | accept |
| `OM-DELTA-0028` | integrations cover "testing, publication and deployment" | adds "observability, and release evidence" + governance discipline ("explicit configuration, health checks, evidence capture, and failure modes") (§B P16) | accept |
| `OM-DELTA-0029` | dashboard scope: "current configuration, operating state, the status of 3rd party services, computed project KPI..." | adds "bridge queue" and "release blockers" (§B P17) | accept |
| `OM-DELTA-0033` | lifecycle ops: "deployment, upgrades, and testing" | adds "rollback, release readiness, remediation, root-cause diagnosis, and triage" (§B P18) | accept (matches in-service capability owner mentions later) |
| `OM-DELTA-0034` | harvest: "log files, reports and test results" | adds "release evidence, and operational artifacts" (§B P18) | accept |
| `OM-DELTA-0036` | upgrade-independence: "does not force existing applications to make changes in order to continue operating" | adds owner-controlled exception clause ("except where the owner explicitly accepts a migration, compatibility break, or governed remediation") (§B P19) | accept (preserves owner-controlled escape valve) |

### REPHRASE deltas (same content, different words)

| ID | Owner phrasing | Codex phrasing | Risk |
|---|---|---|---|
| `OM-DELTA-0022` | "Requirement specifications, both functional and non-functional, are recorded in the MemBase append-only database" | Adds "Derived semantic indexes may assist retrieval, but they are not authoritative stores" (§B P12) — clarification, treated as REPHRASE because it disambiguates the same concept | None |
| `OM-DELTA-0037` | "to the latest release" | "of existing GT-KB installations" (§B P19) | None |

### Summary

- **High-risk deltas requiring owner review:** 4 (OM-DELTA-0001, 0004, 0007, 0032).
- **Medium-risk deltas requiring owner review:** 1 (OM-DELTA-0003 — application/project terminology choice).
- **Low-risk deltas (Codex encodes existing GT-KB governance):** 32.

Slice 1+ scope decision (per the GO'd proposal §3.4 thresholds) should consider that the owner-vs-Codex revision is more interpretive than purely refactoring: ~14% of deltas (5 of 37) are substantive enough that the canonical artifact decision should not silently adopt Codex's framing. The other ~86% are reasonable encodings of existing governance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
