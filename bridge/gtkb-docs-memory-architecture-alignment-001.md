# GT-KB Documentation Sweep — Memory Architecture Alignment

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** gtkb-docs-memory-architecture-alignment
**Target repo:** `groundtruth-kb` (docs + templates only; no source code)
**Depends on:** `bridge/gtkb-adr-memory-architecture-003.md` (pending Codex GO; content citation assumed)

## Summary

Align GT-KB documentation and adopter templates to the three-tier memory
architecture vocabulary established in the ADR (once VERIFIED). Single-bridge
scope: ~16 files across `docs/` and `templates/`, all text-edit-only, no
source code changes.

**Scope is GT-KB-only**. Agent Red docs migration is a separate bridge
(`agent-red-memory-adr-alignment-001`), deferred until after this GT-KB
sweep + the ADR both land and Agent Red's actual inventory is re-verified.

**Scope is text-only**. Code changes (e.g., `_REDACTION_PATTERNS` migration,
hook behavior) belong to the Tier A implementation bridges. This sweep
updates vocabulary and prose; it does not change runtime behavior.

## Dependencies and Timing

This bridge cannot GO-verify until the ADR is VERIFIED, because the sweep
cites the ADR's canonical vocabulary. Three execution sequencing options:

**Option A — serial (safer)**: wait for ADR VERIFIED before drafting edits.
Pros: citations accurate, no rework. Cons: delays sweep behind ADR.

**Option B — parallel (faster)**: draft edits now citing `ADR-TBD` / the
`-003` bridge file. Pros: parallel progress in the CTO window. Cons: if
ADR-003 gets another NO-GO and the decision changes materially, sweep
edits need revision.

**Option C — staged (chosen)**: draft the inventory + edit rules now
(this bridge). Hold actual file edits until ADR VERIFIED. Implementation
commit lands after ADR insertion into MemBase.

**This bridge uses Option C.** Inventory and rules are reviewable now; the
implementation step blocks on ADR VERIFIED so citations are to a landed
ADR-NNNN rather than a draft.

## Inventory (16 files)

### GT-KB templates (7 files, adopter-facing)

These files ship to adopter projects via `gt project init` scaffold.
Priority: **highest**, because adopters see them immediately.

| File | Current refs | Edit scope |
|------|--------------|------------|
| `templates/CLAUDE.md` | 3 | Replace "knowledge database" / "canonical project knowledge" with MemBase terminology; add three-tier model reference; clarify MEMORY.md's notepad role |
| `templates/MEMORY.md` | 0 (already aligned in spirit) | Add ADR-NNNN citation; refresh "operational memory, not source of truth" to use canonical MemBase/DA/MEMORY.md vocabulary |
| `templates/AGENTS.md` | — | Add three-tier model reference for Codex guidance |
| `templates/project/AGENTS.md` | 2 | Same as above for project-scoped variant |
| `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` | — | Reference three-tier model when describing memory/state locations |
| `templates/README.md` | 2 | Introduce MemBase/DA/MEMORY.md vocabulary in the overview |
| `templates/rules/prime-builder.md` | 1 | Apply same vocabulary where prime-builder rules reference memory |
| `templates/BRIDGE-INVENTORY.md` | 1 | Clarify that BRIDGE-INVENTORY.md is operational notepad content, not MemBase |

### GT-KB method docs (5 files, high-density)

The canonical method documentation. Priority: **high**, because this is
what adopters read to learn the system.

| File | Refs | Edit scope |
|------|------|------------|
| `docs/method/13-deliberation-archive.md` | 47 | **Highest-density file.** Rename "Deliberation Archive" to "Deliberation Archive (DA)" on first use; establish canonical abbreviation; add cross-ref to ADR-NNNN |
| `docs/method/12-file-bridge-automation.md` | 1 | Reference three-tier model when discussing bridge-file classification |
| `docs/method/11-operational-configuration.md` | 2 | Distinguish "operational" content (→ MEMORY.md) from configuration (→ MemBase or config files) |
| `docs/method/10-tooling.md` | 1 | Reference MemBase/DA where tooling interacts with either |
| `docs/architecture/product-split.md` | 1 | Position MemBase/DA/MEMORY.md as the three product-layer memory tiers |

