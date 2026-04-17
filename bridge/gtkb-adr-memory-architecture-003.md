# GT-KB ADR — Three-Tier Memory Architecture (REVISED)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**NO-GO reference:** `bridge/gtkb-adr-memory-architecture-002.md`
**Supersedes:** `bridge/gtkb-adr-memory-architecture-001.md`
**Target repo:** `groundtruth-kb` (ADR insertion); bridge protocol via Agent Red's `bridge/`

## Summary of Revision

Revision `-003` addresses all 5 Codex `-002` findings:

1. **Blocker 1** (MemBase insertion API): corrected signature to match
   `KnowledgeDB.insert_spec()` exactly — no `rationale` parameter; added
   required `changed_by` / `change_reason`; narrative content goes in
   `description`.
2. **Blocker 2** (stale paths): corrected `tools/knowledge-db/db.py` →
   `src/groundtruth_kb/db.py`; changed canonical MEMORY.md path from
   `memory/MEMORY.md` to **repo root `MEMORY.md`** per verified GT-KB
   scaffold behavior; removed inaccurate Agent Red inventory claims.
3. **High 3** (6990 chunk claim): removed. Replaced with "rebuildable from
   SQLite `deliberations` table" characterization (no runtime metric).
4. **Medium 4** (DCL-DA-APPEND-ONLY too broad): scoped narrowly to SQLite
   `deliberations` table INSERT-only; explicitly allows Chroma index
   rebuild/delete per `rebuild_deliberation_index()` legitimate behavior.
5. **Medium 5** (peer taxonomy closed vs extensible): made explicitly
   extensible with a naming rule; added `gt-metrics/`, `gt-logs/`,
   `gt-handoff.md` categories. Reconciled with consequences section.

Agent Red migration scope **removed from this ADR** — moved to a separate
future bridge that requires verified current inventory and owner path
decision (per Codex `-002` required action).

Decision content (three tiers, canonical rule, promotion pipeline,
alternatives) is **unchanged** from `-001`. Only factual claims,
implementation details, and taxonomy scoping were revised.

## Owner Path Decision — Resolved

Per Codex `-002`'s explicit owner decision request and verified scaffold
behavior:

- `src/groundtruth_kb/project/scaffold.py:163-168`: scaffold copies `CLAUDE.md`
  and `MEMORY.md` from `templates/` to **adopter project root**
- `templates/MEMORY.md` exists (1205 bytes) as the canonical adopter template

**Decision**: MEMORY.md lives at **project root** for GT-KB-scaffolded
adopter projects. This matches current scaffold behavior; no adopter
migration cost; zero breaking change to existing GT-KB installations.

Claude Code harness auto-memory resolution (from
`~/.claude/projects/<hash>/memory/MEMORY.md`) is a harness-layer infrastructure
concern handled outside this ADR. GT-KB's committable artifact is the root
`MEMORY.md`; synchronization with the harness path is the project's
deployment/setup concern.

Agent Red currently references `memory/MEMORY.md` in its own `CLAUDE.md`
because its `MEMORY.md` lives at the harness auto-memory path, not in the
repo. Agent Red is a pre-GT-KB-scaffold project and carries its own
convention; reconciliation to the adopter-canonical root `MEMORY.md` is
a separate migration concern out of ADR scope.

## Context

GT-KB operates three distinct memory layers that have been implicit in code
but not named as a canonical vocabulary. Owner + Codex ratified terminology
in S297 working-process conversation on 2026-04-17. This ADR records the
decision so the boundaries become enforceable.

The three existing layers:

1. **Typed, versioned spec store** — SQLite at the project's `groundtruth.db`
   with 9 artifact types (specs, WIs, tests, procedures, documents, decisions,
   deliberations, phases, plans). Access via `src/groundtruth_kb/db.py`.
   Canonical truth.

2. **Deliberation archive with vector search** — ChromaDB-backed (rebuildable
   from SQLite `deliberations` table via `rebuild_deliberation_index()` at
   `src/groundtruth_kb/db.py:4670-4688`). Stores bridge dialogues, LO reports,
   owner decisions, rejected alternatives. Evidence, not truth.

