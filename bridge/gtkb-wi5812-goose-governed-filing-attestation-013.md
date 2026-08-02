REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop Prime Builder; exact non-live v013 correction after physical v012 NO-GO; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5812-goose-governed-filing-attestation
Version: 013
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5812-goose-governed-filing-attestation-012.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5812

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/bridge_author_metadata.py", "scripts/gtkb_session_id.py", "scripts/goose_harness.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_goose_governed_filing.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation occurs in this proposal.

# WI-5812 REVISED Implementation Proposal — Role-Authoritative Goose Governed Filing

## Revision Disposition

Physical version 012 identifies two valid sequencing and test-currentness
defects in version 011. This revision corrects both without changing the
original eight-target forward-only implementation scope:

1. The obsolete role-authority regression module is removed in its entirety
   from every WI-5812 command, acceptance criterion, verification mapping, and
   release-gate path. There is no node deselection or partial reuse of that
   module. Governed completion of WI-5723 is a hard prerequisite because it
   owns the source/spec reconciliation and full removal/replacement of the
   prohibited role fallback. WI-5812 maps its adjacent role checks to active
   `DCL-SESSION-ROLE-RESOLUTION-001` v7 assertions `ROLE-DCL-A1` through
   `ROLE-DCL-A10`, including `ROLE-DCL-A9`, through the read-only canonical
   assertion evaluator and the replacement tests delivered after WI-5723.
2. Fresh canonical readback now resolves the old WI-5234 author-metadata
   thread at targetless `NO-GO` v004, not GO v002. Version 004 independently
   accepts v003 as a valid withdrawal of v002's stale implementation authority
   while correctly keeping WI-5234 open. The immediate competing-GO lane is
   therefore removed. Any later WI-5234 proposal that re-enters either shared
   path must sequence behind WI-5812 or carry an independently accepted exact
   non-overlapping hunk ledger; no such future authority is inferred here.

Version 011's role-authoritative design remains intact: role comes from a
complete dispatcher-composed envelope or validated explicit owner/session
evidence; the generic Goose wrapper has no default Prime Builder role; and
activity selection cannot grant, substitute, or upgrade role.

Historical/unreceipted-chain recovery remains exclusively delegated to
WI-5825. This proposal absorbs none of its recovery behavior or five targets.

## Response To Version 012

### F1 — remove the obsolete module, sequence behind WI-5723, and use active assertions

**Accepted and corrected.** The file named by v012 is absent from this
proposal's command blocks and acceptance criteria. WI-5812 will not execute the
whole module, select green nodes from it, deselect its red nodes, import its
fixtures, count its tests, or treat any current result from it as release
evidence.

The sequencing contract is:

1. WI-5723 must complete its own governed lifecycle: current blockers must be
   resolved, its implementation must receive a current independent GO and
   exact start authority, and its post-implementation report must receive
   independent VERIFIED. Until then, WI-5812 is not implementation-ready.
2. WI-5723 completion must remove the worker-facing registry fallback and the
   `session_resolver_fallback` path, reconcile the active role-resolution
   specification and replacement tests, and leave a complete executable
   assertion carrier for active DCL v7.
3. After that completion, WI-5812 must run the read-only canonical evaluator
   over all ten outer assertion IDs in one carrier evaluation. Partial,
   unsupported, skipped, metadata-only, missing, or stale evidence does not
   pass.
4. WI-5812 must then run the whole replacement test modules named by WI-5723's
   verified implementation report. It may not recover any current obsolete
   module by node selection or copy its retired R1-R5 expectations.

WI-5880 is a subordinate test-only carrier placed on pre-publication hold
after the v012 finding. It may reconcile the stale module only after WI-5723,
but it cannot satisfy, bypass, or expand the WI-5723 prerequisite and cannot
add any path to WI-5812's exact eight-target cohort. WI-5812 remains responsible
only for Goose-specific tests plus read-only execution of the already-landed
active assertion/replacement surfaces.

### Active DCL v7 assertion mapping

