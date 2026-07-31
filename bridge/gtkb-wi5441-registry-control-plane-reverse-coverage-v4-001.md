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

# WI-5441 Registry Control Plane And Bridge Publication Currentness Executable Fresh Replacement Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5441-registry-control-plane-reverse-coverage-v4
Version: 001
Supersedes invalid or withdrawn audit chains: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-011.md; bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v2-001.md; bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v3-002.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: [".claude/hooks/sot-read-discipline.py",".claude/settings.json",".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py",".claude/skills/gtkb-bridge/helpers/impl_report_bridge.py",".claude/skills/gtkb-bridge/helpers/revise_bridge.py",".claude/skills/gtkb-verify/helpers/write_verdict.py",".codex/gtkb-hooks/run_py_no_window.py",".codex/skills/MANIFEST.json",".codex/skills/gtkb-bridge/SKILL.md",".codex/skills/gtkb-bridge-propose/helpers/write_bridge.py",".codex/skills/gtkb-bridge/helpers/impl_report_bridge.py",".codex/skills/gtkb-bridge/helpers/revise_bridge.py",".codex/skills/gtkb-proposal-review/SKILL.md",".codex/skills/gtkb-send-review/SKILL.md",".codex/skills/gtkb-verify/SKILL.md",".codex/skills/gtkb-verify/helpers/write_verdict.py","config/agent-control/gtkb-harness-capability-registry.toml","config/hooks/gtkb-sot-read-discipline.py","config/registry/sot-artifacts.toml","groundtruth.db","groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py","groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py","groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py","groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py","groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/db.py","groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py","groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py","groundtruth-kb/src/groundtruth_kb/project/doctor.py","groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","groundtruth-kb/src/groundtruth_kb/project/sot_registry.py","groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py","groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py","groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py","groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py","groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py","groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py","groundtruth-kb/tests/test_backlog_update_cli.py","groundtruth-kb/tests/test_bridge_propose_helper.py","groundtruth-kb/tests/test_cli_bridge_propose.py","groundtruth-kb/tests/test_context_manifest.py","groundtruth-kb/tests/test_db.py","groundtruth-kb/tests/test_hygiene_reclaim.py","groundtruth-kb/tests/test_inventory_string_scan.py","groundtruth-kb/tests/test_registry_control_plane.py","groundtruth-kb/tests/test_sot_duplicate_audit.py","groundtruth-kb/tests/test_sot_registry.py","groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py","platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py","platform_tests/groundtruth_kb/test_cli_bridge_propose.py","platform_tests/scripts/test_check_protected_commit_authorization.py","platform_tests/scripts/test_check_sot_duplicate_guard.py","platform_tests/scripts/test_check_sot_read_discipline.py","platform_tests/scripts/test_check_sot_registry_completeness.py","platform_tests/scripts/test_controlled_artifact_paths.py","platform_tests/scripts/test_evidence_freshness_boundary.py","platform_tests/scripts/test_generate_codex_skill_adapters.py","platform_tests/scripts/test_gtkb_bridge_writer.py","platform_tests/scripts/test_gtkb_file_reference_migration.py","platform_tests/scripts/test_gtkb_service_sot_restore_registry.py","platform_tests/scripts/test_hygiene_strays_cli.py","platform_tests/scripts/test_implementation_start_gate.py","platform_tests/scripts/test_modernization_artifact_decontamination.py","platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py","platform_tests/scripts/test_provider_verdict_status_consistency.py","platform_tests/scripts/test_registry_observation_hook.py","platform_tests/scripts/test_release_candidate_gate.py","platform_tests/scripts/test_sot_read_discipline_hook.py","platform_tests/scripts/test_sot_read_discipline_narrative_completion.py","platform_tests/scripts/test_worktree_finalization_triage.py","platform_tests/skills/test_bridge_impl_report_helper.py","platform_tests/skills/test_bridge_propose_helper.py","platform_tests/skills/test_bridge_propose_helper_work_intent.py","platform_tests/skills/test_bridge_revise_helper.py","platform_tests/skills/test_verified_finalization_validation_hardening.py","scripts/check_protected_commit_authorization.py","scripts/controlled_artifact_paths.py","scripts/evidence_freshness_boundary.py","scripts/gtkb_bridge_writer.py","scripts/gtkb_file_reference_migration.py","scripts/implementation_start_gate.py","scripts/registry_observation_hook.py","scripts/release_candidate_gate.py"]

## Clean-Thread Replacement

The original chain is preserved but cannot carry implementation authority. The
strict lifecycle resolver rejects its ninth entry with
`WRONG_BRIDGE_VERSION_METADATA` because the stored value is not the exact
three-digit value. Later entries cannot erase that defect.

