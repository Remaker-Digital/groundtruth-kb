REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019feedf-9ae7-7f13-8819-5d6295655342
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder sub-agent; publication-completion lane; transcript-defined ::init gtkb pb
author_metadata_source: Codex runtime session metadata and delegated Prime Builder lane

bridge_kind: prime_proposal
Document: gtkb-wi5950-strict-terminal-recovery
Version: 011
Date: 2026-08-11 UTC
Responds to: bridge/gtkb-wi5950-strict-terminal-recovery-010.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project Authorization Version: 5
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5950
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5950 REVISED — exact recovery cycle under quarantined-W0P forward authority

## Revision Claim

This revision accepts every finding in Loyal Opposition NO-GO `-010` and the
controlling meaning of
`DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`
(canonical MemBase row 14277; content hash
`fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`).
W0P v008, its publication receipt, and commit
`13c9f0f5032e1bcffb3cae60023e2ba20197e86d` remain frozen, append-only,
quarantined mechanics evidence. They are not terminal dependency closure,
successful ratification, or proof that every W0P finalization gate passed.
This proposal requests no W0P success after-action and does not release or
reinterpret that quarantine.

Row 14277 nevertheless authorizes a fresh ordinary WI-5950 cycle now, solely
to normalize and release the shared `registry_control_plane.py` source through
WI-5950's bounded missing-receipt capability. This step precedes, but does not
itself perform or close, the separately sequenced narrow WI-5953
`recovery_required` repair, fresh WI-6140 finalization, registry
declaration/projection parity reconciliation, and later separate W0P forward
revalidation/ratification carrier.

The quarantined commit establishes only the frozen HEAD mechanics baseline for
exact attribution. Against current HEAD
`de467cbc93bbad9f8d826ffd9fa96733f76c504a`, the shared source has exactly the
WI-5950 candidate delta previously declared: `+218/-0`, entirely the
owner-gated `recover_missing_bridge_publication_capability` helper. The focused
WI-5950 test remains unchanged. Neither target is staged. The W0P claim is
`null`; that is collision evidence only, never W0P closure evidence. The fresh
GO requested here can therefore bind an ordinary `go_implementation` claim and
schema-v3 packet without absorbing quarantined W0P or unrelated worktree bytes.

## Requirement Sufficiency

Existing WI-5950 requirements are sufficient for this exact two-target
missing-publication-receipt slice. The original approved proposal, active PAUTH
v5, owner recovery authorization, implementation reports `-005`/`-007`,
NO-GO findings `-006`/`-008`/`-010`, and row 14277 completely define the
behavior, target cohort, dependency interpretation, and verification boundary.
Row 14277 changes predecessor interpretation and forward sequencing; it does
not change WI-5950 product semantics and grants no waiver.

