NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5420 Corrected Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5420-canonical-parity-disposition-cli
Version: 007
Responds to GO: bridge/gtkb-wi5420-canonical-parity-disposition-cli-006.md
Approved proposal: bridge/gtkb-wi5420-canonical-parity-disposition-cli-005.md
Corrects implementation report: bridge/gtkb-wi5420-canonical-parity-disposition-cli-003.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5420

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: test | governance_evidence
kb_mutation_in_scope: false
requires_verification: true
Recommended commit type: feat:

## Implementation Claim

The version-006 test-fixture correction is complete. The two WI-5420 real-audit
fixtures now pass metadata-bearing generated proposal content through
`writer.normalize_bridge_envelope_head(...)` immediately before
`writer._run_bridge_compliance_audit(...)`. The positive fixture reaches and
passes the real compliance audit; the omitted-disposition fixture reaches and
asserts the intended `Cross-Harness Disposition` denial.

The accepted production implementation remains unchanged from version 003.
Both production source hashes are byte-identical to the version-005 and
version-006 boundary. No dispatcher configuration, dispatcher runtime state,
TAFE, harness state, credential, deployment, release, Git history, or MemBase
mutation was performed.

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

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE`
  remains active for `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` and covers
  WI-5420 through active project membership.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` establishes the
  status-first bridge envelope placement exercised by the corrected fixtures.
- The owner's dispatcher-configuration hold was honored: this implementation
  did not inspect or mutate dispatcher configuration or runtime state.

## Prior Deliberations

- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` records the owner
  decision that status remains line 1 and governed writers materialize the
  `::init` and `::open` envelope lines.
- `bridge/gtkb-wi5420-canonical-parity-disposition-cli-004.md` records the
  independent NO-GO that identified the two fixture failures.
- `bridge/gtkb-wi5420-canonical-parity-disposition-cli-005.md` narrows the
  correction to the two real-audit call sites.
- `bridge/gtkb-wi5420-canonical-parity-disposition-cli-006.md` independently
  verifies the byte boundary, root cause, and authorized remedy.

## Specification-Derived Verification Mapping

| Specification | Executed verification evidence |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | The positive and omitted-disposition real-audit fixtures both executed; explicit dispositions passed and omission reached the parity denial. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The latest independent GO, Prime Builder claim, schema-v3 implementation-start packet, exact three-target authorization, and governed report helper were validated. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5420, the numbered bridge chain, implementation bytes, executed evidence, and this report preserve the governed lifecycle. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All sixteen approved links are carried forward and candidate applicability is executed against this exact report content before filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping carries every linked specification to an executed command or direct byte/state verification with observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live reads confirmed the active PAUTH, matching project, WI-5420 membership, and exact target-path headers. |
| `SPEC-AUQ-POLICY-ENGINE-001` | The focused suite proves dispositions remain explicit caller inputs and omission remains fail-closed; no waiver or owner choice is inferred. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The three changed paths are in-root GT-KB platform source/test paths and no adopter path is present. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5420 --json` confirmed WI-5420 version 4 remains open/backlogged in the authorized project; no duplicate or unauthorized backlog mutation was made. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Both corrected tests execute the real bridge compliance audit rather than a mocked parity result. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The accepted production path emits durable structured proposal content, while malformed or missing parity dispositions remain denied. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The canonical proposal writer and numbered NEW/GO/NEW lifecycle remain in use; no alternate writer or queue was introduced. |
| `ADR-CROSS-HARNESS-PARITY-001` | The focused suite retains distinct caller-supplied Claude and Codex disposition statements and verifies them through the real audit. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact hashes, three-target diff inventory, scoped Ruff gates, and scoped `git diff --check` isolate WI-5420 from unrelated worktree changes. |
| `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` | Both fixtures call the governed normalizer before audit; the focused suite passes all 12 tests. |
| `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` | Envelope lines are produced by `normalize_bridge_envelope_head`, not hand-authored in either fixture, and the resulting content passes the real gate ordering. |

## Commands Run And Observed Results

1. Pre-correction focused baseline:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short`
   -> `2 failed, 10 passed, 1 warning`. Both failures were the exact
   artifact-head-envelope failures recorded by versions 004 through 006.
2. Final focused suite:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short`
   -> `12 passed, 1 warning in 9.19s`.
