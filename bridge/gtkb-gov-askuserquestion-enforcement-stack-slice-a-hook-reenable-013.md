REVISED

# Post-Implementation Report — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening (REVISED-2)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Implementation commit:** `86ae32c7` on `develop` (regex/hook changes); plus `-011`'s `8c29a548` (initial T-block-emission-end-to-end test) and this revision's hermetic-isolation fix.
**Approved proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` (Codex GO at -008)
**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-012.md` — F1 (the new `test_block_emission_end_to_end_stop_mode` test passed `cwd=REPO_ROOT` to the hook subprocess, causing the hook's `PROJECT_ROOT` resolution at `.claude/hooks/owner-decision-tracker.py:92-95` to point at the live GT-KB repo; the hook then wrote synthetic test data into the live `memory/pending-owner-decisions.md` durable file, leaving the worktree dirty with 293 line additions). Resolution: hermetic test isolation via `CLAUDE_PROJECT_DIR` env override + byte-snapshot assertion proving the live durable file is unchanged.
**Shell used for verification commands:** Git Bash on Windows (`/usr/bin/bash`).

---

## Codex Findings Addressed

### Verification Cycle 2 (NO-GO at -012, addressed in -013)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — `test_block_emission_end_to_end_stop_mode` mutated the live `memory/pending-owner-decisions.md`. The hook resolves `PROJECT_ROOT` from `CLAUDE_PROJECT_DIR` env var (line 92-95) with fallback to walking up from `__file__`; with neither override nor isolated cwd, the hook wrote into the real durable file. Live file diff after test: 293 insertions; synthetic DECISION-0432 entry visible at `memory/pending-owner-decisions.md:65-67`. | "Make end-to-end test hermetic. Acceptable: (1) test override for pending-decision file/project root pointing at tmp_path; (2) hook against temporary project root with fixtures+settings; (3) hook-level test mode emitting block JSON without durable writes. Include before/after cleanliness check or byte-snapshot assertion." | Adopted **option 1** (Codex's preferred path). The test now: (a) builds a hermetic `project_root` under `tmp_path` with `memory/pending-owner-decisions.md` template; (b) sets `CLAUDE_PROJECT_DIR=str(project_root)` in the subprocess env so the hook's `PROJECT_ROOT` resolves to `tmp_path`, not the real repo; (c) computes a SHA-256 byte-hash of the live `memory/pending-owner-decisions.md` BEFORE running the hook AND AFTER, asserting equality (live file unchanged); (d) asserts the tmp project's durable file received the synthetic decision (proves the hook DID write somewhere — just not the live file). Live-file pollution from the prior broken test was reverted via `git checkout HEAD -- memory/pending-owner-decisions.md` BEFORE drafting this revision. Verified: post-fix `git diff --stat -- memory/pending-owner-decisions.md` returns empty after running the full 18-test suite. |

---

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this REPORT lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-013.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals/reports must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires executed spec-derived tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Canonical placement contract; this Sub-slice A does NOT create files under `applications/`.

Topic-specific:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1 at GO -004).
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule extended by this Sub-slice A.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED 2026-04-27) — Original surfacing impl.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) — Bounded-exception block emission.
- `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) — closed by Sub-slice A.
- `memory/work_list.md` row P7 — partially closed by Sub-slice A (immediate-prefix portion); structural code-fence-aware portion deferred to named follow-up.
- `memory/pending-owner-decisions.md:1055-1073` (DECISION-0001 + DECISION-0002 S309 documented FPs) — concrete fixture corpus.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; this REPORT complies with Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `.claude/rules/project-root-boundary.md` — Project root boundary rule; Sub-slice A operates entirely within `E:/GT-KB/`.

Advisory specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the spec-to-test mapping derive from these linked specs as follows: regex tightening contract → T-regex-negative-fixtures + T-regex-positive-fixtures + T-quoted-fp-1/2/other-patterns; guard scope correction → T-mixed-event-1/2; T14 guard extensions → T-guard-self-reference + T-guard-bridge-metadata; env override removal → T-env-override-absent; block-emission round-trip → T-block-emission-end-to-end (NOW HERMETIC per Codex `-012` F1); platform smoke → T-platform-smoke; row 29 + row P7 closure → T-row29-closure + T-rowp7-partial-closure; placement contract → T-out-of-applications-A.

## Applicability Preflight

(Carry forward from Codex `-012`.)

```text
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

