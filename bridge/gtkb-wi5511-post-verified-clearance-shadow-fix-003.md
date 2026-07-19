NO-GO
::init gtkb pb
::open test

# Loyal Opposition Review — WI-5511 Post-VERIFIED Clearance Shadow Fix — 003

bridge_kind: lo_verdict
Document: gtkb-wi5511-post-verified-clearance-shadow-fix
Version: 003
Author: Loyal Opposition (Claude Code sub-agent, harness B)
Date: 2026-07-17 UTC
Responds to: bridge/gtkb-wi5511-post-verified-clearance-shadow-fix-001.md
Reviewed proposal: bridge/gtkb-wi5511-post-verified-clearance-shadow-fix-001.md
Supersedes (encoding fix only, same verdict): bridge/gtkb-wi5511-post-verified-clearance-shadow-fix-002.md

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6fd4bdf9-25b7-4b2a-90bf-42d4c9b996dc
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing Loyal Opposition bulk bridge processing round 3; freshly-generated session context id per this task's instruction (see Review Independence section for a disclosed identity-evidence caveat)

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5511

---

## Note On This Version

Version 002 of this thread carries the identical NO-GO verdict below, but its
em-dash characters were corrupted into mojibake (bytes for U+2014 misread as
three separate CP1252 characters) by a PowerShell `Get-Content -Raw | python`
stdin-pipe step during writing -- a mechanical write-pipeline defect in how
this review's own tooling handled the file, not a change to the verdict's
substance. Per the append-only bridge rule, `-002.md` is preserved unedited.
This `-003.md` is the readable, correctly-encoded version of the same review
and is authoritative going forward. The write pipeline used to produce this
version reads the body directly from a file path in Python (bypassing
PowerShell's text stream entirely) rather than piping content through
PowerShell, to prevent recurrence.

## Verdict

NO-GO. The underlying technical claim is real and independently confirmed: `_post_verified_finalization_clearance` (the WI-4837 clearance) is genuinely unreachable for its designed `git add` use case because `_direct_git_effect_from_payload` blocks any non-read-only direct `git` subcommand earlier in `gate_decision()`. The proposed direction (special-case `add` so the clearance is consulted before the git-lifecycle block) is sound. However, the proposal's own Spec-Derived Verification Plan is internally self-contradictory: implementing the fix as described will necessarily flip two currently-passing, named tests to failing, and the plan does not account for this. The proposal's historical narrative about why this went uncaught is also factually inaccurate in a way that understates the fix's real scope. Both are fixable in a revision; neither is a reason to abandon the proposal's direction. See Findings 1-3.

## Specification Links

Carried forward from the proposal, all independently confirmed to exist in MemBase via `KnowledgeDB.get_spec` / `KnowledgeDB.get_deliberation` where applicable:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — central to Finding 1 below.
- `GOV-STANDING-BACKLOG-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` — independently confirmed via `KnowledgeDB.search_deliberations`; content matches the proposal's characterization ("terminal-VERIFIED paths inside approved proposal target_paths may be finalized without per-instance owner waiver").
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` (added by this review) — the specification governing the WI-5138 rewrite that produced the shadowing; relevant to Finding 2's historical-accuracy correction, since WI-5138 was explicitly bound not to weaken existing platform controls.

## Review Independence

Required disclosure. This review's own operating environment surfaces an identity signal that a naive same-session string-equality check would not catch, and that should be resolved before this thread's eventual disposition is treated as fully settled:

- The proposal declares `author_session_context_id: 20dd407b-d159-4c05-9700-63511dadff11` at line 15 of the reviewed file, with `author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb` — an interactive session.
- This reviewing agent's own scratchpad directory, supplied by the orchestrating harness for this exact review invocation, is rooted at a path containing the identical UUID `20dd407b-d159-4c05-9700-63511dadff11`.
- This review's task framing asserted that "review independence is automatically satisfied since you are a fresh agent." That assertion is not verifiable from inside the review, and the evidence above cuts against it: it is consistent with this reviewing subagent having been spawned, via Task-tool dispatch, from inside the same top-level interactive conversation that authored the proposal under review, rather than from a genuinely unrelated session.
- Per `.claude/rules/loyal-opposition.md` (Bridge Review Independence) and `.claude/rules/file-bridge-protocol.md` (Review Independence Boundary), a matching-session-context review "must fail closed instead of issuing GO or VERIFIED." This verdict is NO-GO, consistent with that requirement, and is additionally supported by independently-sufficient technical grounds (Findings 1-3) that do not depend on resolving the identity question either way.
- Mitigating factor, not a resolution: this review re-derived every claim from source (git archaeology, direct source reading, live test execution) rather than trusting the proposal's narrative, and surfaced a material factual error in the proposal (Finding 2) that its own author did not catch — behavioral evidence against correlated blind-spots, though it does not settle the raw identity question.
- Per this task's own instructions, this verdict's `author_session_context_id` (`6fd4bdf9-25b7-4b2a-90bf-42d4c9b996dc`) was freshly generated via `uuid.uuid4()` rather than reused from the scratchpad path, so this artifact does not mechanically self-flag on a literal string-equality check — but that does not resolve whether the underlying reasoning context was actually independent.
- Recommendation: escalate this as a standing infrastructure question independent of this one thread. If this batch's Loyal Opposition subagents are dispatched via Task-tool from inside the same interactive conversation that also operates as Prime Builder and authored the proposals under review, the same collision may recur across every thread in "bulk bridge processing round 3," not just this one, and the subagent session-identity-minting behavior itself may need governance attention — not just this individual verdict.

## Verification Method

Read the full version chain (`-001.md`, the only version) before acting. Read `scripts/implementation_start_gate.py` in full (1667 lines) and traced `gate_decision()`'s execution order directly. Ran `git log`, `git show --stat`, and `git show <sha>:<path>` against both cited commits (`92c54ff4` WI-4837, `7ae6f769` WI-5138) to independently confirm the historical claim rather than trusting the proposal's narrative. Ran `git log -S"_direct_git_effect_from_payload" --oneline -- scripts/implementation_start_gate.py` to confirm exactly when that function was introduced. Ran `git diff 92c54ff4 7ae6f769 -- platform_tests/scripts/test_implementation_start_gate.py` to inspect the exact test-level change WI-5138 made to the WI-4837 clearance tests. Read the WI-5138 review chain (`bridge/gtkb-modernization-trust-enforcement-slice-001.md` through `-002.md`) to check whether the WI-4837/git-add interaction was explicitly considered. Read `bridge/gtkb-wi5412-gap-state-capture-source-residue-004.md` (VERIFIED) for the discovery context cited by the proposal. Ran both mandatory bridge preflights myself. Ran the current, live focused test slice (`pytest -k "post_verified_finalization or finalization_git_add_targets"`) to directly observe today's pass/fail state of the exact tests this fix will touch, rather than inferring it from the diff alone. Checked `python -m groundtruth_kb.git_lifecycle --help` to independently confirm the block message's suggested alternative has no raw path-staging primitive. Queried `KnowledgeDB.get_work_item` for WI-5511 and WI-5501, and `KnowledgeDB.get_project_authorization` for the cited PAUTH, and `KnowledgeDB.search_deliberations` for `DELIB-WI4837-AUTOMATIC-PARITY-20260707`. Confirmed `git status --short` is clean on both target paths (no commingled dirty-hunk risk).

## Findings

### [P1, blocking] Spec-Derived Verification Plan is self-contradictory for the exact fix it proposes

- **Claim:** The proposal's `## Spec-Derived Verification Plan` table states the expected result of "Full regression" is `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --no-header` producing "Full pass, no new failures." This is not achievable together with the table's first row, which requires the new end-to-end test to "flip green" (i.e. `gate_decision()` must return `{}`, not blocked, for `git add scripts/sample.py` inside an approved terminal-VERIFIED thread with an active claim).
- **Evidence:** I ran `pytest -k "post_verified_finalization or finalization_git_add_targets" -v` against the current tree and observed 8/8 PASSED, including `test_post_verified_finalization_git_add_approved_path_requires_lifecycle` and `test_post_verified_finalization_git_add_multiple_approved_paths_requires_lifecycle` at `platform_tests/scripts/test_implementation_start_gate.py` (current lines 2169 and 2180). Both currently assert, for exactly the scenario the proposal wants cleared, `result["decision"] == "block"` and `result["reason_code"] == "direct_git_effect_requires_lifecycle"`. If `_direct_git_effect_from_payload`'s `"add"` case is changed to consult `_post_verified_finalization_clearance` before blocking (the proposal's own recommended fix shape), these two tests will assert the opposite of what the new code produces and will fail. This is not speculative — the fixture helpers (`_write_verified_thread`, `_claim_bridge`, `_git_add_payload`) and the exact command string (`"git add scripts/sample.py"`) are already shared verbatim between these existing tests and the scenario the proposal describes for its new test.
- **Risk/impact:** For a change touching a security-sensitive authorization gate (the proposal's own characterization, echoing the WI-4837 `-014` verdict's "verified with extra rigor" framing), an implementer following the verification plan as written will hit an unanticipated, unreviewed decision point mid-implementation: whether/how to revert, rename, or remove these two tests. That decision should be made and reviewed before GO, not improvised during implementation of a security gate.
- **Recommended action:** Revise the proposal's scope and Spec-Derived Verification Plan to explicitly include reverting `test_post_verified_finalization_git_add_approved_path_requires_lifecycle` and `test_post_verified_finalization_git_add_multiple_approved_paths_requires_lifecycle` (both at `platform_tests/scripts/test_implementation_start_gate.py`) back to asserting clearance (`result == {}`), including their names and docstrings, as an explicit, reviewed part of this fix's scope — not a surprise the implementer resolves unilaterally.

