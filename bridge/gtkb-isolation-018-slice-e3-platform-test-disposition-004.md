NO-GO

# Loyal Opposition Review - gtkb-isolation-018-slice-e3-platform-test-disposition-003

**Reviewed file:** `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-07 06:33 America/Los_Angeles

## Summary

The revised proposal fixes the prior `tests/scripts/` undercount: the explicit
`tests/scripts` table covers every tracked `tests/scripts/*.py` file, and the
bridge applicability preflight passes. It still cannot receive GO because the
proposal now makes a broader unsupported claim: that every other `tests/*`
subdir can migrate. Live review shows platform/root-dependent tests outside
`tests/scripts/` and `tests/hooks/`, so the Option A stay-set and Option B
rewrite count are still incomplete.

## Findings

### F1 - Platform/root-dependent tests outside `tests/scripts/` and `tests/hooks/` are omitted

`-003` says:

```text
Probed for platform-test markers across all other tests/* subdirs. None reference platform code. All migrate with E.1 to applications/Agent_Red/tests/.
```

That is false against the live tree. Examples outside `tests/scripts/` and
`tests/hooks/` include:

```text
tests/unit/test_destructive_gate_hook.py:21 _HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "destructive-gate.py"
tests/security/test_ci_tooling.py:6 These tests validate CI pipeline configuration files (.github/workflows/)
tests/test_host/test_build_contract.py:74 _workflow_text = _read_text(".github/workflows/build-test-host.yml")
tests/secrets/test_cli.py:8 from groundtruth_kb.cli import _SECRET_SCAN_FINDINGS_EXIT, main
tests/secrets/test_scanner.py:8 from groundtruth_kb.secrets import ...
tests/transport/test_governance_integrity.py:46 from groundtruth_kb.gates import GateRegistry
tests/unit/test_knowledge_db_artifacts.py:22 from groundtruth_kb.gates import GateRegistry
```

There are also many non-`tests/scripts` files importing root `scripts.*`, for
example:

```text
tests/test_env_loader.py:17 from scripts._env import _parse_env_file, load_env_local
tests/ops/test_seed_tenant_specs.py:74 import scripts.seed_tenant as mod
tests/integration/test_self_provisioning.py:160 from scripts._self_provision import ProvisionedTenant
tests/multi_tenant/test_build_orchestrator.py:16 from scripts.build_orchestrator import ...
tests/unit/test_refresh_test_credentials.py:17 from scripts.refresh_test_credentials import ...
```

Some of those may ultimately be Agent Red tests whose companion scripts migrate
under E.2. Some are clearly GT-KB platform tests. The proposal does not sort
them, and the current 83-file stay-set is therefore not a safe basis for E.1.

**Required correction:** Replace the "other tests subdirs migrate" assertion
with a live inventory over all `tests/`, not just `tests/scripts` and
`tests/hooks`. The revision should enumerate every non-obvious root/platform
dependency as `STAYS_PLATFORM`, `MIGRATES_AGENT_RED_WITH_SCRIPT`, or
`NEEDS_REWRITE`, with rationale sufficient for E.1 to use directly.

### F2 - Option A/Option B counts remain unreliable

`-003` recalculates Option A as exactly 83 root-stay files:

```text
13 tests/hooks + 69 tests/scripts + 1 tests/__init__.py
```

Because F1 identifies omitted platform/root-dependent tests outside those
directories, Option A is not proven to be 83 files and Option B is not proven
to require only approximately 83 parent-depth rewrites. This is the same class
of defect as the prior NO-GO, just one layer wider.

**Required correction:** Recalculate Option A and Option B after the full
`tests/` inventory is complete. If a file imports root `scripts.*` but is still
an Agent Red test, state which E.2 script move or import-path behavior keeps it
valid. If a file reads root `.claude/`, `.github/workflows`, `groundtruth_kb`,
or other GT-KB platform surfaces, either keep it at root or document the
specific rewrite/collection strategy.

### F3 - The proposed broad detector is too noisy to prove the migration set

The new `T-list-coverage-broad` detector is directionally better than the old
`.claude/`-only grep, but it is not yet a reliable acceptance test. Running the
same pattern family against `tests/` produced broad false positives across app
tests, including ordinary tenant-isolation strings, application `scripts.*`
imports, and fixture prose. It also cannot directly account for non-Python
files such as the `tests/hooks/fixtures/*.jsonl` files that the proposal counts
inside the 83-file stay-set.

The proposal acknowledges that false positives need per-file review, but the
review outcome is not captured in the disposition table. As written, the test
can say "many things matched" but cannot prove "no platform test will silently
migrate."

**Required correction:** Make the coverage check produce a reviewable manifest
or table with exact dispositions and counts. The expected result should be a
set comparison against the final `STAYS_PLATFORM` / `MIGRATES_AGENT_RED` /
`NEEDS_REWRITE` inventory, not just "flags all 83 plus possible false
positives."

### F4 - Minor count wording inconsistency should be cleaned up

`-003` says both:

```text
All 69 tests/scripts/*.py files plus 2 supporting files = 69+2 = 71 platform files.
```

and:

```text
13 tests/hooks + 69 tests/scripts + 1 tests/__init__.py = 83 files
```

Live `git ls-files -- 'tests/scripts/*.py'` returns 69 files including
`tests/scripts/__init__.py` and `tests/scripts/conftest.py`. The final 83-file
arithmetic uses the correct interpretation, but the prose/table wording should
be corrected so future E.1 reviewers do not double-count `tests/scripts`.

## Evidence Reviewed

- Live role authority resolved Codex harness `A` to `loyal-opposition` in
  `harness-state/role-assignments.json`; the harness-local operating-role file
  is a legacy pointer only.
- Live `bridge/INDEX.md` showed
  `gtkb-isolation-018-slice-e3-platform-test-disposition` latest status
  `REVISED: bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`.
- `git ls-files -- 'tests/scripts/*.py'` returns 69 files, and every one is
  explicitly referenced in `-003`.
- `git ls-files -- 'tests/hooks/*'` returns 13 tracked files.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition`
  passed against operative file
  `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition`
  reported zero must-apply evidence gaps in advisory Slice-1 mode.
- Targeted `rg` checks outside `tests/scripts/**` and `tests/hooks/**` found
  root `.claude`, `.github/workflows`, `groundtruth_kb`, and `scripts.*`
  dependencies as shown in F1.
- `DELIB-S334-OQ-E3-OPTION-A` exists in MemBase, so this NO-GO does not dispute
  the owner decision itself; it disputes the proposed implementation inventory
  used to operationalize that decision.

## Applicability Preflight

- packet_hash: `sha256:28aa9e54081b8a5b1bd6cb651fe4aa1dbaffa26ec066fb2bd1adf1b2d4eb55cc`
- bridge_document_name: `gtkb-isolation-018-slice-e3-platform-test-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Advisory Clause Preflight

- Bridge id: `gtkb-isolation-018-slice-e3-platform-test-disposition`
- Operative file: `bridge\gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Slice 1 mode: advisory; this report does not block NO-GO.

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking |

## Result

Please revise as
`bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`.

The revision should keep the Option A owner decision intact, but it must make
the platform/app/needs-rewrite disposition complete across all of `tests/`, not
only `tests/scripts` and `tests/hooks`, before E.1 uses the inventory.
