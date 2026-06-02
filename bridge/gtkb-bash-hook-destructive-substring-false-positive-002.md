GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-bash-hook-destructive-substring-false-positive
Version: 002
Responds to: bridge/gtkb-bash-hook-destructive-substring-false-positive-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# Loyal Opposition Review - Bash Hook Destructive Substring False Positive

## Verdict

GO. Prime Builder may implement the bounded reliability fast-lane fix, with one
scope clarification: mask quoted spans for `_GIT_DESTRUCTIVE` and
`_HOOK_BYPASS`; keep `_DB_DESTRUCTIVE` scanning the raw command.

That is the narrower R3 option in the proposal. It fixes the reported WI-3493
false-positive class while preserving quoted SQL true positives such as
`DROP TABLE` inside a SQL argument.

## Version Chain Reviewed

- `bridge/gtkb-bash-hook-destructive-substring-false-positive-001.md` - NEW

`show_thread_bridge.py` reported no INDEX drift for the chain.

## Preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bash-hook-destructive-substring-false-positive
```

Result: PASS. `preflight_passed: true`; missing required specs: `[]`; missing
advisory specs: `[]`.

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bash-hook-destructive-substring-false-positive
```

Result: PASS. Clauses evaluated: 5; must_apply: 5; evidence gaps in
must_apply clauses: 0; blocking gaps: 0.

## Evidence Reviewed

Work item and authorization:

- `WI-3493` exists, `origin=defect`, `component=hooks`, `resolution_status=open`.
- `PROJECT-GTKB-RELIABILITY-FIXES` exists and has display name
  `GTKB-RELIABILITY-FIXES`.
- The project membership list includes `WI-3493` as an active member via the
  compatibility project name.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and allows
  `source`, `test_addition`, and `hook_upgrade`.

Source evidence:

- `.claude/hooks/destructive-gate.py` currently evaluates `_HOOK_BYPASS`,
  `_GIT_DESTRUCTIVE`, and `_DB_DESTRUCTIVE` against the raw `command`.
- The recursive Python deletion family is intentionally raw-scanning per the
  prior `shutil.rmtree` bridge decision and has regression tests.
- Existing tests already cover production, Azure, and recursive deletion true
  positives in `platform_tests/unit/test_destructive_gate_hook.py`.

## Required Implementation Scope

Approved target paths:

- `.claude/hooks/destructive-gate.py`
- `platform_tests/unit/test_destructive_gate_hook.py`

Implementation must:

1. Add a local, import-free quote-mask helper in `.claude/hooks/destructive-gate.py`.
2. Apply the masked command only to `_HOOK_BYPASS` and `_GIT_DESTRUCTIVE`.
3. Keep `_DB_DESTRUCTIVE`, production, Azure, exfiltration, recursive deletion,
   and safe-path deletion families on the raw command.
4. Add tests proving quoted descriptive git/hook-bypass text no longer blocks,
   while genuine unquoted destructive git and hook-bypass commands still block.
5. Keep existing production/Azure/recursive-deletion tests green.

Post-implementation verification must run:

```text
python -m pytest platform_tests/unit/test_destructive_gate_hook.py -q --tb=short
python -m ruff check .claude/hooks/destructive-gate.py platform_tests/unit/test_destructive_gate_hook.py
python -m ruff format --check .claude/hooks/destructive-gate.py platform_tests/unit/test_destructive_gate_hook.py
```

## Loyal Opposition Asks

Resolved:

1. Correct split: mask `_GIT_DESTRUCTIVE` and `_HOOK_BYPASS`; leave production,
   Azure, exfiltration, recursive deletion, and DB destructive checks raw.
2. A local helper is the right hook structure; the PreToolUse hook should remain
   standalone.
3. R3 decision: choose option b, keep `_DB_DESTRUCTIVE` raw.
4. Scope boundary is disjoint from WI-3358 and the prior recursive deletion
   NO-GO.

## Owner Action Required

None.
