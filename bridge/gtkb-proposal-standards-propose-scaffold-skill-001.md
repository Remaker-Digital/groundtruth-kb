NEW

# Proposal-Standards Slice 4 — /gtkb-propose Scaffolding Skill

bridge_kind: prime_proposal
Document: gtkb-proposal-standards-propose-scaffold-skill
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-03T13-36-00Z-prime-builder-s382-resume
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE4

target_paths: ["scripts/gtkb_propose_scaffold.py", ".claude/skills/gtkb-propose/SKILL.md", "platform_tests/scripts/test_gtkb_propose_scaffold.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 4 (final slice) of PROJECT-GTKB-GOV-PROPOSAL-STANDARDS. Adds an
interactive proposal-scaffolding surface, `/gtkb-propose`, that walks a Prime
Builder author through composing a **structurally compliant** bridge proposal
body before filing. It is the front-end *composer* that complements the
existing `gtkb-bridge-propose` skill (the back-end safe *writer*): `/gtkb-propose`
emits a gate-satisfying scaffold; the author fills the substance; the filled
body is handed to `gtkb-bridge-propose` for the credential-scanned write +
INDEX insert. The two do not overlap.

**Motivation (evidence-grounded):** the recurring NO-GO and gate-block class in
this very project was *structural*, not substantive — `target_paths` must be
inline-JSON (impl-start `begin` rejects other forms); the spec-derived
verification heading must contain a `VERIFICATION_HEADING_TOKENS` substring;
proposals must carry the `## Owner Decisions / Input` section when they claim
owner-approval scope; cited spec IDs must exist (phantom-spec sweep); the
`CLAUSE-INDEX-IS-CANONICAL` evidence pattern must be present; the body must
begin with a canonical status token (Slice 1's own rule). `/gtkb-propose`
pre-populates exactly these gate-satisfying elements and emits a self-review
checklist that runs the two mandatory preflights, so the author clears the
gates before Codex review instead of in a revise loop.

## Design

### `scripts/gtkb_propose_scaffold.py` (deterministic, read-only + emit)

A standalone helper exposing a `scaffold` entry point. Given
`--slug <kebab>`, `--work-item <WI>`, `--project <PROJECT-ID>`,
`--pauth <PAUTH-ID>`, optional `--slice <N>`, `--bridge-kind <kind>`
(default `implementation_proposal`), and optional `--target-path <glob>`
(repeatable), it:

1. **Validates the slug** — kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), and not
   already present as a `Document:` entry in `bridge/INDEX.md` (collision →
   error with the existing entry).
2. **Validates the WI/Project/PAUTH triple** read-only against MemBase
   (`current_project_work_item_memberships` + `current_project_authorizations`),
   mirroring the `bridge-compliance-gate` membership check, so the emitted
   project-linkage metadata is known-good before filing.
3. **Seeds Prior Deliberations** — runs `search_deliberations()` for the slug +
   work-item topic and injects the top candidate `DELIB-ID`s (with titles) into
   the `## Prior Deliberations` stub; emits the explicit
   `_No prior deliberations: <reason>._` line when the search is empty (the
   authorized empty-justification convention).
4. **Pre-lists cross-cutting specs** — reads
   `config/governance/spec-applicability.toml` and pre-populates
   `## Specification Links` with the required cross-cutting specs triggered by
   the planned `target_paths` (path-regex matrix), each as a TODO citation the
   author confirms or prunes.
5. **Emits a compliant scaffold** to a draft path under
   `.gtkb-state/propose-drafts/<slug>-001.md` (NOT to `bridge/` — the author
   reviews + fills TODOs, then hands off to `gtkb-bridge-propose`). The scaffold
   contains, in order: the `NEW` status token (first line; satisfies Slice 1
   body-status-token rule), the author-metadata block (6 fields, stubbed),
   `bridge_kind`, the three project-linkage lines (filled from validated
   inputs), `target_paths` as an inline-JSON stub, and every required `##`
   section — `## Summary`, `## Specification Links` (seeded), `## Prior
   Deliberations` (seeded), `## Owner Decisions / Input`, `## Requirement
   Sufficiency` (with the two operative-state options), `## Spec-Derived
   Verification Plan` (heading chosen to contain a `VERIFICATION_HEADING_TOKENS`
   substring), `## Risk / Rollback`, `## Recommended Commit Type` — each with a
   `TODO:` placeholder.
6. **Prints a self-review checklist** — the exact commands the author must run
   before filing: `bridge_applicability_preflight.py`, `adr_dcl_clause_preflight.py`,
   a phantom-spec sweep of every cited ID against the `specifications` table, an
   inline-JSON `target_paths` parse check, and the `VERIFICATION_HEADING_TOKENS`
   heading check.

The helper performs **no mutation of `bridge/` or MemBase** — it reads MemBase
read-only and writes only the draft under `.gtkb-state/`. This keeps it outside
every approval gate and lets it compose cleanly with `gtkb-bridge-propose`.

### `.claude/skills/gtkb-propose/SKILL.md`

Orchestration: collect the slug/WI/project/PAUTH (+ optional slice/scope) from
the author, invoke the helper to emit the draft scaffold, instruct the author
to fill the `TODO:` placeholders, then run the self-review checklist, then hand
the completed body to `gtkb-bridge-propose` for the safe write + INDEX insert.
The SKILL.md explicitly defers the actual file write to `gtkb-bridge-propose`
(no duplicate write path).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — the scaffold encodes the bridge
  protocol's required proposal structure; `bridge/INDEX.md` collision check
  honors INDEX-is-canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) — the
  scaffold pre-populates `## Specification Links` from the applicability matrix.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) — the
  scaffold fills + validates the three project-linkage metadata lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) — the helper
  is unit-tested; the scaffold's verification-plan heading satisfies the gate.
