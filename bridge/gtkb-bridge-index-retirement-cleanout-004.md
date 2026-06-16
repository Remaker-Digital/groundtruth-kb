REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-bridge-index-retirement-cleanout-revision-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# Bridge Index Retirement Cleanout Proposal - Revision After NO-GO

bridge_kind: prime_proposal
Document: gtkb-bridge-index-retirement-cleanout
Version: 004
Responds to: bridge/gtkb-bridge-index-retirement-cleanout-003.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4578

target_paths: ["groundtruth.db", "AGENTS.md", "CLAUDE.md", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", ".claude/rules/**", ".claude/skills/**", ".claude/hooks/**", ".claude/settings.json", ".codex/skills/**", ".codex/gtkb-hooks/**", ".codex/hooks.json", ".agent/skills/**", ".api-harness/skills/**", "config/agent-control/**", "config/dispatcher/**", "config/governance/**", "config/registry/**", "docs/**", "applications/Agent_Red/CLAUDE_ARCHIVE.md", "applications/Agent_Red/docs/**", "applications/Agent_Red/tests/**", "scripts/**", "groundtruth-kb/CHANGELOG.md", "groundtruth-kb/release-notes-*.md", "groundtruth-kb/docs/**", "groundtruth-kb/src/**", "groundtruth-kb/templates/**", "groundtruth-kb/tests/**", "platform_tests/**", "harness-state/harness-registry.json", "harness-state/harness-identities.json", "bridge/gtkb-bridge-index-retirement-cleanout-*.md", "bridge/gtkb-lo-review-dispatch-reliability-*.md", "bridge/INDEX.md"]

implementation_scope: membase, source, config, cli, tests, skills, hooks, templates, protected_narrative, historical_classification, harness_dispatch_reliability
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This revision keeps the core invariant from `001`: `bridge/INDEX.md` must not
exist and must not be regenerated as compatibility output. It addresses the
`003` NO-GO by making the bootstrap work explicit: mandatory bridge gates,
preflight scripts, dispatcher queue ingestion, and LO review delivery must be
converted to no-index operation before broad cleanup proceeds.

This revision also records the inventory discovered after the initial proposal:
with session archives and drift backups excluded, active/non-archive search
still found 390 files and 1,848 lines related to `bridge/INDEX.md`, `INDEX`
bridge parsers/writers, compatibility-view language, or associated error codes.

The work belongs under the existing umbrella project
`PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`, but that project currently contains
obsolete compatibility-view backlog items that must be retired or superseded:

- `WI-4508` - "Dual-write mode: TAFE + generated INDEX.md" is now contrary to
  the owner directive.
- `WI-4577` - "Post-cutover INDEX archival ineffectiveness" is obsolete as
  framed, because the desired invariant is no generated INDEX at all.
- Phase 6 "Compatibility View" in the TAFE project needs to become
  "No-Compatibility Cutover Cleanup" or be retired in favor of this work.

The revised scope is therefore not "clean up docs." It is a no-backward-
compatibility bridge cutover cleanup program that removes active INDEX
dependencies while preserving versioned bridge artifacts as historical audit
records.

## Specification Links

- `DELIB-20263438` - owner agreement that role, dispatchability, and rule-based
  dispatch are independent.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher state and audit belong
  to the centralized dispatcher path.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - bridge work routing depends on
  harness, role, topic, prompt, and envelope data.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative dispatcher rules are routing
  authority.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - `::open <activity>` participates in
  dispatch eligibility.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session state must be read from
  durable session-envelope surfaces.
- `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, and `SPEC-TAFE-R6` - dispatcher hard gates,
  health, and telemetry must replace index-derived actionability.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - must be revised or superseded because its
  current INDEX-canonical clause contradicts the owner directive.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the cleanup itself remains
  bridge-reviewed and spec-derived.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner correction is durable
  architecture/process authority.

## Prior Deliberations

- `DELIB-20263438` - owner decision for corrected role/dispatch architecture.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - dispatch hard gates before
  calibrated selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-V1-DISPATCH-POLICY-20260612` - conservative
  deterministic v1 dispatch routing.
- `DELIB-20260635` and `DELIB-20260637` - session/topic envelope containment.
- Owner directives in this session:
  - "`bridge/INDEX.md` must not exist."
  - "We do not want backward compatibility."
  - "We want to rip out all traces of the old bridge implementation and retain
    nothing except historical artifacts for audit purposes."
  - "Remember: every mutating task requires the bridge protocol."
  - "Once you have exhausted your search, update your implementation proposal
    or create additional proposals and add them to an umbrella backlog project."

## Owner Decisions / Input

No new owner decision is needed for LO review of this revision. The owner has
already selected the no-backward-compatibility path and confirmed the protocol
requirement. If LO concludes that a temporary headless Codex-as-LO fallback is
needed, that should be surfaced as a separate implementation/reconfiguration
proposal before changing harness routing.

## Requirement Sufficiency

Requirements are sufficient for a reviewed cleanup program, but the existing
formal and project artifacts are contradictory. This proposal therefore includes
formal-artifact and project/backlog correction as first-class work, not as
incidental documentation cleanup.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Sweep old bridge text without preserving credentials, environment values, or cloud secrets. | Credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Mutate only in-root GT-KB files listed in target paths. | Root-boundary review and `git diff --name-only`. | |
| CQ-COMPLEXITY-001 | Yes | Retire index-specific paths instead of hiding them behind compatibility wrappers. | Source review and old-symbol search. | |
| CQ-CONSTANTS-001 | Yes | Replace bridge-index constants with dispatcher/TAFE authority names where runtime constants remain. | Ruff and targeted tests. | |
| CQ-SECURITY-001 | Yes | Dispatcher health must not imply cloud/deployment mutation authority; cloud and production changes remain oversight-gated. | Prompt/rule review and health tests. | |
| CQ-DOCS-001 | Yes | Active docs, skills, and startup prompts must say no compatibility bridge and document dispatcher CLI/skill use. | Repository search with historical exceptions only. | |
| CQ-TESTS-001 | Yes | Tests must prove no `bridge/INDEX.md` recreation and healthy dispatcher/TAFE routing without it. | Targeted pytest groups below. | |
| CQ-LOGGING-001 | Yes | Health/status must expose recent launches, exits, output, stale state, circuit breakers, and queue ingestion failures. | Dispatch-health JSON assertions and diagnose outputs. | |
| CQ-VERIFICATION-001 | Yes | Treat any break caused by the missing index as a defect until classified historical. | Search, tests, and CLI health commands. | |

## Inventory Evidence

Read-only search command family:

```text
rg -l "bridge/INDEX[.]md|INDEX\\.md|BridgeIndex|bridge index|INDEX entry|INDEX update|INDEX insertion|ERR_NO_INDEX_ENTRY|BRIDGE_INDEX|compatibility view|compatibility output" ...
```

With `bridge/**`, `archive/**`, `memory/**`, harness session archives, and drift
backups excluded, the active/non-archive hit set is:

| Category | Files |
|---|---:|
| instructions/docs/skills | 63 |
| config/governance | 14 |
| runtime source/scripts/hooks | 105 |
| tests/fixtures | 151 |
| current generated/state surfaces | 5 |
| total active/non-archive files | 390 |
| total active/non-archive matching lines | 1,848 |

Representative P0/P1 hits:

- `scripts/bridge_applicability_preflight.py` still fails `ERR_NO_INDEX_ENTRY`.
- `config/governance/adr-dcl-clauses.toml` still declares
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.
- `scripts/session_self_initialization.py` still tells agents to read live
  `bridge/INDEX.md`.
- `scripts/cross_harness_bridge_trigger.py --help` still says it reads live
  `bridge/INDEX.md`.
- `scripts/single_harness_bridge_dispatcher.py --help` still says it reads
  `bridge/INDEX.md`.
- `.claude/skills/bridge-propose/helpers/write_bridge.py` still writes
  `bridge/INDEX.md`.
- `.claude/skills/bridge/helpers/scan_bridge.py`, `revise_bridge.py`,
  `impl_report_bridge.py`, and `show_thread_bridge.py` still parse or require
  the index.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py`,
  `bridge/index_mutation.py`, `bridge/status_driver.py`, `bridge/detector.py`,
  `tafe_index_generator.py`, and `tafe_index_preview.py` retain index-specific
  behavior or text.
- `config/agent-control/system-interface-map.toml`,
  `SESSION-STARTUP-INDEX.md`, and `LOYAL-OPPOSITION-STARTUP-OVERLAY.md` still
  contain active index authority language.
- Active skills including `bridge-config`, `gtkb-bridge`, `gtkb-propose`,
  `bridge-propose`, `verify`, and `kb-session-wrap` still refer to a deprecated
  generated compatibility view.

## LO Review Reliability Evidence

The current configured LO dispatch targets are not yet reliable enough to trust
blindly:

- OpenRouter headless review attempt timed out after more than four minutes and
  left no verdict file.
- Ollama headless review attempt exited with
  `ollama_harness: max-turn exhaustion before final assistant text` and left no
  verdict file.
- Antigravity/Gemini can launch and write bridge files without recreating
  `bridge/INDEX.md`, but its first verdict (`002`) was shallow and its corrected
  verdict (`003`) contains useful adverse findings while also mislabeling the
  author identity as Codex and using the wrong bridge-id suffix in some
  preflight evidence.

This revision therefore treats `003` as useful review evidence but not as a
fully trustworthy final LO standard. A follow-on proposal must harden Ollama
and/or Antigravity LO review output quality before GT-KB relies on cheap LO
review as the only gate.

## Dispatcher And Harness Command Surface To Document

The corrected bridge-config skill and startup/rule artifacts must document at
least these live surfaces:

```powershell
gt bridge dispatch config
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Use these for dispatcher topology, rule eligibility, target selection, and
health. Health must include runtime work-delivery evidence, not only eligible
target existence.

```powershell
gt harness list
gt harness roles
gt harness register --id <ID> --name <name> --type <type> --invocation-surfaces <json> --reason <reason>
gt harness activate <ID> --reason <reason>
gt harness suspend <ID> --reason <reason>
gt harness resume <ID> --reason <reason>
gt harness retire <ID> --reason <reason>
gt harness set-role <ID> --role <prime-builder|loyal-opposition> --reason <reason>
gt harness set-precedence <ID> <number> --reason <reason>
```

Use these for harness registration, lifecycle, role assignment, and reviewer
precedence. Dispatchability still comes from dispatcher config/projection and
must remain independent from role assignment.

```powershell
python scripts/cross_harness_bridge_trigger.py --diagnose
python scripts/cross_harness_bridge_trigger.py --reset-recipient <recipient>
python scripts/cross_harness_bridge_trigger.py --dry-run --verbose
python scripts/single_harness_bridge_automation.py --ensure --dry-run --verbose
python scripts/single_harness_bridge_automation.py --dispatch-now --dry-run --verbose
python scripts/single_harness_bridge_dispatcher.py --diagnose
```

Use these for trigger/dispatcher diagnosis, reset, scheduled-task activation
checks, and one-shot dispatch tests. Their help text and implementations must
be corrected so they do not claim or require `bridge/INDEX.md`.

```powershell
python scripts/ollama_harness.py --skill bridge-review -p <prompt>
python scripts/openrouter_harness.py --skill bridge-review -p <prompt>
python scripts/verify_antigravity_dispatch.py --recipient C --prompt-fixture <file> --json
gemini -m gemini-2.5-flash --skip-trust --approval-mode=yolo -p <prompt>
```

Use these only as LO/dispatch verification surfaces until the dispatcher CLI
exposes first-class launch/output/quality evidence.

## Revised Implementation Plan

1. **Bootstrap no-index governance gates.** Update applicability preflight,
   clause preflight, bridge compliance gates, implementation authorization, and
   bridge proposal/revision/report helpers so a versioned bridge file can be
   discovered and reviewed without any index entry. Update
   `GOV-FILE-BRIDGE-AUTHORITY-001` and `adr-dcl-clauses.toml` so the
   INDEX-canonical clause is removed, retired, or replaced.

2. **Make dispatcher/TAFE queue state complete.** Ensure new versioned bridge
   files become pending flow/stage work without `bridge/INDEX.md`. `gt bridge
   dispatch status|health` must report queue/actionability, selected targets,
   last launch, exit code, output presence, stale dispatch state, circuit
   breakers, and unclaimed stages.

3. **Harden LO review delivery.** Fix Ollama max-turn exhaustion, OpenRouter
   timeout/no-output behavior, and Antigravity verdict metadata/evidence
   quality. If those cannot be made trustworthy quickly, add a reviewed
   temporary topology allowing headless Codex to act as Loyal Opposition only
   for this cleanup proposal.

4. **Rewrite active agent guidance.** Update `AGENTS.md`, `CLAUDE.md`,
   startup overlays, startup payload source, rules, skills, system maps, and
   dashboards to state that `bridge/INDEX.md` must not exist and that dispatcher
   CLI/skills are the access/configuration surfaces.

5. **Remove runtime INDEX paths.** Retire or replace index parsers, writers,
   serializers, repair scripts, CLI groups, MCP surfaces, doctor checks, TAFE
   preview/generator references, and bridge helper paths whose sole purpose is
   reading or writing `bridge/INDEX.md`.

6. **Update templates and fixtures.** Stop scaffolding `bridge/INDEX.md`, update
   golden fixtures, and keep old-format fixtures only when explicitly labeled
   historical import/audit inputs.

7. **Retire obsolete backlog work.** Retire or supersede `WI-4508`, reframe or
   retire `WI-4577`, and replace TAFE Phase 6 "Compatibility View" with a
   no-compatibility cleanup/cutover phase.

8. **Historical classification.** Preserve prior versioned `bridge/*.md` audit
   files, but ensure active surfaces cannot mistake historical bridge files for
   current queue state.

## Spec-Derived Verification Plan

```text
Test-Path bridge/INDEX.md
```

Expected: `False`.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-retirement-cleanout
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-retirement-cleanout
```

Expected: pass without `bridge/INDEX.md` and resolve the latest versioned
bridge file from TAFE/dispatcher state or direct versioned-file discovery.

```text
python -m groundtruth_kb bridge dispatch config --json
python -m groundtruth_kb bridge dispatch status --json
python -m groundtruth_kb bridge dispatch health --json
```

Expected: report topology, queue completeness, selected targets, launch/output
evidence, stale state, and reset guidance without reading or recreating
`bridge/INDEX.md`.

```text
python scripts/cross_harness_bridge_trigger.py --diagnose
python scripts/single_harness_bridge_dispatcher.py --diagnose
```

Expected: help text and diagnose output contain no claim that the dispatcher
reads `bridge/INDEX.md`; diagnose distinguishes topology health from actual
work-delivery health.

```text
python scripts/ollama_harness.py --skill bridge-review -p "<bounded review prompt>"
gemini -m gemini-2.5-flash --skip-trust --approval-mode=yolo -p "<bounded review prompt>"
```

Expected: at least one configured LO harness produces a valid, metadata-correct,
evidence-bearing verdict without `bridge/INDEX.md`.

```text
rg -n "bridge/INDEX[.]md|INDEX\\.md|BridgeIndex|bridge index|INDEX entry|INDEX update|INDEX insertion|ERR_NO_INDEX_ENTRY|BRIDGE_INDEX|compatibility view|compatibility output" AGENTS.md CLAUDE.md .agent .api-harness .claude .codex config docs groundtruth-kb applications scripts platform_tests harness-state --glob "!archive/**" --glob "!memory/**" --glob "!harness-state/**/session-envelope-archive/**" --glob "!bridge/**" --glob "!**/__pycache__/**"
```

Expected: no active references except explicitly historical/audit-labeled
fixtures or migration tests.

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_startup_index.py platform_tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_cli_bridge_index.py groundtruth-kb/tests/test_bridge_status_driver.py -q --tb=short
python -m ruff check groundtruth-kb/src scripts platform_tests
python -m ruff format --check groundtruth-kb/src scripts platform_tests
```

Expected: all updated tests pass; tests that retain old index expectations are
either removed, reframed as historical import tests, or fail the cleanup.

## Risks / Rollback

The largest risk is that the old bridge index is still embedded in mandatory
governance gates. This revision makes that the first implementation slice, so
the cleanup does not strand future bridge proposals.

The second risk is weak automated LO review. Current evidence is not sufficient
to trust Ollama/OpenRouter/Antigravity blindly. This is why LO review hardening
is part of the revised plan.

Rollback must not recreate `bridge/INDEX.md`. If a slice fails, revert the
specific source/config/doc/test changes or pause dispatch; do not restore the
retired index file or compatibility generator.
