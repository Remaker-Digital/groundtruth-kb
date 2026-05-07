# Operating-Model Terminology Reconciliation Table — Slice 0 §3.2 Deliverable

**Status:** Slice 0 deliverable per `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` REVISED-1 (-003) GO at -004.

**Authority:** none (this file is informational input to the Slice 0 inventory; not cited by any rule, hook, test, or canonical governance artifact).

**Baseline:** the **owner verbatim text** at `docs/operating-model-DRAFT-2026-04-30.md` §A is canonical for Slice 0; Codex's revision text at §B is annotated proposed clarifications, NOT canonical (per the GO'd Slice 0 framing).

**Format:** 15 terms × 5 columns. Each term is a `### §` section with five labeled fields:
- **Canonical meaning** — concise definition derived from §A (owner verbatim) with §B (Codex revision) as supplement.
- **Allowed synonyms** — alternative terms that mean the same thing in current artifacts.
- **Forbidden uses** — meanings the term has had historically that should be avoided going forward.
- **Current conflicting artifacts** — concrete file paths or "(spot-check found no conflicts)".
- **Remediation action** — `replace` / `clarify` / `preserve as historical` / `defer to Slice N` with brief rationale.

The 15 × 5 = 75 cells satisfy the §Specification-Derived Verification criterion in REVISED-1 (-003).

---

### §1. application

- **Canonical meaning:** the lifecycle object managed by GT-KB. Implementation work is performed *for* an application, by Prime Builder + Loyal Opposition + the owner, mediated by GT-KB. In the current GT-KB development context, GT-KB is both the platform and the active application; for Agent Red Customer Experience adoption, Agent Red is the application and GT-KB is the platform.
- **Allowed synonyms:** "the active application", "the hosted application" (when referring to the application in its deployed/running state).
- **Forbidden uses:** "application" used for the entire `E:\GT-KB` repository when the meaning is platform-level (use "platform" instead); "application" used as synonym for "project" (a project is scoped *work* within an application; not the whole application).
- **Current conflicting artifacts:** `CLAUDE.md` "Project Identity" section frames Agent Red as "Project Name" rather than "Application Name"; many `bridge/` files use "GT-KB project" loosely; `memory/work_list.md` mixes application-scope and project-scope work.
- **Remediation action:** **defer to Slice 1** (this terminology choice is `OM-DELTA-0003` in `docs/operating-model-DRAFT-2026-04-30.md` §C; medium-risk delta requiring owner review before any canonical artifact adopts it).

### §2. project

- **Canonical meaning:** scoped implementation work inside the active application or GT-KB platform — a subsystem, feature area, remediation effort, governance improvement, or cross-cutting change. Projects contain work items; projects are not the application itself. Per owner verbatim §A: "Projects are a response to the introduction of new requirement specifications or changes to existing related specifications."
- **Allowed synonyms:** "workstream" (occasional), "program" (used for multi-slice initiatives like `GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION`).
- **Forbidden uses:** "project" used to mean the entire GT-KB repository (that is the platform context); "project" used as synonym for "application".
- **Current conflicting artifacts:** `CLAUDE.md` "Project Identity" frames whole-repo as project; many bridge file metadata lines use `target_project: gt-kb-platform` mixing project and platform; `memory/work_list.md` rows like `GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION` use project term as program.
- **Remediation action:** **defer to Slice 1** (paired with §1 application; both clarified together in canonical operating-model artifact).

### §3. work item

- **Canonical meaning:** the unit of selectable work in the backlog. Per owner verbatim §A: "work items, which are usually within projects, from the backlog... some work items are stand-alone, high priority or urgent work items." Work items have priority, dependencies, and required context; they are the granularity at which Prime Builder + owner agree on definition and relative priority during project formulation.
- **Allowed synonyms:** "WI", "WI-NNNN" (the canonical KB ID prefix), "task" (occasional, loose).
- **Forbidden uses:** "work item" conflated with "issue" or "ticket" (those are external-system terms); "work item" used for bridge proposal or implementation report (those are governance artifacts, not units of work).
- **Current conflicting artifacts:** spot-check found no major drift between MemBase `work_item` records and `memory/work_list.md` row semantics; minor: row 21 of `memory/work_list.md` uses "GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS" as one row encompassing 5 logical work items (clarification needed for whether umbrella rows are themselves work items).
- **Remediation action:** **clarify** (preserve canonical meaning; clarify that umbrella rows in `memory/work_list.md` are organizational containers, with each contained logical work item still subject to standard bridge protocol).

### §4. backlog

