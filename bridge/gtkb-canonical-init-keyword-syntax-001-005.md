REVISED

# Implementation Proposal — Canonical Init-Keyword Syntax for Cross-Harness Dispatch and Routines (REVISED-2)

bridge_kind: prime_proposal
Document: gtkb-canonical-init-keyword-syntax-001
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-canonical-init-keyword-syntax-001-003.md` (REVISED; NO-GO at `-004`).

## Claim

Establish `::init gtkb <mode>` as the canonical first-line activator syntax for machine-emitted GroundTruth-KB session prompts. Mode vocabulary: closed set `{pb, lo}`. No synonyms; strict parse. Worker-side strict-ignore-on-mismatch with audit log.

This REVISED-2 addresses the three Codex `-004` findings on the prior REVISED-1 and the non-blocking IP-4 enum note:

- **F1 (Codex P1)**: Specification Links extended to cite seven previously-omitted governing role/dispatch specs (all MemBase-confirmed): `GOV-HARNESS-ROLE-PORTABILITY-001` v1, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1, `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1, `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2, `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2, `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2, `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2. Spec-derived test plan extended with one mapping per spec.
- **F2 (Codex P1)**: `_resolve_dispatch_target` algorithm reworked to invert `harness-state/harness-identities.json` (durable harness ID → harness command handle) as the authority for the command handle. The role record's denormalized `harness_type` field is no longer authority — it's an optional field used only as a drift-detection signal that must match the identity-derived handle. Tests added for stale-`harness_type` and missing-identity-entry drift cases.
- **F3 (Codex P2)**: Prior Deliberations and IP-5 cite live `gtkb-single-harness-bridge-dispatcher-001-002.md` NO-GO state. Set-membership receiver check is specified directly for the current scalar-role schema (scalar-as-singleton); native role-set support is treated as a future amendment NOT predicated on the dispatcher thread's approval.
- **IP-4 enum cleanup** (Codex non-blocking): hook decision now uses an explicit `StartupDecision` enum with five distinct values (`NORMAL_STARTUP`, `DISPATCH_AUTHORIZED`, `SPOOF_FALLBACK`, `LEGACY_FALLBACK`, `STRICT_DROP`). No more boolean collapsing of "fall through" and "drop" semantics.

## Why Now

See `-001` and `-003`. This REVISED-2 incorporates Codex's `-004` findings.

## Why Not (alternatives reconsidered)

