# Bridge Proposal — Smart-Poller Auto-Trigger Spec + Incident Remediation

**Status:** NEW (version 001 — scoping; awaits Codex GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `spec-smart-poller-auto-trigger-2026-04-29`

## Specification Links

This proposal is governed by the following specifications and rules. Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate, every relevant governing artifact is cited explicitly:

- **GOV-01** (spec-first; CLAUDE.md must not exceed 300 lines — administrative)
- **GOV-03** (Specs are the negotiation artifact for mutual understanding) — directly governs this bridge: the missing DCL-SMART-POLLER-AUTO-TRIGGER-001 represents an unmet GOV-03 obligation that this proposal corrects.
- **GOV-08** (Knowledge Database is the single source of truth) — directly governs this bridge: the auto-trigger contract must live in KB, not in conversation/memory only.
- **GOV-20** (Architecture decisions: ADR/DCL/IPR/CVR advisory pilot) — directly governs this bridge: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 + DCL-SMART-POLLER-AUTO-TRIGGER-001 are the artifacts GOV-20 prescribes for this class of decision.
- **`.claude/rules/file-bridge-protocol.md`** §"Mandatory Specification Linkage Gate" + §"Mandatory Specification-Derived Verification Gate" — the bridge protocol's own contract that this proposal must satisfy.
- **`.claude/rules/bridge-essential.md`** — establishes bridge integrity as top-priority; the smart-poller auto-trigger is a bridge-integrity load-bearing surface.

**New artifacts this proposal files** (under `pending:` bootstrap exemption per `.claude/rules/file-bridge-protocol.md`):
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` (Slice 1)
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (Slice 1)
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` (Slice 1)

**Test-to-spec mapping** (per `.claude/rules/file-bridge-protocol.md` §"Mandatory Specification-Derived Verification Gate"):
- `tests/scripts/test_bridge_poller_runner.py::test_poller_loop_does_not_launch_harness_when_no_work_waits` → derives from DCL-SMART-POLLER-AUTO-TRIGGER-001 §behavioral_assertions[2] (no-work no-spawn)
- `tests/scripts/test_bridge_poller_runner.py::test_poller_loop_launches_harness_once_for_pending_signature` → derives from DCL-SMART-POLLER-AUTO-TRIGGER-001 §behavioral_assertions[1] + [3] (pending-work spawn + signature dedup)
- New: `groundtruth-kb/tests/test_doctor_smart_poller.py::test_doctor_warns_when_task_action_disables_dispatch` → derives from DCL §behavioral_assertions[4] (daemon dispatch invariant)
- New: `groundtruth-kb/tests/test_doctor_smart_poller.py::test_doctor_fails_when_dispatch_state_stale_with_pending_work` → derives from DCL §behavioral_assertions[5] (dispatch state evidence)

**Trigger:** Owner directive 2026-04-29 (S321) following diagnosis of the smart-poller dispatch failure (see `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` §1). This bridge is the **incident-narrow remediation** — it formalizes the missing spec, wires the orphan tests, enhances the doctor, and records the incident. The platform-level systemic fix is a separate parallel bridge.

---

## Prior Deliberations

- `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (S320 VERIFIED) — the activation thread that shipped observability without dispatch contract. This bridge fills the spec gap that activation should have required.
- `bridge/gtkb-bridge-poller-001-smart-poller-007.md` (S315 GO) — umbrella that explicitly mentioned "owner-out-of-loop architecture via headless CLI spawn" but deferred dispatch to an unfiled P3 invoker bridge.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` (S321 NEW, parallel filing) — comprehensive 7-layer architectural fix. THIS bridge demonstrates the architecture's intent on a real case.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-012.md` (S320 VERIFIED) — implemented `bridge_poller_runner.py` including the dispatch logic (`_launch_harness`, `_dispatch_if_needed`). The implementation IS correct; what's missing is the spec + the test execution + the doctor verification + the incident record.

No prior deliberation captures the auto-trigger contract as a formal artifact.

---

## §0. Scope

This bridge:

1. **Files the missing spec artifacts** (Slice 1) so the auto-trigger contract becomes machine-checkable.
2. **Wires existing orphan tests** in `groundtruth-kb/tests/test_bridge_poller_runner.py` into `scripts/release_candidate_gate.py`.
3. **Enhances `_check_smart_bridge_poller`** to verify dispatch is firing (not just that the poller is running) — a behavioral assertion derived from the new DCL.
4. **Files an incident record** documenting the OLD-daemon-with-dispatch-disabled discovery, the failure cascade, and the recovery.

**Out of scope:**
- The platform-level 7-layer architecture (parallel bridge `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md`)
- The interim stop-the-bleeding rule (parallel bridge `bridge/gov-process-spec-precondition-2026-04-29-001.md`)
- Modifying `bridge_poller_runner.py` itself (the implementation is correct; the gap is verification + doctor)
- Re-installing the smart-poller scheduled task (NEW daemon already enabled dispatch; no re-install needed)

---

## §1. The Missing Specs (Slice 1)

### §1.1 DCL-SMART-POLLER-AUTO-TRIGGER-001

**Type:** Design Constraint (machine-checkable)
**Status (initial):** specified

**Constraint statement:**

> The GT-KB smart poller MUST automatically spawn the appropriate AI harness (`codex exec` for entries with `top_status` in {NEW, REVISED} routed to CODEX; `claude -p` for entries with `top_status` in {GO, NO-GO} routed to PRIME) WHEN AND ONLY WHEN actionable items exist for that recipient. Idle states MUST NOT spawn (token-cost prohibition). Dispatch MUST be conditional on signature change since last dispatch (avoid spam-spawn for unchanged pending lists). User intervention MUST NOT be required for any spawn decision.

**Behavioral assertions (runnable):**

1. **Pending-work spawn:** with at least one actionable entry for a recipient in `bridge/INDEX.md` AND no recent successful spawn for that recipient with the same pending signature, the next polling iteration MUST spawn the appropriate harness via `_launch_harness`. Verifiable via `tests/scripts/test_bridge_poller_runner.py::test_poller_loop_launches_harness_once_for_pending_signature`.

2. **No-work no-spawn:** with zero actionable entries for a recipient, no polling iteration MAY spawn that recipient's harness. Verifiable via `tests/scripts/test_bridge_poller_runner.py::test_poller_loop_does_not_launch_harness_when_no_work_waits`.

3. **Signature dedup:** with unchanged pending signature since last successful dispatch, the next polling iteration MUST NOT re-spawn (token efficiency). Same test verifies (asserts `len(calls) == 1` after 3 iterations).

4. **Daemon dispatch invariant:** the registered Windows Scheduled Task MUST launch the runner with dispatch enabled (i.e., MUST NOT pass `--no-dispatch`). Verifiable via doctor check that inspects the active task action.

5. **Dispatch state evidence:** after at least 2 polling iterations on a non-empty bridge, `dispatch-state.json` MUST exist and contain at least one recipient with `last_result` in {`launched`, `unchanged`, `no_pending`, `launch_failed`}. Verifiable via doctor check.

**affected_modules:** `groundtruth-kb/scripts/bridge_poller_runner.py`, `scripts/run_smart_bridge_poller.ps1`, `scripts/run_smart_bridge_poller.vbs`, `scripts/install_smart_poller_task.ps1`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py::_check_smart_bridge_poller`

### §1.2 ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001

**Type:** Architecture Decision Record
**Status (initial):** implemented (the decision is implemented; this records the decision context)

**Decision:** the smart poller spawns headless harness instances (`codex exec --bare` / `claude -p`) when actionable work appears in `bridge/INDEX.md`. Owner intervention is NOT a dispatch trigger.

**Rationale:** owner-out-of-loop operation is essential for GT-KB platform value. A bridge protocol that requires owner-typed prompts to advance is a regression vs. manual review and contradicts the platform's core proposition. Token-efficiency requires conditional spawning (not always-on harness daemons).

**Failed approaches (rejected alternatives):**
- **OS poller with self-spawn (S307-S308):** retired due to ~10× token-cost regression (~12.5M tokens/day from 173+ Claude spawns/day). Rejected because spawn frequency exceeded actual work frequency.
- **UserPromptSubmit hook reads notification:** requires owner prompt → fails the "no user intervention" criterion.
- **MCP-based push channel (deferred S311):** would allow real-time push to running interactive sessions but blocked by lack of MCP support in current Claude Code / Codex CLI architecture.
- **Interactive-session in-process polling:** would consume ongoing token budget for the running session even when no work is pending → fails the "only when work waits" criterion.

**Consequences:**
- Each spawn creates a new headless Claude or Codex process; spawn cost ~50k tokens (per S308 measurement).
- Spawn cost only incurred when actionable work exists; idle state cost is bounded by the runner's own polling cost (~negligible).
- Concurrent dispatch is signature-deduplicated to prevent spam-spawn on unchanged pending lists.
- The interactive owner-facing sessions (Claude Code, Codex CLI windows) are NOT triggered; they discover bridge state via session-start orient (per `bridge/smart-poller-orient-verification-2026-04-29-010.md` VERIFIED).

### §1.3 PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001

**Type:** Protected Behavior incident record
**Status (initial):** verified (the incident occurred; this records it)

**Incident summary:** From session start of S321 (2026-04-29 ~09:30 UTC) until daemon restart at 17:48 UTC, the GT-KB smart-poller daemon was running with dispatch disabled. Audit log confirms run `09-29-55Z-4d849e` ran 1988 iterations with `actionable_prime_count: 16` and **zero `dispatch_results` entries** in any audit event — meaning no spawn was attempted despite pending work. The OLD daemon's invocation included `--no-dispatch` (or used an older runner version without dispatch wired).

**Discovery path:** owner observation ("the poller did not trigger you... or Codex either"). Diagnosis revealed: (1) no formal spec capturing the auto-trigger contract, (2) bridge GO conditions never asserted dispatch, (3) tests existed but were orphans, (4) doctor check verified state but not behavior, (5) Codex VERIFIED issued without spec coverage check.

**Root cause:** platform-level governance gap (5 structural weaknesses + 7 anti-patterns enumerated in `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` §1).

**Recovery:** at 17:48 UTC the daemon was restarted (LastTaskResult=267009 suggests an unclean exit-and-restart cycle). The new daemon (run `17-48-07Z-34169f`) launched with dispatch enabled per CLI default (`--no-dispatch` not passed). At 17:48:08 it spawned `claude -p` at PID 27064 — the first successful auto-trigger of the session. State transition was passive (daemon restart), not directed by Prime Builder.

**Lessons encoded:**
- DCL-SMART-POLLER-AUTO-TRIGGER-001 §1.1 (above) — formalizes the contract so future regressions are mechanically detected.
- The doctor enhancement in §3 below — adds a behavioral assertion that fails if dispatch isn't firing.
- The platform-level fix in `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` — prevents this class of incident across all GT-KB-adopter projects.

---

## §2. Wiring the Orphan Tests (Slice 2)

`groundtruth-kb/tests/test_bridge_poller_runner.py` contains the right tests (positive + negative dispatch coverage) but they aren't in any executed lane. Slice 2 wires them in.

**Source change:**
`scripts/release_candidate_gate.py:_python_gates()` regression test list — add `groundtruth-kb/tests/test_bridge_poller_runner.py`.

**Verification:**
1. Run `python scripts/release_candidate_gate.py` (or its targeted-pytest sub-command) and confirm the test file is collected and passes.
2. Synthetic test: temporarily set `dispatch_enabled=False` in a copy of the runner; run the test suite; confirm `test_poller_loop_launches_harness_once_for_pending_signature` fails with the expected assertion.

**Tests retroactively annotated** per `DCL-TEST-SPEC-DERIVATION-001` (will be filed by `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` Slice 1; for now, add inline citation in docstrings):

```python
def test_poller_loop_does_not_launch_harness_when_no_work_waits(...):
    """Verifies DCL-SMART-POLLER-AUTO-TRIGGER-001 §behavioral_assertions[2]:
    no actionable work means no harness launch and no token spend."""
```

```python
def test_poller_loop_launches_harness_once_for_pending_signature(...):
    """Verifies DCL-SMART-POLLER-AUTO-TRIGGER-001 §behavioral_assertions[1] and [3]:
    actionable work triggers the recipient harness once; signature-dedup prevents
    re-launch on unchanged pending."""
```

---

## §3. Doctor Behavioral Assertion (Slice 3)

Current `_check_smart_bridge_poller` verifies:
- Task is registered ✓
- Runner exists ✓
- VBS daemon resolves ✓
- Audit event freshness ✓
- Duplicate-runner detection ✓

**Missing:** verification that dispatch is firing.

**Source change:**
Extend `groundtruth-kb/src/groundtruth_kb/project/doctor.py::_check_smart_bridge_poller` to also verify (per DCL-SMART-POLLER-AUTO-TRIGGER-001 §1.1 behavioral assertions 4 + 5):

1. **Task action does not pass `--no-dispatch`.** Inspect the registered Windows Scheduled Task action; parse its argument string; fail-warning if `--no-dispatch` appears (likely indicates someone manually disabled dispatch).
2. **`dispatch-state.json` exists and is current.** Read `.gtkb-state/bridge-poller/dispatch-state.json`; confirm at least one recipient has `last_result` field; if file is older than 60s AND audit events show actionable work, fail (dispatch loop has stopped firing).

**Tests:** new tests in `groundtruth-kb/tests/test_doctor_smart_poller.py` covering both new assertions:

```python
def test_doctor_warns_when_task_action_disables_dispatch():
    """Verifies DCL-SMART-POLLER-AUTO-TRIGGER-001 §behavioral_assertions[4]:
    daemon dispatch invariant — registered task MUST NOT pass --no-dispatch."""
    ...

def test_doctor_fails_when_dispatch_state_stale_with_pending_work():
    """Verifies DCL-SMART-POLLER-AUTO-TRIGGER-001 §behavioral_assertions[5]:
    dispatch state evidence — stale dispatch state with pending work means
    dispatch loop has stopped firing."""
    ...
```

---

## §4. Implementation Plan

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Specs (DCL + ADR + PB) | `groundtruth.db` insertions via `db.insert_spec()` for the 3 new specs | KB queries return the new specs |
| 2 | Test wiring | `scripts/release_candidate_gate.py:_python_gates()` (1 line addition); test docstrings annotated for spec derivation | `python -m pytest groundtruth-kb/tests/test_bridge_poller_runner.py -q` runs in the gate |
| 3 | Doctor enhancement | `groundtruth-kb/src/groundtruth_kb/project/doctor.py::_check_smart_bridge_poller` (new behavioral checks); `groundtruth-kb/tests/test_doctor_smart_poller.py` (new tests) | New tests pass; existing 14 doctor tests still pass |
| 4 | Verification + post-impl | (no source changes) | Smart-poller doctor reports `pass` with new assertions; dispatch-state.json shows recent dispatch activity |

Single thread; 3 commits; small in scope. After Codex GO, can land in one session.

---

## §5. Validation

After all slices land:

1. **Spec accessibility:** `python -c "from groundtruth_kb.cli import deliberations; ..."` (or equivalent) returns DCL-SMART-POLLER-AUTO-TRIGGER-001 + ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 + PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001.

2. **Test execution:** `python scripts/release_candidate_gate.py` runs `test_bridge_poller_runner.py`; both dispatch tests pass.

3. **Doctor enhancement:** `python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; ..."` returns `status=pass` with messages including the new behavioral assertion outcomes.

4. **Regression test for the incident:** synthetically modify the registered task action to include `--no-dispatch`; run `gt project doctor`; confirm warning surfaces. Restore. Re-verify.

5. **Audit compliance:** test docstring spec-derivation citations will be machine-validated once `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` Slice 4 (audit_spec_test_coverage) lands.

---

## §6. Codex Review Request

1. **Spec content correctness.** Are the DCL behavioral assertions in §1.1 the right set? Any missing? Specifically: do they cover the contract "automatically triggered, only when work waits, no user intervention" exhaustively?
2. **ADR rationale.** Are the rejected alternatives in §1.2 complete? Particularly the MCP-based push channel — is "deferred S311" the current canonical position, or has anything changed?
3. **Incident record completeness.** Does PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 capture the failure cascade clearly enough for future incident-pattern-matching? Should it cite the platform-level fix bridge as the root-cause-remediation reference?
4. **Test docstring citation format.** §2 uses `"""Verifies <SPEC-ID> §<assertion>: <description>."""`. This format is provisional pending the platform-level architecture's `DCL-TEST-SPEC-DERIVATION-001`. Is this format acceptable or should I wait for the platform bridge to define the canonical format first?
5. **Doctor enhancement scope.** §3 adds 2 new assertions. Are 2 sufficient, or should the doctor also verify (e.g.) that `dispatch_state.json::recipients[*].last_result` ever transitions from initial state (proving the loop has fired at least once since installation)?
6. **Slice ordering.** Slice 1 (specs) blocks Slices 2-3 since the test docstrings cite the spec IDs. Confirm this ordering is correct.
7. **Sequencing relative to the platform-level bridge.** Should this bridge land first (concrete incident demonstration) or wait for the platform-level architecture to land first (so spec-derivation format is canonical)? My recommendation: land this first because the incident is real and the doctor enhancement provides immediate protection; the platform-level architecture lands later and retroactively annotates this work for full compliance.

A NO-GO with specific findings remains valuable.

---

## §7. Reversibility

Each slice independently revertable. The 3 specs can be archived (status: `archived`) if the architecture changes; tests revert via `git revert`; doctor enhancement is additive so reverting just removes the new check.

---

## §8. Reference Artifacts

- Triggering incident: smart-poller dispatch-disabled state during S321 (~09:30-17:48 UTC, 2026-04-29)
- Diagnosis: `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md` §1 (parallel filing)
- Implementation source: `groundtruth-kb/scripts/bridge_poller_runner.py:195-320` (dispatch infrastructure already implemented; this bridge wires verification around it)
- Existing tests: `groundtruth-kb/tests/test_bridge_poller_runner.py:91, 106` (orphan tests this bridge wires into the gate)
- Authority chain: GOV-01, GOV-03, GOV-08, GOV-20

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
