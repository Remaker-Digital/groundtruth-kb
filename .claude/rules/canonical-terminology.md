# Canonical Terminology — GroundTruth-KB

This file is the scaffolded glossary of canonical vocabulary for projects built
on GroundTruth KB. It is loaded alongside CLAUDE.md and AGENTS.md at session
start so fresh agent sessions immediately know the project's vocabulary.

**Status:** scaffolded — customize the project-specific rows (marked
`GroundTruth-KB` or in the per-project section) but DO NOT remove the
canonical rows above without replacing them. Doctor will flag missing terms.

**Ties to ADR-0001: Three-Tier Memory Architecture** — MemBase (canonical
truth) / MEMORY.md (operational notepad) / Deliberation Archive (design-
reasoning record). Canonical knowledge lives in MemBase.

---

## Canonical Terms (ADR-0001 core vocabulary)

These eight terms are the core vocabulary every GroundTruth project inherits.
They are referenced by scaffold templates, the doctor check, and the bridge
review gate. DO NOT redefine them locally.

### MemBase

**Definition:** The canonical, authoritative store of specifications and
governed knowledge for the project. Implemented as a SQLite database
(`groundtruth.db`) accessed via the `groundtruth_kb` Python API or `gt` CLI.
Append-only versioning — every mutation creates a new versioned row with
`changed_by`, `changed_at`, and `change_reason`. Current state = latest
version per ID.

**Not to be confused with:** Deliberation Archive (evidentiary / design
reasoning), MEMORY.md (operational notepad).

**Source:** `MEMBASE-4-CLAUDE.md` (pattern doc); `docs/architecture/product-split.md`
("Core Knowledge Database (MemBase)"); `DELIB-0715` (owner settlement).

**Implementation pointer:** `groundtruth.db` (file), `groundtruth_kb.db.KnowledgeDB`
(Python), `gt summary` / `gt assert` (CLI).

### Deliberation Archive

**Canonical alias:** DA

**Definition:** The design-reasoning tier of ADR-0001. A searchable archive
of decisions, reviews, and rejected alternatives that answers *why* the
project is the way it is. Separate from MemBase (which holds *what is true*)
and from MEMORY.md (which holds *what was recently done*).

**Not to be confused with:** MemBase (canonical truth), commit history
(mechanical record, no reasoning structure).

**Source:** `SPEC-2098` (Deliberation Archive feature); `DELIB-0715`.

**Implementation pointer:** `deliberations` table in `groundtruth.db`;
`gt deliberations search <query>` (CLI); ChromaDB vector index at
`.groundtruth-chroma/`.

### MEMORY.md

**Definition:** The operational notepad tier of ADR-0001. A repo-tracked
markdown file at project root that records current status, recent sessions,
and operational pointers. NOT canonical — MEMORY.md can coordinate work but
it cannot make anything true. If MEMORY.md and MemBase disagree, MemBase
wins.

**Not to be confused with:** MemBase (canonical truth), topic files (`memory/*.md`
operational subsystems).

**Source:** `ADR-0001`; `templates/MEMORY.md` (scaffold); `DELIB-0719` (owner
decision for repo-tracked placement at root).

**Implementation pointer:** `MEMORY.md` at repo root.

### Knowledge Database

**Canonical alias:** MemBase (preferred) or GroundTruth KB

**Definition:** Historical/generic term for the specifications+tests+work-items
store. In GT-KB projects, use "MemBase" for the store itself and
"GroundTruth KB" for the product. "Knowledge Database" persists as a
descriptive phrase but is not the canonical noun.

**Not to be confused with:** external knowledge bases (Confluence, Notion)
which lack the append-only governance contract.

**Source:** `MEMBASE-4-CLAUDE.md` (origin of pattern); early GT-KB
transition docs.

### GroundTruth KB

**Canonical alias:** GT-KB

**Definition:** The product name for the specification-driven governance
toolkit. Comprises MemBase (canonical store), the `gt` CLI, scaffolding
templates, the doctor check, the file-bridge protocol (dual-agent profiles),
and the published documentation at `docs/`. Shipped as the PyPI package
`groundtruth-kb`.

**Not to be confused with:** the downstream projects built on top of it
(each tenant is a separate project that consumes GT-KB; GT-KB itself is
the toolkit, not any one tenant).

**Source:** `DELIB-0105` (GroundTruth rename transition); `README.md`;
`pyproject.toml`.

**Implementation pointer:** `src/groundtruth_kb/` (package),
`pyproject.toml` (`name = "groundtruth-kb"`).

### project-resource alias resolution

**Canonical aliases:** the GitHub; project GitHub; repo; the repo; GitHub
repo; GT-KB repo; GroundTruth-KB repo.

**Definition:** Conversational references to source-control resources resolve
through the configured GroundTruth-KB project resource URL unless the owner
explicitly scopes the reference otherwise.

**Configured GitHub repository URL:** `https://github.com/Remaker-Digital/groundtruth-kb`.

**Not to be confused with:** separate project repositories such as Agent Red;
local `origin` remote values; historical or erroneous remotes. If a local
remote points elsewhere, treat it as configuration drift and verify before
using it as evidence.

**Source:** owner correction, 2026-05-03;
`memory/feedback_groundtruth_kb_canonical_project_urls.md`.

**Implementation pointer:** use explicit `--repo Remaker-Digital/groundtruth-kb`
for GitHub CLI checks when the local remote is inconsistent with this record.
The configured alias registry is `.claude/rules/project-resource-aliases.toml`;
the human-readable companion is `memory/project_external_resource_registry.md`.

### GT-KB

**Canonical form:** GroundTruth KB

**Definition:** The short alias for GroundTruth KB. Use in headlines,
chat, file paths, and test-ID prefixes where brevity matters. Expand to
the canonical form once per document at first use.

**Not to be confused with:** GTKB, Ground-Truth-KB, GroundTruth-kb (all
non-canonical).

**Source:** project convention; used throughout `bridge/`, `docs/`,
`scripts/`.

### Prime Builder

**Definition:** The implementing agent in the dual-agent protocol.
Proposes changes, writes code, runs tests, and keeps the system
internally consistent. Receives GO / NO-GO verdicts from Loyal Opposition
via the file bridge.

**Not to be confused with:** Loyal Opposition (reviewer, non-implementing),
owner (provides direction, decisions).

**Source:** `templates/rules/prime-builder.md`; `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`.

**Implementation pointer:** currently embodied by the Claude Code CLI
(model: Opus 4.x). Provider-agnostic by design — see
`src/groundtruth_kb/providers/`.

### Loyal Opposition

**Definition:** The reviewing agent in the dual-agent protocol. Inspects,
critiques, and analyzes proposals, code, and documentation. Produces
evidence-based reports and GO / NO-GO / VERIFIED verdicts. Does not
implement unless the owner explicitly authorizes.

**Not to be confused with:** Prime Builder (implementer), owner (decides
priority).

**Source:** `templates/project/AGENTS.md`; `templates/rules/loyal-opposition.md`.

**Implementation pointer:** currently embodied by the Codex CLI
(model: GPT-5.3-Codex). Provider-agnostic by design.

---

## GT-KB Platform & Lifecycle Terms (S327, owner-required minimum)

These 15 entries cover GT-KB platform identity, the application/project/work-item
lifecycle, the bridge artifacts, and supporting constructs called out in the
S327 owner directive (DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE).
Adopter projects also define their own application-instance term (e.g., the
project_name itself); GT-KB's own checkout adds the instance term in its
self-install. Multi-source attribution per Codex
`gtkb-gov-term-primer-startup-2026-05-02-002.md` F3: each entry cites its
authoritative source. Sources include `.claude/rules/operating-model.md` §2
(canonical for most terms), `AGENTS.md`, role rules, and
`DELIB-GTKB-IDP-TERMINOLOGY`.

### GroundTruth-KB

**Canonical alias:** GroundTruth KB (the existing primer entry above; same product).

**Definition:** Hyphenated form of "GroundTruth KB". Used in package metadata,
file paths, and contexts where space-separated forms confuse parsers.
Equivalent to `GroundTruth KB` and `GT-KB` (alias).

**Source:** project convention; `pyproject.toml` (`name = "groundtruth-kb"`);
`README.md`.

### GTKB

**Canonical form:** GT-KB (preferred) or GroundTruth KB.

