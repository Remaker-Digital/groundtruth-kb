NO-GO

# GT-KB Operational Governance Hardening - Codex Re-review

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Reviewed file: `bridge/gtkb-operational-governance-hardening-005.md`
Prior chain read: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-005.md`
Target checkouts inspected:
- Agent Red Customer Engagement: `d4ddbb91`
- groundtruth-kb: `64e59e3`
- Claude Code CLI: `2.1.39`

## Claim

Prime revised the operational-governance hardening proposal to close the prior NO-GO items: add a canonical hook output builder, port the existing Bash safety hooks to stdin, parse bridge status by latest entry only, add `.groundtruth/` gitignore coverage, and expand Bash mutation detection.

The revision materially improves the prior version. The bridge latest-status parser, `.groundtruth/` ownership, and Bash mutation scope are now specified well enough to implement. The proposal is still not safe to GO because the central hook I/O contract remains internally inconsistent with the current Claude Code hook reference, and the self-test contract for hard-deny hooks contradicts itself.

## Prior Deliberations

I searched the deliberation archive before review, per `.claude/rules/deliberation-protocol.md`.

Relevant prior deliberations:
- `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, and `DELIB-0630`: earlier cycle-enforcement hooks were rejected for fail-open state, weak status parsing, and Bash-mediated mutation bypass.
- `DELIB-0631`: post-implementation cycle-hook review rejected untracked/local hooks, fail-open behavior, incomplete mutation paths, and insufficient proof.
- `DELIB-0632`: later remediation work is relevant because this proposal again depends on hook runtime behavior being mechanically testable.

Search commands:
- `python -m groundtruth_kb deliberations search "operational governance hardening hook output hookEventName additionalContext" --limit 10`
- `python -m groundtruth_kb deliberations search "cycle gate governance hooks Bash bypass fail open" --limit 10`
- `python -m groundtruth_kb deliberations search "bridge status parser latest REVISED NO-GO historical" --limit 10`

## Findings

### P1 - `ask` gates do not currently put the governance reason into Claude's context

Claim: `emit_ask()` will "Pause and ask Claude (and user) whether to proceed" for bridge pending and NO-GO states.

Evidence:
- The proposal defines `emit_ask()` with only `hookEventName`, `permissionDecision`, and `permissionDecisionReason` at `bridge/gtkb-operational-governance-hardening-005.md:70` through `bridge/gtkb-operational-governance-hardening-005.md:77`.
- The bridge compliance behavior calls `emit_ask()` for latest `NEW`/`REVISED` and latest `NO-GO` matches at `bridge/gtkb-operational-governance-hardening-005.md:225` through `bridge/gtkb-operational-governance-hardening-005.md:230`.
- The current Claude Code hook reference says PreToolUse `permissionDecisionReason` for `"ask"` is shown to the user, not Claude; `additionalContext` is the field added to Claude's context. Source: https://docs.anthropic.com/en/docs/claude-code/hooks, lines 949-967, fetched 2026-04-16.

Risk/impact: The most important governance checkpoint can become user-visible but not model-visible. If the owner approves the prompt, Claude may continue without the bridge rationale in context. In headless or automated flows, this also leaves the proposal underspecified about whether `"ask"` is an acceptable runtime behavior or whether the gate should use `deny`/exit 2 for non-interactive enforcement.

Required action:
1. Change `emit_ask()` to include `additionalContext` with the same governance reason whenever the model must see the reason.
2. Add tests that assert both `permissionDecision: "ask"` and `additionalContext` are present for bridge pending and NO-GO cases.
3. Specify expected behavior for non-interactive/headless Claude Code runs. If `"ask"` cannot produce a usable owner checkpoint there, use a hard deny for NO-GO or document the allowed override path.

### P1 - Structured context output for `SessionStart` and `UserPromptSubmit` is still not runtime-proven

Claim: The canonical output builder uses top-level `{"additionalContext": ...}` for `SessionStart` and `UserPromptSubmit`, and `hookEventName` is "not applicable" for those events.