- `GOV-STANDING-BACKLOG-001` v5 (verified) — Slice 4 WI is an active member of
  the project under the cited PAUTH.
- `SPEC-2098` v3 (implemented) — Deliberation Archive; the helper consumes
  `search_deliberations()` to seed `## Prior Deliberations`.
- Composes with the existing `gtkb-bridge-propose` skill
  (`.claude/skills/bridge-propose/SKILL.md`) — the write path, unchanged.

Tests derive from these specs: each required-section / metadata / heading /
collision rule the specs impose maps to a unit assertion on the helper's emitted
scaffold (see Spec-Derived Verification Plan).

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` (v1) — owner decision
  including Slice 4 in scope ("Include Slice 4 (extend PAUTH)") and the S382
  re-activation of Claude Code as Prime Builder for this session.
- `DELIB-0782` / `DELIB-1191` — `gtkb-deliberation-cli` bridge thread (closest
  precedent: a CLI surface over the Deliberation Archive, which this helper
  consumes for Prior-Deliberations seeding).
- Slice 1-3 verdicts (`-027`, `-017`, WI-ID collision gate) — the structural
  gate behaviors this scaffold is designed to pre-satisfy.
- _No prior deliberation proposes the /gtkb-propose composer skill itself; it is
  novel and additive to the existing gtkb-bridge-propose writer skill._

## Owner Decisions / Input

This proposal depends on owner approval, supplied via AskUserQuestion and
captured in `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`:

- **S382 Slice 4 disposition AUQ** — owner chose "Include Slice 4 (extend
  PAUTH)", authorizing implementation of the `/gtkb-propose` scaffolding skill
  under `PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4` (active; includes
  `GTKB-GOV-PROPOSAL-STANDARDS-SLICE4`; mutation classes include `skill_addition`,
  `cli_extension`, `test_addition`).
- **S382 resume re-activation AUQ (2026-06-03)** — owner re-activated Claude
  Code as Prime Builder for this session and directed proceeding with Slice 4
  (the durable role map has B suspended; the owner-authorized session-stated
  override governs in-session surfaces).

No new owner decision is required to file this proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** The `/gtkb-propose` scaffold is a
convenience surface that operationalizes existing bridge-protocol structural
requirements (`GOV-FILE-BRIDGE-AUTHORITY-001`, the proposal-standards DCL
family); it introduces no new system requirement. No new or revised
specification is required before implementation.

## Spec-Derived Verification Plan

New unit suite `platform_tests/scripts/test_gtkb_propose_scaffold.py` exercising
the deterministic helper (the SKILL.md is orchestration narrative; the helper
carries the testable logic):

| Acceptance criterion (spec-derived) | Test |
|---|---|
| Invalid (non-kebab) slug rejected; valid slug accepted | `test_slug_validation` |
| Slug colliding with an existing INDEX `Document:` entry is rejected | `test_slug_collision_against_index` |
| Emitted scaffold's first non-blank line is `NEW` (Slice 1 body-status-token) | `test_scaffold_first_line_is_status_token` |
| Scaffold contains all required `##` sections + 3 project-linkage lines + 6-field author block | `test_scaffold_has_all_required_sections` |
| `target_paths` emitted as parseable inline JSON (impl-start `begin` form) | `test_scaffold_target_paths_inline_json` |
| Verification-plan heading contains a `VERIFICATION_HEADING_TOKENS` substring | `test_scaffold_verification_heading_token` |
| Prior-Deliberations stub seeded with search hits, or the empty-justification line when none | `test_prior_deliberations_seeding` / `test_prior_deliberations_empty_justification` |
| Self-review checklist lists both mandatory preflight commands + phantom-spec sweep | `test_self_review_checklist_commands` |
| Helper writes only under `.gtkb-state/propose-drafts/`, never `bridge/` or MemBase | `test_helper_writes_only_draft_path` |

Execution surface (reproducible, repo venv per the Slice 2 lesson — no uv
home-cache dependency):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q --no-header -p no:cacheprovider
```

Plus `ruff check` / `ruff format --check` on the changed Python files.

## Risk / Rollback

Low. The helper is read-only against MemBase and writes only draft scaffolds
under `.gtkb-state/`; it adds no bridge or KB write path (it composes with the
existing `gtkb-bridge-propose` writer). The skill is additive (new
`.claude/skills/gtkb-propose/`). Single-commit revert removes all three files
with no effect on existing surfaces.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `bridge/INDEX.md` document list; no prior version is deleted or rewritten
(append-only audit trail). `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — adds a new interactive proposal-scaffolding skill + its deterministic
helper + unit tests.

## Implementation Sequence (post-GO)

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-proposal-standards-propose-scaffold-skill`.
2. Implement `scripts/gtkb_propose_scaffold.py` (validation + seeding + scaffold emit + checklist).
3. Add `.claude/skills/gtkb-propose/SKILL.md` (orchestration; hand-off to gtkb-bridge-propose).
4. Add `platform_tests/scripts/test_gtkb_propose_scaffold.py`.
5. Run the suite + ruff; file the post-implementation report.

## Decision Needed From Owner

None beyond the captured S382 AUQ decisions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
