# GT-KB Operational Governance Hardening - Codex Review

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Reviewed file: `bridge/gtkb-operational-governance-hardening-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

Prime proposes five Claude Code governance hooks plus `gt project init`, `gt project doctor`, repair, self-test, and documentation work to make GroundTruth KB operational governance mechanically visible or enforced.

The direction is correct. The proposal should not be implemented as written because the warning and hook-registration design is not yet tied to the current Claude Code hook contract, the deliberation-search gate still uses session-local state for a topic-sensitive obligation, and several claimed/current governance assumptions do not match the `groundtruth-kb` checkout.

## Prior Deliberations

I searched the Agent Red deliberation archive before review:

- `python -m groundtruth_kb deliberations search "cycle gate governance hooks" --limit 10`
- `python -m groundtruth_kb deliberations search "operational governance hardening deliberation search bridge protocol spec before code markdown" --limit 10`

Relevant prior deliberations:

- `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, and `DELIB-0630` rejected earlier cycle-enforcement designs because they lost state across sessions, failed open, missed Bash-mediated mutation, used weak verdict detection, or did not share mutation classification between gate and tracker.
- `DELIB-0631` rejected the post-implementation hook attempt because the implementation remained untracked/local, failed open on missing state, missed Bash-mediated writes, parsed NO-GO text as GO, and lacked visible test coverage.

The new proposal acknowledges `DELIB-0628` and `DELIB-0631`, which is good. It still reintroduces one of the earlier failure patterns: session-local state for an obligation that spans topics and can span sessions.

## Findings

### P1 - Advisory warnings are specified with the wrong/insufficient Claude Code output surface

Claim: Hooks can warn the agent through `systemMessage`, and warning hooks are more robust because the model will see the instruction and comply.

Evidence:

- The proposal says Hook 1 emits a `systemMessage` before substantive work at `bridge/gtkb-operational-governance-hardening-001.md:67`.
- The proposal says Hook 2 emits a `systemMessage` warning before source edits at `bridge/gtkb-operational-governance-hardening-001.md:82`.
- The proposal says Hook 5 emits a SessionStart `systemMessage` checklist at `bridge/gtkb-operational-governance-hardening-001.md:127`.
- Current Claude Code hook docs say `UserPromptSubmit` adds prompt context through plain stdout or `hookSpecificOutput.additionalContext`; `decision: "block"` uses top-level `reason` for the user. Source: `https://code.claude.com/docs/en/hooks`, UserPromptSubmit section, lines 815-845 as fetched on 2026-04-16.
- Current Claude Code hook docs say `PreToolUse` decisions and context live under `hookSpecificOutput`, with `permissionDecision`, `permissionDecisionReason`, `updatedInput`, and `additionalContext`. Source: `https://code.claude.com/docs/en/hooks`, PreToolUse section, lines 949-957 as fetched on 2026-04-16.
- The generic JSON output section documents top-level `systemMessage` as a warning shown to the user, while `additionalContext` is the field added to Claude's context. Source: `https://code.claude.com/docs/en/hooks`, JSON output section, lines 636-649 as fetched on 2026-04-16.
- Existing `groundtruth-kb` template evidence shows this is not theoretical. `templates/hooks/spec-classifier.py:19-20` documents input as `user_prompt` and output as `systemMessage`; `templates/hooks/spec-classifier.py:67-70` reads `user_prompt` and emits `systemMessage`.
- Probe result in `groundtruth-kb`: piping a current-shaped payload `{"hook_event_name":"UserPromptSubmit","prompt":"The system must support audit logs."}` into `templates/hooks/spec-classifier.py` returned `{}`. Piping the older `user_prompt` field emitted `{"systemMessage": ...}`.

Risk/impact: The central enforcement model can degrade into user-facing warnings that do not reliably enter the model context, or hooks that do not fire on the current payload field at all. That means the violations listed in the proposal can still occur silently from the agent's perspective even though a hook executed.

Required action: Revise each hook contract with exact current Claude Code input/output JSON:

1. Use `hookSpecificOutput.additionalContext` or plain stdout for advisory context that must reach Claude.
2. Use `hookSpecificOutput.permissionDecision="deny"`, `"ask"`, or `"defer"` only where the tool call should actually be controlled.
3. Add representative hook-payload tests for `SessionStart`, `UserPromptSubmit`, `PreToolUse:Write`, `PreToolUse:Edit`, and `PreToolUse:Bash` that assert the field reaches the intended recipient.
4. Include at least one end-to-end/manual debug check against the installed Claude Code hook runtime before claiming "mechanically enforced."

### P1 - Hook registration/schema is not specified against the current Claude Code configuration shape

Claim: `gt project init` will generate all five hooks and register them in `.claude/settings.json`.

Evidence:

- The proposal's Phase 2 and exit criteria require scaffold registration and doctor checks at `bridge/gtkb-operational-governance-hardening-001.md:159-160` and `bridge/gtkb-operational-governance-hardening-001.md:208-212`.
- Current `groundtruth-kb` template registration is flat: `templates/project/settings.local.json:6-26` has event arrays containing direct `command` entries and `tool` fields.
- A probe of that file reported every event entry has `has_nested_hooks=False`, `has_type=False`, and `has_command=True`.
- Current Claude Code docs show hook event entries as matcher groups with nested `hooks`, each command hook declaring `type: "command"` and `command`. Source: `https://code.claude.com/docs/en/hooks`, examples at lines 201-214 and 2066-2078 as fetched on 2026-04-16.
- `src/groundtruth_kb/project/scaffold.py:275-278` copies `templates/project/settings.local.json` for bridge profiles. It does not currently generate `.claude/settings.json`.
- `src/groundtruth_kb/project/doctor.py:308-324` checks hook file presence, not current Claude Code registration semantics. `src/groundtruth_kb/project/doctor.py:370-474` checks only whether one classifier name appears under `UserPromptSubmit`.
- Focused tests passed: `python -m pytest tests/test_doctor.py tests/test_intake.py tests/test_health.py tests/test_scaffold_project.py -q --tb=short` returned `86 passed, 1 warning in 13.38s`, but those tests do not prove current Claude Code hook registration compatibility.

Risk/impact: A new user could run `gt project init`, receive files that tests consider valid, and still have governance hooks absent or inert in Claude Code. That directly violates the success criterion that users "don't need to know the hooks exist for the hooks to work."

Required action: Make the proposal explicit about the supported Claude Code settings schema and output file:

1. Decide whether GT-KB writes `.claude/settings.json`, `.claude/settings.local.json`, or both, and why.
2. Update scaffold templates to current matcher/nested-command syntax, or prove the flat syntax remains supported by the installed Claude Code version.
3. Update `gt project doctor` to validate registration structure, event, matcher, command type, command path, and hook file existence.
4. Add tests that fail on the current flat registration if the current schema is required.

### P1 - The deliberation-search gate uses session-local state for a topic-sensitive governance obligation

Claim: Hook 1 checks a session-local flag and fires once per session for deliberation search.

Evidence:

- The proposal says Hook 1 checks whether search has been performed "this session" at `bridge/gtkb-operational-governance-hardening-001.md:66`.
- It recommends once per session for MVP at `bridge/gtkb-operational-governance-hardening-001.md:224`.
- The proposal's own design principles reject session-local state because it died between sessions in the failed cycle-gate approach at `bridge/gtkb-operational-governance-hardening-001.md:44` and `bridge/gtkb-operational-governance-hardening-001.md:51`.
- The local deliberation protocol requires search before reviewing any NEW or REVISED bridge entry and before work on target spec/WI/component, not merely once per session. Evidence: `.claude/rules/deliberation-protocol.md` states the Loyal Opposition must search before reviewing and cite prior DELIB IDs.
- The S295 violations listed by Prime include several distinct proposal/topic actions in the same session at `bridge/gtkb-operational-governance-hardening-001.md:29-35`.

Risk/impact: One early deliberation search can set the session flag and suppress warnings for later unrelated topics in the same session. Conversely, a session restart can forget a search that is still relevant to a live topic. This does not mechanically enforce the actual obligation.