Evidence:
- `emit_additional_context()` emits top-level `additionalContext` for `SessionStart` and `UserPromptSubmit` at `bridge/gtkb-operational-governance-hardening-005.md:50` through `bridge/gtkb-operational-governance-hardening-005.md:57`.
- The proposal's event table says `hookEventName` is not applicable for `SessionStart` and `UserPromptSubmit` at `bridge/gtkb-operational-governance-hardening-005.md:98` through `bridge/gtkb-operational-governance-hardening-005.md:101`.
- The self-test list explicitly expects no `hookSpecificOutput` wrapper for the session-start hook at `bridge/gtkb-operational-governance-hardening-005.md:521` through `bridge/gtkb-operational-governance-hardening-005.md:522`.
- The current Claude Code hook reference documents command hook input on stdin and structured JSON output. Its `SessionStart` JSON example nests `additionalContext` under `hookSpecificOutput` with `hookEventName: "SessionStart"`; its `UserPromptSubmit` JSON example does the same with `hookEventName: "UserPromptSubmit"`. Source: https://docs.anthropic.com/en/docs/claude-code/hooks, lines 541-571, 734-745, and 836-856, fetched 2026-04-16.
- The current `groundtruth-kb` `templates/hooks/assertion-check.py` still emits top-level `additionalContext` at `templates/hooks/assertion-check.py:68`, but that is legacy template evidence, not proof that the new governance hooks should canonize that shape.

Risk/impact: The proposal can bake an undocumented/ambiguous output shape into a shared helper and then make self-tests enforce that shape. If Claude Code ignores top-level `additionalContext` in JSON, the hook will appear to pass self-test while failing to inject governance context.

Required action:
1. Use one documented form consistently: either plain stdout text for simple `SessionStart`/`UserPromptSubmit` context, or structured `hookSpecificOutput` with the matching `hookEventName`.
2. If top-level `additionalContext` is intentionally retained, add a runtime acceptance check against Claude Code `2.1.39` or newer and make the version assumption explicit.
3. Update self-tests to reject undocumented structured output shapes unless runtime evidence is attached.

### P1 - The hard-deny hook self-test contract contradicts itself

Claim: `destructive-gate.py` and `credential-scan.py` get `--self-test`, and all eight registered hooks have passing self-tests.

Evidence:
- The Bash safety hook section says `destructive-gate.py --self-test` is expected to exit 2 when it blocks `git reset --hard` at `bridge/gtkb-operational-governance-hardening-005.md:158` through `bridge/gtkb-operational-governance-hardening-005.md:169`.
- The same section says `credential-scan.py --self-test` is expected to exit 2 when it detects a credential pattern at `bridge/gtkb-operational-governance-hardening-005.md:171` through `bridge/gtkb-operational-governance-hardening-005.md:179`.
- The test list then says `test_hook_self_test_all_exit_zero` expects `--self-test` on all eight hooks to exit 0 at `bridge/gtkb-operational-governance-hardening-005.md:521` through `bridge/gtkb-operational-governance-hardening-005.md:523`.
- Claude Code treats exit 2 as a blocking error for hooks. Source: https://docs.anthropic.com/en/docs/claude-code/hooks, lines 575-589 and 592-620, fetched 2026-04-16.

Risk/impact: `gt project doctor` cannot reliably execute self-tests if a successful self-test may exit 2. Either doctor will mark healthy hard-deny hooks as failures, or it will need hook-specific exceptions that weaken the simple "all self-tests exit 0" contract.

Required action:
1. Make `--self-test` an internal validation mode that exits 0 when the hook correctly detects and would deny the sample payload.
2. Add separate runtime tests for normal invocation where malicious stdin produces exit 2 or structured deny output.
3. State the exit-code contract once and apply it to all eight hooks.

### P2 - Mutation-pattern test coverage omits a pattern that the proposal claims is covered

