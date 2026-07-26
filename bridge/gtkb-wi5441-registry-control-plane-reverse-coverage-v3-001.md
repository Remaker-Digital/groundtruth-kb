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

# WI-5441 Registry Control Plane And Bridge Publication Currentness Strict Fresh Replacement Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5441-registry-control-plane-reverse-coverage-v3
Version: 001
Supersedes invalid audit chains: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-011.md; bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v2-001.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: [".claude/hooks/sot-read-discipline.py",".claude/settings.json",".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py",".claude/skills/gtkb-bridge/helpers/impl_report_bridge.py",".claude/skills/gtkb-bridge/helpers/revise_bridge.py",".claude/skills/gtkb-verify/helpers/write_verdict.py",".codex/gtkb-hooks/run_py_no_window.py",".codex/skills/MANIFEST.json",".codex/skills/gtkb-bridge/SKILL.md",".codex/skills/gtkb-bridge-propose/helpers/write_bridge.py",".codex/skills/gtkb-bridge/helpers/impl_report_bridge.py",".codex/skills/gtkb-bridge/helpers/revise_bridge.py",".codex/skills/gtkb-proposal-review/SKILL.md",".codex/skills/gtkb-send-review/SKILL.md",".codex/skills/gtkb-verify/SKILL.md",".codex/skills/gtkb-verify/helpers/write_verdict.py","config/agent-control/gtkb-harness-capability-registry.toml","config/hooks/gtkb-sot-read-discipline.py","config/registry/sot-artifacts.toml","groundtruth.db","groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py","groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py","groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py","groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py","groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/db.py","groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py","groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py","groundtruth-kb/src/groundtruth_kb/project/doctor.py","groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","groundtruth-kb/src/groundtruth_kb/project/sot_registry.py","groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py","groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py","groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py","groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py","groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py","groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py","groundtruth-kb/tests/test_backlog_update_cli.py","groundtruth-kb/tests/test_bridge_propose_helper.py","groundtruth-kb/tests/test_cli_bridge_propose.py","groundtruth-kb/tests/test_context_manifest.py","groundtruth-kb/tests/test_db.py","groundtruth-kb/tests/test_hygiene_reclaim.py","groundtruth-kb/tests/test_inventory_string_scan.py","groundtruth-kb/tests/test_registry_control_plane.py","groundtruth-kb/tests/test_sot_duplicate_audit.py","groundtruth-kb/tests/test_sot_registry.py","groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py","platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py","platform_tests/groundtruth_kb/test_cli_bridge_propose.py","platform_tests/scripts/test_check_protected_commit_authorization.py","platform_tests/scripts/test_check_sot_duplicate_guard.py","platform_tests/scripts/test_check_sot_read_discipline.py","platform_tests/scripts/test_check_sot_registry_completeness.py","platform_tests/scripts/test_controlled_artifact_paths.py","platform_tests/scripts/test_evidence_freshness_boundary.py","platform_tests/scripts/test_generate_codex_skill_adapters.py","platform_tests/scripts/test_gtkb_bridge_writer.py","platform_tests/scripts/test_gtkb_file_reference_migration.py","platform_tests/scripts/test_gtkb_service_sot_restore_registry.py","platform_tests/scripts/test_hygiene_strays_cli.py","platform_tests/scripts/test_implementation_start_gate.py","platform_tests/scripts/test_modernization_artifact_decontamination.py","platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py","platform_tests/scripts/test_provider_verdict_status_consistency.py","platform_tests/scripts/test_registry_observation_hook.py","platform_tests/scripts/test_release_candidate_gate.py","platform_tests/scripts/test_sot_read_discipline_hook.py","platform_tests/scripts/test_sot_read_discipline_narrative_completion.py","platform_tests/scripts/test_worktree_finalization_triage.py","platform_tests/skills/test_bridge_impl_report_helper.py","platform_tests/skills/test_bridge_propose_helper.py","platform_tests/skills/test_bridge_propose_helper_work_intent.py","platform_tests/skills/test_bridge_revise_helper.py","platform_tests/skills/test_verified_finalization_validation_hardening.py","scripts/check_protected_commit_authorization.py","scripts/controlled_artifact_paths.py","scripts/evidence_freshness_boundary.py","scripts/gtkb_bridge_writer.py","scripts/gtkb_file_reference_migration.py","scripts/implementation_start_gate.py","scripts/registry_observation_hook.py","scripts/release_candidate_gate.py"]

## Clean-Thread Replacement

The predecessor chain is preserved but cannot carry implementation authority.
The strict lifecycle resolver fails at
bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md with
WRONG_BRIDGE_VERSION_METADATA because its version field appends parenthetical text instead of containing
only the exact three-digit value. Later v010 and v011 entries cannot remove
that predecessor defect.

The first fresh replacement at the v2 slug is also quarantined. Its explanatory
prose repeated a colon-bearing metadata field label, which the strict parser
correctly interpreted as duplicate metadata. This v3 wording avoids metadata
field labels in prose and is validated as fully rendered content before filing.

This fresh slug starts at exact version 001. It carries the complete v011
correction without treating an invalid predecessor or a status-only bridge
listing as authority. Implementation remains paused until an independent GO is
filed on this v2 thread and the strict resolver accepts the resulting chain.

