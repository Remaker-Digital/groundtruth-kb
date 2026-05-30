NEW

# GT-KB Bridge Implementation Report - Bridge Preflight Path Warning - 005

bridge_kind: implementation_report
Document: gtkb-bridge-preflight-path-warning
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-bridge-preflight-path-warning-004.md
Approved proposal: bridge/gtkb-bridge-preflight-path-warning-003.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3272
Implementation authorization packet: sha256:514be086e748afcdf49e1c7e7ebbeebadb009e16c8683186f958bf690d8abb0c
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex Desktop default reasoning

## Implementation Claim

Implemented the non-blocking missing-parent-directory warning authorized by `bridge/gtkb-bridge-preflight-path-warning-004.md`.

`scripts/bridge_applicability_preflight.py` now computes `warnings.missing_parent_dirs` from a new narrow collector, `collect_cited_implementation_paths()`, instead of from the existing broad applicability parser. The collector reads only explicit `target_paths:` / `target_path:` metadata and path rows in `## Files Changed` / `## Files Expected To Change` sections. The existing `extract_target_paths()` behavior remains available for applicability matching and was not converted into the warning source.

The warning is rendered in JSON, in Markdown as `- warnings.missing_parent_dirs: [...]`, and as a stderr line for CLI/tooling consumers when missing parent directories are present. The warning is advisory only: `preflight_passed` and the command exit-code semantics are unchanged.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - preflight is part of the policy engine surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - preflight enforces proposal spec-linkage quality; this enhancement improves output quality.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol and bridge filing authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files remain inside `E:\GT-KB`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specifications to executed tests.
- `GOV-STANDING-BACKLOG-001` - this implements tracked work item `WI-3272`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the warning improves bridge artifact trustworthiness by surfacing misplaced cited paths early.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this report advances the approved proposal into post-implementation verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the enhancement is captured as governed bridge work.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Owner Decisions / Input

No new owner decision is required. This implementation remains inside the active project authorization recorded in the approved proposal and GO.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner authorization for `PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`, including `WI-3272`.
- `bridge/gtkb-bridge-preflight-path-warning-003.md` - approved revised implementation proposal.
- `bridge/gtkb-bridge-preflight-path-warning-004.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_preflight_no_warning_when_parent_exists`, `test_preflight_warns_only_invalid_paths`, and `test_preflight_no_warning_when_path_exists` verify the policy surface warns only when appropriate. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `test_preflight_warns_when_parent_missing` verifies a cited target path with a missing parent is surfaced in `warnings.missing_parent_dirs`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_preflight_warns_for_files_changed_section_path` verifies bridge report/proposal `Files Changed` style path evidence is included in the narrow warning source. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_preflight_warning_ignores_incidental_prose_paths` verifies incidental prose, prior-deliberation citations, and bridge-file citations do not enter the warning list. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The focused preflight test suite executes 15 tests and reports 15 passing tests. |
| `GOV-STANDING-BACKLOG-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report carries forward the approved WI, bridge thread, project authorization, linked specs, and verification evidence. |

## Commands Run

```text
python scripts\implementation_authorization.py validate --target scripts/bridge_applicability_preflight.py --target platform_tests/scripts/test_bridge_applicability_preflight.py
```

Observed result:

```text
"authorized": true
"targets": [
  "scripts/bridge_applicability_preflight.py",
  "platform_tests/scripts/test_bridge_applicability_preflight.py"
]
```

```text
python -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py -q --tb=short
```

Observed result:

```text
collected 15 items
platform_tests\scripts\test_bridge_applicability_preflight.py .......... [ 66%]
.....                                                                    [100%]
15 passed
```

```text
python -m ruff check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result:

```text
All checks passed!
```

```text
python -m ruff format --check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result:

```text
2 files already formatted
```

```text
git diff --check -- scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result: exit code 0, no whitespace errors. Git also emitted the existing Windows line-ending notice for `platform_tests/scripts/test_bridge_applicability_preflight.py`.

```text
python -m ruff check .
```

Observed result: exit code 1 with 2,078 unrelated lint findings across the existing repository baseline. Representative first findings were import ordering in `.claude/hooks/advisory-router-scan.py`, `SIM109` in `.claude/hooks/bridge-axis-2-surface.py`, import ordering in `.claude/hooks/code-quality-baseline-proposal-check.py`, and many Agent Red/application/script findings. The edited slice files were separately checked and passed with `python -m ruff check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py`. The broad repo-wide ruff failure was not introduced by this slice and was not remediated here to avoid unrelated changes.

## Files Changed

- `scripts/bridge_applicability_preflight.py` - added the narrow cited-implementation-path collector, missing-parent warning computation, Markdown/JSON rendering, and stderr warning output.
- `platform_tests/scripts/test_bridge_applicability_preflight.py` - added focused regression coverage for valid, invalid, mixed, existing-file, `Files Changed` section, incidental-prose false-positive, and output-schema cases.

## Evidence Anchors

- `scripts/bridge_applicability_preflight.py:48` defines the `Files Changed` / `Files Expected To Change` heading matcher.
- `scripts/bridge_applicability_preflight.py:207` adds `collect_cited_implementation_paths()` as the warning-only collector.
- `scripts/bridge_applicability_preflight.py:227` adds `compute_missing_parent_dir_warnings()`.
- `scripts/bridge_applicability_preflight.py:379` adds `warnings.missing_parent_dirs` to the packet.
- `scripts/bridge_applicability_preflight.py:414` renders the warning line in Markdown.
- `scripts/bridge_applicability_preflight.py:454` emits the stderr warning for tooling consumers.
- `platform_tests/scripts/test_bridge_applicability_preflight.py:312` through `:377` cover the approved warning behaviors.

## Acceptance Criteria Status

- [x] IP-1 landed: `collect_cited_implementation_paths()` was added as a separate narrow collector.
- [x] Existing `extract_target_paths()` remains available for applicability matching; the new warning does not use broad incidental prose scanning.
- [x] `warnings.missing_parent_dirs` is present in JSON and Markdown output.
- [x] The CLI emits a stderr warning when missing parent directories are present.
- [x] `preflight_passed` and exit-code semantics remain unchanged because the warning is advisory only.
- [x] IP-2 landed: focused tests cover existing parent, missing parent, mixed valid/invalid paths, existing target path, `Files Changed` section path, incidental-prose false-positive guard, and schema preservation.
- [x] Focused pytest, Ruff check, Ruff format check, and `git diff --check` pass on the touched files.
- [!] The proposal-listed broad command `python -m ruff check .` was run but fails on unrelated existing repository lint debt; this report includes the observed failure rather than claiming a repo-wide clean state.

## Risk And Rollback

Residual risk: the warning is filesystem-sensitive, so a path whose parent is intentionally created later will produce an advisory warning until that parent exists. That is acceptable under the approved non-blocking behavior.

Rollback: revert the new collector, missing-parent computation, warning packet/rendering/stderr output, and added tests. The existing applicability matching behavior remains isolated and can continue unchanged.

## Recommended Commit Type

`feat` - adds a non-blocking bridge preflight warning capability and regression tests.

## Loyal Opposition Asks

1. Verify that warning collection is limited to explicit target metadata and `Files Changed` / `Files Expected To Change` section rows.
2. Confirm broad prose path extraction remains isolated to applicability matching and does not feed `warnings.missing_parent_dirs`.
3. Confirm the repo-wide Ruff failure is existing unrelated baseline debt or return a targeted NO-GO if the touched files contain a verification gap.