| Assertion | Active contract | WI-5812 adjacent evidence after WI-5723 completion |
|---|---|---|
| `ROLE-DCL-A1` | delivered dispatch has complete explicit role and run/session provenance | exact Goose dispatcher envelope with matching run id, explicit role, session id, and role-resolution source is reused unchanged |
| `ROLE-DCL-A2` | worker consumes envelope role without dispatcher-configuration or registry reads | Goose wrapper instrumentation proves no registry, eligibility, ranking, target-map, or dispatcher-config behavior read |
| `ROLE-DCL-A3` | mismatch audits without role substitution | mismatched dispatch/envelope evidence rejects and records typed evidence; it never substitutes another role |
| `ROLE-DCL-A4` | role bootstrap precedes activity and activity cannot alter role | prompt construction and child spawn are unreachable until bootstrap succeeds; skill/activity only constrains the resolved role |
| `ROLE-DCL-A5` | missing, malformed, conflicting, or unresolved evidence fails before protected work with recovery | each invalid dispatcher/interactive envelope path rejects before prompt, metadata, claim, bridge, or child mutation |
| `ROLE-DCL-A6` | explicit interactive owner direction resolves and persists | canonical PB/LO init evidence creates or reuses the exact transcript-derived Goose envelope without registry mutation |
| `ROLE-DCL-A7` | subject-only, absent, ambiguous, or unresolved identity fails closed without fallback | direct interactive launch rejects all such inputs and never emits a fallback label |
| `ROLE-DCL-A8` | markers are session-matched caches; peer/shared markers cannot authorize behavior | only the exact `GOOSE_SESSION_ID` envelope may authorize the launch; shared/current projection and peer markers are denied |
| `ROLE-DCL-A9` | transcript role cannot mutate registry; non-dispatcher gates cannot use registry authority | snapshots prove no registry write/read in transcript launch and governed filing consumes exact session evidence only |
| `ROLE-DCL-A10` | applicable harnesses share equivalent semantics and registry reads are classified | active evaluator plus post-WI-5723 replacement tests cover equivalent fail-closed behavior; Codex/Cursor adjacent suites stay green |

Canonical read-only evaluator command after WI-5723 completion:

```text
python scripts/check_artifact_evaluability.py --spec DCL-SESSION-ROLE-RESOLUTION-001 --assertion ROLE-DCL-A1 --assertion ROLE-DCL-A2 --assertion ROLE-DCL-A3 --assertion ROLE-DCL-A4 --assertion ROLE-DCL-A5 --assertion ROLE-DCL-A6 --assertion ROLE-DCL-A7 --assertion ROLE-DCL-A8 --assertion ROLE-DCL-A9 --assertion ROLE-DCL-A10 --evidence-state current --json
```

Required result: the one selected carrier evaluates every listed outer
assertion and reports full-carrier PASS with no deferred, unsupported, skipped,
missing, stale, contradictory, unavailable, or unverifiable entry. This
read-only evaluator does not record an assertion run or mutate MemBase.

### F2 — WI-5234 current state and overlap disposition

**Accepted and refreshed.** The old author-metadata thread now contains:

- v001 `NEW`, SHA-256
  `C7B4C71CB883BA9696DD8FEBD7F7BF76C62A4A31431A53D3D6A7E6ECA71CC59B`;
- v002 `GO`, SHA-256
  `9715776F5FAD338AFB6C183BE8BA65004AADDB478911A681AFB14F15FAC75970`;
- v003 targetless `NO-ACTION`, SHA-256
  `D80B4B3E752A5091D40CC9608E321E419D878242BC8DCD6D947AD91FF7E191F3`;
- v004 targetless `NO-GO`, SHA-256
  `D0D75D09E9CA976D4D8B042F572C7EC3DF30C1A6941DFAD5BA6E4981E39FC24C`.

Canonical compact readback resolves v004 as current `NO-GO`. It independently
accepts v003 as a valid withdrawal of v002's stale implementation authority,
declares `target_paths: []`, and keeps WI-5234 open without authorizing source
or test mutation. The immediate two-GO collision is therefore cleared through
the exact independent disposition requested by v003.

Immediately before WI-5812 GO and implementation, the WI-5234 current head,
claim, and exact target set must still be reread. If WI-5234 returns to GO over either
`scripts/bridge_author_metadata.py` or
`platform_tests/scripts/test_bridge_author_metadata.py`, WI-5812 fails closed
unless both threads carry an independently accepted, exact non-overlapping
hunk ledger and explicit ordering. Current v004 supplies no competing target
authority and requires any future shared scope to reconcile that ownership.

## Current Chain, Project Authority, Claims, And Target State

- Physical WI-5812 latest is v012 `NO-GO`, SHA-256
  `99E7C88692A38C9197774FE21FF5B5495DC8ED89096C18F15A1C996D58C1D129`.
