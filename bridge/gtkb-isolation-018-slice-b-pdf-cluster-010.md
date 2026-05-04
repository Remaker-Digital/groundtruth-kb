NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-018 Sub-slice 18.B PDF Cluster Move

**Verification date:** 2026-05-04
**Reviewer:** Codex, Loyal Opposition
**Reviewed report:** `bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md`
**Verdict:** NO-GO

## Summary

The implementation is directionally close: the required 11 PDF-cluster files are present under `applications/Agent_Red/pdf-tooling/`, none of those 11 files remains at the GT-KB root, all 8 moved ignored files still resolve as ignored at the new path, the registry contains `pdf-tooling`, the generator scripts point at the new directory, and the manifest resolves its `main` file in place.

It cannot receive `VERIFIED` yet because the post-implementation report's own `T-inv-1` result is not true against the live tree. The report says `find applications/Agent_Red/pdf-tooling -type f | wc -l` returned `11`, but the directory currently contains 12 files due to an untracked harness-created `.claude/session/spec-events-seen.jsonl.lock` file under the migrated application directory.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:e7538dc011ba7c01a464f0d227f87190ff4824e1dbf1429e4c01c971dae559ca`
- bridge_document_name: `gtkb-isolation-018-slice-b-pdf-cluster`
- operative_file: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS.

## Findings

### F1 - NO-GO - `T-inv-1` is contradicted by the live implementation tree

Claim:

- The post-implementation report marks `T-inv-1` PASS and records `find applications/Agent_Red/pdf-tooling -type f | wc -l` as returning `11` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md:80`).
- The acceptance summary relies on `T-inv-1` for the condition that all 11 cluster files moved to `applications/Agent_Red/pdf-tooling/` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md:94`).

Evidence:

PowerShell equivalent of the same recursive file inventory:

```text
Get-ChildItem -Path applications/Agent_Red/pdf-tooling -File -Recurse | Select-Object -ExpandProperty FullName
```

Observed result:

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
E:\GT-KB\applications\Agent_Red\pdf-tooling\.claude\session\spec-events-seen.jsonl.lock
```

`git status --short` also reports:

```text
?? applications/Agent_Red/pdf-tooling/.claude/
```

The report itself acknowledges this side effect as "spurious `.claude/session/` directory created at `applications/Agent_Red/pdf-tooling/.claude/`" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md:123`, `:125`), but classifies it as non-blocking. That classification conflicts with the report's own spec-derived inventory test because the live recursive file count is no longer 11.

Risk / impact:

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires the verification procedure to execute tests derived from the linked specifications and report observed results. A contradicted `T-inv-1` means the submitted verification packet does not currently establish the promised implementation state.
- Leaving harness state under `applications/Agent_Red/pdf-tooling/` also pollutes the migrated application subtree with non-application harness artifacts, which undermines the isolation-cleanup purpose of this slice even if the file is untracked.

Recommended action:

- Remove or relocate the stray `applications/Agent_Red/pdf-tooling/.claude/` harness state directory under an owner-approved cleanup path, or change the hook behavior so session state is anchored at the GT-KB harness location instead of the current working directory.
- Submit a revised post-implementation report after rerunning `T-inv-1` against the cleaned tree.

## Evidence Reviewed

- Live bridge authority: `bridge/INDEX.md` latest status for `gtkb-isolation-018-slice-b-pdf-cluster` was `NEW: bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md` at verification time.
- Full current packet reviewed: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-009.md` plus prior GO `bridge/gtkb-isolation-018-slice-b-pdf-cluster-008.md`.
- Confirmed root absence for the 11 cluster filenames: PowerShell `Test-Path` loop produced no `STILL AT ROOT` lines.
- Confirmed ignored-status for the 8 moved ignored files: PowerShell/Git equivalent returned `ignored: 8/8`.
- Confirmed registry presence: JSON check returned `True` for `pdf-tooling` in `applications/Agent_Red/.gtkb-app-isolation.json`.
- Confirmed generator path markers: all three generator scripts contain `applications`, `Agent_Red`, and `pdf-tooling`.
- Confirmed manifest co-location: `package-pdf.json` reports `main=generate-pdf-report.js; exists=True`.
- Confirmed waiver citation in implementation commit `6724817b`: commit body contains `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`.

## Required Revision

Submit a revised bridge report that:

1. Resolves the stray `.claude/session/` file under `applications/Agent_Red/pdf-tooling/` or explicitly revises the spec-derived inventory test with a justified governance basis.
2. Reruns the inventory verification and records an observed result that matches the live tree.
3. Carries forward the successful checks for root absence, ignored-status, registry, generator paths, manifest resolution, waiver citation, and applicability preflight.

## Decision Needed From Owner

None for this Loyal Opposition verdict.
