NEW

bridge_kind: prime_proposal
Document: gtkb-bridge-revise-cli-slice-1
Version: 001
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: feat
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS
Work Item: WI-3429
Owner Decision: DELIB-20260623
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

# `gt bridge revise` CLI — Slice 1 (core mechanism + mechanical fix-classes)

## Summary

Implement WI-3429 Slice 1: a deterministic `gt bridge revise` CLI that replaces
per-cycle AI-authored REVISED bridge filings with a single command. Evidence
(this project's own batch-1 reconciliation thread): a mechanical REVISED cycle
— carry forward unchanged content, add a citation, widen `target_paths`, re-run
preflights — consumed multiple NO-GO rounds and thousands of tokens of
hand-copied boilerplate that a deterministic transform produces in
milliseconds. This directly serves `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
and the owner's operational-load-reduction objective.

WI-3429 is large (7 steps, 6 fix-classes). This slice builds the **rigid core**
plus the three highest-frequency *mechanical* fix-classes; the structural
fix-classes are deferred to Slice 2 (see Scope below). "Bias toward rigidity,
accept relaxation later" per the WI's S367 owner meta-policy note.

## Scope

### Slice 1 (this proposal)

Core mechanism (all 7 WI-3429 steps, wired to existing primitives):

1. Resolve the latest indexed-operative file for `--thread <slug>` (the current
   top-of-stack Prime-authored `NEW`/`REVISED` file via the same operative-file
   resolution the preflights use).
2. Carry forward its content byte-identically.
3. Apply the named fix via a fix-class dispatch table.
4. Bump the version number (max on-disk + INDEX, +1).
5. Write the new bridge file via the scanner-safe path
   (`scan_credential_hits` + `handle_hits_abort_or_redact` +
   `ensure_author_metadata` from `write_bridge.py`).
6. Update `bridge/INDEX.md` atomically with the `REVISED` status line
   (`bridge_index_writer.atomic_index_update` driving
   `write_bridge.compose_index_update(slug, new_version, "REVISED", text)`).
7. Re-run `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py`
   on the new operative file and surface both results.

Fix-classes implemented in Slice 1 (the mechanical ones):

- `content_carryforward_only` — version bump with byte-identical content (e.g.,
  re-file after a concurrent INDEX clobber). No content args.
- `citation_add` — append one or more spec IDs to the `## Specification Links`
  section (`--add-citation SPEC-ID`, repeatable). Idempotent (skips IDs already
  present).
- `target_paths_add` — append one or more concrete paths to the `target_paths`
  block (`--add-target-path <path>`, repeatable). Idempotent.

Surfaces: `--thread`, `--reason` (required; recorded in a
`Responds to: ... (revise: <reason>)` line and the version's provenance),
`--fix-class`, the class-specific repeatable options above, and `--dry-run`
(prints the would-be new file + INDEX line; writes nothing).

### Slice 2 (deferred; NOT this proposal)

Structural fix-classes requiring content-structure parsing:
`target_paths_glob_widen`, `partition_update`, `pauth_swap`. Tracked as
follow-on; this proposal does not implement them and `--fix-class` rejects them
with a "deferred to Slice 2" message so the surface fails closed.

## Owner Decisions / Input

- Owner instruction this session: **"tackle the 5 remaining WIs"**, and AUQ
  selection **"Operational-load CLIs first"** (2026-06-03), recorded as
  `DELIB-20260623`. WI-3429 (`gt bridge revise`) is the first operational-load
  CLI in that sequence.
- Implementation is authorized by project-scoped authorization
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS` (active;
  owner decision `DELIB-20260623`; included work item WI-3429; allowed mutation
  classes `source`, `test_addition`, `cli_extension`).
- WI-3429's own description (S367) records the owner meta-policy: "pursue
  deterministic CLI enhancements aggressively; bias toward rigidity, accept
  relaxation later, do not tolerate drift" — the basis for the Slice-1/Slice-2
  rigid-core split.

## Specification Links

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the governing principle:
  repetitive AI-authored plumbing (REVISED boilerplate) is a defect; move it
  behind a deterministic service. This CLI is a direct instance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow
  state; the CLI's INDEX mutation must be atomic and preserve the version chain.
- `GOV-08` — MemBase/artifact truth; the carried-forward content must be
  byte-identical so no audit information is lost.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the CLI must
  preserve (and, for `citation_add`, extend) the `Specification Links` section;
  it must never drop links on carry-forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — single `Work Item:`,
  `Project:`, and `Project Authorization:` metadata present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the implementation PAUTH
  governs this slice.
- `GOV-STANDING-BACKLOG-001` — WI-3429 is a governed backlog item under this
  project.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all new/modified files inside
  `E:\GT-KB` (the `groundtruth-kb/` package + `bridge/`).
- `.claude/rules/file-bridge-protocol.md` — the REVISED-filing protocol the CLI
  automates (version monotonicity, status tokens, INDEX-at-top, claim-before-write).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the CLI produces governed
  bridge artifacts (REVISED files) and must keep their references durable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — each revised file carries
  forward its provenance and source references rather than discarding them.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — a REVISED is a lifecycle
  transition on a bridge thread; the CLI preserves the version chain.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — establishes the
  deterministic-services bias this CLI embodies.
- `DELIB-20260623` — this session's owner decision authorizing the 5-WI
  implementation push, CLIs first; WI-3429 is the first.
- The batch-1 reconciliation thread
  (`gtkb-deterministic-services-stale-status-reconciliation`, 5 NO-GO rounds)
  is the empirical motivation: most rounds were mechanical
  carry-forward/citation/target_paths fixes — exactly Slice 1's fix-classes.
- The `gt backlog update`/`resolve` CLI thread
  (`gtkb-backlog-update-cli-slice-1`, VERIFIED) is the sibling
  deterministic-services CLI precedent for surface design and test structure.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/bridge_revise.py` (new — core logic:
  operative resolution, fix-class dispatch table, version bump, orchestration)
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` (modify — register
  the `@bridge_group.command("revise")` click command delegating to
  `bridge_revise.py`)
- `groundtruth-kb/tests/test_bridge_revise.py` (new — unit tests)

## Requirement Sufficiency

**Existing requirements sufficient.** WI-3429's description is the operative
requirement; `DELIB-S312`, `GOV-FILE-BRIDGE-AUTHORITY-001`, and the
file-bridge-protocol govern the behavior. No new specification capture required
for Slice 1. (If LO judges a formal `SPEC-*`/`DCL-*` is warranted for the
fix-class taxonomy, that is a requirement-capture NO-GO I will address before
implementation.)

## Design (reuse-first)

The implementation is mostly wiring to existing primitives:

- **Operative resolution + version bump:** reuse the operative-file resolver
  used by `scripts/bridge_applicability_preflight.py` (`find_operative_file`),
  and compute the next version from `max(on-disk versions, INDEX versions) + 1`.
- **Scanner-safe write:** reuse `write_bridge.scan_credential_hits`,
  `handle_hits_abort_or_redact`, `ensure_author_metadata`.
- **Atomic INDEX REVISED line:** reuse
  `bridge_index_writer.atomic_index_update(index_path, mutate, state_dir=...)`
  with `mutate = lambda text: compose_index_update(slug, new_version, "REVISED", text)`
  (a pure str→str transform, safe inside the lock). `bridge_index_writer` is the
  serialized INDEX writer (`scripts/bridge_index_writer.py`).
- **Session/claim:** reuse `write_bridge.resolve_work_intent_session_id()`
  (which already checks BOTH `CLAUDE_SESSION_ID` and `CLAUDE_CODE_SESSION_ID`)
  and the work-intent registry, so the CLI does not re-derive session id and
  does not re-introduce the env-var seam.
- **Preflight rerun:** subprocess `bridge_applicability_preflight.py` and
  `adr_dcl_clause_preflight.py` with `--bridge-id <slug>`, capture + echo
  the `preflight_passed`/blocking-gaps summary.

New code is the CLI command, the operative-content fix-class dispatch table
(3 pure str→str transforms for Slice 1), and orchestration.

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `test_citation_add_appends_and_is_idempotent` | adding an existing spec id is a no-op; a new id is appended under `## Specification Links` |
| `GOV-08` (byte-identical carry-forward) | `test_content_carryforward_only_is_byte_identical_except_version` | new file content equals source except the version line + provenance |
| `target_paths_add` behavior | `test_target_paths_add_appends_and_is_idempotent` | new path appended to `target_paths`; duplicate path skipped |
| version bump | `test_version_bump_is_max_plus_one` | next version = max(on-disk, INDEX) + 1 |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX) | `test_index_revised_line_inserted_atomically` | `compose_index_update` prepends `REVISED: bridge/<slug>-<v>.md` to the existing Document entry |
| fail-closed on Slice-2 classes | `test_deferred_fix_classes_rejected` | `--fix-class pauth_swap` exits non-zero with a Slice-2 message |
| `--dry-run` | `test_dry_run_writes_nothing` | no file created, no INDEX change; preview printed |
| preflight rerun | `test_revise_reruns_preflights` (monkeypatched subprocess) | both preflight invocations issued; summary surfaced |

Test command (resolved venv interpreter):
`groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_bridge_revise.py -q`
plus `ruff check` and `ruff format --check` on the changed Python files.

## Acceptance Criteria

1. `gt bridge revise --thread <slug> --reason <r> --fix-class content_carryforward_only`
   produces the next-version file (byte-identical content + bumped version +
   provenance line) and an atomic `REVISED` INDEX line.
2. `--fix-class citation_add --add-citation <SPEC>` and
   `--fix-class target_paths_add --add-target-path <path>` apply idempotent
   appends to the correct sections.
3. Slice-2 fix-classes are rejected fail-closed.
4. `--dry-run` writes nothing and prints the preview.
5. Both preflights are re-run and their results surfaced.
6. New + modified Python passes `ruff check` and `ruff format --check`; the new
   test module passes.
7. The CLI reuses `resolve_work_intent_session_id` + the work-intent claim (no
   new session-id derivation path).

## Risks / Rollback

- **Risk: carry-forward not byte-identical** (drops a section / mangles
  encoding). Mitigation: `content_carryforward_only` is a literal copy + version
  line edit; a test asserts byte-identity except the version/provenance lines.
- **Risk: INDEX race** under concurrent writers. Mitigation: the INDEX mutation
  goes through `atomic_index_update`'s exclusive lock (the serialized INDEX
  writer), not a raw edit.
- **Risk: scope creep into Slice-2 classes.** Mitigation: `--fix-class` is a
  closed `click.Choice`; Slice-2 classes fail closed.
- **Rollback:** new module + one test file + a localized command registration;
  revert is a clean `git revert` of the feature commit. No data migration.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/`,
`groundtruth-kb/tests/`, `bridge/`). No `applications/` paths.

## Recommended Commit Type

`feat` (net-new CLI capability + module + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