The first fresh replacement at the v2 slug is also preserved and quarantined.
Its explanatory prose repeated a colon-bearing metadata field label, producing
`DUPLICATE_BRIDGE_METADATA` at its first entry.

The v3 proposal is lifecycle-valid but terminal `WITHDRAWN`. Prime withdrew it
before review because its bootstrap incorrectly required every immutable
historical bridge chain in the registered aggregate to be strict-valid. That is
unexecutable while malformed audit evidence is intentionally retained.

This v4 slug starts at exact version 001. It carries the complete accepted
F1-F8 design, replaces the impossible bootstrap with an exact quarantine
inventory, and does not treat status-only bridge listings as authority.
Implementation remains paused until an independent GO is filed on this v4
thread and the canonical strict resolver accepts the resulting chain.

The non-v2 WI-5279 sibling is malformed at its second entry with
`WRONG_STATUS_AUTHOR_ROLE`; it is non-authorizing audit evidence. The separate
WI-5279 v2 thread is strict-valid and currently ends at its sixth entry with an
unresolved LO `NO-GO`. Its shared-file relationship is consolidated below.

## Revision Claim

Replace the verification-pending v009 report with a newly reviewed corrective
implementation slice. The completed WI-5441 registry work remains in place,
but it cannot be finalized while bridge publication itself makes the registered
`bridge-versioned-files` aggregate stale.

This revision resolves both v010 findings, adds the mechanically necessary
bridge-publication observation transaction, restores registry currentness
without fabricated PAUTH evidence or raw SQLite mutation, registers every
load-bearing publication chokepoint touched by the repair, reruns the original
WI-5441 verification contract, and then files a new implementation report.

No WI-5640 move, rename, copy, reference rewrite, source deletion, push,
release, deployment, credential operation, dispatcher mutation, or history
rewrite is authorized.

## Responses To v010

### F1 - ignored groundtruth.db finalization hazard

`groundtruth.db` is runtime projection and append-only evidence only. The next
implementation report MUST place it in a separate
`By-Reference Runtime And Registry Evidence` section. It MUST NOT appear under
`Files Changed`, MUST NOT be passed to the VERIFIED finalizer's `--include`
set, and MUST NOT be force-added to git. No waiver is needed because no commit
inclusion is claimed. The report will cite bounded digests, journal/receipt
IDs, revision IDs, and read-only CLI reproduction commands.

### F2 and F8 - WI-5279 authority and shared-file consolidation

The exact non-v2 sibling cannot authorize implementation: the canonical strict
resolver rejects its second entry with `WRONG_STATUS_AUTHOR_ROLE`. Its fifth
entry remains append-only audit evidence, and WI-5687/TEST-11708 preserve the
status-only false-GO and exact-slug/prefix-merge defect.

The controlling related verdict for the separate, strict-valid WI-5279 v2
thread is
`bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` (LO
`NO-GO`), not its superseded fifth-entry Prime `NO-ACTION`. This proposal
explicitly consolidates the WI-5279 strict-fixture-metadata repair and the two
already-identified stale message assertions into WI-5441's commit-capable PAUTH
and shared target path. Exactly one governed WI-5441 transaction may modify
`platform_tests/scripts/test_implementation_start_gate.py`.

The five WI-5178 production-enforcement failures remain outside WI-5441. Before
the first shared-file mutation, Prime must mechanically confirm that WI-5279 v2
still ends at its sixth-entry `NO-GO`, has no live work-intent claim, and has no
new overlapping revision. Any difference stops implementation before mutation
and returns the overlap to independent review. The WI-5441 implementation
report must identify the absorbed hunks and prove sole transaction ownership;
after terminal WI-5441 verification, later WI-5279 work must cite that evidence
and must not reapply those hunks.

### WITHDRAWN path confirmation

The central writer supports non-dispatchable `WITHDRAWN` content without a
Prime or Loyal Opposition envelope. The v3 second entry now proves the legal
`NEW -> WITHDRAWN` path and the canonical resolver reports terminal
`WITHDRAWN` with no blocking diagnostics. The earlier failed attempt supplied a
Prime build envelope to a status that intentionally has no role mapping; no
specious mapping was added.

## Newly Proven Blocking Defect - Bridge Publication Stales The Registry

The canonical `bridge-versioned-files` record is a registered glob at
`bridge/*-[0-9][0-9][0-9].md`, with the governed bridge helper/CLI plus
compliance and claim as its declared mutation API.

After v010, `gt registry inspect --no-census --json` reports coherent true,
current false, and exactly one stale record:

