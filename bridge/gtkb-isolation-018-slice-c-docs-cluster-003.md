NO-GO

# Loyal Opposition Review - ISOLATION-018 Slice 18.C Docs Cluster

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-07 UTC / 2026-05-06 America/Los_Angeles
Reviewed proposal: `bridge/gtkb-isolation-018-slice-c-docs-cluster-002.md`
Operative parked draft reviewed: `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md`
Verdict: NO-GO

## Claim

The bridge preflight passes and the overall migration shape is directionally
right, but the proposal is stale against the live docs inventory and omits a
secret-safety verification gate for a documentation cluster that now has known
credential-scan sensitivity. It needs a revised proposal before implementation.

## Applicability Preflight

- packet_hash: `sha256:df8fb8c959ae44dfaf5e86ac5b3e7b1724f691214a4f9bdf29774d75fd8b3a05`
- bridge_document_name: `gtkb-isolation-018-slice-c-docs-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-002.md`
- operative_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-002.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Evidence Checked

```text
git ls-files docs | rg -v '^docs/(gtkb-dashboard|specification-scaffold|assets/gtkb-dashboard)/' | Measure-Object
```

Observed result: 170 non-platform tracked files under `docs/`, not 166.

```text
git ls-files docs-site | Measure-Object
```

Observed result: 88 tracked files under `docs-site/`.

```text
python -m groundtruth_kb secrets scan --paths docs docs-site --redacted --fail-on verified-provider
```

Observed result: exit 0; 47 redacted `candidate-high` findings, 298 paths
scanned, and no `verified-provider` findings.

## Findings

### F1 - P1: The live docs inventory no longer matches the proposal's acceptance criteria

Claim: The proposal's fixed expected count and subdirectory list are stale.

Evidence: `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md` expects 166
tracked Agent Red docs files in T-rule-1, T-inv-1, and the `VERIFIED`
acceptance criteria. The live tree currently has 170 non-platform tracked files
under `docs/`. Grouping those files by first subdirectory also shows
`docs/release/` with 2 tracked files, but the migration strategy's Step 2 list
does not include `docs/release/`.

Risk/impact: Implementation can either miss tracked Agent Red release docs or
make the post-implementation tests fail against stale expected counts. Either
outcome weakens the isolation proof.

Recommended action: Revise the proposal to use the live 170-file non-platform
docs inventory, explicitly include `docs/release/` or justify why it stays at
root, and update T-rule-1, T-inv-1, and the acceptance criteria. Prefer adding
a generated migration manifest so the implementation verifies exact paths, not
only aggregate counts.

Decision needed from owner: None.

### F2 - P2: The test plan omits a redacted secret scan for the moved docs surfaces

Claim: The proposal moves documentation and transcript-like files from paths
that are now known to be credential-scan sensitive, but the specification-
derived test plan does not require a redacted secret scan before `VERIFIED`.

Evidence: A redacted scan of the current `docs` and `docs-site` surfaces found
47 `candidate-high` findings and no `verified-provider` findings. The finding
set includes docs under `docs/operations/`, `docs/owner-messages-*`, and
`docs-site/docs/getting-started/`. The proposal's T-rule/T-inventory/workflow
tests do not include any `groundtruth_kb secrets scan` command.

Risk/impact: A large docs move could carry or create secret-like material
without explicit verification evidence, especially immediately after the
repository secret-purge work.

Recommended action: Add a `T-secret-1` verification step using redacted output,
for example:

```text
python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider
```

The post-implementation report should record that no `verified-provider`
findings exist and should summarize any remaining `candidate-high` findings
without exposing raw matched values.

Decision needed from owner: None.

## Required Revision

Submit a revised 18.C proposal with live inventory counts, explicit handling of
`docs/release/`, updated acceptance criteria, and a redacted secret-scan gate.

File bridge scan: 1 entry processed.
