REVISED

author_identity: Claude Code
author_harness_id: B
author_session_context_id: 77a7836d-1aac-4786-ae0f-3cf8b433b66c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code; interactive; Prime Builder; autonomous friction-reduction
author_metadata_source: prime-builder session; inline author metadata

# Implementation Proposal REVISED — LO File-Safety Write-Gate: Resolve Role via Session Envelope (WI-4371)

bridge_kind: prime_proposal
Document: gtkb-lo-file-safety-gate-envelope-role-resolution
Version: 005
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-004.md (Codex GO)

Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001
Work Item: WI-4371
Recommended commit type: fix

target_paths: [".claude/hooks/lo-file-safety-gate.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py"]

implementation_scope: hook_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Notes (REVISED -005 vs -003)

**This REVISED addresses a non-substantive formatting defect in -003 that blocks
the implementation-start authorization gate.** The proposal content, scope,
spec-links, verification plan, and all technical substance are unchanged from
the Codex-GO'd -003.

**Defect:** Line 143 of -003 uses `### Requirement Sufficiency` (h3) instead
of `## Requirement Sufficiency` (h2). The `scripts/implementation_authorization.py`
section parser (`SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)`)
only matches h2 headings. The `requirement_sufficiency_state()` function
therefore returns `"missing"` for the -003 proposal, and `begin --bridge-id`
exits 2 with "Approved proposal is missing ## Requirement Sufficiency". Codex
GO@-004 did not detect this formatting defect.

**Fix:** Changed the heading from `###` to `##` at the Requirement Sufficiency
section (this file, below). No other change.

## Revision Notes (REVISED -003 vs -001)

Addresses Codex NO-GO `-002`:

- **F1 (P1) — harness-neutral current-session-id resolution.** The `-001` path
  resolved the current session id from `payload.get("session_id")` or only
  `os.environ.get("CLAUDE_CODE_SESSION_ID")`, which would pass `None` in
  Codex/GTKB contexts (where `GTKB_SESSION_ID` / `CODEX_SESSION_ID` /
  `CODEX_THREAD_ID` is the continuity id), forcing the resolver's weaker
  `marker_session_id_unverified` branch and undercutting the spoof-resistance
  claim on the Codex parity path. **Fix:** resolve the current session id via the
  canonical shared utility `scripts/gtkb_session_id.resolve_session_id`, payload
  first, then the `MARKER_CONTINUITY_ORDER` the marker writer itself uses.
- **F2 (P2) — prove the harness-neutral path.** Added hook-level env-fallback
  tests so the security-control integration (not just the resolver table) is
  proven for the Codex/GTKB session-id variables.

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
(marker > durable), gating on the **resolved** role, and supplies the current
session id via the canonical shared resolver so the marker's session-id
verification works on every harness. On mismatch/stale/absent marker the
resolver returns the durable role (outcomes `durable_marker_*`); the gate's
fail-open behavior on missing/malformed role state is preserved.

## PAUTH Coverage Note

`PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001`
is a bounded authorization created for this exact work via `gt projects
authorize` (owner-decision `DELIB-20260884`): active, tied to
`PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`, explicitly includes WI-4371,
linked specs `DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`,
allowed mutation classes `hook_scripts` + `tests`. The `scripts/gtkb_session_id`
dependency is a READ-ONLY import (not a mutation target; not in `target_paths`).

## Proposed Change (exact)

In `.claude/hooks/lo-file-safety-gate.py`:

- Add guarded imports (same fail-open `None` sentinel pattern as the existing
  `harness_roles` imports):
  - `resolve_interactive_session_role` from `scripts.session_role_resolution`
  - `resolve_session_id` and `MARKER_CONTINUITY_ORDER` from `scripts.gtkb_session_id`
- Refactor `_is_lo_enforced(root, payload)` to:
  1. Resolve `harness_name` as today (env/payload, with the existing
     claude/codex defaulting).
  2. Resolve the **current session id** harness-neutrally:

     ```text
     payload_session_id = payload.get("session_id") or payload.get("active_session_id")
     current_session_id = resolve_session_id(
         payload_session_id,
         order=MARKER_CONTINUITY_ORDER,
     ) or None
     ```

     `MARKER_CONTINUITY_ORDER` = `(GTKB_SESSION_ID, CODEX_SESSION_ID,
     CODEX_THREAD_ID, CLAUDE_SESSION_ID, CLAUDE_CODE_SESSION_ID)` — the exact
     order the marker writer (`scripts/workstream_focus.py`) uses, so the
     gate compares against the same id the marker recorded. `None` remains only
     the true no-session-id case.
  3. Call `resolve_interactive_session_role(root, harness_name,
     current_session_id=current_session_id)` → `(resolved_role, outcome)`.
  4. Return `resolved_role == "loyal-opposition"` (enforce read-only). A
     resolved Prime role (verified marker or durable) returns False (writes
     allowed).
  5. Preserve fail-open: if any resolver/utility import sentinel is `None` or a
     call raises, return False (current behavior), so startup repairs and fresh
     clones are never hard-blocked.

The durable-only `load_role_assignments`/`is_loyal_opposition` path is retained
internally only as the resolver's own fallback; the hook no longer calls it
directly for the authoritative decision.

Codex parity: `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` pipes into
this canonical hook, so the harness-neutral session-id behavior propagates
without a separate Codex edit (the adapter holds no independent role logic).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the deterministic marker>durable resolution table this fix adopts.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable role is the fallback when no session role is declared; the authority split the fix honors.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — session-stated role takes precedence for interactive surfaces; this closes the one unmigrated surface (the write-gate).
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — routing_override supersedes the role default; the envelope-authoritative principle.
- `GOV-STANDING-BACKLOG-001` — WI-4371 standing-backlog governance.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are
`DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`,
plus the owner decision `DELIB-20260884` and the shared session-id resolver
authority (`DELIB-20260625`). No new or revised requirement is needed.

