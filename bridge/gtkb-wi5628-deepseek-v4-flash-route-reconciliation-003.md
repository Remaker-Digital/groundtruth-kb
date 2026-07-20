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
Version: 003
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-002.md
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
projection. Change only D's headless `--model` value from
`kimi-k2-7-code-cloud` to `deepseek-v4-flash-cloud`.

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
version/provenance and headless model argument changed. Concurrent unrelated
MemBase records and all other projection records must be preserved.

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

## Requirement Sufficiency

Existing requirements are sufficient. The work is one append-only registry
transaction through an existing governed CLI. No new harness, route taxonomy,
role, capability, or dispatcher policy is introduced.

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
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Owner Decisions / Input

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` requires at least
  one reliable independent LO reviewer and closure of derived reliability work.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` requires Ollama model selection
  to agree with the canonical route authority.
- PAUTH version 4 includes WI-5628 and permits the bounded MemBase,
  configuration, metadata, and projection transaction while retaining all
  per-slice gates.

No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE`
- `DELIB-202665813` - prior route-switch review evidence establishing the
  canonical MemBase plus projection transaction.

## Proposed Transaction

1. Confirm latest bridge status exact `GO`, acquire the exact WI-5628 claim,
   and finalize the implementation-start packet for both targets.
2. Capture operation-time D row, projection object, hashes, diff attribution,
   dispatcher configuration, routing resolution, live workers, and health.
3. Parse the current `invocation_surfaces` JSON and construct a new `headless`
   object that differs only at the value immediately following `--model`.
4. Prove the JSON and command shape in an isolated test root through existing
   harness operation and CLI tests.
5. Execute exactly one live command:

```text
gt harness set-invocation-surface --harness D --surface headless --value-json <captured-headless-object-with-only-model-changed> --reason "WI-5628: reconcile D with canonical DeepSeek V4 Flash bridge-review route"
```

6. Read back MemBase and the root projection through canonical APIs.
7. Prove only D's append-only version/provenance and headless model argument
   changed; all other invocation fields, roles, status, precedence,
   capabilities, eligibility, rankings, caps, and harness records are equal.
8. Prove routing, provider ID, and dispatcher label agree.
9. Dispatch one substantive independently reviewable item through D and require
   exit code `0` plus a valid numbered verdict.

No direct DB edit, projection edit, nested projection write, routing TOML edit,
dispatcher rule edit, daemon restart, or credential operation is allowed.

## Cross-Harness Disposition

Applicability is role-relative and active-only under
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`.

- **D / Ollama / active Loyal Opposition:** applicable. Its adapter-specific
  headless model argument is the inconsistent surface being corrected.
- **F / OpenRouter / active Loyal Opposition:** not changed. F uses its own
  provider and model resolution contract; forcing D's provider route onto F
  would violate rather than improve parity.
- **A / Codex / active Prime Builder:** not changed. This is a role- and
  adapter-specific LO invocation correction.
- **B, C, E, H and any other registered harness:** no invocation, role,
  status, capability, precedence, eligibility, or route changes.

The universal invariant is behavioral: every active applicable harness must
report and execute its own canonical invocation identity. The concrete model
value is role/provider-specific. No parity waiver is required.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4; WI-5628; TEST-11673; bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-002.md",
  "canonical_authority": "REQ-HARNESS-REGISTRY-001, GOV-HARNESS-STATE-SOT-CONSOLIDATION-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001, SPEC-DISPATCHER-CONTROL-SURFACE-001",
  "primary_route": "MemBase harness record, gt harness set-invocation-surface, generated root registry projection, canonical Ollama route resolver, dispatcher config, live D verdict, independent verification.",
  "before_behavior": "D explicitly invokes Kimi while routing and dispatcher authorities identify DeepSeek V4 Flash; Kimi dispatches return HTTP 429.",
  "after_behavior": "D's canonical headless invocation, route resolver, provider ID, and dispatcher label agree on DeepSeek V4 Flash and one substantive live D review exits 0.",
  "self_descriptive_naming": "WI-5628, TEST-11673, transaction reason, and verification rows all name D DeepSeek V4 Flash route reconciliation.",
  "obsolete_guidance_disposition": "The nested noncanonical projection is removed from scope. No historical harness row or bridge artifact is rewritten.",
  "history_preservation": "MemBase appends a new D version; bridge, work-item, test, PAUTH, transaction, and verification evidence remain append-only.",
  "baseline": {
    "authoritative_store": "groundtruth.db harnesses table, D version 81 at proposal revision time",
    "canonical_projection": "harness-state/harness-registry.json",
    "headless_model": "kimi-k2-7-code-cloud",
    "routing_and_dispatcher_label": "deepseek-v4-flash-cloud",
    "nested_projection": "noncanonical and outside transaction scope"
  },
  "expected_result": {
    "mem_base": "one new D harness version with only headless model and append-only provenance changed",
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
    "The transaction changes only D headless model plus append-only provenance.",
    "No nested registry projection is written or treated as authority.",
    "All non-D records and all D role/status/capability/precedence/dispatch fields are preserved.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "Either target changes after operation-time baseline capture without attributable preservation.",
    "The current headless object no longer contains exactly one expected Kimi model argument.",
    "The canonical command would mutate any non-model invocation field.",
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
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Command transcript and structured pre/post comparison | One governed command; no direct file/DB edit; only intended model delta plus provenance. |
| Cross-harness parity | Compare all pre/post harness records and run applicable parity checks | D identity becomes truthful; A/B/C/E/F/H records are semantically unchanged; no waiver needed. |
| Route agreement | Ollama routing resolver, provider model ID probe, and `gt bridge dispatch config --json` | Route key and dispatcher label are `deepseek-v4-flash-cloud`; provider ID is `deepseek-v4-flash:cloud`. |
| Existing behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` | Exit 0. |
| Live reliability | Dispatch D against a substantive independent LO item | Process exits 0; valid numbered verdict is published; no HTTP 429, provider-status mismatch, or stale circuit breaker. |
| Worktree preservation | Structured DB/projection diff plus `git diff -- groundtruth.db harness-state/harness-registry.json` | WI-5628 delta is attributable; all foreign changes and unrelated rows/records remain. |
| Nonimpairment | `gt bridge dispatch health --json` before and after | No daemon restart, cap, route-policy, lease, TAFE, credential, deployment, or release mutation. |

## Acceptance Criteria

- Exact GO, claim, and implementation-start packet authorize both real targets.
- One canonical transaction appends one D harness version and regenerates the
  root projection.
- Only D's headless model plus append-only provenance changes.
- Root canonical readers, Ollama resolver, provider ID, and dispatcher label
  agree on DeepSeek V4 Flash.
- Nested projection and all non-D harness records remain untouched.
- Focused tests pass.
- One substantive live D review exits `0` and publishes a valid independent
  verdict without HTTP 429 or status mismatch.
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