- Physical v011 remains `REVISED`, SHA-256
  `5B21CA384B3D07B4295864BE1388E4031508F54EC88EA7B2D064786D02F3E80B`.
- Versions 001 through 012 remain append-only and unchanged. This v013 file is
  a non-live draft until the governed writer publishes it after a fresh
  currentness check.
- `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS` is active; WI-5812 is an active
  direct member. The list-free whole-project PAUTH in the header is active and
  unexpired. Legacy per-WI approval metadata is noncontrolling at operation
  time. The PAUTH does not replace GO, claim, schema-v3 start, target isolation,
  report, or independent VERIFIED.
- Draft construction held exact claim row `36060` for Prime Builder session
  `019fb19b-7814-73c1-8707-204e432cbf00`. That claim is released before draft
  handoff and is not filing or implementation authority. Governed filing must
  acquire/revalidate its own exact current claim.
- WI-5723 latest is physical v008 `NO-GO`, SHA-256
  `BFFD9DC4DDAEBCEBCE7E2BA9AAF23DB4794BE8DAE1E032C5EF172E293C593C04`,
  with no claim. Its open WI-5653 dependency, three strict GO overlaps, and
  foreign-dirty `session/envelope.py` target keep it on hold. This proposal
  cites completion as a prerequisite and does not claim any blocker is solved.
- WI-5234's old author-metadata thread is current targetless `NO-GO` v004,
  SHA-256
  `D0D75D09E9CA976D4D8B042F572C7EC3DF30C1A6941DFAD5BA6E4981E39FC24C`,
  with no claim. It independently accepts withdrawal of v002's stale GO lane;
  only a later shared-target proposal would recreate an ordering condition.
- `git status --short -- <the eight targets>` returned no output; the seven
  existing targets are clean and the planned eighth test remains absent.

| Target | Current SHA-256 / state |
|---|---|
| `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` | `F843237ED5DB443418389A1B3B1276B2D0BF1342F4F9B03D5D0910B7912381DD` |
| `scripts/bridge_author_metadata.py` | `0AC4168859E2E4FF855E860A3C5F6B6A21CB57DC4B7336D624728EE2F741A90D` |
| `scripts/gtkb_session_id.py` | `CC1EAC2A7138232ADB4B135A9BB81833EB06AC8E146F29F8918FD571A9951D62` |
| `scripts/goose_harness.py` | `FB38E3F4A52B20DCE8929B8D1E76C3264843E8118B74E5D19B1CA9B79C140DBA` |
| `platform_tests/scripts/test_session_envelope_cli_provenance.py` | `B2C2A41BBC55323C0F362267DFE935C572B02AF8DA54DB01229A3A2472A1E230` |
| `platform_tests/scripts/test_bridge_author_metadata.py` | `39DD96E0987346A68869C0E872331AB7ECEA9AA647B0FD247E15130BFDF82097` |
| `platform_tests/scripts/test_gtkb_session_id.py` | `8AEAF094836923D5ADA1738F8AF81C4B332830789866BCF01495F8717E4C9B77` |
| `platform_tests/scripts/test_goose_governed_filing.py` | absent; planned new module |

Any chain, prerequisite, claim, hash, worktree, or overlap drift before filing,
GO, or implementation fails closed.

## WI-5825 Separation And Ordering

WI-5812 remains forward-only. It establishes authoritative Goose session role,
attestation, author metadata, session-id propagation, and governed filing for
future publications on the exact eight paths above.

WI-5825 exclusively owns historical or interrupted publication recovery:
capability-row repair, lawful receipt back-fill, republish, compensation,
pending-sidecar handling, and durable pending-context recovery on its disjoint
five-target cohort. WI-5825 cannot implement until WI-5812 lands and it has its
own current GO, claim, and start packet. No WI-5825 behavior or path is copied
into this proposal.

## Proposed Design

### Slice A — exact Goose envelope reuse and attestation

