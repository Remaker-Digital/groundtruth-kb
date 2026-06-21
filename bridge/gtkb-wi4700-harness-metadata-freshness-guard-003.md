REVISED

# WI-4700 Harness Metadata Freshness Guard Proposal (REVISED-1)

bridge_kind: prime_proposal
Document: gtkb-wi4700-harness-metadata-freshness-guard
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-20 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-20T21-27-34Z-prime-builder-B-715632
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code auto-dispatch; Prime Builder role from ::init gtkb pb

Project Authorization: PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4700

target_paths: [".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", ".claude/rules/operating-model.md", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py", "groundtruth-kb/tests/test_doctor_canonical_terminology.py", "groundtruth-kb/tests/test_doctor_harness_state_sot.py", "platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py", "groundtruth.db", "bridge/gtkb-wi4700-harness-metadata-freshness-guard-*.md"]

implementation_scope: harness_metadata_freshness_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
protected_source_mutation_in_scope: true
protected_narrative_mutation_in_scope: true

---

## Summary

This REVISED-1 submission addresses two NO-GO findings from
`bridge/gtkb-wi4700-harness-metadata-freshness-guard-002.md`:

**P1 (addressed):** `config/dispatcher/rules.toml` was absent from the
original `target_paths`. That file is the authoritative source of harness
D's `dispatch_cost = 5` overlay, which is then projected into
`harness-state/harness-registry.json` by
`groundtruth_kb.harness_projection.generate_harness_projection`. The revised
proposal adds `config/dispatcher/rules.toml` to `target_paths` and updates the
implementation plan to fix the overlay at its canonical source before
regenerating the projection. The projection file must not be hand-edited.

**P2 (addressed):** `.api-harness/routing.toml` has been removed from the
mutating `target_paths`. The routing file records the current model selection
and is not stale — the problem is that canonical/registry metadata does not
accurately describe what the routing file says. The routing file is used as
**read-only verification evidence** (confirming the harness currently routes to
cloud Kimi models) and is not itself an implementation target.

The underlying problem remains unchanged: harness D (Ollama) shows
`dispatch_cost = 5` in `config/dispatcher/rules.toml`, implying free local
inference, while `.api-harness/routing.toml` confirms the harness currently
routes all skills to `kimi-k2-7-code-cloud` — a cloud-backed model. Canonical
terminology and operating-model text still describe Ollama as serving locally
from `http://localhost:11434`. This proposal authorizes correcting those stale
claims at their authoritative sources and adding a deterministic doctor guard.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source, configuration, narrative,
  and MemBase evidence changes must proceed through bridge GO, implementation-start,
  report, and LO verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  links the implementation to concrete project authorization, specs, target
  paths, and verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The header carries the
  active PAUTH, project, and `WI-4700` work-item linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The post-implementation
  report must show a failing-before/passing-after doctor guard or equivalent
  targeted fixture proving stale metadata is detected.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` and
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - The bounded PAUTH enables
  proposal work but does not bypass review and verification.
- `REQ-HARNESS-REGISTRY-001` - The harness registry must remain a reliable
  operational input for role, dispatchability, and routing decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - Doctor implementation and tests are
  GT-KB platform artifacts under the project root.
- `GOV-STANDING-BACKLOG-001` - `WI-4700` remains the durable backlog item until
  corrected artifacts and the doctor guard are verified.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The metadata correction and doctor
  guard must be durable, reviewable project artifacts.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Implementation must prevent stale
  canonical/registry claims from drifting away from the routing source used by
  dispatch.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Owner selected the
  systemic freshness guard option: correct stale "Ollama=local/free" text and
  add a deterministic doctor check comparing canonical/registry metadata to
  `.api-harness/routing.toml`.
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-002.md` - LO NO-GO
  verdict: P1 identified `config/dispatcher/rules.toml` as the authoritative
  dispatch-cost source omitted from original target_paths; P2 identified
  `.api-harness/routing.toml` inclusion as broader than the stated correction
  scope. Both findings are fully addressed in this revision.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` - OpenRouter registry integration
  context; registry metadata must not overstate provider cost or capability.
- `bridge/gtkb-lo-review-dispatch-reliability-008.md` - Prior reliability
  verification context that WI-4700 complements by removing stale router inputs.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md` - Related
  Ollama provider-failure/fallback reliability work; WI-4700 does not duplicate
  fallback implementation, only metadata freshness.

## Owner Decisions / Input

No new owner decision is required. The owner selected the systemic freshness
guard in `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION`, and
`PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD` bounds the allowed mutation
classes to source, tests, config, protected narrative files, governance
evidence, project links, and `WI-4700` MemBase updates. The `config/` mutation
class in the PAUTH explicitly covers `config/dispatcher/rules.toml`.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4700` explicitly requires both parts:
correcting stale canonical/registry text and adding a deterministic doctor check
that fails when canonical or registry dispatch metadata diverges from
`.api-harness/routing.toml`. No new formal requirement is needed before
implementation.

## Implementation Plan

1. Acquire an implementation-start packet after LO GO for this bridge id and
   the declared target paths.

2. Update `config/dispatcher/rules.toml` — the authoritative overlay source
   (P1 fix):
   - Harness D entry: change `dispatch_cost = 5` to `dispatch_cost = 20`
     (matching OpenRouter harness F, which also routes cloud models; the
     current `5` implies free local inference and is materially stale for a
     cloud-backed route).
   - Harness D `description`: change from `"Ollama: cheapest Loyal Opposition
     dispatch target."` to `"Ollama-shim: cloud-routed LO dispatch target
     (current route: kimi-k2-7-code-cloud via cloud API)."` so the field
     accurately reflects the routing layer.

3. Regenerate `harness-state/harness-registry.json` from the updated overlay
   (P1 fix, generation step):
   - Run `groundtruth-kb/.venv/Scripts/gt.exe harness regenerate-projection` or
     the equivalent `groundtruth_kb.harness_projection.generate_harness_projection`
     call after updating rules.toml.
   - The projection file must not be hand-edited; it must be derived from the
     MemBase harnesses table combined with the updated dispatch overlay in
     `config/dispatcher/rules.toml`.

4. Update protected narrative files so the Ollama harness description reflects
   the current cloud-backed routing:
   - `.claude/rules/canonical-terminology.md` — update the `ollama` entry to
     note that the harness currently routes via `kimi-k2-7-code-cloud` through
     the cloud API and is NOT serving local open-weight models from localhost.
     The upstream Ollama platform remains local-capable; the GT-KB harness route
     is currently cloud-backed per `.api-harness/routing.toml`.
   - `.claude/rules/operating-model.md` §3 — update the Ollama harness Phase-1
     entry so the "locally hosts open-weight models via the Ollama platform
     CLI/server at `http://localhost:11434`" description is corrected to reflect
     the current cloud routing.
   - Both mutations require narrative-artifact-approval packets created and
     committed before the protected files are edited, per the standard
     narrative-artifact gate workflow.

5. Add a deterministic doctor check `_check_harness_metadata_freshness` in
   `groundtruth-kb/src/groundtruth_kb/project/doctor.py` that:
   - Reads `.api-harness/routing.toml` (read-only evidence) to determine the
     current provider/model for each harness.
   - Reads `config/dispatcher/rules.toml` to get dispatch cost overrides per
     harness.
   - For any harness whose routing.toml model_id contains `:cloud` or whose
     provider is `openrouter` while `dispatch_cost <= 10` in rules.toml, emits
     WARN so the stale low-cost claim is surfaced.
   - For any harness whose routing.toml `provider` is `ollama` and model_id
     contains `:cloud`, additionally flags canonical terminology or registry
     description text that still says "local" or `localhost` for that harness.
   - Initial severity: WARN (not FAIL) to give operational visibility before
     promoting to a hard gate in a follow-on slice.

6. Add focused tests:
   - `groundtruth-kb/tests/test_doctor.py` — `_check_harness_metadata_freshness`
     clean-pass case (cloud provider + cost >= 20), stale-low-cost case (cloud
     route + `dispatch_cost = 5`), and missing routing file graceful WARN.
   - `groundtruth-kb/tests/test_doctor_ollama.py` — Ollama-specific case:
     Ollama harness routing to `:cloud` model triggers local-description WARN.

7. Update `WI-4700` MemBase evidence after tests pass and file a post-
   implementation report with all command outputs and residual risks.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4700-harness-metadata-freshness-guard`
  and `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4700-harness-metadata-freshness-guard`.
  Expected: no missing required specs and no blocking clause gaps.
- `REQ-HARNESS-REGISTRY-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: run the
  new doctor tests. Expected: stale `dispatch_cost = 5` with cloud route causes
  WARN; corrected `dispatch_cost = 20` passes. Projection regenerated from
  updated rules.toml reflects corrected values.
- `config/dispatcher/rules.toml` correctness: inspect harness D entry after
  implementation — `dispatch_cost` must be `20` and `description` must reference
  cloud routing.
- `.api-harness/routing.toml` read-only evidence: confirm the file is unchanged
  before and after implementation (sha256 identical pre/post).
- Protected narrative correctness: run
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py -q --tb=short`.
  Expected: pass.
- Doctor regression: run
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_ollama.py groundtruth-kb/tests/test_doctor_harness_state_sot.py -q --tb=short`.
  Expected: pass, including the new freshness-guard cases.

## Risk / Rollback

Primary risk: the `dispatch_cost = 20` correction may change dispatch target
selection order for the LO role (harness D was previously ranked first on cost;
at cost=20 it ties with harness F). Mitigation: the `selection_order` in
rules.toml prefers `cost` then `availability`; harness D (`dispatch_availability
= 95`) beats harness F (`dispatch_availability = 90`) when costs are equal, so
harness D retains preference. The net effect is the ranking is preserved while
the stated cost is accurate.

Secondary risk: narrative-artifact-approval packets required for protected
narrative edits; missing packets will trigger the gate hook and block
implementation. Mitigation: create approval packets before editing protected
files, following the established packet workflow.

Rollback is a normal single-thread revert of narrative/config/source/test
changes plus a projection regeneration from the original rules.toml values. No
deployment, credential lifecycle change, retired poller restoration, bridge
bypass, or unrelated formal-artifact mutation is in scope.

## Bridge Filing

This REVISED proposal is filed as
`bridge/gtkb-wi4700-harness-metadata-freshness-guard-003.md`, the next
numbered file in the chain. No prior version is deleted or rewritten.
Dispatcher/TAFE state plus the numbered file chain are the live workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — the expected change corrects stale harness metadata and adds a guard
against recurrence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
