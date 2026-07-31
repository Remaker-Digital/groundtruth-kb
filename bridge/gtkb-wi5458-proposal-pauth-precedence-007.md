NEW
::init gtkb lo
::open build


author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5458-proposal-pauth-precedence - 007

bridge_kind: implementation_report
Document: gtkb-wi5458-proposal-pauth-precedence
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5458-proposal-pauth-precedence-006.md
Approved proposal: bridge/gtkb-wi5458-proposal-pauth-precedence-005.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458
Recommended commit type: fix(bridge):

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Implementation Claim

The governed implementation-proposal filing service now ranks every active
PAUTH that already covers the requested work item. Exact singleton coverage
wins over explicit multi-work-item coverage, smaller explicit lists win over
larger lists, and unrestricted project-membership coverage is the final
fallback. The candidate list is sorted independently of database insertion
order. Multiple candidates tied at the best rank fail before content
construction, candidate preflights, or writer invocation.

One structured candidate-rank ledger now flows through the internal project
state and filing result. Dry-run JSON, live JSON, live text output, and the
generated proposal metadata disclose the selected PAUTH, each covering
candidate's coverage class, included-work-item count, specificity rank, and
selected flag. Existing restrictive coverage semantics are unchanged.

No dispatcher, TAFE, harness, runtime, project, PAUTH, work-item, credential,
Git, deployment, release, or unrelated source mutation occurred.

## Governed Start Evidence

- Work-intent claim: `go_implementation`, rowid `33118`, session
  `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, acquired
  `2026-07-18T17:10:46Z`.
- Schema-v3 implementation-start packet:
  `sha256:f2e79f7db75343f69fdc74725daf6ce6317affe8220895de324e06e3fdbbe055`.
- Pre-start packet:
  `sha256:d97a6a21de103d74026e8625c18ff4c4dcdbef49c7995f3efcd3cdca0d396794`.
- Exact V2 PAUTH:
  `PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718`,
  active and restricted to `WI-5458`.
- Operation-time authorization returned `authorized: true` for each of the
  three target paths immediately before its first mutation.

## Preimage And Result Hashes

| Target | Preimage SHA-256 | Implemented SHA-256 |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` | `5DB92B0B3462099350A7F2F6F6C61841755B3BF223143BF33959A007A16791F2` | `FD543C0327640E0EEAC1CF3F095A5F53CE15559ABA5D1E796AA760EA9A18DAE6` |
| `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` | `E2C325C924256A94048AE578FFBB99D43B8ED53BA0258E0D671D26FD41ED39C4` | `9012B51CDEB1E7599918FF38D8D6D7A2E54658517B270D2F34A00A42FE36F550` |
| `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` | `44D2AFAD4E1DD0D28439C9B8F60897EF51F1EED38FECA95E2A8ACB953C16865D` | `71DB09A6BE8C6428C5DD9614BE34114DBDCB98C24EAFB725D64D9E8F37200A8E` |

The three preimages are the exact clean bytes from focused predecessor commit
`2c23cef7215d82dd8d177a4b90417efb983749a2`. Predecessor commits
`435d45b77ca7299b38da4ccfe71648fd47d21637`,
`bb539c8148ed8c4477c65c5fd0f7aa2841d6adc0`, and `2c23cef7` are all
ancestors of current HEAD.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
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

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded governed defect-repair program and the exact WI-5458 V2 PAUTH.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps
  dispatcher configuration and runtime mutation outside this implementation.
- No new owner decision is required. Every proposal, claim, start,
  operation-time, independent-verification, and focused-finalization gate
  remains intact.

## Prior Deliberations

