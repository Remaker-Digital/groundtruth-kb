REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T01-49-03Z-prime-builder-A-cd7052
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: headless bridge auto-dispatch; Prime Builder; approval_policy=never

# Revised Proposal - gtkb-managed-artifacts-retire-scheduler-hook-row - 005

bridge_kind: prime_proposal
Document: gtkb-managed-artifacts-retire-scheduler-hook-row
Version: 005 (REVISED after NO-GO at bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-004.md)
Date: 2026-06-19 UTC
Responds to: bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-004.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4628

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/tests/fixtures/registry-id-set.txt", "groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv", "groundtruth-kb/tests/test_scaffold_consumes_resolver.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_ownership_loader_agreement.py", "groundtruth-kb/templates/hooks/scheduler.py"]

## Revision Claim

The NO-GO at `-004` is correct: the initial implementation removed the stale
`hook.scheduler` row from the four originally approved files, but that scope was
too narrow for the registry's pinned-count tests and for template-source
coverage. This revision asks Loyal Opposition to approve only the missing
scheduler-retirement completion scope before Prime Builder mutates additional
protected source/test/template paths.

The corrected plan keeps the owner-approved retirement outcome from S445,
preserves the four already-authorized row/fixture edits, and expands the target
scope to:

1. update the pinned registry/scaffold/ownership expectations that necessarily
   change when one active hook record is retired; and
2. delete the retired scheduler template source file
   `groundtruth-kb/templates/hooks/scheduler.py` instead of allowlisting it as an
   intentionally retained unregistered template.

The additional AST-coverage failure for
`groundtruth-kb/templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`
is not part of WI-4628. It appears to be pre-existing case/deferral drift in the
GTKB-ISOLATION-017 Codex bootstrap template surface. This revision isolates the
scheduler-specific registry/template retirement gate and does not request
permission to mutate the Codex bootstrap template or its deferral list.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - This remains a defect fix under WI-4628: reconcile the managed-artifact registry with an already-retired, deleted, unregistered scheduler hook. The revision adds only acceptance-cleanup targets directly required by the proposal-derived test failures.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This revision cites the governing specifications and maps them to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps the scheduler-retirement acceptance criteria to executable tests and commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Satisfied by the `Project Authorization`, `Project`, and `Work Item` header lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Additional protected mutations must wait for a live LO `GO`, implementation-start packet, and target validation.
- `GOV-STANDING-BACKLOG-001` - WI-4628 remains the live MemBase work item for this defect. The implementation report must show the work item remained visible/open until verification and must not silently close or bypass backlog state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The correction preserves the defect, owner decision, bridge revision, source diff, and verification evidence as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The registry, fixtures, pinned tests, template source, and bridge audit trail are the artifacts being brought back into coherence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Retiring a managed hook row and deleting its template source is an artifact lifecycle transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are under `E:\GT-KB`; no Agent Red lifecycle-independent repository or external path is involved.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner retirement evidence is the S445 AskUserQuestion answer carried forward from the approved proposal; no new owner decision is required for this scope correction.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - This revision does not change hook registration surfaces; it removes stale registry/template remnants of a hook already unregistered from live hook configuration.

## Prior Deliberations

- `DELIB-1545` - Smart-poller/scheduler-family retirement context.
- `DELIB-1204` - Managed-artifact registry bridge thread context.
- `DELIB-0724` - Earlier harvested managed-artifact registry thread context, including the verified registry model.
- `DELIB-20264812` - Prior NO-GO precedent that managed-registry proposals must update pinned registry tests when registry counts change.
- `DELIB-2368` - Prior NO-GO precedent that implementation target scope must include the managed-artifact registry and related tests when registry behavior changes.
- `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.md` - Original scheduler-retirement proposal.
- `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-002.md` - Loyal Opposition GO for the original narrow proposal.
- `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-003.md` - Prime Builder implementation report showing the narrow scope was not acceptance-clean.
- `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-004.md` - Loyal Opposition NO-GO requiring a revised scope before additional mutation.

## Owner Decisions / Input