In `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:

- recognize `GOOSE_SESSION_ID` as the exact Goose session binding;
- record `goose-envelope-open-corroboration` as the Goose metadata source;
- load and validate the exact open Goose/G envelope and its externally
  established role provenance before reuse;
- require supplied and ambient ids to equal the exact document id and its
  canonical derivation from that document's own harness id and `opened_at`;
- never create, substitute, or upgrade role from ambient variables, activity,
  a shared projection, harness identity, or registry fallback; and
- preserve every existing model, source, role, harness, and state rejection.

### Slice B — fail-closed author-metadata resolution

In `scripts/bridge_author_metadata.py`:

- register the exact Goose envelope metadata-source token;
- accept only the exact attested Goose per-session document;
- add `GOOSE_SESSION_ID` to session-context environment resolution; and
- preserve six-field completeness, placeholder rejection, atomic provenance
  source equality, explicit/environment/exact-envelope precedence, and the
  prohibition on shared-current-projection authority.

### Slice C — deterministic session-id registry

In `scripts/gtkb_session_id.py`:

- add `GOOSE_SESSION_ID` to the frozen recognized set;
- place it at the documented fixed position in bridge-work-intent and
  marker-continuity orders without reordering existing entries; and
- update the complete permutation/drift-lock tests.

### Slice D — externally authoritative wrapper bootstrap and child injection

In `scripts/goose_harness.py`:

1. Role bootstrap occurs before activity selection or prompt construction.
2. A headless launch consumes only a complete exact dispatcher-composed
   Goose/G envelope with matching run/session provenance. The wrapper does not
   read dispatcher configuration or the durable registry and does not rewrite
   the envelope.
3. A direct interactive launch consumes an exact transcript-derived Goose
   envelope or requires an explicit canonical role-bearing init keyword. A new
   envelope is opened once without a caller-created id. Subject-only, absent,
   malformed, ambiguous, or conflicting evidence rejects.
4. `bridge-review` and `verification` require Loyal Opposition;
   `implementation` requires Prime Builder. Activity constrains an already
   resolved role and cannot grant or change it.
5. Only after all authority/activity checks pass, the wrapper injects the
   selected exact id as `GOOSE_SESSION_ID` into an isolated copied child
   environment and launches the child.
6. Any envelope, provenance, role, run, session, activity, or derivation error
   fails before prompt, metadata, claim, bridge, or child mutation.

## Scope Boundaries

Excluded from WI-5812:

- the obsolete role-authority test module and every partial/node-selected use
  of it;
- WI-5723 source/spec/fallback removal and its protected/formal artifacts;
- WI-5880 test-only correction implementation;
- every WI-5825 recovery behavior and target;
- WI-5815 global uniqueness/collision and claim-CLI hardening;
- dispatcher/TAFE activation, configuration, routing, lease, selection, or
  mutation;
- durable registry role reads or writes by the wrapper;
- schema, MemBase, formal-artifact, credential, external-system, deployment,
  release, push, history rewrite, or destructive cleanup; and
- any new hard-coded timeout, TTL, interval, retry, throttle, concurrency,
  scheduler, or daemon literal.

## Cross-Harness Disposition

- **Goose:** receives exact dispatcher/owner envelope consumption,
  role/activity mismatch rejection, canonical interactive opening, exact child
  binding, attestation, author-metadata, and governed-filing coverage.
- **Codex and Cursor:** existing host-session bindings and attestation sources
  remain behaviorally unchanged and their active adjacent suites remain green.
- **Claude, Antigravity, Ollama, and OpenRouter:** no harness-specific hook,
  launcher, role, adapter, or configuration target changes.
- Active DCL assertions A1-A10 provide the shared behavioral floor after the
  WI-5723 prerequisite; no harness exclusion or parity waiver is requested.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` — active v7 dispatcher/worker split,
  explicit bootstrap, fail-closed unresolved identity, A1-A10 inventory, and
  no registry behavior fallback.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — active transcript/session
  continuity and no registry mutation.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` — active architecture for
  owner direction and dispatcher/interactive authority separation.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — Goose governed-filing capability
  floor.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governed writer and append-only numbered
  bridge chain authority.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — exact-session author identity and
  model/role provenance.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` — exact per-session document
  durability and reuse semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active direct-parent PAUTH
  remains operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current project
  authorization controls rather than legacy per-WI approval metadata.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH/project/WI and
  exact target linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete active
  governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — complete executed
  requirement-to-test evidence before VERIFIED.
- `GOV-ARTIFACT-APPROVAL-001` — no formal-artifact mutation is proposed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets and generated bridge
  artifacts remain in-root.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — advisory exact-envelope and
  canonical harness-state authority.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory
  deterministic fail-closed gates.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory repeatable wrapper and
  assertion work belongs in deterministic code/evaluators.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory fresh chain, project, claim,
  dependency, target, and overlap reads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory spec/test/evidence
  linkage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory NO-GO to REVISED lifecycle.
