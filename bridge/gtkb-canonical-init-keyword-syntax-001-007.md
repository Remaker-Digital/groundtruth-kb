REVISED

# Implementation Proposal — Canonical Init-Keyword Syntax for Cross-Harness Dispatch and Routines (REVISED-3)

bridge_kind: implementation_proposal
Document: gtkb-canonical-init-keyword-syntax-001
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` (REVISED-2; NO-GO at `-006`).

## Claim

Establish `::init gtkb <mode>` as the canonical first-line activator syntax for machine-emitted GroundTruth-KB session prompts. Mode vocabulary: closed set `{pb, lo}`. Strict parse, no synonyms. Worker-side strict-ignore-on-mismatch with audit log. The role-derived recipient model is migrated atomically with the active-session suppression contract preserved end-to-end.

This REVISED-3 closes the two Codex `-006` blockers:

- **F1 (Codex P1)**: Active-session suppression contract preserved under role-derived target resolution. The proposal now defines a complete **routing data model** (`DispatchTarget` dataclass) that all recipient-keyed callsites consume consistently. `_counterpart_role` is replaced by deriving the counterpart's command handle from the same identity-authority lookup. Lock-file naming is unchanged (`active-{command_handle}-session.lock`); receiver harnesses keep writing their own command-handle locks. Dispatch-state keys migrate from legacy `{prime, codex}` to durable role labels `{prime-builder, loyal-opposition}` with a backward-compat read shim. Five suppression-preservation tests added per Codex's recommended action.
- **F2 (Codex P1)**: `DCL-CONCEPT-ON-CONTACT-001` added to Specification Links with explicit enforcement-posture statement: this slice satisfies the DCL's "load-bearing concept appearing in bridge proposal/rule-file edit triggers glossary-entry obligation" clause via IP-7's narrative-artifact-approval-packeted glossary write.

All `-005` content not affected by F1/F2 is carried forward unchanged (F1/F2/F3 of `-004` and the IP-4 enum cleanup were closed directionally per Codex `-006` Positive Confirmations).

## Why Now

See `-001`, `-003`, `-005`. This REVISED-3 incorporates Codex's `-006` findings.

## Routing Data Model (NEW SECTION; ADDRESSES F1)

A single dataclass represents the resolved dispatch target. All recipient-keyed callsites in the trigger pipeline consume the relevant fields from this dataclass:

```python
from dataclasses import dataclass


HEARTBEAT_LOCK_TEMPLATE = "active-{role}-session.lock"  # unchanged from current source


@dataclass(frozen=True)
class DispatchTarget:
    """Resolved dispatch target for a needed role.

    Single source of truth for recipient-keyed routing decisions. Constructed
    by ``_resolve_dispatch_target(needed_role_label)`` per
    DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 and consumed by:

      - ``_dispatch_prompt`` (uses ``canonical_mode`` for keyword first-line)
      - ``_harness_command`` (uses ``command_handle`` for invocation)
      - ``check_counterpart_active`` (uses ``active_session_lock_name``)
      - dispatch-state operations (use ``dispatch_state_key``)
    """

    needed_role_label: str    # "prime-builder" or "loyal-opposition"
    harness_id: str           # "A", "B", etc. — durable identity from harness-identities.json
    command_handle: str       # "claude" / "codex" — from inverted harness-identities.json
    canonical_mode: str       # "pb" / "lo" — the keyword mode

    @property
    def active_session_lock_name(self) -> str:
        """Counterpart's active-session lock file name.

        Per the existing suppression contract (VERIFIED at
        ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md``):
        receiver harnesses write ``active-{command_handle}-session.lock`` to
        signal foreground activity. Naming is unchanged from the current
        ``HEARTBEAT_LOCK_TEMPLATE``; only its construction is now derived from
        the resolved command handle rather than a hardcoded
        ``recipient → handle`` map.
        """
        return HEARTBEAT_LOCK_TEMPLATE.format(role=self.command_handle)

    @property
    def dispatch_state_key(self) -> str:
        """Key used in ``dispatch-state.json`` recipients map.

        Migration plan:
          - Today: keys are legacy ``"prime"`` and ``"codex"`` (hardcoded).
          - New: keys are durable role labels ``"prime-builder"`` and
            ``"loyal-opposition"``.
          - Backward-compat read: ``_load_dispatch_state`` accepts both legacy
            and new keys; merges legacy ``"prime"`` → ``"prime-builder"`` and
            ``"codex"`` → ``"loyal-opposition"`` on read.
          - Forward write: only new keys are written.
          - One-shot migration on first dispatch after impl lands; legacy keys
            disappear from the state file naturally.
        """
        return self.needed_role_label
