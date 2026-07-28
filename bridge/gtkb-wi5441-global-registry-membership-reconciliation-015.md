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

# GT-KB Bridge Implementation Report - gtkb-wi5441-global-registry-membership-reconciliation - 015

bridge_kind: implementation_report
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 015
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-014.md
Controlling GO: bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md
Prior implementation report: bridge/gtkb-wi5441-global-registry-membership-reconciliation-013.md
Approved proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
Recommended commit type: fix:

## Revision Claim

The v014 blocking test failure is corrected, the entire affected suite has been
run, and the known WI-5178 residuals are named precisely. A fresh canonical
reconciliation after commit `f3e353db6` then exposed two load-bearing package
members that the previous Git-index-only observer could not see while they were
untracked. This revision repairs that observer blind spot, admits exactly those
two members through the canonical additive registry transaction, corrects the
classification of unreadable disposable paths, and records a complete deep
census with zero load-bearing and zero unknown gaps.

No artifact was deleted, moved, renamed, retired, narrowed, or replaced. No
WI-5640 Stage B apply, obsolete-source cleanup, dispatcher activation, push,
release, deployment, credential action, or history rewrite occurred.

## Response To v014 NO-GO

- **F1 closed.** The expected classification for `.codex/hooks.json` is now
  `registry:wi5441-member-codex-hooks-json-82c735c2c8`, matching the canonical
  exact registry record. The complete
  `platform_tests/scripts/test_implementation_start_gate.py` suite collected
  210 tests and returned 206 passed / 4 failed. The v014-introduced failure is
  gone. The four residuals are the pre-existing WI-5178 fixtures:
  `test_work_intent_acquire_denial_creates_no_claim`,
  `test_work_intent_extension_denial_leaves_claim_unchanged`,
  `test_work_intent_renew_denial_leaves_go_claim_unchanged`, and
  `test_work_intent_reclassify_denial_leaves_draft_claim_unchanged`. The first
  two expected denials do not raise; the latter two refer to the absent
  `WorkIntentAuthorizationError` symbol. None is changed by WI-5441.
- **F2 framing corrected.** v012 prescribed a `Controlling GO:` remedy that the
  checker did not implement. v013 implemented that new mechanism within the
  already-authorized v007/v008 target paths. The path authorization was
  pre-existing; the accepted-link mechanism was implementation-time work and is
  not described here as previously implemented or previously reviewed.
- **F3, F4, and F5 retained as separate hardening candidates.** The ordinal
  constraint, independent packet/chain derivation, and resolver-backed test
  fidelity findings are valid, but v014 explicitly made them nonblocking. They
  are preserved durably in v014 and the existing finalization-path advisory
  chain. This revision does not weaken or further change the protected-commit
  checker.
- **F6 retained as nonblocking cleanup.** The misleading test name is preserved
  as a separate exact-scope cleanup rather than mixed into registry closure.
- **F7 closed.** `DELIB-202667356` is cited below and its constraint is carried:
  corrected-chain support must not weaken protected-commit controls, and
  terminal history remains resolved through the public lifecycle resolver.

## Fresh-State Repair Forward

v014 correctly verified the bytes and evidence in v013, but its instruction not
to rerun registry work relied on the then-stated 2,346-record closure. The owner
commit at `f3e353db6` made the reconciliation source and its test Git-tracked.
A fresh canonical reconciliation then reported exactly two
`unregistered_load_bearing` candidates:

- `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py`
- `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`

The old package observer enumerated only `git ls-files`, so it could not report
new nonignored files before their first commit. The observer now enumerates
`git ls-files --cached --others --exclude-standard`. It therefore sees tracked
and untracked nonignored package/test members while continuing to exclude
ignored caches and runtime debris. A temporary-repository regression proves all
three cases.

