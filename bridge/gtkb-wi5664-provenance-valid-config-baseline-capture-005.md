NO-ACTION
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5664 Configuration Baseline Capture — WI-5640 Isolation Hold

bridge_kind: operational_state_change
Document: gtkb-wi5664-provenance-valid-config-baseline-capture
Version: 005
Responds to: bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664
target_paths: []

## Disposition

No configuration capture or skill-reference implementation may proceed through
this chain. Version 004 correctly establishes that all five proposed
`config/agent-control/gtkb-*` baseline files are the still-untracked WI-5640
file-move apply. Committing them under WI-5664 would violate the owner’s
explicit `DELIB-202667194` isolate-skill-rename decision.

No target was changed or staged. The five candidates remain untracked foreign
evidence. The real index still contains only the unrelated staged WI-5661 hunk
provenance report, which is preserved untouched.

## Reproduced Blocking Evidence

- `git ls-files --error-unmatch` finds no tracked baseline for the five
  proposed `gtkb-*` configuration targets.
- The four rule candidates and command-surface candidate still contain the
  retired bare `verify` / `bridge-propose` / `proposal-review` references, so
  byte-equality and projection checks do not prove the WI-5664 correction.
- The rule-projection generator currently treats the untracked `gtkb-*` rules
  as canonical. Editing only the tracked `.claude/rules` projections would
  intentionally fail the 38-projection parity gate; editing or committing the
  untracked canonical candidates would absorb WI-5640 work.
- Working-byte equality is insufficient for commit evidence because Git’s LF
  normalization can change staged blobs. A later proposal must bind acceptance
  to staged blob IDs or explicitly specified LF-normalized bytes.

## Clear Condition

Resume WI-5664 only after the separate WI-5640 lifecycle supplies a governed,
tracked canonical baseline for the affected `config/agent-control/gtkb-*`
files, or a governed replacement explicitly selects a different authority
direction. Then file a fresh provenance-valid WI-5664 proposal that:

1. cites `DELIB-202667194` and the governing WI-5640 baseline evidence;
2. inventories every exact bare-to-`gtkb-*` substitution across canonical
   rules, projections, command-surface source, compatibility mirror, and
   packaged snapshot;
3. asserts zero retired bare references after the staged patch;
4. proves staged/blob-level parity using declared normalization semantics; and
5. excludes every WI-5640 line not contained in the separately governed
   baseline commit.

The independently trackable command-surface correction may be included in that
fresh proposal, but it does not make the blocked rule-mirror outcome complete
and must not be used to terminally close WI-5664 by itself.

## Requirement Sufficiency

The WI-5664 skill-reference requirement is sufficient, but its current
canonical precondition is not satisfied. This is a dependency/authority hold,
not a new owner-choice request. `DELIB-202667194` already requires WI-5640 work
to remain in its own governed lifecycle.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-WORK-TREE-HYGIENE-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

- `DELIB-202667193` — authorizes the skill-rename sweep with independent
  per-slice gates.
- `DELIB-202667194` — requires govern-existing hunk isolation and explicitly
  excludes the un-GO’d WI-5640 file-move apply from sweep commits.
- Version 004 — independently confirms both the ownership conflict and the
  missing exact-reference/blob-level verification.

## Owner Decisions / Input

No new owner decision is requested. The owner has already selected separate
WI-5640 governance; this disposition preserves that boundary.

## Pre-Filing Preflight Subsection

Applicability and mandatory ADR/DCL clause preflights must pass against this
completed disposition before filing.

## Specification-Derived Verification

- Direct Git tracking checks establish that all five capture candidates lack a
  committed baseline.
- Exact reference scans reproduce retained bare names in the five candidates.
- The current projection relationship proves a tracked-only rule edit would be
  red rather than a complete repair.
- No implementation tests, formatting, staging, commit, or source mutation are
  run under this NO-ACTION disposition.

## Risk And Rollback

Proceeding would canonize an unapproved cross-program migration and still leave
the actual stale references intact. This hold avoids both failures. No
implementation mutation occurred, so no rollback is required; bridge history
remains append-only.
