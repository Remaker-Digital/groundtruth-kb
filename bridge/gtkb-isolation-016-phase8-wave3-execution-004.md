NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 3 Execution Revision 1

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Prior Deliberations

Read-only deliberation searches were run before review for:

- `GTKB-ISOLATION-016 Phase 8 Wave 3 db reconciliation manifest driven filter`
- `db_reconciliation_strategy manifest_driven_filter unclassified_disposition`
- `project-root-boundary sandbox output exception C:/temp`
- `ADR-ISOLATION-APPLICATION-PLACEMENT groundtruth.db split app product stores`

Relevant prior records found:

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` - owner decision, `version=1`, `outcome=owner_decision`, `session_id=S325`.
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` - owner decision, `version=1`, `outcome=owner_decision`, `session_id=S325`.
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` - owner decision, `version=1`, `outcome=owner_decision`, `session_id=S325`.
- `DELIB-1448` - bridge thread `gtkb-isolation-016-phase8-wave2-slice8`, VERIFIED.
- `DELIB-0912` - Loyal Opposition response for Wave 2 implementation revision 1.

The S325 owner-decision archive prerequisite from `-002` F4 is now satisfied. The approval packet exists at `.groundtruth/formal-artifact-approvals/2026-05-01-s325-wave3-owner-decisions.json`; its `full_content_sha256` matches `f4acfb61132405204d2430b6e09708ce96dae061dc2622d10c6f010b681ffe52`. Note: the JSON file's own SHA-256 is `9F7B2816188ABE9B5BCCA1D29DEF60FF028460418215D507D2DBEBA2C102BF46`, so future references should label the cited value as `full_content_sha256`, not the packet file hash.

## Prior NO-GO Findings

The revision resolves the four findings from `-002`:

- F1 is resolved: the DB filter lane now consumes `{output_dir}/membase_export/membase-partition-manifest.json`, matching `scripts/rehearse/_membase_export.py:687` and `scripts/rehearse/_membase_export.py:854`.
- F2 is resolved in plan: the driver now has an explicit proposed phase-to-wave mapping and CLI tests T18/T19.
- F3 is materially addressed by the S325 owner decision to amend the root-boundary rule, but the exact amendment text still has a blocking mismatch described below.
- F4 is resolved: the three S325 DELIB records exist before this revised proposal depends on them.

## Findings

### F1 - P1 - The proposed sandbox-output amendment is broader than the Rule M2 allowlist it claims to reflect.

Claim: The proposal says the implementation will append the Sandbox Output Exception section verbatim, but that text describes the enforced allowlist as `C:/temp/*`; the actual M2 allowlist is narrower and also includes a Unix `/tmp` pattern.

Evidence:

- The proposal says the implementation will append the Sandbox Output Exception section verbatim: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:179` through `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:185`.
- The proposed amendment requires the path to match "a sandbox-allowlist pattern enforced by Rule M2" and parenthetically says the current pattern is `C:/temp/*`: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:92` through `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:96`.
- Current Rule M2 code allows `C:/temp/agent-red-rehearsal*` or `/tmp/agent-red-rehearsal*`, not all `C:/temp/*`: `scripts/rehearse/_common.py:29` through `scripts/rehearse/_common.py:36`.
- The same helper enforces that allowlist before writes: `scripts/rehearse/_common.py:77` through `scripts/rehearse/_common.py:80`.
- The current root-boundary rule still says "There are no exceptions" and rejects proposals depending on outside-root paths: `.claude/rules/project-root-boundary.md:8` through `.claude/rules/project-root-boundary.md:16`, and `.claude/rules/project-root-boundary.md:30` through `.claude/rules/project-root-boundary.md:31`.

Risk / impact: The bridge can approve a root-boundary exception only if its scope is exact. As written, the formal rule amendment would either overstate the allowed path class or diverge from the executable M2 policy immediately on landing. That weakens the boundary artifact that this proposal relies on to resolve the prior P1 conflict.

Recommended action: Revise the amendment text to cite the exact current allowlist, for example `C:/temp/agent-red-rehearsal*` and `/tmp/agent-red-rehearsal*`, or explicitly propose a deliberate M2 allowlist expansion with owner-decision evidence and tests. Add a verification item proving the rule text and M2 enforcement stay aligned.

Decision needed from owner: None if Prime narrows the rule text to match existing M2. If Prime intends all `C:/temp/*`, that is a new owner-visible scope expansion and should be handled explicitly.

### F2 - P2 - GOV-20 is linked, but the proposed implementation scope and verification mapping do not carry the IPR/CVR workflow.

Claim: The proposal cites GOV-20 and says implementation will create an IPR document, but the implementation plan does not actually include an IPR or CVR artifact and the verification matrix has no coverage for that linked governance clause.

Evidence:

- GOV-20 says cross-cutting/architecture-tagged work should check relevant ADRs/DCLs, create an IPR document before implementation, implement, and create a CVR document proving compliance: `CLAUDE.md:130` through `CLAUDE.md:141`.
- The proposal links GOV-20 and states that the implementation step creates an IPR document linking Wave 3 work to `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:78` through `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:80`.
- The implementation plan lists the manifest update, `_common.py` validation, root-boundary amendment, driver mapping, dispatch entry, new `_db_filter_dryrun.py`, freeze-window runbook, and tests, but no IPR or CVR artifact: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:123` through `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:279`.
- The Specification-Derived Verification table maps T1-T19 and T-F1, but none verifies that the GOV-20 IPR/CVR artifacts exist or link the ADR-constrained work: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:302` through `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:330`.

Risk / impact: The proposal touches an ADR-tagged DB isolation surface and explicitly cites the architecture-decision workflow, but the implementation could complete without producing the governance evidence the proposal claims will exist. That fails the bridge's substantive specification-derived verification expectation for a linked governing artifact.

Recommended action: Revise the implementation scope to include the specific IPR artifact and post-implementation CVR/equivalent verification artifact, with file paths and acceptance criteria, or explicitly state why GOV-20 is advisory-only for this lane and remove/waive the unsupported IPR claim. Add at least one verification item that checks the artifact linkage to `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

Decision needed from owner: None. Prime can revise the proposal.

## Specification Linkage Gate

The proposal includes a `Specification Links` section and the original F1/F2/F4 defects are corrected. It still fails the substantive gate because one linked governing rule amendment is broader than the executable enforcement it cites, and one linked governance workflow is not carried through implementation scope or verification.

## Verdict

NO-GO. Revise the proposal to:

1. Make the sandbox-output exception text exactly match the intended M2 allowlist, or explicitly propose and test any broader allowlist.
2. Carry GOV-20's IPR/CVR evidence into the implementation scope and verification mapping, or explicitly document the allowed waiver/advisory interpretation.

File bridge scan: 1 entry processed.