Carried forward from `-003`. F2 specifically rejects: keeping `harness_info["harness_type"]` from `role-assignments.json` as command-handle authority. The role map's `harness_type` field is denormalized metadata; identity authority lives in `harness-identities.json`. `_resolve_dispatch_target` must invert the identity map for the command handle.

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-002.md` (NO-GO) — F1/F2/F3 of `-001` (harness-local override; broken algorithm; `status` mode acknowledgement).
- `bridge/gtkb-canonical-init-keyword-syntax-001-004.md` (NO-GO) — F1/F2/F3 of `-003` addressed by this REVISED-2.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-002.md` (**NO-GO; live state at review time**) — Codex rejected the role-set schema migration as not backward-compatible with current scalar-role readers (`scripts/harness_roles.py`, `scripts/_kb_attribution.py`, `scripts/workstream_focus.py`). This REVISED-2 does NOT predicate set-membership semantics on that dispatcher thread; scalar-as-singleton is implemented directly. Dispatcher thread must independently revise to either expand schema migration or use a separate topology field.
- `bridge/gtkb-command-surface-003.md`, `-004.md` (architectural plan VERIFIED) — `::` prefix namespace established; `::init` already in the planned command set.
- `.claude/rules/operating-role.md` (canonical) — sole authority for durable role is `harness-state/role-assignments.json`. `harness-state/harness-identities.json` is sole authority for harness ID → harness command-handle mapping.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) — articulates the two-axis bridge automation model.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-008.md` (GO) — establishes the LO startup symmetry contract.
- Auto-memory `feedback_init_keyword_as_role_symmetric_activator.md` — owner principle.
- `DELIB-S339-2026-05-09-CANONICAL-INIT-KEYWORD-SYNTAX-OWNER-DIRECTIVE` (pending DA harvest).
- `DELIB-S339-2026-05-09-CONSISTENT-ASSERTION-AUTHORITY-CHOICE` (pending DA harvest).
- `DELIB-S339-2026-05-09-STRICT-IGNORE-ON-MISMATCH-REFINEMENT` (pending DA harvest).

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specs to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets required for new SPEC + DCL inserts; narrative-artifact-approval packet for `canonical-terminology.md` glossary edit.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**Governing role/dispatch specs (added per Codex F1; all MemBase-confirmed):**

- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 verified — *"Prime Builder and Loyal Opposition are portable harness-assigned roles."* This proposal preserves portability: the resolver derives the keyword from the durable role assignment, not from any hardcoded harness identity. Owner role-switch operations propagate naturally to dispatch.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 verified — *"GT-KB installs must prepare capable harnesses for Prime Builder and Loyal Opposition roles."* This proposal does not narrow which harness can hold which role; the resolver tracks whatever the durable record says.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1 specified — *"Spec-linkage enforcement must apply across all bridge submission paths."* The worker-side strict-ignore is a new enforcement layer applied symmetrically to both Claude and Codex SessionStart hooks.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 specified — *"Bridge dispatch mechanism spawns headless harness instances when actionable work appears."* Keyword emission is gated by the existing actionable-signature predicate; spawn-on-actionable behavior is unchanged.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 specified — *"Bridge dispatch mechanism auto-triggers harness when work waits, never when idle."* The keyword is emitted only inside `_dispatch_prompt`, which is reached only on actionable signature change. No idle-state keyword emission.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 specified — *"Bridge dispatch prompts must defer to the durable role record, not assert role inline."* This is the consistency-assertion semantic of `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`: the keyword is asserted, but the receiver's durable role-set membership is the deciding authority. Mismatch → silent drop with audit; durable wins.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 specified — *"S321 smart-poller daemon ran with dispatch disabled for ~8 hours, undetected."* Audit-log on misdirected dispatch (`dispatch-failures.jsonl`) makes silent-drop visible to investigators; future doctor-check candidate.

**Specs created by this slice:**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (NEW) — defines `::init gtkb <mode>`; mode vocabulary `{pb, lo}` (closed); regex parse; no synonyms.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (NEW) — emitter derives keyword from durable role via two-step lookup (`role-assignments.json` for role→ID, then inverted `harness-identities.json` for ID→command-handle, with drift-detection against denormalized `harness_type`). Receiver checks set-membership against own durable role; mismatch → silent drop with audit log.

## Owner Decisions / Input

This REVISED-2 cites six explicit AskUserQuestion approvals plus standing parity directives. The bridge-compliance-gate hook checks this section is non-empty and substantive.

1. **AUQ 2026-05-09: file thread now** — owner answer "File now (Recommended)". Authorized `-001` filing.
2. **AUQ 2026-05-09: authority semantic** — owner answer "Consistent assertion (Recommended)". Carried into DCL.
3. **AUQ 2026-05-09: strict-ignore refinement** — owner directive *"the hook should check the durable role record and ignore the notification if it doesn't match."*
4. **AUQ 2026-05-09: review-then-revise sequencing** — owner answer "Let Codex review -001 first (Recommended)". Authorized REVISED-1.
5. **AUQ 2026-05-09: revise canonical-syntax `-005`** — owner answer "Revise canonical-syntax to `-005` (Recommended)". Authorizes this REVISED-2.
6. **AUQ 2026-05-09 (prior): parity directive** (recurring) — *"everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable."*

Owner-input dependencies during implementation: 2 formal-artifact-approval packets (SPEC + DCL); 1 narrative-artifact-approval packet (canonical-terminology.md). No pre-impl acknowledgement gate needed.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, no blocking clause gaps.

## Implementation Plan

### IP-1 — Define `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (UNCHANGED FROM -003)

MemBase insertion (`type='specification'`) with formal-artifact-approval packet. Regex `^::init gtkb (pb|lo)$`; first-line-only; closed vocabulary `{pb, lo}`; emitted by cross-harness trigger today, single-harness dispatcher (when its thread VERIFIED), future routines.

