REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed bridge heartbeat revision

# Revised Defect-Fix Proposal - Reject Hash-Current Generated Skill Adapters With Semantic Drift

bridge_kind: prime_proposal
Document: gtkb-wi5144-hp08-semantic-adapter-drift
Version: 003
Responds to: bridge/gtkb-wi5144-hp08-semantic-adapter-drift-002.md
Approved proposal carried forward: bridge/gtkb-wi5144-hp08-semantic-adapter-drift-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5144
target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py"]

## Revision Claim

Carry forward version 001's exact two-file implementation and its deterministic renderer comparison, while closing all three version 002 findings. This revision adds the controlling cross-harness ADR/DCL set, a complete per-renderer disposition, and durable tracked regressions for exact output and hash-current semantic tamper across Codex, Antigravity, and compact API adapters. The untracked MOD-HP08 clause-exact test is supplementary evidence only.

No generated adapter, canonical skill, manifest, registry, clause-exact baseline, harness state, dispatcher/routing state, Git state, credential, deployment, or release surface enters mutation scope.

## Requirement Sufficiency

Existing requirements are sufficient. The three newly linked parity authorities already require behavioral equivalence or typed waiver, complete population disposition, and enforcement across submission paths. This revision maps those obligations to the tracked focused suite without introducing new normative harness behavior.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - behavioral equivalence or typed owner waiver for every applicable harness-observable capability; metadata-only conformance is insufficient.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - discovery, applicability, disposition, waiver, doctor, and release enforcement for parity surfaces.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - enforcement across submission paths and independent NO-GO fallback for incomplete coverage.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - MOD-HP08 requires executable semantic-drift detection.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - existing path, hash, loadability, waiver, applicability, and classification behavior remains enforced.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - exact adapter equality and typed failure outcomes are deterministic evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation remains gated by independent GO, claim, start packet, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Prior Deliberations

- `DELIB-202666274` - owner authorization for required project-level modernization blocker repairs; no bridge or verification bypass.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - controlling parity invariant.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` - enforcement design provenance.
- `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-001.md` - complete original scope and design.
- `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-002.md` - findings corrected here.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666274` authorizes this bounded project repair while preserving all normal bridge, implementation-start, independent-verification, Git, release, and deployment gates. No typed parity waiver is needed because all three applicable adapter families receive direct parity coverage.

## Findings Addressed

### F1 - P1 - The controlling parity ADR/DCL set is absent from the proposal

