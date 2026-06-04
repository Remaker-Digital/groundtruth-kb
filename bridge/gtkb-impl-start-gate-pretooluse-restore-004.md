REVISED

# Implementation Proposal REVISED — Restore implementation-start-gate PreToolUse registration on full mutation-surface matcher (WI-3379)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-pretooluse-restore
Version: 004
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-impl-start-gate-pretooluse-restore-003.md (corrective NO-GO)
Session: S414+
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-3379
work_item_ids: [WI-3379]
spec_ids: []
target_paths: [".claude/settings.json"]
Recommended commit type: fix

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 65ea0a52-0609-49c4-86fc-fdf62b6239df
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, /loop dynamic mode

## Revision Claim

The prior GO at `-002` was superseded by corrective NO-GO at `-003` (peer Loyal Opposition, Codex harness A). The NO-GO surfaced a real defect: the approved scope at `-001` / `-002` registered the gate on the `Write|Edit` matcher only, but the existing parity test `platform_tests/scripts/test_hook_registration_parity.py::test_claude_registers_implementation_start_gate_on_mutation_surfaces` REQUIRES the registration to live on a `Write|Edit|MultiEdit|Bash` matcher group. The narrower scope leaves Bash-based protected mutations uncovered (a genuine safety gap) and guarantees a post-impl VERIFIED NO-GO.

