NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f78d0-941d-78f2-87d4-bb342596fcba
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop forked independent Loyal Opposition proposal review; explicit owner role assignment; reasoning_effort=high
author_metadata_source: CODEX_THREAD_ID

bridge_kind: lo_verdict
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 004
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md
Date: 2026-07-19 UTC

# Loyal Opposition Review - WI-5628 DeepSeek V4 Flash route reconciliation

## Verdict

`NO-GO`. Version 003 corrects the target-path and mutation-scope defects from the
prior verdict, and its canonical transaction is executable as declared. It does
not, however, reconcile the proposal with the already GO'd and partly executed
WI-5446 route-switch chain, omits the owner decision that explicitly authorized
that earlier transaction, leaves the older single-source directive and the newer
explicit registry-pin decision unresolved, and omits a directly applicable
blocking harness-state reader contract from its specification-to-test mapping.
These authority and lifecycle defects must be resolved before a second
transaction is authorized.

## First-Line Eligibility And Independence

- The owner explicitly assigned this interactive context the Loyal Opposition
  review task. `NO-GO` is an LO-authorized status under
  `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer `CODEX_THREAD_ID`:
  `019f78d0-941d-78f2-87d4-bb342596fcba`.
- Version 003 author session:
  `019f77f8-0931-75e2-a78d-7dea7037f743`
  (`bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md:6`).
- `scripts.bridge_review_independence.self_review_reason(...)` returned `None`;
  the session contexts are distinct and the review is independent.
- Immediately before publication, the canonical chain head was version 003 with
  status `REVISED`; version 004 did not exist and no claim was held.

## Positive Confirmations

- The full WI-5628 chain, versions 001 through 003, was inspected.
- Version 003 now declares the exact paths written by the canonical operation:
  `groundtruth.db` and `harness-state/harness-registry.json`
  (`bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md:24`).
  It correctly sets `kb_mutation_in_scope: true`.
- The canonical `gt harness set-invocation-surface` implementation appends the
  MemBase harness record and regenerates the root registry projection; no nested
  registry target is required.
- PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4 is active and includes WI-5628.
- Both mandatory preflights pass: no missing mechanically required or advisory
  specs and no blocking clause gaps.
- Live authorities confirm the residual mismatch: D's root registry argv still
  names `kimi-k2-7-code-cloud`
  (`harness-state/harness-registry.json:222`), while routing and dispatcher
  authorities name `deepseek-v4-flash-cloud`
  (`.api-harness/routing.toml:147`, `.api-harness/routing.toml:153`,
  `config/dispatcher/rules.toml:28`).

## Findings

### F1 - P1 Blocking - The proposal does not reconcile the existing WI-5446 authority and lifecycle

**Claim.** Version 003 presents the registry repoint as a standalone WI-5628
transaction but omits the pre-existing WI-5446 bridge chain and its controlling
owner decision.

**Evidence.**

- `DELIB-202666767` explicitly authorized WI-5446 to add the DeepSeek V4 Flash
  route, repoint routing defaults and skills, repoint D's registry headless
  `--model`, update the dispatcher label, and adjust focused tests.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md:171`
  proposed the same governed D registry repoint. Independent LO granted GO at
  `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md`.
- The implementation report claims that the registry transaction ran
  (`bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-005.md:65`).
- The latest WI-5446 verdict is `NO-GO`, but it expressly confirms the
  DeepSeek route-switch substance and blocks terminal verification because
  `config/dispatcher/rules.toml` contains unrelated commingled changes
  (`bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-006.md`).
- WI-5446 remains open, while live D has reverted or remained at Kimi. Version
  003 cites neither WI-5446 nor its bridge chain and does not explain the
  contradiction between the earlier implementation report and current state.

**Impact.** Two open work items and two bridge chains now claim authority over
one logical model-repoint lifecycle. A second GO could duplicate a transaction,
obscure whether the earlier report was inaccurate or its result was later lost,
and leave both work items non-terminal with conflicting completion evidence.

**Required correction.** Revise WI-5628 to state explicitly whether it
supersedes, absorbs, depends on, or performs residual recovery for WI-5446.
Carry forward `DELIB-202666767` and the WI-5446 GO/report/NO-GO evidence; explain
why live registry state contradicts the earlier report; sequence or terminally
disposition the predecessor chain/work item so only one lifecycle owns final
verification.

### F2 - P1 Blocking - Single-source authority and the explicit registry pin are not reconciled

**Claim.** Version 003 cites the older no-hardcoding decision while proposing to
replace one explicit registry `--model` literal with another, but omits the newer
owner decision that specifically authorized that pin.

**Evidence.**

- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` says Ollama model selection must
  be selectable through one source of truth and not hardcoded elsewhere.
- Version 003 cites that decision while changing only D's explicit headless
  model argument from Kimi to DeepSeek
  (`bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md:33`,
  `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md:132`,
  `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md:160`).
- `DELIB-202666767`, which version 003 omits, later explicitly authorizes
  repointing D's registry `--model` as part of the Flash swap.
- Runtime already supports route-derived selection: `resolve_model` chooses
  `requested_model`, then the skill route, then the default route
  (`scripts/ollama_harness.py:364`). Omitting an explicit `--model` is therefore
  a viable architecture that must at least be considered against a duplicated
  pin.

**Impact.** The proposal cannot establish whether the registry literal is a
scoped exception/supersession authorized by the newer decision or stale
projection duplication contrary to the older single-source contract. Merely
asserting equality across duplicated values does not settle which surface owns
selection or how future route changes stay synchronized.

**Required correction.** Cite both deliberations and state their precedence and
scope relationship. Either document the newer decision as an explicit bounded
exception/supersession for D's argv pin, with a durable synchronization
invariant, or revise the invocation to derive the model from the canonical
routing skill/default. Map the selected authority to verification that proves
future selection behavior, not only one-time value equality.

### F3 - P1 Blocking - A directly applicable reader-contract specification is omitted

**Claim.** The proposal's verification plan invokes the canonical
`groundtruth_kb.harness_projection.read_roles` reader but does not cite or test
against the specification that governs that entrypoint.

**Evidence.**

- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` requires harness-state reads to
  use `groundtruth_kb.harness_projection.read_roles`, `read_identity`, and
  `read_capabilities`; the implementation identifies this DCL directly
  (`groundtruth-kb/src/groundtruth_kb/harness_projection.py:44`,
  `groundtruth-kb/src/groundtruth_kb/harness_projection.py:472`).
- Version 003 explicitly uses `read_roles` as acceptance evidence
  (`bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md:247`) but
  omits the DCL from `## Specification Links` and its
  `## Specification-Derived Verification` table.
- The mechanical applicability preflight is a floor, not a ceiling; its clean
  result does not waive a directly applicable specification found by full
  review.

**Impact.** The proposal fails the mandatory concrete specification-linkage and
spec-derived verification standard for an authority it directly exercises.

**Required correction.** Add
`DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` to Specification Links and map its
relevant clauses to the canonical-reader readback test. Verify that no direct
registry parse is used as operational authority.

## Required Revisions

1. Reconcile WI-5628 with WI-5446 and its complete bridge lifecycle, including
   the contradictory implementation-report/live-state evidence.
2. Cite `DELIB-202666767` and resolve its explicit model-pin authorization
   against `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE`.
3. Add `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` and its derived test mapping.
4. Re-run both mandatory preflights against the revised numbered proposal.

## Prior Deliberations

- `DELIB-202666767` - directly authorizes the DeepSeek V4 Flash route switch and
  D registry `--model` repoint under WI-5446; omitted from version 003.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - authorizes the
  Dispatcher-Next closure program but does not erase predecessor lifecycle or
  specification-linkage obligations.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` - requires a selectable Ollama
  model source of truth without duplicated hardcoded model versions.
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - prior Kimi route decision,
  superseded by `DELIB-202666767` for future D dispatch.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - historical DeepSeek Pro pin,
  also superseded by `DELIB-202666767`.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md` through
  `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-006.md` - existing
  GO, implementation report, and latest NO-GO for the same logical switch.

## Applicability Preflight

- packet_hash: `sha256:4caaf63f502c05ef8ebec737b7dad260639cfc61283a72b0c87a794998696d4b`
- candidate_evidence_hash: sha256:8c15dbea4f86fb93a6c881f801b66838d9cf4dc09c5c12befe1764a0e754f30e
- bridge_document_name: `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`
- declared_target_paths: ["groundtruth.db", "harness-state/harness-registry.json"]
- applicability_path_evidence: ["bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-002.md", "groundtruth-kb/tests/test_harness_ops.py", "groundtruth.db", "harness-state/harness-registry.json", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md`
- operative_file: `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`
- Operative file: `bridge\gtkb-wi5628-deepseek-v4-flash-route-reconciliation-003.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Commands Executed

- `gt bridge show gtkb-wi5628-deepseek-v4-flash-route-reconciliation --json --compact` - latest `REVISED`, version 003.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5628-deepseek-v4-flash-route-reconciliation` - exit 0; no missing specs. The shared-tree CLI rendered packet `647a...`; the governed writer freshness audit rebuilt and required packet `4caa...`, which is embedded above.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5628-deepseek-v4-flash-route-reconciliation` - exit 0; zero blocking gaps.
- `gt deliberations show DELIB-202666767 --json` and `gt deliberations show DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE --json` - authority content inspected.
- Read-only full-chain inspection of WI-5628 versions 001-003 and WI-5446 versions 003-006, plus scoped code, registry, routing, dispatcher, work-item, test, project-authorization, and specification queries.

## Owner Decisions / Input

No new owner decision is required. Prime Builder must reconcile existing owner
authority and work-item lifecycle evidence in the revised proposal.

## Disposition

Prime Builder should file a revised numbered proposal after resolving all three
P1 findings. No implementation is authorized by this verdict, and this review
modified no non-bridge file.

Skills applied: `proposal-review`, `gtkb-bridge`.
