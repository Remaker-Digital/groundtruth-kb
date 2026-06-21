NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - impl-start gate does not honor the emergency-bridge-infrastructure-repair exemption

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-emergency-bridge-repair-exemption
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4697

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

`.claude/rules/codex-review-gate.md` (line 89) and the gate's own design proposal `bridge/gtkb-implementation-start-authorization-gate-001.md` (IP-3 line 125; Acceptance Criteria line 214; Risk-mitigation line 231) both specify that "Emergency bridge infrastructure repair (per bridge-essential.md)" is exempt from the bridge-proposal / live-GO requirement. That exemption exists only in rule prose: `scripts/implementation_start_gate.py` has NO mechanical exemption path. `gate_decision()` (line 1073) is the sole denial point and unconditionally blocks every protected mutation (including the bridge-function source/hook/config files under `scripts/**`, `.claude/hooks/**`, `.claude/settings.json`, `.codex/hooks.json`, `config/**`) whenever a live-GO implementation-authorization packet plus matching work-intent claim cannot be produced. When the review/dispatch pipeline itself is the thing being repaired, no GO can be minted, so the gate creates a circular deadlock: the repair that would restore the bridge is blocked by the very gate the broken bridge cannot authorize.

## Defect / Reproduction

Observed (S 2026-06-20): a genuine owner-authorized emergency bridge-infrastructure repair could not be performed because the impl-start gate blocked the protected source edit and the broken pipeline could not produce a live-GO packet. This is the same class previously hit during the gate's own bootstrap: `bridge/gtkb-implementation-start-authorization-gate-005.md` § "Emergency Repair Note" (lines 91-99) records that the initial gate-repair patch was blocked by `GTKB-IMPLEMENTATION-START-GATE` because the live latest bridge status was `NO-GO`, and Prime Builder had to fall back to the *documented-but-unimplemented* emergency exemption as a manual human procedure. That manual fallback only works for a human operator who can reason about the rule; the headless gate has no exemption, so the exemption is unenforceable by design.

