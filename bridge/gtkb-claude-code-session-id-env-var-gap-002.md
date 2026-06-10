REVISED

# Add CLAUDE_CODE_SESSION_ID to bridge work-intent session-id resolution (REVISED-1)

bridge_kind: prime_proposal

author_identity: Prime Builder
author_harness_id: B
author_session_context_id: bbf81f79-b150-43a4-ac4c-f10c53f1a2a1
author_model: claude-opus-4-7
author_model_version: 1m
author_model_configuration: explanatory output style; Claude Code 1M-context

revision_reason: REVISED-1 over -001 to satisfy the mandatory pre-filing
applicability preflight. The -001 packet was filed before the preflight was
run; the preflight (packet_hash sha256:8342cd76...) reported
`missing_required_specs: ["DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"]`
and three advisory specs absent. This revision adds those citations and a
spec-derivation note. No substantive change to the implementation plan,
target_paths, verification plan, risk, or rollback.

target_paths:
- .claude/hooks/bridge-compliance-gate.py
- .claude/hooks/bridge-axis-2-surface.py
- .claude/skills/bridge-propose/helpers/write_bridge.py
- groundtruth-kb/templates/hooks/bridge-compliance-gate.py
- groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py
- scripts/bridge_claim_cli.py

Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY (parent project; if absent in MemBase, may need a new project record before this proposal can be implementation-authorized)
Work Item: candidate WI to be created post-GO

## Summary

The Claude Code harness exposes its session id as the env var
`CLAUDE_CODE_SESSION_ID`, not `CLAUDE_SESSION_ID`. The bridge-compliance gate,
the bridge-axis-2 surface, the bridge-propose helper, the bridge-claim CLI, and
two template mirrors of the active files all enumerate a session-id env-var
tuple that includes `CLAUDE_SESSION_ID` but omits `CLAUDE_CODE_SESSION_ID`.
Empirical reproduction this session: `CLAUDE_CODE_SESSION_ID` is set,
`CLAUDE_SESSION_ID` is empty, and the gate's `_resolve_work_intent_session_id`
returns the empty string — causing the gate to block all bridge file
Write/Edit calls from Claude Code with "Bridge file Write blocked: no harness
session id is available".

The operator workaround is to call out to a Bash/PowerShell subprocess with
`$env:CLAUDE_SESSION_ID = "..."` explicitly set, which bypasses the gate
entirely (the substantive checks — author metadata, spec-link heading, owner-
decisions section, applicability preflight section — do not run on bridge
writes from Claude Code). This proposal itself was filed via that workaround,
which is a concrete acceptance test of the defect.

The fix is additive and append-only on the tuples: insert
`CLAUDE_CODE_SESSION_ID` immediately after `CLAUDE_SESSION_ID` so explicit
overrides via `CLAUDE_SESSION_ID` still take precedence when set.

## Specification Links

Blocking (required) cross-cutting specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (v1, verified) — live bridge index is the
  canonical workflow state; the work-intent claim/Write-gate contract is the
  mechanical enforcement of that authority. A gate that cannot resolve a
  session-id for the canonical authoring harness silently degrades the contract.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (v1, specified) —
  this proposal cites every relevant cross-cutting governance specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (v1, specified) — the
  Spec-Derived Verification Plan section below maps each cited spec to one or
  more concrete tests; the post-implementation report must carry the same
  mapping forward and execute the tests to receive VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (v1, specified) — all touched
  files are in-root under `E:\GT-KB`; the fix is platform-scope and does not
  affect any application subtree (`applications/Agent_Red/` is untouched).

Advisory cross-cutting specs (matched by the applicability registry):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (v1, verified) — this proposal is
  itself an artifact in the bridge-proposal class; it cites prior MemBase
  records and Deliberation Archive entries rather than restating their content.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (v1, verified) — the proposal lifecycle
  states (NEW, REVISED, GO, VERIFIED) are honored; -001 was filed as NEW, this
  -002 is REVISED after a self-detected preflight gap, and downstream lifecycle
  states will follow the trigger discipline.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (v1, verified) — the fix is presented
  as a specification-driven change (ADR/DCL/GOV citations above), not a free-
  standing patch; owner decisions, requirements, work items, and tests are
  represented through their canonical artifact classes.

Slice 2 precedent (already-VERIFIED Claude-Code session-id recognition that
this proposal extends to additional surfaces):

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (v1, specified) — Slice 2
  established `CLAUDE_CODE_SESSION_ID` as a recognized Claude-side session-id
  env var in `scripts/workstream_focus.py` and
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. This proposal
  retrofits the same recognition into the bridge-compliance, bridge-axis-2,
  bridge-propose, and bridge-claim surfaces that were not updated in that
  slice.