Two failures remain expressly non-waived: WI-6140 exact-source packet-horizon
self-invalidation and registry declaration/projection parity incoherence.
Neither is claimed solved by WI-5950. They remain downstream terminal/current
prerequisites before any W0P quarantine release, revalidation, ratification, or
success after-action. Per `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3, the
registry drift does not block this unrelated, content-only, exact two-target
WI-5950 lifecycle.

## Findings Addressed

### F1 (P0) — v009 contradicted the controlling W0P quarantine authority

Corrected. This revision cites row 14277 and uses W0P v008/receipt/commit only
as frozen quarantined mechanics evidence. It makes no claim of W0P
terminalization, dependency closure, successful ratification, or green
canonical finalization. The exact source attribution is evidence about the
current Git baseline only:

- current HEAD: `de467cbc93bbad9f8d826ffd9fa96733f76c504a`;
- quarantined mechanics commit: `13c9f0f5032e1bcffb3cae60023e2ba20197e86d`;
- source HEAD/index blob: `d0ef9f186b36ba0bbef38e6600c5c602f104ab50`;
- source worktree delta versus HEAD: exactly `218 insertions, 0 deletions`;
- source postimage: 226,032 bytes, SHA-256
  `3f7a60311de62e312f3d627635788bc109b99f233664461f3c2c86953512105e`;
- focused test postimage: 9,148 bytes, SHA-256
  `7c69b7c16a414794a693ee0e0129f8a6aaba3ba0360345a3280ece2d7d50ccdc`;
- staged delta for both exact targets: empty;
- W0P claim: `null`, used only to prove no live claim collision.

The W0P transition-digest/preimage-scoping bytes are frozen in the quarantined
commit and are not attributed to this proposal. The remaining additive source
hunk and focused test are the exact WI-5950 cohort. A later W0P carrier must
independently revalidate all W0P gates after WI-5953, WI-6140, and registry
parity are terminal/current.

### F2 (P1) — v009 omitted the non-waived registry-parity condition

Corrected and kept outside this proposal's target set. Current authoritative
registry evidence remains unresolved:

- `config/registry/sot-artifacts.toml` is `MM`;
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
  is `MM`;
- both HEAD blobs are `0be24b087320e125ee4cd864ebf1432beb05e00d`;
- both index blobs are `d4a1aca0e15172acad63f218f32c9814b2055677`;
- both worktree mirrors are SHA-256
  `12e824cf58780adf882f205b3550694595840139ff6784ade6f18c6e0076c0d4`;
- neither worktree mirror registers the load-bearing
  `scripts/batch_finalize_verified.py` membership identified by the live
  registry validator;
- the dedicated
  `gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization`
  carrier remains at `-003` `NEW`, not `VERIFIED`.

Those registry paths are foreign and excluded. WI-5950 does not add them to
`target_paths`, stage them, mutate them, infer an admission, or claim their
carrier is complete. The applicable governed registry carrier must reach an
independently terminal and current state before any W0P quarantine release or
W0P revalidation/ratification. That condition does not block WI-5950's own
ordinary exact two-target GO, report, and atomic VERIFIED lifecycle.

## Exact Current Candidate Evidence

The WI-5950 candidate adds
`recover_missing_bridge_publication_capability`, an owner-authorization-gated
exact-byte recovery path for genuinely missing publication receipts on
existing pre-capability bridge files. It refuses an existing receipt and does
not edit bridge files, repair `recovery_required` rows, enable dispatch, or
mutate the legacy TAFE dispatcher. The later in-place poisoned-receipt
operation remains owned by the distinct narrow WI-5953 carrier.

Current source delta is one additive hunk beginning at
`recover_missing_bridge_publication_capability`; `git diff --check` passes.
The focused module exercises authorization, exact-byte/lifecycle binding,
existing-receipt refusal, missing-target refusal, success, and idempotence/
single-use behavior.

## Scope And Implementation Sequence

1. Obtain an independent GO on this exact row-14277-corrected revision.
2. Acquire a fresh `go_implementation` claim and create a current schema-v3
   implementation-start packet for exactly the two declared targets.
3. Re-read HEAD, index, worktree hashes, target ownership, PAUTH, row 14277,
   and foreign claims. Stop on drift; otherwise adopt the unchanged candidate
   bytes.
4. Run the focused module, adjacent registry-control-plane recovery regression
   coverage, W0P preimage-scoping non-regression coverage, Python compilation,
   Ruff lint, Ruff format check, exact diff review, applicability preflight,
   clause preflight, and pre-verdict executability.
5. File a fresh post-implementation report containing exact observed evidence
   and reiterating that W0P remains quarantined.
6. Leave VERIFIED publication and atomic commit finalization to an independent
   Loyal Opposition context; its include set must contain only the WI-5950
   numbered chain and exact two implementation targets.
7. After WI-5950 terminalizes through its own ordinary gates, continue the
   separately governed row-14277 sequence: narrow WI-5953, fresh WI-6140,
   registry parity terminal/current closure, then separate W0P revalidation.

No database operation, live bridge-receipt recovery, MemBase mutation,
registry mutation, dispatcher/TAFE mutation, configuration change, destructive
cleanup, staging, commit, push, history rewrite, credential action, deployment,
or release is in scope for Prime Builder implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Prior Deliberations

- `DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`
  (row 14277; content hash
  `fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`)
  — controlling quarantine and forward-recovery authority.
- `DELIB-20260808-WI6073-PUBLICATION-CAPABILITY-RECOVERY-AUTHORIZATION` —
  bounded WI-5950 missing-receipt recovery authority.
- `bridge/gtkb-wi5950-strict-terminal-recovery-001.md` — original approved
  behavior and exact target boundary.
- `bridge/gtkb-wi5950-strict-terminal-recovery-008.md` — scope/claim overlap
  NO-GO whose mechanical collision is now absent.
- `bridge/gtkb-wi5950-strict-terminal-recovery-010.md` — quarantine and
  registry-parity corrections accepted here.
- `bridge/gtkb-w0p-finalization-machinery-repair-008.md` — frozen quarantined,
  non-closing historical mechanics evidence only.
- `DELIB-202667714` — owner decision underlying active project-wide PAUTH v5.

## Owner Decisions / Input

No new owner decision is required. Row 14277 explicitly authorizes this fresh
ordinary WI-5950 cycle while preserving W0P quarantine and the downstream
WI-5953, WI-6140, registry-parity, and separate W0P revalidation sequence. The
owner also requires the legacy TAFE dispatcher to remain disabled. This
revision contains no dispatcher or TAFE mutation.

## Specification-Derived Verification Plan

| Requirement | Executable evidence |
| --- | --- |
| Exact missing-receipt recovery semantics | Focused `test_publication_capability_recovery.py` proves owner gate, exact bytes/lifecycle, missing/existing cases, success, and single-use behavior. |
| Registry-control-plane non-regression | Existing recovery/compensation tests in `groundtruth-kb/tests/test_registry_control_plane.py` and adjacent publication-capability modules. |
| Quarantined-W0P non-impairment | Adjacent W0P preimage-scoping suite remains green; report cites row 14277 and makes no closure/ratification claim. |
| Exact attribution and hygiene | HEAD/index blob equality, `+218/-0` source diff, focused test hash, empty staged set, no foreign claim, and `git diff --check`. |
| Project/bridge authority | Fresh independent GO, `go_implementation` claim, schema-v3 packet, PAUTH v5, applicability/clause/executability gates. |
| Registry-parity boundary | Exact read-only status/hash evidence for both foreign registry mirrors and WI-6075 carrier; neither registry path enters the target/finalization set. |
| Python quality | `py_compile`, Ruff check, and Ruff format check on both exact Python targets. |
| Atomic WI-5950 terminal state | Independent VERIFIED helper finalizes exact WI-5950 chain plus two targets in one local commit. |
| Non-impairment | No database recovery, registry, dispatcher/TAFE, config, external, credential, deployment, or release mutation. |

## Acceptance Criteria

1. Independent GO approves this exact row-14277-corrected two-target scope.
2. No proposal, report, or verdict treats W0P v008/receipt/commit `13c9f0f5`
   as terminal dependency closure, successful ratification, or proof all gates
   passed.
3. Fresh claim and schema-v3 packet both read `go_implementation` for the same
   Prime Builder session and exactly the two declared targets.
4. Candidate hashes, index cleanliness, and `+218/-0` attribution remain true
   at implementation start and report filing.
5. Focused, adjacent, compile, Ruff, diff, applicability, clause, and
   executability checks pass on exact final bytes.
6. Independent VERIFIED creates the atomic WI-5950 local commit without any
   unrelated worktree path.
7. Registry parity remains explicit separate governed work; both registry
   paths remain excluded, and W0P quarantine release/revalidation fails closed
   until the applicable carrier is independently terminal and current.
8. WI-5950 may terminalize without W0P ratification solely under row 14277's
   bounded forward-recovery authority and its own ordinary exact gates.
9. The disabled legacy TAFE dispatcher remains disabled and untouched.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5950; NO-GO 010; DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001 row 14277; quarantined W0P v008/commit 13c9f0f5",
  "canonical_authority": "the WI-5950 numbered bridge chain, row 14277, active PAUTH v5, exact source/test bytes, and independent WI-5950 finalization",
  "primary_route": "REVISED -> independent GO -> go_implementation claim/schema-v3 packet -> exact report -> atomic WI-5950 VERIFIED",
  "before_behavior": "v009 incorrectly interpreted frozen W0P mechanics evidence as terminal dependency closure and omitted the non-waived registry-parity condition",
  "after_behavior": "W0P remains quarantined; row 14277 permits bounded WI-5950 source normalization while preserving WI-5953, WI-6140, registry parity, and later W0P revalidation as separate governed work",
  "self_descriptive_naming": "recover_missing_bridge_publication_capability names the missing-receipt-only operation and distinguishes it from WI-5953 recovery_required repair",
  "obsolete_guidance_disposition": "v009 terminalization language is rejected by NO-GO 010; immutable prior versions remain history only",
  "history_preservation": "all bridge versions, the W0P receipt, and quarantined commit remain append-only and are neither rewritten nor reinterpreted",
  "baseline": {
    "head_commit": "de467cbc93bbad9f8d826ffd9fa96733f76c504a",
    "quarantined_w0p_mechanics_commit": "13c9f0f5032e1bcffb3cae60023e2ba20197e86d",
    "source_delta": "+218/-0",
    "source_sha256": "3f7a60311de62e312f3d627635788bc109b99f233664461f3c2c86953512105e",
    "test_sha256": "7c69b7c16a414794a693ee0e0129f8a6aaba3ba0360345a3280ece2d7d50ccdc",
    "w0p_claim": "null; collision evidence only",
    "registry_parity": "unresolved, foreign, excluded"
  },
  "expected_result": {
    "missing_receipt_helper_present": true,
    "focused_and_adjacent_tests_green": true,
    "exact_two_target_atomic_finalization": true,
    "w0p_quarantine_released": false,
    "registry_or_dispatcher_or_tafe_mutation": false
  },
  "rollback": {
    "instructions": "stop without mutation on drift; any later rollback removes only the WI-5950 additive hunk and focused test under separate authority",
    "verification": "repeat hashes, exact diff, focused and adjacent tests, claims, packet, registry readback, and bridge lifecycle checks"
  },
  "hard_invariants": [
    "only the exact two WI-5950 targets are adopted",
    "W0P v008, its receipt, and commit remain quarantined non-closing evidence",
    "no old draft-claim packet is reused",
    "no live recovery, database, registry, dispatcher, or TAFE mutation occurs in this implementation slice",
    "no VERIFIED survives without its same-transaction local commit"
  ],
  "fail_closed_conditions": [
    "any target hash, index, claim, PAUTH, proposal/GO, packet, or target-set drift",
    "any foreign work ownership or attribution ambiguity",
    "any mandatory test or gate failure",
    "any finalization set containing unrelated paths",
    "any attempt to use WI-5950 as W0P quarantine release or registry-parity authority"
  ],
  "essential_context_preservation": "WI-5950 repairs genuinely missing pre-capability receipts only; narrow WI-5953 repairs recovery_required next; WI-6140 is then freshly finalized; registry parity closes separately; W0P revalidation/ratification comes last"
}
```

## Pre-Filing Preflight Subsection

The completed draft must pass the canonical applicability and mandatory clause
preflights before live filing. The governed revision helper reruns both checks,
credential scanning, live-version monotonicity, and exact-target PAUTH
evaluation and must fail closed on any drift. After filing, pre-verdict
executability is run on the live v011 bytes.

## Risk And Rollback

The recovery helper can create a consumed receipt only when supplied exact
owner authority and content, so misuse risk is material but bounded by strict
file/lifecycle binding and existing-receipt refusal. The larger governance risk
is again misreading quarantined W0P evidence as closure; row 14277 citations,
explicit non-waivers, and the fail-closed sequence above prevent that
interpretation. Any drift before report filing stops without target mutation.
A later source rollback is limited to the exact WI-5950 additive hunk and
focused test under separate authority; numbered bridge history, registry
worktree bytes, and quarantined W0P evidence are never deleted or rewritten.

## Recommended Commit Type

`feat:` — this adds the bounded owner-gated missing-publication-receipt recovery
capability while preserving the row-14277 quarantine boundary.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
