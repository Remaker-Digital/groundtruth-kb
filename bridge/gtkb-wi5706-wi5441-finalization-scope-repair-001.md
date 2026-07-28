NEW
::init gtkb pb
::open build

# WI-5706 Exact Repair-Forward of WI-5441 Finalization Scope Contamination

bridge_kind: prime_proposal
Document: gtkb-wi5706-wi5441-finalization-scope-repair
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5706-REPAIR-FORWARD-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5706

target_paths: [".gtkb-index-hl705ij2/index"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Commit `f9e85829e` terminally finalized WI-5441 but recorded 17 changed paths
instead of the authorized 12-path cohort. The five extras were four valid Loyal
Opposition advisories, which must remain, and one unregistered transient Git
index, `.gtkb-index-hl705ij2/index`, which must be removed from the current
tree.

This proposal authorizes only the append-only WI-5706 repair-forward: adopt and
verify the transient's already-absent current-tree postimage, preserve every
other committed byte, produce an exact 12-versus-5 disposition report, and
create one bounded local governed finalization commit. It does not implement
WI-5704 recurrence prevention, alter source/configuration/registry content,
rewrite history, push, activate the dispatcher, or delete any bridge or
advisory artifact.

## Deterministic Commit Inventory

`git diff-tree --no-commit-id --name-status -r f9e85829e` currently yields
exactly 17 paths. The intended 12-path WI-5441 cohort is:

- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-014.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-015.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-018.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-020.md`
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py`
- `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

The five extras and their required dispositions are:

- `.gtkb-index-hl705ij2/index` - remove from the current tree and include that
  deletion in the WI-5706 repair-forward commit.
- `bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md` - preserve.
- `bridge/gtkb-lo-bridge-state-report-unknown-status-silent-exclusion-advisory-001.md` - preserve.
- `bridge/gtkb-lo-gov-file-bridge-authority-spec-body-path-orphaned-advisory-001.md` - preserve.
- `bridge/gtkb-lo-owner-decision-capture-auq-binding-gap-advisory-001.md` - preserve.

Two unrelated, currently untracked advisory files shown by `git status` are
pre-existing worktree content. WI-5706 neither edits nor stages them:
`bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`
and
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every cited and mutated
  path to remain inside the GT-KB root; WI-5706 changes no hosted application.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the decision, work item,
  proposal, disposition report, and verification evidence to remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit append-only bridge
  and backlog lifecycle states for the repair and its terminal disposition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the owner decision, risk,
  repair plan, report, and derived follow-on WI-5704 to remain durable artifacts.
- `GOV-WORK-TREE-HYGIENE-001` - requires deterministic report-first hygiene
  and prevents Git state from independently determining artifact membership.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the registry authoritative for
  membership; the unregistered transient has no retention claim, while the
  registered audit artifacts remain authoritative and usable.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - distinguishes the
  unregistered transient cleanup from a registered identity transition; this
  proposal performs no registry declaration mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires the bounded owner
  decision and active project authorization without waiving bridge GO,
  implementation-start, reporting, or independent verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires append-only bridge history and
  strict current-state resolution; no WI-5441 bridge file may be removed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this
  proposal to link every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the live
  PAUTH/project/work-item triple above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires each linked
  specification to map to executed verification evidence before `VERIFIED`.
- `GOV-STANDING-BACKLOG-001` - establishes canonical WI-5706 as the durable
  work authority for this repair-forward.

## Prior Deliberations

- `DELIB-202667516` - the owner explicitly authorized WI-5706 exactly as
  stated, including the sole transient deletion, preservation obligations,
  deterministic disposition report, verification, and one local commit.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - establishes
  registry-authoritative membership and the retained/disposable distinction
  implemented by WI-5441. WI-5706 repairs finalization scope; it does not reopen
  that implementation.

## Owner Decisions / Input

`DELIB-202667516` records the owner's exact response, "Authorize WI-5706
exactly as stated." It is bound to WI-5706 and supplies the owner evidence for
active project authorization
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5706-REPAIR-FORWARD-20260728`.
No additional owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. The linked specifications, canonical WI-5706
v2, `DELIB-202667516`, and the active exact-scope PAUTH fully determine the one
allowed postimage and the preserved/excluded paths. No new requirement or
interpretive owner choice is needed.

## Implementation Plan

1. Re-run the 17-path `f9e85829e` inventory and write the exact 12-versus-5
   disposition into the implementation report.
2. Hash the 12 intended paths and four preserved advisories from `f9e85829e`
   and the current tree; require byte identity for every retained path.
3. Confirm `.gtkb-index-hl705ij2/index` is unregistered, absent from the
   working tree, and the sole non-bridge path admitted to the WI-5706 commit.
4. Confirm the two unrelated untracked advisories remain untouched and
   unstaged.
5. Stage only the transient deletion plus the status-bearing WI-5706 report and
   independently authored terminal verdict required by finalization.
6. Run the implementation-start, registry, lifecycle, staged-scope, and
   protected-commit checks. Any mismatch fails closed without restoring,
   deleting, or staging another path.
7. Create one local governed finalization commit. Do not push. Re-run the strict
   WI-5441 and WI-5706 lifecycle checks and require the expected clean or
   explicitly excluded worktree state.

## Spec-Derived Verification Plan

| Specification | Verification | Required result |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every listed path against `git rev-parse --show-toplevel` and reject root escape or `applications/` placement | All 17 historical paths and the sole target remain within the platform root. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Cross-check `DELIB-202667516`, WI-5706, PAUTH, proposal, report, and verdict linkage | Every decision and result has a durable governed artifact edge. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Strict WI-5441 and WI-5706 lifecycle resolution plus final `gt backlog show WI-5706 --json` | Append-only states are valid and WI-5706 reaches an explicit terminal outcome. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify the owner decision, risk, report, and separate WI-5704 recurrence work remain durable | No requirement, finding, or future work is left only in session prose. |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff-tree --no-commit-id --name-status -r f9e85829e`; deterministic path-set classifier in the report; final `git status --short` | Exactly 12 intended plus 5 extras; only the transient is removed; unrelated dirty paths remain excluded. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `gt registry validate --json`; `gt registry reconcile --deep --json` | Registry valid/coherent; zero unregistered-load-bearing and invalid/unknown objects; transient has no membership claim. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Compare registry generation and TOML/package/projection digests before and after | No registry generation or declaration/projection mutation. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `gt projects show-authorization PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5706-REPAIR-FORWARD-20260728`; implementation-start preflight | PAUTH active, includes only WI-5706 scope, and exact target path is authorized. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --no-header`; strict live-chain resolution for WI-5441 and WI-5706 | Tests pass; WI-5441 remains terminal; WI-5706 reaches the filed status without altering predecessors. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge compliance audit against final proposal/report content | Every cited specification exists and no placeholder or missing linkage remains. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Mandatory applicability preflight and `python -m pytest platform_tests/scripts/test_project_authorization.py -q --no-header` | Preflight passes; project/PAUTH/WI triple is live and exact. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute every row in this table and include per-spec outcomes in the report | No linked spec lacks executed evidence. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5706 --json` before report and after terminal finalization | Canonical WI remains linked and is reconciled to its terminal outcome. |

Additional exact-scope checks:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_artifact_membership_reconciliation.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/check_protected_commit_authorization.py --staged
```

The implementation report must include the pre/post commit ids, all retained
path hashes, the exact staged path set, and the explicit exclusion state of the
two unrelated untracked advisories.

## Risk / Rollback

The primary risk is repeating the original over-broad finalization by staging
an advisory, registry file, implementation file, or reconciliation scratch
path. Exact-set staging and pre-commit path enumeration bound that risk. The
second risk is incorrectly treating the four valid advisories as contamination;
their byte hashes are therefore preservation assertions, not deletion targets.

Before commit, rollback is restoring the transient path from `HEAD` and
clearing only WI-5706 staging. After commit, history is append-only: any defect
requires a separately authorized repair-forward commit. No reset, amend,
rebase, history rewrite, or push is authorized.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi5706-wi5441-finalization-scope-repair`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore`: the implementation changes no runtime source or configuration; it
repairs the current-tree and audit state created by an over-broad finalization
commit.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
