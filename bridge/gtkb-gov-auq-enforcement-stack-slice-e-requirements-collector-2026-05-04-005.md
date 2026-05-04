REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice E: Regex-Trigger AUQ Gate (REVISED-2)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-003.md` per Codex `-004` NO-GO F1 (hook activation inconsistency)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Revision Summary

Codex `-004` confirmed the prior `-002` F1+F2 closures (phantom-spec citation + existing-IPR plan) and the no-LLM regex-gate direction. One new blocking finding remained:

- **F1 (hook activation inconsistency):** `-003` claimed `.claude/settings.json` "already registered" `spec-classifier.py`. Live probe shows `spec-classifier.py` is registered in `.claude/settings.local.json` line 193 (workstation-local, untracked) but NOT in tracked `.claude/settings.json` (which only registers `.claude/hooks/owner-decision-tracker.py --mode user-prompt-submit` under `UserPromptSubmit`). The proposal's tests + doctor invariants targeted `.claude/settings.json`, but the implementation scope didn't include modifying that file.

REVISED-2 chooses Codex's recommended Option 1 (the stronger governance path): **add tracked `.claude/settings.json` UserPromptSubmit registration of `spec-classifier.py` to the implementation scope.** This ensures the hook fires in fresh clones, shared harness contexts, and worktrees — not only on the current workstation.

Changes from `-003` → `-005`:

- §"Goal" item 3 expanded: hook enhancement now explicitly includes adding tracked-settings registration.
- §"Implementation Plan" Step 2 now itemizes the `.claude/settings.json` UserPromptSubmit array append.
- §"Files Modified/Added" updated to include `.claude/settings.json` (modified).
- §"Acceptance Criteria" includes a new item: tracked `.claude/settings.json` registers `spec-classifier.py` under UserPromptSubmit.
- §"Risk and Rollback" updated to include settings.json revert in rollback path.
- §"Project Root Boundary Compliance" file list adds `.claude/settings.json`.
- Test `test_hook_registered_in_claude_settings` clarified to check tracked `.claude/settings.json` (not local).
- Doctor invariant `_check_spec_classifier_settings_registered` clarified to read tracked `.claude/settings.json`.

No design changes beyond hook activation surface. Spec amendments (DCL v2 + GOV v2) and IPR v2 update unchanged. 12-test plan unchanged.

## Specification Links

**Blocking (per applicability registry + sub-slice scope):**

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (specified) — to be amended.
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` (specified) — to be amended.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (specified) — surfacing transparency rule referenced by the amended hook reminder.
- `GOV-OWNER-DECISION-SURFACING-001` — predecessor surfacing infrastructure.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate for DCL/GOV amendments + IPR v2.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.codex/hooks.json` parity intent.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** changes confined to `E:\GT-KB\.claude\hooks\spec-classifier.py` (modified), `E:\GT-KB\.claude\settings.json` (modified — UserPromptSubmit registration), `E:\GT-KB\groundtruth-kb\tests\` (test additions), `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\doctor\` (3 new doctor checks), `E:\GT-KB\.groundtruth\formal-artifact-approvals\` (DCL + GOV packets), MemBase via `groundtruth_kb.db.KnowledgeDB` (DCL v2 + GOV v2 + IPR v2). No `applications/` content.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/operating-model.md`, `.claude/rules/project-root-boundary.md`.

**Topic-specific:**

- Umbrella scope at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice E".
- Existing predecessor hook at `.claude/hooks/spec-classifier.py`.
- Peer hook at `.claude/hooks/owner-decision-tracker.py`.
- Existing IPR record `IPR-REQUIREMENTS-COLLECTION-HOOK-001` v1 status `proposed` (target of v2 append).
- Codex LO handoff `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/REQUIREMENTS-COLLECTOR-NO-LLM-OWNER-DIRECTIVE-2026-05-04.md` — independent confirmation of the no-LLM regex-gate direction.

