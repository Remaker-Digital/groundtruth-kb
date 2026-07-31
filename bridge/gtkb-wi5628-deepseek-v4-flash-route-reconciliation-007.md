REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - Reconcile harness D to DeepSeek V4 Flash

bridge_kind: prime_proposal
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 007
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-006.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5628

target_paths: ["groundtruth.db", "harness-state/harness-registry.json"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

Use one canonical `gt harness set-invocation-surface` transaction to append a
new harness D record in MemBase and regenerate the one canonical root registry
projection. Remove D's explicit headless `--model kimi-k2-7-code-cloud` pair
and retain `--skill bridge-review`. The adapter then resolves
`deepseek-v4-flash-cloud` from the existing canonical Ollama routing
configuration instead of hardcoding any selected model in the harness record.

The authoritative write is `groundtruth.db`; the generated hot-path projection
is `harness-state/harness-registry.json`. The nested
`groundtruth-kb/harness-state/harness-registry.json` is removed from scope
because the command does not write it and
`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` identifies the root projection as the
canonical registry surface.

## Finding Responses

### F1 - Declared targets could not execute the canonical transaction

Accepted and corrected.

- `groundtruth.db` is now an exact target.
- `harness-state/harness-registry.json` remains the generated target.
- `kb_mutation_in_scope` is now `true`.
- The nested registry projection is removed.

The live command is not a file edit. It calls the append-only harness operation,
then regenerates the root projection. Before execution, Prime Builder records:

- the complete structured D row from MemBase;
- the parsed D root-projection object;
- SHA-256 and Git attribution for both targets;
- the exact current headless object.

After execution, structured comparison must prove that only the D harness
version/provenance and removal of the two headless model-override arguments
changed. Concurrent unrelated MemBase records and all other projection records
must be preserved.

### F2 - Governing registry and parity specifications were omitted

Accepted and corrected. This revision adds
`REQ-HARNESS-REGISTRY-001`,
`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, and
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, maps each to verification, and
includes the required Cross-Harness Disposition.

### F3 - Three advisory specifications were uncited

Accepted and corrected. This revision cites
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

### Version 004 F1 and Version 006 F1 - WI-5446 authority and canonical history

Accepted and corrected. WI-5628 is the residual recovery and superseding
registry step for the intended WI-5446 outcome, not a second route-creation
lifecycle.

- `DELIB-202666767` authorized WI-5446's DeepSeek V4 Flash outcome.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-004.md`
  independently approved that implementation.
- The v005 report and v006 NO-GO prove that the route configuration, dispatcher
  label, tool/readiness behavior, and focused tests were implemented and found
  substantively sound. The v006 blocker was commingled
  `config/dispatcher/rules.toml` attribution, not a route defect.
- The complete append-only MemBase history does not substantiate the registry
  transaction claimed by WI-5446 v005. Across all D versions through v81, the
  selected-model transitions are only v1 `None`, v22
  `deepseek-v4-pro-cloud`, and v25 `kimi-k2-7-code-cloud`. No D row ever
  contains `deepseek-v4-flash-cloud` in the headless model pair.
- Later `gt bridge dispatch config` eligibility transactions preserved Kimi;
  they did not overwrite a recorded Flash row. D version 81 was written at
  `2026-07-19T04:21:36+00:00` by
  `gt-bridge-dispatch-config-cli` with reason
  `set dispatch eligibility via gt bridge dispatch config` and still preserves
  Kimi.
- The root projection truthfully reflects the newest MemBase row. The durable
  report/history conflict is preserved as audit evidence: WI-5446 v005 claimed
  the governed D registry transaction, while canonical append-only history
  shows that step was not recorded.

WI-5628 therefore owns only the residual registry correction. It carries
forward the already implemented and reviewed WI-5446 route/test/dispatcher
evidence, changes neither those files nor their claims, and executes the
intended but unsubstantiated residual registry step by removing the duplicated
selected-model override. Only WI-5628 owns verification of that residual live
route consistency.

### Version 006 F2 - WI-5446 terminal closure was circular and unauthorized

Accepted and removed from this proposal. WI-5628 does not mutate WI-5446,
declare canonical supersession metadata, or make predecessor terminalization a
post-VERIFIED acceptance condition. Its implementation and verification end
with the bounded D registry transaction and fresh live D proof.

WI-5446 remains an explicit predecessor lifecycle conflict after WI-5628. It
will be dispositioned separately through its existing bridge/work-item
authority, with any terminal MemBase transition occurring only after applicable
`GOV-15` owner-approved evidence and independent review. That later lifecycle
must cite WI-5628's terminal result plus both bridge threads, but it is not a
target, invariant, or verification predicate of WI-5628.

### Version 004 F4 - Hardcoded replacement would violate routing single-SoT

Accepted and corrected. The transaction no longer replaces one hardcoded model
with another. It removes the explicit `--model` pair and leaves the stable skill
selector in the invocation. `scripts/ollama_harness.py` already resolves that
skill through `.api-harness/routing.toml`, whose active
`routing.ollama.skills.bridge-review` value is
`deepseek-v4-flash-cloud`.

This reconciles the two owner decisions without discarding either:
`DELIB-202666767` controls the selected DeepSeek V4 Flash outcome, while
`DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` controls the durable implementation
method. The earlier explicit registry pin was a bounded implementation choice
under WI-5446; it is superseded here because live evidence proves that duplicate
writer-owned literals do not remain synchronized. The canonical route retains
the owner-selected model while D's invocation retains only the stable
`bridge-review` skill selector.

### Version 004 F5 - Canonical reader contract was omitted

Accepted and corrected. This revision cites
`DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` and verifies all root projection
readback through `groundtruth_kb.harness_projection.read_roles`.

## Requirement Sufficiency

Existing requirements are sufficient. The work is one append-only registry
transaction through an existing governed CLI. No new harness, route taxonomy,
role, capability, model selection, or dispatcher policy is introduced. The
existing routing SoT already selects DeepSeek V4 Flash.

This proposal performs no work-item terminal transition. `GOV-15` and
`GOV-STANDING-BACKLOG-001` remain the authority for the later, separate
WI-5446 disposition.

## In-Root Placement Evidence

Both targets are inside `E:\GT-KB`:

- `groundtruth.db`
- `harness-state/harness-registry.json`

Both are currently dirty from governed concurrent work. WI-5628 claims only
the operation-time append to harness D and its generated projection delta. It
must preserve all foreign rows and bytes through structured readback and exact
diff attribution.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - FR1 makes the append-only MemBase harness record
  authoritative, FR5 defines the generated hot-path projection, and FR8 makes
  invocation surfaces data-driven.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - identifies the root registry
  projection and canonical read APIs.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - all committed readers use
  `groundtruth_kb.harness_projection.read_roles` rather than direct JSON reads.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - Ollama skill routing is the only
  live selected-model authority; the harness record must not override it.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - the resolved DeepSeek route must expose
  the tools required for substantive LO review.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - verdict metadata must derive
  from the selected route returned by the adapter.
- `ADR-CROSS-HARNESS-PARITY-001` - owner-visible model identity and actual
  headless invocation must agree.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires role-relative,
  active-only applicability and this Cross-Harness Disposition.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires a reliable independent LO
  lane with truthful model identity.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - configuration changes use governed
  CLI/API transactions rather than direct mutation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001` - WI-5446 remains visible for a separate governed
  disposition rather than being mutated after WI-5628 verification.
- `GOV-15` - any later terminal WI-5446 transition requires explicit
  owner-approved evidence and is outside this proposal.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Owner Decisions / Input

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` requires at least
  one reliable independent LO reviewer and closure of derived reliability work.
- `DELIB-202666767` selects DeepSeek V4 Flash as D's reviewer route and
  authorized the predecessor WI-5446 transaction. WI-5628 preserves that
  outcome while superseding its duplicated explicit-pin implementation method.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` requires Ollama model selection
  to remain selectable through one canonical route authority rather than a
  harness invocation override.
- PAUTH version 4 includes WI-5628 and permits the bounded MemBase,
  configuration, metadata, and projection transaction while retaining all
  per-slice gates.

No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-202666767` - owner-selected DeepSeek V4 Flash outcome and predecessor
  WI-5446 implementation authority.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE`
- `DELIB-202665813` - prior route-switch review evidence establishing the
  canonical MemBase plus projection transaction.
- `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md` through
  `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-006.md` -
  predecessor GO, implementation report, and audit-trail-only NO-GO. The
  report's registry claim conflicts with canonical MemBase history and is
  preserved rather than treated as proof.
- `bridge/gtkb-ollama-routing-single-sot-cleanup-004.md` - VERIFIED authority
  that Ollama model selection remains in routing configuration.

## Proposed Transaction

1. Confirm latest bridge status exact `GO`, acquire the exact WI-5628 claim,
   and finalize the implementation-start packet for both targets.
2. Capture operation-time D row, projection object, hashes, diff attribution,
   dispatcher configuration, routing resolution, live workers, and health.
3. Parse the current `invocation_surfaces` JSON and construct a new `headless`
   object that differs only by removing the adjacent `--model` and
   `kimi-k2-7-code-cloud` argv elements.
4. Prove the JSON and command shape in an isolated test root through existing
   harness operation and CLI tests.
5. Execute exactly one live command:

```text
gt harness set-invocation-surface --harness D --surface headless --value-json <captured-headless-object-with-explicit-model-pair-removed> --reason "WI-5628: remove D model override and use canonical DeepSeek V4 Flash bridge-review route"
```

6. Read back MemBase and the root projection through canonical APIs.
7. Prove only D's append-only version/provenance and removal of the explicit
   headless model pair changed; all other invocation fields, roles, status, precedence,
   capabilities, eligibility, rankings, caps, and harness records are equal.
8. Prove routing, provider ID, and dispatcher label agree.
9. Dispatch one substantive independently reviewable item through D and require
   exit code `0` plus a valid numbered verdict.

No direct DB edit, projection edit, nested projection write, routing TOML edit,
dispatcher rule edit, daemon restart, or credential operation is allowed.
No WI-5446 work-item mutation or terminal transition is allowed in this scope.

## Cross-Harness Disposition

Applicability is role-relative and active-only under
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`.

- **D / Ollama / active Loyal Opposition:** applicable. Its stale explicit
  headless model override is removed so its adapter follows the shared route.
- **F / OpenRouter / active Loyal Opposition:** not changed. F uses its own
  provider and model resolution contract; forcing D's provider route onto F
  would violate rather than improve parity.
- **A / Codex / active Prime Builder:** not changed. This is a role- and
  adapter-specific LO invocation correction.
- **B, C, E, H and any other registered harness:** no invocation, role,
  status, capability, precedence, eligibility, or route changes.

The universal invariant is behavioral: every active applicable harness must
report and execute the model selected by its canonical provider route. The
concrete route remains role/provider-specific. No parity waiver is required.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; DELIB-202666767; DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4; WI-5446; WI-5628; TEST-11673; bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md through -006.md; bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-004.md",
  "canonical_authority": "REQ-HARNESS-REGISTRY-001, GOV-HARNESS-STATE-SOT-CONSOLIDATION-001, DCL-HARNESS-STATE-SOT-READER-CONTRACT-001, DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001, SPEC-DISPATCHER-CONTROL-SURFACE-001",
  "primary_route": "MemBase harness record, gt harness set-invocation-surface, generated root registry projection, canonical Ollama route resolver, dispatcher config, live D verdict, independent verification.",
  "before_behavior": "D explicitly invokes Kimi while routing and dispatcher authorities identify DeepSeek V4 Flash; Kimi dispatches return HTTP 429.",
  "after_behavior": "D has no selected-model override; its canonical route resolver, provider ID, and dispatcher label agree on DeepSeek V4 Flash and one substantive live D review exits 0.",
  "self_descriptive_naming": "WI-5628, TEST-11673, transaction reason, and verification rows all name D DeepSeek V4 Flash route reconciliation.",
  "obsolete_guidance_disposition": "The nested noncanonical projection is removed from scope. No historical harness row or bridge artifact is rewritten.",
  "history_preservation": "MemBase appends a new D version; bridge, work-item, test, PAUTH, transaction, and verification evidence remain append-only.",
  "baseline": {
    "authoritative_store": "groundtruth.db harnesses table, D version 81 at proposal revision time; complete selected-model transitions are v1 none, v22 deepseek-v4-pro-cloud, and v25 kimi-k2-7-code-cloud, with no DeepSeek Flash row through v81",
    "canonical_projection": "harness-state/harness-registry.json",
    "headless_override": "--model kimi-k2-7-code-cloud",
    "routing_and_dispatcher_label": "deepseek-v4-flash-cloud",
    "nested_projection": "noncanonical and outside transaction scope"
  },
  "expected_result": {
    "mem_base": "one new D harness version with only the explicit model pair removed plus append-only provenance",
    "projection": "root registry regenerated from MemBase with no unrelated semantic delta",
    "live_dispatch": "one substantive D LO verdict, process exit 0, no 429, no status mismatch, no stale circuit residue",
    "runtime_effect": "no daemon restart, cap change, TAFE mutation, lease reset, credential operation, deployment, release, push, or history rewrite"
  },
  "rollback": {
    "instructions": "Before VERIFIED and only if live DeepSeek proof fails, use the same canonical command to append a D version restoring the exact captured pre-change headless object. Never edit the DB or projection directly.",
    "verification": "Read back D through gt harness show and canonical projection APIs; prove all non-provenance fields equal the captured pre-change state."
  },
  "hard_invariants": [
    "MemBase is authoritative and the root registry is generated.",
    "The transaction only removes D's explicit headless model pair and appends provenance.",
    "No nested registry projection is written or treated as authority.",
    "All non-D records and all D role/status/capability/precedence/dispatch fields are preserved.",
    "WI-5628 owns only residual live-state verification and performs no WI-5446 lifecycle mutation.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "Either target changes after operation-time baseline capture without attributable preservation.",
    "The current headless object no longer contains exactly one adjacent --model and kimi-k2-7-code-cloud pair.",
    "The canonical command would mutate any invocation field other than removing that exact pair.",
    "Readback, projection, route resolver, dispatcher label, or live provider identity disagrees.",
    "The live D review exits nonzero or fails to publish a valid substantive verdict."
  ],
  "essential_context_preservation": "Preserve WI-5628, TEST-11673, owner decisions, PAUTH v4, MemBase authority, root projection authority, exact pre-state D object, all foreign DB/projection changes, route/provider/dispatcher identities, live failure and success evidence, and rollback data."
}
```

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| `REQ-HARNESS-REGISTRY-001` FR1/FR5/FR8 | Pre/post DB row history plus canonical projection readback | Exactly one new D version; root projection matches latest MemBase row; invocation remains data-driven. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | `gt harness show --harness D` and `groundtruth_kb.harness_projection.read_roles` | Both canonical readers agree; nested projection is neither read nor written as authority. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | Source/API inspection and canonical reader readback | No direct committed JSON reader is introduced; root projection readback uses `read_roles`. |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | Resolve `bridge-review` with no `--model` override | Selected tag is `deepseek-v4-flash-cloud` from routing configuration. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` and `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Readiness/tool probe plus live verdict metadata | DeepSeek has required tools and published metadata derives from `deepseek-v4-flash:cloud`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Command transcript and structured pre/post comparison | One governed command; no direct file/DB edit; only the exact two-element override removal plus provenance. |
| Cross-harness parity | Compare all pre/post harness records and run applicable parity checks | D identity becomes truthful; A/B/C/E/F/H records are semantically unchanged; no waiver needed. |
| Route agreement | Ollama routing resolver, provider model ID probe, and `gt bridge dispatch config --json` | Route key and dispatcher label are `deepseek-v4-flash-cloud`; provider ID is `deepseek-v4-flash:cloud`. |
| Existing behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` | Exit 0. |
| Live reliability | Dispatch D against a substantive independent LO item | Process exits 0; valid numbered verdict is published; no HTTP 429, provider-status mismatch, or stale circuit breaker. |
| Predecessor evidence | Inspect every D MemBase version and WI-5446 v003-v006 | Report/history conflict is preserved accurately: WI-5446 claimed the registry write, but no Flash registry row exists; WI-5628 performs no predecessor work-item mutation. |
| Worktree preservation | Structured DB/projection diff plus `git diff -- groundtruth.db harness-state/harness-registry.json` | WI-5628 delta is attributable; all foreign changes and unrelated rows/records remain. |
| Nonimpairment | `gt bridge dispatch health --json` before and after | No daemon restart, cap, route-policy, lease, TAFE, credential, deployment, or release mutation. |

