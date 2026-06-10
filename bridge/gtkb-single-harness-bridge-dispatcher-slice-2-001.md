NEW

# Implementation Proposal — Single-Harness Bridge Dispatcher (Slice 2: Dispatcher Script + Desktop Scheduled Task)

bridge_kind: prime_proposal
Document: gtkb-single-harness-bridge-dispatcher-slice-2
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Parent thread (Slice 1): `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` (Codex VERIFIED).

## Bridge INDEX Canonicalness Evidence (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This bridge artifact is filed under `bridge/` at `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`. The INDEX update inserts a new `Document:` block at the top of `bridge/INDEX.md` (after the header comments) with `NEW: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`. No prior bridge file is deleted or rewritten by this filing.

## Bulk-Operations Clause Scope Clarification (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This proposal is not a bulk operation against the standing backlog. It is a single-thread implementation proposal that builds the Slice 2 dispatcher substrate authorized by the Slice 1 ADR / SPEC / DCL artifacts. DECISION DEFERRED markers:

- DECISION DEFERRED: cross-platform installers (macOS launchd, Linux systemd, cron) are out of scope for this slice; Slice 2 ships Windows Task Scheduler as primary substrate per `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` platform binding. A future slice (or owner directive) ports the installer to other platforms.
- DECISION DEFERRED: MemBase status promotion of Slice 1's `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` and `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` from `specified` to `implemented` is deferred to a follow-on hygiene packet (separate formal-artifact-approval packets required; not in scope here).
- DECISION DEFERRED: dispatcher mode-flag refinements (e.g., per-mode interval overrides; explicit role-set re-resolution at each wake) are deferred to a future Slice 3 if evidence warrants.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory of Slice 2 work.
- review packet: this proposal file IS the review packet.
- formal-artifact-approval packets: no new SPEC/ADR/DCL inserts in this slice (Slice 1 already landed them); Slice 2 produces no new MemBase rows. Narrative-artifact-approval packets are needed for the `.claude/rules/bridge-essential.md` amendment (IP-7) per the operational-mode update.

## Claim

Build the runtime dispatcher substrate the Slice 1 governance scaffolding authorized: a `scripts/single_harness_bridge_dispatcher.py` script that wakes from a Windows Task Scheduler task on a fixed interval (default 5 minutes), reads `bridge/INDEX.md`, computes per-role actionable signatures byte-identically to the cross-harness event-driven trigger's scheme, and spawns subprocess workers via the canonical init-keyword + env-var contract (per `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` + `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`) when (a) the per-role actionable signature has changed and (b) no foreground session lock is held by the active harness.

After Slice 2, an owner in single-harness mode can write a NEW bridge proposal as Prime Builder, close their interactive session, and return later to find Codex/Claude has reviewed it in a fresh subprocess in the LO role — no manual two-session bridge protocol drudgery required.

## Why Now

Slice 1 is VERIFIED. Single-harness operating mode is governed end-to-end at the schema, attribution, doctor, hook, and test layers — but with no dispatcher script and no scheduled task, single-harness owners still must run a manual two-shell bridge protocol (or stay in dual-harness mode). Slice 2 closes that loop.

The Slice 1 ADR (`ADR-SINGLE-HARNESS-OPERATING-MODE-001`) explicitly identifies the dispatcher substrate as a Slice 2 deliverable, and the Slice 1 DCL (`DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`) constrains the substrate to a host-platform scheduled task surface. The shape of the implementation is already governed; this proposal turns the governed contract into a runtime.

## Why Not (alternatives considered + rejected)