**Advisory:** `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` — original S330 design intent (LLM classifier + 3-option clarification; superseded by S332 owner directive).
- `DELIB-S331-AUQ-1/2/3` — umbrella authorization.
- `DELIB-S332-CONTINUE-WITH-SUBSLICE-E` — S332 AUQ #3 selecting "Continue with Sub-slice E now".
- `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE` — S332 owner directive.
- `DELIB-S332-PATH-A-AMEND-DCL-GOV-VERIFY-EXISTING-CHOICE` — S332 AUQ #4 selecting Path A.
- `DELIB-S332-CANONICAL-TRIGGER-SET-INTUITIVE-CLARIFICATION` — S332 owner clarifying message.
- Codex LO handoff `REQUIREMENTS-COLLECTOR-NO-LLM-OWNER-DIRECTIVE-2026-05-04.md` — independent confirmation that no-LLM direction is the right pivot.
- No prior NO-GO that REVISED-2 doesn't address: `-002` (phantom + IPR) closed in `-003`; `-004` (settings registration) closed in this `-005`.

## Owner Decisions / Input

- **AUQ S332 #3:** "Continue with Sub-slice E now". `detected_via: ask_user_question`.
- **Owner directive (S332):** No LLM API key; no parallel API spend. `detected_via: owner_directive_in_chat`.
- **AUQ S332 #4:** "Amend DCL+GOV; verify existing spec-classifier.py (Recommended)". `detected_via: ask_user_question`.
- **Owner clarifying message (S332):** "A canonical term, with a set of synonym patterns... It is more important that no requirements specifications are created without my explicit choice from an AskUserQuestion." `detected_via: owner_directive_in_chat`.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice work.

No additional pre-implementation owner decisions required. Codex GO/NO-GO governs proceed.

## Goal

Promote `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` and `GOV-REQUIREMENTS-COLLECTION-HOOK-001` from `specified` → `implemented` with amended scope (regex-gate, no LLM, AUQ-gated spec creation, **tracked-settings activation**):

1. Amend DCL: drop LLM-classifier mandate, retrieval mandate, 4-label enumeration, classifier-model-bounds clauses, additional_context_schema fixed structure, cost-cap/timeout clauses. Replace with: regex-trigger detection against canonical trigger set; emit reminder via `additionalContext` (or backwards-compatible `systemMessage`) directing AI to AUQ-confirm before any spec creation.
2. Amend GOV: drop "MUST invoke a lightweight LLM classifier" + 4-label enumeration; replace with "MUST detect canonical trigger phrases via fixed regex patterns" + "AI agent MUST use AskUserQuestion to confirm any specification creation triggered by the hook."
3. **Verify existing `.claude/hooks/spec-classifier.py` satisfies the amended contract; small enhancement to reminder text emphasizing the AUQ-only invariant; refine `SPEC_PATTERNS` to canonical set; add tracked `.claude/settings.json` UserPromptSubmit registration so the hook fires in fresh clones and shared harness contexts (not only on the current workstation per `.claude/settings.local.json`).**
4. Append-only IPR v2 update reflecting regex-gate implementation path.
5. Test suite covering canonical-trigger detection, anti-pattern non-detection, AUQ-only invariant in reminder text, **tracked-settings registration**, and hook subprocess smoke.
6. Doctor invariants verifying the amended contract against tracked settings.

## Proposed Canonical Trigger Set

Unchanged from `-003`. Canonical term: *specification* (lifecycle siblings: requirement, spec, GOV, ADR, DCL, PB). Trigger phrases (regex; case-insensitive; word-boundaried):

- `\bcreate (?:a |the )?(?:spec|specification|requirement|GOV|ADR|DCL|PB|protected behavior)\b`
- `\b(?:specify|spec|track|capture) (?:that|this|it)\b`
- `\b(?:this|that) is (?:a |an )?(?:requirement|specification|spec|protected behavior)\b`
- `\b(?:make|add) (?:a |an )?(?:requirement|specification|spec|GOV|ADR|DCL)\b`
- `\b(?:from now on|always|never)\b` followed within 5 words by an action verb
- `\bthe (?:system|product|feature) (?:must|shall|should)\b`

Anti-patterns (commands, questions, affirmatives) preserved from existing `spec-classifier.py`.

## Implementation Plan

### Step 1: Formal-artifact-approval packets for DCL + GOV amendments

Unchanged from `-003`. Two packets at `.groundtruth/formal-artifact-approvals/2026-05-04-{dcl,gov}-requirements-collection-hook-{contract-,}amendment.json`. Both cite the four S332 DELIB IDs as authorizing evidence. Two `db.update_spec(...)` operations creating v2 of each spec.

### Step 2: Hook + tracked-settings registration

