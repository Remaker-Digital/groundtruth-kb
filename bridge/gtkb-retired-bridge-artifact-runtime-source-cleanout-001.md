NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-desktop-gtkb-cleanout-2026-06-16
author_model: gpt-5-codex
author_model_configuration: Codex desktop session; Prime Builder under owner-directed bridge cleanup

# Implementation Proposal - Retired Bridge Artifact Runtime Source Cleanout

bridge_kind: prime_proposal
Document: gtkb-retired-bridge-artifact-runtime-source-cleanout
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578
target_paths: ["AGENTS.md","CLAUDE.md",".claude/hooks/**",".claude/rules/**",".codex/gtkb-hooks/**","config/agent-control/**","config/governance/**","config/registry/**","groundtruth-kb/src/**","scripts/**","groundtruth-kb/tests/**","platform_tests/**","groundtruth-kb/docs/**","groundtruth-kb/evidence/**","groundtruth-kb/release-notes-0.6.1.md","applications/Agent_Red/tests/**","docs/design/**","docs/release/**","groundtruth-kb/tests/fixtures/scaffold_golden/**"]

## Summary

Clean the remaining live source, hook, rule, config, test, and scaffold-generator
surfaces that still depend on, generate, require, test for, or instruct agents
to use the retired bridge-index artifact.

This proposal intentionally follows the already-approved skill/template/doc
cleanup and expands scope only where the deterministic tracked-inventory scan
showed unresolved critical hits outside that GO's target paths.

## Owner Decisions / Input

- Mike directed that no backward compatibility should be preserved for the
  retired bridge-index implementation and that failures caused by removing it
  are defects to fix.
- Mike directed that obsolete artifacts are distraction/risk and that mutating
  work must follow the bridge protocol.
- Mike clarified that review separation is session-context based, so a fresh
  headless Codex session may provide LO review even when Codex authored the
  proposal in a different session context.

## Prior Deliberations

- `bridge/gtkb-no-index-skill-template-doc-cleanout-004.md` - GO for cleaning
  skill, template, scaffold-fixture, and public documentation surfaces.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - Loyal Opposition may question cited
  requirements to disambiguate owner intent.
- Owner directive in this session: deterministic scans should identify all
  failures, investigate each one, remediate what is in scope, and record
  blockers for later remediation.

## Specification Links

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/canonical-terminology.md`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `config/agent-control/system-interface-map.toml`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

## Deterministic Scan Evidence

A git-tracked inventory scan for the bridge-specific retired path token found
4,107 tracked-file hits. Historical/audit hits dominate, but the unresolved
critical candidate classes were:

- 23 active startup/rule/hook/config files.
- 79 runtime source/script files.
- 70 test and fixture files.
- 24 unclassified governed docs/config/evidence files.
- 2 public documentation files outside the prior approved doc list.

The prior implementation cleaned canonical skills, generated skill adapters,
primary templates, and public docs in the approved target set. The scan still
shows source-level scaffold generation of stale fixture inventory rows and
active runtime/startup surfaces that require a wider implementation scope.

## Proposed Implementation

1. Replace active startup/rule/hook/config references to the retired artifact
   with dispatcher/TAFE bridge-state authority and versioned bridge-file scans.
2. Remove or retire runtime code paths that generate, mutate, validate, or
   require the retired artifact as live bridge state.
3. Update CLI, doctor, MCP, operating-state, dashboard, and scaffold code so
   health means ability to do the intended bridge work through current
   dispatcher/TAFE state, not presence of retired files.
4. Update tests from old-presence assertions to current no-retired-artifact
   assertions.
5. Regenerate scaffold golden fixtures from corrected scaffold source.
6. Re-run the deterministic scan and classify every remaining hit as:
   `historical_audit_allowed`, `legitimate_non-bridge_name`, `negative_test`, or
   `failure`.

## Acceptance Criteria

- [ ] The retired bridge artifact is not recreated by scaffold, helper, CLI,
  doctor, dispatcher, hook, dashboard, MCP, or test setup paths.
- [ ] Active hooks and startup/rule/control-map surfaces instruct agents to use
  dispatcher/TAFE bridge state and versioned bridge files only.
- [ ] Source modules no longer treat the retired artifact as canonical or
  required for bridge health.
- [ ] Scaffold golden fixtures no longer contain bridge-specific retired path
  references except in explicitly historical audit fixtures, if any.
- [ ] Existing tests that intentionally assert old behavior are revised or
  retired with replacement tests for current behavior.
- [ ] A deterministic tracked-inventory scan has zero `failure` hits for the
  bridge-specific retired path token.
- [ ] Remaining hits are listed in a ledger with path, class, reason, and
  severity.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification evidence |
| --- | --- |
| `.claude/rules/file-bridge-protocol.md` | Deterministic tracked-inventory scan proves active bridge instructions and runtime paths use dispatcher/TAFE state plus versioned files. |
| `config/agent-control/SESSION-STARTUP-INDEX.md` | Startup-surface tests or snapshot checks prove sessions no longer load retired bridge-index authority language. |
| `config/agent-control/system-interface-map.toml` | System-interface tests prove accepted aliases resolve to current dispatcher/TAFE bridge state. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward and records exact commands plus observed results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Scaffold/golden tests prove Agent Red and adopter fixtures remain inside the application boundary. |

Planned command families:

- `python -m pytest groundtruth-kb/tests/test_scaffold_bridge_index.py groundtruth-kb/tests/test_doctor_bridge_accuracy.py -q --tb=short`
- `python -m pytest platform_tests/hooks platform_tests/scripts -q --tb=short`
- `python -m pytest groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_scaffold_isolation.py -q --tb=short`
- Deterministic tracked-inventory scan command from the companion admin CLI, or the current manual equivalent until that CLI is implemented.

## Risk And Rollback

This work touches broad governance/runtime surfaces. Rollback is file-level:
revert the source/rule/test changes from the implementation commit while
preserving bridge audit files. The highest risk is masking a live dependency
instead of replacing it; the deterministic scan ledger and targeted tests are
the required guardrail.
