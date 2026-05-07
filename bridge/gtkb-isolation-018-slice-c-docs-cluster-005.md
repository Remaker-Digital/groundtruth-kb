GO

# Loyal Opposition Review - ISOLATION-018 Slice 18.C Docs Cluster REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-07 UTC / 2026-05-06 America/Los_Angeles
Reviewed proposal: `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md`
Prior NO-GO: `bridge/gtkb-isolation-018-slice-c-docs-cluster-003.md`
Verdict: GO

## Claim

The revised proposal resolves both prior findings. It aligns the docs-cluster
move with the live 170-file non-platform inventory, explicitly includes
`docs/release/`, and adds redacted pre/post secret-scan gates.

## Applicability Preflight

- packet_hash: `sha256:1a4c90c47bce7f7f4ea4c2d1a805b9104af0604590666edbe3f35e8f0955a744`
- bridge_document_name: `gtkb-isolation-018-slice-c-docs-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md`
- operative_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Evidence Checked

```text
git ls-files docs | rg -v '^docs/(gtkb-dashboard|specification-scaffold|assets/gtkb-dashboard)/'
```

Observed result: 170 non-platform tracked docs files.

```text
git ls-files docs/release
```

Observed result: 2 tracked files.

```text
git ls-files docs-site
```

Observed result: 88 tracked files.

```text
python -m groundtruth_kb secrets scan --paths docs docs-site --redacted --fail-on verified-provider
```

Observed result: exit 0; 47 redacted `candidate-high` findings, 298 paths
scanned, and no `verified-provider` findings.

## Gate Checks

- F1 resolved: the revision updates expected docs count from 166 to 170 and
  adds `git mv docs/release applications/Agent_Red/docs/`.
- F2 resolved: the revision adds T-secret-1 and T-secret-2 using redacted
  secret scans and `--fail-on verified-provider`.
- Specification-derived test mapping: PASS. The new secret-scan gates are tied
  to the verified secret-scan tooling threads and the existing isolation tests
  remain mapped to placement, inventory, workflow, registry, and root-boundary
  constraints.
- Root-boundary gate: PASS. All moves remain within `E:\GT-KB`, with Agent Red
  content moving under `applications/Agent_Red/`.

## Implementation Conditions

- Run T-secret-1 before moves and T-secret-2 after moves; the report must record
  redacted candidate counts and confirm zero `verified-provider` findings.
- Recompute live tracked counts at implementation time before commit; if the
  non-platform docs count is no longer 170 or docs-site is no longer 88, stop
  and revise.
- The post-implementation report must show the 22 platform docs files still at
  root and no tracked Agent Red docs files left under root `docs/`.
- Preserve the in-place workflow path-update checks from the original proposal.

Decision needed from owner: None.

File bridge scan: 1 entry processed.
