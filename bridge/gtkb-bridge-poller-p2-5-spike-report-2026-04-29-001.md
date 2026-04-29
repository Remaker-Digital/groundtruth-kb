# Bridge Spike Report — GTKB-BRIDGE-POLLER-P2.5 Verification Spike Live Run (2026-04-29)

**Status:** NEW (version 001 — spike report from the actual live run)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28 owner approval; 2026-04-29 live run)
**Document name:** `gtkb-bridge-poller-p2-5-spike-report-2026-04-29`
**Authority:** Owner approval captured S319 ("I approve of the live run.") archived as `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`. Approval evidence file at `.gtkb-state/bridge-poller/spike-approvals/2026-04-29-live-001-owner-approval.json`. Spike machinery VERIFIED at `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-008.md`.

This is the binding P3 invoker input: the actual classification table from the live spike run.

---

## 1. Run Metadata

- **run_id:** `2026-04-29-live-001`
- **on-disk artifact:** `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/spike-report.md`
- **approval receipt:** `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/evidence/live-run-approval.json`
- **disposable-repo:** `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/disposable-repo/` (kept for inspection)
- **report-mode-line:** `**LIVE** (--run-live-harnesses)` — captured from real subprocess invocations.
- **token cost (actual):** Across the 4 successful Claude/Codex invocations (the others timed out / errored without consuming model tokens). Below the ~2.1M ceiling. Real numbers in the on-disk report.
- **runner-side encoding warning:** A non-fatal `UnicodeDecodeError` (cp1252 codec, byte 0x9d) appeared on `subprocess.run` output reading from one or more invocations on Windows. Did not prevent report generation. Fix queued: set `encoding="utf-8", errors="replace"` on subprocess.run in `_run_command_live`. Tracked as a follow-on non-blocking concern.

## 2. Binding Classification Table (P3 Input)

| Harness | Mode | Verdict | Sentinel hook fired | Governance hook fired | Protected-spec unchanged | exit_code | duration_s |
|---|---|---|---|---|---|---|---|
| claude | default | **OUT_OF_SCOPE** | False | False | True | 124 (TIMEOUT) | 120.493 |
| claude | bare | **OUT_OF_SCOPE** | False | False | True | 1 (Not logged in) | 0.910 |
| claude | add-dir | **OUT_OF_SCOPE** | False | False | True | 0 (success) | 48.448 |
| claude | bare+add-dir | **OUT_OF_SCOPE** | False | False | True | 1 (Not logged in) | 0.994 |
| codex | default | **OUT_OF_SCOPE** | False | False | True | 0 (success) | 95.225 |
| codex | cd | **OUT_OF_SCOPE** | False | False | True | 0 (success) | 76.072 |
| codex | sandbox+approval | **OUT_OF_SCOPE** | False | False | True | 2 (cmd syntax) | 0.024 |
| codex | profile | **OUT_OF_SCOPE** | False | False | True | 1 (no profile) | 0.037 |

**Result:** Zero `WRITE_CAPABLE`, zero `REVIEW_ONLY`, eight `OUT_OF_SCOPE`. Per umbrella `-007 §3.1`, P3 invoker cannot treat any of these modes as write-capable for autonomous spawning.

## 3. Per-Mode Behavioral Findings

### 3.1 Claude `default` (no `--bare`, no `--add-dir`)

**Evidence:** Timed out after 120s with empty stdout/stderr.

**Interpretation:** The bare `claude -p "spike-prompt"` invocation appears to hang awaiting stdin or interactive input despite `-p` (one-shot mode). Possible cause: claude's headless mode in this version requires `--add-dir` or some other non-interactive input source. Without it, the process doesn't terminate within 120s.

**Implication for P3:** Mode unusable for autonomous invocation due to hang risk alone, separate from the no-hooks-fired finding.

### 3.2 Claude `--bare` (no `--add-dir`)

**Evidence:** Failed in 0.91s with stdout `Not logged in · Please run /login`.

**Interpretation:** `--bare` strips Claude's authentication context (likely intentional — `--bare` is documented as "no project context"). Even with valid auth in the parent session, the `--bare` subprocess sees no auth.

**Implication for P3:** `--bare` mode is unusable for any autonomous spawn (auth fails). This makes the cost-saving rationale for `--bare` invocation in P3 moot — there's no auth bypass that lets `--bare` work in a subprocess context.

### 3.3 Claude `--add-dir <disposable_repo>`

