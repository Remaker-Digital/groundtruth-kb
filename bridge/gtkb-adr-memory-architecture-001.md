# GT-KB ADR — Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** gtkb-adr-memory-architecture
**Target repo:** `groundtruth-kb` (MemBase insertion target); bridge protocol via Agent Red's `bridge/`
**Proposed artifact:** `spec` with `type='architecture_decision'`, next unused `ADR-NNNN` ID

## Summary

Propose formalizing the three-tier memory architecture that has been implicit
in GT-KB's code (`intake.py`'s capture → confirm split, the existence of
ChromaDB-backed deliberations alongside typed specs) but never named as a
canonical vocabulary. Owner and Codex ratified the terminology in S297
working-process conversation on 2026-04-17. This ADR records the decision
and makes the boundaries enforceable.

Once inserted into GT-KB's MemBase, this ADR becomes the governing
architectural reference for:

- The `/gtkb-spec-intake` skill's confirm-before-mutate contract (Tier A bridge)
- `/gtkb-bridge-propose` and `/gtkb-decision-capture` skill designs
- Downstream DCL-* constraints that enforce promotion boundaries
- Adopter-facing documentation vocabulary (docs sweep bridge will follow)

## Context

GT-KB currently operates three distinct memory layers without a shared name:

1. **A typed, versioned spec store** — `groundtruth.db` holds 9 artifact types
   (specs, WIs, tests, procedures, documents, decisions, deliberations, phases,
   plans). Access via `tools/knowledge-db/db.py`. Canonical truth.

2. **A deliberation archive with vector search** — ChromaDB-backed (6990
   chunks as of S282), append-only with content_hash dedup. Stores bridge
   dialogues, LO reports, owner decisions, rejected alternatives. Evidence,
   not truth.

3. **Markdown operational notes** — `memory/MEMORY.md` (harness-auto-loaded)
   plus topic files (`memory/feedback_*.md`, `memory/project_*.md`). Mixed
   content: current-work state, snapshots of (1), prose projections of (2),
   pinned lessons, strategic documents.

The boundary between (1) and (2) is already operational — `intake.py`'s
`capture_requirement()` writes deliberations; `confirm_intake()` writes specs.
Owner confirmation gates the DA→MemBase promotion.

The boundary between (3) and the other two has been unclear. `MEMORY.md` is
30+ KB, contains version numbers (MemBase-authoritative), session narrative
(DA-evidentiary), feedback indexes (pointers), and current-focus notes
(operational). This mixing:

- Exceeds the 24.4 KB harness auto-load limit (current warning: only part loaded)
- Makes it ambiguous what is authoritative vs advisory in `MEMORY.md`
- Creates drift risk: when versions update in MemBase, `MEMORY.md` becomes stale
- Leaves adopters without a clean mental model for managing memory

Owner statement of intent (2026-04-17, captured as owner-conversation deliberation):

> *MEMORY.md should be a notepad for managing and organizing ad hoc work tasks.*

Codex concurrence (2026-04-17, same thread):

> *MemBase is authoritative... Deliberation Archive is evidentiary... MEMORY.md
> is human/agent notepad for live task organization, session handoff, current
> focus, scratch state. MEMORY.md can coordinate work, but it cannot make
> anything true.*

## Decision

### Three-tier memory architecture

| Tier | Role | Authority | Primary Storage | Mutation |
|------|------|-----------|-----------------|----------|
| **MemBase** | Curated specifications, knowledge, decisions, work items, traceability | **Authoritative** — may drive build, test, deploy, verify | `groundtruth.db` (SQLite) | Append-only versioned (`UNIQUE(id, version)`), governance-constrained |
| **Deliberation Archive (DA)** | Indexed, searchable working-process evidence: chats, bridge docs, LO reports, rationale, rejected alternatives, unresolved questions | **Evidentiary** — cites, searches, contextualizes; does not assert truth | `groundtruth.db` deliberations table + ChromaDB vector index | Strictly append-only, content-hash deduped, redaction-applied |
| **MEMORY.md (operational notepad)** | Ad-hoc work coordination: current focus, blocked items, session handoff, temporary assumptions, active-work scratch state | **Operational / provisional** — may coordinate work, cannot make anything true | `memory/MEMORY.md` markdown (harness-auto-loaded) | Freeform, rewritten as work progresses |

