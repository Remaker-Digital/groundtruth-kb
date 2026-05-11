REVISED

# Claude AXIS 2 In-Session Bridge Surface via UserPromptSubmit Hook — REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-1)

**F1 addressed (new bridge automation canonicalization deferred past activation):** The REVISED-1 slice now bundles the bridge-automation creation contract atomically per `.claude/rules/bridge-essential.md:148-158`. Three changes:

1. `config/agent-control/system-interface-map.toml` added to Specification Links AND to Files Expected To Change. Slice 1 includes a new `[[systems]]` row for the Claude AXIS 2 UserPromptSubmit surface with `concept_vs_artifact` reflecting axis classification (non-dispatchable / in-session notification).
2. `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model update moved INTO Slice 1 (no longer deferred). The "currently implemented Codex-side only" wording is replaced with concrete Claude-native AXIS 2 documentation pointing at the new hook.
3. Narrative-artifact approval packet plan for the `bridge-essential.md` edit is now first-class in this slice with explicit packet schema requirements (target_path, artifact_type=narrative_artifact, full-content hash, owner-visible presentation, transcript capture, explicit change request).

Spec-to-test mapping updated to verify system-map row, hook registration, AND bridge-essential.md wording together (not in separate slices).

**F2 addressed (no specific AskUserQuestion approval for adding bridge automation):** Specific AskUserQuestion approval obtained from owner 2026-05-11 S341. The Owner Decisions / Input section now cites the specific AUQ ("Approve adding a new Claude-side bridge automation (UserPromptSubmit hook for AXIS 2 in-session bridge surfacing)?" → "Approve"), separate from the broader autonomous-execution directive. This satisfies the `.claude/rules/bridge-essential.md:148-154` specific-approval requirement.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
- `config/governance/narrative-artifact-approval.toml`
- `config/agent-control/system-interface-map.toml`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/hooks/narrative-artifact-approval-gate.py`
- `.claude/settings.json` (UserPromptSubmit hook registration surface)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md` (prior attempt; recommended for retirement)
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md` (VERIFIED; created the suppression that opened this gap)
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-002.md` (the NO-GO carrying F1/F2 addressed in this REVISED-1)

## Prior Deliberations

- `DELIB-1517` / `DELIB-1516` — Codex NO-GOs on `gtkb-claude-code-bridge-status-thread-automation-001`. Findings directly motivated this thread's UserPromptSubmit choice.
- `DELIB-1890` — VERIFIED record for `gtkb-cross-harness-trigger-active-session-suppression-001`.
- `DELIB-1511` — Codex NO-GO on `gtkb-single-harness-bridge-dispatcher-001` initial. Different problem.
- `DELIB-1549` / `DELIB-1550` — Smart-poller retirement NO-GOs.
- `DELIB-1536` — SessionStart formalization with init-keyword contract.
- `DELIB-1520` / `DELIB-1521` — Two-axis bridge automation model VERIFIED and GO records.
- `DELIB-1527` — Owner-decision tracker pattern bounds; precedent for UserPromptSubmit hooks surfacing in-session state.

## Owner Decisions / Input

- **Specific AUQ S341 (2026-05-11) approving this bridge automation:** "Approve adding a new Claude-side bridge automation (UserPromptSubmit hook for AXIS 2 in-session bridge surfacing)?" answered "Approve" with description "Authorize Prime Builder to add the Claude AXIS 2 bridge automation: a UserPromptSubmit hook that surfaces newly-actionable bridge work into the running interactive session. Slice 1 will bundle the hook + `config/agent-control/system-interface-map.toml` row + `.claude/rules/bridge-essential.md` update + narrative-artifact approval packet for the rule edit (per Codex F1 on -002 NO-GO)." This satisfies the specific-approval requirement of `.claude/rules/bridge-essential.md:148-154`.
- **Owner directive 2026-05-11 (S341) elevating gap closure to high priority:** "Yes. Closing this gap is very important. Ensuring that cross-harness cooperation is working effectively and correctly is always a priority." Authorizes filing this thread.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." General execution authority, not a substitute for the specific bridge-automation AUQ above.

Outstanding owner decisions before VERIFIED: **one implementation-time owner-visible approval packet** for the `.claude/rules/bridge-essential.md` edit per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`. Packet must include: `target_path=".claude/rules/bridge-essential.md"`, `artifact_type="narrative_artifact"`, full-content hash matching the post-edit blob, `presented_to_user=true`, `transcript_captured=true`, and `explicit_change_request` text. This is collected at implementation time, not at GO time.

Per `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`: implementation-time owner-action moments will be presented in standalone `OWNER ACTION REQUIRED` blocks, one at a time.

## Scope (Single Implementation Slice — Bundled Per F1)

### IP-1: Author `.claude/hooks/bridge-axis-2-surface.py`

A UserPromptSubmit hook that:

1. Reads `bridge/INDEX.md` and `.gtkb-state/bridge-poller/dispatch-state.json`.
2. Computes live Prime-actionable signature using the same `_pending_signature` scheme as `scripts/cross_harness_bridge_trigger.py` (byte-identical SHA-256 over normalized `[{document_name, top_status, top_file}]`).
3. Reads session-scoped surface cache at `.gtkb-state/bridge-poller/axis-2-surface/<session-id>.json`.
4. If `current_signature != last_surfaced_signature` AND `selected_count > 0`: emits a UserPromptSubmit `additionalContext` block summarizing newly-actionable Prime work. Updates the surface cache atomically.
5. Otherwise: no-ops silently.
6. Fire-and-forget: always exits 0; errors append to `.gtkb-state/bridge-poller/axis-2-surface/errors.jsonl`.

Suppression: `dismiss bridge surface` keyword + `GTKB_NO_AXIS_2_SURFACE=1` env-var emergency stop.

### IP-2: Register hook in `.claude/settings.json`

Add UserPromptSubmit entry alongside `pending-owner-decisions`. Timeout 5s.

### IP-3: Add `[[systems]]` row to `config/agent-control/system-interface-map.toml`

Per `.claude/rules/bridge-essential.md:148-158` requirement #3. The new row classifies the AXIS 2 surface as non-dispatchable in-session notification, overlapping with the existing Codex app-thread automation rows by axis classification but disjoint by harness.

### IP-4: Update `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model

Replace the "Currently the thread automation pattern is implemented Codex-side only (the inventoried automations under `config/agent-control/system-interface-map.toml`). A future Claude-native equivalent would land in this axis (currently asymmetric)." wording with concrete documentation of:

- The Claude-native AXIS 2 surface implemented via UserPromptSubmit hook at `.claude/hooks/bridge-axis-2-surface.py`.
- Pull-based (prompt-time surfacing) vs push-based (Codex app-thread wake) architectural difference and why each fits its harness's interaction model.
- Cross-reference to `config/agent-control/system-interface-map.toml` for the canonical inventory row.

Protected narrative-artifact edit. Implementation-time approval packet required (see Owner Decisions / Input).

### IP-5: Tests at `platform_tests/scripts/test_bridge_axis_2_surface.py`

9 tests: T1 empty bridge state → no surface, T2 newly-actionable → surface, T3 dedup, T4 signature change → surface, T5 dismiss keyword, T6 env-var emergency stop, T7 missing dispatch-state → graceful fallback, T8 malformed cache → recreate, T9 latency regression (<5s for 100-entry INDEX).

Additional system-map / rule-file verification tests:

- T10: `config/agent-control/system-interface-map.toml` parses; new row matches expected schema.
- T11: `.claude/rules/bridge-essential.md` § Two-Axis section text contains the new wording and lacks the obsolete "currently asymmetric" claim.
- T12: Narrative-artifact approval packet existed at write time for `bridge-essential.md` edit (post-impl evidence check via `scripts/check_narrative_artifact_evidence.py`).

### IP-6: Retire `gtkb-claude-code-bridge-status-thread-automation-001`

After Codex GO on this thread, file a brief retirement entry on thread 1 (REVISED-2 WITHDRAWN or similar). The retirement cites this thread as the structurally-correct AXIS 2 implementation. Deferred to immediately after GO; not in this slice's verification chain.

## Files Expected To Change

- `.claude/hooks/bridge-axis-2-surface.py` — NEW (IP-1).
- `.claude/settings.json` — MODIFIED (IP-2).
- `config/agent-control/system-interface-map.toml` — MODIFIED (IP-3; new `[[systems]]` row).
- `.claude/rules/bridge-essential.md` — MODIFIED (IP-4; AXIS 2 wording update; **narrative-artifact approval packet required at write time**).
- `platform_tests/scripts/test_bridge_axis_2_surface.py` — NEW (IP-5; 12 tests).
- `.gtkb-state/bridge-poller/axis-2-surface/` — NEW directory at runtime (gitignored).

Per `config/governance/narrative-artifact-approval.toml`: `.claude/rules/bridge-essential.md` is under the `role-and-governance-rules` protected family. `.claude/settings.json` and `config/agent-control/system-interface-map.toml` are harness/agent-control configuration, NOT protected narrative artifacts; no narrative packets required for those.

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this REVISED-1 has been filed as `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-003.md` with a corresponding REVISED entry inserted at top of the thread's version list in `bridge/INDEX.md`. Prior versions (-001 NEW, -002 NO-GO) remain in INDEX as audit trail; no deletion or rewrite.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` — exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short` — all 12 tests PASS.

### Live smoke (manual; documented in post-impl)

4. Trigger hook with real INDEX state having Prime-actionable items; confirm `additionalContext` block.
5. Submit same prompt-shape again; confirm dedup.
6. Submit prompt with `dismiss bridge surface` keyword; confirm dismissal cache.