- `bridge/gtkb-wi5458-proposal-pauth-precedence-005.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-006.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded
  owner-authorized defect-remediation envelope.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - durable
  prohibition on dispatcher-configuration mutation during this work.
- `DELIB-20266083` - owner decision establishing restrictive
  `included_work_item_ids` semantics.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `gt projects show-authorization` confirmed the selected V2 PAUTH active, exact-project linked, and restricted to `WI-5458`; schema-v3 start selected the same ID. |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | Focused tests cover exact singleton, two- and three-item explicit lists, unrestricted fallback, and equal-rank ambiguity without broadening `_authorization_covers_work_item`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Exact claim plus packet `sha256:f2e79f...` authorized all three and only the three declared targets; per-target validation returned `authorized: true`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Ambiguity test observes zero preflights, zero writer calls, and no bridge directory; this report uses the governed implementation-report helper. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Focused live and dry-run tests assert selected PAUTH, project, WI, target paths, and candidate-rank metadata in generated output. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability preflight below passes with no missing required or advisory specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every linked specification to executed evidence; 43 focused tests and every static gate pass. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | `gt projects show` confirmed exact order `WI-5476`, `WI-5420`, `WI-5294`, `WI-5458`, `WI-5466`, `WI-5488`; all three predecessors are committed ancestors. |
| `GOV-STANDING-BACKLOG-001` | Fresh canonical target-name scans found only ordered successor WI-5466 and the canonically withdrawn/no-mutation WI-5484 route; no undisclosed live claimant exists. |
| `ADR-CROSS-HARNESS-PARITY-001` | Selection is implemented in the shared harness-neutral filing service; no harness branch or provider-specific behavior was introduced. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Both established proposal-filing suites pass together, preserving supported interactive-consumer behavior. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI, linked test, PAUTH, GO, claim, start packet, source, tests, and this numbered report remain distinct governed artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation is derived from WI-5458 and its approved numbered bridge chain, with no scratch or noncanonical dependency. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Lifecycle is `REVISED v005 -> independent GO v006 -> implementation -> NEW v007`; independent VERIFIED remains pending. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All three target paths resolve inside `E:\GT-KB`; no adopter or external path changed. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact-path status, SHA-256 hashes, scoped diff-stat, Ruff, format, compile, and `git diff --check` isolate the three reviewed targets amid unrelated shared-worktree dirt. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\test_cli_bridge_propose.py groundtruth-kb\tests\test_cli_bridge_propose.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `gt projects show PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-BRIDGE-PROPOSAL-FILING --json`
- `gt backlog list --contains proposal_filing.py --json`
- `gt backlog list --contains cli_bridge_propose.py --json`
- `gt backlog list --contains test_cli_bridge_propose.py --json`
- `scripts/bridge_applicability_preflight.py` in candidate-content mode
  against the exact completed bytes subsequently filed as this v007.
- `scripts/adr_dcl_clause_preflight.py` in mandatory candidate-content mode
  against the exact completed bytes subsequently filed as this v007.

## Observed Results

- Baseline before implementation: `38 passed`, one pre-existing unknown
  `asyncio_mode` configuration warning.
- Final focused suite: `43 passed`, the same single pre-existing warning.
- Five new cases cover both insertion orders, smaller explicit-list
  precedence, equal-rank rejection with zero publication, and dry-run
  candidate-ledger disclosure.
- Ruff check: `All checks passed!`
- Ruff format: `3 files already formatted`.
- `py_compile`: exit `0`, no output.
- `git diff --check`: exit `0`; only line-ending normalization advisories.
- Scoped diff: three files, `300 insertions`, `5 deletions`.
- Candidate applicability and mandatory clause preflights: PASS as recorded
  below.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`

All unrelated shared-worktree paths are excluded from this report and remain
untouched.

## Recommended Commit Type

- Recommended commit type: `fix(bridge):`
- Diff-stat justification: the delta corrects PAUTH-selection precedence and
  adds focused regression coverage without changing dispatcher or harness
  topology.

```text
     .../src/groundtruth_kb/bridge/proposal_filing.py   | 107 +++++++++++-
     .../src/groundtruth_kb/cli_bridge_propose.py       |  11 ++
     .../groundtruth_kb/test_cli_bridge_propose.py      | 187 +++++++++++++++++++++
     3 files changed, 300 insertions(+), 5 deletions(-)
```

## Acceptance Criteria Status

- [x] Exact singleton PAUTH coverage wins in both insertion orders.
- [x] Smaller explicit lists win; unrestricted project coverage is fallback.
- [x] Equal best ranks fail before content, preflights, writer, or bridge path.
- [x] Dry-run JSON, dry-run text, live JSON, live text, and generated proposal
  metadata disclose the selected PAUTH and ranked candidates.
- [x] The six-member project order is unchanged, with WI-5458 before WI-5466
  and WI-5488 last.
- [x] Fresh target scans found no undisclosed live claimant.
- [x] WI-5476, WI-5420, and WI-5294 focused commits are ancestors; their
  behavior remains green in the combined focused suite.
- [x] Focused tests, Ruff, format, compile, diff, applicability, and mandatory
  clause gates pass.
- [x] No dispatcher/TAFE configuration or runtime, harness state, credential,
  staging, commit, push, deployment, release, or unrelated mutation occurred.

## Risk And Rollback

The intentional residual behavior is fail-closed: two equally specific active
PAUTHs now stop proposal filing until governance removes the ambiguity. That
may surface previously hidden duplicate authorization state, but it prevents
row order from silently widening authority.

Rollback requires separate authority and reverts only the reviewed WI-5458
hunks in the three target files. Rerun the 43-test suite and static gates after
rollback. Project, PAUTH, work-item, bridge, claim, start-packet, verdict, and
commit history remain append-only.

## Pre-Filing Preflight Subsection

- Applicability preflight: PASS against these exact completed candidate bytes;
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`, packet
  `sha256:314e7e54dff035c1e8490eea3292d151f16172ae9a6aa63ea2ec40d797bcaa40`.
- Mandatory clause preflight: PASS against these exact completed candidate
  bytes; five clauses evaluated, four `must_apply`, one `may_apply`, zero
  mandatory evidence gaps, zero blocking gaps, exit `0`.
- First-line role eligibility: active session role is Prime Builder, authorized
  to file the post-implementation `NEW`; current exact thread latest status is
  independent `GO` v006 and the exact `go_implementation` claim is held by
  this report's author session.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
