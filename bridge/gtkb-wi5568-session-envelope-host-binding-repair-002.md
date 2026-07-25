GO
::init gtkb lo
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5568-session-envelope-host-binding-repair
Version: 002
Date: 2026-07-24 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: A-2026-07-24T21-41-16Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata
Reviewer role: loyal-opposition
Responds to: bridge/gtkb-wi5568-session-envelope-host-binding-repair-001.md

# Loyal Opposition Verdict — WI-5568 Session-Envelope Host Binding Repair

## Verdict

GO. Version 001 presents a bounded repair for the host-session persistence
defect, with active owner authorization, complete current specification linkage,
and a regression plan that exercises both the envelope and bridge-claim paths.

## First-Line Role Eligibility Check

- This writer resolves as `loyal-opposition` in the open Codex A session
  `A-2026-07-24T21-41-16Z`, with Loyal Opposition worker-role provenance and
  the `build` activity envelope.
- The latest bridge status was independently rechecked as `NEW` on version 001.
- `GOV-FILE-BRIDGE-AUTHORITY-001` authorizes Loyal Opposition to publish this
  `GO`; the governed writer will repeat the role, claim, and transition checks
  immediately before publication.

## Review Independence

- Proposal author: `prime-builder/codex`, session
  `019f9329-a174-7763-8f7e-29679f39e6bd`.
- Reviewer: `loyal-opposition/codex`, session
  `A-2026-07-24T21-41-16Z`.
- The readable author metadata and distinct session contexts satisfy the
  session-context independence requirement.

## Applicability Preflight

Executed: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5568-session-envelope-host-binding-repair`

- packet_hash: `sha256:7f13cd332970f71ee63ec8beda74e662aa3acf92b9708444aa647639e59803f3`
- bridge_document_name: `gtkb-wi5568-session-envelope-host-binding-repair`
- content_file: `bridge/gtkb-wi5568-session-envelope-host-binding-repair-001.md`
- operative_file: `bridge/gtkb-wi5568-session-envelope-host-binding-repair-001.md`
- candidate_evidence_hash: `sha256:3dd6d56e5efe0cc9a55c8a885ef6994075bb6d3126815d5159b3b0e4a663146f`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

Executed: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5568-session-envelope-host-binding-repair`

- Clauses evaluated: 5; must_apply: 4; may_apply: 1; not_applicable: 0.
- Evidence gaps in must-apply clauses: 0.
- Blocking gaps: 0; exit 0.

## Prior Deliberations

- `DELIB-20260724-WI5568-RUNTIME-SCOPE-AUTHORIZATION`, cited by the proposal
  and its active PAUTH, authorizes only host-session binding, refresh
  persistence, mismatch fail-closed behavior, and focused provenance/claim
  regressions.
- Semantic deliberation search was performed for the runtime host-binding
  scope. Its broad historical matches supplied no contradicting owner decision;
  the recorded owner-decision identifier above is the applicable authority.

## Independent Verification

- Confirmed active PAUTH
  `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-WI5568-RUNTIME-20260724` is limited to
  WI-5568, `source`, `test_addition`, and `governance_evidence`; it explicitly
  forbids the broader role-authority purge and unrelated worktree changes.
- Inspected `cli_session_handoff.py`: the envelope-open path currently calls
  `open_session` without a host session ID, while later metadata attestation can
  bind a host document only after the initial open. The proposed repair directly
  addresses that ordering gap.
- Ran the proposed focused regressions:

```text
python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_claim_cli.py -q --tb=short
37 passed in 20.20s
```

## Required Implementation Boundaries

1. Limit mutation to the three declared paths:
   `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`,
   `platform_tests/scripts/test_session_envelope_cli_provenance.py`, and
   `platform_tests/scripts/test_bridge_claim_cli.py`.
2. Read and resume only the exact host-keyed envelope. Do not use a shared
   projection, global marker, or a different session document as authority.
3. Preserve no-host-ID and non-Codex behavior. Contradictory role-bearing
   refresh input must fail before changing either the exact document or shared
   projection.
4. Do not modify `session/envelope.py`; if its existing API is insufficient,
   submit a revised proposal for fresh LO review.
5. Before implementation, acquire the required implementation-start
   authorization and complete the specified focused test, Ruff, and diff checks.

## Scope and Non-Authority

This GO authorizes only the bounded WI-5568 implementation described in version
001 after the required operation-time gates pass. It does not authorize the
separate retired-authority purge, unrelated workspace changes, deployments,
credential lifecycle work, or a broader session-envelope redesign.

## Commands Executed

```text
gt bridge show gtkb-wi5568-session-envelope-host-binding-repair --json --compact
gt projects show-authorization PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-WI5568-RUNTIME-20260724 --json
gt deliberations search "WI5568 runtime host binding" --limit 10 --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5568-session-envelope-host-binding-repair
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5568-session-envelope-host-binding-repair
python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_claim_cli.py -q --tb=short
```

## Owner Action Required

None. The recorded owner decision and active PAUTH cover this bounded repair.

Skills applied: gtkb-bridge, gtkb-proposal-review

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
