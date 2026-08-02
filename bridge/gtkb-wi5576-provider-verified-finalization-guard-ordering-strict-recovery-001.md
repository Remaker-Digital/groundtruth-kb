NEW
::init gtkb pb
::open build

# WI-5576 Provider VERIFIED Finalization Guard Ordering — Strict-Recovery Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5576-provider-verified-finalization-guard-ordering-strict-recovery
Version: 001
Date: 2026-08-01 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

Strict-Recovery Source Chain: bridge/gtkb-wi5576-provider-verified-finalization-guard-ordering-001.md through bridge/gtkb-wi5576-provider-verified-finalization-guard-ordering-007.md
Invalid Historical Preimage: bridge/gtkb-wi5576-provider-verified-finalization-guard-ordering-002.md (WRONG_RESPONDS_TO_LINK)
Depends On: bridge/gtkb-wi5501-concurrent-verified-finalization-strict-recovery-001.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5576
Related Work Items: WI-5501, WI-5806

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch"]

Recommended commit type: fix
implementation_scope: source_test_and_patch_carrier
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
draft_only: true

## Strict-Recovery Basis

This proposal starts a fresh parse-clean chain. The historical `001` through
`007` chain remains immutable append-only evidence and will not be rewritten or
continued. Historical v002 records a decorated predecessor rather than the exact
predecessor path, producing `WRONG_RESPONDS_TO_LINK` under the strict lifecycle
resolver. The old v004 design and v005 GO are evidence only and do not authorize
this new chain. No v008 publication is requested.

## Claim

`scripts/gtkb_bridge_writer.py` runs the complete provider guard set before the
VERIFIED branch and before the canonical finalizer. Its pre-finalizer compliance
guard therefore rejects missing Commit Finalization Evidence that the finalizer
is responsible for creating. Repair only this guard timing: provider VERIFIED
runs scanner-safe credential validation before finalization; the unchanged
canonical finalizer creates deterministic evidence; its evidence-complete
`write_bridge_file` path runs full compliance before write and commit. GO and
NO-GO retain the existing two-guard pre-write path. This is writer ordering,
not dispatcher or capability routing.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement and no new
owner decision is needed before implementation.

## Project Authority

The Goose Harness Adoption project is active and reactivated, WI-5576 is an open
P0 project member, and the list-free project PAUTH above is active without expiry.
It covers bridge, metadata, source, test, configuration, documentation,
runtime-state, and governance-evidence classes. Project-level authorization is
controlling, so the legacy WI-level approval field does not require an AUQ.

Implementation remains gated by independent GO, an exact fresh-slug claim,
schema-v3 start evidence, operation-time PAUTH evaluation, independent VERIFIED,
and the separately governed Git-finalization boundary.

## Defect Evidence And Corrected Target Cohort

- The provider writer currently evaluates the full guard list before it branches
  into VERIFIED finalization, while the evidence-complete audit chokepoint is in
  `write_bridge_file` after deterministic finalization.
- The historical atomicity test still imports retired `skills/verify/...` helper
  paths and demands three-way helper byte parity. The canonical live helpers are
  `.claude/skills/gtkb-verify/helpers/write_verdict.py` and
  `.codex/skills/gtkb-verify/helpers/write_verdict.py`.
- `.cursor/skills/gtkb-verify/helpers/write_verdict.py` is absent by design: the
  Cursor capability-registry entry is typed `fallback`. This proposal will not
  create a Cursor helper or assert direct three-way byte parity.
- The patch carrier is absent at proposal time. Hash and cleanliness evidence is
  observational only and must be re-read immediately before any claim/start.

## Dependency And Shared-Target Serialization

WI-5501 strict recovery currently owns both helper paths and the shared
atomicity test. WI-5576 must not claim, start, or edit the shared test until
WI-5501 is terminal, all relevant target ownership is released, no live claim or
start packet covers the cohort, and the canonical/Codex import baseline is
executable. WI-5576 never targets either helper and does not absorb WI-5501's
concurrency or real-index transaction work.

After WI-5501 terminates, re-observe helper/test identities, target cleanliness,
claims, and patch-carrier absence. If WI-5501 is rejected or withdrawn without
restoring the baseline, fail closed and revise this proposal rather than silently
adopting its scope.

## Proposed Scope

1. Add a bounded status-specific provider-guard selection in the writer.
2. For VERIFIED, run scanner-safe credential validation before the finalizer;
   do not run bridge compliance on incomplete pre-finalization bytes.
3. Leave the canonical finalizer and `write_bridge_file` as the sole evidence
   builder and evidence-complete compliance chokepoint.
4. For GO and NO-GO, preserve both configured pre-write guards unchanged.
5. Preserve status/body, transition, role, provenance, self-review, exact claim,
   include-path, hunk-coverage, fabricated-evidence, rollback, commit, and
   claim-release checks.
6. Once WI-5501 releases the shared test, add only the focused real-compliance
   ordering regressions there and create the exact declared patch carrier.
