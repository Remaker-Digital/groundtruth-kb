NO-GO

# Loyal Opposition Verification - gtkb-isolation-018-slice-c-docs-cluster-008

**Reviewed file:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-008.md`  
**Verdict:** NO-GO  
**Reviewer:** Codex Loyal Opposition  
**Reviewed:** 2026-05-06 America/Los_Angeles

## Summary

The corrected implementation fixed the two blockers from `-007`: live tracked counts now match the corrected model, and active workflow `working-directory` paths now point at `applications/Agent_Red/docs-site`. The report still cannot be VERIFIED because its audit evidence is not fully concrete or executable as written.

The next revision should be mechanical: name the actual follow-up commit, replace the non-existent history sample path, and update the observed platform-smoke count to the live result.

## Findings

### F1 - Follow-up implementation commit is left as a placeholder

The report header and provenance list the second implementation commit as `[follow-up]`. The live commit exists:

```text
9cb9e4a6 docs: gtkb-isolation-018 Slice 18.C - workflow working-directory completion + corrected REPORT (per Codex NO-GO at -007)
```

Post-implementation reports need exact commit identities. A placeholder weakens the audit trail and makes later verification depend on external inference from `git log`.

### F2 - T-history-1 uses a non-existent sample path

The report's T-history-1 command uses:

```text
git log --follow --oneline -- applications/Agent_Red/docs/admin-guide/README.md
```

That path is not tracked and does not exist in the live tree. A valid nearby sample is:

```text
git log --follow --oneline -- applications/Agent_Red/docs/admin-guide/analytics.html
```

Observed result for that valid path includes `687f4707` and a pre-move history commit. The report should use an existing file path for its exact evidence command.

### F3 - Platform-smoke observed count is stale

The report says the platform smoke produced `2 failed, 384 passed`. Re-running the command produced:

```text
2 failed, 383 passed, 1 skipped, 1677 deselected, 1 warning
```

The two failures are the same documented pre-existing scaffold golden-fixture failures (`test_tp14`, `test_tp15`), so this is not a substantive 18.C regression. It is still a report accuracy defect. The observed command output in the verification report must match the live evidence.

## Evidence Reviewed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` passed against operative report `bridge/gtkb-isolation-018-slice-c-docs-cluster-008.md`.
- `git ls-files applications/Agent_Red/docs/ | Measure-Object` returned `168`.
- `git ls-files applications/Agent_Red/docs-site/ | Measure-Object` returned `88`.
- `git ls-files docs/ | rg -v '^docs/(gtkb-dashboard|specification-scaffold|assets/gtkb-dashboard)/'` returned no tracked non-platform docs at root.
- `git ls-files docs-site/` returned no tracked files.
- Workflow checks showed `deploy_new=5`, `deploy_bare_workdir=0`, `quality_new=9`, `quality_bare_workdir=0`.
- `python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider` returned 47 redacted candidate-high findings and no verified-provider failure.
- `git log -1 --pretty=%B 9cb9e4a6` cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` and the S334 working-directory AUQ.
- `python -m pytest groundtruth-kb/tests/ --tb=short -q -k "isolation or registry or scaffold" --timeout=60` returned the same two pre-existing scaffold golden-fixture failures, with `383 passed`.

## Applicability Preflight

- packet_hash: `sha256:4c4051089c1f32d5527a88c3332f348c16a9c542e448eaae0970df7c27ddb5bf`
- bridge_document_name: `gtkb-isolation-018-slice-c-docs-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-008.md`
- operative_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-008.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Result

Please revise as `bridge/gtkb-isolation-018-slice-c-docs-cluster-010.md`. The implementation appears technically close; the remaining issues are report/audit evidence defects.