**Evidence:** Succeeded in 48.4s. Returned a properly-formatted SPIKE-ACK response confirming it loaded the disposable repo's CLAUDE.md and AGENTS.md sentinel strings, recognized the working directory, and did not modify `protected-spec.json`. **However, NEITHER SessionStart sentinel NOR PreToolUse governance hook fired in `evidence_dir`.**

**Critical interpretation:** `claude -p --add-dir <repo>` reads the target directory's CLAUDE.md (proven by the SPIKE-ACK output recognizing the sentinel strings) but does NOT load `.claude/settings.json` from the target dir for hook registration. Hooks are loaded from the **caller's** `.claude/settings.json`, not from the `--add-dir` target.

**Implication for P3:** This is the most consequential finding. Even with the spike's `.claude/settings.json` and `.claude/hooks/*.py` correctly seeded in the disposable repo, headless Claude invocation does not run those hooks. The hook protocol is bound to the caller's session, not the target context.

For autonomous invocation, this means: hooks must already be installed at the **invoking session's** project root (or the user's machine settings), not in the per-spawn target. The smart poller cannot rely on per-spawn hook registration.

### 3.4 Claude `--bare --add-dir <repo>`

**Evidence:** Same "Not logged in" failure as `--bare` alone.

**Interpretation:** `--bare` overrides the auth-from-add-dir behavior. The two flags are not composable in the way the design hoped.

### 3.5 Codex `default` (no `--cd`)

