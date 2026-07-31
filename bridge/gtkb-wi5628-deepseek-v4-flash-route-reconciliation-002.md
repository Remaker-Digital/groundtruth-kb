NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f78ba-0b91-7431-a1e4-efcde47929ce
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: independent headless Loyal Opposition proposal review; transcript-defined loyal-opposition role; repository-native read-only evidence gathering

bridge_kind: lo_verdict
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 002
Date: 2026-07-19 UTC
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md

# Loyal Opposition Review - WI-5628 DeepSeek V4 Flash route reconciliation

## Verdict

`NO-GO`. The route reconciliation is necessary and the proposed end state agrees
with WI-5628, TEST-11673, PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v3, and the live
routing/dispatcher authorities. The implementation packet is not executable as
declared, however: its canonical command necessarily appends a MemBase harness
record and regenerates one root projection, while the proposal excludes
`groundtruth.db`, declares no KB mutation, and instead names a second projection
that the command does not write. The proposal also omits directly governing
harness-registry/parity specifications and the mandatory Cross-Harness
Disposition section. Those are authorization and specification-linkage blockers,
not implementation details that can be repaired after GO.

## Review Independence

- Proposal author session: `019f77f8-0931-75e2-a78d-7dea7037f743`.
- Reviewer session: `019f78ba-0b91-7431-a1e4-efcde47929ce`.
- The session contexts are distinct.
- The owner task explicitly resolves this context as independent headless Loyal
  Opposition. `NO-GO` is an LO-authorized status and the latest thread status
  inspected before filing was `NEW`.

## Positive Confirmations

- WI-5628 is open under
  `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE`, identifies the three-way route
  conflict, and links TEST-11673.
- TEST-11673 correctly requires the D registry argv, Ollama routing authority,
  dispatcher budget, a dry-run/applied transaction check, and one successful live
  D dispatch without provider mismatch, HTTP 429, or stale circuit residue.
- PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v3 is active, includes WI-5628, and has a
  mutation-class envelope capable of carrying the corrected metadata,
  runtime-state, and configuration scope. No new owner decision is indicated by
  this review.
- Live root and nested registry projections still carry
  `kimi-k2-7-code-cloud` for D
  (`harness-state/harness-registry.json:222`,
  `groundtruth-kb/harness-state/harness-registry.json:222`), while the root
  projection is version 81 and the nested projection is version 80
  (`harness-state/harness-registry.json:232`,
  `groundtruth-kb/harness-state/harness-registry.json:232`).
- Live routing and dispatcher budget authorities select
  `deepseek-v4-flash-cloud`
  (`.api-harness/routing.toml:147`,
  `.api-harness/routing.toml:153`,
  `config/dispatcher/rules.toml:28`).
- The latest observed D dispatch selected the Kimi route and exited 1 after
  repeated HTTP 429 responses. That corroborates the work item's problem
  statement, but does not cure the proposal-scope defects below.
- Both mandatory preflights exited 0. Their outputs are reproduced below.

## Findings

### F1 - P1 Blocking - The declared target set cannot execute the proposed canonical transaction

**Claim.** The proposal says implementation is one canonical
`gt harness set-invocation-surface` transaction, declares only the root and
nested registry projections as targets, and sets `kb_mutation_in_scope: false`
(`bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md:24`,
`:29`, and `:43`).

**Evidence.**

- The CLI opens the configured KnowledgeDB, calls
  `harness_ops.set_invocation_surface`, and then calls
  `generate_harness_projection`
  (`groundtruth-kb/src/groundtruth_kb/cli.py:10349`,
  `groundtruth-kb/src/groundtruth_kb/cli.py:10352`,
  `groundtruth-kb/src/groundtruth_kb/cli.py:10362`).
- The operation appends a new harness version in MemBase while preserving other
  fields (`groundtruth-kb/src/groundtruth_kb/harness_ops.py:501`,
  `groundtruth-kb/src/groundtruth_kb/harness_ops.py:512`,
  `groundtruth-kb/src/groundtruth_kb/harness_ops.py:533`).
- Root configuration resolves that database to `groundtruth.db`
  (`groundtruth.toml:2`).
- Projection generation resolves one path:
  `<project_root>/harness-state/harness-registry.json`, then writes that one path
  (`groundtruth-kb/src/groundtruth_kb/harness_projection.py:388`,
  `groundtruth-kb/src/groundtruth_kb/harness_projection.py:400`,
  `groundtruth-kb/src/groundtruth_kb/harness_projection.py:434`,
  `groundtruth-kb/src/groundtruth_kb/harness_projection.py:449`).
- The analogous WI-5047 route-switch proposal included `groundtruth.db` and set
  `kb_mutation_in_scope: true`
  (`bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md:20`,
  `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md:26`);
  its GO review explicitly records why the DB carrier is required
  (`bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-002.md:116`).

**Impact.** A GO on version 001 would authorize a target set that omits the
canonical transaction's authoritative write and includes a projection the
transaction does not update. The resulting implementation-start packet could
not truthfully authorize or verify the proposed command.

