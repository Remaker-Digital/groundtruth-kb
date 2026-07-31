REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5272 Ordinary-Worker Prompt And Skill Contract - Foundation-Aware Revision

bridge_kind: prime_proposal
Document: gtkb-wi5272-ordinary-worker-prompt-skill-contract
Version: 005
Responds to: bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-004.md
Revises: bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5272-ORDINARY-WORKER-PROMPT-SKILL-CONTRACT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5272
Related Work Items: WI-5268, WI-5270, WI-5271, WI-5464
target_paths: ["config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/activity-disposition-profiles.toml", ".claude/rules/codex-session-bootstrap.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-loyal-opposition-runbook.md", ".claude/skills/bridge/SKILL.md", ".claude/skills/verify/SKILL.md", ".claude/skills/dispatcher-control/SKILL.md", ".claude/skills/bridge-config/SKILL.md", ".claude/skills/bridge-reconciliation/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/verify/SKILL.md", ".codex/skills/dispatcher-control/SKILL.md", ".codex/skills/bridge-config/SKILL.md", ".codex/skills/bridge-reconciliation/SKILL.md", ".codex/skills/MANIFEST.json", "platform_tests/skills/test_skill_catalog_contract.py", "platform_tests/scripts/test_session_startup_control_map.py", "platform_tests/scripts/test_benchmark_activity_envelope_load.py", "platform_tests/scripts/test_wi5266_envelope_resource_routing.py"]
implementation_scope: configuration_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: docs:

## Revision Claim

Every version-004 blocking condition is accepted and re-evaluated against
current canonical state.

The foundation is now real, evaluated authority:

- `bridge/gtkb-dispatcher-black-box-spec-foundation-034.md` is independent
  `VERIFIED` and committed at
  `6262862c8852d4d94530a4074a3047f921e7164e`;
- all five foundation records named by versions 003 and 004 exist in MemBase
  at version 2, `status=specified`, with one executable assertion each;
- fresh assertion execution reports aggregate `PASS` for the activity-envelope
  record and for the worker-safe-packet, ordinary-worker-boundary,
  worker-context-facade, and foundation-first records;
- the active WI-5272 PAUTH includes all five now-real records, permits only
  bridge/metadata/configuration/source/test work for WI-5272, and forbids
  dispatcher mutation, destructive cleanup, Git push/history rewrite,
  release, deployment, credentials, and external systems.

This revision does not authorize current implementation. The required
worker-context and mediated-view predecessors are not both terminal:

- WI-5270's version-004 `VERIFIED` candidate is untracked and not
  focused-finalized; WI-5464 owns its correction and re-evaluation;
- WI-5271 has reached only a new foundation-aware `REVISED` v005 and remains
  awaiting independent review, implementation, verification, and focused
  finalization.

In addition, `.codex/skills/MANIFEST.json` is currently dirty from separately
owned work. No WI-5272 process may overwrite or absorb that state.

The current session has a build activity envelope. It may file this corrected
proposal, but it cannot perform the configuration-like prompt, rule, skill,
adapter, startup, or activity-profile mutations proposed here. Any future
implementation must begin in an initialized `ops` activity envelope with a
fresh reviewed baseline and all ordinary bridge/start/operation-time authority.

The owner's dispatcher-configuration troubleshooter hold remains absolute.
This WI targets ordinary-worker prompt/skill/startup behavior only. It does not
authorize dispatcher topology, dispatcher configuration/runtime state, TAFE
state, harness registry state, dispatch ranking, or independent
troubleshooter-owned mutation. Any overlap discovered at operation time blocks
the WI.

## Findings Addressed

### F1 - Five governing foundation records were absent

Resolved. Fresh governed reads return version 2, `specified`, one assertion
each for:

- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`;
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`;
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`;
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`;
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`.

Fresh `gt assert --spec` runs report aggregate `PASS`.

### F2 - The foundation-first owner decision was omitted

Resolved. This revision explicitly carries
`DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` and derives its
predecessor gates from that decision.

### F3 - Foundation state needed a fresh filing-time check

Resolved for proposal review. Foundation v034 is committed `VERIFIED`, the
five records are version 2, and their assertions pass. Implementation must
repeat the checks and stop on any drift.

### Corrected version-003 predecessor and activity-envelope requirements

Retained as hard implementation barriers. WI-5270 and WI-5271 must both be
independently terminal and focused-finalized. The implementation session must
carry an initialized `ops` activity envelope; build or ordinary state cannot
substitute for it. A fresh claim, schema-v3 start packet, exact target
authorization, and operation-time checks remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved version-2 foundation now supplies canonical ordinary-worker,
safe-packet, activity-envelope, worker-context-facade, and foundation-first
requirements. This proposal aligns prompts and governed skills to those
requirements; it creates no new authority and requests no exception.

## Proposed Scope

1. Rewrite ordinary-worker startup, role, bridge, verification,
   dispatcher-control, bridge-config, and bridge-reconciliation guidance so
   ordinary PB and LO sessions consume assigned work through the terminal
   worker-context and mediated packet facades.
2. Preserve role-adapted baseline behavior and knowledge while defining an
   ordinary worker mechanically as a session envelope without an initialized
   activity envelope.
3. Remove ordinary-flow instructions that require direct raw bridge-file,
   bridge-state, dispatcher configuration/runtime, TAFE, harness-registry,
   ranking/scheduling, lease, process, or other-harness inspection.
4. Keep explicit operator, maintenance, `ops`, and case-authorized `build`
   routes where canonically required, without allowing those routes to leak
   into ordinary-worker instructions.
5. Regenerate Codex skill adapters and manifest from canonical Claude skill
   sources, preserving generated-artifact provenance and catalog parity.
6. Add deterministic tests covering ordinary-worker language, ops/build
   distinctions, facade references, raw-internal exclusions, adapter
   generation, catalog consistency, and startup resource-routing behavior.
7. Do not mutate dispatcher topology/configuration/runtime, TAFE state, harness
   registry/identity, hooks, credentials, release/deployment surfaces, adopter
   application files, Git remote state, or independent troubleshooter work.

## Hard Implementation-Start Gates

1. Foundation v034 remains `VERIFIED` and commit
   `6262862c8852d4d94530a4074a3047f921e7164e` remains its durable carrier.
2. All five version-2 foundation records remain present with approved content
   and passing assertions.
3. WI-5270 reaches fresh independent terminal `VERIFIED` after WI-5464
   re-evaluation and is focused-finalized at an exact commit.
4. WI-5271 reaches independent terminal `VERIFIED` and is focused-finalized,
   providing the exact mediated command/schema that prompts and skills will
   name.
5. The implementation session is initialized with an `ops` activity envelope.
   Ordinary or build envelope state fails closed.
6. The dispatcher-configuration troubleshooter hold remains honored. Any
   dispatcher config/runtime target or independently owned hunk is excluded
   and blocks implementation rather than being adopted.
7. The active WI-5272 PAUTH remains current and unchanged in scope.
8. All 22 targets are clean and unclaimed, or every differing byte has a
   separately terminal, focused-finalized owner whose exact resulting hash is
   adopted by fresh independent review. In particular, the current dirty
   `.codex/skills/MANIFEST.json` state must be resolved or explicitly adopted.
9. A fresh WI-5272 `GO`, exact same-session `go_implementation` claim,
   schema-v3 implementation-start packet, and per-target operation-time
   authorization all cover the same project, work item, thread, targets,
   mutation classes, session, and `ops` activity envelope.
10. Any dispatcher/TAFE/harness-state, credential, release, deployment, Git
    push/history rewrite, destructive cleanup, or unrelated worktree request
    fails closed.

## Cross-Harness Disposition

| Harness | Disposition | Required evidence |
| --- | --- | --- |
| Claude Code | Canonical prompt/rule/skill behavior is in scope. | Ordinary PB/LO instructions use the same terminal facades and exclusion language. |
| Codex | Generated adapter and manifest parity is in scope. | Regeneration from canonical sources plus adapter/catalog hash and focused test evidence. |
| Cursor | No Cursor-specific target is changed by this WI. | Typed non-applicability remains valid only if shared ordinary-worker behavior reaches Cursor through existing common surfaces; otherwise a reviewed follow-up is required before VERIFIED. |
| Antigravity | No Antigravity-specific target is changed by this WI. | Typed non-applicability remains valid only if shared ordinary-worker behavior reaches Antigravity through existing common surfaces; otherwise a reviewed follow-up is required before VERIFIED. |
| Headless providers | Provider dispatcher configuration/runtime is out of scope. | Shared packet semantics only; provider-specific gaps route to WI-5275/WI-5276. |

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`

## Owner Decisions / Input

No new owner decision is required for proposal review. The owner-defined
ordinary-worker baseline, foundation-first order, safe packet content,
raw-bridge protection, and ops/build authority split are now canonical
version-2 requirements.

The dispatcher-configuration troubleshooter hold remains binding. This
proposal cannot authorize any dispatcher configuration/runtime mutation, and
its future configuration-like prompt/skill implementation cannot begin
outside an initialized `ops` activity envelope.

## Specification-Derived Verification

| Requirement | Executable verification | Required result |
| --- | --- | --- |
| Ordinary-worker definition | Deterministic scans and startup tests for absent activity envelope plus role-adapted baseline language | PB/LO ordinary workers retain baseline behavior but acquire no protected-surface authority. |
| Worker-safe packet and facade routing | Exact scans for the focused-finalized WI-5270/WI-5271 commands and assignment-content contract | Ordinary guidance names only the governed facade routes for assigned content. |
| Protected-internal exclusion | Negative scans across all canonical targets and generated projections | No ordinary-flow raw bridge/state/config/runtime/TAFE/harness/ranking/lease/process dependency remains. |
| Activity-envelope split | Tests over ordinary, `ops`, build-without-case, and case-authorized build text/behavior | `ops` owns configuration-like mutation; build internals remain case-specific; no substitution. |
| Dispatcher hold | Target inventory and operation-time ownership check | No dispatcher configuration/runtime or troubleshooter-owned byte is changed. |
| Generated adapter provenance | Canonical skill regeneration check, manifest comparison, and skill catalog tests | Codex adapters derive from canonical Claude sources; manifest is exact and no foreign state is overwritten. |
| Cross-harness parity | Shared-surface tests plus typed applicability review for Cursor, Antigravity, and headless providers | No unsupported harness silently receives weaker ordinary-worker protection. |
| Foundation and operation-time authority | Fresh foundation/commit/spec/assertion, predecessor, PAUTH, claim, schema-v3 start, target, activity-envelope, and per-target checks | Every layer agrees; drift blocks before mutation. |
| Worktree hygiene | Exact target hashes/status before and after plus target-only diff/whitespace checks | Only WI-5272-owned hunks change. |
| Mandatory bridge gates | Candidate/live applicability and clause preflights | No missing specs, errors, or blocking gaps. |