1. **In-process timer / daemon spawned by a harness lifecycle hook.** Rejected by `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Excluded Substrates: the dispatcher must survive interactive session termination. This is the lesson encoded by `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` and the retired smart-poller incident class.
2. **Re-enabling the retired smart poller for single-harness mode.** Rejected because the smart poller was retired in Slice 4 of the bridge-poller-event-driven-replacement thread (2026-05-09) for cause; rebuilding the same substrate under a different name would re-introduce the same class of issues. The single-harness dispatcher is a *different* substrate (host-platform scheduled task) governed by a different DCL.
3. **Extending the cross-harness event-driven trigger to handle single-harness mode.** Tempting but rejected: the trigger fires from `PostToolUse` + `Stop` hooks of the *active* harness, which means it only fires when a foreground session is interacting. In single-harness mode the owner is often *not* in a session; the bridge work would never get dispatched. The Desktop scheduled task is owner-out-of-loop by design, which is exactly what single-harness mode needs.
4. **HTTP webhook / message-bus subscriber substrate.** Rejected by `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Excluded Substrates as out-of-scope complexity.
5. **Manual operator pattern (two-session bridge dance).** Rejected as the steady-state mode: it works (and is the current single-harness workaround) but defeats the operating mode's core promise of reducing owner-loop attention. Manual mode remains the *fallback* when the dispatcher is unhealthy or unregistered.

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` (Codex VERIFIED) — Slice 1 closure; authorizes Slice 2 as the next thread.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-013.md` (Slice 1 REVISED-6) — § Scope explicitly identifies Slice 2 deliverables: "dispatcher script + Desktop task setup + system-interface-map entry + Slice 2 integration tests".
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md` (Codex VERIFIED) — canonical init-keyword + IP-4 receiver-side enum + test-helper hermeticity. Slice 2 emits the canonical keyword per this thread's contract.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) — retired the smart poller; this proposal must NOT re-introduce its substrate.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` (VERIFIED) — active-session-suppression contract that Slice 2 honors.
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-006.md` (GO) — kind-aware-routing dispatchability contract that Slice 2 inherits.
- `DELIB-1511` — prior single-harness dispatcher review preserving the scalar-reader migration concern (closed in Slice 1).
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — smart-poller retirement context.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — owner directive that single-harness operation is first-class.
- `DELIB-0832` — GT-KB installs configure Prime Builder and capable harness role paths.

## Owner Decisions / Input

This proposal is filed under the standard governance path. The Slice 1 owner approvals (the scoped auto-approval activation AUQ from S343 2026-05-12, plus all carried-forward AUQs from `-005`/`-007`) continue to authorize the *direction* of the work but do NOT extend to Slice 2's implementation-time mutations.

Owner-input dependencies at Slice 2 implementation time (cited here so Codex review can validate the packet plan):

1. **AUQ: approval-sequencing path for Slice 2 packets.** If any packet pre-implementation owner-input is required (see below), Prime Builder will ask the owner to choose between default sequential AUQs and scoped auto-approval as in Slice 1. If no formal-artifact mutations are needed (the current plan; see § Implementation Plan IP-1 through IP-7), no per-packet AUQs are required at implementation time.
2. **Narrative-artifact-approval packet for `.claude/rules/bridge-essential.md` amendment (IP-7).** The amendment adds the single-harness dispatcher as a third bridge-dispatch substrate (alongside the cross-harness event-driven trigger and the legacy OS-poller class which is do-not-re-enable). One narrative-artifact-approval packet required.
3. **No new MemBase rows.** Slice 1's ADR + SPEC + DCL already cover the architecture, behavior, and substrate constraint. Slice 2 implements them; status promotion (specified → implemented) is DECISION DEFERRED to a follow-on hygiene packet.

Status promotion of Slice 1's specs is intentionally DECISION DEFERRED so that Slice 2's success-criteria evidence (Codex VERIFIED on this proposal's post-impl report + scheduled-task fires successfully in the wild) can be cited in the promotion packet, rather than requiring promotion concurrent with Slice 2 implementation.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Will run after this NEW entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps.

## Scope (Slice 2)

In-scope:

- `scripts/single_harness_bridge_dispatcher.py` — the wake routine (IP-1).
- Windows Task Scheduler installer + uninstaller (IP-2).
- `config/agent-control/system-interface-map.toml` entry for the dispatcher's scheduled task surface (IP-3).
- Doctor check upgrade: `_check_single_harness_dispatcher_when_required` learns to verify task registration + last-run-time freshness (IP-4).
- Slice 2 integration tests (IP-5).
- Narrative-artifact amendment to `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract adding the single-harness dispatcher as a recognized substrate (IP-7).

Out-of-scope (DECISION DEFERRED markers above):

- macOS launchd / Linux systemd / cron installers (separate platform-extension slice or owner directive).
- MemBase status promotion of Slice 1's specs (follow-on hygiene packet).
- Per-mode interval overrides, advanced dispatch heuristics (future Slice 3 if needed).
- New SPEC/ADR/DCL artifacts (Slice 1 already covers; no new architectural decisions needed).