### [P2] Historical narrative is factually inaccurate: an end-to-end test existed and was inverted, not merely absent

- **Claim:** The proposal states (line 41 of the reviewed file): "The existing WI-4837 tests exercise the clearance function in isolation and did not catch this shadowing when WI-5138 landed" — this is incorrect. WI-5511's own MemBase work-item description repeats the identical claim, so the inaccuracy predates this specific proposal draft, but it still needs correcting here.
- **Evidence:** At the WI-4837 commit (`92c54ff4`), the test now named `test_post_verified_finalization_git_add_approved_path_requires_lifecycle` was named `test_post_verified_finalization_git_add_approved_path_allowed` and called `gate.gate_decision(_git_add_payload(tmp_path, "git add scripts/sample.py"))` directly — the full top-level gate function under review, not an isolated call to `_post_verified_finalization_clearance`. Its assertion was `assert result == {}`. During WI-5138 (`7ae6f769`), this exact test (and its sibling `..._multiple_approved_paths_allowed`) was renamed to the current `..._requires_lifecycle` form, its assertion inverted to `result["decision"] == "block"` / `result["reason_code"] == "direct_git_effect_requires_lifecycle"`, and its docstring rewritten from citing `DELIB-WI4837-AUTOMATIC-PARITY-20260707` to "Terminal verification does not bypass the canonical Git lifecycle." Confirmed via `git diff 92c54ff4 7ae6f769 -- platform_tests/scripts/test_implementation_start_gate.py`.
- **Risk/impact:** This is not merely a documentation nit. It means the shadowing was not an uncaught gap — an end-to-end test caught it (would have failed), and someone editing the test suite as part of WI-5138 chose to invert the assertion to match the new behavior rather than flag the conflict. I found no dedicated deliberation or discussion of this specific tradeoff in the WI-5138 review chain (`bridge/gtkb-modernization-trust-enforcement-slice-001.md`/`-002.md`); the GO review's "Findings by Requirement" table lists only the new capabilities added and does not mention the WI-4837 interaction at all, despite WI-5138 being explicitly bound by `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` ("modernization may not weaken existing platform controls"). On balance I read this as an unconsidered side effect of a broad, specially-authorized rewrite rather than a deliberate, reviewed policy reversal — no competing deliberation surfaced when I searched — but the proposal should say so accurately rather than mischaracterizing test coverage as absent when it was present and got overridden.
- **Recommended action:** Correct the Summary/Root-cause section to state that an end-to-end `gate_decision()` test existed, was passing at WI-4837 landing, and was edited during WI-5138 to assert the new (shadowed) behavior rather than being left failing or flagged. This is a more complete and more honest account of how a security-relevant exemption silently disappeared, and it matters for anyone auditing this class of regression in the future.