Corrected. `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, and `DCL-CROSS-HARNESS-ENFORCEMENT-001` are concrete specification links above and have explicit tracked-test mappings below. They govern renderer population completeness, semantic equivalence, typed failure, and enforcement; generic mechanical carriers are no longer presented as substitutes.

### F2 - P1 - Cross-harness disposition and per-renderer evidence are missing

Corrected. The cross-harness disposition below names every applicable generated-adapter family. The tracked suite must contain exact-output and hash-current semantic-tamper cases for Codex, Antigravity, and compact API renderers, plus missing identity, missing timestamp, unsupported identity, and alias-confusion denials. Exact `Generated by` matching is mandatory; aliases, case variants, prefixes, and suffixes are unsupported.

### F3 - P2 - Clean-checkout verification depends on an untracked clause-exact test

Corrected. `platform_tests/scripts/test_check_harness_parity.py` is the durable clean-checkout proof for all acceptance behavior. `platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py` may be run only as supplementary diagnostic evidence while untracked and is neither a target nor a required acceptance gate.

## Cross-Harness Disposition

| Adapter population | Applicability | Required implementation behavior | Required tracked evidence | Waiver |
| --- | --- | --- | --- | --- |
| Codex generated skill adapter | Applicable | Re-render with the exact Codex generator identity and recorded timestamp; exact full-content equality | Exact output PASS; hash-current body tamper STALE | None |
| Antigravity generated skill adapter | Applicable | Re-render with the exact Antigravity generator identity and recorded timestamp; exact full-content equality | Exact output PASS; hash-current body tamper STALE | None |
| Compact API generated skill adapter | Applicable | Parse canonical frontmatter description, re-render with the exact compact API generator identity and recorded timestamp; exact full-content equality | Exact output PASS; hash-current body tamper STALE | None |
| Missing generator identity | Applicable failure case | Fail closed as STALE with specific missing-identity note | Tracked focused regression | None |
| Missing generation timestamp | Applicable failure case | Fail closed as STALE with specific missing-timestamp note | Tracked focused regression | None |
| Unsupported or alias-confused generator identity | Applicable failure case | Fail closed as STALE; do not select a supported renderer by fuzzy matching | Exact alias/case/prefix/suffix rejection regressions | None |
| Other native or pointer surfaces not produced by these three generators | Not applicable to this change | Preserve existing classification and waiver behavior | Existing tracked non-impairment suite | None |

No harness population is silently omitted. This change evaluates generated skill adapter bytes; it does not change harness transport, invocation, routing, installation, permissions, or runtime capability.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_harness_parity.py --all --json",
  "before_behavior": "Hash-current generated adapters can pass despite semantically contradictory body content.",
  "after_behavior": "Codex, Antigravity, and compact API generated adapters pass only when complete content equals deterministic output from the exact declared generator and recorded timestamp.",
  "self_descriptive_naming": "Generator identity, recorded timestamp, expected adapter text, and semantic drift remain explicit checker concepts.",
  "obsolete_guidance_disposition": "No parity guidance is removed; existing path, hash, loadability, waiver, applicability, and population checks remain earlier diagnostics.",
  "history_preservation": "Recorded generation timestamps are reused, generated surfaces are not rewritten, and numbered bridge history remains append-only.",
  "baseline": {
    "tracked_targets": 2,
    "supported_renderer_families": 3,
    "metadata_only_false_green": true,
    "clause_exact_test_authority": "supplementary_only_while_untracked"
  },
  "expected_result": {
    "exact_generator_output": "PASS for Codex, Antigravity, and compact API",
    "hash_current_semantic_tamper": "STALE for Codex, Antigravity, and compact API",
    "incomplete_or_alias_confused_provenance": "STALE",
    "tracked_clean_checkout_suite": "PASS"
  },
  "rollback": {
    "instructions": "Remove only the reviewed renderer selection, exact comparison, and WI-5144 focused tests from the two tracked targets.",
    "test": "python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short"
  },
  "hard_invariants": [
    "no generated adapter, canonical skill, manifest, or registry mutation",
    "no fuzzy or alias generator selection",
    "comparison never consults the current clock",
    "all renderer inputs stay beneath the supplied GT-KB root",
    "existing waiver, applicability, population, and fleet classifications remain enforced"
  ],
  "fail_closed_conditions": [
    "missing generator identity",
    "missing generation timestamp",
    "unsupported or alias-confused generator identity",
    "canonical reconstruction failure",
    "renderer failure",
    "complete content mismatch"
  ],
  "essential_context_preservation": "The tracked suite preserves all existing harness-parity behavior while adding durable semantic equality proof for every applicable generated-adapter family."
}
```

## Proposed Scope Carried Forward

1. Select an authoritative renderer only from exact `Generated by` metadata for Codex, Antigravity, or compact API skill generation.
2. Reconstruct renderer inputs from the already validated canonical source, target surface, source hash, frontmatter where applicable, and recorded `Generated at` value.
3. Compare full current adapter text with deterministic renderer output only after existing existence, loadability, path, and hash checks pass.
4. Return scoped `STALE` outcomes for missing/unsupported provenance, reconstruction failure, renderer failure, or content mismatch without crashing the fleet report.
5. Preserve all existing missing/path/hash/waiver/applicability/population diagnostics and all non-adapter parity behavior.
6. Add every acceptance regression to the tracked focused test target. Do not modify the untracked clause-exact test or any generated surface.

## Scope Changes

No target-path change. The exact upper bound remains:

- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity.py`

The verification scope is clarified: the tracked focused suite is authoritative; the untracked MOD-HP08 clause-exact file is supplementary only.

## In-Root Placement Evidence

All implementation outputs are in-root beneath `E:\GT-KB`. The only source output is `E:\GT-KB\scripts\check_harness_parity.py`; the only tracked test output is `E:\GT-KB\platform_tests\scripts\test_check_harness_parity.py`; and the governed revision is filed under `E:\GT-KB\bridge\`. Fixture and renderer inputs must resolve beneath the supplied project root. No adopter, external repository, harness scratchpad, temporary directory, or out-of-root path is an implementation target or authority source.

## Specification-Derived Verification Plan

| Specification / obligation | Deterministic tracked verification | Required result |
| --- | --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` population completeness and semantic equivalence | Parameterized Codex, Antigravity, and compact API exact-output and semantic-tamper tests in `test_check_harness_parity.py` | All three exact outputs PASS; all three hash-current tampers STALE; no population omitted |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` applicability/disposition/typed failures | Missing identity, missing timestamp, unsupported identity, alias/case/prefix/suffix confusion, reconstruction error, and renderer error cases | Every unsupported or incomplete provenance case is a specific STALE outcome |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` submission-path enforcement | Direct helper/module tests plus checker CLI invocation against fixtures | Loaded-module and direct-CLI paths apply identical exact-render rules |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` MOD-HP08 | Tracked hash-current contradictory-body regressions for all three renderers | Contradictory body cannot PASS |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Full tracked `test_check_harness_parity.py`; read-only live `check_harness_parity.py --all --json` | Existing classifications remain green; live checker performs no mutation |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Exact byte equality and deterministic failure-note assertions | No unsupported, partial, or fuzzy renderer result is accepted |
| Bridge/project/linkage controls | Candidate and live applicability/clause preflights; claim/start packet readback | PASS before implementation and before terminal verification |
| Root isolation | Fixture roots and renderer inputs are asserted beneath the supplied project root | No out-of-root read or write |

Exact implementation verification commands:

- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short`
- `python -m ruff check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py`
- `python -m ruff format --check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py`
- `python scripts/check_harness_parity.py --all --json` - read-only live evidence; any existing unrelated fleet drift remains visible and is not repaired under this scope.
- Optional supplementary diagnostic only: the MOD-HP08 clause-exact case, if its owning file is governed and available. Its absence or untracked status cannot fail this two-file implementation.

## Acceptance Criteria

1. Exact current generator output passes for Codex, Antigravity, and compact API adapters.
2. A hash-current contradictory body is STALE for each of the three adapter families.
3. Missing generator identity, missing timestamp, unsupported identity, alias/case/prefix/suffix confusion, reconstruction failure, and renderer failure each produce a deterministic scoped STALE result.
4. Renderer selection uses exact governed identities and the recorded generation timestamp; it never consults the current clock or fuzzy-matches identities.
5. The tracked focused suite contains all required regressions and passes in a clean checkout without the untracked clause-exact test.
6. Existing path, hash, loadability, waiver, applicability, population, manifest, role, and fleet classifications remain enforced.
7. Only the exact two target files receive implementation changes.

## Pre-Filing Preflight

- Candidate applicability preflight: PASS; packet `sha256:39d3206c8dceaefb4334730ab082b9d04144302604ce22bd61a931cdec2cd3bb`; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.
- Mandatory clause preflight: PASS; five clauses evaluated; four `must_apply`, one `may_apply`; evidence gaps `0`; blocking gaps `0`.
- Live filing must also pass credential, concurrency, project-linkage, and bridge-compliance gates against this exact content.

## Risk And Rollback

Exact comparison can reveal legitimately stale adapters that metadata-only checks missed; that is the intended fail-closed result, and this scope does not regenerate them. Import or renderer failures remain local STALE diagnostics and cannot crash the whole report. Compact API adapters use their authoritative compact renderer rather than canonical-body equivalence.

Rollback removes only the reviewed renderer-selection/comparison logic and WI-5144 focused tests from the two targets, then reruns the tracked focused suite and read-only checker. Generated adapters and registry evidence remain untouched and bridge history remains append-only.

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
