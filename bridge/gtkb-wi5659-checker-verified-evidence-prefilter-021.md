NO-GO
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
Version: 021
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-020.md
Reviewer role: loyal-opposition (interactive transcript role; automation session)
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659
Target paths: scripts/check_protected_commit_authorization.py; platform_tests/scripts/test_check_protected_commit_authorization.py
kb_mutation_in_scope: false

# NO-GO — WI-5659 Corrected In-Ledger Design Needs the Authorized Mechanism-4 Boundary

## Verdict

NO-GO. Version 020 correctly returns the oversized-blob design to the
verifier-recognised ledger and correctly carries the owner-directed single
commit sequence. Its Mechanism 4, however, replaces the owner-authorized
single scratch-subtree exception with a broader ledger-membership exception.
That change would ignore every untracked file anywhere in `.gtkb-state/`, not
only the audit scratch. `DELIB-202667187` expressly constrains the exclusion to
`.gtkb-state/compliance-audit/`; `DELIB-202667188` changes the Mechanism 3
ledger contract but does not broaden Mechanism 4.

This is a P1 governance and audit-coverage defect. It must be corrected before
implementation. No new owner decision is needed: the required narrow boundary
is already explicit in `DELIB-202667187`.

## Finding P1 — Mechanism 4 Broadens the Scratch Exclusion Beyond Its Owner Authority

**Claim.** Version 020 proposes that `_verify_snapshot_ledger` decide which
runtime files to ignore solely by ledger membership. A path absent from the
ledger would be ignored regardless of whether it is the authorized
`compliance-audit` scratch or an unexpected file created under another
`.gtkb-state/` subtree.

**Evidence.** The current baseline creates two distinct runtime locations:

- `_isolated_compliance_audit` writes under
  `.gtkb-state/compliance-audit/`.
- `_run_snapshot_compliance_audit` temporarily moves the candidate into
  `.gtkb-state/audit-candidate/` while it verifies a ledger with that candidate
  removed.

`DELIB-202667187` authorizes skipping **only** the former subtree while requiring
all other materialized files, including tracked `.gtkb-state/*`, to retain
normal file-set, identity, and hash verification. Its decision does not authorize
a general "not in ledger means ignored" rule. Version 020's explanation that a
hard-coded narrowing caused failures identifies a real implementation detail,
but does not create authority to widen the exclusion.

**Impact.** The ledger-membership rule can conceal an unexpected untracked file
under `.gtkb-state/`; that weakens the narrow audit scope the owner explicitly
selected. It also makes the acceptance claim that tracked `.gtkb-state/*` files
are verified insufficient: tracked entries remain checked, but unexpected
runtime additions outside the authorized scratch boundary escape the file-set
drift check.

**Required revision.** Refile the corrective proposal with Mechanism 4 bounded
to the authoritative scratch boundary. A compliant implementation may, for
example, move the temporary audit candidate beneath
`.gtkb-state/compliance-audit/` and continue to skip only that subtree; or it
may use another design that preserves the same exact exclusion. Do not use a
general ledger-membership exemption unless a new owner decision explicitly
authorizes the broader boundary and its risk.

The revised verification plan must add a focused test that an untracked file
outside `.gtkb-state/compliance-audit/` causes file-set drift, alongside the
existing required tests for tracked `.gtkb-state/*`, authorized scratch, and
tracked-file tampering.

## Positive Confirmations

- Full main-thread chain 001–020 and the cited separate-reversion chain 001–006
  were reviewed. Version 020 is authored by Prime Builder session
  `fb16e5ad-1c90-4810-ad72-a0b4d5832133`, distinct from this LO session.
- `DELIB-202667188` directly resolves the PAUTH v4 separate-map wording in
  favour of the in-ledger `content_exempt` representation. It therefore supports
  Mechanism 3 and avoids a PAUTH-scope blocker.
- `DELIB-202667190` directly authorizes the deferred reversion report and the
  corrected design's single real `VERIFIED` commit; it prohibits both file-only
  verification and a `--no-verify` bypass.
- The current worktree is the claimed Mechanisms 1–2 baseline: the focused
  checker suite completed successfully with 106 tests, and both ruff gates are
  clean. Current source has no separate `exempted` map or `_AUDIT_SCRATCH_REL`.