## Implementation Plan

### IP-1 — `scripts/single_harness_bridge_dispatcher.py` (NEW)

Single-file Python script implementing the wake routine. Key behaviors:

1. **Project-root resolution** — reuse `_resolve_project_root` pattern from `scripts/cross_harness_bridge_trigger.py:99` (explicit `--project-root` flag → package resolver → `GTKB_PROJECT_ROOT` env var → fail-closed).
2. **Single-instance lock** — acquire `.gtkb-state/bridge-poller/dispatcher.lock` (file-existence + mtime freshness; sanity TTL per `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS`, default 120 s). Stale-lock reclaim if older than TTL. Per `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Configuration.
3. **Active-session foreground-suppression check** — read `<state-dir>/active-{handle}-session.lock` for the active harness's command-handle. If fresh, skip dispatch (the owner is in an interactive session; do not compete with foreground work). Per `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` VERIFIED contract.
4. **Applicability check** — read `harness-state/role-assignments.json`. If exactly one harness identity has a multi-element role-set containing both `prime-builder` and `loyal-opposition`, the dispatcher is applicable. Otherwise no-op with `last_result="not_applicable_multi_harness"` recorded in state.
5. **Live INDEX read + signature compute** — read working-tree `bridge/INDEX.md`. Use the existing `parse_index` + `compute_actionable_pending` from `groundtruth_kb.bridge.detector` and `groundtruth_kb.bridge.notify`. Compute per-role actionable signature using `_signature(_selected_oldest_first(filtered, max_items))` byte-identical to `scripts/cross_harness_bridge_trigger.py:135` so the dispatch-state record format remains uniform.
6. **Signature-change predicate** — for each role in the active harness's role-set, compare current signature to `<state-dir>/dispatch-state.json::recipients[<needed_role_label>]::last_dispatched_signature`. If unchanged → skip. If changed → spawn.
7. **Subprocess spawn** — invoke `claude -p <prompt>` or `codex exec <prompt> --cd <root>` per the active harness's command-handle (resolved via `harness-state/harness-identities.json`). Prompt's first line is the canonical init keyword `::init gtkb <mode>`. Env vars set on child: `GTKB_PROJECT_ROOT`, `GTKB_BRIDGE_POLLER_RUN_ID` (UUID-based dispatch ID), `GTKB_BRIDGE_DISPATCH_KEYWORD` (the same keyword string). Use `subprocess.Popen` + `CREATE_NO_WINDOW` on Windows so no console window flashes.
8. **Fire-and-forget** — script exits 0 regardless of spawn outcome. Spawn failures appended to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` in the same JSONL format the cross-harness trigger uses.
9. **State path collision** — the dispatcher MUST use `.gtkb-state/bridge-poller/` (the same path the cross-harness trigger uses). This is intentional: the two substrates are mutually exclusive at runtime (only one applies in any given topology), so they can share the dispatch-state file safely. The `recipients` map keys are role labels per IP-3c migration from canonical-init-keyword Slice; no key collision possible.
10. **CLI** — `--project-root`, `--state-dir`, `--max-items` (default 2 per Slice-1 SPEC cap), `--dry-run`, `--verbose`. Mirror the cross-harness trigger's flag surface so tests and operator UX are uniform.

The script is ~400–500 LOC including docstrings, error handling, and lock-management. It reuses the trigger's design constants by *importing* from the trigger module where possible (DRY) or *replicating* with byte-identity tests (when a separate copy is needed to avoid circular imports). The choice between import-vs-replicate is per-function; tests will pin byte-identity where replication is used.

### IP-2 — Windows Task Scheduler installer + uninstaller

