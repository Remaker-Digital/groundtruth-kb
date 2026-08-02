NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; strict-lifecycle recovery proposal
author_metadata_source: explicit_interactive_session_metadata

# WI-5555/WI-5556 — Codex No-Window Evidence Strict Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project Authorization Version: 2
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5555
Work Item: WI-5556
target_paths: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "scripts/codex_no_window_smoke_probe.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

No KB mutation: this proposal does not create, update, migrate, or otherwise
mutate MemBase, `groundtruth.db`, a specification, a work item, a project, a
project authorization, or a Deliberation Archive record. Project reactivation
and owner-decision records cited below are completed historical prerequisites,
not declared implementation targets.

No protected implementation has started. This proposal creates no claim-backed
implementation authority until independent `GO`, an exact implementation
claim, a schema-v3 start packet, fresh operation-time PAUTH validation, and
clean exact preimages all pass.

## First-Line Role Eligibility Check

PASS. Harness A is the active Prime Builder and may file this substantive
`NEW` proposal. Prime does not author `GO`, `NO-GO`, or `VERIFIED`.

## Recovery Claim

Create one strict-valid recovery thread for the still-live WI-5555/WI-5556
repair. The historical thread's version 001 declares decorated metadata
`Version: 001 (NEW)`, so the strict lifecycle resolver rejects that chain with
`WRONG_BRIDGE_VERSION_METADATA`. Historical version 006's Loyal Opposition GO
correctly rejects a dormant-state NO-ACTION closure, but it cannot supply
implementation authority through the structurally invalid chain.

This replacement preserves the complete corrected design from historical
version 003 and version 006's finding that implementation has not started. The
old versions remain append-only evidence and are not rewritten.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5555/TEST-11613 defines exact
return-code typing, WI-5556/TEST-11614 defines fail-closed readiness on
`codex_models_manager::` ERROR output, the terminal WI-5389 validator contract
defines the schema-v3 baseline, and the specifications below govern the
project, bridge, verification, and nonimpairment boundaries.

No new formal requirement or per-WI implementation approval is needed. The
owner's project-level model makes active member WIs inherit the parent project's
approval while preserving every bridge, claim, PAUTH, start, verification, and
finalization gate.

## Project Reactivation And Authorization

The owner directed reactivation, captured in `DELIB-202667749`. The project is
now active at version 6 with `completed_at=null`; WI-5555 and WI-5556 remain
active open members. The list-free project PAUTH is active at version 2 and
permits bridge, source, test, metadata, and governance-evidence work.

That PAUTH forbids `git_commit`. This proposal therefore authorizes no commit
or finalization. After independent VERIFIED, any focused finalization requires
its own current exact authority. TAFE and dispatcher mutation remain forbidden.

## In-Root Placement Evidence

The live proposal belongs under `E:/GT-KB/bridge`, and every declared target is
under the `E:/GT-KB` project root. No source, fixture, generated artifact, log,
cache, credential, or dependency outside that root becomes implementation
authority.

## Exact Current Evidence

All six declared targets are tracked, clean, unstaged, and currently have these
SHA-256 identities:

| Path | SHA-256 |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py` | `8b5cafeaf3a83002025d2b12b23354b6a22241504d8f191a6809fedbc41a9b8b` |
| `groundtruth-kb/tests/test_codex_no_window_verification.py` | `19e93034d1d731683a184dfda5f43d778eab8fe83fcd64539e4c91c151561b9b` |
| `scripts/codex_no_window_smoke_probe.py` | `576d3030bdd2ba053916fdeb218f621b44b4ada08cdc9c1d44b2ba2358369515` |
| `platform_tests/scripts/test_codex_no_window_smoke_probe.py` | `13f9c859c2006990b686d1c0b2071f8e1f6094e698a46e99eb7e57e2b5dd5f8f` |
| `platform_tests/scripts/test_verify_codex_dispatch.py` | `319dace31700e2cc680d5f08c3f4300921a2cbf36f91f5fc4994226222df269c` |
| `platform_tests/scripts/test_dispatcher_runtime.py` | `df3af33107f5166a8133ae8c27716fd5d60befb226fc3715a0954a5dc73c780f` |

Fresh baseline verification is 45/45 package, smoke-probe, and dispatch-verifier
tests passing, plus 7/7 selected dispatcher-runtime tests passing. Ruff check
and format-check pass on the exact cohort. Those results prove baseline health,
not feature completion.

The defect is reproduced directly: `schema_failure_reason()` returns `None`
for wrapper and command-step return codes `false` and `0.0`. Current source uses
membership in `{0, "0"}`, and Python equality therefore accepts bool and float
zero. Current source also has no `codex_models_manager::` ERROR classifier or
stable model-cache-error reason.

## Proposed Implementation

### IP-1 — Exact return-code success semantics

Add one package-canonical helper that accepts only:

- exact `int` type with value `0`, excluding `bool`; or
- exact `str` type with value `"0"`.

Use that helper for every schema-v3 command-step and wrapper return-code check.
Preserve the current stable failure reasons and every unrelated schema rule.
Producer-side success aggregation must use the same exact semantics so written
evidence and validator decisions cannot disagree.

### IP-2 — Fail-closed model-manager diagnostics

Classify a captured line only when it contains both an ERROR-severity marker
and a logger identity beginning with `codex_models_manager::`. Any such line
makes the producer's run and overall probe fail. The shared validator returns
the stable reason `codex_no_window_verification_model_cache_error` when stored
schema-v3 evidence contains the diagnostic.

The match is line-oriented and namespace-specific. Negative controls must prove
that unrelated loggers, lower severities, warnings, and ordinary prose do not
trigger it. Deterministic in-root test strings cover `::cache`, `::manager`, a
manager-only case, and another namespace child. No home-directory model cache,
external provider state, runtime log, or credential is read or mutated.

### IP-3 — Shared consumers and nonimpairment

Keep `verify_codex_dispatch` and dispatcher readiness on the single shared
validator path; do not add a fork. Preserve private-desktop containment,
workspace create/read/remove sentinel lifecycle, marker chain, wrapper, expiry,
ACL, zero-visible-window, PB-only role, and max-items requirements.

No live headless probe is required to implement or test this repair. All new
tests use deterministic in-root fixtures. Do not start, stop, reroute, enable,
or reconfigure a harness, dispatcher, worker, or TAFE.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5555; WI-5556; TEST-11613; TEST-11614; DELIB-202667749; historical corrected proposal v003 and LO v006",
  "canonical_authority": "GOV-HARNESS-ONBOARDING-CONTRACT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; shared codex_no_window_verification schema-v3 validator",
  "primary_route": "Strict-valid proposal, independent GO, exact claim/start, six-path implementation, mapped tests, implementation report, independent VERIFIED, then separately authorized finalization",
  "before_behavior": "Bool and float zero are accepted as successful return codes, and model-manager ERROR output can coexist with readiness PASS.",
  "after_behavior": "Only exact integer zero or compatibility string zero succeeds, and any ERROR from the codex_models_manager namespace produces one stable fail-closed readiness reason across producer and consumers.",
  "self_descriptive_naming": "An exact success-return-code helper and model-manager ERROR classifier expose the validation intent directly.",
  "obsolete_guidance_disposition": "The historical cache-submodule-only design and dormant NO-ACTION closure remain preserved but are not current authority.",
  "history_preservation": "Both work items, both tests, WI-5389 evidence, the historical bridge chain, and this replacement remain distinct append-only artifacts.",
  "baseline": {
    "focused_tests": "45 passed plus 7 dispatcher-runtime selections",
    "false_accepts": ["wrapper false", "wrapper 0.0", "step false", "step 0.0"],
    "targets_clean": true,
    "project_version": 6
  },
  "expected_result": {
    "return_codes": "Exact int 0 excluding bool and exact str 0 only",
    "diagnostics": "Any codex_models_manager namespace ERROR fails producer and both consumers",
    "negative_controls": "Unrelated logger, lower severity, warnings, and prose remain accepted",
    "runtime": "No live dispatcher, TAFE, harness, provider, cache, credential, or external-system mutation"
  },
  "hard_invariants": [
    "Do not weaken containment, sentinel, marker, wrapper, expiry, ACL, role, or max-items checks.",
    "Do not read or mutate an external model cache, home directory, credential, runtime log, or provider state.",
    "Do not mutate dispatcher or TAFE state.",
    "Do not implement from the structurally invalid historical GO.",
    "Do not commit under a PAUTH that forbids git_commit."
  ],
  "rollback": {
    "instructions": "Under separate authority, restore only the exact six reviewed preimages; preserve bridge, project, PAUTH, claim, verdict, and test history.",
    "verification": "Rerun all mapped tests, Ruff, format, compile, exact hashes, scoped diff, and runtime/TAFE non-mutation checks."
  },
  "fail_closed_conditions": [
    "Missing fresh GO, exact claim, schema-v3 start packet, or allowed operation-time PAUTH result.",
    "Any target, project, membership, or ownership drift.",
    "Any bool, float, nonzero, malformed, or unrecognized return-code representation.",
    "Any codex_models_manager ERROR evidence.",
    "Any implementation need outside the exact six-path cohort."
  ],
  "essential_context_preservation": "The implementation report must retain both WI/test identities, exact before/after hashes, false-accept reproductions, stable reason, all negative controls, mapped commands, and explicit dispatcher/TAFE/external-state non-mutation evidence."
}
```

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Evidence

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — governed fleet
  defect lifecycle authority.
