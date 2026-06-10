REVISED

# Implementation Proposal — Canonical Init-Keyword Syntax for Cross-Harness Dispatch and Routines (REVISED-1)

bridge_kind: prime_proposal
Document: gtkb-canonical-init-keyword-syntax-001
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-canonical-init-keyword-syntax-001.md` (NEW; NO-GO at `-002`).

## Claim

Establish `::init gtkb <mode>` as the canonical first-line activator syntax for machine-emitted GroundTruth-KB session prompts (cross-harness dispatch, single-harness dispatcher routine, future routines). Mode vocabulary: closed set `{pb, lo}`. No synonyms; strict parse.

This REVISED-1 addresses the three Codex NO-GO findings on `-001`/`-002` plus two owner refinements landed 2026-05-09:

- **F1 (Codex P1)**: drop harness-local-override authority entirely. The sole authority for durable role is `harness-state/role-assignments.json` per `.claude/rules/operating-role.md`. Harness-local files (e.g., `harness-state/codex/operating-role.md`) are legacy pointers, not authority sources.
- **F2 (Codex P1)**: replace the broken `_resolve_dispatch_mode(recipient)` algorithm. The new algorithm resolves *needed role* (the durable-role label that this work requires) → harness ID via `harness-state/role-assignments.json` → harness command-handle via `harness-state/harness-identities.json`. The trigger no longer assumes `recipient="codex" ⇒ LO` or `recipient="prime" ⇒ PB`; it derives both the recipient and the keyword from the durable role map.
- **F3 (Codex P2)**: drop `status` from the mode vocabulary. Closed vocabulary becomes `{pb, lo}`. Both modes have explicit consumers (cross-harness trigger today; single-harness dispatcher per `bridge/gtkb-single-harness-bridge-dispatcher-001.md` tomorrow). The original `status` mode targeted the now-paused bridge-status thread (subsumed into single-harness dispatcher per owner directive 2026-05-09); no current consumer remains. No pre-impl owner acknowledgement needed because the closed vocabulary `{pb, lo}` matches the owner's original directive verbatim.
- **Owner refinement A**: `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` worker-side contract changes from "warn-and-fall-back" to **strict-ignore-on-mismatch** — silent drop with audit-log entry; the dispatched session exits without processing the prompt. Per owner directive 2026-05-09: *"the hook should check the durable role record and ignore the notification if it doesn't match."*
- **Owner refinement B**: consistency check uses **set-membership** (forward-compatible with role-set semantics from `gtkb-single-harness-bridge-dispatcher-001`). Today's scalar-role schema is treated as a singleton set; tomorrow's role-set schema makes set-membership the natural form.

## Why Now

Owner directive 2026-05-09: canonical syntax establishment. See `-001` for full context. This REVISED-1 incorporates Codex's substantive findings and owner's two refinements landed during `-002` review.

## Why Not (alternatives reconsidered)

The `-001` "Why Not" section enumerated three rejected paths (status quo prose, per-session override, synonyms). All three remain rejected. Codex's F2 makes a fourth path emerge:

- **Hard-coded recipient handle → mode mapping** (the broken `-001` algorithm): rejected per Codex F2. Cannot survive owner role-switch operations. Replaced with two-step durable-record lookup.

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-002.md` (NO-GO) — three findings F1/F2/F3 addressed by this REVISED-1. Codex's non-blocking notes confirm the strict parser shape, defense-in-depth policy, and Slice-independence sequencing remain correct.
- `bridge/gtkb-single-harness-bridge-dispatcher-001.md` (NEW; awaiting Codex review) — adds role-set semantics to `harness-state/role-assignments.json`. This REVISED-1 is forward-compatible with role-set semantics: the consistency check uses set-membership; today's scalar `role` field is treated as a singleton set.
- `bridge/gtkb-command-surface-003.md`, `-004.md` (architectural plan VERIFIED) — `::` prefix namespace established; `::init` already in the planned command set.
- `.claude/rules/operating-role.md` (canonical) — sole authority for durable role is `harness-state/role-assignments.json`. Harness-local files are legacy pointers (per `harness-state/codex/operating-role.md:1,5,10`). Drives F1 fix.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) — articulates the two-axis bridge automation model.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-008.md` (GO) — establishes the LO startup symmetry contract; the `::init gtkb lo` keyword activates LO-startup-mode behavior coherently.
- Auto-memory `feedback_init_keyword_as_role_symmetric_activator.md` — owner principle that the init-keyword is the role-symmetric activator unifying parity (LO/Prime) and auto-process default.
- `DELIB-S339-2026-05-09-CANONICAL-INIT-KEYWORD-SYNTAX-OWNER-DIRECTIVE` (pending DA harvest) — owner directive establishing the canonical syntax requirement.
- `DELIB-S339-2026-05-09-CONSISTENT-ASSERTION-AUTHORITY-CHOICE` (pending DA harvest) — owner AUQ resolution: keyword derived from durable role, not override.
- `DELIB-S339-2026-05-09-STRICT-IGNORE-ON-MISMATCH-REFINEMENT` (pending DA harvest) — owner refinement: silent drop, not warn-and-fall-back.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state; this proposal does not modify bridge protocol mechanics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specifications to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`. Out-of-repo state unaffected.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets required for the new `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` artifact insertions at implementation time. One narrative-artifact-approval packet for the `.claude/rules/canonical-terminology.md` glossary edit.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — new specs are lifecycle events.

