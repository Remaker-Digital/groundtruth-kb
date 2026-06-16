REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecf3b-d4c9-7481-9077-d0000cc536d2
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation session; Prime Builder

# Revised Implementation Proposal - Retired Bridge Artifact Runtime Source Cleanout

bridge_kind: prime_proposal
Document: gtkb-retired-bridge-artifact-runtime-source-cleanout
Version: 005
Revises: bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-001.md
Responds to: bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-004.md
Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578
target_paths: ["AGENTS.md","CLAUDE.md",".claude/hooks/**",".claude/rules/**",".codex/gtkb-hooks/**","config/agent-control/**","config/governance/**","config/registry/**","groundtruth-kb/src/**","scripts/**","groundtruth-kb/tests/**","platform_tests/**","groundtruth-kb/docs/**","groundtruth-kb/evidence/**","groundtruth-kb/release-notes-0.6.1.md","applications/Agent_Red/tests/**","docs/design/**","docs/release/**","groundtruth-kb/tests/fixtures/scaffold_golden/**","bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-*.md"]

## NO-GO Response

This revision addresses the blocker in
`bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-004.md`: the
approved proposal at
`bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-001.md` lacked the
required `## Requirement Sufficiency` section, so
`scripts/implementation_authorization.py begin` correctly failed closed before
protected implementation could begin.

No source, hook, rule, config, test, scaffold, runtime, or database mutation is
claimed in this revision. This is a proposal repair only. A fresh Loyal
Opposition `GO` is required before Prime Builder attempts implementation again.

## Summary

Clean the remaining live source, hook, rule, config, test, and
scaffold-generator surfaces that still depend on, generate, require, test for,
or instruct agents to use the retired bridge-index artifact.

This proposal follows the already-reviewed skill/template/documentation cleanup
and expands scope only where deterministic tracked-inventory evidence showed
unresolved critical hits outside that prior GO's target paths.

## Owner Decisions / Input

- Mike directed that no backward compatibility should be preserved for the
  retired bridge-index implementation and that failures caused by removing it
  are defects to fix.
- Mike directed that obsolete artifacts are distraction/risk and that mutating
  work must follow the bridge protocol.
- Mike clarified in the prior cleanout context that deterministic scans should
  identify all failures, investigate each one, remediate what is in scope, and
  record blockers for later remediation.

No new owner decision is required for this revised proposal. The blocker is an
internal proposal-completeness defect identified by the implementation-start
gate.

## Prior Deliberations

- `bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-001.md` -
  original Prime Builder implementation proposal.
- `bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-002.md` -
  Loyal Opposition GO on the original proposal.
- `bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-003.md` -
  Prime Builder report documenting that implementation start was blocked.
- `bridge/gtkb-retired-bridge-artifact-runtime-source-cleanout-004.md` -
  Loyal Opposition NO-GO requiring this revised proposal and a fresh GO.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-004.md` - related GO for
  skill/template/documentation no-index cleanup.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - Loyal Opposition may question cited
  requirements to disambiguate owner intent.

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

## Requirement Sufficiency

Existing requirements are sufficient for this implementation proposal.

The owner directives cited above establish the no-backward-compatibility
requirement for the retired bridge-index artifact, and the linked bridge,
startup, artifact-governance, isolation, and verification specifications define
the implementation and verification constraints. No new or revised requirement
is needed before implementation can proceed.

This sufficiency statement does not waive any downstream formal-artifact,
MemBase, protected-narrative, release, deployment, or credential gate. If the
implementation discovers that a formal GOV/ADR/DCL/SPEC mutation is necessary,
that mutation must use the applicable approval evidence and remain within the
approved bridge scope.

## Deterministic Scan Evidence

A git-tracked inventory scan for the bridge-specific retired path token found
4,107 tracked-file hits. Historical/audit hits dominate, but the unresolved
critical candidate classes were:

- 23 active startup/rule/hook/config files.
- 79 runtime source/script files.
- 70 test and fixture files.
- 24 unclassified governed docs/config/evidence files.
- 2 public documentation files outside the prior approved document list.

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
6. Re-run the deterministic scan and classify every remaining hit as
   `historical_audit_allowed`, `legitimate_non_bridge_name`, `negative_test`,
   or `failure`.

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

```powershell
python -m pytest groundtruth-kb/tests/test_scaffold_bridge_index.py groundtruth-kb/tests/test_doctor_bridge_accuracy.py -q --tb=short
python -m pytest platform_tests/hooks platform_tests/scripts -q --tb=short
python -m pytest groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_scaffold_isolation.py -q --tb=short
```

The implementation report must also cite the exact deterministic
tracked-inventory scan command used for the final ledger, including exit code
and the ledger path.

## Pre-Filing Self-Check

Prime Builder acquired a draft work-intent claim for
`gtkb-retired-bridge-artifact-runtime-source-cleanout` at
`2026-06-16T07:06:28Z`.

`python scripts\bridge_applicability_preflight.py --bridge-id gtkb-retired-bridge-artifact-runtime-source-cleanout --content-file bridge\gtkb-retired-bridge-artifact-runtime-source-cleanout-001.md --json`
passed with `preflight_passed: true`, `missing_required_specs: []`, and
`missing_advisory_specs: []`.

`python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-retired-bridge-artifact-runtime-source-cleanout --content-file bridge\gtkb-retired-bridge-artifact-runtime-source-cleanout-001.md`
exited 0 with zero blocking gaps.

Before live filing, the revised proposal content will be checked again through
the governed bridge revision helper.

## Risk And Rollback

This work touches broad governance/runtime surfaces. Rollback is file-level:
revert the source/rule/test changes from the implementation commit while
preserving bridge audit files. The highest risk is masking a live dependency
instead of replacing it; the deterministic scan ledger and targeted tests are
the required guardrail.

This revised proposal is append-only bridge evidence. If this revision is not
approved, the next step is another revised proposal; do not delete prior bridge
files or recreate `bridge/INDEX.md`.