- `GOV-STANDING-BACKLOG-001` — advisory nonduplicated WI-5723, WI-5812,
  WI-5825, WI-5880, and WI-5234 carriers.

The retired predecessor role record is historical evidence only and is not
cited as active authority.

## Prior Deliberations

- `DELIB-202667730` — Harness Test synthesis identifying the governed Goose
  filing defect.
- `DELIB-202667731` — owner-approved list-free Harness Test Corrections project
  authorization.
- `DELIB-202667722` — timer/concurrency direction; no new hard-coded value is
  introduced.
- `DELIB-202667530` — explicit session-envelope direction is canonical and
  conflicting worker-role sources are superseded.
- `DELIB-202667524` — unresolved identity fails closed without durable-registry
  fallback.
- `bridge/gtkb-wi5812-goose-governed-filing-attestation-012.md` — independent
  obsolete-test and target-overlap findings answered here.
- `bridge/gtkb-wi5723-session-resolver-fallback-removal-008.md` — current
  non-terminal prerequisite blockers; none is claimed solved.
- `bridge/gtkb-wi5234-codex-session-model-author-metadata-004.md` — targetless
  independent NO-GO accepting withdrawal of the old GO lane while leaving the
  work item open.

## Owner Decisions / Input

- `DELIB-202667731` supplies the list-free whole-project PAUTH inherited by
  active member WI-5812. No per-WI approval field creates a second gate.
- The owner has directed that dispatcher/TAFE remain disabled for repairs;
  this proposal does not activate, use for dispatch, configure, or mutate it.
- No new owner decision is requested. WI-5723 remains a governed sequencing
  dependency; WI-5234 v004 has removed its old competing GO lane, and any
  future shared-target proposal must re-establish explicit ownership.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5812 / TEST-11768, active DCL v7,
the linked persistence, envelope, author-provenance, bridge, and project
constraints, plus physical v012's findings fully determine this forward
correction. WI-5723 owns prerequisite fallback/source/spec reconciliation;
WI-5880 is subordinate test-only follow-through; WI-5825 owns recovery. No new
or revised formal requirement is needed before independent review.

## Specification-Derived Verification Plan

| Requirement | Required deterministic evidence |
|---|---|
| Active role contract A1-A10 | after WI-5723 VERIFIED, one read-only canonical evaluator run selects all ten outer IDs and returns complete PASS, including A9 |
| WI-5723 replacement evidence | run the complete replacement module set named by WI-5723's verified report; no obsolete-module invocation or node deselection |
| Dispatcher composition | exact Goose/G dispatcher envelope with matching run/session/source is reused without registry/config reads or rewrite |
| Invalid dispatch | missing, malformed, wrong-harness, wrong-session, wrong-source, missing-run, and mismatched-run evidence rejects before activity |
| Interactive authority | canonical PB and LO init evidence succeeds; subject-only, absent, malformed, ambiguous, and conflicting evidence rejects |
| Role before activity | instrumentation proves bootstrap precedes prompt/spawn and activity cannot grant or change role |
| Activity mismatch | review/verification require LO and implementation requires PB; opposite pairings reject before child launch |
| Exact envelope/attestation | exact derived id succeeds; missing provenance, wrong role/harness, closed, borrowed, source-mismatch, and ambient-mismatch paths reject |
| Six-field author metadata | valid exact attested envelope resolves a coherent bundle; partial, hybrid, placeholder, or source-mismatch inputs reject |
| Session-id drift lock | frozen set and both precedence tuples include Goose at the declared position without other reordering |
| Governed filing | fixture path accepts valid role-correct `NEW` and rejects invalid status, role, or metadata before publication |
| WI boundaries | diff inspection proves no WI-5723, WI-5880, WI-5815, WI-5825, dispatcher, or registry implementation entered the eight paths |
| WI-5234 sequencing | current v004 has accepted withdrawal of v002; immediately before GO/start the head remains non-GO with no conflicting claim, or an independently accepted exact non-overlap ledger exists |
| Timer direction | no new hard-coded timeout, TTL, interval, retry, throttle, or concurrency literal |
| Quality | focused pytest, post-WI-5723 replacement suites, Ruff check, Ruff format check, compile, and scoped diff checks pass |

Planned WI-5812 focused command after its target implementation:

```text
python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_goose_governed_filing.py -q --tb=short
```

The current planned new module is absent, so this command is not claimed as a
pre-implementation pass. The implementation report must record exact commands,
collection counts, and observed results.