### Canonical rule

> **MEMORY.md can coordinate work, but it cannot make anything true.**

### Promotion pipeline

Ad-hoc content begins in MEMORY.md and promotes outward through governed steps:

```text
Ad-hoc note in MEMORY.md
    ├── evidence / rationale / citation
    │     → Deliberation Archive (via db.insert_deliberation)
    │
    ├── accepted project truth / spec / WI / decision
    │     → MemBase (via intake.confirm_intake or db.insert_spec)
    │       [requires governed intake, classification, approval, or reconciliation]
    │
    ├── implementation coordination
    │     → Bridge proposal / work plan
    │       (bridge file + bridge/INDEX.md entry)
    │
    └── operational procedure
          → docs / runbook / skill / plugin
            (package code, not memory notes)
```

**Critical invariant**: *Nothing in the Deliberation Archive becomes
authoritative until it is promoted into MemBase through a governed intake,
classification, approval, or reconciliation step.*

### MEMORY.md content taxonomy

**MEMORY.md MAY contain:**

- Current work focus ("working on Tier A implementation bridges")
- Blocked items and their reasons
- Session handoff notes ("next session: start with credential-patterns bridge")
- Temporary assumptions in play ("assuming SonarCloud paid plan decision pending")
- Active-work commands or file pointers relevant to the current thread

**MEMORY.md MUST NOT contain (per owner 2026-04-17):**

- Canonical specs (belong in MemBase)
- Durable architecture decisions (belong in MemBase as ADRs)
- Long-term project truth (belong in MemBase)
- Raw chat history (belong in DA)
- Vector-search evidence (belong in DA)
- Deployment records (belong in MemBase or operational logs)
- Secrets or credentials (belong nowhere in this repo; violates SPEC-0058)
- Final verification claims (belong in MemBase via VERIFIED bridges)

### Peer markdown taxonomy — `memory/gt-*.md` namespace

Formalize peer files under a `gt-*` namespace to distinguish GT-KB-managed
projections from user-authored notes or third-party plugin files. All peer
files are **projections** (read-optimized views derived from MemBase or DA);
they are not canonical.

| File | Source of truth | Regenerated when | Role |
|------|----------------|------------------|------|
| `memory/gt-kb-state.md` | MemBase (version, commit, test counts, release) | Session-wrap | Current MemBase snapshot for fast session-start read |
| `memory/gt-sessions.md` | DA (owner-conversation + session-wrap records) | Session-wrap (append) | Narrative session log (append-only, prose) |
| `memory/gt-feedback/*.md` | DA (pinned lessons, curated) | Session-wrap when new lesson surfaces | One file per pinned lesson; stable filenames |
| `memory/gt-strategy/*.md` | MemBase (strategic specs: vision, POR) | When strategy specs update | Projections of strategic MemBase content |

`MEMORY.md` then serves as:

- An **index** pointing to the gt-* peers
- A **current-focus notepad** (the operational tier content above)
- Target size: **well under 24.4 KB** to stay within harness auto-load limit

### Harness alignment

- `MEMORY.md` is the sole harness-auto-loaded file in this tier
- Peer `gt-*.md` files are Read-on-demand
- Third-party plugins/skills use their own scoped directories (not `memory/`)
- User-authored notes at project root or non-`gt-*.md` filenames are respected

## Alternatives Considered

### 1. Single unified memory store (rejected)

Treat all three tiers as one memory. Rejected because:

- Mutation policies differ fundamentally (append-only-versioned vs strictly
  append-only vs freeform rewrite)
- Query interfaces differ (field-based vs similarity-based vs human-reads-file)
- Authorship differs (agent-authored governance vs harvested context vs
  agent/human scratch)
- Quality expectations differ (GOV-18 assertion quality vs redaction-only vs
  no quality gate)
- Conflating them obscures which statements can drive build/test/deploy

### 2. Two-tier model (MemBase + DA, MEMORY.md folded into one) (rejected)

Place MEMORY.md content into either MemBase (as operational specs) or DA (as
session deliberations). Rejected because:

- Operational state is not authoritative (not MemBase-appropriate)
- Operational state is not evidence (not DA-appropriate)
- The harness-auto-load property of MEMORY.md is infrastructurally unique and
  worth preserving as its own tier
- Collapsing creates policy confusion: either MemBase holds provisional
  content (undermines authoritative claim) or DA holds operational state
  (undermines evidentiary claim)

### 3. Different terminology (partially rejected)

Alternatives considered: "KnowledgeBase + WorkingMemory + Notes",
"Truth + Evidence + Notes", "Authoritative + Provisional + Scratch". The
chosen naming (MemBase / Deliberation Archive / MEMORY.md) was selected
because:

- **MemBase** is a distinctive project-owned name that externalizes a
  concept adopters can reason about
- **Deliberation Archive** matches the existing DB table name and vector
  index convention
- **MEMORY.md** is unchanged from harness-native convention
- All three terms are short, pronounceable, and can appear in adopter docs
  without translation

### 4. Hierarchical subdirectories instead of flat `gt-*.md` prefix (deferred)

Alternatives: `memory/gt/feedback/`, `memory/gt/strategy/`, vs flat
`memory/gt-feedback/`, `memory/gt-strategy/`. Deferred — this ADR records the
namespace convention; the docs sweep bridge will decide flat vs hierarchical
based on file count projections. Both are compatible with the taxonomy.

## Consequences

### For Tier A skills

- **`/gtkb-spec-intake`**: the confirm-before-mutate contract is the
  operational expression of the DA → MemBase promotion rule. No change to
  Tier A `-003`'s design; this ADR provides the architectural citation.
- **`/gtkb-bridge-propose`**: bridge proposal files are DA-class
  (evidentiary, working-process). Skill uses standard bridge/INDEX.md
  conventions without touching MEMORY.md.
- **`/gtkb-decision-capture`**: owner decisions go to DA with
  `source_type=owner_conversation`. Promotion to MemBase (if a decision
  creates binding rule/spec) is a separate step.

### For Tier A implementation

- **`gtkb-phase-a-metrics-collector-001`**: its output file location moves
  from `docs/phase-a-skills-metrics.md` (in Tier A `-003`) to
  `memory/gt-phase-a-metrics.md` (gt-* namespace, peer projection). This
  alignment is noted as a minor revision to the metrics bridge scope.
- **`gtkb-hook-scanner-safe-writer-001`**: deny-log if used goes to
  `memory/gt-scanner-deny.log` (projection), not root-level operational noise.

### For adopters (external GT-KB users)

- `gt project init` scaffold should include the `memory/gt-*.md` taxonomy
  pre-populated with adopter-ready templates
- `gt doctor` should verify `MEMORY.md` stays under 24.4 KB and that
  peer files exist
- Adopter docs get three-tier vocabulary anchor (replaces ad-hoc "memory"
  references)

### For DCL-* constraints

This ADR enables future DCL-* derivations:

- **DCL-MEMBASE-NO-SILENT-WRITE**: no automatic spec/WI/ADR/DCL/doc creation
  without owner confirmation (enforces the confirm gate)
- **DCL-DA-APPEND-ONLY**: deliberation table inserts only; no UPDATE or DELETE
  (already true; this makes it a reviewable constraint)
- **DCL-MEMORY-MD-SIZE**: `MEMORY.md` must stay under 24.4 KB (harness limit)
- **DCL-MEMORY-PEER-PREFIX**: GT-KB-managed peer files must use `gt-*` prefix
  to avoid third-party collision

Each DCL is deferred to a separate bridge; this ADR enables them.

### For Agent Red (current project)

- Current `memory/MEMORY.md` (30.6 KB, over limit) is out of compliance
- Current `memory/feedback_*.md` (6 files) should migrate to `memory/gt-feedback/`
- Current `memory/project_*.md` (3 files) should migrate to `memory/gt-strategy/`
- Migration happens in the documentation sweep bridge (separate scope); this
  ADR only establishes the architecture

### Cost

- One-time migration effort for existing projects (Agent Red; docs sweep bridge scope)
- Minor additional Read-calls per session when peer files are needed (on-demand
  loading; offset by smaller MEMORY.md load at session start)
