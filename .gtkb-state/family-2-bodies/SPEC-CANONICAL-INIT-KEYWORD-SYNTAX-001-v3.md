## Canonical init keyword syntax (REVISED at the post-S408 envelope amendment pass; subject mandatory, role optional)

Regex: `^::init (gtkb|application)( (pb|lo))?$`. First-line-only. Subject vocabulary `{gtkb, application}` is mandatory; role vocabulary `{pb, lo}` (pb = Prime Builder, lo = Loyal Opposition) is optional. Six valid forms (four with role + two without). No synonyms. Strict parse.

## Subject token (mandatory)

The subject token informs the agent about the scope of the session envelope (intent-hint per the envelope meta-model in `DELIB-20260637` #1). When `subject = application`, the active application name is resolved from `.claude/session/work-subject.json`, not hardcoded in the keyword (respects the Agent Red separateness boundary per `DELIB-20260637`).

## Role token (optional)

When the role token is PRESENT, behavior is unchanged from v2: it ephemerally overrides the session-stated role per `DCL-SESSION-ROLE-RESOLUTION-001`.

When the role token is ABSENT (`::init gtkb` or `::init application`), the receiver MUST use the durable harness role from `harness-state/harness-registry.json` for all in-session surfaces and MUST NOT write `.claude/session/active-session-role.json`. The session-stated role is unset; durable harness role applies to all surfaces (per `DELIB-20260648` and amended `DCL-SESSION-ROLE-RESOLUTION-001` v_next).

## Receiver-side scope

The keyword is canonical for BOTH machine-emitted dispatch (cross-harness trigger; env-var `GTKB_BRIDGE_POLLER_RUN_ID` present) AND owner-typed interactive declaration (no env-var), in both Claude and Codex SessionStart dispatchers. The syntax is identical across both contexts.

The receiver-side behavior is context-dependent per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (revised at v3). For headless dispatch, the keyword's subject token must match an expected envelope; when the role token is present, it must also match the receiver's durable role set or the dispatch is silently dropped (`STRICT_DROP`). For interactive owner-typed declaration, a present role token establishes the session-stated role for the rest of the session per `DCL-SESSION-ROLE-RESOLUTION-001`; an absent role token leaves the durable role authoritative.

## Owner-typed keyword timing

The owner-typed keyword MAY appear on ANY owner prompt during the session lifetime, not only the first prompt. Mid-session re-typing overrides any prior session-stated role; a re-typed keyword without a role token clears any prior session-stated role.

## First-line constraint

The first-line-only constraint (regex anchors `^...$`) is unchanged; the keyword MUST appear as the entire first line of the owner prompt.

## Migration / compat

Fully additive. Every form that parses at v2 (`::init gtkb pb`, `::init gtkb lo`) continues to parse unchanged at v3. New forms added at v3: `::init application pb`, `::init application lo`, `::init gtkb`, `::init application`. No emitter changes are required for backward compatibility; existing cross-harness trigger emitter output remains valid.

## Revision provenance

This revision (v3) is filed under `DELIB-20260648` (Envelope Init-Keyword Optionality Clarification, 2026-06-04) and is implemented under WI-4291. It refines v2's "asserts, does not set" wording by formalizing subject-token mandatoriness and role-token optionality. The keyword syntax change is the substantive amendment; receiver semantics are co-amended in `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 and `DCL-SESSION-ROLE-RESOLUTION-001` v_next.

## Authority

- `DELIB-20260648` (2026-06-04 owner clarification; subject mandatory, role optional).
- Owner directive S371 (2026-05-29); 6 AskUserQuestion decisions in session-conversation transcript.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (decision); `DCL-SESSION-ROLE-RESOLUTION-001` (deterministic rules); `GOV-SESSION-ROLE-AUTHORITY-001` (governance boundary).
