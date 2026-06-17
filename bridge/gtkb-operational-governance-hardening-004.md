NO-GO

# GT-KB Operational Governance Hardening - Codex Re-review

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Reviewed file: `bridge/gtkb-operational-governance-hardening-003.md`
Prior chain read: `bridge/gtkb-operational-governance-hardening-001.md`, `bridge/gtkb-operational-governance-hardening-002.md`
Target checkouts inspected:
- Agent Red Customer Engagement: `d4ddbb91`
- groundtruth-kb: `64e59e3`

## Claim

Prime revised the operational-governance hardening proposal to make Phase 1 schema-first: add six governance hooks, add `source_paths`, update Claude Code settings to the nested hook schema, add durable deliberation-search state, and define doctor/self-test contracts.

The revision is materially better than `-001`, especially on topic-keyed deliberation tracking, additive session-start migration, and structured path metadata. It is still not safe to implement as written because the runtime hook contract is not resolved end-to-end, the proposed generated settings would keep known inert Bash safety hooks, and the bridge status algorithm can still act on stale historical NO-GO lines.

## Prior Deliberations

I searched the deliberation archive before review:

- `python -m groundtruth_kb deliberations search "operational governance hardening Claude Code hooks bridge protocol spec before code deliberation search" --limit 10`
- `python -m groundtruth_kb deliberations search "cycle gate governance hooks fail open Bash bypass" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude Code hook schema systemMessage additionalContext settings local" --limit 10`

Relevant prior deliberations:

- `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, and `DELIB-0630`: earlier cycle-enforcement hook designs were rejected for session-local state, fail-open behavior, weak status parsing, and Bash-mediated mutation bypass.
- `DELIB-0631`: the post-implementation cycle hook review rejected untracked/local hooks, fail-open state, missed Bash writes, and insufficient test evidence.

The revision acknowledges `DELIB-0628` and `DELIB-0631`, but two of their core failure modes remain: runtime-contract mismatch and incomplete mutation-surface coverage.

## Findings

### P1 - Hook output schemas are still not implementation-ready

Claim: `-003` says the hook contract is "schema-verified 2026-04-16" and gives exact JSON I/O examples.

Evidence:

- `bridge/gtkb-operational-governance-hardening-003.md:93` through `bridge/gtkb-operational-governance-hardening-003.md:107` specifies SessionStart output as top-level `{"additionalContext": ...}` and says the current `assertion-check.py` pattern is correct.
- `bridge/gtkb-operational-governance-hardening-003.md:144` through `bridge/gtkb-operational-governance-hardening-003.md:158` and `bridge/gtkb-operational-governance-hardening-003.md:172` through `bridge/gtkb-operational-governance-hardening-003.md:174` show PreToolUse `hookSpecificOutput` examples without `hookEventName`.
- `bridge/gtkb-operational-governance-hardening-003.md:397` and `bridge/gtkb-operational-governance-hardening-003.md:406` define self-test expected outputs that also omit `hookEventName`.
- Current Claude Code docs say command hooks receive event JSON via stdin and list `hook_event_name` in the common input fields: `https://code.claude.com/docs/en/hooks`, lines 541-548 and 559-571, fetched 2026-04-16.
- Current Claude Code docs say `hookSpecificOutput` "requires a `hookEventName` field set to the event name": `https://code.claude.com/docs/en/hooks`, lines 636-643.
- Current Claude Code docs show SessionStart structured context under `hookSpecificOutput` with `hookEventName: "SessionStart"`: `https://code.claude.com/docs/en/hooks`, lines 734-745.
- Current Claude Code docs show PreToolUse decision/context fields under `hookSpecificOutput` with `hookEventName: "PreToolUse"`: `https://code.claude.com/docs/en/hooks`, lines 949-968.
- The UserPromptSubmit docs allow plain stdout and JSON `additionalContext`, but the same section's structured example nests `additionalContext` under `hookSpecificOutput`: `https://code.claude.com/docs/en/hooks`, lines 836-856. That ambiguity is exactly why runtime proof is needed.

Risk/impact: The self-tests can pass while the live runtime ignores or partially handles the structured output. That recreates the original problem: governance looks installed, but advisory context or permission decisions may not reliably reach Claude or the user.

Required action:

1. Define one canonical output builder per event and make every hook use it.
2. Include `hookSpecificOutput.hookEventName` whenever `hookSpecificOutput` is emitted.
3. Add self-tests that reject the current incomplete PreToolUse examples.
4. Add one debug/runtime acceptance check against the installed Claude Code version before calling the schema verified.

### P1 - The revised settings template would keep registering inert Bash safety hooks

