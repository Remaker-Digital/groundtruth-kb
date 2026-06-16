NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-bridge-index-retirement-cleanout-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# Bridge Index Retirement Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-bridge-index-retirement-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth.db", "AGENTS.md", "CLAUDE.md", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", ".claude/rules/**", ".claude/skills/**", ".claude/hooks/**", ".claude/settings.json", ".codex/skills/**", ".codex/gtkb-hooks/**", ".codex/hooks.json", ".agent/skills/**", ".api-harness/skills/**", "config/agent-control/**", "config/dispatcher/**", "config/governance/**", "config/registry/**", "docs/**", "applications/Agent_Red/CLAUDE_ARCHIVE.md", "applications/Agent_Red/docs/**", "applications/Agent_Red/tests/**", "scripts/**", "groundtruth-kb/CHANGELOG.md", "groundtruth-kb/release-notes-*.md", "groundtruth-kb/docs/**", "groundtruth-kb/src/**", "groundtruth-kb/templates/**", "groundtruth-kb/tests/**", "platform_tests/**", "bridge/gtkb-bridge-index-retirement-cleanout-*.md", "bridge/INDEX.md"]

implementation_scope: membase, source, config, cli, tests, skills, hooks, templates, protected_narrative, historical_classification
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Remove all live dependencies on the retired `bridge/INDEX.md` implementation.
The file is already absent and that absence is now the desired invariant:
`bridge/INDEX.md` must not exist, must not be generated as compatibility output,
and must not be read, written, restored, scaffolded, or cited as live bridge
authority.

The only acceptable remaining references to the old bridge index are historical
audit references that are clearly marked as historical, archived, or quoted as
evidence of retired behavior. Any active instruction, runtime module, hook,
template, test, health command, status command, skill, scaffold, generated
surface, or startup payload that still depends on `bridge/INDEX.md` is a defect.

This proposal intentionally does not update `bridge/INDEX.md`. The currently
documented bridge-propose helper path still advertises an INDEX compatibility
write; that behavior is part of the cleanup scope and must not be used to file
this proposal.

## Specification Links

- `DELIB-20263438` - owner agreement that bridge dispatch is rule-based and
  independent from operating role assignment; the old file-index bridge model
  must not confuse the new dispatcher implementation.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher state, target
  resolution, and audit recording belong to the centralized dispatcher path.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - bridge work routing is based on
  envelope dimensions such as harness, role, topic, and prompt, not a
  monolithic index file.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative dispatch rules are the
  routing authority.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - `::open <activity>` is part of dispatch
  eligibility input.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session subject/envelope state must
  be read from durable envelope state, not inferred from index entries.
- `SPEC-TAFE-R4` - target selection applies hard gates before availability,
  cost, quality, and precedence tie-breakers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - currently contradictory legacy authority
  text that must be revised or superseded so it no longer requires
  `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this work must remain
  bridge-reviewed and spec-derived despite the retired index writer.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner's correction is a durable
  architecture/process requirement, not a transient preference.

## Prior Deliberations

- `DELIB-20263438` - owner decision for corrected role/dispatch architecture.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - dispatch hard gates before
  calibrated selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-V1-DISPATCH-POLICY-20260612` - conservative
  deterministic v1 dispatch routing.
- `DELIB-20260635` and `DELIB-20260637` - session/topic envelope containment.
- Current owner directives in this session:
  - "`bridge/INDEX.md` must not exist."
  - "We do not want backward compatibility."
  - "We want to rip out all traces of the old bridge implementation and retain
    nothing except historical artifacts for audit purposes."
  - "Remember: every mutating task requires the bridge protocol."

## Owner Decisions / Input

No further owner decision is required before Loyal Opposition review. The owner
has explicitly selected the no-backward-compatibility path and confirmed that
mutating cleanup work must proceed through the bridge protocol.

## Requirement Sufficiency

Existing requirements are sufficient for the cleanup. The owner decision
clarifies that any compatibility output for the old bridge index is not a
requirement; it is contradictory legacy behavior. The implementation may need
to update or retire formal artifacts whose current text still declares
`bridge/INDEX.md` authoritative.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not preserve credentials, environment values, or cloud-service secrets while sweeping old bridge text. | Credential scan on bridge artifacts plus review of changed files. | |
| CQ-PATHS-001 | Yes | Mutate only in-root GT-KB files listed in `target_paths`; do not use external roots. | Root-boundary review and `git diff --name-only`. | |
| CQ-COMPLEXITY-001 | Yes | Prefer deleting or retiring index-specific code over adding adapters that hide the legacy dependency. | Source review and search for old parser/writer surfaces. | |
| CQ-CONSTANTS-001 | Yes | Replace magic bridge-index names with dispatcher/TAFE authority constants where a runtime path remains. | Ruff plus targeted source review. | |
| CQ-SECURITY-001 | Yes | Health/status must not imply cloud or deployed-service mutation authority; cloud changes remain oversight-gated. | Health CLI tests and prompt/rule review. | |
| CQ-DOCS-001 | Yes | Active docs and instructions must state no compatibility bridge and no `bridge/INDEX.md`. | Repository search with historical/audit exceptions only. | |
| CQ-TESTS-001 | Yes | Tests must prove absence of `bridge/INDEX.md` and dispatcher/TAFE functionality without it. | Targeted pytest commands in verification plan. | |
| CQ-LOGGING-001 | Yes | Dispatch status/health should expose blocked/failed routing caused by missing new-state dependencies. | Bridge health/status JSON assertions. | |
| CQ-VERIFICATION-001 | Yes | Treat any break from the removed index as a defect to fix before VERIFIED. | Full search, targeted tests, and CLI health commands. | |

