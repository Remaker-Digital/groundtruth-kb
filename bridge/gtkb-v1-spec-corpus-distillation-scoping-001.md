NEW

# Implementation Proposal — V1 Release Strategy: §10.2 Spec-Corpus Distillation Scoping (WI-3402)

bridge_kind: governance_advisory
Document: gtkb-v1-spec-corpus-distillation-scoping
Version: 001
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: bfc70de3-76e6-4db9-a78b-ce2758bb8679
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Project: GTKB-V1-RELEASE-STRATEGY-001
Project Authorization: PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING
Work Item: WI-3402
work_item_ids: [WI-3402]
target_paths: []
requires_verification: false
implementation_scope: governance_review_scoping
spec_ids: []

---

## Claim

Scope the future implementation thread for V1 spec-corpus distillation per DELIB-2234 §10.2 + §9.6. Deliverable here is the slice plan, directory layout, content-extraction policy, and acceptance criteria for distilling the in-tree `specs/` corpus from scattered narrative sources. No `specs/` content is created in this proposal — that begins under the per-slice implementation PAUTHs minted after this scoping reaches GO.

## KB-Mutation Negation (self-demonstration)

target_paths is `[]`; no MemBase spec mutation, no protected narrative artifact edit, no source file change. The artifact produced is this scoping document.

## Why Now

DELIB-2234 §10.2 makes in-tree `specs/` the V1 spec-corpus home prior to a v1.0 cut migrating to a standalone `groundtruth-spec` repo. §9.6 makes spec-corpus presence a release-gate prerequisite. The corpus today is distributed across `.claude/rules/`, MemBase narrative descriptions, bridge files, and `independent-progress-assessments/`. Distillation consolidates the canonical statements into one navigable tree, eliminating ambiguity between rule files and DA-archived narrative.

Per DELIB-2234 §8.16, distillation is *also* the §10.5 rule-corpus cleanse; running them separately would create the same drift twice. Scoping them as one effort prevents that.

## Why Not (alternatives considered)

1. **Defer until v1.0 cut migrates to `groundtruth-spec` repo.** Rejected: the in-tree-first path is a deliberate choice (in-tree iteration is faster than cross-repo). Deferring distillation pushes the V1 cut.
2. **Distill into MemBase as new spec rows instead of `specs/` directory.** Rejected: MemBase is canonical for governed spec rows, but the corpus distillation produces *narrative* spec material (cross-spec context, examples, reasoning) that doesn't fit a single `description` field. The two are complementary: MemBase = governed primary statements; `specs/` = narrative reference.
3. **Distill rule-corpus separately from spec-corpus.** Rejected per DELIB-2234 §8.16 — same drift twice.

## Prior Deliberations

- `DELIB-2234` — V1 release strategy: §10.2 spec-corpus distillation, §9.6 release-gate dependency, §8.16 distillation = rule-corpus cleanse.
- `DELIB-20260674` — owner AUQ approving PAUTH minting for V1 release strategy scopings (S414 wave-7).
- `memory/v1-release-strategy-deliberation-S347.md` — Hybrid Variant + 3-tier corpus framing.

_No prior bridge proposal exists for this scoping; this is the first._

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — spec-corpus distillation produces release-gate evidence per DELIB-2234 §9.6.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` — adopters consume the distilled corpus as their authoritative spec surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the distilled `specs/` tree is itself an artifact under change control.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal carries linked governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification Plan section below.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — scoping → per-slice implementation → per-slice verification chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the scoping artifact persists as durable bridge evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — distillation stays at GT-KB root `specs/`; no `applications/` paths involved.

## Owner Decisions / Input

- 2026-06-04 UTC, S414: owner AUQ → "Mint V1 release strategy PAUTH; I draft 3 scopings (Recommended)" recorded as `DELIB-20260674`. The PAUTH `PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING` includes WI-3402, allowed_mutation_classes=`["bridge_proposal_authoring"]`.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-2234 §10.2 + §9.6 + §8.16 define the distillation's intent; this scoping concretizes the directory layout and slice plan within that intent.

## Proposed Scope of the Future Implementation Thread

### Directory Layout

Per WI-3402 description, the first-slice directory layout is:

```text
specs/
├── 00-overview/
│   ├── README.md                  # Map of the corpus
│   ├── architecture-summary.md
│   └── glossary.md                # Distilled from .claude/rules/canonical-terminology.md
├── 10-roles-and-governance/
│   ├── prime-builder.md           # Distilled from .claude/rules/prime-builder-role.md + prime-builder.md
│   ├── loyal-opposition.md        # Distilled from .claude/rules/loyal-opposition.md
│   ├── governance-principles.md   # GOV-01 through GOV-20 + GOV-* index
│   └── deliberation-archive.md
├── 30-bridge-protocol/
│   ├── overview.md                # File bridge protocol summary
│   ├── statuses.md                # NEW/REVISED/GO/NO-GO/VERIFIED/ADVISORY/DEFERRED/WITHDRAWN
│   ├── workflow.md                # Propose → review → execute → report → verify
│   └── claim-and-write-discipline.md
└── 99-history/
    └── rejected-alternatives.md   # Index of WITHDRAWN/NO-GO patterns with rationale
