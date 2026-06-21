NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - bridge-compliance-gate regex: accept markdown-bold variant or emit pattern in error message

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-gate-regex-bold-variant
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3496

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The `bridge-compliance-gate` hook detects required proposal sections with ATX-anchored heading regexes (`^#{1,6}\s*<name>\s*$`, e.g. `SPEC_LINK_HEADING_RE`, `REQUIREMENT_SUFFICIENCY_HEADING_RE`, `OWNER_DECISIONS_HEADING_RE`, `PRIOR_DELIBERATIONS_HEADING_RE`, `SPEC_TEST_HEADING_RE`). An author who writes a section header in the markdown-bold variant (`**Specification Links**`) instead of an ATX heading (`## Specification Links`) is hard-denied as if the section were absent, and the hard-deny messages (e.g. line ~1293 "Implementation proposals must include concrete Specification Links"; line ~1359 the Requirement Sufficiency gap; line ~1305 the Owner Decisions / Input gap) do NOT state the heading form the hook expects. The author has written the section but cannot tell from the message why it was not recognized. This is a developer-experience defect in the mechanical bridge gate.

The fix makes the hard-deny messages self-documenting by appending the canonical ATX heading form the hook recognizes (e.g. "expected a heading line such as `## Specification Links` — the markdown-bold form `**Specification Links**` is not recognized as a heading"). This is the "emit pattern in error message" arm of the WI's two-option title. It is purely additive to message text: it does not change which content the hook accepts or rejects, so it cannot regress any acceptance/rejection decision. This mirrors the precedent already in the hook at `_ask_reason_for_content` (line ~726), which already names the expected `## Specification Links` form in its ask-checkpoint message.

## Defect / Reproduction

Root cause: section-presence helpers scan for a heading line matching an ATX-only regex. `SPEC_LINK_HEADING_RE` (line ~101) is `^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$`; `REQUIREMENT_SUFFICIENCY_HEADING_RE` (line ~224), `OWNER_DECISIONS_HEADING_RE` (line ~159), `PRIOR_DELIBERATIONS_HEADING_RE` (line ~128), and `SPEC_TEST_HEADING_RE` (line ~133) are the same ATX shape. The markdown-bold form `**Specification Links**` is markdown emphasis, not a heading, so none of these regexes match it. When the heading is absent in strict form, `_has_concrete_spec_links` / `_requirement_sufficiency_section_gap` / `_has_concrete_owner_decisions_section` report the section absent and `_deny_reason_for_content` returns a hard-deny.

Reproduction (logical): write a bridge proposal whose section header is `**Specification Links**` (bold) instead of `## Specification Links`, with otherwise-concrete spec citations beneath it. Run the gate on the Write. Observed: hard-deny "Implementation proposals must include concrete Specification Links before bridge submission" — the message gives no indication that the bold form is the problem or that an ATX heading is required. Expected (post-fix): the same hard-deny message additionally states the recognized heading form (`## Specification Links`) and notes that the markdown-bold variant is not recognized as a heading, so the author can immediately correct the heading.

