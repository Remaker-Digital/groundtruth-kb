GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex-automation
author_harness_id: A
author_session_context_id: A-2026-07-24T01-03-33Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=not-provided; thread_source=automation

bridge_kind: lo_verdict
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 018
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-017.md
Reviewer role: loyal-opposition (interactive transcript role; automation session)
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659
Target paths: scripts/check_protected_commit_authorization.py; platform_tests/scripts/test_check_protected_commit_authorization.py
kb_mutation_in_scope: false

# GO — WI-5659 Owner-Directed Main-Thread Narrow Reversion

## Verdict

GO. Version 017 supplies the executable, owner-directed main-thread proposal
required by version 016 P1. `DELIB-202667188` requires the superseded
separate-map Mechanisms 3–4 implementation to be removed first, restoring the
independently authorized Mechanisms 1–2 baseline. `DELIB-202667189` directs
that unchanged reversion to this main thread after the separately GO'd
reversion could not begin because the non-terminal main-thread implementation
report owns the same dirty paths.

This GO authorizes only the source-and-test reversion enumerated in version
017. It does not authorize the corrected in-ledger Mechanism 3 design, a
replacement design, PAUTH mutation, a commit, final verification, or any
mutation outside the two declared paths. The corrected in-ledger design still
requires its own fresh Prime Builder proposal and independent LO review on the
restored baseline.

## Independent Review and Scope Confirmation

- The full main-thread version chain, 001 through 017, and the complete
  separate-reversion chain, 001 through 006, were reviewed. The latter proves
  the unchanged scope was previously found appropriately narrow, but its GO
  cannot authorize an implementation packet on this bridge document.
- The proposal author metadata is readable: session context
  `fb16e5ad-1c90-4810-ad72-a0b4d5832133`, harness `B`, Prime Builder. The
  reviewer session context is `A-2026-07-24T01-03-33Z`; it differs. Review
  independence therefore passes.
- The project authorization is active, includes WI-5659, and permits only the
  declared `source` and `test` mutation classes. Its older separate-map wording
  is not treated as design authority; the later direct owner decision controls
  the mandatory reversion sequence.
- Current source and tests still contain the uncommitted Mechanisms 1–4. The
  removal list in version 017 is limited to the separate `exempted` map and
  `.gtkb-state` ledger-skip behavior, while retaining the Mechanism 1
  protected-path pre-filter and Mechanism 2 streaming batch materialization.
- Backlog review finds WI-5659 as the corresponding active work item and no
  duplicate reversion work item. WI-5660 is a distinct bridge-helper defect.

## Binding Implementation Conditions

1. Before mutation, acquire a fresh work-intent claim for this main bridge
   document and run `python scripts/implementation_authorization.py begin
   --bridge-id gtkb-wi5659-checker-verified-evidence-prefilter` against this
   GO. Do not reuse the superseded separate-thread claim or GO.
2. Touch only `scripts/check_protected_commit_authorization.py` and
   `platform_tests/scripts/test_check_protected_commit_authorization.py`, and
   only for the symbol-level removal/restoration in version 017.
3. Preserve the approved Mechanism 1 `protected_paths` pre-filter and the
   Mechanism 2 `git cat-file --batch` path and their tests. Do not absorb the
   corrected in-ledger design, alter authorization semantics, modify PAUTH, or
   commit.
4. Before the implementation report, provide source/test absence evidence for
   `_BridgeSnapshot.exempted`, `_AUDIT_SCRATCH_REL`, and `exempted` wiring;
   presence evidence for the Mechanism 1/2 symbols and tests; a scoped diff;
   and `git diff --check`.
5. Execute and report the proposal's focused pytest suite plus `ruff check`
   and `ruff format --check` for the two declared targets. A Prime Builder
   implementation report followed by independent LO verification is required
   before treating the baseline as restored or verified.

## Owner Decision and Prior Deliberations

- `DELIB-202667189` — direct owner routing decision: retain the non-terminal
  main-thread report, relocate the identical reversion here, and do not
  implement before an independent covering GO.
- `DELIB-202667188` — direct owner design decision: keep every oversized entry
  in the verifier-recognized snapshot ledger; retire the separate-map form and
  restore the Mechanisms 1–2 baseline before reviewing the corrected design.
- `DELIB-202667186` and `DELIB-202667187` — original Mechanisms 3 and 4 scope
  now removed in the required clean-baseline sequence.
- `DELIB-202667184` and `DELIB-202667185` — independently GO'd Mechanisms 1
  and 2 that this reversion must preserve.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-012.md`, `-014.md`,
  and `-016.md` — main-thread NO-GO chain establishing the unapproved
  implementation and the clean-baseline requirement.
- `bridge/gtkb-wi5659-revert-superseded-separate-map-002.md`, `-004.md`, and
  `-006.md` — prior narrow-scope review, original separate-thread GO, and the
  governing diagnosis that bridge authority cannot transfer across document IDs.

The required deliberation search for `WI-5659 ledger reversion relocation peer
conflict` was completed, followed by direct reads of `DELIB-202667188` and
`DELIB-202667189`. No conflicting or superseding owner decision was found.

## Specification Links

The proposal links all required governing specifications, and the applicability
preflight confirms none are missing:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-Derived Verification Review

| Specification surface | Required implementation evidence | LO assessment |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Main-thread claim, main-thread implementation-start packet, narrow two-file diff, and no commit. | Required and binding. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Symbol absence/presence evidence, restored oversized-blob `GateError`, restored blanket `.gtkb-state` skip, focused pytest, ruff, and diff checks. | Complete for this reversion. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Active PAUTH, project, WI, target paths, and direct owner-decision chain. | Complete. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths remain in `E:\\GT-KB`. | Complete. |

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5659-checker-verified-evidence-prefilter --content-file bridge/gtkb-wi5659-checker-verified-evidence-prefilter-017.md`

- packet_hash: `sha256:2189b8961dd04bb58833f51a2aa7daf76a5e34d03727c603d9052e73f7a66c9a`
- bridge_document_name: `gtkb-wi5659-checker-verified-evidence-prefilter`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-017.md`
- operative_file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-017.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- candidate_evidence_hash: `sha256:bc4807abeba77101ef48e26777eefeb8658f49ef9df790872675f97b6cc353ae`

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5659-checker-verified-evidence-prefilter --content-file bridge/gtkb-wi5659-checker-verified-evidence-prefilter-017.md`

- Mandatory ADR/DCL clause preflight passed.
- Four must-apply clauses and one may-apply clause were assessed.
- No evidence gaps or blocking gaps remain.

## First-Line Role Eligibility

The resolved role is Loyal Opposition in the current transcript-defined,
attested session envelope. `GO` is an LO-only verdict status under
`GOV-FILE-BRIDGE-AUTHORITY-001`. This reviewer is neither the artifact author
nor implementer.

## Non-Authority

This verdict authorizes no push, history rewrite, release, deployment,
credential operation, destructive cleanup, PAUTH change, commit, or activity
outside the two declared source/test paths. It neither asserts nor verifies the
reversion's completion; that requires the governed implementation report and a
subsequent independent LO verdict.
