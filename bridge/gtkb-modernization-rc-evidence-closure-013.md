REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; owner-authorized WI-5165 historical-evidence closure correction

# Revised Implementation Proposal - WI-5165 Historical-Evidence Closure Correction

bridge_kind: prime_proposal
Document: gtkb-modernization-rc-evidence-closure
Version: 013
Responds to: bridge/gtkb-modernization-rc-evidence-closure-012.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5165

target_paths: ["scripts/collect_modernization_semantic_evidence.py", "bridge/gtkb-modernization-rc-evidence-closure-015.md"]

implementation_scope: source_format_and_canonical_bridge_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses all three P1 findings in version 012 under the owner's exact historical-evidence closure authorization. Collector invocation `20260715163526-76461cb465c3` is historical evidence bound to committed HEAD `0a8877c8fe21b017c5c3d2f6df0dbd4734ab375b`; it is not current receipt-validity evidence and will never be represented as current after a later commit. The current collector status remains honestly `BLOCKED=12 INVALID=14` at HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`.

After a fresh independent GO, Prime Builder proposes only:

1. Ruff-format `scripts/collect_modernization_semantic_evidence.py` while preserving its normalized Python AST exactly.
2. File canonical numbered implementation report `bridge/gtkb-modernization-rc-evidence-closure-015.md` as the sole durable carrier for the historical invocation's receipt hashes, counts, original binding, current-invalid distinction, verification commands, and residual blockers.
3. Leave terminal review and the exact complete-chain local commit to independent Loyal Opposition through `write_verdict.py --finalize-verified` at version 016.

No collector run, receipt mutation, modernization status promotion, or program closure is proposed.

## Requirement Sufficiency

Existing modernization, project-authorization, bridge, non-impairment, Git-binding, artifact-evaluability, and specification-derived-verification requirements are sufficient when combined with `DELIB-20260715-WI5165-HISTORICAL-EVIDENCE-CLOSURE-CORRECTION-AUTHORIZATION` and PAUTH version 3. The owner authorization resolves the authority choice requested by version 012 without waiving current-validity rules or any modernization acceptance requirement.

## Owner Decisions / Input

- `DELIB-20260715-WI5165-HISTORICAL-EVIDENCE-CLOSURE-CORRECTION-AUTHORIZATION` - Mike authorized historical-only classification of invocation `20260715163526-76461cb465c3`, canonical numbered-report evidence, and exact complete-chain local VERIFIED finalization while all modernization blockers remain open.
- Owner reply in Codex task `019f6610-1bc5-7781-88bf-900dccbc6010`: `AUTHORIZE WI-5165 HISTORICAL-EVIDENCE CLOSURE CORRECTION`.
- PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715` version 3, rowid 710 - operation-time authority implementing that bounded decision.

## Findings Addressed

### F1 - P1 - The claimed collected baseline is currently false and finalization would invalidate it again

Corrected. This revision makes no current-validity claim for the prior invocation. The canonical report must state both observations without conflation:

- historical observation at original HEAD `0a8877c8fe21b017c5c3d2f6df0dbd4734ab375b`: 13 receipts were collected by invocation `20260715163526-76461cb465c3`;
- current validation at HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`: `BLOCKED=12 INVALID=14`, with zero current collected receipts because the historical records are HEAD-bound and some session-envelope bindings have changed.

The finalizer commit may advance HEAD without creating a paradox because historical receipt validity is not an acceptance criterion. Current collector status is expected to remain non-passing after finalization. The implementation report will preserve the historical files' hashes and provenance only; it will not use them to satisfy current RC closure.

### F2 - P1 - The owner-authorized four-file finalizer cannot pass the canonical predecessor-chain gate

Corrected by the new owner decision and PAUTH version 3. The one authorized local finalizer transaction contains exactly 17 paths:

```json
[
  "scripts/collect_modernization_semantic_evidence.py",
  "bridge/gtkb-modernization-rc-evidence-closure-001.md",
  "bridge/gtkb-modernization-rc-evidence-closure-002.md",
  "bridge/gtkb-modernization-rc-evidence-closure-003.md",
  "bridge/gtkb-modernization-rc-evidence-closure-004.md",
  "bridge/gtkb-modernization-rc-evidence-closure-005.md",
  "bridge/gtkb-modernization-rc-evidence-closure-006.md",
  "bridge/gtkb-modernization-rc-evidence-closure-007.md",
  "bridge/gtkb-modernization-rc-evidence-closure-008.md",
  "bridge/gtkb-modernization-rc-evidence-closure-009.md",
  "bridge/gtkb-modernization-rc-evidence-closure-010.md",
  "bridge/gtkb-modernization-rc-evidence-closure-011.md",
  "bridge/gtkb-modernization-rc-evidence-closure-012.md",
  "bridge/gtkb-modernization-rc-evidence-closure-013.md",
  "bridge/gtkb-modernization-rc-evidence-closure-014.md",
  "bridge/gtkb-modernization-rc-evidence-closure-015.md",
  "bridge/gtkb-modernization-rc-evidence-closure-016.md"
]
```

