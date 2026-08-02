NEW
::init gtkb pb
::open build

# WI-5554 Strict Recovery: Make Verdict Freshness Evidence Producible

bridge_kind: prime_proposal
Document: gtkb-wi5554-verdict-candidate-preparation-strict-recovery
Version: 001
Date: 2026-08-01 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-V2-20260719
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554
Related Work Items: WI-5348, WI-5445, WI-5524, WI-5600

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/bridge_applicability_preflight.py", "scripts/gtkb_bridge_writer.py", "platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: configuration_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
selected_remediation: shared_verdict_candidate_preparation
draft_only: true

## Strict-Recovery Claim

The historical `gtkb-wi5554-lo-verdict-candidate-preflight` chain cannot carry
a new strict implementation start because immutable v005 declares
`Version: 005 (NEW; post-implementation report)`. The strict resolver requires
exact three-digit metadata and rejects the chain with
`WRONG_BRIDGE_VERSION_METADATA`.

This fresh document begins an independent parse-clean lifecycle without
rewriting or deleting historical evidence. Version 001 intentionally has no
`Responds to` field. No historical claim, packet, GO, report, or finalization
receipt transfers into this chain. The approved design is restated from the
exact eight-target v007 proposal and independent v008 GO; the active V2 PAUTH
remains the implementation authority.

## Requirement Sufficiency

Existing requirements sufficient. This work supplies the missing sanctioned
producer for the already-approved fail-closed verdict-freshness requirement. It
does not create a new role, status, queue, provider contract, or authority.

## Historical Evidence

- Historical v002 rejected broad full-bar widening and selected narrow evidence
  freshness.
- Historical v004 approved the narrow validator design.
- Historical v005 is immutable implementation evidence but has invalid
  decorated version metadata.
- Historical v006 identified the missing production producer, stale fixture,
  and packet-stability defect.
