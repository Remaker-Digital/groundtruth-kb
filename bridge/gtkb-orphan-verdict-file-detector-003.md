NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ed875-33a6-7692-b15b-79bc1199ff69
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: codex-exec

# GT-KB Bridge Implementation Report - gtkb-orphan-verdict-file-detector - 003

bridge_kind: implementation_report
Document: gtkb-orphan-verdict-file-detector
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-orphan-verdict-file-detector-002.md
Approved proposal: bridge/gtkb-orphan-verdict-file-detector-001.md
Recommended commit type: feat:

## Implementation Claim

Implemented WI-4621 as a standalone, read-only orphan verdict audit.

The new script `scripts/audit_orphan_verdict_files.py`:

- Enumerates `bridge/*.md` under the selected project root or `--bridge-dir` override.
- Treats a bridge file name as canonical only when it matches `<slug>-NNN.md`, with a greedy slug segment so slugs containing digits remain valid.
- Reads the first non-blank line and classifies only `GO`, `NO-GO`, and `VERIFIED` as verdict-shaped.
- Reports files that are both verdict-shaped and non-canonical as orphan verdict files.
- Emits Markdown by default and JSON via `--json`.
- Returns exit `1` when orphan findings exist, exit `0` when clean, and exit `2` for audit errors.

The new test file `platform_tests/scripts/test_audit_orphan_verdict_files.py` covers the approved detector behavior against temporary bridge directories, without depending on the live bridge corpus.

Implementation commit: `956cfbc38 feat(bridge): add orphan verdict audit`.

During the live audit run, the detector found one existing orphan verdict-shaped file: `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.lo-verdict.md`. Per the Hygiene PB automation instruction to capture stray cleanup work, I recorded follow-up work item `WI-4643` in `PROJECT-GTKB-MAY29-HYGIENE` to reconcile that existing orphan file. That cleanup is deliberately not mixed into this implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/file-bridge-protocol.md` Section File Naming and Section Body Status-Token Rule
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Owner Decisions / Input

No new owner decision was required. Implementation authority carried forward from the approved proposal and active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, owner decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`.

The additional follow-up work item `WI-4643` was recorded under the explicit automation instruction: if stray or odd cleanup defects are found, add them as work items to the open hygiene project.

## Prior Deliberations

- `bridge/gtkb-orphan-verdict-file-detector-001.md` - approved implementation proposal.
- `bridge/gtkb-orphan-verdict-file-detector-002.md` - Loyal Opposition GO verdict.
- `WI-4621` - original backlog item for making non-canonical verdict-shaped files visible failures instead of silent orphans.
- `WI-4643` - follow-up cleanup item created from the detector's live finding for `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.lo-verdict.md`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md` | `test_flags_timestamped_verdict_shaped_orphan`, `test_canonical_numbered_verdict_not_flagged`, and `test_canonical_slug_containing_digits_not_flagged` verify canonical numbered file-chain treatment and non-canonical verdict detection. |
| `.claude/rules/codex-review-gate.md` | `test_flags_timestamped_verdict_shaped_orphan` and `test_json_output_lists_orphans` verify reviewer-verdict tokens `GO` and `NO-GO` are surfaced when filed outside the numbered bridge path; `test_canonical_numbered_verdict_not_flagged` verifies canonical verdicts are not false positives. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The implementation is limited to the approved `target_paths` from `bridge/gtkb-orphan-verdict-file-detector-001.md`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The focused test file maps each approved behavior to executable pytest coverage and passed. |
| `.claude/rules/project-root-boundary.md` | Changed files are in-root and match the GO packet target paths. Test fixtures use temporary bridge directories and do not read or write out-of-root GT-KB artifacts. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The live orphan discovered by the audit was preserved as backlog work item `WI-4643` instead of being silently ignored or folded into unrelated cleanup. |

## Commands Run

Initial root-venv verification attempts failed because that environment lacks repo test/lint dependencies:

```powershell
.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_audit_orphan_verdict_files.py -q
.venv/Scripts/python.exe -m ruff check scripts/audit_orphan_verdict_files.py platform_tests/scripts/test_audit_orphan_verdict_files.py
.venv/Scripts/python.exe -m ruff format --check scripts/audit_orphan_verdict_files.py platform_tests/scripts/test_audit_orphan_verdict_files.py
```

