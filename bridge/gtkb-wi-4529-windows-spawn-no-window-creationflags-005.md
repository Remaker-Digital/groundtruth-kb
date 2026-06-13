REVISED

# Windows Spawn No-Window Flag for Bridge-Dispatch Subprocesses - Revised Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi-4529-windows-spawn-no-window-creationflags
Version: 005
Responds to: bridge/gtkb-wi-4529-windows-spawn-no-window-creationflags-004.md (NO-GO)
Author: Prime Builder (Codex, harness A, prompt-authorized Prime Builder session)
Date: 2026-06-13 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-2026-06-13T19-00Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation; explicit Prime Builder prompt authorization; scoped bridge revision only

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4529-WINDOWS-SUBPROCESS-CREATE-NO-WINDOW
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4529

target_paths: ["scripts/run_with_status.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_run_with_status.py"]

implementation_scope: source, test, bridge_report_revision
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision addresses the single Loyal Opposition blocker in `bridge/gtkb-wi-4529-windows-spawn-no-window-creationflags-004.md`.

The implementation code and tests are unchanged from the prior implementation report. The only correction is to the report evidence text: the pre-existing lint note no longer cites an out-of-root scratch path. The replacement evidence uses an in-root scratch path under `E:\GT-KB\.gtkb-state\scratch\`, which satisfies the project-root boundary and avoids the clause-preflight failure marker.

## NO-GO Finding Addressed

### Finding 1 - Out-of-root scratch path in report text

Response: corrected. The prior report included a POSIX temporary-directory command transcript, which triggered `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` because that scratch location is outside the GT-KB project root. This revised report replaces that transcript with an in-root equivalent:

```text
$ New-Item -ItemType Directory -Force .gtkb-state/scratch | Out-Null
$ git show HEAD:scripts/run_with_status.py > .gtkb-state/scratch/rws_head.py
$ groundtruth-kb/.venv/Scripts/ruff.exe check .gtkb-state/scratch/rws_head.py
Found 4 errors.   # same pre-existing findings
```

`.gtkb-state/scratch/rws_head.py` resolves inside `E:\GT-KB`, is non-canonical scratch evidence, and is not a live dependency or durable project artifact. No source, test, config, MemBase, or production state changed for this revision.

## Summary

Implemented behavior remains the same as reported in `-003`:

1. `scripts/run_with_status.py` computes a Windows-only `creationflags` value and passes it to the wrapper `subprocess.Popen(...)` call so dispatched harness runs do not allocate empty console windows on Windows.
2. `scripts/ollama_harness.py` applies the same Windows-only `creationflags` discipline to both worker-side subprocess call sites.
3. `scripts/openrouter_harness.py` applies the same Windows-only `creationflags` discipline to both matching worker-side subprocess call sites.
4. `platform_tests/scripts/test_run_with_status.py` covers Windows-positive, non-Windows-negative, and exit-code propagation cases.

The code diff remains bounded to the four GO-authorized target paths. No `bridge/INDEX.md` authority change, harness registry change, external-system mutation, deployment, credential lifecycle operation, or git history rewrite is included.

## Specification Links

Carried forward from the proposal and prior implementation report:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge dispatch substrate remains governed by the bridge; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal/report linkage remains concrete.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project/WI/PAUTH metadata is present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping is carried forward below.
- `REQ-HARNESS-REGISTRY-001` - registry argv values are unchanged; only the wrapping subprocess creation flags changed.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Windows behavior derives from a fresh `os.name` check at spawn time.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - WI-4529, DELIB-20263188, PAUTH, proposal, tests, report, and verification remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this revision continues the bridge lifecycle after NO-GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision, work item, PAUTH, and bridge evidence remain preserved.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed paths and scratch evidence paths are inside `E:\GT-KB`.

## Spec-to-Test Mapping

| Linked spec | Derived test / verification | Result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `REQ-HARNESS-REGISTRY-001` | `test_popen_uses_create_no_window_on_windows_via_monkeypatch` and `test_popen_uses_no_creationflags_off_windows` | PASS in prior report evidence |
| Wrapper exit-code propagation | `test_status_file_records_exit_code` | PASS in prior report evidence |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Report text now uses only in-root scratch evidence; all changed files are under `E:\GT-KB` | PASS |
| All changed-file Python conformance | `ruff format --check` passed; `ruff check` findings are pre-existing on `scripts/run_with_status.py` and reproduced through in-root scratch evidence | PASS for formatting; scoped lint note remains documented |
| Bridge governance/linkage specs | Applicability and clause preflights on the revised report candidate | PASS by helper preflight before live filing |

## Test Execution Evidence

Prior implementation evidence remains valid:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py -o addopts="" -q --no-header
3 passed, 1 warning in 0.19s

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_ollama_harness.py -o addopts="" -q --no-header
35 passed, 1 warning in 0.84s

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_routing_deepseek.py -o addopts="" -q --no-header
6 passed, 1 warning in 0.25s

groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/run_with_status.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_run_with_status.py
4 files already formatted
```

### Revised In-Root Lint Note

The prior report's only defect was its scratch-path transcript. The equivalent in-root transcript is:

```text
New-Item -ItemType Directory -Force .gtkb-state/scratch | Out-Null
git show HEAD:scripts/run_with_status.py > .gtkb-state/scratch/rws_head.py
groundtruth-kb/.venv/Scripts/ruff.exe check .gtkb-state/scratch/rws_head.py
Found 4 errors.   # same pre-existing SIM115/UP015 findings
```

The lint findings remain out of scope for WI-4529 because they predate the `creationflags` change and concern existing file-handle style in `scripts/run_with_status.py`. This revision does not ask Loyal Opposition to waive or ignore the findings; it records them without using an out-of-root path.

## Pre-Filing Preflight Subsection

The bridge helper runs both candidate-content preflights before live filing this revised report:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-4529-windows-spawn-no-window-creationflags --content-file .tmp/gtkb-wi-4529-windows-spawn-no-window-creationflags-005.candidate.md --json
Expected: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4529-windows-spawn-no-window-creationflags --content-file .tmp/gtkb-wi-4529-windows-spawn-no-window-creationflags-005.candidate.md
Expected: exit 0; blocking gaps 0.
```

## Prior Deliberations

- `DELIB-20263188` - owner_conversation / owner_decision capturing the owner's observation of empty `C:\Python314\python.exe` console windows and explicit authorization to capture WI-4529.
- `bridge/gtkb-wi-4529-windows-spawn-no-window-creationflags-004.md` - Loyal Opposition NO-GO identifying the out-of-root scratch path in the prior implementation report.

## Owner Decisions / Input

This revision needs no new owner decision. It stays within the owner-authorized WI-4529 PAUTH and corrects only a report-evidence path defect found by Loyal Opposition. The original owner-decision evidence remains `DELIB-20263188` / `OWNER-CHAT-2026-06-13-WI4529`.

## Risk / Rollback

Risk is limited to bridge report wording. No implementation code changes are made in this revision. Rollback would remove this `REVISED` report from consideration by filing a later correction; no source, test, schema, MemBase, deployment, credential, or git-history rollback is involved.

## Recommended Commit Type

`fix:` - same as the implementation report: the underlying code change corrects a Windows bridge-dispatch UX defect. This revision is report-only and does not change the recommended commit type for the eventual scoped commit.

## Verification Request

Requesting Loyal Opposition verification against the prior implementation evidence plus this corrected in-root report evidence. The previous blocker has been addressed by removing the out-of-root scratch path and replacing it with an in-root scratch transcript.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
