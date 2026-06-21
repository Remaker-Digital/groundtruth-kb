# GroundTruth-KB Operating Model

**Status:** Canonical (rule-cited soft authority). Active.

**Authority model:** This file is the canonical operating-model artifact for GT-KB. It carries **rule-cited soft authority only**: it is cited by `.claude/rules/loyal-opposition.md` and `AGENTS.md` as the operating-model reference, and its terminology and framing are the alignment baseline for future remediation work. **No hook or test mechanically enforces compliance with this artifact's text.** Hook-enforced compliance (e.g., scanners that gate writes on operating-model violations) is intentionally deferred per the Slice 0 evidence-based recommendation against Slice 5 (recurring hygiene automation) at this stage.

**Source:** Owner verbatim text captured at `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` §10. Five substantive clarifying decisions per S324 AskUserQuestion answers archived as `DELIB-S324-OM-DELTA-{0001,0003,0004,0007,0032}-CHOICE` (`source_type='owner_conversation'`, `outcome='owner_decision'`, `session_id='S324'`). Slice 0 inventory at `independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md`. Slice 1 bridge thread at `bridge/gtkb-operating-model-slice-1-canonical-artifact-2026-04-30-*.md`.

**Promotion path for changes:** any future change to this artifact requires an owner-approved bridge proposal and a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001`.

---

## §1. Operating Model

GT-KB (GroundTruth-KB) is an Internal Developer Platform for AI-assisted software development. It exists to reduce the owner's routine role to specifications, clarifications, and decisions, while the platform and AI agents preserve durable artifacts, create tests, implement approved work, verify outcomes, and maintain release-readiness evidence.

In GT-KB terminology, an **application** is the lifecycle object managed by GT-KB. A **project** is a named grouping of related known work in the backlog; it may group related sub-projects, individual work items, or both. A project is not the hosted application itself. A **sub-project** is a named grouping of related work items inside a project. The **platform** is GT-KB itself; the lifecycle infrastructure that manages applications. A **hosted application** is an application deployed and running in service. In the current work, GT-KB is both the platform and the active application, but the same application/project distinction applies.

Application development progresses through backlog selection. The backlog is the unified view of all known work for an application or platform, including all work items and the project/sub-project groupings that organize those work items. Chronology is preserved in the audit trail, but backlog order is not merely chronological. Projects often contain multiple work items whose dependencies and required context affect execution order. Work items from different projects may be interleaved when dependencies, urgency, or readiness require it. Some work items are stand-alone, high priority, or urgent, and may be selected outside any project. Reordering is interactive and typically occurs when the application has changed substantially - for example, when implementation progress, new requirements, defects, environment changes, third-party integration changes, or changed owner priorities make the previous ordering stale.

Projects normally arise from new requirements, changed requirements, defects, governance needs, architectural decisions, operational findings, or discovered drift. Project formulation is interactive with the owner. It begins by identifying the related requirements and decisions that define the objective. The owner and Prime Builder then identify projects, sub-projects, and work items within that scope and place the known work in the backlog according to priority, dependency, and readiness.

Requirement identification in owner chat is assisted by Prime Builder and by GT-KB's artifact-oriented governance. Candidate requirements must not silently become formal requirements. Formal specification creation or update requires an owner-visible confirmation path and the applicable approval evidence. Functional requirements, non-functional requirements, architecture decisions, design constraints, protected behaviors, and governance rules are specification surfaces when they constrain implementation or verification.

Prime Builder operates with an **interrogative default** for owner factual claims about GT-KB. When the owner states a fact about GT-KB capabilities, implementation, history, or state, Prime Builder verifies the statement against the existing evidence trail (rule files, KB records, git history, runtime artifacts) before treating it as canonical input. Where the statement is incorrect or partial, Prime Builder surfaces the correction with evidence; the corrected statement is then offered to the owner as a candidate specification via the chat-derived spec approval workflow per `GOV-SPEC-CAPTURE-TRANSPARENCY-001`. The interrogative default does NOT apply to claims the agent cannot verify (e.g., owner-stated business facts, customer information, organizational decisions); those are accepted as factual when there is no other source of fact. Source: `DELIB-S324-PB-INTERROGATION-DIRECTIVE` (S324 owner directive).

Prime Builder investigates implementation options for approved or selected work and prepares an implementation proposal. The proposal must cite the governing specifications, decisions, constraints, and prior deliberations that shape the work. It must also identify the tests or verification procedures that will show whether the implementation satisfies those specifications.

The implementation proposal is conveyed to Loyal Opposition through the file bridge. The Loyal Opposition agent investigates, evaluates and critiques the Implementation Proposal and questions the cited requirements to disambiguate the owner's intent in order to substantiate requests for changes and corrections. Loyal Opposition responds with a numbered bridge verdict. `GO` means the proposal is ready for Prime Builder implementation within the approved scope. `NO-GO` means the proposal requires revision before implementation. If Prime Builder receives `NO-GO`, it revises and resubmits. If Prime Builder receives `GO`, it proceeds according to the approved proposal. `DEFERRED` is owner-directed non-actionable parking state with a recorded reason and clear/resume condition; it is not a Loyal Opposition verdict and does not authorize implementation.

Implementation begins with test or verification creation where the approved proposal requires it. Tests must be derived from the linked specifications and must be capable of showing whether the implementation satisfies the requirements. Prime Builder then implements the work and files an implementation report through the bridge. The report must carry forward the specification links, describe the implemented changes, identify the tests run, and report observed results.

Loyal Opposition reviews the implementation report, inspects the relevant code, tests, artifacts, and evidence, and responds with findings. If errors, omissions, inadequate tests, or implementation gaps remain, Loyal Opposition issues `NO-GO` and Prime Builder corrects and resubmits. The cycle continues until Loyal Opposition can record `VERIFIED`. `VERIFIED` is dated evidence that the implementation has been verified against the linked specifications; it is not a mere assertion that a specification exists or has been claimed.

Topical owner exchanges, implementation proposals, implementation reports, advisory reports, Prime Builder insights, Loyal Opposition insights, decisions, trade-offs, and rationale are preserved in the Deliberation Archive when they cross the capture threshold from brainstorming into requirements, decisions, plans, risks, procedures, review findings, or accepted future work. The Deliberation Archive is used to disambiguate owner expectations, specification wording, phrasing, and intent.

MemBase is the authoritative append-only/versioned knowledge database for governed records such as specifications, tests, work items, procedures, documents, environment configuration, test coverage, and backlog snapshots. Derived semantic indexes may assist retrieval, but they are not authoritative stores. MemBase records distinguish current state from historical versions and avoid fields that encode misleading lifecycle concepts.

GT-KB is strongly biased toward durable artifacts, traceability, modular implementation, versioned interfaces, automated checks, and release evidence. It maintains inventories and reports that connect requirements, deliberations, work items, implementation reports, tests, configuration, artifact versions, releases, and operating state. Where current implementation does not yet provide that coverage, artifacts state the gap plainly rather than implying the capability is complete.

The owner may enter interactive commands that clarify decisions, directives, active workspace, role assignment, project focus, or operating state. GT-KB also provides CLI surfaces for platform lifecycle operations such as project initialization, upgrade, health checks, configuration inspection, role-support surfaces, and operating-state reports.

GT-KB may integrate with third-party services for testing, publication, deployment, observability, and release evidence. Those integrations are governed as platform capabilities with explicit configuration, health checks, evidence capture, and failure modes.

GT-KB includes dashboard and reporting surfaces that give the owner centralized visibility into the state of the active application and platform: current configuration, operating state, bridge queue, release blockers, third-party-service status, requirements and test status, computed KPIs, implementation evidence, inventory, historical release data, and reporting plus interactive access to MemBase. Claims about dashboard capabilities must distinguish implemented surfaces from intended surfaces.

GT-KB assists with application lifecycle operations such as testing, deployment, upgrades, rollback, release readiness, remediation, root-cause diagnosis, and triage. It harvests relevant environment and application state, such as logs, reports, test results, release evidence, and operational artifacts, when doing so improves diagnosis or reduces owner burden — particularly during in-service incidents or defects.

GT-KB is distributed as an installable and upgradeable platform bundle. It supports fresh installs and upgrades of existing GT-KB installations. Upgrading GT-KB preserves application lifecycle independence: an upgrade to the platform does not force the active application to change merely to continue operating, except where the owner explicitly accepts a migration, compatibility break, or governed remediation.

---

## §2. Canonical Terminology

The terms below have canonical meanings in GT-KB. Allowed synonyms appear in parentheses. Forbidden uses are noted where they have caused historical drift.

- **application** — the lifecycle object managed by GT-KB. Examples: Agent Red, GT-KB itself (when GT-KB is the active application). Allowed synonyms: "the active application", "hosted application" (when in service). Forbidden: using "application" for the entire `E:\GT-KB` repository when the platform-level meaning is intended (use "platform" instead); using "application" as a synonym for "project".

- **project** — a named grouping of related known work in the backlog. A project may group sub-projects, individual work items, or both. Examples: GTKB-DASHBOARD-002, GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION. Allowed synonyms: "workstream"; "program" (for multi-slice initiatives). Forbidden: using "project" to mean the entire GT-KB repository (that is the platform context); using "project" as a synonym for "application".

- **sub-project** — a named grouping of related work items inside a project. Allowed synonyms: "subproject". Forbidden: using "sub-project" as a separate application or separate backlog source.

- **platform** — GT-KB itself; the lifecycle infrastructure that manages applications. Allowed synonyms: "GT-KB", "GroundTruth-KB", "GT-KB platform". Forbidden: using "platform" for hosted applications (the platform manages applications, is not one).

- **hosted application** — an application deployed and running in service, distinct from its application's GT-KB lifecycle record. Allowed synonyms: "deployed application", "running application", "production application", "in-service application".

- **work item** — the atomic unit of known work in the backlog. All work items are backlog items; there is no separate conceptual class of "backlog item" distinct from work items. Allowed synonyms: "WI", "WI-NNNN" (KB ID prefix), "task" (loose). Forbidden: confusing with "issue" or "ticket" (those are external-system terms).

- **backlog** — the unified view of all known work for an application or platform, including all work items and the project/sub-project groupings that organize those work items. Known work lives in one MemBase source of truth (the canonical `work_items` table), surfaced through `gt backlog list`. Per S337 owner directive (`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`), the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` migration is complete: the former transitional markdown backlog view under `memory/` was deleted (Slice 7-prime), and the steady state is "MemBase only." Allowed synonyms: "work_list", "the work list", "standing backlog". Forbidden: using "backlog" as a synonym for "ignore list" or "deprecated"; using "backlog item" as a separate conceptual class distinct from work item.