The reproduction is exercised by the new regression tests, which assert (a) the bold-variant heading is still treated as a missing section (acceptance/rejection unchanged) and (b) the hard-deny message now names the expected ATX form.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py`. The live hook under `.claude/hooks/` and the tracked activation source under `groundtruth-kb/templates/hooks/` are currently byte-identical (sha256 `5b530f74...`) and are updated in lockstep, matching the precedent in `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the Project Authorization / Project / Work Item linkage metadata lines required of an implementation proposal.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the affected component is the bridge-compliance gate that enforces file-bridge authority at Write time; clearer denials strengthen, not weaken, the authority model (blocking applicability rule, doc-match `*`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable bridge-proposal artifact contract by helping authors produce well-formed section headings rather than silently failing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification (mandatory linkage); the defect itself concerns the Specification Links section-detection path enforced under this DCL.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each test from a cited spec clause and runs executed test commands (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - one of the affected deny paths is the Owner Decisions / Input (AskUserQuestion) section gate; the message-clarity fix touches its hard-deny text, so the AUQ policy surface is in scope and must not be weakened.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform hook (live + template) and platform tests; no `applications/` or adopter surface is touched and no platform/application placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3496 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the hook has a Codex parity surface; updating the live hook and the tracked template in lockstep preserves cross-harness parity of the enforcement boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix keeps the gate's deny messages traceable to the heading contract documented in `.claude/rules/file-bridge-protocol.md`, preserving artifact traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the change touches the gate that helps proposals reach a verified lifecycle state; clearer denials reduce churn in the proposal-to-GO transition.

## Prior Deliberations

- `DELIB-2215` - Bridge thread gtkb-bridge-compliance-gate-wi-auto-regex-fix (VERIFIED) - prior regex-detection fix in this same hook; precedent that compliance-gate regex defects are corrected through a scoped bridge thread.
- `DELIB-20263744` - VERIFIED, Bridge Compliance Gate WI-AUTO Regex Fix - the verified outcome of that prior regex fix; confirms the lockstep live+template + parametrized-test pattern used here.
- `DELIB-20263745` - Loyal Opposition Review, Bridge Compliance Gate WI-AUTO Regex Fix - the review of that prior regex fix; documents the reviewer expectations for compliance-gate regex changes.
- _No prior deliberations specifically address the "emit expected heading pattern in the deny message" message-clarity arm; the WI-3351 spec-test-heading fix (`test_bridge_compliance_gate_spec_test_heading.py`) is the closest structural precedent (lockstep live+template, parametrized test) and is followed here._

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and the section-requirement rules in `.claude/rules/file-bridge-protocol.md` already establish which sections an implementation proposal must contain and that the canonical heading form is the ATX `## <Section>` heading (the body status-token and section-gate rules cite `## Specification Links`, `## Requirement Sufficiency`, `## Owner Decisions / Input`, `## Prior Deliberations`). This fix makes the existing gate's deny messages name that already-required form; it adds no new public API, no new CLI surface, and no new or revised requirement/specification. The acceptance/rejection behavior of the gate is unchanged.

## Proposed Scope

1. In `.claude/hooks/bridge-compliance-gate.py`, augment the hard-deny message strings in `_deny_reason_for_content` for the section-presence failures so each names the canonical ATX heading form the hook recognizes and notes that the markdown-bold variant is not recognized as a heading. Concretely, extend the deny messages for:
   - the missing-Specification-Links branch (line ~1293) -> add "expected a heading line such as `## Specification Links`; the markdown-bold form `**Specification Links**` is not recognized as a heading".
   - the Requirement Sufficiency gap branch (line ~1359) -> add "expected a `## Requirement Sufficiency` heading; the markdown-bold form is not recognized".
   - the Owner Decisions / Input branch (line ~1305) -> add "expected a `## Owner Decisions / Input` heading; the markdown-bold form is not recognized".
   This is a message-text-only change. No regex, no acceptance/rejection logic, and no control flow is modified. (Optional internal helper: a single `_CANONICAL_HEADING_HINT` constant or small formatter to keep the three messages consistent and DRY; still message-text-only.)
2. Apply the identical change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so the live hook and the tracked activation template remain byte-identical (lockstep, per the spec-test-heading precedent).
3. Add a new regression test file `platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py`, parametrized over both the live and template hook copies (mirroring `test_bridge_compliance_gate_spec_test_heading.py`), covering the assertions in the verification plan.

Scope discipline: the "accept markdown-bold variant as a heading" alternative in the WI title is deliberately NOT taken — treating `**...**` as a heading would broaden five regexes and could mask malformed proposals (a behavior change). The message-clarity arm fully resolves the author-confusion defect with zero acceptance-behavior change and is the lower-risk, single-concern path. If the owner later prefers the accept-bold arm, that is a separate behavior-change proposal.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (Specification Links section detection) | `test_bold_spec_links_heading_deny_message_names_atx_form` | A proposal whose Specification Links header is the markdown-bold form `**Specification Links**` is still denied, AND `_deny_reason_for_content` includes the canonical `## Specification Links` ATX form in its message. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (acceptance behavior unchanged) | `test_bold_heading_section_still_treated_as_missing` | The bold-variant heading is still treated as a missing section (acceptance/rejection decision unchanged); a proper `## Specification Links` ATX heading with concrete citations is NOT denied. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (lockstep live+template) | `test_deny_message_identical_across_live_and_template` (parametrized `gate` fixture over live + template) | Both hook copies expose the augmented deny message identically (parametrized test passes for both `live` and `template`). |
| `SPEC-AUQ-POLICY-ENGINE-001` (Owner Decisions / Input gate message clarity) | `test_owner_decisions_bold_heading_deny_message_names_atx_form` | A proposal that claims owner-approval scope but uses a markdown-bold `**Owner Decisions / Input**` header is denied AND the message names the canonical `## Owner Decisions / Input` ATX form. |

Execution commands:
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py -q --tb=short`
- `python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py`
- `python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py`

## Acceptance Criteria

1. The hard-deny messages for the missing Specification Links, missing Requirement Sufficiency, and missing Owner Decisions / Input sections each name the canonical ATX heading form (e.g. `## Specification Links`) and note that the markdown-bold variant is not recognized as a heading.
2. The gate's acceptance/rejection behavior is unchanged: a bold-variant heading is still treated as a missing section, and a proper ATX `## <Section>` heading with concrete content is still accepted.
3. `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical after the change.
4. The new regression tests pass for both the live and template hook copies; `ruff check` and `ruff format --check` are clean on all three changed files.

## Risks / Rollback

- Risk: a message-string edit could accidentally alter the deny condition or break an existing test that asserts substring presence in a deny message. Mitigation: the change is append-only to message text within existing branches; existing assertions look for substrings such as "Specification Links" that remain present. The new tests lock the augmented text.
- Risk: live and template copies drift if only one is edited. Mitigation: edit both, and the parametrized test asserts the augmented message is present in both copies (a drift would fail the `template` parametrization).
- Risk: scope creep into accepting the bold variant as a heading. Mitigation: explicitly out of scope; this proposal changes message text only.
- Rollback: revert the message-string edits in both hook copies and remove the new test file. The change is fully reversible with no migration, no schema change, and no state.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/hooks/test_bridge_compliance_gate_heading_pattern_message.py`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3496 is origin=defect, single-concern, message-text-only, introduces no new public surface and no new/revised spec, and is bounded to two byte-identical hook copies + one new test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3496 (P3, origin=defect) is in scope for this batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing reliability fast-lane authorization (via PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) under which small, single-concern defect fixes proceed through the normal bridge protocol without a fresh per-item owner approval.

## Recommended Commit Type

`fix`