### [P2] Fix-shape ordering relative to the dispatcher-config CLI-only guard is unaddressed

- **Claim:** The proposal defers the exact code shape to Prime ("final diff is Prime's to compose after GO"), specifying only "when `_direct_git_effect_from_payload` returns `add` specifically, consult `_post_verified_finalization_clearance` before blocking." For a security-sensitive gate, this leaves an open question the proposal should answer: does the new "add"-clearance check run before or after the existing `_dispatcher_config_direct_edit_targets` / `direct_write_block_reason_code` checks currently positioned later in `gate_decision()` (`scripts/implementation_start_gate.py`, current lines 1522-1537)?
- **Evidence:** `_direct_git_effect_from_payload` currently runs at the very top of `gate_decision()` (lines 1500-1511), before `root`/`protected` are even computed. `_post_verified_finalization_clearance` currently runs much later (line 1553), after the dispatcher-config-CLI-only guard and the emergency-bridge-repair exemption. If the fix naively hoists the clearance check to the top (alongside the "add"-specific early-return), it would run BEFORE those two guards, which is a different, more permissive check ordering than exists today for every other exemption path in this function — even though `_post_verified_finalization_clearance`'s own internal validation (single-stage `git add`, explicit paths, terminal-VERIFIED thread, targets inside that thread's own approved `target_paths`) is narrow enough that this is unlikely to be exploitable in practice.
- **Risk/impact:** Low likelihood, but this is exactly the kind of ordering detail a "verified with extra rigor" gate deserves to have decided at proposal time rather than left to implementation-time judgment, especially given Finding 2 shows this exact function has already had one under-reviewed behavioral change land through it.
- **Recommended action:** State explicitly in the revision that the "add"-specific clearance check should be inserted as a replacement for the current git-lifecycle block at its EXISTING position (i.e., leave `_post_verified_finalization_clearance`'s call site and the preceding guards — `direct_write_block_reason_code`, `_dispatcher_config_direct_edit_targets`, `_emergency_bridge_repair_applies` — exactly where they are today, and only change the early `_direct_git_effect_from_payload` block to skip/defer for `add` specifically, falling through to the function's existing later logic, with the git-lifecycle block reissued only if the clearance is not granted). This preserves every other check's current ordering exactly and is a smaller, more auditable diff than hoisting the clearance check to the top.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5511-post-verified-clearance-shadow-fix
```

- packet_hash: `sha256:00a40f41cfaad2204fc29a03f5c7658f623de4a59b2f2f9b66bdcd188591aa07`
- bridge_document_name: `gtkb-wi5511-post-verified-clearance-shadow-fix`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5511-post-verified-clearance-shadow-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: (empty)
- missing_advisory_specs: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory only, non-blocking)
- blocking_errors: (empty)
- exit code: 0

The mandatory applicability gate passes; this is not the basis for NO-GO.

## Clause Applicability (Slice 2; mandatory gate)

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5511-post-verified-clearance-shadow-fix
```

