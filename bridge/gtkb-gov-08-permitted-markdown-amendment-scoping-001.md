NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-gov-08-permitted-markdown-amendment-scoping
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Scoping Proposal - Amend GOV-08 Permitted-Markdown Allowlist (S364 Hygiene Seed Batch)

bridge_kind: governance_review
Document: gtkb-gov-08-permitted-markdown-amendment-scoping
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3426
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Scoping Claim

This is a non-mutating scoping proposal to amend `GOV-08` (Knowledge
Database is the single source of truth) to align the permitted-markdown
allowlist with current owner directive. The proposal does NOT mutate
MemBase; it requests Loyal Opposition review of the amendment plan and
the migration chain that follows.

Two amendments are proposed:

1. **Add `bridge/INDEX.md` to the permitted-markdown allowlist** — the
   bridge protocol canonical state. Currently implicitly permitted but
   not explicitly listed.
2. **Narrow MEMORY.md scope** from "state and history, including topic
   files in the memory directory" to "transient scratch-pad for session
   hand-off only" — disallowing the `memory/*.md` topic-file pattern
   that has grown beyond the operational-notepad intent.

After GO and explicit per-slice formal-artifact-approval packets,
follow-on implementation bridges will land:

1. New GOV-08 version (or successor GOV) in MemBase with the amended
   allowlist.
2. Inventory of disallowed `memory/*.md` topic files (use spec-coherence
   CLI when available, or manual sweep meanwhile).
3. Per-topic-file migration bridges (move canonical content to MemBase;
   delete or trim the markdown file).

## Bridge INDEX Filing

