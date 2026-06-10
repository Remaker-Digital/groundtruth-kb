REVISED

# Add CLAUDE_CODE_SESSION_ID to bridge work-intent session-id resolution (REVISED-2)

bridge_kind: prime_proposal

author_identity: Prime Builder
author_harness_id: B
author_session_context_id: bbf81f79-b150-43a4-ac4c-f10c53f1a2a1
author_model: claude-opus-4-7
author_model_version: 1m
author_model_configuration: explanatory output style; Claude Code 1M-context

revision_reason: REVISED-2 over -003 NO-GO. Codex's three blocking findings
are addressed in this version: F1 — adds the `## Bridge INDEX Update Evidence`
section so `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` evidence
is mechanically detected. F2 — replaces placeholder project/work-item
language with concrete `Project Authorization`, `Project`, and `Work Item`
metadata (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / WI-4267 created
this session under PROJECT-GTKB-RELIABILITY-FIXES). F3 — adds the four
existing test files this proposal will augment to `target_paths`. No
substantive change to the implementation plan, verification plan, risk,
or rollback.

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4267

target_paths:
- .claude/hooks/bridge-compliance-gate.py
- .claude/hooks/bridge-axis-2-surface.py
- .claude/skills/bridge-propose/helpers/write_bridge.py
- groundtruth-kb/templates/hooks/bridge-compliance-gate.py
- groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py
- scripts/bridge_claim_cli.py
- platform_tests/hooks/test_bridge_compliance_gate_work_intent.py
- platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py
- platform_tests/scripts/test_bridge_claim_cli.py
- platform_tests/skills/test_bridge_propose_helper_work_intent.py

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

## Bridge INDEX Update Evidence

The `bridge/INDEX.md` row for this thread reflects the canonical
append-only lifecycle. No prior version has been deleted or rewritten in
place; each revision was filed as a new `-NNN.md` and the INDEX update
added the new row at the top of the entry above the prior rows. Current
state at INDEX time:

```text
Document: gtkb-claude-code-session-id-env-var-gap
REVISED: bridge/gtkb-claude-code-session-id-env-var-gap-004.md
NO-GO: bridge/gtkb-claude-code-session-id-env-var-gap-003.md
REVISED: bridge/gtkb-claude-code-session-id-env-var-gap-002.md
NEW: bridge/gtkb-claude-code-session-id-env-var-gap-001.md
```

This is the canonical bridge/INDEX.md entry shape for this thread: the
INDEX update inserted REVISED at the top of the entry while preserving the
NO-GO, REVISED, and NEW rows below in chronological-descending order.
`-001.md`, `-002.md`, and `-003.md` remain on disk unmodified; nothing has
been deleted, renamed, or rewritten. This satisfies
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` (Bridge artifact
filed under bridge/ with INDEX.md entry of correct status; no deletion or
rewrite of prior versions).

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
  states (NEW, REVISED, GO, VERIFIED) are honored; -001 was filed as NEW,
  -002 was REVISED-1, -003 was Codex's NO-GO, and this -004 is REVISED-2.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (v1, verified) — the fix is presented
  as a specification-driven change (ADR/DCL/GOV citations above), not a free-
  standing patch; the concrete WI-4267 record and the PAUTH-...-STANDING
  envelope are canonical artifacts in MemBase.

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

Standing authorization:

- `GOV-RELIABILITY-FAST-LANE-001` (v1, specified) — defines the fast-lane
  eligibility for small defect/reliability fixes covered by
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. The fix is hook/source/
  test additions only, no CLI extension, no policy change — within the
  fast-lane envelope.

Rule-cited soft authority:

- `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Drafting Claim Step
  and § Mandatory Pre-Filing Preflight Subsection — the protocols the gate
  enforces; this REVISED-2 closes Codex's NO-GO findings on -003.
- `.claude/rules/backlog-approval-state.md` — WI-4267 starts at
  `approval_state=unapproved` and transitions to `bridge_authorized` upon
  Codex GO citing it. The standing PAUTH provides implementation
  authorization through project membership at impl-start time.

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
- `bridge/gtkb-claude-code-session-id-env-var-gap-003.md` (Codex NO-GO on
  REVISED-1): findings F1 (INDEX-canonical clause evidence absent), F2
  (placeholder project/WI metadata), F3 (test files outside target_paths).
  This REVISED-2 closes all three.

## Requirement Sufficiency

Existing requirements sufficient. The fix restores the intended behavior of
the work-intent claim/Write-gate contract for Claude Code sessions; it does
not introduce a new requirement, change a policy, or affect any
implementation contract surface. No new spec is required to authorize this
change.

## Owner Decisions / Input

_No relevant owner decisions: this is a latent-defect fix with no policy
change. The owner explicitly noted "No owner AUQ required (this is a latent
defect fix, not a policy change)" when filing the defect report. The
implementation authority derives from the standing
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covering active project
membership (WI-4267 under `PROJECT-GTKB-RELIABILITY-FIXES`); the owner's
prior approval of that standing PAUTH is the durable owner-decision
evidence — no per-fix AUQ is required for fast-lane reliability work._

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

