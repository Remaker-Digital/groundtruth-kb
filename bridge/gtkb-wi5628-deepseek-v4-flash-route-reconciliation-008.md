GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7901-9f5c-7f93-a0c9-9602e609c505
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Loyal Opposition; explicit owner role assignment; independent focused proposal review
author_metadata_source: CODEX_THREAD_ID plus current owner transcript role assignment

bridge_kind: lo_verdict
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 008
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-007.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5628

# Loyal Opposition Final Review - WI-5628 DeepSeek V4 Flash route reconciliation

## First-Line Role Eligibility Check

PASS. The owner explicitly assigned this interactive context as an independent
Loyal Opposition reviewer. `GO` is a Loyal Opposition-authorized status under
`GOV-FILE-BRIDGE-AUTHORITY-001`. Durable identity resolution identifies Codex
as harness A; the transcript-defined Loyal Opposition role controls this
interactive session without changing the durable dispatcher/default registry.

## Review Independence And Claim

PASS.

- Version 007 author session:
  `019f77f8-0931-75e2-a78d-7dea7037f743`.
- Current reviewer session from `CODEX_THREAD_ID`:
  `019f7901-9f5c-7f93-a0c9-9602e609c505`.
- `scripts.bridge_review_independence.self_review_reason(...)` has no refusal
  condition because the session contexts differ.
- Governed claim row `33452` was acquired for this exact slug and reviewer
  session before verdict drafting. The chain head was version 007 `REVISED`,
  and version 008 did not exist before publication.

## Verdict

GO. Version 007 accurately resolves both blocking findings from version 006 and
is approved only within its declared two-target scope.

The implementation may execute exactly one canonical
`gt harness set-invocation-surface` transaction that removes D's adjacent
`--model` / `kimi-k2-7-code-cloud` argv pair while retaining
`--skill bridge-review`. The transaction may append one D MemBase version and
regenerate only the canonical root projection. It does not authorize a direct
database or projection edit, a routing or dispatcher change, or any WI-5446
work-item mutation.

## Acceptance Findings

### F1 - Canonical D history is stated accurately

PASS. A read-only query inspected all 81 append-only D rows in `groundtruth.db`,
versions 1 through 81. The only selected-model transitions are:

- v1: no explicit model pair;
- v22: `deepseek-v4-pro-cloud`; and
- v25: `kimi-k2-7-code-cloud`.

There are zero D versions containing `deepseek-v4-flash-cloud` in the headless
model pair. Versions 26 through 81 preserve Kimi. Version 081 was written by
`gt-bridge-dispatch-config-cli` for dispatch eligibility and does not overwrite
a recorded Flash row. Version 007 states these facts directly.

### F2 - The WI-5446 report/history conflict is preserved

PASS. WI-5446 version 005 claims that its governed registry transaction changed
D to DeepSeek V4 Flash. Canonical MemBase history does not substantiate that
claim. WI-5446 version 006 accepted the route, dispatcher-label, readiness, and
test substance while blocking finalization for a commingled dispatcher-config
diff. Version 007 preserves both pieces of evidence without rewriting either
thread or promoting the implementation report above canonical history.

### F3 - Scope is one canonical residual transaction

PASS. The exact targets are `groundtruth.db` and
`harness-state/harness-registry.json`; `kb_mutation_in_scope` is true. The
nested projection is excluded. The proposed command uses the current structured
headless object and removes only the explicit two-element model override. The
adapter's existing precedence then resolves `bridge-review` through
`.api-harness/routing.toml`.

Live authority agrees with the proposed result:

- `.api-harness/routing.toml` maps the Ollama default and `bridge-review` skill
  to `deepseek-v4-flash-cloud`;
- that route maps to provider model `deepseek-v4-flash:cloud`;
- `scripts/ollama_harness.py::resolve_model` gives an explicit requested model
  precedence over the skill route, then the default route;
- `gt bridge dispatch config --json` identifies D as
  `deepseek-v4-flash-cloud`; and
- the current D MemBase row and root projection still contain the explicit
  Kimi pair.

Removing the pair, rather than replacing it with another selected-model
literal, satisfies both owner decisions: `DELIB-202666767` controls the
DeepSeek V4 Flash outcome, while
`DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` controls the single-source routing
method.

### F4 - WI-5446 terminal mutation is excluded

PASS. Version 007 removes WI-5446 terminalization from the proposed
transaction, hard invariants, verification predicates, and acceptance
criteria. WI-5446 remains open and unchanged. Any later terminal transition
must use a separate owner-approved `GOV-15`-governed lifecycle with independent
review, and must cite WI-5628's terminal result plus both bridge threads.
Nothing in this GO authorizes that later mutation.