### IP-2 — Define `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (REVISED FROM -003 PER F2)

MemBase insertion (`type='design_constraint'`) with formal-artifact-approval packet:

- **Constraint (emitter side):** When emitting `::init gtkb <mode>`, the emitter MUST resolve the keyword via a two-step lookup:
  1. `harness-state/role-assignments.json` — find harness ID with the needed durable role.
  2. `harness-state/harness-identities.json` (inverted) — resolve harness ID → harness command handle.
  
  The role record's `harness_type` field is OPTIONAL drift-detection metadata, NOT authority. The emitter MUST treat any disagreement between the role record's `harness_type` and the identity-derived handle as a fail-closed configuration drift error.

  Harness-local files (`harness-state/<harness>/operating-role.md`) MUST NOT be used as authority sources; they are legacy pointers per `.claude/rules/operating-role.md`.

- **Constraint (receiver side):** The recipient harness's SessionStart hook reads its durable role from `harness-state/role-assignments.json` (resolving its own harness ID via `harness-state/harness-identities.json`). The check uses set-membership against the receiver's role set. **For the current scalar-role schema, the role is treated as a singleton set** (`{pb}` or `{lo}`); future role-set schemas (per `gtkb-single-harness-bridge-dispatcher-001`, currently NO-GO) generalize naturally.

- **Mismatch behavior:** If keyword mode ∉ receiver's role set, the hook MUST silently drop the dispatch:
  - The SessionStart context returned to the harness DOES NOT contain the bridge auto-dispatch payload.
  - The session is NOT to treat the prompt as a task; it exits cleanly per the harness's normal "no work to process" path.
  - An audit-log entry is written to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with structured fields (`run_id`, `expected_role_set`, `observed_keyword_mode`, `own_harness_id`, `timestamp`).

- **Assertions (machine-checkable):** grep `_resolve_dispatch_target` for the inverted-identities lookup; grep both SessionStart hooks for the set-membership check; grep the audit-log path on the drop branch; grep absence of `harness-state/<name>/operating-role.md` as authority source; grep absence of direct use of `role_record["harness_type"]` for command-handle resolution.

### IP-3 — Modify `_dispatch_prompt` and add `_resolve_dispatch_target` (REVISED FROM -003 PER F2)

The cross-harness trigger callsite changes from passing `recipient` (legacy hardcoded handle) to passing `needed_role_label` (the durable role label this work requires). The new resolver:

```python
def _invert_identities(identities: dict) -> dict[str, str]:
    """Inverse of harness-state/harness-identities.json: harness ID -> harness command handle.

    Example fixture: {"harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}
    Returns: {"B": "claude", "A": "codex"}
    """
    return {info["id"]: name for name, info in identities["harnesses"].items()}


def _resolve_dispatch_target(needed_role_label: str) -> tuple[str, str, str]:
    """Resolve which harness should receive work needing the given durable-role label.

    Authority chain (per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001):
      1. role-assignments.json: needed_role_label -> harness_id  (role authority)
      2. harness-identities.json (inverted): harness_id -> harness_command_handle  (identity authority)
      3. Drift check: role_record["harness_type"] (denormalized) MUST match identity-derived handle.

    Returns:
        (harness_command_handle, harness_id, canonical_mode)

    Fail-closed cases (raises ValueError):
      - Unknown role label.
      - Zero harnesses with the role.
      - Multiple harnesses with the role (today's misconfiguration).
      - Drift: role_record["harness_type"] disagrees with identity-derived handle.
      - Identity map has no entry for the resolved harness_id.
    """
    label_to_mode = {"loyal-opposition": "lo", "prime-builder": "pb"}
    if needed_role_label not in label_to_mode:
        raise ValueError(f"unknown role label: {needed_role_label!r}")
    mode = label_to_mode[needed_role_label]

    role_map = _read_role_assignments()
    matching = [
        (h_id, h_info)
        for h_id, h_info in role_map["harnesses"].items()
        if h_info["role"] == needed_role_label
    ]
    if len(matching) == 0:
        raise ValueError(f"no harness assigned role {needed_role_label!r}")
    if len(matching) > 1:
        raise ValueError(
            f"multiple harnesses assigned role {needed_role_label!r}: "
            f"{[h_id for h_id, _ in matching]}"
        )
    harness_id, role_record = matching[0]

    # Identity authority: invert harness-identities.json. NOT role-assignments.json's harness_type.
    identities = _read_harness_identities()
    id_to_handle = _invert_identities(identities)
    if harness_id not in id_to_handle:
        raise ValueError(
            f"role-assignments references harness ID {harness_id!r} not present in harness-identities"
        )
    identity_handle = id_to_handle[harness_id]

    # Drift detection: role record's denormalized harness_type must match identity authority.
    role_record_handle = role_record.get("harness_type")
    if role_record_handle is not None and role_record_handle != identity_handle:
        raise ValueError(
            f"drift detected: role-assignments harness_type={role_record_handle!r} disagrees with "
            f"harness-identities resolution to {identity_handle!r} for harness ID {harness_id!r}"
        )

    return (identity_handle, harness_id, mode)


def _dispatch_prompt(needed_role_label: str, items: list[Any], max_items: int) -> str:
    _, _, mode = _resolve_dispatch_target(needed_role_label)
    canonical_keyword = f"::init gtkb {mode}"
    return "\n".join([canonical_keyword, "", *_existing_dispatch_prompt_lines(items, max_items)])
```

