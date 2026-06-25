NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 2bb5c7b5-3956-4498-94d7-f7b2711e8e02
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal — Canonical End-to-End GT-KB Lifecycle Reference (WI-3352)

bridge_kind: prime_proposal
Document: gtkb-canonical-lifecycle-reference
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

## Project Authorization

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: WI-3352

Owner decision basis: DELIB-20265586 (PAUTH grant 2026-06-23) and DELIB-20266085 (AUQ 2026-06-25 — "Implement WI-3352 now under PAUTH").

## Summary

WI-3352 (P3, documentation): the deliberate → plan(project) → specify → propose →
GO → implement → report → VERIFIED → commit lifecycle is documented only in
fragments across five-plus files (`.claude/rules/operating-model.md` §1,
`CLAUDE.md` workflow + bridge sections, `.claude/rules/file-bridge-protocol.md`,
`.claude/rules/deliberation-protocol.md`). No single canonical pipeline artifact
exists. `groundtruth-kb/docs/method/01-overview.md` presents only the 7-step spec
workflow with the bridge described separately, omitting the **deliberate** and
**commit** bookends. New-agent orientation has no one place to learn the whole
integrated cycle.

This proposal authors **one canonical lifecycle reference** and makes it
discoverable from the two surfaces a new agent encounters first: the published
method docs and the role-neutral session-startup index.

## Specification Links

