NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Sub-slice 18.B PDF Cluster Move

**Review date:** 2026-05-04
**Reviewer:** Codex, Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md`
**Verdict:** NO-GO

## Summary

The revised proposal passes the mechanical applicability preflight and fixes the prior blockers around moving `package-pdf.json` with the PDF tooling cluster. It still cannot receive GO because the ignored-file contract remains internally inconsistent after adding `package-pdf.json` as the eighth ignored moved file.

This is a narrow proposal-quality blocker: the migration scope is directionally sound, but the implementation and verification contract must consistently require eight ignored-file `.gitignore` migrations, including `package-pdf.json`, before Prime Builder acts.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:a42c6383f21ca4c51b1be447fa1f2712d16357b8f7a99b49915035acf52e1161`
- bridge_document_name: `gtkb-isolation-018-slice-b-pdf-cluster`
- operative_file: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS. This satisfies the mechanical bridge applicability gate, but it does not override the substantive findings below.

## Findings

### F1 - NO-GO - Ignored-file preservation is still inconsistent for `package-pdf.json`

Claim:

- The proposal correctly states that `package-pdf.json` is gitignored and now in scope as an ignored moved file (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:110`, `:166`, `:169`).
- It also says Step 4 was updated to remove 8 root ignore patterns and add 8 new-path patterns (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:23`, `:183`).

Contradictory evidence in the same proposal:

- The default behavior text still says to preserve ignored status by adding `Generate-PDF-Report.ps1` "and the 6 others", which accounts for only seven ignored files and omits `package-pdf.json` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:185`).
- The proposed commit message still says "7 gitignored files" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:196`).
- The rollback/risk language still says "7 specific lines" and "7 gitignored files" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:272`, `:277`).
- OQ-B still asks about "the 7 currently-gitignored files", despite `package-pdf.json` being the eighth ignored moved file (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:284`).

Live repository evidence confirms there are eight ignored root files in the expanded cluster:

```text
git check-ignore -v -- Generate-PDF-Report.ps1 generate-pdf-report.js generate-pdf-report.py generate-pdf.bat PDF-Generation-Instructions.md PRODUCTION-READINESS-ASSESSMENT.md PRODUCTION-READINESS-SUMMARY.txt package-pdf.json
```

Observed output includes:

```text
.gitignore:172:Generate-PDF-Report.ps1
.gitignore:173:PDF-Generation-Instructions.md
.gitignore:174:generate-pdf-report.js
.gitignore:175:generate-pdf-report.py
.gitignore:176:generate-pdf.bat
.gitignore:177:package-pdf.json
.gitignore:366:PRODUCTION-READINESS-ASSESSMENT.md
.gitignore:367:PRODUCTION-READINESS-SUMMARY.txt
```

Risk / impact:

- Prime Builder could follow the commit/OQ/rollback language and migrate only seven ignored patterns, leaving `package-pdf.json` with the wrong new-path ignore status.
- This keeps the same ambiguity that the prior NO-GO required the revision to remove, now concentrated on `.gitignore` behavior rather than file movement.

Recommended action:

- Revise every ignored-file count and instruction to say eight ignored moved files.
- Explicitly include `package-pdf.json` in the new-path ignored-status migration language, commit message, risk/rollback text, and OQ-B.

### F2 - NO-GO - T-gi-1 does not verify the stated ignored-status contract

Claim:

- The proposal says "T-gi-1 default-behavior coverage extends to all 8 ignored files including `package-pdf.json`" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:23`).
- The spec-to-test mapping treats `.gitignore` integrity as directly covered by T-gi-1 (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:243`).

Evidence:

T-gi-1 checks only one file:

```text
cd applications/Agent_Red/pdf-tooling && git check-ignore Generate-PDF-Report.ps1
```

That command does not verify `package-pdf.json`, the JS/Python/BAT files, the PDF instructions document, or the two production-readiness files (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-005.md:221`).

Risk / impact:

- A post-implementation report could pass T-gi-1 while failing to preserve ignored status for `package-pdf.json`.
- Because `package-pdf.json` is the manifest whose split caused an earlier NO-GO, its new-path status needs explicit verification, not implied coverage.

Recommended action:

- Replace T-gi-1 with a command that checks all eight ignored moved files at their new paths, including `package-pdf.json`.
- Make the expected result require one matching `.gitignore` rule for each of the eight moved ignored files.

## Non-blocking Observations

- The mechanical preflight passed with `missing_required_specs: []`.
- Live `git ls-files` confirms that only the three `.docx`/`.png` files are tracked; `package-pdf.json` is correctly classified as ignored in this revision.
- The 11-file move, generator `OUTPUT_PATH` edits, root-absence test, and manifest co-location test are now directionally consistent.

## Required Revision

Submit a revised bridge proposal that:

1. Updates all remaining seven-file references to eight ignored moved files.
2. Names `package-pdf.json` wherever ignored-status preservation is described.
3. Rewrites T-gi-1 to check all eight ignored moved files under `applications/Agent_Red/pdf-tooling/`.
4. Carries forward or reruns the applicability preflight after revision.

## Decision Needed From Owner

None.
