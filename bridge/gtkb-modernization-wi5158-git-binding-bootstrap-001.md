NEW

# WI-5158 governed Git binding bootstrap and scoped local integration

bridge_kind: prime_proposal
Document: gtkb-modernization-wi5158-git-binding-bootstrap
Version: 001
Author: Codex Prime Builder (harness A)
Date: 2026-07-10T20:25:38Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3618-1eea-7252-b02b-a3b9b6401bf7
author_model: GPT-5 family (Codex)
author_model_version: not exposed by harness
author_model_configuration: Codex desktop, default collaboration mode, interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-WI-5158-PILOT-20260710
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5158

target_paths: [".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5158-001/manifest.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5158-001/command-packet.ps1", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5158-001/initial-registry.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5158-001/preflight-evidence.json", ".gtkb-state/git-lifecycle/branch-bindings.json", ".gtkb-state/git-lifecycle/branch-binding-audit.jsonl", ".gitattributes", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "config/agent-control/system-interface-map.toml", "docs/gtkb-systems-and-tools.md", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/authority.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/bindings.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/scoped_commit.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/promotion.py", "scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "scripts/check_git_branch_binding_promotion.py", "groundtruth-kb/tests/test_cli_git_lifecycle.py", "groundtruth-kb/tests/test_git_lifecycle_models.py", "platform_tests/scripts/test_git_binding_bootstrap.py", "platform_tests/scripts/test_git_branch_binding.py", "platform_tests/scripts/test_git_scoped_commit.py", "platform_tests/scripts/test_git_work_item_promotion.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py", "platform_tests/scripts/test_system_interface_map.py", "platform_tests/scripts/test_gitattributes_lf_policy.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
deferred_bootstrap_da_mutation: true

---

## Summary

Implement the first local, governed Git-lifecycle substrate for GT-KB: versioned project and work-item branch bindings, operation-time wrong-branch and wrong-worktree rejection, scoped automated commits, VERIFIED-only work-item integration into the bound project branch, and bootstrap adoption/recovery. The slice also moves VERIFIED finalization onto the same scoped-commit service so there is one mutation method rather than a second commit path.

The binding service cannot enforce its own first installation before it exists. This proposal therefore uses the one-time bootstrap transition in `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v2. It does not itself authorize that bootstrap. After this proposal receives independent Loyal Opposition `GO`, the Prime Builder may acquire work intent and implementation-start evidence and materialize the exact packet. That packet receives a second independent LO review and a separate owner hash approval before any ref, worktree, registry, audit, or source mutation.

No remote push, GitHub mutation, project-to-`develop` promotion, `stage` operation, dispatcher mutation, quiescence, cleanup, release, or deployment is in scope.

## Current Entry Evidence

- Formal authority is active: `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1, and `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v2.
- The active PAUTH includes only WI-5158, is plan-incomplete, and explicitly forbids shared-checkout work, unapproved bootstrap, remote/GitHub operations, dispatcher control, cleanup, release, and unrelated mutation.
- Exact `develop` base: `5297fc6719a4980ca175e4fe50ec9dbcabfa4a7e`.
- Proposed imported seed: `85fc4900d1257a37be9311f91f5748a118620aeb`; 412 commits, zero merges, commit-inventory SHA-256 `b9ce9302430d1ab9e8ec76cd1d2f80550317e80b2db95c090fa72daa2896e859`, raw-diff SHA-256 `dd9ba16e8bdc48c9e2f2a60540b5fc244c308e87a5117cc71a5e4d534a148f06`.
- Exact archive regression result: 242 passed, 6 failed. The two failure classes are Cursor LF export policy and a system-map authority pointer to an ignored generated dashboard report. Both are explicit targets below; broader decontamination remains out of scope and blocks project promotion.
- At proposal preparation, the deterministic refs, two worktree paths, branch-binding registry, branch-binding audit, bootstrap packet root, and this bridge slug were absent. No different Prime Builder session held an active same-project claim. Every fact is revalidated at each later transition.

## Deterministic Identities

- Manifest: `GBM-WI-5158-001`.
- Project branch: `project/gtkb-platform-modernization-git-lifecycle`.
- Work-item branch: `work-item/wi-5158-implement-governed-project-and-work-item-branch`.
- Project worktree: `.gtkb-state/git-lifecycle/worktrees/project-gtkb-platform-modernization-git-lifecycle`.
- Work-item worktree: `.gtkb-state/git-lifecycle/worktrees/wi-5158-implement-governed-project-and-work-item-branch`.
- Binding registry: `.gtkb-state/git-lifecycle/branch-bindings.json`.
- Append-only audit: `.gtkb-state/git-lifecycle/branch-binding-audit.jsonl`.
- Exact-packet review thread: `gtkb-modernization-wi5158-bootstrap-manifest-review` with `bridge_kind: governance_review`.

The work-item title normalizer produces a 47-character slug before the WI prefix. Names are immutable after activation. A local or remote collision, case-fold collision, pre-existing unbound ref, changed title input, or ambiguous normalization blocks without suffixing or adoption.

## One-Time Bootstrap Review Protocol

The implementation bridge and the exact bootstrap packet use two independent review gates to avoid a circular self-approval path:

1. This NEW proposal receives an independent LO `GO` or `NO-GO`. A `GO` establishes implementation design and target-scope approval only. It is not bootstrap execution authority.
2. Under that current `GO`, the Prime Builder acquires the matching work-intent claim and creates implementation-start evidence without editing source or Git state.
3. The Prime Builder materializes `manifest.json`, `command-packet.ps1`, `initial-registry.json`, and `preflight-evidence.json` under the approved bootstrap packet root. These are runtime review artifacts, not source implementation.
4. A separate `governance_review` bridge proposal presents every byte and hash, exact current authority versions, exact GO path, claim and implementation packet, current `develop`, refs, worktree paths, repository fingerprint, target-cleanliness result, shared-checkout fingerprint, expected before/after states, denial behavior, and recovery commands.
5. A distinct LO session reviews that exact packet. `NO-GO` requires replacement packet material and a new review version. `GO` is packet-review evidence only and cannot mutate Git.
6. The owner receives the exact `GBM-WI-5158-001` content hash and both LO review references in a standalone decision. Only explicit approval activates the bootstrap transaction.
7. Immediately before the first mutation, all evidence is revalidated. Any changed hash, head, ref, path, claim, packet, role, worktree, target, or shared-checkout fingerprint invalidates approval and requires a regenerated review and owner decision.
8. An append-only DA bootstrap-attempt record consumes the exception before the first Git command. After that record, only same-manifest and same-transaction recovery is eligible.

This stricter packet-review step implements the DCL requirement that the complete command packet, initial registry, expected hashes, failure behavior, and recovery commands be independently reviewed without invalidating the implementation thread's current `GO`.

No MemBase or Deliberation Archive mutation is authorized by this proposal or included in its 35-path implementation target set. The single-use bootstrap-attempt DA insertion is a deferred governance transaction: the later exact-manifest `governance_review` must declare `groundtruth.db` and its by-reference finalization treatment, and the owner must explicitly authorize that exact insertion before it occurs. It is never included in the WI source commit.

## Bootstrap Command Semantics

The later content-hashed PowerShell packet may perform only the following ordered local operations:

1. Acquire the repository-scoped bootstrap lock and repeat the complete read-only preflight.
2. Insert the single-use DA attempt record with the manifest hash, transaction ID, authority versions, refs, worktree paths, repository identity, and preflight hash.
3. Use expected-null `git update-ref` transactions to create the project ref at the exact `develop` base and the WI ref at the exact imported seed.
4. Create only the two named isolated worktrees, each attached to its deterministic ref.
5. Atomically install the exact reviewed generation-1 binding registry and append the exact reviewed bootstrap event.
6. Run the reviewed bootstrap validator over refs, ancestry, worktree identity, registry and audit hashes, authority, claim, target paths, imported-seed hashes, and shared-checkout preservation.

Before active validation, the packet cannot edit, stage, commit, reset, clean, move, or delete source or shared-checkout content; push; contact GitHub mutation APIs; change dispatcher state; acquire quiescence; drain or terminate a worker; force-update a ref; rewrite history; or perform cleanup.

Partial failure preserves refs, worktrees, runtime records, and source. Recovery may only finish or reconcile the exact transaction using expected old/new values. It never deletes unique state, chooses another base, renames, suffixes, widens targets, or infers authority from branch existence.

## Binding Registry And Authority

`groundtruth_kb.git_lifecycle` supplies deterministic models, hashing, repository operations, authority resolution, bindings, scoped commits, and local promotion:

- `models.py`: schema-versioned immutable records, canonical JSON, record and envelope hashes, transitions, and validation.
- `repository.py`: canonical repository fingerprint, Git common-directory and worktree identity, repository lock, expected-old ref operations, ancestry, index/diff inspection, and preservation evidence.
- `authority.py`: current MemBase project/WI/PAUTH state, formal carrier versions, proposal and latest `GO`, work-intent ownership, implementation-start packet, target paths, session role/provenance, and dependency evidence. It associates evidence but cannot create authority.
- `bindings.py`: reserve, activate, validate, close, recover, bootstrap adoption, generation compare-and-swap, registry atomic replacement, and audit append.
- `scoped_commit.py`: authorized path/hunk intersection, temporary index, hooks and credential preflight, commit evidence, and unrelated-byte preservation.
- `promotion.py`: current VERIFIED-only work-item integration into exactly the bound project branch.

Every protected mutation revalidates current authority, session, claim, target scope, binding generation, branch, worktree, repository, index, and head immediately before mutation. Cached startup context, copied packets, dispatcher routing, or an earlier successful assertion never suffice.

## Governed CLI

Add the following discoverable commands with deterministic `--dry-run` and JSON behavior:

- `gt git binding create-project`
- `gt git binding create-work-item`
- `gt git binding list`
- `gt git binding show`
- `gt git binding validate`
- `gt git binding close`
- `gt git binding recover`
- `gt commit scoped --binding-id <id>`
- `gt git promote work-item`

`gt git promote project` and `gt git promote stage` are exposed only as explicit fail-closed deferred surfaces pointing to WI-5159. They cannot create a PR, push, or mutate GitHub in this slice.

The system interface map and human companion identify the binding registry as host-local association state, MemBase as lifecycle authority, the CLI as the only ordinary mutation route, and dispatcher configuration as non-authoritative for worker role.

## Scoped Commit And VERIFIED Finalization

`gt commit scoped` computes the allowed staged set from the intersection of active PAUTH, current bridge target paths, current work-intent ownership, active binding, and reviewed hunk evidence. It uses a disposable index, preserves pre-existing staged/unstaged/untracked/ignored state, rejects broad pathspecs and ambiguous mixed-owner hunks, runs canonical hooks and credential checks, and appends evidence linking the resulting commit to the WI, project, PAUTH, bridge, claim, binding, target set, and transaction.

The Claude, Codex, and Cursor `write_verdict.py --finalize-verified` helpers remain byte-identical. After validating verdict structure, review independence, evidence anchors, report claims, and predecessor history, they call the scoped-commit service with the pending VERIFIED verdict as part of the same reviewed transaction. They no longer maintain an independent Git commit implementation.

The service must support the pending-verdict transaction without treating the not-yet-committed VERIFIED file as prior authority. The validated LO verdict body plus current implementation report is the transaction input; the committed verdict becomes durable terminal evidence only if the scoped commit succeeds. Failure removes only the newly written verdict and temporary index while preserving all implementation and unrelated bytes.

## Local Work-Item Integration

After the VERIFIED scoped commit exists, `gt git promote work-item` revalidates the source commit, current terminal verdict, required tests/checks, dependencies, target project binding, and unchanged source/target heads. It integrates only into `project/gtkb-platform-modernization-git-lifecycle`, records source and target bindings plus resulting commit, and marks no lifecycle state on conflict or interruption.

The project branch remains local. This slice cannot push it, open a PR, merge to `develop`, create `stage`, or claim published status. Imported commits are project migration evidence. The WI-5158 attributed diff begins at `85fc4900d1257a37be9311f91f5748a118620aeb`.

## Explicit Baseline Repairs

Two pre-existing failures are included because this slice touches their governed surfaces and cannot claim non-impairment while masking them:

1. Add `.cursor/skills/** text eol=lf` to `.gitattributes`; ensure the three verify helpers export byte-identically on Windows; retain the existing CRLF regression linkage to WI-4722.
2. Change the `dashboard` system-map `authoritative_source` from ignored generated output to tracked generator `scripts/session_self_initialization.py`; retain `docs/gtkb-dashboard/session-startup-report.md` as a generated read surface; update the human companion. The generated report remains ignored and non-authoritative.

No other root residue, `.gtkb-state`, `.groundtruth`, bridge history, memory, dashboard, or baseline cleanup is permitted.

## Cross-Harness Disposition

The governed Git-lifecycle CLI and package are shared platform surfaces, so every harness invokes the same authority, binding, scoped-commit, and promotion implementation. Dispatcher target rules are neither role evidence nor an implementation dependency.

- **Claude Code:** `.claude/skills/verify/helpers/write_verdict.py` remains the canonical helper resource and delegates VERIFIED finalization to `gt commit scoped`.
- **Codex:** `.codex/skills/verify/helpers/write_verdict.py` is regenerated from the canonical Claude skill resource with `scripts/generate_codex_skill_adapters.py`; byte parity with the canonical helper is required.
- **Cursor:** `.cursor/skills/verify/helpers/write_verdict.py` remains the documented fallback copy and must be byte-identical and LF-only. This proposal does not claim that a Cursor adapter generator exists.
- **Antigravity:** `.agent/skills/verify/SKILL.md` continues to invoke the canonical shared Claude helper, so no duplicate Antigravity helper target is required.
- **Ollama/OpenRouter:** provider wrappers continue to invoke the canonical shared Claude helper, so no provider-local helper target is required.

No parity waiver is requested. Implementation verification must run both catalog and operational checks with `python scripts/check_harness_parity.py --all --markdown` and `python scripts/harness_parity_phase2.py --project-root . --format markdown`, plus the existing helper-parity regression tests. A catalog PASS alone is not an operational-readiness claim.

## Managed-Artifact Structural Review

This Prime Builder review is advisory input to the independent bridge verdict; it is not that verdict.

1. **Registry Authority Assessment: PASS.** `config/agent-control/harness-capability-registry.toml` registers `skill.verify` with `.claude/skills/verify/SKILL.md` as its canonical source. The helper is a managed resource beneath that skill. No competing registration was found.
2. **Target-Path Completeness Assessment: PASS (35 declared paths).** The proposal includes the canonical Claude helper, generated Codex mirror, documented Cursor fallback, `.gitattributes`, shared CLI/package surfaces, and focused platform tests. The Codex generator already mirrors helper resources, so generator source modification is unnecessary. The capability registry and Codex/Cursor manifests hash `SKILL.md`, which does not change, so mutating those files would create false churn. Antigravity and provider harnesses consume the canonical shared helper and require no duplicate target.
3. **Stale-Assumption Warnings: none.** Cursor is treated as a documented fallback, not as a generated adapter. No retired Tier A registry, superseded authority, or dispatcher-role inference is used.
4. **Specification Linkage Gap Report: none.** The proposal links the Git-lifecycle carriers and the applicable cross-harness parity ADR/DCL, with executable catalog, operational, byte-parity, and LF checks.
5. **Lifecycle Compliance Status: PASS.** The first filing is `NEW`, the active PAUTH contains only WI-5158, all owner decisions are cited, and no predecessor bridge chain exists for this slug.
6. **Overall Recommendation: GO for independent structural review.** This recommendation concerns proposal completeness only and grants no implementation, bootstrap, Git, or verification authority.

## Specification Links

- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - selects project/WI branches with governed promotion and released-main semantics.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - defines the lifecycle outcome this first substrate must begin satisfying.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - controls registry, bootstrap, binding, commit, integration, recovery, and expected-red later promotion assertions.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires preserved behavior and explicit baseline/final evidence.
- `GOV-WORK-TREE-HYGIENE-001` - requires isolated work and preservation of unrelated dirty state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - limits work to the active PAUTH and WI-5158.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent review, implementation report, and terminal verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal and later report to cite applicable live specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI linkage in the proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires LO to execute and map spec-derived tests before VERIFIED.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires executable evaluator coverage and honest residual red state.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires dependency evidence before local WI integration and later project promotion.
- `ADR-CROSS-HARNESS-PARITY-001` - requires semantic capability equivalence across active harnesses without assuming shared-file invocation.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires catalog and operational parity evidence, typed disposition, and explicit handling of generated and fallback surfaces.
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` - prevents local/project/stage state from being presented as released authority.
- `GOV-STANDING-BACKLOG-001` - keeps WI-5158 and later slices in the canonical MemBase backlog.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires implementation, tests, reports, decisions, and follow-on work to remain one traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit candidate, active, blocked, verified, complete, superseded, and recovery states rather than ambiguous prose.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable capture of the bootstrap decision, risk, evidence, and deferred work.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-CHARTER` - owner-approved scope and exclusions for governed Git lifecycle.
- `DELIB-20260710-GTKB-MODERNIZATION-TWO-TIER-BRANCH-MODEL` - selects project and work-item branch tiers.
- `DELIB-20260710-GTKB-MODERNIZATION-BRANCH-NAMING-RULE` - defines deterministic immutable names.
- `DELIB-20260710-GTKB-MODERNIZATION-BRANCH-BINDING-BOOTSTRAP-DCL-V2-APPROVAL` - approves the one-time bootstrap amendment but not a manifest.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-LEGACY-BASELINE-AUDIT` - freezes the import inventory/diff and decontamination blockers.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-BASELINE-NONIMPAIRMENT-EVIDENCE` - records 242/248 baseline tests and the two bounded repair classes.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-EXECUTION-ENTRY-PACKET` - defines PAUTH, targets, operating mode, tests, order, and retained gates.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-PILOT-AUTHORIZATION` - owner-authorizes PAUTH creation, seed presentation, and this proposal filing only.
- `DELIB-20260710-GTKB-MODERNIZATION-STAGE-CI-RULESET-PROPOSAL` - defers remote project/stage promotion to WI-5159 and WI-5101.
- `INTAKE-c5792b0c` - confirmed governed Git-lifecycle requirement intake.

## Owner Decisions / Input

The owner explicitly approved the Gate 1.5 packet at SHA-256 `571d41ab8b6a3ca5a669aa613100121c01cfb4547cd6898602429d52b388f51d`. The resulting decision `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-PILOT-AUTHORIZATION` authorizes the active PAUTH, proposed seed presentation, interactive-PB plus independent-LO operating mode, and this NEW bridge filing.

That decision explicitly withholds bootstrap, refs, worktrees, registry, source edits, commits, integration, push, GitHub, dispatcher, cleanup, promotion, release, and deployment. A later owner decision must name the exact `GBM-WI-5158-001` hash after both LO reviews and live claim/start evidence.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`, and `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v2 expressly cover this slice, including the otherwise circular first installation. The non-impairment, worktree, PAUTH, bridge, evaluability, dependency, and published-state carriers above close the applicable authority set. No new or revised requirement is needed before implementation review.

## Spec-Derived Verification Plan

| Governing carrier | Required verification | Expected result for WI-5158 |
|---|---|---|
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | CLI, binding, scoped-commit, and local-integration tests | Project/WI tiers and local-only boundary pass; remote tiers remain blocked |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` A1-A5, A7, A9 | New bootstrap/binding/commit/promotion tests plus `gt assert` | A1-A5, A7, A9 pass |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` A6, A8 | Evaluator plus deferred-command tests | Remain honestly red or partial with WI-5159 evidence; no false full PASS |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Exact archived baseline matrix rerun plus focused/full regression | Improves from 242/248 to 248/248; no new failure |
| `GOV-WORK-TREE-HYGIENE-001` | Bootstrap preservation, wrong-worktree, dirty-index, untracked/ignored tests | Shared checkout byte/index fingerprint unchanged; unrelated state preserved |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live PAUTH and negative scope tests | Only WI-5158 and listed classes/paths are eligible |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain, claim, implementation-start, report, independent VERIFIED | No same-session review; no mutation before current evidence |
| Proposal/project linkage DCLs | Compliance audit and phantom-spec sweep | PAUTH/project/WI/target/spec headers parse and resolve |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | LO report mapping and executed commands | Every applicable carrier maps to current test output |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `scripts/check_git_branch_binding_promotion.py` and assertion record | Deterministic current evidence, explicit invalidation, no missing-as-pass |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Work-item promotion dependency/head-change tests | Unsatisfied or changed dependencies block without merge |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Claude/Codex/Cursor helper byte and LF checks, catalog parity, operational parity | No stale adapter or unwaived role-critical gap; shared-helper consumers remain correctly wired |
| `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` | CLI negative tests and audit inspection | No non-main state presented as published and no remote mutation |
| Artifact-oriented ADR/DCL/GOV carriers | DA, bridge, report, test, audit, and backlog linkage inspection | Every decision and transition has one durable carrier and explicit lifecycle state |

Required command set, using the repository venv:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_work_item_promotion.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_system_interface_map.py platform_tests/scripts/test_gitattributes_lf_policy.py groundtruth-kb/tests/test_cli_discoverability.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/scripts/test_parity_coverage_complete.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --markdown
groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --project-root . --format markdown
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py groundtruth-kb/src/groundtruth_kb/git_lifecycle scripts/implementation_start_gate.py scripts/protected_mutation_guard.py scripts/check_git_branch_binding_promotion.py groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_work_item_promotion.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same Python targets>
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli commit preflight --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli assert --spec DCL-GIT-BRANCH-BINDING-PROMOTION-001 --triggered-by WI-5158-verification
git diff --check
```

Bootstrap failure fixtures must cover stale/changed manifest, changed `develop`, existing ref, worktree collision, registry collision, prior attempt, same-project holder, target overlap, dirty shared-index preservation, lock contention, failed ref/worktree/registry/audit steps, crash, and same-manifest recovery. Scoped-commit fixtures must cover mixed hunks, foreign staged content, untracked and ignored files, hook/credential failure, changed head, and commit rollback. Promotion fixtures must cover non-VERIFIED status, stale verdict, dependency failure, wrong project, conflict, changed heads, and interrupted audit.

## Applicability Preflight

Pending-content checks executed against this draft before filing:

- `bridge_applicability_preflight.py`: exit 0, `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `adr_dcl_clause_preflight.py`: exit 0; five clauses evaluated, three `must_apply`, zero evidence gaps, and zero blocking gaps.
- Phantom-spec sweep: 19 unique formal IDs cited, 19 resolved, zero missing.
- Structure: first non-blank token `NEW`; 35 unique inline-JSON target paths; zero unresolved scaffold placeholders.
- Expected warnings identify only absent parent directories/files that this proposal would create later: the new `git_lifecycle` package and the not-yet-materialized bootstrap/registry runtime files. The warnings grant no creation authority and must remain absent until their respective gates.

These checks are rerun against the final composed body by the Codex non-bypass bridge writer and remain review evidence rather than implementation authority.

## Risk / Rollback

Highest risk is the one-time bootstrap: a partial local ref/worktree/registry transaction cannot be made reusable by deleting evidence. Mitigation is exact owner-hashed input, two independent LO reviews, expected-old ref updates, repository lock, append-before-mutation DA reservation, atomic registry replacement, append-only audit, shared-checkout before/after fingerprint, and same-manifest recovery only.

The source implementation is intended to finish as one scoped WI commit on the bound WI branch. A later rollback is a governed revert commit, never reset, amend, rebase, force update, or deletion. Failed implementation leaves the WI branch/worktree and source evidence intact. Failed local integration leaves both branches intact and advances no lifecycle state.

The imported baseline is not rolled back or promoted by this slice. Artifact Decontamination remains responsible for its broader residue. No cleanup action is a recovery mechanism.

## Bridge Filing

This proposal is filed as `bridge/gtkb-modernization-wi5158-git-binding-bootstrap-001.md` through the credential-scanned Codex non-bypass writer after role eligibility, author metadata, compliance, work-intent, target JSON, formal-ID, and preflight checks pass. Dispatcher/TAFE state plus the numbered file chain remain the live workflow state. No aggregate queue artifact is created.

## Recommended Commit Type

`feat(git-lifecycle): add governed branch binding bootstrap`

The eventual diff adds a new governed lifecycle capability. Baseline repairs are subordinate to making the same touched integration surfaces portable and valid.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
