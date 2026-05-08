NEW

# Implementation Proposal — GTKB-BRIDGE-POLLER-EVENT-DRIVEN-REPLACEMENT-001 (Slice 0 Scoping)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-bridge-poller-event-driven-replacement-001`
**Type:** Architectural replacement scoping. Slice 0 = scope confirmation + slice plan; Slices 1-N = phased implementation. This proposal does NOT itself implement any code change — it scopes the architecture and sequences the work so each downstream slice files its own implementation bridge.
**Status:** NEW
**Source authorization:** S337 owner conversation 2026-05-08 directly motivated this thread:
1. Owner asked: can Codex schedule/trigger Claude routines and vice versa? Goal: replace timer-based polling with event-driven cross-harness triggering.
2. Owner confirmed the project's "Codex hooks not live on Windows" stance predates OpenAI's Windows hook support landing.
3. Owner directed an empirical retest, captured as `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550).
4. Owner directed filing this scoping bridge.

## Claim

The smart-poller's 15-second timer-based polling of `bridge/INDEX.md` can be retired and replaced with **symmetric hooks-based cross-harness triggering** because Codex hooks now fire on Windows (per the empirical retest in `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`). Both directions become event-driven, native, and bounded by per-event work rather than polling cadence.

This proposal scopes the replacement architecture, sequences the implementation slices, and explicitly does NOT itself ship any operational change. Each slice files its own implementation bridge.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the test plan below derives from each affected component.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`. All artifacts touched by this proposal remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.

**Domain-specific** (governed artifacts being changed in subsequent slices):

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v1 — empirically falsified per DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST. v2 with approval packet supersedes the "forward-compatible only on Windows" stance.
- `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v1 — mirrors the ADR; v2 with approval packet.
- `DELIB-0836` v1 — original deliberation; preserved as historical record. Superseded by `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`.
- The smart-poller program family: `bridge/gtkb-bridge-poller-001-smart-poller-007.md`, `bridge/gtkb-bridge-poller-p1-detector-004.md`, `bridge/gtkb-bridge-poller-p2-registry-006.md`, `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md`, `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-*.md`, `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-*.md`.

**Authoring sources to update** (in subsequent slices):

- `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section (narrative authority subject to narrative-artifact-approval gate from `gtkb-narrative-artifact-approval-extension-001`).
- `bridge/gtkb-narrative-artifact-approval-extension-001-005.md`, `-006.md`, `-010.md` Slice A.1 + C posture about Codex template parity being "forward-compatible only" — superseded via subsequent bridge thread (bridge artifacts are append-only).

**Bridge / protocol specs** (referenced but not changed):

- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/bridge-essential.md` — bridge integrity mandate; "Bridge Polling: Halted" 2026-04-25 incident history; "Operational Mode" smart-poller activation context.

**Governance gates**:

- `GOV-ARTIFACT-APPROVAL-001` v3 (rowid 8453) — formal-artifact-approval packets required for ADR/DCL/GOV/SPEC/PB/DELIB and narrative-artifact mutations.
- `GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001` Slices A.1 + A.2 + C (cumulative VERIFIED at `-011`) — runtime gate that validates narrative-artifact edits in this thread.

## Owner Decisions / Input

S337 owner AUQ history relevant to this thread:

| Question | Answer |
|---|---|
| Project stance is stale — what's the next concrete step? | "Run the empirical retest now" |
| Codex hooks confirmed live on Windows — next step? | "Capture as DELIB, then file scoping bridge for full architecture" |
| Approve DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08? | "Approve as proposed" |

This proposal is the second deliverable from the third AUQ ("then file scoping bridge for full architecture"). Implementation slices below require separate Codex GO before any operational change ships.

## Empirical Foundation

`DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550, source_type=report, outcome=informational) captures the test:

- Codex CLI version: `codex-cli 0.128.0-alpha.1`.
- Feature flag `codex_hooks` is `stable, true` by default (no manual `[features] codex_hooks = true` setting needed in `~/.codex/config.toml`).
- SessionStart and Stop hooks fired during `codex exec --skip-git-repo-check "..."` invocation on Windows.
- Sentinel evidence at `.tmp/codex-hook-test/sentinel.txt` (gitignored; reproducible via `codex exec` from the test directory).

