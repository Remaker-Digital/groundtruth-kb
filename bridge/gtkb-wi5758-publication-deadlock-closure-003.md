NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - WI-5758 publication-deadlock closure

bridge_kind: implementation_report
Document: gtkb-wi5758-publication-deadlock-closure
Version: 003
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5758-publication-deadlock-closure-002.md
Controlling GO: bridge/gtkb-wi5758-publication-deadlock-closure-002.md
Approved proposal: bridge/gtkb-wi5758-publication-deadlock-closure-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5758
target_paths: ["scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py", "platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py"]

implementation_scope: exact-eight-path-publication-recovery-observation-and-reporting-closure
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

## Implementation Claim

Implemented all four changes approved in versions 001/002:

1. governed bridge publications preserve truthful aggregate evidence on
   retained-file compensation failures;
2. pending publication state survives process death without persisting the raw
   capability secret, and later processes can finalize or roll back the exact
   publication;
3. `gt registry observe` provides an honest operator-attributed escape hatch
   for already-registered identities; and
4. `gt bridge state-report` surfaces bridge-publication aggregate currentness
   plus a runnable remedial command before the publication gate fails closed.

Independent pre-report review found two crash-idempotency defects, incomplete
sidecar-to-row binding, unsafe cleanup ordering, an incomplete operator remedy,
and a broader filesystem/SQLite concurrency race. The bounded defects were
corrected before this report: rollback now uses atomic quarantine and survives
hard exits on either side of its commit, sidecars bind every exact row field,
cleanup failure cannot compensate an already released publication, and the
remedy includes `--change-reason`.

The broader concurrency class across direct filesystem writers plus the
existing consume/compensate paths is preserved for later corrective intake in
`bridge/gtkb-advisory-bridge-publication-recovery-toctou-001.md`. No claim of
universal cross-process exclusion is made here.

No dispatcher or TAFE process was activated or mutated. No Git index, commit,
push, deployment, release, credential, external system, project definition,
PAUTH definition, or formal artifact was changed. Live database activity was
limited to normal claim/authorization audit bookkeeping; implementation and
tests did not run operator observation against the live registry aggregate.

## First-Line Role Eligibility And Implementation Authority

- Current role: Prime Builder from the owner-declared `::init gtkb pb` session
  envelope; harness A is active and registered as Prime Builder.
- Status authored: `NEW`, the Prime Builder implementation-report status after
  an independent GO.
- Project authority model: WI-5758 is an active member of the active parent
  project and inherits its active whole-project PAUTH. No per-WI approval is
  treated as authority.
- Schema-v3 implementation packet:
  `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5758-publication-deadlock-closure.json`.
- Packet hash:
  `sha256:35d494f77bfdc97dcea7850dee44c91e1b9e293e4d2762acd3bb2e1ab3a6ec5b`.
- Pre-start packet hash:
  `sha256:edc59a68ed08743ce619a6a77d59cc15ead8a8512b6e8222400cb9dacb2f87fc`.
- Operation-time evaluator decision: allowed for all eight exact target paths,
  classified as four `source` and four `test` mutations under PAUTH version 3.
- Claim session: `019fb19b-7814-73c1-8707-204e432cbf00`; claim acquired at
  `2026-07-30T09:17:25Z` and extended twice while implementation and
  independent defect review completed.

The implementation-start transaction succeeded and produced its final packet
at `2026-07-30T09:26:28Z`, but required approximately 527 seconds. That
known peer-history scan cost remains documented in
`bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md`; no gate
was bypassed.

## Files Changed

- `scripts/gtkb_bridge_writer.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py` (new)

Scoped tracked diff: 1,770 insertions and 22 deletions across seven tracked
files, plus the new 157-line CLI test module. All eight paths are unstaged.
No foreign or unapproved path entered the implementation cohort.

## Implementation Details

### Durable, secret-free pending publication state

`write_bridge_file()` now persists an atomic sidecar before bridge-file
creation under `.gtkb-state/bridge-publication-pending/`. It records schema,
capability hash, content digest, document, version, status, target, session,
and creation time, but never the raw capability secret. File bytes are flushed
and `fsync`-ed before `os.replace()` publishes the sidecar.

The loader validates schema and every binding, including the target derived
from document/version. Restart recovery passes those exact fields to the
control plane; recovery selects the exact capability hash plus target/session
row and rejects any binding mismatch. Claim release derives its slug from the
verified recovery receipt rather than trusting sidecar prose.

Successful consume+claim release, deferred finalize, rollback, and
compensation remove the sidecar. A cleanup-only failure after a completed
publication is non-destructive and cannot enter compensation after the claim
has already been released.

### Crash-idempotent finalize and rollback

`recover_bridge_publication()` supports secret-free recovery of exact
`minted`, `expired`, `consumed`, and terminal `compensated` states:

- finalize from `minted`/`expired` requires exact target bytes, exact preimage,
  latest preimage evidence, two stable aggregate scans, and repeated target
  digest validation before appending the post-image revision and consuming the
  row;
