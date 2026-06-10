REVISED

# Claude AXIS 2 In-Session Bridge Surface via UserPromptSubmit Hook — REVISED-2

bridge_kind: prime_proposal
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 005 (REVISED-2 post NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-2)

**F1 addressed (proposed verification commands don't exist in current CLI surface):** All verification commands probed against live `--help` surfaces before inclusion this pass.

- Resolver verification command corrected from `python scripts/resolve_system_interface.py --kind bridge-automation-claude-axis-2` to `python scripts/resolve_system_interface.py bridge-automation-claude-axis-2 --json` (positional `term` + `--json` flag per `scripts/resolve_system_interface.py:223-228`). The Slice 1 implementation must add the new `[[systems]]` row with `id` or canonical alias such that this positional resolver call returns the new row.
- Narrative-evidence verification command corrected from `python scripts/check_narrative_artifact_evidence.py --target-path .claude/rules/bridge-essential.md` to **two** complementary forms per the live CLI surface (`scripts/check_narrative_artifact_evidence.py:273-282`):
  1. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/bridge-essential.md --json` — runs after the protected file and matching packet are staged; verifies the staged blob's sha256 matches the packet's `full_content_sha256`.
  2. `python scripts/check_narrative_artifact_evidence.py --staged --json` — runs as the commit-ready full-stage check (runs UNDER `.githooks/pre-commit` already; the explicit invocation in the post-impl report documents that the staging-state check was exercised).

**F2 addressed (regression command not executable in Windows/PowerShell):** Regression command corrected to enumerate actual files probed via `find . -name "test_*"`:

Cross-harness trigger test files (4 found):
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py`

Owner-decision-tracker test files (3 found):
- `platform_tests/hooks/test_owner_decision_tracker.py` (primary)
- `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py`
- `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py`

Regression command updated to use explicit file enumeration (no glob expansion ambiguity on Windows/PowerShell).

**Carry-forward from REVISED-1:** F1/F2 from -002 (canonicalization bundle + specific AUQ approval) remain addressed; Shape C + slice progression with in-slice verification remain the recommended approach.

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
- `.claude/settings.json`
- `scripts/resolve_system_interface.py`
- `scripts/check_narrative_artifact_evidence.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-002.md` (initial NO-GO; addressed in REVISED-1)
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-004.md` (REVISED-1 NO-GO; addressed in this REVISED-2)
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md` (VERIFIED; created the suppression that opened this gap)
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md` (prior attempt; recommended for retirement)

## Prior Deliberations

(Carry-forward from REVISED-1, unchanged): `DELIB-1517` / `DELIB-1516` (prior periodic-spawn NO-GOs), `DELIB-1890` (active-session-suppression VERIFIED), `DELIB-1511` (single-harness dispatcher NO-GO), `DELIB-1549` / `DELIB-1550` (smart-poller retirement NO-GOs), `DELIB-1536` (SessionStart init-keyword contract), `DELIB-1520` / `DELIB-1521` (two-axis bridge automation model), `DELIB-1527` (owner-decision tracker pattern bounds).

## Owner Decisions / Input

(Carry-forward from REVISED-1, unchanged):

- **Specific AUQ S341 (2026-05-11) approving this bridge automation:** "Approve adding a new Claude-side bridge automation (UserPromptSubmit hook for AXIS 2 in-session bridge surfacing)?" answered "Approve". Satisfies `.claude/rules/bridge-essential.md:148-154`.
- **Owner directive 2026-05-11 (S341) elevating gap closure to high priority:** "Yes. Closing this gap is very important."
- **AUQ S341 (2026-05-11) autonomous-execution directive:** broad execution authority.

Outstanding owner decisions before VERIFIED: one implementation-time owner-visible narrative-artifact approval packet for the `.claude/rules/bridge-essential.md` edit (collected at implementation time per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`). Per CODEX-WAY-OF-WORKING.md: the packet will be presented in a standalone `OWNER ACTION REQUIRED` block, one decision per packet.

## Scope

(Unchanged from REVISED-1, single implementation slice bundled per F1 of -002):

