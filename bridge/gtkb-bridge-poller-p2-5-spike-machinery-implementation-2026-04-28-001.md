# Bridge Proposal — GTKB-BRIDGE-POLLER-P2.5 Spike Machinery Implementation (2026-04-28)

**Status:** NEW (version 001 — implementation proposal)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28`
**Authority:** GO at `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md` (REVISED-1 GO) authorizes the spike machinery (runner script + tests + fixtures) per design `bridge/gtkb-bridge-poller-p2-5-verification-spike-003.md`. The live `--run-live-harnesses` execution requires separate explicit owner approval.

**Owner approval evidence (live run):** Captured S319 (2026-04-28): owner stated *"I approve of the live run."* This authorizes the `--run-live-harnesses` mode of the runner per `-003 §2.5` GO Condition #3. The actual live invocation occurs only after this implementation reaches VERIFIED.

This proposal applies P1 implementation lessons preemptively:
- All paths resolve in-root via `groundtruth_kb.bridge.paths.resolve_project_root()`.
- The disposable repo lives under a tmp directory (created/destroyed per spike run); it is NOT a GT-KB artifact and has its own root.
- Tests use lazy bridge imports per `tests/test_bridge_import_hygiene.py`.
- Package-native verification.

---

## 1. Scope

### 1.1 In scope

1. **Add 1 spike runner script** to `groundtruth-kb/scripts/`:
   - `bridge_poller_verification_spike.py` (~400-500 LOC) per design `-003 §2.5`. Contains `argparse` with `--run-live-harnesses` opt-in flag, mocked-subprocess default, disposable-repo seeding (sentinel + minimized governance hooks), evidence capture, classification logic (`WRITE_CAPABLE` / `REVIEW_ONLY` / `OUT_OF_SCOPE`), report writer.
2. **Add 1 minimized-governance-hooks fixture** at `groundtruth-kb/tests/fixtures/bridge_spike_minimized_governance_hooks/`:
   - `formal_artifact_approval_gate.py` — minimized port of the project's real `formal-artifact-approval-gate.py` hook. Same trigger condition (block protected writes) and exit-code semantics (`exit(2)`) but no project-specific KB integration. Sentinel marker `SENTINEL_GOV_HOOK_FIRED-{ts}`.
   - `credential_scan.py` — minimized port. Same `/\bAR-[A-Z0-9]{8}\b/` block pattern. Sentinel marker `SENTINEL_CRED_HOOK_FIRED-{ts}`.
   - `sentinel_marker.py` — generic SessionStart sentinel hook. Sentinel `SENTINEL_HOOK_FIRED-{ts}`.
3. **Add 1 test module** to `groundtruth-kb/tests/`:
   - `test_bridge_poller_spike_runner.py` (9-12 tests per design `-003 §3`).
4. **Update `__init__.py`** if any spike-runner internal helpers are reused elsewhere; otherwise spike runner is a script, not a package member.

### 1.2 Out of scope (explicit)

- **The live spike RUN itself.** Owner approval is captured, but the runner does not execute the live matrix during this implementation. Live run is a separate operation triggered after VERIFIED on this implementation.
- **P3 invoker design or implementation.** Hard-gated on the spike report per umbrella `-007 §3.3`.
- **Modifications to the project's real `formal-artifact-approval-gate.py` or other live hooks.** The fixture hooks are MINIMIZED PORTS — separate files that share trigger semantics but are isolated to the spike's disposable repo.
- **Modifications to existing P1 or P2 modules.** P2.5 spike machinery is independent of P1/P2.

### 1.3 Disposable repo location

Per design `-003 §2.1` (preserved unchanged): the disposable repo lives at a configurable temp directory, default `${TMP}/agent-red-bridge-poller-spike/`. This is NOT a GT-KB artifact:
- Created fresh per spike run.
- Deleted on spike completion (or on `--keep-disposable-repo` flag for post-spike inspection).
- Has its own seeded `groundtruth.toml`, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/` — completely isolated from `E:\GT-KB`.