- `DELIB-202666274` — list-free Goose Harness Adoption project authority.
- `DELIB-202667749` — owner-directed project reactivation, completed with
  active status and cleared terminal timestamp.
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-004.md` — terminal
  shared schema-v3 predecessor.
- Historical `gtkb-wi5555-wi5556-codex-no-window-evidence-strictness` versions
  001–006 — corrected design, prior independent review, invalid dormant
  closure, and current LO direction; evidence only because the chain is
  strict-invalid.

## Owner Decisions / Input

No new owner decision is required. The parent project is active and approved,
and the two WIs inherit that approval. This statement does not bypass the fresh
independent GO, claim, start, PAUTH, verification, or separately authorized
finalization requirements.

## Specification-Derived Verification Plan

| Requirement | Command/evidence | Acceptance |
| --- | --- | --- |
| TEST-11613 exact return-code typing | Parameterize package and producer tests over exact `0`, `"0"`, booleans, floats, nonzero ints/strings, null, collections, and malformed values for wrapper and every command step | Only exact int zero excluding bool and exact string zero pass; stable existing reasons remain unchanged. |
| TEST-11614 model-manager diagnostics | Deterministic lines for `codex_models_manager::cache`, `::manager`, manager-only, another child, unrelated logger, warning/info, and prose | Namespace ERROR fails producer and validator with the stable reason; every negative control remains accepted. |
| Shared consumer parity | Focused `test_verify_codex_dispatch.py` and selected `test_dispatcher_runtime.py` cases | Both consumers surface the same validator decision without forked parsing. |
| Schema-v3 and harness nonimpairment | Full package and smoke-probe test modules | Containment, sentinel, marker, wrapper, expiry, ACL, zero-visible-window, role, and max-items behavior remains green. |
| Code quality and exact scope | Ruff check/format on all six paths; `py_compile` on both production modules; `git diff --check`; exact hashes/status | All gates pass and only reviewed six-path hunks exist. |
| Governance and runtime containment | Candidate/live applicability and clause preflights; claim/start/PAUTH receipts; before/after runtime and TAFE observation | Every gate passes; no dispatcher, TAFE, harness, cache, provider, credential, or external state changes. |

The implementation report must give exact commands, results, durations,
pre/post hashes, scoped diff, and explicit disposition of all six paths.
Independent Loyal Opposition verification remains mandatory.

## Timer, Concurrency, And SoT-Latency Review

This focused reproduction completed in seconds and did not prove a timer too
short. Existing hard-coded smoke-probe waits remain outside this defect slice;
their inventory and centralized externalization belong to WI-5804/WI-5806.
This implementation must introduce no new timer, retry, throttle, threshold,
fan-out, or concurrency literal. No new concurrency or SoT-latency failure was
observed, so no duplicate Advisory Report or correction WI is created.

## Risks And Rollback

The main risks are overmatching ordinary output, producer/validator divergence,
and weakening containment to recover readiness. Exact namespace/severity tests,
shared helper semantics, negative controls, and the six-path boundary mitigate
them. Rollback is restoration of the exact reviewed preimages under separate
authority; numbered artifacts remain append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py`
- `groundtruth-kb/tests/test_codex_no_window_verification.py`
- `scripts/codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