- **IP-1:** `.claude/hooks/bridge-axis-2-surface.py` UserPromptSubmit hook (reads INDEX + dispatch-state, computes signature via existing `_pending_signature` scheme, surfaces newly-actionable Prime work to running session, deduplicates via session-scoped cache, supports `dismiss bridge surface` keyword + `GTKB_NO_AXIS_2_SURFACE=1` emergency stop).
- **IP-2:** Register hook in `.claude/settings.json` UserPromptSubmit array.
- **IP-3:** Add `[[systems]]` row to `config/agent-control/system-interface-map.toml` with axis classification (non-dispatchable / in-session notification) and Claude-harness identity. The row's `id` (or accepted alias) MUST resolve to `bridge-automation-claude-axis-2` via the positional resolver call in test 7 below.
- **IP-4:** Update `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model — replace "currently implemented Codex-side only / asymmetric" wording with concrete Claude-native AXIS 2 documentation. Narrative-artifact approval packet collected at write time per IP plan.
- **IP-5:** `platform_tests/scripts/test_bridge_axis_2_surface.py` — 12 tests (T1-T9 hook behavior; T10 system-map row schema; T11 rule-file wording; T12 narrative-artifact evidence post-impl).
- **IP-6 (DEFERRED):** Retire `gtkb-claude-code-bridge-status-thread-automation-001` after Codex GO on this thread.

## Files Expected To Change

- `.claude/hooks/bridge-axis-2-surface.py` — NEW.
- `.claude/settings.json` — MODIFIED.
- `config/agent-control/system-interface-map.toml` — MODIFIED.
- `.claude/rules/bridge-essential.md` — MODIFIED (narrative packet required at write time).
- `platform_tests/scripts/test_bridge_axis_2_surface.py` — NEW (12 tests).
- `.gtkb-state/bridge-poller/axis-2-surface/` — NEW directory (gitignored).

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this REVISED-2 has been filed as `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md` with a corresponding REVISED entry inserted at top of the thread's version list in `bridge/INDEX.md`. Prior versions (-001 through -004) remain as audit trail.

## Test Plan (REVISED-2)

All commands below were probed against live `--help` surfaces before inclusion. Each is executable in the declared Windows/PowerShell environment at `E:\GT-KB`.

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` — exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short` — all 12 tests PASS.

### Live smoke (manual; documented in post-impl)

4. Trigger hook with real INDEX state having Prime-actionable items; confirm `additionalContext` block emitted.
5. Submit same prompt-shape again; confirm dedup.
6. Submit prompt with `dismiss bridge surface` keyword; confirm dismissal cache.

### System-map and rule-file verification (per F1 bundle from -002)

7. **System-map row resolves** (REVISED command per F1 of -004):
   ```
   python scripts/resolve_system_interface.py bridge-automation-claude-axis-2 --json
   ```
   Expected: JSON output describing the new `[[systems]]` row (axis classification, harness, related rule paths).

8. **Rule wording check:**
   ```
   grep "Claude-native AXIS 2" .claude/rules/bridge-essential.md
   ```
   Expected: finds the new wording; the obsolete "currently asymmetric" phrasing should be absent or contextualized as historical.

9. **Narrative-artifact evidence — staged form** (REVISED command per F1 of -004):
   ```
   python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/bridge-essential.md --json
   ```
   Run AFTER the protected file and matching packet are staged via `git add`. Expected exit 0; JSON output confirms packet's `full_content_sha256` matches the staged blob's sha256.

10. **Narrative-artifact evidence — commit-ready form** (REVISED command per F1 of -004):
    ```
    python scripts/check_narrative_artifact_evidence.py --staged --json
    ```
    Documents the staging-state check that runs UNDER `.githooks/pre-commit`. Expected exit 0 once packet is present.

### Regression (REVISED enumeration per F2 of -004)

Cross-harness trigger tests (probed file paths):

```
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py -q
```

Owner-decision-tracker tests (probed file paths):

```
python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q
```

11. Combined regression — all PASS unchanged.

### Spec-to-test mapping (REVISED references)

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1, 11 |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All paths under `E:\GT-KB` |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | This proposal + post-impl report |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Hook is harness-specific; role assignments unchanged |
| GOV-ARTIFACT-APPROVAL-001 | 9, 10 (narrative-artifact packet evidence) |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | 9, 10 |
| `config/governance/narrative-artifact-approval.toml` | 9, 10 (packet schema match per `:150-168`) |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | IP-4 documents asymmetric design intent |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Hook surfaces state; does not spawn new sessions |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 | Hook does NOT auto-dispatch |
| SPEC-AUQ-POLICY-ENGINE-001 | Hook output is informational |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | Deterministic SHA-256 signature |
| `config/agent-control/system-interface-map.toml` | 7 |
| `.claude/rules/bridge-essential.md` | 8, 9, 10 |
| `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` | Implementation-time narrative-artifact approval packet presented in standalone `OWNER ACTION REQUIRED` block, one per packet |

## Acceptance Criteria (Unchanged from REVISED-1)

- [ ] Hook script + registration + new `[[systems]]` row + `bridge-essential.md` AXIS 2 update all land in Slice 1.
- [ ] Narrative-artifact approval packet for `bridge-essential.md` edit exists with matching sha256.
- [ ] All 12 tests PASS.
- [ ] Live smoke confirms in-session surface emission + dedup + dismissal.
- [ ] Existing trigger + owner-decision-tracker tests PASS (test 11 enumeration).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback (Unchanged from REVISED-1)

R1-R5 mitigations preserved; `GTKB_NO_AXIS_2_SURFACE=1` emergency stop available.

## Recommended Commit Type

`feat:` — adds Claude-side AXIS 2 surface closing the asymmetry documented in `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model.

## Loyal Opposition Asks

1. Confirm the corrected resolver and narrative-evidence commands satisfy F1 of -004 (commands now match live CLI surfaces).
2. Confirm the explicit-enumeration regression form satisfies F2 of -004 (executes in Windows/PowerShell environment).
3. Confirm REVISED-1's accepted bundle (system-map row + rule-file edit + narrative-packet plan + AUQ approval) carries forward unchanged.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
