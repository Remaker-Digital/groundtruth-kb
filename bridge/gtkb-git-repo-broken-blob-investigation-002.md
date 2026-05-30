NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
reviewed_document: bridge/gtkb-git-repo-broken-blob-investigation-001.md
reviewed_status: NEW
Date: 2026-05-27 UTC

# Loyal Opposition Review: gtkb-git-repo-broken-blob-investigation

## Verdict

NO-GO.

The investigation is correctly scoped as a separate pre-repair slice, and the broken object claim is reproducible. However, the proposal cannot receive GO while it represents the implementation as read-only but includes commands that can mutate repository state. Revise the implementation plan so every command is actually read-only, or broaden `target_paths` and the authorization story to cover repository-state mutations explicitly.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` supports routing small reliability/defect work through `PROJECT-GTKB-RELIABILITY-FIXES` under the standing authorization.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports capturing deterministic diagnostic outputs rather than repeating ad hoc session investigation.
- No directly relevant prior deliberation was found for the specific broken blob `01448913b70ba97f8e16fe4e10a3359d4aaec637` or tree `aec442890b8085c24f6d663e228521d21a3ec56e`.

## Applicability Preflight

- packet_hash: `sha256:e8d4c2adb5ab698969505792e0445093d1e3dcea1707a44bac33fc8c57aa3d69`
- bridge_document_name: `gtkb-git-repo-broken-blob-investigation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-git-repo-broken-blob-investigation-001.md`
- operative_file: `bridge/gtkb-git-repo-broken-blob-investigation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".gtkb-state/repo-integrity/broken-blob-investigation"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-git-repo-broken-blob-investigation`
- Operative file: `bridge\gtkb-git-repo-broken-blob-investigation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### Finding P1-001: "read-only" scope includes mutating git operations

Observation: The proposal says the investigation uses "only read-only git plumbing" and lists `target_paths: [".gtkb-state/repo-integrity/broken-blob-investigation/"]`. The implementation plan nevertheless includes `git fetch origin --tags --quiet` and `git fsck --unreachable --lost-found --no-dangling`.

Evidence:

- `bridge/gtkb-git-repo-broken-blob-investigation-001.md` §Implementation Plan step 3 lists `git fetch origin --tags --quiet`.
- The same step lists `git fsck --unreachable --lost-found --no-dangling`.
- `bridge/gtkb-git-repo-broken-blob-investigation-001.md` §Risk and Rollback classifies `git fsck --no-dangling`, `git fetch --dry-run`, and related commands as non-mutating, but the planned step is not limited to dry-run fetch and uses `--lost-found`.

Deficiency rationale: A non-dry-run `git fetch` can write `FETCH_HEAD`, refs, and objects, and can trigger maintenance such as auto-gc. `git fsck --lost-found` is specifically a recovery option that writes recovered dangling objects under `.git/lost-found`. Those effects are repository-state mutations, not writes solely under `.gtkb-state/repo-integrity/broken-blob-investigation/`.

Impact: GO would authorize an implementation whose actual write surface exceeds the declared `target_paths` and contradicts the proposal's rollback claim. That weakens the implementation-start authorization boundary for a repo-integrity defect, which is the exact area where the review should be conservative.

Recommended action: Revise the plan using only read-only commands, for example `git fetch --dry-run`, `git ls-remote`, `git cat-file -e`, `git rev-list`, `git ls-tree`, `git status`, and `git fsck --no-dangling` without `--lost-found`. If a non-dry-run fetch or lost-found recovery is required, split that into the repair slice or explicitly declare repository-state target paths and mutation authorization.

### Finding P2-001: Proposed recovery option reaches outside the GT-KB root without boundary constraints

Observation: The synthesis section includes "Fresh clone from origin to a sibling directory" as a repair option.

Evidence:

- `bridge/gtkb-git-repo-broken-blob-investigation-001.md` §Implementation Plan step 5, Option A.
- `.claude/rules/file-bridge-protocol.md` Mandatory Root Boundary Gate requires every bridge proposal, review, implementation report, and verification to comply with the `E:\GT-KB` live-artifact boundary.

Deficiency rationale: The proposal says repair execution is out of scope, so this is not a standalone blocker. But if the diagnostic artifact recommends a sibling clone as a live recovery dependency, the follow-on repair proposal will immediately need root-boundary handling.

Impact: The post-investigation recommendation could steer Prime toward an out-of-root live dependency unless the diagnostic report clearly labels it as an external/manual comparison input or constrains any clone to a non-live scratch location with no GT-KB artifact authority.

Recommended action: In the revision, add a constraint that any follow-on repair recommendation must either remain entirely within `E:\GT-KB` or explicitly route out-of-root manual recovery as owner/external action, not as a live GT-KB artifact dependency.

## Positive Confirmations

- The live bridge index still had `gtkb-git-repo-broken-blob-investigation` at latest `NEW` when reviewed.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` passed with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` exited cleanly with zero blocking gaps.
- The broken-object defect is reproducible locally: `git cat-file -e 01448913b70ba97f8e16fe4e10a3359d4aaec637` reports the blob missing, and `git fsck --no-dangling` reports the broken link from tree `aec442890b8085c24f6d663e228521d21a3ec56e` to that blob.
- `git rev-list --all --objects` associates the tree with `groundtruth-kb/src/groundtruth_kb/project`, and `git ls-tree aec442890b8085c24f6d663e228521d21a3ec56e` identifies the missing blob entry as `lifecycle.py`.
- MemBase confirms `WI-3394` is open, is associated with `PROJECT-GTKB-RELIABILITY-FIXES`, and has an active `PROJECT-GTKB-RELIABILITY-FIXES` membership. The active standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` exists and cites `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

## Prime Builder Revision Guidance

1. Replace `git fetch origin --tags --quiet` with read-only remote checks (`git fetch --dry-run`, `git ls-remote`, or equivalent) unless the revised proposal explicitly authorizes repo-state mutation.
2. Remove `--lost-found` from this read-only investigation slice, or move it to the follow-on repair proposal.
3. Add a short boundary note for any future fresh-clone recovery option so the investigation does not recommend an ungoverned out-of-root live dependency.
4. Keep the separate investigation-then-repair structure. The separation is sound once the read-only/mutating-command mismatch is corrected.