## Implementation Plan

1. **Freeze the invariant.** Treat `bridge/INDEX.md` absence as PASS. Add tests
   or health assertions that fail if runtime code, scaffolds, or helpers
   recreate it.

2. **Classify references.** Run a full repository search for `bridge/INDEX.md`,
   `INDEX.md`, bridge-index parser/writer names, compatibility-view language,
   and related error codes. Classify each hit as historical audit evidence,
   active instruction text, source/runtime dependency, scaffold/template,
   test fixture/assertion, or formal artifact requiring revision/retirement.

3. **Rewrite active guidance.** Update `AGENTS.md`, `CLAUDE.md`, active rules,
   startup overlays, session-start payload sources, skills, system maps, and
   dashboards so agents are told: no index, no compatibility output, dispatcher
   and TAFE-backed bridge state only.

4. **Remove runtime dependencies.** Replace bridge-index readers, writers,
   serializers, parsers, scaffold generators, dispatcher fallbacks, health
   checks, and status surfaces with dispatcher/TAFE-backed APIs. Delete or
   retire commands whose sole purpose is mutating `bridge/INDEX.md`.

5. **Fix health semantics.** Update `gt bridge dispatch health`, `gt status`,
   project doctor checks, startup reports, and hook health checks so they
   reveal ability to dispatch and complete work under the new model.

6. **Update tests and fixtures.** Convert tests that create or require
   `bridge/INDEX.md` into tests that prove the file is absent and that
   dispatcher/TAFE state handles queue/actionability. Historical fixtures may
   remain only when clearly labeled as old-format audit input.

7. **Preserve historical artifacts.** Keep versioned `bridge/*.md` files as the
   audit trail unless separately approved for archival relocation. Do not edit
   prior bridge verdict/proposal files to rewrite history.

8. **Regenerate adapters.** Regenerate cross-harness skill adapters after
   canonical Claude skill sources are corrected.

## Spec-Derived Verification Plan

```text
Test-Path bridge/INDEX.md
```

Expected: `False`.

```text
rg -n "bridge/INDEX[.]md|INDEX\\.md|BridgeIndex|bridge index|INDEX entry|INDEX update|INDEX insertion|ERR_NO_INDEX_ENTRY|BRIDGE_INDEX|compatibility view|compatibility output" AGENTS.md CLAUDE.md .agent .api-harness .claude .codex config docs groundtruth-kb applications scripts platform_tests --glob "!archive/**" --glob "!memory/**" --glob "!harness-state/session-envelope-archive/**" --glob "!bridge/**" --glob "!**/__pycache__/**"
```

Expected: no active references except explicitly historical/audit-labeled
fixtures or test inputs.

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
```

Expected: pass. Proves dispatcher config/status/health and dispatch routing do
not need `bridge/INDEX.md`.

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_startup_index.py platform_tests/hooks/test_workstream_focus.py -q --tb=short
```

Expected: pass. Proves startup/user-visible prompts no longer instruct agents
to read or restore `bridge/INDEX.md`.

```text
python -m pytest groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_cli_bridge_index.py groundtruth-kb/tests/test_bridge_status_driver.py -q --tb=short
```

Expected: updated or retired tests pass. Any remaining test that requires
`bridge/INDEX.md` is a cleanup failure unless it is explicitly testing
historical import/audit behavior.

```text
python -m ruff check groundtruth-kb/src scripts platform_tests
python -m ruff format --check groundtruth-kb/src scripts platform_tests
```

Expected: pass for touched Python paths.

```text
python -m groundtruth_kb bridge dispatch status --json
python -m groundtruth_kb bridge dispatch health --json
python -m groundtruth_kb status
```

Expected: status/health report dispatch readiness, target eligibility, and last
dispatch results without reading or recreating `bridge/INDEX.md`.

## Risks / Rollback

Primary risk: the current codebase still contains many bridge-index readers and
tests, so removing compatibility will reveal breakage across startup, hooks,
doctor checks, scaffolding, and dispatcher status. That is intended. Failures
caused by missing `bridge/INDEX.md` are defects to fix, not reasons to restore
the file.

Second risk: deleting or rewriting historical bridge audit files could destroy
traceability. Mitigation: preserve prior versioned `bridge/*.md` files as audit
history and only classify or relocate them through reviewed follow-on work.

Rollback for active source/config/doc changes is a normal revert of this slice.
Rollback must not recreate `bridge/INDEX.md`; if the new implementation fails,
the correct rollback is to restore the last dispatcher/TAFE-backed healthy
state or pause dispatch, not to restore the retired index.