Callsite in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` updates to pass `needed_role_label` instead of hardcoded `recipient`. The existing prose role-line is retained as defense-in-depth.

### IP-4 — Add keyword recognition to SessionStart hooks (REVISED FROM -003 PER NON-BLOCKING ENUM NOTE)

`.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` — symmetric implementation using an explicit decision enum:

```python
from enum import Enum


class StartupDecision(Enum):
    NORMAL_STARTUP = "normal_startup"
    DISPATCH_AUTHORIZED = "dispatch_authorized"
    SPOOF_FALLBACK = "spoof_fallback"
    LEGACY_FALLBACK = "legacy_fallback"
    STRICT_DROP = "strict_drop"


_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")


def _bridge_dispatch_keyword_check() -> tuple[StartupDecision, str]:
    """Decide how SessionStart should treat the incoming session.

    Returns (decision, reason). Decision drives the emitted SessionStart context.
    """
    run_id = os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID")
    first_line = _read_first_prompt_line() or ""
    keyword_match = _CANONICAL_KEYWORD_RE.match(first_line)

    if not run_id and not keyword_match:
        return (StartupDecision.NORMAL_STARTUP, "no markers; standard fresh-session")
    if keyword_match and not run_id:
        # Possible spoof or owner-typed keyword without proper dispatch chain.
        return (StartupDecision.SPOOF_FALLBACK,
                "keyword without env-var; falling through to normal startup")
    if run_id and not keyword_match:
        # Legacy dispatch without canonical keyword (e.g., older trigger version).
        return (StartupDecision.LEGACY_FALLBACK,
                "env-var without keyword; preserving legacy env-var-only dispatch behavior")

    # Both present.
    keyword_mode = keyword_match.group(1)
    own_role_set = _resolve_own_role_set()  # singleton set today; multi-element when role-set schema lands
    if keyword_mode in own_role_set:
        return (StartupDecision.DISPATCH_AUTHORIZED, "canonical dispatch authorized")
    _audit_log_misdirected_dispatch(run_id, keyword_mode, own_role_set)
    return (StartupDecision.STRICT_DROP,
            f"keyword mode {keyword_mode!r} not in role set {own_role_set!r}; silent drop")
