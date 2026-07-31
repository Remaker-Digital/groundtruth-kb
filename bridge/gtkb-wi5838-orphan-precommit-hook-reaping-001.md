NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5838-orphan-precommit-hook-reaping
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5838

target_paths: ["groundtruth-kb/src/groundtruth_kb/governance/parent_liveness.py", "scripts/ops/gate_orphan_reap.py", "config/governance/gate-parent-liveness.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_gate_parent_liveness.py", "platform_tests/scripts/test_gate_orphan_reap.py"]
implementation_scope: gate_parent_liveness_self_exit_and_orphan_reaping_sweep
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5838 Implementation Proposal — Parent-Liveness Self-Exit and Orphan Reaping for Pre-Commit Gate Children

## Summary

A pre-commit gate child that outlives its dead parent `git commit` process converts a single failed commit into an installation-wide bridge-publication outage, because the orphan continues to acquire and hold the one global control-plane lock while every peer publication hard-fails on a bounded acquisition timeout. No mechanism today checks parent liveness inside the gate child, and no sweep reclaims a hold that an abandoned child is still taking. This proposal adds (a) a stdlib-only, PID-reuse-immune parent-liveness watchdog that the control-plane-touching gate arms for the duration of its run and that exits the process promptly once the parent is gone, and (b) a protect-by-default orphan-detection sweep plus a doctor check that surfaces any surviving orphaned gate child with an explicit, owner-invoked reclaim path. Lock acquisition, ordering, exclusivity, and timeout semantics are untouched: the orphan's exit is what reclaims the lock, because the kernel releases an advisory file lock when its holder exits.

This proposal is filed as the first numbered bridge file `bridge/gtkb-wi5838-orphan-precommit-hook-reaping-001.md`, opening an append-only versioned bridge file chain. No prior version exists and none is deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

Every claim below was re-derived this session from the live worktree at HEAD `8a35eabc8`, the code of record, and a fresh `gt backlog show WI-5838 --json`. Line numbers are current-worktree references.

1. **The incident.** Per the WI-5838 record (`source_owner_directive` OWNER-TRANSCRIPT-20260731-SUBAGENT-IMPLEMENTATION-MANDATE, finalization root-cause diagnosis 2026-07-31): during the wi5827 VERIFIED finalization failure, pre-commit hook child PID 6688 (`check_protected_commit_authorization.py --staged`) outlived its dead parent `git commit` process PID 34760 by roughly 11 minutes, consuming about 320 CPU-seconds and holding `.gtkb-state/sot-registry/control-plane.lock` for its life. Concurrent bridge publications across the installation were denied with "timed out acquiring registry lock".

2. **One global lock, bounded wait, hard failure.** `RegistryPaths.resolve` pins a single installation-wide lock at `.gtkb-state/sot-registry/control-plane.lock` (line 250). `_RegistryFileLock` (line 254) is an exclusive advisory file lock with a default 30-second acquisition deadline (line 255); on expiry it raises `TimeoutError("timed out acquiring registry lock ...")` (line 283) rather than queueing. Nineteen call sites take that lock, including `load_registry_snapshot` (lines 824, 837). A single long holder therefore does not slow peers down — it fails them outright.

3. **The gate is a lock consumer.** `scripts/check_protected_commit_authorization.py` imports `load_registry_snapshot` from `groundtruth_kb.project.registry_control_plane` (line 2130) and is invoked by the live hook. `git config core.hooksPath` resolves to `.githooks`, and `.githooks/pre-commit` line 32 runs `"$PYTHON_BIN" scripts/check_protected_commit_authorization.py --staged`. Of the five Python gates in that hook, this is the **only** one that references the control plane at all (verified by direct scan: `scan_secrets.py`, `check_dev_environment_inventory_drift.py`, `check_narrative_artifact_evidence.py`, and `check_ruff_format.py` each have zero references). The fleet-wide-publication harm class is therefore precisely scoped to one gate.