- Historical v007 supplied the exact eight-target corrected implementation plan.
- Historical v008 independently approved that plan under the active V2 PAUTH.
- Historical v009 attempted `NO-ACTION`, which is not terminal closure.
- Historical v010 restored `NO-GO` because the approved implementation remains
  outstanding.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` and v007
  preserve the stale-verdict reproduction and correction.
- `bridge/gtkb-wi5600-provider-applicability-preflight-recovery-002.md`
  preserves missing-section enrichment as separate work serialized after
  WI-5554.

The old chain is evidence, not the parent of this proposal.

## Authorization Boundary

The exact active V2 PAUTH authorizes WI-5554 only across the eight declared
targets and the approved configuration/source/test mutation classes. It does
not authorize credential lifecycle, destructive cleanup, dispatcher/TAFE
mutation, external-system mutation, Git staging/commit/history/push,
production deployment, or release. The obsolete three-target PAUTH remains
revoked. This proposal performs no KB mutation and no MemBase write.

Project/WI implementation approval is inherited from the active parent project,
but fresh independent GO, exact claim, schema-v3 start, operation-time PAUTH,
independent VERIFIED, and separately governed Git finalization remain mandatory.

## Proposed Scope

1. Add public deterministic verdict-candidate preparation primitives to
   `scripts/bridge_applicability_preflight.py` that normalize a root-contained
   intended path, resolve the exact canonical same-thread artifact named by
   `Responds to`, expose one public candidate-evidence hash implementation,
   replace exactly one existing applicability section, and return final
   prepared content with the path-bound hash inserted.
2. Add a write-free CLI preparation mode requiring `--content-file` and exact
   `--candidate-path`. Send prepared bytes to stdout and diagnostics to stderr;
   incompatible JSON/report modes fail closed.
3. Make `write_bridge_file()` prepare content after author metadata and envelope
   normalization and immediately before compliance audit. Audited and written
   bytes must be identical.
4. Preserve `NO-GO` without applicability unchanged. Do not synthesize missing
   applicability for `GO` or `VERIFIED`; WI-5600 retains any separately
   approved missing-section enrichment.
5. Make active and template hooks use the public hash implementation when
   importable, retaining only a byte-equivalent fail-closed fallback for partial
   installations.
6. Move tests away from hook-private fixture construction, rebuild the stale
   hard-block fixture through the public API, and add writer/CLI end-to-end,
   fixed-source stability, unrelated-state invariance, and applicable-
   governance invalidation coverage.
7. Run the unchanged atomic VERIFIED finalization suite without changing
   `write_verdict.py`.
8. Preserve status, provenance, independence, transition, evidence-anchor,
   project, claim, start, finalization, credential, and append-only gates.

## Out Of Scope

- Provider missing-section generation or provider/adapter/skill/helper changes.
- Widening pending candidate preflight beyond NEW and REVISED.
- Adding Specification Links requirements to verdicts.
- Dispatcher/TAFE configuration or activation, workers, claims/leases,
  eligibility/routing, credentials, deployment, release, external systems,
  Git publication, destructive cleanup, history rewrite, alternate queues, or
  unrelated mutation.

TAFE remains deliberately disabled and must not be activated.

## Timer, Threshold, And Concurrency Boundary

Do not introduce a hard-coded timeout, retry delay/count, TTL, polling interval,
threshold, throttle, fan-out value, or per-harness concurrency limit. Candidate
preparation is a synchronous deterministic transformation. Any necessary timer
or concurrency control must consume centralized typed configuration or be
proposed separately under the timer-governance program. Evidence of an
insufficient value must update its exact existing WI or create a governed
correction WI only when no owner exists.

Last-moment preparation must rebuild packet and candidate hashes as one
operation. Unrelated authoritative-state changes must preserve a fixed-source
packet hash; applicable governance changes must invalidate it. A candidate
denied after state movement is rebuilt from fresh state, never retried with
stale bytes. Overlapping claim, packet, worker, peer target, or hunk ownership
fails closed before mutation.

## Start Conditions And Shared-File Sequencing

Implementation starts only when all are freshly true:

1. This exact v001 has a same-slug independent GO.
2. The V2 PAUTH remains active and the obsolete PAUTH remains revoked.
3. WI-5445 and WI-5524 remain independently terminal and finalized.
4. A new exact eight-target claim exists for this fresh recovery slug.
5. A schema-v3 implementation-start packet derives from the fresh GO.
6. No old-chain claim or packet is reused.
7. No live worker or peer owns an approved target or hunk.
8. Current target bytes are reobserved and exact WI-5554 hunks are isolated.
9. A canonical hunk patch has verified target membership and forward/reverse
   applicability.
10. Active and template hook copies finish byte-identical.
11. Operation-time authorization passes before every protected mutation.
12. WI-5600 remains serialized behind terminal WI-5554 ownership.

Any failed condition stops before protected mutation.

## Strict Lifecycle

- Metadata in this chain remains exactly three numeric digits.
- The next independent Loyal Opposition response may issue v002 GO or NO-GO
  responding only to this v001.
- Implementation requires that fresh GO, exact claim, and schema-v3 start.
- The PB implementation report is the next numeric version and reports exact
  changed hunks and executed evidence.
- A different independent Loyal Opposition session issues terminal VERIFIED or
  NO-GO.
- NO-ACTION is not implementation closure; finalization remains focused and
  atomic; historical bridge files remain untouched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — fresh chain, exact claim/start, and independent verdict authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every applicable requirement is cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification maps each requirement to executed evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — exact targets and hunks make the repair independently evaluable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — sanctioned publication routes and topology remain usable.
- `GOV-WORK-TREE-HYGIENE-001` — foreign worktree/index bytes are preserved.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — active/template hook behavior and typed dispositions are explicit.
- `ADR-CROSS-HARNESS-PARITY-001` — applicable hook behavior remains aligned.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex inherits the governed writer path without private helper forks.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-level PAUTH controls implementation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the cohort stays inside the V2 envelope.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — authorization is re-evaluated before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, and WI linkage are explicit.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — historical NO-ACTION does not close implementation.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — current author/session metadata is explicit.
- `SPEC-AUQ-POLICY-ENGINE-001` — active inherited project approval means no new AUQ.
- `GOV-STANDING-BACKLOG-001` — timer findings route to existing governed owners.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — malformed history, risks, and follow-on work remain durable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — proposal, code, tests, report, and verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — old invalid history and fresh candidate state remain explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifacts remain in the GT-KB root.

## Specification-Derived Verification Plan

| Requirement | Verification | Required result |
|---|---|---|
| Bridge authority/evaluability | Prepare and audit GO, NO-GO, and VERIFIED through the public API and both hooks. | Exact-source packet and candidate hash pass without hook-private calls. |
| Nonimpairment | Exercise writer-mediated and direct-CLI routes. | Both produce identical audit-passing final bytes. |
| Status semantics | Test NO-GO without applicability and GO/VERIFIED without applicability. | NO-GO is unchanged; GO/VERIFIED remain denied. |
| Source freshness | Use wrong thread/version and mutate applicable governance. | Exact source rebuilds; stale evidence cannot survive. |
| Candidate freshness | Mutate one byte after preparation. | Both hooks deny candidate-hash mismatch. |
| Concurrency determinism | Rebuild around unrelated state changes, then applicable-governance change. | Unrelated change preserves hash; applicable change invalidates it. |
| Writer integration | Invoke real `write_bridge_file()` after normalization. | Audited bytes exactly equal written bytes. |
| Atomic finalization | Run the existing atomic VERIFIED suite unchanged. | Full suite and rollback behavior pass. |
| Parity | Compare active/template tracked content and focused decisions. | Canonical content and decisions match; final raw bytes are byte-identical. |
| Hygiene/authority | Re-run PAUTH, GO, claim/start, hunk, lint, format, compile, diff, and index checks. | Only authorized WI-5554 hunks are attributed. |

Required verification includes focused pytest over the two hook modules, the
applicability-preflight and writer modules, plus the unchanged atomic VERIFIED
suite; Ruff check and format-check on all changed Python; `py_compile`; exact
hunk hash/size and forward/reverse apply; `git diff --check`; and candidate/live
applicability plus mandatory clause gates. The implementation report must map
every specification to an actual command/result and duration.

## Cross-Harness Disposition

- Claude active hook and packaged template are direct implementation targets
  and must finish with identical content and equivalent decisions.
- Codex uses the governed writer and the same shared applicability service; no
  Codex-specific hook or helper fork is added.
- Cursor and other harnesses receive no new projection in this slice; their
  typed capability disposition remains unchanged.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5554; historical versions 001-010; approved v007 scope and v008 GO; active V2 PAUTH; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; shared applicability service; governed writer; active/template compliance hooks; active V2 project PAUTH",
  "primary_route": "Prepare final candidate evidence after normalization and immediately before audit, then write exactly the audited bytes.",
  "before_behavior": "The validator requires fresh verdict evidence but sanctioned writer and direct-CLI routes lack a public last-moment producer, leaving approved GO or VERIFIED content difficult to produce safely.",
  "after_behavior": "Writer and direct-CLI routes rebuild exact-source evidence and bind it to final normalized candidate bytes through one public implementation before audit.",
  "baseline": {
    "active_hook_git_blob": "7cac8ee53485835df4d5372a96a2b2f19a35e192",
    "template_hook_git_blob": "7cac8ee53485835df4d5372a96a2b2f19a35e192",
    "applicability_preflight_git_blob": "c9de9bcab3f7d2d165d5379b94f6a4620a9b4927",
    "writer_git_blob": "2be05e971f742366d83514b86a448661ba9a06d5",
    "target_status": "all eight targets clean at proposal preflight"
  },
  "self_descriptive_naming": "verdict candidate preparation identifies the produced artifact and exact pipeline phase without adding aliases.",
  "history_preservation": "Historical 001-010 files remain immutable; this fresh chain carries independent authorization and receipts.",
  "obsolete_guidance_disposition": "Historical v005 decorated metadata and v009 closure implication remain evidence but are noncontrolling; v007/v008 design evidence is restated, not continued.",
  "configuration_authority": "No local timer, retry, threshold, throttle, fan-out, or concurrency literal is added; centralized typed timer governance remains controlling.",
  "expected_result": "GO and VERIFIED candidates become producible through sanctioned routes without weakening status, freshness, provenance, independence, or atomic-finalization gates.",
  "essential_context_preservation": "Preserve exact-source binding, final-byte hash, active/template parity, NO-GO semantics, GO/VERIFIED missing-section denial, WI-5600 serialization, exact PAUTH, append-only history, and dispatcher/TAFE no-touch.",
  "hard_invariants": [
    "Audited and written bytes are identical.",
    "PENDING_PREFLIGHT_STATUSES remains NEW and REVISED.",
    "NO-GO without applicability remains valid; missing GO or VERIFIED applicability remains denied.",
    "No dispatcher, TAFE, helper, provider, credential, timer, Git-publication, or unrelated mutation occurs."
  ],
  "fail_closed_conditions": [
    "Fresh GO, exact claim/start, V2 PAUTH, dependency terminality, target cleanliness, or hunk isolation is stale.",
    "The exact Responds-to source or final candidate path escapes the root or is ambiguous.",
    "More or fewer than one applicability section would be replaced.",
    "Any focused negative control, parity check, applicability gate, clause gate, or exact-scope check fails."
  ],
  "rollback": "Under separate authority, revert only verified WI-5554 hunks after reverse-applicability proof; preserve all numbered bridge and foreign worktree bytes."
}
```