Versions 001 through 015 are explicit predecessor/helper include paths; version 016 is created by independent Loyal Opposition through the atomic finalizer. Any different version sequence, missing predecessor, extra staged path, different source path, or helper failure invalidates this manifest and fails closed. Prime Builder will not author version 014 or 016 and will not create the commit.

### F3 - P1 - CODEX-INSIGHT-DROPBOX cannot be the durable canonical evidence carrier

Corrected. The dropbox path is removed from `target_paths`, the proposed operation, acceptance criteria, and finalizer manifest. Canonical numbered implementation report `bridge/gtkb-modernization-rc-evidence-closure-015.md` is the sole durable carrier. It must embed the complete 13-receipt hash table, invocation and focused-test counts, original HEAD/scope/session binding, present invalidity reasons, exact commands and results, and all residual blockers.

## Scope Changes

- Removed `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MODERNIZATION-RC-EVIDENCE-CLOSURE-2026-07-15.md` from implementation and finalization scope.
- Added the exact future canonical implementation report `bridge/gtkb-modernization-rc-evidence-closure-015.md` as the durable evidence target.
- Expanded the authorized finalizer transaction from the impossible four-path set to the exact complete numbered chain `001` through `016` plus the collector source.
- Reclassified the prior collector invocation from proposed current evidence to historical evidence only.
- Preserved the format-only source correction, no-rerun rule, no-receipt-mutation rule, and all modernization blockers.

## Proposed Operation

1. Require latest status GO at version 014, exact approval of this version 013, a matching Prime Builder work-intent claim, PAUTH version 3, and an implementation-start packet admitting exactly the two declared `target_paths`.
2. Re-read the current collector status. Require the expected non-passing `BLOCKED=12 INVALID=14` state and record it as current state, not as an implementation failure.
3. Record pre-format source SHA-256 `758ad51bf999f80cf145b822606b8e8a4baf96916138b9d567fc72812223d7cf` and normalized AST SHA-256 `58bd75c2a77e990c20bced152e2fd894a162b96b2d98c3d3bab3dd25055563e8`; fail closed if either changes before implementation start.
4. Run Ruff formatter once on `scripts/collect_modernization_semantic_evidence.py` and require the normalized AST digest to remain identical.
5. Read, hash, count, and summarize the existing invocation and verification outputs without mutating them. Do not run collector `all`.
6. Run the complete specification-derived verification matrix below.
7. File version 015 through the governed implementation-report helper with complete embedded evidence and the exact 17-path finalizer manifest.
8. Leave terminal verification and commit creation to an independent Loyal Opposition session using `write_verdict.py --finalize-verified` at version 016.

## Hard Invariants And Exclusions