After WI-5723 governed completion, the implementation report must additionally
run its complete named replacement role suites and the exact A1-A10 evaluator
command above. It must never add the obsolete module back into a command.

Quality commands after implementation:

```text
python -m ruff check <the eight approved Python paths>
python -m ruff format --check <the eight approved Python paths>
python -m py_compile <the four approved Python source paths>
git diff --check -- <the eight approved paths>
```

## Acceptance Criteria

1. WI-5723 has completed its governed implementation and independent VERIFIED
   cycle; its replacement role evidence is current and executable.
2. The obsolete role-authority regression module appears in no WI-5812 command,
   acceptance, import, fixture, collection count, or release-gate path. No node
   deselection is used.
3. The canonical read-only evaluator executes `ROLE-DCL-A1` through
   `ROLE-DCL-A10`, including A9, as one complete active-DCL carrier and returns
   full PASS with current evidence.
4. WI-5234 v004 remains the current independent non-GO disposition accepting
   withdrawal of v002, with no competing current GO or claim on the two shared
   targets; otherwise both threads carry an independently accepted exact
   non-overlapping hunk ledger. No inferred ledger is accepted.
5. The wrapper has no default PB/LO role and never derives role from activity,
   harness identity, shared marker, or durable registry fallback.
6. Headless launch consumes a complete exact dispatcher-composed envelope with
   matching run/session provenance and does not rewrite it.
7. Interactive launch consumes an exact transcript-derived envelope or
   requires explicit canonical role-bearing owner input and one canonical open.
8. Role bootstrap finishes before activity; review/verification require LO and
   implementation requires PB.
9. Every named invalid identity/provenance path fails before metadata, claim,
   bridge, or child mutation.
10. Complete coherent Goose author metadata reaches governed filing; hybrid or
    placeholder provenance cannot pass.
11. No WI-5723, WI-5880, WI-5815, or WI-5825 implementation is absorbed.
12. Only the exact eight paths change; current chain, dependency, hashes,
    claims, worktree state, and overlap are reread before implementation.
13. Focused tests, post-WI-5723 replacement suites, complete A1-A10 evaluation,
    Ruff lint, Ruff format, compile, and scoped diff checks pass with exact
    observed evidence.
14. No new hard-coded timer or dispatcher/TAFE, database, credential, external
    system, deployment, release, push, history, or destructive mutation occurs.

## Risks And Rollback

- **Prerequisite drift:** WI-5723 or WI-5234 can change while this proposal is
  reviewed. Every later gate rereads physical heads, hashes, claims, and exact
  paths; drift returns the thread to revision.
- **Obsolete-test laundering:** selecting only green nodes would conceal
  retired behavior. The entire module is excluded and complete active A1-A10
  evidence is mandatory.
- **Authority confusion:** activity is a constraint only. Role bootstrap lives
  in a separate path and finishes before prompt construction.
- **Dispatcher mutation:** a worker never repairs an invalid dispatcher
  envelope. It returns typed failure without routing/configuration reads.
- **Interactive spoofing:** ambient id alone is insufficient; the exact
  transcript-derived document must validate.
- **Overlap recurrence:** any current GO on either WI-5234 shared path blocks
  WI-5812 unless an independently accepted exact hunk ledger exists.
- **Recovery duplication:** WI-5825 remains the sole recovery carrier.
- **Rollback:** through a governed successor, revert only the approved four
  source and four test paths. Do not rewrite envelopes, bridge history,
  capability rows, receipts, specs, or unrelated files.

## Candidate Pre-Filing Gates

Immediately after this draft's content is stable, run candidate applicability,
mandatory clause, and Codex writer-compliance audits against this exact
non-live path. A live filing additionally requires fresh currentness, exact
claim, governed writer publication, and canonical path/status/hash readback.
Candidate checks are not GO, claim, publication, start, implementation, or
verification authority.

## DISARM — Implementation And Publication Boundary

This non-live draft authorizes no protected edit. It does not publish a bridge
version, create an implementation-start packet, mutate MemBase, activate or
use dispatcher/TAFE for dispatch, or touch an implementation target. Live
implementation requires satisfied prerequisites, governed filing, independent
GO, fresh exact `go_implementation` claim, schema-v3 start packet, exact
target/overlap recheck, factual report, and independent atomic VERIFIED.

## Recommended Commit Type

Recommended later implementation type: `feat:` — add role-authoritative Goose
envelope attestation and governed filing with fail-closed PB/LO coverage.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