The first corrected deep census then found 278 unreadable entries and classified
all of them `invalid_unknown` before consulting either registry identity or
observer evidence. All 278 were disposable runtime/cache objects: 241 under
`.gtkb-state`, 27 under `.pytest-tmp`, and 10 in package test/runtime caches.
Unreadable paths now retain the same authority ordering as readable paths:
registered unreadable entries are `invalid_unknown`, observed unreadable entries
are `unregistered_load_bearing`, and unregistered/unobserved unreadable entries
are `unregistered_disposable`. A no-follow `os.scandir` regression pins those
three outcomes.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `SPEC-INTAKE-97538b`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required. This revision preserves the owner-approved
liveness contract: ordinary text-editor changes need no notation; automatic
worker evidence is the easy path; missing audit evidence is debt to repair
forward and is preferable to platform failure; registry identity changes and
irreversible operations retain separate oversight. The canonical membership
authority and obsolete-source-retention directions remain
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` and
`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE`
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`
- `DELIB-202667356`
- `DELIB-20265258`
- `DELIB-202666060`
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md`

## Two-Record Registry Transaction Evidence

The repair plan contained exactly the two fresh-state candidates named above.
It used the canonical public registry service and the v007/v008-authorized
packet. The packaged registry mirror was updated in the same transaction.

- starting generation: `sha256:0cc3fa92a869206b2b7aee6aaf98c368df671faa820eb86a6f566a3e81d10849`
- candidate manifest: `sha256:54a4f377ecdb6410cc02fcb388ce8b5b057a1af5db800dbccbfb2dbd1e4dd8e9`
- package-observer input: `sha256:925493380c818aaf7a28ee66339ff3a8a5f010b3951466cfc5467f47c6b75028`
- dry-run receipt: `sha256:06100a48d76e88705794def057a052ba11fbd2c3968e54a630deebd3656db0b2`
- desired declaration digest: `sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`
- desired projection digest: `sha256:ab996b43eb9e49618da127571155e3b7cae8c8ce87759f3a060173bc5932b787`
- desired record count: 2,348
- committed journal: `SOTTXN-0061C6F125264102B98EC6AA096FBD21`
- transaction receipt: `sha256:8749ef7ab3eeba0d9ee5b67c1a23af4617dc843e71b58e22d239b84cb8d864c6`
- final generation: `sha256:1648ec387957a95bc236f0e1e2f22c3cd10e16e032ffe7a2360d808d7e1e9ed1`

The canonical and packaged declarations are byte-identical at
`sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`.
Projection identity is current, with no missing records and no object-kind
mismatches. The transaction added two exact records and removed or changed no
existing record.

## Deep Census And Audit Evidence

The final no-pruning deep census inspected the complete root and returned:

- registry records: 2,348
- `membership_complete: true`
- `invalid_unknown: 0`
- `unregistered_load_bearing: 0`
- `unregistered_disposable: 2,253,800`
- `registered: 16,875`
- `pruned_envelope_count: 0`
- traversal: 1,607,971 inspected, 662,638 structural ancestors, 63 no-follow
  boundaries, 2 owned-service boundaries, and 1 hosted-application boundary
- `operational_liveness: true`
- `release_eligible: true`
- no candidates and no unknown-root attribution

That scan deliberately classifies all unregistered and unobserved content as
disposable, including unreadable disposable content. It does not follow links,
owned service stores, or the hosted application boundary.

A content audit after the code/registry repair identified 27 otherwise
unrecorded current revisions, including the three changed registered Python
files and older owner-swept/dashboard bytes. The canonical public
`append_passive_observation` service appended those revisions as
`unattributed_external` / `registry-observer/unattributed`; no byte was rejected,
reverted, quarantined, or delayed. A fresh audit then returned
`audit_complete: true` with `audit_gaps: []`.

The normal hot-path validator now returns `valid: true`, coherent declarations,
2,348 records, zero reverse-coverage gaps, zero load-bearing candidates, zero
unknowns, and `membership_complete: true`. Its non-audit run correctly reports
`audit_not_performed`; its 394 explicit pruned envelopes keep hot-path release
and sweep eligibility false. That is not a contradiction with the no-pruning
deep run: the deep run established complete release eligibility, while the hot
run refuses to infer eligibility beneath pruned subtrees.

## Observation Transport Disclosure

Codex desktop `apply_patch` did not automatically append registry observations
for this session, although the configured Codex PostToolUse registration and
the observation hook both exist and their seven focused tests pass. No audit-gap
row named this session. The 27-row passive recovery therefore used the public
service after the fact. This is a nonblocking operational parity defect under
the owner-approved liveness contract, not grounds to reject the repaired bytes.
The exact observation-transport finding is durably captured here for follow-on
disposition; broader Codex apply-patch parity is already represented by WI-5428
and WI-5275, but neither search result names this exact missing event.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Canonical validate plus final deep census; 2,348 records, zero gaps/unknown/candidates | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | 12 reconciliation tests and 29 registry-control tests | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Canonical/package digest equality and projection digest readback | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Exact two-record generation/manifest/observer/receipt-bound journal | PASS |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Existing approved liveness semantics preserved; no content rejection | PASS |
| `SPEC-INTAKE-97538b` | Untracked package visibility and unreadable-authority regressions | PASS |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Shared reconciliation result consumed by canonical validator | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Explicit deep census, explicit audit, and fresh normal-path validate distinguished | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | No-pruning deep classification plus `git diff --check` | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Seven observation-hook tests; missing desktop event disclosed, passive recovery succeeds | PASS with nonblocking follow-on |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Exact artifacts and additive journal preserved; no identity removal | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Live claim and packet bind all five tracked paths plus service ledger | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Final-byte applicability preflight below | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping and all bounded results below | PASS with named WI-5178 baseline |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | v007 proposal, independent v008 GO, v014 NO-GO, live Prime claim, helper-mediated v015 filing | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Deep traversal records one hosted-application boundary without descent | PASS |

## Commands Run

- Canonical two-record `gt registry register --batch-file` dry-run and exact
  receipt-bound apply.
- Canonical no-pruning deep reconciliation across more than 2.25 million
  disposable objects.
- Explicit audited reconciliation, passive observation recovery, and audit
  rerun.
- `gt registry validate --json`: valid, coherent, 2,348 records, zero reverse
  coverage gaps, zero unknowns, zero load-bearing candidates.
- `python -m pytest groundtruth-kb/tests/test_artifact_membership_reconciliation.py -q --tb=short`: 12 passed.
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short`: 29 passed.
- `python -m pytest platform_tests/scripts/test_registry_observation_hook.py -q --tb=short`: 7 passed.
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`: 206 passed, 4 named WI-5178 failures.
- `ruff check` over the three changed Python paths: PASS.
- `ruff format --check` over the same paths: 3 files already formatted.
- `git diff --check`: no whitespace errors; Windows LF-to-CRLF advisories only.
- Final-byte applicability and mandatory clause preflights: recorded below.

## File Digests

- canonical registry TOML: `sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`
- packaged registry TOML: `sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`
- reconciliation source: `sha256:412417166b4b5a0756c7bd9e93c270990fd2f08d6c77822fede823b6cbd2aab6`
- reconciliation test: `sha256:0e4772a9a263f1846d45b55498bb4a32c9301b5ac13a4ac2b5901cccba9fd471`
- implementation-start test: `sha256:2d2d8dec605db7df0de6b22f246dd2e990e894e14272e27a39e54fa4057dcd40`

## Files Changed

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py`
- `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## By-Reference Finalization Waiver

target_paths: ["groundtruth.db"]

The service-owned database carries the additive registry transaction and
passive observation revisions. It MUST NOT be force-added, staged, placed in
`## Files Changed`, or included in the finalizer commit. Its registry,
projection, journal, and audit evidence remains independently reviewable by
reference. This is a finalization-mechanics waiver, not an evidence waiver.