- **Canonical meaning:** the ordered set of active and candidate work organized by priority. Per owner verbatim §A: "The backlog is a roughly chronological stack of highest-to-lowest priority engineering work." Reordering is interactive and triggered by substantial application changes. The canonical implementation is `memory/work_list.md` per `GOV-STANDING-BACKLOG-001` (`DELIB-0838`).
- **Allowed synonyms:** "work_list" (per `memory/work_list.md`), "the work list", "standing backlog".
- **Forbidden uses:** "backlog" as synonym for "ignore list" or "deprecated"; "backlog" referring to a non-`memory/work_list.md` source as the canonical priority list.
- **Current conflicting artifacts:** several historical bridge files refer to "backlog" generically without citing `memory/work_list.md`; some MemBase work_item records use a `priority` field that is not synchronized with `memory/work_list.md` ordering.
- **Remediation action:** **clarify** (`memory/work_list.md` is THE canonical backlog per `GOV-STANDING-BACKLOG-001`; `DELIB-0838` is the originating decision; MemBase priority fields are advisory, not canonical).

### §5. specification

- **Canonical meaning:** an owner-articulated record of what the system must do, recorded in MemBase as one of the spec subtypes (`SPEC-NNNN` functional/non-functional, `GOV-NNN` governance, `DCL-NNN` design constraint, `ADR-NNN` architecture decision, `PB-NNN` protected behavior, `REQ-NNN` requirement). Specifications constrain implementation and verification. Per owner verbatim §A: "Requirement specifications, both functional and non-functional, are recorded in the MemBase append-only database."
- **Allowed synonyms:** "spec", "SPEC-NNNN", "GOV-NNN", "DCL-NNN", "ADR-NNN", "PB-NNN", "REQ-NNN" (each is a spec subtype).
- **Forbidden uses:** "specification" used for technical-design documents or implementation proposals (those are pre-implementation artifacts, not specs); "specification" used for tests (tests *derive from* specs, but are not specs themselves).
- **Current conflicting artifacts:** some bridge files (e.g., older platform-spec-coverage threads) use "specification" loosely for design proposals; MemBase has a clear distinction via the `type` column.
- **Remediation action:** **clarify** (specification = MemBase record with one of the canonical type values; design documents are documentation; implementation proposals are bridge artifacts).

### §6. requirement