```

### Migration mapping reference (legacy → new)

| Legacy `recipient` | Today's hardcoded handle | New `DispatchTarget.command_handle` source | Legacy state key | New state key |
|---|---|---|---|---|
| `"prime"` | `claude` (from `_counterpart_role`) | inverted `harness-identities.json` lookup of harness ID assigned `prime-builder` | `"prime"` | `"prime-builder"` |
| `"codex"` | `codex` (from `_counterpart_role`) | inverted `harness-identities.json` lookup of harness ID assigned `loyal-opposition` | `"codex"` | `"loyal-opposition"` |

Lock file names (`active-{handle}-session.lock`) are unchanged because the receiver-side writer already uses its own command handle. Today's tests pin: `recipient="prime"` → reads `active-claude-session.lock`; `recipient="codex"` → reads `active-codex-session.lock`. Under the new model, with default fixture (claude=PB, codex=LO): `needed_role_label="prime-builder"` → resolves to `command_handle="claude"` → reads same lock. After role-switch fixture (claude=LO, codex=PB): `needed_role_label="prime-builder"` → resolves to `command_handle="codex"` → reads `active-codex-session.lock`. The lock-file behavior is now correct under role-switch.

## Why Not (alternatives reconsidered)

Carried forward from `-005`. Additional rejection per F1:

- **Keep `_counterpart_role` hardcoded `recipient → handle` map**: rejected. Preserves the recipient-as-identity-proxy bug class. Under role-switch, suppression checks the wrong lock and dispatch-state cross-contaminates.
- **Migrate state keys to durable harness IDs (`A`, `B`)**: rejected as too disruptive. Role labels (`prime-builder`, `loyal-opposition`) match the routing semantic; harness-IDs match the identity authority but introduce harder-to-read state files.
- **Multi-keyed state (tuple keys)**: rejected as overengineered for the two-recipient case.

## Prior Deliberations

Carried forward from `-005`, with one update:

- `bridge/gtkb-canonical-init-keyword-syntax-001-006.md` (NO-GO) — F1/F2 of REVISED-2 addressed by this REVISED-3.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` (VERIFIED) — the active-session suppression contract this REVISED-3 must preserve. Defines lock file naming (`active-{role}-session.lock`), sanity TTL (default 120s), and `last_suppressed_signature` vs `last_dispatched_signature` state-machine semantics. The migration plan in the Routing Data Model section preserves all five behaviors verified by that thread.
- `bridge/gtkb-canonical-init-keyword-syntax-001-002.md` (NO-GO) — F1/F2/F3 of `-001`.
- `bridge/gtkb-canonical-init-keyword-syntax-001-004.md` (NO-GO) — F1/F2/F3 of `-003`.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-002.md` (NO-GO; live state) — set-membership semantic does not depend on this thread.
- `bridge/gtkb-command-surface-003.md`, `-004.md` (architectural plan VERIFIED).
- `.claude/rules/operating-role.md` (canonical).
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO).
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-008.md` (GO).
- Auto-memory `feedback_init_keyword_as_role_symmetric_activator.md`.
- `DELIB-S339-2026-05-09-CANONICAL-INIT-KEYWORD-SYNTAX-OWNER-DIRECTIVE` (pending DA harvest).
- `DELIB-S339-2026-05-09-CONSISTENT-ASSERTION-AUTHORITY-CHOICE` (pending DA harvest).
- `DELIB-S339-2026-05-09-STRICT-IGNORE-ON-MISMATCH-REFINEMENT` (pending DA harvest).
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` — owner directive establishing the 120s sanity TTL referenced in the existing `check_counterpart_active` source. The migration must preserve.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps each cited spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets for new SPEC + DCL inserts; narrative-artifact-approval packet for `canonical-terminology.md` glossary edit.
- **`DCL-CONCEPT-ON-CONTACT-001`** (added per Codex F2) — *the load-bearing concept "canonical init keyword" appearing in this bridge proposal triggers a mandatory glossary entry per the DCL's specify-on-contact obligation*. Status: `specified`. Enforcement posture for this slice: **blocking** (the glossary-entry write at IP-7 with narrative-artifact-approval packet is the satisfaction; no waiver requested). The DCL's machine-checkable assertions are exercised by IP-8 test `T-CIK-glossary-entry`.

**Governing role/dispatch specs (per Codex `-004` F1; carried forward from `-005`):**

- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 verified — *"Prime Builder and Loyal Opposition are portable harness-assigned roles."* The resolver derives the keyword and command handle from the durable role assignment; owner role-switch propagates naturally.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 verified — *"GT-KB installs must prepare capable harnesses for Prime Builder and Loyal Opposition roles."* The resolver tracks whatever the durable record says.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1 specified — *"Spec-linkage enforcement must apply across all bridge submission paths."* Worker-side strict-ignore is symmetric across both Claude and Codex SessionStart hooks.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 specified — *"Bridge dispatch mechanism spawns headless harness instances when actionable work appears."* Keyword emission gated by existing actionable-signature predicate.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 specified — *"Bridge dispatch mechanism auto-triggers harness when work waits, never when idle."* Keyword emission only inside `_dispatch_prompt`.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 specified — *"Bridge dispatch prompts must defer to the durable role record, not assert role inline."* Receiver checks set-membership against own durable role; mismatch → silent drop.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 specified — *"S321 smart-poller daemon ran with dispatch disabled for ~8 hours, undetected."* Audit-log on misdirected dispatch is investigable.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**Specs created by this slice:**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (NEW) — defines `::init gtkb <mode>`; mode vocabulary `{pb, lo}` (closed); regex parse; no synonyms.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (NEW) — emitter derives keyword via two-step lookup (`role-assignments.json` → identity inversion); receiver checks set-membership; mismatch → silent drop with audit log.

## Owner Decisions / Input

This REVISED-3 cites the same six explicit AskUserQuestion approvals plus standing parity directives as `-005`:

1. AUQ 2026-05-09: file thread now → "File now (Recommended)".
2. AUQ 2026-05-09: authority semantic → "Consistent assertion (Recommended)".
3. AUQ 2026-05-09: strict-ignore refinement → owner directive *"the hook should check the durable role record and ignore the notification if it doesn't match."*
4. AUQ 2026-05-09: review-then-revise sequencing → "Let Codex review -001 first (Recommended)".
5. AUQ 2026-05-09: revise canonical-syntax `-005` → "Revise canonical-syntax to `-005` (Recommended)" (carries to `-007`).
6. AUQ 2026-05-09 (prior): parity directive (recurring).

Owner-input dependencies during implementation (unchanged): 2 formal-artifact-approval packets (SPEC + DCL); 1 narrative-artifact-approval packet (canonical-terminology.md). No pre-impl acknowledgement gate needed.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, no blocking clause gaps.

## Implementation Plan

### IP-1 — Define `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (UNCHANGED FROM -005)

