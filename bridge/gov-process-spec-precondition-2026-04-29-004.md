NO-GO

# Loyal Opposition Review - Activate Existing Specification-Linkage Enforcement REVISED-1

**Document:** `gov-process-spec-precondition-2026-04-29`
**Reviewed version:** `bridge/gov-process-spec-precondition-2026-04-29-003.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Claim

The revision correctly narrows the work to activating the existing framework hook and closes the prior `Specs:` / `Specification Links` schema conflict. It still cannot receive GO because the byte-for-byte hook it proposes to activate does not reject or hard-block non-compliant bridge writes, while the proposal's acceptance criterion and cited DCL require rejection/blocking.

## Prior Deliberations

Searches for `gov-process-spec-precondition`, `spec-linkage`, `bridge-compliance-gate`, and `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` found one related deliberation: `DELIB-0993`, sourced from `bridge/gtkb-gov-proposal-standards-slice1-002.md`, referencing the same `bridge-compliance-gate.py` surface. No prior deliberation found for this specific `gov-process-spec-precondition-2026-04-29` thread or the new S321 DCL IDs.

## Findings

### F1 - The proposed byte-for-byte hook asks; it does not reject

**Severity:** High

**Evidence:** The revised proposal says the new activation test derives from `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1`, which requires the Write/Edit hook to "MUST reject non-compliant bridge proposals": `bridge/gov-process-spec-precondition-2026-04-29-003.md:27`. Its scope and acceptance criteria also require a synthetic payload to "blocks a non-compliant bridge write" and future bridge proposals to be "blocked at write time": `bridge/gov-process-spec-precondition-2026-04-29-003.md:37-40`, `bridge/gov-process-spec-precondition-2026-04-29-003.md:67`.

The template hook to be copied byte-for-byte imports `emit_ask`, not `emit_deny`, and the non-compliant bridge-proposal path calls `emit_ask(...)` before exiting zero: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:176-237`. The canonical output helper defines `emit_ask` as "Pause and ask user whether to proceed" with `permissionDecision: "ask"`; `emit_deny` is the helper that "Hard-block[s] tool execution" with `permissionDecision: "deny"`: `groundtruth-kb/src/groundtruth_kb/governance/output.py:30-53`.

The cited DCL artifact is stricter than an ask prompt: `scripts/_temp_create_s321_specs.py:92-100` says the hook "MUST reject" proposals lacking concrete `Specification Links`, and `scripts/_temp_create_s321_specs.py:323-331` says verified/implemented governing specs need a check that fails closed.

**Risk / impact:** A user approval prompt is useful visibility, but it is not mechanical rejection. Approving this proposal as written would mark the S321 DCL's write-time assertion as enforced when the actual behavior remains user-overridable. That repeats the documentation-only enforcement gap this bridge is meant to reduce.

**Required revision:** Choose one of these contracts and make the proposal/test plan match it:

1. For true enforcement, copy or adapt the hook so non-compliant bridge proposals emit `permissionDecision: "deny"` or otherwise use a documented hard-blocking path, and update tests to assert that hard-blocking output.
2. For visibility-only activation, revise the proposal and DCL/test mapping to say the hook only prompts/asks, not rejects/blocks, and leave DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1 explicitly unenforced until a later bridge changes the hook behavior.

### F2 - The test plan still has an exit-code mismatch

**Severity:** Medium

**Evidence:** The revised test case says a non-compliant synthetic Write should make the hook return "non-zero exit / blocking response": `bridge/gov-process-spec-precondition-2026-04-29-003.md:110`. The template exits with code `0` after both ask decisions and pass decisions: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:195-237`. The canonical structured-hook path for blocking is also exit-zero with `permissionDecision: "deny"`, not non-zero exit: `groundtruth-kb/src/groundtruth_kb/governance/output.py:46-53`.

**Risk / impact:** A literal implementation of the proposed test can either fail against the byte-for-byte template or incorrectly treat any `hookSpecificOutput` as "blocking", hiding the ask-vs-deny gap in F1.

**Required revision:** Specify the exact assertion. For enforcement, assert `returncode == 0` and `hookSpecificOutput.permissionDecision == "deny"`. For visibility-only activation, assert `permissionDecision == "ask"` and explicitly do not call it blocking.

## Positive Evidence

- The selected bridge entry remained actionable: live `bridge/INDEX.md:8-11` showed latest status `REVISED: bridge/gov-process-spec-precondition-2026-04-29-003.md`.
- The revised proposal removed the conflicting `Specs:` schema and uses `## Specification Links`: `bridge/gov-process-spec-precondition-2026-04-29-003.md:13-27`.
- The cited DCL/GOV IDs exist in `groundtruth.db` at status `specified`: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`, and `GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001`.
- The current GT-KB workspace still lacks active hook activation, which matches the proposal's problem statement: `.claude/settings.json:5-15` registers only `formal-artifact-approval-gate.py` under `PreToolUse`, and `.claude/hooks/bridge-compliance-gate.py` is absent.

## Decision Needed From Owner

None. This is a revision task for Prime Builder.

## Scan Result

File bridge scan: 1 entries processed.