3. Adjacent diagnostic suite:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q --tb=short`
   -> `13 failed, 38 passed, 1 warning in 10.21s`. The WI-5420 module passed
   12/12. The adjacent module returned exactly the 13 pre-existing failures
   reconciled in versions 004 and 006, not 15.
4. Scoped lint:
   `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
   -> `All checks passed!`.
5. Scoped format:
   `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
   -> `1 file already formatted`.
6. Scoped whitespace check:
   `git diff --check -- platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
   -> exit `0`; Git emitted only its working-copy LF-to-CRLF warning.
7. Exact-target authorization:
   `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target <each exact target>`
   -> all three targets returned `"authorized": true`.
8. Report plan:
   `groundtruth-kb/.venv/Scripts/python.exe .claude/skills/bridge/helpers/impl_report_bridge.py plan gtkb-wi5420-canonical-parity-disposition-cli --compact`
   -> latest status `GO`, GO file version 006, next version 007, all sixteen
   linked specifications, exactly three included changed files.

The one warning in both pytest runs is the repository's existing
`PytestConfigWarning: Unknown config option: asyncio_mode`.

## Adjacent Failure Reconciliation

The 13 adjacent failures are outside the WI-5420 test module and match the
pre-existing count independently recorded in versions 004 and 006:

- `test_harness_surface_without_disposition_denied`: live and template.
- `test_placeholder_disposition_denied`: live and template.
- `test_bullet_only_disposition_denied`: live and template.
- `test_blank_bullet_disposition_denied`: live and template.
- `test_harness_surface_with_concrete_disposition_passes`: live and template.
- `test_off_surface_without_disposition_not_triggered`: live and template.
- `test_template_and_active_hook_byte_identical`: one LF/CRLF byte mismatch.

The six live/template pairs fail earlier on the artifact-head-envelope or live
project-authorization fixture gates. The byte-identical test reports only the
pre-existing line-ending mismatch. No adjacent file was modified.

## Exact Byte And Scope Evidence

- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`:
  `sha256:a264066ceb32e20a8086b82992c2363aea8a5e364028a62e339e77d75383890c`
  - unchanged from the approved read-only boundary.
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`:
  `sha256:e634d1d2036eb77c5d25f02f45300d9b2cb854de74793d1c1b339ef1755adca9`
  - unchanged from the approved read-only boundary.
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`:
  `sha256:a8982154061c7beb8562de8befdd42df5bedc849057730b1d24b1704d0d5c179`
  - changed from the approved pre-correction hash
  `89a2c9f4e522a57c5acc084ff472e55da7e98ee6af78e29671f40442b08061f4`.

Scoped diff summary:

```text
3 files changed, 201 insertions(+), 2 deletions(-)
```

The three carried-forward WI-5420 implementation paths are the only included
changed files. No dispatcher, TAFE, harness-state, credential, Git-history,
release, deployment, adopter, or MemBase path was touched by this correction.

## Acceptance Criteria Status

- PASS: focused proposal-filing suite reports 12/12 passed.
- PASS: the positive fixture passes after governed envelope normalization.
- PASS: omission reaches and asserts the intended parity denial.
- PASS: adjacent failures returned from 15 to the exact 13 pre-existing count.
- PASS: scoped Ruff lint, Ruff format, and diff checks pass.
- PASS: both production source hashes remain exact.
- PASS: the test hash changed from the approved pre-correction boundary.
- PASS: all sixteen specification mappings and executed evidence are present.

## Applicability Preflight

Candidate applicability executed against the exact version-007 report content
before filing and reported:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`

## Clause Applicability

The mandatory clause preflight executed against the exact version-007 report
content before filing and reported five clauses evaluated, four `must_apply`,
one `may_apply`, zero evidence gaps in `must_apply` clauses, zero blocking
gaps, and exit code zero.

## Risk And Rollback

Residual risk is limited to the adjacent suite's already-tracked fixture and
line-ending failures. They do not impair the focused WI-5420 behavior, and this
correction does not modify their test or hook paths.

Rollback is a governed revert of only the two normalizer call-site edits in
`platform_tests/groundtruth_kb/test_cli_bridge_propose.py`. The accepted
production source bytes and numbered bridge history remain unchanged.

## Loyal Opposition Ask

Independently verify the implementation against all sixteen linked
specifications and the executed evidence above. Record `VERIFIED` only through
the mandatory atomic commit-finalization helper with the three carried-forward
source/test paths and the numbered verdict artifact; otherwise return `NO-GO`
with exact findings.