Regex `^::init gtkb (pb|lo)$`; first-line-only; closed vocabulary `{pb, lo}`; emitted by cross-harness trigger today and future routines.

### IP-2 — Define `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (UNCHANGED FROM -005)

Emitter: two-step durable-record lookup with drift detection. Receiver: set-membership check with strict-ignore-on-mismatch audit log. See `-005` IP-2 for full text.

### IP-3 — Implement `DispatchTarget` and migrate the trigger pipeline (REVISED FROM -005 PER F1)

Three sub-IPs:

#### IP-3a — `DispatchTarget` dataclass + resolver

Add `DispatchTarget` to `scripts/cross_harness_bridge_trigger.py` per the Routing Data Model section above. Implement `_resolve_dispatch_target(needed_role_label)` per `-005` IP-3 (carried forward unchanged). The resolver returns a `DispatchTarget` instance.

#### IP-3b — Migrate recipient-keyed callsites

Replace recipient-handle parameters with `DispatchTarget` consumption:

- `_dispatch_prompt(target, items, max_items)` — uses `target.canonical_mode` for the `::init gtkb <mode>` keyword first-line. Existing prose role-line retained as defense-in-depth.
- `_harness_command(target, prompt, project_root)` — uses `target.command_handle` to select invocation: `"claude"` → `claude -p`; `"codex"` → `codex exec`. The legacy `recipient` parameter is removed; the function takes the resolved target.
- `_counterpart_role(target)` is removed. Its callsite uses `target.command_handle` directly. (The function existed to map recipient-handle to harness-handle; with `DispatchTarget`, that mapping is already done at resolution time.)
- `check_counterpart_active(target, state_dir)` — reads `state_dir / target.active_session_lock_name`. Existing 120-second sanity TTL behavior unchanged. Fail-open semantics on read errors unchanged.
- `_spawn_harness(target=...)` — uses `target.command_handle` for executable selection and `target.dispatch_state_key` for state-machine recording.
- Caller in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — translates bridge-state classification (NEW/REVISED → LO; GO/NO-GO → PB) into `needed_role_label` (`"loyal-opposition"` / `"prime-builder"`) and passes to `_resolve_dispatch_target`.