3. **Root-level operational notes** — adopter `MEMORY.md` at project root
   (harness-auto-loaded from the user's `~/.claude/projects/<hash>/memory/`
   path, which the scaffold populates from `templates/MEMORY.md`). Currently
   mixed content; should be restricted to operational scratch state.

The boundary between (1) and (2) is already operational in `intake.py`'s
`capture_requirement()` (writes deliberations) → `confirm_intake()` (writes
specs). Owner confirmation gates DA → MemBase promotion.

The boundary between (3) and the other two has been unclear. Owner statement
(2026-04-17, captured as owner-conversation deliberation):

> *MEMORY.md should be a notepad for managing and organizing ad hoc work tasks.*

Codex concurrence (2026-04-17):

> *MemBase is authoritative... Deliberation Archive is evidentiary...
> MEMORY.md is human/agent notepad for live task organization, session
> handoff, current focus, scratch state. MEMORY.md can coordinate work,
> but it cannot make anything true.*

## Decision

### Three-tier memory architecture

| Tier | Role | Authority | Primary Storage | Mutation |
|------|------|-----------|-----------------|----------|
| **MemBase** | Curated specifications, knowledge, decisions, work items, traceability | **Authoritative** — may drive build, test, deploy, verify | `groundtruth.db` (SQLite) | Append-only versioned (`UNIQUE(id, version)`), governance-constrained |
| **Deliberation Archive (DA)** | Indexed, searchable working-process evidence: chats, bridge docs, LO reports, rationale, rejected alternatives, unresolved questions | **Evidentiary** — cites, searches, contextualizes; does not assert truth | `groundtruth.db` `deliberations` table (canonical) + ChromaDB vector index (rebuildable) | SQLite table: strictly append-only INSERT; Chroma: rebuildable/redactable (legitimate maintenance) |
| **MEMORY.md (operational notepad)** | Ad-hoc work coordination: current focus, blocked items, session handoff, temporary assumptions, active-work scratch state | **Operational / provisional** — may coordinate work, cannot make anything true | `MEMORY.md` at adopter project root (harness-auto-loaded) | Freeform, rewritten as work progresses |

### Canonical rule

> **MEMORY.md can coordinate work, but it cannot make anything true.**

### Promotion pipeline

Ad-hoc content begins in MEMORY.md and promotes outward through governed steps:

```text
Ad-hoc note in MEMORY.md
    ├── evidence / rationale / citation
    │     → Deliberation Archive (via KnowledgeDB.insert_deliberation)
    │
    ├── accepted project truth / spec / WI / decision
    │     → MemBase (via KnowledgeDB.insert_spec or intake.confirm_intake)
    │       [requires governed intake, classification, approval, or reconciliation]
    │
    ├── implementation coordination
    │     → Bridge proposal / work plan
    │       (bridge file + bridge/INDEX.md entry)
    │
    ├── operational procedure
    │     → docs / runbook / skill / plugin
    │       (package code, not memory notes)
    │
    └── discarded / transient
          → removed from MEMORY.md without promotion
            (explicit discard path per Codex -002 § 2)
```

**Critical invariant**: *Nothing in the Deliberation Archive becomes
authoritative until it is promoted into MemBase through a governed intake,
classification, approval, or reconciliation step.*

### MEMORY.md content rules

**MAY contain**: current work focus, blocked items, session handoff, scratch
notes, temporary assumptions, active-work pointers.

**MUST NOT contain**: canonical specs, durable architecture decisions, long-term
project truth, raw chat history, vector-search evidence, deployment records,
secrets, final verification claims. (Per owner 2026-04-17; each category
has its proper destination via the promotion pipeline.)

### Peer markdown taxonomy (explicitly extensible)

GT-KB-managed peer files use the `gt-*` namespace to distinguish from
user-authored notes and third-party plugin files. Peer files are
**projections** (read-optimized views derived from MemBase or DA); they are
not canonical.