- **specification** — an owner-articulated record of what the system must do, recorded in MemBase as one of the spec subtypes (`SPEC-NNNN`, `GOV-NNN`, `DCL-NNN`, `ADR-NNN`, `PB-NNN`, `REQ-NNN`). Allowed synonyms: "spec", per-subtype IDs. Forbidden: using "specification" for technical-design documents, implementation proposals, or tests.

- **requirement** — an owner-stated capability or behavior the system must provide. Allowed synonyms: "FR" (functional), "NFR" (non-functional), "candidate requirement" (pre-approval). Forbidden: using "requirement" loosely for "preference" or "wish"; promoting inferred behaviors to requirements without explicit owner statement.

- **implementation proposal** — a Prime Builder document conveyed to Loyal Opposition through the file bridge for pre-implementation review. Allowed synonyms: "bridge proposal", "proposal" (in bridge context), "NEW" (the bridge file status when first filed). Forbidden: using "implementation proposal" to mean a specification or an implementation report.

- **implementation report** — a Prime Builder document conveyed to Loyal Opposition through the file bridge for post-implementation verification. Allowed synonyms: "post-impl", "post-implementation report". Forbidden: confusing with "implementation proposal" (proposal is pre-impl; report is post-impl); using "implementation report" to claim VERIFIED before LO records that verdict.