- **Canonical meaning:** an owner-stated capability or behavior the system must provide. Per owner verbatim §A: "the formalization of new requirements specifications is performed via a mechanically enforced dialog with the owner in the interactive session." Requirements become formal specifications through the approval gate; before approval they are candidate requirements.
- **Allowed synonyms:** "FR" (functional requirement), "NFR" (non-functional requirement), "candidate requirement" (pre-approval state).
- **Forbidden uses:** "requirement" used loosely for "preference" or "wish" (the owner can express preferences without invoking requirement-formalization); "requirement" implied without explicit owner statement (Prime Builder must not silently promote inferred behaviors to requirements per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`).
- **Current conflicting artifacts:** `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` Slices B/C/D address chat-derived candidate-vs-formal requirement distinction; some intake records pre-DELIB-0874 conflated requirements and preferences.
- **Remediation action:** **clarify** (requirement = formal spec via approval gate; preference = owner observation; candidate requirement = pre-approval intermediate state per chat-derived-spec-approval workflow).

### §7. implementation proposal

- **Canonical meaning:** a Prime Builder document conveyed to Loyal Opposition through the file bridge for pre-implementation review. Per owner verbatim §A: "Prime Builder reviews and investigates the implementation options for meeting the project's requirements and creates a detailed implementation proposal." Per `.claude/rules/file-bridge-protocol.md`, every proposal must cite governing specifications and identify tests/verification procedures.
- **Allowed synonyms:** "bridge proposal", "proposal" (in bridge context), "NEW" (the bridge file status when first filed).
- **Forbidden uses:** "implementation proposal" used to mean a specification (proposal cites specs but is not a spec); "implementation proposal" used for an implementation report (the pre-impl document, not the post-impl report).
- **Current conflicting artifacts:** spot-check found no major conflicts; bridge protocol consistently uses "implementation proposal" / "post-implementation report" distinction.
- **Remediation action:** **preserve as historical** (canonical meaning is well-established; no remediation needed).

### §8. implementation report

- **Canonical meaning:** a Prime Builder document conveyed to Loyal Opposition through the file bridge for post-implementation verification. Per owner verbatim §A: "the Prime Builder ... creates an Implementation Report which is conveyed to the Loyal Opposition agent for verification." Per `DCL-VERIFIED-BRIDGE-HISTORY-001`, the report must carry forward specification links, describe implemented changes, identify executed tests, and report observed results.
- **Allowed synonyms:** "post-impl", "post-implementation report", "post-impl report".
- **Forbidden uses:** "implementation report" confused with "implementation proposal" (proposal is pre-impl; report is post-impl); "implementation report" used to claim VERIFIED before LO records that verdict (per `OM-DELTA-0018`: VERIFIED is dated evidence, not a Prime claim).
- **Current conflicting artifacts:** spot-check found no major conflicts.
- **Remediation action:** **preserve as historical**.

### §9. verification

- **Canonical meaning:** Loyal Opposition's evaluation of an implementation report against the linked specifications, resulting in VERIFIED or NO-GO. Per owner verbatim §A: "the cycle continues until the Loyal Opposition is satisfied and records the final Implementation Report as VERIFIED." Per `OM-DELTA-0018` (Codex revision-delta inventory): VERIFIED is dated evidence that the implementation has been verified, not a mere assertion that a specification exists.
- **Allowed synonyms:** "VERIFIED" (the bridge status), "VERIFIED-terminal" (when a thread reaches terminal closure).
- **Forbidden uses:** "verification" used to mean "test pass" alone (tests passing is necessary but not sufficient; verification is LO's judgment incorporating test execution evidence and spec coverage); "VERIFIED" claimed by Prime without LO recording the verdict.
- **Current conflicting artifacts:** historical phantom-VERIFIED entries in bridge INDEX (e.g., `gtkb-membase-effective-use-umbrella` claimed VERIFIED at -014 but only -001 existed on disk per `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`); the `gtkb-platform-spec-coverage-verified-runner` thread implements the mechanical verification gate that detects such phantoms.
- **Remediation action:** **clarify** (VERIFIED = LO judgment + dated evidence + executed-test record; phantom VERIFIED entries should be flagged by the verified-runner per its assertions; defer schema-level enforcement to Slice 2).

### §10. release

- **Canonical meaning:** a tagged, deployable build of the GT-KB platform or hosted application, accompanied by a release manifest enumerating constituent component versions per `GOV-RELEASE-MANIFEST-README-001` (approved S323 candidate; not yet canonical). Per owner verbatim §A: "GT-KB is distributed as an installable bundle which may be used to create fresh installs or to upgrade existing GT-KB installs to the latest release."
- **Allowed synonyms:** "version", "build", "tag" (specifically: a version-tagged build).
- **Forbidden uses:** "release" used for incremental development commits (release implies tagged + manifest); "release" used for staging-only deployments (those are deployments, not releases).
- **Current conflicting artifacts:** release process is described differently across `groundtruth-kb/templates/`, `bridge/` files, and `docs/` files; the candidate spec `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001` (S323-approved, not yet canonical) attempts to formalize the release model.
- **Remediation action:** **defer to Slice 2** (schema and lifecycle alignment slice; release semantics depend on the candidate-spec `GOV-RELEASE-*` follow-on impl bridges per work_list row 21).

### §11. MemBase

- **Canonical meaning:** the authoritative append-only/versioned knowledge database for governed records — specifications, tests, work items, procedures, documents, environment configuration, and other governed artifact types. Implemented as `groundtruth.db` (SQLite). Per owner verbatim §A: "Requirement specifications, both functional and non-functional, are recorded in the MemBase append-only database."
- **Allowed synonyms:** "Knowledge Database", "KB", "groundtruth.db" (file-level), "knowledge_db" (Python module/class).
- **Forbidden uses:** "MemBase" used for ChromaDB or other derived semantic indexes (those are retrieval aids, not authoritative stores per `OM-DELTA-0022`); "MemBase" used for `memory/MEMORY.md` (session-state file, not canonical knowledge); "MemBase" used for general-purpose storage outside the governed-records scope.
- **Current conflicting artifacts:** `CLAUDE.md` "Knowledge Database Access" section uses both "Knowledge Database" and "KB"; `.claude/rules/bridge-essential.md` does not use "MemBase" term; `memory/MEMORY.md` is sometimes confused with MemBase (it is session state, not authoritative records).
- **Remediation action:** **clarify** (MemBase = authoritative `groundtruth.db`; ChromaDB = derived semantic index; `memory/MEMORY.md` = session state; introduce a single canonical name and use it consistently in canonical operating-model artifact).

### §12. Deliberation Archive

- **Canonical meaning:** the structured record of decisions, deliberations, advisory reports, owner conversations, Prime Builder insights, Loyal Opposition insights, and rationale crossing the capture threshold from brainstorming into requirements/decisions/plans/risks/procedures/review-findings/accepted-future-work (per `OM-DELTA-0020` referencing `DELIB-0874`). Implemented as the `deliberations` table in `groundtruth.db` with semantic indexing in ChromaDB.
- **Allowed synonyms:** "DA", "deliberation_archive" (the table), "DELIB-NNNN" (individual archive records).
- **Forbidden uses:** "Deliberation Archive" used for general session transcripts (transcript harvest is a feeder; the DA is the structured archive); "DA" used for `memory/MEMORY.md`.
- **Current conflicting artifacts:** spot-check found rule files use "DA" / "Deliberation Archive" consistently; `.claude/rules/deliberation-protocol.md` is the active discipline.
- **Remediation action:** **preserve as historical** (canonical meaning well-established; clarify only that DA records are governed by `GOV-ARTIFACT-APPROVAL-001` for formal mutations).

### §13. dashboard

- **Canonical meaning:** the GT-KB graphical surface providing centralized owner visibility into platform and application state — current configuration, operating state, bridge queue, release blockers, requirements/test status, implementation evidence, inventory, historical release data, and KPIs. Per owner verbatim §A: "GroundTruth-KB includes a graphical dashboard with an underlying database that provides the owner with centralized access to information about the state of the project."
- **Allowed synonyms:** "Grafana dashboard" (current implementation), "project dashboard", "GT-KB dashboard".
- **Forbidden uses:** "dashboard" used for static documentation or README-style views (dashboard implies live data + interactive); "dashboard" used to claim implemented capabilities that are only intended (per `OM-DELTA-0030`: claims must distinguish implemented from intended surfaces).
- **Current conflicting artifacts:** `docs/gtkb-dashboard/` contains both implemented and intended-surface artifacts; `bridge/gtkb-dashboard-002` thread shows current vs. target state; some MEMORY.md / CLAUDE.md text overstates dashboard completeness.
- **Remediation action:** **defer to Slice 4** (docs/dashboard/CLI alignment slice should reconcile current-vs-target claims and label intended surfaces explicitly).

### §14. platform

- **Canonical meaning:** GT-KB itself; the lifecycle infrastructure that manages applications, containing rules, hooks, scripts, templates, governance specs, bridge protocol, MemBase + DA, dashboard, and CLI surfaces. Per Codex revision §B P2: "an application is the lifecycle object managed by GT-KB."
- **Allowed synonyms:** "GT-KB", "GroundTruth-KB", "GT-KB platform", "framework" (occasionally; broader than platform).
- **Forbidden uses:** "platform" used for hosted applications (platform manages applications, is not one); "platform" used for individual modules within GT-KB (those are platform components, not the platform itself).
- **Current conflicting artifacts:** `CLAUDE.md` uses "GT-KB" extensively, sometimes ambiguously between platform and application; `memory/work_list.md` rows mix platform-scope and application-scope work; `bridge/` metadata fields like `target_project: gt-kb-platform` use platform-as-project.
- **Remediation action:** **defer to Slice 1** (platform/application/project terminology decision is `OM-DELTA-0003`; cluster of related deltas requires consolidated owner review).

### §15. hosted application

- **Canonical meaning:** an application deployed and running in service, distinct from its application's GT-KB lifecycle record. The application's GT-KB-managed lifecycle (specs, tests, deliberations, work items) exists whether or not the application is hosted; "hosted application" specifically refers to the deployed-running state. Per owner verbatim §A: "applications which experience outages or defects while in service" implies the hosted/in-service context.
- **Allowed synonyms:** "deployed application", "running application", "production application", "in-service application".
- **Forbidden uses:** "hosted application" used for an application during pre-deployment development (during development, it is the application but not yet hosted); "hosted application" used as synonym for "application" (the distinction matters for incident-response capability invocation).
- **Current conflicting artifacts:** the term is rarely used in current artifacts (Codex introduced it via `OM-DELTA-0003`); some adopter docs in `groundtruth-kb/templates/` use "deployed app" or "running app" inconsistently.
- **Remediation action:** **defer to Slice 1** (terminology decision; clustered with §1 application and §14 platform).

---

## Aggregate Observations

- **15 terms × 5 cells = 75 cells filled.** No TBD or empty cells in any cell expected to contain content.
- **Remediation distribution:**
  - `defer to Slice 1`: 4 terms (`application`, `project`, `platform`, `hosted application`) — all clustered around `OM-DELTA-0003` terminology choice.
  - `defer to Slice 2`: 1 term (`release`) — depends on candidate-spec `GOV-RELEASE-*` follow-on impl bridges.
  - `defer to Slice 4`: 1 term (`dashboard`) — depends on docs/dashboard/CLI alignment slice.
  - `clarify`: 6 terms (`work item`, `backlog`, `specification`, `requirement`, `verification`, `MemBase`) — straightforward clarifications in canonical operating-model artifact.
  - `preserve as historical`: 3 terms (`implementation proposal`, `implementation report`, `Deliberation Archive`) — canonical meaning well-established; no remediation needed.
- **Cluster finding:** the 4 `defer to Slice 1` terms (`application`, `project`, `platform`, `hosted application`) are not independent decisions; they form a single terminology cluster with `OM-DELTA-0003` as the underlying delta. Slice 1 should treat them as one decision package.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