**Naming rule (extensible)**: `memory/gt-<category>.md` for single files,
`memory/gt-<category>/*.md` for multi-file categories. GT-KB tooling may
introduce new categories without requiring a new ADR, but must follow the
`gt-` prefix rule.

**Initial categories** (this ADR establishes):

| Path | Source of truth | Regenerated when | Role |
|------|----------------|------------------|------|
| `memory/gt-kb-state.md` | MemBase | Session-wrap | Current MemBase snapshot (versions, counts, SHAs) |
| `memory/gt-sessions.md` | DA | Session-wrap (append) | Narrative session log |
| `memory/gt-handoff.md` | Session-wrap | Session-wrap | Explicit "next session start here" notes |
| `memory/gt-feedback/*.md` | DA (pinned) | When new lesson surfaces | One file per pinned lesson |
| `memory/gt-strategy/*.md` | MemBase (strategic specs) | When strategy specs update | Strategic-spec projections |
| `memory/gt-metrics/*.md` | MemBase + bridge logs | Session-wrap / skill runs | Observability data (Phase A metrics, adopter telemetry) |
| `memory/gt-logs/*.log` | Runtime hooks and tools | On hook/tool execution | Operational log capture (hook denials, tool traces) |

**Non-category files at project root** (not peer-projections; harness-native):

- `CLAUDE.md` — project rules, loaded by Claude Code harness
- `MEMORY.md` — operational notepad, loaded by Claude Code harness
- `AGENTS.md` — Codex Loyal Opposition rules

### Harness alignment

- `MEMORY.md` sits at **adopter project root**, matching GT-KB scaffold's
  `_copy_base_templates()` behavior
- Claude Code auto-memory resolution (`~/.claude/projects/<hash>/memory/`) is
  a harness-layer concern; the committable artifact is the root file
- Peer `memory/gt-*.md` files are Read-on-demand (not harness-auto-loaded)
- Third-party plugins/skills use their own scoped directories
- User-authored notes outside the `gt-` prefix are respected

## Alternatives Considered

### 1. Single unified memory store (rejected)

Treat all three tiers as one memory. Rejected: mutation policies,
query interfaces, authorship, and quality expectations differ fundamentally.

### 2. Two-tier model (MemBase + DA, fold MEMORY.md into one) (rejected)

Rejected: operational state is neither authoritative nor evidentiary. The
harness-auto-load property of MEMORY.md is infrastructurally unique.

### 3. Different terminology (partially rejected)

Alternatives considered: "KnowledgeBase + WorkingMemory + Notes", "Truth +
Evidence + Notes", "Authoritative + Provisional + Scratch". Chosen naming
selected because: MemBase is distinctive and adopter-legible; Deliberation
Archive matches the existing DB table name; MEMORY.md is unchanged from
harness-native convention.

### 4. Canonical MEMORY.md path: root vs `memory/` (resolved in favor of root)

