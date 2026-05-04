REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice E: Regex-Trigger AUQ Gate (REVISED-1)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-001.md` per Codex `-002` NO-GO + owner directive (no LLM API parallel; canonical regex triggers; AUQ-only spec creation)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Revision Summary

Three drivers converged this cycle:

- **Codex `-002` F1:** `-001` cited a phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` not in MemBase. Actual live spec: `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (the surfacing-transparency rule that `GOV-REQUIREMENTS-COLLECTION-HOOK-001` itself references). REVISED-1 cites the correct spec.
- **Codex `-002` F2:** `-001` proposed creating `IPR-REQUIREMENTS-COLLECTION-HOOK-001` but the record exists in MemBase (status `proposed`, v1, created during S330). REVISED-1 proposes an append-only v2 update to that existing record reflecting the regex-gate implementation path.
- **Owner directive (this turn) — primary scope change:** "We will not add an API key for parallel API usage." + "It is acceptable for the regex-based solution to require that I use explicit language" + "A canonical term, with a set of synonym patterns which I can remember and are intuitive is sufficient." + "It is more important that no requirements specifications are created without my explicit choice from an AskUserQuestion." This reframes Sub-slice E entirely: the hook is a **regex-based gate that detects canonical trigger phrases and forces AUQ-confirmation before any spec creation** — not an LLM classifier. The DCL and GOV contracts both currently mandate LLM classification; both require formal-artifact amendment.

REVISED-1 therefore proposes:

1. **DCL + GOV amendment** (formal-artifact-approval packets) replacing LLM-classifier clauses with regex-trigger + AUQ-gate semantics.
2. **Verification** that the existing `.claude/hooks/spec-classifier.py` (regex-based, 120 LOC) satisfies the amended contract after a small enhancement to its reminder text + canonical trigger set.
3. **IPR v2 append-only update** linking the regex-gate implementation rather than creating a new IPR.
4. **Tests** covering canonical trigger detection + the AUQ-only spec-creation invariant (the strict requirement: no spec is created without an AUQ in the same turn).
5. **Doctor invariants** per the amended DCL.

Scope shrinks materially: no LLM client, no Anthropic API spend, no 15s blocking latency, no retrieval pipeline (still allowed but not required). Implementation grows by ~80-120 LOC (canonical trigger refinement + reminder text update + tests) rather than ~700 LOC.

## Specification Links

**Blocking (per applicability registry + sub-slice scope):**

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (specified) — to be amended; the GOV requirement being amended + implemented.
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` (specified) — to be amended; the binding contract being amended.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (specified) — surfacing transparency (positive + negative paths) that the hook's reminder text must direct AI agent to honor. **Replaces phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` citation in `-001`.**
- `GOV-OWNER-DECISION-SURFACING-001` — predecessor surfacing infrastructure (`memory/pending-owner-decisions.md`).
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate for the DCL/GOV amendments + IPR v2 append.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.codex/hooks.json` registration intent.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** changes confined to `E:\GT-KB\.claude\hooks\spec-classifier.py` (modified), `E:\GT-KB\.claude\settings.json` (already registered), `E:\GT-KB\groundtruth-kb\tests\` (test additions), MemBase via formal-artifact-approval (DCL + GOV amendments + IPR v2). No `applications/` content.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/operating-model.md`, `.claude/rules/project-root-boundary.md`.

**Topic-specific:**

- Umbrella scope at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice E" lines 186-190.
- Existing predecessor hook at `.claude/hooks/spec-classifier.py` (the implementation being verified).
- Peer hook at `.claude/hooks/owner-decision-tracker.py` (UserPromptSubmit + Stop modes; coexists at the same UserPromptSubmit slot).
- Existing IPR record `IPR-REQUIREMENTS-COLLECTION-HOOK-001` v1 status `proposed` (target of v2 append).