Observed result: pytest rejected configured `--timeout=30`; `.venv` had no `ruff` module.

Focused verification was rerun with the GT-KB venv and repo addopts cleared because the local environment still lacks the timeout plugin configured in `pyproject.toml`:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_audit_orphan_verdict_files.py -q
```

Observed result: `6 passed, 1 warning in 0.24s`. Warning: unknown config option `asyncio_mode` in this local pytest environment.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/audit_orphan_verdict_files.py platform_tests/scripts/test_audit_orphan_verdict_files.py
```

Observed result: `All checks passed!`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/audit_orphan_verdict_files.py platform_tests/scripts/test_audit_orphan_verdict_files.py
```

Observed result: `2 files already formatted`.

Live audit self-check:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/audit_orphan_verdict_files.py --json; $code = $LASTEXITCODE; "exit_code=$code"; exit 0
```

Observed result: one finding, exit code `1` as expected for visible orphan findings:

```json
{
  "bridge_dir": "E:/GT-KB/bridge",
  "orphan_count": 1,
  "orphans": [
    {
      "first_line_status": "GO",
      "path": "E:/GT-KB/bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.lo-verdict.md",
      "reason": "verdict-shaped file name is not canonical <slug>-NNN.md"
    }
  ]
}
```

Backlog follow-up capture:

```powershell
python -m groundtruth_kb.cli backlog add --json --title "Reconcile orphan managed-artifacts LO verdict file" --origin hygiene --component bridge-files --priority P2 --project-name "PROJECT-GTKB-MAY29-HYGIENE" --related-bridge-threads '["bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.lo-verdict.md","bridge/gtkb-orphan-verdict-file-detector-001.md"]' --depends-on-work-items '["WI-4621"]'
python -m groundtruth_kb.cli backlog show WI-4643 --json
python -m groundtruth_kb.cli projects show PROJECT-GTKB-MAY29-HYGIENE --json | Select-String -Pattern 'WI-4643|Reconcile orphan managed-artifacts'
```

Observed result: `WI-4643` was created, remains `approval_state: "unapproved"`, and appears as an active May29 Hygiene project member.

## Observed Results

- Focused pytest: `6 passed, 1 warning`.
- Ruff lint: clean.
- Ruff format check: clean.
- Live audit: found one existing non-canonical verdict-shaped orphan and exited `1`, which is the intended visible-failure behavior.
- Follow-up backlog capture: `WI-4643` created in the May29 Hygiene project for the live orphan cleanup.
- Local commit created: `956cfbc38 feat(bridge): add orphan verdict audit`.

## Files Changed

- `scripts/audit_orphan_verdict_files.py`
- `platform_tests/scripts/test_audit_orphan_verdict_files.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: adds a new read-only bridge audit capability and focused tests.

```text
 scripts/audit_orphan_verdict_files.py                      | 100 +++++++++++++++++++++++++++++
 platform_tests/scripts/test_audit_orphan_verdict_files.py | 119 ++++++++++++++++++++++++++++++++++++
 2 files changed, 219 insertions(+)
```

## Acceptance Criteria Status

- [x] A verdict-shaped file whose name does not match `<slug>-NNN.md` is reported as an orphan and produces a non-zero exit.
- [x] Canonical numbered verdict files and non-verdict files are not flagged.
- [x] The audit is read-only; it does not rename, delete, or rewrite any bridge file.
- [x] `--json` provides machine-readable output.
- [x] Ruff lint and format checks are clean on both changed files.

## Risk And Rollback

Residual risk is low. The implementation is additive and read-only; it does not change bridge dispatch, bridge filing, implementation authorization, or existing status parsing. The main risk is false positive/negative classification, covered by focused tests for canonical verdicts, non-canonical verdicts, non-verdict non-canonical files, and slugs containing digits.

Rollback is deletion of `scripts/audit_orphan_verdict_files.py` and `platform_tests/scripts/test_audit_orphan_verdict_files.py`, plus reverting commit `956cfbc38`. No schema, hook, dispatch, or bridge state migration is required.

## Loyal Opposition Asks

1. Verify that the detector implements the approved WI-4621 scope without mutating bridge files.
2. Confirm that the live orphan finding is a correct visible-failure result and that cleanup is properly separated into `WI-4643`.
3. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