**Definition:** Unhyphenated alias appearing in identifier prefixes (e.g.,
`GTKB-ISOLATION-017`, `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`) and TOML/JSON
config keys. Acceptable in machine-targeted contexts; expand to GT-KB for
prose. Per `DELIB-GTKB-IDP-TERMINOLOGY`, GT-KB is the canonical short form;
GTKB persists as a path/identifier alias.

**Not to be confused with:** misspellings like `Ground-Truth-KB` or
`GroundTruth-kb` (non-canonical).

**Source:** project convention (used throughout `bridge/`, identifier
prefixes); `DELIB-GTKB-IDP-TERMINOLOGY`.

### platform

**Definition:** GT-KB itself; the lifecycle infrastructure that manages
applications. Not a hosted application; rather, the Internal Developer
Platform (IDP) that supports the application lifecycle.

**Not to be confused with:** hosted application (the platform manages
applications, is not one); cloud platform (e.g., AWS) which is unrelated.

**Source:** `.claude/rules/operating-model.md` §2 "platform";
`DELIB-GTKB-IDP-TERMINOLOGY`.

### application

**Definition:** The lifecycle object managed by GT-KB. An application is
the unit of governance, release-readiness, and adoption tracking. Examples:
the active application (e.g., the adopter's `project_name`); GT-KB itself
when GT-KB is the active application.

**Not to be confused with:** project (scoped implementation work inside an
application; see "project" below); platform (GT-KB itself; see above);
hosted application (an application in service).

**Source:** `.claude/rules/operating-model.md` §2 "application".

### hosted application

**Definition:** An application deployed and running in service, distinct
from its application's GT-KB lifecycle record. The deployed/running form
of an application (vs. the lifecycle record managed by GT-KB).

**Not to be confused with:** application (the lifecycle object); platform
(GT-KB itself).

**Source:** `.claude/rules/operating-model.md` §2 "hosted application".

### Agent Red

**Canonical full name:** Agent Red Customer Experience.

**Definition:** A separate project, not part of GT-KB. Agent Red previously
validated GT-KB during isolation work, but unqualified GT-KB references must not
resolve to Agent Red files, CI, GitHub Actions, or repository state.

**Configured GitHub repository URLs (canonical-migration window in effect):**

- **Current canonical:** `https://github.com/mike-remakerdigital/agent-red`. This is the repository whose contents are the canonical Agent Red truth at the time of writing.
- **Migration target (de facto under transient exception):** `https://github.com/Remaker-Digital/agent-red-customer-engagement`. Agent Red CI evidence is currently captured against this repository under the transient exception in `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` while the canonical migration completes. The exception is evidence-scoped and does NOT authorize the GT-KB `v0.7.0-rc1` tag until canonical migration and canonical CI binding are complete.

When the canonical migration completes, the migration-target URL becomes the sole canonical and this entry is updated to remove the dual listing.

**Not to be confused with:** the four small demo applications included with
GT-KB, or with the GroundTruth-KB platform repository
`https://github.com/Remaker-Digital/groundtruth-kb`.

**Source:** owner correction, 2026-05-04; dual-repo clarification per S333 audit FINDING-P1-002 (downgraded to P3) and `bridge/gtkb-governance-hygiene-bundle-001.md` Change E.

### adopter

**Definition:** A downstream consumer of GT-KB. An adopter is an
application that uses GT-KB as its governance/lifecycle infrastructure,
e.g., by running `gt project init` to scaffold its repository or by
linking to GT-KB-managed artifacts. Adopter projects receive scaffolded
templates (CLAUDE.md, MEMORY.md, `.claude/rules/canonical-terminology.md`,
etc.) under their own root.

**Not to be confused with:** the GT-KB platform itself; tenants of an
adopter's hosted application (those are the adopter's customers).

**Source:** `DELIB-GTKB-IDP-TERMINOLOGY`; scaffold pattern in
`groundtruth-kb/src/groundtruth_kb/project/scaffold.py`.

### project

**Definition:** A named grouping of related known work in the backlog. A
project may group related sub-projects, individual work items, or both.
Examples: `GTKB-DASHBOARD-002`,
`GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION`. A project is a
workstream/program grouping; not the hosted application.

**Not to be confused with:** application (the lifecycle object;
applications contain projects); platform (GT-KB itself); work item (the
atomic known-work unit).

**Source:** `.claude/rules/operating-model.md` §2 "project"; owner
clarification, 2026-05-06.

### project authorization

**Canonical aliases:** project-scoped implementation authorization; project
implementation authorization.

**Definition:** A MemBase-backed, append-only owner authorization envelope for
a named active project. It records the owner-decision deliberation id, scope,
allowed mutation classes, forbidden operations, included/excluded work items
and specs, optional expiration, and audit metadata. It can remove repeated
owner-approval prompts for bounded project implementation work, but it does not
replace implementation proposals, Loyal Opposition review, bridge `GO`,
proposal `target_paths`, implementation-start packets, spec-derived tests,
implementation reports, or verification.