- Adopter learning curve for the three-tier model (offset by clearer mental model)

## Implementation Plan

### Artifact insertion

Insert one MemBase spec record:

```python
db.insert_spec(
    id=f"ADR-{next_unused_id:04d}",
    type="architecture_decision",
    status="verified",  # as post-VERIFIED bridge
    priority="major",
    title="Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)",
    description="<contents of this ADR's Decision section>",
    rationale="<contents of this ADR's Context + Alternatives sections>",
    source_paths=["bridge/gtkb-adr-memory-architecture-001.md"],
    # plus any links to source code:
    # intake.py capture/confirm, db.py deliberation/spec tables
)
```

Exact ID assigned at insertion time based on current max ADR ID + 1.

### Bridge post-impl evidence

- `db.get_spec(id='ADR-NNNN', version=1)` returns the inserted record
- Spec content round-trips (description + rationale fields intact)
- `list_specs(type='architecture_decision')` includes the new ADR

### Downstream coordination

- Tier A implementation bridges (especially `gtkb-phase-a-metrics-collector-001`
  and `gtkb-hook-scanner-safe-writer-001`) cite this ADR's consequences
  sections for file-path conventions
- Documentation sweep bridge (`gtkb-docs-memory-architecture-alignment-001`,
  separate) touches all docs that currently describe memory patterns, aligning
  them to this ADR's vocabulary

## Prior Deliberations

- S297 owner-conversation (2026-04-17): MemBase/DA distinction ratified
- S297 owner-conversation (2026-04-17): MEMORY.md notepad role defined
- S297 owner-conversation (2026-04-17): peer taxonomy scope confirmed (Full ADR selected over Minimal)
- Codex advisory note (2026-04-17): three-layer architecture framework
- `bridge/gtkb-operational-skills-tier-a-002.md` Codex NO-GO (2026-04-17): Finding 3 cites `intake.py`'s capture/confirm as existing operational expression of the decision
- `bridge/gtkb-operational-skills-tier-a-003.md` REVISED: spec-intake contract embedding
- `bridge/gtkb-operational-skills-tier-a-004.md` GO: Tier A scope approval

## Scanner Safety

Pre-flight regex scan against this ADR body: 0 hits. References to test-key
pattern families use descriptive naming ("AR-family API keys", "Anthropic API
keys", "Azure SAS") rather than literal quoted strings.

## Exit Criteria

1. ADR inserted into `groundtruth-kb/groundtruth.db` as `spec` with
   `type='architecture_decision'`, next unused `ADR-NNNN` ID
2. `db.get_spec()` round-trip verifies content intact
3. `list_specs(type='architecture_decision')` includes the new ADR
4. Post-impl bridge references the inserted ADR-NNNN ID
5. Tier A implementation bridges can cite `ADR-NNNN` as a review-gate anchor
6. Documentation sweep bridge can cite `ADR-NNNN` as the canonical vocabulary source

## GO Request

Codex: please review the decision content, alternatives, and consequences.
Specific review targets:

1. **Naming**: is "MemBase / Deliberation Archive / MEMORY.md" the canonical
   set to ship to adopters, or should alternative naming (e.g.,
   "KnowledgeBase", "Working Memory") be considered?
2. **Promotion rule completeness**: does the promotion pipeline cover all
   realistic content transitions, or is there a 5th path I missed?
3. **Peer taxonomy specifics**: are the four proposed peer categories
   (`gt-kb-state.md`, `gt-sessions.md`, `gt-feedback/*.md`, `gt-strategy/*.md`)
   correct, or should additional categories be named (e.g., handoff, metrics,
   doctor-output)?
4. **DCL enablement**: are the four proposed DCL-* constraints appropriate,
   or should this ADR make some of them directly binding vs deferring to
   separate bridges?
5. **Agent Red migration**: should the migration of current
   `memory/feedback_*.md` and `memory/project_*.md` files to the `gt-*`
   namespace be part of the documentation sweep bridge, or a separate
   per-file bridge?

If approved, I will insert the ADR into GT-KB MemBase, file a post-impl
report, then draft the documentation sweep bridge citing the VERIFIED ADR.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
