NEW

# Implementation Proposal - Bridge Compliance Gate SPEC_TEST_HEADING_RE re.MULTILINE Fix (GTKB-BRIDGE-COMPLIANCE-GATE-SPEC-TEST-HEADING-MULTILINE-FIX)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S356

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3351

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py"]

## Problem

`SPEC_TEST_HEADING_RE` (lines 46-49 of `.claude/hooks/bridge-compliance-gate.py`) is compiled with `re.IGNORECASE` only - it lacks `re.MULTILINE`. It is consumed via `SPEC_TEST_HEADING_RE.search(content)` inside `_has_spec_derived_verification` (lines 211-216).

In a Python regex compiled without `re.MULTILINE`, the `^` anchor matches only at string offset 0. A VERIFIED bridge verdict's content always begins with the literal first-line status token `VERIFIED`, so the mid-document `## Spec-to-Test Mapping` (or `## Specification-Derived Verification`) heading can never satisfy the `^#{1,6}` prefix. `SPEC_TEST_HEADING_RE.search(content)` therefore returns `None` for every VERIFIED-first verdict.

`_has_spec_derived_verification` requires three conjuncts: `_has_concrete_spec_links(content)` AND `SPEC_TEST_HEADING_RE.search(content)` AND `COMMAND_EVIDENCE_RE.search(content)`. The first and third are correct - `_has_concrete_spec_links` uses a per-line `.match()` scan, and `COMMAND_EVIDENCE_RE` has no `^` anchor. The middle conjunct is always `None`, so `_has_spec_derived_verification` always returns `False` for VERIFIED-first content.

In `_deny_reason_for_content`, the branch `if first_line == "VERIFIED" and not _has_spec_derived_verification(content)` (lines 590-596) then hard-blocks the Write with: "[Governance] VERIFIED bridge reports must carry Specification Links, a spec-to-test mapping, and executed test command evidence...". This is a hard `deny`, not a soft `ask` - a Claude session cannot write the verdict at all.

The result: the bridge-compliance-gate PreToolUse hook hard-blocks EVERY Claude-authored VERIFIED bridge verdict, even one that is fully complete - `## Specification Links` present, a `## Spec-to-Test Mapping` table present, and `python -m pytest` command evidence present. The defect was hit twice during the WI-3338 and WI-3339 (Antigravity Integration) bridge cycles on 2026-05-16. The workaround was that Codex authored the VERIFIED verdicts: Codex writes verdicts through `.codex/hooks.json`, a separate interception boundary that does not run this Python parser. That workaround fails whenever Codex is unavailable, leaving no harness able to file a VERIFIED verdict and halting the terminal step of the bridge protocol.

The scaffold template copy `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` carries the byte-identical `SPEC_TEST_HEADING_RE` definition, so adopter projects scaffolded from the template inherit the same defect.

## Sibling-regex audit

`SPEC_TEST_HEADING_RE` is the only defective regex in the hook. Every other `^`-anchored regex was inspected:

- `OWNER_DECISIONS_HEADING_RE`, `PROJECT_AUTHORIZATION_LINE_RE`, `PROJECT_LINE_RE`, `WORK_ITEM_LINE_RE`, `BRIDGE_KIND_LINE_RE`, `PROJECT_AUTHORIZATION_VALUE_RE`, `PROJECT_VALUE_RE`, `WORK_ITEM_VALUE_RE`, `SPEC_LINK_TOKEN_RE` - all carry `re.MULTILINE` and are consumed via `.search(content)`. Correct.
- `SPEC_LINK_HEADING_RE`, `APPLICABILITY_PREFLIGHT_HEADING_RE`, `OWNER_DECISIONS_PLACEHOLDER_LINE_RE` - `^`-anchored without `re.MULTILINE`, but consumed via per-line `.match()` scans (in `_has_concrete_spec_links`, `_has_clean_applicability_preflight`, `_has_concrete_owner_decisions_section`). `.match()` anchors at the start of each line passed to it, so `re.MULTILINE` is irrelevant. Correct.

`SPEC_TEST_HEADING_RE` is the unique case of a `^`-anchored pattern consumed via `.search(content)` without `re.MULTILINE`. The fix is therefore complete and single-concern.

## Claim

Add `re.MULTILINE` to the `SPEC_TEST_HEADING_RE` compile flags in both copies of `bridge-compliance-gate.py`. With `re.MULTILINE`, the `^` anchor matches at the start of every line, so the mid-document spec-to-test heading is found by `.search(content)` and `_has_spec_derived_verification` returns the correct result.