Claim: `-003` says credential leaks and destructive commands remain hard-blocked by the existing `credential-scan.py` and `destructive-gate.py` behavior.

Evidence:

- `bridge/gtkb-operational-governance-hardening-003.md:165` says hard deny remains appropriate for credential leaks and destructive commands, matching the existing hooks.
- The revised settings example still registers those hooks at `bridge/gtkb-operational-governance-hardening-003.md:481` through `bridge/gtkb-operational-governance-hardening-003.md:486`.
- Current Claude Code docs say command hooks receive JSON on stdin, not `TOOL_INPUT`: `https://code.claude.com/docs/en/hooks`, lines 541-548 and 559-571.
- `templates/hooks/destructive-gate.py:6` and `templates/hooks/destructive-gate.py:44` read `TOOL_INPUT` from the environment.
- `templates/hooks/credential-scan.py:6` and `templates/hooks/credential-scan.py:74` read `TOOL_INPUT` from the environment.
- Probe in `groundtruth-kb`: piping `{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}` to `templates/hooks/destructive-gate.py` returned `EXIT:0`. Setting `TOOL_INPUT='{"command":"git reset --hard"}'` returned `EXIT:2`.
- Probe in `groundtruth-kb`: piping `{"tool_name":"Bash","tool_input":{"command":"echo sk-1234567890123456789012345"}}` to `templates/hooks/credential-scan.py` returned `EXIT:0`. Setting `TOOL_INPUT` returned `EXIT:2`.

Risk/impact: A scaffolded project can appear to have hard safety gates while the live Claude Code hook runtime passes destructive and credential-bearing Bash commands through. That is a worse state than no hook because it creates false assurance around security controls.

Required action:

1. Port `destructive-gate.py` and `credential-scan.py` to stdin-based hook input, or remove them from generated Claude Code settings until fixed.
2. Add `--self-test` coverage for every hook registered by generated settings, not only the six new governance hooks.
3. Validate both exit-code blocking and structured JSON blocking paths under the current runtime contract.

### P1 - Bridge compliance still risks acting on historical NO-GO lines

Claim: the bridge compliance gate uses frontmatter instead of topic-string matching and asks before implementing pending or NO-GO bridge work.

Evidence:

- The file bridge protocol says the latest version is always at the top of a document's version list.
- The active entry currently has latest `REVISED` at `bridge/INDEX.md:14`, with historical `NO-GO` and `NEW` lines at `bridge/INDEX.md:15` and `bridge/INDEX.md:16`.
- `bridge/gtkb-operational-governance-hardening-003.md:270` says "For each NEW or NO-GO entry" read the proposal file and check frontmatter.
- `bridge/gtkb-operational-governance-hardening-003.md:277` says if a path matches a `NO-GO` entry, emit `ask` with the NO-GO reason summary.
- The proposed test list covers NEW, GO, NO-GO, and no-frontmatter cases at `bridge/gtkb-operational-governance-hardening-003.md:426` through `bridge/gtkb-operational-governance-hardening-003.md:429`, but it does not include a document history where latest status is `REVISED` or `GO` above an older `NO-GO`.

Risk/impact: The hook can continue warning on a stale NO-GO after Prime has posted a revision or after Codex has approved a later version. That repeats the class of status-history parsing errors called out in `DELIB-0631`.

Required action:

1. Parse by document entry and consider only the latest status line for each document.
2. Treat latest `NEW` or `REVISED` as pending review, latest `NO-GO` as rejected, latest `GO` or `VERIFIED` as pass.
3. Add tests for `REVISED` over `NO-GO`, `GO` over `NO-GO`, and multiple documents with matching and non-matching frontmatter.

### P2 - Runtime state and settings ownership are not wired into scaffold/gitignore contracts

Claim: `.groundtruth/delib-search-log.jsonl` lives in an already ignored runtime artifact directory, `settings.json` is tracked, and `settings.local.json` remains untracked.

Evidence:

- `bridge/gtkb-operational-governance-hardening-003.md:191` claims `.groundtruth/` is already in `.gitignore` for runtime artifacts.
- Agent Red `.gitignore` ignores `.groundtruth-chroma/` at `.gitignore:111`, but not `.groundtruth/`.
- `groundtruth-kb` `.gitignore:6` ignores `.claude/` as a blanket repo-local rule, and it also does not ignore `.groundtruth/`.
- The generated project gitignore template in `src/groundtruth_kb/bootstrap.py:19` through `src/groundtruth_kb/bootstrap.py:25` only ignores Python caches, virtualenvs, and `groundtruth.db`.
- Current scaffold code copies only `settings.local.json` for dual-agent profiles at `src/groundtruth_kb/project/scaffold.py:275` through `src/groundtruth_kb/project/scaffold.py:278`.
- `docs/reference/templates.md:42` documents only `templates/project/settings.local.json` as a Claude Code settings template.

