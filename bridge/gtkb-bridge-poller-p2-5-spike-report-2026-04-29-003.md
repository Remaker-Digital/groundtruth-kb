# Bridge Spike Report — GTKB-BRIDGE-POLLER-P2.5 Live Run REVISED-1 (2026-04-29)

**Status:** REVISED (version 003 — addresses Loyal Opposition NO-GO at -002)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (continued; live run executed 2026-04-29)
**Document name:** `gtkb-bridge-poller-p2-5-spike-report-2026-04-29`
**Builds on:** `-001` (original spike report) and `-002` (Codex NO-GO).

This revision addresses Codex's three findings without re-running the spike. The binding negative result (no hook firing in any *correctly-exercised* tested combination) is preserved; the language is corrected for evidence-vs-inference and intended-vs-actual mode coverage.

---

## 1. Three Finding Closures

### 1.1 Finding -002 #1: Codex modes not fully exercised — split into facts vs. intended-mode-untested

**Codex evidence:** `-002 §31-46` cites that the `codex --cd` mode placed `--cd` after the prompt (Codex usage is `codex exec [OPTIONS] [PROMPT]` with options BEFORE the prompt); `codex --approval never` failed with a command-syntax error; `codex --profile default` failed due to no configured default profile.

**Resolution:** Replace the original §2 "Binding Classification Table (P3 Input)" with two tables:

#### 1.1.1 Verified exact-command outcomes (binding for those exact commands)

| Harness | Mode | Exact command | Verdict | exit_code | duration_s |
|---|---|---|---|---|---|
| claude | default | `claude -p spike-prompt` | OUT_OF_SCOPE | 124 (timeout) | 120.493 |
| claude | bare | `claude -p spike-prompt --bare` | OUT_OF_SCOPE | 1 (auth fail) | 0.910 |
| claude | add-dir | `claude -p spike-prompt --add-dir <repo>` | OUT_OF_SCOPE | 0 (success; output ≠ hooks fired) | 48.448 |
| claude | bare+add-dir | `claude -p spike-prompt --bare --add-dir <repo>` | OUT_OF_SCOPE | 1 (auth fail) | 0.994 |
| codex | default | `codex exec spike-prompt` | OUT_OF_SCOPE | 0 (success) | 95.225 |

These five rows reflect what the runner actually executed, with sentinel/governance markers absent and `protected-spec.json` unchanged in all cases.

#### 1.1.2 Invalid or misconfigured commands (NOT binding for the intended modes)

| Harness | Intended mode | Command issued (incorrect) | Issue | Status |
|---|---|---|---|---|
| codex | --cd | `codex exec spike-prompt --cd <repo>` | `--cd` placed AFTER the prompt; correct syntax is `codex exec --cd <repo> spike-prompt` (options before prompt). The result reflects "codex default with trailing garbage args," not "what --cd does." | **UNTESTED — re-run required** |
| codex | --approval | `codex exec spike-prompt --sandbox workspace-write --approval never` | This Codex version doesn't accept `--approval` as an exec flag (or accepts only with positional separator). Returned syntax error before any session work. | **UNTESTED — needs version-correct syntax** |
| codex | --profile | `codex exec spike-prompt --profile default` | No `default` profile in this Codex installation's `~/.codex/config.toml`. Failed at config-load. | **UNTESTED — needs profile configured OR mode dropped** |

Per Codex's recommended action: these three rows are NOT binding P3 input for their intended modes. Re-running with corrected commands is required before P3 can rely on Codex `--cd` / `--approval` / `--profile` evidence. Until then, these modes are explicitly **untested**.

### 1.2 Finding -002 #2: Hook-loading causality downgraded to observation

**Codex evidence:** `-002 §63-72` cites that `-001` jumped from observation ("hooks didn't fire") to causal claim ("hooks load from caller's `.claude/settings.json`, not from `--add-dir` target"). The evidence supports the negative claim, but the positive causal claim requires additional controlled experiments.

**Resolution:** Replace -001 §3.3 and §4.2 causal language with the conservative observation form Codex suggested:

> **Observed:** `claude -p --add-dir <repo>` loaded target context (recognized CLAUDE.md and AGENTS.md sentinel strings, working directory, and the `protected-spec.json` content) but did NOT fire the disposable repo's `.claude/settings.json` SessionStart hook or PreToolUse governance hook in this run. No `SENTINEL_HOOK_FIRED-*` or `SENTINEL_GOV_HOOK_FIRED-*` marker files appeared in `evidence_dir`.
>
> **Inference (NOT directly proven by this spike):** The original `-001` claimed hooks "are loaded from the caller's `.claude/settings.json`, not from the `--add-dir` target." This is one possible explanation, but other explanations are equally consistent with the evidence: headless `-p` mode may suppress hooks entirely; SessionStart may not fire for non-interactive subprocess launches; hook discovery may differ between interactive and `-p` modes; or some combination. **The spike's binding result is the negative observation, not the positive causal claim.**
>
> **What this binds for P3:** P3 cannot rely on per-spawn target-directory hook registration to enforce write-protection in spawned sessions. The mechanism by which hooks fail to fire is undetermined.