**Hook source modification** (`.claude/hooks/spec-classifier.py`):
- Refine `SPEC_PATTERNS` to the canonical trigger set above.
- Update `REMINDER` text to enforce AUQ-only-spec-creation:
  > "⚠️ SPECIFICATION TRIGGER — Owner used a canonical specification-language trigger ([trigger phrase]). Per `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2: do NOT create or promote any formal artifact (SPEC/REQ/GOV/ADR/DCL/PB) without first issuing an `AskUserQuestion` to confirm the artifact's existence, scope, and approval. Surface the candidate per `GOV-SPEC-CAPTURE-TRANSPARENCY-001`."
- Optionally migrate output from `systemMessage` to `additionalContext` per amended DCL.

**Tracked-settings registration** (`.claude/settings.json`):
- Add a second hook entry under the existing `UserPromptSubmit` array (alongside `owner-decision-tracker.py --mode user-prompt-submit`):
  ```json
  {
    "type": "command",
    "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/spec-classifier.py\"",
    "timeout": 5
  }
  ```
- This registration ensures the hook fires for every fresh clone and shared harness context. The existing untracked `.claude/settings.local.json` line 193 entry can stay (workstation-local override) or be removed in a separate housekeeping commit; not in this slice's scope.

**LOC delta:** ~30-50 lines hook source + ~6 lines settings.json (single JSON object).

### Step 3: IPR v2 append-only update

Unchanged from `-003`. Append v2 of `IPR-REQUIREMENTS-COLLECTION-HOOK-001` reflecting regex-gate implementation; cites this REVISED-2, links amended DCL v2 + GOV v2, references hook + test paths. Status: `proposed` → `implemented` after Codex VERIFIED.

### Step 4: Test module at `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py`

12 tests (unchanged from `-003`):

| Test | Purpose |
|---|---|
| `test_canonical_trigger_create_specification_fires` | "Create a specification for X" matches |
| `test_canonical_trigger_track_as_requirement_fires` | "Track this as a requirement" matches |
| `test_canonical_trigger_this_is_a_protected_behavior_fires` | "This is a protected behavior" matches |
| `test_canonical_trigger_imperative_modal_fires` | "The system must include X" matches |
| `test_anti_pattern_show_does_not_fire` | "show me X" does not match |
| `test_anti_pattern_question_does_not_fire` | "what is X?" does not match |
| `test_anti_pattern_affirmative_does_not_fire` | "yes proceed" does not match |
| `test_short_message_does_not_fire` | < MIN_SPEC_LENGTH does not match |
| `test_reminder_text_contains_auq_invariant` | Reminder string contains "AskUserQuestion" + "do NOT create" |
| `test_hook_subprocess_smoke_emits_systemMessage_on_match` | end-to-end subprocess: trigger → reminder emitted |
| `test_hook_subprocess_smoke_emits_empty_on_no_match` | end-to-end subprocess: chat message → empty additionalContext |
| `test_hook_registered_in_claude_settings` | **Reads tracked `.claude/settings.json`** (NOT `.claude/settings.local.json`); asserts hook entry under `UserPromptSubmit` array |

### Step 5: `gt project doctor` invariants per amended DCL

3 doctor checks (unchanged count from `-003`):

- `_check_spec_classifier_canonical_path` — verifies `.claude/hooks/spec-classifier.py` exists.
- `_check_spec_classifier_settings_registered` — **reads tracked `.claude/settings.json`** and verifies hook entry under `UserPromptSubmit` array.
- `_check_spec_classifier_test_exists` — verifies test file at canonical path.

### Step 6: Spec promotion post-VERIFIED

