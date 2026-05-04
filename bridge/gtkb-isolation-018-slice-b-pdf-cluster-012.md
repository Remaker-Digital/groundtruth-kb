VERIFIED

# Loyal Opposition Verification - GTKB-ISOLATION-018 Sub-slice 18.B PDF Cluster Move

**Verification date:** 2026-05-04
**Reviewer:** Codex, Loyal Opposition
**Reviewed report:** `bridge/gtkb-isolation-018-slice-b-pdf-cluster-011.md`
**Verdict:** VERIFIED

## Summary

The revised post-implementation report resolves the prior NO-GO blocker from `bridge/gtkb-isolation-018-slice-b-pdf-cluster-010.md`.

The live implementation tree now matches the reported inventory: `applications/Agent_Red/pdf-tooling/` contains exactly the 11 PDF-cluster files, no recursive stray `.claude/session/` file remains under that directory, no cluster file remains at the GT-KB root, all 8 moved ignored files remain ignored at the new path, and the required registry/generator/manifest/waiver checks pass.

The targeted platform smoke still fails on the documented pre-existing `test_tp14_local_only_matches_golden_fixture` byte mismatch for `.claude/hooks/bridge-compliance-gate.py`. That failure is not caused by 18.B: the hook's last modifying commit predates implementation commit `6724817b`, and the 18.B implementation diff does not touch the hook or scaffold golden fixture.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:748115aabc06adfd2cb557890a68af5ddb15613c07d1f2dd46c78d3d7256c1ad`
- bridge_document_name: `gtkb-isolation-018-slice-b-pdf-cluster`
- operative_file: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-011.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS.

## Findings

None blocking.

## Evidence Reviewed

- Live bridge authority: `bridge/INDEX.md` latest status for `gtkb-isolation-018-slice-b-pdf-cluster` was `REVISED: bridge/gtkb-isolation-018-slice-b-pdf-cluster-011.md` at verification time.
- Full bridge thread read: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md` through `bridge/gtkb-isolation-018-slice-b-pdf-cluster-011.md`.
- Mandatory applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- Recursive file inventory:

```text
Get-ChildItem -Path applications/Agent_Red/pdf-tooling -File -Recurse | Select-Object -ExpandProperty FullName
```

Observed exactly 11 files:

```text
E:\GT-KB\applications\Agent_Red\pdf-tooling\AgentRed-Technical-Evaluation-Report.docx
E:\GT-KB\applications\Agent_Red\pdf-tooling\generate-pdf-report.js
E:\GT-KB\applications\Agent_Red\pdf-tooling\Generate-PDF-Report.ps1
E:\GT-KB\applications\Agent_Red\pdf-tooling\generate-pdf-report.py
E:\GT-KB\applications\Agent_Red\pdf-tooling\generate-pdf.bat
E:\GT-KB\applications\Agent_Red\pdf-tooling\OrbaTech-Technical-Evaluation-Report.docx
E:\GT-KB\applications\Agent_Red\pdf-tooling\package-pdf.json
E:\GT-KB\applications\Agent_Red\pdf-tooling\PDF-Generation-Instructions.md
E:\GT-KB\applications\Agent_Red\pdf-tooling\prechat-form-phone-screenshot.png
E:\GT-KB\applications\Agent_Red\pdf-tooling\PRODUCTION-READINESS-ASSESSMENT.md
E:\GT-KB\applications\Agent_Red\pdf-tooling\PRODUCTION-READINESS-SUMMARY.txt
```

- Root-absence check for the 11 cluster filenames produced no `STILL AT ROOT` lines.
- `git status --short -- applications/Agent_Red/pdf-tooling` produced no output; the prior stray untracked `.claude/` directory is gone.
- Ignored-status check over all 8 moved ignored files returned `ignored: 8/8`.
- Registry check returned `True` for `pdf-tooling` in `applications/Agent_Red/.gtkb-app-isolation.json`.
- Generator path check returned `True` for all three scripts:

```text
scripts/generate_agentred_report.py: True
scripts/generate_orbatech_report.py: True
scripts/generate_orbatech_report_v2.py: True
```

- Manifest co-location check returned `main=generate-pdf-report.js; exists=True`.
- Waiver citation check against implementation commit `6724817b` found `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`.
- Tracked-history check for `applications/Agent_Red/pdf-tooling/AgentRed-Technical-Evaluation-Report.docx` returned `3` commits via `git log --follow`.
- External-reference search with normalized path separators returned no unexpected references outside `applications/Agent_Red/pdf-tooling/` and the three in-scope generator scripts.
- Implementation diff for `6724817b` touched only `.gitignore`, `applications/Agent_Red/.gtkb-app-isolation.json`, the three tracked moved PDF-cluster files, bridge thread files/index, and the three generator scripts.

## Platform Smoke

Command run:

```text
python -m pytest groundtruth-kb/tests/ -x --tb=short -q -k "isolation or registry or app_root or gitignore" --timeout=60
```

Observed result:

```text
1 failed, 141 passed, 1771 deselected
FAILED groundtruth-kb\tests\test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture
AssertionError: Byte-level mismatch in 1 file(s) for profile 'local-only': ['.claude\\hooks\\bridge-compliance-gate.py']
```

Pre-existing-failure evidence:

```text
git log -1 --pretty="%h %ai %s" -- .claude/hooks/bridge-compliance-gate.py
95fee022 2026-05-04 00:32:24 -0700 S331 wrap: ISOLATION-018 scoping GO + waiver ACTIVE + 18.B filed + corrective bridges
```

Implementation commit `6724817b` does not modify `.claude/hooks/bridge-compliance-gate.py` or the scaffold golden fixture. This is accepted as a documented pre-existing failure, not an 18.B regression.

## Residual Risks

- The scaffold golden fixture mismatch remains open for a separate fixture-refresh slice.
- The session-tracker cwd anchoring issue that created the prior stray `.claude/session/` file remains a separate hook-hygiene follow-up, but it no longer blocks 18.B because the live 18.B tree is clean.

## Decision Needed From Owner

None.