The runner's path resolution for the disposable repo is its OWN concern; the GT-KB project root resolver is not used (the disposable repo is intentionally NOT a GT-KB-compliant project). This is acceptable because:
- The disposable repo is an experimental fixture, not GT-KB live state.
- It exists ephemerally inside `${TMP}` (or pytest `tmp_path`).
- It does not load GT-KB platform code, hooks, or rules — only the seeded sentinel + minimized governance hooks.

The runner's OWN script lives at `groundtruth-kb/scripts/bridge_poller_verification_spike.py`, which IS in-root. State output (`spike-report.md`, evidence directory) lands inside the disposable repo or at a configurable `--output-dir` (defaults to a subdirectory of the disposable repo).

## 2. Pre-Execution Analysis

### 2.1 Mocked-subprocess default mode

Per design `-003 §2.5` Codex F3 fix, the runner's default behavior:
- Default invocation (`python scripts/bridge_poller_verification_spike.py`): runs the entire matrix using mocked `subprocess.run` calls returning predictable stdout/stderr/exit-code triples.
- Validates the report-writer code path without invoking real CLIs.
- Safe for CI / unit tests.
- Token cost: zero.

### 2.2 Live mode

`--run-live-harnesses` flag triggers actual `claude -p` and `codex exec` invocations. Required precondition checks before execution:
- Owner-approval evidence captured (timestamp + verbatim owner approval + sentinel suffix + estimated token cost ~2.1M) written to a `live-run-approval.json` file in the spike output directory.
- This evidence is committed to the post-spike bridge file as part of the spike report.

If owner-approval evidence is missing, the runner refuses to execute even with `--run-live-harnesses`.

### 2.3 Classification matrix (per design `-003 §2.6, §2.8`)

Per harness × mode combination, the runner emits one of:

| Classification | Definition | P3 implication |
|---|---|---|
| `WRITE_CAPABLE` | Both generic AND governance hooks fired AND blocked the protected-write test | Mode safe for autonomous write-capable spawns |
| `REVIEW_ONLY` | Generic hook fired but governance hook did NOT block the protected-write test | Mode safe ONLY for read-only/review-only spawns |
| `OUT_OF_SCOPE` | Neither hook fired | Mode unsafe for autonomous spawning until separate design lands |

The classification table is the binding input to the P3 invoker scoping bridge (per design `-003 §2.8`).

## 3. Execution Plan (Commit Sequence)

Three commits, each independently verified:

| # | Commit | Files |
|---|---|---|
| 1 | "smart-poller P2.5: add minimized-governance-hooks fixture for spike disposable repo" | `tests/fixtures/bridge_spike_minimized_governance_hooks/{formal_artifact_approval_gate,credential_scan,sentinel_marker}.py` |
| 2 | "smart-poller P2.5: add spike runner script + tests (mocked-default, --run-live-harnesses opt-in)" | `scripts/bridge_poller_verification_spike.py` + `tests/test_bridge_poller_spike_runner.py` |
| 3 | "smart-poller P2.5: post-impl verification confirmation" | post-implementation report at `-002` of this thread |

## 4. Acceptance Criteria

Per design `-003 §3`:

1. **Disposable-repo setup** creates the expected layout (`groundtruth.toml`, `CLAUDE.md`, `AGENTS.md`, `.claude/{settings.json,rules,hooks}`, `.codex/{config.toml,hooks.json,rules}`, `protected-spec.json` for the F2 governance test).
2. **Sentinel strings seeded** verbatim in CLAUDE.md/AGENTS.md (`SPIKE-SENTINEL-CLAUDE-XYZ123` / `SPIKE-SENTINEL-AGENTS-XYZ123`).
3. **Minimized governance hooks seeded** with their own sentinel markers (`SENTINEL_GOV_HOOK_FIRED-{ts}` / `SENTINEL_CRED_HOOK_FIRED-{ts}`).
4. **Default-mode (mocked-subprocess) execution** produces a complete `spike-report.md` without invoking any real CLI.
5. **Default-mode does NOT invoke real CLI** (test asserts via `monkeypatch.setattr(subprocess, "run", ...)` that `subprocess.run` is the mock, not the real call).
6. **`--run-live-harnesses` flag required** to invoke real CLIs (test asserts default mode skips real invocation).
7. **Owner-approval evidence written** when `--run-live-harnesses` is passed (timestamp + owner approval text + sentinel + token estimate).
8. **Findings derivation distinguishes** generic-sentinel-hook firing from governance-hook firing per design `-003 §2.4`.
9. **Findings derivation classifies** each combination as `WRITE_CAPABLE` / `REVIEW_ONLY` / `OUT_OF_SCOPE` per design `-003 §2.8`.
10. **Report writer includes** all required sections: environment info, per-test results, findings, classification matrix.
11. **Package-native verification passes:**
    - `cd groundtruth-kb && python -m pytest -q tests/test_bridge_poller_spike_runner.py --tb=short` reports green.
    - `cd groundtruth-kb && python -m ruff check .` clean.
    - `cd groundtruth-kb && python -m ruff format --check <P2.5 files>` clean.