- **verification** — Loyal Opposition's evaluation of an implementation report against the linked specifications, resulting in `VERIFIED` or `NO-GO`. `VERIFIED` is dated evidence that the implementation has been verified against the linked specifications; it is not a mere assertion that a specification exists or has been claimed. Forbidden: using "verification" to mean "test pass" alone; claiming `VERIFIED` by Prime without LO recording the verdict.

- **release** — a tagged, deployable build of the GT-KB platform or hosted application, accompanied by a release manifest enumerating constituent component versions. Allowed synonyms: "version", "build", "tag" (specifically a version-tagged build). Forbidden: using "release" for incremental development commits; using "release" for staging-only deployments (those are deployments, not releases).

- **MemBase** — the authoritative append-only/versioned knowledge database for governed records. Implemented as `groundtruth.db` (SQLite). Allowed synonyms: "Knowledge Database", "KB", "groundtruth.db" (file-level), "knowledge_db" (Python module/class). Forbidden: using "MemBase" for ChromaDB or other derived semantic indexes (those are retrieval aids, not authoritative stores); using "MemBase" for `memory/MEMORY.md` (that is session state, not canonical knowledge).

- **Deliberation Archive** — the structured record of decisions, deliberations, advisory reports, owner conversations, Prime Builder insights, Loyal Opposition insights, and rationale crossing the capture threshold. Implemented as the `deliberations` table in `groundtruth.db` with semantic indexing in ChromaDB. Allowed synonyms: "DA", "deliberation_archive" (the table), "DELIB-NNNN" (individual archive records). Forbidden: using "Deliberation Archive" for general session transcripts (transcript harvest is a feeder; the DA is the structured archive).