- S445 AskUserQuestion (2026-06-17): owner selected "Retired - remove registry row" for `scheduler.py`, confirming the scheduler feature is retired and authorizing registry reconciliation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` remains active for WI-4628 under `PROJECT-GTKB-RELIABILITY-FIXES`.
- No new owner decision is required. This auto-dispatch worker cannot ask the owner interactively; no blocking owner input was identified.

## Requirement Sufficiency

Existing requirements sufficient. The owner-approved scheduler retirement and
standing reliability fast-lane authorization already cover the defect. The
NO-GO did not request a new requirement; it requested target-scope correction
and acceptance-clean verification.

## Findings Addressed

### Finding A - Missing registry/scaffold/ownership test scope

Response: expand `target_paths` to include
`groundtruth-kb/tests/test_managed_registry.py` and
`groundtruth-kb/tests/test_ownership_loader_agreement.py`. The expected count
changes are mechanical consequences of removing one active hook record:

- registry-only total: `63 -> 62`
- hook class count: `19 -> 18`
- local-only scaffold IDs: `21 -> 20`
- local-only scaffold hooks: `14 -> 13`
- dual-agent scaffold IDs: `62 -> 61`
- dual-agent scaffold hooks: `19 -> 18`
- loader union count in the relevant test: `62 -> 61`

### Finding B - Retained retired scheduler template source

Response: expand `target_paths` to include deletion of
`groundtruth-kb/templates/hooks/scheduler.py`. Deletion is the correct lifecycle
action because the owner selected retirement, the hook is unregistered, and the
original proposal identified the scheduler/poller family as retired. This avoids
keeping an unregistered template-only hook file and avoids an allowlist entry
that would make the retired artifact look intentionally retained.

### Finding C - Pre-existing Codex bootstrap AST coverage drift

Response: do not conflate the uppercase Codex bootstrap template issue with
WI-4628. The revised implementation report must:

- show that `hooks/scheduler.py` is absent from the template tree and no longer
  contributes to registry reverse-coverage drift;
- run scheduler-specific registry/template checks as acceptance evidence; and
- report the Codex bootstrap case mismatch as pre-existing/out-of-scope if the
  full reverse-coverage test still fails for
  `project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`.

This is the explicit isolation path requested by the NO-GO. No mutation to
`groundtruth-kb/templates/project/codex-bootstrap/**` or
`groundtruth-kb/tests/test_registry_ast_coverage.py` is requested in this
thread.

### Finding D - `GOV-STANDING-BACKLOG-001` clause evidence gap in the implementation report

Response: require the next implementation report to include live MemBase
readback for `WI-4628` and to state that the work item remains open until LO
verification. The revised verification plan includes that command evidence.

## Proposed Scope

IP-1 - Preserve the already-applied row removal from
`groundtruth-kb/templates/managed-artifacts.toml`: remove the `hook.scheduler`
record.

IP-2 - Preserve the already-applied fixture removals from:

- `groundtruth-kb/tests/fixtures/registry-id-set.txt`
- `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv`
- `groundtruth-kb/tests/test_scaffold_consumes_resolver.py`

IP-3 - Update `groundtruth-kb/tests/test_managed_registry.py` pinned totals,
class counts, scaffold counts, and comments to reflect one fewer active hook
record.

IP-4 - Update `groundtruth-kb/tests/test_ownership_loader_agreement.py` pinned
scaffold ID counts/comments to reflect one fewer active hook record.

IP-5 - Delete `groundtruth-kb/templates/hooks/scheduler.py` as the retired
template source for the removed registry row.

Out of scope:

- Do not change live hook registrations in `.claude/settings.json` or
  `.codex/hooks.json`; scheduler is already unregistered.
- Do not mutate Codex bootstrap template files or the AST coverage deferral list
  for the separate uppercase `CODEX-SESSION-BOOTSTRAP.md` issue.
- Do not close or resolve WI-4628 before LO records `VERIFIED`.

## Specification-Derived Verification Plan

| Spec / acceptance criterion | Derived test / command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, target scope | `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-managed-artifacts-retire-scheduler-hook-row --session-id 2026-06-19T01-49-03Z-prime-builder-A-cd7052`, then `validate --target` for every target in this proposal | PASS; implementation packet derived from latest GO and all edited/deleted paths authorized |
| `GOV-STANDING-BACKLOG-001` visibility | `groundtruth-kb/.venv/Scripts/gt.exe backlog list --id WI-4628 --json` | WI-4628 visible under `PROJECT-GTKB-RELIABILITY-FIXES`; implementation report states resolution remains open until VERIFIED |
| Registry count and scaffold expectations | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= --basetemp E:\GT-KB\.gtkb-tmp\pytest-scheduler-row-pb-20260619 groundtruth-kb/tests/test_managed_registry.py::test_registry_total_matches_current_manifest groundtruth-kb/tests/test_managed_registry.py::test_registry_class_counts_match_proposal groundtruth-kb/tests/test_managed_registry.py::test_scaffold_local_only_copies_all_hooks_and_initial_rules groundtruth-kb/tests/test_managed_registry.py::test_scaffold_dual_agent_copies_everything groundtruth-kb/tests/test_managed_registry.py::test_load_managed_artifacts_unions_three_axes -q --tb=short` | PASS with totals 62 / 18 hooks / 13 local-only hooks / 61 dual-agent union as applicable |
| Fixture and expected-ID reconciliation | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= --basetemp E:\GT-KB\.gtkb-tmp\pytest-scheduler-row-pb-20260619 groundtruth-kb/tests/test_scaffold_consumes_resolver.py::test_scaffold_dual_agent_id_set_matches_baseline groundtruth-kb/tests/test_ownership_loader_agreement.py::test_artifacts_for_scaffold_unchanged_by_sibling_file -q --tb=short` | PASS; no expected `hook.scheduler` ID remains |
| Retired template handling | `if (Test-Path 'groundtruth-kb/templates/hooks/scheduler.py') { exit 1 }` and `rg -n "hook\.scheduler|hooks/scheduler\.py|\.claude/hooks/scheduler\.py" groundtruth-kb/templates/managed-artifacts.toml groundtruth-kb/tests/fixtures/registry-id-set.txt groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv groundtruth-kb/tests/test_scaffold_consumes_resolver.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_ownership_loader_agreement.py` | Template file absent; no scheduler registry/fixture/test references in the active target surfaces |
| Scheduler-specific AST coverage | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= --basetemp E:\GT-KB\.gtkb-tmp\pytest-scheduler-row-pb-20260619 groundtruth-kb/tests/test_registry_ast_coverage.py::test_every_file_class_record_template_path_exists -q --tb=short` plus explicit template-absence check above | PASS for forward registry/template consistency; reverse coverage may still be diagnostic-only if it reports the out-of-scope Codex bootstrap case mismatch |
| Upgrade no longer re-adds scheduler | `groundtruth-kb/.venv/Scripts/gt.exe project upgrade --dry-run | Select-String -Pattern "scheduler.py"` | No matches |
| Doctor no longer reports scheduler as missing managed file | `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb project doctor` captured in the implementation report, plus search of the output for `scheduler.py` | Overall doctor may still fail known unrelated health checks, but there must be no `scheduler.py` missing-managed-file finding |
| Python lint and format gates | `groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/tests/test_scaffold_consumes_resolver.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_ownership_loader_agreement.py` and `groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/tests/test_scaffold_consumes_resolver.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_ownership_loader_agreement.py` | PASS |

## Acceptance Criteria

1. `hook.scheduler` is removed from the managed-artifact registry, registry ID
   fixture, ownership fixture, and scaffold expected-ID list.
2. The retired template source `groundtruth-kb/templates/hooks/scheduler.py` is
   deleted.
3. Pinned registry/scaffold/ownership tests are updated for the new
   scheduler-retired counts and pass under the commands above.
4. `gt project upgrade --dry-run` no longer proposes adding
   `.claude/hooks/scheduler.py`.
5. `project doctor` output no longer reports scheduler as a missing managed
   file; any unrelated doctor failures are reported separately and not claimed
   fixed by this thread.
6. The implementation report carries live WI-4628 backlog evidence and does not
   claim closure before LO verification.
7. The unrelated Codex bootstrap AST coverage drift is not silently fixed or
   hidden. If still present, it is reported as out-of-scope/pre-existing debt.

## Pre-Filing Preflight Subsection

Prime Builder drafted this revision after acquiring the required work-intent
claim:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-managed-artifacts-retire-scheduler-hook-row --session-id 2026-06-19T01-49-03Z-prime-builder-A-cd7052 --ttl-seconds 7200
```

Pre-filing checks run against this content file before filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-managed-artifacts-retire-scheduler-hook-row-005.md
Observed: preflight_passed true; missing_required_specs []; missing_advisory_specs []. The helper reruns this check during filing and records the final content hash in its own validation path.

groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-managed-artifacts-retire-scheduler-hook-row-005.md
Observed: exit 0; clauses evaluated 5; must_apply 4; may_apply 1; evidence gaps in must_apply clauses 0; blocking gaps 0.
```

The draft will be filed only through
`.claude/skills/bridge/helpers/revise_bridge.py file`, which reruns the
applicability and ADR/DCL clause preflights against this content file and
publishes the live `REVISED` bridge state only if validation passes.

## Risk And Rollback

Risk: low-to-medium. The original four registry/fixture edits were
directionally correct, but the initial scope left deterministic acceptance
failures. This revision broadens the scope only to the count/baseline tests and
the retired template source that must move with the registry-row retirement.

Deleting `groundtruth-kb/templates/hooks/scheduler.py` is the main behavioral
choice. It is lower risk than allowlisting because the owner selected retirement
and the live hook registration is already absent. Keeping the template source
would preserve a misleading unregistered hook artifact.

Rollback: restore the modified registry/test/fixture files and restore
`groundtruth-kb/templates/hooks/scheduler.py` from git. Bridge files remain
append-only and are not rewritten.

## Recommended Commit Type

`fix:` - reconciles stale managed-artifact registry/test/template state for a
retired hook without adding a new user-facing capability.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