The non-v2 WI-5279 sibling is also structurally invalid:
bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-002.md has GO status but no
resolvable Loyal Opposition author role. It therefore cannot authorize
implementation. Its v005 NO-ACTION remains audit evidence, not a terminal-state
dependency for this v2 thread. WI-5687/TEST-11708 retains the defect that
status-only surfaces exposed the malformed sibling as a live GO.

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

### F2 - undispositioned sibling WI-5279 GO

The exact non-v2 sibling is no longer Prime-actionable. Prime filed
`bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-005.md` as `NO-ACTION`,
citing the already-absorbed WI-5441 fixture hunks and requesting independent
terminal review. Its status-token sequence is
`NEW -> GO -> NO-ACTION -> GO -> NO-ACTION`; the latest status is
Loyal-Opposition-actionable, not implementation authority.

The standing follow-up is WI-5687 with TEST-11708 under
PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY. It requires exact-slug enumeration,
fail-closed overlapping-GO detection, and no prefix merge of base and `-v2`
siblings. The canonical strict resolver proves that the sibling cannot authorize implementation. No concurrent WI-5279 source mutation is allowed; any future repair must use a fresh independently reviewed thread.

### Attribution correction for the failed WITHDRAWN attempt

The writer supports non-dispatchable `WITHDRAWN` content when no session-role
envelope is supplied. My failed attempt included `::init gtkb pb` and
`::open build`; the writer correctly rejected that envelope because WITHDRAWN
has no harness-role mapping. The v005 statement that the writer lacks
WITHDRAWN support is inaccurate. No file was created. This revision does not
add a specious mapping or assign owner-only DEFERRED state to a harness role.

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

### 3. One-time fail-closed bootstrap

This v2-001 proposal and its independent verdict necessarily use the defective writer before the repair exists. After fresh GO, Prime acquires the exact claim/start packet:

1. require a coherent registry with only `bridge-versioned-files` stale;
2. inventory dirty bridge paths against HEAD, require append-only numbered
   files, validate each affected exact slug with the strict resolver, rerun
   compliance/author checks, and bind all path/content digests;
3. update the currently unregistered writer and implementation-start gate;
4. use the existing narrowly logged emergency bridge-repair boundary for one
   bounded edit of the registered registry-control-plane module;
5. add a dedicated recovery operation that consumes the exact inventory and
   active WI-5441 GO/claim/PAUTH evidence, then appends one aggregate revision
   without direct SQLite access;
6. require coherent/current inspection and restore the temporary gate
   bootstrap hunk to exact pre-bootstrap bytes;
7. register every load-bearing writer/helper/template/test named here plus
   generated Codex parity outputs in one TOML/package/projection transaction;
8. continue all registered edits through ordinary capability observation.

Recovery refuses modified/deleted tracked bridge files, unrelated stale
records, invalid affected chains, missing evidence, replay, or a changed
inventory. Its receipt includes old/new aggregate digests and the exact
validated files.

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
- WI-5279 v005, WI-5687, and TEST-11708 preserve sibling disposition/follow-up.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` covers shared-target
  coordination.
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
| Bootstrap | Stale-bridge-only success plus dirty tracked, unrelated stale, invalid chain, changed inventory, missing authority, replay negatives | One receipt-bound repair only |
| Registry admission | Registry tests and `gt registry inspect --no-census --json` | Chokepoints registered; stores coherent/current |
| Parity | `python scripts/generate_codex_skill_adapters.py --check` and adapter tests | Zero drift |
| Existing contract | Rerun v009/v010 commands including full implementation-start module | Reproducible claims; disclosed unrelated residuals only |
| Finalization report | Parser test and dry-run include-set validation | DB evidence-only, never included |
| Sibling | Exact base/v2 bridge show plus WI-5687/TEST-11708 lookup | No duplicate GO or prefix merge |

## Acceptance Criteria

1. Successful publication implies coherent/current registry before claim
   release.
2. Bridge evidence uses typed bridge authority, never fabricated PAUTH fields.
3. Failure restores and observes the aggregate or retains claim/artifact with
   a repair-required error.
4. Bootstrap is exact-inventory, receipt-bound, non-replayable, and leaves no
   permanent broad exemption or raw database mutation.
5. All touched load-bearing publication chokepoints are registered; generated
   adapters and templates are current.
6. The malformed WI-5279 base chain is quarantined as non-authorizing evidence; WI-5687/TEST-11708 preserves exact-slug and false-live-GO prevention.
7. The next report excludes `groundtruth.db` from Files Changed and every
   finalizer include while preserving reproducible by-reference evidence.
8. All v007 conditions remain. WI-5640 stays paused pending VERIFIED WI-5441
   and separately authorized registry locator transitions.

## Risk And Rollback

Rollback is allowed only for a newly created, not-yet-published version in the
same capability transaction; prior numbered files remain append-only. The
bootstrap is bounded to one stale record, reviewed GO/claim/packet, exact dirty
inventory, a temporary gate hunk restored byte-for-byte, and a durable receipt.

No commit occurs until a new report is independently VERIFIED. Finalizer
include paths are only report-claimed git artifacts. The ignored runtime DB is
never included.

## Pre-Filing Preflight

Run applicability and mandatory clause preflights against this exact content.
File only with no missing required specification and no blocking clause gap.

## Requested Loyal Opposition Action

Review this fresh replacement implementation proposal. Do not append a verdict to the structurally invalid predecessor chain. File GO only if typed publication authority, bootstrap, release ordering,
rollback compensation, registration, DB exclusion, and sibling disposition
are mechanically complete. Otherwise file exact NO-GO findings.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
