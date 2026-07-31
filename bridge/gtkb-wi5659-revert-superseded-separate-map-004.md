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
Document: gtkb-wi5659-revert-superseded-separate-map
Version: 004
Responds to: bridge/gtkb-wi5659-revert-superseded-separate-map-003.md
Reviewer role: loyal-opposition (interactive transcript role; automation session)
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659
Target paths: scripts/check_protected_commit_authorization.py; platform_tests/scripts/test_check_protected_commit_authorization.py
kb_mutation_in_scope: false

# GO — WI-5659 Narrow Reversion of the Superseded Separate-Map Design

## Verdict

GO. The revised reversion proposal resolves both prior blocking findings. It now
cites and applies the controlling owner decision, `DELIB-202667188`: oversized
entries must remain in the ledger with an explicit content-exempt marker, and
the already-present separate-map implementation must first be removed so the
working tree returns to the independently authorized Mechanisms 1–2 baseline.

This GO authorizes **only** that narrow source-and-test reversion. It does not
authorize the corrected in-ledger Mechanism 3 design, a replacement design,
any PAUTH mutation, a commit, or final verification. A subsequent, fresh,
independently reviewed proposal remains required before the corrected
in-ledger design may be implemented.

## Independent Review and Scope Confirmation

- The full reversion thread (`-001` through `-003`) was read. Version `-003`
  corrects `-002` by making `DELIB-202667188` a substantive owner-decision
  input and by retaining the complete dependency chain.
- Proposal author session context is
  `fb16e5ad-1c90-4810-ad72-a0b4d5832133`; reviewer session context is
  `A-2026-07-24T01-03-33Z`. They differ, and author metadata is readable.
- The active project authorization was rechecked as active and permits the
  declared source-and-test mutation classes. The owner’s later deliberation
  controls the substantive design choice; this verdict neither creates nor
  changes an authorization record.
- The live worktree is intentionally still carrying Mechanisms 1–4 and has no
  commit for this thread. The proposal’s exact removal list preserves the
  approved Mechanism 1 protected-path prefilter and Mechanism 2 batched
  materialization while removing only the superseded separate-map and
  `.gtkb-state`-skip behavior.
- Backlog review found WI-5659 as the sole corresponding active work item; no
  duplicate reversion work item or parallel actionable bridge entry exists.

## Authorized Reversion Boundary

Prime Builder may perform only the removal and restoration enumerated in
`-003`: remove the separate `exempted` map and its parameter/wiring, restore
oversized-blob failure behavior for this baseline, remove the hard-coded
`.gtkb-state` skip and literal scratch-path exception, and remove their
Mechanism 3–4-specific tests/helpers. The pre-existing Mechanism 1 and
Mechanism 2 behavior and their tests must remain intact.

Before filing an implementation report, demonstrate that the resulting diff is
limited to the two declared paths and that the superseded symbols/behaviors are
absent while the Mechanism 1 and 2 symbols/tests remain. Run the proposal’s
targeted pytest suite plus `ruff check`, `ruff format --check`, and
`git diff --check`. Do not absorb unrelated dirty-tree content.

## Owner Decision and Prior Deliberations

- `DELIB-202667188` — owner chose “Keep them in ledger”; supersedes the
  separate-map wording and directs the clean-baseline reversion before a
  corrected Mechanism 3 is reviewed.
- `DELIB-202667186` — original Mechanism 3 scope, now superseded in its
  separate-map form by the later owner choice.
- `DELIB-202667187` — Mechanism 4 scope, likewise removed with this reversion.
- `DELIB-202667184` and `DELIB-202667185` — approved Mechanism 1 and 2
  baseline that this reversion must preserve.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-012.md`, `-014.md`,
  and `-016.md` — main-thread NO-GO chain that requires the clean baseline
  before a corrected Mechanism 3 can proceed.
- `bridge/gtkb-wi5659-revert-superseded-separate-map-002.md` — prior NO-GO
  whose owner-decision and dependency-chain omissions are corrected by `-003`.

## Applicability Preflight

- packet_hash: `sha256:8970c85e2e20ac1c4ce695241f8c72538fc09c8ed1ea50a611c8edf46af59fbd`
- bridge_document_name: `gtkb-wi5659-revert-superseded-separate-map`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5659-revert-superseded-separate-map-003.md`
- operative_file: `bridge/gtkb-wi5659-revert-superseded-separate-map-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- candidate_evidence_hash: `sha256:6c34386ddb4d0e64b9856509323cb9053ae546cc096ee4ea9616174ac7a5fa80`

## Clause Applicability

- ADR/DCL clause preflight: passed; four must-apply clauses and one may-apply
  clause assessed, with zero blocking gaps.
- Deliberation search and direct review of the controlling owner decision were
  completed. Search results did not supersede the specific, directly retrieved
  `DELIB-202667188` decision.

## First-Line Role Eligibility

The resolved session role is Loyal Opposition under the transcript-defined
`::init gtkb lo` automation context. `GO` is a Loyal Opposition verdict status
under `GOV-FILE-BRIDGE-AUTHORITY-001`; the reviewer is not the artifact author
or implementer.

## Non-Authority

This verdict authorizes no commit, push, release, deployment, credential use,
or mutation outside the two declared source/test paths. It does not declare
the baseline restored, verified, or commit-ready; those require a subsequent
Prime Builder report and independent LO review.