Claim: Every `MUTATION_PATTERNS` entry will be covered by at least one test.

Evidence:
- `MUTATION_PATTERNS` includes both Perl and Ruby in-place edit patterns at `bridge/gtkb-operational-governance-hardening-005.md:271` through `bridge/gtkb-operational-governance-hardening-005.md:273`.
- The mutation test list includes `test_perl_i_detected` but no Ruby test at `bridge/gtkb-operational-governance-hardening-005.md:530` through `bridge/gtkb-operational-governance-hardening-005.md:547`.
- The exit criteria still require all mutation patterns to be covered by at least one test at `bridge/gtkb-operational-governance-hardening-005.md:579`.

Risk/impact: This is a smaller issue than the hook I/O contract, but it is a direct mismatch between the stated success criterion and the proposed test list.

Required action: Add `test_ruby_i_detected` or remove Ruby from `MUTATION_PATTERNS` until it is covered.

## Resolved Prior Items

The following prior NO-GO items are resolved at proposal level:

- Latest-status bridge parsing: the proposal now specifies one latest status per document and tests `REVISED` over `NO-GO` plus `GO` over `NO-GO`.
- Bash mutation scope: the proposal now covers more than redirection and centralizes the classifier.
- `.groundtruth/` ownership: the proposal now includes Agent Red, GT-KB, and generated-project `.gitignore` changes plus scaffold tests.
- Existing Bash safety hooks: the proposal correctly recognizes the current GT-KB templates are inert under stdin-shaped Claude Code payloads and includes portation in Phase 1.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-operational-governance-hardening`.
- Read all referenced version files: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-005.md`.
- Read `.claude/rules/deliberation-protocol.md` and searched the deliberation archive. Initial searches hit a Windows `cp1252` output encoding failure; reruns with `PYTHONIOENCODING=utf-8` completed and returned the DELIB IDs cited above.
- Checked current Claude Code hook docs at https://docs.anthropic.com/en/docs/claude-code/hooks on 2026-04-16.
- Ran `claude --version` -> `2.1.39 (Claude Code)`.
- Inspected `groundtruth-kb` templates and scaffold files:
  - `templates/hooks/destructive-gate.py`
  - `templates/hooks/credential-scan.py`
  - `templates/hooks/assertion-check.py`
  - `templates/hooks/spec-classifier.py`
  - `templates/project/settings.local.json`
  - `src/groundtruth_kb/project/scaffold.py`
  - `src/groundtruth_kb/bootstrap.py`
  - `docs/reference/templates.md`
  - `.gitignore`
- Probed current GT-KB Bash safety templates:
  - stdin payload with `git reset --hard` into `templates/hooks/destructive-gate.py` -> `EXIT:0`
  - `TOOL_INPUT='{"command":"git reset --hard"}'` into `templates/hooks/destructive-gate.py` -> `EXIT:2`
  - stdin payload with `sk-1234567890123456789012345` into `templates/hooks/credential-scan.py` -> `EXIT:0`
  - `TOOL_INPUT='{"command":"echo sk-1234567890123456789012345"}'` into `templates/hooks/credential-scan.py` -> `EXIT:2`
- Queried `groundtruth-kb/groundtruth.db` schema: `source_paths_present=False`.
- No full test suite was run because this was a proposal review, not an implementation verification.

## GroundTruth KB Vision Filter

The proposal is aligned with the GroundTruth KB vision in intent: it moves governance work out of Mike's memory and into generated controls. The remaining gap is mechanical proof. A governance hook that asks the user but does not tell Claude why, or a self-test that sometimes exits as a blocker and sometimes as success, still leaves Mike responsible for noticing whether enforcement actually happened.

## Decision

NO-GO as written.

Prime should revise the hook output helper and self-test contract before implementation. The next revision can be narrow: make `ask` model-visible, use a documented context-output shape for `SessionStart` and `UserPromptSubmit` or attach runtime proof, make all `--self-test` commands exit 0 on success, and add the missing Ruby mutation test.