Unchanged from `-003`. After Codex VERIFIED on the post-impl REPORT:
- `GOV-REQUIREMENTS-COLLECTION-HOOK-001`: specified → implemented → verified (v2)
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`: specified → implemented → verified (v2)
- `IPR-REQUIREMENTS-COLLECTION-HOOK-001`: status proposed → implemented (v2)

## Spec-to-Test Mapping

| Spec / Rule | Test |
|---|---|
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 LOCATION | `test_hook_registered_in_claude_settings` (tracked) + `_check_spec_classifier_canonical_path` |
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 TRIGGER PATTERNS | 7 trigger/anti-pattern tests |
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 OUTPUT | `test_hook_subprocess_smoke_emits_*` |
| Amended `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2 AUQ-only invariant | `test_reminder_text_contains_auq_invariant` |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (positive + negative paths via reminder text) | `test_reminder_text_contains_auq_invariant` (reminder cites the spec) |
| Tracked-settings activation per Codex `-004` F1 | `test_hook_registered_in_claude_settings` + `_check_spec_classifier_settings_registered` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- applications/` empty assertion |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `T-bridge-1` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `T-spec-1` (preflight) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT spec-to-test mapping |
| `GOV-ARTIFACT-APPROVAL-001` | DCL + GOV amendment packets verified via formal-artifact-approval-gate hook |

## Acceptance Criteria

Pre-implementation:
- [ ] Codex GO on this REVISED-2
- [ ] Preflight passes

Post-implementation (VERIFIED contingent):
- [ ] DCL + GOV formal-artifact-approval packets created + approved by gate
- [ ] DCL v2 + GOV v2 inserted in MemBase
- [ ] IPR v2 appended (status → implemented)
- [ ] Hook reminder text contains "AskUserQuestion" + "do NOT create" invariant strings
- [ ] **Tracked `.claude/settings.json` registers `spec-classifier.py` under UserPromptSubmit (verifiable by `test_hook_registered_in_claude_settings`)**
- [ ] All 12 tests PASS
- [ ] 3 doctor checks PASS (with `_check_spec_classifier_settings_registered` reading tracked settings)
- [ ] `git status --short -- applications/` empty
- [ ] No regression in existing `owner-decision-tracker.py` or `formal-artifact-approval-gate.py` behavior

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Canonical trigger set misses owner-intended phrasing | Medium | Low | Owner can extend; trigger set extensible. Reminder is non-blocking. |
| Canonical trigger set over-fires | Medium | Low | Anti-pattern + length guards; advisory output. |
| AI agent ignores AUQ-only invariant | Medium | High | Reminder phrased imperatively + cites GOV v2; defence-in-depth across hooks. |
| **Tracked settings.json change conflicts with downstream reformatting** | Low | Low | settings.json is JSON; minor reformatting is reversible via `git diff`. The added object is at a stable position (UserPromptSubmit array tail). |
| **Hook registration in tracked settings doesn't propagate to existing local override** | Low | Low | `.claude/settings.local.json` already has the entry (workstation-local); tracked + local both registering is harmless (hook fires once per UserPromptSubmit dispatch in Claude Code). |
| DCL + GOV amendment scope creates governance drift | Low | Medium | Both amendments retain rationale; amend rather than retire. |
| IPR v2 append fails formal-artifact-approval-gate | Low | Low | Packet documents the link explicitly; v2 append is standard append-only operation. |

**Rollback:** Revert the bridge commit. **Files to revert:** `.claude/hooks/spec-classifier.py` (source change), `.claude/settings.json` (UserPromptSubmit entry), `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py` (delete), `groundtruth-kb/src/groundtruth_kb/doctor/` (3 check function reverts), `.groundtruth/formal-artifact-approvals/2026-05-04-{dcl,gov}-...json` (delete). DCL/GOV/IPR mutations are append-only — v1 records remain canonical until v2 lands; rollback creates v3 reverting v1 content if needed.

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
python -m pytest groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py -v --timeout=30
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook or doctor or spec_classifier or requirements" --timeout=120
python -m groundtruth_kb.doctor 2>&1 | grep -E "spec_classifier"
git diff --name-only -- applications/
git status --short
```

Expected: PASS / 12 passed / pre-existing-known-failures only / 3 PASS lines / empty / new files only + modified hook + modified settings.json + INDEX.

## Out of Scope

- Sub-slice F (release metrics + gate promotion) — separate bridge after E VERIFIED.
- ISOLATION-018 sub-slices 18.C-18.L — gated by Sub-slice F.
- Pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` failure — separate housekeeping bridge.
- LLM-based classification, retrieval-augmented options, transcript-chat scanning, LO INSIGHTS scanning — explicitly removed per owner directive.
- Removal of duplicate `spec-classifier.py` entry in `.claude/settings.local.json` — separate housekeeping commit (harmless to leave both registered).

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/.claude/hooks/spec-classifier.py` (modified — pattern refinement + reminder text update)
- **`E:/GT-KB/.claude/settings.json` (modified — UserPromptSubmit registration of `spec-classifier.py`)**
- `E:/GT-KB/groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py` (new)
- `E:/GT-KB/groundtruth-kb/src/groundtruth_kb/doctor/` (3 new check functions)
- `E:/GT-KB/.groundtruth/formal-artifact-approvals/` (2 amendment packets)
- MemBase `groundtruth.db` (DCL v2 + GOV v2 + IPR v2)

No `applications/` content modified. No `.codex/hooks.json` change.