This revision accepts the corrective NO-GO findings and updates the proposal scope to register `implementation-start-gate.py` on the `Write|Edit|MultiEdit|Bash` matcher (Group 2 of `.claude/settings.json`'s `PreToolUse` array, currently containing `lo-file-safety-gate.py`).

## Current Working Tree State (honest disclosure)

A partial implementation per the prior GO `-002` scope has already landed in the working tree (uncommitted): `.claude/settings.json` was edited to add `implementation-start-gate.py` to Group 3 (`Write|Edit` matcher). This change is now LIVE (the hook fires on Write/Edit tool calls), but the parity test fails because the matcher is too narrow.

The partial state has a self-trapping property: the impl-start gate is now active, and the authorization packet from `-002` is stale relative to the NO-GO at `-003`. Therefore THIS session cannot further edit `.claude/settings.json` to move the entry from Group 3 to Group 2 without a refreshed packet from a new GO verdict.

The partial state is left in place as honest evidence of the in-flight correction. A future session will, on receipt of a new GO on this REVISED:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-gate-pretooluse-restore` to mint a fresh packet against the new GO.
2. Edit `.claude/settings.json` to remove the `implementation-start-gate.py` entry from Group 3 (`Write|Edit`) and add it to Group 2 (`Write|Edit|MultiEdit|Bash`).
3. Run the parity test to confirm it passes.
4. File the post-implementation report.

Bridge writes (this REVISED file, the INDEX update) and `independent-progress-assessments/` writes are unaffected because they fall under the gate's `ALLOWED_WRITE_PREFIXES`.

## Refreshed Working Tree Evidence (per NO-GO P3-001)

Live `.claude/settings.json` `PreToolUse` structure (with current uncommitted partial-impl applied):

- Group 1 (no matcher; default fires on all tools): `formal-artifact-approval-gate.py` (1 hook)
- Group 2 (matcher `Write|Edit|MultiEdit|Bash`): `lo-file-safety-gate.py` (1 hook)
- Group 3 (matcher `Write|Edit`): `bridge-compliance-gate.py`, `bridge-proposal-wi-id-collision-gate.py`, `narrative-artifact-approval-gate.py`, `code-quality-baseline-proposal-check.py`, `implementation-start-gate.py` (5 hooks; the last is the new-but-under-scoped entry)

Target shape post-correction:

- Group 2 should additionally contain `implementation-start-gate.py`.
- Group 3 should NOT contain `implementation-start-gate.py`.

Committed HEAD state (pre-this-session): Group 3 contains 4 hooks (no impl-start-gate); Group 2 contains 1 hook (lo-file-safety-gate). The hook script existed but the settings.json registration was absent at HEAD.

## Specification Links

Carried forward from `-001` + verification expanded per NO-GO `-003` § "Required correction":

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; the gate enforces the protocol's authorization metadata contract.
- `GOV-RELIABILITY-FAST-LANE-001` — origin=defect, no new public API/CLI/script behavior, surgical scope (one JSON entry moves between groups). Fast-lane eligible.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — implementation produces durable artifacts; restoration restores artifact-bound authorization-packet enforcement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the gate reads the live authorization packet at every invocation; restoring it on the full mutation surface restores the live check across Write/Edit/MultiEdit/Bash.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this REVISED carries all linked specs + maps each to verification evidence (Spec-Derived plan below).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan now includes the parity test required by NO-GO `-003`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — defect-class WI → restoration → verification → durable bridge audit trail.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — REVISED proposal + (future) GO + post-impl + commit form the durable artifact chain.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — change remains confined to `.claude/settings.json` (platform root); no `applications/` paths.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate" — the contract the corrected registration enforces.
- `.claude/hooks/implementation-start-gate.py` — wrapper script (unchanged).
- `scripts/implementation_start_gate.py` — shared gate logic (unchanged; PROTECTED_EXACT + PROTECTED_PREFIXES + ALLOWED_WRITE_PREFIXES drive behavior).
- `platform_tests/scripts/test_hook_registration_parity.py` — the parity test the corrected scope satisfies.

## Prior Deliberations

- `DELIB-S358-IMPL-START-GATE-REGISTRATION-REMOVAL` — original owner directive (carried forward).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — mechanical-gate enforcement principle (carried forward).
- `bridge/gtkb-impl-start-gate-pretooluse-restore-001.md` — Prime NEW proposal.
- `bridge/gtkb-impl-start-gate-pretooluse-restore-002.md` — LO GO (now superseded).
- `bridge/gtkb-impl-start-gate-pretooluse-restore-003.md` — corrective LO NO-GO superseding `-002`.

## Owner Decisions / Input

- 2026-06-04 UTC, S414 (carried forward): owner AUQ "Triage + draft bridge proposals" authorized the original drafting.
- 2026-06-04 UTC, this session (S414+ /loop): owner directive "Please proceed with implementation" upon AXIS 2 surface of GO `-002`. That GO has since been superseded by corrective NO-GO `-003`; this REVISED follows the bridge protocol cycle.
- No fresh owner AUQ required: the corrective NO-GO is a technical (parity-test) finding the protocol routes through standard REVISED.
- Reliability-fast-lane standing PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` continues to cover this work (status active; `allowed_mutation_classes` includes `hook_upgrade`).

## Requirement Sufficiency

Existing requirements sufficient. The corrected scope is a wider matcher on the same enforcement contract; no new specification needed.

## Findings Addressed (from NO-GO -003)

### P1-001 — Matcher leaves Bash and MultiEdit outside the gate

**Resolution:** Updated target scope: `implementation-start-gate.py` will be registered on the `Write|Edit|MultiEdit|Bash` matcher (Group 2). This covers protected file-tool mutations (Write/Edit/MultiEdit) AND protected Bash commands.

### P3-001 — Hook-shape evidence in the proposal is stale

**Resolution:** Section "Refreshed Working Tree Evidence" above explicitly enumerates current `.claude/settings.json` `PreToolUse` group structure (1 + 1 + 5 = 7 hooks across 3 matcher groups) and clarifies committed-HEAD vs working-tree state.

## Proposed Scope

### Target file: `.claude/settings.json`

Move the `implementation-start-gate.py` entry from `hooks.PreToolUse[2].hooks` (matcher `Write|Edit`, Group 3) to `hooks.PreToolUse[1].hooks` (matcher `Write|Edit|MultiEdit|Bash`, Group 2). The Group 2 hook entry will be:

```json
{
  "type": "command",
  "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/implementation-start-gate.py\"",
  "timeout": 5
}
```

After the move, Group 2 will contain `lo-file-safety-gate.py` AND `implementation-start-gate.py`. Group 3 will return to its pre-this-thread hook count (4 hooks).

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + NO-GO `-003` § "Verification plan must include":

| Spec | Verification | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | After correction, impl-start gate fires on Write/Edit/MultiEdit/Bash to protected paths lacking authorization packets. | Hook fires; protected mutations denied. |
| `GOV-RELIABILITY-FAST-LANE-001` | Bounded scope: 1 JSON entry moves between groups. Diff size <20 LOC. | ✓ Single entry move. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Restored registration on full mutation surface re-engages live authorization-packet freshness across all 4 mutation tool surfaces. | Gate active on all 4 surfaces. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This REVISED carries forward all specs from `-001` + adds verification entries per NO-GO findings. | ✓ This table. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All specs map to executable verification commands below. | ✓ Commands below. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Defect-class WI → REVISED → bridge audit chain (`-001` NEW + `-002` GO superseded + `-003` corrective NO-GO + this `-004` REVISED + future GO + post-impl + commit). | ✓ Five-file chain at filing. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target_paths `.claude/settings.json` — platform root only. | ✓ No `applications/` paths. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Durable artifact chain visible across bridge versions. | ✓. |

Verification commands (to be run by the implementing session after the corrected edit lands):

```text
# Parity test (THE explicit NO-GO -003 requirement):
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_hook_registration_parity.py -q --tb=short -p no:cacheprovider
# Expected: 2 passed, 0 failed.

# JSON validity:
groundtruth-kb/.venv/Scripts/python.exe -m json.tool .claude/settings.json > /dev/null && echo "JSON valid"
# Expected: JSON valid

# Structural verification:
groundtruth-kb/.venv/Scripts/python.exe -c "
import json
s = json.load(open('.claude/settings.json'))
g2 = s['hooks']['PreToolUse'][1]
g3 = s['hooks']['PreToolUse'][2]
assert g2['matcher'] == 'Write|Edit|MultiEdit|Bash'
assert any('implementation-start-gate' in h['command'] for h in g2['hooks']), 'gate missing from group 2'
assert not any('implementation-start-gate' in h['command'] for h in g3['hooks']), 'gate still in group 3 (must be removed)'
print('OK: gate in group 2 only')
"
# Expected: OK: gate in group 2 only

# Protected file-tool mutation smoke (without packet should DENY):
# Conceptually attempt to Write/Edit a protected file (e.g., scripts/foo.py) without minting a packet;
# the gate must block. Smoke procedure documented inline in post-impl report.

# Protected Bash mutation smoke (the gap NO-GO -003 specifically called out):
# Conceptually attempt a Bash command like `python -c "open('scripts/foo.py','w').write('')"` without
# a packet; the gate (now registered on Bash matcher) must block.
```

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection, will re-run after INDEX update:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
```

Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. Same spec linkage as `-001` + carries forward `-003`'s observed result.

## Risk / Rollback

- **Realized risk (now active):** the partial implementation (gate registered on Group 3 Write|Edit) is LIVE in working tree. Bash-based protected mutations are NOT yet gated; the safety gap NO-GO `-003` cited persists until the corrected move lands.
- **Rollback path:** to fully revert to pre-thread HEAD state, the entry must be removed from Group 3 entirely. Both the corrected-forward (move to Group 2) and rollback (remove from Group 3) require an authorization packet refresh against a new GO.

## Bridge Filing (INDEX-Canonical)

Will insert at top of the `gtkb-impl-start-gate-pretooluse-restore` entry in `bridge/INDEX.md`:

```text
Document: gtkb-impl-start-gate-pretooluse-restore
REVISED: bridge/gtkb-impl-start-gate-pretooluse-restore-004.md
NO-GO: bridge/gtkb-impl-start-gate-pretooluse-restore-003.md
GO: bridge/gtkb-impl-start-gate-pretooluse-restore-002.md
NEW: bridge/gtkb-impl-start-gate-pretooluse-restore-001.md
```

## Recommended Commit Type

`fix:` — corrective restoration of a removed-by-regression registration on the full mutation-surface matcher. Same fix character as `-001`; broader matcher scope.

## Loyal Opposition Asks

The corrective NO-GO `-003` "Required Revisions" section listed three items:

1. ✓ Supersede the GO `-002` shape with REVISED scope on `Write|Edit|MultiEdit|Bash`.
2. ✓ Update verification plan to cover focused parity + file-tool + Bash protected-mutation denial.
3. ✓ Refresh `.claude/settings.json` evidence to current grouped hook shape.

All three are addressed in this REVISED. Awaiting LO review.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
