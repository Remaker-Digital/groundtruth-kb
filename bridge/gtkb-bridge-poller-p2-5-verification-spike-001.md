NEW

# GTKB-BRIDGE-POLLER-P2.5 — Verification Spike Scoping

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Parent program:** `GTKB-BRIDGE-POLLER-001` (work_list row 14)
**Umbrella:** `bridge/gtkb-bridge-poller-001-smart-poller-007.md` (REVISED-3 GO; this slice implements §3 verification spike)
**Companion bridges:** `bridge/gtkb-bridge-poller-p1-detector-003.md` (REVISED-1; foundation; independent), `bridge/gtkb-bridge-poller-p2-registry-001.md` (parallel scoping; independent)
**Gates:** P3 invoker design — no P3 implementation bridge files until this spike's report is reviewed and Codex GO's the consequent invoker design.

---

## Prior Deliberations

- `DELIB-1121` halt-os-pollers-token-regression VERIFIED (the S308 baseline this work avoids regressing).
- Umbrella REVISED-3 GO at `-007` §3 is the immediate scoping authority.
- `feedback_mcp_verification_required.md` from S311 establishes the empirical-verification-before-load-bearing-design pattern this spike applies to non-MCP harness primitives.

## 1. Why this spike exists

Codex `-005` correctly identified that the umbrella's headless-invocation
design rests on undocumented assumptions about `claude -p ... --bare`
and `codex exec ...` semantics:

- Does `--bare` strip `CLAUDE.md` auto-discovery? (`claude --help` says yes.)
- Does `--add-dir` restore project context when combined with `--bare`?
- Does any combination preserve the governance hooks (formal-artifact-approval-gate, assertion-ratchet, credential-scan) that umbrella §6 mandates?
- What is the per-spawn token cost in each mode?
- Does `codex exec` auto-load `AGENTS.md`?
- Does `codex exec` honor `.codex/hooks.json` on Windows? (Per `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle", the answer today is "no" — but the spike must verify whether `codex exec` differs from interactive Codex.)

These are empirical questions, not design questions. The spike answers
them with concrete evidence: command invocations, exit codes, full
stdout/stderr, files-changed diffs, and token-cost measurements.

The spike's report becomes the input to the eventual P3 invoker
scoping bridge. Without the spike, P3 would either guess (high risk
per `feedback_mcp_verification_required.md`) or go through multiple
NO-GO/REVISED cycles re-deriving these facts.

## 2. Spike contract

### 2.1 Disposable repo location

`C:/temp/agent-red-bridge-poller-spike/`

This is on the `_OUTPUT_DIR_ALLOWLIST_PATTERNS` whitelist used by the
isolation-rehearsal lanes (per `scripts/rehearse/_common.py:29-32`),
so the spike harness shares the same sandbox safety convention.

### 2.2 Disposable repo seed

The spike runner script seeds the disposable repo with:

```
C:/temp/agent-red-bridge-poller-spike/
  .git/                                  # fresh git init
  CLAUDE.md                              # contains SPIKE-SENTINEL-CLAUDE-XYZ123
  AGENTS.md                              # contains SPIKE-SENTINEL-AGENTS-XYZ123
  .claude/
    settings.json                        # registers no-op SessionStart hook + sentinel-marker hook
    rules/
      operating-role.md                  # active_role: prime-builder
    hooks/
      sentinel_marker.py                 # writes SENTINEL_HOOK_FIRED-{timestamp} on invocation
  .codex/
    config.toml                          # mirrors .claude config
    hooks.json                           # registers sentinel hook on Windows-equivalent surface
    rules/
      operating-role.md                  # active_role: prime-builder
  .gitignore                             # ignores test-output/
  test-output/                           # populated by spike runs (sentinel files, transcripts)
```

Sentinel strings are unique 6-char suffixes regenerated per spike run
to prevent confusion with leftover state from prior runs.

### 2.3 Test matrix

For each test, the spike captures:
- Exact command invocation (verbatim, including all flags)
- Exit code
- **Full** stdout (NOT summarized — per `feedback_no_lossy_compression.md`)
- **Full** stderr
- Files created/modified by the invocation (`git status` before and after)
- Sentinel marker file presence (proves whether the hook fired)
- Approximate token cost from session output where available
- Wall-clock duration

**Claude Code matrix (8 tests):**

| Test ID | Command | Question answered |
|---|---|---|
| C1 | `claude -p "Echo SENTINEL_PRESENT if you see CLAUDE-XYZ123 in your context. Echo SENTINEL_ABSENT otherwise."` | Default `claude -p` auto-loads CLAUDE.md? |
| C2 | `claude -p "..." --bare` | `--bare` strips CLAUDE.md? |
| C3 | `claude -p "..." --add-dir <repo>` | `--add-dir` restores context (no `--bare`)? |
| C4 | `claude -p "..." --bare --add-dir <repo>` | Composition: does `--bare` + `--add-dir` preserve CLAUDE.md? |
| C5 | (any of C1-C4 that fires the hook check) | Does SessionStart hook fire? Sentinel-marker file presence answers. |
| C6 | `claude -p "Touch test-output/scratch.txt and commit"` | Are governance hooks (formal-artifact-approval-gate, etc.) loaded? Attempt a spec write; should be blocked if hooks fired. |
| C7 | All of C1-C4 with token-output capture (`--output-format json` if supported) | Per-spawn token cost in each mode |
| C8 | `claude -p "..."` × 3 sequential runs | Token cost variance across runs (cache effects?) |

**Codex matrix (6 tests):**

| Test ID | Command | Question answered |
|---|---|---|
| K1 | `codex exec "Echo SENTINEL_PRESENT if you see AGENTS-XYZ123 in your context."` | Default `codex exec` auto-loads AGENTS.md? |
| K2 | `codex exec ... --cd <repo>` | Does `--cd` set working dir correctly? |
| K3 | `codex exec ... --sandbox <mode> --approval <policy>` | Sandbox + approval flag behavior; specifically "no-network" + "never-prompt" |
| K4 | `codex exec ... --profile <name>` | Does profile selection load `.codex/config.toml` profile? |
| K5 | (any of K1-K4 with sentinel-marker-hook check) | Does `.codex/hooks.json` fire on Windows during `codex exec`? Per `acting-prime-builder.md` Harness Hook Parity Fallback Principle, expected answer: **no** on Windows. Verify. |
| K6 | All of K1-K4 with token-output capture | Per-spawn token cost in each mode |

### 2.4 Spike report

Single deliverable: `C:/temp/agent-red-bridge-poller-spike/spike-report.md`.

Structure:

```markdown
# Bridge-Poller Verification Spike — Report

Date: <ts>
Spike runner version: <commit-sha>
Sentinel suffix: <6-char>

## Environment

- claude version: <output of `claude --version`>
- codex version: <output of `codex --version`>
- Windows version: <output of `cmd /c ver`>
- Python version: <output of `python --version`>

## Test C1 — claude -p (no flags) auto-loads CLAUDE.md
Command: `claude -p "Echo SENTINEL_PRESENT if you see CLAUDE-XYZ123 in your context. Echo SENTINEL_ABSENT otherwise."`
Exit code: <int>
Stdout: <full>
Stderr: <full>
Files changed: <list>
Sentinel marker file present: <yes/no>
Token cost: <approx>
Walltime: <seconds>

## Test C2 — claude -p --bare ...
[same structure]

[... C3 through K6 ...]

## Findings

### F1 — Does --bare preserve governance context?
Answer: <yes/no/partial>, derived from <test IDs>
Implication for P3 invoker design: <text>

### F2 — Does codex exec honor .codex/hooks.json on Windows?
Answer: <yes/no>, derived from <test IDs>
Implication for P3 invoker design: <text>

### F3 — Per-spawn startup cost actual measurements
| Mode | Avg tokens (n=3) | Range |
|---|---|---|
| claude -p (default) | <num> | <range> |
| claude -p --bare | <num> | <range> |
| claude -p --add-dir | <num> | <range> |
| claude -p --bare --add-dir | <num> | <range> |
| codex exec (default) | <num> | <range> |
| codex exec --sandbox no-network --approval never-prompt | <num> | <range> |

### F4 — Recommended P3 invoker default for Claude
Based on F1+F3, the invoker should use: `<exact command template>`
Rationale: <text>

### F5 — Recommended P3 invoker default for Codex
Based on F2+F3, the invoker should use: `<exact command template>`
Rationale: <text>

## Risk findings

[Anything observed that wasn't in the test matrix but matters]
```

### 2.5 Spike runner script

`scripts/bridge_poller_verification_spike.py`:

```python
"""Run the bridge-poller verification spike. Produces spike-report.md."""

# Skeleton:
def main():
    repo = setup_disposable_repo("C:/temp/agent-red-bridge-poller-spike")
    sentinel = generate_sentinel_suffix()  # 6-char random
    seed_repo(repo, sentinel)

    results = []
    for test_id, command_template, question in CLAUDE_MATRIX + CODEX_MATRIX:
        result = run_test(repo, sentinel, test_id, command_template)
        results.append(result)

    findings = derive_findings(results)
    write_report(repo / "spike-report.md", env_info(), results, findings)
```

The runner is deterministic given a sentinel; re-running produces a
new report with a fresh sentinel. Reports are NOT auto-committed; the
spike author (Prime) reviews the report and files it as evidence in
the post-spike bridge entry.

### 2.6 Acceptable spike outcomes

The spike is **evidence-gathering**, not pass/fail. Any of the
following are acceptable findings:

- `--bare` preserves hooks → P3 default uses `--bare` (cheaper).
- `--bare` strips hooks → P3 default omits `--bare` (more expensive but governance-safe).
- `codex exec` doesn't honor hooks on Windows → P3 Codex invocation either skips Codex on Windows OR explicitly accepts the gap and runs governance verification differently.
- Token costs differ wildly from umbrella §7.2 estimates → §7.2 gets updated based on real numbers.

What's **not acceptable**: making P3 design decisions without the
spike's evidence.

### 2.7 Spike scope NOT including

- MCP-based push channel verification — that's the v2 spike (separate, deferred per umbrella §8).
- Cross-platform spike (Linux, macOS) — Windows-only here. Cross-platform verification deferred to a separate sub-bridge after Windows P3 ships.
- Long-running session economics — single spawn measurements only. Long-session amortization is a v2 concern.

## 3. Verification (of the spike itself)

The spike runner script needs minimal tests because it's a one-time
investigation tool, not production code. Tests cover:

```python
# tests/scripts/test_bridge_poller_spike_runner.py
def test_setup_disposable_repo_creates_expected_layout(tmp_path): ...
def test_setup_disposable_repo_seeds_sentinels(tmp_path): ...
def test_run_test_captures_stdout_stderr_exit_code(tmp_path, monkeypatch): ...
def test_run_test_captures_files_changed(tmp_path): ...
def test_write_report_includes_all_required_sections(tmp_path): ...
```

The actual spike *runs* are not unit tests — they're invocations of
the runner against real `claude` / `codex` CLIs. Those produce the
spike-report.md artifact, which is the deliverable.

## 4. Risk + decision notes

- **Disposable repo isolation**: spike repo is under `C:/temp/`, not in any project tree. Sentinel-based content prevents cross-contamination with real CLAUDE.md / AGENTS.md.
- **Token cost of running the spike itself**: each spawn in the matrix consumes whatever tokens the harness uses. Conservative estimate: 14 tests × ~150k tokens/spawn = ~2.1M tokens for one full spike run. **This is one-time** and produces persistent evidence; vs. the alternative of guessing and going through multiple NO-GO cycles for P3.
- **Spike re-runs needed only if**: harness CLI changes (new `claude` or `codex` version with different flag semantics) — at which point the spike is re-run and the report updated.
- **No production impact**: spike does not touch this project tree, the KB, or any deployable artifact.

## 5. Files changed

### 5.1 New (groundtruth-kb upstream)

- `scripts/bridge_poller_verification_spike.py` (~300-400 LOC for the runner)
- `tests/scripts/test_bridge_poller_spike_runner.py` (~5-8 tests)

### 5.2 Disposable repo artifacts (NOT committed)

- Everything under `C:/temp/agent-red-bridge-poller-spike/`. The spike-report.md is captured as evidence in the post-spike bridge filing, but the disposable repo itself is not committed.

### 5.3 No changes to existing modules

The spike runner is standalone. No changes to `groundtruth_kb/bridge/`, no changes to `scripts/rehearse/`, no changes to settings or hooks of this project.

## 6. Sequencing

- **Independent of P2 registry slice** — both can ship in parallel. P2 produces information that P3 will use; P2.5 produces evidence that P3's design will use.
- **Independent of P1 detector** — different layers of the stack.
- **Gates**: this slice's spike-report.md output IS a hard prerequisite for the P3 invoker scoping bridge. P3 cannot file until the report exists.
- **Implementation owner**: `groundtruth-kb` upstream framework (the runner script). Disposable repo artifacts are not part of either repo.

## 7. Codex Review Asks

1. Confirm the test matrix (§2.3) covers the questions umbrella REVISED-3 §3 raised about `--bare` semantics, `codex exec` flag specification, and per-spawn cost.
2. Confirm the no-lossy-compression evidence capture (§2.3 "Full stdout/stderr") matches `feedback_no_lossy_compression.md`.
3. Confirm acceptable-outcome posture (§2.6) — that the spike is evidence-gathering, not pass/fail.
4. Confirm the spike runner needs only minimal tests (§3) since it's a one-time investigation tool rather than production code.
5. **GO / NO-GO** on this standalone P2.5 slice.

## 8. Decisions Needed From Owner

After Codex GO, before spike runner implementation:

1. **Claude Code spike subscription cost.** Each spike run is ~2.1M tokens (one-time). Owner approve? (Default: yes; cost is justified by avoiding multiple P3 NO-GO cycles.)
2. **Re-run cadence.** Default proposed: re-run only when `claude` or `codex` version changes meaningfully. Owner can override.
3. **Spike report archival.** Default proposed: spike-report.md captured in the post-spike bridge entry as evidence; not committed to repo. Owner can override (e.g., commit to `independent-progress-assessments/` for durability).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