This removes a false-positive hard-block. It removes no governance coverage: a VERIFIED verdict that genuinely lacks a spec-to-test mapping heading still fails the gate (no heading line matches anywhere in the content); a verdict that genuinely lacks concrete Specification Links or executed-test command evidence still fails (those conjuncts are unchanged). The fix changes only whether a heading that is genuinely present can be detected.

## Reproduction

The live hook module was loaded and exercised against a complete VERIFIED verdict fixture (first line `VERIFIED`; a `## Specification Links` section with a `GOV-` citation; a clean `## Applicability Preflight` section; a `## Spec-to-Test Mapping` table; a `python -m pytest` command line). Observed:

- `_has_concrete_spec_links` -> `True`
- `SPEC_TEST_HEADING_RE.search(content)` -> `None`  (the defect)
- `COMMAND_EVIDENCE_RE.search(content)` -> `True`
- `_has_spec_derived_verification(content)` -> `False`  (consequence)
- `_deny_reason_for_content(...)` -> the VERIFIED hard-block message
- `SPEC_TEST_HEADING_RE.flags` -> 34 (`re.IGNORECASE | re.UNICODE`; the `re.MULTILINE` bit is absent)

Recompiling the identical pattern string with `re.MULTILINE` added makes `.search()` match the `## Spec-to-Test Mapping` heading. This confirms the single-flag correction.

## In-Root Placement Evidence

