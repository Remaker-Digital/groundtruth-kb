NO-GO
::init gtkb lo
::open test

author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: 019fbf81-24c3-7d92-9e90-b090ad25e826
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Loyal Opposition; transcript-defined ::init gtkb lo; independent delegated review of exact v005; dispatcher and TAFE deliberately not used
author_metadata_source: exact session envelope, task-local transcript, and parent Prime Builder delegation

# Loyal Opposition Review — WI-5806 Operational-Control Configuration Foundation v005

bridge_kind: lo_verdict
Document: gtkb-wi5806-operational-control-config-foundation
Version: 006
Responds to: bridge/gtkb-wi5806-operational-control-config-foundation-005.md
Reviewed proposal SHA-256: `5A65C3CA034B828F4B3E615559BDAE1C57FC8C7D9F0FF276B5A58FF3038208BE`
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5806

## Verdict

**NO-GO.** V005 correctly repairs the withdrawn three-target authority, makes
the two missing SoT-registry admissions explicit, truthfully treats the three
foreign-created postimages as evidence to be adopted only under fresh
authority, and supplies an acceptable short compatibility boundary while
WI-5909 is unavailable. One defect in the exact source bytes still blocks GO:
the resolver's split-snapshot identity covers the TOML bytes but not the
external governed environment-schema binding that materially defines the
parsed catalog. A snapshot from one binding is therefore accepted with a
different binding over identical TOML bytes and can silently discard a present
override in favor of the relaxed default.

This is a bounded correction. Prime Builder should preserve the six-target
registry-admission transaction and revise only the affected source/test bytes,
their exact hashes, and the resulting evidence.

## First-Line Role Eligibility And Independence

- Requested status: `NO-GO`; authorized only to Loyal Opposition by
  `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session: `019fbf81-24c3-7d92-9e90-b090ad25e826`, harness A,
  transcript-resolved `loyal-opposition` under `::init gtkb lo`.
- V005 author session: `019fbf41-5d5e-74f3-b6f4-1ae7258c299c`, Prime Builder.
- Both identifiers are present and distinct. This is not same-session
  self-review. The reviewer did not author or modify the three implementation
  postimages.

## Applicability Preflight

- packet_hash: `sha256:2235ca4950888bbfc935304d6620b3b5eb97db194d301df3285df889a873f33f`
- candidate_evidence_hash: `sha256:47996d0d919fd8755e7072e50d00971d922375b726d62cb1d8c3df8bc414e6dd`
- bridge_document_name: `gtkb-wi5806-operational-control-config-foundation`
- declared_target_paths: ["config/governance/operational-controls.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py", "groundtruth-kb/tests/test_operational_control_config.py", "groundtruth.db"]
- applicability_path_evidence: ["bridge/gtkb-wi5806-operational-control-config-foundation-002.md", "bridge/gtkb-wi5806-operational-control-config-foundation-004.md", "config/governance/operational-controls.toml", "config/governance/operational-controls.toml`", "config/registry/sot-artifacts.toml", "config/registry/sot-artifacts.toml`", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`", "groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py", "groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py`", "groundtruth-kb/tests/test_operational_control_config.py", "groundtruth-kb/tests/test_operational_control_config.py`", "groundtruth-kb/tests/test_operational_control_config.py`.", "groundtruth.db"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5806-operational-control-config-foundation-005.md`
- operative_file: `bridge/gtkb-wi5806-operational-control-config-foundation-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-TIMER-GOVERNANCE`
- authorization_source: `bridge/gtkb-wi5806-operational-control-config-foundation-005.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["config/governance/operational-controls.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py", "groundtruth-kb/tests/test_operational_control_config.py", "groundtruth.db"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5806-operational-control-config-foundation`
- Operative file: `bridge\gtkb-wi5806-operational-control-config-foundation-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and no
`Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited. Clauses with
`enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-202667748` — owner standing directive for one typed, centralized,
  evidence-tuned timer/concurrency source of truth.
- `DELIB-202667725` — active whole-project Timer Governance authority while
  retaining every per-WI bridge, claim, start, report, and verification gate.
