NEW

author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code; interactive; Prime Builder; envelope closeout
author_metadata_source: prime-builder session; inline author metadata

# Implementation Proposal — LO File-Safety Write-Gate: Resolve Role via Session Envelope (WI-4371)

bridge_kind: prime_proposal
Document: gtkb-lo-file-safety-gate-envelope-role-resolution
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC

Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001
Work Item: WI-4371
Recommended commit type: fix

target_paths: [".claude/hooks/lo-file-safety-gate.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py"]

implementation_scope: hook_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Make the LO file-safety write-gate honor the **session/dispatch envelope role**,
consistent with the owner's model (`DELIB-20260884`): a harness's durable role
assignment is the DEFAULT used only when the envelope specifies no role; the
envelope role is authoritative.

`.claude/hooks/lo-file-safety-gate.py::_is_lo_enforced` (line ~222) currently
resolves the role from the **durable** harness assignment only
(`load_role_assignments` + `is_loyal_opposition`; docstring: "Return True only
when durable role state resolves to LO without Prime"). It never consults the
session-role marker. This is the single role-gated surface NOT migrated by the
all-VERIFIED 10-slice `gtkb-interactive-session-role-override` project (slices
1–10). Symptom: a session operating as Prime via `::init gtkb pb` / the session
envelope has scratch writes blocked because the gate enforces LO read-only off
the durable LO assignment, ignoring the asserted Prime role.

The fix routes `_is_lo_enforced` through
`scripts/session_role_resolution.py::resolve_interactive_session_role`
(marker > durable), gating on the **resolved** role. This is identical to how
the 9 sibling surfaces were migrated and **inherits the resolver's session-id
spoof-resistance**: the marker is honored only when its `session_id` verifies
against the current session; on mismatch/stale/absent marker the resolver
returns the durable role (outcomes `durable_marker_*`). The gate's existing
fail-open behavior on missing/malformed role state is preserved.

## PAUTH Coverage Note

`PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001`
is a bounded authorization created for this exact work via `gt projects
authorize` (owner-decision `DELIB-20260884`): active, tied to
`PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`, explicitly
`--include-work-item WI-4371`, with linked specs
`DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`,
and allowed mutation classes `hook_scripts` + `tests` — exactly this change.
WI-4371 was admitted to the project via `gt projects add-item` (active member).
The authorization is bounded to source/test mutation only; it does not authorize
narrative or rule edits, and the implementation-start packet must still be minted
from this thread's GO.

## Proposed Change (exact)

In `.claude/hooks/lo-file-safety-gate.py`:

- Add an import of `resolve_interactive_session_role` (alongside the existing
  guarded `harness_roles` imports; same fail-open `None` sentinel pattern if the
  import is unavailable).
- Refactor `_is_lo_enforced(root, payload)` to:
  1. Resolve `harness_name` as today (env/payload, with the existing
     claude/codex defaulting).
  2. Resolve the **current session id** from `payload.get("session_id")` /
     `os.environ.get("CLAUDE_CODE_SESSION_ID")` (None when unavailable).
  3. Call `resolve_interactive_session_role(root, harness_name,
     current_session_id=<sid>)` → `(resolved_role, outcome)`.
  4. Return `resolved_role == "loyal-opposition"` (enforce read-only) — i.e.,
     enforce LO file-safety iff the RESOLVED role is LO. A resolved Prime role
     (whether from a verified marker or from durable) returns False (writes
     allowed).
  5. Preserve fail-open: if the resolver import/sentinel is unavailable or the
     resolver raises, return False (current behavior), so startup repairs and
     fresh clones are never hard-blocked.

The durable-only `load_role_assignments`/`is_loyal_opposition` path is retained
internally only as the resolver's own fallback (the resolver composes the
durable role); the hook no longer calls it directly for the authoritative
decision.

Codex parity: `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` pipes into
this canonical hook, so the behavior change propagates without a separate Codex
edit (confirmed: the adapter holds no independent role-resolution logic).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the deterministic marker>durable resolution table this fix adopts.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable role is the fallback when no session role is declared; the authority split the fix honors.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — the decision that session-stated role takes precedence for interactive surfaces; this closes the one unmigrated surface (the write-gate) the ADR's SPOOF_FALLBACK context flagged.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — routing_override supersedes the role default; the envelope-authoritative principle.
- `GOV-STANDING-BACKLOG-001` — WI-4371 standing-backlog governance.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.

### Requirement Sufficiency

Existing requirements sufficient. The governing requirements are
`DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`,
plus the owner decision `DELIB-20260884`. No new or revised requirement is
needed; the fix migrates the one unmigrated surface to the already-specified
resolution model.