- **dashboard** — the GT-KB graphical surface providing centralized owner visibility into platform and application state. Allowed synonyms: "Grafana dashboard" (current implementation), "project dashboard". Forbidden: using "dashboard" for static documentation or README-style views (dashboard implies live data + interactive); using "dashboard" to claim implemented capabilities that are only intended (claims must distinguish implemented from intended).

---

## §3. Implemented vs. Intended Surfaces

This artifact describes the operating model the platform is designed to embody. Some described capabilities are fully implemented; others are intended-but-incomplete. This section maps current capability state. Per `OM-DELTA-0030` discipline: claims about platform capabilities must distinguish implemented surfaces from intended surfaces.

**Fully implemented (as of 2026-04-30):**
- Bridge protocol (NEW / REVISED / GO / NO-GO / VERIFIED plus ADVISORY / DEFERRED / WITHDRAWN non-actionable states with dispatcher/TAFE state and numbered bridge files).
- MemBase (`groundtruth.db`) with append-only/versioned governed records.
- Deliberation Archive (table + ChromaDB semantic index).
- Smart-poller with kind-aware routing and single-instance lock (per `gtkb-bridge-poller-001` umbrella).
- Formal-artifact-approval gate for canonical artifact creation.
- Bridge-compliance-gate hook hard-blocking non-compliant proposals/VERIFIED reports.
- MemBase-only standing backlog (canonical `work_items` table surfaced via `gt backlog list`); the transitional markdown view was retired at migration conclusion (per `GOV-STANDING-BACKLOG-001`, `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`, and owner clarification, 2026-05-06).
- CLI surfaces for `gt deliberations`, project initialization, doctor health checks.
- Ollama harness (identity D, suspended with `loyal-opposition` role) per `ADR-OLLAMA-HARNESS-ADOPTION-001`; Phase-1 surfaces: a framework-free Python shim (`scripts/ollama_harness.py`) exposing the canonical full-parity tool set dispatched through a fail-closed local guard adapter (`DCL-OLLAMA-TOOL-PARITY-GATE-001`); static `.api-harness/routing.toml` routing; current default model is `kimi-k2-7-code-cloud` (cloud-backed via cloud API, not local Ollama inference; the Qwen 2.5 Coder 14B original Phase-1 model has been superseded by cloud routing); author-metadata env-var injection (`DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`); the harness-onboarding capability floor (`GOV-HARNESS-ONBOARDING-CONTRACT-001`); and doctor `_check_ollama_harness`. Bridge dispatch routing active; harness currently suspended.

**Intended-but-partial (as of 2026-04-30):**
- Dashboard surfaces (per `GTKB-DASHBOARD-002` slice progress; some surfaces are integrated, others are parked).
- Interactive MemBase access via dashboard (the current web UI is read-only per `CLAUDE.md`; interactive write access is intended-not-implemented).
- Third-party-service status surface in dashboard (intended; not yet implemented as a unified view).
- Comprehensive release manifest + two-stage release validation (per `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001` and `GOV-RELEASE-MANIFEST-README-001` candidate specs awaiting follow-on impl bridges).
- Recurring hygiene automation (Slice 5 of `GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION` deferred per Slice 0 evidence).
- Cross-harness enforcement of bridge protocol (per `DCL-CROSS-HARNESS-ENFORCEMENT-001` — Claude Code Write/Edit covered; other paths tracked as gap or blocked).
- Ollama harness Phase 2+ (per `PROJECT-GTKB-OLLAMA-INTEGRATION`) — multi-model routing, `.api-harness/skills/` adapter generation, dispatch-substrate wiring, and harness-D role promotion. Not implemented in Phase 1.

When a future capability changes implementation state, this section is updated as part of the relevant implementation thread's post-impl report.

---

## §4. Alignment Tests

This artifact supports a simple alignment check for any GT-KB artifact:

1. Does the artifact reduce the owner's role to specifications, clarifications, and decisions?
2. Does it preserve decisions, rationale, requirements, work, tests, and verification evidence as durable artifacts?
3. Does it distinguish implemented behavior from desired behavior?
4. Does it keep authoritative records separate from derived indexes, summaries, dashboards, or generated reports?
5. Does it use the words `application`, `project`, `work item`, `specification`, `implementation proposal`, `implementation report`, `verification`, `release`, `MemBase`, `Deliberation Archive`, `dashboard`, `platform`, and `hosted application` consistently with §2?

Artifacts that fail these tests are candidates for remediation through the standard bridge protocol.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