- No collector `all` run and no new receipt issuance.
- No deletion, rewrite, copy-forward, backdating, status promotion, or validity reinterpretation of any existing receipt, measurement, issuance, command-run, or focused-test output.
- No semantic source change; normalized AST digest must remain `58bd75c2a77e990c20bced152e2fd894a162b96b2d98c3d3bab3dd25055563e8`.
- No implementation mutation outside the two declared target paths.
- No non-canonical evidence carrier and no committed transient `.gtkb-state/mrc-pytest` content.
- No claim that historical receipts are current, that current collector status passes, or that the modernization program is closed.
- All 13 residual clean-suite assertions remain explicit blockers.
- No unrelated worktree mutation or staging, broad commit, history rewrite, push, deployment, release, credential lifecycle, dispatcher, TAFE, harness, routing, role, database, MemBase, or external-system mutation.
- Prime Builder may author only Prime statuses and may not author GO, NO-GO, or VERIFIED.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-WI5165-HISTORICAL-EVIDENCE-CLOSURE-CORRECTION-AUTHORIZATION and PAUTH version 3",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001; WI-5165",
  "primary_route": "Apply Ruff formatting without AST change, preserve the prior run only as historical evidence in the canonical numbered report, and finalize the complete bridge chain atomically.",
  "before_behavior": "The collector source fails Ruff format-check; the prior invocation is invalid at current HEAD; the proposed dropbox carrier and four-path finalizer are non-executable.",
  "after_behavior": "Collector behavior is unchanged, Ruff gates pass, the canonical report distinguishes historical from current state, and the exact complete bridge chain is eligible for independent atomic finalization.",
  "self_descriptive_naming": "The canonical numbered report and collector source retain the established WI-5165 bridge and semantic-evidence names; no alternate carrier name is introduced.",
  "obsolete_guidance_disposition": "Version 011's current-validity claim, dropbox carrier, and four-path finalizer manifest are preserved as superseded history and are not implementation authority.",
  "history_preservation": "Existing runtime, bridge, Git, PAUTH, and deliberation history remains append-only.",
  "baseline": {
    "current_head": "4ba39a438b84ec40c646cfc46c2741d6e7c6a60f",
    "current_semantic_status": "BLOCKED=12 INVALID=14",
    "historical_invocation": "20260715163526-76461cb465c3",
    "historical_head": "0a8877c8fe21b017c5c3d2f6df0dbd4734ab375b",
    "scope_digest": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240",
    "source_sha256": "758ad51bf999f80cf145b822606b8e8a4baf96916138b9d567fc72812223d7cf",
    "source_ast_sha256": "58bd75c2a77e990c20bced152e2fd894a162b96b2d98c3d3bab3dd25055563e8",
    "pauth_version": 3
  },
  "expected_result": {
    "source": "Ruff-formatted with identical normalized AST digest",
    "carrier": "Canonical report 015 embeds exact historical hashes and current-invalid distinction",
    "current_status": "Remains honestly non-passing until genuinely current evidence exists",
    "finalization": "One independent 17-path local VERIFIED-finalizer commit with no external action"
  },
  "hard_invariants": [
    "Do not rerun or mutate the append-only collector invocation.",
    "Do not represent historical receipts as current validity evidence.",
    "Do not change the collector's normalized Python AST.",
    "Do not mutate outside the two declared implementation target paths.",
    "Do not conceal any of the 13 residual modernization blockers.",
    "Do not stage or commit any path outside the exact 17-path finalizer manifest."
  ],
  "rollback": {
    "instructions": "Before terminal commit, revert only the format-only source delta under separately governed correction authority; never delete runtime evidence or bridge history.",
    "test": "Recompute source AST identity, current collector status, focused tests, Ruff gates, clean-suite semantics, Git-lifecycle checks, and finalizer coverage."
  },
  "fail_closed_conditions": [
    "Missing fresh GO, claim, PAUTH version 3, or exact implementation-start packet.",
    "Source SHA or normalized AST baseline drift before formatting.",
    "Normalized AST changes or any verification gate fails unexpectedly.",
    "Historical evidence is represented as current or any residual blocker is concealed.",
    "Expected bridge sequence or exact finalizer manifest changes.",
    "Any foreign staged path or finalizer failure."
  ],
  "essential_context_preservation": "The canonical report preserves the historical invocation, exact original binding, present invalidity, residual blockers, verification results, and complete-chain finalization authority without promoting stale receipts."
}
```

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - historical/current distinction, format-only non-impairment, and honest residual blockers.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - historical records remain bound to their original HEAD and do not become current after commit.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - executable verification gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct numbered revision, complete predecessor chain, and independent verdict authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete requirement linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - mapped executed evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and exact target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH version 3.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - fresh operation-time authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - owner decision and exact mutation/finalizer envelope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - unchanged linked specification membership.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - fresh GO, claim, and exact packet before source/report mutation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - canonical report carries reviewable evidence; dropbox does not.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - correction remains subordinate to WI-5165 and does not claim program closure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - append-only owner decision, PAUTH, proposal, report, and verdict lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets and evidence sources remain in `E:\GT-KB` and outside adopter scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - helper-mediated Codex bridge filing.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - stale prior verdicts remain preserved and non-operative.

## Prior Deliberations

- `DELIB-20260715-WI5165-HISTORICAL-EVIDENCE-CLOSURE-CORRECTION-AUTHORIZATION` - exact current owner authorization.
- `DELIB-20260715-WI5165-BOUNDED-CLOSURE-CORRECTION-AUTHORIZATION` - superseded four-path carrier/finalizer scope retained as history.
- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-FORMALIZATION-RESULT` - current, honest, non-synthetic evidence authority.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION` - Gate 1 readiness context.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - atomic VERIFIED finalization authority.
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - exact-path local finalization precedent.
- `bridge/gtkb-modernization-rc-evidence-closure-007.md` through `-012.md` - approved collection, implementation evidence, and correction findings.

## Pre-Filing Preflight Subsection

- Candidate applicability preflight: PASS; packet `sha256:29f9b980db11f6712e077b89cb2b52c62b310ee198e080d4f89b4d147cee0d69`, `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, and `blocking_errors: []`.
- Candidate mandatory clause preflight: PASS; 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`, 0 evidence gaps in `must_apply`, and 0 blocking gaps.
- Current authority readback: PASS; PAUTH version 3, rowid 710, owner decision `DELIB-20260715-WI5165-HISTORICAL-EVIDENCE-CLOSURE-CORRECTION-AUTHORIZATION`.
- Current status readback: expected nonzero; HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`, `BLOCKED=12`, `INVALID=14`, scope digest `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.
- Current source baseline: SHA-256 `758ad51bf999f80cf145b822606b8e8a4baf96916138b9d567fc72812223d7cf`; normalized AST SHA-256 `58bd75c2a77e990c20bced152e2fd894a162b96b2d98c3d3bab3dd25055563e8`; Ruff format-check fails as expected before correction.

The governed revision helper must rerun both content preflights and reject placeholders, stale version state, credential findings, or target collisions before filing.

## Specification-Derived Verification Plan

| Governing requirement | Deterministic command or evidence | Required result |
| --- | --- | --- |
| Format-only non-impairment | Recompute source SHA and normalized `ast.dump(..., include_attributes=False)` digest; run `python -m ruff format scripts/collect_modernization_semantic_evidence.py`; recompute AST digest | Pre-format baselines match this proposal; post-format normalized AST digest is identical |
| Source quality | `python -m ruff check scripts/collect_modernization_semantic_evidence.py` and `python -m ruff format --check scripts/collect_modernization_semantic_evidence.py` | PASS |
| Fixed-plan collector coverage | `python -m pytest platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --basetemp .gtkb-state/mrc-pytest/historical-closure-correction-20260715` | PASS; runtime output only |
| Honest current status | `python scripts/collect_modernization_semantic_evidence.py --json status` | Expected nonzero; `BLOCKED=12 INVALID=14`; no claim of current collected receipts |
| Historical evidence integrity | Hash each invocation `20260715163526-76461cb465c3` receipt and count the invocation/focused-test files; compare with versions 009/010 and report 015 | Exact hashes/counts embedded and explicitly labeled historical at original HEAD |
| Honest clean-suite blockers | `python scripts/check_modernization_scope_semantics.py run --phase clean-suite --json` | No new impairment; exact 13 residual assertion failures remain reported |
| Git-lifecycle non-synthesis | `python scripts/check_modernization_git_lifecycle.py --json` | Existing Git-lifecycle checks pass; no synthetic pilot or receipt created |
| Exact source delta | `git diff --check -- scripts/collect_modernization_semantic_evidence.py`; AST comparison; source diff inspection | Formatting-only delta with no whitespace error or behavior change |
| Canonical carrier | Inspect report 015 and activity disposition registry | Complete evidence is in the numbered bridge report; no dropbox artifact exists or is included |
| Governance | Candidate/live applicability and clause preflights; claim status; exact implementation-start packet; PAUTH v3 readback | PASS before implementation/report filing |
| Atomic finalization | Independent LO `write_verdict.py --finalize-verified` with source plus predecessor includes 001-015; helper creates 016 | Exactly the declared 17 paths in one local commit; clean staging; no push, deployment, or release |

## Acceptance Criteria

- Fresh independent GO version 014, matching claim, PAUTH version 3, and exact implementation-start packet precede both target mutations.
- Collector normalized AST digest is unchanged and both Ruff gates pass.
- Focused collector tests pass without collector execution against live evidence or mutation outside runtime test output.
- Current status remains explicitly `BLOCKED=12 INVALID=14`; historical receipts are never counted as current.
- Report 015 embeds the complete historical evidence, current-invalid distinction, exact commands/results, and all residual blockers.
- No dropbox carrier is created, staged, or committed.
- No collector run occurs and no existing receipt or runtime output is changed or deleted.
- Terminal VERIFIED, if warranted, is independently authored and committed only through the exact 17-path atomic finalizer transaction.

## Risk And Rollback

Runtime behavior risk is low because the only source mutation must preserve normalized AST identity. Governance risk remains high if historical evidence is mislabeled or foreign work enters the commit; explicit status language, the complete manifest, clean-staging precondition, and atomic finalizer fail closed on both risks. Modernization remains blocked after this correction.

Before terminal commit, rollback is limited to reverting the format-only source delta under separately governed correction authority. Runtime receipts, numbered bridge history, Deliberation Archive records, and PAUTH history are append-only and must not be deleted or rewritten.

## Recommended Commit Type

`chore(governance): verify WI-5165 historical evidence closure correction`