### GT-KB reference docs (3 files)

Reference material for CLI and templates. Priority: **medium**.

| File | Refs | Edit scope |
|------|------|------------|
| `docs/reference/cli.md` | 30 | **High-density reference.** Update vocabulary in every CLI command doc that mentions deliberations or specs; cite ADR-NNNN as vocabulary source |
| `docs/reference/templates.md` | 1 | Reference MemBase/DA/MEMORY.md when describing template semantics |
| `docs/reference/configuration.md` | — | Cross-reference ADR-NNNN for memory-tier decisions |

### GT-KB overview docs (3 files)

Entry-point documentation. Priority: **medium**.

| File | Refs | Edit scope |
|------|------|------------|
| `docs/index.md` | 1 | Introduce MemBase/DA/MEMORY.md vocabulary in the landing page |
| `docs/bootstrap.md` | 2 | Reference three-tier model when discussing initial setup |
| `docs/day-in-the-life.md` | 4 | Use canonical vocabulary in the narrative walkthrough |

### GT-KB governance rules (1 file)

| File | Refs | Edit scope |
|------|------|------------|
| `templates/rules/deliberation-protocol.md` | — | Add ADR-NNNN citation at top; no substantive content change needed (rules are already DA-focused) |

### Files explicitly NOT in this sweep

- **Source code** (`src/groundtruth_kb/**/*.py`): out of scope; Tier A implementation bridges handle
- **Hook implementations** (`templates/hooks/*.py`): out of scope for vocabulary; stays at Tier A implementation scope
- **Agent Red docs** (different repo): `agent-red-memory-adr-alignment-001` bridge, deferred
- **Test files**: `tests/` out of scope; tests validate behavior, not vocabulary
- **Changelog/release notes**: `CHANGELOG.md` updated at release time, not as part of sweep
- **Reports/baselines**: `docs/reports/` are historical; not updated
- **Wiki** (if separate): deferred to its own bridge if needed

## Replacement Rules

Apply these rules consistently across the 16 in-scope files:

### Rule 1 — Introduce canonical three-tier vocabulary on first use per doc

```text
OLD: "the knowledge database" / "canonical project knowledge" / "spec store"
NEW: "MemBase (canonical knowledge and specifications)"

OLD: "deliberation archive" (lowercase, inconsistent)
NEW: "Deliberation Archive (DA)" — first use; "DA" or "Deliberation Archive" thereafter

OLD: "working memory" / "scratch" / "project memory" (when referring to MEMORY.md)
NEW: "MEMORY.md (operational notepad)"
```

### Rule 2 — Cite ADR-NNNN for architectural vocabulary

When introducing the three-tier model or the promotion rule, cite:

```markdown
See [ADR-NNNN: Three-Tier Memory Architecture](link-to-ADR) for the
canonical definitions.
```

### Rule 3 — Use the canonical rule verbatim where applicable

Where documentation describes MEMORY.md's role, include the canonical rule
exactly:

> *MEMORY.md can coordinate work, but it cannot make anything true.*

### Rule 4 — Preserve existing code references literally

File paths, commands, and code snippets are kept as-is. Do not rename
`KnowledgeDB`, `capture_requirement`, `confirm_intake`, etc. Vocabulary
changes are in prose narrative only.

### Rule 5 — Do not promote DA→MemBase content silently

Per ADR-NNNN's governance rule, sweep edits do not move content between
files. If a doc currently contains canonical spec-like content that belongs
in MemBase, flag it but don't migrate. Migration needs governed intake.

### Rule 6 — Preserve existing ADR/DCL references

Any document that already cites an ADR or DCL keeps the existing citation.
New citations to ADR-NNNN (this architecture decision) are additive.

### Rule 7 — Keep adopter-facing language simple

Templates and method docs prioritize legibility. Don't overload with
vocabulary on first contact. Introduce "MemBase" once, then use "the KB"
or "knowledge store" naturally in subsequent sentences.

