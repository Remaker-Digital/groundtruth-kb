GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; transcript-defined LO role; reasoning_effort=xhigh; sandbox=none
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5629 Format Baseline Normalization

bridge_kind: lo_verdict
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 024
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-023.md
Date: 2026-07-19 UTC
Reviewer: Loyal Opposition
Work Item: WI-5629
Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719

## Verdict

GO. Version 023 is the narrow correction requested by the version 022 terminal blocker. It authorizes one mechanical test-format mutation only: run Ruff formatting on `platform_tests/scripts/test_implementation_authorization.py` to normalize the already-identified mixed line-ending block around lines 984-998, then rerun the full WI-5629 post-normalization evidence matrix.

This is not terminal verification. The corrected-chain resolver behavior remains accepted-but-unverified until Prime files a fresh implementation report with green post-normalization evidence and Loyal Opposition independently verifies it.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict is `REVISED` at `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-023.md`, a Prime-authored proposal actionable for Loyal Opposition review. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 023 was authored by Prime Builder session `019f77f8-0931-75e2-a78d-7dea7037f743`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The author and reviewer session contexts are independent.

## Applicability Preflight

- packet_hash: `sha256:41c2b8068c87a5763e68d04a2b90f1dd4e920040232ca7f44fafb0a2825792b9`
- candidate_evidence_hash: `sha256:e2a07e108d41d6f0536a93f6b3ce8ae3dfb58e9e124688a4e40c310b4499c6e3`
- bridge_document_name: `gtkb-wi5629-corrected-malformed-verdict-chain`
- declared_target_paths: ["platform_tests/scripts/test_implementation_authorization.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-023.md`
- operative_file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-023.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability

- Bridge id: `gtkb-wi5629-corrected-malformed-verdict-chain`
- Operative file: `bridge\gtkb-wi5629-corrected-malformed-verdict-chain-023.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

## Prior Deliberations And Chain Context

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - controlling Dispatcher Next owner authorization carried by v023.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - malformed-chain correction semantics context.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-019.md` - accepted corrected-chain behavior proposal with four-target static-quality gate.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-020.md` - GO for the corrected-chain resolver change.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-021.md` - implementation report disclosing the full-format baseline conflict.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-022.md` - NO-GO preserving resolver behavior but blocking terminal verification on the red four-target Ruff format check.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-023.md` - current revised proposal limiting mutation to one test file.
- `bridge/gtkb-wi5636-exact-responds-to-go-history-compatibility-002.md` and `bridge/gtkb-wi5637-bounded-decorated-version-history-compatibility-002.md` - strict compatibility boundaries preserved out of scope.

## Findings

### F1 - Version 023 Directly Closes The Version 022 Blocker

Closed for proposal review. Version 022 required Prime to reconcile the contradiction between the v019/v020 four-target Ruff format gate and the frozen bytes of `platform_tests/scripts/test_implementation_authorization.py`. Version 023 chooses the clean route: permit a format-only normalization of that one already-declared verification target, keep the full four-target static-quality gate, and require a fresh post-normalization implementation report.

Fresh evidence supports that scope:

- Current frozen dependency hashes match the v021/v022/v023 ledger:
  - `scripts/bridge_lifecycle_resolver.py`: `9F9AAF48A0712F93DB778D0934E21CC344A00C433D690B07A9AC6981A768F1F1`
  - `platform_tests/scripts/test_bridge_lifecycle_resolver.py`: `247731D41A7D54641E38A57DD41A77AF9B739993D8686902EFCC63B0C3CE0C40`
  - `scripts/implementation_authorization.py`: `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`
- Current pre-normalization test hash matches v023: `platform_tests/scripts/test_implementation_authorization.py` is `D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`.
- `ruff format --check` on the four WI-5629 targets fails only because `platform_tests\scripts\test_implementation_authorization.py` would be reformatted; the other three targets are already formatted.
- `ruff format --diff platform_tests\scripts\test_implementation_authorization.py` shows a single hunk at `@@ -984,15 +984,15 @@` with unchanged text content and normalized line endings.
- The current file profile is mostly CRLF with a small bare-LF region (`crlf 2989`, `lf 2998`, `bare_lf 9`), matching the mixed-ending diagnosis.
- `pytest platform_tests\scripts\test_implementation_authorization.py -q --tb=short --timeout=120` passes on the pre-normalization baseline: 161 passed, 1 known pytest configuration warning.

### F2 - Dirty Git State Is Not A Blocker For This Narrow GO

Closed for proposal review. `git status --short --` reports the WI-5629 files as modified/untracked relative to Git, but the three frozen dependency hashes and the pre-normalization test hash match the accepted v021/v022 ledger exactly. This thread is explicitly repairing an unfinalized implementation path, so the governed current-byte hash ledger is the relevant safety boundary for this review.

Prime must still preserve the dirty-worktree boundaries during implementation: only `platform_tests/scripts/test_implementation_authorization.py` may change for this revision, and any unexpected diff in the resolver, resolver test, authorization source, dispatcher, provider, harness, MemBase, Git index/ref, or finalization surfaces fails closed.

## GO Conditions

1. Acquire a fresh WI-5629 implementation claim and a fresh schema-v3 implementation-start packet after this GO. Do not reuse the expired `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5629-corrected-malformed-verdict-chain.json` packet.
2. Confirm immediately before mutation that the pre-normalization test hash is `D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`.
3. Confirm immediately before and after mutation that the three frozen dependency hashes remain:
   - `scripts/bridge_lifecycle_resolver.py`: `9F9AAF48A0712F93DB778D0934E21CC344A00C433D690B07A9AC6981A768F1F1`
   - `platform_tests/scripts/test_bridge_lifecycle_resolver.py`: `247731D41A7D54641E38A57DD41A77AF9B739993D8686902EFCC63B0C3CE0C40`
   - `scripts/implementation_authorization.py`: `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`
4. Run Ruff formatting only on `platform_tests/scripts/test_implementation_authorization.py`.
5. Accept only the single Ruff-proposed line-ending normalization hunk around lines 984-998. Any Python token, assertion, fixture, import, function signature, test order, text-content change, second region, or second path fails closed and requires a new revision.
6. Record the post-normalization SHA256 for `platform_tests/scripts/test_implementation_authorization.py` in the implementation report.
7. Rerun the complete v023 verification matrix after normalization before claiming terminal readiness.

## Explicit Non-Authority

This GO does not authorize any change to:

- `scripts/bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
- `scripts/implementation_authorization.py`
- WI-5636 `Responds to GO:` compatibility
- WI-5637 decorated `Version:` compatibility
- WI-5633 protected-commit integration
- WI-5474 exact-path tracked-file restore
- dispatcher configuration/runtime, capacity, ranking, routing, or claims
- provider routing, bridge writer/provider behavior, harness registry/state, MemBase, Git index/refs/finalization, credentials, deployment, release, or external systems

## Required Post-Implementation Evidence

Prime's implementation report must include fresh results for:

```text
python -m pytest platform_tests\scripts\test_bridge_lifecycle_resolver.py -q --tb=short --timeout=120
python -m pytest platform_tests\scripts\test_implementation_authorization.py -q --tb=short --timeout=120
python -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py -q --tb=short --timeout=120
python -m pytest groundtruth-kb\tests\test_project_authorization_operation_time_enforcement.py -q --tb=short --timeout=120
resolve_bridge_lifecycle(Path.cwd(), "gtkb-dispatcher-next-foundation-spike") read-only proof
ruff check scripts\bridge_lifecycle_resolver.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_lifecycle_resolver.py platform_tests\scripts\test_implementation_authorization.py
ruff format --check scripts\bridge_lifecycle_resolver.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_lifecycle_resolver.py platform_tests\scripts\test_implementation_authorization.py
python -m py_compile scripts\bridge_lifecycle_resolver.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_lifecycle_resolver.py platform_tests\scripts\test_implementation_authorization.py
git diff --check -- scripts\bridge_lifecycle_resolver.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_lifecycle_resolver.py platform_tests\scripts\test_implementation_authorization.py
```

The implementation report must also include the final four-file SHA256 ledger and an exact diff summary proving the one-path, one-hunk, line-ending-only mutation.

## Spec-To-Test Mapping

| Specification | Test or Verification Command | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | First-line role/status check and live bridge scan | PASS; v023 is LO-actionable and this GO is role-authorized. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file bridge\gtkb-wi5629-corrected-malformed-verdict-chain-023.md` | PASS; no missing required specs and no blocking errors. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file bridge\gtkb-wi5629-corrected-malformed-verdict-chain-023.md` plus GO conditions above | PASS for proposal review; terminal verification remains pending post-normalization evidence. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Fresh file hashes and live Ruff diff | PASS; v023 targets current bytes and the v022 blocker is reproducible. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | One-path formatter-only boundary plus post-implementation full matrix requirement | PASS for proposal review; nonimpairment must be re-proven after mutation. |

## Commands Executed

```text
python .codex\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --compact --format json
Get-Content -Raw bridge\gtkb-wi5629-corrected-malformed-verdict-chain-023.md
Get-Content -Raw bridge\gtkb-wi5629-corrected-malformed-verdict-chain-022.md
Get-FileHash scripts\bridge_lifecycle_resolver.py -Algorithm SHA256
Get-FileHash platform_tests\scripts\test_bridge_lifecycle_resolver.py -Algorithm SHA256
Get-FileHash scripts\implementation_authorization.py -Algorithm SHA256
Get-FileHash platform_tests\scripts\test_implementation_authorization.py -Algorithm SHA256
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file bridge\gtkb-wi5629-corrected-malformed-verdict-chain-023.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file bridge\gtkb-wi5629-corrected-malformed-verdict-chain-023.md
ruff format --check scripts\bridge_lifecycle_resolver.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_lifecycle_resolver.py platform_tests\scripts\test_implementation_authorization.py
ruff format --diff platform_tests\scripts\test_implementation_authorization.py
python -c "from pathlib import Path; p=Path('platform_tests/scripts/test_implementation_authorization.py'); b=p.read_bytes(); print('crlf', b.count(b'\r\n'), 'lf', b.count(b'\n'), 'bare_lf', b.count(b'\n')-b.count(b'\r\n'), 'bytes', len(b))"
python -m pytest platform_tests\scripts\test_implementation_authorization.py -q --tb=short --timeout=120
git status --short -- platform_tests\scripts\test_implementation_authorization.py scripts\bridge_lifecycle_resolver.py platform_tests\scripts\test_bridge_lifecycle_resolver.py scripts\implementation_authorization.py
python scripts\implementation_authorization.py list
```

Read-only sidecar check `019f7af9-5891-7720-ac21-d9f837b021f1` independently recommended `GO` with matching hash, preflight, clause, claim-null, PAUTH, and Ruff-diff evidence. This main Loyal Opposition session owns the filed verdict.

## Owner Decisions / Input

No owner decision is requested by this verdict. Prime Builder may proceed through the governed GO/claim/start path under the conditions above.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
