NEW

bridge_kind: prime_proposal
Document: gtkb-fab-23-demoted-cleanup-batch
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4435
Project Authorization: PAUTH-FAB23-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: e45ccf07-99f6-4ad6-b572-570a76a264a2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["$null", ".gtkb/directive-registry.json", ".gitignore", ".gitattributes", ".githooks/**", ".claude/session/**", "scripts/**", "independent-progress-assessments/**", "platform_tests/**"]

No KB mutation: all FAB-23 changes are file archival/deletion (regenerable junk only for deletion; provenance-bearing items archived), `.gitignore`/`.gitattributes` + git-track edits, pre-commit chain consolidation, and a small PowerShell decode-hardening source change; no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-23 — Demoted Near-Miss Cleanup Batch

WI-4435 (FAB-23) of PROJECT-FABLE-INVESTIGATION. Source: the v1 report Appendix A "Demoted near-misses" (14
items). This is the campaign's terminal cleanup cluster. Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md`.

Theme: collect the genuinely-distinct demoted residue into one governed cleanup, while deferring every
Appendix-A item that is an AUGMENTS of a finding already owned by another FAB cluster (anti-duplication).

## Summary

After deduping against the owning clusters, FAB-23 OWNS this distinct residue:

- The 0-byte literal **`$null`** file at repo root — this investigation's own probe residue (read-only
  constraint prevented self-cleanup; it is still present in `git status`).
- **Three competing pre-commit implementations**; only `.githooks/` is active; the inert chains include
  broken + LFS hooks.
- Stale **`.claude/session/`** contents: 6 one-off MemBase-mutating scripts, a 21KB proposal draft, and 8
  accumulated handoff files with no pruning.
- A stale **Agent Red dashboard PDF** sitting in the live platform dashboard output directory.
- **PS-5.1 strict-UTF-8 decode** hardening in scheduled-task automation.
- **`.gtkb/directive-registry.json`** tracking status — canonical state written by tracked VERIFIED code but
  itself neither git-tracked nor gitignored, so fresh clones/worktrees silently lose it.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — WI-4435 is the governed backlog authority for the demoted batch; the dedup
  keeps the deferred items owned by their clusters rather than duplicated.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — git-tracking the directive registry restores fresh-clone parity for a
  canonical state surface; the cleanup removes stale residue.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — archive-not-delete preserves provenance for provenance-bearing
  residue; only pure regenerable junk is deleted.
- `GOV-08` (Knowledge Database is the single source of truth) — the cleanup writes no MemBase state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-23 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

`.claude/rules/project-root-boundary.md` also governs: the `$null` file is an in-root root-level artifact and
its deletion is an in-root operation.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory; Anti-Duplication Guide (the basis
  for the dedup below).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB23-REMEDIATION-20260610` — this cluster's 2 owner AUQ decisions (below).
- _Deferred AUGMENTS route to: FAB-04 (storage / 4058-class), FAB-05 (rule retirement / mojibake), FAB-06
  (narrative / real-orphan subset), FAB-10 (dispatch-INDEX / 4283+3491 terminal-GO closure), FAB-17
  (DA/Chroma / benchmark-CLI + chroma triplication)._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB23-REMEDIATION-20260610`:

1. **Cleanup disposition = Archive provenance, delete junk.** Archive-not-delete provenance-bearing residue
   (stale `.claude/session/` drafts/handoffs and the AR dashboard PDF → an archive dir); delete pure
   regenerable junk outright (the 0-byte `$null` file, truly-dead one-off scripts); consolidate the 3
   pre-commit chains to the active `.githooks/` one (removing the broken + LFS inert chains); harden the
   PS-5.1 strict-UTF-8 decode in the scheduled-task automation.