- `DELIB-202667517` — highly parallel Prime Builder operation is mandatory;
  shared control planes may serialize only short atomic critical sections.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` —
  path-wide MemBase coordination is transitional debt to be enhanced or
  replaced before Dispatcher Next activation.
- `bridge/gtkb-wi5806-operational-control-config-foundation-001.md` through
  `-005.md` — exact proposal, withdrawn GO, authority correction, corrected
  NO-GO, and current six-target revision.
- `bridge/gtkb-wi5909-governed-row-cohort-reservations-001.md` — current
  review-only NEW design for replacing path-wide `groundtruth.db` claim
  collisions; not presently implementation-available.

## Specifications Carried Forward

- `GOV-ENV-LOCAL-AUTHORITY-001`
- `ADR-ENV-SOT-TOPOLOGY-001`
- `DCL-ENV-CLI-ENFORCEMENT-001`
- `GOV-SOT-SINGLETON-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-10`, `GOV-12`, `SPEC-1662`, and `GOV-15`

## Positive Confirmations

- Receipt row `1002` is a consumed bridge-publication capability for exact
  v005, content digest
  `sha256:5a65c3ca034b828f4b3e615559bdae1c57fc8c7d9f0ff276b5a58ff3038208be`,
  with revision `SOTREV-2A1724CB67F344B2A159C7399222996D` and no failure.
- WI-5806 has active first-class membership in
  `PROJECT-GTKB-TIMER-GOVERNANCE`; PAUTH v2 is active and the fresh six-target
  proposal operation-time evaluation is allowed.
- The three foreign-created postimages still match the exact v005 hashes.
  V005 explicitly discloses their author session and adopts no byte without a
  fresh GO/claim/start cycle; that foreign-byte disposition is sound.
- The current production catalog remains schema-only with zero definitions;
  no production consumer imports the new resolver.
- The exact focused suite passed `29/29`; Ruff check, Ruff format check, and
  compile all passed on the reviewed source/test bytes.
- The five cited registry-control-plane tests collected as nine nodes and
  passed `9/9`, including generation/authority preview binding, fault-phase
  coherence, idempotent retry, both declaration revisions, and CLI denial.
- Fresh registry inspection is coherent: canonical and packaged declarations
  are byte-identical at
  `sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`,
  generation
  `sha256:1648ec387957a95bc236f0e1e2f22c3cd10e16e032ffe7a2360d808d7e1e9ed1`,
  and identity current. Reconcile now reports 26 load-bearing gaps because of
  unrelated concurrent work, but exactly the two v005 record IDs remain the
  candidates for the WI-5806 source and test; `invalid_unknown` remains zero.
- A physical latest-file scan found 17 external declarations intersecting the
  six targets, of which only
  `gtkb-artifact-registry-authoritative-hygiene-sweep` also declares the
  canonical registry TOML; all others intersect only `groundtruth.db`.
  Canonical operation-time cross-claim evaluation returned `None`; the two
  visible legacy GO-claim rows were expired/lapsed, not active authority.
- WI-5909 remains NEW and explicitly review-only/governance-held. It is the
  preferred steady-state repair, not a current formal WI-5806 dependency.

## Whole-Database Compatibility Boundary Disposition

The v005 compatibility route is **accepted for the corrected revision**, but
only as a transitional, operation-time condition. This does not excuse P1 and
does not itself authorize implementation.

Prime Builder may proceed before WI-5909 is VERIFIED only if it completes all
read-only preparation, candidate comparison, exact two-record batch, report
skeleton, tests that do not depend on the applied transaction, and collision
inventory before acquiring the six-target claim. It then acquires the claim
last, revalidates exact proposal/PAUTH/packet/target/candidate/generation/lock
state, performs only the identical dry-run/apply/canonical-readback/final report
publication sequence, and releases immediately. Any active peer claim or
cross-claim collision stops the operation; no takeover or wait-loop is
authorized. If WI-5909 becomes independently VERIFIED first, use its governed
resource-cohort route instead.

This is acceptable because the current transaction is an exact two-row
registry admission through the existing linearizable service, the broad claim
is bounded to one prepared operation rather than source authoring or long test
execution, and operation-time conflict remains fail-closed. It is not approval
of path-wide database claims as the steady-state model.

## Findings

### P1 — Catalog/snapshot identity omits the external environment-schema binding

**Claim.** The exact source does not enforce the proposal's one-catalog/
one-environment-snapshot and stale-binding fail-closed invariant when catalog
TOML bytes are unchanged but the governed environment-schema binding changes.

**Evidence.** `OperationalControlDefinition` derives `environment_name` and
`environment_schema_version` from the caller-supplied binding, and its
`definition_digest` includes them. `OperationalControlCatalog.catalog_sha256`,
however, is only `_sha256(payload)` over the TOML bytes. `_snapshot()` binds
only that catalog SHA, source fields, and retained values. Finally,
`resolve_operational_controls()` rejects a split only when
`environment_snapshot.catalog_sha256 != catalog.catalog_sha256`; it does not
bind or compare the definition/binding set.

A no-write probe loaded the same TOML bytes twice with the same schema reference
but verified test bindings `(GTKB_CONTROL_OLD_TIMEOUT, version 1)` and
`(GTKB_CONTROL_NEW_TIMEOUT, version 2)`. The two definition digests differed,
but `same_catalog_sha` was `true`. A snapshot from the old binding containing
the present value `90` was accepted with the new catalog and resolved to value
`30`, source `catalog_relaxed_default`, instead of failing split/stale. The
submitted 29-node suite passed because its split test changes only the raw
catalog SHA and never changes binding identity over identical catalog bytes.

**Deficiency rationale.** The external environment-schema binding is part of
the parsed catalog's effective authority: it determines which `.env.local` key
is retained and the schema version reported in provenance. Treating two
different binding sets as one catalog identity allows a legitimate old
snapshot to be combined with a new binding and converts a present override
into an absent key/default. That is precisely the silent fallback and stale
binding class the proposal says must fail closed.

**Impact.** A later separately governed consumer migration could reuse or pass
the wrong snapshot after an environment-schema binding version/name change and
receive a plausible relaxed default with valid-looking raw catalog and snapshot
digests. Coupled-control validation would then operate on the wrong authority
without a typed failure.

**Required solution.** Define one canonical effective-catalog identity that
binds the exact TOML hash plus the complete normalized validated binding set
(at minimum schema reference, environment name, schema version, and every
attestation field relevant to acceptance). Store that identity on the catalog
and snapshot, include it in snapshot/result provenance, and require exact
identity equality before resolution. Keep the raw TOML SHA separately for file
provenance. Add focused regressions proving that environment name, schema
version, and any accepted attestation-identity change over identical TOML bytes
fail with a typed split/stale-binding error and never fall back to a default.

**Prime Builder context.** The narrow repair belongs in
`operational_control_config.py` plus `test_operational_control_config.py`; the
catalog TOML can remain unchanged. V005 already permits an explicit bounded
source/test correction. Preserve the existing public provenance fields where
compatible, add the effective identity rather than overloading the raw file
hash, and update the exact v007 preimages and executed test count.

## Required Revisions

1. Correct P1 by binding snapshots and resolution to the complete normalized
   effective catalog/environment-schema binding identity, while retaining the
   raw TOML SHA as distinct file provenance.
2. Add and execute the identical-TOML/different-binding negative matrix for at
   least environment name and schema version, plus any other attestation field
   whose change can alter binding validity. Assert typed failure and no relaxed-
   default fallback.
3. Re-run the complete focused source suite, the five named registry test
   functions, Ruff, format, compile, both mandatory preflights, exact reconcile,
   project/PAUTH/currentness, collision, claim, and lock checks. Report actual
   collection counts rather than preserving `29` as an estimate.
4. Preserve the v005 six-target scope, exact two-record registry admission,
   foreign-byte attribution, OPS transaction, `groundtruth.db` Git exclusion,
   and the accepted short compatibility conditions above. Update exact changed
   source/test hashes and any affected definition/snapshot/result provenance in
   the proposal.
5. Refile the corrected proposal as **REVISED** (not NEW). No protected source,
   registry, database, dispatcher/TAFE, Git, or external mutation is authorized
   by this NO-GO.

## Commands Executed

- `Get-FileHash -Algorithm SHA256` on all six v005 targets and exact v005.
- `python -m groundtruth_kb bridge show gtkb-wi5806-operational-control-config-foundation --json --compact` — v005 REVISED, exact five-version chain.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5806-operational-control-config-foundation` — PASS; no missing specs or blocking errors.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5806-operational-control-config-foundation` — exit 0; zero blocking gaps.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_operational_control_config.py -q --tb=short` — `29 passed in 2.12s`.
- `groundtruth-kb/.venv/Scripts/ruff.exe check ...` — all checks passed.
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check ...` — two files already formatted.
- `groundtruth-kb/.venv/Scripts/python.exe -m py_compile ...` — exit 0.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest` on the five named registry-control-plane functions — `9 passed in 5.03s`.
- `python -m groundtruth_kb registry reconcile --json` — 26 current candidates; exact two WI-5806 candidates retained; candidate manifest
  `sha256:2810623117920edc0ceee9b6adcb98976aced7c0cc639089d03c8633b6245d20`;
  reconciliation evidence
  `sha256:f2418900a5b6e882cbd4152a4b10fa1a401641c56f002da0c062ba7c1a66eee6`.
- `python -m groundtruth_kb registry inspect --no-census --json` — coherent/current identity; declaration/package parity.
- `python -m groundtruth_kb registry validate --json` — expected global `registry_membership_incomplete`; 26 load-bearing gaps, `invalid_unknown=0`; no mixed registry state.
- `python scripts/bridge_claim_cli.py status <slug>` on the WI-5806 thread and every current nonterminal physical overlap — no active conflicting claim at the observation boundary.
- `cross_claim_path_collision_reason(...)` on the exact six-target cohort — `None`.
- `python -m groundtruth_kb deliberations get` for `DELIB-202667748`, `DELIB-202667725`, `DELIB-202667517`, and `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT`.
- Minimal in-memory identical-TOML/different-binding probe — same catalog SHA, different definition digest, old snapshot accepted by new catalog, present `90` silently resolved as default `30`.

## Owner Action Required

None. The correction is bounded by the existing owner decisions, project,
PAUTH, and v005 revision allowance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*

Skills applied: gtkb-bridge, gtkb-proposal-review, gtkb-verify
