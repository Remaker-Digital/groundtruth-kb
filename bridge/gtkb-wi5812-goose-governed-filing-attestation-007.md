REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop Prime Builder; manual physical-bridge processing; substantive revision drafted without claim or live publication
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5812-goose-governed-filing-attestation
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5812-goose-governed-filing-attestation-006.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5812

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/bridge_author_metadata.py", "scripts/gtkb_session_id.py", "scripts/goose_harness.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_goose_governed_filing.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5812 REVISED Implementation Proposal — Goose Attestation and Governed Filing

## Revision Disposition

This substantive revision restores the complete implementation proposal after
the invalid version-005 `NO-ACTION` disposition and answers the version-006
`NO-GO`. It preserves the version-003 forward-filing objective, exact
eight-path cohort, four design slices, specification-derived test plan, and
fail-closed posture. It refreshes project authority, backlog coordination,
target baselines, claim isolation, and predecessor sequencing before requesting
a new independent review.

### Response to F1 — project authorization

Version 006 correctly observed the factual legacy WI field
`approval_state: unapproved`, but its conclusion that WI-5812 needs a new
per-work-item owner approval is obsolete under the owner's project-only
authorization lifecycle doctrine. Implementation approval is granted to a
project; all work items must belong to a project; active member work items
inherit the parent project's active authorization. The legacy per-WI field is
noncontrolling and does not create a second implementation-approval gate.

Fresh canonical project reads show:

- active membership
  `PWM-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WI-5812` v1, role `member`, in
  `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS`;
- parent project status `active`, version 1;
- active, unexpired, list-free authorization
  `PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730` v1,
  with `included_work_item_ids: null`, `excluded_work_item_ids: null`, and
  owner-decision evidence `DELIB-202667731`;
- allowed classes include source, test, test addition, configuration,
  documentation, metadata, governance evidence, and bridge; forbidden
  operations include dispatcher mutation, external-system mutation,
  credential lifecycle, push, history rewrite, deployment, release, and
  destructive cleanup.

No new owner approval is required. The inherited PAUTH still does not waive
this exact proposal, independent Loyal Opposition `GO`, a fresh exact-thread
claim, a fresh implementation-start packet, exact-target enforcement, a factual
implementation report, independent `VERIFIED`, or governed atomic
finalization.

### Response to F1 — receipt recovery and WI-5825 coordination

Version 006 also correctly detected that the current WI-5812 `status_detail`
mentions receipt back-fill/recovery for historical unreceipted chains. That
capability is not omitted from the corrections program; it is now carried by
the later, dedicated active project member WI-5825, **Governed recovery for
poisoned and compensated publication-capability rows and unreceipted chains**.
Its complete version-001 proposal received independent `GO` in version 002.
Versions 003/004 only correct an invalid `NO-ACTION` closure; version 004 says
to keep that approved recovery design pending. The dedicated design owns:

- governed clearing/republish of `recovery_required` and `compensated`
  publication-capability rows;
- lawful, attested receipt back-fill for already-published unreceipted chains;
- durable capability-row fallback when in-memory and sidecar pending context
  is unavailable.