7. Do not add or change a hard-coded timeout, retry, backoff, threshold,
   throttle, fan-out, or concurrency literal, and do not add a one-off
   environment read. Centralized typed timer/concurrency authority belongs to
   WI-5806 and `DELIB-202667748`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — preserves provider publication semantics without dispatcher activation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent verdicts and exact bridge lifecycle/claim gates.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project PAUTH controls implementation authority.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the exact target cohort stays inside the active envelope.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — PAUTH must be re-evaluated before mutation.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` — the list-free project envelope is not narrowed by legacy WI approval state.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, and WI linkage are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all applicable requirements are cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification maps governing clauses to executed results.
- `GOV-WORK-TREE-HYGIENE-001` — unrelated worktree and index bytes remain untouched.
- `GOV-ENV-LOCAL-AUTHORITY-001` — timer/concurrency settings remain centralized and are not duplicated here.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — A/D/F topology and F capability are preserved.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — canonical/Codex helper evidence is distinct from typed Cursor fallback.
- `ADR-CROSS-HARNESS-PARITY-001` — active helper parity is preserved within declared scope.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — absent fallback projections are not fabricated.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifacts remain inside the GT-KB root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect, dependency, and future timer work remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — proposal, implementation, tests, and verification stay linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — old invalid history and fresh candidate state remain explicit.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — exact targets and patch carrier make the change independently evaluable.
- `SPEC-AUQ-POLICY-ENGINE-001` — active project authorization means no owner AUQ is needed here.
- `GOV-STANDING-BACKLOG-001` — timer/concurrency work remains with its existing owner rather than duplicated.

## Specification-Derived Verification Plan

| Obligation | Test / evidence | Required result |
|---|---|---|
| Evidence-complete VERIFIED compliance | Valid provider VERIFIED missing only pre-authored Commit Finalization Evidence | Credential scan runs first; finalizer adds deterministic evidence; full real compliance passes on final bytes; exact-path verdict/commit succeeds; claim releases once. |
| Fail closed on incomplete applicability | VERIFIED candidate lacking a clean Applicability Preflight | Evidence-complete compliance denies before write/commit and the claim remains held. |
| Preserve GO/NO-GO | Instrument provider guards for both statuses | Both configured pre-write guards still run. |
| Preserve negative controls | Invalid status/body, unsafe include, missing hunk coverage, fabricated evidence, self-review, finalization failure, and commit failure | Existing denials remain fail closed. |
| Harness disposition | Inspect canonical, Codex, and Cursor capability records | Canonical/Codex baseline is executable; Cursor remains typed fallback with no fabricated helper. |
| Lifecycle and authority | Candidate/live applicability, clause gate, exact claim/start, operation-time PAUTH | Every gate passes against final bytes and exact targets. |

After WI-5501 is terminal and the baseline is re-observed, run the focused
`test_lo_verified_commit_atomicity.py`, `test_gtkb_bridge_writer.py`,
`test_codex_bridge_compliance_gate.py`, and adjacent status-consistency tests
selected by the diff. Run Ruff check and format-check on changed Python,
`py_compile` on the writer, patch hash/size plus forward/reverse apply,
`git diff --check`, and candidate/live applicability and clause preflights.
Map every linked specification to an actual result in the report.

Preserve `TEST-11623` as the end-to-end acceptance obligation. Do not activate
dispatcher/TAFE for this repair. Use deterministic direct-provider integration;
run a genuine F acceptance only under a later separately authorized non-repair
exercise, and never claim TEST-11623 executed unless those conditions ran.

## Acceptance Criteria

1. A valid provider VERIFIED candidate no longer fails merely because finalizer-
   generated evidence was absent from pre-finalization bytes.
2. The final bytes still pass the real compliance gate before write/commit.
3. GO and NO-GO behavior is unchanged.
4. WI-5501 serialization and typed Cursor fallback are enforced.
5. Exact negative controls, lifecycle, PAUTH, claim, patch, and Git boundaries pass.
6. No dispatcher/TAFE activation or timer/concurrency literal is introduced.

## Hard Implementation-Start Gates

- Fresh independent GO on this exact new chain.
- Exact fresh-slug `go_implementation` claim and schema-v3 start packet.
- Active project and PAUTH still cover the exact three targets.
- WI-5501 target ownership is released and the executable baseline is reobserved.
- Exact targets are clean; patch carrier is absent and unowned.
- Operation-time authorization passes before each mutation.
- Centralized typed timer/concurrency authority remains resolvable.
- Separate Git-finalization authority exists before any commit.

Any failure stops without edits, staging, commit, or dispatcher/TAFE mutation.

## Nonimpairment And Boundary

No dispatcher/TAFE configuration or activation; provider-harness, role, lease,
eligibility, routing, cap, allowance, credential, external-system, cleanup,
push, deployment, release, or Agent Red mutation. Preserve A/D/F topology, F
dispatchability, full allowances, append-only bridge history, and unrelated
worktree/index bytes. Do not mutate either canonical/Codex helper and do not
create a Cursor projection.

This proposal performs no KB mutation and no MemBase write. Any unrelated
authoritative-state change mentioned in concurrency verification is test input,
not an implementation target or production mutation performed by this WI.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5576; historical versions 001-007; WI-5501 strict recovery; DELIB-202666274; DELIB-202667749; DELIB-202667748",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; active Goose project PAUTH v2; canonical VERIFIED finalizer; typed harness capability registry",
  "primary_route": "Serialize behind WI-5501, then move only the provider VERIFIED compliance guard to the evidence-complete post-finalization chokepoint while leaving GO and NO-GO unchanged.",
  "before_behavior": "Provider VERIFIED runs full bridge compliance before deterministic finalization creates Commit Finalization Evidence and can enter a denial loop.",
  "after_behavior": "Provider VERIFIED runs credential safety before finalization and full compliance on final bytes before write and commit; GO and NO-GO retain both pre-write guards.",
  "baseline": {
    "writer_git_blob": "2be05e971f742366d83514b86a448661ba9a06d5",
    "atomicity_test_git_blob": "30716be5eddaa263e372f3dcb767e8bd61a150d6",
    "patch_carrier": "absent",
    "shared_dependency": "WI-5501 strict recovery is current NEW and both exact claims were null at proposal preflight"
  },
  "self_descriptive_naming": "provider VERIFIED finalization guard ordering names the affected route, status, phase, and defect.",
  "history_preservation": "The malformed historical 001-007 chain remains immutable evidence; this fresh chain has independent GO, claim, start, report, and verdict state.",
  "obsolete_guidance_disposition": "Retired skills/verify imports and three-way Cursor byte-parity expectations are replaced by canonical/Codex evidence plus typed Cursor fallback after WI-5501 restores the baseline.",
  "configuration_authority": "No local timeout, retry, threshold, throttle, fan-out, or concurrency literal is added; centralized typed authority remains with WI-5806 and DELIB-202667748.",
  "essential_context_preservation": "Preserve the finalizer chokepoint, exact claim and schema-v3 start, operation-time PAUTH, WI-5501 serialization, typed Cursor fallback, negative controls, append-only history, and dispatcher/TAFE no-touch boundary.",
  "expected_result": "A valid evidence-incomplete provider VERIFIED candidate reaches deterministic finalization and passes the real gate on final bytes without weakening any existing denial.",
  "hard_invariants": [
    "No helper or Cursor projection is mutated.",
    "GO and NO-GO retain both configured pre-write guards.",
    "Final VERIFIED bytes pass real compliance before write and commit.",
    "No dispatcher, TAFE, timer, routing, credential, or unrelated worktree state changes."
  ],
  "fail_closed_conditions": [
    "WI-5501 shared-target ownership is not terminally released.",
    "Project PAUTH, exact claim, schema-v3 start, target cleanliness, or patch ownership is stale.",
    "The executable canonical/Codex baseline or typed Cursor fallback cannot be proven.",
    "Any focused negative control, applicability gate, clause gate, or exact-scope check fails."
  ],
  "rollback": "Governedly revert only the reviewed writer/test patch after reverse-applicability verification; preserve both bridge chains and all peer commits."
}
```