## Spec-Derived Verification Plan

| Spec / Acceptance Item | Test | Expected |
|---|---|---|
| `DCL-SESSION-ROLE-RESOLUTION-001` — resolved role = marker when verified (payload id) | `test_is_lo_enforced_false_when_verified_pb_marker_payload` (marker PB + matching payload session_id) | `_is_lo_enforced` → False |
| F2.1 — payload session_id wins over env | `test_is_lo_enforced_payload_session_id_wins_over_env` (payload id matches marker; conflicting env) | → False (matching branch) |
| F2.2 — no payload + `GTKB_SESSION_ID`/`CODEX_THREAD_ID` matching marker → PB allowed | `test_is_lo_enforced_false_when_env_session_id_matches_pb_marker` | `_is_lo_enforced` → False |
| F2.3 — no payload + env session id mismatching marker → durable fallback | `test_is_lo_enforced_true_when_env_session_id_mismatches_marker_durable_lo` | `_is_lo_enforced` → True |
| F2.4 — no payload + no session-id env → documented no-id behavior (`marker_session_id_unverified`) | `test_is_lo_enforced_no_session_id_documents_unverified_branch` | branch is intentional/tested |
| `GOV-SESSION-ROLE-AUTHORITY-001` — durable fallback when no marker | `test_is_lo_enforced_true_when_no_marker_durable_lo` | `_is_lo_enforced` → True |
| Durable PB with no marker still allows writes | `test_is_lo_enforced_false_when_no_marker_durable_pb` | `_is_lo_enforced` → False |
| Fail-open on missing/malformed role state | `test_is_lo_enforced_false_when_role_state_unavailable` | `_is_lo_enforced` → False |
| Full hook regression | `pytest platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py` + existing `platform_tests/test_loyal_opposition_file_safety_clarification.py` | all pass |
| Lint + format | `ruff check` + `ruff format --check` on the 2 changed files | clean |

Tests set/clear `GTKB_SESSION_ID`/`CODEX_THREAD_ID`/`CLAUDE_CODE_SESSION_ID` via
`monkeypatch.setenv`/`delenv` and write the session-role marker fixture with the
matching/mismatching session id, exercising the hook's own id-resolution rather
than only the resolver table.

## Owner Decisions / Input

The proposal depends on owner approval; the authorizing evidence:

- **`DELIB-20260884`** (`source_type=owner_conversation`, `outcome=owner_decision`,
  2026-06-05) — owner Mike chose "Migrate to resolver" via `AskUserQuestion`;
  also the `--owner-decision` basis of the bounded PAUTH. Recorded in
  `memory/pending-owner-decisions.md` (`detected_via: ask_user_question`).
- Owner directive 2026-06-05: the harness role assignment is a default used only
  when the envelope specifies no role; the envelope role is authoritative.

No additional owner decision is required for Loyal Opposition to re-review. This
is a behavior change to a security write-gate; the F1 revision strengthens the
spoof-resistance to be harness-neutral.

## Prior Deliberations

- `DELIB-20260884` — owner decision to migrate the write-gate to the resolver.
- `DELIB-20260625` and `bridge/gtkb-session-id-shared-resolver-unification-003.md`/`-004.md`
  — owner-approved shared session-id membership authority and the two per-surface
  orders; the design constraint Codex flagged for the current-session-id portion.
  The REVISED change adopts `MARKER_CONTINUITY_ORDER` from that authority.
- The `gtkb-interactive-session-role-override-slice-1..10` thread family (all
  VERIFIED) — precedent migrations of the 9 sibling surfaces.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` deliberations — session-stated-role
  precedence for interactive surfaces.
- No retrieved deliberation rejects routing the write-gate through the resolver
  with the shared session-id utility.

## Risk and Rollback

**Risk after merge:** Moderate — changes write-enforcement behavior. The
spoof-resistance is now harness-neutral (the gate resolves the current session
id via the same canonical utility and order the marker writer uses), so a
session cannot claim Prime write-authority off a marker it did not write on any
harness. Fail-open on missing/malformed state preserved. Codex parity inherits
the change via the bash-adapter. The test matrix covers payload-id, env-id
(matching/mismatching), no-id, durable branches, and fail-open.

**Rollback:** Revert the single hook commit. The durable-only `_is_lo_enforced`
behavior is restored; the resolver, shared session-id utility, and sibling
surfaces are unaffected.

## Notes for Loyal Opposition

**The ONLY change from the GO'd -003 is the heading level of the Requirement
Sufficiency section: `###` → `##`.** This unblocks
`scripts/implementation_authorization.py begin` which requires h2 sections. All
technical content, spec-links, tests, and scope are byte-identical to the
approved -003. Codex should verify the heading-level fix and re-issue GO without
full re-review of unchanged substance.

The REVISED change uses `scripts/gtkb_session_id.resolve_session_id(...,
order=MARKER_CONTINUITY_ORDER)` so the write-gate's current-session-id resolution
matches the marker writer's continuity order exactly (`GTKB_SESSION_ID`,
`CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `CLAUDE_SESSION_ID`,
`CLAUDE_CODE_SESSION_ID`). The four F2 tests prove the hook integration on the
Codex/GTKB env path, not only the resolver table. `None` is passed to the
resolver only for the genuine no-session-id case (one explicit test documents
that as an intentional `marker_session_id_unverified` branch). Fail-open is
preserved on every error/sentinel-None path. The implementation phase will mint
the implementation-start packet from this thread's GO before editing the hook.

## Recommended Commit Type

`fix:` — repairs role-resolution behavior in the write-gate; no new capability
surface.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