## Spec-Derived Verification Plan

| Spec / Acceptance Item | Test | Expected |
|---|---|---|
| `DCL-SESSION-ROLE-RESOLUTION-001` — resolved role = marker when verified | `test_is_lo_enforced_false_when_verified_pb_marker` (marker PB + matching session_id) | `_is_lo_enforced` → False (writes allowed) |
| `DCL-SESSION-ROLE-RESOLUTION-001` — marker honored only when session-id verifies | `test_is_lo_enforced_true_when_unmatched_pb_marker_durable_lo` (marker PB, mismatched session_id, durable LO) | `_is_lo_enforced` → True (durable fallback) |
| `GOV-SESSION-ROLE-AUTHORITY-001` — durable fallback when no marker | `test_is_lo_enforced_true_when_no_marker_durable_lo` | `_is_lo_enforced` → True |
| Durable PB with no marker still allows writes | `test_is_lo_enforced_false_when_no_marker_durable_pb` | `_is_lo_enforced` → False |
| Fail-open on missing/malformed role state | `test_is_lo_enforced_false_when_role_state_unavailable` | `_is_lo_enforced` → False (fail-open preserved) |
| Full hook regression | `pytest platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py` + existing `platform_tests/test_loyal_opposition_file_safety_clarification.py` | all pass |
| Lint + format | `ruff check` + `ruff format --check` on the 2 changed files | clean |

## Owner Decisions / Input

The proposal depends on owner approval; the authorizing evidence:

- **`DELIB-20260884`** (`source_type=owner_conversation`, `outcome=owner_decision`,
  2026-06-05) — owner Mike chose "Migrate to resolver" (Option A of three: A
  migrate-to-resolver [CHOSEN]; B keep-durable-for-write-gate-only; C track-only)
  via `AskUserQuestion`. The AUQ answer is mechanically recorded in
  `memory/pending-owner-decisions.md` (`detected_via: ask_user_question`). This
  same DELIB is the `--owner-decision` basis of the bounded PAUTH above.
- The decision was made after the owner clarified (2026-06-05) that the harness
  role assignment is a default used only when the envelope specifies no role;
  the envelope role is authoritative. That clarification is the basis for
  WI-4371 and this proposal.

No additional owner decision is required for Loyal Opposition to review this
proposal. This is a behavior change to a security write-gate; LO review is
expected to scrutinize the spoof-resistance (session-id verification) and the
fail-open preservation.

## Prior Deliberations

- `DELIB-20260884` — owner decision to migrate the write-gate to the resolver (the basis for this proposal and the bounded PAUTH).
- The `gtkb-interactive-session-role-override-slice-1..10` thread family (all VERIFIED) — the precedent migrations of the 9 sibling surfaces to the marker>durable resolver. This proposal applies the identical pattern to the one missed surface.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` deliberations — the decision establishing session-stated-role precedence for interactive surfaces.
- No retrieved deliberation rejects routing the write-gate through the resolver; the spoof-resistance concern (the ADR's SPOOF_FALLBACK context) is satisfied by the resolver's session-id verification.

## Risk and Rollback

**Risk after merge:** Moderate — this changes write-enforcement behavior. The
spoof-resistance is preserved by the resolver's session-id verification (a
session cannot claim Prime write-authority off a marker it did not write).
Fail-open on missing/malformed state is preserved, so startup/fresh-clone paths
are unaffected. The Codex parity path inherits the change via the existing
bash-adapter. The primary residual risk is a regression in the resolver
integration; the test matrix above covers the four resolution branches plus
fail-open.

**Rollback:** Revert the single hook commit. The durable-only `_is_lo_enforced`
behavior is restored; the resolver and all sibling surfaces are unaffected.

## Notes for Loyal Opposition

The fix is a targeted refactor of one function (`_is_lo_enforced`) plus a new
focused test file. It closes the last unmigrated role-gated surface so the
envelope-authoritative model (owner-stated, ADR-decided, 9/10-implemented)
applies uniformly. Please scrutinize: (1) the session-id passed to the resolver
is the CURRENT session's id (not a marker-supplied one), so spoofing is
resisted; (2) fail-open is preserved on every error/missing-state branch; (3)
the Codex bash-adapter genuinely holds no independent role logic (so no separate
Codex edit is needed). The implementation phase will acquire the
implementation-start packet from this thread's GO before editing the hook.

## Recommended Commit Type

`fix:` — repairs role-resolution behavior in the write-gate (writes were wrongly
blocked for envelope-asserted Prime sessions); no new capability surface.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