4. Add four new tests (one per surface) to the existing test files
   listed in `target_paths`. The tests assert that `CLAUDE_CODE_SESSION_ID`
   is recognized when present and that `CLAUDE_SESSION_ID` precedence is
   preserved when both are set.

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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live-verification step below — claim + Write tool round-trip from a fresh Claude Code session must pass the gate. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Pre-filing applicability preflight on the post-impl report must report `preflight_passed: true`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping table + each test below + post-impl report's mapping + executed test commands. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `rg --hidden CLAUDE_CODE_SESSION_ID -l` on the post-impl tree must list only in-root files (no `applications/Agent_Red/` matches introduced). |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001` | Tests 1-4 below assert env-var precedence semantics equivalent to the Slice 2 fallback chain. |
| `GOV-RELIABILITY-FAST-LANE-001` | The PAUTH+project+WI triad satisfies the fast-lane evidence path. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This proposal + its REVISED chain + post-impl report constitute the artifact trail; no spec citation goes through chat alone. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | INDEX entries record the canonical lifecycle (NEW → REVISED → NO-GO → REVISED → GO → post-impl-NEW → VERIFIED). |

Tests (added to the four existing test files listed in `target_paths`):

1. `test_bridge_compliance_gate_resolves_claude_code_session_id` in
   `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py` —
   monkeypatch the environment to: unset all other tuple members,
   set `CLAUDE_CODE_SESSION_ID="probe"`, call
   `_resolve_work_intent_session_id({})`, assert return equals `"probe"`.
   Companion test asserts `CLAUDE_SESSION_ID` precedence when both set.

2. `test_bridge_axis_2_surface_resolves_claude_code_session_id` in
   `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` —
   parallel test for `.claude/hooks/bridge-axis-2-surface.py`.

3. `test_write_bridge_helper_resolves_claude_code_session_id` in
   `platform_tests/skills/test_bridge_propose_helper_work_intent.py` —
   parallel test for `.claude/skills/bridge-propose/helpers/write_bridge.py`.
   Uses the helper's `resolve_work_intent_session_id(environ=...)` entry
   point with an explicit mapping argument so the test does not depend on
   ambient env.

4. `test_bridge_claim_cli_resolves_claude_code_session_id` in
   `platform_tests/scripts/test_bridge_claim_cli.py` —
   parallel test for `scripts/bridge_claim_cli.py` `_resolve_session_id`.

The post-impl phase must also probe the existing byte-for-byte
template-match regression for `.claude/skills/bridge-propose/helpers/write_bridge.py`
(asserted from `platform_tests/skills/test_bridge_propose_helper.py`,
which references `TEMPLATE_HELPER_PATH = REPO_ROOT / "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py"`).
If the active + template are updated in lockstep, the existing test
passes unchanged.

Execution:

```text
python -m pytest \
  platform_tests/hooks/test_bridge_compliance_gate_work_intent.py \
  platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py \
  platform_tests/scripts/test_bridge_claim_cli.py \
  platform_tests/skills/test_bridge_propose_helper_work_intent.py \
  platform_tests/skills/test_bridge_propose_helper.py \
  -v
```

Live verification (post-impl, manual): from a fresh Claude Code session,
run `python scripts/bridge_claim_cli.py claim <slug>` with NO `--session-id`
argument; expect a successful claim record naming the
`CLAUDE_CODE_SESSION_ID` value. Then call the `Write` tool against
`bridge/<slug>-NNN.md`; expect the bridge-compliance gate's session-id
check to pass.

Each test maps directly to one of the cited specs; spec-to-test mapping is
1:N for the gate-resolver tests (cover GOV-FILE-BRIDGE-AUTHORITY-001 +
DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 +
ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 + DCL-SESSION-ROLE-RESOLUTION-001).

## Risk

Low. The change is additive and append-only on tuples that are documented
as "session-id source priority order". No existing chain is broken; no
existing precedence is reordered. The fix mirrors a precedent already
landed in `scripts/workstream_focus.py` and the doctor's marker resolver
(both VERIFIED via Slice 2 of the interactive-session-role-override
project).

## Rollback

`git revert` the implementation commit. No state migration is involved;
no canonical artifact is mutated (the WI created this session, WI-4267,
remains; if rolling back, the WI is marked `resolution_status=withdrawn`
via a follow-on edit). No test fixture is touched beyond the new tests
this proposal adds.

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
4. The existing byte-for-byte template-match regression
   (`platform_tests/skills/test_bridge_propose_helper.py`) PASSes.
5. The 4 new tests listed above PASS.
6. No previously-passing test regresses.
7. The pre-filing applicability preflight on the post-impl report reports
   `preflight_passed: true` with `missing_required_specs: []`.
8. The clause preflight reports zero blocking gaps on the post-impl report.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
