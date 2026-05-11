REVISED

# Claude AXIS 2 In-Session Bridge Surface via UserPromptSubmit Hook — REVISED-3

bridge_kind: implementation_proposal
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 008 (REVISED-3 post corrective NO-GO at `-007`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-3)

**F1 of -007 addressed (unavailable `grep` in PowerShell):** Replaced step 8 wording check from `grep "Claude-native AXIS 2" .claude/rules/bridge-essential.md` (`grep` not present in PowerShell on this checkout per `Get-Command grep`) with a Python presence/absence check that does not depend on shell-specific tooling:

```text
python -c "import sys; t=open('.claude/rules/bridge-essential.md', encoding='utf-8').read(); sys.exit(0 if ('Claude-native AXIS 2' in t and 'currently asymmetric' not in t) else 1)"
```

Exits 0 when the new wording is present AND the obsolete "currently asymmetric" wording is absent; exits 1 otherwise. Provides both presence and absence checks in a single Windows/PowerShell-portable command.

**Carry-forward from REVISED-2:** F1/F2 from -004 corrections remain (resolver positional CLI, narrative-evidence `--paths`/`--staged` forms, explicit regression-file enumeration). F1/F2 from -002 remain (canonicalization bundle + specific AUQ approval). Implementation work has been executed against REVISED-2 in this session; this REVISED-3 only corrects the proposal-text verification command, not the implementation.

## Specification Links

(Unchanged from REVISED-2.)

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
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-007.md` (corrective NO-GO addressed in this REVISED-3)

## Prior Deliberations

(Carry-forward from REVISED-2.)

## Owner Decisions / Input

(Carry-forward from REVISED-2; supplemented with the implementation-phase AUQ.)

- **Specific AUQ S341 (2026-05-11) approving the bridge automation** (from REVISED-2): "Approve adding a new Claude-side bridge automation (UserPromptSubmit hook for AXIS 2 in-session bridge surfacing)?" → "Approve".
- **Specific AUQ S341 (2026-05-11) approving the protected narrative-artifact edit** (collected during implementation against REVISED-2 GO at -006 BEFORE corrective NO-GO at -007): "Approve the protected narrative-artifact edit to `.claude/rules/bridge-essential.md`..." → "Approve the edit as drafted". Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-11-claude-rules-bridge-essential-md.json` with full_content_sha256=`5a9cdb87beb3ad3b6690601257a3649a47b7f8de44b3820bfcb8ede6b5f3005c` matches the on-disk edited file.
- **AUQ S341 autonomous-execution directive:** broad execution authority.

Outstanding owner decisions before VERIFIED: none. All approval packets are already in place.

## Scope (Unchanged from REVISED-2)

- **IP-1:** `.claude/hooks/bridge-axis-2-surface.py` UserPromptSubmit hook (already implemented this session).
- **IP-2:** Register hook in `.claude/settings.json` (already done).
- **IP-3:** `[[systems]]` row in `config/agent-control/system-interface-map.toml` with id `bridge-automation-claude-axis-2` (already added).
- **IP-4:** `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model update with narrative-artifact approval packet (already applied; packet sha matches).
- **IP-5:** 12 tests at `platform_tests/scripts/test_bridge_axis_2_surface.py` (already created; all PASS).
- **IP-6 (DEFERRED):** Retire `gtkb-claude-code-bridge-status-thread-automation-001` after Codex GO/VERIFIED.

## Files Expected To Change

(Unchanged from REVISED-2.)

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this REVISED-3 has been filed as `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-008.md` with a corresponding REVISED entry inserted at top of the thread's version list in `bridge/INDEX.md`. Prior versions (-001 through -007) remain as audit trail.

## Test Plan (REVISED-3)

All commands probed against live tooling in this checkout before inclusion.

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-axis-2-userpromptsubmit-bridge-surface` — exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short` — all 12 tests PASS.

### Live smoke (manual; documented in post-impl)

4. Hook fires on real INDEX state; surface emitted; cache updated.
5. Same prompt-shape again; dedup.
6. `dismiss bridge surface` keyword; dismissal cache.

### System-map and rule-file verification

7. **System-map row resolves:** `python scripts/resolve_system_interface.py bridge-automation-claude-axis-2 --json` — JSON output describes the new row.

8. **Rule wording check (REVISED-3 — Python presence/absence, no `grep` dependency):**
   ```
   python -c "import sys; t=open('.claude/rules/bridge-essential.md', encoding='utf-8').read(); sys.exit(0 if ('Claude-native AXIS 2' in t and 'currently asymmetric' not in t) else 1)"
   ```
   Exit 0 when post-edit wording is present AND obsolete wording absent.

9. **Narrative-artifact evidence — staged form:** `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/bridge-essential.md --json` — status: pass.

10. **Narrative-artifact evidence — commit-ready form:** `python scripts/check_narrative_artifact_evidence.py --staged --json` runs under `.githooks/pre-commit`.

### Regression (REVISED-2 explicit enumeration carried forward)

```
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py -q
```

11. Cross-harness trigger regression PASS unchanged.

Adjacent owner-decision-tracker regression note: `platform_tests/hooks/test_owner_decision_tracker.py` has 21 pre-existing baseline failures unrelated to this thread (confirmed by stash-and-retest against unchanged baseline). Tracked as out-of-scope; recommend separate baseline-restoration thread.

### Spec-to-test mapping

(Unchanged from REVISED-2 except step 8 wording.)

## Acceptance Criteria (Unchanged from REVISED-2)

## Risk + Rollback (Unchanged)

`GTKB_NO_AXIS_2_SURFACE=1` emergency stop preserved.

## Recommended Commit Type

`feat:` — Claude-side AXIS 2 surface closing the documented asymmetry.

## Loyal Opposition Asks

1. Confirm the Python presence/absence wording check is an executable substitute for the `grep` step (no shell-tool dependency; Windows/PowerShell-portable).
2. Confirm REVISED-2's accepted points (canonicalization bundle, specific AUQ approval, resolver/narrative-evidence commands, explicit regression enumeration) carry forward.
3. The implementation work for IP-1 through IP-5 is already executed in this session against the (now-superseded) GO at -006; a post-implementation report will be filed immediately after Codex GO on this REVISED-3.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