**Required correction.** Revise the target set to include `groundtruth.db` and
the root `harness-state/harness-registry.json`, set
`kb_mutation_in_scope: true`, and remove the nested projection unless the
revision introduces and justifies a separate governed writer for it. If the
nested file is intentionally retained, specify the exact authority and
transaction that writes it; the current command is insufficient.

### F2 - P1 Blocking - Directly governing harness-state and parity specifications are omitted

**Claim.** Version 001 cites `ADR-CROSS-HARNESS-PARITY-001`, but does not cite
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, does not contain a
`## Cross-Harness Disposition` section, and omits the registry source-of-truth
requirements that explain the MemBase-to-projection transaction.

**Evidence.**

- `REQ-HARNESS-REGISTRY-001` v3 FR1 makes the append-only MemBase `harnesses`
  table authoritative; FR5 defines the flat registry as generated projection;
  FR8 makes invocation surfaces data-driven.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` v1 identifies the root
  `harness-state/harness-registry.json` as the MemBase roles projection and
  requires canonical access.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` v2
  PARITY-DISPOSITION-GATE requires `## Cross-Harness Disposition` whenever
  proposal target paths touch a harness-surface file.
- The proposal's only relevant matches are its declared target paths and command
  (`bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md:24`,
  `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md:43`);
  the required DCL and disposition heading are absent.

**Impact.** The mandatory specification-linkage gate makes omission of any
relevant governing specification a `NO-GO`. The missing parity disposition also
prevents review of whether this D-only invocation change is role-relative,
universal, or covered by an approved waiver.

**Required correction.** Add
`REQ-HARNESS-REGISTRY-001`,
`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, and
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` to Specification Links, map them to
the verification plan, and add a concrete `## Cross-Harness Disposition`
section covering active applicable harnesses or citing a typed owner-approved
waiver.

### F3 - P2 Revision Hygiene - The applicability preflight reports three uncited advisory specifications

**Evidence.** The mandatory applicability preflight passes its blocking floor
but reports:

`missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]`

**Impact.** This does not independently trigger the blocking gate, but it leaves
version 001 short of the protocol's clean pre-filing expectation and would
persist unchanged on a resubmission unless addressed.

**Required correction.** Cite the three applicable advisory specifications in
the revision, or narrow the triggering prose only if it is genuinely
non-operative. Re-run both preflights against the revised operative file.

## Required Revisions

1. Make the target/mutation declaration match the canonical command:
   `groundtruth.db` plus the root generated registry projection,
   `kb_mutation_in_scope: true`; remove or separately justify the nested
   projection.
2. Add the omitted registry SoT requirement/governance links and the
   cross-harness enforcement DCL, with verification mappings.
3. Add `## Cross-Harness Disposition` with a concrete applicability or waiver
   analysis.
4. Resolve the three advisory-spec omissions and rerun both mandatory
   preflights on the revised numbered proposal.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - authorizes the
  Dispatcher-Next program envelope and PAUTH v3; it does not waive per-slice
  scope accuracy or LO review.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` - establishes the route
  source-of-truth direction carried by the proposal.
- `DELIB-202665813` - prior WI-5047 route-switch GO evidence; directly relevant
  precedent that the canonical harness invocation update mutates
  `groundtruth.db` and then regenerates the registry projection.

## Applicability Preflight

- packet_hash: `sha256:e0f0cccd06ddbca894f5bc4e13d32565088cd465eb45a5842cf1786785295d2e`
- candidate_evidence_hash: `sha256:1719726485e50764e8b22b81399ed570124a8f6bf902c8ac05c4a6f9f272615e`
- bridge_document_name: `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`
- declared_target_paths: ["groundtruth-kb/harness-state/harness-registry.json", "harness-state/harness-registry.json"]
- applicability_path_evidence: ["bridge/`", "groundtruth-kb/harness-state/harness-registry.json", "groundtruth-kb/tests/test_harness_ops.py", "harness-state/harness-registry.json", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md`
- operative_file: `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`
- Operative file: `bridge\gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Commands Executed

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5628-deepseek-v4-flash-route-reconciliation --content-file bridge\gtkb-wi5628-deepseek-v4-flash-route-reconciliation-001.md` - exit 0; blocking preflight passed; three advisory omissions reported.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5628-deepseek-v4-flash-route-reconciliation` - exit 0; no blocking clause gaps.
- Read-only `gt backlog show`, test, project-authorization, specification, bridge-dispatch config/status, and deliberation queries for WI-5628, TEST-11673, PAUTH v3, the governing specs, and the prior route decision.
- Read-only `rg`, `git diff`, and scoped file reads over the proposal, canonical harness mutation/projection code, live registries, routing, dispatcher rules, and the latest D dispatch evidence.

## Disposition

Prime Builder should file a revised numbered proposal after the four required
revisions. No target projection or implementation surface was mutated during
this review.

Skills applied: `proposal-review`, `gtkb-bridge`.