**Specs created by this slice:**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (NEW) — defines the canonical syntax `::init gtkb <mode>`; mode vocabulary `{pb, lo}` (closed); parse rules; no synonyms.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (NEW) — the keyword MUST be derived from the durable role map (`harness-state/role-assignments.json` only; no harness-local override). Override semantics rejected; consistency-assertion semantics REQUIRED. Mismatch → silent drop with audit-log entry; the dispatched session exits without processing the prompt.

## Owner Decisions / Input

This REVISED-1 cites five explicit AskUserQuestion approvals plus standing parity directives. The bridge-compliance-gate hook checks this section is non-empty and substantive.

1. **AUQ 2026-05-09: file thread now** — owner answer "File now (Recommended)". Authorized `-001` filing; carries forward to this REVISED-1.
2. **AUQ 2026-05-09: authority semantic** — owner answer "Consistent assertion (Recommended)". Carried into `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`.
3. **AUQ 2026-05-09: strict-ignore refinement** — owner directive *"the hook should check the durable role record and ignore the notification if it doesn't match."* Drives the worker-side strict-ignore-on-mismatch contract.
4. **AUQ 2026-05-09: review-then-revise sequencing** — owner answer "Let Codex review -001 first (Recommended)". Authorizes this REVISED-1 incorporating Codex findings + owner refinements together.
5. **AUQ 2026-05-09 (prior): parity directive** (recurring) — *"everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable."* Drives the symmetric Claude+Codex hook recognition.

Owner-input dependencies during implementation: 2 formal-artifact-approval packets (SPEC + DCL MemBase insertions); 1 narrative-artifact-approval packet (canonical-terminology.md glossary edit). No pre-impl acknowledgement gate needed: the closed mode vocabulary `{pb, lo}` matches the owner's original directive verbatim.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, no blocking clause gaps.

## Implementation Plan

### IP-1 — Define `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (REVISED FROM -001)

MemBase insertion (`type='specification'`) with formal-artifact-approval packet:

- **Title:** Canonical Init-Keyword Syntax for Machine-Emitted Session Prompts.
- **Body:** Defines syntax as exact regex `^::init gtkb (pb|lo)$` (anchored; lowercase only; single space between tokens). The keyword occupies the entire first line of the prompt; subsequent prompt content is unconstrained. The keyword is emitted by:
  - The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`).
  - GroundTruth-KB single-harness bridge dispatcher (per `bridge/gtkb-single-harness-bridge-dispatcher-001.md` Slice 2 implementation).
  - Future GT-KB routines/automations under `config/agent-control/system-interface-map.toml` that need to invoke a worker session in a specific role.
- Mode vocabulary closed: `pb` (Prime Builder dispatch) and `lo` (Loyal Opposition dispatch). New modes require spec amendment.
- No synonyms; case-sensitive; strict parse. Owner-typed approximations (e.g., `::init gtkb prime`) are not recognized by the hook layer; they fall through to normal session start.

### IP-2 — Define `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (REVISED FROM -001)

