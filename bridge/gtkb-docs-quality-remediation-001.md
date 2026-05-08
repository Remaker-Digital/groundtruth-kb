# GTKB-DOCS-QUALITY-REMEDIATION — Slice 0: Scoping And Sequencing

**Status:** NEW
**Author:** Prime Builder (claude harness B)
**Date:** 2026-05-07
**Session:** S336

## Purpose

Convert the Loyal Opposition NO-GO findings in
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md`
into a bridge-mediated, multi-slice remediation project.

This slice (slice 0) is **scoping only**. It proposes the umbrella project
name, the implementation-slice decomposition, the slice ordering, and the
slice-0 acceptance criteria for Loyal Opposition review. It does NOT
implement any documentation change. Each subsequent slice (1 through 7)
will land as a separate bridge proposal at
`bridge/gtkb-docs-quality-remediation-slice-N-<topic>-001.md` with its own
`Specification Links`, test plan, and Codex GO before any file edits occur.

## Specification Links

**Required (cross-cutting, blocking — per `config/governance/spec-applicability.toml`):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — all bridge work honors the file-bridge
  authority model. Triggered by `bridge/**` path scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals must
  cite every relevant governing specification. Triggered by content
  ("Specification Links", "implementation proposal").
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must be
  derived from linked specifications. Triggered by content
  ("verification", "VERIFIED"). Carried forward to per-slice proposals.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement
  honored. Triggered by content ("Agent Red") because slice 1 affects the
  workspace-root README's repo-identity story.

**Required (rule-cited soft authority):**

- `.claude/rules/file-bridge-protocol.md` — proposal/review/verification
  protocol. Specifically the "Mandatory Specification Linkage Gate",
  "Mandatory Pre-Filing Preflight Subsection", "Mandatory
  Specification-Derived Verification Gate", and "Mandatory Owner Decisions
  / Input Section Gate".
- `.claude/rules/codex-review-gate.md` — no implementation without Codex GO.
- `.claude/rules/operating-model.md` §1, §2, §3 — canonical terminology
  ("application", "platform", "hosted application", "specification",
  "release") and the implemented-vs-intended discipline applied to docs.
- `.claude/rules/loyal-opposition.md` — LO authority over cited
  requirements; the LO INSIGHTS report is the originating evidence.
- `.claude/rules/project-root-boundary.md` — Agent Red is a separate
  project; the workspace-root README must not present Agent Red as the
  GT-KB landing page (slice 1, LO finding F1).
- `.claude/rules/bridge-essential.md` — smart-poller-first /
  retired-OS-poller-disabled topology (slice 5, LO finding F5).
- `.claude/rules/canonical-terminology.md` — version-coherence and
  "bridge"-vs-"poller" disambiguation (slices 4 and 5; LO findings F4, F5).

**Advisory (cross-cutting, advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — concrete requirements/decisions
  preserved as durable artifacts. The LO INSIGHTS file is the durable
  artifact; this proposal references it by path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — slice progression uses
  candidate/active/verified states.

**Originating evidence:**

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md`
  — LO NO-GO findings F1 through F8, recommended implementation sequence,
  expected file touchpoints, verification plan.

## Prior Deliberations

A targeted search of the Deliberation Archive at proposal time did not
surface a prior remediation umbrella for public-docs quality at this scope.
Adjacent prior work likely-relevant to per-slice proposals:

- Bridge automation halts/restorations (slice 5 cross-reference): see
  S290–S294 incident history in `.claude/rules/bridge-essential.md`
  §"Incident History (Lessons Encoded)".
- Repo-identity migration commits: `dbe21f94` ("Migrate repo references
  to mike-remakerdigital/agent-red"), `31c51ceb` ("GitHub project
  refresh — README, issue templates, SECURITY.md") — these introduced the
  current Agent Red root README. Slice 1 reverses that for the GT-KB repo.

Each per-slice proposal will run a focused
`search_deliberations()` for its specific topic before filing.

## Scope

The umbrella project is named **GTKB-DOCS-QUALITY-REMEDIATION**.

It comprises **seven implementation slices** mapped from LO findings F1
through F8. Slice ordering follows the LO report's "Recommended
Implementation Sequence" (slice-0 evidence section §Recommended
Implementation Sequence).

| Slice | LO finding(s) | Topic | Estimated scope |
|---|---|---|---|
| 1 | F1 | Workspace-root `README.md` rewrite as GT-KB repository landing page | 1 file rewrite + verification grep |
| 2 | F2 | Docs CI repair — `scripts/check_docs_cli_coverage.py` and `mkdocs build --strict` both green | `groundtruth-kb/docs/reference/cli.md` updates, version-string updates, release-notes link or relocation, MkDocs/Material warning resolution |
| 3 | F3 | Beginner-facing commands and API examples corrected; executable snippet test suite added | `docs/start-here.md`, `docs/user-journey.md`, `docs/day-in-the-life.md`, `docs/tutorials/first-spec.md`, `docs/bootstrap.md`, `docs/cto-evaluation.md`; new `tests/docs/` |
| 4 | F4 | Version-coherence sweep with single source of truth | `groundtruth-kb/README.md`, `docs/known-limitations.md`, `docs/architecture/product-split.md`; lint or generation rule |
| 5 | F5 | Bridge automation docs scrubbed to smart-poller-first semantics | `docs/start-here.md`, `docs/architecture/product-split.md`, `docs/method/12-file-bridge-automation.md`, `docs/reference/templates.md` |
| 6 | F6, F7 | MkDocs nav cleanup + archival/internal report sanitization | `mkdocs.yml`, relocation/labeling of `docs/reports/agent-red-classification.md` |
| 7 | F8 | Project-specific markdownlint config + CI job | new markdownlint config, `groundtruth-kb/.github/workflows/docs-check.yml` addition |

Each slice will:

1. File its own bridge proposal at
   `bridge/gtkb-docs-quality-remediation-slice-N-<topic>-001.md`.
2. Include `Specification Links` for the slice-specific governing rules
   (e.g., slice 1 cites `project-root-boundary.md`; slice 5 cites
   `bridge-essential.md`).
3. Define spec-derived tests or verification commands.
4. Wait for Codex GO before any file edits.
5. File a post-implementation report at the next `-NNN.md` version with
   spec-to-test mapping and observed results, and wait for Codex VERIFIED.
6. Land as a single scoped commit per slice (no slice bundling).

## Slice Ordering Rationale

Slice 1 (root README) first because it is the highest first-impression
defect, lowest risk, and unblocks evaluation of the repo-identity surface
before any other docs work proceeds against the wrong identity.

Slice 2 (docs CI green) before slice 3 (executable beginner docs) because
the CI gate is the durable signal; broken CI obscures further drift.

Slice 3 (executable beginner docs) is the highest single-finding effort
and the largest content-rewrite surface; placing it after CI repair means
the new tests run under a passing CI rather than a red one.

Slice 4 (version coherence) after slice 2 because slice 2 already touches
the canonical version string in `start-here.md`; slice 4 generalizes that
to a single source of truth.

Slice 5 (bridge automation docs) is independent of slices 1–4 but ordered
fifth because the smart-poller activation tutorial already lives outside
the affected pages, so the rewrite is content-only and benefits from
operating against a stable docs CI.

Slice 6 (nav + archival) and slice 7 (markdownlint) are last because they
are surface/style cleanup; they should not run before the substantive
content slices, otherwise nav and lint config will change again.

## Acceptance Criteria — Slice 0

For Codex to issue **GO** on this slice-0 scoping proposal, all of the
following must hold:

- The umbrella project name `GTKB-DOCS-QUALITY-REMEDIATION` is acceptable
  or a substitute name is proposed in NO-GO.
- The seven-slice decomposition covers LO findings F1 through F8 without
  silent omission.
- The slice ordering is acceptable or a counter-ordering is proposed in
  NO-GO.
- The slice-0 / per-slice proposal split is acceptable as a workflow
  pattern.
- Loyal Opposition records its judgment on whether F2 should be split
  into two slices (CLI-coverage script vs. MkDocs strict) or remain
  combined; this proposal recommends combined, but defers the call to LO.

For Codex to issue **VERIFIED** on this slice 0:

- The slice-0 commit lands the proposal file and the INDEX.md NEW entry
  only — no documentation changes outside `bridge/`.
- The companion umbrella row is added to `memory/work_list.md` with the
  governing-evidence citation pointing to the LO INSIGHTS file.

## Test Plan

Slice 0 is scoping-only and does not modify production code or docs.
Verification is documentation-only:

1. `git diff --stat develop -- bridge/gtkb-docs-quality-remediation-001.md`
   shows the proposal file as the only `bridge/` addition for this slice.
2. `git diff --stat develop -- bridge/INDEX.md` shows the NEW entry inserted
   at the top of the index.
3. `git diff --stat develop -- memory/work_list.md` shows the umbrella row
   added with a governing-evidence citation.
4. `python scripts/bridge_applicability_preflight.py --bridge-id
   gtkb-docs-quality-remediation` reports `preflight_passed: true` with
   `missing_required_specs: []`.
5. No file outside `bridge/`, `memory/work_list.md`, or this proposal text
   is touched in the slice-0 commit.

Per-slice test plans (slices 1–7) are deferred to each slice's own
proposal, which will derive tests from the slice-specific
`Specification Links`.

## Risk And Rollback

**Risk:** None for slice 0 itself — it adds three artifacts (proposal,
INDEX entry, work-list row) and changes no production code or public docs.

**Risk for the umbrella project:** the seven-slice plan represents a
material multi-session effort. If priorities shift, the plan is
abandonable at any slice boundary; abandoned slices remain visible in
INDEX.md as NEW or REVISED entries without a GO, and the umbrella row in
`memory/work_list.md` records the partial-completion state.

**Rollback (slice 0):** revert the slice-0 commit. The INDEX entry and
the proposal file are append-only and would be reverted as a unit. No
production state changes.

## Owner Decisions / Input

- **2026-05-07, AskUserQuestion answer (S336):** Mike selected "Full
  8-finding remediation" in response to the question "How do you want to
  scope the response to the documentation-quality NO-GO?" presented after
  Mike's chat-relay of the LO INSIGHTS verdict. The selection authorizes
  the umbrella project covering F1 through F8 (i.e., all P1+P2+P3 findings).

- **Owner approval scope:** the AUQ answer authorizes the *umbrella
  project scope and slice 0 scoping work*. It does NOT authorize
  implementation of any individual slice. Each slice's bridge proposal
  must obtain its own Codex GO; no implementation slice is pre-approved
  by this scoping selection.

- **Pending owner choice (deferred to per-slice proposals or
  case-by-case):** the LO report (§Open Owner Decisions) notes a later
  positioning question — whether the GitHub root presents GT-KB as a
  package-only toolkit, an Internal Developer Platform, or both. That
  positioning question is in scope for slice 1 (the README rewrite) and
  will be raised via AskUserQuestion at slice-1 proposal time, not now.

## Recommended Commit Type

`chore` — slice 0 adds bridge infrastructure (one proposal file, one
INDEX entry, one `memory/work_list.md` row). No new capability surface, no
production code change, no test-suite change. The follow-on slice commits
will use slice-appropriate Conventional Commits types (e.g., slice 1
likely `docs:`, slice 2 likely `fix:` because it repairs a red CI, slice
3 likely `docs:` + `test:` if commits are separated).

## Files Changed (slice 0 only)

- `bridge/gtkb-docs-quality-remediation-001.md` (this file, NEW).
- `bridge/INDEX.md` (insert NEW entry at top).
- `memory/work_list.md` (add umbrella row with LO INSIGHTS citation).

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing
Preflight Subsection", the
`python scripts/bridge_applicability_preflight.py --bridge-id
gtkb-docs-quality-remediation` invocation will be run after this file is
saved and the INDEX entry is added. Result will be reported in the chat
turn that completes slice-0 filing; if the preflight reports any
`missing_required_specs`, the proposal will be revised before Codex
review begins.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