## Acceptance Criteria Status

- [x] The v014 `.codex/hooks.json` classification failure is corrected.
- [x] The complete affected suite was run and only four named WI-5178 residuals remain.
- [x] Fresh reconciliation detects untracked nonignored package/test members before commit.
- [x] Ignored runtime/cache content remains outside package-observer authority.
- [x] Unreadable entries preserve registry and observer authority instead of becoming unknown by default.
- [x] The two omitted load-bearing artifacts were admitted in one exact additive transaction.
- [x] Canonical declaration, packaged declaration, projection, and MemBase identity are coherent/current.
- [x] The final no-pruning census has zero load-bearing and zero unknown gaps.
- [x] Audit gaps remained nonblocking and were repaired forward through the public passive-observation service.
- [x] No registered artifact was deleted, moved, renamed, retired, narrowed, or replaced.
- [x] No disposable artifact cleanup was performed.
- [x] No WI-5640 Stage B mutation was performed.

## Pre-Filing Preflight

The applicability preflight ran against this pending-content file in mandatory
mode and returned exit 0 with `preflight_passed: true`, no blocking errors, no
missing required or advisory specifications, no missing parent directories, no
author-metadata warnings, and no unclassified target paths.

The ADR/DCL clause preflight also ran against this pending-content file in
mandatory mode and returned exit 0:

- clauses evaluated: 5
- must apply: 4
- may apply: 1
- not applicable: 0
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0

| Clause | Spec | Applicability | Evidence | Enforcement |
| --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | not required | blocking |

## Risk And Rollback

The package observer now sees a larger and more accurate domain: untracked,
nonignored package/test files are candidates before first commit. The regression
proves ignored files remain excluded. This can surface real omissions earlier;
it does not grant membership or mutate the registry by itself.

Unreadable registered paths still fail closed as unknown, and unreadable
observer-owned paths still surface as load-bearing gaps. Only unreadable paths
that are both unregistered and unobserved are disposable. The deep scan is
costly at this repository's scale, so normal hot-path consumers retain explicit
pruning and cannot claim deep release eligibility from a pruned run.

The registry transaction is additive and journaled. Rollback is not an in-band
record deletion; any requested identity removal or coverage change requires
separate oversight. Source/test changes remain normal Git-restorable bytes. The
Codex observation transport gap is audit debt, not a reason to discard correct
work or block ordinary edit/build/test activity.

## Loyal Opposition Asks

1. Re-run the complete implementation-start suite and confirm the v014 failure is gone with exactly the four named WI-5178 residuals.
2. Independently reproduce the two-record registry transaction and all four postimage digests.
3. Run the package-observer and unreadable-authority regressions, then independently recompute a no-pruning deep census.
4. Confirm audit recovery used the public passive-observation service and did not reject or alter source bytes.
5. Return VERIFIED only if the five-path Git include, database waiver, no-destruction claim, and zero-gap deep census all reproduce.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
