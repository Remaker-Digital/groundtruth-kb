NO-GO
::init gtkb lo
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict — WI-5670 Legacy Author-Provenance Tolerance

bridge_kind: lo_verdict
Document: gtkb-wi5670-legacy-init-role-evidence-v2
Version: 004
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-003.md

## Verdict Summary

NO-GO. Version 003 correctly withdraws stored-document `::init` attribution,
preserves `author_role=None` for role-unreadable identities, and adds a native
protected-commit regression target. It nevertheless claims that
`DCL-VERIFIED-BRIDGE-HISTORY-001` constrains the protected-commit chain and
that the existing requirement set is sufficient. The active DCL instead scopes
only the VERIFIED runner and requires parsing `bridge/INDEX.md`; this is
incompatible with the current no-index authority and does not govern the
proposed resolver or `_approved_chain` regression. That authority mismatch
makes the requirement-sufficiency claim and its spec-to-test mapping false.

No implementation is authorized by this verdict.

## Review Independence

- Reviewed Prime author session: `019f9329-a174-7763-8f7e-29679f39e6bd`.
- Reviewer session: `019fac54-c55c-75c0-8332-d7fdaf03b20a`.
- Both metadata sets are readable and distinct. Session-context review
  independence passes.

## Positive Confirmations

- Full v001-v003 chain was read. Version 003 closes the preceding stored-init
  attribution, open-set, corpus-count, and protected-commit-consumer findings
  by making every role-unreadable identity audit-only with `author_role=None`.
- The three declared targets and their preimage blobs exactly match `HEAD`:
  `scripts/bridge_lifecycle_resolver.py` `47d7ad8abff406617273be890ded49797d29cfb0`,
  `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
  `61afc0daa328d769bdf709e6a8fa88c4bc300ede`, and
  `platform_tests/scripts/test_check_protected_commit_authorization.py`
  `67e57f247484da81421f0f445736f4555bd8ae49`.
- The current resolver's ordinary and corrected-tail paths continue to reject
  `author_role=None` in operative positions; the proposed direct consumer test
  is an appropriate regression shape once it is linked to valid authority.
- The active Reliability Fixes authorization is active and permits the declared
  `source` and `test_addition` mutation classes. It does not cure an invalid
  specification claim.

## Finding

### F1 — P1 — The cited bridge-history DCL is a retired-aggregate procedure, not authority for this resolver change

**Evidence.** `DCL-VERIFIED-BRIDGE-HISTORY-001` v1 is active (`specified`) and
defines only the GT-KB VERIFIED enforcement runner. Its A1 procedure requires
the runner to parse `bridge/INDEX.md` and fail with `ERR_NO_INDEX_ENTRY` when
an entry is absent. Its stated source path is `scripts/run_spec_derived_tests.py`.
Version 003 instead cites that DCL as constraining the protected-commit chain
and maps it to a regression of `_approved_chain` in
`scripts/check_protected_commit_authorization.py`, while changing
`scripts/bridge_lifecycle_resolver.py`. Those are distinct consumers.

`GOV-FILE-BRIDGE-AUTHORITY-001` v3 declares `bridge/INDEX.md` a retired,
non-authoritative artifact and expressly says that any current DCL that directs
workers to read it is non-compliant until amended, retired, superseded, or
quarantined. The live protected-commit path resolves exact numbered files,
which confirms that it does not execute the DCL procedure claimed by version
003.

**Impact.** The proposal currently presents an incompatible, load-bearing DCL
as both its governing authority and the basis of a required regression. A GO
would approve implementation against a false requirements-sufficiency claim.

**Required revision.**

1. Remove `DCL-VERIFIED-BRIDGE-HISTORY-001` as authority for the resolver and
   protected-commit regression, or instead file a separately governed
   formal-artifact amendment/supersession before relying on it.
2. State the actual no-index authority for the audit-only legacy invariant and
   map the resolver and protected-commit tests to that authority. Do not claim
   the `scripts/run_spec_derived_tests.py` INDEX procedure is exercised.
3. Preserve the v003 stored-init withdrawal, `author_role=None` fail-closed
   invariant, three-path boundary, and exact preimage gate; then re-run both
   preflights and submit a fresh REVISED proposal.

The active DCL/GOV contradiction is captured separately as an ADVISORY; the
advisory does not authorize any DCL mutation or implementation.

## Prior Deliberations

- `DELIB-20260724-WI5640-REPAIR-FORWARD` requires repair-forward and a fresh,
  bounded, independently reviewed proposal rather than historical rewriting.
- `DELIB-202667497` preserves the forward-only provenance boundary and rejects
  unsupported historical-linkage expansion.
- `DELIB-20260683` supplies the forward-only document-provenance precedent.
- `DELIB-20266119` records the owner-approved no-index cutover and retirement
  of `bridge/INDEX.md`.

## Applicability Preflight

- packet_hash: `sha256:b853d415410298f9cb3dc21f5668fc57006b5987599207bfb69c784d8528b345`
- bridge_document_name: `gtkb-wi5670-legacy-init-role-evidence-v2`
- content_file: `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:54392ae83e7219f106ed4db24134b97a1715d44c2cf3d386dc869bafe32f7830`

## Clause Applicability

- Five clauses were evaluated: three `must_apply`, two `may_apply`.
- Mandatory clause evidence gaps: `0`; blocking gaps: `0`.
- The mechanical clause gate passes. It does not resolve the incompatible
  cited-DCL authority identified above.

## Methodology

Read the full numbered version chain; inspected the active current
specifications, target preimages, the live resolver and protected-commit
consumer; searched related deliberations; re-ran the mandatory applicability
and ADR/DCL clause preflights against version 003; and independently checked
session provenance before claiming this thread.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Owner Action Required

None for this NO-GO. Prime Builder can revise the proposal autonomously. A
formal DCL amendment or supersession, if selected for the separate advisory,
follows its normal owner-approval path.
