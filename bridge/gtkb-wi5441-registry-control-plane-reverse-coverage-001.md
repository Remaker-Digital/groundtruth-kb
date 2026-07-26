NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# WI-5441 Registry Control Plane And Reverse-Coverage Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5441-registry-control-plane-reverse-coverage
Version: 001
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "scripts/controlled_artifact_paths.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "scripts/registry_observation_hook.py", "platform_tests/scripts/test_registry_observation_hook.py", ".claude/settings.json", ".codex/gtkb-hooks/run_py_no_window.py"]

## Claim

Implement the bounded WI-5441 registry control plane and reverse-coverage
substrate required by
`bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md` before
WI-5640 may resume. `config/registry/sot-artifacts.toml` remains the sole
artifact-membership authority and the MemBase `sot_artifacts` table remains
its exact projection. This slice adds the missing mechanical mutation,
observation, recovery, and coverage services; it creates no second registry.

This proposal combines architecture Phase 2 (CLI Control Plane) with only the
Phase 3 coverage/currentness work required to make that control plane
verifiable and useful. Initial classification closure, quarantine, sweep, and
expiry remain separate later phases. The slice must report current registry
gaps honestly; it does not declare the current 50-row registry complete.

## Current-State Evidence

1. `gt registry --help` currently exposes only `audit-duplicates`, `diff`,
   `list`, `show`, `sync`, and `validate`. It has no `register`, `amend`,
   `observe`, `recover`, or `inspect` command.
2. The canonical `groundtruth_kb.project.sot_registry` reader does not load,
   validate, compare, or project `coverage_mode`, although the Phase 1B DB
   schema has a nullable column and journal/revision tables.
3. Public `sync` still legitimizes direct TOML edits, contrary to
   `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2.
4. `_check_sot_registry_completeness` checks declaration/projection parity and
   existence only. It does not perform reverse filesystem coverage, observed
   revision freshness, or incomplete-journal checks.
5. `scripts/controlled_artifact_paths.py` remains a hardcoded protection
   inventory. The current write and commit gates do not resolve membership
   through the canonical registry reader and no post-write service appends
   observed revisions.
6. The WI-5640 manifest currently has only 7/90 source paths, 0/90 destination
   paths, and 0/1 manifest paths covered by the registry. That migration must
   remain paused until this slice is independently VERIFIED and a later
   reconciliation reaches closure.

## In-Root Placement Evidence

Every declared target is under `E:\GT-KB`. The sole new source and test files
are `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`,
`groundtruth-kb/tests/test_registry_control_plane.py`,
`scripts/registry_observation_hook.py`, and
`platform_tests/scripts/test_registry_observation_hook.py`. Their registry
coverage must be established in the same governed implementation transaction
that creates them.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v2 - sole membership authority, atomic
  registration, observed currentness, reverse coverage, and ERROR severity.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 - explicit coverage modes, safe
  normalized locators, no implicit defaults, and overlap validation.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2 - exact declaration parity,
  append-only revision evidence, recoverable journal, and retirement of
  direct-edit-plus-sync.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1 - locked CLI-only
  register/amend/observe boundaries and identity-transition prohibition.
- `GOV-WORK-TREE-HYGIENE-001` v2 - report-first inventory and no destructive
  action before closed reconciliation and a separately approved sweep.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - deterministic
  enforcement across write, commit, doctor, and unsupported-harness paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - current bounded
  PAUTH, independent GO, work-intent claim, and implementation-start evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - concrete links and
  clause-derived executable verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent review and terminal
  verification through the numbered bridge.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - root boundary and immediate
  `applications/<child>/` isolation.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - controlling
  owner decision: the registry is ultimate membership authority; registration
  is easy; removal and registered identity changes require oversight.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-001.md` and
  `-002.md` - independently approved architecture, command boundary, phase
  decomposition, transaction invariants, and verification plan.
- `bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md`
  - independently VERIFIED governing specification formalization.