MemBase insertion (`type='design_constraint'`) with formal-artifact-approval packet:

- **Constraint (emitter side):** When emitting `::init gtkb <mode>`, the emitter MUST derive `<mode>` from the durable role map at `harness-state/role-assignments.json`. The emitter resolves harness IDs through `harness-state/harness-identities.json`. Harness-local files (`harness-state/<harness>/operating-role.md`) MUST NOT be used as authority sources; they are legacy pointers per `.claude/rules/operating-role.md`.
- **Constraint (receiver side):** The recipient harness's SessionStart hook reads its durable role from `harness-state/role-assignments.json` (resolving its own harness ID via `harness-state/harness-identities.json`). The hook checks whether the keyword's mode is in the receiver's durable role set. **If the keyword's mode is NOT in the role set, the hook MUST silently drop the dispatch:** the SessionStart context indicates a misdirected dispatch; the emitted prompt is NOT treated as a task; the session exits with an audit-log entry to the dispatch-failures log. No warning is surfaced to the owner unless the audit log accumulates repeated misdirections (operational signal of configuration drift).
- **Set-membership semantic:** today's scalar `role` field is treated as a singleton set (`{pb}` if `role="prime-builder"`, `{lo}` if `role="loyal-opposition"`). When `gtkb-single-harness-bridge-dispatcher-001` Slice 1 lands the role-set schema, the check generalizes naturally.
- **Assertions (machine-checkable):** grep `_dispatch_prompt` and any role-resolution helper for the two-step lookup pattern (identities then role-assignments); grep both SessionStart hooks for the set-membership check; grep the audit-log path emitted on misdirected dispatch.

### IP-3 — Modify `_dispatch_prompt` in `scripts/cross_harness_bridge_trigger.py` (REVISED PER F2)

The cross-harness trigger today has two layers that need updating:

1. **`groundtruth-kb/src/groundtruth_kb/bridge/notify.py`** — the work-classifier that maps INDEX entries to recipient handles. Today: NEW/REVISED → `recipient="codex"` (line 40, 42, 45 per Codex F2 evidence); GO/NO-GO → `recipient="prime"` (line 76, 77). This hardcodes "codex is LO; prime is PB."
2. **`scripts/cross_harness_bridge_trigger.py:_harness_command`** (lines 256-275) — maps recipient handle to invocation command. Today: `recipient="codex"` → `["codex", "exec", ...]`; `recipient="prime"` → `["claude", "-p", ...]`.

REVISED-1 algorithm (replacing the broken `-001` `_resolve_dispatch_mode`):