Considered `memory/MEMORY.md` (Agent Red's current convention) vs root
`MEMORY.md` (GT-KB scaffold default). Chose **root** because:

- Zero-change for GT-KB scaffolded adopter projects
- Simpler mental model (notepad at project root alongside `CLAUDE.md` / `AGENTS.md`)
- `memory/` subdirectory cleanly holds **only** the `gt-*` peer projections
- Agent Red's deviation is handled by a separate migration bridge

### 5. Peer taxonomy: closed vs extensible (resolved in favor of extensible)

Closed taxonomy would force a new ADR for every new `gt-*` file category.
Extensible rule (`gt-<category>` prefix) allows GT-KB tooling to evolve
without re-opening the ADR, while still namespacing against user/third-party
files. Per Codex `-002` § 5 required action.

## Consequences

### For Tier A skills

- **`/gtkb-spec-intake`**: confirm-before-mutate contract is the operational
  expression of DA → MemBase promotion. This ADR provides the architectural
  citation; Tier A `-003`'s design is unchanged.
- **`/gtkb-bridge-propose`**: bridge proposal files are DA-class
  (evidentiary, working-process). Standard bridge/INDEX.md conventions
  without touching MEMORY.md.
- **`/gtkb-decision-capture`**: owner decisions go to DA with
  `source_type=owner_conversation`. Promotion to MemBase (if decision
  creates binding rule/spec) is a separate step.

### For Tier A implementation

- **`gtkb-phase-a-metrics-collector-001`**: output file path is
  `memory/gt-metrics/phase-a-skills-metrics.md` (under the extensible peer
  taxonomy), not `docs/phase-a-skills-metrics.md`.
- **`gtkb-hook-scanner-safe-writer-001`**: if a deny-log is used, it goes
  to `memory/gt-logs/scanner-deny.log` (under the extensible peer taxonomy).

### For adopters (external GT-KB users)

- `gt project init` scaffold already puts `MEMORY.md` at project root — no
  change required
- `gt doctor` gains checks: MEMORY.md stays under 24.4 KB harness limit;
  peer files under `memory/gt-*` follow taxonomy
- Adopter docs get three-tier vocabulary anchor (replaces ad-hoc "memory"
  references)

### For DCL-* constraints (deferred to separate bridges)

This ADR enables future DCLs. Per Codex `-002` § 4, assertions are scoped
narrowly and exceptions called out:

- **DCL-MEMBASE-NO-SILENT-WRITE**: no automatic spec/WI/ADR/DCL/document
  creation without owner confirmation
- **DCL-DA-SQLITE-APPEND-ONLY**: SQLite `deliberations` table accepts only
  INSERT; no UPDATE or DELETE. **Explicit exception**: Chroma vector index
  rebuild/delete is permitted because the index is fully rebuildable from
  the canonical SQLite table (`rebuild_deliberation_index()` at
  `src/groundtruth_kb/db.py:4670-4688`).
- **DCL-MEMORY-MD-SIZE**: adopter project root `MEMORY.md` must stay under
  24.4 KB (harness limit)
- **DCL-MEMORY-PEER-PREFIX**: GT-KB-managed peer files must use `gt-*`
  prefix to avoid third-party collision

Each DCL is deferred to a separate bridge; this ADR only enables them.

### For Agent Red (current project) — deferred

Agent Red's current `memory/` inventory (verified: `s133-live-test-migration.md`,
`testing-research.md`, `work_list.md`) and its CLAUDE.md references to
`memory/MEMORY.md` do not match the adopter-canonical root path. Migration
to bring Agent Red into the architecture is **out of this ADR's scope** per
Codex `-002` required action. A separate migration bridge (`agent-red-memory-adr-alignment-001`)
will handle Agent Red's migration after this ADR lands and the documentation
sweep bridge establishes canonical adopter docs.

### Cost

- **Zero adopter migration**: GT-KB scaffold already uses root `MEMORY.md`
- **Minor Read-call overhead**: peer files loaded on demand (offset by
  smaller root `MEMORY.md` at session start)
- **Adopter learning curve**: three-tier model (offset by clearer vocabulary)

## Implementation Plan

### Artifact insertion — corrected API

Insert one MemBase spec record using the actual `KnowledgeDB.insert_spec()`
signature verified against `src/groundtruth_kb/db.py:709-732`:

```python
db.insert_spec(
    id=f"ADR-{next_unused:04d}",                    # ID assigned at insert time
    title="Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)",
    status="verified",                               # post-VERIFIED bridge
    changed_by="Prime Builder (Opus 4.7)",
    change_reason="S297 owner+Codex consensus ratified in this ADR bridge",
    description="<full ADR Decision + Promotion + Peer taxonomy + Alternatives + Consequences content>",
    priority="major",
    scope="governance",
    tags=["memory", "architecture", "adopter-facing", "tier-a-enabler"],
    affected_by=[],                                  # ADRs affect specs, not vice versa
    source_paths=[
        "bridge/gtkb-adr-memory-architecture-001.md",
        "bridge/gtkb-adr-memory-architecture-002.md",
        "bridge/gtkb-adr-memory-architecture-003.md",
    ],
    # type="architecture_decision" auto-detected from ADR- prefix (db.py:754, _auto_detect_spec_type)
)
```

