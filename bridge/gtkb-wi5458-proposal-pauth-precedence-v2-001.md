NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


bridge_kind: prime_proposal
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 001
Date: 2026-07-29 UTC

# WI-5458 v2 - Validated Proposal PAUTH Selection And Currentness

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Claim

File one strict-resolver-valid recovery proposal for the remaining WI-5458
defect. The proposal-filing command will gain a validated explicit project-
authorization selector, reject stale authorization state before publication,
apply the canonical operation/target classifier, and expose machine-readable
decision evidence. The implementation remains limited to the three previously
approved WI-5458 files.

The prior thread is preserved unchanged as incident evidence. Its version 007
contains `Version: 007 (NEW; post-implementation report)` rather than the exact
required `Version: 007`. The strict lifecycle resolver therefore raises
`WRONG_BRIDGE_VERSION_METADATA`, and
`scripts/implementation_authorization.py begin` cannot authorize the otherwise
resumable version-008 report NO-GO. Appending to that structurally invalid chain
cannot repair its strict prefix. This v2 thread replaces it as the executable
continuation without deleting or rewriting any prior bridge artifact.

## Requirement Sufficiency

Existing requirements sufficient.

This recovery implements the already-recorded WI-5458 acceptance contract and
the version-008 findings. It does not create a new authorization model. Full
cross-gate project-authorization operation-time parity remains owned by WI-5178;
this slice implements only the proposal-filing enforcement point needed to
unblock WI-5166 and then WI-5178.

## Current Evidence

- Strict resolver result for `gtkb-wi5458-proposal-pauth-precedence`:
  `WRONG_BRIDGE_VERSION_METADATA` at version 007.
- Implementation-start recovery result: denied because the version metadata
  does not match the numbered path; no packet or source mutation occurred.
- The three target files are clean and tracked at baseline commit
  `8317c8b17d00967b7b272d392d148e96fda3b886`.
- Baseline file SHA-256 values:
  - `proposal_filing.py`: `BEBD88385FCC51F46C4DC15798638B0A303EBAAAD69E0EF67799CFFF45D558EC`
  - `cli_bridge_propose.py`: `9012B51CDEB1E7599918FF38D8D6D7A2E54658517B270D2F34A00A42FE36F550`
  - `test_cli_bridge_propose.py`: `1DD916F19D2307E33D1FF2660C1E674A00D0FC6C3CE39DF183E034E2CFB3F156`
- Focused baseline:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short`
  passed `20/20` with one existing pytest configuration warning.
- The exact WI-5458 PAUTH is current, active, unexpired, project-matched,
  WI-5458-scoped, and permits source, test, bridge, metadata, and governance-
  evidence mutation. It forbids commit, push, dispatcher mutation, external
  mutation, deployment, release, credentials, and destructive cleanup.

## Proposed Implementation

### 1. Explicit selector

Add `--project-authorization <PAUTH-ID>` to
`gt bridge file-implementation-proposal`. Carry the value through
`FilingRequest`, project-state resolution, generated proposal metadata,
`FilingResult`, JSON output, and text output.

The selector is optional. Automatic deterministic ranking remains the default.
When present, it may resolve an equal-best-rank ambiguity but may not silently
select a less-specific authorization while a more-specific current candidate
exists.

### 2. Currentness before ranking

Before automatic ranking or explicit selection, validate every candidate input
needed by this filing point:

- current row exists and `status == active`;
- `expires_at` is absent or valid ISO-8601 strictly later than decision time;
- `superseded_by` is empty;
- owner-decision identity is present and resolves;
- authorization project equals the selected active project;
- restrictive work-item coverage is satisfied, with exclusions dominant;
- linked specifications do not intersect `excluded_spec_ids`;
- requested operation normalizes to `bridge_proposal_filing`;
- every target path receives one canonical mutation class permitted by the
  authorization; forbidden-operation precedence remains absolute.

Expired and already-superseded status-active rows are removed from automatic
candidate ranking. Malformed or otherwise unresolvable currentness evidence
fails closed rather than silently falling through. An explicitly requested
expired, superseded, unknown, cross-project, or non-covering authorization is
always denied with a stable reason.

`included_spec_ids` is recorded in the decision evidence. This WI does not
invent a new restrictive interpretation beyond the current canonical
operation-time contract: explicit specification exclusions deny. WI-5178 owns
any broader cross-gate inclusion-semantics change and its parity fixtures.

### 3. Canonical operation and target evaluation

Use
`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`
with the root-bound governed taxonomy. Do not create a second operation or
mutation-class registry. The request is `bridge_proposal_filing`; the exact
normalized proposal targets are evaluated before content construction,
candidate preflights, writer invocation, or bridge publication.

### 4. Decision evidence and side-effect boundary

Return a stable decision object containing selector mode, requested and
selected authorization IDs, authorization version, normalized envelope hash,
project, work item, linked specifications, normalized operation, classified
targets, evaluator/taxonomy versions and hashes, decision time, and reason.
Render that object in generated proposal metadata and expose it through both
JSON and text command output.

All explicit-selector and currentness failures occur before proposal content,
candidate preflights, bridge writer calls, or bridge-file creation. Tests use a
recording writer and preflight probe to prove zero calls on denial.

### 5. Create-missing-state compatibility

Preserve the existing owner-approved `--create-missing-state` route. A supplied
selector must identify an existing authorization and is validated before any
missing membership is created. Automatic creation continues to require the
owner decision and emits the same operation-time decision contract after the
new authorization exists. No denied selector may be used as a request to create
or substitute authorization state.

## Version-008 Finding Disposition

| Finding | Disposition |
|---|---|
| F1 - no validated explicit selector | Implement the CLI/request/service selector, constrain it to the best specificity rank, validate its complete current envelope, disclose it in all outputs, and add ambiguity-override plus denial tests. |
| F2 - expired status-active rows remain eligible | Parse expiry, reject malformed currentness, exclude expired/superseded rows before automatic ranking, and deny an explicitly selected stale row. Canonical operation/target evaluation is run before side effects. |
| Missing operation-time spec linkage | Add `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` to this proposal and the implementation report mapping. |
| Invalid v007 report metadata | Preserve the old chain; use this clean v2 thread because strict-prefix history cannot be repaired by append. |

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| PAUTH envelope and restrictive WI scope | Focused unit fixtures for exact, explicit-list, fallback, exclusion, unknown, cross-project, and non-covering selection. |
| Operation-time currentness | Focused fixtures for active, malformed expiry, expired, superseded, forbidden operation, disallowed class, and no-side-effect denial; assert evaluator decision fields. |
| Explicit selector | CLI help, JSON, text, dry-run metadata, live metadata, equal-rank override, and lower-rank rejection tests. |
| Deterministic ranking | Preserve insertion-order independence and existing specificity tests; expired/superseded candidates cannot affect the best rank. |
| Bridge and project linkage | Candidate and live applicability preflights with exact project, work item, PAUTH, target paths, and operation-time DCL. |
| Independent verification | Full focused pytest, Ruff check, Ruff format check, diff check, preflights, and exact three-file status/diff inventory. |

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2
```