- finalize from `consumed` is idempotent when the exact target and current
  revision remain present;
- rollback atomically moves the target to a deterministic same-volume
  quarantine, validates the quarantined bytes, restores or retains unknown
  bytes on mismatch/failure, restores preimage evidence, and marks the row
  compensated;
- rollback from `consumed` with the target already quarantined/missing resumes
  safely after a pre-commit process death; and
- retry from `compensated` validates current preimage truth, removes any exact
  post-commit quarantine orphan, and returns the existing receipt.

Hard-exit tests use child processes and `os._exit`, not only cleared module
state. They cover the original create-before-consume crash plus rollback exits
before compensation commit and after commit but before quarantine cleanup.

### Truthful retained-file observation

Compensation failure paths preserve `recovery_required` and the exact failure
reason while appending an aggregate revision that truthfully observes retained
filesystem state. The revision uses
`operation='direct_in_place_content_change'` and binds
`evidence_source_reference` to the capability hash. Currentness is restored
without laundering the anomaly or granting new mutation authority.

### Operator observation escape hatch

The previously hidden `gt registry observe` surface now supports:

- legacy internal `--event-file` capability consumption;
- repeatable `--artifact <registry-id>` for glob/aggregate identities;
- repeatable `--path <project-relative-path>` for registered exact paths;
- required `--change-reason`, optional `--changed-by`, and `--json`; and
- actor-session resolution from the active harness/session environment, with
  honest `unattributed_external` fallback.

`append_passive_observation()` accepts exact record IDs as well as resolved
paths, refuses virtual, unregistered, or missing identities, and changes only
revision evidence. Tests prove currentness restoration and declaration-row
preservation.

### Pre-cliff registry publication visibility

`gt bridge state-report` adds a top-level `registry_publication` block:

```text
enabled, aggregate_current, stale_count, stale_record_ids
```

The check is scoped to `bridge-versioned-files`; incomplete control-plane
fixtures disable it without changing queue semantics. Markdown adds a fourth
owner table and, when stale, warns that all bridge publication will fail and
prints the runnable command:

```text
gt registry observe --artifact bridge-versioned-files --change-reason "Re-observe bridge publication aggregate"
```

The report remains read-only. A live read-only measurement completed in
19.291 seconds and materialized 630,546 output characters; the access-cost
context is linked to the existing append-only latency advisory and the new
concurrency Advisory rather than hidden.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `GOV-17`
- `GOV-10`
- `SPEC-1662`
- `SPEC-1830`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Related Artifacts

- `DELIB-202667526` - live concurrency evidence and control-plane lock convoy.
- `DELIB-202667531` through `DELIB-202667534` - project authorization, design
  constraints, and WI-5758 routing.
- `bridge/gtkb-lo-bridge-publication-registry-currentness-deadlock-advisory-001.md`
  and `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` - source
  deadlock advisories.
- `bridge/gtkb-wi5758-publication-deadlock-closure-001.md` and `-002.md` - exact
  approved design and independent GO.
- `bridge/gtkb-advisory-bridge-publication-recovery-toctou-001.md` - residual
  cross-process concurrency class found during implementation review.
- `bridge/gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md` and
  `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md` -
  append-only access-cost evidence.
- WI-5696 remains the separate general admission/automatic-observation lane;
  this implementation changes only the bridge-publication loop and operator
  escape hatch described in the approved proposal.

## Owner Decisions / Input

No new owner decision is required for independent verification of this bounded
implementation. WI-5758 remains inside the active parent project's PAUTH and
exact GO. The residual broader concurrency correction is diagnostic only and
must be routed later through an active project-linked carrier; it is not
silently implementation-approved by this report.

## Requirement Sufficiency

Existing requirements remain sufficient for the approved WI-5758 changes and
their bounded safety corrections. They are not sufficient to select a
universal cross-process coordinator or incremental aggregate-index design;
that future architecture work remains explicitly deferred to the concurrency
Advisory and independent alternatives investigation.

## Spec-to-Test Mapping

| Approved requirement / behavior | Executed evidence |
| --- | --- |
| Consecutive governed publications remain current | `test_three_sequential_bridge_publications_remain_current_without_manual_observation` performs three mint/create/consume cycles and asserts currentness after each. |
| Retained compensation failures preserve truthful currentness and audit debt | Registry-control-plane compensation tests assert retained bytes, `recovery_required`, capability-bound passive revision, and current aggregate. |
| Create-before-consume process death is recoverable | `test_hard_exit_between_create_and_consume_recovers_in_fresh_process` uses a real child `os._exit`, durable secret-free sidecar, later finalize, claim release, and currentness assertion. |
| Rollback is crash-idempotent on both sides of commit | Parameterized hard-exit test covers pre-commit quarantine and post-commit/pre-cleanup exit; retry removes exact quarantine and reaches terminal compensated state. |
| Sidecar recovery binds the exact capability row | `test_restart_recovery_rejects_sidecar_capability_hash_mismatch` preserves file, sidecar, and claim on mismatch. |
| Cleanup-only failure cannot undo a completed publication | `test_sidecar_cleanup_failure_does_not_compensate_released_publication` asserts file retention and consume/release ordering. |
| Operator observation restores registered identities without declaration mutation | CLI tests assert revision provenance, scoped currentness, unknown/missing rejection, and unchanged registry declarations. |
| State report surfaces current/stale aggregate without queue mutation | State-report tests assert JSON/Markdown states, complete remedy, unchanged bridge queue payload, and byte-identical input files. |
| No new lifecycle token or dispatcher/TAFE dependency | Full `VALID_STATUSES` set is pinned; pending sidecars are not read by queue derivation; no changed target is dispatcher/TAFE configuration. |
| Project/bridge operation-time authority | Schema-v3 packet records allowed source/test classifications for all eight exact targets under the parent-project PAUTH and independent GO. |