Reproduction (logical, hook-level): pipe a PreToolUse payload for a protected bridge-function edit (e.g. `tool_name="Write"`, `file_path="scripts/cross_harness_bridge_trigger.py"`) into `scripts/implementation_start_gate.py` with NO active authorization packet. Current behavior: `gate_decision()` returns `{"decision": "block", ...}` (deadlock — no exemption is consulted even when valid owner emergency-repair evidence is present in the environment). Expected behavior: when (a) owner emergency-repair evidence is present in the environment AND (b) every changed path is a bridge-function path, the gate allows the edit and records the use to the gate audit trail; absent either condition, the gate still blocks (fail-closed).

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_start_gate.py`, `platform_tests/scripts/test_implementation_start_gate.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governing authority for permanent bridge-repair; this fix makes the *mechanical* gate honor the standing bridge-repair authority the spec grants, instead of blocking the repair it is supposed to permit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the exemption use is captured as a durable audit-trail artifact (gate-denials/usage JSONL) rather than an untracked human workaround, preserving the artifact lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs/rules (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives tests from each governing clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4697 is origin=defect, single source file + test, no new public surface and no new/revised spec, so it qualifies for the reliability fast-lane this spec defines.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the blocking clause (`BLOCKING_CLAUSE_ID`) the gate cites today; the fix must NOT weaken it for ordinary work — the exemption is scoped to bridge-function paths + owner emergency evidence and fails closed otherwise, so project-authorization-driven bypass remains prohibited.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform gate (`scripts/...`) and platform tests; no application-placement boundary is crossed and no adopter surface is touched.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the gate is shared by Claude (`.claude/hooks/implementation-start-gate.py`) and Codex (`.codex` registration); the exemption lives in the shared `gate_decision()` so both harness surfaces honor it identically (parity preserved).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the emergency-repair decision remains artifact-backed (owner evidence + audit-log record) rather than inferred or silent.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the gate source triggers the spec-on-contact obligation; the existing governing rule (`codex-review-gate.md`) is already the requirement, so no new spec is created.

## Prior Deliberations

- `DELIB-20260667` - Bridge thread: gtkb-impl-start-gate-pretooluse-restore (8 versions, VERIFIED) - establishes the gate's PreToolUse enforcement surface this fix extends with an exemption branch.
- `DELIB-20261021` - Loyal Opposition Review - Impl-Start-Gate Verb-Aware Path Extraction - prior review of `gate_decision()`/path-extraction behavior on the same source file; confirms the conservative classification posture the exemption must not undermine.
- `DELIB-20261020` - Loyal Opposition Verification - Impl-Auth and Impl-Start-Gate Parser Hygiene - prior verification of this gate module; the change set here is in the same module and reuses its established `is_protected_path` / audit-log surfaces.
- `DELIB-20265457` - Owner decision (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch in which WI-4697 is in scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - the standing reliability fast-lane authorization: WI-4697 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items (pipeline-repair and P1/P2 first); WI-4697 is P2.

Note: the implemented emergency-repair exemption is gated on owner-supplied emergency evidence at invocation time (env-var marker, mirroring the existing `GTKB_SOT_READ_DISCIPLINE_BYPASS` owner-authorized bypass pattern). This proposal does not itself invoke the exemption; it implements the mechanical path that the already-approved `codex-review-gate.md` exemption requires.

## Requirement Sufficiency

Existing requirements sufficient. The emergency-bridge-infrastructure-repair exemption is already a specified contract: `.claude/rules/codex-review-gate.md` line 89 ("Emergency bridge infrastructure repair (per bridge-essential.md)") and the gate design proposal `bridge/gtkb-implementation-start-authorization-gate-001.md` (IP-3, Acceptance Criteria, and Risk-mitigation, which prescribe the exact narrow shape: "Limit it to bridge-function files, require bridge-unusable detection or explicit owner emergency directive, and require a follow-up bridge/incident report"), under the standing bridge-repair authority `GOV-FILE-BRIDGE-AUTHORITY-001`. This defect is that the contract was never implemented in code; the fix enforces the existing contract. No new or revised requirement/specification is introduced.

## Proposed Scope

Single-concern defect fix to `scripts/implementation_start_gate.py`, mirroring the proven owner-authorized-bypass pattern already used by `.claude/hooks/sot-read-discipline.py` (`gate_decision` line 224 early-return on `GTKB_SOT_READ_DISCIPLINE_BYPASS`):

1. Add an `EMERGENCY_BRIDGE_REPAIR_ENV_VAR` constant (e.g. `GTKB_EMERGENCY_BRIDGE_REPAIR=1`) — the owner-supplied emergency-repair evidence marker. This mirrors the existing SoT bypass env-var contract (owner-authorized, single-invocation, must be documented per rule).
2. Define a narrow `BRIDGE_FUNCTION_PATHS` allow-set for the exemption (the bridge-function source/hook/config surfaces named in `bridge-essential.md` / `codex-review-gate.md`: `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, `scripts/implementation_start_gate.py`, `scripts/implementation_authorization.py`, `scripts/bridge_claim_cli.py`, the `groundtruth_kb/bridge/**` package, `.claude/hooks/**` bridge gate hooks, `.claude/settings.json`, `.codex/hooks.json`). Scope deliberately narrow per gate-001's mitigation ("Limit it to bridge-function files").
3. In `gate_decision()` (line 1073), AFTER `changed_paths()` computes `paths`/`mutating` and the `protected` set is determined (i.e. only when the edit would otherwise be blocked), add an exemption branch that allows the mutation IF AND ONLY IF: (a) the emergency env-var marker is set to `1`, AND (b) every path in `protected` is a bridge-function path per the allow-set (fail-closed: if any changed path is outside the allow-set, or the `<unknown-mutating-target>` fallback is present, the exemption does NOT apply and normal blocking proceeds). The branch returns `{}` (allow) and records the exemption use via a new `_record_gate_exemption(...)` helper writing to the existing gate audit JSONL surface (reusing `GTKB_GATE_DENIALS_PATH` / a sibling key) so the incident/report trail required by gate-001 Acceptance Criteria is preserved deterministically.
4. Add regression tests in `platform_tests/scripts/test_implementation_start_gate.py` (see verification plan).

This is the defect-removal path: it implements the already-specified exemption mechanically. It does NOT introduce a general bypass, does NOT weaken `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` for ordinary work, and does NOT alter packet/claim semantics for the non-emergency path.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (mechanical bridge-repair must be possible) | `test_emergency_bridge_repair_allows_bridge_function_edit_without_packet` | With `GTKB_EMERGENCY_BRIDGE_REPAIR=1` set and a protected edit to a bridge-function path (e.g. `scripts/cross_harness_bridge_trigger.py`) and NO authorization packet, `gate_decision()` returns `{}` (allow). |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (no bypass for ordinary work) | `test_emergency_env_does_not_exempt_non_bridge_protected_edit` | With `GTKB_EMERGENCY_BRIDGE_REPAIR=1` set but a protected edit to a NON-bridge-function path (e.g. `scripts/sample.py`) and no packet, `gate_decision()` still returns `decision == "block"` (exemption is scoped, fails closed). |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (fail-closed default) | `test_no_emergency_env_blocks_bridge_function_edit` | Without the env-var, a protected bridge-function edit with no packet still returns `decision == "block"` (exemption requires owner evidence; absence = block). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (audit-trail capture) | `test_emergency_exemption_records_audit_trail` | When the exemption allows an edit, a usage record is appended to the gate audit JSONL (asserted via `GTKB_GATE_DENIALS_PATH` redirected to a tmp file), capturing the incident trail gate-001 requires. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
- `python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`
- `python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`

## Acceptance Criteria

1. `gate_decision()` allows a protected bridge-function mutation (no packet) when the owner emergency-repair env marker is set, and records the use to the gate audit trail.
2. The exemption fails closed: it does NOT apply when the marker is absent, when any changed path is outside the narrow bridge-function allow-set, or when the `<unknown-mutating-target>` fallback is present.
3. Non-emergency behavior is unchanged: ordinary protected edits still require a live-GO packet + matching work-intent claim; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` is not weakened.
4. The four derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files; the pre-existing tests in `test_implementation_start_gate.py` remain green (no regression).

## Risks / Rollback

- Risk: the exemption becomes a loophole for ordinary work. Mitigation (per gate-001): two-condition AND gate (owner env evidence AND bridge-function-only paths), fail-closed default, and a deterministic audit-trail record of every use; the allow-set is narrow and enumerated, not a prefix wildcard over `scripts/**`.
- Risk: env-var marker could be left set across a session. Mitigation: the marker mirrors the SoT bypass single-invocation contract documented in `codex-review-gate.md`/`bridge-essential.md`; repeated use is auditable in the JSONL trail. (Tightening to a one-shot consume is out of scope for this defect fix and would be a separate enhancement.)
- Risk: allow-set drift versus the actual bridge-function file set. Mitigation: the set is enumerated in one constant adjacent to `PROTECTED_PREFIXES`; a follow-on could derive it from a registry, but that is a new requirement and out of scope here.
- Rollback: revert the exemption branch + constants + helper in `scripts/implementation_start_gate.py` and the added tests; the change is additive (a guarded early-return on an otherwise-blocked path) and fully reversible with no migration and no state schema change.

## Files Expected To Change

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