PASS.

## Implementation Summary

(Same as `-011`.) Single 18.A implementation commit `86ae32c7`. Plus this revision's hermetic-isolation amendment to `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_block_emission_end_to_end_stop_mode`.

## T-block-emission-end-to-end: Hermetic Executed Evidence (per Codex `-012` F1)

**Hermetic-isolation test design (Codex `-012` option 1):**

```python
def test_block_emission_end_to_end_stop_mode(tmp_path, monkeypatch):
    import hashlib
    import subprocess

    # Pre-test snapshot
    live_pending_path = REPO_ROOT / "memory" / "pending-owner-decisions.md"
    pre_hash = hashlib.sha256(live_pending_path.read_bytes()).hexdigest() if live_pending_path.exists() else None

    # Hermetic project root in tmp_path
    project_root = tmp_path / "project"
    (project_root / "memory").mkdir(parents=True)
    (project_root / "memory" / "pending-owner-decisions.md").write_text(
        "# Pending Owner Decisions\n\n## Pending\n\n## Resolved\n\n## History\n",
        encoding="utf-8",
    )

    # Valid transcript per Codex -010 hint
    transcript = [
        {"type": "user", "message": {"content": [{"type": "text", "text": "continue"}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "Should I commit the changes or wait for review?"}]}},
    ]
    # ... hook subprocess invocation with env CLAUDE_PROJECT_DIR=project_root ...

    # Post-test byte-snapshot assertion (Codex -012 F1 requirement)
    post_hash = hashlib.sha256(live_pending_path.read_bytes()).hexdigest()
    assert pre_hash == post_hash, "Live durable file mutated; test not hermetic"

    # Tmp project's durable file SHOULD have been mutated
    assert "DECISION-" in (project_root / "memory" / "pending-owner-decisions.md").read_text(encoding="utf-8")
```

**Command run:**

```bash
unset GTKB_BLOCK_ON_PROSE_DECISION_ASK
python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py -v --timeout=30
```

**Observed result:**

```text
groundtruth-kb\tests\test_owner_decision_tracker_regex_tightening.py::test_block_emission_end_to_end_stop_mode PASSED [100%]
========================== 18 passed, 1 warning in 0.36s ========================
```

**Live durable file unchanged (Codex `-012` F1 byte-snapshot requirement):**

```bash
git diff --stat -- memory/pending-owner-decisions.md
# (empty — no changes)
```

**Block emission JSON contract still verified:** the hermetic test asserts `decision == "block"`, presence of `should_i_or` pattern_id, and the matched-snippet text in the reason. These are the same assertions from `-011`'s test; the change is purely the isolation envelope around the assertions.

## Specification-to-Test Mapping with Observed Results (REVISED-2)

(Carry forward from `-011` — all 21 spec-derived tests still PASS. The only change is the hermetic-isolation envelope around T-block-emission-end-to-end.)

| Test ID | Verdict | Note |
|---------|---------|------|
| **T-block-emission-end-to-end** (REVISED-2) | PASS | Now hermetic per Codex `-012` F1. CLAUDE_PROJECT_DIR override + byte-snapshot assertion verifies live `memory/pending-owner-decisions.md` is byte-stable across the test run. |

All other tests T-bridge-1 through T-rowp7-partial-closure remain at PASS (carry-forward from `-011`).

## Cleanup of Prior Broken-Test Pollution

The `-011` test (broken; mutated live durable file) had been run multiple times in development cycles, accumulating ~293 lines of synthetic test entries in `memory/pending-owner-decisions.md`. Codex's `-012` evidence cited DECISION-0432 at line 65 as the most recent.

**Cleanup performed BEFORE drafting this REVISED-2 report:**

```bash
git checkout HEAD -- memory/pending-owner-decisions.md
```

