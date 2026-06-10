REVISED

bridge_kind: governance_advisory
Document: gtkb-adr-0001-membase-migration
Version: 005
Responds to: bridge/gtkb-adr-0001-membase-migration-004.md GO
Author: Prime Builder (Opus 4.8, harness B)
Date: 2026-05-31 UTC
Session: S379
Recommended commit type: docs

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S379-adr-0001-membase-migration-005-format-revised
author_model: Opus 4.8
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-31-ADR-0001.json", ".gtkb-state/adr-0001-migration-source.json", ".gtkb-state/migrate_adr0001.py", ".gtkb-state/verify_adr0001.py", "bridge/gtkb-adr-0001-membase-migration-*.md", "bridge/INDEX.md"]

# GT-KB ADR-0001 MemBase Storage-Gap Migration (format-only REVISED after GO -004)

**Bridge file home:** `E:\GT-KB\bridge\gtkb-adr-0001-membase-migration-005.md` (in-root, under `E:\GT-KB\bridge\`)
**Proposed mutation:** one append-only `specifications` row insert (`ADR-0001`, `type=architecture_decision`, `version=1`) into the in-root MemBase `E:\GT-KB\groundtruth.db`, governed by a per-artifact formal-artifact-approval packet.

## Response to GO -004 (format-only REVISED — no substantive change)

`-003` received GO at `-004`. This REVISED changes **only the presentation of `target_paths`** so `scripts/implementation_authorization.py begin` can mechanically extract them: the GO'd `-003` expressed `target_paths` as a `**bold label**` + bullet list, which `extract_target_paths` does not parse (it accepts inline JSON, a `## Files Expected To Change` heading, or a `## target_paths` heading). `-005` adds the inline-JSON `target_paths:` metadata line above and an `## Authorized Target Paths` reading section below.

**No scope, content, field-value, verification, or classification change** from the GO'd `-003`. The authorized path set is byte-identical to `-003`. All `-003` resolutions to the `-002` NO-GO (F1 governance_review classification, F3 in-root source removal of the archived-DB dependency, F4 verification coverage) stand unchanged.

## Authorized Target Paths

- `groundtruth.db` — the `ADR-0001` row (governed by the formal-artifact-approval packet).
- `.groundtruth/formal-artifact-approvals/2026-05-31-ADR-0001.json` — the approval packet.
- `.gtkb-state/adr-0001-migration-source.json` — the in-root migration source (already created at authoring time).
- `.gtkb-state/migrate_adr0001.py` — deterministic insert helper.
- `.gtkb-state/verify_adr0001.py` — read-only verifier (T1–T11).
- `bridge/gtkb-adr-0001-membase-migration-*.md` — this thread's bridge files.
- `bridge/INDEX.md` — the INDEX entry.

## Classification Rationale (F1)

The `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` metadata (`Project Authorization` / `Project` / `Work Item`) applies to **project-implementation** proposals — source, config, test, script, or feature work scoped by a project-scoped implementation authorization. Its recognized exemption is `bridge_kind` in `{spec_intake, governance_review, loyal_opposition_advisory}`.

This proposal creates exactly one **canonical governance artifact** (an ADR). It writes no source, config, test, or feature code. The sole mutations are (1) the `ADR-0001` `specifications` row, governed per-artifact by `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`, and (2) the append-only bridge/INDEX audit trail. Governance-artifact creation is governed by the formal-artifact-approval packet, not the project-authorization chain. Precedent: `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-007.md` (ADR/DCL governance, also `governance_review`). Codex confirmed at `-004` that `governance_review` is a recognized exemption in `.claude/hooks/bridge-compliance-gate.py`.

## Summary

`ADR-0001` "Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)" is cited 57 times across 30 in-root files yet has **zero rows** in the in-root MemBase `E:\GT-KB\groundtruth.db` — a cited-but-not-stored governance hole (GOV-08). It is not an un-formalized concept: it was authored and Codex-VERIFIED in S297 via `gtkb-adr-memory-architecture` (`-006` = VERIFIED), but the verified row lived only in the old, now-archived root's gitignored MemBase and never migrated when the root moved to `E:\GT-KB`. This proposal closes the gap by migrating the **byte-identical verified row** into the in-root MemBase via the formal-artifact-approval packet workflow. It does not re-litigate the S297 decision.

## Context

- Live `SELECT … WHERE id='ADR-0001'` on `E:\GT-KB\groundtruth.db` → 0 rows (all versions). `ADR-001` (3-digit, "Per-interface transport dispatch") has 4 versions; `'ADR-0001' != 'ADR-001'`, so no `UNIQUE(id,version)` collision.
- `gtkb-adr-memory-architecture-006` (in-root) VERIFIED the original row: `status=verified`, `version=1`, description length 4920, 8 `U+2014` em-dashes.
- Owner directed (AskUserQuestion, S379, `DECISION-0880`) to **migrate the exact verified content** at `status=verified`.

## Decision: exact row to be inserted

The deterministic insert helper reads the **in-root** migration source and inserts into `E:\GT-KB\groundtruth.db`. The `description` is transferred byte-identically (all 8 `U+2014` em-dashes preserved); it is never retyped.

| Field | Value | Provenance |
|---|---|---|
| `id` | `ADR-0001` | byte-identical; matches 57 citations |
| `version` | `1` | first row in the in-root DB (append-only) |
| `title` | `Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)` | byte-identical |
| `type` | `architecture_decision` | byte-identical (GOV-20) |
| `status` | `verified` | per owner AUQ; carries the S297 Codex verification of identical content |
| `priority` | `major` | byte-identical |
| `scope` | `governance` | byte-identical |
| `tags` | `["memory","architecture","adopter-facing","tier-a-enabler"]` | byte-identical |
| `description` | the 4920-char verified body (`description_sha256: 9e2f1467…`) | byte-identical from in-root source |
| `assertions` | `None` | byte-identical |
| `authority` | `stated` | byte-identical |
| `affected_by` | `None` | byte-identical |
| `testability` | `None` | byte-identical |
| `source_paths` | original 4 bridge files **+ this migration bridge** | provenance enrichment (disclosed) |
| `changed_by` | `prime-builder/S379-adr-0001-membase-migration` | reflects THIS insert event |
| `changed_at` | UTC at insert time | reflects THIS insert event |
| `change_reason` | cites the formal-artifact-approval packet path + S297 verification provenance (`gtkb-adr-memory-architecture-006` VERIFIED) + the cited-but-not-stored gap | reflects THIS insert event |

Disclosed deltas from the archived row (everything else byte-identical): attribution fields describe THIS insert; `source_paths` adds this migration bridge for provenance.

## In-Root Migration Source (F3)

The exact verified bytes were relocated at **authoring time** (the one-time relocation mandated by `.claude/rules/project-root-boundary.md`) into:

- Path: `.gtkb-state/adr-0001-migration-source.json` (in-root, under `E:\GT-KB`)
- `description_sha256`: `9e2f1467ba9054c244b7148438ef3f9beb7a5e61fd0b80dc840e0a012c0fa9c4`
- `record_sha256`: `de2003fdac39176d731a217d4e5498f02937c314663634df257076240fdc4413`
- `description_length`: 4920; `description_emdash_count`: 8

The GO'd implementation (insert + verify) reads ONLY this in-root source. `E:\Claude-Playground` is historical evidence and is not opened during implementation or verification. At approval time the packet's `full_content` is populated from this in-root source and its `full_content_sha256` must equal `9e2f1467…`.

## Specification Links

- `GOV-20` — Architecture Decision Governance: ADRs stored as `type=architecture_decision`.
- `GOV-08` — Knowledge Database is the single source of truth: the cited-but-not-stored hole this closes.
- `GOV-ARTIFACT-APPROVAL-001` — Formal artifact approval gate: the binding owner authorization for this insert.
- `PB-ARTIFACT-APPROVAL-001` — Canonical artifact writes require approval evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — Approval hook must display full content before insertion.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — Strict formalization gate governs ADR insertion.
- `SPEC-2098` — Deliberation Archive: the DA tier named by `ADR-0001`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals cite all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derives from linked specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root/`applications/` boundary; governs the authoring-time relocation and the in-root-only implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata rule; satisfied via the `governance_review` exemption.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifacts (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle states (advisory).
- `.claude/rules/file-bridge-protocol.md` — bridge protocol + mandatory gates.
- `.claude/rules/codex-review-gate.md` — pre-implementation review for KB mutations.
- `.claude/rules/project-root-boundary.md` — root boundary + relocate-to-in-root clause.
- `.claude/rules/canonical-terminology.md` — the always-loaded read-surface citing `ADR-0001`.

## Requirement Sufficiency

**Existing requirements sufficient.** The architecture decision is owner-settled (`DELIB-0715` epistemic hierarchy; `DELIB-0719` MEMORY.md placement) and Codex-VERIFIED (`gtkb-adr-memory-architecture-006`). Governing requirements for the storage act: `GOV-20`, `GOV-08`, `GOV-ARTIFACT-APPROVAL-001`. No new or revised requirement is created; this relocates an already-verified artifact into the in-root canonical store.

## Prior Deliberations

- `DELIB-0715` (owner_conversation / owner_decision, S299) — "MemBase Canonical Definition (Owner Settlement)"; the "Epistemic Hierarchy (settled)" table naming all three tiers. Owner-decision basis.
- `DELIB-0719` (owner_conversation / owner_decision, S299) — S299 owner decisions incl. repo-root `memory/MEMORY.md` placement.
- `DELIB-0737` (bridge_thread / go) — `gtkb-adr-memory-architecture` at GO; authored `ADR-0001`.
- `DELIB-1171` (bridge_thread) — same thread, later orphaned-historical harvest.
- `DELIB-0733`, `DELIB-0806`, `DELIB-1192`, `DELIB-1193` — `gtkb-docs-memory-architecture-alignment` thread family that propagated the vocabulary.
- Bridge chain `gtkb-adr-memory-architecture-001.md` … `-006.md` — proposal → NO-GO → revision → GO (`-004`) → post-impl (`-005`) → VERIFIED (`-006`).
- Classification precedent: `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-007.md` — ADR/DCL governance work classified `bridge_kind: governance_review`.
- This thread's own GO at `bridge/gtkb-adr-0001-membase-migration-004.md` (no blocking findings).
- This proposal does not revisit a previously-rejected approach; the S297 rejected alternatives are preserved inside the migrated `description`.

## Owner Decisions / Input

- **Originating directive (S379):** Owner handed this hygiene task — "formalize `ADR-0001` … use the formal-artifact-approval packet workflow per `GOV-ARTIFACT-APPROVAL-001`."
- **Approach decision (AskUserQuestion, S379, `DECISION-0880`):** Owner selected **"Migrate exact verified content"** (byte-identical migration at `status=verified`) over "author fresh, status=specified" and "migrate body, reset to specified." Recorded `detected_via: ask_user_question` in `memory/pending-owner-decisions.md`.
- **Binding content approval (post-GO, before insert):** The exact `ADR-0001` content + metadata is presented to the owner and captured in a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-31-ADR-0001.json` (`full_content` from the in-root source; `full_content_sha256` == `9e2f1467…`) per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`, before the insert. Bridge GO authorizes proceeding to that approval step; it does not replace it.

## Spec-Derived Verification Plan

Post-implementation verification provides a **spec-to-test mapping** from every linked governing/gate specification to an executed check against in-root state. Tests are structural (the artifact carries no machine assertions). Executed via a read-only `python .gtkb-state/verify_adr0001.py` plus `db.get_spec` readback and `git status --short`.

| Test | Maps to spec | Executed check |
|---|---|---|
| T1 | GOV-08, GOV-20 | `get_spec('ADR-0001')` returns exactly one row, `version=1`, in `E:\GT-KB\groundtruth.db`. |
| T2 | fidelity | Inserted `description` length == 4920 AND `U+2014` count == 8 AND `sha256(description)` == `9e2f1467…` (== in-root source). |
| T3 | GOV-20 | `title`/`type`/`status`/`priority`/`scope`/`tags`/`authority` equal the in-root source exactly. |
| T4 | GOV-20 | `list_specs(type='architecture_decision')` includes `ADR-0001`. |
| T5 | GOV-08 (gap closure) | Re-run phantom-sweep for `ADR-0001` returns a row — the acceptance criterion. |
| T6 | non-regression | `ADR-001` (3-digit) still has 4 unchanged versions; no collateral mutation. |
| T7 | GOV-ARTIFACT-APPROVAL-001, PB-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001 | Packet exists at `.groundtruth/formal-artifact-approvals/2026-05-31-ADR-0001.json`; `full_content_sha256` == `9e2f1467…` == inserted `description` hash; inserted `change_reason` cites the packet path. |
| T8 | ADR-ISOLATION-APPLICATION-PLACEMENT-001, project-root-boundary | `rg` over `.gtkb-state/migrate_adr0001.py`, `.gtkb-state/verify_adr0001.py`, and the inserted `change_reason`/`source_paths` finds no live `E:\Claude-Playground` read dependency; the helper's source path is the in-root `.gtkb-state/adr-0001-migration-source.json`. |
| T9 | GOV-FILE-BRIDGE-AUTHORITY-001 | `bridge/INDEX.md` carries the `gtkb-adr-0001-membase-migration` entry chain (NEW → NO-GO → REVISED → GO → … → VERIFIED); no prior version deleted or rewritten (append-only). |
| T10 | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (provenance) | Inserted `source_paths` includes the original 4 `gtkb-adr-memory-architecture` bridge files + this migration bridge (prior-chain linkage preserved). |
| T11 | file-bridge-protocol target_paths | `git status --short` shows only authorized `target_paths` changed (bridge `*.md` + INDEX; `groundtruth.db` is gitignored so it does not appear — row existence is proven by T1, not git). |

## Project Root Boundary Compliance

All generated/output artifacts are **in-root under `E:\GT-KB`**: this bridge file under `E:\GT-KB\bridge\`; the migration source `E:\GT-KB\.gtkb-state\adr-0001-migration-source.json`; the helpers under `E:\GT-KB\.gtkb-state\`; the approval packet under `E:\GT-KB\.groundtruth\formal-artifact-approvals\`; the mutated MemBase `E:\GT-KB\groundtruth.db`. No output path lies outside the root, and **no implementation or verification step reads any path outside `E:\GT-KB`**. The archived `E:\Claude-Playground` MemBase was read only once at authoring time to produce the in-root hashed source (the relocation mandated by `.claude/rules/project-root-boundary.md`); it is historical evidence with no live dependency.

## Bridge / INDEX Compliance

This REVISED is filed at `bridge/gtkb-adr-0001-membase-migration-005.md` with a `REVISED` line inserted at the top of the existing entry in `bridge/INDEX.md`. No prior bridge file or INDEX version is deleted or rewritten; the bridge audit trail remains append-only with `bridge/INDEX.md` as canonical workflow state.

## Clause Scope Clarification (Not a Bulk Operation)

This is a single-artifact governance migration (one `specifications` row), not a bulk standing-backlog operation. Owner-visibility is the formal-artifact-approval packet plus this in-root bridge inventory; no work-item state transitions occur.

## Implementation Plan

1. **(Done at authoring)** Relocate the verified bytes into the in-root hashed source `.gtkb-state/adr-0001-migration-source.json`. The archived DB is not read again.
2. Author the deterministic insert helper `.gtkb-state/migrate_adr0001.py`: read the **in-root source**, call the in-root `KnowledgeDB` insert with the field values above. Invoked as `python .gtkb-state/migrate_adr0001.py`. No archived-DB access.
3. Generate and present the formal-artifact-approval packet (`full_content` from the in-root source; `full_content_sha256` == `9e2f1467…`) for owner approval per `GOV-ARTIFACT-APPROVAL-001`.
4. `python scripts/implementation_authorization.py begin --bridge-id gtkb-adr-0001-membase-migration` to create the impl-start packet scoped to `target_paths`.
5. Run the insert helper; then run `.gtkb-state/verify_adr0001.py` executing T1–T11.
6. File the post-implementation report carrying the spec-to-test mapping and observed results for VERIFIED review.

## Risk and Rollback

- **Content fidelity:** byte-identical transfer from the in-root hashed source + T2/T7 hash checks.
- **Out-of-root dependency:** eliminated; T8 proves no live `E:\Claude-Playground` read.
- **ID collision:** excluded (`ADR-0001` distinct from `ADR-001`; zero existing rows).
- **Rollback:** MemBase is append-only; an erroneous insert is superseded by `version=2` with a correcting `change_reason`, never deleted. Blast radius is one net-new row.
- **Out of scope:** cross-environment ADR propagation (the gitignored-`groundtruth.db` adopter-reach question) remains a pre-existing, separate concern; closing the in-root gap is what makes live phantom-sweeps pass.

## Recommended Commit Type

`docs:` — the change formalizes a governance artifact; the git-committed surface is the bridge audit trail (`groundtruth.db` is gitignored, so the row itself is not committed). Matches the `governance_review` convention of the precedent ADR/DCL thread. (`chore:` is an acceptable alternative for a data-only migration.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