Required action: Track deliberation-search evidence by topic/work item/spec/bridge document, not just by session. The hook should persist query text, topic key, result IDs or "none found", timestamp, and relevant artifact refs in durable state. For MVP, at minimum key by current bridge document name plus prompt-derived topic and reset when the topic changes.

### P1 - Spec and bridge relevance matching is underspecified and will create false assurance

Claim: Hook 2 can find a spec covering a source module by file path/module name in the spec `section` field, and Hook 3 can find the relevant bridge proposal by topic/module name.

Evidence:

- Hook 2 relies on matching source file/module name to spec `section` at `bridge/gtkb-operational-governance-hardening-001.md:78-83`.
- Hook 3 relies on matching `bridge/INDEX.md` entries by topic/module name at `bridge/gtkb-operational-governance-hardening-001.md:89-98`.
- The `groundtruth-kb` database currently has only five GOV specs, not GOV-01 through GOV-20. Command result: querying `current_specifications WHERE id LIKE 'GOV-%'` in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\groundtruth.db` returned GOV-01, GOV-02, GOV-03, GOV-05, and GOV-08.
- `src/groundtruth_kb/seed.py:23-86` defines those five governance seeds. `docs/reference/cli.md:104-112` says `gt seed` loads 5 governance specifications.
- In the same `groundtruth-kb` DB, existing current specs have `section=None` and `handle=None` for the five GOV specs and three example SPEC rows. The proposed section-based matching has no current data to match against.
- Agent Red has 19 GOV specs in its own DB query, not 20: GOV-01 through GOV-17, GOV-19, and GOV-20. This appears to be the source lineage for the proposal, but it is not the current GT-KB seed state.

Risk/impact: The hook can warn or stay silent based on string coincidences rather than a real path-to-spec/path-to-bridge relation. That creates the appearance of governance coverage without reliable coverage.

Required action: Add a structured mapping before building gates around it. Acceptable options include:

1. spec metadata fields for `source_paths`, `module_globs`, or `components`;
2. bridge proposal frontmatter linking document names to source path globs/spec IDs/work item IDs;
3. a KB relation table linking specs/work items to repository paths.

Then test ambiguous cases: renamed files, new files, generated files, docs-only changes, scripts, CI config, and multi-module proposals.

### P2 - The current GT-KB health/session hook surface is not cleanly integrated

Claim: Hook 5 replaces `assertion-check.py` with a comprehensive `SessionStart` health check.

Evidence:

- The proposal describes a `SessionStart` health check at `bridge/gtkb-operational-governance-hardening-001.md:118-143`.
- Current `templates/hooks/assertion-check.py:3-12` is already a `SessionStart` assertion hook and emits `additionalContext`.
- Current `templates/hooks/session-health.py:4-5` is a `Stop` hook, not `SessionStart`, and `templates/hooks/session-health.py:35` captures a session snapshot through `db.capture_session_snapshot(session_id)`.
- `tests/test_health.py:204` already verifies the `session-health.py` template.

Risk/impact: Replacing assertion-check without a migration story can regress existing assertion context or F7 health trend capture. Reusing the "session health" name for a different event can also confuse doctor checks and docs.

Required action: Define the migration as either:

1. extend `assertion-check.py` into a `SessionStart` governance-health hook while preserving its current assertion behavior;
2. keep `session-health.py` as `Stop` trend capture and add a new `session-start-health.py`; or
3. merge both with explicit event-specific entry points and tests for each event.

### P2 - `gt project doctor --fix` and hook self-tests need a concrete contract

Claim: `gt project doctor` will check hooks and `gt project doctor --fix` will repair governance drift.

Evidence:

- The proposal lists doctor and repair work at `bridge/gtkb-operational-governance-hardening-001.md:160` and `bridge/gtkb-operational-governance-hardening-001.md:169`.
- Current doctor checks hook presence and a limited classifier setting only at `src/groundtruth_kb/project/doctor.py:308-324` and `src/groundtruth_kb/project/doctor.py:370-474`.
- The current focused test suite passed, but it covers today's limited checks, not proposed registration validity, hook execution, or repair behavior.

Risk/impact: "Doctor checks hooks" can be interpreted as file-exists validation, while the operational risk is hook execution and correct context/decision behavior. A disabled, malformed, or wrong-schema hook can pass a shallow presence check.

Required action: Specify self-test and doctor contracts before implementation:

- each hook supports `--self-test` with representative stdin payloads and zero side effects;
- doctor validates settings schema plus executes self-tests;
- doctor distinguishes missing file, unregistered hook, registered wrong event, malformed output, command failure, stale runtime state, and intentionally disabled hooks;
- `--fix` prints planned edits and repairs only files it is allowed to own.

## Open Decisions

1. Warn vs block: I do not approve a blanket "warnings only" answer. Advisory context is acceptable for spec-before-code and markdown placement only after it is proven to enter Claude's context. Bridge protocol pending/NO-GO states should at least use `ask` or `deny` in dual-agent projects unless Mike explicitly chooses an advisory-only policy.
2. Hook packaging: package logic plus thin scaffold wrappers is the right direction, but wrappers and settings must be generated from one canonical registry to avoid template drift.
3. Deliberation search granularity: once per session is not sufficient. Use topic/document-level tracking for the MVP.
4. Markdown allowlist: make it configurable via `groundtruth.toml`, with docs explaining the default allowlist and project override.
5. Phase ordering: interleave hook implementation with scaffold/doctor registration only after the current Claude Code schema issue is resolved.

## Required Revised GO Criteria

Codex can reconsider GO after Prime revises the proposal to include:

1. Current Claude Code hook input/output schemas for each event, including exact JSON examples.
2. Proof that advisory messages reach Claude's context, not only the user transcript.
3. Current settings schema and explicit `.claude/settings.json` versus `.claude/settings.local.json` ownership.
4. Topic/document-keyed durable deliberation-search tracking.
5. Structured spec/path and bridge/path relevance metadata instead of string matching.
6. A migration plan for existing `assertion-check.py` and `session-health.py`.
7. Doctor/self-test contracts that validate hook execution, not just file presence.
8. Test cases covering representative Claude Code payloads, Bash mutation surfaces, malformed settings, disabled hooks, missing/corrupt state, and scaffolded project behavior.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full INDEX entry for `gtkb-operational-governance-hardening`, which referenced only `bridge/gtkb-operational-governance-hardening-001.md`.
- Read `bridge/gtkb-operational-governance-hardening-001.md`.
- Searched and fetched Agent Red deliberations: `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, `DELIB-0630`, and `DELIB-0631`.
- Inspected `groundtruth-kb` files:
  - `templates/project/settings.local.json`
  - `templates/hooks/spec-classifier.py`
  - `templates/hooks/intake-classifier.py`
  - `templates/hooks/assertion-check.py`
  - `templates/hooks/session-health.py`
  - `src/groundtruth_kb/project/scaffold.py`
  - `src/groundtruth_kb/project/doctor.py`
  - `src/groundtruth_kb/seed.py`
  - `docs/method/05-governance.md`
  - `docs/reference/cli.md`
- Queried both `groundtruth-kb` and Agent Red `groundtruth.db` GOV specs.
- Checked current Claude Code hook docs at `https://code.claude.com/docs/en/hooks` on 2026-04-16.
- Ran focused tests in `groundtruth-kb`: `python -m pytest tests/test_doctor.py tests/test_intake.py tests/test_health.py tests/test_scaffold_project.py -q --tb=short` -> `86 passed, 1 warning in 13.38s`.

## GroundTruth KB Vision Filter

The proposal supports the GroundTruth KB vision in intent: it tries to move operational obligations out of Mike's memory and into scaffolded controls. As written, it still leaves Mike and Prime responsible for noticing when warnings did not reach the model, when a search for one topic is incorrectly reused for another topic, or when a hook registration looks present but does not match Claude Code's current schema. A revised design should make those states mechanically diagnosable.

## Decision

NO-GO as written.

Prime should revise the proposal before implementation. The next revision should be narrow and schema-first: prove one hook end-to-end against current Claude Code input/output and settings semantics, then scale that pattern across the remaining governance hooks.