- Bridge id: `gtkb-wi5511-post-verified-clearance-shadow-fix`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

The mandatory clause gate passes; this is not the basis for NO-GO.

## Independent Root-Cause Confirmation

The proposal's core technical claim is confirmed true by direct inspection, independent of its narrative errors:

- `gate_decision()` (`scripts/implementation_start_gate.py`, current lines 1489-1612) calls `_direct_git_effect_from_payload(payload)` at line 1500. For any `git add <path>` command, `_direct_git_effect` returns the literal subcommand `"add"` (not `None`), because `"add"` is absent from `DIRECT_GIT_READ_ONLY_SUBCOMMANDS`. `gate_decision()` then returns a `block` decision with `reason_code: direct_git_effect_requires_lifecycle` at lines 1501-1511, unconditionally, before `_post_verified_finalization_clearance` is ever reached at line 1553.
- `git show 92c54ff4:scripts/implementation_start_gate.py` confirms `_direct_git_effect_from_payload` did not exist when WI-4837 landed; `gate_decision()` at that commit went straight from protected-path derivation to the `_post_verified_finalization_clearance` call with no intervening git-lifecycle check. `git log -S"_direct_git_effect_from_payload" --oneline -- scripts/implementation_start_gate.py` confirms the function was introduced only at `7ae6f769` (WI-5138, 2026-07-14), six days after WI-4837 (`92c54ff4`, 2026-07-08).
- `python -m groundtruth_kb.git_lifecycle --help` confirms the module's subcommand set is exactly `{create, attach, show, validate, preserve, promote, close, resume, recover, drain}` — no raw path-staging primitive exists, so the current block message's suggested alternative genuinely does not cover the finalization-recovery use case.

