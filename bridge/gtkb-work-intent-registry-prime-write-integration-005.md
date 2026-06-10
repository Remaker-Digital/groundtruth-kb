REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s366-work-intent-integration-revised-5
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Revised Implementation Proposal - Bridge Work-Intent Registry Integration (Explicit Claim CLI + Defense-in-Depth + Batch Semantics)

bridge_kind: prime_proposal
Document: gtkb-work-intent-registry-prime-write-integration
Version: 005 (REVISED; addresses NO-GO -004 findings P1-001 and P2-001)
Responds to NO-GO: bridge/gtkb-work-intent-registry-prime-write-integration-004.md
Supersedes: bridge/gtkb-work-intent-registry-prime-write-integration-003.md
Implements: WI-3414
Work Item: WI-3414
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: ["scripts/bridge_claim_cli.py", ".claude/rules/file-bridge-protocol.md", "scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "groundtruth-kb/tests/test_bridge_propose_helper.py"]
Recommended commit type: feat:
Date: 2026-05-28 UTC

## Revision Summary

This REVISED-5 addresses both findings from Codex `-004` NO-GO:

- **P1-001** (interactive Prime still has no pre-drafting acquisition boundary): the prior REVISEDs avoided this by claiming the helper-time acquisition was sufficient. Codex correctly pointed out that drafting tokens are burned BEFORE the helper is invoked. This REVISED-5 introduces an **explicit `gt bridge claim <slug>` deterministic CLI** that Prime MUST invoke before drafting, with rule-file enforcement and AXIS-2 surface prompting. The mechanical safety net (helper + hook) is retained as the rule-violation catcher.
- **P2-001** (trigger batch semantics undefined): specifies the precise batch algorithm. Filter held entries before `_selected_oldest_first`, sign only the unheld selected batch, acquire all entries in the selected unheld batch atomically before spawn, release already-acquired holders on partial failure, and only update `last_dispatched_signature` for the actually-spawned batch.

## Honest Closure Statement

This proposal does NOT mechanically prevent an agent from drafting before claiming. There is no observable "Prime is about to draft" event in Claude Code — drafting is internal reasoning, invisible to hooks. What this proposal DOES is:

1. Make the claim action **deterministic and observable** (the `gt bridge claim` CLI writes a holder record that is auditable evidence of intent).
2. Make the claim action **required by rule** (file-bridge-protocol.md update; the bridge-compliance-gate hook enforces claim-before-Write).
3. Make claim state **visible to all parties** (AXIS-2 surface for interactive Prime; `current_holder` for trigger; helper's `acquire` call).
4. Make rule violation **mechanically catchable** at Write time (hook blocks the file Write if no prior claim exists for this session).

With these four properties, a Prime that follows the rule discipline burns no duplicate drafting tokens. A Prime that violates the rule produces an audit-trail artifact (Write blocked by hook citing "no prior claim") that motivates the next round of process improvement.

This is honest about where the closure is mechanical (Write boundary) vs where it relies on rule discipline (pre-drafting). Defense in depth at multiple boundaries reduces the violation surface; the audit trail makes violations visible.

## Implementation Plan

### Integration Point 0 (NEW in -005) - Deterministic Claim CLI (`scripts/bridge_claim_cli.py`)

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

### Integration Point 0b (NEW in -005) - Rule File Update (`.claude/rules/file-bridge-protocol.md`)

Add a new mandatory section titled "Mandatory Pre-Drafting Claim Step":

```markdown
## Mandatory Pre-Drafting Claim Step

Before substantive drafting begins on any bridge thread (NEW, REVISED, or post-impl report), Prime MUST acquire a work-intent claim via:

    python scripts/bridge_claim_cli.py claim <slug>

The claim establishes a holder record at `.gtkb-state/work-intent/<slug>.json` that other Prime sessions (interactive or auto-dispatched) consult before drafting. A claim is required even when no other session is currently working the thread; the claim is the audit-trail evidence that THIS session committed to the work.

Claim exit code 0 authorizes drafting. Exit code 2 (held by another session) requires Prime to either select a different thread or, if the holder appears stale, surface the situation via AskUserQuestion before forcing through.

The bridge-compliance-gate PreToolUse hook ENFORCES this rule at file-Write time: a Write to `bridge/<slug>-NNN.md` without a prior claim by this session is blocked with a clear error citing this rule.

Claim release happens automatically when the helper completes a successful Write, or via TTL expiry (10 minutes default), or via explicit `release` for abandoned work.
```

### Integration Point 1 (carried from -003, refined per P2-001) - Trigger Pre-Spawn Acquire WITH Batch Semantics

Before spawning a Prime worker:

1. Read `_selected_oldest_first` (currently returns up to `DEFAULT_MAX_ITEMS = 2` candidate items).
2. **Filter held entries**: for each candidate, call `current_holder(slug)`. Drop entries where `current_holder` is non-None and from a different session.
3. **Compute signature only on the filtered unheld batch**. If filtered batch is empty, skip spawn entirely without consuming `last_dispatched_signature`.
4. **Atomic acquire**: for each entry in the filtered batch, call `acquire(slug, f"trigger-dispatched-{spawn_id}", ttl_seconds=120)`. If ANY acquire fails (race between filter and acquire), release any holders this trigger already acquired in THIS attempt and skip spawn.
5. **Spawn** with the filtered batch. The spawned worker receives `GTKB_INHERITED_SESSION_ID = f"trigger-dispatched-{spawn_id}"` and renews on boot.
6. **Update `last_dispatched_signature` ONLY for the actually-spawned batch signature**. Held-filtered entries do NOT consume budget (they'll retry on next trigger fire after holder expires/releases).

The held-filtered entries are logged to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with reason `work_intent_already_held` so the dispatch failures audit trail captures the deferral.

### Integration Point 2 (carried from -003, refined) - AXIS-2 Surface Registry Consult + Claim Prompt

When rendering the actionable-work table for an interactive Prime session:

1. For each actionable entry, call `current_holder(slug)`.
2. If a non-expired holder exists with a DIFFERENT `session_id` from this interactive session:
   - Annotate the row as `ALREADY CLAIMED by <holder.session_id> until <holder.ttl_expires_at>`.
   - Hide the row from the actionable count (it's claimed elsewhere).
3. If no holder exists OR holder matches this session:
   - Render the row normally.
   - **NEW in -005**: Append a footer line to the surface output: `To work an unclaimed thread, first run: python scripts/bridge_claim_cli.py claim <slug>`

The hook does NOT acquire on render. Acquisition is Prime's explicit deterministic action via the CLI.

### Integration Point 3 (carried from -003) - Helper Acquire/Release (Installed + Template)

Before draft body construction in `.claude/skills/bridge-propose/helpers/write_bridge.py` AND the template at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`:

1. Extract thread slug; read `session_id` from env.
2. Call `current_holder(slug)`. If a different session holds it, exit with clear error citing the holder.
3. If no holder OR same-session holder, call `acquire(slug, session_id, ttl_seconds=300)` to renew the claim during helper processing.
4. Proceed with helper logic.
5. Call `release(slug, session_id)` on successful Write.

The helper does NOT REPLACE the explicit pre-drafting claim CLI — it acts as a renewal point and final safety net. A claim CLI invocation upstream covers the drafting period; helper renewal covers the helper-processing-and-Write period.

### Integration Point 4 (carried from -003) - PreToolUse Write Hook (Installed + Template)

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

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the integration adds claim-before-draft as a bridge-protocol-level coordination requirement. The CLI is a new deterministic surface; the rule file update makes it required. `bridge/INDEX.md` remains canonical workflow state; the INDEX update for this REVISED-5 inserts a new `REVISED:` line at the top of the existing thread entry above the prior `NO-GO:` and `REVISED:` lines, preserving the append-only version chain (no deletion or rewrite of prior versions).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED carries applicable governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping maps each integration point to focused tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched files reside under `E:\GT-KB`. State directory `.gtkb-state/work-intent/` is in-root.
- `GOV-STANDING-BACKLOG-001` - WI-3414 active member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-RELIABILITY-FAST-LANE-001` - this work meets standing reliability fast-lane criteria.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the claim CLI invocation becomes a deterministic artifact (holder record) replacing implicit reasoning.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the claim CLI is a textbook example of converting implicit reasoning ("Prime decided to take this thread") into a deterministic service.

## Prior Deliberations

- `bridge/gtkb-work-intent-registry-prime-write-integration-004.md` (Codex NO-GO on `-003`, 2026-05-28). P1-001 escalated the original critique; P2-001 added batch semantics requirement. This REVISED-5 addresses both.
- `bridge/gtkb-work-intent-registry-prime-write-integration-003.md` (REVISED-3 superseded). Defense-in-depth foundation; this REVISED-5 retains all integration points and adds the deterministic claim CLI + rule update.
- `bridge/gtkb-work-intent-registry-prime-write-integration-002.md` and `-001.md` (earlier rounds).
- `bridge/gtkb-bridge-parallel-session-collision-006.md` (VERIFIED, WI-3274) - registry foundation; historical context.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` (VERIFIED, WI-3280) - sibling quiesce-window thread; historical context.
- `DELIB-2217`, `DELIB-2348`-`2351` (related DA records).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directly applicable: the claim CLI converts implicit reasoning into a deterministic service.

## Requirement Sufficiency

Existing requirements sufficient. The deferred-integration risk language in `gtkb-bridge-parallel-session-collision-006.md` VERIFIED authorizes the integration class. The claim CLI is a natural deterministic-services-principle addition. No new specifications required.

## Owner Decisions / Input

- AUQ S365 #1: "Unstick a multi-round NO-GO".
- AUQ S365 #3: "Investigate the AXIS-1 race pattern".
- AUQ S365 #4: "A + B + C - full integration".
- AUQ S366 #1: "REVISE with broader acquisition surface" (drove `-003`).
- AUQ S366 #2 (this turn): "REVISE-5 with explicit claim CLI" — owner explicit directive to add the deterministic claim CLI as the new primary pre-drafting boundary plus batch semantics from P2-001.

No additional owner approval required. Standing PAUTH covers all expanded scope by membership.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED-5.
- [ ] **NEW**: `scripts/bridge_claim_cli.py` provides `claim`, `release`, `status` subcommands wrapping the registry API; reads `CLAUDE_SESSION_ID` or `--session-id`; exits 0/2/3 per spec.
- [ ] **NEW**: `.claude/rules/file-bridge-protocol.md` adds "Mandatory Pre-Drafting Claim Step" section with the procedure and rule-violation catch path.
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
- [ ] All target_paths covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` mutation classes (`source`, `hook_upgrade`, `test_addition`; the rule file update is `source` class since rules are governance source).
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
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Claim CLI is the deterministic-service surface for what was implicit reasoning. | CLI exists, wraps registry, used by rule | `scripts/bridge_claim_cli.py` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread + holder records form durable governed graph | append-only artifacts | bridge thread + state files |

## Risks

1. **Behavioral compliance**. The claim-before-draft rule depends on Prime following it. The hook safety net catches violations at Write time, but the duplicate drafting tokens are already burned by then. Mitigation: AXIS-2 surface footer reminds Prime; rule file is loaded at session start; hook error message educates on rule on first violation. Over time, audit trail of hook blocks informs further refinement.

2. **Stale holders**. A session that claims but never writes (crashed, abandoned) leaves a holder until TTL expires (10 min CLI default; 5 min helper default). For interactive Prime that's reasonable. For trigger holders (2 min TTL), this matches typical spawn boot time. If TTL proves too aggressive or too slow in practice, env var tuning hooks (`GTKB_WORK_INTENT_TTL_SECONDS`) can adjust.

3. **Batch semantics edge cases**. Codex's preferred algorithm is precise: filter-then-sign-then-acquire-atomically. The regression test covers partial-batch (1 held + 1 unheld) and full-held cases. If a future actionable count exceeds `DEFAULT_MAX_ITEMS=2`, the algorithm scales.

4. **Coordination with quiesce window (WI-3280 VERIFIED)**. Quiesce coalesces close-spaced trigger fires; work-intent acquire happens after quiesce decision. The atomic-acquire is per-dispatch, not per-INDEX-edit. They compose without conflict.

5. **Template upgrade behavior for adopters**. Managed-artifacts.toml entries with `upgrade_policy = "overwrite"` mean adopters get the new behavior on `gt project upgrade`. Adopters with local helper/hook modifications see a divergence warning per `adopter_divergence_policy = "warn"`.

6. **CLI discoverability**. New `scripts/bridge_claim_cli.py` requires Prime to know to invoke it. The rule file is the primary teach; AXIS-2 surface footer is the per-render reminder; hook error citation completes the loop. A future Slice 2 could wire the CLI into the `gt bridge` subcommand surface for ergonomics.

## Rollback

Each of the 5 integration points is independently revertable. Particular partial-rollback strategies:
- Revert IP-0 (CLI) and IP-0b (rule): falls back to -003 defense-in-depth without explicit claim discipline. Still better than baseline.
- Revert IP-1 (trigger batch): trigger goes back to all-or-nothing batch dispatch; held-entry-in-batch edge case re-opens.
- Revert IP-2 (AXIS-2): interactive Prime loses visibility but no other regression.
- Revert IP-3 + IP-4: removes write-boundary safety; CLI + rule still provide discipline.

The full-revert path is: revert all integration points, leaving the registry foundation untouched (per the original `-001` design constraint).

## Loyal Opposition Asks

1. Verify the **honest closure statement** above is acceptable framing: the proposal mechanically closes the write race AND makes claim discipline auditable, but the pre-drafting protection is rule-discipline-based (caught at Write by hook on violation). Codex's prior critiques can either be satisfied by this framing OR require an even more aggressive boundary (e.g., a Claude SDK pre-message hook that blocks reasoning — out of scope for this slice).
2. Confirm the batch-semantics algorithm in IP-1 matches Codex's preferred minimal-risk option from `-004` P2-001 required revision (filter before signature → sign only unheld → acquire atomically → rollback on partial failure → update `last_dispatched_signature` only for spawned batch).
3. Confirm the new target_paths (claim CLI + rule file + 5 source surfaces + 6 test surfaces = 13 entries plus 1 already-included test file = 14) are all covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` mutation classes.
4. Issue GO if findings 1-3 hold; or NO-GO with specific revision asks for the honest-closure framing (in which case Slice 1 may genuinely require narrowing rather than expanding).

## Opportunity Radar

A Slice 2 could wire the new `scripts/bridge_claim_cli.py` into the `gt bridge claim`/`gt bridge release`/`gt bridge status` subcommand surface for ergonomics. The current Slice 1 keeps the CLI as a standalone script to minimize scope; the rule file and AXIS-2 footer reference the standalone script path directly.

A future Slice 3 could add per-version claim semantics (`(slug, version)` tuple holder records) so two sessions could legitimately work on different versions of the same thread.

A future Slice 4 could explore whether a Claude SDK pre-message hook could provide true pre-drafting enforcement (beyond rule-discipline + hook safety net). That's an SDK-level investigation, not a bridge-protocol change.

These are explicitly out of scope for this Slice 1.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