## Commands Executed And Observed Results

- Implementation-start gate:
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5758-publication-deadlock-closure --session-id 019fb19b-7814-73c1-8707-204e432cbf00`.
  Result: exit 0; valid schema-v3 packet; approximately 527 seconds.
- First integrated suite: `95 passed`, one pre-existing `asyncio_mode` warning.
- Expanded final suite:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py groundtruth-kb/tests/test_registry_control_plane.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py -q --tb=short`.
  Result: `102 passed`, one pre-existing warning, 74.52 seconds.
- Post-format focused safety suite: `7 passed`, same warning, 11.04 seconds.
- Ruff check on all eight target files: `All checks passed!`.
- Ruff format check: `8 files already formatted`.
- `git diff --check -- <eight targets>`: exit 0; only Git informational
  future-CRLF warnings.
- `gt registry observe --help`: exit 0 and displays artifact/path/reason/actor/
  JSON options; no live observation was executed.
- Live read-only `gt bridge state-report --json`: exit 0, 19.291 seconds,
  630,546 output characters.
- Independent post-fix subagent review: no blocking findings remain across
  crash idempotency, exact binding, cleanup ordering, runnable remedy, or the
  bounded atomic-quarantine/stable-observation mitigations.

## Acceptance Criteria Status

- [x] Successful governed publications leave the aggregate current without manual observation.
- [x] Retained compensation failures preserve truthful currentness and visible audit debt.
- [x] Process death between create and consume is finalizable by a fresh process without the raw secret.
- [x] Rollback is exact, quarantined, and idempotent across pre/post-commit process death.
- [x] Mismatched bytes and sidecar/row bindings fail closed.
- [x] Operator observation restores currentness only for existing registered identities under honest provenance.
- [x] Registry declaration, identity, lifecycle, and membership surfaces remain unchanged by observation.
- [x] State report surfaces current/stale aggregate and a runnable remedy without changing queue semantics.
- [x] No new bridge status token, pending lifecycle state, dispatcher/TAFE write, or application-root placement change.
- [x] Pytest, Ruff check, Ruff format check, and diff check pass.
- [x] Only the eight approved in-root targets changed.

## Risk And Rollback

Residual risks are explicit:

- stable repeated finalize observation is not a universal filesystem mutex;
- existing consume/compensate paths require the broader concurrency review;
- sidecar cleanup still benefits from future generation-aware coordination;
- scoped bridge aggregate hashing adds measurable cost as append-only history
  grows; and
- operator observation truthfully records present state but is not mutation
  authority and must not be used to launder unknown identity transitions.

These risks are bounded by exact bindings, fail-closed validation, atomic
quarantine, audit-preserving `recovery_required`, read-only reporting, and the
separate concurrency Advisory.

Rollback before terminal finalization is an exact-path revert of the eight
implementation targets. Runtime sidecars/quarantines are bookkeeping pointers;
recovery re-verifies every row and byte before acting. Numbered bridge history,
claims, packets, advisories, and approval evidence remain immutable audit
records and are not deleted by rollback.

## Loyal Opposition Asks

1. Independently verify the eight-file diff against versions 001/002 and the
   schema-v3 packet.
2. Re-run the 102-test suite plus Ruff/diff checks.
3. Inspect hard-exit recovery, terminal idempotency, exact sidecar bindings,
   retained-file observation, operator observation boundaries, and read-only
   state-report behavior.
4. Confirm the implementation does not overclaim resolution of the broader
   cross-process race recorded in the separate Advisory.
5. Return `VERIFIED` through governed atomic finalization if satisfied, or
   `NO-GO` with concrete findings.

## Mutation Boundary

No dispatcher or TAFE state was activated or mutated. This report is filed as
the next numbered bridge file without the canonical helper because that helper
would publish dispatcher/TAFE state contrary to the owner's deliberate repair
hold. The implementation claim is released only after this exact report exists
and passes candidate preflights.

## Pre-Filing Preflight

Before filing, this exact candidate must pass credential scan, bridge
compliance audit-only, applicability preflight, mandatory clause preflight,
Prime Builder status eligibility, exact target absence, and live-claim checks.
Any blocking result stops publication.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