```python
def _resolve_dispatch_target(needed_role_label: str) -> tuple[str, str, str]:
    """Resolve which harness should receive work needing the given durable-role label.

    Args:
        needed_role_label: "loyal-opposition" or "prime-builder" — the role
            the work requires per its bridge-state classification.

    Returns:
        (harness_command_handle, harness_id, canonical_mode):
          - harness_command_handle: str matching the keys in
            harness-state/harness-identities.json (e.g., "claude", "codex").
          - harness_id: durable harness ID (e.g., "A", "B").
          - canonical_mode: "pb" or "lo" — the keyword mode to emit, derived
            from needed_role_label, NOT from any hardcoded recipient handle.

    Fail-closed: raises ValueError with explicit reason on:
      - Unknown role label.
      - Zero harnesses with the role (no-recipient configuration).
      - Multiple harnesses with the role (multi-harness misconfiguration).
    """
    label_to_mode = {"loyal-opposition": "lo", "prime-builder": "pb"}
    if needed_role_label not in label_to_mode:
        raise ValueError(f"unknown role label: {needed_role_label!r}")
    mode = label_to_mode[needed_role_label]

    role_map = _read_role_assignments()  # harness-state/role-assignments.json
    matching = [
        (h_id, h_info)
        for h_id, h_info in role_map["harnesses"].items()
        if h_info["role"] == needed_role_label
    ]
    if len(matching) == 0:
        raise ValueError(f"no harness assigned role {needed_role_label!r}")
    if len(matching) > 1:
        # In single-harness role-set future, the lone harness has both roles;
        # this branch handles future schema. For today's scalar-role schema,
        # multiple matches is misconfiguration; fail closed.
        raise ValueError(
            f"multiple harnesses assigned role {needed_role_label!r}: "
            f"{[h_id for h_id, _ in matching]}"
        )
    harness_id, harness_info = matching[0]
    harness_type = harness_info["harness_type"]  # "claude" or "codex"
    return (harness_type, harness_id, mode)


def _dispatch_prompt(needed_role_label: str, items: list[Any], max_items: int) -> str:
    _, _, mode = _resolve_dispatch_target(needed_role_label)
    canonical_keyword = f"::init gtkb {mode}"
    return "\n".join([canonical_keyword, "", *_existing_dispatch_prompt_lines(items, max_items)])
```

The callsite in `notify.py` and the trigger entry-point change from passing `recipient` (legacy hardcoded handle) to passing `needed_role_label` (the durable role label this work requires). The classifier is unchanged at the bridge-state level (NEW/REVISED still need LO; GO/NO-GO still need PB), but the binding to a concrete harness is deferred to `_resolve_dispatch_target` and uses the durable-role map.

The existing prose role-line in the dispatch prompt is retained as defense-in-depth fallback context.

### IP-4 — Add keyword recognition to SessionStart hooks (Claude + Codex) (REVISED FROM -001)

`.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` — symmetric implementation:

```python
def _bridge_dispatch_keyword_check() -> tuple[bool, str | None]:
    """Returns (should_process, reason).

    should_process is True only when:
      - GTKB_BRIDGE_POLLER_RUN_ID is set (env-var marker; defense-in-depth).
      - First prompt line matches the canonical regex.
      - Mode in the keyword is in the receiver's durable role set.
    """
    run_id = os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID")
    first_line = _read_first_prompt_line()  # via stdin or hook payload context
    if not run_id and not _CANONICAL_KEYWORD_RE.match(first_line):
        return (True, "no marker present; normal startup")  # no canonical-keyword path
    if not run_id:
        return (False, "keyword without env-var; possible spoof; falling through to normal startup")
    if not _CANONICAL_KEYWORD_RE.match(first_line):
        return (False, "env-var without keyword; possible legacy dispatch; processing under env-var-only semantic")
    # Both present.
    keyword_mode = _CANONICAL_KEYWORD_RE.match(first_line).group(1)
    own_harness_id = _resolve_own_harness_id()  # via harness-state/harness-identities.json
    own_role_set = _resolve_own_role_set(own_harness_id)  # via harness-state/role-assignments.json; today returns singleton
    if keyword_mode not in own_role_set:
        # Strict-ignore-on-mismatch per owner refinement.
        _audit_log_misdirected_dispatch(run_id, keyword_mode, own_harness_id, own_role_set)
        return (False, "keyword mode not in durable role set; silent drop")
    return (True, "canonical dispatch authorized")


_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")
```

Behavior table:

| Env-var | Keyword | Mode-in-set | Behavior |
|---|---|---|---|
| absent | absent | n/a | normal startup (no canonical path) |
| absent | present | n/a | warning; fall through to normal startup; do NOT bypass |
| present | absent | n/a | warning; fall through to legacy env-var-only dispatch behavior |
| present | present | yes | dispatch processed; emit auto-dispatch context |
| present | present | no | silent drop; audit log; session exits cleanly |

