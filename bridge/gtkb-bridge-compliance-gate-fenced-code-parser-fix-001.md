NEW

# Implementation Proposal - Bridge Compliance Gate Fenced-Code Parser Fix (GTKB-BRIDGE-COMPLIANCE-GATE-FENCED-CODE-PARSER-FIX)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-gate-fenced-code-parser-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S355

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3336

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py"]

## Problem

The bridge-compliance-gate PreToolUse hook contains three section-scanner helpers that locate a markdown section by its heading and then collect the section's lines until they reach the next heading. All three use the identical boundary test - a line whose stripped form `startswith("#")` - with no fenced-code-block awareness.

`_has_clean_applicability_preflight` (lines 386-403) is the most consequential. It finds the `## Applicability Preflight` heading, collects subsequent lines, and stops at the first line whose stripped form `startswith("#")`. It then requires the collected section text to contain both a `packet_hash` line and a `missing_required_specs: []` line.

GO and VERIFIED bridge verdicts idiomatically paste the raw output of `scripts/bridge_applicability_preflight.py` inside a fenced code block (```` ```text ````). That pasted tool output is itself markdown and contains a literal `## Applicability Preflight` line. The fence-blind parser treats that in-fence `#` line as the section boundary, stops there, and never reaches the `packet_hash` / `missing_required_specs: []` lines that appear below it inside the same fence. `_has_clean_applicability_preflight` returns `False`, and `_deny_reason_for_content` hard-blocks the Write with: "[Governance] GO and VERIFIED bridge verdicts must include a clean Applicability Preflight section with packet_hash and missing_required_specs: []...".

This is a hard `deny`, not a soft `ask` - the verdict cannot be written at all.

Concrete evidence of the live defect and the harness-parity gap: `bridge/gtkb-prime-worker-context-aware-auq-slice-2-004.md` is a Codex-authored GO verdict. Its real `## Applicability Preflight` heading is at line 66; lines 70-97 paste the preflight tool output inside a ```` ```text ```` fence, and that pasted block contains `## Applicability Preflight` (line 77) and `## Clause Applicability` (line 99/110) heading lines. The `packet_hash` and `missing_required_specs: []` lines sit at lines 79 and 85, below the in-fence `## Applicability Preflight` line. Codex wrote that file successfully because Codex writes verdicts through `.codex/hooks.json`, a separate gate that does not run this Python parser. A Claude session authoring the byte-identical verdict format is hard-blocked by `.claude/hooks/bridge-compliance-gate.py`. The two harnesses therefore disagree on whether a standard, idiomatic GO verdict is a valid bridge write - a real harness-parity defect.

The two sibling scanners share the identical fence-blind boundary scan and the identical class of bug:

- `_has_concrete_spec_links` (lines 189-208) collects the `## Specification Links` section the same way. A proposal that pastes a `## Specification Links`-shaped line inside a fenced block before its real citation bullets would have its real citations mis-truncated.
- `_has_concrete_owner_decisions_section` (lines 231-250) collects the `## Owner Decisions / Input` section the same way and is vulnerable identically.

The defect class is latent for the two sibling scanners today because real proposals rarely fence a section-heading-shaped line ahead of the real section content, but the parser is incorrect for all three, and a consistent fix removes the whole class rather than only the one instance currently firing.

The scaffold template copy `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` is byte-identical to the live hook (verified with `diff`) and carries all three buggy scanners, so adopter projects scaffolded from the template inherit the defect.

## Claim

Make the section-boundary scan in `bridge-compliance-gate.py` fenced-code-block aware: track ```` ``` ```` fence open/close state while collecting a section, and do not treat a `#` line as a section boundary while inside a fence. Apply the fix consistently across all three scanners by routing them through one shared, pure, importable helper. Apply the byte-identical change to the scaffold template. Add a regression test in the platform test lane.

This removes a false-positive hard-block. It removes no governance coverage: a GO/VERIFIED verdict that genuinely lacks a `packet_hash` or a `missing_required_specs: []` line still fails the gate, because those lines are still absent from the (now correctly bounded) section text; a proposal that genuinely lacks concrete spec links or a concrete owner-decisions section still fails. The fix only changes where the section ends - it never relaxes what the section must contain.

## In-Root Placement Evidence

All three `target_paths` are in-root under `E:\GT-KB`: `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, and `platform_tests/hooks/`. The bridge proposal file resides under `E:\GT-KB\bridge\`. No `target_path` and no output path is outside the project root.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and bridge verdict files are canonical workflow state; a gate hook that hard-blocks a valid GO/VERIFIED verdict obstructs that canonical workflow. The direct governing authority for keeping the verdict-write gate correct.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - establishes the Claude/Codex hook-parity model. This proposal repairs a concrete parity gap: the Claude-side compliance gate rejects a verdict format the Codex-side gate accepts.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate participates in the deterministic policy engine; the fix keeps the gate's verdict-classification path deterministic and correct.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the fence-aware boundary scan is a deterministic state machine over markdown lines, with no LLM classification.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries concrete specification links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-test mapping and executed test command evidence.
- GOV-RELIABILITY-FAST-LANE-001 - a small, single-concern defect fix filed through the reliability fast-lane under the standing project and standing authorization.
- GOV-STANDING-BACKLOG-001 - WI-3336 is tracked in the MemBase backlog under PROJECT-GTKB-RELIABILITY-FIXES.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root under `E:\GT-KB`; the scaffold-template copy keeps adopter applications consistent with the platform.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and fix are preserved as durable artifacts (WI-3336, this proposal, the regression test).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, test, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3336 moves through backlogged, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search ("bridge compliance gate hook parity fenced code applicability preflight") was run against the canonical `current_deliberations` view. Relevant prior records:

- DELIB-1637, DELIB-1638, DELIB-1639, DELIB-1640 - the `gtkb-codex-bridge-compliance-gate-parity` review chain (Codex Bridge-Compliance-Gate Hook Parity, NEW through REVISED-3 GO). That thread brought the Codex-side gate to parity with the Claude-side gate's intent. It did not inspect the section-boundary scanners for fenced-code correctness; this proposal addresses a parity gap that thread did not surface.
- DELIB-1920 - "Bridge thread: gtkb-codex-bridge-compliance-gate-parity (8 versions, GO)" - the consolidated thread record for the prior parity work.
- DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 - S337 owner decision refreshing the harness hook-parity fallback stance; the broader governance context for treating Claude/Codex gate divergence as a defect.

No prior deliberation rejected or already addressed a fenced-code-aware section scan in this hook.

## Owner Decisions / Input

- 2026-05-16 UTC, S355: the owner identified the `_has_clean_applicability_preflight` fence-blind parser bug in `.claude/hooks/bridge-compliance-gate.py`, supplied `bridge/gtkb-prime-worker-context-aware-auq-slice-2-004.md` as evidence of the harness-parity gap, and directed Prime Builder to route the fix through the GT-KB bridge protocol: file a proposal under the slug `gtkb-bridge-compliance-gate-fenced-code-parser-fix`, cite the relevant specifications, include spec-derived tests (a verdict fixture with fenced preflight output must pass the gate; a verdict genuinely missing `packet_hash` must still fail), obtain a Loyal Opposition GO, then implement. This proposal executes that directive. No further owner decision is pending for the fix itself; implementation proceeds on Codex GO under the standing reliability-fast-lane authorization (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING).

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already establishes the bridge verdict files as canonical workflow state, and ADR-CODEX-HOOK-PARITY-FALLBACK-001 already establishes the Claude/Codex hook-parity requirement; the fix aligns the gate's parser with those existing requirements. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single-concern defect fix tracked by exactly one work item, WI-3336, an active member of PROJECT-GTKB-RELIABILITY-FIXES. No work-item state inventory, bulk transition, or backlog cleanup is performed. The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001) covers this fix through active project membership under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; that governance requires no per-fix formal-artifact-approval packet.

## Bridge INDEX Update Evidence

A NEW entry for `gtkb-bridge-compliance-gate-fenced-code-parser-fix` is inserted at the top of `bridge/INDEX.md`, below the header comments and above the first existing Document entry. No prior bridge file and no prior INDEX entry is deleted or rewritten; the append-only audit trail is preserved.

## Proposed Scope

### IP-1: Fenced-code-aware section scan in the live hook

In `.claude/hooks/bridge-compliance-gate.py`, add one pure, importable helper that collects a section's lines with fenced-code-block awareness:

```python
def _collect_section_lines(lines: list[str], start: int) -> list[str]:
    """Collect section lines from index `start` until the next heading.

    A line whose stripped form starts with "#" ends the section ONLY when
    the scan is not inside a fenced code block. A line whose stripped form
    starts with a triple backtick toggles fence state; heading-shaped lines
    inside a fence (e.g. pasted tool output) are body content, not a
    section boundary.
    """
    section: list[str] = []
    in_fence = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            section.append(line)
            continue
        if not in_fence and stripped.startswith("#"):
            break
        section.append(line)
    return section
```

Route all three section scanners through the helper, replacing each inline `for line in lines[start:]: ... if stripped.startswith("#"): break` loop:

- `_has_clean_applicability_preflight` - `section = _collect_section_lines(lines, start)`.
- `_has_concrete_spec_links` - same substitution.
- `_has_concrete_owner_decisions_section` - same substitution.

The collected-lines content and every downstream check (`PREFLIGHT_PACKET_HASH_RE`, `PREFLIGHT_MISSING_REQUIRED_RE`, `SPEC_LINK_TOKEN_RE`, `SPEC_PLACEHOLDER_RE`, `OWNER_DECISIONS_PLACEHOLDER_LINE_RE`) are unchanged. Behavior changes only for sections whose body contains a fenced block with a heading-shaped line: those lines are now correctly treated as body, so the scan reaches the real section end. For sections with no in-fence heading, the helper yields exactly the same lines as the current inline loop.

### IP-2: Identical fix in the scaffold template

Apply the byte-identical change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so adopter projects scaffolded from the template do not inherit the defect. The two files are byte-identical today (verified with `diff`) and remain byte-identical after the fix.

### IP-3: Regression test

Add `platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py`, parametrized over both hook copies (live + template), importing the hyphenated hook modules by path (the pattern already used by the existing `test_bridge_compliance_gate_*` modules in `platform_tests/hooks/`). Coverage:

- `_has_clean_applicability_preflight` returns `True` for a GO verdict whose real `## Applicability Preflight` heading is followed by a ```` ```text ```` fenced block that itself contains `## Applicability Preflight` / `## Clause Applicability` lines, with the real `packet_hash: sha256:<64-hex>` and `missing_required_specs: []` lines inside that fence (the core regression - currently returns `False`).
- `_has_clean_applicability_preflight` still returns `False` for a GO verdict whose Applicability Preflight section genuinely lacks a `packet_hash` line (gate coverage preserved).
- `_has_clean_applicability_preflight` still returns `False` for a GO verdict that genuinely lacks the `missing_required_specs: []` line (gate coverage preserved).
- `_has_concrete_spec_links` returns `True` for a proposal whose `## Specification Links` section contains a fenced block with a heading-shaped line before the real `SPEC-`/`GOV-` citation bullets.
- `_has_concrete_owner_decisions_section` returns `True` for a proposal whose `## Owner Decisions / Input` section contains a fenced block with a heading-shaped line before the real, non-placeholder decision text.
- `_collect_section_lines` unit cases: stops at a real out-of-fence heading; does not stop at an in-fence heading; collects to end-of-input when a fence is never closed (defensive - an unterminated fence yields the rest of the document, which is acceptable and strictly more permissive than the buggy early stop).

### Out of scope

Tilde-delimited fences (`~~~`) are not used anywhere in the `bridge/` corpus; the helper handles backtick fences only. If a tilde fence is ever introduced, the helper degrades to the current (buggy) behavior for that one section, which is no worse than today. No behavior change to `_advisory_report_template_gaps`, the project-metadata gate, the WI-project membership check, or the pending-proposal `ask` checkpoint.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | A GO verdict pasting preflight output inside a fence passes the Applicability Preflight gate | test_go_verdict_with_fenced_preflight_output_passes |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | The verdict format Codex writes (fenced preflight output) is accepted by the Claude-side gate | test_go_verdict_with_fenced_preflight_output_passes |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A GO verdict genuinely missing packet_hash still fails the gate | test_go_verdict_missing_packet_hash_still_fails |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A GO verdict genuinely missing missing_required_specs still fails the gate | test_go_verdict_missing_required_specs_line_still_fails |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `_has_concrete_spec_links` reaches real citations past an in-fence heading | test_spec_links_with_fenced_heading_still_detected |
| SPEC-AUQ-POLICY-ENGINE-001 | `_has_concrete_owner_decisions_section` reaches real content past an in-fence heading | test_owner_decisions_with_fenced_heading_still_detected |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | `_collect_section_lines` is a deterministic fence/heading state machine (stops at real heading, not in-fence heading, runs to EOF on unterminated fence) | test_collect_section_lines_fence_state_machine |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Both hook copies carry the fix | all tests, parametrized over the live and template hooks |

Execution command:

`python -m pytest platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py -v`

The post-implementation report will also re-run the existing bridge-compliance-gate tests (`test_bridge_compliance_gate_project_metadata.py`, `test_bridge_compliance_gate_wi_project_membership.py`, `test_bridge_compliance_gate_hard_block_workspace.py`, `test_bridge_compliance_gate_index_exemption.py`) to confirm no regression, and `ruff` over the changed files.

## Acceptance Criteria

- IP-1, IP-2, and IP-3 landed.
- A GO/VERIFIED verdict that pastes `bridge_applicability_preflight.py` output inside a fenced code block (the format in `bridge/gtkb-prime-worker-context-aware-auq-slice-2-004.md`) passes `_has_clean_applicability_preflight`.
- A GO/VERIFIED verdict genuinely missing `packet_hash` or `missing_required_specs: []` still fails the gate (coverage preserved).
- `_has_concrete_spec_links` and `_has_concrete_owner_decisions_section` are routed through the same fence-aware helper.
- The live hook and the scaffold template copy remain byte-identical.
- The new test file passes; existing bridge-compliance-gate tests still pass; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Two implementation options were considered.

Option A (selected): one shared, pure helper `_collect_section_lines` that all three scanners call. Rationale: the three scanners have the identical fence-blind bug; a single fence-aware helper fixes the whole class in one place, removes the triplicated inline loop, and is directly unit-testable - matching the existing test pattern for this hook, which imports and exercises helper functions. The helper is underscore-prefixed and private; external hook behavior changes solely by the fence-awareness correction.

Option B (rejected): add an inline `in_fence` flag to each of the three scanner loops independently. Rejected because it triplicates the fence-tracking logic, leaves three places to drift out of sync on a future change, and offers no single unit-testable surface for the fence state machine. Option A's consolidation is the same refactor-for-testability pattern used by the sibling `gtkb-bridge-compliance-gate-index-exemption` fix.

## Risks / Rollback

- Risk: the fence detection is too eager and a non-fence line that starts with three backticks suppresses a real section boundary. Mitigation: a markdown line whose stripped form starts with ```` ``` ```` is a fence delimiter by the CommonMark spec; there is no other meaning. Inline code spans use single backticks and do not start a line with three. Covered by test_collect_section_lines_fence_state_machine.
- Risk: an unterminated fence makes a section run to end-of-document. Mitigation: this is strictly more permissive than the current early stop and cannot cause a false-negative on a real section; a malformed proposal with an unterminated fence is already a separate authoring defect. Covered by the unterminated-fence test case.
- Risk: the helper extraction changes behavior for sections with no fenced block. Mitigation: with `in_fence` never set, the helper's break condition is identical to the current inline loop; covered by the missing-packet_hash and missing-missing_required_specs tests, which exercise non-fenced failure paths.
- Rollback: revert the three files; the change is self-contained with no schema, configuration, or data migration.

## Recommended Commit Type

`fix` - repairs broken hook behavior (a false-positive hard-block) with no new capability surface. The shared-helper extraction is an internal refactor in service of the fix and of testability, not a new public interface.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