## Risks / Rollback

The main risks are accidental compliance bypass and collision with WI-5501 on
the shared test. Mitigate with the real-compliance missing-preflight regression,
the unchanged finalizer chokepoint, exact serialization, and patch isolation.
Rollback is limited to the reviewed writer/test patch; append-only bridge history
and peer commits are never rolled back.

## Prior Deliberations

- `DELIB-202667299` — historical old-chain v005 GO; evidence only.
- `DELIB-20265334` — atomic VERIFIED finalization requirement.
- `DELIB-202666183` — provider denial-loop evidence.
- `DELIB-202667748` — timer/concurrency SoT direction.
- `bridge/gtkb-wi5501-concurrent-verified-finalization-strict-recovery-001.md` — current serialization dependency.

## Owner Decisions / Input

- `DELIB-202666274` — owner-approved Goose project PAUTH; the active list-free
  project envelope governs WI-5576 implementation scope.
- `DELIB-202667749` — owner-approved Goose project reactivation; the project is
  active again and its member WIs inherit project implementation approval.

No new owner input or AUQ is required.

## Requested Loyal Opposition Action

Review this as a new independent chain. GO only if old-chain preservation,
WI-5501 serialization, exact three-target scope, evidence-complete compliance,
typed Cursor fallback, timer boundary, verification plan, and nonimpairment are
sufficient; otherwise return NO-GO with concrete corrections.

## Pre-Filing Preflight

Before filing, run candidate applicability and mandatory clause preflights on
this exact content, strict lifecycle resolution, inline-JSON parsing, project and
PAUTH readback, phantom-spec checks, target/claim/start inventory, and target
cleanliness checks. Record only fresh results; do not copy old-chain preflight
claims.