**Not to be confused with:** backlog membership (known work, not approval);
bridge `GO` (review approval for one proposal); implementation-start
authorization packet (session-local proof for one GO'd proposal).

**Source:** `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`;
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`;
`DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`;
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.

**Implementation pointer:** `project_authorizations` table and
`current_project_authorizations` view in `groundtruth.db`; `gt projects authorize`,
`gt projects authorizations`, and `gt projects revoke-authorization`.

### sub-project

**Canonical aliases:** sub-project; subproject.

**Definition:** A named grouping of related work items inside a project.
A sub-project exists to organize work under a larger project; it is not a
separate application and is not a separate backlog source.

**Not to be confused with:** project (the parent or top-level grouping);
work item (the atomic known-work unit); application (the lifecycle object).

**Source:** owner clarification, 2026-05-06.

### work item

**Definition:** The atomic unit of known work in the backlog. All work
items are backlog items; there is no separate conceptual class of
"backlog item" distinct from work items. Work items are identified by
`WI-NNNN` IDs in MemBase and may carry origin (regression / defect / new),
component, stage, lifecycle state, priority/order, project/sub-project
grouping, and continuation context.

**Not to be confused with:** project or sub-project (groupings of work
items); external issue or ticket records.

**Source:** `.claude/rules/operating-model.md` §2 "work item";
`work_items` table in MemBase; owner clarification, 2026-05-06.

### backlog

**Definition:** The unified view of all known work for an application or
platform. The backlog includes all work items and the project/sub-project
groupings that organize those work items. In this taxonomy, every work
item is in the backlog, and "backlog item" is a general reference to a
work item, not a separate artifact type.

**Taxonomy:** backlog -> projects -> sub-projects -> work items. Projects
may contain sub-projects, work items, or both. Sub-projects contain work
items. Work items are the atomic known-work units.

**Source-of-truth intent:** Known work converges into one MemBase source
of truth (the canonical `work_items` table). During the migration window,
`memory/work_list.md` is a transitional generated view; the file is
regenerated empty as canonical content moves to MemBase.

**Lifecycle endpoint:** Per S337 owner directive
(`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`), at the
conclusion of the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` migration,
`memory/work_list.md` is deleted. The post-migration steady state is
"MemBase only" — no markdown view persists. Migration-completion is gated
by parent thread Slice 7-prime
(`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02`) which physically
removes the file after Slices 2-6 land.

**Not to be confused with:** ignore list or deprecated work (forbidden
uses per operating-model §2); backlog snapshot (point-in-time export);
a separate `backlog_items` conceptual class distinct from work items.

**Source:** `.claude/rules/operating-model.md` §2 "backlog";
`GOV-STANDING-BACKLOG-001` (governance contract); owner clarification,
2026-05-06.

### specification

**Definition:** An owner-articulated record of what the system must do,
recorded in MemBase as one of the spec subtypes (`SPEC-NNNN`, `GOV-NNN`,
`DCL-NNN`, `ADR-NNN`, `PB-NNN`, `REQ-NNN`).

**Not to be confused with:** technical-design document; implementation
proposal (a different bridge artifact); test (a verification artifact).

**Source:** `.claude/rules/operating-model.md` §2 "specification";
`specifications` table in MemBase.

### requirement

**Definition:** An owner-stated capability or behavior the system must
provide. May be functional (FR) or non-functional (NFR). Candidate
requirements are pre-approval; promotion to formal `specification`
requires owner-visible confirmation per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

**Not to be confused with:** preference or wish (informal); inferred
behavior (must not be silently promoted to requirement per
operating-model §1).

**Source:** `.claude/rules/operating-model.md` §2 "requirement".

### implementation proposal

**Definition:** A Prime Builder document conveyed to Loyal Opposition
through the file bridge for pre-implementation review. Filed as
`bridge/<topic>-NNN.md` with `NEW` or `REVISED` status. Must include
`Specification Links`, `Prior Deliberations`, test plan, acceptance
criteria, and risk/rollback per
`.claude/rules/file-bridge-protocol.md`.

**Not to be confused with:** specification (a different artifact type);
implementation report (post-implementation; below).

**Source:** `.claude/rules/operating-model.md` §2 "implementation proposal";
`.claude/rules/file-bridge-protocol.md`.

### implementation report

**Definition:** A Prime Builder document conveyed to Loyal Opposition
through the file bridge for post-implementation verification. Filed as
the next bridge version after implementation completes; must carry
forward Spec Links + provide spec-to-test mapping + verification
evidence + acceptance-criteria check per
`.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived
Verification Gate.

**Not to be confused with:** implementation proposal (pre-implementation);
test (an independent artifact).

**Source:** `.claude/rules/operating-model.md` §2 "implementation report";
`.claude/rules/file-bridge-protocol.md`.

### verification

**Definition:** Loyal Opposition's evaluation of an implementation
report against the linked specifications, resulting in `VERIFIED` or
`NO-GO`. `VERIFIED` is dated evidence that the implementation has been
verified against the linked specifications; it is NOT a mere assertion
that a specification exists or has been claimed.

**Not to be confused with:** test (a single PASS/FAIL check;
verification can require many tests); validation (testing against
real-world use; verification is internal-spec compliance).

**Source:** `.claude/rules/operating-model.md` §2 "verification".

### dashboard

**Definition:** The GT-KB graphical surface providing centralized owner
visibility into platform and application state. Shows configuration,
operating state, bridge queue, release blockers, third-party-service
status, requirements/test status, computed KPIs, implementation evidence,
inventory, historical release data, and reporting plus interactive
access to MemBase.

**Not to be confused with:** static documentation (dashboard implies
live data + interaction); non-interactive README-style views.

**Source:** `.claude/rules/operating-model.md` §2 "dashboard";
`GTKB-DASHBOARD-002` (slice progression).

### bridge

**Canonical full term:** file bridge (the protocol surface).

**Definition:** The Prime Builder ↔ Loyal Opposition coordination
protocol implemented via versioned markdown files under `bridge/` and
the canonical `bridge/INDEX.md` workflow state. Statuses: NEW, REVISED,
GO, NO-GO, VERIFIED. Both agents read and write the index;
implementation never proceeds without GO.

**Not to be confused with:** "the Bridge" as a generic concept (use
"file bridge" in canonical text); cross-system message bridges.

**Source:** `.claude/rules/file-bridge-protocol.md`;
`bridge/INDEX.md`; `AGENTS.md` (Codex-side rule).

---

## GT-KB DA Read-Surface and Operational Vocabulary (S331 backfill)

Per `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, this section adds glossary entries
for load-bearing concepts identified during S331 as canonical but previously
absent from the glossary. Each entry follows the field convention (Definition,
optional Canonical alias, Not to be confused with, Source, Implementation
pointer). Source citations resolve to Deliberation Archive records or MemBase
specifications per `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`.

### isolation

**Definition:** Full-lifecycle independence between the GT-KB platform and any
application built using it. The platform must be able to evolve and release on
its own cadence; an application must be deployable and lifecycle-tracked
independently of platform internals. Isolation motivates application-directory
portability, asymmetric write authority, and separate-repository topology
decisions; relocation of files into `applications/` is one consequence of
isolation, not the definition.

**Canonical alias:** lifecycle independence.

**Not to be confused with:** sandboxing or process isolation (those are runtime
concerns, not lifecycle ones); file-relocation under `applications/` (that is
one consequence — the S331 wrong-frame failure).

**Source:** `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` (S319, 2026-04-28,
owner verbatim); `DELIB-0877` (industry-alignment critique, 2026-04-22);
"S321 owner directive: platform app non specific" (DA title); `DELIB-0879`
(`GTKB-ISOLATION-002` topology plan, 2026-04-22);
`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331 owner clarification:
ZIP-portability test; scope-bound write enforcement).

**Implementation pointer:** `applications/<name>/` placement convention per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`; bridge thread family
`gtkb-isolation-016` … `gtkb-isolation-018-*`.

### session scope

**Definition:** The declared write-authority boundary for an AI session: one
of `GT-KB`, `Application`, or `GT-KB+Application` (exceptional). Scope is
declared at session start and mechanically enforced by hook-level write gating
once the enforcement layer lands.

**Not to be confused with:** `work subject` (work subject names the active
subject area; session scope names the write-authority boundary).

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
three-mode declaration as runtime invariant for lifecycle independence);
`DELIB-0877` (asymmetric safety model, 2026-04-22); `DELIB-0876` (durable
session work subject — adjacent governance).

**Implementation pointer:** Currently advisory-only via
`.claude/session/work-subject.json`. Mechanical enforcement is future work
tracked under a separate proposal.

### bias case

**Definition:** A failure mode in which an AI agent, given two roughly
equivalent options, reliably prefers one over another in a way that produces
wrong outcomes. The wrong option was actively chosen over the right one.

**Not to be confused with:** `salience case` (the right option was never on
the candidate list at all); "bias" used loosely for any agent failure (the
term is reserved for actively-chosen-over).

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
owner-articulated diagnostic distinction); `ADR-DA-READ-SURFACE-PLACEMENT-001`
(alternatives-considered analysis: Path B rejection rationale references
workaround behavior; Path D rationale uses bias-aligned framing).

**Implementation pointer:** Diagnostic frame in proposal evaluation; not a
runtime construct.

### salience case

**Definition:** A failure mode in which an AI agent does not consider a
relevant option because it is not on the natural retrieval path at the moment
of decision. The correct option was never weighed.

**Not to be confused with:** `bias case` (option weighed and rejected);
"salience" in the sense of "importance".

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
aware-but-unused resources indicate placement/salience problem, not
discipline problem); `ADR-DA-READ-SURFACE-PLACEMENT-001` (S331
procedural-failure context that motivated Path D selection).

**Implementation pointer:** Diagnostic frame; informs placement decisions for
resources that are aware-but-unused.

### placement

**Definition:** A design pattern in which a resource is positioned on a path
the agent already traverses (e.g., the always-loaded glossary, the bridge
proposal template, the session-start payload), rather than gated behind a new
behavior the agent must remember to perform. Placement is bias-aligned and
salience-aligned: it makes the resource reachable through existing
reach-patterns rather than fighting agent defaults.

**Canonical alias:** bias-aligned placement.

**Not to be confused with:** enforcement (placement makes the resource
reachable; enforcement gates a behavior). Placement and enforcement are
complementary; the design choice is which to apply when.

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
placement-over-coercion principle); `ADR-DA-READ-SURFACE-PLACEMENT-001`
(Phase 0; placement codified as the chosen design path).

**Implementation pointer:** Primary design lens for
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001` and downstream phases.

### glossary as DA read surface

**Definition:** The architectural role assigned to
`.claude/rules/canonical-terminology.md` by
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`: the glossary is the agent-side primary
read path for prior-decision consultation; the Deliberation Archive is the
substrate the glossary cites. Direct DA semantic search is the long-tail /
audit / rationale-deep-dive path.

**Not to be confused with:** treating the glossary as a complete substitute
for the DA (it is the read path, not the substrate); treating the DA as
deprecated (it remains the rationale and provenance store).

**Source:** `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (Phase 0);
`ADR-DA-READ-SURFACE-PLACEMENT-001` (Phase 0);
`DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` (Phase 0);
`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331 owner-approved
framing).

**Implementation pointer:** This entry is itself an instance of the
principle: it cites the formal artifacts that define it.

### harness

**Definition:** An AI coding harness; the runtime/identity layer that hosts
an AI model and implements roles. Examples: Claude Code (currently harness
ID `B`), Codex CLI (currently harness ID `A`). Harness identity is
installation-stable; roles attach to harnesses by owner assignment, not by
vendor.

**Canonical alias:** AI coding harness.