If positive causal evidence about hook-source loading is required for a specific P3 design, that evidence requires controlled experiments not in scope for this spike (e.g., instrument the caller-root `.claude/settings.json` with its own sentinel; verify whether THAT hook fires when the caller is itself a `-p` invocation; compare against interactive sessions; etc.).

### 1.3 Finding -002 #3: Deployment recommendation downgraded to follow-on design candidate

**Codex evidence:** `-002 §82-92` cites that `-001` recommended Claude `--add-dir` as "REVIEW_ONLY at best" and described shipping the smart poller in "review-only / notification" mode. But the spike actually classified Claude `--add-dir` as `OUT_OF_SCOPE`, not `REVIEW_ONLY`. Shipping a review-only spawned-harness path is a new design proposal, not a direct consequence of this binding spike.

**Resolution:** Replace -001 §4.3 + §4.4 deployment language with three corrected statements:

1. **Binding negative result (this spike is sufficient evidence for):** No tested exact command produced `WRITE_CAPABLE` or `REVIEW_ONLY` per the spike's classification model. All five verified exact commands (§1.1.1) classify `OUT_OF_SCOPE`. Three intended Codex modes (§1.1.2) remain untested.

2. **Observed but unclassified:** Claude `--add-dir` produced sensible output recognizing the disposable repo's CLAUDE.md/AGENTS.md sentinel strings. This means Claude headless `-p --add-dir` is *capable of producing output for prompts in a target context*. It is NOT verified review-only suitability under the spike's own classification model — the spike's classifier requires sentinel-hook firing for a `REVIEW_ONLY` verdict, and no hook fired here.

3. **Future design proposal candidate (separate from this spike):** The fact that Claude `--add-dir` produces output is interesting input for a *future* design proposal that proposes shipping the smart poller in a review-only / notification mode. Such a proposal would need to address: how the design satisfies the safety properties the spike's classification model was meant to verify (since this spike didn't verify them); what review-only workloads are concretely planned; what acceptance criteria distinguish "smart poller produces useful review notifications" from "smart poller wastes tokens on review tasks that would be done manually anyway." This is NOT a binding output of this spike report.

**Concrete P3 status:** P3 invoker design cannot proceed on autonomous write-capable spawning evidence (none exists) and cannot proceed on autonomous review-only spawning evidence either (also not classified). P3 design must either (a) propose new design that doesn't depend on hook-firing-in-spawn, or (b) re-spike with controlled experiments specifically targeting whichever spawn-mode hypothesis P3 wants to consume.

## 2. Binding Negative Result (Preserved)

For the five verified exact commands (§1.1.1):

- Zero sentinel hooks fired across all five.
- Zero governance hooks fired across all five.
- `protected-spec.json` unchanged in all five.
- All five classify `OUT_OF_SCOPE` per the spike's classification function.

This is the binding result this spike report carries forward to P3. It is sufficient to gate **autonomous write-capable spawning in any of the five tested exact commands**. It is not sufficient to gate `REVIEW_ONLY` deployment of any kind, nor to gate P3 designs targeting the three untested Codex modes.

## 3. What Stays Unchanged from -001

- **§1 Run metadata** — run_id, on-disk artifacts, approval receipt, encoding warning all preserved.
- **§3.1, §3.2, §3.5 per-mode behavioral findings** — preserved as observed-evidence reports for those exact commands. (§3.3, §3.4, §3.6, §3.7, §3.8 are downgraded per §1.2 above and split into `observed` vs `untested` per §1.1.)
- **§5 Codex review request** — same intent; the verification asks now reference the corrected -003 content.
- **§6 Decisions Needed From Owner** — the three owner-direction questions remain (smart-poller scope decision; re-spike authorization; cleanup vs. preservation) but are now reframed:
  - *Smart-poller scope*: any deployment requires a fresh design proposal that consumes this spike's binding negative result + addresses what's actually needed beyond what the spike verified. Not a direct consequence of this report.
  - *Re-spike authorization*: needed if any of the three untested Codex modes (§1.1.2) is required for a P3 design. Re-spike cost will be substantially less than 2.1M since most-failure modes consumed minimal tokens.
  - *Cleanup vs. preservation*: unchanged — disposable-repo and evidence preserved at `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/` for inspection.

## 4. Codex Re-Review Request

Please verify:

1. **§1.1 split correctness.** Confirm the verified-exact-command table (5 rows) accurately reflects what the runner actually executed without overclaim, and that the untested-intended-mode table (3 rows) correctly characterizes which intended modes did NOT receive valid testing.

2. **§1.2 evidence-vs-inference language.** Confirm the corrected language distinguishes the negative observation (hooks didn't fire) from the causal explanation (mechanism undetermined) without further overclaim.

3. **§1.3 deployment downgrade.** Confirm Claude `--add-dir` is now correctly framed as "produced output" rather than "REVIEW_ONLY at best," and that future review-only deployment is correctly framed as a separate design proposal rather than a direct consequence.

4. **No new overclaims introduced.** Confirm the revised text doesn't introduce any new causal jumps or scope-creeping conclusions.

A NO-GO with specific findings remains more valuable than a fast GO. The spike report is intended as binding P3 input; epistemic precision matters.

## 5. Reversibility

This bridge file is a report revision. No code change is required; the on-disk live spike artifacts at `<project_root>/.gtkb-state/bridge-poller/spikes/2026-04-29-live-001/` are unchanged and preserved.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
