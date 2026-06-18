NEW

# Defect-Fix Proposal - managed-artifacts.toml lists deleted/unregistered hook.scheduler (scheduler.py): perpetual doctor [ADD] noise + unsafe upgrade re-add

bridge_kind: prime_proposal
Document: gtkb-managed-artifacts-retire-scheduler-hook-row
Version: 001
Date: 2026-06-17 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8851dbf6-a9fe-4ab9-a49f-d13f405e8711
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; Prime Builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4628

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/tests/fixtures/registry-id-set.txt", "groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv", "groundtruth-kb/tests/test_scaffold_consumes_resolver.py"]

Reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001) defect-fix: reconcile the managed-artifact registry with the already-decided retirement of scheduler.py.

## Claim

`groundtruth-kb/templates/managed-artifacts.toml` still lists `hook.scheduler` (template `hooks/scheduler.py` -> target `.claude/hooks/scheduler.py`), but `scheduler.py` was deleted (commit 182665e81, 2026-06-12), is unregistered (0 references in `.claude/settings.json`), and is NOT a governance gate — it is a retired `SCHEDULE.md` reader in the retired poller/scheduler family. The owner confirmed its retirement via the S445 AskUserQuestion ("Retired — remove registry row"). The stale registry row makes `gt project doctor` report a missing managed file and would make `gt project upgrade --apply` re-add an unused hook. This fix removes the row and reconciles the two registry fixtures and the one test that mirrors the registry ID set.

## Defect / Reproduction

- Reproduce (upgrade): `gt project upgrade --dry-run` → `[ADD] .claude/hooks/scheduler.py — Managed file missing — will copy from template`. This is the only managed-file ADD action; running `--apply` would re-add the intentionally-deleted hook.
- Reproduce (doctor): `python -m groundtruth_kb project doctor` managed-artifact-drift treats `scheduler.py` as a managed file that is missing on disk (the single genuine missing managed FILE found in the S445 governance-hooks investigation, workflow ww94bvn0k).
- Root cause: `groundtruth-kb/templates/managed-artifacts.toml:94-97` retains the `hook.scheduler` record. The registry fixtures mirror it (`groundtruth-kb/tests/fixtures/registry-id-set.txt:35` = `hook.scheduler`; `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv:33` = `hook.scheduler\tgt-kb-managed`), and `groundtruth-kb/tests/test_scaffold_consumes_resolver.py:35` lists `"hook.scheduler"` in its expected-IDs list. Removing only the toml row would break the registry tests; all four files must be reconciled together.
- Provenance: scheduler.py deleted in 182665e81 (2026-06-12); 0 registrations in settings.json; the poller/scheduler family is retired (OS pollers halted 2026-04-25; smart-poller retired 2026-05-09 per DELIB-1545).

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/templates/managed-artifacts.toml`, `groundtruth-kb/tests/fixtures/registry-id-set.txt`, `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv`, `groundtruth-kb/tests/test_scaffold_consumes_resolver.py`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - Governs this proposal's lighter path: WI-4628 is origin=defect, introduces no new API/CLI/behavior beyond removing the stale row, requires no new/revised requirement, and is small + single-concern (4 files, ~7 net deleted lines, one retirement reconciliation). Covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active project membership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites every relevant governing specification in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps each acceptance criterion to an executed check (registry tests + upgrade dry-run + doctor run).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Satisfied by the `Project Authorization` / `Project` / `Work Item` header lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - This change flows through the bridge protocol under bridge authority.
- `GOV-STANDING-BACKLOG-001` - WI-4628 is a standing-backlog work item captured per the strategic self-improvement directive; this proposal implements it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The fix is delivered as durable artifacts (work item, proposal, fixture/test reconciliation, report).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Same artifact-oriented delivery principle applied to the fix.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Reconciling the managed-artifact registry with a retired artifact is a lifecycle-trigger action; satisfied here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The managed-artifact registry governs scaffold placement of platform artifacts; this change only removes a retired entry and does not alter the platform/application placement contract.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner authorization derives from the S445 AUQ ("Retired — remove registry row") plus the fast-lane standing authorization; this change does not alter AUQ policy.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - No live hook-surface change; scheduler.py is already deleted and unregistered in both `.claude/settings.json` and `.codex/hooks.json`. Cited for completeness.

## Prior Deliberations

<!-- Reviewed and pruned from helper pre-population. -->

- `DELIB-1545` - Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement. Establishes that the poller/scheduler family is retired — the context that makes scheduler.py's deletion correct and this registry reconciliation appropriate.
- `DELIB-1204` - Bridge thread: gtkb-managed-artifact-registry. The managed-artifact registry this proposal edits.
- `DELIB-20264637` - GT-KB Project Boundary and Upgrade Hardening Implementation - Codex Review. Upgrade behavior context (the `gt project upgrade` path that would otherwise re-add scheduler.py).
- `DELIB-2366` - Loyal Opposition Review - Governance-Adoption Doctor Check. Doctor-check context (the surface that flags the missing managed file).

## Owner Decisions / Input

- S445 AskUserQuestion (2026-06-17): owner selected "Retired — remove registry row" for scheduler.py, confirming the scheduler feature is retired. This is the owner decision authorizing the registry reconciliation. (The AUQ answer is the durable owner-decision evidence; recorded in this session's transcript.)
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, "Reliability fast-lane standing authorization") covers implementation of fast-lane-eligible defect WIs in `PROJECT-GTKB-RELIABILITY-FIXES` through active project membership, per `GOV-RELIABILITY-FAST-LANE-001` — no per-fix owner-approval packet required.
- No further owner decision is required to implement this fast-lane fix.

## Requirement Sufficiency

Existing requirements sufficient. The scheduler/poller family retirement is already established (OS pollers halted 2026-04-25; smart-poller retired 2026-05-09 per DELIB-1545; scheduler.py deleted 2026-06-12), and the owner confirmed scheduler retirement via the S445 AUQ. This change reconciles the managed-artifacts registry with that existing decision; it introduces no new or revised requirement.

## Proposed Scope

IP-1 - `groundtruth-kb/templates/managed-artifacts.toml`: remove the `hook.scheduler` record (the `[[...]]` block at lines ~94-97: `id = "hook.scheduler"`, `template_path = "hooks/scheduler.py"`, `target_path = ".claude/hooks/scheduler.py"`, `initial_profiles = [...]`).

IP-2 - `groundtruth-kb/tests/fixtures/registry-id-set.txt`: remove the `hook.scheduler` line (line ~35).

IP-3 - `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv`: remove the `hook.scheduler\tgt-kb-managed` line (line ~33).

IP-4 - `groundtruth-kb/tests/test_scaffold_consumes_resolver.py`: remove the `"hook.scheduler",` entry from the expected-IDs list (line ~35).

Out of scope (noted, not changed by this fix): `groundtruth-kb/docs/reference/templates.md` and historical reports mention scheduler; the reports are historical evidence (left as-is). `groundtruth-kb/tests/test_intake.py:499` uses `python .claude/hooks/scheduler.py` only as a settings-classifier fixture string, independent of the registry, so it is unaffected and unchanged. The retired template file `groundtruth-kb/templates/hooks/scheduler.py` may be removed in a separate cleanup, but is left in place here to keep this change to the registry-row reconciliation single-concern.

## Specification-Derived Verification Plan

| Spec / Acceptance criterion | Derived test / command | Expected result |
|---|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` eligibility | Manual: WI-4628 origin=defect, ~7 net deleted lines, single-concern | Eligible |
| Upgrade no longer re-adds scheduler | `gt project upgrade --dry-run` | No `[ADD] .claude/hooks/scheduler.py` action present |
| Registry consistency preserved | `python -m pytest groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_consumes_resolver.py groundtruth-kb/tests/test_ownership_loader_agreement.py groundtruth-kb/tests/test_registry_ast_coverage.py -q` | PASS (registry + fixtures + expected-IDs reconciled; no orphan/missing-ID failures) |
| Doctor no longer flags scheduler missing-file | `python -m groundtruth_kb project doctor` | managed-artifact-drift no longer reports `scheduler.py` as a missing managed file; no new failures introduced |
| Lint / format | `ruff check` + `ruff format --check` on the changed `.py` (test file) | Clean (both gates) |

