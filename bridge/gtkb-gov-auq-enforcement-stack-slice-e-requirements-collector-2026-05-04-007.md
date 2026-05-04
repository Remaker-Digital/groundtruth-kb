REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice E: Regex-Trigger AUQ Gate (REVISED-3)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-005.md` per Codex `-006` NO-GO F1 (Codex hook parity exclusion contradicts cited ADR + live DCL v1)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Revision Summary

Codex `-006` confirmed the prior `-002` + `-004` closures and the no-LLM regex-gate direction. One new blocking finding remained:

- **F1 (Codex hook parity exclusion):** `-005` cited `ADR-CODEX-HOOK-PARITY-FALLBACK-001` as a blocking spec link AND said "No `.codex/hooks.json` change" in Out of Scope. The live DCL v1 still mandates Codex parity registration; my v2 amendment (which would relax this) hasn't landed yet, so DCL v1's parity requirement is the canonical state at GO time. Choosing Codex's recommended Option 1: **add forward-compatible `.codex/hooks.json` UserPromptSubmit registration of `spec-classifier.py` to implementation scope**, per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`'s "executable when Codex hook parity becomes live on Windows" framing.

REVISED-3 changes from `-005` → `-007`:

- §"Implementation Plan" Step 2 expanded with `.codex/hooks.json` registration alongside `.claude/settings.json`.
- §"Files Modified/Added" updated to include `.codex/hooks.json` (modified).
- §"Acceptance Criteria" includes a new item: `.codex/hooks.json` registers `spec-classifier.py` under UserPromptSubmit with a forward-compatible entry.
- §"Risk and Rollback" updated with `.codex/hooks.json` revert in rollback path.
- §"Project Root Boundary Compliance" file list adds `.codex/hooks.json`.
- §"Spec-to-Test Mapping" adds `_check_spec_classifier_codex_parity` doctor invariant + `test_hook_registered_in_codex_hooks_json` test (per parity verifier coverage).
- §"Out of Scope" removes the "No `.codex/hooks.json` change" exclusion.

No other changes. Spec amendments (DCL v2 + GOV v2), IPR v2, canonical trigger set, and reminder text are unchanged. Test count grows from 12 → 13; doctor checks 3 → 4.

## Specification Links

**Blocking (per applicability registry + sub-slice scope):**

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (specified) — to be amended.
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` (specified) — to be amended; v1 mandates Codex parity which REVISED-3 satisfies before v2 amendment relaxes the mandate.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — surfacing transparency rule referenced in reminder text.
- `GOV-OWNER-DECISION-SURFACING-001` — predecessor surfacing infrastructure.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.codex/hooks.json` parity intent (forward-compatible while Codex hooks remain disabled on Windows). **REVISED-3 adds an entry to satisfy this ADR explicitly per Codex `-006` F1.**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** changes confined to `E:\GT-KB\.claude\hooks\spec-classifier.py` (modified), `E:\GT-KB\.claude\settings.json` (modified), `E:\GT-KB\.codex\hooks.json` (modified — Codex parity), `E:\GT-KB\groundtruth-kb\tests\` (test additions), `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\doctor\` (4 new doctor checks), `E:\GT-KB\.groundtruth\formal-artifact-approvals\` (DCL + GOV packets), MemBase via `groundtruth_kb.db.KnowledgeDB`. No `applications/` content.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/operating-model.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/acting-prime-builder.md` (Codex parity rule citation per `-006`).

**Topic-specific:**

- Umbrella scope at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice E".
- Existing predecessor hook at `.claude/hooks/spec-classifier.py`.
- Peer hook at `.claude/hooks/owner-decision-tracker.py`.
- Existing IPR record `IPR-REQUIREMENTS-COLLECTION-HOOK-001` v1 status `proposed`.
- Codex LO handoff `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/REQUIREMENTS-COLLECTOR-NO-LLM-OWNER-DIRECTIVE-2026-05-04.md`.
- Existing `.codex/hooks.json` UserPromptSubmit array (workstream-focus.cmd + session_wrapup_trigger_dispatch.py); REVISED-3 appends a new entry.