The audit-log entry on misdirected dispatch is structured: `{run_id, expected_mode_in_set, observed_keyword_mode, own_harness_id, own_role_set, timestamp}` written to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` (existing file; existing schema-compatible).

### IP-5 — Coordinate with `gtkb-single-harness-bridge-dispatcher-001` (NEW)

The single-harness dispatcher thread (NEW; awaiting Codex review) emits the same canonical syntax. Sequencing:

- Both threads land VERIFIED independently.
- The dispatcher thread (Slice 2 follow-on) consumes `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` for its worker-spawn logic.
- The role-set schema landed by the dispatcher thread (Slice 1) makes the set-membership check natural; today's scalar-role check is forward-compatible by treating a scalar as a singleton set.

This thread does not gate on the dispatcher thread, and vice versa. Owner sequencing decides which lands first.

### IP-6 — CS-2 coordination — registry entry (UNCHANGED FROM -001)

When CS-2 (`gtkb-command-surface` next slice) lands, the registry will include a `::init` entry. The entry's `argument_handling` field documents `gtkb {pb|lo}` as the only accepted argument forms (vocabulary updated from `-001`'s `{pb|lo|status}`). This thread does not gate on CS-2.

### IP-7 — Add canonical-terminology entry per specify-on-contact (REVISED FROM -001)

Per `DCL-CONCEPT-ON-CONTACT-001`, touching the load-bearing concept "canonical init keyword" requires a glossary entry. Add to `.claude/rules/canonical-terminology.md` § GT-KB DA Read-Surface and Operational Vocabulary:

- **canonical init keyword** — the `::init gtkb <mode>` syntax emitted as the first line of machine-generated GT-KB session prompts. Mode vocabulary: closed set `{pb, lo}`. Defined by `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`; emission discipline by `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`. Allowed synonyms: none. Receiver-side mismatch → silent drop with audit-log entry.

The glossary edit requires a narrative-artifact-approval packet (per `narrative-artifact-approval-gate.py`).

### IP-8 — Tests (REVISED FROM -001 PER F2)

Five test surfaces. Tests patch BOTH `harness-state/harness-identities.json` and `harness-state/role-assignments.json` fixtures (per Codex F2 directive — assume neither file's content is fixed).

1. `tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — pure parser test:
   - Valid: `::init gtkb pb`, `::init gtkb lo`.
   - Invalid: `::init gtkb prime`, `::init gtkb LO`, `::init gtkb status`, `:: init gtkb pb`, `::init  gtkb pb`, missing prefix, trailing whitespace, etc.
2. `tests/scripts/test_cross_harness_bridge_trigger.py` (extend) — `test_dispatch_target_resolved_via_role_assignments`:
   - Patches identities and role-assignments fixtures.
   - For `needed_role_label="loyal-opposition"` with default fixture (A=LO, B=PB) → resolves to harness "codex"/A, mode "lo"; emits `::init gtkb lo` as first line.
   - Switches fixture (A=PB, B=LO) → resolves to harness "claude"/B, mode "lo"; emits `::init gtkb lo` to claude command, NOT codex command.
   - Asserts the keyword tracks the durable role, not the legacy recipient handle.