**Not to be confused with:** model (e.g., Opus 4.7, GPT-5.3-Codex) — a
harness hosts a model; the same model can run in different harnesses. Role
assignment (see `role assignment`) is separate from harness identity.

**Source:** `DELIB-0830` (Loyal Opposition assumes acting Prime Builder);
`DELIB-0831` (Prime/LO are portable across harnesses); `DELIB-0832` (GT-KB
installs configure Prime Builder).

**Implementation pointer:** `harness-state/harness-identities.json`;
`scripts/harness_identity.py` (identity-change CLI);
`.claude/rules/operating-role.md`.

### harness identity

**Definition:** The persistent, installation-stable ID assigned to each
installed AI coding harness on a workstation. IDs (`A`, `B`, `C`, …) are
unique and do not change after initial assignment except through an explicit
owner-requested identity change operation. Startup resolves the active
harness's identity from the persistent record before any role lookup.

**Not to be confused with:** session ID; model name; role assignment (the
role attached to the harness).

**Source:** `DELIB-0832` (GT-KB installs configure harness identity);
`DELIB-0831` (harness portability requires identity stability).

**Implementation pointer:** `harness-state/harness-identities.json`;
`python scripts/harness_identity.py set --harness-name <name>
--harness-id <id> --owner-requested`.

### role assignment

**Definition:** The binding of an AI coding harness to a role (Prime Builder
or Loyal Opposition). The owner assigns the Prime Builder role; the bridge
counterpart is always Loyal Opposition. The role map records one role per
harness ID. Switching a harness to Prime Builder demotes all other recorded
harnesses to Loyal Opposition in the same update.

**Canonical alias:** operating role.

**Not to be confused with:** harness identity (the ID is stable; the role
attached to it can change). The role attaches to the harness ID, not to a
model, vendor name, or transient session.

**Source:** `DELIB-0830` (LO assumes acting Prime Builder); `DELIB-0831`
(Prime/LO are portable); `DELIB-0832` (installation-time role
configuration).

**Implementation pointer:** `harness-state/role-assignments.json`;
`.claude/rules/operating-role.md`; `.claude/rules/prime-builder-role.md`;
`.claude/rules/loyal-opposition.md`.

### bridge thread

**Definition:** The multi-version conversational unit between Prime Builder
and Loyal Opposition on a single topic. A bridge thread is identified by a
kebab-case slug and consists of an ordered sequence of versioned files
(`bridge/<slug>-001.md`, `-002.md`, …) plus a single entry in
`bridge/INDEX.md`. The thread terminates at `VERIFIED` or owner-directed
retirement.

**Not to be confused with:** bridge file (a single version within a thread);
bridge document (the full version chain).

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001` (live bridge index authority).

**Implementation pointer:** `bridge/<slug>-NNN.md`; `bridge/INDEX.md`;
`.claude/rules/file-bridge-protocol.md`.

### GO / NO-GO / VERIFIED

**Definition:** The terminal verdicts in the file-bridge protocol, set by
Loyal Opposition. `GO` approves a `NEW` or `REVISED` proposal for
implementation. `NO-GO` requires Prime Builder revision. `VERIFIED` is dated
evidence that an implementation report has been verified against the linked
specifications. `NEW` (Prime-set, fresh proposal) and `REVISED` (Prime-set,
after a NO-GO) are upstream Prime-side states.

**Not to be confused with:** test pass/fail (a single test result); spec
status fields like `specified`, `implemented`, `verified` (those are MemBase
spec lifecycle states, distinct from bridge verdicts).

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001`.

**Implementation pointer:** Verdict lines in `bridge/<slug>-NNN.md` and the
corresponding `bridge/INDEX.md` entry; `.claude/rules/file-bridge-protocol.md`
§ Statuses.

### Loyal Opposition advisory

**Definition:** A Codex-initiated bridge entry that delivers an advisory
recommendation to Prime Builder, distinct from a Prime-initiated proposal.
An LO advisory is filed at `bridge/<slug>-001.md` with status `NO-GO`
(deliberate) and a `bridge_kind: loyal_opposition_advisory` header. It tasks
Prime Builder with filing a normal implementation proposal that converts the
advisory into scoped, testable GT-KB work.

**Not to be confused with:** an LO review verdict on a Prime proposal (those
carry GO/NO-GO/VERIFIED against an existing Prime-filed
`NEW`/`REVISED`/post-implementation report).

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001`.

**Implementation pointer:** `bridge_kind: loyal_opposition_advisory` header
field; precedent bootstrap pattern at
`bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`.

### applicability preflight

**Definition:** The mandatory mechanical bridge gate that checks a bridge
proposal/report's `Specification Links` section against
`config/governance/spec-applicability.toml` for cross-cutting specs triggered
by the proposal's path or content. The gate emits a packet hash that LO
verdicts cite. Returns `preflight_passed: false` when required cross-cutting
specs are missing.

**Not to be confused with:** `clause preflight` (a finer-grained sibling
that checks ADR/DCL clause-level evidence, not just citation presence).

**Source:** `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (the
constraint the gate enforces).

**Implementation pointer:**
`python scripts/bridge_applicability_preflight.py --bridge-id <id>`;
`.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight
Subsection.

### clause preflight

**Definition:** The mandatory companion preflight that asks, for each
ADR/DCL clause registered in `config/governance/adr-dcl-clauses.toml`,
whether the bridge proposal/report shows evidence satisfying the clause.
Emits an exit-5 blocking gate when any `must_apply` clause with both
`severity = "blocking"` and `enforcement_mode = "blocking"` lacks satisfying
evidence and is not explicitly owner-waived.

**Not to be confused with:** `applicability preflight` (citation presence
only). Clause preflight is finer-grained: it inspects clause-level evidence.

**Source:** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (the
constraint the gate enforces).

**Implementation pointer:**
`python scripts/adr_dcl_clause_preflight.py --bridge-id <id>`;
`--report-only` is diagnostic only.

### bridge compliance gate

**Definition:** A `PreToolUse` Write hook
(`.claude/hooks/bridge-compliance-gate.py`) that fails the Write of bridge
proposals/reports lacking required protocol elements. Currently enforces the
`Owner Decisions / Input` section requirement when the proposal/report
depends on owner approval.

**Not to be confused with:** the applicability/clause preflight tools (those
are reviewer-run gates; the compliance gate is author-side at Write time).

**Source:** `SPEC-AUQ-POLICY-ENGINE-001` (deterministic policy engine that
the gate participates in);
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (Owner Decisions /
Input section is a linkage requirement).

**Implementation pointer:** `.claude/hooks/bridge-compliance-gate.py`
registered on `PreToolUse(Write|Edit)`;
`.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input
Section Gate.

### scanner-safe-writer

