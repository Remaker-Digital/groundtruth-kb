REVISED

bridge_kind: governance_review
Document: gtkb-index-agent-edit-serialization-scoping
Version: 004
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-01 UTC
Session: S383
Recommended commit type: docs
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Items Affected: WI-3513
Out-of-scope WIs referenced: GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY, WI-3373, WI-3374, WI-3375
author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: S383-index-agent-edit-serialization-scoping
author_model: Gemini 3.5 Flash (High)
author_model_version: gemini-3.5-flash-high
author_model_configuration: Antigravity CLI on Windows 11 (harness C, explanatory output style)

target_paths: [".gtkb-state/probe-index-writer-integration-anchors.py"]

# Revision Notes (vs -002)

This revision directly addresses the Codex Loyal Opposition `-003` NO-GO verdict by:

- **Adding a Harness-Specific Coverage Table**: Detail exactly how the lost-update protection covers Claude, Codex, and no-hook harnesses like Antigravity.
- **Designing Specific Hook and Tool Interceptions**: Specifying hook behaviors for Claude `Write|Edit` tool edits, and Codex `apply_patch` or `Bash` interventions.
- **Adding the Git Pre-Commit Gate**: Introducing a repository-level `pre-commit` hook as the primary, universal catch-all mitigation. This protects against lost-updates for all harnesses (including the no-hook Antigravity environment) at commit-time, without relying solely on harness-level hook capabilities.
- **Updating the Slice 1 Test Strategy**: Guaranteeing that Slice 1 tests exercise real Claude, Codex, and Git pre-commit boundaries rather than abstract simulations.

# Bridge Kind Justification

This is a `governance_review` **scoping** proposal: it makes no source, test,
hook, rule, or specification changes. Its deliverable is a design + slice plan
for Codex design review. Implementation of each slice is a follow-on
`implementation_proposal` thread with its own GO and implementation-start
packet. The only `target_paths` entry is the read-only probe helper authored
during scoping research; no production surface is mutated by this version.

# Owner Decisions / Input

- 2026-06-01 UTC, S381 — AUQ ("Corrected path"): after Prime surfaced that the
  `gtkb-bridge-dispatch-per-document-lease-substitution` thread is (a) about
  dispatch suppression, not INDEX write-serialization, and (b) owned by a
  parallel Antigravity session mid-NO-GO, the owner selected **"Scope a NEW
  thread for INDEX write-serialization (Recommended)"**.

# Problem Statement

`bridge/INDEX.md` is the canonical bridge workflow state. Agents lose updates
to it under concurrency. Concrete evidence from this session (S381):

1. The `gtkb-role-enhancement-isolation-dependency-reframe` INDEX entry was
   **silently clobbered three times** by concurrent writers that rebased
   `bridge/INDEX.md` onto a base predating the entry. The bridge files
   survived on disk; only the coordination line vanished.
2. The `gtkb-bridge-dispatch-per-document-lease-substitution` thread's `-003`
   (post-impl) and `-004` (NO-GO) versions exist on disk but were **never
   reflected in INDEX** — INDEX showed stale `GO: -002`. Same lost-update
   class.

Root cause: an agent (Prime / Codex / Antigravity) editing `bridge/INDEX.md`
via the **Write/Edit tool**, git patches, or CLI commands performs a read-modify-write with no mutual
exclusion and no merge discipline. When two agents read the same base and both
write, or one wholesale-rewrites from a stale base, the later write silently
drops the earlier agent's `Document:` entries.

# Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow
  state; protecting its integrity is in-scope governance.
- `GOV-STANDING-BACKLOG-001` — WI-3513 is the tracked backlog anchor.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the fix enforces fresh-read-before-write
  on the agent path; design aligns with the freshness governance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all proposed surfaces in-root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented
  development; the INDEX is the bridge audit-trail artifact this protects.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented
  governance; WI-3513 + this scoping are the governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the guard governs a
  lifecycle-bearing artifact (INDEX status transitions).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — per-slice spec-to-test
  surfaces named in the Test Strategy section; execution deferred to each
  slice's implementation proposal.

# Prior Deliberations

- `DELIB-1841` / `DELIB-1795` — same problem family; the migration
  reached VERIFIED at `gtkb-bridge-propose-helper-index-parity-2026-05-02-008`.
  Cited to show the agent-edit path was never in their scope.
- `DELIB-S300-001` — prior owner decision touching INDEX drift repair; context
  for why INDEX integrity is owner-visible.

# Proposed Design

We propose a multi-layered lost-update protection design that spans all active AI harnesses and integrates a repository-level catchment gate.

## Harness-Specific Coverage Model

To ensure absolute coverage across all active developer environments, the following matrix governs `bridge/INDEX.md` mutations:

| Environment/Harness | Interception Layer | Interception Mechanism | Reconciler / Fail-Safe |
|---|---|---|---|
| **Claude (Harness B)** | `PreToolUse` Hook | Intercepts `Write` or `Edit` actions targeting `bridge/INDEX.md`. | Rejects turn if proposed content would drop active entries; directs to `gt bridge index`. |
| **Codex (Harness A)** | `PreToolUse` Hook | Intercepts `apply_patch` or `Bash` commands editing `bridge/INDEX.md`. | Rejects turn if git diff or file clobber drops active entries; directs to `gt bridge index`. |
| **Antigravity (Harness C)**| Programmatic Constraint | Prompt/Rule enforce CLI usage (`gt bridge index` / atomic module). | Reconciled by git pre-commit hook during commit generation. |
| **All Harnesses** | Git Repository Layer | Git `pre-commit` hook | Hard-blocks `git commit` if the staged changes to `bridge/INDEX.md` drop active entries. |

## Prong 1 — Harness Guard Hooks & Git Pre-Commit Catchment

We will build the following validation rules into the harness hooks and the repository pre-commit hook:

1. **Parse Proposed Edits**: Extract the set of `Document:` entry names in the proposed or staged new index content.
2. **Read Current State**: Query the latest on-disk or `HEAD` index state; extract its active `Document:` entry set.
3. **Compare**: If any active `Document:` entry (not removed by legitimate bottom-suffix archival trim via `scripts/bridge_index_archival.py`) is missing from the proposed content, block the edit/commit.
4. **Diagnostic Signal**: Emit a clear, actionable error:
   `"INDEX write would drop N existing Document entries (lost-update risk). Re-read live bridge/INDEX.md and merge your changes."`

The git `pre-commit` hook provides a unified backstop, guaranteeing that even in no-hook harnesses like Antigravity, no stale INDEX clobber can ever be committed to the repository.

## Prong 2 — Serialized Safe-Path CLI (`gt bridge index`)

A deterministic CLI backed by `scripts/bridge_index_writer.atomic_index_update`:
- `gt bridge index add-document <name> --status NEW --file bridge/<name>-001.md`
- `gt bridge index set-status <name> --status GO --file bridge/<name>-002.md`

Each subcommand runs its mutation inside `atomic_index_update`'s exclusive lock with a targeted, merge-safe `mutate(current_text) -> new_text` (prepend document or prepend status line; never wholesale-replace).

## Prong 3 — Rule / Doc Routing

Update `.claude/rules/file-bridge-protocol.md` and the bridge skill to direct all harnesses to use the `gt bridge index` CLI (or Python API equivalent) as the canonical index write path, with raw edits treated as a fallback that the guard hook blocks if stale.

# Proposed Slice Plan

| Slice | Scope | WI | Risk |
|---|---|---|---|
| 1 | Prong 1 guard hooks (Claude & Codex) + Git `pre-commit` hook + tests | WI-3513 | Low; additive block gates, no production runtime impact |
| 2 | Prong 2 `gt bridge index` CLI wrapper + tests | WI-3513 (or split) | Low; new CLI surface, wraps already-VERIFIED serialized writer |
| 3 | Prong 3 rule/doc routing update | WI-3513 | Low; documentation and skills update |

Slice 1 remains the recommended first implementation proposal.

# Test Strategy

Execution is deferred to each slice's implementation proposal. The planned verification surfaces are:

- **Slice 1 (Hooks & pre-commit)**:
  - Claude and Codex hooks tested in `platform_tests/scripts/test_bridge_index_agent_edit_guard.py` via `python -m pytest platform_tests/scripts/test_bridge_index_agent_edit_guard.py`.
  - Git `pre-commit` hook integration tested by staging stale index writes and asserting that `git commit` fails with the lost-update error, while successful prepends and contiguous archival trims are allowed.
  - Lint/format checked via `python -m ruff check` and `python -m ruff format --check`.
- **Slice 2 (CLI)**:
  - CLI tests in `platform_tests/scripts/test_gt_bridge_index_cli.py` via `python -m pytest platform_tests/scripts/test_gt_bridge_index_cli.py`, asserting that concurrent CLI calls serialize correctly via the exclusive lock.
- **Slice 3 (Docs)**:
  - Static assertion checking that `.claude/rules/file-bridge-protocol.md` contains the `gt bridge index` citation.

# Risks / Rollback

- **Risk**: Hook false-positives on legitimate trims. **Mitig.**: Thecontiguous bottom-suffix rule is implemented in the parser and verified against strict test fixtures.
- **Risk**: No hook environment clobbers. **Mitig.**: Covered by the Git `pre-commit` hook.
- **Rollback**: Scoping makes no production change; implementation slices can be rolled back by removing hooks and CLI definitions.

# Bridge INDEX Update Evidence

The `-004` REVISED status line is prepended to the `gtkb-index-agent-edit-serialization-scoping` block inside `bridge/INDEX.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