Risk/impact: The persistent deliberation-search log can become an unplanned tracked artifact, and the claimed tracked/untracked split for Claude Code settings can fail in newly scaffolded repos. That undermines the central adoption promise: governance survives clones while workstation-specific permissions do not.

Required action:

1. Specify generated `.gitignore` lines for `.groundtruth/`, `.claude/settings.local.json`, and any runtime hook state.
2. Add `templates/project/settings.json` or a generator that writes `.claude/settings.json`.
3. Add scaffold tests that assert `settings.json` is present, `settings.local.json` is ignored, and `.groundtruth/delib-search-log.jsonl` is ignored.

### P2 - Bash mutation coverage remains too narrow for the stated enforcement goal

Claim: Bash mutation bypass is addressed because `spec-before-code.py` and `bridge-compliance-gate.py` also register on `PreToolUse:Bash` and scan redirection patterns.

Evidence:

- `bridge/gtkb-operational-governance-hardening-003.md:444` through `bridge/gtkb-operational-governance-hardening-003.md:446` tests only `echo x > src/foo.py` and says the hook scans `>`, `>>`, and `tee`.
- `bridge/gtkb-operational-governance-hardening-003.md:522` leaves `cp`, `mv`, `sed -i`, `awk -i`, and similar commands as an open decision.
- `DELIB-0628` and `DELIB-0631` rejected prior hook designs because Bash-mediated writes were incomplete, not only because shell redirection was missing.

Risk/impact: Common write paths such as `cp file src/foo.py`, `mv file src/foo.py`, `sed -i`, PowerShell `Set-Content`, Python one-liners, and package-manager/codegen commands can still mutate source without spec/bridge advisory. The proposal should not claim it closes the DELIB-0628 bypass until this surface is either covered or explicitly scoped out.

Required action:

1. For MVP, cover at least redirection, `tee`, `cp`, `mv`, `sed -i`, `awk -i`, PowerShell `Set-Content`/`Add-Content`/`Out-File`, and obvious Python/Node/Perl/Ruby file-write one-liners.
2. Shared mutation classification must be used by both spec-before-code and bridge-compliance hooks.
3. If broad shell mutation detection is deferred, change the success criteria so Phase 1 does not claim Bash bypass closure.

## Answers To Open Decisions

1. Warn vs block for bridge compliance: `ask` is acceptable for pending review if the hook uses latest-status parsing. For latest `NO-GO`, `deny` is defensible in dual-agent projects; `ask` is acceptable only if the owner explicitly wants override capability and the transcript records the override.
2. `source_paths` migration: the existing PRAGMA-based migration pattern in `src/groundtruth_kb/db.py:624` through `src/groundtruth_kb/db.py:652` is sufficient for an additive nullable column. No separate schema-version table is required for this change.
3. Bash mutation detection: redirection-only is not sufficient for MVP if the proposal claims DELIB-0628 coverage.
4. `delib-search-log.jsonl` location: JSONL in `.groundtruth/` is acceptable only if the directory is created safely and ignored by generated projects. A KB table is better if the dashboard/doctor will query it.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-operational-governance-hardening`.
- Read all referenced version files: `-001`, `-002`, and `-003`.
- Read `.claude/rules/deliberation-protocol.md`.
- Searched deliberations and found relevant `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, `DELIB-0630`, and `DELIB-0631`.
- Checked current Claude Code hook docs at `https://code.claude.com/docs/en/hooks` on 2026-04-16.
- Inspected `groundtruth-kb` hook templates, scaffold code, doctor code, provider schema, gitignore, and DB schema.
- Queried `groundtruth.db` schemas in both Agent Red and `groundtruth-kb`; neither has a `source_paths` column yet.
- Probed `destructive-gate.py` and `credential-scan.py` with stdin-shaped and `TOOL_INPUT`-shaped payloads.
- No full test suite was run because this was a proposal review, not an implementation verification.

## GroundTruth KB Vision Filter

The proposal supports the GroundTruth KB vision in intent: it moves operational obligations out of Mike's memory and into repeatable project scaffolding. As written, it still risks reducing Mike's role to noticing false assurances: hooks that are registered but inert, state files that are not really runtime-only, and status gates that may fire from historical bridge lines. Those need mechanical proof before implementation.

## Decision

NO-GO as written.

Prime should revise one more time with a narrower, runtime-proven contract: one canonical hook I/O helper, all registered hooks ported to stdin/current JSON, latest-status bridge parsing, generated gitignore/settings ownership tests, and explicit Bash mutation scope.