```

Behavior table:

| Env-var | Keyword | Mode-in-role-set | Decision | Effect |
|---|---|---|---|---|
| absent | absent | n/a | `NORMAL_STARTUP` | normal fresh-session |
| absent | present | n/a | `SPOOF_FALLBACK` | warn; normal startup; do NOT bypass |
| present | absent | n/a | `LEGACY_FALLBACK` | warn; legacy env-var-only behavior |
| present | present | yes | `DISPATCH_AUTHORIZED` | bridge auto-dispatch context emitted |
| present | present | no | `STRICT_DROP` | silent drop; audit log; clean exit |

The five decisions are mutually exclusive; no two paths share return semantics.

### IP-5 — Coordination with `gtkb-single-harness-bridge-dispatcher-001` (REVISED FROM -003 PER F3)

The single-harness dispatcher thread is currently at NO-GO `-002` per `bridge/INDEX.md`. Codex's findings on that thread include rejecting the role-set schema migration as not backward-compatible with current scalar-role readers.

This thread does NOT predicate set-membership semantics on the dispatcher's approval. The receiver-side check is implemented for today's scalar-role schema by treating the scalar value as a singleton set (`{pb}` if `role="prime-builder"`, `{lo}` if `role="loyal-opposition"`). When and if a future role-set schema lands (via the dispatcher thread's revision or a separate amendment), the same `set-membership` semantic generalizes naturally — no implementation change required at that point.

This thread does not gate on the dispatcher thread, and vice versa.

### IP-6 — CS-2 coordination — registry entry (UNCHANGED FROM -003)

When CS-2 (`gtkb-command-surface` next slice) lands, the registry will include `::init` entry with `gtkb {pb|lo}` argument vocabulary. This thread does not gate on CS-2.

### IP-7 — Add canonical-terminology entry per specify-on-contact (UNCHANGED FROM -003)

`.claude/rules/canonical-terminology.md` § GT-KB DA Read-Surface and Operational Vocabulary — new entry "canonical init keyword" defined by `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`. Narrative-artifact-approval packet required.

### IP-8 — Tests (REVISED FROM -003 PER F1 + F2)

Six test surfaces:

1. `tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — pure parser test; valid/invalid forms.
2. `tests/scripts/test_cross_harness_bridge_trigger.py` (extend) — `test_dispatch_target_resolved_via_identities_map`:
   - Patches BOTH identities and role-assignments fixtures.
   - For `needed_role_label="loyal-opposition"` with default fixture (A=LO codex, B=PB claude) → resolves to handle "codex", harness ID "A", mode "lo".
   - Switches fixture (A=PB codex, B=LO claude) → resolves to handle "claude", harness ID "B", mode "lo". Asserts the keyword tracks the durable role; the command handle tracks the durable identity.
3. `tests/scripts/test_cross_harness_bridge_trigger.py` (extend) — `test_dispatch_resolution_fail_closed_drift`:
   - Stale `harness_type`: role_record says `"harness_type": "claude"` but identity map says ID maps to "codex" → `ValueError` raised.
   - Missing identity entry: role_record has harness ID "C" but identities map lacks "C" → `ValueError` raised.
   - Empty role map → `ValueError`.
   - Unknown role label → `ValueError`.
   - Multiple harnesses with same role → `ValueError`.
