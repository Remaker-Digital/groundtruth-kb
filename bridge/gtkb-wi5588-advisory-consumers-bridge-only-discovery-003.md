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

# GT-KB Bridge Implementation Report - gtkb-wi5588-advisory-consumers-bridge-only-discovery - 003

bridge_kind: implementation_report
Document: gtkb-wi5588-advisory-consumers-bridge-only-discovery
Version: 003
Responds to: bridge/gtkb-wi5588-advisory-consumers-bridge-only-discovery-002.md
Approved proposal: bridge/gtkb-wi5588-advisory-consumers-bridge-only-discovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5588-ADVISORY-CONSUMERS-2026-07-18
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5588
Recommended commit type: feat:
target_paths: ["scripts/advisory_intake_scanner.py", "scripts/advisory_grilling_gate_lint.py", "scripts/sot_compactness_audit.py", "scripts/benchmarks/advisory_latency.py", "platform_tests/scripts/test_advisory_intake_scanner.py", "platform_tests/scripts/test_advisory_grilling_gate_lint.py", "platform_tests/scripts/test_sot_compactness_audit.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_advisory_candidate_promote.py"]
kb_mutation_in_scope: false

## Implementation Claim

Completed the approved nine-path WI-5588 slice. The advisory intake scanner,
owner-grilling lint, compactness audit, and latency benchmark now discover
advisory authority only from current status-bearing numbered bridge ADVISORY
entries. Retired dropbox discovery, candidate-event-store liveness, legacy
mode-header recognition, and alternate compactness report writing are removed
from these consumers. The five focused test modules include explicit negative
coverage for legacy dropbox, unnumbered, non-ADVISORY, superseded, and retired
writer/source modes.

Implementation began only after the current Prime Builder session acquired the
matching GO claim and created a schema-v3 implementation packet:

- claim session: `019f9329-a174-7763-8f7e-29679f39e6bd`
- packet hash: `sha256:a2ba4c6c8041b02dddaaa7f5411a4f64e17c007b54b094f3923d619c1519312e`
- pre-start packet hash: `sha256:fa7ec3d7dd281488f2a840ed15e1211ba4b96492174e448ced896756e3ee867b`
- authorization envelope hash: `E51E42C659B9609657FBE7A29EE0C49E74B88DA1841F4CAAB83663DBE0BF2C48`
- operation-time decision: allowed for all four source and five test targets at
  `2026-07-29T21:05:08Z`

## Specification Links

- `DCL-SUPERSEDED-SOT-LEAKAGE-001`
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
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Owner Decisions / Input

No new owner decision is required. The implementation carries forward
`DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` and the active exact-WI
authorization named above. It does not infer dispatcher, TAFE, credential,
deployment, release, push, history-rewrite, cleanup, or external-system
authority.

## KB Mutation Disposition

No Knowledge Database or MemBase mutation was performed or is claimed by this
report. References to MemBase describe read-only liveness checks performed by
the changed scanner; `groundtruth.db` is intentionally outside `target_paths`.

## Prior Deliberations

