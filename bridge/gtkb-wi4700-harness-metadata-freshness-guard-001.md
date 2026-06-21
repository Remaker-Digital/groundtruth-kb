NEW

# WI-4700 Harness Metadata Freshness Guard Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4700-harness-metadata-freshness-guard
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-20 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-pb-2026-06-20-cost-autodispatch-wi4700
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder session role from `::init gtkb pb`

Project Authorization: PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4700

target_paths: [".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", ".claude/rules/operating-model.md", "harness-state/harness-registry.json", ".api-harness/routing.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py", "groundtruth-kb/tests/test_doctor_canonical_terminology.py", "groundtruth-kb/tests/test_doctor_harness_state_sot.py", "platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py", "groundtruth.db", "bridge/gtkb-wi4700-harness-metadata-freshness-guard-*.md"]

implementation_scope: harness_metadata_freshness_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
protected_source_mutation_in_scope: true
protected_narrative_mutation_in_scope: true

---

## Summary

Owner deliberation `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION`
identified stale harness/model metadata that can mislead cost-optimized
dispatch. The canonical terminology and operating-model text still describe
Ollama as a local Ollama-served model surface, while `.api-harness/routing.toml`
currently routes the `ollama` API-harness skills to cloud Kimi model ids. The
harness registry also records the Ollama harness with very low dispatch cost,
which can make a cloud-backed and currently unreliable route appear cheap.

This proposal requests approval to correct the stale canonical/registry
surfaces and add a deterministic doctor guard so the same divergence cannot
silently reappear. The implementation must distinguish the upstream Ollama
platform from the GT-KB harness route that may target cloud model ids through
the current routing file.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source, configuration,
  narrative, and MemBase evidence changes must proceed through bridge GO,
  implementation-start, report, and LO verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  links the implementation to concrete project authorization, specs, target
  paths, and verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The header carries
  the active PAUTH, project, and `WI-4700` work-item linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The post-implementation
  report must show a failing-before/passing-after doctor guard or an equivalent
  targeted fixture proving stale metadata is detected.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` and
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - The bounded PAUTH enables
  proposal work but does not bypass normal review and verification.
- `REQ-HARNESS-REGISTRY-001` - The harness registry must remain a reliable
  operational input for role, dispatchability, and routing decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - The doctor implementation and
  tests are GT-KB platform artifacts under the project root; no adopter or
  archive path is in scope.
- `GOV-STANDING-BACKLOG-001` - `WI-4700` remains the durable backlog item until
  the corrected artifacts and doctor guard are verified.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The metadata correction and doctor
  guard must remain durable, reviewable project artifacts.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - The implementation must prevent stale
  canonical/registry claims from drifting away from the routing source used by
  dispatch.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Owner selected the
  systemic freshness guard option: correct stale "Ollama=local/free" text and
  add a deterministic doctor check comparing canonical/registry metadata to
  `.api-harness/routing.toml`.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` - OpenRouter registry integration
  context; relevant because registry metadata must not overstate provider cost
  or capability.
- `bridge/gtkb-lo-review-dispatch-reliability-008.md` - Prior reliability
  verification context that WI-4700 now complements by removing stale router
  inputs.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md` - Related
  Ollama provider-failure/fallback reliability work; WI-4700 should not
  duplicate fallback implementation, only metadata freshness.
- `bridge/gtkb-wi-4557-api-harness-state-reconciliation-*.md` - Prior API
  harness state reconciliation context; WI-4700 adds a durable guard so stale
  state does not return.

## Owner Decisions / Input

No new owner decision is required. The owner selected the systemic freshness
guard in `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION`, and
`PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD` bounds the allowed mutation
classes to source, tests, config, protected narrative files, governance
evidence, project links, and `WI-4700` MemBase updates.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4700` explicitly requires both
parts: correcting stale canonical/registry text and adding a deterministic
doctor check that fails when canonical or registry dispatch metadata diverges
from `.api-harness/routing.toml`. No new formal requirement is needed before
implementation.

## Implementation Plan

1. Acquire an implementation-start packet after LO GO for this bridge id and
   the declared target paths.
2. Update the canonical terminology and operating-model text so it accurately
   distinguishes the upstream Ollama platform, the GT-KB Ollama harness, and
   cloud model ids currently selected through `.api-harness/routing.toml`.
3. Reconcile `harness-state/harness-registry.json` dispatch metadata so cost
   and naming no longer imply a free local route when the selected default
   route is cloud-backed.
4. Add a deterministic doctor check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
   that compares the canonical/registry harness metadata against the routing
   file and fails or warns when provider/model/cost claims diverge materially.
5. Add focused tests covering clean metadata, stale local/free claims while
   routing points at cloud Kimi, and missing/malformed routing or registry
   data.
6. Update `WI-4700` MemBase evidence after tests pass and file a
   post-implementation report with all command outputs and residual risks.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4700-harness-metadata-freshness-guard`
  and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4700-harness-metadata-freshness-guard`.
  Expected: no missing required specs and no blocking clause gaps.
- `REQ-HARNESS-REGISTRY-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: run the
  new focused doctor tests for harness metadata freshness. Expected: stale
  local/free canonical or registry claims fail when `.api-harness/routing.toml`
  routes the harness to cloud Kimi; aligned metadata passes.
- Protected narrative correctness: run the existing canonical terminology
  doctor tests, including
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py -q --tb=short`.
  Expected: pass.
- Doctor regression: run
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_ollama.py groundtruth-kb/tests/test_doctor_harness_state_sot.py -q --tb=short`.
  Expected: pass, including the new freshness-guard cases.
- Project evidence: run `gt backlog show WI-4700 --json` after the evidence
  update. Expected: status detail cites this bridge chain and the passing
  freshness-guard verification.
- Dispatch visibility: run `gt bridge dispatch status --json` and
  `gt bridge dispatch health --json`. Expected: current dispatcher health is
  disclosed honestly; this WI fixes metadata freshness, not every dispatch
  runtime failure.

## Risk / Rollback

Primary risk is overcorrecting by pretending the upstream Ollama platform is no
longer local-capable. Mitigation: wording must distinguish upstream Ollama from
the GT-KB harness route currently configured in `.api-harness/routing.toml`.

Rollback is a normal single-thread revert of the narrative/config/source/test
changes plus a MemBase evidence correction if the doctor guard is too broad. No
deployment, credential lifecycle change, retired poller restoration, bridge
bypass, or unrelated formal-artifact mutation is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4700-harness-metadata-freshness-guard`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the expected change corrects stale harness metadata and adds a guard
against recurrence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