4. **No parent-liveness check anywhere in the gate path.** `.githooks/pre-commit` spawns each gate as a plain foreground child and returns its exit code; nothing in the hook or in the gate observes whether the invoking `git` process still exists. A `git` process that dies — killed, timed out by a harness, or terminated with its terminal — leaves the child running to completion with no signal that its work has become pointless.

5. **The lock record carries no holder identity.** The lock file is initialized with a single byte `b"0"` (lines 264-266) and never records a holder PID, session id, or acquisition timestamp. A "lock-ownership sweep" therefore cannot validate ownership by reading the lock; there is no holder metadata to validate against. This is a load-bearing constraint on the design below: the sweep must identify orphans by process ancestry, not by lock introspection.

6. **There is no stale lock file to clean.** Because `_RegistryFileLock` uses `msvcrt.locking` on Windows (line 274) and `fcntl.flock` on POSIX (line 278), the kernel releases the lock when the holding process exits, whether or not `__exit__` ran. The residue is a live process, not a file. This is why the correct remedy is to make the orphan exit — and why doing so requires no change to lock semantics at all.

7. **Ongoing, not historical.** Concurrent workers in this same program recorded control-plane lock-timeout contention during both proposal filings and test execution this session; a 210-test suite could not complete because every protected-path check serialized on that single lock. The contention surface that the incident saturated is under load right now.