- `bridge/gtkb-wi5441-registry-db-schema-008.md` and `-009.md` - Phase 1B
  schema is substantively accepted but its historical terminal finalization
  remains NO-GO on a separate bridge-finalizer defect. This proposal uses the
  live additive schema but does not claim that thread is terminal VERIFIED.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-003.md` and
  `-004.md` - exact WI-5640 readiness consumer and LO finding that the live
  registry transaction surface is absent.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` - preserve incident history and use a
  fresh governed repair-forward transaction.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - old migration sources stay
  in place; this slice performs no source deletion.

## Owner Decisions And Authorization

The owner directed this Prime Builder session to deliver WI-5441 before
continuing WI-5640 and designated the interactive Codex session as the
independent Loyal Opposition reviewer. The active authorization is
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724`.
It permits source, test, configuration, and MemBase metadata changes only for
this bounded slice. It forbids cleanup, dispatcher/external mutation, history
rewrite, push, release, deployment, and credential operations. One local
governed finalization commit is permitted only through an independently
VERIFIED verdict; no push is authorized.

## Proposed Design

### 1. Canonical record and resolver

- Extend `SoTArtifact` and both canonical readers with mandatory
  `coverage_mode` values: `exact`, `recursive`, `glob`, `opaque_container`, or
  `virtual`.
- Validate normalized project-relative paths, Windows case-fold collisions,
  no path escape, no-follow semantics, permitted virtual schemes, object-kind
  compatibility, and ambiguous overlaps.
- Assign an explicitly reviewed mode to every current declaration through the
  governed control-plane transaction. No mode may be inferred permanently
  from punctuation, current existence, or object type.
- Resolve any concrete path to zero or one canonical member. A multi-match or
  semantically inconsistent overlap is a hard error.

### 2. Locked recoverable transaction

- Add one cross-process registry lock under `.gtkb-state/sot-registry/`.
  Mutations fail with a bounded, machine-readable lock error rather than
  racing.
- Before changing TOML, projection, revision rows, or a registered identity,
  write an intent row to `sot_registry_transaction_journal` containing the
  operation, input/declaration digest, actor session, and exact requested
  records.
- Serialize declarations deterministically, write and fsync a same-directory
  temporary file, atomically replace TOML, update the projection and revision
  ledger in a DB transaction, then mark the journal complete with final
  declaration digest and deterministic receipt.
- Preserve enough preimage and phase evidence for `gt registry recover` to
  converge after a process interruption. Any incomplete journal blocks a new
  mutation, validation success, commit, release, or migration readiness.
- Fault injection at each phase must prove either the old state or the new
  complete state, never mixed membership.

### 3. CLI boundary

- `gt registry inspect --json`: read-only full-root declaration, projection,
  revision, journal, and reverse-coverage report.
- `gt registry recover --json`: lock, inspect incomplete journals, restore or
  finish deterministically, and emit a receipt.
- `gt registry register`: accept one explicit declaration or an exact in-root
  JSON manifest. Batch input is one all-or-nothing transaction. Existing
  identical records are explicit idempotent no-ops; conflicting ID or locator
  reuse aborts the batch.
- `gt registry amend`: change non-identity declaration fields only. Locator,
  coverage mode, lifecycle effect, or membership-set changes fail and route to
  the later transition-request workflow.
- `gt registry observe`: automated-only observation of exact registered
  concrete members. Append digest, size, object kind, operation, actor/session,
  and predecessor revision; never grant membership.
- `gt registry validate --json`: include declaration/projection parity,
  locator validity, observed freshness, incomplete journals, and reverse
  coverage. Any defect returns nonzero.
- Retire public mutating `sync`. It may emit a read-only repair plan but cannot
  write projection rows after a direct TOML edit.

### 4. Reverse coverage and currentness

- Walk the platform root deterministically without following symlinks,
  junctions, or reparse points. Skip service/runtime exclusions by explicit
  rule and skip only immediate `applications/<child>/` repositories; files
  directly under `applications/` stay in scope.
- Classify each in-scope filesystem object as registered member, structural
  ancestor, declared service payload, unregistered, or invalid/unknown.
  The control plane does not guess whether an unregistered item is
  load-bearing or disposable.
- `inspect` reports all unregistered/unknown paths. `validate` and doctor fail
  ERROR while unknown, unregistered-load-bearing, stale revision, parity, or
  journal defects remain. Initial reconciliation is a separate proposal that
  supplies evidence-backed load-bearing/disposable dispositions.

### 5. Write and commit integration

- Refactor `scripts/controlled_artifact_paths.py` to consult the canonical
  registry resolver. Preserve the current hardcoded protected set as a
  fail-closed superset until reconciliation proves registry closure; this
  slice must not underprotect a current path.
- Keep implementation-start authorization checks and add registry owner-role,
  mutation-API, membership, and incomplete-journal checks for registered
  targets. Registered delete/move/rename remains denied because transition
  apply is intentionally absent.
- Add one `scripts/registry_observation_hook.py` adapter. Register it in
  Claude PostToolUse and the existing Codex Bash/apply_patch PostToolUse
  batches. It extracts exact mutated paths and calls the canonical observer.
- Unsupported or failed post-write paths do not silently pass: `inspect` and
  doctor report stale state and `check_protected_commit_authorization.py`
  blocks a staged registered member whose current digest lacks matching
  revision evidence.

### 6. Migration consumer contract

- Support a hash-bound JSON batch large enough for WI-5640 to register its
  exact manifest, retained sources, and canonical destinations in one
  transaction after initial registry reconciliation is independently
  VERIFIED.
- The migration must use only canonical `load_toml` / `load_projection` /
  resolver APIs. Raw TOML edits, public sync, and direct SQLite remain blocked.
- This slice does not run the WI-5640 registration batch or migration planner.

## Cross-Harness Disposition

- Claude: register the canonical PostToolUse observer in
  `.claude/settings.json`; focused fixtures prove governed writes append
  revision evidence.
- Codex: add the same observer to the existing posttooluse Bash and
  apply_patch batches in `.codex/gtkb-hooks/run_py_no_window.py`.
- Cursor and Goose: no native observer is added in this bounded slice.
  Registry inspection, doctor, and protected-commit freshness checks must
  expose stale changes and fail closed.
- API, Ollama, OpenRouter, and other unsupported direct-write paths receive
  the same inspect/doctor/commit backstop. This is an explicit temporary
  disposition, not a claim of native hook parity.

## Requirement Sufficiency

Existing requirements sufficient.

The cited v2/v3 GOV/DCL family is sufficient for this implementation. It
defines membership, locator semantics, transaction atomicity, currentness,
recovery, reverse coverage, and enforcement. The implementation must not
invent disposal classification or destructive authority; those require later
bounded proposals.

## Specification-Derived Verification Plan

| Requirement | Exact verification | Expected result |
| --- | --- | --- |
| Explicit record schema | `groundtruth-kb/tests/test_sot_registry.py` coverage-mode, path-escape, case-fold, overlap, virtual-scheme tests | Every invalid/ambiguous declaration fails; every current record has a reviewed mode |
| Locked atomic mutation | `groundtruth-kb/tests/test_registry_control_plane.py` concurrent-writer and phase-by-phase fault-injection nodes | One writer; no partial TOML/projection/revision state; recover converges |
| Batch register | CLI runner tests for one record, 181-record fixture, idempotent retry, duplicate ID/locator, stale digest | Exact all-or-nothing result and deterministic receipt |
| Direct-edit retirement | CLI tests modify TOML out of band then run `sync`, `validate`, and a mutation | `sync` cannot write; drift blocks mutation and validation |
| Observed revisions | control-plane and hook tests mutate exact/recursive/glob members and virtual/opaque fixtures | Concrete revisions append with predecessor; virtual/opaque use declared currentness path |
| Reverse coverage | synthetic no-follow inventory tests plus live `gt registry inspect --json` | Every in-scope object classified once; application children and service payloads bounded exactly |
| Doctor ERROR | `platform_tests/scripts/test_check_sot_registry_completeness.py` | parity, locator, stale, incomplete-journal, unknown/load-bearing gaps are ERROR |
| Canonical protection | `platform_tests/scripts/test_controlled_artifact_paths.py` and `test_implementation_start_gate.py` | registry resolver applies; hardcoded fallback remains a superset; registered identity changes deny |
| Commit freshness | `platform_tests/scripts/test_check_protected_commit_authorization.py` | stale registered staged paths deny; matching current revision proceeds to normal authorization checks |
| Claude/Codex observation | `platform_tests/scripts/test_registry_observation_hook.py` | exact Bash/apply_patch/Write/Edit targets observed; failures remain visible and fail closed downstream |
| WI-5640 compatibility | focused `test_gtkb_file_reference_migration.py` preflight against a closed fixture registry | canonical readers accept the transaction receipt; unregistered writes remain blocked |
| Quality | Ruff check/format on changed Python paths; `git diff --check`; bridge applicability and clause preflights | All pass with no scope spillover or blocking gaps |

The implementation report must list exact pytest node IDs and executed command
results. A broad green summary cannot substitute for the fault-injection,
reverse-coverage, observer, and stale-commit checks above.

## Acceptance Criteria

1. `gt registry --help` exposes `inspect`, `recover`, `register`, `amend`, and
   `observe`; batch registration is one recoverable transaction.
2. Concurrent writers, duplicate identities, unsafe locators, semantic
   overlaps, stale declaration digests, and injected failures cannot publish
   partial membership.
3. Every current declaration has an explicit reviewed `coverage_mode`, and
   TOML/current projection parity includes it with zero field divergence.
4. `validate --json` reports parity, locator validity, reverse-coverage
   categories, stale revisions, and incomplete journals and exits nonzero for
   any defect.
5. Successful governed Claude/Codex writes append exact revision evidence;
   unsupported writes are visible as stale and cannot pass the commit gate.
6. Current controlled-path and implementation authorization protection is not
   weakened before registry reconciliation closes.
7. The 181-record WI-5640 fixture can be admitted atomically through the new
   batch interface, but no live WI-5640 registration or migration is executed
   by this slice.
8. No transition apply, quarantine, sweep, delete, cleanup, push, release,
   deployment, credential, dispatcher, or history-rewrite operation is added
   or executed.
9. Only the nineteen declared target paths may change. Any generated or
   required spillover stops implementation and requires a revised proposal.

## Risks And Rollback

- Transaction defects could split TOML and projection authority. Mitigation:
  intent-first journal, same-directory atomic replace, DB transaction,
  preimage, phase fault injection, and mandatory recovery before new mutation.
- Reverse-coverage mistakes could misclassify essential artifacts. Mitigation:
  this slice is report-only for unregistered paths and does not quarantine or
  delete anything; unknown remains blocking.
- Switching protection to an incomplete registry could underprotect current
  paths. Mitigation: preserve hardcoded protection as a fail-closed superset
  until independently reviewed reconciliation closure.
- Hook gaps could leave stale revisions. Mitigation: visible stale state plus
  doctor and protected-commit backstops; no unsupported path is called native
  parity.
- Rollback before terminal verification restores exact preimages for the
  nineteen targets and runs journal recovery. Existing history is never reset
  or rewritten.

## Requested Loyal Opposition Action

Review whether the proposed transaction is genuinely atomic and recoverable,
whether reverse coverage is bounded correctly, whether hook gaps fail closed,
and whether the exact target set is sufficient without absorbing later sweep
or quarantine phases. File `GO` or `NO-GO` as version 002 in an independent
session context. Do not issue implementation authorization outside this exact
scope.

## Owner Action Required

None. The controlling owner decision and bounded PAUTH are already recorded.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