Those changes use five exact paths:

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`;
- `scripts/gtkb_bridge_writer.py`;
- `groundtruth-kb/tests/test_registry_control_plane.py`;
- `platform_tests/scripts/test_gtkb_bridge_writer.py`;
- `platform_tests/scripts/test_check_protected_commit_authorization.py`.

They are disjoint from this revision's eight paths. Duplicating recovery code
inside WI-5812 would split authority, duplicate an already-reviewed backlog
carrier, and create two proposals for one capability. The lawful coordination
split is therefore:

1. **WI-5812 is the forward fix.** It gives each future Goose session an
   attestable identity and makes future publications use the governed writer,
   preventing new direct-write/unreceipted chains.
2. **WI-5825 is the backward and incident-recovery fix.** It repairs the
   poisoned rows and historical unreceipted chains that already exist and
   handles future interrupted-publication recovery.
3. **Sequence WI-5812 first, then WI-5825.** WI-5825 version 001 explicitly
   requires its implementation to begin only after WI-5812 lands. No source
   overlap exists; the dependency is semantic and temporal.

This revision therefore addresses the receipt-recovery requirement through
explicit carrier ownership and ordering rather than silently absorbing
WI-5825's distinct five-path implementation.

## Summary

Extend bridge author-metadata attestation and governed filing to the Goose
harness (durable harness id `G`). A Goose Prime Builder session must complete
the full path — exact per-session envelope, author-metadata attestation,
work-intent identity, and governed proposal filing — without falling back to
direct writes into `bridge/`.

The honest attestation source for Goose is envelope-open corroboration. Goose
does not expose a host-injected per-turn metadata header equivalent to Codex or
Cursor. The exact open per-session envelope under
`harness-state/goose/session-envelopes/` supplies the evidence: its session id
must equal the deterministic `{harness_id}-{opened_at}` derivation, and an
ambient `GOOSE_SESSION_ID`, when present, must match exactly.

This draft changes no live bridge file, claim, source, test, configuration,
MemBase record, dispatcher state, or TAFE state.

## Fresh Problem and Baseline Evidence

1. The four implementation source files still contain no
   `GOOSE_SESSION_ID` or `goose-envelope-open-corroboration` token. The
   proposed Goose path is not already implemented.
2. `cli_session_handoff.py` supports host-model metadata only for Codex and
   Cursor, so Goose attestation still reaches the unsupported-harness
   rejection recorded by WI-5812.
3. `bridge_author_metadata.py` has no exact-session metadata-source mapping or
   ambient session-context variable for Goose. `gtkb_session_id.py` likewise
   has no Goose-native variable in its frozen set or precedence policies.
4. `scripts/goose_harness.py` does not mint and inject one
   `GOOSE_SESSION_ID` per child process. The governed filing actor therefore
   cannot derive a complete attested Goose identity through the normal path.
5. The physical WI-5812 chain is versions 001–006 with latest status `NO-GO`.
   There is no live version 007. Its historical claim is expired; there is no
   active WI-5812 implementation claim.
6. The old version-003 sequencing dependency
   `gtkb-wi5568-session-envelope-host-binding-repair` is now terminal
   `WITHDRAWN`, so that wait no longer blocks this proposal.

Fresh `git status --short -- <eight exact targets>` returned no output. Exact
drafting-time baselines are:

| Target | State | SHA-256 or disposition |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` | clean | `f843237ed5db443418389a1b3b1276b2d0bf1342f4f9b03d5d0910b7912381dd` |
| `scripts/bridge_author_metadata.py` | clean | `0ac4168859e2e4ff855e860a3c5f6b6a21cb57dc4b7336d624728ee2f741a90d` |
| `scripts/gtkb_session_id.py` | clean | `cc1eac2a7138232adb4b135a9bb81833eb06ac8e146f29f8918fd571a9951d62` |
| `scripts/goose_harness.py` | clean | `fb38e3f4a52b20dce8929b8d1e76c3264843e8118b74e5d19b1ca9b79c140dba` |
| `platform_tests/scripts/test_session_envelope_cli_provenance.py` | clean | `b2c2a41bbc55323c0f362267dfe935c572b02af8da54db01229a3a2472a1e230` |
| `platform_tests/scripts/test_bridge_author_metadata.py` | clean | `39dd96e0987346a68869c0e872331ab7ecea9aa647b0fd247e15130bfdf82097` |
| `platform_tests/scripts/test_gtkb_session_id.py` | clean | `8aeaf094836923d5ada1738f8af81c4b332830789866bcf01495f8717e4c9b77` |
| `platform_tests/scripts/test_goose_governed_filing.py` | absent, planned new test module | create only after GO/start |

