NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Sub-slice 18.B PDF Cluster Move

**Review date:** 2026-05-04
**Reviewer:** Codex, Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md`
**Verdict:** NO-GO

## Summary

The proposal passes the mechanical applicability preflight, but it cannot receive GO because its core low-risk claim and its no-import-break test are contradicted by live repository evidence.

The proposed move would relocate `generate-pdf-report.js` and the two report `.docx` outputs while leaving known callers/generators behind at root or under `scripts/`. As written, the proposal would either break the PDF npm entrypoint or leave report generators producing Agent Red artifacts back at the GT-KB root, directly undermining the purpose of this slice.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:73182b861cf74ae380fc31528c867186d2b49270fedfb472cb40d6233daaa337`
- bridge_document_name: `gtkb-isolation-018-slice-b-pdf-cluster`
- operative_file: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS. This removes the mechanical spec-linkage blocker, but it does not override the substantive findings below.

## Prior Deliberations

Relevant deliberations found in `groundtruth.db`:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` - owner decision authorizing the Agent Red nested placement rule.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` - owner decision authorizing the pending-migration waiver during ISOLATION-018.
- `DELIB-0961` / `DELIB-0960` - prior NO-GO bridge-thread reviews around GTKB-ISOLATION-016 Phase 8 Agent Red migration rehearsal.
- `DELIB-1013` / `DELIB-1014` / `DELIB-1020` - prior GO / verification records for migration planning and isolation phase scope.

No prior deliberation found that rejects moving this PDF cluster into `applications/Agent_Red/pdf-tooling/`. The blocker is the proposal's incomplete dependency/accounting surface.

## Findings

### F1 - NO-GO - The proposal's no-reference premise is false

Claim:

- The proposal states that "no Python/JS imports affected; no source-code references to any cluster file" and that its grep returns empty after excluding only `bridge/`, `memory/`, and `independent-progress-assessments/` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md:9`, `:18`).
- The proposed T-import-1 expects the same reference search to be empty (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md:174`).

Evidence:

```text
rg -n "Generate-PDF-Report|generate-pdf-report|PDF-Generation|prechat-form-phone-screenshot|AgentRed-Technical-Evaluation|OrbaTech-Technical-Evaluation|PRODUCTION-READINESS-ASSESSMENT|PRODUCTION-READINESS-SUMMARY" -g "*.py" -g "*.js" -g "*.json" -g "*.toml" -g "*.yml" -g "*.yaml"
```

Observed hits:

```text
generate-pdf-report.js:5: * Run with: node generate-pdf-report.js
generate-pdf-report.py:6:Run with: python generate-pdf-report.py
package-pdf.json:5:  "main": "generate-pdf-report.js",
package-pdf.json:7:    "generate-pdf": "node generate-pdf-report.js",
scripts\generate_agentred_report.py:34:OUTPUT_PATH = os.path.join(BASE, "AgentRed-Technical-Evaluation-Report.docx")
scripts\generate_orbatech_report_v2.py:18:    "OrbaTech-Technical-Evaluation-Report.docx"
scripts\generate_orbatech_report.py:35:OUTPUT_PATH = os.path.join(BASE, "OrbaTech-Technical-Evaluation-Report.docx")
```

Risk / impact:

- The proposal's own T-import-1 would fail.
- `package-pdf.json` is explicitly left out of scope (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md:91-92`, `:239`), but it points at `generate-pdf-report.js`, which this slice moves.
- The report generator scripts continue writing Agent Red report outputs to the GT-KB root. Running them after this move would recreate root-level Agent Red artifacts, reintroducing the rule violation this slice is meant to reduce.

Recommended action:

- Revise the slice to account for all live references before moving files.
- Either include `package-pdf.json` and the relevant report-generator path updates in this slice, or explicitly classify those references as retired/non-live with evidence and add a regression check that they cannot recreate root-level Agent Red files.
- Update T-import-1 so it reflects the revised scope and actually passes before implementation.

### F2 - NO-GO - The out-of-scope split for `package-pdf.json` is unsafe as written

Claim:

- The proposal keeps `package-pdf.json` out of scope because it "moves separately in 18.H" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md:91-92`, `:239`).

Evidence:

`package-pdf.json` contains:

```text
"main": "generate-pdf-report.js",
"generate-pdf": "node generate-pdf-report.js"
```

Risk / impact:

- Moving `generate-pdf-report.js` without moving or updating the companion manifest leaves the manifest in a broken location for the duration between 18.B and 18.H.
- That contradicts the proposal's low-risk/no-import-break rationale and creates unnecessary cross-slice dependency debt.

Recommended action:

- Move `package-pdf.json` with the PDF tooling in 18.B, or revise 18.B to leave `generate-pdf-report.js` in place until the manifest slice.
- If the split is retained, document a temporary compatibility strategy and add a test proving `npm --prefix` or equivalent PDF generation still resolves the moved script correctly.

### F3 - NO-GO - The generator scripts can recreate root-level Agent Red outputs after the migration

Claim:

- The goal is to move the PDF cluster out of `E:/GT-KB/` root into `E:/GT-KB/applications/Agent_Red/pdf-tooling/` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md:72`).

Evidence:

The following scripts hardcode their output paths to the repository root:

```text
scripts\generate_agentred_report.py:34:OUTPUT_PATH = os.path.join(BASE, "AgentRed-Technical-Evaluation-Report.docx")
scripts\generate_orbatech_report.py:35:OUTPUT_PATH = os.path.join(BASE, "OrbaTech-Technical-Evaluation-Report.docx")
scripts\generate_orbatech_report_v2.py:16-19: OUTPUT_PATH resolves to "OrbaTech-Technical-Evaluation-Report.docx" under repo root
```

Risk / impact:

- Post-migration execution of these scripts recreates root-level Agent Red / identity-report artifacts.
- This conflicts with `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 and with the proposal's T-rule-2 expectation that those files are absent from root.

Recommended action:

- Update the generator scripts in the same slice to write to `applications/Agent_Red/pdf-tooling/`, or retire them with explicit evidence that they are no longer live.
- Add a test that inspects these generator `OUTPUT_PATH` values and fails if they resolve to the GT-KB root for Agent Red report outputs.

## Non-blocking Observations

- The mechanical bridge applicability preflight passed with `missing_required_specs: []`.
- The tracked-file inventory probe matches the proposal's claim that only three cluster files are currently tracked:

```text
git ls-files | rg '^(generate-pdf|Generate-PDF|PDF-Gener|PRODUCTION-READ|AgentRed-Tech|OrbaTech-Tech|prechat-form)'

AgentRed-Technical-Evaluation-Report.docx
OrbaTech-Technical-Evaluation-Report.docx
prechat-form-phone-screenshot.png
```

- The current `.gitignore` evidence supports the proposal's claim that the seven named tooling/report files are ignored by exact-name patterns.

## Required Revision

Submit a revised bridge proposal that:

1. Reconciles the live references in `package-pdf.json` and `scripts/generate_*report*.py`.
2. Updates the migration scope or sequencing so no moved file's live caller/companion is left broken.
3. Updates the spec-derived test plan so T-import-1 passes and includes coverage preventing root-level report output recreation.
4. Carries forward the successful applicability preflight or reruns it after revision.

## Decision Needed From Owner

None. This is a proposal-quality blocker that Prime Builder can address in a revised bridge entry.
