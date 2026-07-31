NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5458-proposal-pauth-precedence-v2 - 009

bridge_kind: implementation_report
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 009
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-008.md
Approved proposal: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458
Recommended commit type: feat:
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py","groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py","platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]
kb_mutation_in_scope: false

## Implementation Claim

Implemented the approved WI-5458 V2 proposal-filing authorization repair within
the three-file GO scope. `gt bridge file-implementation-proposal` now accepts a
validated `--project-authorization` selector, applies restrictive work-item
coverage before ranking, fixes the best specificity cohort before currentness
pruning, and evaluates the selected normalized PAUTH envelope with the canonical
operation-time evaluator before proposal content, preflights, or publication.

The filing service now emits one stable authorization-decision object in the
generated proposal, JSON result, and text result. That evidence binds the exact
session role provenance, selector inputs, candidate ranks/dispositions,
authorization version/currentness/envelope hash, owner-decision snapshot,
project/membership/bridge preimage, linked specification sets, normalized
operation/targets, and evaluator/taxonomy hashes. It revalidates the same inputs
after candidate preflights and denies publication if they drift.

Create-missing behavior is now fail-closed: source/test/configuration targets
cannot mint authority; bridge/metadata targets are first evaluated in memory,
then missing membership and a narrow exact-WI PAUTH are created in one bounded
database transaction. Dry-run does not persist that state, and injected PAUTH
creation failure rolls the membership insertion back.

This implementation performs no MemBase mutations; the transaction behavior
above is runtime behavior implemented and exercised only against disposable
test databases.

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

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-conversation authority carried by the active WI-5458 PAUTH.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718` v1 - bounded source/test implementation carrier used for the three approved targets.
- No new owner decision was required during implementation. No dispatcher activation, Git staging, commit, push, release, or deployment was performed.

## Prior Deliberations

- `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-008.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The 39-test platform suite covers normalized envelope fields/hash, allowed classes, forbidden operation, spec exclusion, and stable decision identity; 15 canonical evaluator tests also pass. |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | The automatic/explicit coverage matrix proves listed nonmember allow, empty-list member allow, unlisted member denial, empty-list nonmember denial, and exclusion precedence with no preflight/writer side effects. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | The platform suite covers `Z`/offset expiry normalization, malformed/naive denial, expiry/supersession pruning, fixed-cohort no-fallback, forbidden operation, disallowed class, and post-preflight invalidation; canonical evaluator suite: 15 passed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py validate` returned `authorized: true` for exactly the three modified paths before final verification. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Exact `gt bridge show gtkb-wi5458-proposal-pauth-precedence-v2 --json` showed latest v008 `GO`; report planner selected v009 `NEW`; no Loyal Opposition status was authored by Prime Builder. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The 39-test suite asserts project, WI, PAUTH, candidates, target paths, bridge preimage, and decision metadata in service/CLI output. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Generated content retains auto-linked specifications and includes linked/included/excluded spec sets in the stable decision evidence; 39 tests passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every carried-forward specification to executed evidence; platform/package/evaluator suites total 77 passing tests. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | WI-5458 was implemented first as v007 requires; overlapping WI-5560, WI-5466, and WI-5234 work was not absorbed or mutated. |
| `GOV-STANDING-BACKLOG-001` | Work remained linked to WI-5458 and its active project; no aggregate backlog or dispatcher route was used. |
| `ADR-CROSS-HARNESS-PARITY-001` | The behavior is implemented in the shared Python CLI/service; package CLI compatibility suite: 23 passed. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | JSON/text/generated-content parity is pinned by decision-identity and CLI tests; 39 platform tests and 23 package CLI tests passed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Change is carried by WI-5458, PAUTH, proposal v007, GO v008, implementation-start packet, and this append-only report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Governed artifacts precede source mutation; the report planner confirms the exact three changed targets and v009 report route. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Latest GO and live claim were rechecked before implementation; this report transitions the thread to manual LO verification without self-verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing Agent Red target rejection remains covered in the 39-test platform suite; no application subtree changed. |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff --check` passed, Ruff check/format passed, and the report contains only the three clean-at-start authorized targets; 22 unrelated dirty paths remain excluded. |

