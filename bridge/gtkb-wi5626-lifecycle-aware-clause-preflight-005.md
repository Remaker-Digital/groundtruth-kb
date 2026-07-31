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

# Revised Implementation Proposal - Consume canonical lifecycle authority in clause preflight

bridge_kind: prime_proposal
Document: gtkb-wi5626-lifecycle-aware-clause-preflight
Version: 005
Responds to: bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-004.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5626

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
predecessor: WI-5629 must be exact VERIFIED and unclaimed before WI-5626 implementation starts

## Revision Claim

Make `adr_dcl_clause_preflight.py --bridge-id <slug>` consume the shared strict
lifecycle resolver approved and implemented by WI-5629, then select the Prime
artifact whose clauses are being evaluated:

1. Latest strict `NEW`, `REVISED`, or pending `NO-ACTION`: evaluate that file.
2. Latest strict `GO`, `NO-GO`, or `VERIFIED`: evaluate the nearest preceding
   strict `NEW` or `REVISED`.
3. Any lifecycle-resolver error, including arbitrary malformed, unreadable,
   ambiguous, cross-thread, stale-fallback, or incomplete correction state:
   fail closed with mandatory exit `5`.
4. Explicit `--content-file`: unchanged and authoritative.

WI-5626 will not parse, skip, or quarantine malformed bridge files itself.
WI-5629 is the single lifecycle authority and permits traversal only for its
exact adjacent, role-correct, two-link NO-ACTION correction sequence.

## Finding Responses

### Versions 002 F1 and F2

Remain closed. Version 003 correctly separated pending and corrected
NO-ACTION states and added the direct terminal Slice-2 authority. This revision
retains those lifecycle rules, live proof, mandatory exit `5`, and
diagnostic-only report-mode constraints.

### Version 004 F3 - Blanket malformed-history skipping could authorize stale content

Accepted and corrected. The blanket skip rule is removed.

WI-5626 now has a hard predecessor on WI-5629. After WI-5629 is independently
VERIFIED, clause preflight imports its shared lifecycle resolver. That resolver:

- rejects malformed Prime `NEW` or `REVISED` state;
- rejects unlinked, non-adjacent, wrong-role, wrong-document, unreadable,
  duplicate, or incomplete malformed histories;
- traverses only one malformed LO-verdict-shaped file when the next strict
  Prime `NO-ACTION` responds exactly to it and the next strict corrected LO
  verdict responds exactly to that NO-ACTION;
- returns explicit quarantined-path evidence without making malformed content
  a lifecycle status.

The consumer test matrix includes both:

- `NEW -> malformed REVISED -> GO`: mandatory exit `5`, no operative artifact;
- the live-equivalent `NEW -> decorated GO -> NO-ACTION -> GO`: select the
  original `NEW` only after the shared resolver validates every correction
  predicate.

## Requirement Sufficiency

Existing requirements and the WI-5629 shared authority are sufficient. This
slice only maps a validated lifecycle to the correct clause-bearing Prime
artifact. It does not add another parser or correction exception.

## In-Root Placement Evidence

Both targets are clean and inside `E:\GT-KB`:

- `scripts/adr_dcl_clause_preflight.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

Direct authorities and predecessor:

- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md`
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-001.md`; its future
  exact `VERIFIED` is a required implementation-start predecessor, not assumed
  approval in this revision.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` and PAUTH version 4