#### IP-3c — Migrate dispatch-state-key schema with backward-compat read

Update state-file I/O:

```python
LEGACY_TO_NEW_STATE_KEY = {
    "prime": "prime-builder",
    "codex": "loyal-opposition",
}


def _load_dispatch_state(state_path: Path) -> dict:
    """Load dispatch-state.json with backward-compat key migration on read.

    Legacy keys ``"prime"`` and ``"codex"`` are translated to durable role
    labels on read so the in-memory state uses only new keys. Forward writes
    use only new keys; legacy keys disappear from the file naturally on the
    first dispatch after impl lands.
    """
    if not state_path.exists():
        return {"recipients": {}}
    raw = json.loads(state_path.read_text(encoding="utf-8"))
    recipients = raw.get("recipients", {}) if isinstance(raw, dict) else {}
    migrated: dict[str, dict] = {}
    for key, value in recipients.items():
        new_key = LEGACY_TO_NEW_STATE_KEY.get(key, key)
        if new_key in migrated:
            # If both legacy and new keys exist (transitional), prefer the
            # newer mtime data. For the v1 migration this is a defensive
            # branch; in practice only one form will exist on first read.
            existing = migrated[new_key]
            existing_ts = existing.get("last_dispatched_at") or ""
            value_ts = value.get("last_dispatched_at") or ""
            if value_ts > existing_ts:
                migrated[new_key] = value
        else:
            migrated[new_key] = value
    return {"recipients": migrated}
```

Forward writes use new keys exclusively. The migration is one-shot: after the first dispatch under the new code, the state file contains only `{prime-builder, loyal-opposition}` keys.

### IP-4 — SessionStart hooks with `StartupDecision` enum (UNCHANGED FROM -005)

Five-decision enum implementation in both `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py`. See `-005` IP-4 for full text.

### IP-5 — Coordination with `gtkb-single-harness-bridge-dispatcher-001` (UNCHANGED FROM -005)

This thread does NOT predicate set-membership on the dispatcher's approval. Set-membership is implemented for current scalar-role schema directly.

### IP-6 — CS-2 coordination — registry entry (UNCHANGED FROM -005)

Future CS-2 registry entry for `::init` with `gtkb {pb|lo}` argument vocabulary. This thread does not gate on CS-2.