8. **`.githooks/pre-commit` cannot be a target path.** `classify_target(".githooks/pre-commit")` returns `unclassified` (extension-less, and `.githooks` is in none of the classifier's first-segment sets — `project_authorization_operation_time.py` lines 160-229). `evaluate_envelope` denies any target whose class is outside `allowed_mutation_classes` with `target_mutation_class_not_allowed` (lines 336-340), and `unclassified` is in no PAUTH's allowed set. Declaring the hook script would make `implementation_authorization.py begin` fail closed. The design below consequently requires **no edit to `.githooks/pre-commit`**; every behavior change lives in Python files that classify as `source`, `configuration`, or `test` (verified individually this session).

## Proposed Design

Three slices. Two new modules, one new config file, one new doctor check, and exactly one call-site line added to the incident actor.

### Slice A — Parent-liveness watchdog with prompt self-exit

New module `groundtruth-kb/src/groundtruth_kb/governance/parent_liveness.py`, stdlib-only (`psutil` is not a project dependency; verified against both `pyproject.toml` files). Public surface: `arm_parent_liveness_watchdog(*, config=None) -> ArmResult` and a pure, testable `parent_state(probe) -> ParentState` decider.

**Windows mechanism.** At arm time — while the parent is still alive — the watchdog calls `kernel32.OpenProcess(SYNCHRONIZE, FALSE, ppid)` through `ctypes` and retains the handle for the process lifetime. It then polls `WaitForSingleObject(handle, 0)`; a `WAIT_OBJECT_0` result means the parent has exited. Windows performs no reparenting and does not maintain a live parent link, so a PPID comparison is meaningless there and a bare PID probe is vulnerable to PID reuse. Holding the handle is what makes this correct: an open handle keeps the kernel process object alive, so the PID cannot be recycled behind the probe, and the signalled state is an exact, cheap, allocation-free liveness answer.

**POSIX mechanism.** At arm time the watchdog records `os.getppid()`. It then polls for `os.getppid() != original_ppid`: when the parent exits, the child is reparented to init or to the nearest subreaper, so the observed PPID changes. This is the canonical POSIX orphan test and is likewise immune to PID reuse, because the value that changes is the kernel's own parent link rather than a probe against a recyclable identifier. A secondary `os.kill(original_ppid, 0)` probe raising `ProcessLookupError` corroborates the state for subreaper environments where the PPID may be retained.

**Behavior on detection.** The watchdog emits one structured JSONL telemetry record (armed pid, parent pid, observed state, elapsed, exit code) to the configured telemetry path, then terminates the process with `os._exit(<configured orphan exit code>)`. `os._exit` is deliberate rather than incidental: it bypasses `atexit`, `finally`, and interpreter teardown, so a wedged evaluation inside a lock-holding call cannot delay the exit — and, per evidence item 6, the kernel releases the advisory lock at process exit regardless of whether the context manager's `__exit__` ran. The exit is what reclaims the lock; no lock code is touched.

**Fail-open arming.** If the parent handle cannot be opened, or the parent already appears gone at arm time, or the platform probe is unavailable, the watchdog does not arm, records the reason in telemetry, and returns a non-armed `ArmResult`. A gate must never fail because its watchdog could not arm — the gate's own verdict is the safety property, and the Slice B sweep is the backstop. Arming is idempotent, runs on a daemon thread, and is fully suppressed by `GTKB_GATE_PARENT_LIVENESS_DISABLE=1` for debugging.

**Install site.** `scripts/check_protected_commit_authorization.py` calls `arm_parent_liveness_watchdog()` once at the top of `main()`. This is the only gate that acquires the control-plane lock (evidence item 3), so it is the only gate whose orphaning produces the fleet-wide-publication harm class. Extending the arm call to the other four gates is a named follow-on rather than scope creep: they are covered meanwhile by Slice B, and widening the diff would collide further with the in-flight WI-5742 work described in the Coordination section.

### Slice B — Orphan-detection sweep, protect-by-default

New module `scripts/ops/gate_orphan_reap.py`, modelled on the existing pure-decider shape of `scripts/ops/storm_watchdog_reap.py`: a `Process` record of `(pid, ppid, name, command_line, create_time_epoch)`, a component analysis over parent/child edges, and a `decide_gate_orphan_reap(processes, *, now, config) -> ReapDecision` returning `reap`, `protect`, and per-pid `reasons`. Reusing that shape keeps the decider unit-testable from fixture data with no live process interaction, exactly as the storm watchdog's decider is today.

A process is a **candidate** only when all hold: its command line matches the registered gate-script set; its recorded git-root ancestor is absent from the live process list; and its age exceeds the configured minimum. Identity is the `(pid, create_time_epoch)` pair, never the PID alone, so a recycled PID cannot be misattributed. Everything else is protected, and any ambiguity — unresolvable ancestry, unreadable command line, unknown creation time — resolves to protect. The decider can only ever propose terminating a process it has positively identified as an abandoned gate child.

The CLI defaults to `--report`: it writes findings and exits without acting. Reaping requires the explicit `--reap` flag. **No scheduled task, service, hook registration, or other automation substrate is created.** That is a deliberate constraint, not an omission: `.claude/rules/bridge-essential.md` requires owner approval before any new bridge automation substrate, and the governing PAUTH lists `dispatcher_mutation` among its forbidden operations.

New doctor check `_check_orphaned_gate_processes` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` consumes the same decider and reports WARN when an orphaned gate child is observed, naming the pid, its age, and the explicit reclaim command. Detection is continuous and safe; termination stays owner-invoked.

### Slice C — Configuration surface, no hard-coded timer literals

New file `config/governance/gate-parent-liveness.toml` carries every tunable: `enabled`, `poll_interval_seconds`, `arm_grace_seconds`, `orphan_exit_code`, `reaper_min_age_seconds`, and `telemetry_path`. Per DELIB-202667722 all values ship in the most relaxed posture the mechanism tolerates, to be tightened only from observed data.

The code contains no timer, interval, or throttle literal. The loader's sole in-code fallback is one named `_RELAXED_FALLBACK` mapping, used only when the config file is absent (an adopter mid-upgrade), and a test asserts that mapping is exactly equal to the shipped config file's values — so the fallback can never silently diverge into a second, hidden source of truth. Coordination with WI-5806 is recorded below.

### Rejected alternatives

- **Arm the watchdog inside `_RegistryFileLock.__enter__`.** Superficially elegant — it would scope liveness to exactly the lock hold — but it puts new behavior inside the lock class that WI-5715 and WI-5788 are actively reasoning about, and inside a file the in-flight WI-5742 diff already touches. Rejected to keep lock semantics provably untouched.
- **Record a holder PID in the lock file so a sweep can validate and clear stale ownership.** This is the shape the WI's "lock-ownership sweep" phrase suggests, but per evidence item 6 there is no stale lock file to clear: the kernel releases the lock at process exit, so a holder record would be write amplification with no reclaim power, and writing into the lock file changes lock-record semantics. Rejected; the holder-metadata question is deferred to the WI-5715 / WI-5788 lane where lock semantics are in scope.
- **Wrap the gates in a supervisor invoked from `.githooks/pre-commit`.** Requires editing an `unclassified` target path that fails `begin` closed (evidence item 8), and puts the liveness logic in Bash where the Windows mechanism is unavailable. Rejected.
- **A scheduled reaper task.** Creates a new automation substrate without owner approval and touches a forbidden operation class. Rejected in favor of the doctor check plus explicit CLI.
- **Bound the gate's runtime instead.** That is WI-5742's job, and it is a different failure mode: a bound limits how long a gate may run, while this work addresses a gate whose parent has died — which is wrong at any duration, including well inside any bound.
- **Depend on `psutil`.** Not a current dependency; adding one for a probe that `ctypes` and `os` already answer exactly is unjustified. Rejected.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — the source spec recorded on WI-5838, and the append-only numbered bridge chain authority under which this thread is filed; the defect's harm is denial of governed bridge publication.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain; the PAUTH triple in this header proceeds under it, and evidence item 8 is a direct consequence of its operation-time target classification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-Derived Verification Plan below is the derivation record the Loyal Opposition verifier executes against.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is created, updated, or retired by this work; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root, under scripts, groundtruth-kb/src, config, and platform_tests; no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the pre-commit gate chain is the write-time layer of the two-layer defense; this work keeps that layer from converting its own failure into a platform-wide denial.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence here derives from fresh canonical reads made this session against the live worktree, the code of record, and MemBase.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — orphan detection becomes a deterministic decider plus doctor surface instead of recurring manual process triage after each finalization failure.
- `GOV-RELIABILITY-FAST-LANE-001` — advisory — a bounded, evidence-backed reliability defect fix on a P1 work item.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes such as observed exit, elapsed bound, and lock reacquisition, not structural presence of a function.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the telemetry record and the doctor finding are durable evidence artifacts rather than transient session state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability from WI-5838 through TEST-11789 to the implementation and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions for WI-5838 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5838 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667722`, `DELIB-202667721`, `DELIB-202667734`, `DELIB-202667730`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with role-transition plan: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667722** — Timer and throttle governance is a first-class concern: relaxed-first bias, registry visibility, no hard-coded values, recurring tuning. Slice C is authored directly against this directive, and the WI-5806 coordination note records the migration path.
- **DELIB-202667721** — Owner decision recorded as the `owner_decision_deliberation_id` of PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730: the list-free whole-project grant under which WI-5838 is authorized as a member work item.
- **DELIB-202667734** — Owner decision authorizing the v2 schema-shape repair of that same authorization; v2 is the active version this proposal cites.
- **DELIB-202667730** — Harness Test final synthesis: the consolidated diagnosis stream from which the 2026-07-31 finalization-failure evidence for this defect was drawn.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase (`groundtruth.db`); every cited code line reference was verified by direct read of the current worktree.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate authorizes this worker to file this NEW proposal for WI-5838. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667721 and DELIB-202667734** — the owner's list-free whole-project grant, recorded as PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 v2 (status active, no expiry, no work-item allowlist), covers WI-5838 as a member of PROJECT-GTKB-HOUSEKEEPING-HARDENING. Per that authorization's scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. **DELIB-202667722** — the owner's timer-governance directive is the standing authority for Slice C's configuration-only, relaxed-first posture. No further owner decision is required for the shipped values; tightening them later is the recurring-tuning activity that directive establishes.
4. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5838 defect description (fresh-read verified via `gt backlog show WI-5838 --json`), its linked test record TEST-11789, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, and the DELIB-202667722 timer-governance directive fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11789` is the spec-derived anchor created with WI-5838 per GOV-12. Its recorded expected outcome is the end-to-end acceptance statement this plan is built to demonstrate: *when the parent git process terminates during a long pre-commit gate, the gate child detects the lost parent, exits promptly, and releases the control-plane lock; a concurrent bridge publication that was blocked proceeds without a manual intervention.* The anchor test below reproduces exactly that sequence rather than asserting the mechanism's internals.

New modules: `platform_tests/scripts/test_gate_parent_liveness.py` and `platform_tests/scripts/test_gate_orphan_reap.py`. All timing in tests is driven by test-local config overrides through the Slice C loader; no test embeds a timer literal.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11789 / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_orphaned_lock_holder_exits_and_unblocks_peer` | End-to-end anchor: a synthetic parent spawns a child that acquires the control-plane lock and blocks; a second process attempts acquisition and is blocked; the parent is terminated; the child self-exits within the configured bound with the configured orphan exit code; the blocked acquirer then succeeds with no manual intervention |
| TEST-11789 (prompt exit) | `test_watchdog_exits_within_configured_bound` | Observed elapsed time from parent death to child exit is within the configured poll interval plus tolerance, on the running platform |
| WI-5838 (Windows mechanism) | `test_windows_handle_probe_detects_dead_parent`, `test_windows_handle_pins_pid_against_reuse` | The retained `SYNCHRONIZE` handle reports `WAIT_OBJECT_0` after parent exit, and a recycled PID cannot cause a false negative; skipped off-Windows |
| WI-5838 (POSIX mechanism) | `test_posix_reparent_detected`, `test_posix_kill0_corroborates` | Reparenting changes the observed PPID and is detected; the `ProcessLookupError` probe corroborates; skipped off-POSIX |
| WI-5838 (fail-open arming) | `test_arm_failure_is_non_fatal`, `test_disable_env_suppresses_arming` | An unopenable parent handle, an already-dead parent at arm time, and the disable env var each leave the gate running normally with a non-armed result and a telemetry reason recorded; the gate's own exit code is unchanged |
| WI-5838 / GOV-FILE-BRIDGE-AUTHORITY-001 (no semantic change) | `test_lock_semantics_unchanged` | With the watchdog armed and the parent alive, acquisition order, exclusivity, blocking behavior, and timeout behavior of `_RegistryFileLock` are byte-for-byte identical to the unarmed baseline; no lock-file content is written by this work |
| WI-5838 (sweep decider) | `test_dead_git_root_orphan_is_reapable`, `test_live_parent_gate_is_protected`, `test_young_orphan_is_protected`, `test_non_gate_process_is_protected`, `test_unresolvable_ancestry_is_protected`, `test_pid_reuse_not_misattributed` | Fixture-driven decider: only a positively identified abandoned gate child older than the configured minimum is reapable; every ambiguity resolves to protect; identity is the pid and creation-time pair |
| WI-5838 (no new substrate) | `test_report_is_default_and_reap_requires_flag` | The CLI takes no action without `--reap`; the diff registers no scheduled task, service, or hook |
| WI-5838 (doctor surface) | `test_doctor_warns_on_orphaned_gate_child`, `test_doctor_clean_when_none` | The doctor check reports WARN naming the pid, age, and reclaim command when an orphan is present, and passes otherwise |
| DELIB-202667722 / GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 | `test_config_is_sole_source_of_values`, `test_relaxed_fallback_matches_shipped_config` | Every tunable resolves from `config/governance/gate-parent-liveness.toml`; the single named in-code fallback mapping equals the shipped file exactly; a scan of the new modules finds no timer literal |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` both pass clean on every changed Python file (separate gates).
2. `python -m pytest platform_tests/scripts/test_gate_parent_liveness.py platform_tests/scripts/test_gate_orphan_reap.py -q --tb=short` passes green on Windows, with platform-specific cases skipped rather than failed on the non-matching platform.
3. The existing `platform_tests/scripts/test_check_protected_commit_authorization.py` suite remains green; the gate's verdicts, exit codes, and output are unchanged when the parent is alive.
4. The TEST-11789 anchor test demonstrates the full recorded outcome: parent death, prompt child exit, lock release, and a previously blocked acquirer proceeding without manual intervention.
5. `groundtruth-kb/tests/test_registry_control_plane.py` remains green, and the diff contains no change to lock acquisition, release, ordering, exclusivity, or timeout behavior.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals, and registers no new scheduled task, service, daemon, or hook.
7. `gt project doctor` runs clean on a healthy tree and reports the new WARN with a reclaim command when an orphaned gate child is present.
8. No file under `.githooks/` is modified.

## Risk And Rollback

- **False-positive self-exit.** A watchdog that misreads a live parent as dead would abort legitimate commits. Mitigated by mechanisms chosen specifically for exactness: a retained kernel handle on Windows and the kernel's own parent link on POSIX, both immune to PID reuse; corroborating probes; and a configured grace before the first evaluation. The `test_lock_semantics_unchanged` and gate-suite criteria pin the alive-parent path to unchanged behavior.
- **Over-reaping.** Mitigated by protect-by-default in the decider, positive gate-script identification, creation-time-paired identity, a configured minimum age, report-only default, and explicit-flag termination.
- **`os._exit` skipping cleanup.** Deliberate. There is no cleanup the orphan can usefully perform, and per evidence item 6 the lock is kernel-released at exit. Buffered telemetry is flushed before the call.
- **Watchdog overhead.** One daemon thread performing a zero-timeout kernel probe per configured interval; negligible against the ~320 CPU-seconds the incident orphan burned.
- **Concurrent-edit risk.** `scripts/check_protected_commit_authorization.py` is being modified right now by the in-flight WI-5742 implementation; see the Coordination section for the sequencing constraint and rebase baseline.
- **Rollback** is the exact revert of one call-site line plus deletion of the new modules, config file, doctor check, and test modules. Nothing under `bridge/`, no MemBase record, no dispatcher/TAFE state, and no lock file is touched, so revert restores the prior behavior exactly.

## Coordination

- **WI-5742 (GO'd at `bridge/gtkb-wi5742-bound-protected-commit-evaluation-002.md`, keystone) — complementary, sequenced.** WI-5742 bounds how long the protected-commit evaluation may *run*; WI-5838 addresses what happens when the *parent dies*, which is wrong at any duration and would remain wrong inside a perfectly enforced bound. The boundary is crisp: duration versus abandonment. Target paths are disjoint except for one file. WI-5742's declared set is `scripts/check_protected_commit_authorization.py`, `scripts/controlled_artifact_paths.py`, `scripts/implementation_authorization.py`, `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`, `config/governance/protected-commit-timers.toml`, and three test modules. WI-5838 shares only `scripts/check_protected_commit_authorization.py`, and touches it with a single `arm_parent_liveness_watchdog()` call at the top of `main()`. That overlap is unavoidable and deliberate: per evidence item 3 this is the only control-plane-touching gate, so installing the watchdog anywhere else would leave the incident actor unprotected. **Rebase baseline:** HEAD `8a35eabc8`, with `scripts/check_protected_commit_authorization.py` and `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` both currently modified in the worktree by the in-flight WI-5742 implementation, and WI-5742's `timer_config.py` and `protected-commit-timers.toml` not yet present on disk. WI-5838 implementation MUST be sequenced strictly after WI-5742 lands through its own governed cycle; the implementing session re-baselines the `main()` line reference before editing and records the re-baseline in the implementation report.
- **WI-5715 and WI-5788 — lock semantics are out of scope here.** WI-5715 covers scaling coherent registry authority reads for parallel workloads; WI-5788 covers the 30-second acquisition timeout causing hard filing failures under sustained concurrency. WI-5838 changes no lock semantics whatsoever: not acquisition, not release, not ordering, not exclusivity, not the timeout, and not the lock record. It only causes an abandoned holder to exit, after which the kernel reclaims the hold. Acceptance criterion 5 makes that a verified property rather than an assurance. The holder-metadata question surfaced in evidence item 5 is explicitly handed to that lane rather than resolved here.
- **WI-5819 — sibling residue, cross-linked not absorbed.** WI-5819 covers detecting and remediating a stale zero-byte `.git/index.lock`, a downstream residue of this same 2026-07-31 incident. The two are genuinely different: `.git/index.lock` is a filesystem artifact that survives its creator and must be removed, whereas the control-plane lock is a kernel advisory lock that cannot go stale and has nothing to remove. The shared surface is the doctor: WI-5819 adds stale-index.lock detection, WI-5838 adds orphaned-gate-child detection. Neither absorbs the other, and a future consolidation of incident-residue doctor checks would be its own work item.
- **WI-5583 — similar shape, not a duplicate.** WI-5583 covers reaping orphaned Codex Desktop git *probe* processes under PROJECT-GTKB-GOOSE-HARNESS-ADOPTION. The distinctions are material and should prevent any merge: different producer (harness desktop integration versus the git pre-commit hook chain); different resource profile (CPU-idle probes versus a CPU-burning evaluation at roughly 320 CPU-seconds); different lock involvement (no `.git/index.lock` and no control-plane lock, versus a control-plane lock hold that denies fleet-wide publication); and different remedy surface (harness process hygiene versus gate-child parent liveness). The decider introduced here is deliberately shaped like `scripts/ops/storm_watchdog_reap.py` so that if the owner later chooses to unify the reaping surfaces, the two deciders compose rather than conflict.
- **WI-5806 — timer externalization, aligned.** WI-5806 externalizes hard-coded timer values to the canonical configuration store with relaxed-first defaults. WI-5838 introduces no hard-coded timers and ships its tunables in a dedicated config file precisely so it adds nothing for WI-5806 to clean up. If WI-5806 designates a single canonical timer store, this work's keys migrate into it under WI-5806's own cycle; WI-5838 does not pre-empt that decision by writing into WI-5742's `config/governance/protected-commit-timers.toml`, which would also create a target-path collision.
- **Live contention.** Evidence item 7 records that this session's concurrent workers hit control-plane lock timeouts during both filings and test execution, including a 210-test suite that could not complete. This is the motivating condition, not a historical footnote.

## DISARM — KB Mechanics

This work performs no MemBase mutation. It creates and modifies source, configuration, and test files only. No specifications, ADRs, DCLs, GOV records, work items, tests, or Deliberation Archive entries are created, updated, or retired. The `kb_mutation_in_scope: false` flag accurately reflects that scope; every artifact ID cited in this proposal is a read-only reference.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5838-orphan-precommit-hook-reaping`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple in this header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself. Every declared target path was classified this session and resolves to source, configuration, or test — all within the authorization's allowed mutation classes.

## Recommended Commit Type

Recommended commit type: fix — repairs a P1 reliability defect in which a died-parent commit converts into an installation-wide publication outage, with regression coverage. The new modules are remediation plumbing for that defect class, not a new capability surface.

## Loyal Opposition Review Questions

1. Is confining the Slice A arm call to `scripts/check_protected_commit_authorization.py` the right scope, given it is the only control-plane-touching gate, or should the remaining four pre-commit gates be armed in this work item despite the wider diff and the WI-5742 collision surface?
2. Is `os._exit` with a distinct exit code the right termination for an orphan, or should the watchdog attempt a graceful unwind first at the cost of a wedged evaluation potentially delaying lock release?
3. Are the protect-by-default conditions in the Slice B decider sufficient, or should reaping additionally require a corroborating telemetry record from an armed watchdog before a process is ever eligible?
4. Is the deferral of holder metadata in the lock record to the WI-5715 / WI-5788 lane correct, or does the sweep need holder identity to be trustworthy?
5. Does the TEST-11789 anchor test, which reproduces the recorded expected outcome end to end, satisfy the spec-derived testing requirement for every linked specification?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
