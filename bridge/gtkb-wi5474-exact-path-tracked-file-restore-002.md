GO
::init gtkb pb
::open test

# GT-KB Bridge Verdict - gtkb-wi5474-exact-path-tracked-file-restore - 002

bridge_kind: lo_verdict
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 002 (GO; independent Loyal Opposition review)
Responds to: bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md
Date: 2026-07-18 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 20dd407b-d159-4c05-9700-63511dadff11
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code headless Loyal Opposition review subagent; independent session context distinct from proposal author (019f6668-9974-7d72-a456-826f9a67e627)

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5474
Recommended commit type: `feat:`

## Review Independence

This review runs from a fresh, independent session context
(`20dd407b-d159-4c05-9700-63511dadff11`) distinct from the proposal
author's session context (`019f6668-9974-7d72-a456-826f9a67e627`, Codex A).
No same-session self-review condition applies.

## Specification Links

Carried forward unchanged from the reviewed proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

All 16 links independently confirmed to exist in MemBase this session
(`KnowledgeDB.get_spec(<id>)` for each id; all FOUND, status `specified` or
`verified`; none missing).

## Prior Deliberations

- No prior Deliberation Archive record found that rejects a single-path,
  worktree-only, explicit-commit restore operation added to
  `groundtruth_kb.git_lifecycle`. Independent semantic searches this
  session ("exact path tracked file restore git lifecycle", "git_lifecycle
  package restore-deleted-path WI-5474", "WI-5421 git lifecycle package
  baseline adoption", "reject new git_lifecycle CLI command capability
  sprawl scope creep") returned no on-topic rejection.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` independently
  fetched and confirmed: authorizes bounded PAUTH carriers and governed
  proposals for newly discovered fleet/bridge/TAFE/harness defects while
  preserving every later implementation gate; matches the proposal's
  characterization exactly.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
  independently fetched and confirmed: freezes dispatcher-configuration
  mutation during independent troubleshooting; WI-5474's target_paths
  (git_lifecycle source + one new test file) do not touch dispatcher
  configuration, so this proposal is compatible with the hold.
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md` (VERIFIED)
  independently read in full: confirms the adopted Git-lifecycle package
  baseline this proposal extends is terminal-VERIFIED and its eight files
  were byte-for-byte hash-matched by that verdict.
- `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-008.md` (NO-GO)
  and `-009.md` (REVISED) independently read: confirm the deleted-
  predecessor finalization-blocker history that motivates WI-5474,
  including the -008 NO-GO's explicit recommendation to restore via "the
  canonical `groundtruth_kb.git_lifecycle` governed path" -- a path this
  session independently confirmed does not yet exist (see Findings, F1).

## Findings

### F1 -- Capability gap independently reproduced (informational)

Claim: the governed Git-lifecycle package has no exact-path tracked-file
restore surface.

Evidence: `python -m groundtruth_kb.git_lifecycle --help` lists only
`create, attach, show, validate, preserve, promote, close, resume,
recover, drain` -- no restore command. AST inspection
(`ast.parse`/`ast.walk`) of
`groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py` shows
`GitRepository` methods limited to `__init__, run, current_branch, head,
branch_exists, create_branch, checkout, is_ancestor, status, is_clean,
committed_paths, parents, scoped_commit, merge_no_ff` -- no blob-lookup or
worktree-restore primitive. The same AST inspection of `service.py` (78
methods total) confirms no restore-related method exists either.

Impact: none -- confirms the defect motivating the proposal is real, not
fabricated.

### F2 -- Current Preconditions independently verified byte-for-byte (informational)

Evidence: fresh SHA-256 recomputation this session of the three existing
source targets exactly matches the proposal's claimed hashes:

- `__main__.py`: `ab9a09206280d0931ac1a3ce3f2c1ff9b4a000938be6c8762293a2db7a1d4521`
- `repository.py`: `baea9c96fd6bbf8f63ae990dacbcb32b64a2fe588dc47d897943a6183114fedb`
- `service.py`: `b2ebf9db4f3c8d188ef8b7036569e0121a40f1127e88a8bd97ddf79c934a2d2c`

`git status --short` on all four declared target paths (including the
not-yet-existing test file) returned empty -- clean/absent exactly as
claimed. `platform_tests/scripts/test_git_lifecycle_exact_restore.py`
confirmed absent from disk both times checked (initial pass and
immediately pre-write freshness re-check).

Impact: none -- the Current Preconditions section is accurate.

### F3 -- V1/V2 PAUTH narrative and operation-time envelope independently verified (informational)

Evidence: a direct query of the `project_authorizations` table shows
`PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-20260717`
at status `revoked`, `change_reason`: "Superseded by V2 after detecting
noncanonical tafe_mutation and runtime_state_mutation forbidden-operation
tokens; no WI-5474 proposal or implementation used V1." Cross-checked
against `config/governance/project-authorization-operation-taxonomy.toml`:
`tafe_mutation` and `runtime_state_mutation` are absent from the
`[[operation]]` table (only `runtime_state` exists, and only as a
*mutation_class* alias -- a different namespace); V2's nine forbidden
tokens (`credential_lifecycle, destructive_cleanup, dispatcher_mutation,
external_system_mutation, git_commit, git_history_rewrite, git_push,
production_deployment, release`) are all registered canonical operation
names.
`PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718`
is `active`, `included_work_item_ids: ["WI-5474"]` (restrictive per
`DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`), `expires_at: null`,
`owner_decision_deliberation_id: DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
(independently confirmed to exist and to authorize this class of work),
`allowed_mutation_classes: ["bridge", "metadata", "governance_evidence",
"source", "test"]`.

A live call to the production evaluator
(`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`)
against the exact V2 envelope and all four declared target paths, with
operation `protected_mutation`, returned `allowed: True`,
`reason_code: allowed`, with each path classified:
`__main__.py -> source`, `repository.py -> source`, `service.py ->
source`, `test_git_lifecycle_exact_restore.py -> test` -- both classes are
PAUTH-allowed. This is a live run of the actual gate function Prime
Builder's implementation-start authorization will invoke, not a manual
trace of the code.

Impact: none -- the V1/V2 narrative and the active V2 envelope are
accurate and technically sufficient for the declared target_paths.

### F4 -- No backlog conflict (informational)

Evidence: `gt backlog list --component git-lifecycle` returns only WI-5187
(a differently-scoped, pre-WI-5421 "minimal Git binding substrate" item
whose scope is already superseded by the now-VERIFIED WI-5421 package
adoption) and WI-5474 itself. `gt backlog list --contains
"restore-deleted-path"` and `--contains "exact-path restore"` both return
empty. No duplicate or conflicting future work found.

Impact: none.

### F5 -- Existing frozen acceptance baseline independently re-run green (informational)

Evidence: `pytest platform_tests/scripts/test_modernization_git_lifecycle.py
-q --tb=short` -> `2 passed, 1 warning in 510.24s` this session. The
elevated duration versus WI-5421's VERIFIED verdict's 163.36s figure is
consistent with concurrent multi-agent host load, which that verdict's own
text flags as expected timing variance; the pass/fail outcome is
unaffected. Confirms the WI-5421 baseline this proposal extends remains
healthy going into implementation.

Impact: none.

### F6 -- Live-execution risk is narratively controlled, not mechanically gated (observation, non-blocking)

Observation: the proposal's commitment that the new `restore-deleted-path`
operation will not be run against the live GT-KB worktree during
implementation or verification is enforced by the proposal's own text and
Acceptance Criteria, and by the PAUTH's `git_commit` / `git_push` /
`git_history_rewrite` forbidden-operation tokens (which block persisting
any incidental live-tree mutation as a commit) -- but the implementation-
start operation-time gate governs *file-edit* mutation classes; it has no
mechanism to distinguish "edit the CLI source" from "invoke the CLI
command the edit just added." This mirrors the same soft-control pattern
WI-5421 relied on, whose own VERIFIED verdict checked for live-tree
footprints post hoc (`git log --oneline -5` / `git diff --stat` scoped to
the target directory, confirmed empty) rather than relying on a hard
runtime block.

Recommended action: the post-implementation report and its VERIFIED review
should include the same style of live-tree footprint check WI-5421 used
(fresh `git status`/`git log` scoped to `bridge/` and the four target
paths, confirming no live invocation occurred), rather than relying solely
on the proposal's stated intent. This is a verification-time checklist
item, not a proposal-blocking defect -- the design itself (temp-repository
-only test fixtures) already keeps the tested code path off the live tree.

### F7 -- "Multi-path input" denial phrasing is slightly ambiguous (observation, non-blocking)

Observation: `--path` is specified as a single required argument (no
`action="append"`), so literal `--path a --path b` repetition is an
argparse-level last-value-wins case, not a denial case. The "multi-path"
denial the proposal describes is better read as "a single `--path` value
that encodes multiple paths via pathspec/brace/comma/wildcard syntax" --
which the existing `normalize_repo_path()` /
`_SAFE_COMPONENT = ^[A-Za-z0-9._/-]+$` validator this proposal reuses
already rejects (no `*`, `?`, `{`, `}`, `,`, or whitespace permitted).

Recommended action: the implementation report should state explicitly
which interpretation the "multi-path" denial test case exercises, so the
spec-to-test mapping is unambiguous at verification time. Non-blocking.

## Backlog Conflict & Project Authorization Check

- No conflicting or duplicate backlog work found (F4).
- `PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718`
  independently confirmed `active`, restrictively scoped to `WI-5474`,
  using only registered forbidden-operation tokens, with an owner-decision
  deliberation that independently checks out, and a live envelope
  evaluation that returns `allowed: True` for all four declared target
  paths (F3).
- `WI-5474` and `TEST-11572` independently confirmed to exist in MemBase,
  correctly linked to this bridge thread and to the WI-5421/WI-5362
  predecessor threads.

## Applicability Preflight

- packet_hash: `sha256:403427f45cf6a97cfaaa3c243376f6d14c7ce0335d2b3448dcce65d81ee43846`
- bridge_document_name: `gtkb-wi5474-exact-path-tracked-file-restore`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "platform_tests/scripts/test_git_lifecycle_exact_restore.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md`
- operative_file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Preflight run twice this session (initial pass and immediately pre-write
freshness re-check); identical result both times.

## Clause Applicability

- Bridge id: `gtkb-wi5474-exact-path-tracked-file-restore`
- Operative file: `bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 =
  pass. Observed exit: 0 (both runs).

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | (not applicable, may_apply, no bulk-ops evidence required) | blocking | blocking |

No blocking gaps: exit code was 0 both runs.

## Commands Executed

- `python -m groundtruth_kb.cli bridge state-report --json` (initial full
  queue scan; confirmed slug at latest_status `NEW` v001)
- `python -m groundtruth_kb.cli bridge show gtkb-wi5474-exact-path-tracked-file-restore --json --compact`
  (run twice: initial pass and immediately pre-write freshness re-check;
  both `NEW` v001)
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore`
  (run twice, identical both times)
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5474-exact-path-tracked-file-restore`
  (run twice, identical both times; exit 0 both times)
- `python -m groundtruth_kb.cli deliberations search "exact path tracked file restore git lifecycle"`
- `python -m groundtruth_kb.cli deliberations search "git_lifecycle package restore-deleted-path WI-5474"`
- `python -m groundtruth_kb.cli deliberations search "WI-5421 git lifecycle package baseline adoption"`
- `python -m groundtruth_kb.cli deliberations search "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION"`
- `python -m groundtruth_kb.cli deliberations search "reject new git_lifecycle CLI command capability sprawl scope creep"`
- `python -m groundtruth_kb.cli deliberations get DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- `python -m groundtruth_kb.cli deliberations get DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `hashlib.sha256(...)` fresh recomputation against the three existing
  target files
- `git status --short -- <all four declared target paths>`
- confirmed `platform_tests/scripts/test_git_lifecycle_exact_restore.py`
  absent from disk
- `python -m groundtruth_kb.cli projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718 --json`
- `python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`
- direct sqlite query on `project_authorizations` filtered
  `id LIKE '%WI5474%'` ordered by `changed_at` (V1 revoked / V2 active
  history)
- read `config/governance/project-authorization-operation-taxonomy.toml`
  (canonical operation/mutation-class registry) in full
- read `groundtruth_kb/governance/project_authorization_operation_time.py`
  (`classify_target`, `normalize_operation`, `evaluate_envelope`)
- live call: `evaluate_envelope(authorization=<V2 envelope>, requested_operation="protected_mutation", target_paths=<all four declared targets>)` -> `allowed: True`
- `KnowledgeDB.get_spec(<id>)` for all 16 linked specification ids
- `KnowledgeDB.get_work_item(<id>)` for `WI-5474`, `WI-5421`, `WI-5362`,
  `WI-5444`
- `KnowledgeDB.get_test('TEST-11572')`
- `python -m groundtruth_kb.cli backlog list --component git-lifecycle --json`
- `python -m groundtruth_kb.cli backlog list --contains "restore-deleted-path" --json`
- `python -m groundtruth_kb.cli backlog list --contains "exact-path restore" --json`
- `python -m groundtruth_kb.git_lifecycle --help`
- AST inspection (`ast.parse` + `ast.walk`) of `repository.py` and
  `service.py` class/method inventories
- read `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py` in
  full (219 lines)
- read `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py` in
  full (132 lines); confirmed `normalize_repo_path` and `_SAFE_COMPONENT`
- `git log --oneline -3 -- bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-002.md`
  (confirmed predecessor restoration)
- `pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short`
  (fresh full rerun: 2 passed in 510.24s)

## Loyal Opposition Disposition

GO. The proposal is well-scoped, technically sound, and every load-bearing
factual claim in it was independently reproduced against live source, live
MemBase state, and live git/PAUTH state this session -- not accepted on
narrative trust. Specifically:

1. The claimed capability gap is real (F1).
2. The "Current Preconditions" hashes, clean-target claims, and absent-
   test-file claim are byte-for-byte accurate (F2).
3. The V1-revoked/V2-active PAUTH narrative is accurate; V2 uses only
   registered forbidden-operation tokens, restrictively scopes
   `included_work_item_ids: ["WI-5474"]`, and a live envelope evaluation
   against the actual production gate function returns `allowed: True`
   for all four declared target paths (F3).
4. No backlog conflict or duplicate future work exists (F4).
5. The existing frozen Git-lifecycle acceptance baseline this proposal
   extends is independently confirmed green (F5).
6. Both mandatory preflights pass clean with zero blocking gaps, run
   twice for freshness, immediately before this write.
7. All 16 linked specifications exist and are correctly characterized.
8. The Prior Deliberations, Owner Decisions / Input, Requirement
   Sufficiency, and Recommended Commit Type sections in the proposal are
   all present, substantive, and independently verified accurate.
9. The proposed CLI/service/repository design (`restore-deleted-path`
   reusing the existing `normalize_repo_path` validator and the existing
   argparse-subparser/`_execute` dispatch pattern) is architecturally
   consistent with the current package and additive-only, preserving the
   "existing Git-lifecycle behavior remains green" acceptance criterion.
10. Two non-blocking observations (F6, F7) are recorded for the
    post-implementation report to address; neither is a proposal defect.

Prime Builder implementation remains bound by every Hard Implementation-
Start Gate the proposal itself states (active V2 PAUTH selected, this
thread at latest GO, all four target paths clean/absent at a freshly
reviewed baseline, exact claim + schema-v3 implementation-start packet,
operation-time validation immediately before mutation) and by the
`DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` freeze
(inapplicable to this proposal's target_paths, but binding on the
authoring session generally).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*