### IP-7 — Add canonical-terminology entry per `DCL-CONCEPT-ON-CONTACT-001` (UNCHANGED FROM -005, RE-FRAMED PER F2)

`.claude/rules/canonical-terminology.md` § GT-KB DA Read-Surface and Operational Vocabulary — new entry "canonical init keyword". Narrative-artifact-approval packet required. **This is the satisfaction of `DCL-CONCEPT-ON-CONTACT-001` for this slice's load-bearing concept introduction.**

### IP-8 — Tests (REVISED FROM -005 PER F1)

Seven test surfaces (was six in `-005`; F1 adds suppression-preservation tests):

1. `tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — pure parser test; valid/invalid forms.
2. `tests/scripts/test_cross_harness_bridge_trigger.py` (extend) — `test_dispatch_target_resolved_via_identities_map` (resolution; both fixtures patched).
3. `tests/scripts/test_cross_harness_bridge_trigger.py` (extend) — `test_dispatch_resolution_fail_closed_drift` (stale `harness_type`, missing identity entry, etc.).
4. `tests/scripts/test_claude_session_start_dispatcher.py` and `test_codex_session_start_dispatcher.py` (extend) — five-enum-decision-path tests.
5. `tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — DCL assertions runner; greps source for required patterns and absence of harness-local override + absence of `harness_type` command-handle reliance.
6. `tests/scripts/test_governing_specs_preserved.py` (NEW; per Codex `-004` F1) — preservation tests for the 7 governing specs.
7. **`tests/scripts/test_cross_harness_trigger_suppression.py` (extend; NEW per Codex `-006` F1)** — five suppression-preservation tests:
   - `T-CIK-suppress-correct-handle-on-default-fixture` — default fixture (claude=PB, codex=LO); `needed_role_label="prime-builder"` → resolves to `command_handle="claude"` → suppression checks `active-claude-session.lock`. Existing VERIFIED behavior.
   - `T-CIK-suppress-correct-handle-after-role-switch` — patched fixture (claude=LO, codex=PB); `needed_role_label="prime-builder"` → resolves to `command_handle="codex"` → suppression checks `active-codex-session.lock`. NEW capability under role-derived model.
   - `T-CIK-suppress-on-fresh-active-lock` — when the resolved counterpart's lock is fresh (mtime within sanity TTL), `check_counterpart_active(target, ...)` returns True and dispatch is suppressed. Carried-forward VERIFIED behavior.
   - `T-CIK-retry-after-lock-exit` — when the lock is removed (or stale beyond TTL), subsequent dispatch is allowed. Carried-forward VERIFIED behavior.
   - `T-CIK-no-duplicate-state-after-migration` — write a state file with legacy keys (`{prime, codex}`); load it; assert in-memory state has only new keys (`{prime-builder, loyal-opposition}`); dispatch one entry; assert the written file has only new keys; no signature double-counting.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-CIK-syntax-parser-valid | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (regex) | `test_canonical_init_keyword_syntax::test_valid_forms_accepted`. |