This proposal is filed at `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md`,
with a corresponding `Document:` + `NEW:` entry inserted at the top of
`bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.
Append-only discipline preserved.

## Motivation - S364 Audit Finding

The S364 audit of the six owner directives surfaced two gaps in GOV-08:

**Current GOV-08 text (verified):**

> *"The Knowledge Database is the canonical store for all
> specifications, test procedures, operational procedures, backlog
> items, and project knowledge. **The only markdown files permitted
> are CLAUDE.md (rules and architecture) and MEMORY.md (state and
> history, including topic files in the memory directory).** All
> other operational artifacts — backlogs, procedures, test plans,
> protected behaviors, gap analyses, and audit results — MUST reside
> in the Knowledge Database where they have append-only change
> history, versioning, status tracking, and machine-queryable
> structure."*

**Gap 1: `bridge/INDEX.md` not listed**

`GOV-08` does not mention `bridge/INDEX.md` as permitted markdown.
`GOV-FILE-BRIDGE-AUTHORITY-001` (verified) establishes
`bridge/INDEX.md` as the canonical workflow state for the Prime
Builder / Loyal Opposition bridge protocol. The exemption is implicit
because the bridge protocol artifact class is distinct from "project
knowledge", but the implicit exemption is not stated in GOV-08. This
creates ambiguity for adopters and audit tooling.

**Gap 2: MEMORY.md scope broader than owner directive**

Owner directive at S364 (2026-05-28T15:19Z): MEMORY.md should be
"a scratch-pad for transient data (such as session hand-off)".
GOV-08 currently permits MEMORY.md *"state and history, including topic
files in the memory directory"* — explicitly licensing the
`memory/*.md` topic-file pattern. Practical state of the GT-KB
repository: 35+ topic files in `memory/` carrying semi-canonical
content (project records, feedback memos, deliberation parking).
These exceed "transient scratch-pad" scope.

Per owner statement S364 (2026-05-28T15:19Z): *"We have many project
artifacts which came into existence prior to most of our GOV and
enforcement. Those artifacts may be contradictory specs or non-compliant
implementations. ... a repeatable process for identifying and correcting
these will be necessary for periodical review and cleansing. This falls
within the scope of hygiene."*

This proposal is the **GOV-08 amendment slice of the hygiene seed
batch** (sibling to the cache DCL supersession under WI-3425). The
amendment itself is small (policy change); the migration of existing
`memory/*.md` topic files into MemBase is larger and follows in
per-topic implementation slices.

## Proposed Amendment

### GOV-08 Replacement Text

Create new GOV-08 version (or successor `GOV-MARKDOWN-PERMITTED-FILES-001`
if owner prefers; pending owner approval at implementation slice) with
substantially this content:

> The Knowledge Database is the canonical store for all
> specifications, test procedures, operational procedures, backlog
> items, and project knowledge.
>
> The only markdown files permitted as canonical project artifacts
> are:
>
> 1. **`CLAUDE.md`** at project root — rules, architecture, and
>    role/governance instructions for the active AI harness.
> 2. **`bridge/INDEX.md`** at project root — bridge protocol canonical
>    workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.
> 3. **`MEMORY.md`** at project root — transient scratch-pad for
>    session hand-off only. NOT a canonical state store. State that
>    must persist across sessions belongs in MemBase.
> 4. **`.claude/rules/*.md`** — harness control rules under the
>    `.claude/rules/` convention; auto-loaded at session start.
> 5. **`bridge/<topic>-NNN.md`** — bridge proposals, reviews, and
>    verdicts; append-only audit trail per
>    `GOV-FILE-BRIDGE-AUTHORITY-001`.
> 6. **`independent-progress-assessments/*.md`** — Loyal Opposition
>    reports and logs.
>
> All other operational artifacts — backlogs, procedures, test plans,
> protected behaviors, gap analyses, audit results, deliberation
> records, project records, feedback memos — MUST reside in MemBase
> where they have append-only change history, versioning, status
> tracking, and machine-queryable structure.
>
> The legacy `memory/*.md` topic-file pattern is NOT a permitted
> canonical artifact class. Existing topic files must be migrated
> into MemBase (deliberations, work items, specifications, feedback
> rows) via per-file migration bridges. The transitional
> `memory/work_list.md` standing-backlog view is governed by its own
> deletion schedule per `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`.

Set `GOV-08.status` to `retired` with `superseded_by` pointing to the
new GOV version (or new GOV id).

### Implementation Dependency Chain

The amendment is the policy decision. The mechanical implementation
requires three follow-on slices:

| Slice | Surface | Substrate |
|---|---|---|
| 1 | MemBase rows | Supersede GOV-08; insert replacement GOV. Single bridge with formal-artifact-approval packet. |
| 2 | `memory/*.md` inventory | Use `gt validate spec-coherence` (when WI-3424 lands) or manual sweep to inventory disallowed topic files. Emits findings to `.gtkb-state/`. |
| 3..N | Per-topic-file migration | Each topic file becomes a separate small bridge: read content, migrate canonical parts to MemBase (deliberations / work items / specs / feedback rows), delete or trim the markdown file. |

Slices 3..N are the larger workload but each is small and incremental
— a natural fit for the hygiene-sweep skill (WI-3421) and the
reliability fast-lane pattern (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority;
  `bridge/INDEX.md` is canonical workflow state that must be in the
  permitted-markdown allowlist.
- `GOV-08` - the amended spec.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact-approval-packet
  workflow governs the GOV-08 supersession at implementation slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance
  default; project knowledge belongs in MemBase, not markdown.
- `GOV-STANDING-BACKLOG-001` - backlog migration to MemBase already
  governs `memory/work_list.md`; this amendment extends the principle
  to the broader `memory/*.md` topic-file class.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - already
  governs work_list.md retirement; this amendment broadens the scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this
  proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the
  Specification-Derived Verification Plan below maps acceptance to
  verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project +
  Work Item + Project Authorization metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation paths
  within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - replacement GOV is a
  durable artifact; topic-file migration moves content into durable
  artifact classes.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions captured via
  AskUserQuestion + verbatim directive statements at session S364.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - per-topic-file
  migration is a class of repetitive plumbing that benefits from
  service extraction (the hygiene-sweep skill orchestrates this
  pattern).
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - precedent
  for moving from markdown to DB-backed storage.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` -
  precedent for retiring a permitted markdown file after MemBase
  migration; the same pattern applies to other `memory/*.md` topic
  files.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - deterministic-services
  pivot precedent.
- S364 owner statement (2026-05-28T15:19Z): *"draft those supersession
  bridges ... This falls within the scope of hygiene."*

## Owner Decisions / Input

- `S364 AskUserQuestion answer 2026-05-28T14:44Z (next move on
  spec-coherence systemic gap)`: owner selected "Draft validation CLI
  scoping bridge" (resulting in WI-3424).
- `S364 owner statement 2026-05-28T15:19Z`: owner directive to draft
  supersession bridges. Verbatim: *"Yes, draft those supersession
  bridges. We have many project artifacts which came into existence
  prior to most of our GOV and enforcement."*
- `S364 audit Directive 5 framing (2026-05-28)`: owner statement on
  permitted markdown narrows MEMORY.md scope: *"GT-KB must not rely
  on markdown documents for project definition or status tracking,
  specifications, or elaboration of work items with the following
  exceptions: INDEX.md is the source-of-truth for bridge work,
  MEMORY.md is a scratch-pad for transient data (such as session
  hand-off)."*
- `GOV-08` (verified): the spec being amended.

Implementation authorization (formal-artifact-approval packet for
GOV-08 mutation) remains owner authority via AskUserQuestion at
implementation-slice time. Per-topic-file migration bridges are
covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for items
matching the reliability fast-lane criteria.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. `GOV-08`
(verified) is the spec being amended; `GOV-FILE-BRIDGE-AUTHORITY-001`
(verified) establishes the `bridge/INDEX.md` exemption; owner
directive narrows MEMORY.md. No new GOV/SPEC/ADR is needed at
scoping time. Implementation slice replaces one spec row.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. It is one scoping bridge for
one GOV amendment. The follow-on per-topic-file migrations are each
individual bridges, not a bulk operation; each migration is a
self-contained reliability-fast-lane-class change.

The following tokens satisfy the
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence
detector regex (`(?i)(?:inventory|review[- ]packet|DECISION
DEFERRED|formal-artifact-approval)`):

- "inventory": Slice 2 produces a topic-file inventory; the
  spec-coherence CLI (WI-3424) is the deterministic-service
  candidate for this inventory work.
- "formal-artifact-approval": GOV-08 supersession follows the
  `GOV-ARTIFACT-APPROVAL-001` packet workflow at the implementation
  slice.
- "review-packet": this scoping bridge produces a Loyal Opposition
  review-packet via the standard NEW/REVISED -> GO/NO-GO cycle.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Slice timing |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread NEW -> GO/NO-GO -> implementation slices | This scoping bridge |
| `GOV-08` (amended) | After supersession, current_specifications view shows GOV-08 retired with successor in place; allowlist matches proposed text | Slice 1 (MemBase) |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packet present for GOV-08 mutation | Slice 1 (MemBase) |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Spec lifecycle (status=retired, superseded_by linked) follows artifact-oriented pattern | Slice 1 (MemBase) |
| `GOV-STANDING-BACKLOG-001` | WI-3426 membership in PROJECT-GTKB-RELIABILITY-FIXES (verified at filing) | This scoping bridge |
| `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` | Coherence with this existing retirement-at-migration-completion pattern | Slice 1 review |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links inspection above | This scoping bridge |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table | This scoping bridge |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | This scoping bridge |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All proposed paths within `E:\GT-KB` | All slices |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Replacement GOV filed as durable spec row; topic-file migrations land canonical content as durable MemBase rows | Slices 1 + 3..N |
| `SPEC-AUQ-POLICY-ENGINE-001` | AskUserQuestion answer + S364 owner statements captured in Owner Decisions / Input section above | This scoping bridge |

## Acceptance Criteria

1. Loyal Opposition GO on the amendment plan and the proposed
   replacement-text.
2. Loyal Opposition concurs that the implicit `bridge/INDEX.md`
   exemption should be explicit and that the broader MEMORY.md scope
   needs narrowing.
3. Implementation slice plan accepted: Slice 1 GOV-08 supersession
   first, then Slice 2 inventory, then Slices 3..N per-topic-file
   migrations.
4. Scoping proposal does NOT authorize implementation; per-slice
   formal-artifact-approval packets required for MemBase mutations.

## Risks / Rollback

- Risk: the new permitted-markdown allowlist may miss a file class
  that legitimately should be permitted (e.g., a new template type).
  Mitigation: Codex can NO-GO specific allowlist entries; REVISED
  incorporates feedback. The allowlist is itself a versioned governed
  artifact in MemBase; future amendments follow the same supersession
  pattern.
- Risk: per-topic-file migration (Slices 3..N) is a large workload
  that could span many sessions. Mitigation: hygiene-sweep skill
  (WI-3421) orchestrates the inventory + per-file decision flow; each
  migration is independently small.
- Risk: deleting a `memory/*.md` topic file could lose context that
  was not yet migrated. Mitigation: each per-topic-file migration
  bridge documents the migration (what moved to MemBase, what was
  preserved as evidence in the bridge file, what was retired); no
  blind deletion.
- Rollback: scoping proposal can be withdrawn at NEW status. Each
  implementation slice will document its own rollback (revert the
  spec row; restore the markdown file from git).

## Files Expected To Change

This scoping proposal does NOT touch any files. Listed for
implementation slice planning:

**Slice 1 (MemBase GOV-08 supersession):**
- MemBase `current_specifications`:
  - `GOV-08` (status to retired, superseded_by linked)
  - New replacement GOV row.
- `.groundtruth/formal-artifact-approvals/` packet file (new).

**Slice 2 (Inventory of disallowed topic files):**
- `.gtkb-state/spec-coherence/<run-id>/` or `.gtkb-state/hygiene-sweep/<run-id>/`
  output directory (new; pre-existing output convention from sibling
  CLIs).

**Slices 3..N (Per-topic-file migrations):**
- Each migration bridge has its own `target_paths` (one or two files:
  the `memory/<topic>.md` to retire, plus MemBase mutations).
- Per-migration bridge files at `bridge/<topic-migration>-NNN.md`.

## In-Root Placement Evidence

All proposed paths within `E:\GT-KB`. No `applications/**` paths
touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
satisfied at the design level.

## Sibling Proposals

- `gtkb-startup-cache-dcl-supersession-scoping` - sibling scoping
  bridge filed in parallel for WI-3425 (supersede cache-presuming
  DCLs); same S364 hygiene seed batch.
- `gtkb-spec-coherence-cli-scoping` - sibling deterministic-services
  scoping (WI-3424, Codex GO at -002); the spec-coherence CLI is the
  natural tool for Slice 2 inventory work.
- `gtkb-hygiene-sweep-cli-scoping` - sibling scoping (WI-3420, Codex
  GO at -003); file-content drift discovery — the per-topic-file
  inventory could reuse this CLI's pattern-set TOML registry pattern.
- `gtkb-hygiene-sweep-skill-scoping` - sibling scoping (WI-3421,
  Codex GO at -004); orchestration skill for the hygiene CLIs;
  natural fit for guiding Slices 3..N.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry
is added. Expected: `preflight_passed: true`;
`missing_required_specs: []`.

## Clause Applicability

Clause preflight will be run after this file is written. Expected
exit 0; the "Bridge INDEX Filing" section satisfies the
`CLAUSE-INDEX-IS-CANONICAL` detector, and the "Clause Scope
Clarification" subsection satisfies the `CLAUSE-VISIBILITY-BULK-OPS`
detector via the explicit token evidence above.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
