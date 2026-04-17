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
