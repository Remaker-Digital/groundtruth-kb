ADVISORY

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# Advisory — Retired-Index Procedure Remains Active in VERIFIED Bridge-History DCL

bridge_kind: governance_advisory
Document: gtkb-lo-verified-runner-index-dcl-conflict-advisory
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-07-29 UTC

## Source

Direct Loyal Opposition review of
`bridge/gtkb-wi5670-legacy-init-role-evidence-v2-003.md`, with live MemBase
and numbered-bridge inspection on 2026-07-29. The proposal cited
`DCL-VERIFIED-BRIDGE-HISTORY-001` as protected-commit-chain authority; the
review established that its active procedure still requires the retired
aggregate. The related proposal received a separate NO-GO at
`bridge/gtkb-wi5670-legacy-init-role-evidence-v2-004.md`.

## Claim

`DCL-VERIFIED-BRIDGE-HISTORY-001` v1 remains `specified` but is formally
incompatible with `GOV-FILE-BRIDGE-AUTHORITY-001` v3. The DCL instructs the
VERIFIED runner to parse `bridge/INDEX.md`, identify a `Document:` entry there,
and fail with `ERR_NO_INDEX_ENTRY` when it is absent. The active GOV declares
`bridge/INDEX.md` retired, absent, non-authoritative, and forbidden as a
current read, writer, recovery, or operational dependency. It expressly says
current DCLs with executable INDEX guidance must be amended, retired,
superseded, or quarantined through their governed lifecycle.

## Evidence

- Live `DCL-VERIFIED-BRIDGE-HISTORY-001` v1, scope `GT-KB platform VERIFIED
  enforcement runner`, names `scripts/run_spec_derived_tests.py` as its source
  path. Its A1 requires parsing all versions listed in `bridge/INDEX.md`; its
  A2 requires an owner-approved waiver for a REVISED removal.
- Live `GOV-FILE-BRIDGE-AUTHORITY-001` v3 says numbered status-bearing files
  plus TAFE/dispatcher runtime state are authoritative, and says any current
  formal artifact that directs a worker to read or infer state from the retired
  aggregate is non-compliant.
- `DELIB-20266119` records the owner-approved no-index cutover and confirms
  `bridge/INDEX.md` and its reconciliation stack were retired rather than
  retained as a fallback.
- Current protected-commit code resolves exact numbered files through
  `scripts/bridge_lifecycle_resolver.py`; it does not execute the DCL's
  INDEX-based procedure. This made the false citation visible during WI-5670
  review, but the DCL conflict is platform-wide and outside that narrow repair.
- Duplicate search found historical references and generic retired-aggregate
  advisories but no current ADVISORY that captures this exact active
  `DCL-VERIFIED-BRIDGE-HISTORY-001` contradiction.

## Impact

The active VERIFIED-runner contract cannot be truthfully implemented or cited
as current authority without violating the active bridge authority rule. It
creates false requirements-sufficiency and spec-to-test claims, and risks a
future reintroduction of a retired aggregate dependency.

## Recommended Prime Action

Prime Builder should route this advisory to a governed formal-artifact
disposition: amend or supersede the DCL with a no-index full-thread procedure
that uses the numbered-file reader and live TAFE/dispatcher state as applicable,
or retire/quarantine it until a correctly authorized replacement exists. The
replacement must include an approval-complete postimage and focused runner
tests. Do not silently edit the DCL, revive `bridge/INDEX.md`, or treat this
advisory as implementation authorization.

## Prior Deliberations

- `DELIB-20266119` — owner no-index cutover decision.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` — forward repair remains preferred to
  history rewriting for governed bridge incidents.
- `DELIB-202667497` and `DELIB-20260683` — related provenance-review context;
  neither grants an INDEX exception.

## Owner Decision Needed

No owner decision is requested by this advisory. Capture is evidence-only and
does not choose between amendment, supersession, retirement, or quarantine.
Those formal-artifact options require their normal governed owner-approval
path when Prime Builder disposes the advisory.

## Classification Slot

- Classification: `adapt`.
- Implementation implied: yes, but only after Prime Builder obtains the normal
  governed formal-artifact route and an implementation proposal receives an
  independent Loyal Opposition GO.

## Non-Approval Statement

This ADVISORY is not implementation approval. It does not authorize protected
source/configuration edits, a DCL mutation, bridge-index recreation, dispatcher
activation, or a bridge GO.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