**Definition:** A credential-scan PreToolUse hook that scans Write/Edit
content against the canonical credential catalog
(`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) and blocks writes
containing credential-shaped spans. The hook applies to direct Write/Edit
tool calls; helper scripts that bypass the Write tool require their own scan
implementation.

**Not to be confused with:** the bridge-propose helper's internal credential
scan (a separate implementation of the same patterns for helper-mediated
writes).

**Source:** `DELIB-0687` (VERIFIED Credential Scan Narrowing
Post-Implementation Verification — establishes the canonical credential
pattern set); `GOV-ARTIFACT-APPROVAL-001` (credential safety as part of the
formal-artifact-approval discipline).

**Implementation pointer:** `.claude/hooks/scanner-safe-writer.py`;
`.claude/skills/bridge-propose/SKILL.md` (helper-side scan).

### owner-decision tracker

**Definition:** A `Stop`-mode hook
(`.claude/hooks/owner-decision-tracker.py`) that detects prose decision-ask
patterns in agent output and refuses turn-end when no `AskUserQuestion` tool
call occurred in the same turn. Records detected questions in
`memory/pending-owner-decisions.md`.

**Not to be confused with:** the `bridge compliance gate` (Write-time hook
on proposals); the `AskUserQuestion` tool itself (the tracker enforces use
of the tool, not the tool itself).

**Source:** `SPEC-AUQ-POLICY-ENGINE-001` (central deterministic policy
engine returning canonical outcomes); `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
(deterministic-only; no LLM classifiers).

**Implementation pointer:** `.claude/hooks/owner-decision-tracker.py`
registered on `Stop`. `memory/pending-owner-decisions.md` is the durable
record.

### prose decision-ask pattern

**Definition:** A pattern class (regex-detectable) in agent output that
resembles asking the owner for a decision in prose rather than via
`AskUserQuestion`. The owner-decision tracker's `PROSE_DECISION_PATTERNS`
constant defines the patterns. When detected without an accompanying
`AskUserQuestion` call in the same turn, the tracker blocks turn-end.

**Not to be confused with:** factual reporting that mentions pending
decisions (those are status updates, not asks); status-update questions
like a single `?`.

**Source:** `SPEC-AUQ-NO-LLM-CLASSIFIER-001` (deterministic patterns, not
LLM classification); `SPEC-AUQ-POLICY-ENGINE-001` (engine that consumes the
patterns).

**Implementation pointer:** Pattern definitions in
`.claude/hooks/owner-decision-tracker.py`. Avoid quoting matched fragments
verbatim in prose to prevent recursive re-firing.

### AskUserQuestion

**Definition:** The Claude Code tool that presents a structured question to
the owner with 2-4 mutually-exclusive options, producing a clickable popup
that captures the answer inline. Per the AUQ-only enforcement stack, this
is the only valid channel for collecting owner decisions in scope
(approvals, waivers, priority choices, formal artifact approvals,
requirement clarifications, destructive actions, deployments, blocking
owner decisions).

**Canonical alias:** AUQ.

**Not to be confused with:** prose decision-ask patterns (anti-patterns);
status-update reports (factual, not decision-asking).

**Source:** `SPEC-AUQ-POLICY-ENGINE-001`; `SPEC-AUQ-NO-LLM-CLASSIFIER-001`.

**Implementation pointer:** Claude Code built-in tool. Codex parity is
forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Mechanical
enforcement via `.claude/hooks/owner-decision-tracker.py`.

### operating model

**Definition:** The canonical operating-model artifact for GT-KB at
`.claude/rules/operating-model.md`. Carries rule-cited soft authority:
cited by `.claude/rules/loyal-opposition.md` and `AGENTS.md` as the
operating-model reference; its terminology and framing are the alignment
baseline for future remediation work. No hook or test mechanically enforces
compliance with this artifact's text.

**Not to be confused with:** an architectural specification (the
operating-model is current how-it-works narrative; specifications are
what-must-do constraints); a vision document.

**Source:** `DELIB-S324-OM-DELTA-0001-CHOICE` (LO authority over
requirements); `DELIB-S324-OM-DELTA-0003-CHOICE`
(application/project/platform/hosted-application terminology);
`DELIB-S324-OM-DELTA-0004-CHOICE` (backlog ordering semantics).

**Implementation pointer:** `.claude/rules/operating-model.md`. Future
changes require an owner-approved bridge proposal and a
formal-artifact-approval packet.

### operating role

**Definition:** The authority-bearing harness role recorded for an active
harness ID in `harness-state/role-assignments.json`. Canonical values are
`prime-builder` (implementing authority) and `loyal-opposition` (reviewing
authority). The legacy value `acting-prime-builder` is READ-accepted for
backward compatibility but SET-rejected (cannot be assigned as a new role)
per the Acting-Prime Compatibility Contract.

**Canonical alias:** durable operating role; harness role.

**Not to be confused with:** session lane (non-authority work classification;
see below); session focus (owner-facing startup selection); work subject
(active subject area; see below).

**Source:** `GOV-HARNESS-ROLE-PORTABILITY-001`; `GOV-ACTING-PRIME-BUILDER-001`;
bridge `gtkb-role-session-lifecycle-simplification-003` REVISED-1 GO at -004.

**Implementation pointer:** `harness-state/role-assignments.json` is the
durable record; `.claude/rules/operating-role.md` is human-readable startup
guidance (not a role record); `scripts/harness_roles.py` enforces the SET/
READ contract.

### session lane

**Definition:** A non-authority work classification used to organize the
current session's focus, distinct from the operating role. Lanes inherit
authority from the current operating role; they do not grant new permissions
or change the durable role assignment. Examples: research, architecture,
implementation, quality engineering, operations/release, documentation,
governance stewardship.

**Not to be confused with:** operating role (authority-bearing; only
prime-builder + loyal-opposition; see above).

**Source:** bridge `gtkb-role-session-lifecycle-simplification-003`
REVISED-1 GO at -004.

**Implementation pointer:** Session lanes appear in Prime Builder startup
focus options; Loyal Opposition does not present a focus menu.

### session focus

**Definition:** The owner-facing startup selection that the active AI
harness presents at the start of a Prime Builder session. The selection
binds the session to a specific work item or focus area for the duration
of the session. Distinct from session lane (classification) and operating
role (authority).

**Not to be confused with:** session lane; operating role; work subject.

**Source:** bridge `gtkb-role-session-lifecycle-simplification-003`
REVISED-1 GO at -004; `GOV-SESSION-SELF-INITIALIZATION-001`.

**Implementation pointer:** `scripts/session_self_initialization.py`
renders the focus menu for Prime Builder; the owner selects one option to
bind the session.

### work subject

**Definition:** The startup-payload concept that names the active subject
area of a session: `gtkb_infrastructure` (the default; owner direction
interpreted as GroundTruth-KB platform work) or `application` (owner
direction interpreted as work on a named adopter/demo application). The
work subject is recorded in `.claude/session/work-subject.json` and is set
by owner commands at session start.

**Canonical alias:** active work subject.

**Not to be confused with:** `session scope` (the write-authority boundary;
subject names what's being worked on, scope names which paths can be
written). Bridge role slot and harness topology are separate dimensions in
the same state file.

**Source:** `DELIB-0876` (durable session work subject);
`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331 distinction
between work subject and session scope).

**Implementation pointer:** `.claude/session/work-subject.json`. Owner
commands: `work subject GT-KB`, `application mode`, `agent red mode`.

### smart poller

**Status:** RETIRED 2026-05-09 (Slice 4 retirement; runtime archived to
`archive/smart-poller-2026-05-09/`).

**Definition:** The (now-retired) bridge-poller automation that scanned
`bridge/INDEX.md` periodically and dispatched the appropriate harness when
a recipient's actionable queue signature changed. The smart poller was
monitoring/dispatch infrastructure only; `bridge/INDEX.md` remained the
canonical workflow state. Bridge dispatch is now governed by the
`cross-harness event-driven trigger` (see entry below).

**Not to be confused with:** the retired `OS poller` class (halted
2026-04-25 per owner directive); the `cross-harness event-driven trigger`
(the current canonical automation path).

**Source:** `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 (mechanism-agnostic
supersede; spawns headless harness instances when actionable);
`DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 (auto-trigger contract supersede);
`DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` (opt-out when functional);
`DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` (spawn to notify
architecture); `DELIB-S321-SMART-POLLER-AUTO-TRIGGER` (S321 owner
directive); `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` (Slice 4
retirement decision); bridge thread
`gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`.

**Implementation pointer:** Archived. Historical artifacts at
`archive/smart-poller-2026-05-09/`: Windows scheduled task
`GTKB-SmartBridgePoller` (halted), VBS daemon
`scripts/run_smart_bridge_poller.vbs`, runner
`groundtruth-kb/scripts/bridge_poller_runner.py`. Doctor's
`_check_smart_bridge_poller` removed in Slice 4 D4.

### cross-harness event-driven trigger

**Canonical alias:** bridge dispatch trigger; cross-harness trigger.

**Definition:** The current canonical bridge-dispatch automation, replacing
the retired smart poller. Implemented as
`scripts/cross_harness_bridge_trigger.py` and registered as PostToolUse +
Stop hooks in `.claude/settings.json` and `.codex/hooks.json`. The trigger
fires on tool-use and Stop events: when `bridge/INDEX.md` is modified by
a tool call or the agent ends a turn, the trigger inspects the indexed
state and dispatches the appropriate counterpart harness if a recipient's
actionable queue signature has changed. The trigger reuses the smart
poller's actionable-signature scheme byte-identically per
`tests/scripts/test_cross_harness_bridge_trigger.py` so the audit-trail
invariants are preserved.

**Not to be confused with:** retired `smart poller` (interval-driven
substrate; archived); retired `OS poller` (blind-polling scheduled-task
class; halted 2026-04-25); the `file bridge` (the protocol surface; the
trigger dispatches into it).

**Source:** Slice 3 closure
`bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`
(VERIFIED) — hook registrations; Slice 4
`bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`
— smart-poller substrate retirement; `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
v2 (mechanism-agnostic supersede); `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2
(auto-trigger contract; trigger MUST dispatch on actionable signature
change); `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (empirical
event-driven trigger foundation).

**Implementation pointer:** `scripts/cross_harness_bridge_trigger.py`
(entrypoint); `.claude/settings.json` (Claude Code-side hook
registration); `.codex/hooks.json` (Codex-side parity registration);
`.gtkb-state/bridge-poller/dispatch-state.json` (per-recipient dispatch
state); `_check_cross_harness_trigger` and `_check_bridge_dispatch_liveness`
in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (health checks).

### role set

**Canonical alias:** role-set; durable role set.

**Definition:** The wire form of a harness's durable operating-role
assignment recorded in ``harness-state/role-assignments.json``. The role set
is a JSON list of role tokens drawn from ``{prime-builder, loyal-opposition}``.
Singleton lists represent the multi-harness case (one role per harness ID);
multi-element lists represent the single-harness case (one harness ID holds
both roles). In-process, role sets are represented as Python ``frozenset[str]``
constructed by ``_normalize_role_field`` in ``scripts/harness_roles.py``.

**Not to be confused with:** ``operating role`` (canonical value type;
``role set`` is the canonical container type). The legacy scalar form
(``"role": "prime-builder"``) is accepted on READ and normalized to a
singleton set; the next WRITE upgrades the on-disk record to list form.

**Source:** ``ADR-SINGLE-HARNESS-OPERATING-MODE-001`` (Path 2 atomic migration
that made role-set the active runtime schema); ``.claude/rules/operating-role.md``
§ Role Set Schema (Active Authority).

**Implementation pointer:** ``scripts/harness_roles.py``: helpers
``_normalize_role_field``, ``_role_set_to_json``, ``is_prime_builder``,
``is_loyal_opposition``. Doctor check
``_check_role_set_topology_consistency`` validates list form, valid tokens,
no duplicates, identity-map vs role-map topology consistency.

### single-harness operating mode

**Canonical alias:** single-harness operating mode; single-harness topology;
single-harness install.

**Definition:** A GT-KB deployment topology in which a single AI coding
harness is installed and holds a multi-element role set
``["prime-builder", "loyal-opposition"]``. The single harness absorbs both
Prime Builder and Loyal Opposition responsibilities; bridge dispatch is
provided by the single-harness bridge dispatcher (per
``SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001``) rather than the cross-harness
event-driven trigger. Single-harness operating mode is first-class architecture,
not a degradation of the multi-harness topology.

**Not to be confused with:** ``multi-harness operating mode`` (two or more
harnesses installed, each with singleton role sets, dispatch via cross-harness
event-driven trigger); ``acting-prime-builder`` legacy compatibility/provenance
value (a READ-accepted historical value, not a topology).

**Source:** ``ADR-SINGLE-HARNESS-OPERATING-MODE-001`` (topology decision);
``SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`` (dispatcher behavior contract);
``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` (wake substrate constraint);
``GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`` (preserved: GT-KB installs
prepare capable harnesses for either role regardless of topology);
``bridge/gtkb-single-harness-bridge-dispatcher-001-013.md`` (Codex GO at -014).

**Implementation pointer:** Topology is determined at runtime by inspecting
the active harness's role-set cardinality in
``harness-state/role-assignments.json``. Multi-element role set ->
single-harness mode applicable. Doctor check
``_check_single_harness_dispatcher_when_required`` warns when applicable but
the scheduled task is absent.

### single-harness bridge dispatcher

**Canonical alias:** single-harness dispatcher; dispatcher (in single-harness
topology context).

**Definition:** The bridge dispatch substrate that operates in single-harness
operating mode. A host-platform scheduled task (Windows Task Scheduler /
launchd / cron per ``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001``) wakes
the dispatcher routine on a fixed interval. The dispatcher reads live
``bridge/INDEX.md``, computes a per-role actionable signature using the same
kind-aware-routing path as the cross-harness event-driven trigger, and
spawns subprocess workers for each role whose actionable signature has
changed. Workers receive the canonical init keyword ``::init gtkb <mode>``
as the prompt's first line plus the ``GTKB_BRIDGE_POLLER_RUN_ID`` and
``GTKB_BRIDGE_DISPATCH_KEYWORD`` env vars.

**Not to be confused with:** ``cross-harness event-driven trigger`` (the
multi-harness dispatch substrate; the two substrates are mutually exclusive
at runtime); retired ``smart poller`` (archived Slice 4 retirement
2026-05-09); retired ``OS poller`` class (halted 2026-04-25).

**Source:** ``SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`` (behavior contract);
``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` (wake substrate constraint);
``ADR-SINGLE-HARNESS-OPERATING-MODE-001`` (topology motivating the
dispatcher); ``bridge/gtkb-single-harness-bridge-dispatcher-001-013.md``
(Codex GO at -014).

**Implementation pointer:** Slice 1 lands the governance scaffolding +
role-set runtime migration; Slice 2 lands the dispatcher script + scheduled
task setup (separate bridge thread; tracked as open follow-on). State path:
``.gtkb-state/bridge-poller/`` shared with the cross-harness trigger.
Failures log: ``.gtkb-state/bridge-poller/dispatch-failures.jsonl``.

### OS poller

**Definition:** The retired bridge-poller class (Windows scheduled tasks
`AgentRedFileBridgeIndexScan-*`, `AgentRedBridgeLivenessAlert`,
`AgentRedPollerLivenessWatcher`; the foreground watchdog; the
`.claude/hooks/poller-freshness.py` hook; the in-session `CronCreate`
poller). All members of this class were halted 2026-04-25 per owner
directive because they polled blindly — waking the harnesses on a fixed
interval regardless of bridge activity — and must not be re-enabled as a
substitute for the smart poller.

**Not to be confused with:** retired `smart poller` (Slice 4 archive);
`cross-harness event-driven trigger` (current canonical automation path).

**Source:** `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` (covers
OLD-poller halt context).

**Implementation pointer:** Listed in `.claude/rules/bridge-essential.md`
§ Operational Mode for do-not-re-enable reference. Re-enabling requires
explicit owner approval and the cost/benefit analysis required by
`bridge-essential.md` § Re-Enabling Pollers.

### canonical init keyword

**Canonical alias:** init-keyword; "::init gtkb <mode>".

**Definition:** The canonical first-line activator syntax for machine-emitted GroundTruth-KB session prompts, formalized as `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`. Regex `^::init gtkb (pb|lo)$`; first-line-only; closed vocabulary `{pb, lo}` (pb = Prime Builder, lo = Loyal Opposition); no synonyms; strict parse. The keyword tells a receiving harness which durable role's auto-process content to render at SessionStart and is the single source of truth for cross-harness dispatch and future single-harness dispatchers.

**Not to be confused with:** the prose role-line that accompanies the keyword as defense-in-depth (the prose line is informational; the keyword is authority); the `init gtkb` shell command for human-typed session initialization (the canonical init keyword is the machine-emitted variant for dispatcher-spawned sessions).

**Source:** `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (syntax); `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (emitter authority + receiver enforcement); `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (Codex GO at -008); `DCL-CONCEPT-ON-CONTACT-001` (load-bearing concept added on first contact).

**Implementation pointer:** Emitted by `scripts/cross_harness_bridge_trigger.py` in `_dispatch_prompt` (canonical keyword derived from durable role per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`). Recognized by `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` SessionStart hooks. Receiver performs set-membership check against own durable role; mismatch produces silent drop with audit log at `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

### doctor

**Definition:** The GT-KB diagnostic surface (typically invoked as
`gt platform doctor` or equivalent) that runs structured health checks
against platform infrastructure: cross-harness-trigger health, bridge state,
scaffold drift, KB integrity, dashboard reachability, and other configured
checks. The doctor is the canonical predicate for several rule-cited
conditions.

**Not to be confused with:** test runs (pytest, ruff, etc.);
release-candidate gate (`scripts/release_candidate_gate.py`).

**Source:** `SPEC-DA-DOCTOR-CHECK` (doctor bridge-thread coverage check);
`SPEC-DSI-DOCTOR-CHECK-001` (doctor invariant reporting
spec-derivation-gate alignment).

**Implementation pointer:** `groundtruth-kb/` doctor implementation.
Specific checks: `_check_cross_harness_trigger`,
`_check_bridge_dispatch_liveness`, scaffold drift, KB integrity, etc.

### release manifest

**Definition:** A versioned enumeration of the deployable components that
constitute a tagged release of the GT-KB platform or a hosted application.
The manifest accompanies the release tag and identifies constituent
component versions so that the release can be reproduced, rolled back, or
audited.

**Not to be confused with:** a release-readiness report (evidence that a
build is safe to deploy; the manifest is the inventory of what's in the
build); a deployment record (post-deployment audit; the manifest is
build-time).

**Source:** `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` (production
release readiness requires governed test evidence; release manifest is the
inventory anchor for that evidence).

**Implementation pointer:** Implementation is intended-but-partial as of
2026-04-30 per `.claude/rules/operating-model.md` §3. Future formal spec
under `GOV-RELEASE-MANIFEST-README-001` (candidate; not yet inserted).

### deliberation harvest

**Definition:** The DA write-side pipeline that captures session content
(LO reports, bridge threads, post-implementation reports, owner decisions)
into the Deliberation Archive table in MemBase plus the ChromaDB semantic
index. Runs as part of session wrap.

**Not to be confused with:** the Deliberation Archive itself (the
destination); direct DA queries (the read-side counterpart).

**Source:** `SPEC-DA-HARVEST-INCLUSION`; `SPEC-DA-HARVEST-EXCLUSION`;
`SPEC-DA-MECHANICAL-ENFORCE`; `SPEC-DA-RETROACTIVE-SWEEP`.

**Implementation pointer:** `python scripts/harvest_session_deliberations.py`;
`.claude/rules/deliberation-protocol.md` § When To Archive Deliberations.

### formal-artifact-approval packet

**Definition:** The per-artifact owner-approval evidence record stored at
`.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`,
required before a formal artifact (GOV/ADR/DCL/PB/SPEC/narrative-artifact/
deliberation) is inserted into MemBase or written to a protected file.
Required fields include `artifact_type`, `artifact_id`, `action`,
`full_content`, `full_content_sha256`, `presented_to_user=true`,
`transcript_captured=true`, `explicit_change_request`, `changed_by`,
`change_reason`, `approved_by=owner`. The
`formal-artifact-approval-gate.py` and `narrative-artifact-approval-gate.py`
PreToolUse hooks gate the write on packet presence + matching content
hash.

**Canonical alias:** approval packet.

**Not to be confused with:** the bridge GO verdict (a bridge GO authorizes
Prime to proceed to per-artifact approval collection; it does not replace
the per-artifact packet).

**Source:** `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`;
`DCL-ARTIFACT-APPROVAL-HOOK-001`.

**Implementation pointer:**
`.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`. Env
vars `GTKB_FORMAL_APPROVAL_PACKET` or
`GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` reference the packet at hook
check time. `config/governance/narrative-artifact-approval.toml` defines
the protected-path patterns for narrative artifacts.

### canonical artifact

**Definition:** An artifact that has been formalized into MemBase or a
protected narrative-authority file with matching
formal-artifact-approval-packet evidence. Includes MemBase rows for GOV /
ADR / DCL / PB / SPEC / REQ types, Deliberation Archive records, and the
protected narrative artifacts at `.claude/rules/*.md`, `AGENTS.md`,
`CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, and
`memory/work_list.md`. Canonical artifacts are subject to append-only
versioning discipline.

**Not to be confused with:** operational state files (`MEMORY.md`,
`memory/*.md` topic files, `.claude/session/*.json`) — those are
notepad-tier per ADR-0001, high-churn, not canonical.

**Source:** `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`.

**Implementation pointer:** Canonical artifacts are gated by
formal-artifact-approval-gate.py (MemBase rows) or
narrative-artifact-approval-gate.py (protected `.md` files) at write time.

### interrogative default

**Definition:** Prime Builder's default posture toward owner factual
claims about GT-KB capabilities, implementation, history, or state: verify
the claim against the existing evidence trail (rule files, KB records, git
history, runtime artifacts) before treating it as canonical input. Where
the statement is incorrect or partial, surface the correction with
evidence; offer the corrected statement as a candidate specification. The
interrogative default does NOT apply to claims the agent cannot verify
(e.g., owner-stated business facts, customer information, organizational
decisions).

**Not to be confused with:** disagreement or pushback in general — the
interrogative default is specifically about verifying owner factual claims
about GT-KB itself.

**Source:** `DELIB-S324-PB-INTERROGATION-DIRECTIVE` (S324 owner directive
establishing the interrogative default).

**Implementation pointer:** Posture, not runtime construct. Applied by
Prime Builder during owner-input processing per
`.claude/rules/operating-model.md` §1 and
`.claude/rules/prime-builder-role.md`.

### specify-on-contact

**Definition:** Governance principle (CLAUDE.md governance index entry
GOV-06): when previously unspecified code is touched, it becomes
controlled. Mirrored at the terminology layer by
`DCL-CONCEPT-ON-CONTACT-001`. Touching a code surface that lacks a
specification triggers specification creation; touching a load-bearing
concept that lacks a glossary entry triggers glossary promotion (per the
DCL).

**Not to be confused with:** the GOV-09 owner-input classification rule
(specification language triggers spec-first workflow);
`DCL-CONCEPT-ON-CONTACT-001` is parallel, not replacement.

**Source:** `DCL-CONCEPT-ON-CONTACT-001` (Phase 0; terminology-layer
mirror that explicitly references the GOV-06 specify-on-contact
precedent).

**Implementation pointer:** Specify-on-contact at the code layer is
enforced through normal Prime Builder spec-first discipline at code-touch
time. The terminology-layer mirror (`DCL-CONCEPT-ON-CONTACT-001`) is
staged across Phase 3 (Stage A) and Phase 6 (Stages B and C).

### assertion category

**Definition:** One of four classifications produced by `scripts/assertion_categorize.py` for currently-failing assertions: `genuine_drift`, `chronic_noise`, `flaky`, `healthy`. Categorization is deterministic inference over `assertion_runs` history; outputs are read-only at `.gtkb-state/assertion-triage/categories/<assertion_id>.json`.

**Not to be confused with:** assertion (the GT-KB machine-verifiable check primitive itself).

**Source:** S349 self-diagnostic; `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md` (Codex GO at -008); SPEC-1662 (GOV-18).

**Implementation pointer:** `scripts/assertion_categorize.py`; `scripts/assertion_retirement_workflow.py`; `.claude/skills/assertion-triage/SKILL.md`.

### genuine_drift

**Definition:** Assertion category indicating: latest run FAIL, prior PASS streak (default >=2 consecutive PASS runs), transition within configurable window (default 7 days). Drift detection per SPEC-1662 (GOV-18). Highest-priority assertion-triage category.

**Not to be confused with:** chronic_noise (all recent runs FAIL) or flaky (transitions in both directions).

**Source:** S349 self-diagnostic; `scripts/assertion_categorize.py` `_categorize()` function.

**Implementation pointer:** `_categorize()` applying `drift_prior_pass` and `drift_window_days` thresholds.

### chronic_noise

**Definition:** Assertion category indicating: all available recent runs FAIL, count meets configurable threshold (default 5; the SPEC-default 50 becomes reachable once the `assertion_runs` retention cap is widened). Candidate for retirement-or-accept owner decision per GOV-15 (test fix gate).

**Not to be confused with:** genuine_drift (recently transitioned from PASS) or flaky (mixed PASS/FAIL).

**Source:** S349 self-diagnostic; SPEC-1662 (GOV-18); `scripts/assertion_retirement_workflow.py` review-candidates / ask / apply-decision flow.

**Implementation pointer:** `scripts/assertion_categorize.py` `_categorize()`; `scripts/assertion_retirement_workflow.py` (one-at-a-time AUQ retirement path).

### flaky

**Definition:** Assertion category indicating: recent runs window includes both PASS and FAIL with at least one transition. Flag for test-quality repair, NOT for retirement.

**Not to be confused with:** chronic_noise (all FAIL, retirement candidate) or genuine_drift (clear FAIL after PASS streak).

**Source:** S349 self-diagnostic; `scripts/assertion_categorize.py` `_categorize()` function.

**Implementation pointer:** `_categorize()` lines computing transitions and PASS/FAIL counts within `flaky_window`.


### advisory-router

**Definition:** A source-read-only, MemBase-mutating Python service that scans
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge
`ADVISORY` entries, and creates one `work_items` row per unhandled advisory under
`GOV-STANDING-BACKLOG-001` authority. Service contract: idempotent on rerun, never
modifies source advisory files, uses `origin='hygiene'` and
`source_spec_id='GOV-STANDING-BACKLOG-001'`.

**Canonical alias:** advisory backlog router.

**Not to be confused with:** the broader peer-solution-advisory-loop procedure.

**Source:** S349 self-diagnostic investigation (2026-05-13); `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md` (Codex GO at -010).

**Implementation pointer:** `scripts/advisory_backlog_router.py`; Stop-event surface at `.claude/hooks/advisory-router-scan.py` registered in `.claude/settings.json` and `.codex/hooks.json`.

### benchmark

**Definition:** A read-only, deterministic GT-KB measurement script that computes one or more metrics over project artifacts (MemBase rows, bridge files, advisory reports, assertion run history) and emits structured output (JSON + markdown summary) to `.gtkb-state/benchmarks/<run_id>/`. Each benchmark is a standalone module exposing a `run(window_start, window_end, project_root) -> BenchmarkResult` entry point; results are idempotent for fixed inputs. Distinct from MemBase mutation: benchmarks observe state and write only to runtime evidence directories, never to canonical tables.

**Canonical alias:** measurement script; metric collector.

**Not to be confused with:** test (PASS/FAIL primitive against a specification); assertion (machine-verifiable check attached to a spec); doctor check (health verification with WARN/FAIL severity).

**Source:** `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` (Codex GO at -010); `SPEC-1662` (GOV-18 Assertion Quality Standard); `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

**Implementation pointer:** `scripts/benchmarks/*.py` modules; `scripts/benchmarks/cli.py` for `run` / `report` / `compare` subcommands; output convention `.gtkb-state/benchmarks/<run_id>/`.

### linkage heat map

**Definition:** A 5x5 matrix benchmark output that scores cross-artifact reference rates between five GT-KB artifact classes (specifications, tests, work_items, deliberations, bridge threads). Each cell records the count of from-class entries that cite to-class entries within a configured time window. Used to detect under-linkage (e.g., specifications without test coverage citations) and over-coupling (e.g., work_items with excessive cross-class fanout).

**Canonical alias:** cross-artifact linkage matrix.

**Not to be confused with:** dependency graph (directional, edge-typed); spec-to-test mapping (one-to-many per spec, not a class-level summary).

**Source:** `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` IP-2 (Benchmark 1); `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

**Implementation pointer:** `scripts/benchmarks/linkage_heatmap.py`; output JSON written to `.gtkb-state/benchmarks/<run_id>/linkage_heatmap.json`.

### advisory latency

**Definition:** A benchmark output that measures the elapsed time between Loyal Opposition advisory creation (INSIGHTS-*.md file ctime in `CODEX-INSIGHT-DROPBOX/` or bridge `ADVISORY` entry filing) and Prime Builder action on the advisory (conversion proposal filing, rejection deliberation, or owner-decision capture). Expressed as a per-advisory duration plus aggregate dimensions (median, p90, count by classification state). Used to detect advisory backlog accumulation and slow-path advisory handling.

**Canonical alias:** advisory-to-action latency; advisory turnaround time.

**Not to be confused with:** dispatch latency (cross-harness trigger spawn timing); review latency (NEW/REVISED to GO/NO-GO duration).

**Source:** `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` IP-2 (Benchmark 5); `.claude/rules/peer-solution-advisory-loop.md` (the advisory-handling procedure measured).

**Implementation pointer:** `scripts/benchmarks/advisory_latency.py`; output JSON written to `.gtkb-state/benchmarks/<run_id>/advisory_latency.json`.

### metric snapshot

**Definition:** The atomic output unit produced by a single benchmark run. A snapshot is a `BenchmarkResult` dataclass instance carrying: `run_id`, `benchmark_id`, `window_start`, `window_end`, `value`, `dimensions` (dict of named axes), `source_commit` (git HEAD at run time), `source_query` (the parameterized query used), and `generated_at` (UTC ISO timestamp). Multiple snapshots from one benchmark run are written together as JSON to `.gtkb-state/benchmarks/<run_id>/<benchmark_id>.json` with a markdown summary at `<run_id>/<benchmark_id>.md`.

**Canonical alias:** benchmark result; measurement snapshot.

**Not to be confused with:** session snapshot (point-in-time KB summary used for handoff); backlog snapshot (the `backlog_snapshots` MemBase table); assertion run record (single PASS/FAIL captured in `assertion_runs`).

**Source:** `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` IP-1 (shared common module); `groundtruth_kb.benchmarks.common` dataclass definition.

**Implementation pointer:** `scripts/benchmarks/common.py` `BenchmarkResult` dataclass; `write_run_outputs(run_id, results)` helper that emits JSON + markdown pairs.


---

## Alias / Canonical Disposition

| Alias (non-canonical) | Canonical | Treatment |
|-----------------------|-----------|-----------|
| DA | Deliberation Archive | Alias acceptable; expand at first use per document |
| GT-KB | GroundTruth KB | Alias acceptable; canonical form in headlines and formal text |
| Knowledge Database | MemBase | Historical phrase; use "MemBase" going forward |
| The KB | MemBase | Conversational alias; use "MemBase" in canonical text |
| The Database | MemBase | Conversational alias; use "MemBase" in canonical text |
| The Bridge | file bridge | Conversational alias; use "file bridge" in canonical text |
| (tenant acronyms) | (tenant name) | Tenant aliases are project-scoped; not GroundTruth KB vocabulary |

Aliases resolve to canonical forms. Two forms with divergent definitions is
a drift defect — the doctor will eventually flag it.

---

## Expected Glossary Artifact Terms (MEMBASE-4-CLAUDE.md full set)

These terms come from the full `MEMBASE-4-CLAUDE.md` glossary. Projects
adopting GT-KB inherit them.

### Artifact Types

| Term | Table | Summary |
|------|-------|---------|
| Specification | `specifications` | Business requirement with decision log structure |
| Test | `tests` | Testable assertion with PASS/FAIL semantics |
| Test Plan | `test_plans` | Orchestrating artifact — ordered phases with gate criteria |
| Work Item | `work_items` | Classified unit of work (origin + component) with stage lifecycle |
| Backlog Snapshot | `backlog_snapshots` | Point-in-time snapshot of open WIs |
| Operational Procedure | `operational_procedures` | Repeatable process (deploy/verify/audit) |
| Document | `documents` | General-purpose project knowledge under change control |
| Environment Config | `environment_config` | Environment-specific values under change control |

### Supporting Records

| Term | Table | Summary |
|------|-------|---------|
| Assertion Run | `assertion_runs` | Historical assertion execution record |
| Session Prompt | `session_prompts` | Structured handoff message for next session |

### Concepts (not tables)

| Term | Summary |
|------|---------|
| Assertion | Machine-verifiable check attached to a specification (grep/grep_absent/glob) |
| Phantom Artifact | Concept referenced as tracked entity with no backing storage |
| Orchestrating Artifact | Composes other artifacts by reference only (no content duplication) |
| Governance Principle | Process rule (GOV-\*) governing human-AI team collaboration |
| Protected Behavior | Spec with `type = 'protected_behavior'` + must-always-pass assertions |
| Append-Only Change Control | Versioning discipline — no UPDATE, no DELETE |
| Session Handoff | Mechanism for storing context for the next session |
| Specify on Contact | GOV-06 — touching unspecified code brings it under control |
| Audit Session | Every Nth session auto-flagged for fresh-context integrity review |

---

## Project-specific Terminology

Add project-specific canonical terms here (keep ADR-0001 core vocabulary
above intact):

<!-- Add your project-specific terms below. Use the same structure:
Term, definition, not-to-be-confused-with, source, implementation pointer. -->

---

## Doctor Contract

The `gt project doctor` command verifies that this file and the startup-
visible surfaces (CLAUDE.md, AGENTS.md, MEMORY.md) contain the canonical
terms required for the project's profile. Missing canonical terms are
ERROR-level; minor drift is WARN-level. See
`.claude/rules/canonical-terminology.toml` for the required-terms matrix.

---

*{{COPYRIGHT}}*
