NO-GO

# Loyal Opposition Review - WI-4237 bridge reconciliation operator skill

bridge_kind: lo_verdict
Document: gtkb-bridge-reconciliation-operator-skill
Version: 002
Responds to: bridge/gtkb-bridge-reconciliation-operator-skill-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-20 UTC
Recommended commit type: docs:

## Verdict

NO-GO.

The re-scope direction is sound and the proposal passes the mandatory bridge
preflights, but the verification plan is not currently executable inside the
declared target scope. The proposal requires `test_api_skill_adapters.py` to
pass while the repository already has API-adapter drift in files that are not
listed as target paths for this bridge.

## Role And Authority Check

- Interactive session role: Loyal Opposition, per owner init `::init gtkb lo`.
- Durable harness projection: `gt harness roles` reports Codex harness `A` with
  role `loyal-opposition`; Claude harness `B` is `prime-builder`.
- `GO` / `NO-GO` are Loyal Opposition status tokens, so this verdict is
  role-authorized.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-reconciliation-operator-skill
```

Observed result: `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`.

Warning retained for Prime Builder: missing parent directories were reported
for the new skill locations:

```text
.agent/skills/bridge-reconciliation/SKILL.md
.api-harness/skills/bridge-reconciliation/SKILL.md
.claude/skills/bridge-reconciliation/SKILL.md
.codex/skills/bridge-reconciliation/SKILL.md
```

These are consistent with new skill directories and are not the reason for
NO-GO.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-reconciliation-operator-skill
```

Observed result: exit 0, `Evidence gaps in must_apply clauses: 0`,
`Blocking gaps (gate-failing): 0`.

## Prior Deliberations

- `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` exists and records
  the owner decision to re-scope WI-4237 to a no-index operator skill/runbook
  wrapping the surviving reconciliation tooling.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` exists and authorizes the
  bridge reconciliation project while preserving bridge GO, implementation-start,
  verification, and no-bulk-mutation gates.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` remains the
  governing decision for the verified-backlog reconciler surface the skill will
  document.
- Semantic search for `bridge reconciliation operator skill no index wrap scan
  reconciler` returned the WI-4237 re-scope decision, WI-4238 wrap-scan
  verification context, and prior bridge-authority/no-index context. No retrieved
  deliberation rejects the no-index re-scope.

## Blocking Finding

### FINDING-P1-001 - Verification plan depends on out-of-scope API adapter drift repair

Claim: The proposal's verification command requires
`platform_tests/scripts/test_api_skill_adapters.py` to pass, but that test
currently fails because the existing `.api-harness` generated adapters are
already out of sync outside the WI-4237 target path list.

Evidence:

- Proposal target paths at
  `bridge/gtkb-bridge-reconciliation-operator-skill-001.md:22` include
  `.api-harness/skills/bridge-reconciliation/SKILL.md` and
  `.api-harness/skills/MANIFEST.json`, but do not include the already-drifted
  generated adapter files `.api-harness/skills/bridge/SKILL.md`,
  `.api-harness/skills/kb-session-wrap/SKILL.md`, or
  `.api-harness/skills/proposal-review/SKILL.md`.
- The proposal's command block at
  `bridge/gtkb-bridge-reconciliation-operator-skill-001.md:91` requires
  `platform_tests/scripts/test_api_skill_adapters.py`.
- `platform_tests/scripts/test_api_skill_adapters.py:22` checks manifest SHA
  parity for every generated API adapter, and
  `platform_tests/scripts/test_api_skill_adapters.py:50` runs
  `scripts/generate_api_skill_adapters.py --check` for the whole repository.
- Review command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_generate_codex_skill_adapters.py platform_tests\scripts\test_generate_antigravity_skill_adapters.py platform_tests\scripts\test_generate_api_skill_adapters.py platform_tests\scripts\test_api_skill_adapters.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4237-adapters-review
```

Observed result: 33 passed, 2 failed. Both failures were in
`test_api_skill_adapters.py`. The generator check reported:

```text
API skill adapters: would update 4 file(s)
- .api-harness/skills/bridge/SKILL.md
- .api-harness/skills/kb-session-wrap/SKILL.md
- .api-harness/skills/proposal-review/SKILL.md
- .api-harness/skills/MANIFEST.json
```

Impact:

Prime Builder cannot satisfy the stated verification plan under the current
target-path envelope. Passing the cited test would require either out-of-scope
edits to existing API adapter files or a different, narrower verification plan.
Approving the proposal as written would set Prime Builder up to violate the
bridge target-path boundary or return with a post-implementation report whose
own planned tests still fail.

Required revision:

Revise the proposal using one of these paths:

1. Include the pre-existing API adapter drift repair in scope by adding the
   required `.api-harness/skills/*.md` files to `target_paths` and explaining why
   that broader adapter regeneration belongs inside WI-4237; or
2. Keep WI-4237 narrow and replace the whole-repository
   `test_api_skill_adapters.py` requirement with focused discoverability and
   generator-unit coverage that proves the new `bridge-reconciliation` adapter is
   generated/registered without requiring unrelated API adapter drift to be
   repaired in this bridge. If this path is chosen, explicitly cite
   `test_generate_api_skill_adapters.py` for API generator behavior and defer the
   existing API adapter drift to a separate work item or bridge.

## Positive Checks

- `scripts/bridge_backlog_terminal_reconciliation.py` is already broken as the
  proposal claims; it imports deleted `bridge_reconciliation_audit`.
- Review command
  `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_wrap_scan_reconciliation.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4237-review`
  passed: 8 passed.
- Review command
  `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_verified_backlog_reconciler.py --dry-run --json`
  exited 0 with `errors: []`, `candidate_count: 96`, and
  `would_resolve_ids: []` in the current pre-WI-4704 state.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-reconciliation-operator-skill --format json --preview-lines 20
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-reconcile-operator-skill --format json --preview-lines 10
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-reconciliation-operator-skill
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-reconciliation-operator-skill
gt deliberations get DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL --json
gt deliberations get DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT --json
gt deliberations get DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM --json
gt deliberations search "bridge reconciliation operator skill no index wrap scan reconciler" --limit 8 --json
rg --files .claude .codex .agents .agent .api-harness config scripts platform_tests
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_wrap_scan_reconciliation.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4237-review
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_generate_codex_skill_adapters.py platform_tests\scripts\test_generate_antigravity_skill_adapters.py platform_tests\scripts\test_generate_api_skill_adapters.py platform_tests\scripts\test_api_skill_adapters.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4237-adapters-review
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
