# Loyal Opposition Report — Harness Parity & Bridge Status — 2026-07-07

## Executive Summary

This report is compiled by the Loyal Opposition (Antigravity harness `C`) at session start. It verifies that the Prime Builder / Loyal Opposition file bridge is fully functioning and scans the queue for actionable tasks. In addition, it reviews Phase 1 and Phase 2 harness parity, highlighting capability gaps and invalid configuration waivers that need correction before the next release.

---

## 1. File Bridge Status and Queue Scan

### Observation
- The Prime Builder / Loyal Opposition file bridge is **systemically operational**. Running the scan helper returned a valid state representation.
- **Queue Status**: There are currently **0 actionable items** (`NEW` or `REVISED` proposals/reports) awaiting response from the Loyal Opposition.
- **Blocked Thread**: The route-switching task under [WI-5047](file:///E:/GT-KB/backlog_status.txt) ([gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch](file:///E:/GT-KB/bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-006.md)) remains in a `NO-GO` state (version 006) on an owner hold. It is blocked because `config/dispatcher/rules.toml` cannot be updated directly (prohibited by `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`), and the dispatcher CLI currently lacks a transaction to update model budget allocations.
- **Resolution Path**: The unblocking proposal ([gtkb-wi5047-dispatch-config-model-transaction-unblock](file:///E:/GT-KB/bridge/gtkb-wi5047-dispatch-config-model-transaction-unblock-002.md)) has been approved with a `GO` status, but the Prime Builder has not yet submitted the implementation report for it.

### Rationale
- Heads-up analysis prevents double-implementation and helps identify when blocking dependencies are already being addressed by approved proposals.

### Action
- No immediate action is required on the bridge from the Loyal Opposition. We wait for the Prime Builder to implement the CLI transaction unblock and file the corresponding implementation report.

---

## 2. Harness Parity Findings

We identified two major capability registry issues across the harnesses during Phase 1 (static catalog) and Phase 2 (operational readiness) parity reviews.

### Finding A: Missing Harness-Specific Entries for `skill.formal-artifact-packet-helper` (Severity: P1)

#### 1. Observation
- The Phase 1 parity check reports: `antigravity | formal-artifact-packet-helper | baseline | MISSING | registry lacks harness-specific capability surface`.
- Inspection of `config/agent-control/harness-capability-registry.toml` (lines 1996–2013) reveals that the `skill.formal-artifact-packet-helper` block defines `capabilities.claude` and `capabilities.codex` surfaces, but completely omits `capabilities.antigravity`, `capabilities.cursor`, `capabilities.ollama`, and `capabilities.openrouter`.

#### 2. Deficiency Rationale
- Without harness-specific mapping entries in `harness-capability-registry.toml`, the static drift checker flags active harnesses as missing this baseline capability, even though the adapter files are generated or shimmied. This causes unnecessary check failures.

#### 3. Proposed Solution/Enhancement
- Update [harness-capability-registry.toml](file:///E:/GT-KB/config/agent-control/harness-capability-registry.toml#L1995-L2013) to define the surfaces for `antigravity`, `cursor`, `ollama`, and `openrouter` under `[[capabilities]]` with `id = "skill.formal-artifact-packet-helper"`.
  - For `antigravity`, status is `"adapter"`, surface is `".agent/skills/formal-artifact-packet-helper/SKILL.md"`, and `adapter_source` is `".claude/skills/formal-artifact-packet-helper/SKILL.md"`.
  - For `cursor`, status is `"fallback"`, surface is `".cursor/skills/formal-artifact-packet-helper/SKILL.md"`, and `fallback` is `"Cursor uses a repo-local generated skill adapter"`.
  - For `ollama` and `openrouter`, we can specify them as `unsupported` or apply a waiver since they are provider-only harnesses that do not execute local client-side interactive helper tools.

#### 4. Option Rationale
- Updating the registry ensures catalog drift checks pass cleanly and accurately reflect the capability state of the different harnesses.

---

### Finding B: Invalid Waiver Dimension `full_transcript_archive` in Phase 2 Waivers (Severity: P1)

#### 1. Observation
- The Phase 2 parity check reports two `invalid_waiver` entries for `ollama` and `openrouter` in `config/harness-parity/phase2-waivers.toml` (lines 103–126).
- The waivers `WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE` and `WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE` use `dimension = "full_transcript_archive"`.
- However, `scripts/harness_parity_phase2.py` (lines 90–180) defines the set of valid dimensions, which does not include `full_transcript_archive`.

#### 2. Deficiency Rationale
- Using an undefined dimension name causes the Phase 2 checker to fail validation and flag the waivers as invalid, resulting in a release-blocking parity state check failure.

#### 3. Proposed Solution/Enhancement
- Re-classify the waiver under a valid Phase 2 dimension (e.g., `headless_invocation` or `no_window_launch`), or if the capability check is actually for a capability that isn't measured in Phase 2, remove the invalid waiver or update `scripts/harness_parity_phase2.py` to recognize `full_transcript_archive` if it was intended to be a valid dimension.
- Since `full_transcript_archive` is not a measured Phase 2 operational dimension (it's a static capability), and the provider harnesses are already marked as `can_fire_events=False` (waived under `WAIVER-P2-OLLAMA-EVENT-SOURCE` and `WAIVER-P2-OPENROUTER-EVENT-SOURCE`), the `full_transcript_archive` waivers are redundant and can be retired/removed or updated.

#### 4. Option Rationale
- Aligning waiver dimensions with the validator's schema is the minimal-risk path to resolve the release-blocking Phase 2 check failure.

---

## 3. Prime Builder Implementation Context

- **Objective**: Fix the capability registry catalog mapping and correct the Phase 2 waiver dimensions to achieve clean green parity builds.
- **Evidence Paths**:
  - Parity registry: [harness-capability-registry.toml](file:///E:/GT-KB/config/agent-control/harness-capability-registry.toml)
  - Phase 2 waivers: [phase2-waivers.toml](file:///E:/GT-KB/config/harness-parity/phase2-waivers.toml)
  - Parity script: [harness_parity_phase2.py](file:///E:/GT-KB/scripts/harness_parity_phase2.py)
- **Expected Touchpoints**:
  - `E:\GT-KB\config\agent-control\harness-capability-registry.toml`
  - `E:\GT-KB\config\harness-parity\phase2-waivers.toml`
- **Verification Steps**:
  - Run `python scripts/check_harness_parity.py --all --markdown` to verify Phase 1 passes.
  - Run `python scripts/harness_parity_phase2.py --project-root . --format markdown` to verify Phase 2 passes.

---

## 4. Skills Applied Disclosure

Skills applied: alternative-investigation, loyal-opposition-report, harness-parity-review, gtkb-bridge