- `bridge/gtkb-wi5588-advisory-consumers-bridge-only-discovery-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5588-advisory-consumers-bridge-only-discovery-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Focused tests reject legacy dropbox, retired writer/source modes, unnumbered entries, and superseded/non-ADVISORY latest entries; 67 passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work followed v001 proposal -> independent v002 GO -> matching claim/start -> canonical v003 report filing. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Proposal, GO, schema-v3 authorization evidence, tests, and this implementation report are durable governed artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All 23 v001 specification links are carried forward in this report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Five focused test modules: 67 passed; Ruff check and format check passed on all nine paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report preserves exact PAUTH, project, WI, proposal, GO, and nine target paths. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Grilling-gate tests preserve all five dispositions, required adopt/adapt enumeration, waiver logging, and warning-only behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Every changed path and all generated evidence remain inside `E:/GT-KB`; no adopter path changed. |
| `GOV-STANDING-BACKLOG-001` | WI-5588 remains the exact open work item linked to the active project and this bridge chain. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Scanner/lint behavior is deterministic Python and focused tests exercise ordinary CLI plus Stop-hook behavior without harness-specific interception. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Current bridge status and MemBase work-item linkage replace scratch/dropbox candidate authority. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Current latest numbered status controls discovery; superseded ADVISORY entries are explicitly excluded by tests. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | All four production scripts use numbered bridge ADVISORY as the sole advisory discovery input; negative fixtures prove legacy inputs have no authority. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Intake and lint consume each thread's latest numbered status; latency uses current numbered files in the requested time window. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Schema-v3 packet selected active PAUTH version 1 and classified exactly four source plus five test targets. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Protected edits followed independent GO, matching live claim, and successful implementation-start packet. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Normalized envelope `E51E42...2C48` allowed the exact WI-5588 target cohort and excluded every other path. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Registered operation-time evaluator returned `allowed` at packet creation and implementation start. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Work ran in the declared build envelope; dispatcher activation/mutation was not attempted. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Final diff contains only the approved consumers/tests and adds no dispatcher, TAFE, or harness-runtime access. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Exact source/test-only build operation and exclusions are recorded in the packet and report. |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped status/diff isolated exactly nine targets; 164 unrelated dirty paths and six foreign staged paths were preserved. `git diff --check` passed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Full focused matrix passed 67/67; no alternate advisory store, configuration, dispatcher, or runtime state was added. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_advisory_intake_scanner.py platform_tests/scripts/test_advisory_grilling_gate_lint.py platform_tests/scripts/test_sot_compactness_audit.py platform_tests/scripts/test_benchmark_advisory_latency.py platform_tests/scripts/test_advisory_candidate_promote.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/ruff.exe check <all-nine-targets>`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check <all-nine-targets>`
- `git diff --check -- <all-nine-targets>`
- `rg -n "scan_intake_advisories\\(" -g "*.py"` and a bounded scan for retired `--source` callers.

## Observed Results

- Pytest collected 67 items: **67 passed**, with one pre-existing warning for the unknown `asyncio_mode` pytest option.
- Ruff check: **All checks passed**.
- Ruff format check: **9 files already formatted**.
- `git diff --check`: exit 0; only informational Windows LF-to-CRLF working-copy notices.
- Caller scan found no production or external Python caller of `scan_intake_advisories` and no bounded command surface invoking the retired scanner `--source` option.

## Files Changed

- `platform_tests/scripts/test_advisory_candidate_promote.py`
- `platform_tests/scripts/test_advisory_grilling_gate_lint.py`
- `platform_tests/scripts/test_advisory_intake_scanner.py`
- `platform_tests/scripts/test_benchmark_advisory_latency.py`
- `platform_tests/scripts/test_sot_compactness_audit.py`
- `scripts/advisory_grilling_gate_lint.py`
- `scripts/advisory_intake_scanner.py`
- `scripts/benchmarks/advisory_latency.py`
- `scripts/sot_compactness_audit.py`

Excluded out-of-scope dirty paths: 164.

Postimage SHA-256 evidence:

- `scripts/advisory_intake_scanner.py`: `D8B2E91670CCE301B2732E1588377D109F41579159CDAA46A3DE8639EAB68DA0`
- `scripts/advisory_grilling_gate_lint.py`: `0EF53AAF81FE295A7BF3B1A5B7F88FE25FED43FB0317E170FB8128C3BA180753`
- `scripts/sot_compactness_audit.py`: `25BFD5CBB1BC0D03D5DF4EC02AC352875C380C27FEA990026AB2B552D04D74F0`
- `scripts/benchmarks/advisory_latency.py`: `875D8C37A565D61924F3C32C8CE1F589AC667BA79DE13C70F72B6E84733E7BCF`
- `platform_tests/scripts/test_advisory_intake_scanner.py`: `4D8F6F3BF375CB8E2B349E83CBB300AA4A0FBAB8C69CBDDD7DD51D7B349E7D75`
- `platform_tests/scripts/test_advisory_grilling_gate_lint.py`: `DC1C86929B132316AA778156B2FD0535710959E88A7F8B5B573485A36CE883FB`
- `platform_tests/scripts/test_sot_compactness_audit.py`: `44CAE7D6E8BE72F2A1E6990E9041E9388D2AE4205D4B1902B3A04A775B442BA6`
- `platform_tests/scripts/test_benchmark_advisory_latency.py`: `42914EDAB24437B468B1A1ED9EC36E8BC109D2CC5AEBC24E8EFC1EA55AF4F679`
- `platform_tests/scripts/test_advisory_candidate_promote.py`: `0149AA260CEA4B89538B3AF9A3CF3F62D9F03A53F2CFD6B287C2EA7F4210B197`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     .../scripts/test_advisory_candidate_promote.py     |   4 +-
     .../scripts/test_advisory_grilling_gate_lint.py    | 173 ++++++------
     .../scripts/test_advisory_intake_scanner.py        | 290 +++++++++------------
     .../scripts/test_benchmark_advisory_latency.py     |  31 +++
     .../scripts/test_sot_compactness_audit.py          |  33 +--
     scripts/advisory_grilling_gate_lint.py             |  63 +++--
     scripts/advisory_intake_scanner.py                 |  48 ++--
     scripts/benchmarks/advisory_latency.py             |  73 +++---
     scripts/sot_compactness_audit.py                   |  40 +--
     9 files changed, 357 insertions(+), 398 deletions(-)
```

## Acceptance Criteria Status

- All four production scripts use status-bearing numbered bridge ADVISORY entries as their only advisory discovery input and do not create or load an alternate advisory store.
- The focused tests prove bridge-only discovery, owner-grilling preservation, canonical evidence metrics, and fail-closed rejection of unsupported inputs.
- The implementation diff contains only the nine declared target paths and makes no configuration, dispatcher, TAFE, runtime-state, credential, deployment, release, push, history-rewrite, or cleanup mutation.
- The implementation report carries forward every linked specification, maps each to executed evidence, and reports exact pytest and both ruff results.

## Risk And Rollback

Residual risk is limited to existing bridge documents whose advisory prose does
not carry a unique disposition in a recognized section; they remain
fail-closed/excluded rather than being guessed into intake. Latency continues to
use filesystem modification time for numbered bridge events because the
approved benchmark surface is file-based; the focused window/citation tests
cover deterministic behavior.

Rollback requires separate authority to revert only these nine source/test
postimages and rerun the five focused test modules plus both Ruff commands.
Bridge files, claim/start evidence, and this report remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
