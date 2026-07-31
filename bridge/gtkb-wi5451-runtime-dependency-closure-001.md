NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5451 - Make dispatcher generation identity cover the executable dependency closure

bridge_kind: prime_proposal
Document: gtkb-wi5451-runtime-dependency-closure
Version: 001
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5451-RUNTIME-DEPENDENCY-CLOSURE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5451
Related Work Items: WI-5427, WI-5429, WI-5448
Related Test Artifact: TEST-11554
target_paths: ["scripts/dispatcher_runtime_dependency_manifest.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime_dependency_manifest.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]
implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix(dispatcher):

## Summary

Replace WI-5427's fixed four-path dispatcher-generation tuple with a
deterministic manifest of the complete repository-owned executable source
closure rooted in the daemon and supervisor. A byte change to any load-bearing
local module must change the generation identity; an unrelated source,
configuration, bridge, test, or application change must not.

The manifest builder will resolve repository-owned static imports without
executing imported code, include an explicit bounded declaration of dynamic
provider/helper modules, reject unresolved or ambiguous local dependencies,
and produce stable path/hash/size diagnostics plus one aggregate generation
hash. The daemon will use that one manifest implementation for both loaded and
current generation identity.

This proposal does not implement WI-5427, WI-5448, or WI-5429 and does not
adopt their unverified bytes. Shared daemon targets remain hard-sequenced
behind terminal focused disposition of WI-5427 and WI-5448. No live daemon
handoff, start, stop, restart, generation activation, dispatcher/TAFE
configuration transaction, or runtime-state mutation is authorized.

## Requirement Sufficiency

Existing requirements sufficient.

`DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` requires deterministic
loaded/current generation identity and safe supervised handoff.
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and
`ADR-DISPATCHER-ARCHITECTURE-001` keep the identity inside the one canonical
daemon/supervisor architecture.
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` requires unrelated worktree changes
not to strand dispatch and forbids disturbing live work.
WI-5451 and linked TEST-11554 supply the concrete dependency-closure
acceptance condition. No requirement revision is needed.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded PAUTH and proposal lifecycle for this newly discovered in-scope
  fleet defect while preserving every downstream gate.
- `bridge/gtkb-wi5427-daemon-generation-handoff-001.md` defines the
  predecessor generation-handoff design and the incomplete fixed source tuple.
- `bridge/gtkb-wi5427-daemon-generation-handoff-004.md` records the independent
  NO-GO that must be resolved before shared daemon-byte mutation.
- `bridge/gtkb-wi5427-daemon-generation-handoff-005.md` is the current
  REVISED predecessor report awaiting independent terminal disposition.
- `bridge/gtkb-wi5448-dead-daemon-lease-restart-001.md` and
  `bridge/gtkb-wi5448-dead-daemon-lease-restart-002.md` define independently
  GO-approved overlapping daemon ownership that must be dispositioned first.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-001.md` and
  `bridge/gtkb-wi5429-finalized-runtime-generation-admission-002.md` define
  the downstream consumer of WI-5451's terminal manifest identity.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  decision authorizing this bounded defect-repair lifecycle.
- Active
  `PAUTH-DISPATCHER-BLACK-BOX-WI5451-RUNTIME-DEPENDENCY-CLOSURE-20260717`
  authorizes one proposal now and source/test implementation only after
  independent GO, exact claim, implementation-start authorization, and
  predecessor ownership clearance.
- The owner-directed dispatcher troubleshooter hold remains controlling.
  This proposal authorizes no dispatcher configuration or runtime-state
  mutation and no live process operation.
- No new owner decision is requested.

## Current Target State And Ordering

Observed before filing:

- `scripts/dispatcher_runtime_dependency_manifest.py` is absent.
- `platform_tests/scripts/test_dispatcher_runtime_dependency_manifest.py` is
  absent.
- `scripts/gtkb_dispatcher_daemon.py` exists, is dirty, and has SHA-256
  `dc1e1a077cb83c1d2dc9c69180d01d8cca77e56cd179d5f8ddf859deaf608556`.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` exists, is dirty,
  and has SHA-256
  `153af7f6d53db772acce98b940b19fb5dc0a83bd931f9ec43025f6e913110995`.

The two dirty files are foreign predecessor ownership, not WI-5451
implementation. Implementation must not begin until all of these conditions
hold:

1. WI-5427 has a terminal independent VERIFIED disposition and focused
   finalization.
2. WI-5448 has a terminal independent VERIFIED disposition and focused
   finalization, or a canonical terminal withdrawal/supersession proves no
   remaining overlapping byte ownership.
3. Both shared targets are clean relative to HEAD and match their terminal
   predecessor evidence.
4. Both new targets remain absent.
5. The latest WI-5451 bridge entry is an independent GO, an exact matching
   `go_implementation` claim is active, and schema-v3 implementation-start
   authorization validates all four exact targets.

WI-5429 is downstream: it may consume the terminal WI-5451 manifest identity
but is not a prerequisite and receives no implementation bytes here.

## Proposed Implementation

1. Add `scripts/dispatcher_runtime_dependency_manifest.py` as a pure,
   read-only manifest builder. Its roots are
   `scripts/gtkb_dispatcher_daemon.py` and
   `scripts/ensure_dispatcher_daemon.py`.
2. Parse Python source with `ast` rather than importing it. Resolve only
   repository-owned modules through explicit in-root search roots:
   `scripts/` and `groundtruth-kb/src/`. Standard-library and third-party
   imports remain environment dependencies outside this source-generation
   manifest and are reported separately without being hashed as repository
   files.
3. Follow direct local imports transitively, cycle-safely, with
   path-boundary checks and canonical POSIX-relative paths. Include explicit,
   bounded dynamic dependencies for modules loaded by path or name, including
   the daemon's dispatcher runtime/monitor helpers and the supported harness
   readiness providers. Dynamic dependencies must be declared in one
   self-describing registry in the helper; runtime string interpolation may
   not silently widen or shrink the closure.
4. Fail closed with stable diagnostics when a repository-local import is
   unresolved or ambiguous, a declared dynamic path is missing, a path escapes
   the project root, a file cannot be read, or two module identities resolve
   inconsistently.
5. Emit one deterministically ordered manifest containing schema version,
   roots, path, byte size, SHA-256, dependency provenance, exclusions, and
   diagnostics. Derive the aggregate generation only from the canonical
   serialized repository-owned path/hash/size set.
6. Replace the fixed tuple in `scripts/gtkb_dispatcher_daemon.py` with the
   helper's single API for loaded and current generation computation. Preserve
   existing status keys and fail-closed `generation: null` behavior when the
   manifest is invalid.
7. Add focused unit tests for transitive static imports, cycles, explicit
   dynamic declarations, unresolved/ambiguous local imports, path escape,
   deterministic ordering, aggregate-hash sensitivity, and unrelated-path
   stability. Extend daemon tests only for the narrow integration and
   backward-compatible status contract.
8. Do not launch, stop, restart, signal, hand off, or inspect a live daemon.
   Tests use isolated temporary repositories and fixtures only.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; WI-5451; TEST-11554; PAUTH-DISPATCHER-BLACK-BOX-WI5451-RUNTIME-DEPENDENCY-CLOSURE-20260717",
  "canonical_authority": "DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Build one deterministic repository-owned executable dependency manifest from explicit daemon/supervisor roots, static AST imports, and a bounded dynamic-dependency registry, then use it for both loaded and current generation identity.",
  "before_behavior": "A fixed four-path tuple can report generation_match=true after an omitted load-bearing repository module changes.",
  "after_behavior": "Every included load-bearing repository-source change alters generation identity, unrelated paths do not, and incomplete or ambiguous closure yields an explicit fail-closed diagnostic.",
  "self_descriptive_naming": "dispatcher_runtime_dependency_manifest, manifest_roots, repository_dependencies, dynamic_dependency_registry, unresolved_local_import, and aggregate_generation identify the mechanism directly.",
  "obsolete_guidance_disposition": "The fixed RUNTIME_GENERATION_RELATIVE_PATHS tuple is superseded only after terminal WI-5427 and WI-5448 ownership and independent WI-5451 verification; proposal GO alone does not activate the new identity.",
  "history_preservation": "PAUTH, work item, linked test, bridge chain, predecessor reports, exact target hashes, generated manifest diagnostics, and terminal verification remain reconstructable; no prior artifact or runtime evidence is rewritten.",
  "baseline": {
    "generation_identity": "fixed four-path tuple in the unverified WI-5427 candidate",
    "known_omission_class": "repository-owned direct and dynamically loaded modules outside the tuple",
    "shared_target_ownership": "WI-5427 and WI-5448 remain non-terminal"
  },
  "expected_result": {
    "identity_input": "canonical ordered repository-owned executable dependency closure",
    "load_bearing_change": "aggregate generation changes",
    "unrelated_change": "aggregate generation remains unchanged",
    "closure_error": "generation is unavailable with stable diagnostics"
  },
  "rollback": {
    "instructions": "Use a separately governed focused revert of only the four WI-5451 targets after predecessor-byte separation.",
    "verification": "Rerun the focused manifest and daemon suites and confirm no process, configuration, TAFE, lease, claim, eligibility, routing, or runtime-state surface changed."
  },
  "hard_invariants": [
    "No implementation edit occurs before terminal WI-5427 and WI-5448 ownership clearance plus independent WI-5451 GO, exact claim, and schema-v3 start.",
    "No dispatcher configuration, TAFE, live runtime state, worker, lease, claim, role, eligibility, routing, credential, external system, Git history, deployment, or release state is mutated.",
    "Manifest construction executes no target module and reads no path outside E:/GT-KB.",
    "Unknown or ambiguous repository-local executable dependencies fail closed.",
    "Unrelated repository dirt does not alter generation identity.",
    "WI-5429 admission and any live generation handoff remain out of scope."
  ],
  "fail_closed_conditions": [
    "A repository-local static import is unresolved or ambiguous.",
    "A declared dynamic dependency is missing, unreadable, duplicated inconsistently, or outside the project root.",
    "Manifest roots, canonical ordering, path hashing, or aggregate serialization cannot be established.",
    "A shared target differs from terminal predecessor evidence at implementation start.",
    "Any predecessor, review, claim, PAUTH, implementation-start, or exact-target gate is absent."
  ],
  "essential_context_preservation": "The manifest preserves root provenance, every canonical relative path, hash, size, static or dynamic discovery reason, exclusion class, diagnostic, schema version, and aggregate generation."
}
```

## Specification-Derived Verification

| Governing requirement | Planned verification | Expected result |
|---|---|---|
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Focused manifest and daemon tests over direct, transitive, cyclic, and dynamic repository dependencies. | Loaded/current identity uses one complete deterministic source manifest and changes for every included dependency byte change. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Inspect exact four-file diff and run the existing daemon unit suite in isolated fixtures. | One canonical daemon/supervisor architecture remains; no alternate dispatcher, queue, poller, or activation path appears. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Tests dirty unrelated source/config/bridge/application paths and record fixture state before/after. | Unrelated changes do not change generation; no worker, lease, eligibility, routing, configuration, TAFE, or runtime state changes. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Exact pre-start hashes/status plus predecessor terminal checks and post-edit exact-target diff review. | WI-5427/WI-5448 bytes are terminal and clean before WI-5451 edits; no foreign hunk is claimed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Validate active PAUTH, latest GO, exact claim, schema-v3 start packet, and four target paths before editing. | Every protected mutation is authorized and exact; forbidden dispatcher/runtime operations remain absent. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live applicability plus mandatory clause preflights. | No required/advisory specification is missing and no blocking clause gap exists. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001` | Execute TEST-11554 through the focused helper/daemon tests, Ruff check/format, `py_compile`, and `git diff --check`. | All mapped checks pass and the linked test's falsifiable expected outcome is proven. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect WI, TEST, PAUTH, proposal, GO, claim/start, implementation report, exact diff, and independent verdict as distinct states. | The correction remains reconstructable and cannot become active from proposal or implementation evidence alone. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Root-boundary tests and exact target inspection. | All live dependencies and mutations remain inside E:/GT-KB and outside adopter/application repositories. |

## Pre-Filing Preflight Subsection

Observed against this exact candidate before filing:

- applicability preflight passed;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `blocking_errors: []`;
- mandatory clause preflight exited 0 with zero blocking gaps.

The governed writer must re-run bridge compliance before publication. Any
candidate drift, missing specification, collision, credential finding, or
publication-admission failure cancels filing.

## Acceptance Criteria

- The manifest contains every repository-owned executable dependency reachable
  from the daemon/supervisor roots through supported static imports or the
  explicit dynamic dependency registry.
- Any included file byte change changes the aggregate generation.
- Changes outside the closure leave the aggregate generation unchanged.
- Missing, escaped, unreadable, unresolved, or ambiguous local dependencies
  yield `generation: null` plus deterministic diagnostics.
- Manifest order and aggregate identity are stable across process, filesystem,
  and traversal ordering.
- The daemon's existing loaded/current generation and status contract remains
  backward compatible except for additive manifest diagnostics.
- WI-5427 and WI-5448 are terminally dispositioned and shared targets are clean
  before the first implementation edit.
- Focused tests, adjacent daemon tests, Ruff, formatting, compilation,
  applicability, clause preflight, and diff checks pass.
- No live process, dispatcher/TAFE configuration, runtime state, worker, lease,
  claim, eligibility, routing, credential, Git, deployment, release, or
  unrelated source surface is mutated.
- Independent Loyal Opposition VERIFIED is required for terminal closure.

## Risk And Rollback

The primary risk is an incomplete resolver that still omits a load-bearing
module, or an overbroad resolver that makes unrelated source changes force
handoff. The design therefore combines AST-based local import resolution with
one explicit dynamic registry, stable diagnostics, root containment, and tests
for both sensitivity and exclusion. It does not infer arbitrary runtime module
names or execute source while discovering dependencies.

Rollback is a separately governed focused revert of only the four declared
targets after exact predecessor-byte separation. Numbered bridge and MemBase
history remain append-only. Rollback performs no live restart, handoff,
configuration transaction, runtime-state mutation, deployment, or release.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
