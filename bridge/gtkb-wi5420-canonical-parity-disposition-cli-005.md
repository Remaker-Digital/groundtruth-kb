REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5420 Revised Test-Fixture Parity Correction

bridge_kind: prime_proposal
Document: gtkb-wi5420-canonical-parity-disposition-cli
Version: 005
Responds to: bridge/gtkb-wi5420-canonical-parity-disposition-cli-004.md
Carries forward approved scope from: bridge/gtkb-wi5420-canonical-parity-disposition-cli-001.md
Corrects implementation report: bridge/gtkb-wi5420-canonical-parity-disposition-cli-003.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5420

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Revision Claim

This revision accepts the independent finding in version 004 and narrows the
remaining implementation delta to the two failing test call sites in
`platform_tests/groundtruth_kb/test_cli_bridge_propose.py`. The tests currently
inject author metadata and invoke the real compliance audit without first
calling the same governed envelope normalizer used by both production bridge
writer paths. They therefore fail on the newer artifact-head envelope gate
before reaching the WI-5420 parity behavior they are intended to prove.

The correction will pass each generated proposal through
`writer.normalize_bridge_envelope_head(...)` immediately after the test author
metadata helper and before `writer._run_bridge_compliance_audit(...)`. This
matches the production order in both bridge writer paths: credential handling,
author metadata, envelope normalization, then compliance audit.

The accepted production implementation in
`groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` and
`groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` is carried forward
unchanged. Those two source targets are included so the final implementation
report and verification transaction can account for the complete previously
approved WI-5420 diff, but this correction does not authorize additional source
behavior changes.

## Response To Version 004

### Blocking finding - focused test evidence did not reproduce

Accepted. Prime Builder independently reran the exact focused command on
2026-07-18 UTC and reproduced `2 failed, 10 passed, 1 warning`. Both failures
name the missing line-2/line-3 bridge artifact-head envelope and occur before
the tests' parity assertions.

Correction: normalize each test proposal through the governed writer's
`normalize_bridge_envelope_head` function before invoking the real compliance
audit. The positive test must then return `decision == "pass"` and the omission
test must reach and assert the intended `Cross-Harness Disposition` denial.

### Non-blocking observation - production path needed fresh confirmation

Addressed through production-sequence parity rather than a second writer. The
test calls the same normalizer and real compliance audit exposed by the
production bridge writer module, in the same order used by both governed
production write paths. The correction will also retain the existing CLI filing
tests and rerun the adjacent compliance-gate suite. No alternate bridge writer,
queue, or dispatcher path is introduced.

## Requirement Sufficiency

Existing requirements sufficient.

The original approved proposal, version 004 finding, the now-canonical
artifact-head envelope specifications, and the active project authorization
fully define this test-only correction. No new owner choice or formal
requirement is needed.

## Current-Byte Boundary

Immediately before implementation, Prime Builder must confirm these exact
candidate bytes or return for renewed review:

- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`:
  `sha256:a264066ceb32e20a8086b82992c2363aea8a5e364028a62e339e77d75383890c`
  and read-only for this correction.
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`:
  `sha256:e634d1d2036eb77c5d25f02f45300d9b2cb854de74793d1c1b339ef1755adca9`
  and read-only for this correction.
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`:
  `sha256:89a2c9f4e522a57c5acc084ff472e55da7e98ee6af78e29671f40442b08061f4`
  before the two test-call-site edits.

All three paths are currently modified relative to committed HEAD solely as the
carried-forward WI-5420 implementation surface described in version 003. The
implementation report must record the post-correction hash of the test module
and prove the two source hashes remain unchanged.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
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
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` records the owner
  decision that status remains line 1 and governed writers materialize
  `::init` and `::open` at lines 2 and 3. The proposed test correction applies
  that decision to the real-audit fixture instead of bypassing it.
- `bridge/gtkb-wi5420-canonical-parity-disposition-cli-002.md` records the
  independent GO for the original production implementation.
- `bridge/gtkb-wi5420-canonical-parity-disposition-cli-004.md` records the
  independently reproduced failure and the required test-only remedy.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE`
  remains active and permits the bridge, source, test, metadata, and governance
  evidence classes needed for WI-5420 while preserving its registered
  prohibited operations.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` supplies the
  controlling owner decision for status-first envelope placement.

## Proposed Scope

- Modify only the two real-audit call sites in
  `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`.
- Normalize the metadata-bearing generated proposal immediately before each
  real compliance audit.
- Preserve the positive test's explicit-disposition pass assertion.
- Preserve the omission test's fail-closed `Cross-Harness Disposition` denial
  assertion.
- Keep both production source files byte-identical to the hashes above.
- Run the focused and adjacent suites plus scoped Ruff and diff checks.
- File a corrected implementation report carrying all sixteen linked
  specifications and current executed evidence.
- Do not mutate dispatcher configuration, dispatcher runtime state, TAFE,
  harness state, credentials, deployment, release state, Git history, or any
  path outside the three exact targets.

## Specification-Derived Verification Plan

| Specification | Required executed verification |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run both real-audit tests; explicit dispositions must pass and omission must reach the parity denial. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Validate the exact GO, claim, implementation-start packet, three target paths, and governed report filing. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve the numbered proposal/report/verdict chain and WI-5420 MemBase linkage. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live applicability preflights with all sixteen specifications cited. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with exact commands and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Audit project authorization, project, work item, and exact target-path headers. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Confirm the CLI still consumes explicit caller dispositions and does not infer a waiver or owner choice. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all changed paths remain GT-KB platform paths and no adopter path appears. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5420 and its linked test remain the durable work authority. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Execute the real compliance audit in both the passing and denied test cases. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Verify the CLI produces durable structured proposal content and fails closed before publication. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the canonical proposal lifecycle and writer remain unchanged. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify generated text retains distinct caller-supplied Claude and Codex dispositions. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare pre/post hashes and `git diff --name-only` for exactly the three carried-forward WI-5420 targets. |
| `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` | Assert normalized content keeps `NEW` on line 1 and materializes `::init gtkb lo` and `::open build` on lines 2 and 3 before audit. |
| `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` | Exercise the governed normalizer rather than hand-authoring envelope lines, then execute the real audit. |

## Acceptance Criteria

- The focused proposal-filing suite reports 12 passed with no WI-5420 failure.
- The positive real-audit test passes after governed envelope normalization.
- The omitted-disposition test reaches the intended parity gate and raises a
  `Cross-Harness Disposition` denial.
- The adjacent diagnostic suite has no new WI-5420 failures; any unrelated
  failures are enumerated and matched to existing governed work.
- Scoped `ruff check`, `ruff format --check`, and `git diff --check` pass.
- The two production source SHA-256 values remain exactly unchanged.
- The implementation report includes all sixteen specification-to-test rows,
  exact commands, observed results, and the final test-module SHA-256.

## Applicability Preflight

Candidate applicability executed against this revision content and reported:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`

## Clause Applicability

The mandatory clause preflight executed against this revision content and
reported five clauses evaluated, three `must_apply`, two `may_apply`, zero
evidence gaps in `must_apply` clauses, zero blocking gaps, and exit code zero.

## Risks / Rollback

The correction is low risk and test-only. Its main risk is masking a real
production-order defect by normalizing the wrong content or at the wrong point;
the direct line-position assertions and real audit prevent that.

Rollback is a governed revert of only the two test call-site edits. The accepted
production source bytes and numbered bridge history remain unchanged.

## Files Expected To Change

- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`

The two production source files remain in the authorized target inventory for
complete WI-5420 finalization but are not expected to change in this correction.