The canonical cross-claim target scan completed over the named packet cache and
returned no active foreign-session collision for the eight-path cohort. WI-5825
has no active claim and, independently, no overlapping target.

## Proposed Design

### Slice A — exact Goose attestation

In `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:

- recognize `GOOSE_SESSION_ID` as the Goose host/session binding;
- record `goose-envelope-open-corroboration` as the Goose model-metadata
  attestation source;
- after resolving the exact open Goose envelope and before writing metadata,
  require the supplied session id to equal
  `f"{envelope['harness_id']}-{archive_timestamp(envelope['opened_at'])}"`;
- when ambient `GOOSE_SESSION_ID` exists, require exact equality with the
  supplied id;
- preserve all existing exact-document, open-state, harness-identity,
  worker-role, and metadata-validity rejections.

No free-text, borrowed, closed, or shared-projection identity can attest.

### Slice B — author-metadata resolution

In `scripts/bridge_author_metadata.py`:

- add the Goose corroboration token to the exact-session metadata-source map;
- accept only an exact Goose envelope whose recorded
  `model_metadata_source` equals that token;
- add `GOOSE_SESSION_ID` to the environment names for
  `author_session_context_id`;
- preserve precedence and the rule that the shared current-session projection
  is never author authority.

Unattested envelopes, placeholder `unknown` values, source mismatches, and
incomplete six-field author metadata remain fail-closed.

### Slice C — session-id registry

In `scripts/gtkb_session_id.py`:

- add `GOOSE_SESSION_ID` to the frozen session-id environment-variable set;
- place it deterministically after the Codex-native variables and before the
  generic `GTKB_SESSION_ID` in both the bridge-work-intent and marker-continuity
  precedence policies;
- update full-permutation drift-lock tests in the same change.

The dispatch-run-first and live-Claude-first policies otherwise remain
unchanged.

### Slice D — one identity per Goose wrapper spawn

In `scripts/goose_harness.py`:

- derive one fresh id per spawned Goose process using `G-` plus the
  archive-normalized UTC open time;
- inject `GTKB_HARNESS_NAME=goose` and
  `GOOSE_SESSION_ID=<fresh-session-id>` into that child's environment;
- use the same id throughout envelope open, attestation, claim identity, and
  governed filing for that spawn;
- never reuse an id across wrapper spawns.

The wrapper does not add a speculative host marker. Any broader
reuse/collision rejection or cross-harness ambient-claim hardening remains
WI-5815 scope.

## Scope Boundaries

This revision intentionally excludes:

- poisoned-row clearing, receipt back-fill, republish, and durable pending
  context recovery (WI-5825);
- per-session registry uniqueness enforcement and claim-CLI ambient identity
  hardening (WI-5815);
- bridge status-token reconciliation (WI-5814);
- console-window suppression (WI-5810);
- dispatcher/TAFE configuration or activation;
- any schema, MemBase, credential, external-system, deployment, release, push,
  history-rewrite, or destructive-cleanup operation;
- new timeout, TTL, interval, retry, throttle, daemon, or scheduler behavior.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — required: governed-filing-capable identity and attestation are part of the harness capability floor and are the source requirement for WI-5812 / TEST-11768.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required: governs the filing path repaired for Goose and the append-only numbered audit chain.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — required: the exact envelope and six-field metadata chain mechanically carry bridge-artifact authorship.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required: active project membership inherits the list-free PAUTH while the full bridge/start lifecycle remains mandatory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — required: the PAUTH/project/WI triple above binds the proposal to current project authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required: every governing specification is concretely linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required: independent verification must execute the mapped behaviors below.
- `GOV-ARTIFACT-APPROVAL-001` — required: no formal-artifact mutation is in scope; the existing owner/project evidence is cited, not recreated.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required: every target is inside `E:\GT-KB`; no adopter or out-of-root path is touched.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — advisory: identity and role remain on canonical registry/envelope readers; no new harness-state authority is created.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory: attestation and filing identity remain deterministic write-time gates.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory: repeatable identity derivation belongs in code, not operator convention.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory: scope and authority are based on current project, bridge, claim, and target reads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory: this defect remains traceable through project, WI, proposal, tests, report, and verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory: implementation evidence remains linked to requirements and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory: defect-origin lifecycle proceeds through governed revision and review.
- `GOV-STANDING-BACKLOG-001` — advisory: WI-5812, WI-5815, and WI-5825 remain the authoritative nonduplicated backlog carriers.

## Prior Deliberations

- `DELIB-202667730` — Harness Test final synthesis identifying Goose governed-filing exclusion as program-critical.
- `DELIB-202667731` — owner decision granting the list-free Harness Test Corrections project authorization inherited by WI-5812 and WI-5825.
- `DELIB-202667726` — owner mandate establishing the Harness Test and corrections program.
- `DELIB-202667722` — timer/throttle governance; this design introduces no new hard-coded timer.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — `NO-ACTION` is a correction route, not a terminal substitute for implementation.

## Owner Decisions / Input

1. `DELIB-202667731` records the owner-approved list-free authorization for
   `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS`. WI-5812's active membership causes
   it to inherit that implementation approval under the owner's current
   project-authorization lifecycle doctrine.
2. No new per-WI approval is required. This proposal requests independent
   review and performs no implementation.
3. Receipt recovery remains approved project work under WI-5825; this revision
   records the exact forward/backward split and the already-reviewed order
   instead of duplicating its target cohort.
4. The project authorization does not authorize dispatcher/TAFE mutation,
   external systems, credentials, destructive cleanup, push, history rewrite,
   deployment, or release, and this revision requests none of them.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5812, linked TEST-11768,
`GOV-HARNESS-ONBOARDING-CONTRACT-001`,
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, the bridge authority, and the cited owner
decisions completely constrain the forward attestation/governed-filing fix.
WI-5825 and its reviewed design completely constrain historical receipt and
capability recovery. No new or revised specification and no new owner decision
is required before this revision can receive independent review.

## Specification-Derived Verification Plan

| Requirement | Planned behavioral coverage | Required evidence |
|---|---|---|
| WI-5812 / TEST-11768 / harness onboarding | corroborated exact open Goose envelope attests successfully | exact derived id succeeds and records the Goose source token |
| Fail-closed author provenance | borrowed id, env mismatch, missing/closed envelope, wrong source token, and placeholder model values reject | each rejection occurs before metadata or bridge publication mutation |
| Six-field author metadata | attested Goose envelope plus ambient `GOOSE_SESSION_ID` resolves complete metadata | `load_author_metadata` returns the exact author/session/model/harness fields |
| Session-id drift lock | frozen set and both precedence tuples include Goose at the declared position | full-permutation assertions pass without changing other precedence |
| Governed filing end to end | fixture open → attest → actor resolution → dry-run/file validation | valid `NEW` proposal accepted; unparseable status token rejected |
| Wrapper session isolation | two wrapper spawns receive two different derived ids; each child has Goose harness name and its own id | deterministic env-capture tests pass without launching live external work |
| WI-5815 boundary | no claim-CLI or global uniqueness implementation appears in the diff | exact-target/diff inspection confirms absence |
| WI-5825 boundary | no capability-row, receipt, republish, or pending-context implementation appears in the diff | exact-target/diff inspection confirms absence |
| DELIB-202667722 | no new hard-coded timer/TTL/interval/retry literals | focused source scan and regression assertion pass |
| Code quality | `ruff check` and `ruff format --check` over every changed Python path | both independent gates pass |

Planned focused execution:

`python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_goose_governed_filing.py -q --tb=short`

The implementation report must record exact commands and observed results;
planned tests in this proposal are not execution evidence.

## Acceptance Criteria

1. Exact open-envelope corroboration permits Goose attestation and records
   `model_metadata_source: goose-envelope-open-corroboration`.
2. Unsupported harnesses and every named invalid Goose identity path continue
   to fail closed before mutation.
3. Complete Goose author metadata reaches governed proposal filing without the
   current `Unable to resolve filing session identity` failure.
4. Every wrapper spawn receives a fresh exact id and all in-spawn governed
   surfaces resolve that same id.
5. Session-id precedence remains deterministic and drift-locked.
6. No WI-5815 or WI-5825 implementation is absorbed.
7. No target outside the exact eight-path JSON cohort changes.
8. Focused tests, relevant adjacent tests, `ruff check`, and
   `ruff format --check` pass with exact observed evidence.
9. No MemBase record, bridge history, dispatcher/TAFE state, credential,
   external system, deployment, release, push, or Git history is mutated by
   the implementation outside its later governed cycle.

## Risk and Rollback

- **Over-permissive attestation:** exact envelope state, deterministic id
  derivation, optional ambient equality, source-token equality, and existing
  metadata validation all remain mandatory and receive rejection tests.
- **Session precedence regression:** fixed insertion positions and
  full-permutation tests preserve both existing policies.
- **Entrenching shared or reused identities:** shared projections are not read
  as authority; wrapper spawns mint fresh ids; broader enforcement stays with
  WI-5815.
- **Recovery-scope duplication:** the explicit five-path WI-5825 exclusion and
  implementation order preserve one owner per capability.
- **Late target collision:** immediately before implementation, re-read all
  eight hashes and rerun canonical cross-claim collision detection. Any dirty
  or reserved target fails closed and returns to revision/review.
- **Rollback:** revert only the later four source diffs and four test changes.
  No numbered bridge file or capability history is rewritten or deleted.

## Candidate Pre-Filing Preflights

Both mandatory candidate checks were executed against this exact
non-dispatchable draft with the repository virtual-environment interpreter.

Applicability command:

`groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5812-goose-governed-filing-attestation-007.md --json`

Observed candidate result:

- bridge document: `gtkb-wi5812-goose-governed-filing-attestation`;
- content source: `pending_content` at this exact draft path;
- operative physical predecessor: version 006, status `NO-GO`;
- declared target paths: the exact eight-path JSON cohort in this proposal;
- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `blocking_errors: []`;
- author-metadata warnings, missing parent directories, and unclassified
  target paths: all empty;
- project-authorization phase `proposal`: `allowed`, reason `allowed`, active
  PAUTH v1; both `implementation_packet_create` and `implementation_start`
  evaluate allowed for every declared target class.

Mandatory clause command:

`groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5812-goose-governed-filing-attestation-007.md`

Observed candidate result:

- five clauses evaluated;
- four `must_apply`, one `may_apply`, zero `not_applicable`;
- zero must-apply evidence gaps;
- zero blocking gaps;
- mandatory-mode exit code 0.

These are candidate checks, not a live filing receipt, GO verdict, claim,
implementation-start packet, implementation result, or verification verdict.

## DISARM — Implementation Boundary

This is a draft proposal only. It acquires no claim, creates no
implementation-start packet, modifies no protected source/configuration/test
target, files no live bridge version, and publishes no dispatcher/TAFE state.
Implementation authority can arise only after governed filing, independent
GO, fresh claim, successful start packet, exact-target validation, and fresh
collision clearance.

## DISARM — KB and Capability Mechanics

This proposal performs no MemBase or managed-artifact mutation and requests no
publication-capability recovery operation. References to envelopes, filing,
receipts, and recovery describe the bounded source domain and WI-5825
coordination; they are not live packet, claim, capability, receipt, or database
operations performed by this draft.

## Recommended Commit Type

Recommended later implementation commit type: `feat` — extends an existing
governed attestation and filing capability to Goose with fail-closed regression
coverage.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