### F5 - Specification and verification coverage is sufficient

PASS. The proposal links the registry/projection, canonical-reader, Ollama
routing/tool/metadata, dispatcher, cross-harness parity, source-freshness,
bridge, project-authorization, artifact-lifecycle, backlog, worktree-hygiene,
and non-impairment authorities. Its verification plan maps those requirements
to structured pre/post history, canonical readback, focused tests, route
agreement, live D completion, predecessor-evidence inspection, and unrelated
worktree preservation.

## Implementation Conditions

1. Reconfirm exact latest `GO`, acquire the WI-5628 implementation claim, and
   create an implementation-start packet for exactly `groundtruth.db` and
   `harness-state/harness-registry.json`.
2. Capture operation-time D history, current headless object, canonical
   projection, target hashes, dirty attribution, route resolution, dispatcher
   config, and health before mutation.
3. Execute one `gt harness set-invocation-surface` command using the captured
   headless object with only the adjacent explicit model pair removed.
4. Fail closed if the current object does not contain exactly one such pair or
   if any unrelated D field, non-D record, routing file, dispatcher rule,
   nested projection, daemon state, credential, or WI-5446 record would change.
5. Run the proposal's focused tests and canonical reader/route checks, then
   require one substantive independent D verdict with process exit 0 before
   requesting VERIFIED.
6. Preserve all foreign dirty bytes in both targets through structured
   comparison and exact attribution. Do not restore either whole file from a
   stale baseline.

## Applicability Preflight

- packet_hash: `sha256:86a2c2805c2b1cd5a41e1dd7934d3ebe321492987b099f4b1ef156e2f583cef3`
- candidate_evidence_hash: `sha256:87e3b91bd9d309ee28b3317a48230f5633713e671082304c08c229beaafaa876`
- bridge_document_name: `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`
- declared_target_paths: ["groundtruth.db", "harness-state/harness-registry.json"]
- applicability_path_evidence: ["bridge/gtkb-ollama-routing-single-sot-cleanup-004.md`", "bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md", "bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md`", "bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md`", "bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-006.md`", "bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-004.md", "bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-006.md", "bridge/work-item", "config/dispatcher/rules.toml`", "groundtruth-kb/tests/test_harness_ops.py", "groundtruth.db", "harness-state/harness-registry.json", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "scripts/ollama_harness.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-007.md`
- operative_file: `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`
- Operative file: `bridge\gtkb-wi5628-deepseek-v4-flash-route-reconciliation-007.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-202666767` selects DeepSeek V4 Flash for D and authorizes the
  predecessor WI-5446 governed route-switch outcome.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` requires selected Ollama model
  identity to remain selectable through one routing source of truth rather
  than duplicated hardcoded invocation literals.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` requires a reliable
  independent LO lane and independent review for this program.
- `DELIB-202665813` is prior route-switch review evidence for the canonical
  append-only MemBase plus root-projection transaction.
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-006.md` is the
  direct NO-GO whose canonical-history and lifecycle findings version 007
  resolves.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md` through
  `-006.md` preserve the predecessor approval, implementation claim, and
  audit-trail conflict.

## Methodology Trail

- Resolved durable harness identity A and transcript-defined Loyal Opposition
  role; verified current reviewer and version 007 author session IDs differ.
- Verified live bridge/dispatcher health and exact thread head, then acquired
  the exact governed claim.
- Read the complete WI-5628 chain, with focused comparison of versions 006 and
  007, plus WI-5446 versions 003 through 006.
- Read both controlling owner deliberations directly from the Deliberation
  Archive and queried WI-5446, WI-5628, and TEST-11673 from MemBase.
- Queried every D harness row read-only and parsed every headless argv model
  pair; inspected current canonical projection, routing configuration,
  resolver precedence, dispatcher config, and health.
- Ran both mandatory preflights against operative version 007; both exited 0
  with no missing specifications or blocking gaps.
- Ran `git diff --check` on version 007. No source, test, configuration,
  dispatcher, work-item, database, Git-history, deployment, or credential
  mutation was performed by this review.

## Owner Decisions / Input

No owner action is required. The proposal can proceed through the normal
implementation claim, implementation-start, report, and independent
verification lifecycle. Any later WI-5446 terminal transition remains a
separate owner-approved `GOV-15` matter.

## Decision

GO. Prime Builder may implement only the exact one-transaction residual
registry correction and verification plan approved above.

Skills applied: `proposal-review`, `gtkb-bridge`.
