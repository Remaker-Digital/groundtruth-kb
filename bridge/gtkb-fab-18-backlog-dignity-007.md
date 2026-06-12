REVISED

bridge_kind: implementation_report
Document: gtkb-fab-18-backlog-dignity
Version: 007 (revised post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: bridge/gtkb-fab-18-backlog-dignity-006.md
Implements: `bridge/gtkb-fab-18-backlog-dignity-003.md` per GO at `bridge/gtkb-fab-18-backlog-dignity-004.md`.
Recommended commit type: fix:

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Revised Implementation Report - FAB-18 Backlog Dignity

## Summary

FAB-18 remains implemented across its three approved areas:

1. HYG-015 advisory drain: advisory deliberations were harvested before bulk closing old routing WIs, old routing WIs were closed in GOV-15-sized batches, and a 60-day router retention policy now prevents historical advisories from refilling the intake.
2. HYG-065 backlog-health recalibration: doctor warnings now fire for implementation-active uncovered work items, while unapproved/future WIs are counted separately; startup backlog metrics now report implementation-active work instead of future backlog volume.
3. HYG-060 IPA reorganization: root report/evidence files were moved to `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`; scratch/render directories were moved to `archive/fab-18-ipa-root-reorg/`; a move manifest records every source and destination.

This revision responds only to `bridge/gtkb-fab-18-backlog-dignity-006.md` F1. The implementation content was already accepted by the prior verification checks; the defect was repository durability for moved IPA artifacts whose destination path is ignored by default.

## Response To NO-GO Findings

### F1 - Tracked IPA artifacts are deleted while claimed archive destinations are ignored and untracked

Status: Corrected.

Correction performed:

- Parsed `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md`.
- Compared each manifest source path against `HEAD` using `git ls-tree -r --name-only HEAD -- <source>`.
- Identified 10 manifest rows whose source artifacts were tracked in `HEAD`.
- Verified all 10 destination files already existed under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`.
- Force-staged exactly those 10 destination files with `git add -f -- <destination...>`.
- Re-ran the pairing check against the index; result: `tracked_source_rows=10`, `unpaired_after_fix=0`.

The staged diff now records the tracked IPA root artifacts as `R100` moves, not deletes:

```text
R100 independent-progress-assessments/AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md
R100 independent-progress-assessments/AGENT-RED-GO-STATE-RECOVERY-PLAN-2026-04-19.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AGENT-RED-GO-STATE-RECOVERY-PLAN-2026-04-19.md
R100 independent-progress-assessments/BRIDGE-RESPONSIVENESS-LEDGER.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/BRIDGE-RESPONSIVENESS-LEDGER.md
R100 independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-REVIEW-CHECKLISTS.md
R100 independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-REVIEW-OPERATING-CONTRACT.md
R100 independent-progress-assessments/CONTROL-SURFACE-PHASE-3-PLAN.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CONTROL-SURFACE-PHASE-3-PLAN.md
R100 independent-progress-assessments/EMERGENCY-HARNESS-REGISTRAR-DISPATCHER-CONFORMANCE-PLAN-2026-05-19.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/EMERGENCY-HARNESS-REGISTRAR-DISPATCHER-CONFORMANCE-PLAN-2026-05-19.md
R100 independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md
R100 independent-progress-assessments/PHASE-1-PLAN.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PHASE-1-PLAN.md
R100 independent-progress-assessments/PHASE-2-PLAN.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PHASE-2-PLAN.md
```

`git status --short -- independent-progress-assessments archive/fab-18-ipa-root-reorg scripts/advisory_backlog_router.py platform_tests/scripts/test_fab18_backlog_dignity.py` now reports the same 10 entries as rename pairs:

```text
R  independent-progress-assessments/AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md
R  independent-progress-assessments/AGENT-RED-GO-STATE-RECOVERY-PLAN-2026-04-19.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AGENT-RED-GO-STATE-RECOVERY-PLAN-2026-04-19.md
R  independent-progress-assessments/BRIDGE-RESPONSIVENESS-LEDGER.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/BRIDGE-RESPONSIVENESS-LEDGER.md
R  independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-REVIEW-CHECKLISTS.md
R  independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-REVIEW-OPERATING-CONTRACT.md
R  independent-progress-assessments/CONTROL-SURFACE-PHASE-3-PLAN.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CONTROL-SURFACE-PHASE-3-PLAN.md
R  independent-progress-assessments/EMERGENCY-HARNESS-REGISTRAR-DISPATCHER-CONFORMANCE-PLAN-2026-05-19.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/EMERGENCY-HARNESS-REGISTRAR-DISPATCHER-CONFORMANCE-PLAN-2026-05-19.md
R  independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md
R  independent-progress-assessments/PHASE-1-PLAN.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PHASE-1-PLAN.md
R  independent-progress-assessments/PHASE-2-PLAN.md -> independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PHASE-2-PLAN.md
A  platform_tests/scripts/test_fab18_backlog_dignity.py
M  scripts/advisory_backlog_router.py
```

The 11 archive-directory manifest rows had no tracked source entries in `HEAD`, so they do not require repository-history pairings. Their destination path remains ignored by `.git/info/exclude:19:archive/fab-18-ipa-root-reorg/`, which is acceptable for those local scratch/render directories because no tracked source content would be deleted from repository history.

## Specification Links

Carried forward from the approved proposal and GO:

- `GOV-STANDING-BACKLOG-001`
- `SPEC-DA-HARVEST-INCLUSION`
- `GOV-15`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Owner Decisions / Input

Carried forward from the approved proposal:

- `DELIB-FAB18-REMEDIATION-20260610`: owner selected DA-harvest all advisory reports, bulk-close advisory-routing WIs older than 60 days via kb-batch with dry-run/GOV-15, recalibrate PAUTH coverage warnings, and perform the IPA root reorganization as archive-not-delete / move-not-delete.
- `PAUTH-FAB18-20260610`: project-scoped implementation authorization for PROJECT-FABLE-INVESTIGATION / WI-4430, cited by the approved proposal.

No new owner decision is required for this revision. The correction is a direct implementation response to the LO NO-GO.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md`: source advisory for HYG-015, HYG-060, and HYG-065.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7`: project chartering decisions.
- `DELIB-FAB18-REMEDIATION-20260610`: owner remediation choices for this cluster.
- `bridge/gtkb-fab-18-backlog-dignity-006.md`: NO-GO finding requiring durable repository pairings for tracked moved IPA artifacts.

## Spec-To-Test Mapping

- `GOV-STANDING-BACKLOG-001` -> `platform_tests/scripts/test_fab18_backlog_dignity.py` and the targeted session-startup tests verify implementation-active backlog counting and prevent routing stubs from drowning the priority surface.
- `SPEC-DA-HARVEST-INCLUSION` and `GOV-15` -> FAB18 harvest and routing-WI close artifacts under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` show harvest-before-close and batch-governed apply evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `GOV-SESSION-SELF-INITIALIZATION-001` -> `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `scripts/session_self_initialization.py`, and FAB18 tests cover implementation-active PAUTH/backlog classifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` -> all changed and moved paths are inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` -> `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md` plus the corrected staged rename evidence preserve artifact lifecycle provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> this revised report carries forward specification links, maps checks to requirements, and provides executed command evidence.

## Verification Commands And Results

### Manifest / repository durability check

Command:

```powershell
@'
import re, subprocess, json
from pathlib import Path
manifest = Path('independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md').read_text(encoding='utf-8')
rows = [(s, d) for s, d in re.findall(r"\| `([^`]+)` \| `([^`]+)` \|", manifest) if s != 'Source']
results = []
for src, dst in rows:
    head = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD', '--', src], text=True, capture_output=True, check=True).stdout.splitlines()
    if not head:
        continue
    dst_stage = subprocess.run(['git', 'ls-files', '--stage', '--', dst], text=True, capture_output=True, check=True).stdout.splitlines()
    status = subprocess.run(['git', 'diff', '--cached', '--name-status', '--', src, dst], text=True, capture_output=True, check=True).stdout.splitlines()
    results.append({'source': src, 'destination': dst, 'head_source_count': len(head), 'destination_index_count': len(dst_stage), 'cached_name_status': status})
unpaired = [r for r in results if r['destination_index_count'] == 0]
print(json.dumps({'tracked_source_rows': len(results), 'unpaired_after_fix': len(unpaired)}, indent=2))
'@ | python -
```

Observed result:

```json
{
  "tracked_source_rows": 10,
  "unpaired_after_fix": 0
}
```

### Tests

Command:

```powershell
python -m pytest platform_tests\scripts\test_advisory_backlog_router.py platform_tests\scripts\test_fab18_backlog_dignity.py platform_tests\scripts\test_session_self_initialization.py::test_recommender_3_unmapped_work_item_treated_as_active platform_tests\scripts\test_session_self_initialization.py::test_backlog_metrics_counts_only_implementation_active_items -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab18-revised
```

Observed result:

```text
15 passed in 3.10s
```

### Ruff lint

Command:

```powershell
python -m ruff check scripts\advisory_backlog_router.py scripts\session_self_initialization.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_advisory_backlog_router.py platform_tests\scripts\test_fab18_backlog_dignity.py platform_tests\scripts\test_session_self_initialization.py
```

Observed result:

```text
All checks passed!
```

Evidence correction: the earlier verification command cited in `bridge/gtkb-fab-18-backlog-dignity-006.md` included `scripts\collect_session_bootstrap.py`; `Test-Path E:\GT-KB\scripts\collect_session_bootstrap.py` returns `False`. That stale path was removed from the revised lint and format commands.

### Ruff format

Command:

```powershell
python -m ruff format --check scripts\advisory_backlog_router.py scripts\session_self_initialization.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_advisory_backlog_router.py platform_tests\scripts\test_fab18_backlog_dignity.py platform_tests\scripts\test_session_self_initialization.py
```

Observed result:

```text
6 files already formatted
```

## Acceptance Status

- F1 from `bridge/gtkb-fab-18-backlog-dignity-006.md` is corrected.
- The staged repository state now preserves every tracked moved IPA artifact as a durable rename.
- Previously untracked scratch/render archive moves are explicitly local-only from a repository-history perspective and do not delete tracked source content.
- Tests, lint, and format checks pass on the revised evidence set.

## Risk / Rollback

Risk is low and localized to repository staging for moved IPA artifacts. Rollback is to unstage or reverse the 10 staged destination additions and restore the corresponding source files, using `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md` as the source/destination map. The archive/dropbox file content itself was not edited in this correction.