Cross-cutting (mechanically applicable to this bridge proposal):
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority (path: `bridge/**`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived executed tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable-artifact bias (this converts fragmented lifecycle knowledge into a durable referenced artifact).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision underlying the durable-artifact bias.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers.

This proposal honors `GOV-FILE-BRIDGE-AUTHORITY-001`: it is filed as an
append-only versioned entry in the canonical numbered bridge-file chain
(`bridge/gtkb-canonical-lifecycle-reference-NNN.md`); no bridge file is deleted
or rewritten in place, and TAFE/dispatcher state is the authoritative workflow
state.

Project-authorization governance:
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization (governs the cited PAUTH; included in the PAUTH `included_spec_ids`).

Subject-matter / surfacing authority (specs the reference documents or whose surface it touches):
- `GOV-SESSION-SELF-INITIALIZATION-001` — fresh-session self-initialization; authorizes surfacing the reference at SessionStart for new-agent orientation.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — startup token-budget / disclosure minimization; the SessionStart surfacing is a single pointer in the role-neutral startup index, NOT new narration injected into the minimized init disclosure, to respect this constraint.

The reference documents (does not modify) the lifecycle these artifacts govern;
the authoritative texts remain `.claude/rules/operating-model.md` §1,
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/deliberation-protocol.md`,
and `CLAUDE.md`. The new doc cites them as sources and adds no new requirements.

## Requirement Sufficiency

Existing requirements sufficient. WI-3352 is a documentation-consolidation work
item; the lifecycle it documents is already fully specified by the governing
artifacts cited above. No new or revised requirement is required before
implementation. This proposal creates a derived reference plus its structural
guard test; it introduces no new behavior contract.

## Prior Deliberations

Deliberation Archive searched (2026-06-25) for prior decisions on a canonical
lifecycle reference / new-agent-orientation pipeline doc:
- `gt deliberations search "WI-3352 canonical end-to-end GT-KB lifecycle reference new-agent orientation"` — no on-point prior decision (top hits: DELIB-20265892 disposition-profile ratification, DELIB-0105 rename, DELIB-0096 extensibility — all unrelated).
- `gt deliberations search "end-to-end GT-KB lifecycle pipeline documentation ... bookends"` and `"new agent orientation onboarding canonical reference docs method"` — no on-point prior decision (hits were generic GO/NO-GO verdicts and 2026-03 documentation audits).
- No prior deliberation rejects or constrains authoring this reference.
- Governing owner decision for this work: `DELIB-20266085` (this session's AUQ disposition) under `DELIB-20265586` (PAUTH grant).

_No prior deliberations on the canonical-lifecycle-reference topic itself; the closest authority is the owner disposition DELIB-20266085._

## Owner Decisions / Input

This work depends on owner approval, supplied via AskUserQuestion and recorded as
`DELIB-20266085`:

- AUQ `AUQ-ADOPTER-EXPERIENCE-RETIREMENT-DISPOSITION-2026-06-25`, Q2 "WI-3352":
  owner answer **"Implement now under PAUTH"** — authorizes the full bridge cycle
  for WI-3352 under the existing PAUTH. This also resolves WI-3352's own
  description note ("not implementation-approved; requires owner approval ...").
- No further owner decision is blocking; scope is bounded to WI-3352 and adds no
  new work item to the project (PAUTH snapshot ACID-invariant preserved).

## target_paths

```json
[
  "groundtruth-kb/docs/method/14-lifecycle.md",
  "groundtruth-kb/docs/method/01-overview.md",
  "groundtruth-kb/docs/method/README.md",
  "config/agent-control/SESSION-STARTUP-INDEX.md",
  "platform_tests/scripts/test_lifecycle_reference.py"
]
```

Mutation classes used (all within the PAUTH `allowed_mutation_classes`
[source, test_addition, hook_upgrade, cli_extension, scaffold_update]):
- `source` / `scaffold_update` — new + edited published method docs and the
  startup-index pointer (markdown source surfaces).
- `test_addition` — the new structural guard test.

No protected narrative-authority file is touched (`SESSION-STARTUP-INDEX.md` is
under `config/agent-control/`, outside the narrative-artifact-approval set of
`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`). No `.claude/rules` or KB spec
mutation is in scope.

## Proposed Change

### Deliverable 1 — Author `groundtruth-kb/docs/method/14-lifecycle.md`

A new published method doc, "The End-to-End Lifecycle," presenting the single
integrated cycle. Planned structure:
- Intro: why one canonical cycle exists; relationship to the 7-step spec workflow
  in `01-overview.md` (this doc is the superset that adds the bridge gates and the
  deliberate/commit bookends).
- A single mermaid flowchart of the full cycle:
  `deliberate → plan(project) → specify → propose → GO → implement → report → VERIFIED → commit`,
  with the NO-GO revise loop (propose ⇄ GO) and the NO-GO re-implement loop
  (report ⇄ VERIFIED).
- One subsection per stage, each with: what happens, the responsible role
  (owner / Prime Builder / Loyal Opposition), the artifact produced, the
  governing source(s), and the gate that must pass to advance. Stages:
  1. **Deliberate** — Deliberation Archive capture (source: deliberation-protocol; operating-model §1).
  2. **Plan (project)** — backlog/project formulation + project authorization (GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001).
  3. **Specify** — requirement → specification capture (GOV-09, GOV-SPEC-CAPTURE-TRANSPARENCY-001).
  4. **Propose** — implementation proposal filed NEW (file-bridge-protocol; codex-review-gate; spec-linkage gate).
  5. **GO** — Loyal Opposition review → GO / NO-GO (review independence).
  6. **Implement** — impl-start authorization packet + code/tests (GOV-12; impl-start gate).
  7. **Report** — post-implementation report filed for verification.
  8. **VERIFIED** — Loyal Opposition verification → VERIFIED (spec-derived verification gate; VERIFIED commit-finalization).
  9. **Commit** — scoped local commit bundling the verified work + verdict.
- "How this maps to the 7-step workflow" reconciliation table.
- Cross-links to the per-stage deep-dive docs (02-specifications, 03-testing,
  04-work-items, 05-governance, 06-dual-agent, 12-file-bridge-automation,
  13-deliberation-archive) and the authoritative rule files.

### Deliverable 2 — Integrate into `01-overview.md` + `README.md`

- `01-overview.md` "Core workflow": add a short paragraph acknowledging the full
  integrated cycle (the deliberate front-bookend and the commit back-bookend, and
  the bridge GO/VERIFIED gates that wrap implementation), with a prominent
  cross-link to `14-lifecycle.md`. The existing 7-step diagram stays; the new text
  frames it as the spec-centric core within the larger cycle.
- `README.md` reading-order index: add row `14 | The End-to-End Lifecycle`.

### Deliverable 3 — Surface at SessionStart (`SESSION-STARTUP-INDEX.md`)

Add a brief "New-agent orientation" pointer to the role-neutral startup index
naming `groundtruth-kb/docs/method/14-lifecycle.md` as the canonical end-to-end
lifecycle reference. This is the architecture-compatible realization of WI-3352's
"surface it in the SessionStart startup disclosure": the live init disclosure is
intentionally minimized (DCL-SESSION-STARTUP-TOKEN-BUDGET-001; init-keyword
relay), and `SESSION-STARTUP-INDEX.md` is the canonical surface both roles resolve
at startup (GOV-SESSION-SELF-INITIALIZATION-001). A pointer here surfaces the
reference for new-agent orientation without expanding the minimized payload or
touching the load-bearing `session_self_initialization.py` generator.

### Deliverable 4 — Spec-derived structural test

New `platform_tests/scripts/test_lifecycle_reference.py` asserting:
- `14-lifecycle.md` exists and names all nine cycle stages (deliberate, plan,
  specify, propose, GO, implement, report, VERIFIED, commit).
- `01-overview.md` cross-links `14-lifecycle.md` and mentions the deliberate +
  commit bookends.
- `README.md` indexes `14-lifecycle.md`.
- `SESSION-STARTUP-INDEX.md` contains the new-agent-orientation pointer to
  `14-lifecycle.md`.

## Specification-Derived Verification Plan

| Requirement (source) | Verification |
|---|---|
| One canonical lifecycle reference exists covering the full cycle (WI-3352; operating-model §1) | `test_lifecycle_reference.py::test_reference_exists_and_covers_all_stages` |
| Reference integrated into `01-overview.md` incl. deliberate+commit bookends (WI-3352) | `test_lifecycle_reference.py::test_overview_links_reference_and_bookends` |
| Reference indexed in method README (WI-3352) | `test_lifecycle_reference.py::test_readme_indexes_reference` |
| Reference surfaced at SessionStart for new-agent orientation (WI-3352; GOV-SESSION-SELF-INITIALIZATION-001) | `test_lifecycle_reference.py::test_startup_index_points_to_reference` |
| Startup minimization respected — pointer only, no init-disclosure narration (DCL-SESSION-STARTUP-TOKEN-BUDGET-001) | review inspection of the diff + the pointer-only assertion |

Execution commands (run on touched files before filing the post-impl report):
- `python -m pytest platform_tests/scripts/test_lifecycle_reference.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_lifecycle_reference.py`
- `python -m ruff format --check platform_tests/scripts/test_lifecycle_reference.py`

## Acceptance Criteria

1. `14-lifecycle.md` authored, documenting all nine stages with role + artifact +
   governing source + advancement gate per stage, and a full-cycle diagram.
2. `01-overview.md` + `README.md` integrated and cross-linked; bookends present.
3. `SESSION-STARTUP-INDEX.md` pointer present; init disclosure unchanged
   (minimization preserved).
4. `test_lifecycle_reference.py` present and PASSING; ruff check + format clean.
5. No new behavior, no spec mutation, no protected-file mutation, no new project
   work item.

## Risk / Rollback

- Risk: low. All changes are additive documentation + one test + a single
  startup-index pointer line. No runtime code path changes.
- Blast radius: the only non-doc surface is `SESSION-STARTUP-INDEX.md` (markdown,
  a pointer line); the live startup generator and the minimized disclosure are
  untouched, so SessionStart behavior is unchanged.
- Rollback: revert the five target paths; no migration, no data, no state.

## Recommended Commit Type

`docs:` — the deliverable is a documentation artifact (new canonical reference +
integration into the published method series and the startup index) plus its
structural guard test. No new runtime capability is added; the test exists solely
to keep the documentation surfaces from regressing. (`test:` is secondary; the
dominant change class is documentation.)
