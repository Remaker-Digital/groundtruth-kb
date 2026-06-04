## Constraint (REVISED at the post-S408 envelope amendment pass; role-token optionality)

Emitter authority is REVISED: the cross-harness event-driven trigger MUST emit the canonical init keyword (subject token always present) for the dispatched-to harness's durable role when dispatching headless work. The emitter MAY omit the role token when the dispatched harness's role assignment can be inferred from durable state; the role token MUST be emitted when the emitter intends to assert a specific role for the receiver (override semantics).

Receiver authority is REVISED to deterministically fork on dispatch context AND role-token presence. The receiver-side decision table is:

| env-var `GTKB_BRIDGE_POLLER_RUN_ID` | Init keyword present | Role token in keyword | Subject token in expected set | Role in durable set | Receiver decision | Effect |
|---|---|---|---|---|---|---|
| absent | absent | n/a | n/a | n/a | NORMAL_STARTUP | render fresh-session disclosure for durable role (per `DCL-SESSION-ROLE-RESOLUTION-001`) |
| absent | present | yes | yes | n/a | INTERACTIVE_OVERRIDE_AUTHORIZED | record session-stated role marker at `.claude/session/active-session-role.json`; render disclosure for keyword role |
| absent | present | no | yes | n/a | INTERACTIVE_SUBJECT_DECLARED | record subject context; DO NOT write `.claude/session/active-session-role.json`; render disclosure for durable role |
| present | absent | n/a | n/a | n/a | LEGACY_FALLBACK | env-var-only dispatch (preserved for backward compatibility) |
| present | present | yes | yes | yes | DISPATCH_AUTHORIZED | bridge auto-dispatch context emitted; render for keyword role |
| present | present | yes | yes | no | STRICT_DROP | silent drop; audit log; clean exit |
| present | present | no | yes | n/a | DISPATCH_AUTHORIZED_SUBJECT_ONLY | bridge auto-dispatch context emitted; render for durable role |
| any | present | any | no | n/a | STRICT_DROP | unrecognized subject; silent drop; audit log; clean exit |

## SPOOF_FALLBACK replacement (carried forward from v2)

The pre-v2 `SPOOF_FALLBACK` decision (keyword without env-var falling through to normal startup) was replaced by `INTERACTIVE_OVERRIDE_AUTHORIZED` in v2. The v3 amendment further refines the interactive (env-var absent) rows by distinguishing keyword-with-role from keyword-without-role; the former writes the active-session-role marker, the latter does NOT.

## Active-session-role marker write rule (v3 addition)

The receiver MUST write `.claude/session/active-session-role.json` ONLY when the `INTERACTIVE_OVERRIDE_AUTHORIZED` decision fires (env-var absent AND keyword present AND role token present AND subject recognized). In all other rows (including `INTERACTIVE_SUBJECT_DECLARED`), the receiver MUST NOT write the marker; the durable harness role from `harness-state/harness-registry.json` is authoritative.

## Receiver-side audit logging

- `STRICT_DROP` continues to append a `misdirected_dispatch_strict_drop` record (or `unrecognized_subject_strict_drop` for the unrecognized-subject row) to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` (unchanged) from either dispatcher.
- `INTERACTIVE_OVERRIDE_AUTHORIZED` records a `session_role_override` record to a new ephemeral log at `.gtkb-state/sessions/<session-id>/role-overrides.jsonl` from either dispatcher.
- `INTERACTIVE_SUBJECT_DECLARED` (new at v3) records a `session_subject_declared` record to the same ephemeral log; the implementation slice will refine the path.

## Headless safety preservation

The headless rows of the decision table (env-var-present) preserve the load-bearing safety property: `STRICT_DROP` continues to fire when env-var is present AND keyword is present AND keyword's subject is unrecognized OR (role token is present AND role is NOT in the receiver's durable role set). The `DISPATCH_AUTHORIZED_SUBJECT_ONLY` row is new at v3 and applies only when the role token is absent; in that case the receiver falls back to its durable role authority.

## Revision provenance

This revision (v3) is filed under `DELIB-20260648` (Envelope Init-Keyword Optionality Clarification, 2026-06-04) and is implemented under WI-4291. It introduces the receiver-side role-token-presence fork; the headless dispatch behavior under role-token-present rows is unchanged from v2.

## Authority

- `DELIB-20260648` (2026-06-04 owner clarification; subject mandatory, role optional; receiver behavior when role token absent).
- Owner directive S371 (2026-05-29); 6 AskUserQuestion decisions in session-conversation transcript.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (decision); `DCL-SESSION-ROLE-RESOLUTION-001` (deterministic rules; co-amended at v_next); `GOV-SESSION-ROLE-AUTHORITY-001` (governance boundary); `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (revised at v3; keyword syntax).