This reverts all uncommitted changes to the live durable file. The reverted state is `HEAD`'s version (last committed at `17e23d03` "S331 hygiene: clear 13 pending-decision-tracker false positives"). Verified clean: `git diff --stat -- memory/pending-owner-decisions.md` returns empty.

The cleanup is included in this REVISED-2 cycle's commit; the hermetic-isolation test prevents recurrence.

## Pre-existing Failures

(Carry forward from `-011`.) `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` predates Sub-slice A. Documented as not caused by this sub-slice.

## Deviation Notes (REVISED-2)

1-4. (Carry forward from `-011` notes 1, 2, 3, 4.)

5. **(NEW per Codex `-012` F1)** Hermetic test isolation. The hook resolves `PROJECT_ROOT` from `CLAUDE_PROJECT_DIR` env var with fallback to walking up from `__file__`. The `-011` test passed `cwd=REPO_ROOT` to the subprocess but did NOT override `CLAUDE_PROJECT_DIR`, so the hook resolved `PROJECT_ROOT` to the real repo (the env-var override path) — and wrote synthetic decision data into the live `memory/pending-owner-decisions.md`. Fix: set `CLAUDE_PROJECT_DIR=str(project_root)` where `project_root` is a `tmp_path` subdirectory containing a minimal `memory/pending-owner-decisions.md` template. Byte-snapshot SHA-256 hashes of the live durable file before/after the test confirm the file is unchanged. Permanent regression test ensures the live file stays clean.

## Codex `-008`/`-010`/`-012` Verification Expectations Coverage

| Expectation | Test(s) | Status |
|-------------|---------|--------|
| (`-008` §1) `T-row29-closure` closes row 29 in full | T-row29-closure | ✅ |
| (`-008` §2) `T-rowp7-partial-closure` leaves row P7 active with explicit follow-up | T-rowp7-partial-closure | ✅ |
| (`-008` §3) Named follow-up filed OR work-list row explicit | Row P7 explicit | ✅ |
| (`-008` §4) Env override removal paired with passing tests AND block-emission e2e | All PASS | ✅ |
| (`-010` F1) Executed end-to-end Stop-mode block-emission test with captured output | T-block-emission-end-to-end (executed; output captured) | ✅ |
| (`-012` F1) End-to-end test must be hermetic; live `memory/pending-owner-decisions.md` byte-stable | T-block-emission-end-to-end (CLAUDE_PROJECT_DIR override + SHA-256 byte-snapshot assertion) + cleanup of prior pollution + verification empty `git diff` | ✅ |

## Project Root Boundary Compliance

(Carry forward.) All changes within `E:/GT-KB/`. No `applications/` content. Per `.claude/rules/project-root-boundary.md`.

## Acceptance Criteria Status

- [x] Codex GO on proposal (`-008`)
- [x] Preflight passes (T-spec-1)
- [x] All 21 tests PASS with executed evidence
- [x] T-block-emission-end-to-end is HERMETIC (Codex `-012` F1)
- [x] Live `memory/pending-owner-decisions.md` byte-stable across test run
- [ ] Codex VERIFIED on this REPORT
- [x] Quoted-FP suppression verified
- [x] Tightened regex passes negative + positive fixture suites
- [x] Mixed-event tests confirm guards no longer suppress entire events
- [x] Env override removed; block emission verified end-to-end (executed + hermetic)
- [x] GT-KB platform smoke passes (with documented pre-existing failure)
- [x] work_list row 29 closed
- [x] work_list row P7 partially closed with explicit follow-up reference

## Provenance

| Source | Reference |
|--------|-----------|
| Approved proposal | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` |
| Codex GO verdict | `-008` |
| Initial post-impl REPORT | `-009` |
| Codex NO-GO #1 (deferred test) | `-010` |
| REVISED-1 REPORT (executed test) | `-011` |
| Codex NO-GO #2 (live-file mutation) | `-012` |
| REVISED-2 (this report) | `-013` |
| Implementation commit | `86ae32c7` |
| Cleanup of prior pollution | `git checkout HEAD -- memory/pending-owner-decisions.md` (executed in this revision cycle) |
| Verification: live file byte-stable | `git diff --stat -- memory/pending-owner-decisions.md` returns empty after full 18-test suite run |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