3. `tests/scripts/test_cross_harness_bridge_trigger.py` (extend) — `test_dispatch_resolution_fail_closed`:
   - Empty role map → `ValueError` raised.
   - Unknown role label → `ValueError` raised.
   - Multiple harnesses with same role (today's misconfiguration) → `ValueError` raised.
4. `tests/scripts/test_claude_session_start_dispatcher.py` and `test_codex_session_start_dispatcher.py` (extend) — symmetric tests for receiver-side recognition:
   - Both env-var + keyword present + mode in own role set → dispatch processed; auto-dispatch context emitted.
   - Both present, mode NOT in own role set → silent drop; audit-log entry written; no auto-dispatch context emitted; session exits cleanly.
   - Keyword without env-var → warning; normal startup proceeds.
   - Env-var without keyword → warning; legacy env-var-only behavior preserved.
   - Tests patch BOTH identities and role-assignments fixtures and assert the receiver derives its own role from the durable map.
5. `tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — DCL assertions runner:
   - Greps `_resolve_dispatch_target` (or successor) for the two-step durable-record lookup.
   - Greps both SessionStart hooks for the set-membership check.
   - Greps the audit-log path on misdirected-dispatch branch.
   - Asserts NO occurrence of `harness-state/<name>/operating-role.md` as authority source (per F1).

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-CIK-syntax-parser-valid | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (regex) | `test_canonical_init_keyword_syntax::test_valid_forms_accepted` — two valid forms parse. |
| T-CIK-syntax-parser-invalid | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (no synonyms) | `test_canonical_init_keyword_syntax::test_invalid_forms_rejected` — synonyms, case variants, whitespace variants, `status` (now invalid) rejected. |
| T-CIK-trigger-resolves-via-role-map | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 emitter clause | `test_cross_harness_bridge_trigger::test_dispatch_target_resolved_via_role_assignments` — both identity and role fixtures patched; assertion the emitted recipient + keyword track the durable role. |
| T-CIK-trigger-fail-closed | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 emitter (fail-closed) | `test_cross_harness_bridge_trigger::test_dispatch_resolution_fail_closed`. |
| T-CIK-claude-receiver-strict-ignore | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause | `test_claude_session_start_dispatcher::test_session_start_strict_ignore_on_mismatch` — silent drop branch. |
| T-CIK-codex-receiver-strict-ignore | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver (parity) | `test_codex_session_start_dispatcher::test_session_start_strict_ignore_on_mismatch`. |
| T-CIK-claude-defense-in-depth | IP-4 defense-in-depth | `test_claude_session_start_dispatcher::test_session_start_warns_on_keyword_without_env_var` and `test_session_start_warns_on_env_var_without_keyword`. |
| T-CIK-codex-defense-in-depth | IP-4 defense-in-depth (parity) | Codex-side parallels. |
| T-CIK-glossary-entry | IP-7 + DCL-CONCEPT-ON-CONTACT-001 | grep `.claude/rules/canonical-terminology.md` for the new "canonical init keyword" entry. |
| T-CIK-dcl-assertions | IP-2 assertions | `test_canonical_init_keyword_assertions` — greps source for required patterns AND absence of harness-local override authority. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix: harness-local override authority dropped; sole authority is `harness-state/role-assignments.json`.
- [ ] Codex confirms F2 fix: `_resolve_dispatch_target` algorithm uses two-step lookup (identities + role-assignments); fails closed on misconfiguration; tests patch both fixture files.
- [ ] Codex confirms F3 fix: closed mode vocabulary is `{pb, lo}` only (matches owner directive verbatim); no pre-impl acknowledgement gate needed.
- [ ] Codex confirms owner refinement A: receiver-side strict-ignore-on-mismatch (silent drop with audit log) replaces warn-and-fall-back.
- [ ] Codex confirms owner refinement B: set-membership consistency check (forward-compatible with role-set semantics from `gtkb-single-harness-bridge-dispatcher-001`).
- [ ] Codex confirms the defense-in-depth policy (keyword + env-var both required for full bypass) is preserved.
- [ ] Codex confirms IP-5 sequencing (this thread independent of dispatcher thread; coordination via shared SPEC + DCL after both VERIFIED).

## Risk / Rollback

- **Risk:** owner mistypes `::init gtkb pb` in a fresh session expecting bypass behavior. Mitigation: defense-in-depth — keyword alone (without env-var) does NOT bypass startup.
- **Risk:** receiver-side strict-ignore-on-mismatch silently drops a legitimate dispatch due to role-map drift. Mitigation: audit-log entry on every drop allows investigation; doctor check could surface accumulated drift; the dispatch-failures.jsonl is structured for tooling.
- **Risk:** the two-step lookup `(identities → role-assignments)` introduces atomicity concerns if the two files drift between reads. Mitigation: both files are owner-managed and rarely change; operations are local file reads; for correctness, the lookup should read both files sequentially without intervening writes; a post-lookup consistency check (assigned harness's `harness_type` matches the resolved name in identities) catches drift.
- **Risk:** future single-harness role-set semantics (per dispatcher thread) require schema migration of `role-assignments.json`. Mitigation: this REVISED-1's set-membership check is forward-compatible; today's scalar `role` field is treated as a singleton set on read.
- **Risk:** dropping `status` from the vocabulary leaves a future `status` mode unspecified. Mitigation: a future spec amendment can extend the vocabulary; the closed-set discipline ensures the addition is owner-visible.
- **Risk:** the existing role-line prose in `_dispatch_prompt` becomes redundant. Mitigation: keep it; it serves as defense-in-depth for cases where the agent's keyword recognition is suppressed.

**Rollback:**
- Remove the canonical keyword first-line from `_dispatch_prompt`.
- Revert `_resolve_dispatch_target` to legacy `recipient`-handle algorithm (NOT recommended; preserves the F2 bug).
- Remove keyword-recognition logic from both SessionStart hooks.
- Revert IP-7 glossary entry.
- Mark `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` MemBase rows superseded.
- Delete the new test files.

## Files Expected To Change (UNCHANGED FROM -001 except IP-3 algorithm)

- `bridge/gtkb-canonical-init-keyword-syntax-001-003.md` (this REVISED-1 proposal).
- `bridge/INDEX.md` (REVISED entry prepended).
- `scripts/cross_harness_bridge_trigger.py` — IP-3 add `_resolve_dispatch_target` helper; modify `_dispatch_prompt` callsite.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — IP-3 update to pass `needed_role_label` instead of hardcoded `recipient` handle.
- `.claude/hooks/session_start_dispatch.py` — IP-4 keyword recognition + set-membership check + strict-ignore + audit log.
- `.codex/gtkb-hooks/session_start_dispatch.py` — IP-4 Codex parity.
- `.claude/rules/canonical-terminology.md` — IP-7 new glossary entry (requires narrative-artifact-approval packet).
- `tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — IP-8 syntax parser tests.
- `tests/scripts/test_cross_harness_bridge_trigger.py` — IP-8 extend with role-resolution tests + fail-closed tests.
- `tests/scripts/test_claude_session_start_dispatcher.py` — IP-8 extend with strict-ignore + defense-in-depth tests.
- `tests/scripts/test_codex_session_start_dispatcher.py` — IP-8 extend or create with Codex parity.
- `tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — IP-8 DCL assertions runner with absence-of-harness-local-override check.
- MemBase: `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` insertion (with packet); `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` insertion (with packet).

## Open Follow-Ons

1. Future: cadence audit-log review tooling — `dispatch-failures.jsonl` should be surfaced in doctor checks if accumulating misdirected dispatches indicate role-map drift.
2. Future: when `gtkb-single-harness-bridge-dispatcher-001` Slice 1 lands the role-set schema, update the set-membership check from singleton-treatment to native set semantics.
3. Future: CS-2 registry entry for `::init` documenting `gtkb {pb|lo}` as the only argument vocabulary.
4. Future: mode vocabulary expansion — if a need arises (e.g., `wrap` for session-wrap routines), file an amendment thread; do not silently extend.

## Recommended Commit Type

`feat:` — net-new capability surface (canonical init-keyword syntax for machine-emitted GT-KB session prompts; role-resolution algorithm; receiver-side strict-ignore semantics). Net-new spec + DCL artifacts. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm F1 fix: harness-local override authority is genuinely removed; the only authority is `harness-state/role-assignments.json`.
2. Confirm F2 fix: the two-step lookup `(identities → role-assignments)` is correct; the fail-closed behavior on configuration anomalies is appropriate; tests genuinely exercise both fixture files.
3. Confirm F3 fix: closed mode vocabulary `{pb, lo}` matches the owner's verbatim directive; no pre-impl acknowledgement gate needed.
4. Confirm owner refinement A: silent-drop with audit log is the correct strict-ignore implementation (vs. warn-and-fall-back from `-001`).
5. Confirm owner refinement B: set-membership check is forward-compatible with the dispatcher thread's role-set schema.
6. Confirm IP-5 sequencing (this thread independent of the dispatcher thread; both consume the SPEC + DCL after VERIFIED).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