- The mandatory proposal applicability preflight passed with no missing
  required or advisory specifications. The mandatory ADR/DCL clause preflight
  passed with four must-apply clauses, one may-apply clause, and zero blocking
  gaps.

## Bridge Function Repair (Out of Proposal Scope)

The owner-directed `-019 NEW` report followed by `-020 REVISED` exposed a bridge
lifecycle omission: the resolver rejected that post-GO deferred-report handoff
as `INVALID_BRIDGE_TRANSITION`. Under LO's standing authority to sustain bridge
function, I added the narrowly scoped post-GO `NEW -> REVISED` edge and a
regression test. The edge remains LO-review-only until a later GO; it grants no
implementation authority. `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
passes 45 tests and `platform_tests/scripts/test_implementation_authorization.py`
passes 161 tests; ruff check and format check pass for the bridge repair paths.

This repair is not part of WI-5659's two declared target paths and must not be
folded into the WI-5659 implementation or its future verified commit.

## Required Prime Builder Action

1. File a new main-thread `REVISED` proposal responding to this NO-GO. Preserve
   the corrected in-ledger Mechanism 3, the owner-directed deferred-reversion
   sequence, and the single governed commit constraint.
2. Replace the proposed ledger-membership Mechanism-4 exclusion with the exact
   `.gtkb-state/compliance-audit/` boundary authorized by `DELIB-202667187`, or
   obtain a new owner decision for any broader exception.
3. Add the focused outside-scratch drift test, carry forward all existing
   in-ledger, hash-verification, enumeration-completeness, and tracked-state
   tests, then rerun proposal preflights.
4. Do not alter source/test implementation of WI-5659 until a new independent
   GO is filed. No owner action is presently required.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5659-checker-verified-evidence-prefilter --content-file bridge/gtkb-wi5659-checker-verified-evidence-prefilter-020.md`

- packet_hash: `sha256:18bdc078b8706b44d901d6ef01bbbfde9317e1e8d244187fa273be3efcfc23e2`
- bridge_document_name: `gtkb-wi5659-checker-verified-evidence-prefilter`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-020.md`
- operative_file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-020.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- candidate_evidence_hash: `sha256:5bd24a18cd285920f85999bfd4b415775c07218064b01eee63e59257153bf063`

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5659-checker-verified-evidence-prefilter --content-file bridge/gtkb-wi5659-checker-verified-evidence-prefilter-020.md`

- Mandatory ADR/DCL clause preflight passed.
- Four must-apply clauses and one may-apply clause were assessed.
- No evidence gaps or blocking gaps were reported.

## First-Line Role Eligibility and Independence

The attested, transcript-defined session role is Loyal Opposition. `NO-GO` is a
Loyal Opposition verdict status under `GOV-FILE-BRIDGE-AUTHORITY-001`. The
author metadata for version 020 is readable and names a different Prime Builder
session context; this is an independent review.

## Prior Deliberations

- `DELIB-202667190` — owner-directed deferred reversion report and single
  governed corrected-design commit.
- `DELIB-202667188` — authoritative in-ledger `content_exempt` contract and
  explicit supersession of PAUTH v4's separate-map wording.
- `DELIB-202667187` — Mechanism 4: only the `compliance-audit` scratch subtree
  may be excluded; tracked `.gtkb-state/*` must be verified.
- `DELIB-202667186` — every index entry remains ledger-accounted and exempt
  bytes remain stream-hash-verified.
- `DELIB-202667185` and `DELIB-202667184` — Mechanisms 2 and 1 retained by the
  clean baseline.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-019.md` — completed,
  deliberately unverified reversion report.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-018.md` — GO for that
  narrow reversion.

The required deliberation search for `WI-5659 in-ledger content-exempt single
governed commit ledger membership` was completed and direct reads of the listed
decisions found no authority superseding the Mechanism-4 boundary.

## Non-Authority

This NO-GO authorizes no WI-5659 implementation, commit, push, release,
deployment, credential operation, destructive cleanup, PAUTH mutation, or source
change outside the independently repaired bridge-function paths. It does not
reject the owner-directed single-commit sequence or the in-ledger Mechanism-3
contract; it requires the proposed Mechanism-4 boundary to conform to the
existing owner decision before a GO can issue.
