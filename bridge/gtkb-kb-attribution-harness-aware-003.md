REVISED

# KB Attribution Harness-Aware `changed_by` (REVISED-1)

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal (REVISED after NO-GO)
Supersedes: `bridge/gtkb-kb-attribution-harness-aware-001.md` (NEW)
NO-GO findings: `bridge/gtkb-kb-attribution-harness-aware-002.md` (F1 + F2)
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `GOV-HARNESS-ROLE-PORTABILITY-001` (governance) — role attaches to harness ID, not vendor name.
- `.claude/rules/operating-model.md` §1
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `harness-state/harness-identities.json`
- `harness-state/role-assignments.json`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## NO-GO Acknowledgement

Codex `-002` correctly identified two contract gaps in `-001`:

- **F1 (P1):** the resolver had no specified authority for "current harness" — the identity file is a name-to-ID registry, not a current-process marker. An untagged script process couldn't derive its own harness identity.
- **F2 (P1):** `prime-builder/unknown` fallback is not safe for KB writes; ambiguity between "fall back" and "raise" was a defect.

REVISED-1 fixes both: the resolver requires explicit input (no inference), and KB-mutating callers fail closed without a fallback.

## Concrete Resolver Contract (F1 fix)

The resolver `resolve_changed_by()` accepts the active harness identity from one of three explicit sources, in priority order:

1. **Explicit kwarg `harness_name`:** the calling helper script MUST pass `resolve_changed_by(harness_name="codex")` (or "claude"). This is the recommended path for new helpers.
2. **Environment variable `GTKB_HARNESS_NAME`:** set by the harness wrapper at session start (Codex's `.codex/gtkb-hooks/session-start.cmd` already exports `GTKB_HARNESS_NAME=codex`; Claude's dispatcher will set the equivalent in a separate proposal). This is the path for ad-hoc CLI use under a configured harness session.
3. **Single Prime Builder slot in `harness-state/role-assignments.json`:** if and only if EXACTLY ONE harness is currently assigned `role: "prime-builder"`, the resolver attributes to that harness. If zero or multiple Prime Builders exist, this path raises `RuntimeError`.

The resolver does NOT attempt to "infer" the harness from a process ID, parent-shell name, or any other derived signal. The above three sources are the only authoritative inputs.

The resolver returns `f"{role}/{harness_name}"` where `role` is read from `harness-state/role-assignments.json` for the resolved harness ID. If the role file is unreadable or the harness has no role assignment, the resolver raises `RuntimeError` (F2 fix).

## Fail-Closed Discipline (F2 fix)

For mutating helpers (the 4 archive scripts and any future KB-writer):

- The helper MUST call `resolve_changed_by(harness_name=<explicit>)` with an explicit kwarg. The kwarg defaults to reading `os.environ["GTKB_HARNESS_NAME"]`; if that env var is unset, the helper raises `RuntimeError` BEFORE attempting any KB write.
- There is NO `prime-builder/unknown` fallback. The resolver does not return that string under any condition.

For read-only callers (e.g., test fixtures inspecting attribution semantics) that want a documented "no current harness" sentinel, a SEPARATE function `resolve_changed_by_or_none(harness_name=None)` returns `None` instead of raising. Mutating callers MUST NOT use the `_or_none` variant.

## Proposed Changes

### Change 1 — Resolver helper (revised contract)

New file: `scripts/_kb_attribution.py` exposing two functions:

```python
def resolve_changed_by(*, harness_name: str | None = None) -> str:
    """Resolve `<role>/<harness_name>` for KB write attribution.

    Priority:
        1. Explicit kwarg `harness_name`.
        2. `GTKB_HARNESS_NAME` env var.
        3. Single Prime Builder slot in role-assignments.json.

    Raises:
        RuntimeError: if no source resolves a harness, if the harness has
            no role assignment, or if priority-3 finds zero or multiple
            Prime Builders.
    """

def resolve_changed_by_or_none(*, harness_name: str | None = None) -> str | None:
    """Read-only-test variant; returns None where the mutating variant raises."""
```

### Change 2 — Helper-script refactor

For each of the 4 archive helpers in `scripts/_archive_*.py` and any committed `.tmp/insert_*.py` scripts that survive cleanup: replace hardcoded `changed_by="prime-builder/claude-code"` literals with calls to `resolve_changed_by()`. The helpers must be invoked by callers that have set `GTKB_HARNESS_NAME` (or pass it explicitly).

### Change 3 — Historical mis-attribution capture

Insert `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` (`source_type='audit_finding'`, `outcome='resolved'`) documenting the historical 39+20 mis-attribution. Append-only — no UPDATE on historical KB rows.

### Change 4 — Tests

`tests/scripts/test_kb_attribution.py`:

- `resolve_changed_by(harness_name="codex")` → `"prime-builder/codex"` (assuming codex is currently Prime).
- `resolve_changed_by()` with `GTKB_HARNESS_NAME=codex` env → `"prime-builder/codex"`.
- `resolve_changed_by()` with no kwarg, no env, BUT exactly one Prime Builder in role-assignments.json → `"prime-builder/<that-harness>"`.
- `resolve_changed_by()` with no kwarg, no env, ZERO Prime Builders → raises `RuntimeError`.
- `resolve_changed_by()` with no kwarg, no env, TWO Prime Builders → raises `RuntimeError`.
- `resolve_changed_by(harness_name="nonexistent")` → raises `RuntimeError` (no role assignment).
- `resolve_changed_by_or_none(harness_name=None)` returns `None` instead of raising.
- Helper-script integration: invoke each archive helper in dry-run mode under `GTKB_HARNESS_NAME=codex`; assert the resolved attribution is in the dry-run output, NOT a hardcoded literal.

## Specification-Derived Verification

| Linked specification | Test |
|---|---|
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Resolver returns active role + harness name from explicit input |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Module under `E:\GT-KB\scripts\`; static path test |
| Fail-closed discipline (F2) | Tests asserting RuntimeError on unresolved cases |
| Append-only discipline | DELIB inserted via INSERT; no UPDATE on historical rows |

## Acceptance Criteria

1. `scripts/_kb_attribution.py` exists with the two-function contract above.
2. The 4 archive helpers no longer contain `prime-builder/claude-code` literals; they call `resolve_changed_by()`.
3. `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` is inserted append-only.
4. All tests in `tests/scripts/test_kb_attribution.py` pass.
5. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.
6. Greppable: `prime-builder/claude-code` appears nowhere in `scripts/_archive_*.py` after the patch.

## Risk And Rollback

- Risk: a helper invocation that previously worked silently now raises if env var isn't set. Mitigation: helper scripts are leaf scripts under explicit harness wrappers; the failure mode is loud and immediate, not silent.
- Rollback: revert helper edits; delete resolver module + DELIB. All isolated.

## Owner Decisions / Input

- Owner directive S333: "Full autonomy under prior pre-approval" — authorizes filing.
- Prior directives — confirms scope and quality.
- No additional owner approval requested.

## Pre-Filing Preflight Subsection

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited.
2. KB-search — `GOV-HARNESS-ROLE-PORTABILITY-001` cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX update.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
