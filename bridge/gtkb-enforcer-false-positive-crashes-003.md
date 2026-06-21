NEW
author_identity: prime-builder/antigravity
author_harness_id: C
author_session_context_id: test-session-123
author_model: Gemini 1.5 Pro
author_model_version: Gemini 1.5 Pro (High)
author_model_configuration: Prime Builder implementation

# Post-Implementation Report - Remediate directive enforcer false-positive blocks causing subprocess crashes

bridge_kind: implementation_report
Document: gtkb-enforcer-false-positive-crashes
Version: 003 (NEW; post-implementation report)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4732
Recommended commit type: fix

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "config/governance/gate-fp-corpus.toml"]

## Implementation Summary

We have remediated the false-positive path-boundary violations in the shared `groundtruth_kb.enforcement` token parser that were triggering tool-denial exits and subprocess crashes:
1. **UNC Pattern Tightened**: Updated `_UNC_ABSOLUTE` regex to require a host server name and a separator (`[\\/]`).
2. **Comment and Double-slash Filtering**: Updated `_classify_path_token` to skip tokens consisting solely of slashes and dots, and to require at least one separator in the remainder of any token starting with `//` or `\\`.
3. **Harness Directory Exemption**: Allowed path checking for local harness-specific directories (`.claude`, `.codex`, `.gemini`, `.api-harness`) by matching them against resolved path parts in `check_path_boundary`.
4. **Regression Corpus Updated**: Added test cases to `config/governance/gate-fp-corpus.toml` for regex double backslashes, double forward-slash comments, and harness-local paths under `C:\Users\`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This proposal is filed as the first version in a canonical numbered bridge chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The remediation is documented and tracked as a work item and bridge thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the work to the governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps spec requirements to tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal is linked to an active project and work item.
- `SPEC-AUQ-POLICY-ENGINE-001` - The parser is tightened to reduce false positives while preserving true positives.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The project root boundary is preserved for all non-harness paths.
- `GOV-STANDING-BACKLOG-001` - The work is tracked under the backlog work item WI-4732.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Shared parser edits preserve hook behavior parity across harnesses.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The regression corpus is updated as executable artifact evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The thread remains in implementation lifecycle until LO verification.

## Prior Deliberations

- `DELIB-20265277` - Loyal Opposition Review - Closure of Duplicate Fail-Soft Registry Thread
- `DELIB-20265498` - Loyal Opposition GO verdict - WI-4703 dispatch non-transient fast-trip
- `DELIB-20261101` - Loyal Opposition Review - Envelope Open Disclosure Refactor (REVISED-1 NO-GO)
- `DELIB-20261244` - Loyal Opposition Review - Envelope Open Disclosure Refactor (REVISED-1 NO-GO)
- `DELIB-20261758` - Bridge thread: gtkb-wi3326-project-rehome-executable-packet-repair (6 versions, VERIFIED)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` - Active project authorization that covers all unimplemented work items linked to `PROJECT-GTKB-MAY29-HYGIENE`, including `WI-4732`.

## Specification-Derived Verification Results

| Spec / governing surface | Executed verification evidence | Expected Outcome | Observed Result | Status |
| --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py` | FP corpus tests pass (including new cases) and true blocks still fail closed. | 19 passed | PASS |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run `python -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py` | Hook coverage tests pass. | 5 passed | PASS |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Run `python -m ruff check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` | Python lint checks pass. | All checks passed! | PASS |

## Acceptance Status

- [x] Command text that includes double backslashes or double slashes in regex is not classified as an out-of-root absolute path violation.
- [x] Paths inside allowed harness-local subdirectories under `C:\Users\` are permitted.
- [x] Genuine out-of-root Windows drive-letter, UNC, and MSYS paths remain blocked.
- [x] Focused parser and hook coverage tests pass.
- [x] Ruff check and format check pass.

## Risks / Rollback

Risk is low as changes only narrow the classification of UNC and double-slash paths, and permit specific harness-internal subdirectories.
Rollback is a git revert of the parser changes in `__init__.py` and the added test cases in `gate-fp-corpus.toml`.
