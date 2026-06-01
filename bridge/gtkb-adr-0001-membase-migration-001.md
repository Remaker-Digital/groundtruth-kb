# GT-KB ADR-0001 MemBase Storage-Gap Migration

**Status:** NEW
**Author:** Prime Builder (Opus 4.8)
**Date:** 2026-05-31
**Session:** S379
**Thread:** gtkb-adr-0001-membase-migration
**Bridge file home:** `E:\GT-KB\bridge\gtkb-adr-0001-membase-migration-001.md` (in-root, under `E:\GT-KB\bridge\`)
**Proposed mutation:** one append-only `specifications` row insert (`ADR-0001`, `type=architecture_decision`, `version=1`) into the in-root MemBase `E:\GT-KB\groundtruth.db`

**target_paths:**
- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/2026-05-31-ADR-0001.json`

(Migration helper at `.gtkb-state/migrate_adr0001.py` is operational-tier scratch, not a protected canonical target.)

## Summary

`ADR-0001` "Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)" is cited 57 times across 30 in-root files (rule files, `AGENTS.md`, `MEMORY.md`, skills, scaffold-golden fixtures, release notes) yet has **zero rows** in the in-root MemBase `E:\GT-KB\groundtruth.db`. This is a "cited-but-not-stored" governance hole: phantom-spec sweeps against the live `specifications` table fail for `ADR-0001`, and the rule-cited soft authority it carries is not anchored in the canonical store (GOV-08).

Investigation shows `ADR-0001` is **not an un-formalized concept** — it was authored AND Codex-VERIFIED in S297 (2026-04-17) via the `gtkb-adr-memory-architecture` bridge thread (six versions; `-006` = VERIFIED). The verified row, with a 4920-character description (8 `U+2014` em-dashes), lives only in the **old, now-archived** project root's gitignored MemBase. When the project root moved to `E:\GT-KB` (per `.claude/rules/project-root-boundary.md`, the old location is now "archive only"), the row never migrated — exactly the propagation gap the original verifier flagged as a non-blocking follow-up that was never actioned.

This proposal closes the gap by **migrating the byte-identical verified row** into the in-root MemBase via the formal-artifact-approval packet workflow. It does not re-litigate the S297 architecture decision; the decision content is transferred verbatim.

## Context

### The gap (probed live, not estimated)

- `SELECT * FROM specifications WHERE id='ADR-0001'` against `E:\GT-KB\groundtruth.db` → **0 rows** (all versions).
- `ADR-001` (3-digit) exists with 4 versions ("Per-interface transport dispatch", an Agent-Red-era ADR). `'ADR-0001' != 'ADR-001'` under SQLite string comparison, so there is **no `UNIQUE(id, version)` collision**; the 4-digit padded form is the correct, citation-matching ID.
- 25 distinct `architecture_decision` specs already exist; none names the memory architecture, confirming no alternate-ID row holds this content.

### The verified-but-unmigrated artifact

- `gtkb-adr-memory-architecture-001.md` … `-006.md` (in-root) record the S297 proposal, two NO-GO revisions, GO at `-004`, post-impl report at `-005`, and **VERIFIED at `-006`**.
- `-006` VERIFIED readback (against the old root) shows: `id=ADR-0001`, `type=architecture_decision`, `status=verified`, `version=1`, `title="Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)"`, `priority=major`, `scope=governance`, `tags=["memory","architecture","adopter-facing","tier-a-enabler"]`, `authority=stated`, description length 4920, 8 em-dashes.
- A read-only probe of the archived MemBase recovered that exact row, byte-for-byte, as the migration source.
- `-005` and `-006` both flagged the propagation caveat (`groundtruth.db` is gitignored) and recommended a follow-up; the root relocation made the gap concrete.

### Why migration, not fresh authoring

Owner directed (AskUserQuestion, S379) to **migrate the exact verified content**. The verified body carries nuance the rule-file one-liners do not (the harness auto-memory-path clarification, the 7-category extensible peer taxonomy, the 5th "discarded/transient" promotion path). Faithful migration preserves the owner+Codex-verified decision verbatim.

## Decision: exact row to be inserted

The migration helper reads the archived row programmatically and inserts it into the in-root MemBase. **The `description` field is transferred byte-identically** (preserving all 8 `U+2014` em-dashes); it is NOT retyped from console output (which renders em-dashes as replacement characters). The proposal therefore summarizes the body by section rather than inlining it.

| Field | Value | Provenance |
|---|---|---|
| `id` | `ADR-0001` | byte-identical; matches 57 citations |
| `version` | `1` | first row in the in-root DB (append-only; no prior versions) |
| `title` | `Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)` | byte-identical |
| `type` | `architecture_decision` | byte-identical (GOV-20) |
| `status` | `verified` | per owner AUQ; carries the S297 Codex verification of identical content |
| `priority` | `major` | byte-identical |
| `scope` | `governance` | byte-identical |
| `tags` | `["memory","architecture","adopter-facing","tier-a-enabler"]` | byte-identical |
| `description` | the 4920-char verified body (transferred byte-identically) | byte-identical |
| `assertions` | `None` | byte-identical (this ADR carries no machine assertions) |
| `authority` | `stated` | byte-identical |
| `affected_by` | `None` | byte-identical |
| `testability` | `None` | byte-identical |
| `source_paths` | original 4 bridge files **+ this migration bridge** | provenance enrichment (see Disclosed Deltas) |
| `changed_by` | `prime-builder/S379-adr-0001-membase-migration` | reflects THIS insert event |
| `changed_at` | UTC at insert time | reflects THIS insert event |
| `change_reason` | cites the formal-artifact-approval packet path + S297 verification provenance (`gtkb-adr-memory-architecture-006` VERIFIED) + the cited-but-not-stored gap | reflects THIS insert event |

### Migrated description content (section summary)

The byte-identical 4920-char `description` contains: the three-tier intro (S297 ratification); the three tiers (MemBase = Authoritative; Deliberation Archive = Evidentiary; MEMORY.md = Operational/provisional, with the harness auto-memory-path clarified as an external concern); the canonical rule ("MEMORY.md can coordinate work, but it cannot make anything true"); the 5-path promotion pipeline (including discarded/transient); MEMORY.md MAY/MUST-NOT content rules; the extensible `memory/gt-*` peer taxonomy (7 initial categories); 5 Alternatives Considered with rationale; Consequences (Tier A skills, metrics, hooks, adopters, four enabled DCLs, Agent Red migration deferral); and Bridge History.

### Disclosed deltas from the archived row

Two intentional, disclosed deviations from byte-identical; everything else is verbatim:

1. **Attribution fields** (`changed_by`, `changed_at`, `change_reason`) describe THIS insert event into the in-root DB, not the S297 event into the old DB. Required: these fields describe the act of insertion.
2. **`source_paths`** extends the original four bridge files with this migration bridge, for provenance. Additive metadata, not a content change. If Loyal Opposition prefers byte-identical `source_paths`, that is an acceptable narrowing.

## Specification Links

- `GOV-20` — Architecture Decision Governance: ADRs are stored in MemBase as `type=architecture_decision`; this migration restores `ADR-0001` to that governed store.
- `GOV-08` — Knowledge Database is the single source of truth: the cited-but-not-stored hole is a direct GOV-08 violation this proposal closes.
- `GOV-ARTIFACT-APPROVAL-001` — Formal artifact approval gate: canonical artifact insertion requires an owner-approval packet presenting full content.
- `PB-ARTIFACT-APPROVAL-001` — Protected behavior: canonical artifact writes require approval evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — Approval hook must display the full native proposal/content before canonical insertion.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — Strict formalization gate with scoped auto-approval mode governs ADR insertion.
- `SPEC-2098` — Deliberation Archive (structured storage + semantic search): the DA tier named by `ADR-0001`; confirms the architecture being formalized is implemented.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow state; this proposal is filed under the file-bridge authority model.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals must cite all relevant governing specs (this section).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must derive from linked specs and be executed against the implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — GT-KB root/`applications/` boundary; governs the one-time archived-DB read as a sanctioned relocation source.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — concrete decisions/artifacts preserved durably (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts/reports/decisions (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle states incl. verified (advisory).
- `.claude/rules/file-bridge-protocol.md` — bridge protocol surface and mandatory gates.
- `.claude/rules/codex-review-gate.md` — pre-implementation review requirement for KB mutations.
- `.claude/rules/project-root-boundary.md` — root boundary + the "relocate to in-root home" clause that mandates this migration.
- `.claude/rules/canonical-terminology.md` — the always-loaded read-surface that cites `ADR-0001` (7 occurrences); the primary gap-evidence surface.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed. The architecture decision is already owner-settled (`DELIB-0715` epistemic hierarchy; `DELIB-0719` MEMORY.md placement) and Codex-VERIFIED (`gtkb-adr-memory-architecture-006`). The governing requirements for the storage act are `GOV-20` (ADR governance), `GOV-08` (KB-is-truth), and `GOV-ARTIFACT-APPROVAL-001` (approval gate). This proposal authorizes only the relocation of an already-verified artifact into the in-root canonical store, not any new architecture decision.

## Prior Deliberations

- `DELIB-0715` (owner_conversation / owner_decision, S299, 2026-04-17) — "MemBase Canonical Definition (Owner Settlement)"; the explicit "Epistemic Hierarchy (settled)" table naming all three tiers (MemBase authoritative / Deliberation Archive evidentiary / MEMORY.md operational). The owner-decision basis for the architecture.
- `DELIB-0719` (owner_conversation / owner_decision, S299, 2026-04-17) — S299 owner decisions including the repo-root `memory/MEMORY.md` placement (the MEMORY.md tier).
- `DELIB-0737` (bridge_thread / go) — harvest record of `gtkb-adr-memory-architecture` at GO; the thread that authored `ADR-0001`.
- `DELIB-1171` (bridge_thread / informational) — later harvest of the same thread after it left the active INDEX.
- `DELIB-0733`, `DELIB-0806`, `DELIB-1192`, `DELIB-1193` (bridge_thread) — the `gtkb-docs-memory-architecture-alignment` thread family that propagated `ADR-0001` vocabulary across docs.
- Bridge chain `gtkb-adr-memory-architecture-001.md` … `-006.md` — the full proposal → NO-GO → revision → GO (`-004`) → post-impl (`-005`) → **VERIFIED (`-006`)** provenance.
- This proposal does **not** revisit a previously-rejected approach. The S297 thread's rejected alternatives (single-store, two-tier, alternate terminology) are preserved inside the migrated `description`; nothing here re-opens them.

## Owner Decisions / Input

- **Originating directive (S379):** Owner handed this hygiene task — "formalize `ADR-0001` in the MemBase `specifications` table … use the formal-artifact-approval packet workflow per `GOV-ARTIFACT-APPROVAL-001`."
- **Approach decision (AskUserQuestion, S379):** Presented the discovery that `ADR-0001` was already Codex-VERIFIED in S297 but never migrated, and asked how to close the gap. Owner selected **"Migrate exact verified content"** (byte-identical migration at `status=verified` from the archived MemBase), over "author fresh, status=specified" and "migrate body, reset to specified." Recorded via `detected_via: ask_user_question` in `memory/pending-owner-decisions.md`.
- **Binding content approval (post-GO, before insert):** The exact `ADR-0001` content + metadata will be presented to the owner and captured in a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-31-ADR-0001.json` per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`, before the `specifications` insert occurs. Bridge GO authorizes proceeding to that approval step; it does not replace it.

## Spec-Derived Verification Plan

Post-implementation verification provides a **spec-to-test mapping** from the linked specifications to executed checks against the in-root MemBase. Tests are structural (the artifact carries no machine assertions). Planned execution via a read-only checker `python .gtkb-state/verify_adr0001.py` plus direct `db.get_spec` readback.

| Test | Maps to spec | Check |
|---|---|---|
| T1 | GOV-08, GOV-20 | `get_spec('ADR-0001')` returns exactly one row, `version=1`, in `E:\GT-KB\groundtruth.db`. |
| T2 | (fidelity) | Inserted `description` length == 4920 AND `U+2014` em-dash count == 8 (byte-identical transfer confirmed). |
| T3 | GOV-20 | `title`, `type`, `status`, `priority`, `scope`, `tags`, `authority` equal the archived verified row exactly. |
| T4 | GOV-20 | `list_specs(type='architecture_decision')` includes `ADR-0001`. |
| T5 | GOV-08 (gap closure) | A re-run phantom-sweep query for `ADR-0001` now returns a row — the acceptance criterion ("future phantom-sweeps will pass"). |
| T6 | (non-regression) | `ADR-001` (3-digit) still has its 4 unchanged versions; no collateral mutation. |

## Project Root Boundary Compliance

All generated/output artifacts are **in-root under `E:\GT-KB`**: this bridge file under `E:\GT-KB\bridge\`; the migration helper at `E:\GT-KB\.gtkb-state\migrate_adr0001.py`; the approval packet at `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-31-ADR-0001.json`; the mutated MemBase at `E:\GT-KB\groundtruth.db`. No output path lies outside the root.

The single out-of-root reference is the archived source MemBase under `E:\Claude-Playground\…`, read **once** as the migration source. `.claude/rules/project-root-boundary.md` explicitly mandates this: "Any live GT-KB artifact discovered under `E:\Claude-Playground` must be relocated to its correct in-root home." The read is a relocation, not a live dependency; after migration, nothing in the running system depends on the archived file.

## Bridge / INDEX Compliance

This proposal is filed at `bridge/gtkb-adr-0001-membase-migration-001.md` with a `NEW` entry inserted at the top of `bridge/INDEX.md`. No prior bridge file or INDEX version is deleted or rewritten; the bridge audit trail remains append-only, with `bridge/INDEX.md` as canonical workflow state.

## Clause Scope Clarification (Not a Bulk Operation)

This is a **single-artifact** migration (one `specifications` row), not a bulk standing-backlog operation. Owner-visibility is provided by the formal-artifact-approval packet and this in-root bridge inventory; no work-item state transitions occur.

## Implementation Plan

1. Author the migration helper `.gtkb-state/migrate_adr0001.py` (operational-tier): open the archived MemBase read-only, fetch the `ADR-0001` row, and call the in-root `KnowledgeDB` insert API with the field values above (attribution + `source_paths` per the Disclosed Deltas; all other fields byte-identical). The helper is invoked as `python .gtkb-state/migrate_adr0001.py` (no gate-blocked substrings on the command line).
2. Generate and present the formal-artifact-approval packet (full content + SHA-256) for owner approval per `GOV-ARTIFACT-APPROVAL-001`.
3. Create the implementation-start authorization packet from this thread's `GO` (`python scripts/implementation_authorization.py begin --bridge-id gtkb-adr-0001-membase-migration`).
4. Run the helper to insert the row.
5. Execute T1–T6, then file the post-implementation report carrying the spec-to-test mapping and observed results for VERIFIED review.

## Risk and Rollback

- **Risk:** content fidelity (em-dash corruption). Mitigated by byte-identical programmatic transfer + T2.
- **Risk:** wrong status. Mitigated by explicit owner AUQ selecting `status=verified`.
- **Risk:** ID collision. Excluded by probe (`ADR-0001` distinct from `ADR-001`; zero existing rows).
- **Rollback:** MemBase is append-only; an erroneous insert is corrected by a superseding `version=2` with a correcting `change_reason`, never by deletion. Because no row exists today, the blast radius is a single net-new row.
- **Out of scope:** the broader cross-environment ADR-propagation question (how GT-KB-governance ADRs reach fresh clones / adopters; `groundtruth.db` remains gitignored) is a pre-existing concern, not addressed here. This proposal closes the in-root storage gap so live phantom-sweeps pass.

## Recommended Commit Type

`feat:` — adds a net-new canonical governance artifact (`ADR-0001`) to the in-root MemBase. (The change is data, not code; `feat:` reflects the new governed capability surface. If Loyal Opposition prefers `chore:` for a data-only migration, that is an acceptable alternative.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
