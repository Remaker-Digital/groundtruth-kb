<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project codex`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Canonical Terminology â€” GroundTruth-KB

This file is the scaffolded glossary of canonical vocabulary for projects built
on GroundTruth KB. Base session startup loads only the **core primer subset**
(see `required_primer_terms` in `canonical-terminology.toml`); activity-specific
terms load when an agent opens the corresponding activity envelope with
`::open <activity>` (SPEC-INTAKE-46594e).

**Status:** scaffolded â€” customize the project-specific rows (marked
`GroundTruth-KB` or in the per-project section) but DO NOT remove the
canonical rows above without replacing them. Doctor will flag missing terms.

**Ties to ADR-0001: Three-Tier Memory Architecture** â€” MemBase (canonical
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
Append-only versioning â€” every mutation creates a new versioned row with
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
and operational pointers. NOT canonical â€” MEMORY.md can coordinate work but
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

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#knowledge-database).*

### GroundTruth KB

**Canonical alias:** GT-KB

**Definition:** The product name for the specification-driven governance
toolkit. Comprises MemBase (canonical store), the `gt` CLI, scaffolding
templates, the doctor check, the file-bridge protocol (dual-agent profiles),
and the published documentation at `docs/`. Shipped as the PyPI package
`groundtruth-kb`.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#groundtruth-kb).*

### project-resource alias resolution

**Definition:** Conversational references to source-control resources resolve
through the configured GroundTruth-KB project resource URL unless the owner
explicitly scopes the reference otherwise.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#project-resource-alias-resolution).*

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

**Source:** `templates/rules/prime-builder.md`; the counterpart-harness session-bootstrap template under `templates/project/`.

**Implementation pointer:** the harness currently holding the Prime Builder role assignment per `harness-state/harness-registry.json`. Provider-agnostic by design — see
(model: Opus 4.x). Provider-agnostic by design â€” see
`src/groundtruth_kb/providers/`.

### Loyal Opposition

**Definition:** The reviewing agent in the dual-agent protocol. Inspects,
critiques, and analyzes proposals, code, and documentation. Produces
evidence-based reports and GO / NO-GO / VERIFIED verdicts. Does not
implement unless the owner explicitly authorizes.

**Not to be confused with:** Prime Builder (implementer), owner (decides
priority).

**Source:** `templates/project/AGENTS.md`; `templates/rules/loyal-opposition.md`.

**Implementation pointer:** the harness currently holding the Loyal Opposition role assignment per `harness-state/harness-registry.json`.
Provider-agnostic by design.

---

## GT-KB Platform & Lifecycle Terms (S327, owner-required minimum)

These 15 entries cover GT-KB platform identity, the application/project/work-item
lifecycle, the bridge artifacts, and supporting constructs called out in the
S327 owner directive (DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE).
Adopter projects also define their own application-instance term (e.g., the
project_name itself); GT-KB's own checkout adds the instance term in its
self-install. Multi-source attribution per the Loyal Opposition review
`gtkb-gov-term-primer-startup-2026-05-02-002.md` F3: each entry cites its
authoritative source. Sources include `.codex/rules/operating-model.md` §2
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

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "platform";
`DELIB-GTKB-IDP-TERMINOLOGY`.

### application

**Definition:** The lifecycle object managed by GT-KB. An application is
the unit of governance, release-readiness, and adoption tracking. Examples:
the active application (e.g., the adopter's `project_name`); GT-KB itself
when GT-KB is the active application.

**Not to be confused with:** project (scoped implementation work inside an
application; see "project" below); platform (GT-KB itself; see above);
hosted application (an application in service).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "application".

### hosted application

**Definition:** An application deployed and running in service, distinct
from its application's GT-KB lifecycle record. The deployed/running form
of an application (vs. the lifecycle record managed by GT-KB).

**Not to be confused with:** application (the lifecycle object); platform
(GT-KB itself).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "hosted application".

### Agent Red

**Canonical full name:** Agent Red Customer Experience.

**Definition:** The reference adopter application for GT-KB. Agent Red exercises
the platform's application-isolation contract in continuous use through a
deliberately lifecycle-independent repository and CI cadence. The application
subtree lives at `applications/Agent_Red/` per `CLAUDE.md` Â§ Mandatory Project Root Boundary and is described by `applications/Agent_Red/.gtkb-app-isolation.json`. The hosted form deploys from a lifecycle-independent repository (see "Configured GitHub repository URLs" below).

**Role in GT-KB.** Agent Red is the isolation validator: portability of Agent Red
between GT-KB installations is the operative test of the platform/application
isolation contract (`ADR-APPLICATION-ISOLATION-CONTRACT-001` proposed;
`DCL-APP-ROOT-MINIMIZATION-001` proposed; `applications/Agent_Red/.gtkb-app-isolation.json`). Active adopter-experience work tracks under `PROJECT-GTKB-ADOPTER-EXPERIENCE` (e.g., the Agent Red deployability preservation gate at `bridge/gtkb-agent-red-deployability-preservation-gate-*`).

**Tooling-reference discipline (2026-05-04 narrowing).** Unqualified GT-KB tooling references â€” CLI invocations, CI workflows, GitHub Actions, release evidence, repository state â€” must not resolve silently to Agent Red surfaces. Agent Red surfaces are addressed explicitly when in scope (e.g., adopter-experience work, isolation validation, Agent Red CI binding). The narrowing scopes tooling-reference resolution; it does not alter Agent Red's role as the reference adopter application or the isolation validator.

**Configured GitHub repository URLs (canonical-migration window in effect):**

- **Current canonical:** `https://github.com/mike-remakerdigital/agent-red`. This is the repository whose contents are the canonical Agent Red truth at the time of writing.
- **Migration target (de facto under transient exception):** `https://github.com/Remaker-Digital/agent-red-customer-engagement`. Agent Red CI evidence is currently captured against this repository under the transient exception in `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` while the canonical migration completes. The exception is evidence-scoped and does NOT authorize the GT-KB `v0.7.0-rc1` tag until canonical migration and canonical CI binding are complete.