## Acceptance Criteria

1. The v2 lifecycle is strict-valid and independently receives GO before any
   target-file mutation.
2. `--project-authorization` resolves equal-best-rank ambiguity only after full
   currentness, project, WI, spec-exclusion, operation, and target-class checks.
3. Automatic selection excludes expired and superseded rows before ranking;
   malformed currentness fails closed.
4. Unknown, stale, cross-project, excluded/non-covering, lower-rank, forbidden-
   operation, and disallowed-target selections produce no content, preflight,
   writer call, or bridge file.
5. Generated proposal metadata plus JSON and text output disclose selected and
   requested PAUTH identities and machine-readable evaluator evidence.
6. Existing deterministic specificity and insertion-order behavior remains
   passing.
7. The focused suite, Ruff check, Ruff format check, diff check, and both bridge
   preflights pass.
8. Only the three declared files change. No PAUTH, project, backlog, dispatcher,
   TAFE, harness, credential, external, deployment, release, or cleanup state is
   mutated by implementation.
9. A fresh implementation report receives independent terminal VERIFIED before
   WI-5458 is resolved or WI-5166 proceeds.

## Prior Deliberations

- `DELIB-20266083` - owner decision establishing restrictive
  `included_work_item_ids` semantics.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authority
  for the bounded WI-5458 defect-repair envelope.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - dispatcher
  mutation remains prohibited.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-002.md` and `-004.md` - prior
  proposal findings on deterministic precedence and sibling ownership.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-006.md` - substantive GO for the
  original three-file repair.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-008.md` - implementation NO-GO
  requiring selector and currentness enforcement.

## Intuitiveness / Non-Impairment Disposition

The obvious worker path remains one command. Automatic selection stays the
default for the common unambiguous case. When multiple equally specific
authorizations exist, the denial names the candidates and the same command now
offers an explicit validated selector instead of forcing PAUTH mutation or a
manual bypass. Stale authorization state is rejected before publication with a
bounded recovery message. No artifact content is invalidated because of a
missing audit notation, and ordinary hand edits remain valid; this slice
governs only which existing authorization a bridge-filing operation cites.

Rollback is a scoped reversal of the three implementation files after preserving
the report and verdict evidence. The old invalid bridge chain and this v2 chain
remain append-only audit history.

## Risks

- A selector could become an authority bypass. Mitigation: it must be one of the
  current best-ranked covering candidates and passes the same evaluator.
- Filtering stale rows could silently choose broader authority. Mitigation:
  malformed currentness denies; output discloses all eligible ranked candidates
  and the selected ID; explicit lower-rank selection denies.
- Operation-time semantics could diverge from WI-5178. Mitigation: use the
  canonical evaluator/taxonomy and leave broader cross-gate parity to WI-5178.
- Validation after a side effect could leave partial state. Mitigation: selector
  and existing-state validation precede content, preflight, writer, and bridge
  publication; tests pin zero-call behavior.

## Recommended Commit Type

`fix(bridge)`

## Authority Boundary

This NEW proposal grants only independent Loyal Opposition review actionability.
It does not authorize source/test mutation, implementation start, PAUTH or
project mutation, bridge verdict authorship, Git staging or commit, dispatcher
or TAFE mutation, harness changes, credentials, external operations, cleanup,
deployment, release, or peer-worker launch. Implementation remains paused until
this exact v2 proposal receives independent GO and a matching exact-session
claim and implementation-start packet.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