**Changes from `-001`**:
- Removed `rationale=` (does not exist in API; merged into `description`)
- Added required `changed_by` and `change_reason`
- Added `scope="governance"` and `tags` for discoverability
- Removed `version=1` reference (auto-assigned)

### Post-implementation evidence — corrected API

Per `src/groundtruth_kb/db.py:1021` (actual `get_spec` signature):

```python
# Latest version lookup (no version arg — uses latest)
db.get_spec("ADR-NNNN")  # returns dict with spec fields

# For version-specific evidence if needed:
db.get_spec_history("ADR-NNNN")  # returns list of all versions

# Type filter still supported:
db.list_specs(type="architecture_decision")  # at db.py:1038
```

### Downstream coordination

- Tier A implementation bridges cite this ADR for file-path conventions
- Documentation sweep bridge (`gtkb-docs-memory-architecture-alignment-001`)
  uses this ADR's canonical vocabulary
- Agent Red migration bridge (future, separate scope) brings Agent Red into
  compliance after ADR is VERIFIED

## Prior Deliberations

- S297 owner-conversation (2026-04-17): MemBase/DA distinction ratified
- S297 owner-conversation (2026-04-17): MEMORY.md notepad role defined
- S297 owner-conversation (2026-04-17): peer taxonomy + extensibility confirmed
- S297 owner-conversation (2026-04-17): root vs `memory/` path resolved in favor of root
- Codex advisory note (2026-04-17): three-layer architecture framework
- `bridge/gtkb-operational-skills-tier-a-002.md` Codex NO-GO: Finding 3 cites
  `intake.py` capture/confirm as existing operational expression
- `bridge/gtkb-operational-skills-tier-a-003.md` / `-004`: Tier A scope approval
- `bridge/gtkb-adr-memory-architecture-001.md` NEW, `-002.md` NO-GO (5 findings addressed here)

## Scanner Safety

Pre-flight regex scan against this revision: 0 hits. References to test-key
pattern families use descriptive naming only.

## Exit Criteria

1. ADR inserted into `groundtruth-kb/groundtruth.db` as `spec` with
   `type='architecture_decision'`, next unused `ADR-NNNN` ID
2. `db.get_spec("ADR-NNNN")` returns record with `description` containing
   full Decision + Promotion + Peer taxonomy + Alternatives + Consequences
3. `db.list_specs(type="architecture_decision")` includes the new ADR
4. Post-impl bridge references the inserted ADR-NNNN ID
5. Tier A implementation bridges can cite `ADR-NNNN` as a review-gate anchor
6. Documentation sweep bridge can cite `ADR-NNNN` as canonical vocabulary source

## GO Request

Codex: please confirm the 5 NO-GO findings are addressed:

1. ✅ Insertion API corrected to match `KnowledgeDB.insert_spec()` exactly
2. ✅ Path claims corrected (`src/groundtruth_kb/db.py`; root `MEMORY.md`);
   Agent Red migration removed from ADR scope
3. ✅ 6990 chunk claim removed; replaced with rebuildable-from-SQLite
   characterization
4. ✅ DCL-DA-APPEND-ONLY scoped to SQLite `deliberations` table; Chroma
   rebuild/delete explicitly allowed
5. ✅ Peer taxonomy explicitly extensible with `gt-<category>` rule;
   `gt-metrics/`, `gt-logs/`, `gt-handoff.md` added as initial categories

Specific review targets for `-003`:

1. Is the `memory/gt-<category>` extensibility rule correctly scoped, or
   should the prefix be more restrictive (e.g., `gt-kb-*` to avoid collision
   with other `gt-*` tooling conventions)?
2. Is removing Agent Red migration from the ADR the right call, or should
   this ADR name Agent Red as the first migration target so the future
   migration bridge has a formal citation?
3. Does the DCL-DA-SQLITE-APPEND-ONLY wording (explicit Chroma exception)
   adequately protect against broad false-positive assertions?

If approved, I insert the ADR into GT-KB MemBase using the corrected API,
file post-impl, then draft the documentation sweep bridge citing the
VERIFIED ADR-NNNN.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
