REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# WI-5441 Registry Control Plane And Reverse-Coverage Revised Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5441-registry-control-plane-reverse-coverage
Version: 007
Responds to: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-006.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

target_paths: [".claude/hooks/sot-read-discipline.py", ".claude/settings.json", ".codex/gtkb-hooks/run_py_no_window.py", "config/hooks/gtkb-sot-read-discipline.py", "config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_context_manifest.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "groundtruth-kb/tests/test_sot_duplicate_audit.py", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "platform_tests/scripts/test_check_sot_read_discipline.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_evidence_freshness_boundary.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py", "platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py", "platform_tests/scripts/test_registry_observation_hook.py", "platform_tests/scripts/test_release_candidate_gate.py", "platform_tests/scripts/test_sot_read_discipline_hook.py", "platform_tests/scripts/test_sot_read_discipline_narrative_completion.py", "platform_tests/scripts/test_worktree_finalization_triage.py", "scripts/check_protected_commit_authorization.py", "scripts/controlled_artifact_paths.py", "scripts/evidence_freshness_boundary.py", "scripts/gtkb_file_reference_migration.py", "scripts/implementation_start_gate.py", "scripts/registry_observation_hook.py", "scripts/release_candidate_gate.py"]

## Claim

Implement the WI-5441 registry control plane and the reader-visible transaction,
reverse-coverage, observation, enforcement-consumer, and work-item-lifecycle
repairs required before WI-5640 can resume.

`config/registry/sot-artifacts.toml` remains the sole human-edit membership
authority. `groundtruth.db` remains its exact derived projection and revision
ledger. The packaged v1 TOML is a byte-identical generated distribution mirror,
not a second authority. Every authority-bearing reader must observe one coherent
registry generation or fail closed while a transaction is incomplete.

This slice does not run the WI-5640 registration batch or migration, classify
unregistered objects as disposable/load-bearing, quarantine anything, or delete,
move, or rename any artifact. It supplies the deterministic control plane and
census required for the separately reviewed reconciliation to close first.

## Responses To NO-GO Findings

### F1 - enforcement consumers

The exact scope now includes the migration planner, canonical inventory service,
release gate, decontamination consumer, evidence-freshness boundary, reclaim
consumer, both SoT read-discipline hook copies, and focused tests. Migration and
release cannot use an independently parsed TOML or a projection-only view.

### F2 - reader-visible atomicity

The transaction now has a committed `prepared` journal state before any file
replacement and a universal read barrier. Canonical readers acquire the same
cross-process lock and refuse to return registry data while a nonterminal journal
exists. Multi-store authority consumers use one snapshot API under one lock.
Phase fault tests cover every externally visible transition and recovery path.

### F3 - packaged registry parity

The packaged path and `test_context_manifest.py` are in scope. The packaged file
is regenerated byte-for-byte inside the journaled transaction and is never read
as independent membership authority.

### F4 - census and observation boundaries

The census has exhaustive categories below; it has no broad runtime/service
exclusion. Observation requires a short-lived, single-use capability minted only
after a successful pre-mutation authorization decision and bound to the exact
session, tool event, paths, preimages, GO/start packet, and PAUTH decision.
Direct, mismatched, expired, replayed, or unauthorized calls fail.

### F5 - false WI lifecycle

The historical work-item versions are preserved. A governed CLI update already
set `resolution_status=open` and restored five canonical bridge links, including
the current v002 verdict. The row remains falsely `stage=resolved` because the
current lifecycle rejects all backward transitions. This scope adds a narrowly
guarded owner-approved terminal-reopen operation, tests it, and applies it to
WI-5441 before implementation reporting. The work item must finish this
implementation at `stage=implementing`, not `resolved`.

### F6 - red implementation-start baseline

The current observed baseline is `41 failed, 164 passed` in 32.68 seconds for
`platform_tests/scripts/test_implementation_start_gate.py`. Most failures are
strict-lifecycle fixtures whose synthetic bridge files omit required `Version`
metadata. This scope permits only a test-fixture correction to emit complete
strict metadata and correction of obsolete message expectations already
identified by WI-5279 evidence; it does not weaken the production resolver.

Five remaining work-intent operation-time failures belong to the existing
WI-5178/WI-5279 recovery chain: production
`scripts/bridge_work_intent_registry.py` no longer exposes the expected
authorization subtype or checks acquire/extend/renew/reclassify operations.
That production file is deliberately outside this proposal. The implementation
report must show the full-module residual baseline and separately run the named
registry selectors below; it may not claim the entire module green.

### F7 - canonical backlog-update service

The exact scope now includes
`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`, the governed service
that owns `BacklogUpdateRequest`, GOV-15 validation, attribution, dry-run, and
the single persistence call. `groundtruth-kb/tests/test_db.py` is also included
for the narrow database primitive; the already-scoped
`groundtruth-kb/tests/test_backlog_update_cli.py` proves the end-to-end CLI and
service behavior. No lifecycle bypass in `cli.py` is permitted.

### F8 - current WI-5279 authority and shared-file consolidation

The controlling related verdict is
`bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` (LO NO-GO),
not the superseded `-005` Prime NO-ACTION. This proposal explicitly consolidates
the WI-5279 strict-fixture-metadata repair and the two already-identified stale
message assertions into WI-5441's commit-capable PAUTH and shared target path.
Exactly one governed WI-5441 transaction may modify
`platform_tests/scripts/test_implementation_start_gate.py`. The five production
WI-5178 operation-time failures remain excluded and are not weakened, fixed, or
claimed complete here.

## Current-State Evidence

1. `gt registry --help` has no `register`, `amend`, `observe`, `recover`, or
   `inspect` command, and public `sync` can still legitimize direct TOML edits.
2. `load_toml` and `load_projection` are independent calls. Doctor and reclaim
   can therefore pair values from different generations.
3. `artifact_lifecycle/decontamination.py` and
   `scripts/evidence_freshness_boundary.py` parse the registry directly.
4. Both SoT read-discipline hook copies query `current_sot_artifacts` directly
   and explicitly fail open if the DB is missing or unreadable.
5. `scripts/gtkb_file_reference_migration.py` expands registered files through
   `inventory.string_scan._artifact_inventory`; the release gate has no
   platform-SoT validation step.
6. Canonical TOML and SQLite currently agree on 50 legacy records, but those
   records have no explicit `coverage_mode` and parity alone is not coverage
   completeness.
7. WI-5441 is now `resolution_status=open`, version 4, with canonical bridge
   linkage, but remains `stage=resolved` pending the governed reopen repair.
8. `cli.py` delegates backlog updates to `cli_backlog_update.py`; that service
   currently has no terminal-reopen request field and the normal database
   transition table correctly permits only `resolved -> resolved`.
9. The latest WI-5279 v2 entry is `-006` NO-GO. It names the same
   implementation-start test file, lacks a commit-capable carrier, and retains
   five WI-5178 production-enforcement dependencies. No WI-5279 patch is
   currently present because its prior Prime attempt was reverted.

## In-Root Placement And Scope Evidence

All declared paths are beneath `E:\GT-KB`. The new implementation files are
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`,
`groundtruth-kb/tests/test_registry_control_plane.py`,
`scripts/registry_observation_hook.py`, and
`platform_tests/scripts/test_registry_observation_hook.py`. They are admitted to
the registry through the same bootstrap transaction that creates their final
content. Generated observation intents and lock files under `.gtkb-state/` are
disposable runtime coordination state, not membership authority.

The active PAUTH permits source, test, configuration, and metadata mutations for
WI-5441 and forbids destructive cleanup, dispatcher/external mutation, history
rewrite, push, release, deployment, and credential lifecycle. No forbidden
operation is proposed.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v2 - sole membership authority, atomic
  registration, observed currentness, reverse coverage, and ERROR severity.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 - explicit coverage modes, normalized
  safe locators, no implicit defaults, and overlap validation.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2 - exact declaration parity,
  append-only revisions, recoverable journal, and retirement of direct sync.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1 - locked CLI-only
  mutations, authorized observation, and identity-transition prohibition.
- `GOV-WORK-TREE-HYGIENE-001` v2 - complete report-first inventory and no
  destructive action before independently approved reconciliation.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - mechanical
  write, commit, doctor, release, migration, and unsupported-harness backstops.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live PAUTH,
  independent GO, claim, and exact implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - concrete linkage and
  clause-derived executable evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only independent review and terminal
  verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root platform boundary and
  immediate hosted-application isolation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the false-closure finding,
  revised proposal, implementation evidence, and subsequent reconciliation as
  explicit governed lifecycle artifacts rather than transient session state.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - require an explicit disposition
  for the Claude and Codex observation surfaces and honest backstops for
  harnesses without native PostToolUse support.

## Prior Deliberations And Related Work

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - registry is
  ultimate membership authority; addition is easy; removal and registered
  identity changes require oversight.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-001.md` and
  `-002.md` - approved architecture, transaction invariants, phase boundaries,
  and verification plan.
- `bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md`
  - independently VERIFIED governing specification formalization.
- `bridge/gtkb-wi5441-registry-db-schema-008.md` and `-009.md` - additive Phase
  1B journal/revision schema exists; the historical finalization thread remains
  NO-GO and is not treated as terminal authority.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-003.md` and
  `-004.md` - WI-5640 consumer and the independent finding that this control
  plane is a hard prerequisite.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` - preserve incident history and require
  a fresh reviewed migration transaction.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - obsolete sources remain
  during repeated verification; this slice performs no deletion.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` - current
  controlling LO NO-GO on the overlapping fixture-recovery thread. Its
  commit-carrier blocker is resolved for the shared test-only repair by this
  proposal's commit-capable PAUTH; its five WI-5178 production failures remain
  excluded and unresolved.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` - preserved the same
  shared-target overlap after a concurrent verdict superseded the earlier
  review round; v007 incorporates that finding explicitly.

## Cross-Thread Coordination And Consolidation

- WI-5441 is the sole implementation carrier for the shared
  `platform_tests/scripts/test_implementation_start_gate.py` work: strict
  lifecycle fixture metadata, two stale message expectations, and this
  proposal's five registry-specific selectors. Those changes are one scoped
  transaction under the WI-5441 GO, claim, start packet, PAUTH, report, and
  terminal verification.
- WI-5279 v2 remains latest `-006` NO-GO and must not acquire a concurrent claim,
  file an implementation report, or mutate the shared file while WI-5441 is
  active. This consolidation resolves WI-5279's missing commit-capable carrier
  only for the absorbed test-only hunks; it does not resolve or absorb WI-5178.
- Immediately before the first shared-file mutation, Prime must mechanically
  confirm that WI-5279 is still latest `-006` NO-GO, has no live work-intent
  claim, and has no new overlapping revision. If any condition differs,
  implementation stops before mutation and returns to independent review.
- The WI-5441 implementation report must identify the exact shared-file hunks,
  show that no WI-5279 claim or parallel patch existed, and state that the
  strict-fixture slice is absorbed here. After WI-5441 is independently
  VERIFIED, any later Prime disposition on WI-5279 must cite that VERIFIED
  evidence append-only and must not reapply the absorbed hunks.

## Owner Decisions / Input

The owner directed this Prime Builder session to deliver WI-5441 before
continuing WI-5640 and reserved independent Loyal Opposition review to a
separate interactive Codex session. The owner also established the registry as
the ultimate artifact-membership SoT and required fail-closed mechanical checks
for registered move, rename, and deletion. No additional owner decision is
required for this revision.

## Proposed Design

### 1. Canonical record, resolver, and one-generation snapshot

- Add mandatory `coverage_mode` values: `exact`, `recursive`, `glob`,
  `opaque_container`, and `virtual`.
- Validate normalized project-relative locators, no path escape, Windows
  case-fold collisions, no-follow semantics, approved virtual schemes,
  object-kind compatibility, and ambiguous overlaps.
- Resolve a concrete path to zero or one member; multiple or semantically
  inconsistent matches are hard errors.
- Add `load_registry_snapshot(registry_path, db_path)` which acquires the
  canonical lock once, checks the transaction journal, loads TOML and current
  projection, verifies generation/digest parity, and returns one immutable
  snapshot. Doctor, reclaim, commit, release, migration, decontamination,
  evidence-freshness, read-discipline, and inventory enforcement consumers use
  this API or a resolver created from it.
- Existing `load_toml` and `load_projection` retain compatible single-store
  APIs but acquire the lock and reject a nonterminal journal before returning.
  Only private transaction/recovery helpers may bypass that barrier while
  already holding the lock.

### 2. Reader-linearized journal transaction

For register, amend, and the one-time legacy bootstrap:

1. Acquire the cross-process lock under `.gtkb-state/sot-registry/`.
2. Validate the old TOML, packaged mirror, projection, and absence of another
   incomplete transaction.
3. In SQLite, commit a `prepared` journal row containing operation, old and new
   canonical/package digests, exact requested records, actor/session, start
   packet and PAUTH evidence, expected record count, and deterministic receipt
   seed.
4. While the journal remains `prepared`, serialize deterministically, fsync
   same-directory temporaries, and atomically replace canonical TOML and then
   the byte-identical packaged mirror. Readers block on the journal throughout.
5. In one SQLite transaction, append changed projection versions and revision
   evidence, validate the final generation, and mark the journal `committed`
   with final digests and receipt.
6. Release the lock. Only the committed new generation is now readable.

Recovery under the same lock is deterministic and idempotent:

- old/old files with old projection: mark the prepared operation aborted;
- new/new files with old projection: complete projection/revision rows from the
  journal payload and commit;
- new/old or digest-unknown states: fail closed and emit repair evidence; never
  guess or expose membership;
- committed journal plus matching new generation: return the same receipt.

Fault injection after every durable phase must prove that every authority
consumer returns the old coherent generation, the new coherent generation, or
`RegistryTransactionInProgress`/recovery-required. No consumer may return mixed
membership.

### 3. Receipt-bound 50-record bootstrap and packaged mirror

- Define an explicit reviewed ID-to-`coverage_mode` map for exactly the current
  50 records. No punctuation, file existence, or object type inference becomes
  permanent registry data.
- Run the map once through the same journal transaction, adding the four new
  load-bearing implementation artifacts and any exact consumer artifacts this
  implementation creates.
- Bind old digest, exact 50-record input set, new records, new digest, projection
  versions, packaged-mirror digest, and receipt. Identical retry returns the
  receipt; changed input fails.
- The packaged v1 registry is always byte-identical to the canonical file and
  remains a generated distribution mirror. `test_context_manifest.py` and the
  release gate enforce this relation.

### 4. CLI control plane

- `gt registry inspect --json`: coherent declaration/projection/revision/
  journal/currentness/reverse-coverage report.
- `gt registry recover --json`: locked deterministic recovery with receipt.
- `gt registry register`: one explicit declaration or exact in-root JSON batch,
  all-or-nothing; identical retries are receipt-bound no-ops.
- `gt registry amend`: non-identity fields only. Locator, coverage-mode,
  lifecycle-membership effect, move, rename, and deletion route to a separately
  authorized transition workflow and are denied here.
- `gt registry observe`: internal capability-consuming entry point only; no
  capability means denial and no revision row.
- `gt registry validate --json`: coherent snapshot, schema, locator, parity,
  packaged mirror, currentness, journal, and reverse-coverage checks; any defect
  returns nonzero.
- Public `sync` becomes read-only diagnostics and cannot repair an out-of-band
  TOML edit.

### 5. Exhaustive whole-root census

The walker is deterministic, never follows symlinks/junctions/reparse points,
and reports every encountered object exactly once using separate `object_kind`
and `coverage_class` fields. The only traversal boundaries are:

1. root `.git/`: classify the directory as `vcs_service_state`, report one
   aggregate record, do not traverse its implementation payload;
2. each immediate directory `applications/<child>/`: classify as
   `hosted_application_root`, report it, do not traverse that independent
   application repository.

Direct files under `applications/` remain platform census objects. Runtime and
generated directories including `.gtkb-state`, virtual environments, caches,
and temporary outputs are not excluded. They are visible and resolve to one of:
`registered_member`, `registered_structural_ancestor`, `opaque_container`,
`virtual_declaration` (declaration-only; no traversal effect), `unregistered`,
or `invalid_unknown`. Symlink, junction, and reparse nodes retain those
`object_kind` values and are never followed. An opaque registered container is
classified as one member and its payload is not silently converted into an
exclusion category.

This slice reports unregistered objects and blocks a completeness claim. It does
not decide load-bearing versus disposable or authorize cleanup. WI-5640 remains
paused until the subsequent reviewed reconciliation reaches zero unknown and
zero unregistered load-bearing objects.

### 6. Authorized single-use observation

- After GO/PAUTH/claim/start and target authorization all pass, the PreToolUse
  gate mints a random, short-lived, single-use observation capability. It is
  bound to session ID, tool event ID, normalized exact paths, preimage digests,
  bridge ID, start-packet hash, PAUTH decision, expiry, and operation.
- PostToolUse receives the tool result and must atomically consume a matching
  unused capability. Path, event, session, packet, expiry, result, or preimage
  mismatch denies observation. Failed tools do not create current revisions.
- Revision rows record the consumed capability hash and authorization evidence.
  The commit gate requires both a current digest and matching live implementation
  authority; freshness evidence alone can never authorize an otherwise
  unauthorized mutation.
- Direct `gt registry observe`, fabricated capabilities, mismatched paths,
  mismatched sessions/events, expired capabilities, replay, and capability
  minting after a denied PreToolUse decision are negative-tested.
- This is a deterministic local authorization boundary, not a cryptographic
  security claim against the workstation owner. Unsupported harness writes or
  observer failures remain stale and are blocked by doctor and commit checks.

### 7. Enforcement consumers

- `controlled_artifact_paths.py` resolves membership through the snapshot and
  retains the current hardcoded protected set as a fail-closed superset until
  reconciliation is independently VERIFIED.
- `implementation_start_gate.py` denies registered identity change and any
  registered target when the journal, snapshot, owner-role, mutation API, PAUTH,
  claim, or start evidence is not current; successful decisions mint the exact
  observation capability.
- `check_protected_commit_authorization.py` denies incomplete journals, stale
  registered digests, missing observation authority, unauthorized registered
  identity changes, and snapshot drift.
- SoT read-discipline hooks stop querying SQLite directly and stop failing open;
  both copies consume the canonical snapshot and deny on authority failure.
- Decontamination and evidence freshness stop parsing TOML independently.
- `gtkb_file_reference_migration.py` and inventory consume one coherent snapshot
  and deny any unregistered source/destination/write, incomplete journal, stale
  generation, or missing exact transaction receipt.
- `release_candidate_gate.py` always runs registry validation, packaged parity,
  currentness, and reverse-coverage closure. There is no release skip for this
  authority check.

### 8. WI-5441 lifecycle reconciliation

- `cli.py` adds `--reopen-terminal` and carries it without interpretation into
  `BacklogUpdateRequest.reopen_terminal`, whose backward-compatible default is
  `False`.
- `cli_backlog_update.update_backlog_item` is the canonical validator. A reopen
  request is accepted only when: the flag is true; `--owner-approved` is true;
  the current stage is exactly `resolved`; explicit `resolution_status` is
  nonterminal; explicit target stage is nonterminal; `--change-reason` is
  nonempty and identifies the work item, active PAUTH, and owner-approved
  terminal repair; and `--related-bridge-threads` is a nonempty valid JSON array
  containing existing in-root v007 REVISED and v008 GO files whose parsed
  Document and Work Item metadata match this request and whose lifecycle is
  valid. Static request checks occur before attribution; live current-row and
  bridge checks occur after read-only lookup and before the sole write call.
- The service calls a dedicated database reopen primitive, not the ordinary
  reverse-transition table. The primitive repeats the structural checks and,
  in one transaction, appends exactly one work-item version plus one
  `wi_reopened` event. It never changes `_VALID_STAGE_TRANSITIONS`, rewrites a
  prior row, or auto-retires a project.
- Missing flag, approval, reason, linkage, explicit nonterminal status/stage;
  a nonterminal current stage; and an ordinary `resolved -> implementing`
  update all deny without a new version or event. Dry-run reports the exact
  reopen plan and performs no write.
- Apply one reopen request to WI-5441 with `resolution_status=open` and
  `stage=backlogged`, preserving all prior versions and canonical links through
  v007 and its verdict. After the reopen succeeds, use the ordinary existing
  `backlogged -> implementing` path to set `resolution_status=in_progress` and
  `stage=implementing`.
- The approval evidence consumed by `--owner-approved` is the owner's existing
  direction in this program to repair forward and have this Prime Builder
  deliver WI-5441 before WI-5640 resumes, as recorded in this proposal's Owner
  Decisions section and bounded by the active PAUTH. No new owner decision is
  required.

## Cross-Harness Disposition

- Claude: `.claude/settings.json` registers the canonical PostToolUse observer;
  `.claude/hooks/sot-read-discipline.py` consumes the coherent snapshot and
  fails closed. Focused tests cover Write, Edit, Bash, denied PreToolUse, exact
  event binding, and single-use consumption.
- Codex: `.codex/gtkb-hooks/run_py_no_window.py` invokes the same observer for
  its supported Bash/apply_patch post-tool batches. Focused parity tests require
  the same intent schema, path binding, replay denial, and stale-state backstop.
- The mirrored governed hook at `config/hooks/gtkb-sot-read-discipline.py`
  remains behaviorally identical to the Claude projection and is checked as a
  pair.
- Cursor, Goose, API, Ollama, OpenRouter, Antigravity, and other surfaces do not
  gain a native observer in this bounded slice. No parity is claimed for an
  unavailable event surface. Coherent snapshot validation, doctor, migration,
  release, and protected-commit currentness checks are the fail-closed typed
  compatibility disposition: their writes remain stale until an authorized
  observer path records exact evidence and cannot pass finalization.
- No harness role state, dispatcher routing, or shared-envelope mutation is
  introduced. Authorization and evidence bind to the session and tool event,
  not to a persisted harness role.

## Requirement Sufficiency

Existing requirements sufficient.

The cited v2/v3 GOV/DCL family defines membership, explicit locator semantics,
transaction atomicity, currentness, recovery, reverse coverage, and enforcement.
This proposal does not add disposal authority, transition apply, or destructive
scope.

## Specification-Derived Verification Plan

| Requirement | Exact verification | Expected result |
| --- | --- | --- |
| Explicit schema and bootstrap | `groundtruth-kb/tests/test_sot_registry.py` and `test_registry_control_plane.py` selectors for all modes, exact 50-record map, idempotent receipt, unsafe path/case/overlap rejection | Explicit modes, no inferred defaults, exact retry receipt |
| Reader linearization | Fault injection after journal prepare, canonical replace, mirror replace, DB update, journal commit; parameterize snapshot, individual readers, doctor, hooks, commit, release, migration, inventory, reclaim, decontamination, evidence freshness | Old coherent, new coherent, or explicit in-progress/recovery error; never mixed |
| Packaged parity | `groundtruth-kb/tests/test_context_manifest.py::test_packaged_v1_snapshot_matches_source_checkout_registry_inputs` plus digest assertions in transaction tests | Byte-identical canonical/mirror at every readable generation |
| Reverse coverage | Synthetic root tests for `.git`, immediate application children, direct application files, `.gtkb-state`, venv/cache/temp, opaque, virtual, symlink, junction, reparse, structural ancestor, unregistered, and invalid objects | Every object classified once; only two named traversal boundaries |
| Observer authority | `platform_tests/scripts/test_registry_observation_hook.py` negative and positive selectors | Direct/fabricated/mismatch/expiry/replay denied; one authorized event consumed once |
| Doctor and read discipline | `test_check_sot_registry_completeness.py`, `test_check_sot_read_discipline.py`, `test_sot_read_discipline_hook.py`, narrative completion test | Incomplete journal, stale state, direct projection bypass, and unknown coverage fail closed |
| Commit boundary | `test_check_protected_commit_authorization.py` selectors for stale digest, mismatched capability/start packet, identity change, and coherent success | Unauthorized/stale deny; exact authorized current member proceeds |
| Migration boundary | `test_gtkb_file_reference_migration.py` and inventory unit/CLI tests | Only coherent registered universe accepted; unregistered target or incomplete journal blocks |
| Release boundary | `test_release_candidate_gate.py` registry selectors | No skip; incomplete, stale, mirror drift, or reverse gap fails release |
| Direct-reader retirement | Decontamination, evidence freshness, reclaim, read-hook focused tests plus source grep for raw SoT TOML/current-table access outside canonical module/private transaction code | No authority consumer bypass remains |
| Work-item reopen service | `groundtruth-kb/tests/test_backlog_update_cli.py` selectors `test_backlog_update_reopen_terminal_appends_one_version_and_event`, `test_backlog_update_reopen_terminal_dry_run_writes_nothing`, and parameterized negative cases; `groundtruth-kb/tests/test_db.py` dedicated primitive tests | Service carries and validates the flag/evidence; exact reopen appends one version/event; every incomplete or ordinary reverse request denies |
| Implementation-start registry integration | New selectors `test_registered_target_requires_registry_currentness`, `test_incomplete_registry_journal_blocks_mutation`, `test_registered_identity_change_requires_transition`, `test_authorized_write_mints_observation_intent`, `test_unauthorized_write_mints_no_observation_intent` | All five pass independently |
| Known implementation-start baseline | Full `test_implementation_start_gate.py`, with strict fixture repair and stale-message correction only | Fixture failures removed; five WI-5178 work-intent failures reported, not masked or claimed by this thread |
| Cross-thread shared-file ownership | Pre-mutation bridge/claim check plus implementation-report hunk inventory against WI-5279 v2 `-006` | WI-5279 remains NO-GO and unclaimed; exactly one WI-5441 transaction owns the absorbed test-only hunks; five WI-5178 failures remain separate |
| Quality | Ruff check/format on every changed Python path; `git diff --check`; applicability and clause preflights | Clean, exact-scope evidence |

The implementation report must list exact pytest node IDs and observed results.
No broad green summary may replace phase-fault, consumer, observer-negative,
reverse-census, migration, release, and lifecycle evidence.

The v004 LO baseline is retained: its focused registry-related selection was
`1 failed, 124 passed`; the one failure is unrelated activity-profile packaged
mirror drift surfaced by `test_context_manifest.py`. The release-candidate test
module has two unrelated BOM-driven Windows spawn-audit failures in the Goose
verify writer. This implementation must report those residuals without changing
their paths, masking them, or calling this thread broadly green.

## Acceptance Criteria

1. Every authority-bearing registry consumer uses the coherent snapshot/barrier;
   an automated source scan finds no remaining raw SoT TOML or
   `current_sot_artifacts` access outside the canonical module, schema/migration
   code, and test fixtures.
2. No injected transaction failure exposes mixed canonical TOML, packaged
   mirror, projection, or revision membership to any named consumer.
3. Exactly 50 legacy records receive explicitly reviewed coverage modes through
   one idempotent receipt-bound bootstrap; canonical and packaged TOML are
   byte-identical and projection parity includes `coverage_mode`.
4. The census applies only the two named traversal boundaries and reports every
   other root object exactly once without following reparse-like nodes.
5. Direct or forged observation cannot manufacture commit-acceptable freshness;
   successful Claude/Codex governed writes consume one exact capability and
   unsupported writes remain stale and blocked.
6. Migration and release fail closed on incomplete journal, stale/mixed
   generation, mirror drift, unregistered required paths, or unresolved reverse
   coverage.
7. Registered deletion, move, rename, locator change, coverage membership
   change, and lifecycle membership change remain mechanically denied because
   transition apply is outside this scope.
8. WI-5441 is reopened only through `cli_backlog_update.py`: one approved
   reopen appends one version/event at `open/backlogged`, then the ordinary
   transition reaches `in_progress/implementing`. Canonical linkage is retained
   and no historical row or bridge artifact is rewritten.
9. Strict bridge fixture metadata and the two stale assertions are consolidated
   into this sole WI-5441 carrier without relaxing the resolver. WI-5279 remains
   unclaimed during mutation; its current `-006` verdict and the exact absorbed
   hunks are cited in the report. The five WI-5178 residual failures remain
   disclosed and excluded; all new registry-specific selectors pass.
10. WI-5640 remains paused. No live migration registration, file copy/move,
    reference rewrite, cleanup, commit, push, release, deployment, credential,
    dispatcher, or history-rewrite operation is performed by this proposal.
11. Only the declared target paths may receive source/config/test/metadata
    changes. Any required implementation spillover stops work and requires a
    new revision.

## Risks And Rollback

- Cross-store atomicity is provided by reader linearization, not by pretending
  NTFS and SQLite share one physical transaction. The committed prepared journal
  blocks every authority reader until deterministic recovery completes.
- A missed direct reader would reintroduce split observation. The target census,
  source grep acceptance check, focused consumer tests, and release gate make
  bypass absence executable evidence.
- Census mistakes could hide artifacts. The exclusions are closed and named;
  unregistered/unknown remains visible and blocking, with no cleanup authority.
- Observation capabilities are local governance evidence, not workstation-user
  security. Commit authorization remains independently bound to the live GO,
  PAUTH, claim, start packet, exact target, and current digest.
- A concurrent WI-5279 revision could create ambiguous ownership of the shared
  test file. The mandatory latest-status/claim check stops before mutation, and
  the WI-5441 report carries exact hunk provenance and absorption evidence.
- Rollback before terminal verification runs registry recovery under the lock,
  restores exact scoped preimages, and preserves all journal/revision/work-item
  history. No reset or history rewrite is permitted.

## Pre-Filing Preflight

Run `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` against
this exact completed content before helper-mediated filing. Filing is allowed
only with no missing required/advisory specifications and no blocking clause
gap.

## Requested Loyal Opposition Action

Review this v007 replacement scope finding-by-finding, especially the universal
reader barrier, two-boundary census, observation capability negative cases,
receipt-bound legacy bootstrap, packaged mirror, enforcement-consumer closure,
the end-to-end governed WI lifecycle repair through `cli_backlog_update.py`,
and the explicit WI-5279 shared-file consolidation. File GO or NO-GO as v008
from an independent interactive review session. Do not grant implementation authority outside the
exact declared paths.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