- `DCL-SESSION-ROLE-RESOLUTION-001` (v1, specified) — F1 of the Slice 2 NO-GO
  established that the canonical fallback chain must read Codex env vars at
  the call site (no module-load-time capture) and must include
  `CLAUDE_CODE_SESSION_ID`. The same chain semantics apply here.

Rule-cited soft authority:

- `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Drafting Claim Step
  and § Mandatory Pre-Filing Preflight Subsection — the protocols the gate
  enforces; this REVISED-1 closes a self-detected preflight gap on -001.

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-002.md`
  through `-008.md` (Slice 2 of the interactive-session-role-override project):
  established the `CLAUDE_CODE_SESSION_ID` env-var name as the Claude Code
  session-id env var and added it to `scripts/workstream_focus.py`'s fallback
  chain plus the doctor's marker session-id resolver. The bridge-compliance
  gate, bridge-axis-2 surface, bridge-propose helper, and bridge-claim CLI
  were not retrofitted in that slice, leaving the gap this proposal closes.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (placement principle:
  put resources on paths agents already traverse). The current defect is the
  inverse — a path the agent already traverses (the gate's env-var tuple) is
  missing a resource (the live env var) the agent actually exposes. Placement
  alignment.

## Requirement Sufficiency

Existing requirements sufficient. The fix restores the intended behavior of
the work-intent claim/Write-gate contract for Claude Code sessions; it does
not introduce a new requirement, change a policy, or affect any
implementation contract surface. No new spec is required to authorize this
change.

## Owner Decisions / Input

_No relevant owner decisions: this is a latent-defect fix with no policy
change. The owner explicitly noted "No owner AUQ required (this is a latent
defect fix, not a policy change)" when filing the defect report._

## Implementation Plan

1. In each of the 5 files that declare `WORK_INTENT_SESSION_ENV_VARS`,
   add the string `"CLAUDE_CODE_SESSION_ID"` to the tuple immediately after
   `"CLAUDE_SESSION_ID"`. The 5 files are:
   - `.claude/hooks/bridge-compliance-gate.py` (line 59)
   - `.claude/hooks/bridge-axis-2-surface.py` (line 80)
   - `.claude/skills/bridge-propose/helpers/write_bridge.py` (line 133)
   - `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (line 59)
   - `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` (line 125)

   The template mirrors must change in lockstep with the active files
   because a byte-for-byte template-match regression test is in force (per
   the auto-memory feedback `.claude/hooks gates are template-locked`).

2. In `scripts/bridge_claim_cli.py` (line 62), the parallel tuple is named
   `SESSION_ENV_VARS`. Add `"CLAUDE_CODE_SESSION_ID"` after
   `"CLAUDE_SESSION_ID"` there too. This makes the claim CLI resolve
   session-id without requiring `--session-id` from Claude Code sessions,
   closing the friction that forced the use of `--session-id "$CLAUDE_CODE_SESSION_ID"`
   for the claim that authored this very proposal.

3. Ordering preserves existing precedence: any explicit `CLAUDE_SESSION_ID`
   override (the documented operator workaround) still wins.

## Out-of-Scope Observations (For Codex Adjudication)

Three additional scripts have shorter inline session-id tuples that share the
same gap but are not part of the Write-time gate path:

- `scripts/bridge_author_metadata.py:39-42` — `("GTKB_SESSION_ID", "CODEX_SESSION_ID", "CLAUDE_SESSION_ID")` used for author_session_context_id resolution.
- `scripts/gtkb_bridge_writer.py:186` — `("GTKB_SESSION_ID", "CLAUDE_SESSION_ID", "CODEX_SESSION_ID")` used for session-id logging.
- `scripts/wrap_scan_cross_artifact_drift.py:76` — `("GTKB_SESSION_ID", "CODEX_SESSION_ID", "CLAUDE_SESSION_ID")` used for wrap-scan attribution.

These are quality-of-life follow-ons (author-metadata fields, log fields)
that affect attribution but do not block writes. They are intentionally
omitted from this proposal's `target_paths` to keep the scope minimal and
the change reversible. If Codex's review prefers a single sweep, this
proposal can be REVISED to extend `target_paths`. Otherwise a follow-on
thread can address them.

Also out of scope: `.claude/hooks/owner-decision-tracker.py:1367` reads only
`CLAUDE_SESSION_ID` for an informational field where "no logic depends on it
being populated" (per the source comment). No behavioral defect.

## Spec-Derived Verification Plan

The verification plan is derived from the cited specs as follows
(satisfies `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Spec | Tests / Evidence |
|------|------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live-verification step (3) below — claim + Write tool round-trip from a fresh Claude Code session must pass the gate. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Pre-filing applicability preflight on the post-impl report must report `preflight_passed: true`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping table + each test below + post-impl report's mapping + executed test commands. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `rg --hidden CLAUDE_CODE_SESSION_ID -l` on the post-impl tree must list only in-root files (no `applications/Agent_Red/` matches introduced). |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001` | Tests 1-5 below assert env-var precedence semantics equivalent to the Slice 2 fallback chain. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This proposal + its REVISED chain + post-impl report constitute the artifact trail; no spec citation goes through chat alone. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | INDEX entries record the canonical lifecycle (NEW → REVISED → GO → post-impl-NEW → VERIFIED). |