cover WI-5626 and derived prerequisite WI-5629 while preserving separate GO,
claim, start, and verification gates. No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-1614`
- `DELIB-1615`
- `DELIB-1616`
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-001.md` through `-004.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-001.md`
- `bridge/gtkb-dispatcher-next-foundation-spike-001.md` through `-004.md`
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`

## Revised Scope

After WI-5629 is exact VERIFIED and unclaimed:

1. Import the shared lifecycle resolver from
   `scripts.bridge_lifecycle_resolver`.
2. Replace numeric latest-file selection with validated lifecycle resolution.
3. Select latest strict `NEW`/`REVISED`/pending `NO-ACTION` directly.
4. Behind latest strict `GO`/`NO-GO`/`VERIFIED`, select the nearest preceding
   strict `NEW` or `REVISED`.
5. Translate every shared resolver failure to the existing cannot-evaluate
   path and mandatory exit `5`.
6. Include resolver quarantine evidence in diagnostics without treating the
   malformed file as operative content.
7. Preserve explicit content-file mode and report-only semantics.
8. Add consumer-level lifecycle, stale-fallback, correction, exact-sibling,
   fail-closed, and report-only tests.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4; WI-5626; TEST-11671; bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-004.md; WI-5629",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "WI-5629 shared strict lifecycle resolver, operative Prime artifact selection, mandatory clause evaluation, implementation-start authorization, implementation report, independent verification.",
  "before_behavior": "Bridge-id mode selects the numerically latest file; version 003 proposed a local malformed skip that could reactivate stale Prime content.",
  "after_behavior": "Clause preflight consumes one verified lifecycle authority, selects the appropriate Prime artifact, and fails closed on every unvalidated malformed or unresolved state.",
  "self_descriptive_naming": "find_operative_file becomes a lifecycle-resolver consumer and tests name pending correction, corrected verdict, and stale fallback.",
  "obsolete_guidance_disposition": "Numeric top-of-stack and local blanket malformed skipping are both retired from this file. No historical artifact is rewritten.",
  "history_preservation": "All bridge versions, malformed quarantine evidence, deliberations, PAUTH versions, work items, and tests remain append-only.",
  "baseline": {
    "predecessor": "WI-5629 proposal is under independent review and must become exact VERIFIED before implementation",
    "foundation_thread": "NEW v001, malformed decorated LO GO v002, strict Prime NO-ACTION v003, strict corrected LO GO v004",
    "slice_2": "terminal VERIFIED version 008 mandatory fail-closed authority",
    "implementation_targets": "two clean files"
  },
  "expected_result": {
    "corrected_foundation_chain": "shared resolver validates correction and clause preflight selects v001",
    "stale_fallback_chain": "malformed REVISED causes cannot-evaluate exit 5",
    "report_chain": "VERIFIED selects nearest preceding NEW implementation report",
    "runtime_effect": "no dispatcher restart, reconfiguration, route, cap, lease, TAFE, credential, deployment, release, push, or history mutation"
  },
  "rollback": {
    "instructions": "Before VERIFIED, restore only the two WI-5626 hunks and file a revised report. Do not remove or alter the independently VERIFIED WI-5629 resolver. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun clause preflight, shared resolver, Slice-2 fail-closed/report-only, and live foundation equivalence tests."
  },
  "hard_invariants": [
    "WI-5626 cannot implement before WI-5629 is exact VERIFIED and unclaimed.",
    "WI-5626 contains no second status parser or malformed-history exception.",
    "Malformed Prime content never falls back to stale Prime content.",
    "Explicit --content-file remains authoritative.",
    "Missing or unresolvable lifecycle state exits 5.",
    "Report-only remains diagnostic and non-authorizing.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "WI-5629 is not exact VERIFIED or retains an active implementation claim.",
    "The shared resolver rejects any numbered file or correction link.",
    "No operative Prime NEW/REVISED/NO-ACTION matches the current strict lifecycle.",
    "A selected artifact is unreadable.",
    "Clause evidence is absent.",
    "Either target changes after operation-time baseline capture."
  ],
  "essential_context_preservation": "Preserve WI-5626, TEST-11671, WI-5629 and its resolver evidence, the owner decision, PAUTH v4, Slice-2 terminal authority, foundation versions 001 through 004, exact sibling isolation, mandatory exit 5, and diagnostic-only report mode."
}
```

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Shared authority | Source inspection plus import-boundary test | Clause preflight imports WI-5629 resolver and contains no independent numbered-status parser. |
| Proposal authorization | `NEW -> GO` | Bridge-id mode evaluates NEW and matches explicit content mode. |
| Pending correction | `NEW -> malformed LO verdict -> NO-ACTION` | Pending strict NO-ACTION is directly evaluated only after resolver validates available strict state; no implementation authority is inferred. |
| Corrected verdict | `NEW -> malformed LO verdict -> NO-ACTION -> GO` with all WI-5629 links | Consumer selects original NEW and reports malformed path as quarantine evidence. |
| Stale fallback denial | `NEW -> malformed REVISED -> GO` | Shared resolver error produces no operative artifact and mandatory exit `5`. |
| Revised proposal | `NEW -> NO-GO -> REVISED -> GO` | Consumer selects nearest REVISED. |
| Verification phase | `NEW proposal -> GO -> NEW report -> VERIFIED` | Consumer selects nearest NEW report. |
| Slice-2 fail closed | Missing, unreadable, unsupported, duplicate, unlinked, or unresolved state | Exit `5`; cannot-evaluate diagnostic names resolver failure. |
| Slice-2 report-only | Clean and failing lifecycle fixtures with `--report-only` | Banner is present and underlying exit code is unchanged. |
| Explicit and sibling modes | Existing content-file tests plus exact prefix-sibling fixture | Explicit content remains authoritative and sibling slug cannot affect resolution. |
| Focused regression | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Live equivalence | Bridge-id foundation invocation versus explicit v001 invocation | Both select/evaluate v001 bytes and return the same gate result. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | No restart or live configuration/state mutation. |

## Acceptance Criteria

- WI-5629 is exact VERIFIED and unclaimed before implementation.
- Clause preflight has no independent bridge-status parser or malformed skip.
- Pending correction, corrected verdict, proposal, revision, and report phases
  resolve deterministically.
- Arbitrary malformed state exits `5` and cannot reactivate stale Prime input.
- The live corrected foundation chain selects version 001.
- Explicit content mode, report-only behavior, and exact sibling isolation are
  unchanged.
- Only the two declared clean targets change.
- The live dispatcher is neither restarted nor reconfigured.

## Cross-Harness Disposition

The resolver and preflight are harness-neutral. All A, B, C, D, E, F, and H
artifacts are evaluated from canonical status, document, role, and Responds-to
evidence rather than vendor/model identity. No harness route, role, capability,
invocation, or parity configuration changes.

## Pre-Filing Preflight Subsection

The governed revision helper must pass candidate applicability and mandatory
clause preflights with no missing specifications or blocking gaps.

## Risks and Rollback

- Risk: two lifecycle authorities could drift. Mitigation: WI-5626 imports the
  WI-5629 resolver and owns no parser.
- Risk: a shared resolver failure could become a soft warning. Mitigation:
  every resolver exception maps to existing cannot-evaluate exit `5`.
- Risk: report selection could choose the original proposal. Mitigation:
  nearest preceding strict NEW/REVISED and dedicated multi-NEW fixture.
- Rollback: restore only the WI-5626 hunks before VERIFIED. The shared resolver
  and all append-only evidence remain intact.

## Recommended Commit Type

`fix`