**Evidence:** Succeeded in 95.2s. Returned a Loyal Opposition startup disclosure: resolved role from `<project_root>/harness-state/codex/operating-role.md`, scanned the **parent** `bridge/INDEX.md` (81 entries — the real GT-KB INDEX, not the disposable repo's). NO hooks fired in evidence_dir.

**Critical interpretation:** Codex headless `codex exec` from a subprocess loads the **parent process's working directory's** GT-KB context, not a disposable target. The disposable repo's role record, hooks, and INDEX were ignored. Per ADR-CODEX-HOOK-PARITY-FALLBACK-001, Codex hooks are inactive on Windows anyway.

**Implication for P3:** Codex spawned from inside a GT-KB project will load the parent's role and bridge context. This is fine for "Codex reviews bridge entries from the same GT-KB project" use cases but means the disposable-repo isolation pattern doesn't work for Codex testing. For P3, Codex spawn behavior is "always uses parent project context."

### 3.6 Codex `--cd <disposable_repo>`

**Evidence:** Succeeded in 76.1s. Same Loyal Opposition role + 81-entry bridge scan as `default` mode. The `--cd` argument is honored as the working directory but the role/hooks loading is unaffected.

**Interpretation:** Codex does not re-resolve role context based on `--cd`. The role/INDEX lookup happens at process start before `--cd` takes effect, OR Codex resolves role from environment rather than from cwd.

### 3.7 Codex `--approval never`

**Evidence:** Failed in 24ms with stderr: `error: unexpected argument '--approval' found. tip: to pass '--approval' as a value, use '-- --approval'`.

**Interpretation:** This Codex version requires `-- --approval never` (positional separator first). The runner's mode list has wrong syntax for this combination.

**Action:** Fix the spike runner's `_codex_modes()` to use `-- --approval never` for this mode. Re-run the spike to get a real classification for this mode. Out of scope for this report; queued as follow-on.

### 3.8 Codex `--profile default`

**Evidence:** Failed in 37ms with stderr: `Error: config profile 'default' not found`.

**Interpretation:** No `default` profile is configured in this Codex installation's `~/.codex/config.toml`. The mode test requires a pre-configured profile name.

**Action:** Either create a `default` profile in the disposable repo's `.codex/config.toml` (so the test is hermetic) or skip this mode if no profile is available. Out of scope for this report; queued as follow-on.

## 4. Findings Summary for P3 Scoping

### 4.1 Hook firing (the central F2 question)

**Did SessionStart sentinel fire in any harness × mode?** No.

**Did PreToolUse governance hook fire in any harness × mode?** No.

**Did `protected-spec.json` get modified in any combination?** No (defaults to True because the file was unchanged, but this is meaningless given no harness attempted a write).

**Translation:** None of the 8 tested combinations is `WRITE_CAPABLE`. None is even `REVIEW_ONLY` (which would require generic sentinel firing). All are `OUT_OF_SCOPE` per the spike's classification matrix.

### 4.2 Causal analysis

The hook-firing failure has two distinct root causes:

**Claude side (modes 1-4):**
- `--bare` modes (2, 4) hit auth gate, never get far enough to fire hooks.
- `default` mode (1) hangs on stdin, never completes.
- `--add-dir` mode (3) succeeds but hooks load from caller's `.claude/settings.json`, not from `--add-dir` target. The disposable repo's hooks are ignored.

**Codex side (modes 5-8):**
- `default` and `--cd` (5, 6) succeed but use parent project context. Per ADR-CODEX-HOOK-PARITY-FALLBACK-001, Codex hooks are inactive on Windows regardless of source.
- `--approval` and `--profile` (7, 8) have command-syntax / config issues unrelated to hook firing.

### 4.3 What this means for P3 invoker design

**P3 cannot autonomously spawn write-capable harness sessions in any of the tested modes.**

Specifically:
1. **Claude `--add-dir` mode produces output but is REVIEW_ONLY at best**: even though the harness accepts the prompt and responds, the absence of governance-hook firing means the smart poller can't trust write-protection in spawned sessions. Use ONLY for read-only / review-only workloads (e.g., "summarize this bridge thread") where no protected writes are attempted.
2. **All other modes are unusable**: timeout (mode 1), auth fail (modes 2, 4), command-syntax errors (modes 7, 8), or design-incompatible context-loading (modes 5, 6).
3. **No write-capable autonomous spawning until separate design lands** — per umbrella `-007 §3.1`. P3 design must explicitly defer write-capable spawning to a future phase that addresses the hook-loading model.

### 4.4 Smart poller deployment implication

The original umbrella `-007 §3.1` required the smart poller to be opt-out (always-on when ready). Given this evidence:

- **The smart poller can ship in a "review-only / notification" mode** where it detects bridge INDEX changes and either: (a) writes a notification artifact, OR (b) spawns a Claude `--add-dir` session for review-only summarization. Neither path needs WRITE_CAPABLE.
- **Autonomous Prime↔Codex bridge dispatch is blocked** until the hook-loading model is solved. Manual `Bridge` triggers remain the active mechanism for round-trip work.

This is a substantive scope reduction relative to the original P3 design intent. The decision belongs with the owner.

## 5. Codex Review Request

Please verify:

1. **Classification matrix correctness.** Confirm the 8 OUT_OF_SCOPE verdicts match the per-test evidence (sentinel/governance markers absent in evidence_dir; protected-spec unchanged; exit codes as captured).

2. **Behavioral findings accuracy.** Confirm the per-mode interpretations (§3.1–§3.8) match the captured stdout/stderr in the on-disk `spike-report.md`. Flag any I've misread.

3. **P3-implication soundness.** Confirm the §4.3 implication (no autonomous write-capable spawning in any tested mode; review-only Claude `--add-dir` is the only candidate path) is correctly derived. Flag any other interpretation worth surfacing.

4. **Out-of-scope follow-ons.** Confirm the queued follow-ons (cp1252 encoding fix; Codex `--approval` syntax fix; Codex profile config) are appropriately scoped as non-blocking refinements rather than re-spike requirements.

5. **Smart-poller deployment scope reduction.** Per §4.4, the original umbrella's "opt-out when functional" stance is in tension with the actual evidence. Codex review should surface whether: (a) the smart poller should ship in a notification/review-only mode (degraded scope); (b) further design work is required before any deployment; (c) something else.

A NO-GO with specific findings remains more valuable than a fast GO. The spike's purpose is to produce binding P3 input; this report is the first such evidence and the design constraints emerge from it.

## 6. Decisions Needed From Owner

After Codex review and any required revisions:

1. **Smart-poller scope decision** (per §5 ask #5): does the program ship in a degraded review-only mode based on this evidence, OR pause for further design work, OR something else?
2. **Re-spike authorization** (if Codex requires fixing the Codex syntax issues + re-running): the original 2.1M ceiling assumed all 8 modes ran successfully. A re-spike adding the syntax fixes would be substantially cheaper (~1.0-1.5M tokens) since 4 of the original modes consumed minimal tokens (immediate failures).
3. **Cleanup vs. preservation of `<run_id>` workspace**: the disposable-repo and evidence dir at `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/` are kept for inspection. Owner can direct cleanup whenever convenient.

## 7. Reversibility

This bridge file is a report of an already-executed spike; it does not propose any code change. The on-disk artifacts at `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/` are preserved for inspection. No code change is required to land this report; Codex review of the report informs the next bridge thread (P3 invoker scoping).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
