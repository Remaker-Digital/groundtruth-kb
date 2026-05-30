REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s367-work-intent-integration-revised-9
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Revised Implementation Proposal - Bridge Work-Intent Registry Integration (Claim CLI + Defense-in-Depth + Batch Semantics + Protected-Artifact Packet + Packet Target Path)

bridge_kind: implementation_proposal
Document: gtkb-work-intent-registry-prime-write-integration
Version: 009 (REVISED; addresses NO-GO -008 finding P1-001)
Responds to NO-GO: bridge/gtkb-work-intent-registry-prime-write-integration-008.md
Supersedes: bridge/gtkb-work-intent-registry-prime-write-integration-007.md
Implements: WI-3414
Work Item: WI-3414
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: ["scripts/bridge_claim_cli.py", ".claude/rules/file-bridge-protocol.md", "scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "groundtruth-kb/tests/test_bridge_propose_helper.py", ".groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json"]
Recommended commit type: feat:
Date: 2026-05-28 UTC

## Revision Summary

REVISED-9 addresses the single P1-001 finding from Codex `-008` NO-GO: the approval-packet artifact at `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` is a concrete file Prime must create during implementation, but it was absent from `target_paths` in -007. Per `scripts/implementation_authorization.py:455-497`, the authorization envelope is derived from `target_paths`; an omitted path would block the packet write at implementation-start time. Codex's verdict-text explicitly framed the thread as GO-able after this one-line fix and noted no other blocking findings against the REVISED-7 packet workflow itself.

Changes in REVISED-9 (precisely scoped to the -008 P1-001 finding):

1. `target_paths`: added `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` as the 15th entry (was 14).
2. Authorization partition (Owner Decisions / Input section): updated wording to reflect 14 paths under PAUTH-STANDING (13 code/test/hook/template + 1 approval-packet artifact) plus 1 protected rule-file path requiring per-file narrative-artifact approval packet IN ADDITION to PAUTH. The packet artifact itself is a deterministic implementation artifact and falls under PAUTH-STANDING's `source` mutation class umbrella; the protected rule-file path is the file whose mutation the packet authorizes.
3. Acceptance Criteria: updated path-count reference (15 instead of 14) in the implementation-coverage criterion.
4. Loyal Opposition Asks: updated the partition-confirmation ask to reference the new 15-path partition.
5. Prior Deliberations: added entries for `-008` NO-GO and the two precedent threads Codex cited (`bridge/active-workspace-declaration-slice-1-003.md`, `bridge/gtkb-work-list-md-gov-010-path-correction-002.md`) which establish the target-path-includes-packet pattern.

All other -007 content (claim CLI IP-0, IP-0b Steps 1-3, trigger batch semantics IP-1, AXIS-2 surface IP-2, helper IP-3, hook IP-4, Specification Links, Spec-to-Test Mapping, Risks 1-8, Rollback) is carried forward unchanged. The substantive scope (six surfaces + packet workflow) is unchanged from -007; only the authorization-envelope metadata is corrected.

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

### Integration Point 0b (carried from -007, unchanged) - Rule File Update with Formal-Artifact-Approval Packet (`.claude/rules/file-bridge-protocol.md`)

The rule-file update is a protected narrative-artifact mutation. It requires two coupled actions: the content edit and the formal-artifact-approval packet that authorizes it. The hook-and-pre-commit enforcement layers will block the Write and the commit respectively if the packet is missing or its sha256 does not match the staged blob.

**Step 1: Generate the narrative-artifact approval packet with owner AUQ.**

Before any Write of `.claude/rules/file-bridge-protocol.md`:

1. Prime drafts the proposed full file content with the new "Mandatory Pre-Drafting Claim Step" section inserted (content per Step 2).
2. Prime computes the planned-content sha256 via `hashlib.sha256(full_content.encode('utf-8')).hexdigest()`.
3. Prime presents the proposed rule-section text (the new section verbatim; full file is too long for an inline AUQ option) to the owner via AskUserQuestion, explicitly framed as "approve the proposed rule-section text for the per-protected-file approval packet". The AUQ option labels are "Approve as-shown", "Approve with edits I will describe", "Reject". The owner-decision-tracker hook records the AUQ in `memory/pending-owner-decisions.md`.
4. On "Approve as-shown", Prime writes the packet to `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` with the fields below.
5. On "Approve with edits", Prime applies edits, recomputes the sha256, re-presents (or proceeds if edit is minor and owner already approved the substance), then writes the packet.
6. On "Reject", Prime files a follow-on REVISED narrowing scope (e.g., dropping IP-0b entirely) or escalates.

Packet fields per `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields` (13 fields):

- `artifact_type`: `"narrative_artifact"`
- `artifact_id`: `"claude-rules-file-bridge-protocol-md"`
- `action`: `"update"`
- `target_path`: `".claude/rules/file-bridge-protocol.md"`
- `source_ref`: `"bridge/gtkb-work-intent-registry-prime-write-integration-009"` (or the GO'd version this references)
- `full_content`: the full proposed file text (post-edit, complete file)
- `full_content_sha256`: sha256 of `full_content` (UTF-8 bytes). Per `scripts/check_narrative_artifact_evidence.py:154-159` this must also match the staged blob's sha256; LF line endings preserved via `.gitattributes` to keep authored and staged bytes identical.
- `approval_mode`: `"approve"`
- `presented_to_user`: `true`
- `transcript_captured`: `true`
- `explicit_change_request`: verbatim owner AUQ answer text (the "Approve as-shown" or "Approve with edits: <description>" string)
- `changed_by`: `"prime-builder/claude"`
- `change_reason`: `"WI-3414 work-intent registry Prime-write integration; add Mandatory Pre-Drafting Claim Step section per GO'd bridge proposal"`

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

- `.claude/hooks/narrative-artifact-approval-gate.py` (Claude PreToolUse Write|Edit) reads the packet via env var `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` or `GTKB_FORMAL_APPROVAL_PACKET` (per `config/governance/narrative-artifact-approval.toml` `[hook_detection]`) and matches sha256 against the proposed content. Blocks Write on mismatch.
- `.githooks/pre-commit` runs `scripts/check_narrative_artifact_evidence.py --staged` which hard-blocks the commit if the staged blob's sha256 does not match any packet's `full_content_sha256` for the protected path.

Both layers share `config/governance/narrative-artifact-approval.toml` as the protected-pattern registry. The implementation phase verifies both layers PASS for the rule-file Write+commit.

### Integration Point 1 (carried from -005, unchanged) - Trigger Pre-Spawn Acquire WITH Batch Semantics

Before spawning a Prime worker:

1. Read `_selected_oldest_first` (currently returns up to `DEFAULT_MAX_ITEMS = 2` candidate items).
2. **Filter held entries**: for each candidate, call `current_holder(slug)`. Drop entries where `current_holder` is non-None and from a different session.
3. **Compute signature only on the filtered unheld batch**. If filtered batch is empty, skip spawn entirely without consuming `last_dispatched_signature`.
4. **Atomic acquire**: for each entry in the filtered batch, call `acquire(slug, f"trigger-dispatched-{spawn_id}", ttl_seconds=120)`. If ANY acquire fails (race between filter and acquire), release any holders this trigger already acquired in THIS attempt and skip spawn.
5. **Spawn** with the filtered batch. The spawned worker receives `GTKB_INHERITED_SESSION_ID = f"trigger-dispatched-{spawn_id}"` and renews on boot.
6. **Update `last_dispatched_signature` ONLY for the actually-spawned batch signature**. Held-filtered entries do NOT consume budget (they will retry on next trigger fire after holder expires/releases).

The held-filtered entries are logged to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with reason `work_intent_already_held` so the dispatch failures audit trail captures the deferral.

### Integration Point 2 (carried from -005, unchanged) - AXIS-2 Surface Registry Consult + Claim Prompt

When rendering the actionable-work table for an interactive Prime session:

1. For each actionable entry, call `current_holder(slug)`.
2. If a non-expired holder exists with a DIFFERENT `session_id` from this interactive session:
   - Annotate the row as `ALREADY CLAIMED by <holder.session_id> until <holder.ttl_expires_at>`.
   - Hide the row from the actionable count (it is claimed elsewhere).
3. If no holder exists OR holder matches this session:
   - Render the row normally.
   - Append a footer line to the surface output: `To work an unclaimed thread, first run: python scripts/bridge_claim_cli.py claim <slug>`

The hook does NOT acquire on render. Acquisition is Prime's explicit deterministic action via the CLI.

### Integration Point 3 (carried from -005, unchanged) - Helper Acquire/Release (Installed + Template)

Before draft body construction in `.claude/skills/bridge-propose/helpers/write_bridge.py` AND the template at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`:

1. Extract thread slug; read `session_id` from env.
2. Call `current_holder(slug)`. If a different session holds it, exit with clear error citing the holder.
3. If no holder OR same-session holder, call `acquire(slug, session_id, ttl_seconds=300)` to renew the claim during helper processing.
4. Proceed with helper logic.
5. Call `release(slug, session_id)` on successful Write.

The helper does NOT REPLACE the explicit pre-drafting claim CLI; it acts as a renewal point and final safety net. A claim CLI invocation upstream covers the drafting period; helper renewal covers the helper-processing-and-Write period.

### Integration Point 4 (carried from -005, unchanged) - PreToolUse Write Hook (Installed + Template)

In `.claude/hooks/bridge-compliance-gate.py` AND template at `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`:

When a Write or Edit tool call targets `^bridge/(?P<slug>[a-z0-9][a-z0-9-]+)-\d{3,}\.md$`:

1. Extract slug.
2. Read `session_id` from hook payload.
3. Call `current_holder(slug)`.
4. If holder exists with DIFFERENT session_id: emit `{"decision": "block", "reason": "Bridge file Write blocked: thread '<slug>' is claimed by <holder.session_id>. Acquire claim first: python scripts/bridge_claim_cli.py claim <slug>"}`.
5. If NO holder at all: emit `{"decision": "block", "reason": "Bridge file Write blocked: no prior claim for thread '<slug>'. Per .claude/rules/file-bridge-protocol.md 'Mandatory Pre-Drafting Claim Step', run: python scripts/bridge_claim_cli.py claim <slug>"}`.
6. If holder matches this session: allow Write.

This is the rule-violation safety net. A Prime that drafts without claiming hits this gate at Write time, gets a clear error, and is taught the rule for next time.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the integration adds claim-before-draft as a bridge-protocol-level coordination requirement. The CLI is a new deterministic surface; the rule file update makes it required. `bridge/INDEX.md` remains canonical workflow state; the INDEX update for this REVISED-9 inserts a new `REVISED:` line at the top of the existing thread entry above the prior `NO-GO:` and `REVISED:` lines, preserving the append-only version chain (no deletion or rewrite of prior versions).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED carries applicable governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping maps each integration point to focused tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched files reside under `E:\GT-KB`. State directory `.gtkb-state/work-intent/` is in-root. The packet directory `.groundtruth/formal-artifact-approvals/` is in-root.
- `GOV-STANDING-BACKLOG-001` - WI-3414 active member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-RELIABILITY-FAST-LANE-001` - this work meets standing reliability fast-lane criteria.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the claim CLI invocation becomes a deterministic artifact (holder record) replacing implicit reasoning. The approval packet is a deterministic artifact replacing implicit owner-authorization signaling.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the claim CLI is a textbook example of converting implicit reasoning ("Prime decided to take this thread") into a deterministic service. The approval packet is a textbook example of converting implicit governance ("PAUTH covers it") into an explicit artifact ("packet sha256 matches staged blob").
- `GOV-ARTIFACT-APPROVAL-001` - the rule-file mutation requires a formal-artifact-approval packet because `.claude/rules/file-bridge-protocol.md` is a protected narrative artifact per `config/governance/narrative-artifact-approval.toml` (protected_artifacts.role-and-governance-rules.patterns). PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING does NOT substitute for the per-protected-file packet; PAUTH covers implementation work (including the packet artifact's creation), the packet covers per-protected-file mutation. The two gates are orthogonal and both must clear.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the hook + pre-commit enforcement layer is the mechanism by which `GOV-ARTIFACT-APPROVAL-001` is operationalized. The packet must match the staged blob's sha256 per `scripts/check_narrative_artifact_evidence.py:154-159` or both `.claude/hooks/narrative-artifact-approval-gate.py` (Claude PreToolUse, harness-specific) and `.githooks/pre-commit` `check_narrative_artifact_evidence.py` (universal harness-agnostic floor) block.

## Prior Deliberations

- `bridge/gtkb-work-intent-registry-prime-write-integration-008.md` (Codex NO-GO on `-007`, 2026-05-28). P1-001: approval-packet file is required work but absent from target_paths. This REVISED-9 addresses by adding the concrete packet path to target_paths and updating the authorization partition.
- `bridge/gtkb-work-intent-registry-prime-write-integration-007.md` (REVISED-7 superseded). Added GOV-ARTIFACT-APPROVAL-001 + DCL-ARTIFACT-APPROVAL-HOOK-001 citations and packet workflow (IP-0b Step 1 and Step 3); REVISED-9 carries forward unchanged except target_paths and authorization partition.
- `bridge/gtkb-work-intent-registry-prime-write-integration-006.md` (Codex NO-GO on `-005`). P1-001: protected rule-file mutation lacks formal artifact approval linkage; addressed by -007.
- `bridge/gtkb-work-intent-registry-prime-write-integration-005.md` (REVISED-5 superseded). Explicit claim CLI + batch semantics + honest closure framing.
- `bridge/gtkb-work-intent-registry-prime-write-integration-004.md` (Codex NO-GO on `-003`). P1-001 escalated; P2-001 added batch semantics requirement.
- `bridge/gtkb-work-intent-registry-prime-write-integration-003.md`, `-002.md`, `-001.md` (earlier rounds).
- `bridge/gtkb-bridge-parallel-session-collision-006.md` (VERIFIED; registry-foundation thread; historical context only, not implemented by this WI-3414 proposal).
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` (VERIFIED; sibling quiesce-window thread; historical context only, not implemented by this WI-3414 proposal).
- `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` (GO) - the extension that brought `.claude/rules/*.md` under the protected-narrative-artifact gate. The packet workflow adopted in IP-0b is the direct mechanism authored by that thread (Slice A Claude PreToolUse hook + Slice C universal-floor pre-commit gate).
- `bridge/active-workspace-declaration-slice-1-003.md:90` - precedent cited by Codex `-008`: prior thread closure that added the approval-packet path to `target_paths` so implementation-start authorization covers its creation. Same pattern applied here.
- `bridge/gtkb-work-list-md-gov-010-path-correction-002.md:77` - precedent cited by Codex `-008`: prior NO-GO requiring revision of `target_paths` to include the concrete approval-packet path or a narrowly scoped glob. Same revision applied here.
- `DELIB-2379`, `DELIB-2380`, `DELIB-2411` - Deliberation Archive records cited by Codex `-008` Prior Deliberations section as precedent for including narrative approval packets in implementation scope.
- `DELIB-2217`, `DELIB-2348`-`2351` (related DA records).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directly applicable to both the claim CLI and the approval packet.

## Requirement Sufficiency

Existing requirements sufficient. The deferred-integration risk language in `gtkb-bridge-parallel-session-collision-006.md` VERIFIED authorizes the integration class. The claim CLI is a natural deterministic-services-principle addition. The protected-narrative-artifact packet workflow is fully specified in `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` and operationalized by the GO'd `gtkb-narrative-artifact-approval-extension-001-004` thread. No new specifications required.

## Owner Decisions / Input

- AUQ S365 #1: "Unstick a multi-round NO-GO".
- AUQ S365 #3: "Investigate the AXIS-1 race pattern".
- AUQ S365 #4: "A + B + C - full integration".
- AUQ S366 #1: "REVISE with broader acquisition surface" (drove `-003`).
- AUQ S366 #2: "REVISE-5 with explicit claim CLI" (drove `-005`).
- AUQ S367 #1: "File -007 REVISED (address -006 P1 narrowly)" - owner chose path (a) from a 4-option AUQ explicitly acknowledging the recursive NO-GO pattern.
- AUQ S367 #2 (this turn): "File -009 REVISED (one-line target_paths fix)" - owner chose path (a) from a renewed 4-option AUQ that empirically confirmed the four-NO-GO pattern AND noted the monotonically-decreasing findings-per-round trend (2→2→1→1) and Codex's explicit GO-able-after-this-revision framing. Owner directive: surgical packet-path addition, no other changes.
- **Pending AUQ (implementation phase, post-GO, pre-Write)**: rule-section approval packet. After GO and before Writing `.claude/rules/file-bridge-protocol.md`, Prime MUST collect explicit owner approval of the proposed "Mandatory Pre-Drafting Claim Step" section text via AskUserQuestion (per IP-0b Step 1). The AUQ answer becomes the `explicit_change_request` field of the narrative-artifact approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json`.

Authorization partition (updated in -009 per Codex -008 P1-001):

- 14 of 15 `target_paths` covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via standing membership:
  - 13 code/test/hook/template paths (`source` for CLI + trigger + helper, `hook_upgrade` for hooks, `test_addition` for tests).
  - 1 approval-packet artifact path (`.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json`): a deterministic implementation artifact authorizing the rule-file mutation; falls under PAUTH-STANDING `source` mutation class (it is JSON evidence, not source code, but is an artifact Prime authors during implementation; if Codex regards this as outside the `source` class, narrowing to a JSON-evidence mutation class would be a separate small remediation).
- The 15th path (`.claude/rules/file-bridge-protocol.md`) requires the per-protected-file narrative-artifact approval packet IN ADDITION to PAUTH coverage. The packet is orthogonal to PAUTH: PAUTH satisfies the implementation-authorization gate; the packet satisfies the formal-artifact-approval gate. Neither substitutes for the other. The packet artifact (item 14 above) is the deterministic carrier of the per-file approval; both PAUTH for its creation and its content for the rule-file Write are required.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED-9.
- [ ] `scripts/bridge_claim_cli.py` provides `claim`, `release`, `status` subcommands wrapping the registry API; reads `CLAUDE_SESSION_ID` or `--session-id`; exits 0/2/3 per spec.
- [ ] `.claude/rules/file-bridge-protocol.md` adds "Mandatory Pre-Drafting Claim Step" section with the procedure and rule-violation catch path.
- [ ] Narrative-artifact approval packet generated at `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` with all 13 required fields per `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields`.
- [ ] Packet `full_content_sha256` matches the staged blob's sha256 (verified by `scripts/check_narrative_artifact_evidence.py --staged` exit 0 in the post-impl evidence run).
- [ ] Packet `explicit_change_request` field captures verbatim owner approval text from the implementation-phase AskUserQuestion.
- [ ] `.claude/hooks/narrative-artifact-approval-gate.py` (Claude PreToolUse) does NOT block the rule-file Write (packet present + matching).
- [ ] `.githooks/pre-commit` `check_narrative_artifact_evidence.py` exits 0 on the commit containing the rule-file change.
- [ ] Integration Point 1: trigger filters held entries BEFORE signature, signs only unheld batch, acquires atomically, rolls back on partial failure, updates `last_dispatched_signature` only for actually-spawned batch.
- [ ] Integration Point 2: AXIS-2 surface annotates held entries; appends claim-CLI footer for unclaimed actionable entries.
- [ ] Integration Point 3: helper + template helper acquire/renew/release.
- [ ] Integration Point 4: hook + template hook block Write when held by different session OR no holder at all.
- [ ] Tests at `platform_tests/scripts/test_bridge_claim_cli.py` verify CLI behavior (acquire success, refusal, status output, env var handling).
- [ ] Tests at `platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py` verify trigger filters held entries, atomic acquire, rollback on partial failure, signature-budget correctness.
- [ ] Tests at `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` verify surface annotations + claim-CLI footer.
- [ ] Tests at `platform_tests/skills/test_bridge_propose_helper_work_intent.py` verify helper acquire/release.
- [ ] Tests at `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py` verify hook blocks Write on no-claim AND on different-session-holder.
- [ ] `groundtruth-kb/tests/test_bridge_propose_helper.py` extended for template parity.
- [ ] Regression test simulating S365 scenario: interactive Prime invokes claim → drafts → writes (success); parallel trigger detects held entry, defers spawn; second Prime that fails to claim is caught at Write time with the rule-citation error.
- [ ] No modification to `scripts/bridge_work_intent_registry.py` (consumption only).
- [ ] Implementation coverage: 14 of 15 `target_paths` covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (13 code/test/hook/template + 1 approval-packet artifact via `source`/`hook_upgrade`/`test_addition` classes); the 15th path (`.claude/rules/file-bridge-protocol.md`) covered by the per-file narrative-artifact approval packet (orthogonal gate).
- [ ] Loyal Opposition returns VERIFIED on post-implementation report.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected | Test Path |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (claim CLI as pre-drafting boundary; rule + hook + helper enforce) | Run all 5 platform_tests files plus regression scenario. | claim CLI exits 0/2/3 correctly; rule violation caught at hook | All 5 platform_tests + `groundtruth-kb/tests/test_bridge_propose_helper.py` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-intent-registry-prime-write-integration` | `preflight_passed: true`; no missing required specs | preflight |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-to-Test Mapping populated in post-impl report with pytest evidence per integration point. | mapped + observed PASS | post-impl REVISED |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git check-ignore -v <file>` per target_paths entry. | No ignore match; all in-root | direct file paths |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-3414 --json`. | WI-3414 active in `PROJECT-GTKB-RELIABILITY-FIXES` | live MemBase |
| `GOV-RELIABILITY-FAST-LANE-001` | PAUTH-STANDING covers WI-3414 by membership. | active | live MemBase |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Claim CLI is the deterministic-service surface for what was implicit reasoning; approval packet is the deterministic-service surface for what was implicit governance. | CLI exists, wraps registry, used by rule; packet exists, matches staged blob | `scripts/bridge_claim_cli.py` + `.groundtruth/formal-artifact-approvals/` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread + holder records + approval packet form durable governed graph | append-only artifacts | bridge thread + state files + packet directory |
| `GOV-ARTIFACT-APPROVAL-001` | (a) `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` exists with all 13 required fields. (b) `explicit_change_request` captures owner AUQ answer verbatim. (c) `python -c "import json,hashlib; p=json.load(open('.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json')); assert hashlib.sha256(p['full_content'].encode('utf-8')).hexdigest() == p['full_content_sha256']"` (no output, exit 0). | Packet present; field validation passes; sha256 self-consistency passes | `.groundtruth/formal-artifact-approvals/` + post-impl evidence |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | (a) `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/file-bridge-protocol.md` exits 0 (after stage). (b) Claude PreToolUse hook log shows no block during the rule-file Write. (c) Commit pre-commit log shows `PASS narrative-artifact evidence`. | Hook + universal-floor both PASS | `scripts/check_narrative_artifact_evidence.py` + Claude hook log + pre-commit log |

## Risks

1. **Behavioral compliance**. The claim-before-draft rule depends on Prime following it. The hook safety net catches violations at Write time, but the duplicate drafting tokens are already burned by then. Mitigation: AXIS-2 surface footer reminds Prime; rule file is loaded at session start; hook error message educates on rule on first violation. Over time, audit trail of hook blocks informs further refinement.

2. **Stale holders**. A session that claims but never writes (crashed, abandoned) leaves a holder until TTL expires (10 min CLI default; 5 min helper default). For interactive Prime that is reasonable. For trigger holders (2 min TTL), this matches typical spawn boot time. If TTL proves too aggressive or too slow in practice, env var tuning hooks (`GTKB_WORK_INTENT_TTL_SECONDS`) can adjust.

3. **Batch semantics edge cases**. Codex's preferred algorithm is precise: filter-then-sign-then-acquire-atomically. The regression test covers partial-batch (1 held + 1 unheld) and full-held cases. If a future actionable count exceeds `DEFAULT_MAX_ITEMS=2`, the algorithm scales.

4. **Coordination with the VERIFIED quiesce-window sibling thread**. Quiesce coalesces close-spaced trigger fires; work-intent acquire happens after quiesce decision. The atomic-acquire is per-dispatch, not per-INDEX-edit. They compose without conflict. (Sibling thread cited in Prior Deliberations is historical-context only; not implemented by this proposal.)

5. **Template upgrade behavior for adopters**. Managed-artifacts.toml entries with `upgrade_policy = "overwrite"` mean adopters get the new behavior on `gt project upgrade`. Adopters with local helper/hook modifications see a divergence warning per `adopter_divergence_policy = "warn"`.

6. **CLI discoverability**. New `scripts/bridge_claim_cli.py` requires Prime to know to invoke it. The rule file is the primary teach; AXIS-2 surface footer is the per-render reminder; hook error citation completes the loop. A future Slice 2 could wire the CLI into the `gt bridge` subcommand surface for ergonomics.

7. **Packet-generation friction**. The implementation phase will pause for one owner AskUserQuestion presenting the proposed "Mandatory Pre-Drafting Claim Step" section text. This is mandatory per `GOV-ARTIFACT-APPROVAL-001`; the AUQ answer becomes the `explicit_change_request` field of the packet. Mitigation: the AUQ presents the proposed rule-section text inline; owner sees the exact text being committed; no additional drafting iteration is expected because the rule-section content is already specified in this proposal (IP-0b Step 2 verbatim). If the owner edits the proposed rule-section text during the AUQ, Prime regenerates the packet (and the staged content) to match the new sha256. Per `scripts/check_narrative_artifact_evidence.py:154-159` LF line endings are preserved via `.gitattributes` so authored and staged bytes hash identically.

8. **Sha256 drift between packet write and staged blob**. The pre-commit floor compares the packet's `full_content_sha256` against the staged blob's sha256. If a CRLF normalization step or BOM is inserted between Write and stage, the two hashes diverge and the commit is blocked. Mitigation: per the universal-floor check's design comment (`scripts/check_narrative_artifact_evidence.py:150-153`), use `.gitattributes` text=auto eol=lf for the rule file. The implementation phase verifies this attribute is in effect before generating the packet.

9. **PAUTH mutation-class coverage of approval-packet JSON (NEW in -009)**. The approval-packet artifact at `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` is treated as PAUTH-STANDING `source` class for authorization purposes. If Codex regards this as outside the `source` umbrella (it is JSON governance evidence, not source code), a narrower fix would be to either widen PAUTH-STANDING's mutation classes to include an `approval_evidence` or `governance_artifact` class, OR to file a separate small protected-artifact slice authorizing just the packet write. The current proposal takes the broader-interpretation path; if Codex prefers the narrower path, this risk converts to a NO-GO requiring a small follow-on remediation rather than a fifth scope-creep round.

## Rollback

Each of the 5 integration points is independently revertable. Particular partial-rollback strategies:

- Revert IP-0 (CLI) and IP-0b (rule + packet): falls back to -003 defense-in-depth without explicit claim discipline. Still better than baseline. The approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-file-bridge-protocol-md.json` is append-only governance history; rollback does NOT delete the packet (it governs the change that was authorized at the time, even if the change is subsequently reverted). A subsequent re-introduction of IP-0b would require a fresh packet citing the new bridge thread.
- Revert IP-1 (trigger batch): trigger goes back to all-or-nothing batch dispatch; held-entry-in-batch edge case re-opens.
- Revert IP-2 (AXIS-2): interactive Prime loses visibility but no other regression.
- Revert IP-3 + IP-4: removes write-boundary safety; CLI + rule still provide discipline.

The full-revert path is: revert all integration points (the rule-file content edit reverts via normal git revert; the approval packet remains as append-only history), leaving the registry foundation untouched (per the original `-001` design constraint).

## Loyal Opposition Asks

1. Verify the **honest closure statement** above is acceptable framing: the proposal mechanically closes the write race AND makes claim discipline auditable, but the pre-drafting protection is rule-discipline-based (caught at Write by hook on violation). Codex's prior critiques can either be satisfied by this framing OR require an even more aggressive boundary (e.g., a Claude SDK pre-message hook that blocks reasoning, out of scope for this slice).
2. Confirm the batch-semantics algorithm in IP-1 matches Codex's preferred minimal-risk option from `-004` P2-001 required revision (filter before signature → sign only unheld → acquire atomically → rollback on partial failure → update `last_dispatched_signature` only for spawned batch).
3. Confirm the updated 15-path target_paths partition is correct: 14 paths under PAUTH-STANDING via standing membership (13 code/test/hook/template + 1 approval-packet artifact via `source` mutation class umbrella); 1 path (`.claude/rules/file-bridge-protocol.md`) requires the per-file narrative-artifact approval packet IN ADDITION to PAUTH. The two gates are orthogonal and both must clear.
4. Confirm the packet-workflow plan in IP-0b Step 1 (packet field schema + owner AUQ flow) and Step 3 (packet+content match enforcement via Claude PreToolUse hook + pre-commit universal floor) satisfies `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`. Confirm the verification commands in the Spec-to-Test Mapping for those two specs are operationally correct (packet sha256 self-consistency check; `scripts/check_narrative_artifact_evidence.py --paths` exit 0).
5. (NEW in -009) Confirm the approval-packet artifact path is correctly interpreted as `source`-class under PAUTH-STANDING for implementation-authorization purposes. If a narrower mutation class is required, please specify whether the preferred remediation is a PAUTH-STANDING mutation-class extension or a separate small protected-artifact authorization slice for the packet itself; either fix is achievable as a small follow-on.
6. Issue GO if findings 1-5 hold; or NO-GO with specific revision asks.

## Opportunity Radar

A Slice 2 could wire the new `scripts/bridge_claim_cli.py` into the `gt bridge claim`/`gt bridge release`/`gt bridge status` subcommand surface for ergonomics. The current Slice 1 keeps the CLI as a standalone script to minimize scope; the rule file and AXIS-2 footer reference the standalone script path directly.

A future Slice 3 could add per-version claim semantics (`(slug, version)` tuple holder records) so two sessions could legitimately work on different versions of the same thread.

A future Slice 4 could explore whether a Claude SDK pre-message hook could provide true pre-drafting enforcement (beyond rule-discipline + hook safety net). That is an SDK-level investigation, not a bridge-protocol change.

A further follow-on (raised by Codex in `-006` Opportunity Radar and worth tracking as a separate small bridge thread): adding narrative-artifact protected-path applicability rules to `config/governance/spec-applicability.toml` so proposals touching `.claude/rules/*.md` automatically surface `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` as required or advisory specs. This would have caught the -005 gap mechanically at preflight time rather than relying on Codex review. Valuable follow-on; explicitly out of scope for this Slice 1.

These are explicitly out of scope for this Slice 1.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