## Commands Run

- `python -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py --output-format concise`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py --target groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py --target platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `gt bridge show gtkb-wi5458-proposal-pauth-precedence-v2 --json`

## Observed Results

- Platform proposal-filing suite: `39 passed in 20.20s`.
- Package bridge-propose compatibility suite: `23 passed, 1 warning in 20.60s`; the warning is an unrelated ChromaDB Python 3.16 deprecation notice.
- Canonical PAUTH operation-time evaluator suite: `15 passed in 0.40s`.
- Ruff check: `All checks passed!`; Ruff format: `3 files already formatted`.
- `git diff --check`: exit 0 with no findings.
- Implementation-authorization validation: `authorized: true` for exactly all three report targets.
- Exact bridge state: latest `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-008.md`, status `GO`, eight-version chain before this report.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`

Excluded out-of-scope dirty paths: 22.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     .../src/groundtruth_kb/bridge/proposal_filing.py   | 850 ++++++++++++++++++---
     .../src/groundtruth_kb/cli_bridge_propose.py       |  29 +-
     .../groundtruth_kb/test_cli_bridge_propose.py      | 472 +++++++++++-
     3 files changed, 1237 insertions(+), 114 deletions(-)
```

## Acceptance Criteria Status

- [x] CLI exposes and threads `--project-authorization` through request, service, content, JSON, and text surfaces.
- [x] Automatic and explicit selection share restrictive WI coverage; non-empty includes are authoritative and empty includes alone use active membership fallback.
- [x] Exclusions deny before mutation, and explicit selection is limited to equally best-ranked current covering candidates.
- [x] Best specificity cohort is fixed before stale pruning; expired/superseded exact authority never falls through to broader membership authority.
- [x] Timezone-aware `Z` and offset expiries normalize to UTC; malformed/naive values deny globally.
- [x] Currentness includes lifecycle status and `superseded_by`; owner-conversation evidence and linked-spec exclusions fail closed.
- [x] Canonical `bridge_proposal_filing` operation and root-bound target classifier/evaluator are used with normalized DB envelopes.
- [x] Create-missing source/test/configuration authority is denied before DB/preflight/writer/filesystem effects.
- [x] Positive create-missing bridge/metadata state is narrow, exact-WI, dry-run-safe, and membership insertion rolls back when PAUTH insertion fails.
- [x] One stable decision identity carries selector, cohort, authorization, exact actor, project/membership/bridge preimage, specification, operation, target, evaluator/taxonomy, outcome, and recovery evidence.
- [x] Candidate preflight is followed by fresh state revalidation before writer use; project/authorization/bridge drift denies publication.
- [x] Existing parity, non-impairment, Agent Red isolation, draft, and package CLI behavior remains passing.
- [x] Only the three approved implementation paths changed; overlapping sibling GO work remains serialized for later rebase.

## Risk And Rollback

Residual implementation risk is concentrated in the bounded create-state
transaction: the three-file scope uses the existing private KnowledgeDB
connection so `link_project_work_item(commit=False)` and the self-committing
`insert_project_authorization` share one transaction. An injected insert
failure proves rollback of the pending membership. A future shared DB service
could remove that private-connection dependency, but it is not required for
this approved slice.

The parent project is active at version 15 but retains the historical non-null
`completed_at=2026-07-29T06:04:51Z` from its premature retirement. The decision
evidence deliberately binds that value; this implementation does not silently
rewrite project lifecycle history.

Rollback is a focused revert of the three source/test files after preserving
this report and any LO verdict as append-only evidence. Do not delete bridge
versions or absorb overlapping WI-5560, WI-5466, or WI-5234 hunks. No commit has
been created because the active carrier forbids `git_commit`; terminal focused
finalization therefore requires a separate governed authority after independent
VERIFIED.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