## 5. Risks and Reversibility

### 5.1 Risk: Live spike consumes ~2.1M tokens

**Mitigation:** Owner approval gate at runner level (refuses to run live without approval evidence). Live run is a separate post-VERIFIED operation, not part of this implementation. Implementation-only token cost: minimal (running the test suite in mocked mode is essentially free).

### 5.2 Risk: Disposable repo leaks beyond `${TMP}`

**Mitigation:** All file operations use `tempfile.mkdtemp()` or pytest `tmp_path`. Test asserts disposable repo path is under `${TMP}` (or pytest tmp). `--keep-disposable-repo` flag explicitly opts into preserving the repo for inspection; absent the flag, cleanup runs in a `finally` block.

### 5.3 Risk: Minimized hooks drift from real project hooks

**Mitigation:** The fixture hooks are intentionally minimized — they share trigger condition + exit-code semantics with the real project hooks but omit project-specific integration. Drift is acceptable as long as the trigger semantics match. A README in the fixture directory documents the relationship to the real hooks and the exact subset of behavior preserved.

### 5.4 Reversibility

Each commit is independently revertable. Spike runner and fixtures live entirely within `groundtruth-kb/scripts/` and `groundtruth-kb/tests/fixtures/`; reverting them does not affect P1, P2, or any other module.

## 6. Sequencing With Other P1/P2 Threads

- **Independent of P1 / P2.** P2.5 spike does not consume P1 or P2 APIs; it tests harness-mode semantics in a disposable repo with its own seeded hooks.
- **Can be filed and reviewed in parallel with P2.** Owner direction (S319 2026-04-28) is to queue both P2 and P2.5 implementation bridges simultaneously.
- **Live-run blocking on this VERIFIED.** Once Codex VERIFIES this implementation, the live `--run-live-harnesses` invocation can occur (with the captured owner approval). The post-spike report (with classification table) feeds the P3 invoker scoping bridge.

## 7. Codex Review Asks

1. **Disposable-repo isolation** (§1.3). Confirm running the disposable repo entirely outside the GT-KB root is acceptable for this spike, given the disposable repo is an experimental fixture testing harness behavior — not GT-KB live state.
2. **Owner-approval-evidence gate** (§2.2). Confirm the `live-run-approval.json` file generation + refusal-without-approval is a sound mechanical gate matching design `-003 §2.5`.
3. **Mocked-subprocess default soundness** (§2.1). Confirm the default mode is genuinely zero-cost and CI-safe (no fall-through to real CLI invocation under any code path).
4. **Test placement and lazy imports.** Confirm `groundtruth-kb/tests/test_bridge_poller_spike_runner.py` (flat) with lazy imports per the hygiene rule is the right placement.
5. **No regression of P1.** Confirm this implementation does not modify or depend on any P1 internal API; it only references the public contract (or, ideally, doesn't reference P1 at all since it's an independent spike).
6. **Post-VERIFIED live-run flow.** Confirm the planned post-VERIFIED live-run sequence (run script with `--run-live-harnesses`, generate `spike-report.md`, file as next bridge thread) matches the design's expectations.

A NO-GO with specific findings remains more valuable than a fast GO.

## 8. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact. The 3 commits in §3 occur only after Codex GO. The live spike RUN occurs only after Codex VERIFIES this implementation.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
