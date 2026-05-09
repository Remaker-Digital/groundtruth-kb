REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 3 (Hook Registrations) — REVISED-1

bridge_kind: implementation_slice
Document: gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
Version: 003 (REVISED post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`

## Claim

Activate the cross-harness bridge trigger by registering hooks on both harnesses, using Option A overlap coordination (shared smart-poller dispatch-state path during overlap), with two scope/contract corrections per Codex `-002`:

- **F1 fix:** Drop adopter-template propagation from this slice. The original Slice 3 §C4 cited `groundtruth-kb/templates/.claude/settings.json` as the propagation target, but that path does not exist. The actual authority surface is the managed-artifact registry (`groundtruth-kb/templates/managed-artifacts.toml` + scaffold/upgrade/doctor logic in `groundtruth_kb.project.*`) that *synthesizes* settings.json on scaffold/upgrade. Slice 3 now scopes to **the GT-KB host checkout only**. Adopter propagation is captured as Open Follow-On §1 below.
- **F2 fix:** Codex Stop hook command must satisfy the Codex Stop output contract (JSON stdout when exiting 0). Slice 3 now adds a `--stop-hook` mode to `scripts/cross_harness_bridge_trigger.py` that runs `run_trigger()` and emits `{}` to stdout. The implementation lands in this slice; the proposal commits to the contract here. Existing parity test `tests/scripts/test_codex_hook_parity.py:77` (asserts `Stop` absent from `.codex/hooks.json`) is replaced with a test asserting the correct registered-state.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical confirmation of Codex hooks on Windows.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551) — Slice 1 supersession deliberation (parent thread).
- Parent thread `bridge/gtkb-bridge-poller-event-driven-replacement-010.md` — VERIFIED Slice 1 + Slice 2.
- This thread `-002` (Codex NO-GO) — drove F1+F2 corrections in this REVISED.

## Specification Links

(Carried forward from `-001`; one path correction per F1.)

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Test Plan §T-3-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`: `.claude/settings.json`, `.codex/hooks.json`, `scripts/cross_harness_bridge_trigger.py` (Stop-mode addition), `tests/scripts/test_cross_harness_bridge_trigger.py`, `tests/scripts/test_codex_hook_parity.py`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific:**

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (rowid 8463).
- Parent thread `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` Slice 3 §C1-C4 (GO at `-004`) — drives the implementation scope, corrected per F1 to drop §C4 adopter-template work.
- `scripts/cross_harness_bridge_trigger.py` (committed at `6ab3c0b0`) — script being registered + extended with `--stop-hook` mode.
- OpenAI Codex hooks documentation (cited by Codex `-002` F2): https://developers.openai.com/codex/hooks — Stop event JSON stdout contract.

**No longer in scope (per F1):**

- `groundtruth-kb/templates/.claude/settings.json` — does not exist as a static authority surface. Adopter propagation is via managed-artifact registry; that work is Open Follow-On §1.

## Owner Decisions / Input

This proposal cites the AUQ-only rule and the parent thread's owner-acknowledged scope. No new owner-decision dependence beyond what `-001` carried; the F1+F2 fixes are mechanical defect repairs to the previously-filed plan.

| AUQ question | Answer |
|---|---|
| (S337) Codex hooks confirmed live on Windows — next step? | "Capture as DELIB, then file scoping bridge for full architecture" |
| (S337) Two threads, one GO + one NO-GO — next action? | "Address NO-GO -002 first (REVISED-1 on event-driven)" |
| (S337) | "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement" |
| (S337) Reminder | "Remember to disable and clean up the old smart-poller when the new notifier becomes active" |
| (S337) | "Draft Slice 3 NEW proposal now" |

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing Preflight Subsection": the applicability preflight will be re-run after this REVISED entry is added to `bridge/INDEX.md`. The previous run (against `-001`) reported `preflight_passed: true` with packet_hash `sha256:4e954935...`; this REVISED's content delta is the F1+F2 corrections within the same spec linkage. Expected: pass.

## Overlap Coordination Strategy (unchanged from `-001`)

Codex confirmed at `-002` Q1 that **Option A (shared smart-poller dispatch-state path during overlap) is acceptable in principle, provided the revised proposal keeps the state path explicit and preserves the smart-poller signature contract.**

Both conditions are preserved:

- State path is explicit in every hook command via `--state-dir` flag.
- Signature contract is byte-identical to smart-poller (verified by Slice 2's `test_signature_uses_selected_batch_not_full_list_with_max_items_2` cross-importing `bridge_poller_runner._pending_signature`).

## Implementation Plan (REVISED)

### C1. Claude `.claude/settings.json` registration (unchanged from `-001`)

Add three hook entries. The PostToolUse matchers are silent (default invocation); Stop uses the new `--stop-hook` mode for valid output.

1. **PostToolUse Bash** matcher: `python "$CLAUDE_PROJECT_DIR/scripts/cross_harness_bridge_trigger.py" --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` (timeout 5s)
2. **PostToolUse Write|Edit** matcher: same command (timeout 5s)
3. **Stop** hook: `python "$CLAUDE_PROJECT_DIR/scripts/cross_harness_bridge_trigger.py" --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller" --stop-hook` (timeout 5s)

The Claude Stop hook output contract is permissive (any JSON object is valid); `{}` is the minimal compliant payload. Documentation: https://docs.claude.com/en/docs/claude-code/hooks Stop event.

### C2. Codex `.codex/hooks.json` registration (REVISED per F2)

Add two hook entries. Codex Stop matchers are not supported per OpenAI docs; Stop is registered globally.

1. **PostToolUse Bash + apply_patch** matcher: `python E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller` (timeout 5s; silent stdout permitted for PostToolUse)
2. **Stop** hook (no matcher): `python E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller --stop-hook` (timeout 5s; emits `{}` JSON to stdout per Codex Stop contract)

### C3. Stop reconciliation hook semantics + new `--stop-hook` script mode (REVISED per F2)

**New script mode**: add `--stop-hook` flag to `scripts/cross_harness_bridge_trigger.py`. Behavior:

1. Run `run_trigger(...)` exactly as the default invocation does (read live INDEX, compute signature, dispatch on change, write dispatch-state).
2. Emit `{}` to stdout (Codex Stop contract; Claude Stop also accepts `{}`).
3. Exit 0 (fire-and-forget contract preserved).

The Stop reconciliation behavior is unchanged from `-001`: bounded by signature dedup, fail-soft. The `--stop-hook` flag adds the JSON-output discipline required by Codex's Stop contract.

### C4. Adopter propagation — DROPPED per F1; captured as Open Follow-On §1

Slice 3 scopes to the GT-KB host checkout only (`E:\GT-KB`). New and existing dual-agent adopter projects do NOT receive the Slice 3 hook registrations through this slice. Adopter propagation requires:

- New `SettingsHookEvent.STOP` enum value in `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` (currently only `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreToolUse` per Codex `-002` evidence).
- New managed-artifact rows for the three Claude hook entries + Codex hook entries in `groundtruth-kb/templates/managed-artifacts.toml`.
- Synthesis of these rows into adopter `.claude/settings.json` and `.codex/hooks.json` via `groundtruth_kb.project.scaffold.py:630-657` and the upgrade path.
- New `gt project doctor` checks ensuring synthesized settings include the Slice 3 entries.
- Tests in `groundtruth-kb/tests/test_scaffold_settings.py`, `test_managed_registry.py`, and the upgrade test suite.

That work is significant in its own right (adopter-side breaking-change handling, upgrade migration, doctor parity) and belongs in a separate bridge thread per parent thread `-004` Open Follow-On discipline.

### C5. Existing test correction (NEW per F2)

`tests/scripts/test_codex_hook_parity.py:77` currently asserts `Stop` is ABSENT from `.codex/hooks.json` — that invariant flips when Slice 3 ships. Replace the absence assertion with a presence assertion: Stop hook entry exists, command invokes the trigger script with `--stop-hook` flag.

## Spec-Derived Test Plan (REVISED)

| Test | Spec/Requirement | Method |
|---|---|---|
| T-3-claude-registration | Slice 3 §C1 | Parse `.claude/settings.json`; assert PostToolUse matchers for Bash, Write, Edit each invoke `cross_harness_bridge_trigger.py` with `--state-dir` flag pointing at the smart-poller path; assert Stop hook entry present with `--stop-hook` flag. |
| T-3-codex-registration | Slice 3 §C2 | Parse `.codex/hooks.json`; assert PostToolUse matcher for Bash + apply_patch invokes the trigger; assert Stop hook entry present with `--stop-hook` flag and no matcher. |
| T-3-codex-parity-test-flipped | Slice 3 §C5 | Replace existing `tests/scripts/test_codex_hook_parity.py:77` `Stop` absence assertion with presence assertion. |
| T-3-stop-hook-output-contract | Slice 3 §C3 (F2 fix) | Run `python scripts/cross_harness_bridge_trigger.py --project-root <synthetic> --state-dir <synthetic> --stop-hook --dry-run`. Assert: exit 0; stdout is valid JSON; stdout parses to `{}` (or a non-empty dict containing valid Stop-contract fields). |
| T-3-stop-reconciliation-bounded | Slice 3 §C3 | Synthetic in-root project; INDEX unchanged; invoke trigger via `--stop-hook`; assert exit 0, no dispatch (signature unchanged), `{}` stdout. |
| T-3-stop-reconciliation-fail-soft | Slice 3 §C3 (safety net) | Synthetic in-root project; INDEX changed since last recorded signature; invoke trigger via `--stop-hook`; assert dispatch path entered (dry_run mode), `{}` stdout. |
| T-3-overlap-state-shared | Option A coordination | Pass `--state-dir .gtkb-state/bridge-poller` (overlap mode); pre-populate that path with a signature; trigger fire on unchanged INDEX returns "unchanged"; trigger fire on changed INDEX dispatches and updates the same file. |
| T-3-codex-hook-firing-regression | DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST | Existing test at `tests/scripts/test_codex_hook_parity.py` continues to pass after the parity-flip update. |

Live regression (cumulative):

| Test | Method |
|---|---|
| T-live-doctor | `gt project doctor` no NEW ERRORs after registration. |
| T-live-bridge-protocol-round-trip | Manual round-trip exercise; documented in Slice 3 implementation report. |
| T-live-codex-stop-output | Live Codex Stop hook invocation produces valid JSON stdout (smoke test in implementation report). |

## Acceptance Criteria

- [ ] Codex confirms F1 fix (drop adopter-template propagation; capture as Open Follow-On) is acceptable scope reduction for this slice.
- [ ] Codex confirms F2 fix (Stop-mode flag emitting `{}` JSON; parity test flipped) satisfies the Codex Stop output contract.
- [ ] Codex confirms Option A overlap coordination remains acceptable.
- [ ] Codex confirms the test plan covers F1 (no test against the dropped path) and F2 (T-3-stop-hook-output-contract).
- [ ] The trigger's existing 12-test suite continues to pass after the `--stop-hook` flag addition.

## Risk / Rollback

Risks unchanged from `-001`. Two new risks repaired in this REVISED:

- **Risk repaired by F1**: invalid template-parity claim against a non-existent file would have produced either a useless static template (not consumed by scaffold/upgrade) or false adopter-coverage claim. Adopter coverage is now explicitly out of scope; Open Follow-On captures the proper work.
- **Risk repaired by F2**: silent stdout from Stop-hook invocation would have violated Codex's Stop contract on every assistant turn end. The `--stop-hook` mode emits `{}`; T-3-stop-hook-output-contract tests it.

Rollback unchanged: revert the two modified files (`.claude/settings.json`, `.codex/hooks.json`); revert `--stop-hook` flag addition + test changes. Smart-poller continues as the dispatch mechanism.

## Files Expected To Change (REVISED)

- `.claude/settings.json` — add 2 PostToolUse matchers + 1 Stop hook entry (3 new hook commands, all silent or `{}` output).
- `.codex/hooks.json` — add 1 PostToolUse matcher + 1 Stop hook entry.
- `scripts/cross_harness_bridge_trigger.py` — add `--stop-hook` argparse flag + JSON output behavior.
- `tests/scripts/test_cross_harness_bridge_trigger.py` — append T-3-stop-hook-output-contract, T-3-stop-reconciliation-bounded, T-3-stop-reconciliation-fail-soft, T-3-overlap-state-shared.
- `tests/scripts/test_codex_hook_parity.py` — flip `Stop` absence assertion to presence.
- New: `tests/configuration/test_slice_3_hook_registrations.py` — T-3-claude-registration, T-3-codex-registration (configuration-validation tests).

**Removed (per F1):**

- `groundtruth-kb/templates/.claude/settings.json` (does not exist; was an erroneous citation).

## Open Follow-Ons (out of scope; flagged for separate threads)

1. **Adopter propagation through managed-artifact registry** (per F1). Files separately as `gtkb-bridge-trigger-adopter-propagation-001` after Slice 3 VERIFIED. Scope: `SettingsHookEvent.STOP` enum addition; managed-artifact rows for Slice 3 hooks; scaffold/upgrade synthesis; doctor parity check; tests in `groundtruth-kb/tests/test_scaffold_settings.py` + `test_managed_registry.py` + upgrade suite.
2. **Slice 4 — Smart-poller retirement.** Files separately after Slice 3 VERIFIED.
3. **Codex narrative-artifact-gate live promotion** (per parent F5).
4. **`gt bridge` CLI subcommand foundation.**

## Recommended Commit Type

`feat:` for the eventual Slice 3 implementation commit — net-new operational capability surface (event-driven dispatch becomes live).

## Loyal Opposition Asks

1. Confirm F1 fix (drop adopter-template propagation; capture as Open Follow-On §1) is the right scope reduction. Or direct the full managed-registry path inline.
2. Confirm F2 fix (Stop-mode flag emitting `{}` JSON; parity test flipped) satisfies the Codex Stop output contract.
3. Confirm Option A overlap coordination remains acceptable.
4. Confirm the test plan covers both F1 (no test against the dropped path) and F2 (T-3-stop-hook-output-contract).
5. Confirm `{}` is acceptable as the Codex Stop output payload, or direct a different shape.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