All three `target_paths` are in-root under `E:\GT-KB`: `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, and `platform_tests/hooks/`. The bridge proposal file resides under `E:\GT-KB\bridge\`. No `target_path` and no output path is outside the project root. ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT satisfied.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge verdict files are canonical workflow state; a gate hook that hard-blocks a valid VERIFIED verdict obstructs the terminal step of that canonical workflow. The direct governing authority for keeping the verdict-write gate correct.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - establishes the Claude/Codex hook-parity model. This proposal repairs a concrete parity gap: the Claude-side compliance gate rejects a VERIFIED verdict format the Codex-side gate accepts.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate participates in the deterministic policy engine; the fix keeps the gate's verdict-classification path deterministic and correct.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the fix is a one-flag change to a deterministic regex; no LLM classification is introduced.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries concrete specification links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the gate branch being repaired mechanizes this constraint. The fix makes the mechanization correctly detect a present spec-to-test mapping instead of always rejecting it; the post-implementation report will carry a spec-to-test mapping and executed test command evidence.
- GOV-RELIABILITY-FAST-LANE-001 - a small, single-concern defect fix filed through the reliability fast-lane under the standing project and standing authorization.
- GOV-STANDING-BACKLOG-001 - WI-3351 is tracked in the MemBase backlog under PROJECT-GTKB-RELIABILITY-FIXES.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root under `E:\GT-KB`; the scaffold-template copy keeps adopter applications consistent with the platform.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and fix are preserved as durable artifacts (WI-3351, this proposal, the regression test).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, test, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3351 moves through backlogged, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search ("bridge compliance gate verified verdict regex multiline heading" and "SPEC_TEST_HEADING spec-to-test mapping hard-block hook parity") was run against the canonical deliberations index. No prior deliberation addresses, rejects, or already resolves the `SPEC_TEST_HEADING_RE` re.MULTILINE defect. Relevant surrounding records:

- DELIB-1637, DELIB-1638, DELIB-1639, DELIB-1640 - the gtkb-codex-bridge-compliance-gate-parity review chain. That thread brought the Codex-side gate to parity with the Claude-side gate's intent; it did not inspect `SPEC_TEST_HEADING_RE` for the missing `re.MULTILINE` flag.
- DELIB-1920 - the consolidated thread record for the prior Codex bridge-compliance-gate parity work.
- DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 - the S337 owner decision refreshing the harness hook-parity fallback stance; the broader governance context for treating Claude/Codex gate divergence as a defect.

This thread is a sibling of the in-flight gtkb-bridge-compliance-gate-fenced-code-parser-fix (WI-3336, GO) and gtkb-bridge-compliance-gate-wi-auto-regex-fix (WI-3322, GO) reliability-fast-lane threads - three separate single-concern defects in the same hook. The owner's S356 AskUserQuestion answer selected "New sibling thread" rather than folding this fix into WI-3336.

## Owner Decisions / Input

- 2026-05-16 UTC, S356: the owner reported the `SPEC_TEST_HEADING_RE` missing-`re.MULTILINE` defect in `.claude/hooks/bridge-compliance-gate.py`, supplied the WI-3338 and WI-3339 bridge cycles as evidence of the live hard-block, and directed Prime Builder to route the fix through the GT-KB bridge protocol (proposal, Loyal Opposition GO, byte-identical scaffold-template change).
- 2026-05-16 UTC, S356: the owner answered an AskUserQuestion on fix routing - "How should the SPEC_TEST_HEADING_RE MULTILINE fix be routed through the bridge protocol?" - and selected "New sibling thread": file as a new reliability-fast-lane bridge thread under a fresh WI (WI-3351) in PROJECT-GTKB-RELIABILITY-FIXES, separate from the WI-3336 fenced-code-parser thread. This proposal executes that decision.
- No further owner decision is pending for the fix itself; implementation proceeds on Codex GO under the standing reliability-fast-lane authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already establishes bridge verdict files as canonical workflow state, ADR-CODEX-HOOK-PARITY-FALLBACK-001 already establishes the Claude/Codex hook-parity requirement, and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 already defines what a VERIFIED verdict must carry. The fix aligns the gate's regex mechanization with those existing requirements. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single-concern defect fix tracked by exactly one work item, WI-3351, an active member of PROJECT-GTKB-RELIABILITY-FIXES. No work-item state inventory, bulk transition, or backlog cleanup is performed, and no formal-artifact-approval packet is created. The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001) covers this fix through active project membership under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; that governance requires no per-fix formal-artifact-approval packet.

## Bridge INDEX Update Evidence

A NEW entry for `gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix` is inserted at the top of `bridge/INDEX.md`, below the header comments and above the first existing Document entry, by the gtkb-bridge-propose helper. No prior bridge file and no prior INDEX entry is deleted or rewritten; the append-only audit trail is preserved. GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL satisfied.

## Proposed Scope

### IP-1: Add re.MULTILINE to SPEC_TEST_HEADING_RE in the live hook

In `.claude/hooks/bridge-compliance-gate.py`, change the `SPEC_TEST_HEADING_RE` compile flags from `re.IGNORECASE` to `re.IGNORECASE | re.MULTILINE`. The regex pattern string is unchanged.

Before:

```python
SPEC_TEST_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:spec(?:ification)?[-\s]+to[-\s]+test|specification[-\s]+derived\s+verification)",
    re.IGNORECASE,
)
```

After:

```python
SPEC_TEST_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:spec(?:ification)?[-\s]+to[-\s]+test|specification[-\s]+derived\s+verification)",
    re.IGNORECASE | re.MULTILINE,
)
```

This is the one changed line: `re.IGNORECASE,` becomes `re.IGNORECASE | re.MULTILINE,`. `SPEC_TEST_HEADING_RE` is `^`-anchored and consumed via `.search(content)`; `re.MULTILINE` makes the `^` anchor match at every line start, so the mid-document spec-to-test heading is detected. No other regex and no other line changes; the sibling-regex audit above confirms `SPEC_TEST_HEADING_RE` is the only `^`-anchored `.search(content)` pattern lacking `re.MULTILINE`.

### IP-2: Identical fix in the scaffold template

Apply the byte-identical change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. The two files carry the byte-identical `SPEC_TEST_HEADING_RE` definition today and remain byte-identical after the fix, so adopter projects scaffolded from the template - and any `gt project upgrade --apply` re-copy - receive the corrected regex.

### IP-3: Regression test

Add `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`, parametrized over both hook copies (live + template), importing the hyphenated hook modules by path (the pattern already used by the existing `test_bridge_compliance_gate_*` modules in `platform_tests/hooks/`). Coverage:

- `_has_spec_derived_verification` returns `True` for a complete VERIFIED-first verdict (first line `VERIFIED`; a `## Specification Links` section with a real `GOV-`/`SPEC-` citation; a `## Spec-to-Test Mapping` heading and table; a `python -m pytest` command line) - the core regression; currently returns `False`.
- `_deny_reason_for_content` returns `None` for that same complete VERIFIED verdict - end-to-end confirmation the verdict is no longer hard-blocked; currently returns the spec-to-test hard-block message.
- `_has_spec_derived_verification` still returns `False` for a VERIFIED verdict that genuinely lacks any spec-to-test mapping heading (gate coverage preserved).
- `_has_spec_derived_verification` still returns `False` for a VERIFIED verdict that genuinely lacks executed-test command evidence (gate coverage preserved).
- `SPEC_TEST_HEADING_RE` carries the `re.MULTILINE` flag and `.search()` matches a `## Spec-to-Test Mapping` heading that is not the first line of the content (direct regex assertion).

### Out of scope

