NEW

# Defect-Fix Proposal - Remediate directive enforcer false-positive blocks causing subprocess crashes

bridge_kind: prime_proposal
Document: gtkb-enforcer-false-positive-crashes
Version: 001 (NEW; implementation proposal)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4732

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "config/governance/gate-fp-corpus.toml"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Remediate the false-positive path-boundary violations in the shared `groundtruth_kb.enforcement` command token parser, which trigger tool-denial exits (exit code `4294967295` / `subprocess_execution_failed`) and crash active dispatches to harnesses.

## Defect / Reproduction

The PreToolUse hooks block commands and path arguments due to false positives in the shared parser:
1. Double backslashes (e.g. in regex patterns like `\\-]+\.[\w]+)\b`) match `_UNC_ABSOLUTE` which is overly loose: `_UNC_ABSOLUTE = r"\\\\[^\s|&;'\"]+"`.
2. Double forward-slashes `//` (common in comments or regex) match `_ROOTED` and get classified as a UNC path.
3. Harness-local paths under `C:\Users\micha\.codex` or `.claude` get blocked because they start with the blocked absolute prefix `C:\Users\`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`, `config/governance/gate-fp-corpus.toml`.

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

## Requirement Sufficiency

Existing requirements sufficient.

## Proposed Scope

### [groundtruth-kb]

#### [MODIFY] [__init__.py](file:///E:/GT-KB/groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py)
- Change `_UNC_ABSOLUTE` regex to require a host server name and a separator.
- Update `_classify_path_token` to return `None` if the token consists only of slashes/dots, and to check for a third slash/backslash separator in forward-slash UNC paths to ignore bare `//`.
- Update `check_path_boundary` to allow paths whose parts contain case-insensitive matches for the allowed harness subdirectories: `.claude`, `.codex`, `.gemini`, `.api-harness`.

### [config]

#### [MODIFY] [gate-fp-corpus.toml](file:///E:/GT-KB/config/governance/gate-fp-corpus.toml)
- Add regression test cases for double backslashes in regex, double forward-slashes in commands, and harness-local paths under `C:\Users\`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence | Expected Outcome |
| --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py` | FP corpus tests pass (including new cases) and true blocks still fail closed. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run `python -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py` | Hook coverage tests pass. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Run `python -m ruff check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` | Python lint checks pass. |

## Acceptance Criteria

- [ ] Command text that includes double backslashes or double slashes in regex is not classified as an out-of-root absolute path violation.
- [ ] Paths inside allowed harness-local subdirectories under `C:\Users\` are permitted.
- [ ] Genuine out-of-root Windows drive-letter, UNC, and MSYS paths remain blocked.
- [ ] Focused parser and hook coverage tests pass.
- [ ] Ruff check and format check pass.

## Risks / Rollback

Risk is low as changes only narrow the classification of UNC and double-slash paths, and permit specific harness-internal subdirectories.
Rollback is a git revert of the parser changes in `__init__.py` and the added test cases in `gate-fp-corpus.toml`.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `config/governance/gate-fp-corpus.toml`

## Recommended Commit Type

`fix`