- `scripts/install_single_harness_dispatcher_task.ps1` (NEW) — registers a Windows scheduled task `GTKB-SingleHarnessBridgeDispatcher` with:
  - Trigger: fixed-interval schedule, default 5 minutes (configurable via task definition without code change per `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Configuration).
  - Action: invoke `python single_harness_bridge_dispatcher.py` with `--project-root <gt-kb-root>`.
  - Working directory: GT-KB project root.
  - Hidden console flag (CREATE_NO_WINDOW equivalent via task definition).
  - Idempotent: re-running the installer updates the existing task without creating a duplicate trigger.
- `scripts/uninstall_single_harness_dispatcher_task.ps1` (NEW) — removes the scheduled task. Idempotent (uninstalling a non-existent task succeeds silently with a "not registered" status message).
- Pattern reference: `archive/smart-poller-2026-05-09/install_smart_poller_task.ps1` (archived from the retired smart-poller; the *interface* pattern carries forward even though the substrate's name and purpose differ).

The installers are owner-run (the owner registers the task on their workstation) or `gt project doctor --apply`-driven if/when doctor supports apply mode (out of scope here).

### IP-3 — `config/agent-control/system-interface-map.toml` entry

Add a new `[[systems]]` block:

```toml
[[systems]]
id = "single-harness-bridge-dispatcher"
canonical_name = "single-harness bridge dispatcher"
accepted_aliases = ["single-harness dispatcher", "dispatcher (single-harness topology)"]
discouraged_aliases = []
forbidden_aliases = []
concept_vs_artifact = "axis-1-dispatchable"  # mutually exclusive with cross-harness event-driven trigger at runtime
authoritative_source = "scripts/single_harness_bridge_dispatcher.py + Windows scheduled task GTKB-SingleHarnessBridgeDispatcher"
generated_or_authoritative = "authoritative_runtime"
read_method = "Inspect Task Scheduler entry GTKB-SingleHarnessBridgeDispatcher or run scripts/single_harness_bridge_dispatcher.py --diagnose."
mutation_method = "Use scripts/install_single_harness_dispatcher_task.ps1 to register or update; scripts/uninstall_single_harness_dispatcher_task.ps1 to remove. Editing the script is governed via the bridge protocol."
role_permissions = "Prime Builder owns dispatcher script and installer; Loyal Opposition reviews changes."
startup_visibility = "topology_conditional"  # only surfaced when single-harness topology is applicable
dashboard_visibility = "summary_only"
harness_caveats = "Mutually exclusive with the cross-harness event-driven trigger at runtime; applicability gated by role-set cardinality."
verification_method = "platform_tests/scripts/test_single_harness_bridge_dispatcher.py"
lifecycle_state = "active"
related_specs = [
  "ADR-SINGLE-HARNESS-OPERATING-MODE-001",
  "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001",
  "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001",
  "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001",
  "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001",
]
related_deliberations = ["DELIB-1511", "DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT"]
```

### IP-4 — Doctor check upgrade

Upgrade `_check_single_harness_dispatcher_when_required` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:

Current behavior (Slice 1): applicability-gated; reports WARN when applicable but the dispatcher script is absent.

New behavior (Slice 2):
- Same applicability gate.
- When applicable AND script present: verify the Windows scheduled task `GTKB-SingleHarnessBridgeDispatcher` is registered (via `schtasks /query` or PowerShell `Get-ScheduledTask`). PASS if registered + last-run-time within `interval + sanity_ttl`. WARN if registered but stale. FAIL if applicable + script present but task missing.
- When NOT applicable (multi-harness topology): PASS with "not applicable" (unchanged).
- Cross-platform consideration: on non-Windows hosts, return WARN with platform-not-yet-supported message (until macOS/Linux installers ship in a future slice).

### IP-5 — Slice 2 integration tests

- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` (NEW) — script-level tests:
  - `test_signature_byte_identical_to_trigger`: run dispatcher + cross-harness trigger against same synthetic INDEX, assert signatures match.
  - `test_dispatcher_no_op_in_multi_harness_topology`: applicability check returns false; no spawn; `last_result="not_applicable_multi_harness"`.
  - `test_dispatcher_spawns_in_single_harness_topology_on_signature_change`: synthetic single-harness role-record + INDEX with NEW entry; assert spawn invoked (Popen patched) with the right canonical keyword and env vars.
  - `test_dispatcher_suppresses_on_active_session_lock`: foreground session lock present; assert no spawn; `last_result="counterpart_active_session_present"`.
  - `test_dispatcher_loop_prevention_via_signature_dedup`: spawn once; re-run with same INDEX; second invocation reports `last_result="unchanged"`; no second spawn.
  - `test_dispatcher_emits_canonical_keyword_first_line`: spawn prompt's first line is exactly `::init gtkb <mode>` matching the receiver-side regex.
  - `test_dispatcher_records_dispatch_failures_jsonl`: patched Popen raising → failure record appended to `dispatch-failures.jsonl`.
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (NEW) — installer tests (Windows-only, skipped on other platforms):
  - `test_installer_registers_task` (Windows): runs installer; asserts `Get-ScheduledTask GTKB-SingleHarnessBridgeDispatcher` returns the expected schedule + action.
  - `test_installer_idempotent` (Windows): re-running installer leaves a single registered task; trigger count is 1.
  - `test_uninstaller_removes_task` (Windows): runs uninstaller; asserts task absent.
  - `test_uninstaller_idempotent_on_missing_task` (Windows): runs uninstaller on a non-registered task; exits 0 with informational message.
- `platform_tests/scripts/test_single_harness_doctor_check_upgrade.py` (NEW) — doctor check tests:
  - `test_doctor_passes_when_task_registered_and_fresh` (Windows).
  - `test_doctor_warns_when_task_registered_but_stale` (Windows).
  - `test_doctor_fails_when_applicable_and_script_present_but_task_missing` (Windows).
  - `test_doctor_pass_not_applicable_in_multi_harness` (cross-platform; carry-forward from Slice 1).
  - `test_doctor_warn_when_non_windows_host_applicable`: simulate non-Windows; expect WARN with platform-extension pointer.

All tests follow the established hermeticity discipline (strip `_BRIDGE_DISPATCH_ENV_VARS` from inherited env when building hermetic shells).

### IP-7 — `.claude/rules/bridge-essential.md` amendment (narrative-artifact-approval packet)

Add a new subsection under § Bridge Dispatch Enablement Contract identifying the single-harness dispatcher as the recognized third substrate (alongside the cross-harness event-driven trigger and the retired OS-poller class):

> The bridge protocol has TWO live dispatch substrates as of Slice 2 of `gtkb-single-harness-bridge-dispatcher-slice-2`:
>
> 1. **Cross-harness event-driven trigger** (multi-harness topology) — `scripts/cross_harness_bridge_trigger.py` registered as PostToolUse + Stop hooks. Fires on tool-use and Stop events. Applicable when the role map has two harness IDs with singleton role-sets.
> 2. **Single-harness bridge dispatcher** (single-harness topology) — `scripts/single_harness_bridge_dispatcher.py` invoked by a Windows scheduled task `GTKB-SingleHarnessBridgeDispatcher` on a fixed interval. Applicable when the role map has one harness ID with a multi-element role-set `["prime-builder", "loyal-opposition"]`.
>
> Both substrates honor the same actionable-signature scheme, the same active-session-suppression contract, and the same fire-and-forget audit-log discipline. They are mutually exclusive at runtime; applicability is determined by the role-set topology in `harness-state/role-assignments.json`.

The amendment is small (~30 lines) but is a narrative-authority surface, so a narrative-artifact-approval packet is required per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-S2-signature-byte-identical | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 2 (byte-identical signature scheme) | test_signature_byte_identical_to_trigger |
| T-SHD-S2-multi-harness-noop | ADR-SINGLE-HARNESS-OPERATING-MODE-001 (substrates mutually exclusive at runtime) | test_dispatcher_no_op_in_multi_harness_topology |
| T-SHD-S2-spawn-on-signature-change | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 3 | test_dispatcher_spawns_in_single_harness_topology_on_signature_change |
| T-SHD-S2-active-session-suppression | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Idle Suppression | test_dispatcher_suppresses_on_active_session_lock |
| T-SHD-S2-signature-dedup-loop-prevention | DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 (auto-trigger NEVER fires when work waits, never when idle; preserved by signature-dedup) | test_dispatcher_loop_prevention_via_signature_dedup |
| T-SHD-S2-canonical-keyword-emission | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (first-line activator) | test_dispatcher_emits_canonical_keyword_first_line |
| T-SHD-S2-audit-log-failures | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 (audit-log discipline) | test_dispatcher_records_dispatch_failures_jsonl |
| T-SHD-S2-task-installer-registers | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Platform Bindings (Windows) | test_installer_registers_task |
| T-SHD-S2-task-installer-idempotent | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Installation (idempotent) | test_installer_idempotent |
| T-SHD-S2-task-uninstall | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Installation | test_uninstaller_removes_task, test_uninstaller_idempotent_on_missing_task |
| T-SHD-S2-doctor-task-registration | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check | test_doctor_passes_when_task_registered_and_fresh |
| T-SHD-S2-doctor-stale-warn | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check (liveness) | test_doctor_warns_when_task_registered_but_stale |
| T-SHD-S2-doctor-missing-task-fail | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check | test_doctor_fails_when_applicable_and_script_present_but_task_missing |
| T-SHD-S2-doctor-non-windows-warn | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 (Slice 2 ships Windows-only) | test_doctor_warn_when_non_windows_host_applicable |
| T-SHD-S2-system-interface-map | IP-3 + DCL-CONCEPT-ON-CONTACT-001 (inventory the dispatcher's substrate) | grep `config/agent-control/system-interface-map.toml` for `id = "single-harness-bridge-dispatcher"`; assert structure matches existing entries |
| T-SHD-S2-bridge-essential-amendment | IP-7 narrative amendment | grep `.claude/rules/bridge-essential.md` for "Single-harness bridge dispatcher" + scheduled-task substrate text |

## Acceptance Criteria

- [ ] `scripts/single_harness_bridge_dispatcher.py` exists and passes script-level tests (T-SHD-S2-signature-byte-identical through T-SHD-S2-audit-log-failures).
- [ ] Windows Task Scheduler installer + uninstaller pass installer tests on a Windows host.
- [ ] `config/agent-control/system-interface-map.toml` contains the new `single-harness-bridge-dispatcher` entry with the structure shown in IP-3.
- [ ] Doctor check upgrade passes all five doctor tests.
- [ ] `.claude/rules/bridge-essential.md` amendment landed with narrative-artifact-approval packet evidence.
- [ ] End-to-end verification on a Windows host: register a single-harness role-record, install the scheduled task, write a NEW bridge entry, observe the dispatcher fire within one interval, spawn a subprocess, and process the entry.
- [ ] Post-impl regression command passes from a bridge-auto-dispatched shell environment (carrying both `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_DISPATCH_KEYWORD` in the parent env) without any test inheriting those markers into its child processes.

## Risk + Rollback

**Risks:**

- **R1 (Medium):** Spawning the same harness against itself in single-harness mode could create an unintended recursive loop if signature-dedup fails. Mitigation: signature-dedup is the primary loop-prevention mechanism (proven in cross-harness trigger). Additional defense: the dispatcher inherits the trigger's active-session-suppression contract; if the spawned worker holds its own active-session lock during its run, subsequent dispatcher wakes will suppress until the worker exits.
- **R2 (Low):** Windows Task Scheduler API differs across Windows versions; the installer may need version-specific shims. Mitigation: PowerShell's `Register-ScheduledTask` cmdlet covers Windows 8+ uniformly; the installer requires Windows 10+ (documented in the script header).
- **R3 (Low):** `config/agent-control/system-interface-map.toml` schema doesn't currently define `concept_vs_artifact = "axis-1-dispatchable"`; if that value is rejected by `verification_method`, the test may fail. Mitigation: review existing entries' `concept_vs_artifact` values; if "axis-1-dispatchable" is novel, document it in the schema-defining comment or pick an existing accepted value.
- **R4 (Low):** Doctor's task-registration check requires a Windows `Get-ScheduledTask` PowerShell call; subprocess.run with `powershell` on non-Windows hosts will fail. Mitigation: platform-gate the check with `sys.platform == "win32"`; on other platforms return the not-yet-supported WARN.
- **R5 (Medium):** The dispatcher and the cross-harness trigger share `.gtkb-state/bridge-poller/` state. If a future configuration enables both simultaneously (which the applicability gates prevent today), they could double-dispatch. Mitigation: applicability gate is enforced at the dispatcher entry point; the doctor `_check_role_set_topology_consistency` check catches the mis-configuration.

**Rollback:**

- Delete `scripts/single_harness_bridge_dispatcher.py` and the installer/uninstaller scripts.
- Run the uninstaller to remove the scheduled task on any Windows host where it was registered.
- Revert the `config/agent-control/system-interface-map.toml` entry.
- Revert the doctor check upgrade to the Slice 1 WARN-on-missing-script behavior.
- Revert the `.claude/rules/bridge-essential.md` amendment.
- Delete the new test files.
- Slice 1 (governance scaffolding + runtime migration + Slice 1 tests) is unaffected by Slice 2 rollback.

## Files Expected To Change

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry inserted at top of file, new `Document:` block).
- `scripts/single_harness_bridge_dispatcher.py` (NEW; ~400-500 LOC; IP-1).
- `scripts/install_single_harness_dispatcher_task.ps1` (NEW; IP-2).
- `scripts/uninstall_single_harness_dispatcher_task.ps1` (NEW; IP-2).
- `config/agent-control/system-interface-map.toml` (extend; IP-3).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (upgrade `_check_single_harness_dispatcher_when_required`; IP-4).
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` (NEW; IP-5).
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (NEW; IP-5; Windows-only).
- `platform_tests/scripts/test_single_harness_doctor_check_upgrade.py` (NEW; IP-5).
- `.claude/rules/bridge-essential.md` (amendment; IP-7; narrative-artifact-approval packet required).
- `.groundtruth/formal-artifact-approvals/<date>-claude-rules-bridge-essential-md-single-harness-dispatcher-substrate.json` (NEW; IP-7 narrative packet).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section enumerates all specs the implementation honors.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan maps cited specs to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files remain under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — IP-7 narrative-artifact-approval packet required for `.claude/rules/bridge-essential.md` amendment.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — hook gate satisfied via packet evidence at implementation time.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — operating-mode topology decision (Slice 1; rowid 8480 v1) authorizes this Slice.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — behavior contract (Slice 1; rowid 8481 v1) this Slice implements.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — wake substrate constraint (Slice 1; rowid 8482 v1) this Slice realizes.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — first-line activator keyword the dispatcher emits.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — emitter/receiver consistency contract.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — preserved by the dispatcher's identity-derived spawn (Claude OR Codex per command_handle).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — preserved; the dispatcher applicability gate is role-set-cardinality-driven, not vendor-bound.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — preserved; receiver-side enforcement is unchanged.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 — mechanism-agnostic dispatch-on-actionable-change semantic.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 — actionable-only-spawn invariant.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 — preserved; the dispatcher's receiver is the same set-membership check.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 — audit-log discipline preserved; failures recorded to the shared `dispatch-failures.jsonl`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — implementation governed via durable artifacts (proposal, post-impl report, tests).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-anchored delivery.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — implementation lands behind the bridge VERIFIED lifecycle trigger.
- `GOV-STANDING-BACKLOG-001` — see § Bulk-Operations Clause Scope Clarification above.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` — durable owner-action visibility protocol governs the IP-7 narrative-artifact packet.
- `.claude/rules/operating-role.md` — single-harness topology assignment rule preserved (Slice 1 amendment).
- `.claude/rules/canonical-terminology.md` — single-harness operating mode + single-harness bridge dispatcher glossary entries (Slice 1 amendment) cited by IP-7.
- `.claude/rules/file-bridge-protocol.md` — followed.
- `.claude/rules/codex-review-gate.md` — followed.
- `.claude/rules/bridge-essential.md` — amended in IP-7.

## Recommended Commit Type

`feat:` — net-new runtime capability surface (dispatcher script + installer + scheduled task + doctor upgrade + tests). The IP-7 narrative-artifact amendment is part of the feature scope (not a separate `docs:`-classified change) because it activates the operational-mode contract end-to-end.

## Loyal Opposition Asks

1. Confirm Slice 2's substrate plan (Windows Task Scheduler primary; macOS/Linux deferred) matches the spirit of `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Platform Bindings (which names all three platforms as eventual targets).
2. Confirm signature-scheme byte-identity with the cross-harness trigger is the right design choice (DRY benefit) vs. allowing the two substrates to evolve independently (looser coupling).
3. Confirm the `.gtkb-state/bridge-poller/` state-path sharing between substrates is safe given applicability mutual exclusion.
4. Confirm the IP-7 `.claude/rules/bridge-essential.md` amendment is the right surface for documenting the third substrate, vs. (e.g.) extending the canonical-terminology glossary or filing a new ADR for the dual-substrate model.
5. Confirm the DECISION DEFERRED markers for status promotion + cross-platform installers are appropriately scoped and not silently dropping work.
6. Confirm the Risk R1 mitigation (signature-dedup + active-session-suppression as the loop-prevention pair) is sufficient for the single-harness-spawn-itself topology, or whether an additional explicit recursion guard is warranted.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