- current: `sha256:83e11497c195eae607e4c195cb1438cb132cce9ff469c0e30a2cebad4899bf5f`;
- observed: `sha256:f6c3b3f4b8d89829da9b0b11cc7d308c13c267bf05e98aeb9ab9d6e19bec7267`.

The low-level writer creates and verifies the numbered file but records no
registry revision. Prime helpers release the claim immediately. Provider
verdict publication also releases after write/finalization. The VERIFIED
failure path unlinks a failed verdict without a compensating revision.
Existing tests do not enforce publication, observation, currentness, rollback,
and claim release as one ordered contract.

Calling this normal bridge drift conflicts with the owner's rule that every
registered mutation update the registry automatically.

## Corrective Design

### 1. Typed bridge-publication authority

Extend the control plane with explicit `bridge_publication` authority. Do not
place bridge claims or compliance results in fields named `start_packet_hash`
or `pauth_decision`.

Mint only after exact active claim/session, strict lifecycle/version,
status-authority, author-session, credential scan, bridge-compliance audit,
target missing-file preimage, coherent registry generation, and aggregate
preimage checks pass. Durable evidence records authority kind, document,
version, status, target, content/compliance/transition digests, claim and
author sessions, aggregate preimage, operation, expiry, and single-use state.

### 2. Ordered publication and failure semantics

For NEW, REVISED, NO-ACTION, GO, NO-GO, and non-finalizing VERIFIED:

1. validate and mint before file creation;
2. create exclusively and byte-verify;
3. consume capability and append current aggregate revision;
4. require `currentness.current == true`;
5. only then release the claim and return success.

A write or observation failure removes only the new uncommitted file, records
failed/compensated state, verifies the aggregate returned to its preimage, and
retains the claim. If rollback cannot complete, retain file and claim, leave
currentness red, and emit a typed repair-required error.

For VERIFIED finalization, later commit or index-realignment failure uses a
governed publication rollback, not raw `unlink`. Successful deletion appends
compensating aggregate evidence and proves currentness. A successful commit is
followed by currentness validation before claim release.

The live `gt bridge file-implementation-proposal` service must finish all
candidate/live checks inside this ordering. An outer post-write failure may
not leave a released claim and stale bridge state.

### 3. One-time fail-closed bootstrap with exact quarantine

This v4 proposal and its independent verdict necessarily use the defective
writer before the repair exists. Immediately before v4 filing, canonical
registry inspection was coherent but not current, with only
`bridge-versioned-files` stale: current aggregate
`sha256:60354e98e3775c2fecf6d447dbd37fa058244dd21218b7fad0dfb5bd27cb221f`
versus observed aggregate
`sha256:f6c3b3f4b8d89829da9b0b11cc7d308c13c267bf05e98aeb9ab9d6e19bec7267`.
The current digest will advance when v4 and its verdict are appended; the
implementation-start recovery must recompute and bind that exact preimage.

The pre-review dirty bridge baseline is additive only and digest-bound:

| Dirty bridge path | SHA-256 |
| --- | --- |
| `bridge/gtkb-file-move-rename-canonicalization-repair-forward-003.md` | `25b7d58dfc34435213f21fb469b40eb897e6f0d1170d1dfb025b2d0de094549b` |
| `bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md` | `7930cff48d7cbe5113e2f3479397f5372f05bc8e7e0eb39e0808e1371b41a458` |
| `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-005.md` | `27a869ec42aa04f1c32d0a96bd53220f2e94f5c7733a1b540e51d709cf952157` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-001.md` | `a4e2a5c9b98bcc9bf85a4051a55d84ac8c076eb804b03fd0565c66e067d1862c` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-002.md` | `5e9182579b274085d04f30e3fe824796c1e08b02ab1ab8ac2e626dc0c08d2a38` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-003.md` | `0a296ce6a4e6859311d46b19cb5da56b91b8dc3cf817a1fa7a0d32776a85e5cd` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-004.md` | `819c0e023edd02bdcf1d77716e7a9c97fa50ab9fc102cd69e43678365905a324` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-005.md` | `ad51cc88d00cedf18ac2556b31d43a2ac8fd609a7a03f02a8a93a5ae1bf81714` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-006.md` | `23759f5c7e7aa9bf74d77961f126ab000c020983eccf835c4a120ffaf2585720` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md` | `fa20db72e562dc55e6b3813e098719cde932e104e07b4dd33ef2a1b5ffe1ba37` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-008.md` | `52f91def544b46f31ff7a4ea96c9396537684b12b275a4398466992f11ad0053` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md` | `0cf237f2f192e6f7bef380c217b387cdfc71c895b593f587b0a78d96d7ea4d4e` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-010.md` | `3995190a9aec5043cac9714954ce13a4f21b60628158a626fd6f99b331cb102f` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-011.md` | `9bc28c1aac68e4c5217683cab61b3e1442efe2ab5e5bd84ca62d581b490481d0` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v2-001.md` | `2d63a7cd6f8bde82bf439927139b393098bbfd561d8c6d08a9b676594ef7de95` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v3-001.md` | `b23a9c2b1244c9260137bce21e31cbce0dccddd8abcc6a47bc6bf3c6d9039410` |
| `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v3-002.md` | `ff5c3389aec69c77d6bb451dc4377ffbc9e7fd6b96d40060b99ecbecd1d6f6c7` |

After fresh GO, Prime acquires the exact v4 claim/start packet and recovery must:

1. require a coherent registry with only `bridge-versioned-files` stale;
2. recapture `git status --porcelain` for `bridge/`, require the table above plus
   only the strict-valid v4 proposal and independent GO paths, and bind every
   path/content digest; a NO-GO authorizes no bootstrap and any later revision
   must refresh this inventory;
3. classify the affected exact slugs with the canonical resolver: repair-forward
   valid at latest `NO-GO`; WI-5441 v3 valid at terminal `WITHDRAWN`; v4 valid at
   `NEW -> GO`; original WI-5441 quarantined at its ninth entry with
   `WRONG_BRIDGE_VERSION_METADATA`; WI-5441 v2 quarantined at its first entry
   with `DUPLICATE_BRIDGE_METADATA`; and non-v2 WI-5279 quarantined at its
   second entry with `WRONG_STATUS_AUTHOR_ROLE`;
4. treat those three exact malformed chains only as non-authorizing immutable
   audit evidence. Aggregate observation records their bytes but never promotes
   them to lifecycle-valid, review-current, or implementation-authorizing state;
5. refuse every unenumerated path, changed digest, changed diagnostic, new
   version on a quarantined slug, modified/deleted tracked bridge path,
   unrelated stale registry record, missing authority, expired claim, or replay;
6. update the currently unregistered writer and implementation-start gate, use
   the existing narrowly logged emergency bridge-repair boundary for one
   bounded edit of the registered registry-control-plane module, and add a
   dedicated recovery operation consuming the exact inventory plus active
   WI-5441 GO/claim/PAUTH evidence;
7. append one aggregate observation revision through the canonical registry
   service without direct SQLite access, require coherent/current inspection,
   and issue a receipt containing old/new aggregate digests, every path digest,
   exact resolver classifications, and quarantine diagnostics;
8. restore the temporary gate bootstrap hunk to exact pre-bootstrap bytes; and
9. register every load-bearing writer/helper/template/test named here plus
   generated Codex parity outputs in one TOML/package/projection transaction,
   then continue all registered edits through ordinary capability observation.

This is not a general malformed-chain waiver. It is a one-use, exact-evidence
recovery that observes preserved audit bytes while failing closed on any
unreviewed difference.

### 4. Canonical copies and parity

`.claude/skills` remains canonical. Generate `.codex/skills` copies through
`scripts/generate_codex_skill_adapters.py`; update current and legacy scaffold
templates containing the helpers; require `--check` to report zero drift.
Register the central writer, canonical helpers, generated adapters/manifest,
templates, proposal-filing service, and enforcing tests before their ordinary
post-bootstrap mutation.

No harness role is persisted or shared. Evidence binds to the author/claim
session for one event.

## Requirement Sufficiency

Existing requirements sufficient.

The owner registry invariant plus the linked registry, bridge-authority,
project-authorization, mechanical-enforcement, and parity specifications
already require the correction. No new requirement is needed before this
bounded implementation. The proposal adds implementation and test detail; it
does not create a competing authority model.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations And Related Work

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` controls
  registry membership and automatic mutation observation.
