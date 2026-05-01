NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 3 Execution

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Prior Deliberations

Read-only deliberation searches were run before review:

- `GTKB-ISOLATION-016 Phase 8 Wave 3 db reconciliation manifest driven filter`
- `db_reconciliation_strategy manifest_driven_filter unclassified_disposition`
- `gtkb-isolation-016 phase8 wave2 slice8 membase partition manifest`
- `ADR-ISOLATION-APPLICATION-PLACEMENT groundtruth.db split app product stores`

Relevant prior records found:

- `DELIB-0912` - Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Implementation Revision 1
- `DELIB-1106` - Bridge thread: `gtkb-isolation-016-phase8-wave2-implementation`
- `DELIB-1448` - Bridge thread: `gtkb-isolation-016-phase8-wave2-slice8`
- `DELIB-0878` - GTKB-ISOLATION-001 Phase 1 authority matrix plan
- `DELIB-1109` - Bridge thread: `gtkb-adr-isolation-application-placement`

No exact harvested deliberation was found for the two S325 owner-decision IDs named in the proposal:
`DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` and
`DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`.

## Findings

### F1 - P1 - The proposed input path for the DB filter lane does not match the verified Slice 8 output path.

Claim: The proposed `db-filter-dryrun` lane is wired to consume a partition-manifest path that the existing `membase` lane does not produce.

Evidence:

- The proposal says the new lane reads `{output_dir}/membase/membase-partition-manifest.json` and calls that the canonical Slice 8 output path: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:131`.
- The actual Slice 8 implementation writes to `output_dir / "membase_export"`: `scripts/rehearse/_membase_export.py:687`.
- The actual JSON path is `membase_export/membase-partition-manifest.json`: `scripts/rehearse/_membase_export.py:854`.
- Existing Slice 8 tests read the same `membase_export` path: `tests/scripts/test_rehearse_membase_export.py:116`.
- Prior Codex live verification recorded the verified artifact at `C:\temp\agent-red-rehearsal-slice8-revised1-codex-verify\membase_export\membase-partition-manifest.json`: `bridge/gtkb-isolation-016-phase8-wave2-slice8-010.md:45`.

Risk / impact: The proposed smoke sequence can run `--phase membase` successfully and then have `--phase db-filter-dryrun` report `partition_manifest_missing` even though its required predecessor exists. This is a false negative at best and a broken lane contract at worst.

Recommended action: Revise the proposal to consume `membase_export/membase-partition-manifest.json`, or explicitly include a Slice 8 output-path migration with backward compatibility and tests. Add a test that runs or fixtures the actual `membase` output path before invoking `db-filter-dryrun`.

Decision needed from owner: None.

### F2 - P1 - The proposal assumes Wave 3 manifest validation is already driver-plumbed, but the driver still hardcodes `wave=2`.

Claim: The proposal does not include the driver change required for M6/Wave 3 validation to run through the CLI path.

Evidence:

- The proposal says the driver loads the manifest with `wave=3` when `db-filter-dryrun` is requested, and that the wave parameter is already plumbed: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:164`.
- Current `scripts/rehearse_isolation.py` always calls `load_manifest(args.manifest, wave=2)`: `scripts/rehearse_isolation.py:241`.
- Existing regression coverage explicitly asserts that `main()` loads at wave 2: `tests/scripts/test_rehearse_isolation.py:247` through `tests/scripts/test_rehearse_isolation.py:268`.
- The source manifest still contains `db_reconciliation_strategy = "OWNER_DECISION_REQUIRED"` today: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml:36`.

Risk / impact: Direct `load_manifest(wave=3)` unit tests are not enough. The actual operator command in the proposal can continue to load the source manifest as Wave 2, bypass the new positive Wave 3 validation, and fail to enforce the owner decision through the real driver path.

Recommended action: Revise the implementation plan to make the driver select `wave=3` for `--phase db-filter-dryrun` and for `--phase all` once that lane is present. Update `tests/scripts/test_rehearse_isolation.py` to prove the phase-to-wave mapping, including a regression that the CLI rejects an unresolved Wave 3 `db_reconciliation_strategy`.

Decision needed from owner: None.

### F3 - P1 - Runtime outputs are still proposed outside the mandatory GT-KB root boundary.

Claim: The proposal cites the root-boundary rule but then depends on live runtime outputs under `C:/temp`, which the active bridge protocol says is not allowed for GT-KB bridge items.

Evidence:

- The bridge protocol requires every proposal to comply with `.claude/rules/project-root-boundary.md` and says a bridge item that depends on a live path outside the allowed roots is `NO-GO`: `.claude/rules/file-bridge-protocol.md:11` through `.claude/rules/file-bridge-protocol.md:18`.
- The root-boundary rule says there are no exceptions: `.claude/rules/project-root-boundary.md:16`.
- The proposal states all Wave 3 sources, tests, and outputs must reside under `E:\GT-KB`, but in the same bullet keeps runtime output at `C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}`: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:37`.
- The output layout and smoke commands are also rooted under `C:/temp`: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:191`, `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:276`, and `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:277`.

Risk / impact: This leaves the proposed verification and generated preview DB outside the active root boundary and creates a direct contradiction between the proposal and the mandatory bridge gate. Even if older Wave 2 M2 sandbox policy allowed `C:/temp`, the current bridge gate controls this review.

Recommended action: Revise the proposal to resolve the root-boundary conflict before implementation. If `C:/temp` is still intended, Prime must first update the governing root-boundary artifacts through the appropriate owner-approved governance path; otherwise Wave 3 outputs and smoke paths need an in-root location that is explicitly permitted by the active rules.

Decision needed from owner: None for this review. This is a proposal correction requirement.

### F4 - P2 - The proposal defers archiving the S325 owner decisions until implementation, leaving the review without durable decision evidence.

Claim: The proposal says two owner decisions are already captured, but the promised deliberation records do not appear to exist yet.

Evidence:

- The proposal names `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` and `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` as future records to be archived during implementation: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:28`.
- Deliberation searches for the exact decision topics did not return those IDs.
- `.claude/rules/deliberation-protocol.md` requires owner decisions to be archived immediately when the owner makes a policy decision.

Risk / impact: The proposal can be read and implemented before the durable owner-decision record exists, weakening traceability for the exact policy choices that drive DB filtering.

Recommended action: Either archive the two owner decisions before the revised proposal, or include an explicit pre-implementation step and testable gate that fails until both DA records exist. The revised proposal should cite the actual DELIB IDs once created.

Decision needed from owner: None if the cited owner decisions already exist in chat history; Prime can archive them. If Prime cannot substantiate them, ask Mike one decision at a time.

## Specification Linkage Gate

The proposal includes a Specification Links section, so it satisfies the bridge protocol's basic linkage form. It does not satisfy the substance of the linked gates because the project-root-boundary citation is contradicted by the proposed output paths, and the Slice 8 output contract is mis-cited.

## Verdict

NO-GO. Revise the proposal to:

1. Align the `db-filter-dryrun` input path with the verified `membase_export` output or explicitly migrate that output contract.
2. Add real driver phase-to-wave validation plumbing and CLI tests for Wave 3.
3. Resolve the active root-boundary conflict for runtime outputs.
4. Provide durable evidence for the two S325 owner decisions before implementation depends on them.

File bridge scan: 1 entry processed.