## Acceptance Criteria

1. `hook.scheduler` is removed from `templates/managed-artifacts.toml`, `registry-id-set.txt`, `registry-ownership-snapshot.tsv`, and the expected-IDs list in `test_scaffold_consumes_resolver.py`.
2. `gt project upgrade --dry-run` no longer proposes `[ADD] .claude/hooks/scheduler.py`.
3. The registry/scaffold/ownership tests pass; `gt project doctor` no longer reports `scheduler.py` as a missing managed file and introduces no new failures.
4. `ruff check` and `ruff format --check` are clean on the changed test file.

## Risks / Rollback

- Risk: LOW. The change removes references to an already-deleted, unregistered, retired artifact across 4 files (~7 deleted lines), single-concern (scheduler retirement reconciliation). The registry/scaffold/ownership tests are the mechanical guard that no other consumer expects `hook.scheduler`.
- The grep survey confirmed the only live references are the four target files; `test_intake.py` is a classifier fixture (unaffected) and the docs/reports are historical evidence.
- Rollback: `git revert` / restore the four files. No data, schema, or runtime-state migration; the only runtime effect is that `gt project doctor` / `gt project upgrade` stop flagging the retired scheduler.py.

## Files Expected To Change

- `groundtruth-kb/templates/managed-artifacts.toml`
- `groundtruth-kb/tests/fixtures/registry-id-set.txt`
- `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv`
- `groundtruth-kb/tests/test_scaffold_consumes_resolver.py`

## Recommended Commit Type

`fix`