```

### Slice Plan

**Slice 0 — Directory scaffold + corpus inventory**
- Create `specs/` tree with empty README/index files
- Inventory current canonical statements across `.claude/rules/`, MemBase, bridge files
- Output: corpus-inventory map (which canonical statements move where)

**Slice 1 — `00-overview/` distillation**
- Extract: glossary, architecture summary, corpus map
- Tests: glossary terms preserved verbatim from canonical-terminology.md; broken-link audit

**Slice 2 — `10-roles-and-governance/` distillation**
- Extract: role definitions, GOV-01 through GOV-20 governance index, DA description
- Tests: cited GOV/DCL/ADR references resolve in MemBase

**Slice 3 — `30-bridge-protocol/` distillation**
- Extract: full bridge-protocol vocabulary from `.claude/rules/file-bridge-protocol.md` and related
- Tests: status vocabulary matches `bridge/INDEX.md` semantics

**Slice 4 — `99-history/rejected-alternatives.md` distillation**
- Extract: WITHDRAWN/NO-GO patterns with their captured rationale
- Tests: every cited rejected-alternative resolves to a real bridge file

**Slice 5+ — Per DELIB-2234 §10.5 rule-corpus cleanse**
- Remove or relocate now-redundant canonical statements from `.claude/rules/` once distilled equivalents exist in `specs/`
- Per-rule-file slices to keep blast radius bounded

### Acceptance Criteria (umbrella)

- AC1: Distilled `specs/` corpus covers every GOV/DCL/ADR currently in MemBase.
- AC2: Every distilled spec cites its MemBase ID where applicable.
- AC3: Rule-corpus cleanse removes only canonical statements with distilled equivalents.
- AC4: Broken-link audit passes on the distilled tree.
- AC5: Operators (Prime Builder, Loyal Opposition, owner) can navigate the corpus without external context.

### Out of Scope

- Migration to standalone `groundtruth-spec` repo (DELIB-2234 §10.2 explicitly schedules this for v1.0 cut, post-distillation).
- Distillation of application-scope corpus (`applications/*/CLAUDE.md` etc.) — adopter-scope distillation is a separate WI per Hybrid Variant.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this NEW entry is added to bridge/INDEX.md:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-v1-spec-corpus-distillation-scoping
```

Expected: `preflight_passed: true`, `missing_required_specs: []`.

## Specification-Derived Verification Plan

| Spec | Verification (for this scoping proposal) |
|------|------------------------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` contains the document with NEW status. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Slice plan above includes per-slice test coverage; release-gate dependency surfaces at AC1-AC5. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | Distilled corpus IS the adopter-facing spec surface; AC5 covers operator-navigability. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites every relevant spec in Specification Links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every cited spec to verification evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Scoping → per-slice implementation → verification chain. |

Verification commands (for the scoping artifact itself):

```text
test -f bridge/gtkb-v1-spec-corpus-distillation-scoping-001.md
grep -q "^Document: gtkb-v1-spec-corpus-distillation-scoping" bridge/INDEX.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-v1-spec-corpus-distillation-scoping
```

## Risk and Rollback

- **Risk:** Slice 0 corpus inventory turns out to be larger than tractable for the slice-1+ plan above. Mitigation: Slice 0's deliverable IS the inventory; subsequent slice scoping can be revised to match the actual corpus shape.
- **Risk:** Rule-corpus cleanse (Slice 5+) removes statements still referenced by hooks/CLI. Mitigation: per-rule-file slices keep blast radius bounded; verification step in each slice includes a hook-reference grep.
- **Rollback:** The artifact is the scoping document itself. No source mutation in this proposal.

## Bridge Filing (INDEX-Canonical)

After this file is written, an entry will be inserted at the top of `bridge/INDEX.md`:

```text
Document: gtkb-v1-spec-corpus-distillation-scoping
NEW: bridge/gtkb-v1-spec-corpus-distillation-scoping-001.md
```

## Recommended Commit Type

`docs(bridge):` — scoping proposal only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
