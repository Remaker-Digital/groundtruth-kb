# Canonical Terminology — {{PROJECT_NAME}}

This file is the scaffolded glossary of canonical vocabulary for projects built
on GroundTruth KB. It is loaded alongside CLAUDE.md and AGENTS.md at session
start so fresh agent sessions immediately know the project's vocabulary.

**Status:** scaffolded — customize the project-specific rows (marked
`{{PROJECT_NAME}}` or in the per-project section) but DO NOT remove the
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

**Definition:** Scoped implementation work inside the active application
or GT-KB platform. Examples: `GTKB-DASHBOARD-002`,
`GTKB-OPERATING-MODEL-ALIGNMENT-REMEDIATION`. A project is a
workstream/program; not the hosted application.

**Not to be confused with:** application (the lifecycle object;
applications contain projects); platform (GT-KB itself).

**Source:** `.claude/rules/operating-model.md` §2 "project".

### work item

**Definition:** The unit of selectable work in the backlog. Identified
by `WI-NNNN` IDs in MemBase. Carries origin (regression / defect / new),
component, stage, and lifecycle state. Distinct from `backlog_items`
(which is the scheduling+provenance authority); see operating-model.md
§2 for the relationship.

**Not to be confused with:** backlog (the ordered set; see below);
issue or ticket (external-system terms).

**Source:** `.claude/rules/operating-model.md` §2 "work item";
`work_items` table in MemBase.

### backlog

**Definition:** The ordered set of active and candidate work for an
application or platform, organized by priority. Per
`ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, the canonical
implementation is the `backlog_items` table in MemBase, read via
`gt backlog list`.

**Not to be confused with:** ignore list or deprecated work (forbidden
uses per operating-model §2); backlog snapshot (point-in-time export).

**Source:** `.claude/rules/operating-model.md` §2 "backlog";
`GOV-STANDING-BACKLOG-001` (governance contract);
`ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (DB authority).

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
GO, NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN. Both agents read and write the index;
implementation never proceeds without GO.

**Not to be confused with:** "the Bridge" as a generic concept (use
"file bridge" in canonical text); cross-system message bridges.

**Source:** `.claude/rules/file-bridge-protocol.md`;
`bridge/INDEX.md`; `AGENTS.md` (Codex-side rule).

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