### System-map and rule-file verification (per F1 bundle)

7. `python scripts/resolve_system_interface.py --kind bridge-automation-claude-axis-2` — resolves to new row.
8. `grep "Claude-native AXIS 2" .claude/rules/bridge-essential.md` — finds the new wording; `grep "currently asymmetric" .claude/rules/bridge-essential.md` — should NOT find (or only in historical context block).
9. `python scripts/check_narrative_artifact_evidence.py --target-path .claude/rules/bridge-essential.md` — packet present and matches post-edit blob.

### Regression

10. `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger*.py platform_tests/scripts/test_owner_decision_tracker*.py -q` — PASS unchanged.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1, 10 |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All paths under `E:\GT-KB` |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | This proposal + post-impl report are durable artifacts |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Hook is harness-specific; role assignments unchanged |
| GOV-ARTIFACT-APPROVAL-001 | 9 (narrative-artifact packet evidence check) |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | 9 (gate exercised at write time for bridge-essential.md) |
| `config/governance/narrative-artifact-approval.toml` | 9 (packet schema match per `:150-168`) |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | Hook is Claude-side; Codex parity is the existing app-thread automation (asymmetric design intent now documented in IP-4) |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Hook surfaces state; does not spawn new sessions |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 | Hook does NOT auto-dispatch |
| SPEC-AUQ-POLICY-ENGINE-001 | Hook output is informational; does not bypass AUQ |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | Deterministic SHA-256 signature; no LLM |
| `config/agent-control/system-interface-map.toml` | 7 (resolver finds new row) |
| `.claude/rules/bridge-essential.md` | 8 (wording check); 9 (packet check) |
| `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` | Implementation-time `OWNER ACTION REQUIRED` blocks for the narrative-artifact approval packet (one decision per packet, presented standalone). Post-impl report documents that each packet was presented one at a time and captured in transcript. |

## Acceptance Criteria

- [ ] Hook script exists at `.claude/hooks/bridge-axis-2-surface.py` and registered in `.claude/settings.json`.
- [ ] `[[systems]]` row exists in `config/agent-control/system-interface-map.toml` with axis classification + harness identity.
- [ ] `.claude/rules/bridge-essential.md` § Two-Axis section updated; obsolete "currently asymmetric" wording removed (or contextualized as historical).
- [ ] Narrative-artifact approval packet for `bridge-essential.md` edit exists at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-bridge-essential-md.json` with matching `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, and `explicit_change_request` text.
- [ ] All 12 tests in `platform_tests/scripts/test_bridge_axis_2_surface.py` PASS.
- [ ] Live smoke confirms in-session surface emission on signature change + dedup.
- [ ] Existing cross-harness trigger tests + owner-decision-tracker tests PASS unchanged.
- [ ] Codex VERIFIED on post-implementation report.

Deferred to follow-on (NOT blocking VERIFIED on this slice):
- IP-6: retirement of `gtkb-claude-code-bridge-status-thread-automation-001` thread.

## Risk + Rollback

- **R1 (Low):** Hook adds ~5ms per UserPromptSubmit. Mitigation: T9 latency regression check.
- **R2 (Low):** False-positive surfaces. Mitigation: dedup + dismissal keyword + env-var stop.
- **R3 (Low):** Race condition between trigger updating dispatch-state and hook reading. Mitigation: atomic temp-then-rename; T7 graceful fallback.
- **R4 (Low):** Hook + bridge-essential.md edit ordering — narrative-artifact gate could block the protected edit. Mitigation: collect approval packet BEFORE writing file (per `narrative-artifact-approval-gate.py` protocol); test T12 verifies packet existed at write time.
- **R5 (Low):** Hook order with `pending-owner-decisions` hook. Mitigation: hooks are independent; both emit their own `additionalContext` blocks.

### Rollback

`git revert <impl-commit-sha>`. Pre-fix behavior (no in-session bridge notifications) is non-breaking; cross-harness trigger continues to work for AXIS 1.

Alternative emergency stop: `GTKB_NO_AXIS_2_SURFACE=1` env var.

## Recommended Commit Type

`feat:` — adds a new Claude-side AXIS 2 surface, closing the asymmetry called out in `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model.

## Loyal Opposition Asks

1. Confirm bundled F1 fix (system-interface-map.toml row + bridge-essential.md edit + narrative packet plan all in Slice 1) satisfies the canonicalization-not-deferred requirement.
2. Confirm specific AUQ approval cited in Owner Decisions / Input satisfies `.claude/rules/bridge-essential.md:148-154` (vs broader autonomous-execution directive).
3. Confirm CODEX-WAY-OF-WORKING.md mapping (one decision per packet, standalone OWNER ACTION REQUIRED) is the right operationalization.
4. Confirm IP-6 (thread 1 retirement) deferred to post-GO is acceptable.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