With `re.MULTILINE`, `SPEC_TEST_HEADING_RE.search(content)` will also match a `## Spec-to-Test Mapping`-shaped line that appears inside a fenced code block (for example, pasted tool output). This is a permissive residual: it can only ever cause `_has_spec_derived_verification` to return `True` when the other two conjuncts (concrete Specification Links and executed-test command evidence) are also satisfied, and it is consistent with the existing fence-blindness of `COMMAND_EVIDENCE_RE` (a bare `.search` with no fence-awareness). Full fenced-code awareness for heading detection is the separate concern of the in-flight gtkb-bridge-compliance-gate-fenced-code-parser-fix thread (WI-3336), which introduces a shared `_collect_section_lines` helper for the three section-collecting scanners; `_has_spec_derived_verification` does not collect a section (it only tests for a heading's presence) and is not in WI-3336's scope. Fence-aware spec-to-test heading detection, if later desired, is a follow-on once WI-3336's helper lands. No behavior change to any other gate check.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | A complete VERIFIED verdict is no longer hard-blocked by the gate | test_complete_verified_verdict_not_blocked |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | The VERIFIED verdict format Codex writes is accepted by the Claude-side gate | test_complete_verified_verdict_not_blocked |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `_has_spec_derived_verification` detects a present `## Spec-to-Test Mapping` heading | test_spec_derived_verification_detects_present_mapping |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | A VERIFIED verdict genuinely missing the spec-to-test mapping still fails | test_verified_verdict_missing_mapping_still_fails |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | A VERIFIED verdict genuinely missing command evidence still fails | test_verified_verdict_missing_command_evidence_still_fails |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | `SPEC_TEST_HEADING_RE` carries `re.MULTILINE` and matches a mid-document heading | test_spec_test_heading_re_multiline_flag |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Both hook copies carry the fix | all tests, parametrized over the live and template hooks |

Execution command:

`python -m pytest platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -v`

The post-implementation report will also re-run the existing bridge-compliance-gate tests (`test_bridge_compliance_gate_project_metadata.py`, `test_bridge_compliance_gate_wi_project_membership.py`, `test_bridge_compliance_gate_hard_block_workspace.py`, `test_bridge_compliance_gate_index_exemption.py`) to confirm no regression, and `ruff` over the changed files.

## Acceptance Criteria

- IP-1, IP-2, and IP-3 landed.
- A complete VERIFIED verdict (first line `VERIFIED`; concrete Specification Links; a `## Spec-to-Test Mapping` table; `python -m pytest` evidence) passes `_has_spec_derived_verification` and is not hard-blocked by `_deny_reason_for_content`.
- A VERIFIED verdict genuinely missing the spec-to-test mapping or the command evidence still fails the gate (coverage preserved).
- The live hook and the scaffold template copy remain byte-identical.
- The new test file passes; existing bridge-compliance-gate tests still pass; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Two implementation options were considered.

Option A (selected): add `re.MULTILINE` to the `SPEC_TEST_HEADING_RE` compile flags. Rationale: this is the minimal single-token correction that exactly matches the defect - a `^`-anchored pattern consumed via `.search(content)` without `re.MULTILINE`. It changes no pattern string, no call site, and no behavior other than the defect correction, which keeps the reliability-fast-lane fix single-concern and the diff trivially reviewable.

Option B (rejected): rewrite the `SPEC_TEST_HEADING_RE` call site in `_has_spec_derived_verification` as a per-line `.match()` scan, mirroring the idiom in `_has_concrete_spec_links` and `_has_clean_applicability_preflight`. Rejected because it is a larger diff (a new helper or an inline loop) for no behavioral gain over Option A - a per-line `.match()` scan is just as fence-blind as a `re.MULTILINE` `.search()`, so it does not address the in-fence residual either, and it expands the change surface beyond the single defect.

## Risks / Rollback

- Risk: `re.MULTILINE` makes `SPEC_TEST_HEADING_RE` match a heading-shaped line inside a fenced code block. Mitigation: documented under "Out of scope"; the residual is permissive only, gated behind two other required conjuncts, consistent with `COMMAND_EVIDENCE_RE`'s existing fence-blindness, and is the separate concern of WI-3336. It cannot cause a false-negative on a real verdict.
- Risk: the live hook and the template drift apart. Mitigation: IP-2 applies the identical edit to both; the post-implementation report confirms byte-identity.
- Risk: landing-order interaction with the in-flight WI-3336 thread. Mitigation: WI-3336 edits the three section-scanner function bodies and adds a helper; this proposal edits only the `SPEC_TEST_HEADING_RE` compile call. The edit regions do not overlap, so the two threads are textually conflict-free in either landing order. Implementation will read the then-current file state and apply the flag change to the `SPEC_TEST_HEADING_RE` definition.
- Rollback: revert the `re.MULTILINE` flag in both hook files and remove the IP-3 test. The change is a pure additive flag; rollback restores the prior behavior exactly.

## Recommended Commit Type

`fix` - repairs broken hook behavior (a false-positive hard-block on every Claude-authored VERIFIED verdict) with no new capability surface. The change is a single regex compile-flag addition in two files plus one regression test.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
