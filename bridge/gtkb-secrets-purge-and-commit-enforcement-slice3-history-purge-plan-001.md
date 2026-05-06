NEW

# Owner-Action History-Purge Plan - GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT Slice 3

Author: Prime Builder (Codex, harness A)
Drafted: 2026-05-06
Type: P0 security history-purge approval plan
Risk tier: High. This plan describes a potential destructive Git history
rewrite, but it does not authorize or perform one.
Backlog item: `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`
Requested verdict: `GO` for planning/approval-packet preparation only.

target_paths: ["bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-001.md", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-SECRETS-SLICE2-ALL-REFS-INVENTORY-2026-05-06.json"]

## Trigger

Slice 2 implemented redacted all-local-refs inventory mode and ran:

```powershell
python -m groundtruth_kb secrets scan --all-refs --report-json independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-SECRETS-SLICE2-ALL-REFS-INVENTORY-2026-05-06.json --fail-on= > $null
```

The redacted inventory found 23 verified-provider-class historical findings in
locally reachable refs. No raw matched values are included in this plan.

Per the Slice 2 Loyal Opposition `GO`, if all-ref scanning finds verified
provider history, Prime Builder must file a separate owner-action history-purge
plan before any rewrite or force-push. This file is that plan.

## Specification Links

- `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001`
- `SPEC-SEC-SCAN-REDACTION-001`
- `SPEC-SEC-SCANNER-CLI-001`
- `SPEC-SEC-CI-COVERAGE-001`
- `SPEC-DSI-COMMIT-GATE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/canonical-terminology.md`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

Searches performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "secret history purge verified-provider all-refs rewrite force-push owner approval" --limit 10
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "GitHub history rewrite exposed credentials branch tag rewrite approval" --limit 10
```

The searches returned adjacent governance, CI, cleanup, and repository-operation
records, but no specific prior decision authorizing a credential-history rewrite.
The controlling authority is therefore the P0 owner elevation, the approved
SPEC-SEC family, and Slice 2 `GO` condition 6.

## Current Redacted Findings Summary

The Slice 2 all-refs inventory found:

| Severity | Count |
|---|---:|
| verified-provider-class historical findings | 23 |
| candidate-high historical findings | 740 |

Verified-provider-class provider counts:

| Provider class | Count |
|---|---:|
| `github_oauth_token` | 2 |
| `mailchimp_api_key` | 2 |
| `shopify_access_token` | 2 |
| `shopify_shared_secret` | 11 |
| `stripe_test_secret_key` | 4 |
| `stripe_webhook_secret` | 2 |

These counts are redacted scanner classifications. They are sufficient to
trigger a history-purge planning lane; they are not a license to print,
validate, upload, or reuse any matched value.

## Proposed Plan

### Phase 1 - Read-Only Rewrite Planning Packet

Create a planning packet that includes:

- exact redacted finding fingerprints, provider class, path, line, object id,
  and first observed local ref from the all-refs inventory;
- affected ref inventory: local branches, local tags, and fetched remote-tracking
  refs present during the scan;
- estimated blast radius: branches/tags likely to change, open PR impact,
  collaborator rebase/reset impact, GitHub Actions/cache impact, and release-tag
  impact;
- backup strategy: local mirror clone plus `git bundle --all` before any rewrite;
- dry-run strategy: perform any filter operation only on a throwaway mirror
  clone first, then rescan the rewritten mirror before proposing remote action;
- rollback strategy: preserve bundle/mirror references and exact pre-rewrite
  refs until owner confirms disposal;
- communication checklist for collaborators and external systems.

Phase 1 remains read-only with respect to the live remote.

### Phase 2 - Tool Selection

Evaluate deterministic rewrite tooling without executing against the live
repository:

- `git filter-repo` if available and suitable;
- BFG Repo-Cleaner only if filter-repo is unavailable or unsuitable;
- manual path/object purge only for narrowly scoped objects where tool behavior
  is clearer and safer.

The selected tool must support a dry-run or mirror-only rehearsal, preserve a
machine-readable mapping of rewritten refs, and avoid printing raw values.

### Phase 3 - Owner Approval Packet

Before any destructive operation, present one owner decision with:

- the exact remote and branches/tags affected;
- whether tags will be rewritten, deleted, or preserved;
- whether protected branches require temporary setting changes;
- the exact command sequence to run;
- the backup bundle/mirror location;
- expected collaborator instructions after rewrite;
- residual risk if history is not rewritten;
- residual risk if history is rewritten;
- expected owner reply shape: approve, reject, or request revision.

No rewrite proceeds without explicit owner approval in response to that packet.

### Phase 4 - Execution, Only After Approval

If and only if the owner approves:

- pause normal release work;
- create backup bundle and mirror;
- execute rewrite in mirror first;
- run redacted all-refs scan against rewritten mirror;
- present mirror results before live remote mutation if findings remain;
- push rewritten refs only if the approved packet permits it;
- immediately rerun redacted all-refs inventory after remote mutation;
- file post-execution bridge report and collaborator recovery instructions.

## Out Of Scope Until Explicit Owner Approval

- force-push;
- tag rewrite or tag deletion;
- branch deletion;
- GitHub history rewrite;
- GitHub settings or branch-protection changes;
- credential rotation, validation, provider API calls, or uploads;
- production deployment, release tagging, PyPI publishing, or Agent Red
  repository migration.

## Acceptance Criteria For Planning

- Plan remains raw-value-free.
- Plan cites Slice 2 redacted inventory and provider-class counts.
- Plan identifies backup, dry-run, approval, execution, and rollback phases.
- Plan makes destructive steps impossible without a later explicit owner
  approval packet.
- Loyal Opposition reviews this as a planning artifact, not rewrite authority.

## Recommended Verdict

`GO` for planning/approval-packet preparation only.

`NO-GO` for any live history rewrite until a later owner approval packet is
presented and approved.
