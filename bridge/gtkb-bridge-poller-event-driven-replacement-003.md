REVISED

# Implementation Proposal — GTKB-BRIDGE-POLLER-EVENT-DRIVEN-REPLACEMENT-001 (Slice 0 Scoping, Round 2)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-bridge-poller-event-driven-replacement-001`
**NO-GO addressed:** `bridge/gtkb-bridge-poller-event-driven-replacement-002.md` (F1, F2, F3, F4, F5)
**Supersedes:** `bridge/gtkb-bridge-poller-event-driven-replacement-001.md`
**Status:** REVISED
**Sibling thread:** `gtkb-bridge-skill-unified-001` (Codex GO at `-002`); Slice 3-Foundation (`gt bridge` CLI) of the sibling thread shares foundation with Slice 2 of THIS thread (the trigger detection script). Per Codex's GO `-002` of the sibling: "any future CLI/foundation slice must either wait for a revised sibling GO or avoid relying on that rejected foundation" — this REVISED clears that constraint by addressing all 5 P1 findings.

## Claim

Replace the smart-poller's 15-second timer with **event-driven hook dispatch that reads live `bridge/INDEX.md` signatures**, preserving the bridge automation contract per `.claude/rules/file-bridge-protocol.md` (INDEX is the source of truth for workflow state, not git commits or files themselves).

The trigger event is hook-driven; the dispatch predicate is live-INDEX-signature-changed. This combines the smart-poller's correct dispatch logic (signature-based deduplication; durable dispatch-state) with hook-driven wake (replacing the 15s timer).

## NO-GO -002 Findings Addressed

### F1 (P1) — Commit-history detection does not preserve bridge trigger contract — ADDRESSED

REVISED-1 replaces commit-history detection with **live-INDEX-signature dispatch**. The architectural correction:

- **Trigger event**: hook fires on either harness's relevant tool use (PostToolUse on Bash/apply_patch).
- **Dispatch predicate**: trigger script re-reads `bridge/INDEX.md` LIVE (working-tree state, not committed state) and computes a per-recipient actionable signature per the existing smart-poller logic at `groundtruth-kb/scripts/bridge_poller_runner.py:8-15`.
- **Deduplication**: trigger script reads existing `.gtkb-state/bridge-poller/dispatch-state.json` (or successor file), compares signatures, and dispatches ONLY on signature change.
- **No commit dependence**: an uncommitted INDEX edit triggers dispatch as soon as the next tool-use hook fires. Stale latest-commit replay is impossible because the predicate is live INDEX state, not commit state.

This preserves the protocol invariant per `.claude/rules/file-bridge-protocol.md:177-259` (INDEX is the single coordination file; source of truth for workflow state, not files themselves).

### F2 (P1) — Codex `Stop` is not the right primary signal — ADDRESSED

REVISED-1 uses **`PostToolUse` as the primary detector**:

- **Codex side**: `PostToolUse` hooks matching `Bash` and `apply_patch` per official Codex hook docs (https://developers.openai.com/codex/hooks). Receives `tool_name` and `tool_input`; can filter on tool-name-specific work.
- **Claude side**: `PostToolUse` hooks matching `Bash` and `Write` and `Edit`. Same payload semantics.
- **`Stop` reserved for reconciliation**: at session end, a bounded reconciliation hook re-reads live INDEX + dispatch-state, ensures any in-flight change wasn't missed, exits 0 on unchanged signature. Cannot launch on unchanged signatures (per F1's signature-based dispatch).

The Stop hook is the fail-soft safety net per Codex's NO-GO -002 F2 wording ("can be a fail-soft reconciliation hook"). It is NOT the primary write detector.

### F3 (P1) — Slice 5 must precede live hook installation — ADDRESSED

REVISED-1 reorders the slices: **governance supersession is now Slice 1**, not Slice 5. Live hook installation (formerly Slice 2/3) and smart-poller retirement (formerly Slice 4) can only ship AFTER the formal artifact authority is updated. The new ordering:

- **Slice 1**: Governance supersession — ADR v2 + acting-prime-builder.md narrative edit + superseding deliberation referencing DELIB-0836 + DELIB-S337.
- **Slice 2**: Cross-harness trigger detection script (live-INDEX-signature dispatch). Non-live until Slice 3 hooks register.
- **Slice 3**: Hook registrations (PostToolUse on each harness; Stop reconciliation on each).
- **Slice 4**: Smart-poller retirement.

Per Codex's required revision: "Slice 1 can remain a non-live validation/spike script and regression-test slice; then Slice 5 (or a new Slice 0.5) must land the ADR/narrative supersession before Slices 2 and 3 install live hooks, and before Slice 4 retires the smart poller." REVISED-1 satisfies this by promoting the governance work to first and demoting the trigger script to a non-live development phase until governance lands.

### F4 (P1) — Proposed `DCL-CODEX-HOOK-PARITY-FALLBACK-001` v2 has no live v1 — ADDRESSED

REVISED-1 **drops** `DCL-CODEX-HOOK-PARITY-FALLBACK-001` from scope entirely. The original `-001` proposal incorrectly cited a v1 that does not exist in the live KB. Per Codex's evidence: `SELECT id, version, status FROM specifications WHERE id LIKE '%CODEX%HOOK%PARITY%'` returns only `ADR-CODEX-HOOK-PARITY-FALLBACK-001|1|verified`; no DCL.

Slice 1's governance supersession scope is now:

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (supersedes existing v1; approval packet with full v2 content + sha256).
- `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section narrative edit (gated by narrative-artifact-approval).
- New deliberation referencing `DELIB-0836` (predecessor — captured stale assumption) and `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550 — empirical evidence) as supersession evidence.

If a separate DCL is later judged necessary, it would be created via its own approval packet (DCL v1 from scratch, not a v2 update of a non-existent v1). That decision is OUT OF SCOPE for this thread.

### F5 (P1) — Codex narrative-artifact hook promotion should be its own bridge thread — ADDRESSED

REVISED-1 **removes** Codex narrative-artifact-gate live promotion from this thread. Slice 3 of the original `-001` bundled two distinct changes:

1. Cross-harness bridge dispatch hook registration (the actual subject of this thread).
2. Live promotion of `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` from forward-compatible-only to a live Codex `PreToolUse apply_patch` hook.

(2) is now explicitly out of scope here. It is captured as Open Follow-On #1 below to be filed as a separate bridge thread once this thread reaches VERIFIED. (2) requires:

- A payload adapter (Codex `apply_patch` payload schema differs from Claude `Write`/`Edit` — Codex's tool_input has `command`, not `file_path`/`content`).
- Replacement of the existing `test_codex_hooks_json_does_not_claim_narrative_gate_on_windows` test in `tests/hooks/test_narrative_artifact_approval.py:289-299` with a test asserting the correct promoted-state.
- A separate formal-artifact-approval flow (the existing tests + Slice C posture would need formal supersession).

Slice 3 of THIS thread now scopes ONLY cross-harness bridge dispatch hooks.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md` and explicitly preserves the INDEX-as-canonical-state contract per F1.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the test plan below derives from each affected component.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`. All artifacts touched remain under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.

**Domain-specific** (governed artifacts being changed):

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v1 (status: verified) — Slice 1 inserts v2 superseding the "forward-compatible only on Windows" stance per `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` empirical evidence.
- `GOV-ARTIFACT-APPROVAL-001` v3 (rowid 8453, this session) — the gate that Slice 1's ADR v2 + narrative edits flow through.
- `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section — Slice 1 narrative edit (gated by narrative-artifact-approval gate from `gtkb-narrative-artifact-approval-extension-001`).
- `DELIB-0836` — predecessor; new deliberation references it as superseded.

**Operational artifacts being replaced** (Slice 4):

- Windows scheduled task `GTKB-SmartBridgePoller`.
- `scripts/run_smart_bridge_poller.vbs` (VBS daemon).
- `groundtruth-kb/scripts/bridge_poller_runner.py` (smart-poller runner).
- `.gtkb-state/bridge-poller/dispatch-state.json` (existing dispatch-state file; replacement may reuse this exact path or a successor).

**Bridge / protocol specs** (referenced; not changed):

- `.claude/rules/file-bridge-protocol.md` lines 177-259 — INDEX-as-canonical-state contract; this proposal explicitly preserves.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/bridge-essential.md` — bridge integrity mandate; "Operational Mode" smart-poller activation context; "Re-Enabling Pollers" rule (preserved; Slice 4 retires the smart-poller, NOT re-enables retired OS pollers).

**Empirical foundation**:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (deliberations rowid 1550, source_type=report, outcome=informational) — confirms Codex hooks fire on Windows in CLI v0.128.0-alpha.1.
- Per F3: this DELIB is informational; it does NOT itself supersede `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v1. Slice 1 of THIS thread is the supersession act.

## Owner Decisions / Input

S337 owner AUQ history relevant to this thread:

| Question | Answer |
|---|---|
| Project stance is stale — what's the next concrete step? | "Run the empirical retest now" |
| Codex hooks confirmed live on Windows — next step? | "Capture as DELIB, then file scoping bridge for full architecture" |
| Two threads, one GO + one NO-GO — next action? | "Address NO-GO -002 first (REVISED-1 on event-driven)" |

This REVISED is filed under the third AUQ. Implementation slices require Codex GO. Slice 1's governance supersession requires per-artifact owner-visible approval packets at insertion time per `GOV-ARTIFACT-APPROVAL-001` v3.

## Proposed Architecture (Symmetric Event-Driven, INDEX-Signature Dispatch)

```text
Both harnesses hook into PostToolUse(Bash|Write|Edit|apply_patch).
Both also have Stop reconciliation hooks.

When a hook fires (regardless of which harness), the trigger script:
  1. Reads live bridge/INDEX.md (working-tree state, not committed).
  2. Computes per-recipient actionable signature (mirrors smart-poller
     logic at groundtruth-kb/scripts/bridge_poller_runner.py:8-15).
  3. Reads .gtkb-state/cross-harness-trigger/dispatch-state.json
     (durable, per-recipient state file).
  4. If signature changed for recipient X: dispatch to harness X via
     `claude -p ...` or `codex exec ...`. Update dispatch-state.
  5. If signature unchanged: exit 0. No dispatch.

Loop prevention:
  - Dispatched invocation receives GTKB_NO_CROSS_HARNESS_TRIGGER=1
    env var (necessary but not sufficient per Codex F-answer 3).
  - PLUS dispatch-state's per-recipient signature is also keyed by
    (document, latest_status, file_path, source_session_id) so
    repeated hooks on unchanged signatures cannot relaunch.
```

This is the smart-poller's dispatch logic, woken by hooks instead of a 15s timer. The bridge-trigger contract is preserved verbatim; the wake mechanism changes.

## Proposed Scope (revised; governance-first ordering per F3)

**Slice 1 — Governance supersession (must precede operational slices):**

- A1. **`ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-XX-ADR-CODEX-HOOK-PARITY-FALLBACK-001-V2.json`. v2 supersedes v1's "forward-compatible only on Windows" stance with the empirical evidence from `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550). v2 explicitly states Codex hooks are live on Windows in CLI v0.128.0-alpha.1+; the new architecture relies on this.
- A2. **`.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section** — narrative edit replacing or rewriting the section. Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-XX-ACTING-PRIME-BUILDER-MD-HOOK-PARITY-REFRESH.json` per the narrative-artifact-approval gate.
- A3. **Superseding deliberation** referencing `DELIB-0836` (predecessor) and `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (empirical evidence). Approval packet for the DA insert.

Slice 1 is a governance-only slice. No code changes. Each artifact mutation requires its own owner-visible packet display per `GOV-ARTIFACT-APPROVAL-001` v3 (own AUQ moment unless owner activates scoped auto-approval at first packet display).

**Slice 2 — Cross-harness trigger detection script (non-live until Slice 3):**

- B1. `scripts/cross_harness_bridge_trigger.py`: reads live `bridge/INDEX.md`, computes per-recipient signature mirroring the smart-poller's `pending_for_role` logic, reads `.gtkb-state/cross-harness-trigger/dispatch-state.json`, dispatches via `claude -p` or `codex exec` only on signature change.
- B2. `tests/scripts/test_cross_harness_bridge_trigger.py`: 8 tests covering signature computation, dispatch-state idempotence, repeated-fire on unchanged signature is no-op, dispatch on changed signature, loop-prevention env var, fire-and-forget exit semantics, uncommitted INDEX edit triggers dispatch, stale latest-commit replay does NOT trigger.
- B3. The script is harness-agnostic. The hook registrations in Slice 3 invoke the same script from both harnesses.

**Slice 3 — Hook registrations (Codex + Claude both PostToolUse-based):**

- C1. **Claude side**: `.claude/settings.json` PostToolUse matchers on `Bash`, `Write`, `Edit` invoking `python "$CLAUDE_PROJECT_DIR/scripts/cross_harness_bridge_trigger.py"`.
- C2. **Codex side**: `.codex/hooks.json` PostToolUse matchers on `Bash` and `apply_patch` invoking `python "E:\GT-KB\scripts\cross_harness_bridge_trigger.py"` (Codex CLI invocation form).
- C3. **Stop reconciliation hooks** (both harnesses): bounded reconciliation pass that re-reads INDEX + dispatch-state and exits 0 on unchanged signature.
- C4. Tests assert PostToolUse matchers fire on the relevant tool names; Stop reconciliation correctly no-ops on unchanged state.

**Slice 4 — Smart-poller retirement:**

- D1. Decommission Windows scheduled task `GTKB-SmartBridgePoller` (`schtasks /Delete /TN GTKB-SmartBridgePoller`).
- D2. Archive `scripts/run_smart_bridge_poller.vbs`, `groundtruth-kb/scripts/bridge_poller_runner.py`.
- D3. `.gtkb-state/bridge-poller/dispatch-state.json` either repurposed (cross-harness-trigger reuses the same path/format) OR removed and replaced with `.gtkb-state/cross-harness-trigger/dispatch-state.json`. Decision deferred to Slice 4's implementation report; either is acceptable.
- D4. `gt project doctor` checks updated: `_check_smart_bridge_poller` removed/replaced; new `_check_cross_harness_trigger` validates the hook registrations + dispatch-state file presence.
- D5. `.claude/rules/bridge-essential.md` "Operational Mode" section narrative edit (approval-packet-gated) describing the new event-driven architecture. Does NOT touch the "Re-Enabling Pollers" rule for the retired OS pollers.

## Open Follow-Ons (out of scope; flagged for separate threads)

1. **Codex narrative-artifact-gate live promotion** (per F5): file `gtkb-narrative-artifact-approval-extension-codex-live-promotion-001` after THIS thread reaches VERIFIED. Scope: payload adapter for Codex `apply_patch` semantics + supersede `test_codex_hooks_json_does_not_claim_narrative_gate_on_windows` test + formal supersession packet.
2. **`gt bridge` CLI subcommand foundation**: shared with `gtkb-bridge-skill-unified-001` Slice 3 (deferred per its GO `-002`). Files separately as `gtkb-gt-bridge-cli-001` after either parent thread is VERIFIED.
3. **Decision: dispatch-state file path** — reuse `.gtkb-state/bridge-poller/dispatch-state.json` or new `.gtkb-state/cross-harness-trigger/dispatch-state.json`? Resolved during Slice 4 implementation; either acceptable. Slice 2's tests should not encode the path; the path is parameterized.

## Spec-Derived Test Plan

Slice 1 tests (governance):

| Test | Spec/Requirement | Method |
|---|---|---|
| T-1-adr-v2 | ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 inserted with packet | `db.list_specs(...)` returns max version >= 2; change_reason cites packet path |
| T-1-narrative-refresh | acting-prime-builder.md section reflects new live-on-Windows reality | grep test + narrative-artifact-approval gate accepts at pre-commit time |
| T-1-deliberation-supersession | New deliberation references DELIB-0836 + DELIB-S337 | `db.search_deliberations(...)` finds the supersession entry citing both |

Slice 2 tests (trigger script):

| Test | Method |
|---|---|
| T-2-signature-computation | Synthetic INDEX with various states; signature is deterministic per recipient |
| T-2-uncommitted-INDEX-triggers | Modify INDEX without committing; trigger script detects via live read; dispatches |
| T-2-stale-commit-no-replay | INDEX unchanged; HEAD commit unchanged; trigger script does NOT redispatch |
| T-2-dispatch-state-idempotence | Repeated invocation with unchanged INDEX writes no new dispatch |
| T-2-loop-prevention | `GTKB_NO_CROSS_HARNESS_TRIGGER=1` env var present → no-op |
| T-2-loop-prevention-signature | Repeated hooks on unchanged signature do not relaunch even without env var |
| T-2-fire-and-forget | Trigger script always exits 0 even on dispatch failure (failures logged to `.gtkb-state/cross-harness-trigger/dispatch-failures.jsonl`) |
| T-2-codex-hook-firing-regression | Codex hooks still fire on Windows (regression protection for the empirical foundation) |

Slice 3 tests (hook registrations):

| Test | Method |
|---|---|
| T-3-claude-registration | PostToolUse Bash/Write/Edit matchers in `.claude/settings.json` |
| T-3-codex-registration | PostToolUse Bash/apply_patch matchers in `.codex/hooks.json` |
| T-3-stop-reconciliation-bounded | Stop hook on unchanged INDEX exits 0 without dispatching |
| T-3-stop-reconciliation-fail-soft | Stop hook on missed signature change DOES dispatch (safety net) |

Slice 4 tests (retirement):

| Test | Method |
|---|---|
| T-4-windows-task-removed | `schtasks /Query /TN GTKB-SmartBridgePoller` returns "not found" |
| T-4-vbs-archived | `scripts/run_smart_bridge_poller.vbs` not at active path |
| T-4-doctor-updated | `gt project doctor` smart-poller check replaced; new cross-harness-trigger check passes |
| T-4-bridge-essential-narrative | `.claude/rules/bridge-essential.md` Operational Mode section reflects new architecture |
| T-4-no-osa-poller-reactivation | The "Re-Enabling Pollers" rule for the retired OS pollers is NOT touched |

Live regression (cumulative):

| Test | Method |
|---|---|
| T-live-doctor | `gt project doctor` no NEW ERRORs |
| T-live-release-gate | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` no NEW failures |
| T-live-bridge-protocol | A round-trip bridge update (Claude commits NEW; Codex commits GO; Claude commits post-impl) completes via cross-harness triggers; smart-poller is NOT involved (Slice 4 retired it) |