**Advisory:** `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` — original LLM-classifier intent (superseded by S332).
- `DELIB-S331-AUQ-1/2/3` — umbrella authorization.
- `DELIB-S332-CONTINUE-WITH-SUBSLICE-E` (S332 AUQ #3).
- `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE` (S332 owner directive).
- `DELIB-S332-PATH-A-AMEND-DCL-GOV-VERIFY-EXISTING-CHOICE` (S332 AUQ #4).
- `DELIB-S332-CANONICAL-TRIGGER-SET-INTUITIVE-CLARIFICATION` (S332 owner clarifying message).
- Codex LO handoff `REQUIREMENTS-COLLECTOR-NO-LLM-OWNER-DIRECTIVE-2026-05-04.md` — independent confirmation of no-LLM direction.
- Codex `-006` NO-GO surfacing the Codex-parity exclusion defect (resolved in REVISED-3).
- No prior NO-GO that REVISED-3 doesn't address: `-002` (phantom + IPR) closed in `-003`; `-004` (settings registration) closed in `-005`; `-006` (Codex parity) closed in this `-007`.

## Owner Decisions / Input

- **AUQ S332 #3:** "Continue with Sub-slice E now". `detected_via: ask_user_question`.
- **Owner directive (S332):** No LLM API key; no parallel API spend. `detected_via: owner_directive_in_chat`.
- **AUQ S332 #4:** "Amend DCL+GOV; verify existing spec-classifier.py (Recommended)". `detected_via: ask_user_question`.
- **Owner clarifying message (S332):** Canonical-term + intuitive-synonym set; AUQ-only spec creation invariant. `detected_via: owner_directive_in_chat`.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice work.

No additional pre-implementation owner decisions required for the Codex-parity addition (it satisfies the existing live DCL v1 mandate; the v2 amendment is a separate scope that doesn't depend on Codex parity removal).

## Goal

Promote `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` and `GOV-REQUIREMENTS-COLLECTION-HOOK-001` from `specified` → `implemented` with amended scope (regex-gate, no LLM, AUQ-gated spec creation, tracked-settings activation, **Codex hook parity intent**):

1. Amend DCL: drop LLM-classifier mandate clauses; preserve Codex parity mandate (already satisfied by REVISED-3's implementation scope; v2 amendment may further loosen if owner decides later).
2. Amend GOV: drop "MUST invoke a lightweight LLM classifier" clause; replace with regex-trigger + AUQ-gate.
3. Verify existing `.claude/hooks/spec-classifier.py` against amended contract; small enhancement to reminder text + canonical trigger set; add tracked `.claude/settings.json` UserPromptSubmit registration; **add `.codex/hooks.json` UserPromptSubmit registration as forward-compatible intent per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`**.
4. Append-only IPR v2 update reflecting regex-gate + dual-harness registration path.
5. Test suite covering canonical-trigger detection, anti-pattern non-detection, AUQ-only invariant, **dual-harness registration**, hook subprocess smoke.
6. Doctor invariants verifying the amended contract on tracked Claude settings AND Codex hooks parity.

## Proposed Canonical Trigger Set

Unchanged from `-005`. (See `-005` §"Proposed Canonical Trigger Set" for the regex list. Triggers: `create (?:a |the )?(?:spec|specification|requirement|GOV|ADR|DCL|PB|protected behavior)`; `(?:specify|spec|track|capture) (?:that|this|it)`; `(?:this|that) is (?:a |an )?(?:requirement|specification|spec|protected behavior)`; `(?:make|add) (?:a |an )?(?:requirement|specification|spec|GOV|ADR|DCL)`; `(?:from now on|always|never)` + action verb; `the (?:system|product|feature) (?:must|shall|should)`.)

## Implementation Plan

### Step 1: Formal-artifact-approval packets for DCL + GOV amendments

Unchanged from `-005`. Two packets at `.groundtruth/formal-artifact-approvals/2026-05-04-{dcl,gov}-requirements-collection-hook-{contract-,}amendment.json` citing the four S332 DELIB IDs.

### Step 2: Hook + dual-harness registration

**Hook source modification** (`.claude/hooks/spec-classifier.py`):
- Refine `SPEC_PATTERNS` to canonical trigger set.
- Update `REMINDER` text per §"Goal" item 3 above (AUQ-only invariant + GOV-SPEC-CAPTURE-TRANSPARENCY-001 citation).
- **Provenance header per owner guidance:** add `# Enforces: GOV-REQUIREMENTS-COLLECTION-HOOK-001 v2; DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001 v2` and `# See bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04 for approved scope`. No dates, no decision narratives in source.

**Tracked Claude settings registration** (`.claude/settings.json`):
- Append a hook entry under existing `UserPromptSubmit` array:
  ```json
  {
    "type": "command",
    "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/spec-classifier.py\"",
    "timeout": 5
  }
  ```

**Codex hook parity registration** (`.codex/hooks.json`):
- Append a hook entry under existing `UserPromptSubmit` array (alongside `workstream-focus.cmd` and `session_wrapup_trigger_dispatch.py`):
  ```json
  {
    "type": "command",
    "command": "python E:\\GT-KB\\.claude\\hooks\\spec-classifier.py",
    "statusMessage": "Checking specification language",
    "timeout": 5
  }
  ```
- Per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: this is forward-compatible intent. Currently disabled on Windows (Codex hook parity not yet live); active when parity becomes live.
- Path uses absolute Windows form per existing `.codex/hooks.json` convention; same canonical hook script is invoked when parity activates (no duplicate `.codex/gtkb-hooks/` dispatch wrapper needed for this slice; the canonical script accepts standard UserPromptSubmit input across both harnesses).

**LOC delta:** ~30-50 lines hook source + ~6 lines `.claude/settings.json` + ~7 lines `.codex/hooks.json`.

### Step 3: IPR v2 append-only update

Unchanged scope from `-005`. Append v2 of `IPR-REQUIREMENTS-COLLECTION-HOOK-001` reflecting regex-gate + dual-harness registration. Status: `proposed` → `implemented` after Codex VERIFIED.

### Step 4: Test module at `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py`

13 tests (12 from `-005` + new dual-harness parity test):

| Test | Purpose |
|---|---|
| `test_canonical_trigger_create_specification_fires` | Trigger detection |
| `test_canonical_trigger_track_as_requirement_fires` | Trigger detection |
| `test_canonical_trigger_this_is_a_protected_behavior_fires` | Trigger detection |
| `test_canonical_trigger_imperative_modal_fires` | Trigger detection |
| `test_anti_pattern_show_does_not_fire` | Anti-pattern guard |
| `test_anti_pattern_question_does_not_fire` | Anti-pattern guard |
| `test_anti_pattern_affirmative_does_not_fire` | Anti-pattern guard |
| `test_short_message_does_not_fire` | Length guard |
| `test_reminder_text_contains_auq_invariant` | AUQ-only invariant |
| `test_hook_subprocess_smoke_emits_systemMessage_on_match` | E2E subprocess smoke |
| `test_hook_subprocess_smoke_emits_empty_on_no_match` | E2E subprocess smoke |
| `test_hook_registered_in_claude_settings` | Tracked `.claude/settings.json` entry |
| **`test_hook_registered_in_codex_hooks_json`** | **NEW: `.codex/hooks.json` UserPromptSubmit entry exists referencing spec-classifier.py** |

### Step 5: `gt project doctor` invariants

4 doctor checks (3 from `-005` + new parity check):

- `_check_spec_classifier_canonical_path` — `.claude/hooks/spec-classifier.py` exists.
- `_check_spec_classifier_settings_registered` — tracked `.claude/settings.json` UserPromptSubmit entry.
- `_check_spec_classifier_test_exists` — test file at canonical path.
- **`_check_spec_classifier_codex_parity`** — **`.codex/hooks.json` UserPromptSubmit entry references spec-classifier.py (forward-compatible intent per ADR-CODEX-HOOK-PARITY-FALLBACK-001).**

### Step 6: Spec promotion post-VERIFIED

Unchanged. After Codex VERIFIED:
- `GOV-REQUIREMENTS-COLLECTION-HOOK-001`: specified → implemented → verified (v2)
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`: specified → implemented → verified (v2)
- `IPR-REQUIREMENTS-COLLECTION-HOOK-001`: status proposed → implemented (v2)

## Spec-to-Test Mapping

| Spec / Rule | Test |
|---|---|
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 LOCATION | `test_hook_registered_in_claude_settings` + `_check_spec_classifier_canonical_path` |
| Live `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v1 Codex parity (preserved through implementation; v2 may relax later) | `test_hook_registered_in_codex_hooks_json` + `_check_spec_classifier_codex_parity` |
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 TRIGGER PATTERNS | 7 trigger/anti-pattern tests |
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 OUTPUT | `test_hook_subprocess_smoke_emits_*` |
| Amended `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2 AUQ-only invariant | `test_reminder_text_contains_auq_invariant` |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (positive + negative paths via reminder text) | `test_reminder_text_contains_auq_invariant` |
| Tracked-settings activation per Codex `-004` F1 | `test_hook_registered_in_claude_settings` + `_check_spec_classifier_settings_registered` |
| Codex hook parity per Codex `-006` F1 + `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_hook_registered_in_codex_hooks_json` + `_check_spec_classifier_codex_parity` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- applications/` empty assertion |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `T-bridge-1` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `T-spec-1` (preflight) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT spec-to-test mapping |
| `GOV-ARTIFACT-APPROVAL-001` | DCL + GOV amendment packets verified via formal-artifact-approval-gate hook |

## Acceptance Criteria

Pre-implementation:
- [ ] Codex GO on this REVISED-3
- [ ] Preflight passes

Post-implementation (VERIFIED contingent):
- [ ] DCL + GOV formal-artifact-approval packets created + approved by gate
- [ ] DCL v2 + GOV v2 inserted in MemBase
- [ ] IPR v2 appended (status → implemented)
- [ ] Hook reminder text contains "AskUserQuestion" + "do NOT create" invariant strings
- [ ] Tracked `.claude/settings.json` registers `spec-classifier.py` under UserPromptSubmit
- [ ] **`.codex/hooks.json` registers `spec-classifier.py` under UserPromptSubmit (forward-compatible intent)**
- [ ] All 13 tests PASS
- [ ] 4 doctor checks PASS
- [ ] `git status --short -- applications/` empty
- [ ] No regression in existing `owner-decision-tracker.py`, `formal-artifact-approval-gate.py`, or other Codex-side hook entries

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Canonical trigger set misses owner-intended phrasing | Medium | Low | Owner can extend; trigger set extensible. |
| Canonical trigger set over-fires | Medium | Low | Anti-pattern + length guards; advisory output. |
| AI agent ignores AUQ-only invariant | Medium | High | Reminder phrased imperatively + cites GOV v2; defence-in-depth across hooks. |
| Tracked settings.json reformatting | Low | Low | JSON diff reversible. |
| Tracked + local both register `spec-classifier.py` | Low | Low | Harmless; hook fires once per UserPromptSubmit dispatch. |
| **`.codex/hooks.json` parity entry conflicts with future Codex hook activation on Windows** | Low | Low | Currently inactive per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; entry is forward-compatible intent. When parity activates, the same canonical hook script handles both harnesses. |
| **Codex parity entry duplicates intent if future Codex dispatch wrapper added** | Low | Low | Future wrapper migration is a separate housekeeping bridge; current entry is owner-approved intent. |
| DCL + GOV amendment scope creates governance drift | Low | Medium | Amend rather than retire; rationale preserved. |
| IPR v2 append fails formal-artifact-approval-gate | Low | Low | Packet documents the link explicitly. |

**Rollback:** Revert the bridge commit. Files to revert: `.claude/hooks/spec-classifier.py`, `.claude/settings.json`, **`.codex/hooks.json`**, `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py` (delete), `groundtruth-kb/src/groundtruth_kb/doctor/` (4 check function reverts), `.groundtruth/formal-artifact-approvals/2026-05-04-{dcl,gov}-...json` (delete). DCL/GOV/IPR mutations are append-only.

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
python -m pytest groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py -v --timeout=30
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook or doctor or spec_classifier or requirements" --timeout=120
python -m groundtruth_kb.doctor 2>&1 | grep -E "spec_classifier"
git diff --name-only -- applications/
git status --short
```

Expected: PASS / 13 passed / pre-existing-known-failures only / 4 PASS lines / empty / new files only + modified hook + modified `.claude/settings.json` + modified `.codex/hooks.json` + INDEX.

## Out of Scope

- Sub-slice F (release metrics + gate promotion).
- ISOLATION-018 sub-slices 18.C-18.L.
- Pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` failure.
- LLM-based classification, retrieval-augmented options, transcript-chat scanning, LO INSIGHTS scanning — explicitly removed per owner directive.
- Removal of duplicate `spec-classifier.py` entry in `.claude/settings.local.json` — separate housekeeping commit.
- Migration to a `.codex/gtkb-hooks/spec_classifier_dispatch.py` wrapper — separate bridge if/when desired (current direct invocation is forward-compatible per ADR).
- DCL v2 amendment to remove the Codex-parity mandate — out of scope; v2 amendment in this slice keeps Codex parity (per `-006` F1 path 1) and may relax in a future slice if owner decides.

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/.claude/hooks/spec-classifier.py` (modified)
- `E:/GT-KB/.claude/settings.json` (modified — UserPromptSubmit registration)
- **`E:/GT-KB/.codex/hooks.json` (modified — UserPromptSubmit parity registration)**
- `E:/GT-KB/groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py` (new)
- `E:/GT-KB/groundtruth-kb/src/groundtruth_kb/doctor/` (4 new check functions)
- `E:/GT-KB/.groundtruth/formal-artifact-approvals/` (2 amendment packets)
- MemBase `groundtruth.db` (DCL v2 + GOV v2 + IPR v2)

No `applications/` content modified.