**Advisory:** `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` — original S330 design intent (LLM classifier + 3-option clarification).
- `DELIB-S331-AUQ-1/2/3` — umbrella authorization.
- `DELIB-S332-CONTINUE-WITH-SUBSLICE-E` (this session): owner AUQ #3 selecting "Continue with Sub-slice E now".
- `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE` (this session, NEW): owner directive "We will not add an API key for parallel API usage. That incurs an unacceptable additional cost." Authorizes the no-LLM scope of REVISED-1.
- `DELIB-S332-PATH-A-AMEND-DCL-GOV-VERIFY-EXISTING-CHOICE` (this session, NEW): owner AUQ #4 selecting "Amend DCL+GOV; verify existing spec-classifier.py". Authorizes the formal-artifact amendment path.
- `DELIB-S332-CANONICAL-TRIGGER-SET-INTUITIVE-CLARIFICATION` (this session, NEW): owner clarifying message "A canonical term, with a set of synonym patterns which I can remember and are intuitive is sufficient... It is more important that no requirements specifications are created without my explicit choice from an AskUserQuestion." Authorizes the regex-trigger + AUQ-gate design.

## Owner Decisions / Input

- **AUQ S332 #3:** "Continue with Sub-slice E now" — authorizes filing the proposal. `detected_via: ask_user_question`.
- **Owner directive (this turn):** No LLM API key; no parallel API spend. Authorizes the no-LLM scope. `detected_via: owner_directive_in_chat`.
- **AUQ S332 #4:** "Amend DCL+GOV; verify existing spec-classifier.py (Recommended)" — authorizes the formal-artifact amendment path + linking the existing IPR record. `detected_via: ask_user_question`.
- **Owner clarifying message (this turn):** "A canonical term, with a set of synonym patterns... It is more important that no requirements specifications are created without my explicit choice from an AskUserQuestion." Authorizes the regex-trigger + AUQ-gate design. `detected_via: owner_directive_in_chat`.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice work.
- **Pending owner inputs:**
  1. **Canonical trigger set confirmation:** REVISED-1 proposes a starter trigger set (below). Owner can refine via AUQ during Codex review or implementation.

No additional pre-implementation owner decisions required. Codex GO/NO-GO governs proceed.

## Goal

Promote `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` and `GOV-REQUIREMENTS-COLLECTION-HOOK-001` from `specified` → `implemented` with **amended scope** (regex-gate, no LLM, AUQ-gated spec creation):

1. Amend DCL: drop LLM-classifier mandate, retrieval mandate, 4-label enumeration, classifier-model-bounds clauses, additional_context_schema fixed structure, cost-cap/timeout clauses. Replace with: regex-trigger detection against a canonical trigger set; emit reminder via `additionalContext` (or backwards-compatible `systemMessage`) directing AI to AUQ-confirm before any spec creation. Allowed canonical-path locations broadened to existing `.claude/hooks/spec-classifier.py`.
2. Amend GOV: drop "MUST invoke a lightweight LLM classifier" + 4-label enumeration; replace with "MUST detect canonical trigger phrases via fixed regex patterns" + "AI agent MUST use AskUserQuestion to confirm any specification creation triggered by the hook (the AUQ-only-spec-creation invariant)."
3. Verify existing `.claude/hooks/spec-classifier.py` satisfies the amended contract; small enhancement to reminder text emphasizing the AUQ-only invariant; refine `SPEC_PATTERNS` to a small canonical set.
4. Append-only IPR v2 update reflecting regex-gate implementation path.
5. Test suite covering: (a) canonical-trigger detection (positive cases); (b) anti-pattern non-detection; (c) reminder text contains AUQ-only invariant; (d) settings.json registration; (e) hook subprocess smoke.
6. Doctor invariants verifying the amended contract.

## Proposed Canonical Trigger Set (open for owner refinement)

**Canonical term:** *specification* (and its lifecycle siblings: requirement, spec, GOV, ADR, DCL, PB).

**Trigger phrases (regex; case-insensitive; word-boundaried):**

- `\bcreate (?:a |the )?(?:spec|specification|requirement|GOV|ADR|DCL|PB|protected behavior)\b`
- `\b(?:specify|spec|track|capture) (?:that|this|it)\b`
- `\b(?:this|that) is (?:a |an )?(?:requirement|specification|spec|protected behavior)\b`
- `\b(?:make|add) (?:a |an )?(?:requirement|specification|spec|GOV|ADR|DCL)\b`
- `\b(?:from now on|always|never)\b` followed within 5 words by an action verb (preserves existing behavior)
- `\bthe (?:system|product|feature) (?:must|shall|should)\b` (preserves existing imperative pattern)

