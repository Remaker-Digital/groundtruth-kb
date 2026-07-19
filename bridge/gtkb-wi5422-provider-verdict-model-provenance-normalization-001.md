NEW

# gtkb-wi5422-provider-verdict-model-provenance-normalization - Normalize Provider Verdict Model Provenance Before Trusted Publication

bridge_kind: prime_proposal
Document: gtkb-wi5422-provider-verdict-model-provenance-normalization
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; system-declared GPT-5 family; reasoning configuration not exposed; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5422

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Genuine Alibaba H Loyal Opposition dispatch
`2026-07-17T02-58-22Z-loyal-opposition-H-e94140` spent 1,657 seconds
performing a substantive review, then exhausted all four governed publisher
recovery attempts. The provider supplied model-authored
`author_model_configuration` prose, while the trusted runtime supplied the
provider-observed endpoint, route, requested model, and response model.
`scripts/gtkb_bridge_writer.py::_trusted_author_content` rejected that expected
correction as a fatal metadata conflict before the existing metadata validator
could normalize or validate the artifact, so no verdict was published.

Normalize only the three provider-runtime-owned model provenance fields
(`author_model`, `author_model_version`, and
`author_model_configuration`) to the nonblank trusted runtime values before
strict conflict validation. Continue to reject any conflict in
`author_identity`, `author_harness_id`, or
`author_session_context_id`, and preserve every existing bridge transition,
claim, role, target-path, guard, credential, version, and finalization check.
This is distinct from served-model capture, missing interactive Codex metadata,
publisher tool-selection recovery, and verdict-claim lifecycle defects already
tracked elsewhere.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - Requires truthful, non-placeholder
  author identity and model provenance on bridge artifacts; this is WI-5422's
  source specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Keeps provider verdict publication on the
  canonical append-only bridge writer and preserves role, claim, transition,
  and independent-review gates.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - Requires genuine substantive
  dispatcher-produced proof that the H harness can complete its governed LO
  publication path.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - Defines H's provider route
  and provider-observed model provenance as the relevant runtime evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this
  concrete proposal-to-spec linkage before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the explicit
  project, active project authorization, work item, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the positive,
  negative, and end-to-end evidence below before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - Keeps WI-5422 and TEST-11533 as the durable
  backlog and linked-test carriers for this discovered defect.

## Prior Deliberations

- `DELIB-20265888` - Requires harness-invisible black-box dispatch and
  equivalence maintenance. This repair remains inside the shared governed
  writer and adds no harness-to-harness awareness or routing influence.
- `DELIB-202666274` - Authorizes required project-level blocker repairs while
  preserving independent GO, exact claim, implementation-start, independent
  VERIFIED, and separately gated mechanical operations.

## Owner Decisions / Input

No additional owner decision is required to file this proposal. WI-5422 is a
captured P0 hygiene defect in the active authorized project, and
`DELIB-202666274` directs blocker repairs to continue. Protected implementation
still requires an independent `GO`, an exact current-session claim, successful
implementation-start authorization, and later independent `VERIFIED`.
Dispatcher, TAFE, harness, Git, deployment, release, and credential operations
remain outside this proposal's authority.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
requires trustworthy author metadata, `GOV-FILE-BRIDGE-AUTHORITY-001`
requires canonical governed publication, and TEST-11533 defines both the
permitted normalization and the conflicts that must remain denied. No new or
revised requirement is needed.

## Proposed Implementation

1. Add a writer-local provider-verdict normalization step immediately before
   `_trusted_author_content` performs strict trusted-field conflict checks.
2. Replace only `author_model`, `author_model_version`, and
   `author_model_configuration` with the corresponding nonblank trusted runtime
   values. Model-authored, stale, or missing values for those three fields are
   not authoritative.
3. Keep `author_identity`, `author_harness_id`, and
   `author_session_context_id` under the existing fail-closed conflict rule.
   Missing trusted model values, malformed metadata, or any other trusted-field
   mismatch remains an error.
4. Run the existing complete-author-metadata validator after normalization so
   no required field can be omitted or left as a placeholder.
5. Add focused tests proving that stale provider model values are replaced in
   the published artifact while identity, harness, and session conflicts remain
   denied.

## Scope Boundaries

- The exact implementation scope is limited to
  `scripts/gtkb_bridge_writer.py` and
  `platform_tests/scripts/test_gtkb_bridge_writer.py`.
- The writer and test targets were clean at proposal time, with Git object
  hashes `5c338c8e3e30b136f5173cfad542e0ae1e63be75` and
  `8dd935a511fbd041973ca0cde5420c2221c3cd77`.
- No cloud harness loop, provider request, dispatcher, TAFE, routing,
  eligibility, lease, harness registry, runtime allowance, or recovery ceiling
  is changed.
- No direct harness contact, source-of-truth database mutation, credential
  operation, destructive cleanup, Git staging/commit/push, deployment, or
  release is in scope.
- The existing full model, operation, session, worker-lifetime, and document
  lease allowances remain unchanged.

## Acceptance Criteria

1. A provider verdict containing stale or model-authored values in any of the
   three runtime-owned model fields publishes with the exact trusted runtime
   values.
2. The published bridge artifact contains the trusted model name, model
   version, and provider-observed model configuration and contains none of the
   stale values.
3. Conflicts in author identity, harness ID, or session context still fail
   closed before any bridge artifact is created.
4. Missing or blank trusted model metadata still fails the complete metadata
   floor.
5. Existing role, claim, bridge-version, transition, guard, target-path,
   credential, and VERIFIED finalization tests remain green.
6. After independent implementation approval and focused tests, one fresh
   substantive H dispatcher review publishes a governed verdict without the
   WI-5422 metadata-conflict failure.

## Spec-Derived Verification Plan

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, TEST-11533, and the Alibaba adoption
  contract:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
```

Expected: model-field conflicts normalize to trusted runtime values and publish;
identity, harness, session, malformed, incomplete, and unauthorized cases stay
denied.

- Proposal linkage and clause gates:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5422-provider-verdict-model-provenance-normalization-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5422-provider-verdict-model-provenance-normalization-001.md
```

Expected: both mandatory preflights pass without missing required
specifications or blocking clause gaps.

- Focused static and containment checks:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py
git diff --check -- scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py
```

Expected: clean lint, format, whitespace, and exact two-path containment.

- Genuine black-box verification:

```text
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch report --json
groundtruth-kb/.venv/Scripts/gt.exe bridge show <fresh-H-reviewed-thread> --json
```

Expected: a fresh substantive dispatcher-produced H review exits successfully
with a governed verdict path whose trusted model provenance matches the
provider-observed runtime metadata.

## Risk / Rollback

The primary risk is provenance laundering: accepting model-authored metadata
that does not describe the provider runtime. Constraining normalization to
exactly three runtime-owned model fields, requiring nonblank trusted values,
and retaining strict identity/harness/session checks contains that risk. A
secondary risk is weakening generic writer conflict handling; focused negative
tests must prove all non-model conflicts remain denied.

Rollback is a revert of the exact future focused `fix` commit after separately
authorized finalization. The bridge chain remains append-only evidence and is
not deleted by rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5422-provider-verdict-model-provenance-normalization`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - restores the existing governed provider-verdict publication contract
without adding a new routing or harness capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