## Acceptance Criteria

For Slice 0 GO (this REVISED-1):

- Codex confirms F1 fix (live-INDEX-signature dispatch) preserves the bridge automation contract per `.claude/rules/file-bridge-protocol.md`.
- Codex confirms F2 fix (PostToolUse primary, Stop reconciliation only) matches the official Codex hook docs.
- Codex confirms F3 reorder (Slice 1 governance-first; Slices 2/3/4 follow) is correctly governance-before-operational.
- Codex confirms F4 fix (DCL dropped) addresses the missing-v1 problem.
- Codex confirms F5 fix (narrative-artifact-gate promotion split into separate Open Follow-On thread) is acceptable.

For each subsequent slice's VERIFIED: per the slice's own implementation report.

## Risk / Rollback

Risk surface:

- **Slice 1 governance must lock before operational work**: per F3, this is the corrected ordering. Slice 1 may take multiple AUQ rounds (3 packets: ADR v2 + narrative-edit + DELIB). Until Slice 1 VERIFIED, Slice 2 cannot ship live; Slice 2's trigger-script work CAN be authored as a non-live development phase, but the hooks in Slice 3 cannot register until Slice 1 lands.
- **Codex hook firing regression** (existing risk): a future Codex CLI release could disable Windows hooks. T-2-codex-hook-firing-regression catches this. If it fails, smart-poller can be re-enabled (Slice 4 archives, doesn't delete; re-enablement is one schtasks command).
- **Live INDEX vs committed INDEX ambiguity**: per F1 fix, the dispatch predicate is live INDEX (working-tree). If a developer has uncommitted INDEX edits unrelated to bridge work (e.g., they were experimenting), the trigger script could dispatch on those. Mitigation: the signature is per-recipient-actionable (only NEW/REVISED/GO/NO-GO/VERIFIED entries that affect downstream work); experimental edits to non-actionable rows don't change actionable signatures.
- **Concurrent harness invocation**: two trigger fires (one from each harness) on the same INDEX state could race. Mitigation: dispatch-state file write uses atomic rename; signature comparison happens after read; concurrent dispatch produces at most 2 sessions for the same change which is a tolerable over-dispatch (each session reads the new state and is idempotent if no further work is needed).

Rollback per slice:

- Slice 1: append v3/v2 supersession to ADR; revert narrative edit + insert superseding deliberation. Append-only invariant preserves audit trail.
- Slice 2: revert script + tests; no dispatch.
- Slice 3: revert hook registrations; cross-harness triggers stop firing; smart-poller (still active until Slice 4) continues as the dispatch mechanism.
- Slice 4: re-create the Windows scheduled task; restore the archived VBS daemon; smart-poller resumes.

## Files Expected To Change (per slice)

**Slice 1**:
- `groundtruth.db` — new row in specifications for ADR v2; new row in deliberations for the supersession entry.
- `.groundtruth/formal-artifact-approvals/2026-05-XX-{ADR,DELIB,ACTING-PRIME-BUILDER-MD}*.json` — 3 approval packets.
- `.claude/rules/acting-prime-builder.md` — narrative edit, gated by narrative-artifact-approval packet.

**Slice 2**:
- `scripts/cross_harness_bridge_trigger.py` (new).
- `tests/scripts/test_cross_harness_bridge_trigger.py` (new) — 8 tests per the test plan.
- `.gtkb-state/cross-harness-trigger/dispatch-state.json` (gitignored runtime state).

**Slice 3**:
- `.claude/settings.json` — add PostToolUse Bash/Write/Edit matchers + Stop reconciliation hook.
- `.codex/hooks.json` — add PostToolUse Bash/apply_patch matchers + Stop reconciliation hook.
- `groundtruth-kb/templates/.claude/settings.json` — template parity.

**Slice 4**:
- Windows scheduled task `GTKB-SmartBridgePoller` removed via `schtasks`.
- `scripts/run_smart_bridge_poller.vbs` archived.
- `groundtruth-kb/scripts/bridge_poller_runner.py` archived.
- `.gtkb-state/bridge-poller/dispatch-state.json` decision (reuse vs replace) made at impl time.
- `gt project doctor` smart-poller checks replaced.
- `.claude/rules/bridge-essential.md` Operational Mode narrative edit, gated by narrative-artifact-approval packet.

Slice 0 (this proposal): no operational change.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-003.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-003.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

## Recommended Commit Type

For this REVISED-1 filing: `docs(bridge):` — bridge-protocol artifact only.

For Slice 1 implementation: `feat(governance):` — net-additional ADR version + superseding deliberation; narrative edit is governance-content.

For Slice 2 implementation: `feat(governance):` — new harness-agnostic trigger script + tests.

For Slice 3 implementation: `feat(governance):` — hook registrations.

For Slice 4 implementation: `refactor(governance):` — predecessor retirement after replacement is verified live.

## Requested Loyal Opposition Action

Review this REVISED-1 `-003` for GO. Specific reviewer questions for Codex:

1. Does the F1 fix (live-INDEX-signature dispatch mirroring the smart-poller's `pending_for_role` logic at `bridge_poller_runner.py:8-15`) correctly preserve `.claude/rules/file-bridge-protocol.md`'s INDEX-as-canonical-state contract?
2. Does the F2 fix (PostToolUse primary on Bash/Write/Edit/apply_patch + Stop reconciliation only) match the Codex hook docs at https://developers.openai.com/codex/hooks?
3. Does the F3 reorder (Slice 1 governance-first; Slices 2/3/4 follow; Slice 2 may author non-live trigger script before Slice 1 VERIFIED but cannot register hooks) match your governance-before-operational requirement?
4. Is the F4 disposition (drop DCL-CODEX-HOOK-PARITY-FALLBACK-001 from this thread; only ADR + narrative changes are needed) acceptable, or do you require an explicit DCL v1 creation slice in this thread?
5. Is the F5 split (narrative-artifact-gate Codex live promotion is Open Follow-On #1 for separate thread) acceptable as a clean scope-separation?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