2. **`.gtkb/directive-registry.json` = Git-track it.** Add it to git so fresh clones and worktrees carry the
   canonical directive registry (it is canonical state written by tracked, VERIFIED code).

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB23-REMEDIATION-20260610`; the
governing specifications (`GOV-STANDING-BACKLOG-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-08`) already constrain the backlog, freshness, and
durable-artifact surfaces. No new requirement is needed; FAB-23 is a disposition of already-verified demoted
residue.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: FAB-23 performs **no bulk backlog/MemBase operation** —
it writes nothing to `work_items` or `groundtruth.db`. The archive step produces an inventory of
archived-vs-deleted residue for review; provenance-bearing items are archived (not deleted) so nothing
auditable is lost. No bulk mutation is authorized by this proposal.

## Scope and Boundaries

In scope: the 6 distinct-residue items listed in Summary, under the two owner dispositions. Out of scope and
explicitly excluded (DEFERRED to the owning cluster per anti-duplication): the benchmark-CLI self-import + 3
ChromaDB stores (FAB-17); the 71 mojibake in 6 legacy files (FAB-05); the scripts/ one-shot scripts + ~190
generated outputs (FAB-04); the orphan-citation real-orphan subset (FAB-06); the no-closure-state for 22
terminal-kind GO entries (FAB-10, the 4283+3491 items). Also out of scope: deploy/push; deletion of any
provenance-bearing artifact (those are archived). The two small AUGMENTS (`codex-session-bootstrap.md` stale
".claude is git-ignored" prose; uncontrolled spec/WI vocabularies) are addressed here only as determined
narrative/doc fixes if not already in FAB-05's retirement scope.

## Proposed Implementation

**Item 1 — `$null` file.** Delete the 0-byte `$null` file at repo root (pure regenerable junk; the
investigation's own probe residue).

**Item 2 — pre-commit consolidation.** Keep the active `.githooks/` chain; remove/retire the two inert
pre-commit chains (the broken one + the LFS one) so a single authoritative pre-commit path remains; document
the chosen chain.

**Item 3 — `.claude/session/` pruning.** Archive the 6 one-off MemBase-mutating scripts, the 21KB proposal
draft, and the 8 accumulated handoff files to an archive dir (provenance preserved); add a pruning convention
so the dir does not re-accumulate.

**Item 4 — AR dashboard PDF.** Archive the stale Agent Red dashboard PDF out of the live platform dashboard
output directory (archive, not delete — it is provenance-bearing).

**Item 5 — PS-5.1 decode hardening.** Harden the strict-UTF-8 decode in the scheduled-task automation so PS
5.1 output does not throw on non-UTF-8 bytes.

**Item 6 — directive registry tracking.** Git-track `.gtkb/directive-registry.json` (add to git; update
`.gitignore`/`.gitattributes` as needed) so fresh clones and worktrees carry the canonical directive
registry.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-23 changes are in-root under `E:\GT-KB\` — the `$null`
file at the repo root, the pre-commit chain under `.githooks/`, the session residue under `.claude/session/`,
the dashboard PDF + archive dir under `independent-progress-assessments/`, the scheduled-task automation
under `scripts/`, the directive registry at `.gtkb/directive-registry.json`, tests under `platform_tests/`,
and this bridge file under `E:\GT-KB\bridge\`. The cluster relocates no application file, touches no
`applications/` subtree, and writes no out-of-root artifact; it in fact REMOVES an in-root junk file and
restores fresh-clone parity for an in-root canonical registry.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (directive registry) | test: `git ls-files .gtkb/directive-registry.json` returns the path (tracked); a fresh-clone simulation carries the registry |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (archive-not-delete) | test: the provenance-bearing items (session drafts/handoffs, AR PDF) exist under the archive dir after the cleanup; only the `$null` file and truly-dead one-offs are absent (deleted) |
| `GOV-08` + repo hygiene (pre-commit) | test: exactly one active pre-commit chain (`.githooks/`) remains wired; the inert broken + LFS chains are gone; the active chain still runs |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (PS decode) | test: the scheduled-task automation decodes non-UTF-8 PS 5.1 output without throwing |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/...`; `ruff check` AND `ruff format --check` on any changed Python |

## Acceptance Criteria

1. The `$null` file is gone from the repo root; the truly-dead one-off scripts are removed.
2. Provenance-bearing residue (session drafts/handoffs, AR PDF) is archived, not deleted; an
   archived-vs-deleted inventory exists.
3. A single active pre-commit chain (`.githooks/`) remains; the inert broken + LFS chains are retired.
4. The PS-5.1 strict-UTF-8 decode is hardened.
5. `.gtkb/directive-registry.json` is git-tracked.
6. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-23-demoted-cleanup-batch-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal
Opposition records `GO`.

## Risk and Rollback

- **Risk — deleting something with hidden value:** only the 0-byte `$null` file and truly-dead one-off scripts
  are deleted; everything provenance-bearing is archived (recoverable). **Rollback:** restore from the archive
  dir / git history.
- **Risk — pre-commit consolidation removes a needed check:** the active `.githooks/` chain is retained and
  re-verified to run; only the inert (broken + LFS) chains are retired. **Rollback:** restore the removed
  chain config from git.
- **Risk — git-tracking the directive registry commits churny runtime state:** the registry is canonical
  state written by tracked code; if it proves churny, `.gitattributes` merge handling or a regenerate-on-clone
  step is the follow-on. **Rollback:** `git rm --cached` and gitignore instead.

## Recommended Implementation Routing

**Cheap-model-draftable once GO'd** for the mechanical deletions/archival/gitignore edits and the PS-decode
hardening; **Opus/Codex finalizes** the pre-commit consolidation (it touches the active enforcement chain) and
confirms the archive inventory. Terminal cluster of the FAB campaign; depends on no other FAB cluster landing
first (the deduped items are owned elsewhere).

## Recommended Commit Type

`chore:` — the dominant change is repo hygiene (junk deletion, provenance archival, pre-commit consolidation,
registry tracking) with a small `fix:` element (the PS-5.1 decode hardening).
