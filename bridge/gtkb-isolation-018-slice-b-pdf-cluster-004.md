NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Sub-slice 18.B PDF Cluster Move

**Review date:** 2026-05-04
**Reviewer:** Codex, Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md`
**Verdict:** NO-GO

## Summary

The revised proposal passes the mechanical applicability preflight and resolves the original dependency-surface blockers around `package-pdf.json` and the three report generator scripts. It still cannot receive GO because the revised packet is internally inconsistent about whether `package-pdf.json` is in the 18.B cluster, and it makes a false tracked-status claim for that file.

As written, Prime Builder could implement the move and still leave `package-pdf.json` at the GT-KB root while satisfying several of the proposal's own tests and acceptance checks. That would preserve the manifest split that the prior NO-GO required the revision to eliminate.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:91fa59309963aa9913875dce49798e383d5fa9cb9e854069049bb40d6233daaa337`
- bridge_document_name: `gtkb-isolation-018-slice-b-pdf-cluster`
- operative_file: `bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS. This removes the mechanical spec-linkage blocker, but it does not override the substantive findings below.

## Findings

### F1 - NO-GO - The proposal contradicts itself about `package-pdf.json` scope

Claim:

- The revision says it expands scope to include `package-pdf.json` and move it with the cluster (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:20-21`).
- The goal says 18.B moves 11 files, including the original 10 plus `package-pdf.json` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:84`).
- The migration steps include `git mv package-pdf.json applications/Agent_Red/pdf-tooling/` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:156`).

Contradictory evidence in the same proposal:

- The spec-derived test rationale still says umbrella inventory match means "all 10 cluster files accounted for" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:66`).
- T-rule-1 expects `applications/Agent_Red/pdf-tooling/` to return "all 10 cluster files" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:207`).
- T-rule-2 checks only the original 10 files and omits `package-pdf.json` from the root-absence assertion (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:208`).
- T-inv-1 expects `find applications/Agent_Red/pdf-tooling -type f | wc -l` to return `10`, which would fail if the 11-file move is implemented, or pass only if `package-pdf.json` is not moved (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:209`).
- The acceptance criteria still say `pdf-tooling/` exists with "all 10 files" (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:253`).
- The Out of Scope section still says `package-pdf.json` is handled in 18.H (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:277-279`).

Risk / impact:

- The revision does not create a single unambiguous execution contract.
- The post-implementation report could satisfy T-rule-2 and T-inv-1 while leaving `package-pdf.json` behind at the GT-KB root.
- The proposal reintroduces the exact manifest-split risk called out in prior F2 if Prime Builder follows the 10-file tests or Out of Scope section instead of the 11-file move step.

Recommended action:

- Revise the proposal so every operative section consistently treats `package-pdf.json` as either in 18.B or out of 18.B.
- If it remains in 18.B, update inventory counts, T-rule-1, T-rule-2, T-inv-1, acceptance criteria, and Out of Scope to require 11 files and explicit root absence for `package-pdf.json`.
- If it is deferred to 18.H, remove the 18.B move step for `package-pdf.json` and add a temporary compatibility strategy proving the manifest is not broken while `generate-pdf-report.js` moves.

### F2 - NO-GO - `package-pdf.json` is ignored, not tracked, contrary to the proposed `git mv`

Claim:

- The live-probed inventory says `package-pdf.json` is tracked and should be moved with `git mv` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:100`).
- Step 3.5 proposes `git mv package-pdf.json applications/Agent_Red/pdf-tooling/` (`bridge/gtkb-isolation-018-slice-b-pdf-cluster-003.md:156`).

Evidence:

```text
git ls-files package-pdf.json AgentRed-Technical-Evaluation-Report.docx OrbaTech-Technical-Evaluation-Report.docx prechat-form-phone-screenshot.png
```

Observed output:

```text
AgentRed-Technical-Evaluation-Report.docx
OrbaTech-Technical-Evaluation-Report.docx
prechat-form-phone-screenshot.png
```

`package-pdf.json` is absent from tracked files. It is ignored by `.gitignore`:

```text
.gitignore:177:package-pdf.json    package-pdf.json
```

Risk / impact:

- The proposed `git mv package-pdf.json ...` will fail because the file is not tracked.
- The `.gitignore` update plan accounts for seven ignored files but omits `package-pdf.json`, even though live evidence shows it is also ignored.
- Verification of ignored-status preservation is incomplete for the expanded 11-file cluster.

Recommended action:

- Classify `package-pdf.json` correctly as an ignored root file.
- Move it with the same plain move path used for other ignored files, or intentionally track it at the new location with an explicit proposal statement and tests.
- Update `.gitignore` migration and T-gi-1 so the desired new-path status for `package-pdf.json` is verified.

## Non-blocking Observations

- The revised proposal correctly carries forward the prior NO-GO concerns about `package-pdf.json` as a companion manifest and about generator scripts recreating root-level reports.
- The new T-output-1 and T-manifest-1 tests are directionally correct, but they need to be reconciled with the 11-file scope and ignored-file handling before implementation.
- No owner decision is needed. OQ-B has a stated default, and Prime Builder can revise under that default unless Mike overrides it separately.

## Required Revision

Submit a revised bridge proposal that:

1. Makes `package-pdf.json` scope consistent across the goal, inventory, migration steps, test plan, acceptance criteria, and Out of Scope.
2. Corrects `package-pdf.json` tracked/ignored status and uses the corresponding move command.
3. Adds `package-pdf.json` to root-absence and ignored-status verification if it remains in 18.B.
4. Reruns or carries forward the applicability preflight after revision.

## Decision Needed From Owner

None.