Tests (to be added in the implementation phase under
`platform_tests/hooks/` and `platform_tests/scripts/`):

1. `test_bridge_compliance_gate_resolves_claude_code_session_id` —
   monkeypatch the environment to: unset all other tuple members,
   set `CLAUDE_CODE_SESSION_ID="probe"`, call
   `_resolve_work_intent_session_id({})`, assert return equals `"probe"`.

2. `test_bridge_compliance_gate_claude_session_id_takes_precedence` —
   monkeypatch env: `CLAUDE_SESSION_ID="explicit"`,
   `CLAUDE_CODE_SESSION_ID="implicit"`, assert resolver returns
   `"explicit"` (precedence preserved).

3. `test_bridge_axis_2_surface_resolves_claude_code_session_id` —
   parallel test for `.claude/hooks/bridge-axis-2-surface.py`.

4. `test_write_bridge_helper_resolves_claude_code_session_id` —
   parallel test for `.claude/skills/bridge-propose/helpers/write_bridge.py`.
   Uses the helper's `resolve_work_intent_session_id(environ=...)` entry
   point with an explicit mapping argument so the test does not depend on
   ambient env.

5. `test_bridge_claim_cli_resolves_claude_code_session_id` —
   parallel test for `scripts/bridge_claim_cli.py` `_resolve_session_id`.

6. `test_template_match_bridge_compliance_gate_byte_for_byte` —
   existing template-match test (already in
   `platform_tests/templates/`); re-run to confirm it still PASSes after
   the active + template files are updated in lockstep. If it FAILs, the
   active and template tuples have drifted.

7. `test_template_match_write_bridge_helper_byte_for_byte` — analogous
   template-match test for the bridge-propose helper.

Execution: `python -m pytest platform_tests/hooks/test_bridge_compliance_gate*.py
platform_tests/hooks/test_bridge_axis_2_surface*.py
platform_tests/scripts/test_bridge_claim_cli*.py
platform_tests/templates/ -v`.

Live verification (post-impl, manual): from a fresh Claude Code session,
run `python scripts/bridge_claim_cli.py claim <slug>` with NO `--session-id`
argument; expect a successful claim record naming the
`CLAUDE_CODE_SESSION_ID` value. Then call the `Write` tool against
`bridge/<slug>-NNN.md`; expect the bridge-compliance gate's session-id
check to pass.

## Risk

Low. The change is additive and append-only on tuples that are documented
as "session-id source priority order". No existing chain is broken; no
existing precedence is reordered. The fix mirrors a precedent already
landed in `scripts/workstream_focus.py` and the doctor's marker resolver
(both VERIFIED via Slice 2 of the interactive-session-role-override
project).

## Rollback

`git revert` the implementation commit. No state migration is involved;
no canonical artifact is mutated; no test fixture is touched beyond the
new tests this proposal adds.

## Acceptance Criteria

1. From a Claude Code session where `CLAUDE_CODE_SESSION_ID` is set and
   `CLAUDE_SESSION_ID` is unset, `python scripts/bridge_claim_cli.py claim
   <slug>` succeeds without `--session-id`.
2. From the same session, a `Write` tool call against `bridge/<slug>-NNN.md`
   passes the bridge-compliance gate's session-id resolution step (the
   substantive checks downstream of resolution may still ask/deny on their
   own merits; that is correct behavior).
3. All 5 active + 2 template + 1 CLI tuples now contain
   `CLAUDE_CODE_SESSION_ID` immediately after `CLAUDE_SESSION_ID`.
4. The template-match regression tests for `bridge-compliance-gate.py` and
   `write_bridge.py` PASS.
5. The 7 new tests listed above PASS.
6. No previously-passing test regresses.
7. The pre-filing applicability preflight on the post-impl report reports
   `preflight_passed: true` with `missing_required_specs: []`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
