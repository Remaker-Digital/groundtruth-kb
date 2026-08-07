NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T17-03-48Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

bridge_kind: prime_proposal
Document: gtkb-wi5154-superseded-sot-leakage
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5154
Related Work Items: (none)

target_paths: ["scripts/check_superseded_sot_leakage.py", "platform_tests/scripts/test_check_superseded_sot_leakage.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: perf

# Implementation Proposal - Lifecycle-aware current formal-artifact superseded-SOT scanner

## Problem Statement

WI-5154 (P0, backlogged, open) requires extending deterministic stale-string
and currentness evaluation to current MemBase formal-artifact content, while
classifying append-only bridge, deliberation, evidence, and historical
references as history rather than critical active residue. The canonical
implementation authority `DCL-SUPERSEDED-SOT-LEAKAGE-001` v1 defines evaluator
`superseded-sot-leakage`, canonical invocation `gt assert --spec
DCL-SUPERSEDED-SOT-LEAKAGE-001`, and four required outer assertions
`SOT-LEAK-A1`/`A2`/`A3`/`A4`.

The preimplementation baseline intentionally fails all four outer assertions
because `scripts/check_superseded_sot_leakage.py` is not implemented (verified:
target absent from `E:\GT-KB`). TEST-11323 is the acceptance test covering
current formal-artifact scanning, lifecycle-aware historical treatment, guarded
KEEP semantics, deduplicated severity, deterministic remediation, and gate
blocking.

## Proposed Fix

Implement the `superseded-sot-leakage` evaluator as a deterministic, additive
scanner, plus its spec-derived focused test:

1. **Current formal-artifact scanning** (`SOT-LEAK-A1`): scan current MemBase
   formal records and every active worker-loading, generated, CLI-help, skill,
   rule, hook, scaffold, startup, manifest, and runtime surface for superseded
   authority literals and semantically stale current-state claims, with complete
   currentness evidence (subject version/hash, canonical-carrier resolution,
   lifecycle/provenance metadata, evaluator version, execution time).
2. **Lifecycle-aware historical treatment** (`SOT-LEAK-A2`): classify append-only
   bridge, deliberation, report, evidence, archive, and supersession history as
   lifecycle history; do not report it as critical active residue solely for
   preserving an obsolete literal.
3. **Guarded KEEP semantics** (`SOT-LEAK-A3`): retired-registry sentinels and
   active guard references may be `KEEP` only with current enforcement evidence
   and no active-authority effect.
4. **Deduplicated severity + deterministic remediation + gate blocking**
   (`SOT-LEAK-A4`): a stale active GOV/DCL/skill/startup reference produces one
   deduplicated `P0` finding with deterministic remediation and blocks the
   applicable verification, promotion, or closure gate. Duplicate inventory
   paths resolve to one canonical finding and never inflate count or severity.

The scanner is fail-closed: missing, unavailable, stale, contradictory,
unsupported, or incomplete required coverage produces `FAIL`, `PARTIAL`, or
`UNASSESSED`, never `PASS`. It preserves `STRIP`/`KEEP`/`QUARANTINE` semantics
and never performs remediation, cleanup, quarantine, retirement, Git mutation,
or deployment (those remain separately authorized).

## Scope

- Create `scripts/check_superseded_sot_leakage.py` implementing evaluator
  `superseded-sot-leakage` and its four required outer assertions.
- Create `platform_tests/scripts/test_check_superseded_sot_leakage.py`
  providing TEST-11323 coverage: current formal-artifact scanning,
  lifecycle-aware historical treatment, guarded KEEP semantics, deduplicated
  severity, deterministic remediation, and gate blocking.

## Out of Scope

- Any actual `STRIP`/`KEEP`/`QUARANTINE` remediation, cleanup, quarantine, or
  retirement of findings.
- Git mutation, commit, push, history rewrite, dispatcher drain, deployment, or
  release.
- MemBase / database / credential / harness mutation.
- Any change to the DCL, its approval packet, or the acceptance test itself.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-SUPERSEDED-SOT-LEAKAGE-001` v1 fully
specifies the evaluator, outer assertions, disposition semantics, severity, and
gate effects; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
`GOV-SOT-SINGLETON-001`, `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` govern it. No new owner decision is
needed. This proposal only implements the scanner; all non-implementation
actions remain gated by separate authority.

## Specification Links

- DCL-SUPERSEDED-SOT-LEAKAGE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-SOT-SINGLETON-001
- ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001
- DCL-CANONICAL-CARRIER-NONAUTHORITY-001
- DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## In-Root Placement Evidence

Both targets are inside `E:\GT-KB` (root boundary satisfied):
- `scripts/check_superseded_sot_leakage.py`
- `platform_tests/scripts/test_check_superseded_sot_leakage.py`

Both are currently absent and will be created by this proposal.

## Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Outer assertion A1 (current scanning) | TEST-11323 assertion | Complete currentness evidence, no false `PASS` on missing/stale coverage |
| Outer assertion A2 (historical treatment) | TEST-11323 assertion | Historical fixtures non-operative without critical false positives |
| Outer assertion A3 (guarded KEEP) | TEST-11323 assertion | KEEP only with current enforcement evidence, no active-authority effect |
| Outer assertion A4 (dedup + gate block) | TEST-11323 assertion | One deduplicated P0 finding, deterministic remediation, gate blocked |
| Canonical invocation | `gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001` | All four assertions pass after implementation |
| Regression | `python -m pytest platform_tests/scripts/test_check_superseded_sot_leakage.py -q --tb=short` | All tests pass |
| Static quality | `python -m ruff check scripts/check_superseded_sot_leakage.py platform_tests/scripts/test_check_superseded_sot_leakage.py` and `python -m ruff format --check ...` | Clean |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DCL-SUPERSEDED-SOT-LEAKAGE-001 v1; WI-5154; TEST-11323; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE",
  "canonical_authority": "MemBase versioned formal records, Deliberation Archive owner decisions, and numbered bridge artifacts",
  "primary_route": "gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001 plus pytest",
  "before_behavior": "Preimplementation baseline fails all four outer assertions because scripts/check_superseded_sot_leakage.py is absent.",
  "after_behavior": "The superseded-SOT scanner deterministically scans current formal artifacts with lifecycle-aware history, guarded KEEP, deduplicated severity, deterministic remediation, and gate blocking; all four outer assertions pass.",
  "self_descriptive_naming": "Evaluator id superseded-sot-leakage; assertion ids SOT-LEAK-A1..A4.",
  "obsolete_guidance_disposition": "None introduced; the DCL remains the governing authority.",
  "history_preservation": "Additive scanner only; no formal record, terminal stage, or prior bridge version is rewritten.",
  "essential_context_preservation": "All current formal records, terminal stages, append-only bridge/deliberation/evidence history, STRIP/KEEP/QUARANTINE disposition semantics, and all active worker-loading/runtime surfaces are preserved unchanged.",
  "expected_result": {
    "scanner": "scripts/check_superseded_sot_leakage.py present and deterministic, all four SOT-LEAK assertions pass",
    "test": "platform_tests/scripts/test_check_superseded_sot_leakage.py present and passing (TEST-11323 coverage)",
    "wi_5154": "open until independent VERIFIED finalization"
  },
  "hard_invariants": [
    "fail-closed on missing/stale/contradictory/unsupported/incomplete required coverage",
    "historical references never reported as critical active residue solely for preserving an obsolete literal",
    "guarded KEEP only with current enforcement evidence and no active-authority effect",
    "duplicate inventory paths resolve to one canonical finding",
    "no remediation, cleanup, quarantine, retirement, Git, MemBase, credential, or deployment mutation",
    "only the two declared target paths are implementation scope"
  ],
  "fail_closed_conditions": [
    "missing, unavailable, stale, contradictory, unsupported, or incomplete required coverage",
    "scanner absent or non-deterministic",
    "an active PAUTH, GO, claim, or start authority is absent at implementation time",
    "a fourth path enters scope"
  ],
  "baseline": {
    "wi_5154": "backlogged/open",
    "outer_assertions": "SOT-LEAK-A1/A2/A3/A4 all failing (scanner absent)"
  },
  "expected_interim": {
    "wi_5154": "open; scanner implemented under bridge GO + claim + implementation-start",
    "outer_assertions": "SOT-LEAK-A1/A2/A3/A4 passing under TEST-11323"
  },
  "expected_terminal": {
    "wi_5154": "resolved after independent VERIFIED finalization"
  },
  "rollback": {
    "instructions": "Append a reviewed corrective version; never restore or replace groundtruth.db.",
    "verification": "Repeat separate-process canonical reads and hashes."
  }
}
```

## Prior Deliberations

_No prior deliberations: <fill in reason before filing>._ Candidate seeds from
DCL provenance: DELIB-20260710-GTKB-MODERNIZATION-SUPERSEDED-SOT-LEAKAGE-DCL-APPROVAL;
DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Prerequisites and Implementation-Start Gate (Note)

This proposal is filed as a draft under the covering project-scope PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
(active, project-scoped, list-free, allows source/test mutation). No
implementation may begin until all of the following exist and are verified
independently: (a) an applicable bounded PAUTH covering WI-5154's exact target
paths, (b) an independent bridge **GO** on this proposal, (c) exact declared
target paths matching work intent, (d) a matching work-intent claim, and (e)
successful schema-v3 implementation-start authorization evidence. Cleanup,
quarantine, retirement, Git mutation, drain, and deployment remain out of scope
and require separate applicable authority.

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will acquire a matching claim, pass implementation-start, implement the scanner
and TEST-11323 coverage, run the spec-derived verification, and file an
implementation report requesting VERIFIED.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