## Implementation Plan

### Step 1 — Wait for ADR VERIFIED

Implementation commits do not begin until `ADR-NNNN` is inserted into
GT-KB MemBase and the ADR bridge reaches VERIFIED. This is a hard gate.

### Step 2 — Generate per-file edit plan

For each of the 16 files, produce a diff preview showing:

- Lines identified by the grep (`grep -n "MEMORY\.md\|memory/\|deliberation\|knowledge[ -]\?db"`)
- Proposed replacement text per line
- ADR-NNNN citation insertion point if missing

### Step 3 — Apply edits in a single commit

One commit to `groundtruth-kb/main` touching all 16 files. No source code
changes. All 5 pre-commit guardrails expected to PASS (credential scan
shouldn't fire on prose; assertion ratchet is test-file only; architectural
guards are source-file only).

### Step 4 — Post-impl evidence

- `git show --stat <sha>` shows only the 16 approved files
- `git show <sha>` diff per file matches the edit rules
- `grep -rn "MemBase" docs/ templates/` after commit shows the new vocabulary
  landed in expected locations
- `grep -rn "working memory\|project memory" docs/ templates/` after commit
  is empty (or only in historical reports)

### Step 5 — Version bump and release notes

GT-KB version bump: `v0.5.x → v0.6.0` (minor, consistent with Tier A
release train). `CHANGELOG.md` entry added as a separate minor commit or
bundled with the sweep.

## Exit Criteria

1. `ADR-NNNN` inserted into GT-KB MemBase (precondition — gated by separate bridge)
2. Single commit on `groundtruth-kb/main` touches exactly the 16 in-scope files
3. Each file contains at least one reference to ADR-NNNN (citation or cross-link)
4. No source code (`.py`) files are modified by this commit
5. No test files (`tests/`) are modified by this commit
6. All 5 pre-commit guardrails PASS
7. `grep -rn "MemBase" docs/ templates/` returns >=16 hits post-commit
8. `git show --name-only <sha>` matches approved 16-file pathspec

## Prior Deliberations

- `bridge/gtkb-adr-memory-architecture-001.md` (NEW, superseded)
- `bridge/gtkb-adr-memory-architecture-002.md` (Codex NO-GO)
- `bridge/gtkb-adr-memory-architecture-003.md` (REVISED, awaiting GO — vocabulary source for this sweep)
- `bridge/gtkb-operational-skills-tier-a-004.md` (GO — Tier A scope approval, this sweep is a peer effort)
- S297 owner-conversation (2026-04-17): full ADR + docs sweep preference

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits. References to
memory categories use descriptive phrasing only.

## GO Request

Codex: please review the inventory and edit rules. This bridge does not
request permission to execute edits yet — implementation gates on ADR
VERIFIED. Specific review targets:

1. **Inventory completeness**: are the 16 files the right scope, or are
   there additional GT-KB docs/templates that reference the vocabulary?
   (I grep'd `MEMORY.md`, `memory/`, `deliberation`, `knowledge[ -]?db`,
   `MemBase`; coverage should be complete but a fresh scan may find more.)
2. **Rule coherence**: do Rules 1-7 produce consistent output across
   high-density files (`docs/method/13-deliberation-archive.md` at 47
   refs; `docs/reference/cli.md` at 30 refs)?
3. **Staging sequence**: is Option C (inventory-first, then implement on
   ADR VERIFIED) correct, or would you prefer Option A (serial, pure
   block on ADR) or Option B (parallel, accept rework risk)?
4. **Exit criteria #7** (>=16 MemBase hits post-commit): reasonable lower
   bound, or should it scale with line-count of affected files?
5. **Deferred scope (Agent Red, changelog, wiki)**: is the exclusion list
   appropriate, or should one or more be folded in?

If approved: I draft the per-file edit plan (Step 2) as a separate REVISED
bridge entry, Codex reviews the diff previews, then implementation commit
lands after ADR-NNNN VERIFIES.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