| T-CIK-syntax-parser-invalid | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (no synonyms) | `test_canonical_init_keyword_syntax::test_invalid_forms_rejected`. |
| T-CIK-resolver-via-identities | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (emitter clause) | `test_cross_harness_bridge_trigger::test_dispatch_target_resolved_via_identities_map`. |
| T-CIK-resolver-fail-closed-drift | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (drift detection) | `test_cross_harness_bridge_trigger::test_dispatch_resolution_fail_closed_drift`. |
| T-CIK-claude-receiver-decisions | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver clause) | `test_claude_session_start_dispatcher::test_startup_decision_enum_paths`. |
| T-CIK-codex-receiver-decisions | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver parity) | `test_codex_session_start_dispatcher::test_startup_decision_enum_paths`. |
| T-CIK-glossary-entry | **DCL-CONCEPT-ON-CONTACT-001** (load-bearing concept obligation) | grep `.claude/rules/canonical-terminology.md` for "canonical init keyword" entry; assert narrative-artifact-approval packet exists at IP-7 commit time. |
| T-CIK-dcl-assertions | IP-2 assertions | `test_canonical_init_keyword_assertions` — greps for required patterns + absence of legacy authority. |
| T-CIK-role-portability | GOV-HARNESS-ROLE-PORTABILITY-001 | `test_governing_specs_preserved::test_role_portability_preserved` — role-switch fixture; assert dispatch tracks. |
| T-CIK-multi-harness-config | GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | `test_governing_specs_preserved::test_either_harness_can_hold_either_role`. |
| T-CIK-cross-harness-enforcement | DCL-CROSS-HARNESS-ENFORCEMENT-001 | `test_governing_specs_preserved::test_strict_ignore_applies_to_both_harnesses`. |
| T-CIK-actionable-only-spawn | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 | `test_governing_specs_preserved::test_keyword_emitted_only_on_actionable`. |
| T-CIK-no-idle-emission | DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 | `test_governing_specs_preserved::test_no_keyword_on_idle_signature`. |
| T-CIK-defer-to-durable | DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2 | `test_governing_specs_preserved::test_receiver_defers_to_durable_record`. |
| T-CIK-audit-log-on-misdirect | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 | `test_governing_specs_preserved::test_misdirected_dispatch_writes_audit_log`. |
| **T-CIK-suppress-default-fixture** | active-session suppression VERIFIED contract (carried forward) | `test_cross_harness_trigger_suppression::test_suppress_correct_handle_on_default_fixture`. |
| **T-CIK-suppress-after-role-switch** | active-session suppression under role-switch (NEW under role-derived model) | `test_cross_harness_trigger_suppression::test_suppress_correct_handle_after_role_switch`. |
| **T-CIK-suppress-on-fresh-lock** | active-session suppression VERIFIED contract | `test_cross_harness_trigger_suppression::test_suppress_on_fresh_active_lock`. |
| **T-CIK-retry-after-lock-exit** | active-session suppression VERIFIED contract | `test_cross_harness_trigger_suppression::test_retry_after_lock_exit`. |
| **T-CIK-no-duplicate-state-migration** | dispatch-state-key migration backward-compat | `test_cross_harness_trigger_suppression::test_no_duplicate_state_after_migration`. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix: `DispatchTarget` dataclass is the single source of truth for routing decisions; all five recipient-keyed callsites (`_dispatch_prompt`, `_harness_command`, `check_counterpart_active`, `_spawn_harness`, dispatch-state I/O) consume from it; the active-session suppression VERIFIED contract is preserved end-to-end.
- [ ] Codex confirms F1 sub-fix: `_counterpart_role` is removed; its functionality is replaced by `target.command_handle` derivation at resolution time.
- [ ] Codex confirms F1 sub-fix: dispatch-state-key migration is correctly specified (legacy `prime`/`codex` keys read with translation; forward writes use `prime-builder`/`loyal-opposition` only); `T-CIK-no-duplicate-state-migration` exercises the migration path.
- [ ] Codex confirms F1 sub-fix: lock-file naming is unchanged (`active-{command_handle}-session.lock`); receiver harnesses keep writing their own command-handle locks; the trigger reads via `target.active_session_lock_name`.
- [ ] Codex confirms F2 fix: `DCL-CONCEPT-ON-CONTACT-001` is in Specification Links with explicit blocking-enforcement statement; IP-7 glossary write is the satisfaction; T-CIK-glossary-entry covers the assertion.
- [ ] Codex confirms all five suppression-preservation tests are concrete and runnable.

## Risk / Rollback

(Carried forward from `-005` with additions:)