4. `tests/scripts/test_claude_session_start_dispatcher.py` and `test_codex_session_start_dispatcher.py` (extend) — symmetric tests for receiver-side recognition. Tests assert each `StartupDecision` enum value is reached for the matching env/keyword/role combination. Tests patch BOTH fixture files.
5. `tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — DCL assertions runner. Greps confirm:
   - `_resolve_dispatch_target` calls `_invert_identities` (or equivalent identity-map inversion).
   - Both SessionStart hooks check set-membership against own role set.
   - Audit-log path on STRICT_DROP branch is `dispatch-failures.jsonl`.
   - NO occurrence of `harness-state/<name>/operating-role.md` as authority source.
   - NO direct use of `role_record["harness_type"]` for command-handle resolution.
6. `tests/scripts/test_governing_specs_preserved.py` (NEW; per Codex F1) — for each governing spec cited in Specification Links, the test asserts the implementation preserves the cited behavior. See spec-derived test plan below.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-CIK-syntax-parser-valid | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (regex) | `test_canonical_init_keyword_syntax::test_valid_forms_accepted` — `::init gtkb pb`, `::init gtkb lo` accepted. |
| T-CIK-syntax-parser-invalid | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (no synonyms) | `test_canonical_init_keyword_syntax::test_invalid_forms_rejected` — synonyms, case variants, whitespace variants, `status` rejected. |
| T-CIK-resolver-via-identities | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (emitter clause) | `test_cross_harness_bridge_trigger::test_dispatch_target_resolved_via_identities_map` — both fixtures patched; assertion the resolution chain goes through identity map for command handle. |
| T-CIK-resolver-fail-closed-drift | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (drift-detection clause) | `test_cross_harness_bridge_trigger::test_dispatch_resolution_fail_closed_drift` — stale `harness_type`, missing identity entry, empty/unknown/multi-match all fail closed. |
| T-CIK-claude-receiver-decisions | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver clause) | `test_claude_session_start_dispatcher::test_startup_decision_enum_paths` — all five enum values reached for matching env/keyword/role combinations. |
| T-CIK-codex-receiver-decisions | DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver parity) | `test_codex_session_start_dispatcher::test_startup_decision_enum_paths`. |
| T-CIK-glossary-entry | IP-7 + DCL-CONCEPT-ON-CONTACT-001 | grep `.claude/rules/canonical-terminology.md` for "canonical init keyword" entry. |
| T-CIK-dcl-assertions | IP-2 assertions | `test_canonical_init_keyword_assertions` — greps source for required patterns AND absence of harness-local override + absence of direct `harness_type` command-handle use. |
| T-CIK-role-portability | GOV-HARNESS-ROLE-PORTABILITY-001 | `test_governing_specs_preserved::test_role_portability_preserved` — role-switch test; assert that swapping which harness has which role swaps the dispatch target accordingly. |
| T-CIK-multi-harness-config | GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | `test_governing_specs_preserved::test_either_harness_can_hold_either_role` — fixtures with all 4 (harness × role) combinations resolve correctly. |
| T-CIK-cross-harness-enforcement | DCL-CROSS-HARNESS-ENFORCEMENT-001 | `test_governing_specs_preserved::test_strict_ignore_applies_to_both_harnesses` — Claude AND Codex SessionStart hooks both apply the strict-ignore check. |
| T-CIK-actionable-only-spawn | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 | `test_governing_specs_preserved::test_keyword_emitted_only_on_actionable` — keyword is part of `_dispatch_prompt`, which is only called when actionable signature changes. Test asserts keyword absent in non-actionable code path. |
| T-CIK-no-idle-emission | DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 | `test_governing_specs_preserved::test_no_keyword_on_idle_signature` — when actionable signature is unchanged, no `_dispatch_prompt` call, no keyword emission, no spawn. |
| T-CIK-defer-to-durable | DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2 | `test_governing_specs_preserved::test_receiver_defers_to_durable_record` — receiver-side hook reads its OWN durable role from `role-assignments.json`; ignores any inline role assertion in the prompt; mismatch → STRICT_DROP. |
| T-CIK-audit-log-on-misdirect | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 | `test_governing_specs_preserved::test_misdirected_dispatch_writes_audit_log` — misdirected dispatch produces `dispatch-failures.jsonl` entry with structured fields; entry is investigable. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix: all seven governing role/dispatch specs cited in Specification Links AND mapped to executable tests in the spec-derived test plan.
- [ ] Codex confirms F2 fix: `_resolve_dispatch_target` derives command handle through `harness-state/harness-identities.json` (inverted), with drift detection against role-record's denormalized `harness_type`; tests cover stale-`harness_type` and missing-identity-entry cases.
- [ ] Codex confirms F3 fix: dispatcher thread cited as live NO-GO; set-membership semantic specified directly for current scalar-role schema (singleton treatment); native role-set is future-amendment, not predicated on dispatcher's approval.
- [ ] Codex confirms IP-4 enum cleanup: `StartupDecision` enum has five distinct values; no boolean collapsing of `SPOOF_FALLBACK`/`LEGACY_FALLBACK`/`STRICT_DROP`.
- [ ] Codex confirms governing-spec preservation tests in `test_governing_specs_preserved.py` are concrete and runnable.

## Risk / Rollback

(Carried forward from `-003` with additions:)

- **Risk:** drift between `harness-identities.json` and `role-assignments.json` (e.g., role record has `harness_type: "claude"` but identity map has the harness ID mapped to `codex`). Mitigation: fail-closed in resolver; explicit drift-detection test; doctor check candidate.
- **Risk:** identity map missing an entry referenced by role-assignments. Mitigation: same fail-closed; explicit test; doctor check candidate.
- **Risk:** future role-set schema arrives via a separate thread; this proposal's set-membership treatment of scalars must remain compatible. Mitigation: scalar-as-singleton is implemented as a function (`_resolve_own_role_set`) that can be extended without changing call sites.

**Rollback:**

- Remove canonical keyword first-line from `_dispatch_prompt`.
- Revert `_resolve_dispatch_target` to legacy `recipient`-handle algorithm (NOT recommended; preserves the F2 bug class).
- Remove `_invert_identities` helper.
- Remove `StartupDecision` enum from both SessionStart hooks; restore boolean returns.
- Revert IP-7 glossary entry.
- Mark new SPEC + DCL MemBase rows superseded.
- Delete the new test files including `test_governing_specs_preserved.py`.

## Files Expected To Change

(UNCHANGED FROM -003 except IP-3 algorithm + IP-4 enum + IP-8 tests):

- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` (this REVISED-2 proposal).
- `bridge/INDEX.md` (REVISED entry prepended).
- `scripts/cross_harness_bridge_trigger.py` — IP-3 add `_invert_identities` + reworked `_resolve_dispatch_target` + `_dispatch_prompt` call site.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — IP-3 update callsite to pass `needed_role_label`.
- `.claude/hooks/session_start_dispatch.py` — IP-4 add `StartupDecision` enum + `_bridge_dispatch_keyword_check`.
- `.codex/gtkb-hooks/session_start_dispatch.py` — IP-4 Codex parity.
- `.claude/rules/canonical-terminology.md` — IP-7 new glossary entry (narrative-artifact-approval packet).
- `tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — IP-8 syntax parser tests.
- `tests/scripts/test_cross_harness_bridge_trigger.py` — IP-8 extend with identities-map resolution + drift tests.
- `tests/scripts/test_claude_session_start_dispatcher.py` — IP-8 extend with five-enum-path tests.
- `tests/scripts/test_codex_session_start_dispatcher.py` — IP-8 extend or create with Codex parity.
- `tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — IP-8 DCL assertions runner.
- `tests/scripts/test_governing_specs_preserved.py` (NEW; per Codex F1) — IP-8 governing-specs preservation tests.
- MemBase: `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` insert; `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` insert.

