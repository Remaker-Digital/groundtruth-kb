REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s367-work-intent-integration-revised-11
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Revised Implementation Proposal - Bridge Work-Intent Registry Integration (PAUTH Swap to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY v3)

bridge_kind: implementation_proposal
Document: gtkb-work-intent-registry-prime-write-integration
Version: 011 (REVISED; addresses NO-GO -010 finding P1-001)
Responds to NO-GO: bridge/gtkb-work-intent-registry-prime-write-integration-010.md
Supersedes: bridge/gtkb-work-intent-registry-prime-write-integration-009.md
Implements: WI-3414
Work Item: WI-3414
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
target_paths: ["scripts/bridge_claim_cli.py", ".claude/rules/file-bridge-protocol.md", "scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "groundtruth-kb/tests/test_bridge_propose_helper.py", ".groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json"]
Recommended commit type: feat:
Date: 2026-05-28 UTC

## Revision Summary

REVISED-11 addresses the P1-001 finding from Codex `-010` NO-GO: the prior PAUTH citation (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) was scope-incompatible with the proposal because `GOV-RELIABILITY-FAST-LANE-001` restricts fast-lane work to ~3 source files / ~150 LoC with no new public API/CLI/behavior. This proposal adds a new CLI surface, a new mandatory bridge-protocol rule section, modifies multiple hook/helper/template surfaces, and adds 6 test files. That is bridge-protocol feature work, not a reliability fix.

The fix is structural: swap the cited PAUTH to `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH` (v3, amended in S367 to add WI-3414 and three mutation classes). The new PAUTH's `scope_summary` is "Bridge poller, trigger, index hygiene + reliability WIs spanning poller refactor, role-intent sentinel, helper parity, citation freshness, INDEX edit race coordination, work-intent registry consumption integration" — a direct scope match for the work-intent thread. The sibling quiesce-window thread (`bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md`) was already in the PAUTH's covered WI set; WI-3414 has now been added per the S367 owner-approved amendment.

Changes in REVISED-11 (precisely scoped to the -010 P1-001 finding):

1. **Project**: changed from `PROJECT-GTKB-RELIABILITY-FIXES` to `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.
2. **Project Authorization**: changed from `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` to `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH` (v3).
3. **Owner Decisions / Input**: added S367 AUQ #3 (path selection: amend existing PAUTH) and S367 AUQ #4 (PAUTH v3 amendment approval); added pointer to DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT and the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` (sha256: `78eb437e7be32e291ddf32ebfb387c0fb1f07838879865ad0f276203bec192dc`).
4. **Authorization Partition**: updated to cite PAUTH v3's full mutation-class set `[hook_upgrade, cli_extension, test_addition, spec_status_promotion, source, rules, governance_evidence]` and partition the 15 `target_paths` by class.
5. **Acceptance Criteria**: updated the implementation-coverage criterion to cite PAUTH v3 and the explicit mutation-class coverage.
6. **Spec-to-Test Mapping**: updated `GOV-STANDING-BACKLOG-001` row to reference PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY membership; updated `GOV-RELIABILITY-FAST-LANE-001` row to acknowledge the slice is NOT a fast-lane slice (no longer applicable).
7. **Loyal Opposition Asks**: updated partition-confirmation ask (LO Ask #3) to reference the new PAUTH v3; removed prior LO Ask #5 about the PAUTH-mutation-class question (no longer applicable since v3 explicitly enumerates `source`, `rules`, `governance_evidence`).
8. **Prior Deliberations**: added entries for `-010` NO-GO, DELIB-S367 (PAUTH amendment), and the formal-artifact-approval packet.
9. **Risks**: removed prior Risk #9 about PAUTH-mutation-class coverage (resolved by v3 explicit enumeration); other risks unchanged.
10. **Specification Links**: replaced `GOV-RELIABILITY-FAST-LANE-001` reference with a note that this slice is bridge-protocol feature work governed by the BRIDGE-PROTOCOL-RELIABILITY PAUTH, not reliability-fast-lane work.

All other -009 content (Honest Closure Statement, IP-0 through IP-4, IP-0b Steps 1-3, Spec-to-Test Mapping rows other than the two updated, Risks 1-8, Rollback) is carried forward unchanged. The substantive scope (six surfaces + packet workflow + 15-path target set) is unchanged from -009.

## Honest Closure Statement

This proposal does NOT mechanically prevent an agent from drafting before claiming. There is no observable "Prime is about to draft" event in Claude Code; drafting is internal reasoning, invisible to hooks. What this proposal DOES is:

1. Make the claim action **deterministic and observable** (the `gt bridge claim` CLI writes a holder record that is auditable evidence of intent).
2. Make the claim action **required by rule** (file-bridge-protocol.md update; the bridge-compliance-gate hook enforces claim-before-Write).
3. Make claim state **visible to all parties** (AXIS-2 surface for interactive Prime; `current_holder` for trigger; helper's `acquire` call).
4. Make rule violation **mechanically catchable** at Write time (hook blocks the file Write if no prior claim exists for this session).

With these four properties, a Prime that follows the rule discipline burns no duplicate drafting tokens. A Prime that violates the rule produces an audit-trail artifact (Write blocked by hook citing "no prior claim") that motivates the next round of process improvement.

This is honest about where the closure is mechanical (Write boundary) vs where it relies on rule discipline (pre-drafting). Defense in depth at multiple boundaries reduces the violation surface; the audit trail makes violations visible.

## Implementation Plan

### Integration Point 0 (carried from -005, unchanged) - Deterministic Claim CLI (`scripts/bridge_claim_cli.py`)

New script providing the canonical pre-drafting boundary:

```text
python scripts/bridge_claim_cli.py claim <slug>        # acquires; prints holder record on success, holder info on failure
python scripts/bridge_claim_cli.py release <slug>      # releases if held by this session
python scripts/bridge_claim_cli.py status [<slug>]     # shows current holder(s)
```

The CLI reads `session_id` from `CLAUDE_SESSION_ID` env var (Claude Code provides this) or from `--session-id` flag. It wraps `bridge_work_intent_registry.acquire` / `release` / `current_holder` with TTL default of 600 seconds (10 min, sufficient for typical drafting + helper invocation).

Exit codes:
- 0: claim successful (acquired or renewed by same session)
- 2: claim refused (held by another session); stdout includes holder record JSON
- 3: invalid slug or other error

This is the canonical interactive pre-drafting boundary. Prime invokes this AFTER seeing AXIS-2 surface and BEFORE drafting body.

### Integration Point 0b (carried from -007/-009, unchanged) - Rule File Update with Formal-Artifact-Approval Packet (`.claude/rules/file-bridge-protocol.md`)

The rule-file update is a protected narrative-artifact mutation. It requires two coupled actions: the content edit and the formal-artifact-approval packet that authorizes it. The hook-and-pre-commit enforcement layers will block the Write and the commit respectively if the packet is missing or its sha256 does not match the staged blob.

**Step 1: Generate the narrative-artifact approval packet with owner AUQ.**

Before any Write of `.claude/rules/file-bridge-protocol.md`:

1. Prime drafts the proposed full file content with the new "Mandatory Pre-Drafting Claim Step" section inserted (content per Step 2).
2. Prime computes the planned-content sha256 via `hashlib.sha256(full_content.encode('utf-8')).hexdigest()`.
3. Prime presents the proposed rule-section text (the new section verbatim) to the owner via AskUserQuestion. AUQ option labels are "Approve as-shown", "Approve with edits I will describe", "Reject".
4. On "Approve as-shown", Prime writes the packet to `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` with the fields below.
5. On "Approve with edits", Prime applies edits, recomputes the sha256, re-presents if substantive, then writes the packet.
6. On "Reject", Prime files a follow-on REVISED narrowing scope or escalates.

Packet fields per `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields` (13 fields): `artifact_type=narrative_artifact`, `artifact_id=claude-rules-file-bridge-protocol-md`, `action=update`, `target_path=.claude/rules/file-bridge-protocol.md`, `source_ref=bridge/gtkb-work-intent-registry-prime-write-integration-011` (or current GO'd version), `full_content` (full proposed file text), `full_content_sha256` (sha256 of full_content), `approval_mode=approve`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` (verbatim owner AUQ answer), `changed_by=prime-builder/claude`, `change_reason=WI-3414 work-intent registry Prime-write integration; add Mandatory Pre-Drafting Claim Step section`.

**Step 2: Add the rule section.**

Add a new mandatory section titled "Mandatory Pre-Drafting Claim Step" to `.claude/rules/file-bridge-protocol.md`:

```markdown
## Mandatory Pre-Drafting Claim Step

Before substantive drafting begins on any bridge thread (NEW, REVISED, or post-impl report), Prime MUST acquire a work-intent claim via:

    python scripts/bridge_claim_cli.py claim <slug>

The claim establishes a holder record at `.gtkb-state/work-intent/<slug>.json` that other Prime sessions (interactive or auto-dispatched) consult before drafting. A claim is required even when no other session is currently working the thread; the claim is the audit-trail evidence that THIS session committed to the work.

Claim exit code 0 authorizes drafting. Exit code 2 (held by another session) requires Prime to either select a different thread or, if the holder appears stale, surface the situation via AskUserQuestion before forcing through.

The bridge-compliance-gate PreToolUse hook ENFORCES this rule at file-Write time: a Write to `bridge/<slug>-NNN.md` without a prior claim by this session is blocked with a clear error citing this rule.

Claim release happens automatically when the helper completes a successful Write, or via TTL expiry (10 minutes default), or via explicit `release` for abandoned work.
```

**Step 3: Verify packet + content match at Write time and pre-commit time.**

Two enforcement layers verify the packet:

- `.claude/hooks/narrative-artifact-approval-gate.py` (Claude PreToolUse Write|Edit) reads the packet via env var `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` or `GTKB_FORMAL_APPROVAL_PACKET` and matches sha256 against the proposed content. Blocks Write on mismatch.
- `.githooks/pre-commit` runs `scripts/check_narrative_artifact_evidence.py --staged` which hard-blocks the commit if the staged blob's sha256 does not match any packet's `full_content_sha256` for the protected path.

Both layers share `config/governance/narrative-artifact-approval.toml` as the protected-pattern registry.

### Integration Point 1 (carried from -005, unchanged) - Trigger Pre-Spawn Acquire WITH Batch Semantics

Before spawning a Prime worker:

1. Read `_selected_oldest_first` (currently returns up to `DEFAULT_MAX_ITEMS = 2` candidate items).
2. **Filter held entries**: for each candidate, call `current_holder(slug)`. Drop entries where `current_holder` is non-None and from a different session.
3. **Compute signature only on the filtered unheld batch**. If filtered batch is empty, skip spawn entirely without consuming `last_dispatched_signature`.
4. **Atomic acquire**: for each entry in the filtered batch, call `acquire(slug, f"trigger-dispatched-{spawn_id}", ttl_seconds=120)`. If ANY acquire fails (race between filter and acquire), release any holders this trigger already acquired in THIS attempt and skip spawn.
5. **Spawn** with the filtered batch. The spawned worker receives `GTKB_INHERITED_SESSION_ID = f"trigger-dispatched-{spawn_id}"` and renews on boot.
6. **Update `last_dispatched_signature` ONLY for the actually-spawned batch signature**. Held-filtered entries do NOT consume budget.

The held-filtered entries are logged to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with reason `work_intent_already_held`.

### Integration Point 2 (carried from -005, unchanged) - AXIS-2 Surface Registry Consult + Claim Prompt

When rendering the actionable-work table for an interactive Prime session:

1. For each actionable entry, call `current_holder(slug)`.
2. If a non-expired holder exists with a DIFFERENT `session_id` from this interactive session: annotate the row as `ALREADY CLAIMED by <holder.session_id> until <holder.ttl_expires_at>` and hide from actionable count.
3. If no holder exists OR holder matches this session: render normally and append footer line `To work an unclaimed thread, first run: python scripts/bridge_claim_cli.py claim <slug>`.

The hook does NOT acquire on render. Acquisition is Prime's explicit deterministic action via the CLI.

### Integration Point 3 (carried from -005, unchanged) - Helper Acquire/Release (Installed + Template)

Before draft body construction in `.claude/skills/bridge-propose/helpers/write_bridge.py` AND the template at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`:

1. Extract thread slug; read `session_id` from env.
2. Call `current_holder(slug)`. If a different session holds it, exit with clear error citing the holder.
3. If no holder OR same-session holder, call `acquire(slug, session_id, ttl_seconds=300)` to renew the claim during helper processing.
4. Proceed with helper logic.
5. Call `release(slug, session_id)` on successful Write.

The helper does NOT REPLACE the explicit pre-drafting claim CLI; it acts as a renewal point and final safety net.

### Integration Point 4 (carried from -005, unchanged) - PreToolUse Write Hook (Installed + Template)

In `.claude/hooks/bridge-compliance-gate.py` AND template at `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`:

When a Write or Edit tool call targets `^bridge/(?P<slug>[a-z0-9][a-z0-9-]+)-\d{3,}\.md$`:

1. Extract slug.
2. Read `session_id` from hook payload.
3. Call `current_holder(slug)`.
4. If holder exists with DIFFERENT session_id: emit `{"decision": "block", "reason": "Bridge file Write blocked: thread '<slug>' is claimed by <holder.session_id>. Acquire claim first: python scripts/bridge_claim_cli.py claim <slug>"}`.
5. If NO holder at all: emit `{"decision": "block", "reason": "Bridge file Write blocked: no prior claim for thread '<slug>'. Per .claude/rules/file-bridge-protocol.md 'Mandatory Pre-Drafting Claim Step', run: python scripts/bridge_claim_cli.py claim <slug>"}`.
6. If holder matches this session: allow Write.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the integration adds claim-before-draft as a bridge-protocol-level coordination requirement. The CLI is a new deterministic surface; the rule file update makes it required. `bridge/INDEX.md` remains canonical workflow state; the INDEX update for this REVISED-11 inserts a new `REVISED:` line at the top of the existing thread entry, preserving the append-only version chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED carries applicable governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping maps each integration point to focused tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched files reside under `E:\GT-KB`. State directory `.gtkb-state/work-intent/` is in-root. The packet directory `.groundtruth/formal-artifact-approvals/` is in-root.
- `GOV-STANDING-BACKLOG-001` - WI-3414 active member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` (per PAUTH v3 amendment S367).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the claim CLI invocation becomes a deterministic artifact (holder record) replacing implicit reasoning. The approval packet is a deterministic artifact replacing implicit owner-authorization signaling.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the claim CLI is a textbook example of converting implicit reasoning into a deterministic service. The approval packet is a textbook example of converting implicit governance into an explicit artifact.
- `GOV-ARTIFACT-APPROVAL-001` - the rule-file mutation requires a formal-artifact-approval packet because `.claude/rules/file-bridge-protocol.md` is a protected narrative artifact per `config/governance/narrative-artifact-approval.toml`. The new PAUTH v3 includes a `governance_evidence` mutation class explicitly covering the approval-packet JSON artifact.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the hook + pre-commit enforcement layer is the mechanism by which `GOV-ARTIFACT-APPROVAL-001` is operationalized.
- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` (NEW in -011) - governs the PAUTH v3 amendment. The owner-approved formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` satisfies this constraint and is cited by path in the PAUTH v3 `change_reason`.

Note on `GOV-RELIABILITY-FAST-LANE-001`: this proposal is NO LONGER governed by the reliability-fast-lane spec, because the cited PAUTH is `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH` (not `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`). The new PAUTH's scope is bridge-protocol reliability feature work, not reliability-fast-lane defect fixes.

## Prior Deliberations

- `bridge/gtkb-work-intent-registry-prime-write-integration-010.md` (Codex NO-GO on `-009`, 2026-05-28). P1-001: reliability fast-lane PAUTH is over-applied; proposal scope is bridge-protocol feature work, not fast-lane work. This REVISED-11 addresses by swapping the cited PAUTH to the properly-scoped bridge-protocol-reliability batch (amended v3 per owner AUQ S367 to add WI-3414 + 3 mutation classes).
- `bridge/gtkb-work-intent-registry-prime-write-integration-009.md` (REVISED-9 superseded). Added approval-packet artifact path to target_paths; REVISED-11 carries forward target_paths unchanged.
- `bridge/gtkb-work-intent-registry-prime-write-integration-008.md` (Codex NO-GO on `-007`). P1-001: approval-packet path missing; addressed by -009.
- `bridge/gtkb-work-intent-registry-prime-write-integration-007.md` (REVISED-7 superseded). Added GOV-ARTIFACT-APPROVAL-001 + DCL-ARTIFACT-APPROVAL-HOOK-001 citations and packet workflow.
- `bridge/gtkb-work-intent-registry-prime-write-integration-006.md` (Codex NO-GO on `-005`). P1-001: protected rule-file mutation lacks formal artifact approval linkage; addressed by -007.
- `bridge/gtkb-work-intent-registry-prime-write-integration-005.md` (REVISED-5 superseded). Explicit claim CLI + batch semantics + honest closure framing.
- `bridge/gtkb-work-intent-registry-prime-write-integration-004.md` (Codex NO-GO on `-003`). P1-001 escalated; P2-001 added batch semantics requirement.
- `bridge/gtkb-work-intent-registry-prime-write-integration-003.md`, `-002.md`, `-001.md` (earlier rounds).
- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` (S367 owner-decision deliberation) - captures the S367 AUQ chain that authorized the PAUTH v3 amendment (path selection + per-artifact approval). MemBase row inserted before PAUTH v3 insert.
- `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` (PAUTH v3 amendment approval packet; sha256 `78eb437e7be32e291ddf32ebfb387c0fb1f07838879865ad0f276203bec192dc`) - cited by path in the PAUTH v3 `change_reason` and validates the amendment against `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`.
- `bridge/gtkb-bridge-parallel-session-collision-006.md` (VERIFIED; registry-foundation thread; historical context only).
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` (VERIFIED; sibling quiesce-window thread; already included in the new PAUTH's covered work-item set).
- `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` (GO) - the extension that brought `.claude/rules/*.md` under the protected-narrative-artifact gate.
- `bridge/active-workspace-declaration-slice-1-003.md:90` - precedent cited by Codex `-008` for including approval-packet path in `target_paths`.
- `bridge/gtkb-work-list-md-gov-010-path-correction-002.md:77` - precedent cited by Codex `-008` for narrow-glob packet-path coverage.
- `DELIB-2379`, `DELIB-2380`, `DELIB-2411` - cited by Codex `-008` Prior Deliberations.
- `DELIB-2217`, `DELIB-2348`-`2351`, `DELIB-2452`, `DELIB-2410`, `DELIB-2409`, `DELIB-2405`, `DELIB-2404` (cited by Codex `-010` Prior Deliberations).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directly applicable.
- `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` (S352 amendment precedent for PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BATCH v1->v2; pattern reused for the S367 v2->v3 amendment).

## Requirement Sufficiency

Existing requirements sufficient. The deferred-integration risk language in the registry-foundation thread (VERIFIED) authorizes the integration class. The claim CLI is a natural deterministic-services-principle addition. The protected-narrative-artifact packet workflow is fully specified in `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` and operationalized by the GO'd `gtkb-narrative-artifact-approval-extension-001-004` thread. The PAUTH v3 amendment is governed by `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` and satisfied by the owner-approved formal-artifact-approval packet. No new specifications required.

## Owner Decisions / Input

- AUQ S365 #1: "Unstick a multi-round NO-GO".
- AUQ S365 #3: "Investigate the AXIS-1 race pattern".
- AUQ S365 #4: "A + B + C - full integration".
- AUQ S366 #1: "REVISE with broader acquisition surface" (drove `-003`).
- AUQ S366 #2: "REVISE-5 with explicit claim CLI" (drove `-005`).
- AUQ S367 #1: "File -007 REVISED (address -006 P1 narrowly)".
- AUQ S367 #2: "File -009 REVISED (one-line target_paths fix)".
- AUQ S367 #3 (this turn): "Authorize a new project + PAUTH covering bridge-protocol feature work (Codex Path 2)" - owner directive after the 5th NO-GO at -010 to use a fit PAUTH instead of the standing reliability-fast-lane PAUTH.
- AUQ S367 #4 (this turn): "Amend the existing PAUTH (v2 -> v3): add WI-3414 + 3 mutation classes (Recommended)" - owner directive to amend the existing PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY PAUTH rather than create a new project + PAUTH. The amendment uses the existing PAUTH whose scope_summary already covers bridge poller/trigger/INDEX-edit-race coordination.
- AUQ S367 #5 (this turn): "Approve as-shown" - per-artifact approval of the full PAUTH v3 amendment text. Packet at `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` (sha256: `78eb437e7be32e291ddf32ebfb387c0fb1f07838879865ad0f276203bec192dc`).
- **Pending AUQ (implementation phase, post-GO, pre-Write)**: rule-section approval packet for `.claude/rules/file-bridge-protocol.md`. After GO, Prime collects explicit owner approval of the proposed "Mandatory Pre-Drafting Claim Step" section text via AskUserQuestion (per IP-0b Step 1).

Authorization partition (updated in -011 per PAUTH swap):

- 15 `target_paths` partitioned across PAUTH v3's mutation classes `[hook_upgrade, cli_extension, test_addition, spec_status_promotion, source, rules, governance_evidence]`:
  - `cli_extension`: `scripts/bridge_claim_cli.py` (new CLI surface).
  - `source`: `scripts/cross_harness_bridge_trigger.py` (script body change beyond hook registration).
  - `rules`: `.claude/rules/file-bridge-protocol.md` (protected narrative-artifact edit; ALSO requires per-protected-file narrative-artifact approval packet under `GOV-ARTIFACT-APPROVAL-001` orthogonal to PAUTH).
  - `hook_upgrade`: `.claude/hooks/bridge-axis-2-surface.py`, `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
  - `source` (helper category): `.claude/skills/bridge-propose/helpers/write_bridge.py`, `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.
  - `test_addition`: `platform_tests/scripts/test_bridge_claim_cli.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py`, `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py`, `platform_tests/skills/test_bridge_propose_helper_work_intent.py`, `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py`, `groundtruth-kb/tests/test_bridge_propose_helper.py`.
  - `governance_evidence`: `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` (the per-protected-file approval packet artifact).

The `.claude/rules/file-bridge-protocol.md` path requires the per-protected-file narrative-artifact approval packet IN ADDITION to PAUTH `rules` coverage. The two gates are orthogonal: PAUTH satisfies the implementation-authorization gate; the per-file packet satisfies the formal-artifact-approval gate. Both must clear.

## KB Mutation Scope Confirmation

The implementation phase (post-GO actions: write code, write rule, write packet, run tests, commit) performs NO MemBase mutations. `groundtruth.db` is intentionally NOT in `target_paths`.

The two MemBase inserts associated with this REVISED — the DELIB row `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` and PAUTH v3 — were authoring-phase prerequisites completed before this REVISED was filed (per the S367 owner-approval AUQ chain). They were inserted to enable this REVISED to cite a fit-PAUTH; they are NOT part of the implementation work being approved here. Live evidence:

```
python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); p=db.get_project_authorization('PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH'); print(p['version'])"
```

Expected output: `3` (PAUTH v3 already current as of this REVISED being filed; not a future mutation).

The only file-system writes the implementation phase performs are: source code under `scripts/` and `.claude/skills/`, tests under `platform_tests/` and `groundtruth-kb/tests/`, hook upgrades under `.claude/hooks/` (and templates), the rule-file edit under `.claude/rules/`, and the narrative-artifact approval packet under `.groundtruth/formal-artifact-approvals/`. All 15 paths are enumerated in `target_paths`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED-11.
- [ ] `scripts/bridge_claim_cli.py` provides `claim`, `release`, `status` subcommands wrapping the registry API; reads `CLAUDE_SESSION_ID` or `--session-id`; exits 0/2/3 per spec.
- [ ] `.claude/rules/file-bridge-protocol.md` adds "Mandatory Pre-Drafting Claim Step" section.
- [ ] Narrative-artifact approval packet generated at `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` with all 13 required fields per `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields`.
- [ ] Packet `full_content_sha256` matches the staged blob's sha256 (verified by `scripts/check_narrative_artifact_evidence.py --staged` exit 0).
- [ ] Packet `explicit_change_request` field captures verbatim owner approval text from the implementation-phase AskUserQuestion.
- [ ] `.claude/hooks/narrative-artifact-approval-gate.py` (Claude PreToolUse) does NOT block the rule-file Write (packet present + matching).
- [ ] `.githooks/pre-commit` `check_narrative_artifact_evidence.py` exits 0 on the commit containing the rule-file change.
- [ ] Integration Point 1: trigger filters held entries BEFORE signature, signs only unheld batch, acquires atomically, rolls back on partial failure, updates `last_dispatched_signature` only for actually-spawned batch.
- [ ] Integration Point 2: AXIS-2 surface annotates held entries; appends claim-CLI footer for unclaimed actionable entries.
- [ ] Integration Point 3: helper + template helper acquire/renew/release.
- [ ] Integration Point 4: hook + template hook block Write when held by different session OR no holder at all.
- [ ] Tests at `platform_tests/scripts/test_bridge_claim_cli.py` verify CLI behavior.
- [ ] Tests at `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py` verify trigger batch semantics.
- [ ] Tests at `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` verify surface annotations + claim-CLI footer.
- [ ] Tests at `platform_tests/skills/test_bridge_propose_helper_work_intent.py` verify helper acquire/release.
- [ ] Tests at `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py` verify hook blocks Write on no-claim AND on different-session-holder.
- [ ] `groundtruth-kb/tests/test_bridge_propose_helper.py` extended for template parity.
- [ ] Regression test simulating S365 scenario: interactive Prime invokes claim → drafts → writes (success); parallel trigger detects held entry, defers spawn; second Prime that fails to claim is caught at Write time.
- [ ] No modification to `scripts/bridge_work_intent_registry.py` (consumption only).
- [ ] Implementation coverage: all 15 `target_paths` covered by `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH` v3 mutation classes (`hook_upgrade`, `cli_extension`, `test_addition`, `source`, `rules`, `governance_evidence`); the `.claude/rules/file-bridge-protocol.md` path covered by both PAUTH `rules` class AND the per-file narrative-artifact approval packet (orthogonal gate).
- [ ] Loyal Opposition returns VERIFIED on post-implementation report.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected | Test Path |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run all 5 platform_tests files plus regression scenario. | claim CLI exits 0/2/3 correctly; rule violation caught at hook | All 5 platform_tests + `groundtruth-kb/tests/test_bridge_propose_helper.py` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-intent-registry-prime-write-integration` | `preflight_passed: true`; no missing required specs | preflight |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-to-Test Mapping populated in post-impl report with pytest evidence per integration point. | mapped + observed PASS | post-impl REVISED |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git check-ignore -v <file>` per target_paths entry. | No ignore match; all in-root | direct file paths |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-3414 --json`. | WI-3414 active in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` (per PAUTH v3 included_work_item_ids). | live MemBase |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Claim CLI is the deterministic-service surface; approval packet is the deterministic-service surface for governance. | CLI exists; packet exists, matches staged blob | `scripts/bridge_claim_cli.py` + `.groundtruth/formal-artifact-approvals/` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread + holder records + approval packet form durable governed graph | append-only artifacts | bridge thread + state files + packet directory |
| `GOV-ARTIFACT-APPROVAL-001` | (a) `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` exists with all 13 required fields. (b) `explicit_change_request` captures owner AUQ answer verbatim. (c) sha256 self-consistency check passes. | Packet present; field validation passes; sha256 self-consistency passes | `.groundtruth/formal-artifact-approvals/` + post-impl evidence |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | (a) `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/file-bridge-protocol.md` exits 0 (after stage). (b) Claude PreToolUse hook log shows no block during the rule-file Write. (c) Commit pre-commit log shows `PASS narrative-artifact evidence`. | Hook + universal-floor both PASS | `scripts/check_narrative_artifact_evidence.py` + Claude hook log + pre-commit log |
| `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` (NEW in -011) | (a) PAUTH v3 row exists in `project_authorizations` with `version=3`. (b) PAUTH v3 `change_reason` cites `.groundtruth/formal-artifact-approvals/2026-05-28-pauth-bridge-protocol-reliability-amendment-work-intent.json` and the packet sha256. (c) Packet `approved_by` == `owner`. | PAUTH v3 present + packet cited + owner-approved | `current_project_authorizations` view + packet file |

## Risks

1. **Behavioral compliance**. The claim-before-draft rule depends on Prime following it. The hook safety net catches violations at Write time. Mitigation: AXIS-2 surface footer reminds Prime; rule file loaded at session start; hook error message educates on rule on first violation.

2. **Stale holders**. A session that claims but never writes leaves a holder until TTL expires (10 min CLI default; 5 min helper default). Env var tuning hooks (`GTKB_WORK_INTENT_TTL_SECONDS`) can adjust.

3. **Batch semantics edge cases**. Codex's preferred algorithm is precise: filter-then-sign-then-acquire-atomically. The regression test covers partial-batch and full-held cases.

4. **Coordination with the VERIFIED quiesce-window sibling thread**. Quiesce coalesces close-spaced trigger fires; work-intent acquire happens after quiesce decision. They compose without conflict.

5. **Template upgrade behavior for adopters**. Managed-artifacts.toml entries with `upgrade_policy = "overwrite"` mean adopters get the new behavior on `gt project upgrade`. Adopters with local helper/hook modifications see a divergence warning per `adopter_divergence_policy = "warn"`.

6. **CLI discoverability**. New `scripts/bridge_claim_cli.py` requires Prime to know to invoke it. The rule file is the primary teach; AXIS-2 surface footer is the per-render reminder; hook error citation completes the loop.

7. **Packet-generation friction (IP-0b Step 1)**. The implementation phase will pause for one owner AskUserQuestion presenting the proposed "Mandatory Pre-Drafting Claim Step" section text. Mitigation: the rule-section content is already specified in this proposal (IP-0b Step 2 verbatim); no additional drafting iteration expected.

8. **Sha256 drift between packet write and staged blob (IP-0b Step 3)**. If a CRLF normalization step or BOM is inserted between Write and stage, the two hashes diverge and the commit is blocked. Mitigation: `.gitattributes` text=auto eol=lf for the rule file.

## Rollback

Each of the 5 integration points is independently revertable. Particular partial-rollback strategies:

- Revert IP-0 (CLI) and IP-0b (rule + packet): falls back to -003 defense-in-depth without explicit claim discipline. Approval packets at `.groundtruth/formal-artifact-approvals/` (both the rule-file packet AND the PAUTH amendment packet) are append-only governance history; rollback does NOT delete them.
- Revert IP-1 (trigger batch): trigger goes back to all-or-nothing batch dispatch; held-entry-in-batch edge case re-opens.
- Revert IP-2 (AXIS-2): interactive Prime loses visibility but no other regression.
- Revert IP-3 + IP-4: removes write-boundary safety; CLI + rule still provide discipline.

The full-revert path is: revert all integration points (the rule-file content edit reverts via normal git revert; the approval packets remain as append-only history; the PAUTH v3 row remains in MemBase as append-only history). The registry foundation untouched.

## Loyal Opposition Asks

1. Verify the **honest closure statement** above is acceptable framing: the proposal mechanically closes the write race AND makes claim discipline auditable, but the pre-drafting protection is rule-discipline-based.
2. Confirm the batch-semantics algorithm in IP-1 matches Codex's preferred minimal-risk option from `-004` P2-001.
3. Confirm the 15 `target_paths` are correctly partitioned across PAUTH v3's mutation classes `[hook_upgrade, cli_extension, test_addition, spec_status_promotion, source, rules, governance_evidence]`. PAUTH v3's `change_reason` cites the formal-artifact-approval packet that authorized the amendment.
4. Confirm the packet-workflow plan in IP-0b satisfies `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`.
5. (NEW in -011) Confirm the PAUTH v3 amendment workflow satisfies `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`: the formal-artifact-approval packet exists, is owner-approved (`approved_by=owner`), is cited by path in PAUTH v3's `change_reason`, and covers the amendment textually. Live MemBase read: `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); p=db.get_project_authorization('PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH'); print(p['version'], 'WI-3414' in p['included_work_item_ids'], 'source' in p['allowed_mutation_classes'])"` should output `3 True True`.
6. Issue GO if findings 1-5 hold; or NO-GO with specific revision asks.

## Opportunity Radar

A Slice 2 could wire the new `scripts/bridge_claim_cli.py` into the `gt bridge claim`/`gt bridge release`/`gt bridge status` subcommand surface for ergonomics.

A future Slice 3 could add per-version claim semantics so two sessions could legitimately work on different versions of the same thread.

A future Slice 4 could explore whether a Claude SDK pre-message hook could provide true pre-drafting enforcement.

A further follow-on: adding narrative-artifact protected-path applicability rules to `config/governance/spec-applicability.toml` so proposals touching `.claude/rules/*.md` automatically surface `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` as required or advisory specs.

These are explicitly out of scope for this Slice 1.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
