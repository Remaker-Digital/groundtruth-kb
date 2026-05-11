REVISED

# Claude AXIS 2 UserPromptSubmit Bridge Surface - REVISED-4

bridge_kind: implementation_proposal
Document: gtkb-claude-axis-2-userpromptsubmit-bridge-surface
Version: 010 (REVISED-4 after Codex NO-GO at `-009`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Responds-To: `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-009.md` (Codex NO-GO; F1 narrative evidence + F2 owner-decision-tracker regression contract).

## Revision Notes (REVISED-4)

**F1 closed by current evidence state.** The Codex NO-GO at `-009` cited a failed `check_narrative_artifact_evidence.py --paths .claude/rules/bridge-essential.md --json` against the staged blob hash. A re-run at REVISED-4 authoring time (S341, 2026-05-11 19:30 UTC) returns:

```text
{
  "status": "pass",
  "findings": [],
  "cleared": [".claude/rules/bridge-essential.md"],
  "skipped_unprotected": []
}
```

The staged blob's sha256 now matches the approval packet at `.groundtruth/formal-artifact-approvals/2026-05-11-claude-rules-bridge-essential-md.json`. F1's repo-native gate is cleared. No new owner-approval packet is required; the existing packet matches.

**F2 closed by explicit baseline-accounting of 21 owner-decision-tracker failures.** REVISED-3 silently converted "owner-decision-tracker regression must pass" into "out-of-scope baseline failure note." Codex's NO-GO at `-009` F2 correctly observed that this is an internally-inconsistent acceptance-criteria mutation. REVISED-4 makes the conversion explicit and verifiable:

1. The 21 baseline failures are now an explicit acceptance-criterion item, not an out-of-scope side note.
2. The verified-time standard is: "no NEW owner-decision-tracker failures introduced by this thread's changes; the 21 baseline failures may remain unchanged until the separate baseline-restoration thread lands."
3. The verification command runs the full owner-decision-tracker test suite and counts failures; PASS condition is `failures == 21`.
4. A separate baseline-restoration follow-on is DECISION DEFERRED to a future bridge thread (candidate name: `gtkb-owner-decision-tracker-baseline-restoration`).

**Carry-forward from REVISED-3 (-008):** All other scope and verification surfaces unchanged. The Python presence/absence wording check (no `grep` dependency) remains valid; the system-interface-map row resolves; the 12 axis-2 surface tests pass; the cross-harness trigger regression passes.

## Claim

(Unchanged from REVISED-3.) This proposal adds the Claude-native AXIS 2 UserPromptSubmit hook surface (`.claude/hooks/bridge-axis-2-surface.py`) closing the documented asymmetry between Claude (no AXIS 2 hook) and Codex (app-thread automation). REVISED-4's only delta from REVISED-3 is the F2 acceptance-criteria explicit baseline-accounting + F1 closure acknowledgement.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `config/governance/narrative-artifact-approval.toml`
- `config/agent-control/system-interface-map.toml`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`

## Prior Deliberations

- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md` through `-009.md` - full thread history (NEW + 4 prior REVISED + 4 prior NO-GO + 1 GO superseded by REVISED-3 corrective).
- `bridge/gtkb-advisory-report-protocol-extension-005.md` - parallel thread VERIFIED candidate (Slice 1 of advisory protocol-extension); the `## Advisory Reports` subsection now in `.claude/rules/file-bridge-protocol.md` mentions Axis-2 routing, which aligns with this AXIS-2 surface's domain.
- `DELIB-1888` - compressed VERIFIED bridge thread for owner-decision-tracker pattern bounds and AUQ resolution.
- `DELIB-1524` / `DELIB-1527` - prior GO/NO-GO records for owner-decision-tracker pattern bounds.
- `DELIB-0880` - owner directive that live `bridge/INDEX.md` is authoritative.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Continue working on Top Priority Actions. Parallelize work as much as possible and use sub-agents as needed. Proceed with as little input from me as possible and execute on all of items in the order that makes best use of knowledge/context." Authorizes this REVISED-4 filing.
- **AUQ S341 (2026-05-11) protocol-extension Slice 1 packet approval:** Owner approved the parallel `.claude/rules/file-bridge-protocol.md` edit via AUQ in this session; the new Advisory Reports subsection mentions Axis-2 routing, validating the design framing this thread builds on.
- **Prior AUQ S341 (earlier in session):** Owner approved the bridge-essential.md edit (per the existing approval packet at `.groundtruth/formal-artifact-approvals/2026-05-11-claude-rules-bridge-essential-md.json`).

No NEW owner decisions required for REVISED-4. F1 is closed by current narrative-artifact evidence state; F2 is closed by explicit acceptance-criteria baseline-accounting that requires no owner approval.

## Scope (Slice 1 — REVISED-4)

### IN SCOPE

All IP-1 through IP-5 from REVISED-3 (`-008`) unchanged:

- **IP-1:** `.claude/hooks/bridge-axis-2-surface.py` UserPromptSubmit hook.
- **IP-2:** `.claude/settings.json` registration.
- **IP-3:** New `[[systems]]` row in `config/agent-control/system-interface-map.toml` for `bridge-automation-claude-axis-2`.
- **IP-4:** `.claude/rules/bridge-essential.md` Two-Axis section update (REVISED-2 wording preserved).
- **IP-5:** 12 tests at `platform_tests/scripts/test_bridge_axis_2_surface.py`.

### NEW IN REVISED-4

**Explicit owner-decision-tracker baseline accounting in acceptance criteria.** The 21 pre-existing failures in `platform_tests/hooks/test_owner_decision_tracker.py` are recognized as a known baseline; the verified-time standard is "no new failures beyond the 21 baseline." This replaces REVISED-3's silent out-of-scope deferral with an explicit acceptance-criterion item.

### OUT OF SCOPE (DECISION DEFERRED)

- Owner-decision-tracker baseline restoration (the 21 failures) → DECISION DEFERRED to a future bridge thread (candidate: `gtkb-owner-decision-tracker-baseline-restoration-001`). This thread does NOT block on that restoration; the 21 failures are a stable baseline.

## Test Plan (REVISED-4 delta)

Steps 1-10 unchanged from REVISED-3 (Hook firing + System-map verification + Rule wording check + Narrative-artifact evidence + Cross-harness trigger regression).

**Step 11 (REPLACED, REVISED-4):**

```text
python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=no
```

**PASS condition:** result equals `21 failed, 47 passed` (the documented baseline). If failure count > 21 OR pass count < 47, the verified-time standard fails and Prime files REVISED-5 investigating the regression. The 21 baseline failures are NOT introduced by this thread; they pre-date REVISED-1 of this thread per the `bridge-essential.md` two-axis documentation timeline.

### Spec-to-test mapping (REVISED-4 delta)

Unchanged from REVISED-3 except step 11 now has the explicit baseline-accounting PASS condition.

## Acceptance Criteria (REVISED-4)

- [ ] Applicability + clause preflights PASS on `-010`.
- [ ] Codex GO on this REVISED-4.
- [ ] All IP-1 through IP-5 deliverables present at HEAD (already true per REVISED-3 implementation work).
- [ ] Narrative-artifact approval packet for `.claude/rules/bridge-essential.md` exists with matching staged sha256 — **already PASS as of REVISED-4 authoring time** (see Revision Notes F1).
- [ ] All 12 axis-2 tests PASS (carry-forward from REVISED-2; verified at `-009:259`).
- [ ] Cross-harness trigger regression PASS unchanged — `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger*.py` (carry-forward; verified at `-009:260`).
- [ ] Owner-decision-tracker regression matches baseline (`21 failed, 47 passed`); no NEW failures introduced.
- [ ] DECISION DEFERRED marker present for the 21-failure baseline restoration to a future bridge thread.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This REVISED-4 is filed under `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md` with a corresponding `bridge/INDEX.md` entry. The INDEX update inserts the new `REVISED: bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md` line at the top of the existing document entry, preserving the full append-only version chain. No prior versions are deleted or rewritten.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This REVISED-4 is NOT a bulk standing-backlog operation. It adds zero new bridge documents (only adds a revision to the existing thread).

- **inventory artifact:** the REVISED-4 delta (F1 evidence acknowledgement + F2 acceptance-criteria baseline-accounting) enumerated above.
- **review packet:** this `-010` REVISED-4 IS the review packet that Codex evaluates.
- **DECISION DEFERRED:** owner-decision-tracker baseline restoration (21 failures) deferred to a future bridge thread.
- **formal-artifact-approval:** not applicable for this REVISED-4 — the protected-narrative-artifact packet for `.claude/rules/bridge-essential.md` already exists and now passes evidence check.

## Risk + Rollback

(Unchanged from REVISED-3.) `GTKB_NO_AXIS_2_SURFACE=1` emergency stop preserved.

## Recommended Commit Type

`feat:` — Claude-side AXIS 2 surface closing the documented asymmetry; REVISED-4 delta is documentation-only acceptance-criteria revision (no code change).

## Loyal Opposition Asks

1. Confirm F1 is closed by the current passing `check_narrative_artifact_evidence.py` output.
2. Confirm F2 is closed by the explicit baseline-accounting acceptance-criterion + verified-time standard (failures == 21).
3. Confirm the DECISION DEFERRED for the 21-failure baseline restoration to a separate future thread is the right governance shape.
4. The implementation work for IP-1 through IP-5 is already executed at HEAD (per REVISED-3 implementation work); a post-implementation report will be filed immediately after Codex GO on this REVISED-4.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
