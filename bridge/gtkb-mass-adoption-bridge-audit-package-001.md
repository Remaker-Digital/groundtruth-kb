NEW

# GT-KB Mass Adoption Bridge Audit Package Proposal

bridge_kind: prime_proposal
implementation_scope: protocol
target_project: Agent Red as GT-KB dual-agent adopter
work_item_ids: [GTKB-MASS-001]
target_paths: ["bridge/INDEX.md", "bridge/durable-role-bridge-poller-separation-001.md", "bridge/durable-role-bridge-poller-separation-002.md", "bridge/gtkb-core-spec-intake-001.md", "bridge/gtkb-core-spec-intake-002.md", "bridge/gtkb-core-spec-intake-phase1-001.md", "bridge/gtkb-core-spec-intake-phase1-002.md", "bridge/gtkb-core-spec-intake-phase3a-cli-001.md", "bridge/gtkb-core-spec-intake-phase3a-cli-002.md", "bridge/gtkb-mass-adoption-readiness-phase-a-001.md", "bridge/gtkb-mass-adoption-readiness-phase-a-002.md", "bridge/gtkb-mass-adoption-readiness-phase-a-003.md", "bridge/gtkb-mass-adoption-readiness-phase-a-004.md", "bridge/gtkb-proposal-verification-gates-001.md", "bridge/gtkb-proposal-verification-gates-002.md", "bridge/gtkb-proposal-verification-gates-003.md", "bridge/gtkb-tier-a-current-main-integration-001.md", "bridge/gtkb-tier-a-current-main-integration-002.md", "bridge/gtkb-tier-a-current-main-integration-003.md", "bridge/gtkb-tier-a-current-main-integration-004.md", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-PHASE-A-2026-04-22-07-04.md"]
requires_review: true
requires_verification: true
prior_deliberations: [DELIB-0758, DELIB-0757, DELIB-0785, DELIB-0633, DELIB-0835]

## Status

NEW - Loyal Opposition review requested before implementation.

## Requested Verdict

GO to prepare a bridge-audit package manifest and verification handoff for the
first `GTKB-MASS-001` package, or NO-GO with required revisions.

This proposal does not request approval to stage, commit, push, merge, deploy,
mutate formal artifacts, use credentials, purge history, or run
`gt project upgrade --apply`.

## Claim

Prime Builder should continue `GTKB-MASS-001` by preparing the first
bridge-audit package as a narrow, evidence-backed package boundary.

The package should preserve the current Prime Builder / Loyal Opposition audit
trail and Phase A readiness evidence without mixing in Agent Red application
implementation, dashboard/runtime code, commercial durability code, generated
database state, formal approval packets, or scaffold application.

## Governing Evidence

- `bridge/gtkb-mass-adoption-readiness-phase-a-004.md` verified Phase A and
  recommended bridge-audit-only as the lowest-risk first package.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-PHASE-A-2026-04-22-07-04.md`
  classifies the broad dirty tree and recommends the first review package
  include `bridge/INDEX.md`, referenced bridge files, and the Phase A report
  only if intentionally included despite the dropbox ignore rule.
- `bridge/gtkb-proposal-verification-gates-003.md` is now a current
  post-implementation verification request for `GTKB-GOV-012`; it is bridge
  audit trail and should be considered in the bridge package manifest.
- `memory/work_list.md` keeps `GTKB-MASS-001` active and requires scoped
  commit/review readiness before mass-adoption claims.
- The current workspace remains broadly dirty, so live `git status --short`
  remains the source of truth for package boundaries.

## Prior Deliberations

Relevant prior records:

- `DELIB-0758`: verified earlier GT-KB mass-adoption readiness work but did
  not prove mass-adoption readiness.
- `DELIB-0757`: verified GT-KB adoption-gap closure work.
- `DELIB-0785`: verified GT-KB release-readiness thread.
- `DELIB-0633`: strategic assessment warning against overstating GT-KB
  adoption readiness.
- `DELIB-0835`: strict formal artifact approval and audit-display rule.

## Problem

Phase A identified a defensible first package, but the package has not yet
been converted into a concrete manifest that a later commit/push approval or
review can evaluate.

Without a manifest, the next packaging step risks either:

1. committing too little and losing the bridge audit trail needed for
   continuation; or
2. committing too much and mixing GT-KB bridge evidence with unrelated Agent
   Red application/runtime/generated/formal-artifact work.

## Scope In

Prepare an additive bridge-audit package handoff that:

1. inventories every current `git status --short -- bridge` changed or
   untracked bridge path;
2. separates active-index bridge files from historical tracked bridge files;
3. identifies which untracked bridge files are referenced by the current
   `bridge/INDEX.md`;
4. identifies which referenced bridge files are missing, if any;
5. decides whether the ignored Phase A report should be recommended for
   force-add, copied into a tracked package manifest, or left ignored;
6. creates a package manifest report under
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`;
7. writes a post-implementation bridge handoff requesting Loyal Opposition
   verification.

## Scope Out

1. No `git add`, staging, commit, push, merge, or branch creation.
2. No source-code implementation in Agent Red application files.
3. No upstream `groundtruth-kb` code changes.
4. No dashboard/runtime/generated artifact packaging.
5. No commercial durability file packaging.
6. No generated `groundtruth.db` packaging.
7. No formal DA/GOV/SPEC/PB/ADR/DCL mutation.
8. No `.groundtruth/formal-artifact-approvals/` packaging.
9. No `gt project upgrade --apply`.
10. No mass-adoption, public-adoption, private-beta, or release-readiness
    claim.

## Proposed Implementation Plan

1. Read current `bridge/INDEX.md`.
2. Parse the current document entries and latest status lines.
3. Run/read:

   ```powershell
   git status --short -- bridge
   git ls-files bridge
   git check-ignore -v independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-PHASE-A-2026-04-22-07-04.md
   ```

4. Build a manifest table with columns:
   - path;
   - git status;
   - referenced by current index: yes/no;
   - latest document/status if applicable;
   - package recommendation;
   - rationale.
5. Recommend one of these Phase A report dispositions:
   - force-add the ignored report in a later owner-approved package;
   - leave the report ignored and summarize it in the manifest;
   - move/copy report content only after a separate governance/ignore-policy
     decision.
6. Record required verification for any later package.
7. Do not stage or commit.

## Acceptance Criteria

Loyal Opposition should be able to verify that the package handoff:

1. accounts for all current `bridge/` git-status paths;
2. identifies all current `bridge/INDEX.md` referenced files;
3. identifies missing referenced files, if any;
4. keeps non-bridge application/runtime/generated/formal-artifact changes out
   of the package;
5. makes a clear Phase A report disposition recommendation;
6. preserves explicit non-claims and approval gates;
7. runs no mutating git packaging commands.

## Verification Plan

Run:

```powershell
git diff --check -- bridge/INDEX.md bridge/gtkb-mass-adoption-bridge-audit-package-001.md
python -m pytest tests/scripts/test_standing_backlog_harvest.py -q --tb=short
```

Also run a non-mutating bridge status check using the current GT-KB bridge CLI
when available:

```powershell
python -m groundtruth_kb bridge status --dir . --scope protocol
```

Do not run `git add`, `git commit`, `git push`, deployment commands, formal
artifact mutation commands, or `gt project upgrade --apply`.

## Owner Decision Needed

None at proposal time.

Future owner approval remains required before staging, commit, push, merge,
deployment, credential use, history cleanup, formal artifact mutation, or
`gt project upgrade --apply`.
