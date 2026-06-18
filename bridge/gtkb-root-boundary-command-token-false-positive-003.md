NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019edcc1-18de-74d2-b062-b41eb58e7395
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; PowerShell; approval_policy_never

# GT-KB Bridge Implementation Report - gtkb-root-boundary-command-token-false-positive - 003

bridge_kind: implementation_report
Document: gtkb-root-boundary-command-token-false-positive
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-root-boundary-command-token-false-positive-002.md
Approved proposal: bridge/gtkb-root-boundary-command-token-false-positive-001.md
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-4602 root-boundary command-token false-positive fix.

The shared `groundtruth_kb.enforcement` command scanner now requires drive-letter absolute path candidates to start at a token boundary, so regex/prose snippets such as `Document:\s*` are not interpreted as standalone Windows paths like `t:\s*`. The rooted slash path branch now also excludes URL `://` contexts from rooted-path matching, preserving the existing corpus requirement that URLs are skipped as non-filesystem tokens.

The false-positive corpus now includes:

- a pass case for a drive-shaped regex/prose substring;
- a pass case for a quoted in-root Windows absolute bridge path.

No formal artifact, KB row, deployment, credential, or destructive repository operation was changed.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - Protected source, test, and configuration mutations waited for Loyal Opposition `GO` and a valid implementation-start packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active May29 Hygiene project authorization covers WI-4602.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - This report is filed as the next numbered bridge artifact after the GO verdict.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The approved proposal cites the active project authorization, project, and work item.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The approved proposal and this report carry the governing specification surfaces forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification below maps linked requirements to executed tests and observed results.
- `GOV-STANDING-BACKLOG-001` - WI-4602 remains the governed backlog authority for this defect until verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Root-boundary enforcement still blocks genuine out-of-root Windows, UNC, and MSYS paths.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - The classifier remains deterministic regex/Python logic with regression tests.
- `SPEC-AUQ-POLICY-ENGINE-001` - The policy engine now avoids the specific false block while preserving true blocks.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Hook coverage confirms the shared parser still behaves through Claude/Codex directive adapters.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The observed defect is preserved through WI, proposal, regression corpus, and implementation report artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The regression corpus is executable artifact evidence for the fixed behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The work remains in bridge verification flow until Loyal Opposition returns `VERIFIED`.

## Owner Decisions / Input

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorizes autonomous proposal work for unimplemented work items linked to `PROJECT-GTKB-MAY29-HYGIENE` through `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`.
- No new owner decision was required. This implementation did not request a waiver, production deployment, credential action, destructive cleanup, or formal artifact mutation.

## Prior Deliberations

- `bridge/gtkb-root-boundary-command-token-false-positive-001.md` - Approved implementation proposal for WI-4602.
- `bridge/gtkb-root-boundary-command-token-false-positive-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-fab-14-gate-fp-feedback-loop-013.md` - Prior FAB-14 false-positive corpus and parser-maintenance context.
- `bridge/gtkb-implementation-start-authorization-gate-005.md` - Prior escaped bridge payload regression precedent.
- `WI-4602` - May29 Hygiene work item for the escaped bridge path false-positive.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Created implementation-start packet before source/config edits: `python scripts\implementation_authorization.py begin --bridge-id gtkb-root-boundary-command-token-false-positive`, packet `sha256:5624272c77f5c2900aef6e3c0f63ddd08f35c45852cbebd1beff6b81e6de3272`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `platform_tests/scripts/test_gate_fp_corpus.py` passed 15 tests, including genuine out-of-root drive, UNC, and MSYS block cases plus in-root pass cases. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | The fix is deterministic parser logic in `groundtruth_kb.enforcement`; no LLM classifier is involved. Ruff and focused pytest passed. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Corpus tests prove the intended policy distinction: regex/prose and URLs pass, genuine blocked paths still fail closed. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `platform_tests/scripts/test_fab14_directive_hook_coverage.py` passed 5 tests against Claude/Codex hook coverage. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specification set. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The executed tests below map directly to the parser and hook requirements. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This implementation report is filed as `bridge/gtkb-root-boundary-command-token-false-positive-003.md` through the governed report helper. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-root-boundary-command-token-false-positive`
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-root-boundary-command-token-false-positive`
- `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py -q --tb=short -o timeout=0`
- `python -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --tb=short -o timeout=0`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py`

## Observed Results

- Work-intent claim acquired for `gtkb-root-boundary-command-token-false-positive`, TTL through `2026-06-18T22:50:12Z`.
- Implementation-start authorization succeeded with packet `sha256:5624272c77f5c2900aef6e3c0f63ddd08f35c45852cbebd1beff6b81e6de3272`.
- `platform_tests/scripts/test_gate_fp_corpus.py`: `15 passed in 5.22s`.
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`: `5 passed in 3.87s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `3 files already formatted`.

## Files Changed

- `config/governance/gate-fp-corpus.toml`
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `bridge/gtkb-root-boundary-command-token-false-positive-003.md`

The authorized hook coverage test file was read and executed but not modified.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: the diff repairs root-boundary command parsing behavior and adds regression corpus coverage without adding a new command surface.

```text
 config/governance/gate-fp-corpus.toml             | 8 ++++++++
 groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py | 9 ++++++---
```

## Acceptance Criteria Status

- [x] In-root bridge/proposal command text that includes escaped or quoted path snippets is allowed by `check_bash_command`.
- [x] Regex/prose snippets containing non-token drive-shaped substrings are not classified as filesystem paths.
- [x] Genuine out-of-root Windows drive-letter, UNC, and MSYS paths remain blocked.
- [x] Focused parser tests pass.
- [x] Hook-level coverage remains passing.
- [x] Ruff check and format pass for touched source/test/config surfaces.
- [x] No production deployment, credential action, destructive cleanup, or formal artifact mutation is included.

## Risk And Rollback

Risk is low to moderate because the parser enforces the project root boundary. The change is intentionally narrow: it only tightens token-boundary recognition for drive-letter and rooted slash candidates. Existing true-block corpus cases for out-of-root drive-letter, UNC, and MSYS paths remain passing.

Rollback is a scoped revert of the parser regex comment/code change and the two added corpus pass cases. A rollback would restore the WI-4602 false-positive and should go through a follow-up bridge review if needed.

## Loyal Opposition Asks

1. Verify the parser boundary change against the linked root-boundary, deterministic-classifier, and cross-harness enforcement requirements.
2. Confirm the report includes enough executed evidence for `VERIFIED`.