When the canonical migration completes, the migration-target URL becomes the sole canonical and this entry is updated to remove the dual listing.

**Not to be confused with:** the five adopter fixtures in `groundtruth-kb/examples/` (those are scaffolded examples, not the reference adopter); the GroundTruth-KB platform repository `https://github.com/Remaker-Digital/groundtruth-kb` (the platform that manages Agent Red as its reference adopter); a deployed Agent Red instance running in service (that is a "hosted application" â€” Agent Red's hosted form). Separate-repository topology is the *mechanism* of lifecycle independence; it should not be misread as severance from GT-KB.

**Source:** `GOV-AGENT-RED-GTKB-CONFORMANCE-001`; `DELIB-0834`; owner directive 2026-05-04 (tooling-reference narrowing); owner-decision capture S347 (2026-05-24, reference-adopter framing restoration); dual-repo clarification per S333 audit FINDING-P1-002 (downgraded to P3) and `bridge/gtkb-governance-hygiene-bundle-001.md` Change E.

### `::open` activity marker

**Definition:** A first-line marker caught by a hook. It triggers pre-loading of the
skills, tools, and reference information an agent needs to perform that activity and
to locate further tools. The activity vocabulary is closed:
`{ops, deliberation, build, test, spec, project}`.

**Paired marker:** `::close`, also caught by a hook, triggers harvest of the durable
information produced during that activity before the session context is lost.
Harvested information updates canonical source-of-truth artifacts.

**Three-axis disambiguation (do not conflate):**

| Axis | Mechanism | Example |
|------|-----------|---------|
| **Activity TYPE** | Closed `::open <activity>` keyword | `::open build` |
| **TARGET / subject** | Optional payload on typed open (per-type specs) | project/spec target fields |
| **AREA / scope** | `::init` subject token `{gtkb, application}` | `::init gtkb pb` |

**Source:** owner directive, 2026-08-13.

### adopter

**Definition:** A downstream consumer of GT-KB. An adopter is an
application that uses GT-KB as its governance/lifecycle infrastructure,
e.g., by running `gt project init` to scaffold its repository or by
linking to GT-KB-managed artifacts. Adopter projects receive scaffolded
templates (CLAUDE.md, MEMORY.md, `.codex/rules/canonical-terminology.md`,
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

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "project"; owner
clarification, 2026-05-06.

### project authorization

**Definition:** A MemBase-backed, append-only owner authorization envelope for
a named active project. It records the owner-decision deliberation id, scope,
allowed mutation classes, forbidden operations, included/excluded work items
and specs, optional expiration, and audit metadata. It can remove repeated
owner-approval prompts for bounded project implementation work, but it does not
replace implementation proposals, Loyal Opposition review, bridge `GO`,
proposal `target_paths`, implementation-start packets, spec-derived tests,
implementation reports, or verification.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#project-authorization).*

### sub-project

**Definition:** A named grouping of related work items inside a project.
A sub-project exists to organize work under a larger project; it is not a
separate application and is not a separate backlog source.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#sub-project).*

### work item

**Definition:** The atomic unit of known work in the backlog. All work
items are backlog items; there is no separate conceptual class of
"backlog item" distinct from work items. Work items are identified by
`WI-NNNN` IDs in MemBase and may carry origin (regression / defect / new),
component, stage, lifecycle state, priority/order, project/sub-project
grouping, and continuation context.

**Not to be confused with:** project or sub-project (groupings of work
items); external issue or ticket records.

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "work item";
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

**Source-of-truth intent:** Known work lives in one MemBase source
of truth (the canonical `work_items` table), surfaced through
`gt backlog list`. The migration to a MemBase-only backlog is complete;
no transitional markdown view persists.

**Resource-selection rule:** A current owner instruction that names `backlog`
selects this MemBase resource, even when the requested work is bridge-
or harness-related. Those words qualify the backlog items; they do not replace
the backlog with the bridge queue. Current literal resource terms outrank
activity defaults, startup order, prior context, notes, and conjecture.

**Lifecycle endpoint:** Per S337 owner directive
(`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`), at the
conclusion of the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` migration the former
transitional markdown backlog view under `memory/` was deleted (Slice
7-prime, `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02`). The steady
state is "MemBase only" â€” the canonical `work_items` table is the sole
backlog authority.

**Not to be confused with:** the bridge queue (current handoff/review state,
read with `gt bridge state-report`); ignore list or deprecated work (forbidden
uses per operating-model Â§2); backlog snapshot (point-in-time export);
a separate `backlog_items` conceptual class distinct from work items.

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "backlog";
`GOV-STANDING-BACKLOG-001` (governance contract); owner clarification,
2026-05-06.

### specification

**Definition:** An owner-articulated record of what the system must do,
recorded in MemBase as one of the spec subtypes (`SPEC-NNNN`, `GOV-NNN`,
`DCL-NNN`, `ADR-NNN`, `PB-NNN`, `REQ-NNN`).

**Not to be confused with:** technical-design document; implementation
proposal (a different bridge artifact); test (a verification artifact).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "specification";
`specifications` table in MemBase.

### requirement

**Definition:** An owner-stated capability or behavior the system must
provide. May be functional (FR) or non-functional (NFR). Candidate
requirements are pre-approval; promotion to formal `specification`
requires owner-visible confirmation per `GOV-SPEC-CAPTURE-TRANSPARENCY-001`.

**Not to be confused with:** preference or wish (informal); inferred
behavior (must not be silently promoted to requirement per
operating-model Â§1).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "requirement".

### implementation proposal

**Definition:** A Prime Builder document conveyed to Loyal Opposition
through the file bridge for pre-implementation review. Filed as
`bridge/<topic>-NNN.md` with `NEW` or `REVISED` status. Must include
`Specification Links`, `Prior Deliberations`, test plan, acceptance
criteria, and risk/rollback per
`.codex/rules/file-bridge-protocol.md`.

**Not to be confused with:** specification (a different artifact type);
implementation report (post-implementation; below).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "implementation proposal";
`.codex/rules/file-bridge-protocol.md`.

### implementation report

**Definition:** A Prime Builder document conveyed to Loyal Opposition
through the file bridge for post-implementation verification. Filed as
the next bridge version after implementation completes; must carry
forward Spec Links + provide spec-to-test mapping + verification
evidence + acceptance-criteria check per
`.codex/rules/file-bridge-protocol.md` Mandatory Specification-Derived
Verification Gate.

**Not to be confused with:** implementation proposal (pre-implementation);
test (an independent artifact).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "implementation report";
`.codex/rules/file-bridge-protocol.md`.

### verification

**Definition:** Loyal Opposition's evaluation of an implementation
report against the linked specifications, resulting in `VERIFIED` or
`NO-GO`. `VERIFIED` is dated evidence that the implementation has been
verified against the linked specifications; it is NOT a mere assertion
that a specification exists or has been claimed.

**Not to be confused with:** test (a single PASS/FAIL check;
verification can require many tests); validation (testing against
real-world use; verification is internal-spec compliance).

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "verification".

### dashboard

**Definition:** The GT-KB graphical surface providing centralized owner
visibility into platform and application state. Shows configuration,
operating state, bridge queue, release blockers, third-party-service
status, requirements/test status, computed KPIs, implementation evidence,
inventory, historical release data, and reporting plus interactive
access to MemBase.

**Not to be confused with:** static documentation (dashboard implies
live data + interaction); non-interactive README-style views.

**Source:** `.harness-baseline-configuration/rules/operating-model.md` Â§2 "dashboard";
`GTKB-DASHBOARD-002` (slice progression).

### bridge

**Canonical full term:** file bridge (the protocol surface).

**Definition:** The Prime Builder â†” Loyal Opposition coordination
protocol implemented through dispatcher-backed bridge state and versioned
markdown audit files under `bridge/`. The twelve statuses are fixed by
`CANONICAL_STATUSES` in `groundtruth_kb.bridge.vocabulary`. Aggregate queue
artifacts are not canonical dispatcher or bridge-state authority. Implementation
never proceeds without GO.

**Not to be confused with:** "the Bridge" as a generic concept (use
"file bridge" in canonical text); the backlog; cross-system message bridges.
Bare `bridge`, `bridge work`, `bridge-related`, or `harness` topic
language does not by itself select the bridge queue.

**Source:** bridge-state surfaces; `.codex/rules/file-bridge-protocol.md`
for legacy helper behavior; `AGENTS.md` (cross-harness rule surface).

### bridge queue

**Definition:** The current file-bridge handoff and review workload derived from
bridge state plus the status-bearing numbered files under `bridge/`.
Read it with `gt bridge state-report`. Approved explicit resource terms are
`bridge queue` and `review queue`.

**Not to be confused with:** the backlog, whose known-work authority is MemBase
`current_work_items` and whose read route is `gt backlog list`. Scanning the
bridge at startup or using it as a protected-change gate does not select the
bridge queue as the owner's work resource. If an owner explicitly requests both
resources, preserve both rather than choosing a silent winner.

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-STANDING-BACKLOG-001`;
`DELIB-20260715-WI5266-TERMINAL-VERIFICATION-AUTHORIZATION`.

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

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#isolation).*

### session scope

**Definition:** The declared write-authority boundary for an AI session: one
of `GT-KB`, `Application`, or `GT-KB+Application` (exceptional). Scope is
declared at session start and mechanically enforced by hook-level write gating
once the enforcement layer lands.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#session-scope).*

### bias case

**Definition:** A failure mode in which an AI agent, given two roughly
equivalent options, reliably prefers one over another in a way that produces
wrong outcomes. The wrong option was actively chosen over the right one.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#bias-case).*

### salience case

**Definition:** A failure mode in which an AI agent does not consider a
relevant option because it is not on the natural retrieval path at the moment
of decision. The correct option was never weighed.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#salience-case).*

### placement

**Definition:** A design pattern in which a resource is positioned on a path
the agent already traverses (e.g., the always-loaded glossary, the bridge
proposal template, the session-start payload), rather than gated behind a new
behavior the agent must remember to perform. Placement is bias-aligned and
salience-aligned: it makes the resource reachable through existing
reach-patterns rather than fighting agent defaults.

**Canonical alias:** bias-aligned placement.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#placement).*

### glossary as DA read surface

**Definition:** The architectural role assigned to
`.codex/rules/canonical-terminology.md` by
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`: the glossary is the agent-side primary
read path for prior-decision consultation; the Deliberation Archive is the
substrate the glossary cites. Direct DA semantic search is the long-tail /
audit / rationale-deep-dive path.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#glossary-as-da-read-surface).*

### harness

**Definition:** An AI coding harness; the runtime/identity layer that hosts
an AI model and implements roles. The registered harnesses and their IDs are
enumerated in `harness-state/harness-identities.json`. Harness identity is
installation-stable; roles attach to harnesses by owner assignment, not by
vendor.

**Canonical alias:** AI coding harness.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#harness).*

### harness identity

**Definition:** The persistent, installation-stable ID assigned to each
installed AI coding harness on a workstation. IDs (`A`, `B`, `C`, â€¦) are
unique and do not change after initial assignment except through an explicit
owner-requested identity change operation. Startup resolves the active
harness's identity from the persistent record before any role lookup.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#harness-identity).*

### canonical reader entrypoint

**Definition:** The supported code or CLI interface that consumers use to read
a canonical source-of-truth artifact without re-implementing path, schema,
fallback, or lifecycle semantics.

**Canonical alias:** reader entrypoint.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#canonical-reader-entrypoint).*

### SoT read discipline

Harness-specific contract: each registered harness's native read/search tool events are intercepted per `DCL-SOT-READ-HOOK-CONTRACT-001`.

**Canonical alias:** SoT-read discipline.

**Not to be confused with:** the SoT artifact registry (the data; this is the read-time enforcement) or `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (the governance principle this enforces).

narrative authority `.codex/rules/sot-read-discipline.md`;

**Implementation pointer:** `.codex/hooks/sot-read-discipline.py` (canonical hook) plus per-harness command-verb adapters registered in each harness's hook surface; doctor `_check_sot_read_discipline`; owner-authorized bypass `GTKB_SOT_READ_DISCIPLINE_BYPASS`.

### forbidden substitute

**Definition:** A non-canonical alias path for a source-of-truth artifact that the SoT read discipline blocks reads against, redirecting consumers to the canonical reader/path. Registered in the `forbidden_substitutes` column of the `sot_artifacts` registry.

**Canonical alias:** forbidden-substitute path.

**Not to be confused with:** an archived/historical copy (which may be read for audit via the owner-authorized bypass); a deprecated alias that is not yet registered.

**Source:** `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 (`forbidden_substitutes` metadata); `DCL-SOT-READ-HOOK-CONTRACT-001` v1; `DELIB-20260673`.

**Implementation pointer:** `config/registry/sot-artifacts.toml` (`forbidden_substitutes` entries); enforced by `.codex/hooks/sot-read-discipline.py`.

### handoff prompt

**Definition:** The deterministic-service OUTPUT generated at session close
(canonical ``::wrap``) by the handoff-prompt generator
(``SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001``). A handoff prompt is the
structured content that carries forward session context, continuation scope,
and next-step direction to the next session. It is *generated content*,
distinct from its *persisted record*.

**Canonical alias:** none. Do NOT use "continuation prompt" â€” that label is
explicitly rejected (per ``DELIB-20260883``) as a redundant third term for the
same concept.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#handoff-prompt).*

### role assignment

**Definition:** The binding of an AI coding harness to a role (Prime Builder
or Loyal Opposition). The owner assigns the Prime Builder role; the bridge
counterpart is always Loyal Opposition. The role map records a role SET per harness ID (singleton lists for
multi-harness mode, multi-element lists for single-harness mode). Switching
an ACTIVE harness to Prime Builder updates that harness's role set; other
active harnesses holding operating roles are preserved. The single-active-per-role
invariant is obsolete: multiple active harnesses may hold the same operating
role concurrently (e.g., coexisting Prime Builder or Loyal Opposition
harnesses). Inactive harnesses (registered or suspended) retain their existing
role sets unchanged: role, lifecycle status, event-firing capability, and
headless dispatchability are orthogonal axes per the role/status/dispatchability
model in `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`,
`DELIB-20263438`, and `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3.

**Not to be confused with:** dispatchability. A harness may hold an operating
role without being eligible to receive headless bridge dispatch for that role.
Dispatch eligibility and final target ranking are controlled by
`config/dispatcher/rules.toml`.

**Canonical alias:** operating role.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#role-assignment).*

### bridge thread

**Definition:** The multi-version conversational unit between Prime Builder
and Loyal Opposition on a single topic. A bridge thread is identified by a
kebab-case slug and consists of an ordered sequence of versioned files
(`bridge/<slug>-001.md`, `-002.md`, â€¦) plus a single entry in
the dispatcher-backed bridge state. The thread terminates at `VERIFIED`,
`WITHDRAWN`, or `SUPERSEDED`. `BLOCKED` opens a thread with the typed refusal a
headless session returns when the parent project is not authorized at filing
time; it continues only when Prime Builder files `NEW` or `WITHDRAWN`.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#bridge-thread).*

### GO / NO-GO / NOT-READY / VERIFIED

**Definition:** The Loyal Opposition verdicts in the file-bridge protocol.
`GO` approves a `NEW` or `REVISED` proposal for implementation. `NO-GO`
rejects a proposal and requires a `REVISED` proposal. `NOT-READY` rejects an
implementation report (`READY`) and requires a corrected `READY` report; report
rejection is never `NO-GO`. `VERIFIED` is dated evidence that an implementation
report has been verified against the linked specifications, and is terminal.
`NEW`, `REVISED`, and `READY` are the upstream Prime-side statuses. The code of
record is `TRANSITIONS` in `groundtruth_kb.bridge.vocabulary`.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#go-no-go-verified-deferred).*

### VERDICT-REJECTED

**Definition:** A Prime Builder-authored bridge status that rejects a
governance-noncompliant, Prime-addressed Loyal Opposition verdict (`GO`,
`NO-GO`, or `NOT-READY`) and routes a fresh Loyal Opposition correction. It is
Loyal-Opposition-actionable and may never follow `VERIFIED`, `WITHDRAWN`,
`SUPERSEDED`, or `ADVISORY`.

**Not to be confused with:** `NO-GO` and `NOT-READY` (Loyal Opposition
rejections of a proposal or a report); `WITHDRAWN` (Prime Builder closing its
own proposal before `GO`); an advisory disposition (which stays under
`ADVISORY`, since an advisory carries no verdict to reject).

**Source:** `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001`; code of record
`TRANSITIONS` and `PRIME_AUTHORED_STATUSES` in `groundtruth_kb.bridge.vocabulary`.

### Loyal Opposition advisory

**Definition:** A Loyal-Opposition-initiated bridge entry that delivers an advisory
recommendation to Prime Builder, distinct from a Prime-initiated proposal.
An LO advisory is filed at `bridge/<slug>-001.md` with status `ADVISORY`
and a `bridge_kind: loyal_opposition_advisory` header. It tasks
Prime Builder with filing a normal implementation proposal that converts the
advisory into scoped, testable GT-KB work.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#loyal-opposition-advisory).*

### applicability preflight

**Definition:** The mandatory mechanical bridge gate that checks a bridge
proposal/report's `Specification Links` section against
`config/governance/spec-applicability.toml` for cross-cutting specs triggered
by the proposal's path or content. The gate emits a packet hash that LO
verdicts cite. Returns `preflight_passed: false` when required cross-cutting
specs are missing.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#applicability-preflight).*

### clause preflight

**Definition:** The mandatory companion preflight that asks, for each
ADR/DCL clause registered in `config/governance/adr-dcl-clauses.toml`,
whether the bridge proposal/report shows evidence satisfying the clause.
Emits an exit-5 blocking gate when any `must_apply` clause with both
`severity = "blocking"` and `enforcement_mode = "blocking"` lacks satisfying
evidence and is not explicitly owner-waived.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#clause-preflight).*

### bridge compliance gate

**Definition:** A `PreToolUse` Write hook
(`.codex/hooks/bridge-compliance-gate.py`) that fails the Write of bridge
proposals/reports lacking required protocol elements. Currently enforces the
`Owner Decisions / Input` section requirement when the proposal/report
depends on owner approval.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#bridge-compliance-gate).*

### scanner-safe-writer

**Definition:** A credential-scan PreToolUse hook that scans Write/Edit
content against the canonical credential catalog
(`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) and blocks writes
containing credential-shaped spans. The hook applies to direct Write/Edit
tool calls; helper scripts that bypass the Write tool require their own scan
implementation. Two registered safety-gate hooks implement this surface:
`.codex/hooks/credential-scan.py` (general-purpose, all Write/Edit targets)
and `.codex/hooks/scanner-safe-writer.py` (bridge-scoped, Write-only for
`bridge/*.md` files). Both are registered in each registered harness's tracked
PreToolUse hook-registration surface.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#scanner-safe-writer).*

### owner-decision tracker

**Definition:** A `Stop`-mode hook
(`.codex/hooks/owner-decision-tracker.py`) that detects prose decision-ask
patterns in agent output and refuses turn-end when no `AskUserQuestion` tool
call occurred in the same turn. Records detected questions in
`memory/pending-owner-decisions.md`.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#owner-decision-tracker).*

### prose decision-ask pattern

**Definition:** A pattern class (regex-detectable) in agent output that
resembles asking the owner for a decision in prose rather than via
`AskUserQuestion`. The owner-decision tracker's `PROSE_DECISION_PATTERNS`
constant defines the patterns. When detected without an accompanying
`AskUserQuestion` call in the same turn, the tracker blocks turn-end.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#prose-decision-ask-pattern).*

### AskUserQuestion

**Definition:** The harness-provided owner-decision tool that presents a structured question to
the owner with 2-4 mutually-exclusive options, producing a clickable popup
that captures the answer inline. Per the AUQ-only enforcement stack, this
is the only valid channel for collecting owner decisions in scope
(approvals, waivers, priority choices, formal artifact approvals,
requirement clarifications, destructive actions, deployments, blocking
owner decisions).

**Canonical alias:** AUQ.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#askuserquestion).*

### operating model

**Definition:** The canonical operating-model artifact for GT-KB at
`.codex/rules/operating-model.md`. Carries rule-cited soft authority:
cited by `.codex/rules/loyal-opposition.md` and `AGENTS.md` as the
operating-model reference; its terminology and framing are the alignment
baseline for future remediation work. No hook or test mechanically enforces
compliance with this artifact's text.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#operating-model).*

### operating role

**Definition:** The resolved behavior role for a GT-KB session or harness
context. Interactive sessions resolve from an owner-declared session-stated
role when present, otherwise from the dispatcher/default role metadata recorded
for the active harness ID in `harness-state/harness-registry.json`. Canonical
values are `prime-builder` (implementing authority) and `loyal-opposition`
(reviewing authority). The legacy value `acting-prime-builder` is READ-accepted
for backward compatibility but SET-rejected (cannot be assigned as a new role)
per the Acting-Prime Compatibility Contract.

**Canonical alias:** resolved session role; harness role; dispatcher/default role when specifically referring to registry fallback or headless dispatch routing.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#operating-role).*

### session lane

**Definition:** A non-authority work classification used to organize the
current session's focus, distinct from the operating role. Lanes inherit
authority from the current operating role; they do not grant new permissions
or change the dispatcher/default role assignment. Examples: research, architecture,
implementation, quality engineering, operations/release, documentation,
governance stewardship.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#session-lane).*

### session focus

**Definition:** The owner-facing startup selection that the active AI
harness presents at the start of a Prime Builder session. The selection
binds the session to a specific work item or focus area for the duration
of the session. Distinct from session lane (classification) and operating
role (authority).

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#session-focus).*

### work subject

**Definition:** The startup-payload concept that names the active subject
area of a session: `gtkb_infrastructure` (the default; owner direction
interpreted as GroundTruth-KB platform work) or `application` (owner
direction interpreted as work on a named adopter/demo application). The
work subject is recorded in `.codex/session/work-subject.json` and is set
by owner commands at session start.

**Canonical alias:** active work subject.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#work-subject).*

### session-stated role

**Definition:** A transcript-defined role declared by the owner via the
canonical init keyword `::init gtkb (pb|lo)` on an interactive owner prompt. It
overrides dispatcher/default role metadata for in-session surfaces â€” SessionStart
disclosure rendering, the AXIS 2 harness-native surface filter, the
workstream-focus menu shape, MemBase `changed_by` attribution, and AUQ-keyed
routing â€” for the rest of the contiguous interactive context. It persists
across compaction, resume, and contiguous SessionStart-like boundaries until
the owner explicitly changes it. Runtime marker files such as
`.codex/session/active-session-role.json` and per-session `role-*.json` files
are cache/state only and carry no dispatcher/default role authority; the legacy
single-file marker may be invalidated at SessionStart, but the transcript-defined
interactive role persists through the per-session marker/envelope authority.

**Canonical alias:** interactive session role; session-scoped role.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#session-stated-role).*

### `::init` session marker

**Definition:** A first-line marker caught by a hook. It triggers pre-loading of the
role-related and process-related skills, tools, and reference information a GT-KB
session needs to execute foundational tasks and to locate further tools. Subject
vocabulary `{gtkb, application}` is mandatory; role vocabulary `{pb, lo}` is optional.

**Paired marker:** `::wrap`, also caught by a hook, triggers harvest of the durable
information produced during the session before its context is lost. Harvested
information updates canonical source-of-truth artifacts.

**Source:** owner directive, 2026-08-13.

### smart poller

**Definition:** A retired bridge-poller automation that scanned the legacy
bridge index periodically and dispatched a harness when a recipient's
actionable queue signature changed. Retired, along with every dispatch
substrate that succeeded it. Bridge dispatch is now **manual owner
assignment**; see `dispatcher` below.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#smart-poller).*

### dispatcher

**Definition:** The mechanism by which bridge work is assigned to a harness.
There is currently **no automated dispatcher**: the owner assigns bridge work
manually.

**Dispatcher Next** is the single future dispatcher. It is an active
pre-release objective and is not yet activated. Until then, no script,
scheduled task, hook, or poller may act as a dispatcher, and none may be
described as one.

**Not to be confused with:** any retired dispatch mechanism. Where older
artifacts describe an automated dispatcher, a dispatch trigger, or dispatch
health and topology surfaces, they describe removed mechanisms and carry no
current authority.

**Source:** owner directive, 2026-08-16 (legacy dispatcher disabled and being
purged); `.codex/rules/bridge-essential.md` § Operational Mode.

### role set

**Canonical alias:** role-set; dispatcher role set.

**Definition:** The wire form of a harness's dispatcher/default role assignment
recorded in ``harness-state/harness-registry.json``. The role set
is a JSON list of role tokens drawn from ``{prime-builder, loyal-opposition}``.
Singleton lists represent the multi-harness case (one role per harness ID);
multi-element lists represent the single-harness case (one harness ID holds
both roles). In-process, role sets are represented as Python ``frozenset[str]``
constructed by ``_normalize_role_field`` in ``scripts/harness_roles.py``.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#role-set).*

### single-harness operating mode

**Canonical alias:** single-harness operating mode; single-harness topology;
single-harness install.

**Definition:** A GT-KB deployment topology in which a single AI coding
harness is installed and holds a multi-element role set
``["prime-builder", "loyal-opposition"]``. The single harness absorbs both
Prime Builder and Loyal Opposition responsibilities; bridge dispatch is
provided by the retired scheduled bridge worker (per
``SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001``) rather than the cross-harness
event-driven trigger. Single-harness operating mode is first-class architecture,
not a degradation of the multi-harness topology.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#single-harness-operating-mode).*

### retired scheduled bridge worker

**Canonical alias:** single-harness dispatcher; dispatcher (in single-harness
topology context).

**Definition:** The bridge dispatch substrate that operates in single-harness
operating mode. A host-platform scheduled task (Windows Task Scheduler /
launchd / cron per ``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001``) wakes
the dispatcher routine on a fixed interval. The dispatcher reads
bridge state, computes a per-role actionable signature, and
spawns subprocess workers for each role whose actionable signature has
changed. Workers receive the canonical init keyword ``::init gtkb <mode>``
as the prompt's first line plus the ``GTKB_BRIDGE_POLLER_RUN_ID`` and
``GTKB_BRIDGE_DISPATCH_KEYWORD`` env vars.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#single-harness-bridge-dispatcher).*

### OS poller

**Definition:** The retired bridge-poller class (Windows scheduled tasks
`AgentRedFileBridgeIndexScan-*`, `AgentRedBridgeLivenessAlert`,
`AgentRedPollerLivenessWatcher`; the foreground watchdog; the
`.harness-baseline-configuration/hooks/poller-freshness.py` hook; the in-session `CronCreate`
poller). All members of this class were halted 2026-04-25 per owner
directive because each fixed-interval tick spent an expensive resource â€”
waking a harness into a full investigation â€” unconditionally, with no cheap
deterministic gate (the fixed interval itself was negligibly cheap; the
value/cost defect was the unconditional expensive spawn) â€” and must not be
re-enabled as a substitute for the smart poller.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#os-poller).*

### canonical init keyword

**Canonical alias:** init-keyword; `::init â€¦` family member of **explicit hint**.

**Definition:** The canonical first-line activator syntax for GroundTruth-KB session
envelopes. Regex: `^::init (gtkb|application)( (pb|lo))?$`. First-line-only. Subject
vocabulary `{gtkb, application}` is **mandatory**; role vocabulary `{pb, lo}` is
**optional** (pb = Prime Builder, lo = Loyal Opposition). Six valid forms. No synonyms;
strict parse. When the role token is present it may establish the session-stated role;
when absent the durable harness role from `harness-state/harness-registry.json` applies
without writing `.codex/session/active-session-role.json`.

**Source:** `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3; `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`; `DCL-SESSION-ROLE-RESOLUTION-001`.

**Implementation pointer:** SessionStart hooks; `scripts/session_self_initialization.py`; cross-harness dispatch emitters.

### doctor

**Definition:** The GT-KB diagnostic surface (typically invoked as
`gt platform doctor` or equivalent) that runs structured health checks
against platform infrastructure: bridge state,
scaffold drift, KB integrity, dashboard reachability, and other configured
checks. The doctor is the canonical predicate for several rule-cited
conditions.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#doctor).*

### release manifest

**Definition:** A versioned enumeration of the deployable components that
constitute a tagged release of the GT-KB platform or a hosted application.
The manifest accompanies the release tag and identifies constituent
component versions so that the release can be reproduced, rolled back, or
audited.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#release-manifest).*

### deliberation harvest

**Definition:** The DA write-side pipeline that captures session content
(LO reports, bridge threads, post-implementation reports, owner decisions)
into the Deliberation Archive table in MemBase plus the ChromaDB semantic
index. Runs as part of session wrap.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#deliberation-harvest).*

### explicit hint

**Canonical alias:** explicit-hint; `::` first-line token family.

**Definition:** An inline, first-line-only, `::`-prefixed token that steers the
current session's stance (role, scope, activity, wrap/lifecycle, or routing) through
harness hooks and priority directives. Explicit hints are a **context-management /
progressive-disclosure** mechanism â€” not skills and not free-form prose commands.
Grammar is strict: the token MUST occupy the entire first non-blank line; vocabulary
is closed per hint family; parse failures are rejected or ignored conservatively per
family spec.

**Member families (non-exhaustive closed sets per family spec):**

- **Init-keyword family** â€” `::init (gtkb|application)( (pb|lo))?$` per
  `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3.
- **Wrap-keyword family** â€” `::wrap` per `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001`.
- **Activity open/close family** â€” `::open <activity>` and `::close` or
  `::close <activity>` over the closed activity vocabulary
  `{ops, deliberation, build, test, spec, project}` per
  `SPEC-TOPIC-ENVELOPE-ROUTER-001` / `DCL-TOPIC-ENVELOPE-ROUTING-001`.

**Authority limits:** Explicit hints MUST NOT bypass bridge GO gates, durable or
session-stated role authority, owner-approval gates (`AskUserQuestion` evidence),
work-subject boundaries, or project authorization requirements.

**Source:** `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET`;
`DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`; WI-4482;
`bridge/gtkb-wi4482-explicit-hint-context-management-umbrella-001.md`.

**Implementation pointer:** `.codex/hooks/*` init/ wrap/ topic-router surfaces;
`groundtruth_kb.session.topic_router`; `config/agent-control/activity-disposition-profiles.toml`.

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

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#formal-artifact-approval-packet).*

### canonical artifact

**Definition:** An artifact that has been formalized into MemBase or a
protected narrative-authority file with matching
formal-artifact-approval-packet evidence. Includes MemBase rows for GOV /
ADR / DCL / PB / SPEC / REQ types, Deliberation Archive records, and the
protected narrative artifacts at `.codex/rules/*.md`, `AGENTS.md`,
`CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`,
`applications/<name>/CLAUDE.md`,
`applications/<name>/CLAUDE-REFERENCE.md`, and
`applications/<name>/CLAUDE-ARCHITECTURE.md`. Canonical artifacts are subject to append-only
versioning discipline.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#canonical-artifact).*

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

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#interrogative-default).*

### specify-on-contact

**Definition:** Governance principle (CLAUDE.md governance index entry
GOV-06): when previously unspecified code is touched, it becomes
controlled. Mirrored at the terminology layer by
`DCL-CONCEPT-ON-CONTACT-001`. Touching a code surface that lacks a
specification triggers specification creation; touching a load-bearing
concept that lacks a glossary entry triggers glossary promotion (per the
DCL).

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#specify-on-contact).*

### assertion category

**Definition:** One of four classifications produced by `scripts/assertion_categorize.py` for currently-failing assertions: `genuine_drift`, `chronic_noise`, `flaky`, `healthy`. Categorization is deterministic inference over `assertion_runs` history; outputs are read-only at `.gtkb-state/assertion-triage/categories/<assertion_id>.json`.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#assertion-category).*

### genuine_drift

**Definition:** Assertion category indicating: latest run FAIL, prior PASS streak (default >=2 consecutive PASS runs), transition within configurable window (default 7 days). Drift detection per SPEC-1662 (GOV-18). Highest-priority assertion-triage category.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#genuinedrift).*

### chronic_noise

**Definition:** Assertion category indicating: all available recent runs FAIL, count meets configurable threshold (default 5; the SPEC-default 50 becomes reachable once the `assertion_runs` retention cap is widened). Candidate for retirement-or-accept owner decision per GOV-15 (test fix gate).

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#chronicnoise).*

### flaky

**Definition:** Assertion category indicating: recent runs window includes both PASS and FAIL with at least one transition. Flag for test-quality repair, NOT for retirement.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#flaky).*

### advisory-router

**Definition:** A source-read-only, MemBase-mutating Python service that scans
bridge `ADVISORY` entries and creates one `work_items` row per unhandled advisory under
`GOV-STANDING-BACKLOG-001` authority. Service contract: idempotent on rerun, never
modifies source advisory entries, uses `origin='hygiene'` and
`source_spec_id='GOV-STANDING-BACKLOG-001'`.

**Canonical alias:** advisory backlog router.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#advisory-router).*

### benchmark

**Definition:** A read-only, deterministic GT-KB measurement script that computes one or more metrics over project artifacts (MemBase rows, bridge files, advisory reports, assertion run history) and emits structured output (JSON + markdown summary) to `.gtkb-state/benchmarks/<run_id>/`. Each benchmark is a standalone module exposing a `run(window_start, window_end, project_root) -> BenchmarkResult` entry point; results are idempotent for fixed inputs. Distinct from MemBase mutation: benchmarks observe state and write only to runtime evidence directories, never to canonical tables.

**Canonical alias:** measurement script; metric collector.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#benchmark).*

### linkage heat map

**Definition:** A 5x5 matrix benchmark output that scores cross-artifact reference rates between five GT-KB artifact classes (specifications, tests, work_items, deliberations, bridge threads). Each cell records the count of from-class entries that cite to-class entries within a configured time window. Used to detect under-linkage (e.g., specifications without test coverage citations) and over-coupling (e.g., work_items with excessive cross-class fanout).

**Canonical alias:** cross-artifact linkage matrix.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#linkage-heat-map).*

### advisory latency

**Definition:** A benchmark output that measures the elapsed time between Loyal Opposition advisory creation (bridge `ADVISORY` entry filing) and Prime Builder action on the advisory (conversion proposal filing, rejection deliberation, or owner-decision capture). Expressed as a per-advisory duration plus aggregate dimensions (median, p90, count by classification state). Used to detect advisory backlog accumulation and slow-path advisory handling.

**Canonical alias:** advisory-to-action latency; advisory turnaround time.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#advisory-latency).*

### metric snapshot

**Definition:** The atomic output unit produced by a single benchmark run. A snapshot is a `BenchmarkResult` dataclass instance carrying: `run_id`, `benchmark_id`, `window_start`, `window_end`, `value`, `dimensions` (dict of named axes), `source_commit` (git HEAD at run time), `source_query` (the parameterized query used), and `generated_at` (UTC ISO timestamp). Multiple snapshots from one benchmark run are written together as JSON to `.gtkb-state/benchmarks/<run_id>/<benchmark_id>.json` with a markdown summary at `<run_id>/<benchmark_id>.md`.

**Canonical alias:** benchmark result; measurement snapshot.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#metric-snapshot).*

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
a drift defect â€” the doctor will eventually flag it.

---

## Expected Glossary Artifact Terms (MEMBASE-4-CLAUDE.md full set)

These terms come from the full `MEMBASE-4-CLAUDE.md` glossary. Projects
adopting GT-KB inherit them.

### Artifact Types

| Term | Table | Summary |
|------|-------|---------|
| Specification | `specifications` | Business requirement with decision log structure |
| Test | `tests` | Testable assertion with PASS/FAIL semantics |
| Test Plan | `test_plans` | Orchestrating artifact â€” ordered phases with gate criteria |
| Work Item | `work_items` | Classified unit of work (origin + component) with stage lifecycle |
| Backlog Snapshot | `backlog_snapshots` | Point-in-time snapshot of open WIs |
| Operational Procedure | `operational_procedures` | Repeatable process (deploy/verify/audit) |
| Document | `documents` | General-purpose project knowledge under change control |
| Environment Config | `environment_config` | Environment-specific values under change control |

### Supporting Records

| Term | Table | Summary |
|------|-------|---------|
| Assertion Run | `assertion_runs` | Historical assertion execution record |
| Session Prompt | `session_prompts` | Structured handoff message for next session (the persisted record of a handoff prompt â€” see "handoff prompt") |

### Concepts (not tables)

| Term | Summary |
|------|---------|
| Assertion | Machine-verifiable check attached to a specification (grep/grep_absent/glob) |
| Phantom Artifact | Concept referenced as tracked entity with no backing storage |
| Orchestrating Artifact | Composes other artifacts by reference only (no content duplication) |
| Governance Principle | Process rule (GOV-\*) governing human-AI team collaboration |
| Protected Behavior | Spec with `type = 'protected_behavior'` + must-always-pass assertions |
| Append-Only Change Control | Versioning discipline â€” no UPDATE, no DELETE |
| Session Handoff | Mechanism for storing context for the next session |
| Specify on Contact | GOV-06 â€” touching unspecified code brings it under control |
| Audit Session | Every Nth session auto-flagged for fresh-context integrity review |

---

## Project-specific Terminology

Add project-specific canonical terms here (keep ADR-0001 core vocabulary
above intact):

<!-- Add your project-specific terms below. Use the same structure:
Term, definition, not-to-be-confused-with, source, implementation pointer. -->

### ollama

**Definition:** The fourth GT-KB coding harness (identity `D`), adopted in
Phase 1 of `PROJECT-GTKB-OLLAMA-INTEGRATION`. The upstream Ollama platform
CLI/server (`http://localhost:11434`) is local-capable, but the GT-KB harness
currently routes all skills to cloud model ids via `routing.toml` (in api-harness)
(current route: `kimi-k2-7-code-cloud` â€” cloud-backed, not local inference).
Integrated through `scripts/ollama_harness.py` (a framework-free Python
tool-calling shim) and `routing.toml` (in api-harness) (static routing).

**Canonical alias:** ollama harness.

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#ollama).*

### routing.toml

**Definition:** The static TOML routing config at `routing.toml` (in api-harness). Maps
harness skills to model ids within the Ollama harness's routing configuration.
The current default route (`kimi-k2-7-code-cloud`) is cloud-backed via cloud
API, not a locally-served Ollama model; the upstream Ollama platform CLI/server
remains local-capable but is not the active inference endpoint for GT-KB
dispatch. Schema per `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (`schema_version`,
at least one `[models.<key>]` table, a `[routing]` table with `default_model`).

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#routingtoml).*

### task-to-model routing

**Definition:** The GT-KB pattern binding skill/task contexts to specific models
within a single harness's model pool. In Phase 1 this is expressed via
`routing.toml` (in api-harness) (`[routing].default_model`, with optional
`[routing.skills]` overrides reserved for Phase 2+).

*Full entry â€” alias, disambiguation, source, implementation pointer â€” in [`canonical-terminology-detail.md`](../../groundtruth-kb/docs/reference/canonical-terminology-detail.md#task-to-model-routing).*

## Doctor Contract

The `gt project doctor` command verifies that this file and the startup-
visible surfaces (CLAUDE.md, AGENTS.md, MEMORY.md) contain the canonical
terms required for the project's profile. Missing canonical terms are
ERROR-level; minor drift is WARN-level. See
`.codex/rules/canonical-terminology.toml` for the required-terms matrix.

---

### Worker-role provenance

**Source:** scripts/_kb_attribution.py; groundtruth-kb/src/groundtruth_kb/session/envelope.py L424-464; WI-5010; DELIB-202667078.

Worker-role provenance is the validated role attestation that an **open session envelope** provides. It is not an environment variable, a harness registry role, or a marker file. The changed_by field on MemBase writes (e.g., backlog add-work-item) resolves worker-role provenance by reading the open session envelope worker_role_provenance block, which is populated at envelope-open time from the init keyword resolved role.

An env var like GTKB_SESSION_ID tells the CLI *which* session envelope to read, but it does not *provide* provenance — only the open envelope document does. If resolve_changed_by fails with current session id is missing or does not match, the fix is to open a session envelope, not to set more env vars.

### Unclassified mutation class

**Source:** scripts/bridge_applicability_preflight.py L64 (TARGET_PATH_RE); scripts/implementation_authorization.py target-path classification.

When a target_paths entry matches no classifier rule in bridge_applicability_preflight.py, it is classified as unclassified. Paths classified as unclassified may cause implementation_authorization.py begin to fail if they fall into a protected scope that the classifier did not match. To resolve, refine the glob pattern to match a known classified sub-pattern (e.g., .../**/*.md -> governance_evidence rather than .../**).

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
