# Bridge Proposal — GTKB-BRIDGE-POLLER-P1 Detector Implementation (2026-04-28)

**Status:** NEW (version 001 — implementation proposal)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p1-detector-implementation-2026-04-28`
**Authority:** GO at `bridge/gtkb-bridge-poller-p1-detector-004.md` (REVISED-1) authorizes implementation of the P1 detector/parser/checkpoint slice per the design at `bridge/gtkb-bridge-poller-p1-detector-003.md`.

This is the implementation proposal corresponding to the P1 design GO. The design substance lives in `-003` (REVISED-1, GO'd at `-004`). This proposal describes the *execution plan* for that design: where files land, commit sequence, test integration, CI/release-gate hookup, and verification.

---

## 1. Scope

P1 detector/parser/checkpoint/routing/audit slice. Standalone — no harness invocation, no notification, no project-file mutation outside `~/.gtkb-state/` (or platform-rooted equivalent per below).

### 1.1 In scope

1. **Add 4 source modules** to `groundtruth-kb/src/groundtruth_kb/bridge/`:
   - `detector.py` (~150 LOC) — parser state machine, `ParseResult`/`ParseWarning`/`ParseError` dataclasses per `-003 §3.2`/`§3.3`.
   - `checkpoint.py` (~80 LOC) — bootstrap mode + corrupt-recovery per `-003 §3.7`; checkpoint read/write/diff per `-003 §3.4`.
   - `routing.py` (~70 LOC) — `TransitionOutcome` enum + per-document routing per `-003 §3.5`.
   - `audit.py` (~70 LOC) — audit-log emission per `-003 §3.6`.
2. **Add 4 test modules** to `tests/scripts/`:
   - `test_bridge_detector.py` (12 tests per `-003 §4.1`)
   - `test_bridge_checkpoint.py` (4+ tests per `-003 §4.1`)
   - `test_bridge_routing.py` (2+ tests per `-003 §4.1`)
   - `test_bridge_audit.py` (existing tests from `-001 §3.6`)
3. **Add live-INDEX regression fixture** at `tests/fixtures/bridge_index_live_snapshot.md` — frozen snapshot of current `bridge/INDEX.md` content per `-003 §4.2`.
4. **Update `bridge/__init__.py`** to expose public API surface (`ParseResult`, `parse_index`, `Checkpoint`, `diff_against_checkpoint`, `route_transitions`, `emit_audit`).
5. **Add `pyproject.toml` test discovery hook** if needed (likely not — `tests/scripts/` is already discovered).
6. **Wire into release-candidate gate** (`scripts/release_candidate_gate.py`) so the new test modules run in the standard regression suite.
7. **Update `groundtruth-kb/docs/`** with module documentation if the existing tutorial draft `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` (currently untracked) references P1 — coordinate with that draft as it lands.

### 1.2 Out of scope (explicit)

- **P2 static registry** (separate implementation bridge thread; design GO at `-006`).
- **P2.5 verification spike machinery** (separate implementation bridge thread; design GO at `-004`; live spike RUN owner-approval-gated).
- **P3 invoker / autonomous behavior** (gated on P2.5 spike report; not implementable yet per umbrella `-007 §3.3`).
- **CLI surface** (`gt bridge-trigger reset --bootstrap` / `--replay-existing`) — deferred to umbrella P5 per `-003 §3.7`. P1 implementation exposes Python API only; CLI wiring is a separate slice.
- **Notifications, harness invocation, or any side-effect outside `~/.gtkb-state/`** — explicitly excluded by `-003 §1` and `§2`.
- **Modifications to existing `bridge/` module files** (`poller.py`, `worker.py`, `launcher.py`, `runtime.py`, `context.py`, `handshake.py`). Those are the OLD poller / unrelated infrastructure; P1 adds new modules alongside them without touching existing code.

### 1.3 Path resolution under isolation completion contract

Per `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` and the GT-KB isolation completion plan (`gtkb-isolation-completion-plan-2026-04-28-010` GO), GT-KB platform code currently lives at `groundtruth-kb/src/groundtruth_kb/` (pre-Phase-2-restructure path). This is a transient location; Phase 2 of the isolation plan will mechanically relocate it to `src/groundtruth_kb/`. P1 implementation lands at the current pre-Phase-2 path; Phase 2's import-path rewrites pick it up automatically.

State directory (`~/.gtkb-state/` per `-003 §2`) — during Phase 4 of the isolation plan, this will likely become a platform-rooted subdirectory (`E:\GT-KB\.gtkb-state\` or similar). P1 implementation uses `pathlib.Path.home() / ".gtkb-state"` for compatibility with current workflows; the path will be parameterizable via env var `GTKB_STATE_DIR` to support the future relocation without code change.

## 2. Pre-Execution Analysis

### 2.1 Existing `bridge/` module inventory (verified)

```
groundtruth-kb/src/groundtruth_kb/bridge/__init__.py          (48 LOC; small re-export stub)
groundtruth-kb/src/groundtruth_kb/bridge/context.py           (1186 LOC; OLD poller context)
groundtruth-kb/src/groundtruth_kb/bridge/handshake.py         (211 LOC; OLD handshake)
groundtruth-kb/src/groundtruth_kb/bridge/launcher.py          (365 LOC; OLD launcher)
groundtruth-kb/src/groundtruth_kb/bridge/poller.py            (694 LOC; OLD poller)
groundtruth-kb/src/groundtruth_kb/bridge/runtime.py           (1642 LOC; OLD runtime)
groundtruth-kb/src/groundtruth_kb/bridge/worker.py            (1012 LOC; OLD worker)
```

These are existing modules from the OLD poller architecture (halted S308). P1 implementation ADDS detector.py, checkpoint.py, routing.py, audit.py alongside without modifying any existing file. `__init__.py` is the only existing file modified — to add public API exports for the new modules.

### 2.2 Test infrastructure inventory

`tests/scripts/` is the test directory used by the release-candidate gate (`scripts/release_candidate_gate.py`). New test modules will follow the existing convention (`test_<feature>_<aspect>.py` with pytest functions).

`tests/fixtures/` — checking whether this exists or needs creation. (Will verify during implementation.)

### 2.3 Live INDEX shape (source-verified per `-003 §1`)

```
$ grep -cE "^<!--|^-->" bridge/INDEX.md       # historical comment line count
$ grep -nE "<!--$|^-->$" bridge/INDEX.md      # multi-line comment block boundaries
$ python -c "<refs / missing-refs check>"     # 490 refs, 87 missing
```

Original counts from `-003`: 3 multi-line comment blocks (lines 379-392, 455-464, 519-534), 490 total bridge file refs, 87 missing-on-disk. **Note:** these line numbers were valid as of S315 (2026-04-27); the live INDEX has changed since (this S319 session added at least 2 new document entries plus iteration versions). The frozen snapshot fixture (`tests/fixtures/bridge_index_live_snapshot.md`) captures whatever shape is current at implementation time, regardless of line-number drift.

### 2.4 No-touch verification

Existing `bridge/` source files modified in working tree (per `git status`):
```
M groundtruth-kb/src/groundtruth_kb/bridge/handshake.py
M groundtruth-kb/src/groundtruth_kb/bridge/launcher.py
M groundtruth-kb/src/groundtruth_kb/bridge/poller.py
M groundtruth-kb/src/groundtruth_kb/bridge/worker.py
```

These modifications are from prior-session work (likely S318 or earlier), NOT P1 implementation. Per §1.2 out-of-scope rule, P1 implementation does NOT add to or interact with these modifications. They remain part of the broader session-hygiene work that the GT-KB isolation Phase 1 plan (separate thread) flagged as out-of-its-scope; they will be addressed in a separate session-hygiene bridge thread.

## 3. Execution Plan (Commit Sequence)

Five commits total, each self-contained and independently revertable:

| # | Commit | Files | LOC estimate |
|---|---|---|---|
| 1 | "smart-poller P1: add detector module + tests" | `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` + `tests/scripts/test_bridge_detector.py` + `tests/fixtures/bridge_index_live_snapshot.md` | ~150 src + ~250 test + ~600 fixture |
| 2 | "smart-poller P1: add checkpoint module + tests (bootstrap mode + corrupt-recovery)" | `groundtruth-kb/src/groundtruth_kb/bridge/checkpoint.py` + `tests/scripts/test_bridge_checkpoint.py` | ~80 src + ~120 test |
| 3 | "smart-poller P1: add routing module + tests (TransitionOutcome enum)" | `groundtruth-kb/src/groundtruth_kb/bridge/routing.py` + `tests/scripts/test_bridge_routing.py` | ~70 src + ~80 test |
| 4 | "smart-poller P1: add audit module + tests" | `groundtruth-kb/src/groundtruth_kb/bridge/audit.py` + `tests/scripts/test_bridge_audit.py` | ~70 src + ~80 test |
| 5 | "smart-poller P1: wire __init__ exports + release-candidate gate integration" | `groundtruth-kb/src/groundtruth_kb/bridge/__init__.py` (modified) + `scripts/release_candidate_gate.py` (modified to include the new test modules) | small |

After commit 5, run the full release-candidate gate locally to confirm the new tests pass alongside existing tests. Post-implementation report at `-002` of this thread captures the gate output.

**Per-commit acceptance:** each commit's tests must pass before moving to the next. If commit N's tests fail in CI / locally, halt and report rather than continuing.

## 4. Phase 1 Detector Implementation Acceptance Criteria

Per design `-003 §4.1`/`§4.2`:

1. `ParseResult.documents` non-empty (≥56 documents at current INDEX size).
2. `ParseResult.errors == ()` against the live INDEX snapshot — no truly malformed lines.
3. `ParseResult.warnings` may contain `referenced_file_missing` entries (currently ~87 expected) — acceptable.
4. The 3 multi-line HTML comment blocks (per S315 line numbers; live snapshot at implementation time will pin actual offsets) are consumed silently — neither errors nor warnings.
5. Bootstrap mode emits zero routable transitions on first run.
6. Corrupt-checkpoint recovery is treated as bootstrap mode (no transitions emitted, audit warning logged).
7. CRLF line endings, UTF-8 BOM, trailing whitespace all tolerated without parse errors.
8. All 32-38 tests pass per `-003 §4.1` test list.
9. Release-candidate gate wires the new test modules and they run in the standard suite.

## 5. Risks and Reversibility

### 5.1 Risk: New module surface introduces import or API instability

**Mitigation:** all new modules are leaf modules (no imports from other `bridge/` files except what's needed for type composition). `__init__.py` exports are additive (no existing exports renamed or removed). If a leaf module proves problematic, that single commit can be reverted without affecting others.

### 5.2 Risk: Live INDEX regression test churns on every INDEX change

**Mitigation:** the test asserts shape properties (parse succeeds, errors empty, warnings tolerate missing refs) rather than specific line numbers or document counts. The frozen snapshot fixture is updated only when INDEX format itself evolves (rare); document additions don't break the test.

### 5.3 Risk: Path-resolution issues for `~/.gtkb-state/` on Windows

**Mitigation:** use `pathlib.Path.home() / ".gtkb-state"` consistently; accept env var override `GTKB_STATE_DIR` for test isolation and future relocation. Verify on Windows during implementation (current platform is Windows 11).

### 5.4 Risk: Test fixture (`bridge_index_live_snapshot.md`) becomes stale

**Mitigation:** the snapshot is captured at implementation time. If INDEX format evolves later in a way that breaks parsing, the test surfaces it. Fixture refresh is a separate small bridge thread when needed (no auto-update; we want explicit human review of any format change).

### 5.5 Reversibility summary

Each commit is independently revertable. No existing code is modified except `__init__.py` (additive exports) and `release_candidate_gate.py` (additive test wiring). Full P1 revert is `git revert <commit-1>..<commit-5>` with no cascading impact on existing `bridge/` modules.

## 6. Codex Review Asks

1. **Module location** — confirm landing the new modules at `groundtruth-kb/src/groundtruth_kb/bridge/` (pre-Phase-2 path) is correct, and that Phase 2 isolation file moves will pick them up automatically without P1 needing to anticipate the move.

2. **No-touch boundary** — confirm §1.2's exclusion of existing `bridge/` modules (`poller.py`, `worker.py`, etc.) is the right boundary, and that the in-flight `git status` modifications to those files are correctly out of P1 scope.

3. **State-directory path** — confirm `pathlib.Path.home() / ".gtkb-state"` with `GTKB_STATE_DIR` env override is the right resolution model. Per S319 owner directive that the smart poller should be ready to use, future Phase 4 platform-rooting can change the default without code rework if env override is in place.

4. **Per-commit acceptance** — confirm §3's five-commit sequence with per-commit-test-pass gating is the right granularity vs. larger commits. The benefit is fine-grained revertability; the cost is more commit messages.

5. **Live INDEX snapshot fixture** — confirm capturing the snapshot at implementation time (vs. pinning specific line numbers from `-003 §1`'s S315 source-verify) is appropriate. The implementation-time snapshot may have different counts but will still satisfy the design's shape assertions.

6. **Acceptance criteria completeness** — confirm §4's 9 acceptance criteria cover the design's GO conditions. Flag any criterion implied by `-003` that I've missed.

A NO-GO with specific findings remains more valuable than a fast GO. P1 is the foundation for P2/P2.5/P3; getting it precisely right at implementation time prevents reopening for later issues.

## 7. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact. It records the P1 implementation contract for Codex review. The five commits described in §3 occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