The architecture below assumes this empirical foundation. Slice 1 includes a formal regression test that will fail-loud if the assumption regresses (e.g., a future Codex CLI release re-disables Windows hook firing).

## Proposed Architecture (Symmetric Event-Driven)

```text
+-------------------+        +-------------------+
|  Claude harness B |        |  Codex harness A  |
|  (Prime Builder)  |        | (Loyal Opposition)|
+---------+---------+        +---------+---------+
          |                            |
          | PostToolUse hook on Bash   | Stop hook (or PostToolUse)
          | detects: git commit ...    | detects: bridge file write
          |          bridge/* in diff  |          via Stop event
          |                            |
          v                            v
   shells out:                  shells out:
   `codex exec --json           `claude -p "scan
    "scan bridge/INDEX.md       bridge/INDEX.md and
    and respond to              process actionable
    actionable items"           items" --allowedTools
    --skip-git-repo-check`       "Bash,Read,Edit"`
                                                
          |                            |
          v                            v
   Codex wakes, scans          Claude wakes, scans
   INDEX, processes the        INDEX, processes the
   REVISED, files GO/NO-GO,    GO/NO-GO/VERIFIED,
   commits, exits.             commits, exits.
```

No timer. No background polling process. No Anthropic Cloud routine setup. No API tokens. The only persistent state is the hook configurations (one-time install via `gt project upgrade` or equivalent).

### Detection logic

The PostToolUse hook on Bash needs to identify git commits affecting bridge files. The simplest detection is a regex over the Bash command string: `git\s+commit.*` AND post-commit log inspection that the staged paths included `bridge/`. A more robust path: a small script that the hook shells out to, which uses `git log -1 --name-only HEAD` to inspect the most recent commit.

The Stop hook on Codex side fires on every session end, regardless of what Codex did. The dispatch needs to be conditional: only invoke Claude if the staged/committed work touched `bridge/`. Same script pattern as above.

### Component inventory

Five components in scope (each is its own Slice):

1. **Slice 1 — Cross-harness trigger detection script** (`scripts/cross_harness_bridge_trigger.py`): inspects most recent git commit for `bridge/*.md` paths, decides whether to dispatch the other harness, dispatches via `claude -p` or `codex exec` with appropriate prompt, captures dispatch evidence.
2. **Slice 2 — Claude-side hook registration** (`.claude/settings.json` PostToolUse Bash matcher invokes the trigger script).
3. **Slice 3 — Codex-side hook registration** (`.codex/hooks.json` Stop hook invokes the trigger script).
4. **Slice 4 — Smart-poller retirement plan** (decommission `GTKB-SmartBridgePoller` Windows scheduled task; archive `scripts/run_smart_bridge_poller.vbs`, `groundtruth-kb/scripts/bridge_poller_runner.py`, `.gtkb-state/bridge-poller/dispatch-state.json`; update doctor checks).
5. **Slice 5 — Governance refresh** (Slice A.2-style ADR/DCL v2 + acting-prime-builder.md narrative edit superseding the "forward-compatible only on Windows" stance + supersession deliberation referencing DELIB-0836).

Slice 1 is foundational; Slices 2-3 install it; Slice 4 retires the predecessor; Slice 5 corrects the artifact landscape. The slices have a partial order: Slice 1 must precede 2 and 3; Slice 4 must follow 2 and 3 (the replacement must be live before the predecessor retires); Slice 5 may run in parallel with any of 1-4 because it doesn't touch operational code.

### Failure modes considered