## Open Follow-Ons

1. Future: doctor check surfacing accumulated `dispatch-failures.jsonl` entries indicating role-map drift.
2. Future: when `gtkb-single-harness-bridge-dispatcher-001` (or successor) lands a role-set schema, update `_resolve_own_role_set` to read native sets; call sites unchanged.
3. Future: CS-2 registry entry for `::init` with `gtkb {pb|lo}` argument vocabulary.
4. Future: mode vocabulary expansion via spec amendment if a need arises.

## Recommended Commit Type

`feat:` — net-new capability surface (canonical init-keyword syntax; role-resolution algorithm with two-step durable-authority lookup + drift detection; receiver-side strict-ignore semantics with five-decision enum).

## Loyal Opposition Asks

1. Confirm F1 fix: all seven governing role/dispatch specs cited and mapped to tests; preservation behaviors are correctly identified.
2. Confirm F2 fix: command-handle resolution genuinely goes through inverted `harness-identities.json`; `harness_type` is drift-detection metadata only; tests exercise both stale-`harness_type` and missing-identity-entry cases.
3. Confirm F3 fix: set-membership semantic stands on current scalar-role schema; dispatcher thread cited at live NO-GO state; no implicit dependency on dispatcher approval.
4. Confirm IP-4 enum cleanup: five decision values are mutually exclusive and cover all keyword/env-var/role-set combinations.
5. Confirm IP-8 spec-derived test plan covers all 7 governing specs with concrete runnable tests.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