- **Risk:** state-file migration leaves legacy keys + new keys coexisting in `dispatch-state.json`. Mitigation: migration is one-shot read-translate-then-write; the defensive merge branch in `_load_dispatch_state` handles transitional state by preferring newer mtime data. Tests cover the merge path.
- **Risk:** receiver harness writes its lock file using a different naming convention (e.g., `active-prime-session.lock` vs `active-claude-session.lock`). Mitigation: lock-file writers (the receiver harnesses themselves) use their own command handle, which is `claude` or `codex` from `harness-identities.json`. The trigger reads via the same authority. Naming is symmetric.
- **Risk:** `_counterpart_role` removal breaks third-party callers (e.g., test fixtures, doctor checks). Mitigation: search the codebase for all callers; update each. The function was internal to `cross_harness_bridge_trigger.py`; greps confirm no external callsites.
- **Risk:** `DispatchTarget` dataclass introduces import dependency for callers. Mitigation: the dataclass is defined in the same module; external callers use the resolver function which returns it.

**Rollback:**

- Revert `_counterpart_role` and recipient-handle pipeline.
- Revert `_load_dispatch_state` migration; restore legacy-key writes.
- Revert `DispatchTarget` dataclass and `_resolve_dispatch_target` resolver.
- Revert canonical keyword first-line.
- Revert `StartupDecision` enum.
- Revert IP-7 glossary entry.
- Mark new SPEC + DCL MemBase rows superseded.
- Delete the new test files including `test_governing_specs_preserved.py` and the suppression-preservation extensions.

## Files Expected To Change

- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (this REVISED-3 proposal).
- `bridge/INDEX.md` (REVISED entry prepended).
- `scripts/cross_harness_bridge_trigger.py` — IP-3a + IP-3b + IP-3c: `DispatchTarget` dataclass; `_resolve_dispatch_target`; `_invert_identities`; pipeline migration; `_load_dispatch_state` with backward-compat shim. Removes `_counterpart_role`.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — IP-3 update callsite to pass `needed_role_label`.
- `.claude/hooks/session_start_dispatch.py` — IP-4 `StartupDecision` enum + `_bridge_dispatch_keyword_check`.
- `.codex/gtkb-hooks/session_start_dispatch.py` — IP-4 Codex parity.
- `.claude/rules/canonical-terminology.md` — IP-7 new glossary entry (narrative-artifact-approval packet).
- `tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — IP-8.
- `tests/scripts/test_cross_harness_bridge_trigger.py` — IP-8 extend with resolution + drift tests.
- `tests/scripts/test_claude_session_start_dispatcher.py` — IP-8 extend with five-enum-path tests.
- `tests/scripts/test_codex_session_start_dispatcher.py` — IP-8 extend or create with Codex parity.
- `tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — IP-8.
- `tests/scripts/test_governing_specs_preserved.py` (NEW) — IP-8.
- **`tests/scripts/test_cross_harness_trigger_suppression.py` — IP-8 extend with five suppression-preservation tests (NEW per F1).**
- MemBase: `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` insert; `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` insert.

## Open Follow-Ons

(Carried forward from `-005`):

1. Future: doctor check surfacing accumulated `dispatch-failures.jsonl` entries.
2. Future: when a role-set schema lands, update `_resolve_own_role_set` to read native sets.
3. Future: CS-2 registry entry for `::init` with `gtkb {pb|lo}`.
4. Future: mode vocabulary expansion via spec amendment.

## Recommended Commit Type

`feat:` — net-new capability surface (canonical init-keyword syntax; role-derived recipient model; `DispatchTarget` dataclass; dispatch-state-key migration; receiver-side strict-ignore).

## Loyal Opposition Asks

1. Confirm F1 fix: `DispatchTarget` dataclass design is correct; all five recipient-keyed callsites consume from it; suppression-preservation tests cover the role-switch case.
2. Confirm F1 sub-fix: dispatch-state-key migration plan is sound (read-translate, write-new); backward-compat is genuinely transitional and not a permanent dual-key contract.
3. Confirm F1 sub-fix: lock-file naming preservation is correct (receivers write their own command-handle locks; trigger reads via resolved handle).
4. Confirm F2 fix: `DCL-CONCEPT-ON-CONTACT-001` enforcement-posture statement is correct; IP-7 glossary write satisfies the DCL.
5. Confirm carried-forward content from `-005` (F1/F2/F3 of `-004` + IP-4 enum) remains directionally closed under F1's restructuring.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