| Failure | Behavior | Mitigation |
|---|---|---|
| Hook fires but harness invocation fails | Trigger script logs the failure to `.gtkb-state/cross-harness-trigger/dispatch-failures.jsonl` | Slice 1 includes failure-mode tests |
| Loop: Claude commit triggers Codex which commits which triggers Claude | Each invocation includes a `--no-trigger` flag or env var preventing the receiving harness's commit from re-triggering | Slice 1's dispatch script adds the loop-prevention flag to every dispatched invocation |
| Trigger script error blocks the original git commit | Trigger script always exits 0 (failures are logged, not propagated) | Slice 1 contract: trigger script is fire-and-forget from git's perspective |
| Multiple concurrent triggers | Each harness invocation is a separate process; bridge file writes are append-only and serialized by git | No additional mitigation needed; concurrent dispatch is acceptable |
| Codex hook re-disables on a future CLI version | Slice 1 regression test invokes `codex exec` against a sentinel hook and asserts firing | Test fails loudly; smart-poller could be re-enabled as fallback |

## Spec-Derived Test Plan

Slice 1 tests:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-1-detection | Trigger script identifies bridge/* commits | `tests/scripts/test_cross_harness_bridge_trigger.py::test_detects_bridge_commit` — synthetic git repo with a commit touching `bridge/foo.md`; assert script's `should_dispatch()` returns True |
| T-1-no-detection | Non-bridge commits are ignored | `test_skips_non_bridge_commit` — commit touching only `scripts/x.py`; assert `should_dispatch()` returns False |
| T-1-dispatch-shape | Dispatch invocation is shell-correct | `test_dispatch_command_format` — verify the constructed invocation includes `--allowedTools` (Claude) or `--skip-git-repo-check` (Codex) plus the loop-prevention flag |
| T-1-loop-prevention | Trigger does not re-fire when dispatch flag present | `test_loop_prevention` — env var or flag set; trigger script no-ops |
| T-1-fire-and-forget | Trigger script always exits 0 | `test_exit_zero_on_dispatch_failure` — monkeypatch dispatch to raise; assert script still exits 0 + logs failure |
| T-1-codex-hook-firing-regression | Codex hooks still fire on Windows | `tests/scripts/test_codex_hook_parity.py::test_codex_hooks_fire_on_windows` — invoke `codex exec --skip-git-repo-check "<sentinel prompt>"` from a test fixture directory with a Stop hook; assert sentinel touched |

Slice 2 tests (Claude hook registration):

| Test | Spec/Requirement | Method |
|---|---|---|
| T-2-registration | PostToolUse on Bash matcher present in `.claude/settings.json` | grep + JSON-parse test in `tests/scripts/test_claude_settings.py` |
| T-2-no-bridge-compliance-regression | Existing bridge-compliance + narrative-artifact gates unaffected | re-run `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` + `tests/hooks/test_narrative_artifact_approval.py` |

Slice 3 tests (Codex hook registration):

| Test | Spec/Requirement | Method |
|---|---|---|
| T-3-codex-registration | Stop hook present in `.codex/hooks.json` invoking the trigger script | JSON-parse test |
| T-3-narrative-artifact-codex-template-promotion | The previously-forward-compatible Codex template at `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` is now ALSO registered as a live PreToolUse hook in `.codex/hooks.json` | Asserts both Stop (cross-harness trigger) and PreToolUse Edit/apply_patch (narrative-artifact gate) blocks are present and non-empty |
| T-3-narrative-artifact-codex-live | Slice C narrative-artifact gate fires on Codex apply_patch | Integration test invoking `codex exec` with a prompt that attempts to edit `.claude/rules/example.md` without an approval packet; assert codex's apply_patch is rejected by the hook |

Slice 4 tests (smart-poller retirement):

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-windows-task-removed | `GTKB-SmartBridgePoller` Windows scheduled task does not exist | `schtasks /Query /TN GTKB-SmartBridgePoller` returns "task does not exist" |
| T-4-vbs-archived | `scripts/run_smart_bridge_poller.vbs` no longer present at active path; archived under `archive/` | filesystem assertion |
| T-4-doctor-updated | `gt project doctor`'s smart-poller check is removed or replaced with the cross-harness-trigger check | `tests/scripts/test_doctor_smart_poller_check.py` updated |
| T-4-dispatch-state-cleared | `.gtkb-state/bridge-poller/dispatch-state.json` is removed or marked inactive | filesystem assertion |

Slice 5 tests (governance refresh):

| Test | Spec/Requirement | Method |
|---|---|---|
| T-5-adr-v2 | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 inserted with approval packet | `db.list_specs(...)` returns max(version) >= 2; `change_reason` cites packet path |
| T-5-dcl-v2 | `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v2 inserted | analogous |
| T-5-narrative-edit | `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section reflects the new live-on-Windows reality | grep test + narrative-artifact-approval gate accepts at pre-commit time |
| T-5-supersession-delib | A new deliberation references `DELIB-0836` as superseded | `db.search_deliberations(...)` finds the supersession entry |

Live regression (all slices):

| Test | Method |
|---|---|
| T-live-doctor | `gt project doctor` returns no NEW ERRORs (informational/WARN findings acceptable) |
| T-live-release-gate | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` returns no NEW failures introduced by this thread (per F2 baseline-discipline pattern from `gtkb-backlog-work-list-retirement-directive-001-009.md`) |
| T-live-bridge-protocol | A round-trip bridge update (Claude commits NEW; Codex commits GO; Claude commits post-impl) completes via cross-harness triggers; smart-poller is NOT involved (Slice 4 has retired it) |

## Acceptance Criteria

For Slice 0 GO (this proposal):

- Codex confirms the symmetric hooks-based architecture is acceptable per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v1's stance being empirically falsified.
- Codex confirms the slice sequencing (1 → 2 + 3 → 4; 5 in parallel) is correct.
- Codex confirms the failure-mode list is complete or flags additions.

For each subsequent slice's VERIFIED: per the slice's own implementation report.

For thread cumulative VERIFIED (after all 5 slices land):

- Cross-harness triggers fire on bridge commits in both directions (T-live-bridge-protocol).
- Smart-poller is fully retired; doctor reflects new architecture.
- ADR/DCL/narrative artifacts reflect the corrected stance.
- No new release-gate failures introduced.

## Risk / Rollback

Risk surface:

- **Codex hook firing regression**: a future Codex CLI release could disable Windows hooks. Slice 1's regression test catches this; if it fails, smart-poller can be re-enabled as fallback. Mitigation: Slice 4's smart-poller retirement preserves the disabled Windows scheduled task (renamed/archived rather than deleted) so re-enablement is one schtasks command.
- **Loop avoidance is implementation-critical**: a poorly-designed loop-prevention flag could cause the architecture to thrash. Mitigation: Slice 1's `test_loop_prevention` is mandatory before Slice 2/3 ship; the env var `GTKB_NO_CROSS_HARNESS_TRIGGER=1` propagates across the dispatched invocation.
- **Token cost of mistakenly-firing trigger**: each trigger fire invokes a full headless harness session (~5K-15K tokens per the empirical retest baseline). If the detection logic over-fires on non-bridge commits, token cost balloons. Mitigation: T-1-no-detection + extensive unit-test coverage of the detection regex; explicit allow-list of `bridge/*.md` rather than block-list of non-bridge.
- **Bridge-essential.md "Re-Enabling Pollers" requirement**: the existing rule says re-enabling the OS poller requires "explicit owner approval and the cost/benefit analysis." This proposal RETIRES the smart-poller, not the OS pollers. Slice 4's plan does NOT touch the retired OS poller stance. Mitigation: `.claude/rules/bridge-essential.md` Slice 5 narrative edit clarifies the new architecture without reopening the retired-OS-poller question.
- **Sibling-thread coupling**: `gtkb-narrative-artifact-approval-extension-001` Slice C universal-floor pre-commit gate depends on the "Codex hooks not live on Windows" assumption. This thread's Slice 5 governance refresh + Slice 3's Codex template registration changes the framing: pre-commit becomes defense-in-depth rather than the load-bearing universal floor. Mitigation: Slice 5 explicitly notes the framing change in supersession evidence.

Rollback per slice:

- Slice 1: revert script + tests; trigger detection becomes a no-op.
- Slice 2/3: revert hook registrations; cross-harness triggers stop firing; smart-poller (still active until Slice 4) continues as the dispatch mechanism.
- Slice 4: re-create the Windows scheduled task; restore the archived VBS daemon; smart-poller resumes.
- Slice 5: append v3 supersession to ADR/DCL; revert the narrative edit + insert a superseding deliberation.

## Files Expected To Change

Slice 1:

- `scripts/cross_harness_bridge_trigger.py` (new) — detection + dispatch logic.
- `tests/scripts/test_cross_harness_bridge_trigger.py` (new) — 5 tests per the test plan.
- `tests/scripts/test_codex_hook_parity.py` — extend with `test_codex_hooks_fire_on_windows` (Slice 1 reach into existing file).

Slice 2:

- `.claude/settings.json` — add PostToolUse Bash matcher invoking `scripts/cross_harness_bridge_trigger.py`.
- `groundtruth-kb/templates/.claude/settings.json` — template parity for adopters.

Slice 3:

- `.codex/hooks.json` — add Stop hook block invoking `scripts/cross_harness_bridge_trigger.py`; ALSO add PreToolUse Edit/apply_patch matcher invoking the existing `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` Codex template (live promotion).

Slice 4:

- Windows scheduled task `GTKB-SmartBridgePoller` removed via `schtasks /Delete /TN GTKB-SmartBridgePoller`.
- `scripts/run_smart_bridge_poller.vbs` moved to `archive/` (or path-renamed).
- `groundtruth-kb/scripts/bridge_poller_runner.py` archived.
- `.gtkb-state/bridge-poller/dispatch-state.json` removed or marked inactive.
- `gt project doctor` smart-poller checks (`_check_smart_bridge_poller`, `_check_bridge_poller`) updated or replaced with cross-harness-trigger health check.
- `.claude/rules/bridge-essential.md` "Operational Mode" section updated to describe the new event-driven architecture.

Slice 5:

- `groundtruth.db` — new versions in `specifications` table for `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 + `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v2; new row in `deliberations` superseding `DELIB-0836`.
- `.groundtruth/formal-artifact-approvals/2026-05-XX-{ADR,DCL,DELIB}*.json` — approval packets for each insert.
- `.claude/rules/acting-prime-builder.md` — narrative edit removing or rewriting the "Harness Hook Parity Fallback Principle" section, gated by narrative-artifact-approval packet.

Slice 0 (this proposal): no operational change.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-001.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-001.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

All triggered cross-cutting specs cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Recommended Commit Type

For this proposal filing: `docs(bridge):` — bridge-protocol artifact only, no code or test changes.

For Slice 1 implementation: `feat(governance):` — new cross-harness trigger script + tests.

For Slice 2/3 implementation: `feat(governance):` — hook registrations + Codex template promotion.

For Slice 4 implementation: `refactor(governance):` — smart-poller retirement; replacement is already in place.

For Slice 5 implementation: `feat(governance):` — net-additional ADR/DCL versions + superseding deliberation.

## Requested Loyal Opposition Action

Review this `-001` for GO. Specific reviewer questions for Codex:

1. Does the symmetric hooks-based architecture (Codex Stop hook → `claude -p`; Claude PostToolUse Bash hook → `codex exec`) match your reading of OpenAI's Codex hook semantics? Specifically: is the Stop hook the right event to detect Codex commits, or should it be PostToolUse on apply_patch / Bash (git commit) for more precise filtering?
2. Is the slice sequencing (1 foundational → 2+3 install → 4 retire predecessor → 5 governance in parallel) correct, or do you require Slice 5 to land BEFORE Slices 2-4 because the operational changes are governance-coupled?
3. Is the loop-prevention via `GTKB_NO_CROSS_HARNESS_TRIGGER=1` env var sufficient, or do you require a more durable mechanism (e.g., session-id tracking; "this commit was made by harness X in response to harness Y's commit Z" metadata in the commit message)?
4. Slice 3's Codex template promotion (registering `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` as a live PreToolUse hook in `.codex/hooks.json`) closes the asymmetric-enforcement gap from `gtkb-narrative-artifact-approval-extension-001` Slice C. Should this be a separate bridge thread or kept bundled here? Keeping bundled saves governance ceremony; separating is cleaner audit-wise.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