## Acceptance Criteria

- Exact GO, claim, and implementation-start packet authorize both real targets.
- One canonical transaction appends one D harness version and regenerates the
  root projection.
- Only D's explicit headless model pair is removed plus append-only provenance.
- Root canonical readers, Ollama resolver, provider ID, and dispatcher label
  agree on DeepSeek V4 Flash.
- Nested projection and all non-D harness records remain untouched.
- Focused tests pass.
- One substantive live D review exits `0` and publishes a valid independent
  verdict without HTTP 429 or status mismatch.
- WI-5446 remains unchanged by this scope and is routed to a separate governed,
  owner-approved lifecycle disposition after WI-5628.
- No daemon restart or unrelated dispatcher mutation occurs.

## Pre-Filing Preflight Subsection

The governed revision helper must pass candidate applicability and mandatory
clause preflights with no missing required/advisory specifications and no
blocking gaps.

## Risks and Rollback

- Risk: concurrent MemBase work could be overwritten. Mitigation: append-only
  canonical operation, operation-time row/diff capture, and structured
  unrelated-row equality.
- Risk: DeepSeek route could fail despite capacity probes. Mitigation: live
  substantive review is required before VERIFIED; rollback appends the exact
  captured pre-state through the same command.
- Risk: D-only change could be mistaken for universal parity. Mitigation:
  explicit role-relative cross-harness disposition and all-record equality.
- Rollback: use the same canonical command with the captured pre-change
  headless object. Never edit or restore the binary DB/projection wholesale.

## Recommended Commit Type

`fix`