Required focused commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_skill_catalog_contract.py platform_tests/scripts/test_session_startup_control_map.py platform_tests/scripts/test_benchmark_activity_envelope_load.py platform_tests/scripts/test_wi5266_envelope_resource_routing.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/skills/test_skill_catalog_contract.py platform_tests/scripts/test_session_startup_control_map.py platform_tests/scripts/test_benchmark_activity_envelope_load.py platform_tests/scripts/test_wi5266_envelope_resource_routing.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/skills/test_skill_catalog_contract.py platform_tests/scripts/test_session_startup_control_map.py platform_tests/scripts/test_benchmark_activity_envelope_load.py platform_tests/scripts/test_wi5266_envelope_resource_routing.py
git diff --check -- <all 22 exact targets>
```

## Acceptance Criteria

1. Ordinary PB and LO instructions retain role-adapted baseline behavior while
   using only worker-context and mediated packet facades for assigned content.
2. No ordinary-flow prompt, startup overlay, rule, or governed skill requires
   raw bridge/state, dispatcher config/runtime, TAFE, harness registry,
   ranking/scheduling, lease, process, or other-harness inspection.
3. `ops` configuration authority and case-specific build-internals authority
   are explicit, mechanically distinct, and non-substitutable.
4. Canonical Claude sources, generated Codex adapters, and the manifest are
   consistent and independently tested.
5. WI-5270 and WI-5271 are terminal/focused-finalized before implementation;
   the dirty manifest and all other target ownership are cleanly resolved.
6. The dispatcher-configuration hold is preserved and no dispatcher/TAFE/
   harness-state, credential, deployment, release, Git push/history,
   destructive cleanup, or unrelated mutation occurs.

## Scope Changes

- Replaces absent foundation citations with live version-2 MemBase authority.
- Adds the omitted foundation-first owner decision and committed foundation
  evidence.
- Adds explicit WI-5270, WI-5271, WI-5464, ops-envelope, dirty-manifest, and
  dispatcher-configuration-hold barriers.
- Preserves the original 22 prompt/rule/skill/adapter/test targets and behavior
  goal.

## Pre-Filing Preflight Subsection

Candidate applicability preflight:

- Command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5272-ordinary-worker-prompt-skill-contract --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5272-ordinary-worker-prompt-skill-contract-005.md --json`
- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- packet hash:
  `sha256:a82f3c3f508d33e68a431a281ff3cd7702bef8f18e9d19c5736b4037c800e6ea`

Mandatory clause preflight:

- Command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5272-ordinary-worker-prompt-skill-contract --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5272-ordinary-worker-prompt-skill-contract-005.md`
- clauses evaluated: 5
- `must_apply: 3`
- `may_apply: 2`
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0
- result: PASS (exit 0)

## Risk And Rollback

The primary risks are weakening ordinary-worker isolation, naming a facade
before its exact command is final, overwriting generated-manifest work, and
crossing into independently owned dispatcher configuration. Terminal
predecessors, exact generated provenance, activity-envelope enforcement,
target ownership, and operation-time checks address those risks.

Rollback is a focused revert of WI-5272-owned hunks only. No whole-file
restore, foreign-hunk absorption, database replacement, bridge-history
rewrite, dispatcher/configuration rollback, or unrelated cleanup is
authorized.

## Files Expected To Change

- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `config/agent-control/activity-disposition-profiles.toml`
- `.claude/rules/codex-session-bootstrap.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`
- `.claude/skills/bridge/SKILL.md`
- `.claude/skills/verify/SKILL.md`
- `.claude/skills/dispatcher-control/SKILL.md`
- `.claude/skills/bridge-config/SKILL.md`
- `.claude/skills/bridge-reconciliation/SKILL.md`
- `.codex/skills/bridge/SKILL.md`
- `.codex/skills/verify/SKILL.md`
- `.codex/skills/dispatcher-control/SKILL.md`
- `.codex/skills/bridge-config/SKILL.md`
- `.codex/skills/bridge-reconciliation/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `platform_tests/skills/test_skill_catalog_contract.py`
- `platform_tests/scripts/test_session_startup_control_map.py`
- `platform_tests/scripts/test_benchmark_activity_envelope_load.py`
- `platform_tests/scripts/test_wi5266_envelope_resource_routing.py`

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