## Acceptance Criteria

1. GO and VERIFIED candidates are producible through writer and direct-CLI
   routes without private-hook imports or hand-computed hashes.
2. Preparation occurs after normalization and before audit; audited and written
   bytes are identical.
3. The exact same-thread Responds-to packet is rebuilt at preparation time.
4. NO-GO without applicability is unchanged; missing GO/VERIFIED applicability
   remains denied.
5. Fixed-source hashes survive unrelated state changes and invalidate on
   applicable governance changes.
6. Focused, hard-block, applicability, writer, and unchanged atomicity suites pass.
7. Active and packaged hooks finish byte-identical.
8. Only exact authorized hunks are attributed.
9. No timer/concurrency constant or excluded mutation is introduced.
10. Independent VERIFIED and focused finalization are required for terminality.

## Risks And Rollback

Primary risks are circular byte preparation, multiple-section replacement,
stale concurrent state, and commingled target dirt. All fail closed. Rollback
requires separate authority and reverts only verified WI-5554 hunks after
reverse-applicability verification. Historical files and foreign worktree
bytes remain untouched.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — bounded fleet/harness defect-repair authorization.
- Historical WI-5554 v002/v004/v006/v007/v008/v010 — selection, design, defect evidence, approved scope, independent GO, and outstanding status.
- WI-5348 v006/v007 — stale-verdict reproduction and correction.
- WI-5600 v002 — separate missing-section enrichment serialized after WI-5554.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — owner-approved
  bounded repair and active V2 PAUTH basis for the exact eight targets.
- The owner-approved per-project implementation doctrine applies: WI-5554
  inherits implementation approval from its active parent project.

No new owner input or AUQ is required.

## Requested Loyal Opposition Action

Review this fresh v001 as a standalone chain. Do not reject it solely because
the immutable historical chain is malformed; that is the reason for recovery.
Issue same-slug GO only if the V2 PAUTH, project/WI authority, dependencies,
WI-5600 serialization, target/hunk ownership, centralized timer boundary,
applicability, mandatory clauses, and verification plan remain sufficient.
Any GO must point only to this v001 and declare old claims, packets, and
finalization evidence nontransferable. Otherwise return precise same-slug
NO-GO corrections.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `scripts/bridge_applicability_preflight.py`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`fix(bridge): make verdict freshness evidence producible`
