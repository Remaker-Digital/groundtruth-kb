REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5428-codex-hook-parity-restoration
Version: 005
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5428-codex-hook-parity-restoration-004.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project Authorization Version: 5
Owner Decision: DELIB-202667714
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5428
project_id: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
work_item_ids: ["WI-5428"]
source_spec_ids: ["GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001", "ADR-CODEX-HOOK-PARITY-FALLBACK-001", "SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001", "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001", "GOV-HARNESS-ROLE-PORTABILITY-001", "DCL-SESSION-ROLE-RESOLUTION-001", "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001", "GOV-RELEASE-READINESS-GOVERNED-TESTING-001"]
target_paths: [".codex/config.toml", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: configuration,source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_evidence_work_in_scope: false

# WI-5428 Revised Proposal — restore Codex hook parity under current Assurance PAUTH v5

## Revision And Authority Correction

This version responds to the independent NO-GO in version 004. It preserves the
accepted four-path technical design from version 001 while replacing stale
Assurance PAUTH v3 / `DELIB-202666274` prose with the current operation-time
authority:

- authorization
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  version 5, row 947, active, list-free, and unexpired;
- owner decision `DELIB-202667714`;
- active parent project
  `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` and active member WI-5428;
- allowed classes `bridge`, `metadata`, `configuration`, `source`, `test`,
  `documentation`, `runtime_state`, and `governance_evidence`;
- forbidden operations `credential_lifecycle`, `destructive_cleanup`,
  `dispatcher_mutation`, `external_system_mutation`, `git_history_rewrite`,
  `git_push`, `production_deployment`, and `release`;
- TAFE mutation remains independently forbidden by the owner contract and the
  PAUTH scope summary.

The version-002 GO is not executable because it omitted mandatory Clause
Applicability evidence. Version 003 correctly stopped implementation; version
004 independently confirmed that defect and required this revision. Only a
fresh independent GO on version 005 may authorize a later claim/start attempt.

## First-Line Role And Draft Claim

- The owner-declared interactive role is Prime Builder; Prime Builder may
  author `REVISED` and may not author `GO`, `NO-GO`, or `VERIFIED`.
- Session `019fb19b-7814-73c1-8707-204e432cbf00` acquired the exact
  `draft` claim for this slug at `2026-07-30T18:08:04Z`, row 35083, with no
  competing exact-thread claim.
- The draft claim authorizes proposal publication only. It is not a
  `go_implementation` claim and cannot authorize protected target mutation.

## Claim

Restore the still-missing Codex hook parity implementation through current
carrier WI-5428. Enable the supported Windows hook surface, make the parity
checker interpret the repository's existing no-window batch fan-out without
requiring duplicate registrations, and stop the wrap-up trigger from forcing a
role profile.

The correction is exactly four clean targets. It does not rewrite or normalize
the invalidly closed WI-5364 chain. That history remains append-only evidence;
WI-5428 receives its own proposal, GO, schema-v3 start, implementation report,
independent VERIFIED, and governed atomic local finalization.

## Fresh Reproduction

At HEAD `8a35eabc8cae297cbd295223d6ec904aa15212b8`, with bytecode and pytest
cache writes disabled, the focused suite collected 14 tests and returned
**5 failed, 9 passed, 1 warning in 0.98s**. The failures are:

1. `test_codex_hook_parity_passes_for_repository_configuration`;
2. `test_codex_userpromptsubmit_wrapup_hook_has_headroom_timeout`;
3. `test_codex_hook_parity_requires_session_lifecycle_hook_intent`;
4. `test_codex_hook_commands_avoid_shell_specific_command_substitution`;
5. `test_codex_parity_repository_configuration_wires_bridge_compliance`.

The checker exits 1 with exactly eight findings: hooks disabled; formal-artifact
PreToolUse not recognized; workstream PreToolUse, Bash, apply_patch, and
UserPromptSubmit routes not recognized; session-lifecycle UserPromptSubmit not
recognized; and the wrap-up dispatcher forcing a role. The missing-route
findings are batch-discovery false negatives: `.codex/hooks.json` already
routes the governed handlers through `run_py_no_window --batch`. Adding direct
duplicates would execute governance or lifecycle behavior twice.

## Fresh Target And Excluded-File Preimages

`git status --porcelain=v2 -- <four targets>` returned no records. The four
proposal targets are clean in worktree and index:

| Target | Git blob | SHA-256 |
| --- | --- | --- |
| `.codex/config.toml` | `7deb13bee852276a44b15c23700637bf060f0480` | `f0593f1a674e9411c9680f41101a3f6545f27c98a74dde7edba15c4f2f3cb00f` |
| `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | `dde84f254eaeeaa6a62b58836d4930371a37ccdc` | `3cda1c538e2cb30d4253435de7a0dc00763ab29b8defd402f8a79ec5cdec5486` |
| `scripts/check_codex_hook_parity.py` | `a471fc7bfbc75c8ff9cf6033437fb31fc77655f1` | `6a06f31c90867837954be2ddc40412f6f22b66514230f3619f490455e7959936` |
| `platform_tests/scripts/test_codex_hook_parity.py` | `1cd59cfa2e608ed2312e287ad3502e11a1599da7` | `ebb306c210e0ed990a21c60a103c0d3c342d2db51f6df6fba069e48e202f1b49` |

The two routing files are non-target hash locks and must remain byte-identical:

| Excluded file | Git blob | SHA-256 |
| --- | --- | --- |
| `.codex/hooks.json` | `e4881dca1b6a97c2c95ccc678a24697073909656` | `abd3c88f2b89958601acfe86483de50caf4c283eaa1bc27e1a58c76f5951d44a` |
| `.codex/gtkb-hooks/run_py_no_window.py` | `5e7bcf8f21b85bb243dee55fec5be11afe7cb9d3` | `575b07a5376171d27c9ba766abf0fa515b216d49ee7df63217be176a43f88a54` |

All paths are under `E:\GT-KB`; no Agent Red, adopter, external repository, or
harness-local scratch artifact is a dependency.

## Foreign Overlap And Serialization

- `gtkb-file-move-rename-canonicalization-v3` broadly names
  `.codex/config.toml`, but latest v006 is NO-GO, Stage B is paused, no exact
  claim exists, and the config target is clean. WI-5428 must recheck that
  thread and target hash at implementation start and must not adopt foreign
  hunks.
- WI-5275 historically names `scripts/check_codex_hook_parity.py`, but its
  latest v004 is NO-GO and its current work is broader black-box enforcement;
  no current claim or target mutation exists.
- WI-5364 names the same four paths but WI-5428 is the explicit active
  successor. The WI-5364 latest role-envelope defect and false closure remain
  historical evidence, not active authority or shared ownership.
- The wider worktree is dirty with unrelated program work. Proposal filing and
  any later atomic finalization must remain exact-path scoped and must not stage,
  reset, absorb, or modify unrelated bytes.

Any new competing claim, changed target/excluded hash, resumed overlapping
thread, or required fifth implementation path fails closed before start.

## Requirement Sufficiency

Existing requirements sufficient. The live-Windows hook ADR, Codex parity
specification, batch-aware cross-harness constraint, session-role resolution
rules, modernization nonimpairment contract, governed testing requirement, and
current project PAUTH completely determine this four-path correction. The
observed failure is implementation residue after a false closure, not a missing
policy decision. No new or revised normative requirement is needed before
implementation.

## Cross-Harness Disposition

No typed waiver is requested.

- Codex: enable the existing no-window batch topology, evaluate its expanded
  surfaces, and remove forced wrap-up role injection. Each handler continues to
  execute once.
- Claude: no settings or hook mutation; existing direct registrations remain a
  reference behavior.
- Cursor: no hook mutation; shared workstream, role, and governance semantics
  remain regression inputs.
- Antigravity: no hook mutation; lack of native hook events remains an explicit
  architectural surface difference, not a target for registration cloning.
- Ollama, OpenRouter, Goose, and Alibaba Cloud Studio: no interactive hook
  configuration, eligibility, routing, or dispatcher change.

## Intuitiveness / Nonimpairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5428 fresh reproduction under DELIB-202667714 with the WI-5364 false-closure trail preserved",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py",
  "before_behavior": "Codex hooks are disabled, five of fourteen focused tests fail, the checker reports eight findings because it does not expand the existing batches, and wrap-up forces a role profile.",
  "after_behavior": "Codex hooks use the existing no-window batches, parity expands each route exactly once, all fourteen focused tests pass, and wrap-up discovers role authority canonically.",
  "self_descriptive_naming": "The checker reports outer batch commands separately from expanded event and matcher surfaces while retaining direct-wrapper compatibility.",
  "obsolete_guidance_disposition": "Remove the stale disabled-hooks comment and forced role argument; retain fallback only for an empirically demonstrated runtime regression.",
  "history_preservation": "Do not mutate WI-5364 bridge or backlog evidence; cite it from the WI-5428 implementation report.",
  "essential_context_preservation": "Keep live-hook availability, batch fan-out, single execution, no-window containment, role resolution, fallback conditions, and the complete false-closure trail visible.",
  "baseline": {
    "focused_parity_passed": 9,
    "focused_parity_failed": 5,
    "checker_findings": 8,
    "hooks_enabled": false,
    "target_paths_clean": 4
  },
  "expected_result": {
    "focused_parity_passed": 14,
    "focused_parity_failed": 0,
    "checker_findings": 0,
    "hooks_enabled": true,
    "duplicate_handler_registrations_added": 0
  },
  "rollback": "Through a separately governed transaction, restore only the four WI-5428 hunks to their recorded pre-start blobs; preserve registrations and all bridge history.",
  "hard_invariants": [
    "no governance or lifecycle handler executes twice because of this repair",
    "all hook subprocesses remain under the existing no-window runner",
    "missing or malformed batch evidence fails parity closed",
    "interactive session role is not forced by the wrap-up adapter",
    "no harness is disabled, deprioritized, rerouted, or made ineligible",
    "no dispatcher, TAFE, registry, registration, or historical WI-5364 artifact is mutated"
  ],
  "fail_closed_conditions": [
    "fresh independent GO or matching schema-v3 start is absent",
    "any target or excluded-file preimage changes",
    "a competing claim or overlap becomes active",
    "required batch evidence is unreadable, malformed, incomplete, or absent",
    "a hook bypasses the no-window runner or the role override remains",
    "focused parity, runtime containment, quality, or cross-harness tests fail"
  ]
}
```

## Proposed Scope

1. In `.codex/config.toml`, replace only the stale disabled-hooks comment and
   set `[features].hooks = true`; preserve unrelated bytes.
2. In `session_wrapup_trigger_dispatch.py`, remove only command injection of
   `--role-profile` and the `_interactive_role_profile()` result. Preserve the
   latch, session envelope, no-window execution, trigger semantics, and let
   `session_self_initialization.py` resolve role authority.
3. In `check_codex_hook_parity.py`, reuse the existing public batch-aware
   `scripts.parity_discovery_diff.enumerate_hook_surfaces(config_data,
   project_root=...)`. Do not create a second parser.
4. Validate expanded event-and-matcher surfaces for formal-artifact governance,
   workstream Bash/apply_patch/UserPromptSubmit, session lifecycle, and bridge
   compliance. Fail closed on absent, malformed, unreadable, or incomplete
   batch definitions.
5. Preserve direct-wrapper compatibility, validate the no-window outer batch
   wrapper, reject shell command substitution, and retain per-child timeout
   enforcement rather than inventing a conflicting aggregate timeout.
6. Update the focused test to assert expanded registered routes and cover valid
   batch, absent/malformed/unreadable/incomplete batches, direct wrappers,
   hooks enabled, dynamic role, and no duplicate routing.
7. Do not edit `.codex/hooks.json`, `run_py_no_window.py`, batch definitions,
   other harness configs, dispatcher/TAFE state, harness registry, MemBase, or
   WI-5364 history.

## Implementation-Start Sequence

After an independent evidence-complete GO on version 005, Prime Builder must:

1. re-read the physical latest bridge file and check exact/overlap claims;
2. validate PAUTH v5 at operation time against active project membership,
   requested classes, target classifications, forbidden operations, and the
   exact four-file cohort;
3. re-hash all four targets and both excluded routing files and fail closed on
   any mismatch;
4. acquire the exact `go_implementation` claim and produce a valid named
   schema-v3 implementation-start packet for this proposal/GO pair;
5. mutate only the four approved targets, preserving foreign/unrelated bytes;
6. run the complete verification matrix and file an implementation report;
7. obtain independent VERIFIED; then use only the approved atomic local
   finalization route. No push, release, deployment, or TAFE/dispatcher action
   is permitted.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667714` is the current owner decision for Assurance PAUTH v5 and
  governed local atomic finalization.
- `DELIB-202666274` is historical authority for the earlier Assurance envelope;
  it is retained as context but is not the operation-time PAUTH decision cited
  by this revision.
- `DELIB-202666774` and `DELIB-202667009` require the WI-5364 false-closure and
  role-envelope evidence to remain append-only and visible.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` establishes that
  active project membership, not legacy per-WI approval state, carries current
  implementation approval.

## Owner Decisions / Input

- Owner answer: `Approve Assurance PAUTH v4` in the current owner conversation.
  The governed append-only authorization record materialized that approval as
  active PAUTH version 5, row 947, with owner-decision evidence
  `DELIB-202667714`.
- Owner doctrine: implementation approval is per project; every work item must
  have one parent project and inherits the current whole-project PAUTH rather
  than relying on a legacy per-WI approval field.

No new AUQ is required. WI-5428 is an active member of that owner-approved
Assurance project, and list-free PAUTH v5 supplies project-wide implementation
approval for the declared classes. This does not waive any bridge, claim/start,
testing, verification, exact-target, or atomic-finalization gate.

## Clause Applicability

Version 004 independently executed the mandatory gate against the operative
proposal and reported 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`, zero
must-apply evidence gaps, and zero blocking gaps. This revision preserves and
updates the evidence for the four must-apply clauses:

| Clause | Applicability | Evidence in version 005 |
| --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | Every target and verification dependency is under `E:\GT-KB`; adopter and external roots are excluded. |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | Physical v001-v004 chain is preserved; v005 responds to exact v004 NO-GO and awaits an independent new verdict. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | Exact four targets, source specs, PAUTH v5, owner decision, scope, commands, and acceptance results are linked here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | The matrix below maps live-hook, batch, role, nonimpairment, isolation, and release-readiness requirements to executable checks. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | WI-5428 remains the visible single carrier; no backlog batch operation occurs. |

The candidate must separately pass both mandatory pre-filing commands with no
missing required/advisory specs and no blocking gaps before publication.

## Specification-Derived Verification Plan

| Requirement | Command/evidence | Required result |
| --- | --- | --- |
| Live Codex hooks | Parse `.codex/config.toml`; run `groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py` | `[features].hooks = true`; checker PASS, zero findings. |
| Batch-aware parity | `platform_tests/scripts/test_codex_hook_parity.py` | Valid expanded batches pass; absent, malformed, unreadable, and incomplete definitions fail closed; 14/14 focused tests pass. |
| Dynamic role | `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py` and command-construction inspection | No `--role-profile`; canonical session-role discovery passes. |
| No-window containment | Run `test_codex_hook_runtime_containment.py`, `test_codex_hook_batch_output.py`, `test_codex_no_window_timeout_alignment.py`, and `test_codex_shell_no_window_wrapper.py` | No console, wrapper, timeout, batch-output, or shell-substitution regression. |
| Checker compatibility | Run `test_check_codex_hook_parity.py`, `test_check_codex_hook_parity_resolution_table.py`, and `test_codex_hook_parity_resolution_table_drift.py` | Parser/direct-wrapper/batch resolution remains deterministic; no table drift. |
| Cross-harness nonimpairment | Run `platform_tests/scripts/test_check_harness_parity.py` | Other harness behavior and explicit parity dispositions remain green. |
| Python quality | `ruff check` and `ruff format --check` on the three Python targets | Zero findings and formatting drift. |
| Exact scope | Revalidate PAUTH/claim/start; hash four targets and two exclusions; `git diff --check -- <four>`; inspect scoped status/diff | Only the four approved hunks change; exclusions and unrelated bytes remain unchanged. |
| Audit preservation | Hash/inspect WI-5364 bridge chain and cite it in the report | Historical bytes and false-closure evidence remain unchanged and visible. |

## Acceptance Criteria

1. Codex hooks are enabled on the supported Windows runtime.
2. The checker exits 0 with PASS and zero findings.
3. All 14 focused parity tests pass, including fail-closed batch fixtures.
4. Every required governance/lifecycle handler has exactly one expanded route
   per event and matcher; no duplicate direct registration is added.
5. `.codex/hooks.json` and `run_py_no_window.py` retain their exact hashes.
6. The wrap-up adapter no longer injects `--role-profile`; canonical role tests
   pass.
7. No-window, timeout, checker-resolution, Ruff, and cross-harness regressions
   pass.
8. Only the four authorized target hunks change; unrelated worktree state is
   neither staged nor mutated.
9. WI-5364 history remains byte-identical and is cited in the report.
10. A fresh independent GO, matching schema-v3 start, implementation report,
    independent VERIFIED, and governed atomic finalization exist before
    completion is claimed.

## Risks And Rollback

The primary risk is double execution from literal registrations layered over
existing batch fan-out; the proposal forbids that design. Other risks are a
second parser drifting from the public enumerator, silent acceptance of
incomplete batch evidence, forced-role persistence, concurrent overlap, and
accidental absorption of unrelated dirty bytes. Every case is mapped to a
fail-closed precondition or regression check.

Rollback requires a separately governed transaction and restores only the four
WI-5428 implementation hunks to the recorded pre-start blobs. It never rewrites
bridge history, WI-5364 records, hook registrations, batch definitions,
dispatcher/TAFE state, Git history, or unrelated work.

## Files Expected To Change

- `.codex/config.toml`
- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

## Files Explicitly Excluded

- `.codex/hooks.json`
- `.codex/gtkb-hooks/run_py_no_window.py`
- `bridge/gtkb-wi5364-codex-hook-batch-parity-001.md` through `-004.md`
- all MemBase project/backlog/authorization rows
- all dispatcher, TAFE, harness-registry, credential, Git-push, deployment,
  release, destructive-cleanup, and external-system surfaces

## Non-Approval

This REVISED proposal performs no target or KB mutation and does not authorize
implementation by itself. Protected work remains prohibited until a fresh
independent GO, exact operation-time claim/start packet, target revalidation,
and all later report/verification/finalization gates are satisfied.
This proposal performs no formal-artifact approval-evidence or approval-packet
work and does not target `.groundtruth/formal-artifact-approvals/**`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