**Anti-patterns** (already in `spec-classifier.py`): commands like "stop", "show", "list", "fix"; questions; affirmative responses.

The trigger set is intentionally small + intuitive; owner can extend via AUQ during Codex review without re-architecting. Synonyms encoded inline (`spec|specification|requirement`).

## Implementation Plan

### Step 1: Formal-artifact-approval packets for DCL + GOV amendments

Per `GOV-ARTIFACT-APPROVAL-001`, both amendments require formal-artifact-approval packets. Packets cite the four S332 DELIB IDs (NO-LLM directive, Path A AUQ, canonical-trigger clarification, S331 AUQ #3) as authorizing evidence.

**Files Created:**

- `.groundtruth/formal-artifact-approvals/2026-05-04-dcl-requirements-collection-hook-contract-amendment.json`
- `.groundtruth/formal-artifact-approvals/2026-05-04-gov-requirements-collection-hook-amendment.json`

**MemBase Operations:**

- `db.update_spec(id="DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001", new_version=2, ...)` — replaces LLM-mandate clauses with regex-trigger + AUQ-gate clauses.
- `db.update_spec(id="GOV-REQUIREMENTS-COLLECTION-HOOK-001", new_version=2, ...)` — same.

The amendments preserve the rationale, GOV-20 traceability, ADR linkage, and architectural framing while replacing the binding-contract specifics.

### Step 2: Hook enhancement (`.claude/hooks/spec-classifier.py`)

Minimal enhancement preserving existing 120 LOC structure:

- Refine `SPEC_PATTERNS` to the canonical trigger set above.
- Update `REMINDER` text to emphasize AUQ-only-spec-creation:
  > "⚠️ SPECIFICATION TRIGGER — Owner used a canonical specification-language trigger ([trigger phrase]). Per `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2: do NOT create or promote any formal artifact (SPEC/REQ/GOV/ADR/DCL/PB) without first issuing an `AskUserQuestion` to confirm the artifact's existence, scope, and approval. Surface the candidate per `GOV-SPEC-CAPTURE-TRANSPARENCY-001`."
- Optionally migrate output from `systemMessage` to `additionalContext` if amended DCL allows either.

**LOC delta:** ~30-50 lines (pattern refinement + reminder text update + comments).

### Step 3: IPR v2 append-only update

Append v2 of `IPR-REQUIREMENTS-COLLECTION-HOOK-001` reflecting regex-gate implementation: cites this REVISED-1, links to amended DCL v2 + GOV v2, references the existing hook + test paths. Status promotes from `proposed` → `implemented` after Codex VERIFIED.

### Step 4: Test module at `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py`

Test cases:

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
| `test_hook_subprocess_smoke_emits_systemMessage_on_match` | end-to-end subprocess: `Create a specification for X` → reminder emitted |
| `test_hook_subprocess_smoke_emits_empty_on_no_match` | end-to-end subprocess: chat message → empty additionalContext |
| `test_hook_registered_in_claude_settings` | static config: hook in `.claude/settings.json` UserPromptSubmit |

Total: 12 tests. All pure-Python (no LLM, no API calls).

### Step 5: `gt project doctor` invariants per amended DCL

Add 3 doctor checks (smaller than original 4 since LLM-allowlist invariant retired):

- `_check_spec_classifier_canonical_path` — verifies `.claude/hooks/spec-classifier.py` exists.
- `_check_spec_classifier_settings_registered` — verifies UserPromptSubmit registration.
- `_check_spec_classifier_test_exists` — verifies test file at canonical path.

### Step 6: Spec promotion post-VERIFIED

After Codex VERIFIED on the post-impl REPORT:

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001`: specified → implemented → verified (v2 amended)
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`: specified → implemented → verified (v2 amended)
- `IPR-REQUIREMENTS-COLLECTION-HOOK-001`: status proposed → implemented (v2 append)

## Spec-to-Test Mapping

| Spec / Rule | Test |
|---|---|
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 LOCATION | `test_hook_registered_in_claude_settings` + `_check_spec_classifier_canonical_path` |
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 TRIGGER PATTERNS | 7 trigger/anti-pattern tests |
| Amended `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v2 OUTPUT | `test_hook_subprocess_smoke_emits_*` |
| Amended `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v2 AUQ-only invariant | `test_reminder_text_contains_auq_invariant` |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (positive + negative paths via reminder text) | `test_reminder_text_contains_auq_invariant` (reminder cites the spec; AI agent's behavior verified separately by AUQ tests) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- applications/` empty assertion |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `T-bridge-1` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `T-spec-1` (preflight) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT spec-to-test mapping |
| `GOV-ARTIFACT-APPROVAL-001` | DCL + GOV amendment packets verified via formal-artifact-approval-gate hook |

## Acceptance Criteria

Pre-implementation:
- [ ] Codex GO on this REVISED-1
- [ ] Preflight passes

Post-implementation (VERIFIED contingent):
- [ ] DCL + GOV formal-artifact-approval packets created + approved by gate
- [ ] DCL v2 + GOV v2 inserted in MemBase
- [ ] IPR v2 appended (status → implemented)
- [ ] Hook reminder text contains "AskUserQuestion" + "do NOT create" invariant strings
- [ ] All 12 tests PASS
- [ ] 3 doctor checks PASS
- [ ] `git status --short -- applications/` empty
- [ ] No regression in existing `owner-decision-tracker.py` or `formal-artifact-approval-gate.py` behavior

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Canonical trigger set misses owner-intended phrasing | Medium | Low | Owner can extend via AUQ; trigger set is intentionally small + extensible. Anti-pattern + length guards prevent over-firing. |
| Canonical trigger set over-fires (false positives) | Medium | Low | Anti-pattern guards + minimum-length filter; reminder is non-blocking (advisory `systemMessage`/`additionalContext`); cost is low. |
| AI agent ignores AUQ-only invariant in reminder text | Medium | High | Reminder phrased imperatively + cites GOV v2; bridge-compliance-gate hook (Sub-slice C) already enforces Owner Decisions section on bridge artifacts; formal-artifact-approval-gate enforces approval packets on canonical artifacts. Defence-in-depth across three hooks. |
| DCL + GOV amendment scope creates governance drift | Low | Medium | Both amendments retain rationale/traceability; amend rather than retire. Formal-artifact-approval gate audit trail preserves original v1 + amendment evidence. |
| IPR v2 append fails formal-artifact-approval-gate | Low | Low | Packet documents the link explicitly; v2 append is standard append-only operation. |

**Rollback:** Revert the bridge commit. Hook source change is single-file. Test additions are new file. DCL/GOV/IPR mutations are append-only — v1 records remain canonical until v2 lands. To roll back the spec amendments, file v3 specs that revert v1's content.

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
python -m pytest groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py -v --timeout=30
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook or doctor or spec_classifier or requirements" --timeout=120
python -m groundtruth_kb.doctor 2>&1 | grep -E "spec_classifier"
git diff --name-only -- applications/
git status --short
```

Expected: PASS / 12 passed / pre-existing-known-failures only / 3 PASS lines / empty / new files only + modified hook + INDEX.

## Out of Scope

- Sub-slice F (release metrics + gate promotion) — separate bridge after E VERIFIED.
- ISOLATION-018 sub-slices 18.C-18.L — gated by Sub-slice F.
- Pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` failure — separate housekeeping bridge.
- LLM-based classification, retrieval-augmented options, transcript-chat scanning, LO INSIGHTS scanning — explicitly removed per owner directive.

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/.claude/hooks/spec-classifier.py` (modified — pattern refinement + reminder text update)
- `E:/GT-KB/groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py` (new)
- `E:/GT-KB/groundtruth-kb/src/groundtruth_kb/doctor/` (new check functions)
- `E:/GT-KB/.groundtruth/formal-artifact-approvals/` (2 amendment packets)
- MemBase `groundtruth.db` (DCL v2 + GOV v2 + IPR v2 via append-only operations)

No `applications/` content modified. No `.codex/hooks.json` change (existing hook keeps current registration).