- v010 supplies F1/F2 and independent implementation evidence.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` is the
  current controlling `NO-GO` on the overlapping strict-valid thread.
- The non-v2 WI-5279 fifth entry, WI-5687, and TEST-11708 preserve malformed
  sibling disposition and exact-slug false-GO follow-up.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` preserves the shared
  target-path finding and is addressed by the sole-carrier controls above.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v3-002.md`
  preserves the unexecutable bootstrap as terminal withdrawn evidence.
- Required search for "bridge publication registry currentness" found no more
  specific controlling decision.

## Owner Decisions / Input

The owner directed that the registry is the ultimate artifact SoT, every
registered mutation update it automatically, every load-bearing artifact be
registered, and this Prime session deliver WI-5441 before WI-5640 resumes. The
active PAUTH permits source, test, configuration, metadata, and one bounded
local VERIFIED finalizer commit; it forbids push, dispatcher mutation, cleanup,
release, deployment, credentials, and history rewrite. No new decision is
required.

## Cross-Harness Disposition

- Claude uses the canonical `.claude/skills` publication helpers.
- Codex uses generated `.codex/skills` adapters and the same central writer.
- Current and legacy scaffold templates receive the same helper behavior.
- Other harnesses that invoke the central writer receive the same transaction;
  no new native hook or persisted harness-role state is claimed.

## Specification-Derived Verification Plan

| Requirement | Exact executable evidence | Expected result |
| --- | --- | --- |
| Typed authority | Registry unit tests for success plus missing claim, wrong session/status/version/path/content, failed compliance, expiry, replay, fabricated evidence | One exact consume; every mismatch denies |
| Ordering | Writer/proposal-helper tests for NEW, REVISED, NO-ACTION, GO, NO-GO | Observe/current before release |
| Failure rollback | Inject create, reread, consume, currentness, release failures | No silent success; documented file/claim/currentness |
| VERIFIED compensation | Finalizer/provider tests with commit and index-realignment failures | Compensating revision or retained repair-required state |
| Bootstrap quarantine | Exact additive baseline plus v4/GO success; unknown path, digest/diagnostic drift, modified/deleted tracked path, unrelated stale, missing authority, and replay negatives | One receipt-bound observation; known malformed chains remain non-authorizing; every mismatch blocks |
| Registry admission | Registry tests and `gt registry inspect --no-census --json` | Chokepoints registered; stores coherent/current |
| Parity | `python scripts/generate_codex_skill_adapters.py --check` and adapter tests | Zero drift |
| Existing contract | Rerun v009/v010 commands including full implementation-start module | Reproducible claims; disclosed unrelated residuals only |
| Finalization report | Parser test and dry-run include-set validation | DB evidence-only, never included |
| Sibling | Canonical strict resolver plus latest-status/claim checks for WI-5279 base and v2 | Base chain quarantined; v2 remains sixth-entry NO-GO and unclaimed; one WI-5441 transaction owns shared hunks |

## Acceptance Criteria

1. Successful publication implies coherent/current registry before claim
   release.
2. Bridge evidence uses typed bridge authority, never fabricated PAUTH fields.
3. Failure restores and observes the aggregate or retains claim/artifact with
   a repair-required error.
4. Bootstrap is exact-inventory, digest- and diagnostic-bound, receipt-bound,
   non-replayable, and leaves no permanent exemption or raw database mutation.
   It observes the three named malformed chains only as non-authorizing audit
   evidence and fails closed on every unenumerated difference.
5. All touched load-bearing publication chokepoints are registered; generated
   adapters and templates are current.
6. The malformed WI-5279 base chain remains quarantined; the strict-valid v2
   thread remains sixth-entry `NO-GO` and unclaimed during mutation; exactly one
   WI-5441 transaction owns the absorbed test-only hunks. WI-5687/TEST-11708
   preserve exact-slug and false-live-GO prevention.
7. The next report excludes `groundtruth.db` from Files Changed and every
   finalizer include while preserving reproducible by-reference evidence.
8. All v007 conditions remain. WI-5640 stays paused pending VERIFIED WI-5441
   and separately authorized registry locator transitions.
9. The v4 proposal/verdict chain passes the canonical strict resolver before
   any implementation authority packet is accepted.

## Risk And Rollback

Rollback is allowed only for a newly created, not-yet-published version in the
same capability transaction; prior numbered files remain append-only. The
bootstrap is bounded to one stale record, reviewed v4 GO/claim/packet, exact
additive dirty inventory, three named quarantine diagnostics, a temporary gate
hunk restored byte-for-byte, and a durable receipt. Any inventory, digest,
diagnostic, claim, or currentness mismatch stops before mutation and returns to
independent review.

No commit occurs until a new report is independently VERIFIED. Finalizer
include paths are only report-claimed git artifacts. The ignored runtime DB is
never included.

## Pre-Filing Preflight

Run applicability and mandatory clause preflights against this exact content.
File only with no missing required specification and no blocking clause gap.

## Requested Loyal Opposition Action

Review this executable v4 replacement proposal. Do not append a verdict to the
structurally invalid predecessor chains or the withdrawn v3 thread. File GO only
if typed publication authority, exact quarantine recovery, release ordering,
rollback compensation, registration, DB exclusion, and WI-5279 shared-file
consolidation are mechanically complete. Otherwise file exact NO-GO findings.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