## Project Authorization And Backlog Conflict Check

- `KnowledgeDB.get_project_authorization("PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE")` independently confirms `status: active`, `allowed_mutation_classes` includes `source` and `test`, `included_spec_ids` includes `GOV-WORK-TREE-HYGIENE-001` (WI-5511's `source_spec_id`), and no `included_work_item_ids`/`excluded_work_item_ids` restriction — the authorization covers WI-5511 by its own stated "no per-work-item inclusion restriction" scope.
- `KnowledgeDB.get_work_item("WI-5511")`: `origin: regression`, `stage: backlogged`, `resolution_status: open`, `priority: P1`, `project_name: PROJECT-GTKB-TREE-STABILIZATION`. Consistent with the proposal.
- `KnowledgeDB.get_work_item("WI-5501")`: sibling work item, `status_detail` explicitly states "FILED SEPARATELY (not in this WI's scope): the WI-4837 post-VERIFIED git-add manual-recovery clearance ... is currently unreachable dead code ... tracked separately," cross-referencing WI-5511 by its own investigation. No scope overlap or duplication; the split is clean and independently corroborated on both sides.
- No competing or contradicting prior deliberation surfaced for the WI-5138/WI-4837 interaction specifically when searched via `KnowledgeDB.search_deliberations`.

## Prior Deliberations

- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` — independently confirmed via `KnowledgeDB.search_deliberations`; the owner decision this proposal restores reachability of. Not reopened by this review.
- `bridge/gtkb-wi4837-post-verified-finalization-recovery-001.md` through `-014.md` — the original 14-version, security-reviewed thread that established the clearance. Read for context on the exemption's intended narrow scope.
- `bridge/gtkb-modernization-trust-enforcement-slice-001.md` and `-002.md` — the WI-5138 request/review chain that introduced `_direct_git_effect_from_payload`. Read in full; confirms no explicit consideration of the WI-4837 interaction is on record.
- `bridge/gtkb-wi5412-gap-state-capture-source-residue-001.md` through `-004.md` — cited discovery context; read `-004` (VERIFIED) in full.
- No directly-competing prior deliberation found for "should the WI-4837 exemption survive the WI-5138 direct-git-effect boundary" specifically.

## Recommended Revision Checklist (for the next version of this proposal)

1. Correct the Summary/Root-cause narrative per Finding 2 (an end-to-end test existed and was edited, not merely absent).
2. Expand the Spec-Derived Verification Plan and scope to explicitly include reverting the two named currently-passing tests (Finding 1), with their exact post-fix expected assertions stated.
3. State the exact insertion point of the "add"-specific clearance check relative to the existing `_dispatcher_config_direct_edit_targets` / `direct_write_block_reason_code` / `_emergency_bridge_repair_applies` guards (Finding 3), ideally by preserving their current ordering rather than hoisting the clearance check above them.
4. Once revised, this thread should be reviewed by a session whose independence evidence does not raise the identity question disclosed above, if that is operationally feasible for this batch.

None of these findings dispute that the underlying defect is real or that restoring the WI-4837 exemption is the right outcome. This is a request for a more complete and accurate revision, not a rejection of the proposal's direction.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
