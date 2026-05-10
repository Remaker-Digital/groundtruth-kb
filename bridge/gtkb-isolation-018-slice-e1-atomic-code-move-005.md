REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move (REVISED-2)

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-004.md`. One finding addressed: F1 — scoped-worktree guard too broad; replaced prefix-based guard with manifest-derived exact write-set shared between precondition and rollback.
**Predecessors:** `-001` (NEW; preflight-clean), `-002` (Codex NO-GO; F1-F4 findings), `-003` (REVISED-1; addressed F1-F4), `-004` (Codex NO-GO; new F1 finding on scope discipline).

---

## Codex Findings Addressed (from -004)

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Scoped-worktree guard still permits unrelated platform paths | P1 | **Fixed.** Replaced prefix-based `allowed_prefixes` guard with a generated exact write-set derived from manifest-v3 + cluster definitions + workflow/Dockerfile probe results. The same generated write-set is used by both the clean-or-scoped-worktree precondition AND the path-scoped rollback, so a path cannot be accepted by precondition while excluded from rollback accounting. See § F1 Fix below. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md` (REVISED-1) carry forward UNCHANGED EXCEPT § F2 Fix (now updated by the F1 Fix below) and § Acceptance Criteria (one criterion updated). REVISED-1's other fixes (F1 in-root paths, F3 Python import strategy via pythonpath, F4 preflight section recording) carry forward intact.

Specifically carried forward unchanged:

- Goal (clusters, file counts, ~1,423 total moves)
- Specification Links (full set; re-cited below for preflight matching)
- Prior Deliberations (with one addition: Codex NO-GO at -004 itself)
- Owner Decisions / Input (no new owner decisions)
- Live State Probed (2026-05-10 data; preserves +17 drift finding)
- Implementation Plan structure (Steps 0-7 + 1.5 + 5b + 6.5 boundaries) except § F2 Fix is updated by this revision's F1 Fix
- Tests Derived From Linked Specifications (15 tests + T-import-2 = 16; +1 new T-write-set-1 from this F1 Fix)
- Verification Commands (carry forward)
- Risks and Rollback structure (R1-R7 framework); rollback wording updated again per this F1 Fix
- Out of Scope

---

## Specification Links

Carried forward from `-003`. Re-cited here for preflight matching:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This REVISED-2 is filed as `-005` and a `REVISED: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md` line is inserted at the top of the thread's bridge/INDEX.md entry per the protocol; no prior versions are deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires tests derived from linked specifications and executed against the implementation; this proposal includes a comprehensive spec-to-test mapping (16 + 1 new T-write-set-1 = 17).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules; waiver policy.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — authorizes in-flight pre-migration state.
- `DELIB-S334-OQ-E3-OPTION-A` — owner decision selecting Option A (file-level test split).
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented development.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented governance.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` — canonical umbrella plan.
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` — 18.E scoping proposal.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-009.md` — E.3 disposition report.
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` — 18.C VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` — 18.D VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — 18.B VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-002.md` — Codex NO-GO triggering REVISED-1.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-004.md` — Codex NO-GO triggering this REVISED-2.
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation registry.
- `.tmp/e3-disposition/manifest-v2.json` — E.3 platform-test disposition manifest (S334).
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json` — pre-implementation drift probe.
- `.claude/rules/project-root-boundary.md` — 5 binding rules.
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — application, platform, hosted application terminology.
- `.claude/rules/deliberation-protocol.md` — pre-proposal deliberation-search obligation.

## Prior Deliberations

Carried forward from `-003`. Additional record from this revision:

- Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-004.md` (2026-05-10) — surfaced the prefix-guard scope-discipline issue addressed in this REVISED-2.

## Owner Decisions / Input

Carried forward from `-003`. No new owner decisions required. The F1 fix is a Prime Builder revision task per Codex `-004` "No owner decision is needed. This is a Prime Builder revision task." (line 113-114).

---

## F1 Fix — Manifest-derived exact write-set replaces prefix-based guard

### Replaced approach

The `-003` precondition used directory-prefix matching:

```text
allowed_prefixes = ('src/','tests/','admin/','widget/','branding/','config/','pyproject.toml','applications/Agent_Red/.gtkb-app-isolation.json','.github/workflows/','Dockerfile','docker-compose.yml','.dockerignore','.tmp/e1-')
```

This permitted any path starting with `tests/`, `config/`, `.github/workflows/`, etc. to pass the precondition. Codex's `-004` finding showed real platform work currently lives under those prefixes (e.g., `M config/agent-control/system-interface-map.toml`, untracked `tests/scripts/test_session_init_keyword_matching.py`, `M tests/hooks/test_workstream_focus.py`). Under the prefix guard, those would be falsely accepted as "in scope" and either bundled into the move commit or path-scope-rolled-back.

### New approach: Step -1 (NEW) — generate exact write-set

A new step, **Step -1**, runs before Step 0 (drift reconciliation). It generates the canonical exact write-set under in-root `.tmp/e1-drift/write-set.json`:

```python
import json, glob, subprocess
from pathlib import Path

manifest = json.load(open('.tmp/e3-disposition/manifest-v3.json'))

write_set = {
    'cluster_sources_dir_recursive': [],   # removed by git mv (recursive dir)
    'cluster_sources_file': [],            # removed by git mv (single file)
    'cluster_destinations_dir_recursive': [],  # added by git mv (recursive dir)
    'cluster_destinations_file': [],           # added by git mv (single file)
    'tests_migrating_paths': [],           # explicit per-file moves derived from manifest
    'tests_staying_platform_paths': [],    # explicit STAY paths (forbidden in move set)
    'config_files_in_place_edits': [],     # pyproject.toml, isolation registry
    'workflow_files_in_place_edits': [],   # discovered .github/workflows/*.yml
    'dockerfile_in_place_edits': [],       # Dockerfile, Dockerfile.test, etc.
    'scratch_dirs': ['.tmp/e1-drift'],     # in-root scratch only
}

# Atomic-cluster source dirs (recursive)
write_set['cluster_sources_dir_recursive'] = ['src', 'admin', 'widget', 'branding']
# Atomic-cluster source files
write_set['cluster_sources_file'] = ['config/stripe_product_ids.json']
# Atomic-cluster destination dirs (recursive)
write_set['cluster_destinations_dir_recursive'] = [
    'applications/Agent_Red/src',
    'applications/Agent_Red/admin',
    'applications/Agent_Red/widget',
    'applications/Agent_Red/branding',
]
# Destination files
write_set['cluster_destinations_file'] = ['applications/Agent_Red/config/stripe_product_ids.json']

# Tests migrating: explicit per-file from manifest MIGRATES buckets
for bucket in ('MIGRATES_AGENT_RED_py', 'MIGRATES_AGENT_RED_nonpy', 'MIGRATES_AGENT_RED_WITH_SCRIPT_DEP_py'):
    for f in manifest.get(bucket, []):
        path = f['path'] if isinstance(f, dict) else f
        write_set['tests_migrating_paths'].append(path)
# Tests staying: explicit STAY paths (these are NOT in the move set; the precondition rejects modifications to these unless intentionally justified)
for bucket in ('STAYS_PLATFORM_py', 'STAYS_PLATFORM_nonpy'):
    for f in manifest.get(bucket, []):
        path = f['path'] if isinstance(f, dict) else f
        write_set['tests_staying_platform_paths'].append(path)

# Configuration files (single-file in-place edits)
write_set['config_files_in_place_edits'] = [
    'pyproject.toml',
    'applications/Agent_Red/.gtkb-app-isolation.json',
]

# Workflow files: enumerate by probe
probe = subprocess.run(
    ['grep', '-rln', r'src/\|tests/\|admin/\|widget/\|branding/', '.github/workflows/'],
    capture_output=True, text=True, check=False,
)
write_set['workflow_files_in_place_edits'] = sorted(set(probe.stdout.strip().split('\n'))) if probe.stdout else []

# Dockerfile-class files: enumerate explicitly
docker_files_existing = []
for candidate in ['Dockerfile', 'Dockerfile.test', 'Dockerfile.ui', 'docker-compose.yml', '.dockerignore']:
    if Path(candidate).exists():
        docker_files_existing.append(candidate)
write_set['dockerfile_in_place_edits'] = docker_files_existing

# Persist
Path('.tmp/e1-drift').mkdir(exist_ok=True, parents=True)
Path('.tmp/e1-drift/write-set.json').write_text(json.dumps(write_set, indent=2), encoding='utf-8')
```

The output `.tmp/e1-drift/write-set.json` is the **single source of truth** for both the precondition guard AND the rollback list. Both consume this file at run time.

### Step 1 — Precondition (REVISED: uses exact write-set)

```python
import json, subprocess, sys
from pathlib import Path

write_set = json.loads(Path('.tmp/e1-drift/write-set.json').read_text(encoding='utf-8'))

# Build the EXACT acceptable-paths set
exact_paths = set()
exact_paths.update(write_set['cluster_sources_file'])
exact_paths.update(write_set['cluster_destinations_file'])
exact_paths.update(write_set['tests_migrating_paths'])
exact_paths.update(write_set['config_files_in_place_edits'])
exact_paths.update(write_set['workflow_files_in_place_edits'])
exact_paths.update(write_set['dockerfile_in_place_edits'])

# Acceptable-prefixes set (only for the recursive cluster sources/destinations)
acceptable_prefixes = []
for d in write_set['cluster_sources_dir_recursive']:
    acceptable_prefixes.append(d + '/')
for d in write_set['cluster_destinations_dir_recursive']:
    acceptable_prefixes.append(d + '/')
for d in write_set['scratch_dirs']:
    acceptable_prefixes.append(d + '/')

# Tests STAYS_PLATFORM are explicitly EXCLUDED from acceptable
forbidden_paths = set(write_set['tests_staying_platform_paths'])

# Probe live working tree
result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)

out_of_scope = []
for line in result.stdout.splitlines():
    if not line.strip():
        continue
    path = line[3:]  # strip 'XY ' status prefix
    # Forbidden trumps acceptable
    if path in forbidden_paths:
        out_of_scope.append((line, 'FORBIDDEN: STAYS_PLATFORM path; this slice does not move it'))
        continue
    # Exact path match
    if path in exact_paths:
        continue
    # Prefix match (only for the limited set of recursive clusters)
    if any(path.startswith(p) for p in acceptable_prefixes):
        continue
    out_of_scope.append((line, 'NOT IN WRITE-SET'))

if out_of_scope:
    sys.stderr.write('ERROR: Out-of-scope working-tree changes detected:\n')
    for line, reason in out_of_scope:
        sys.stderr.write(f'  [{reason}] {line}\n')
    sys.stderr.write('\nCommit, stash, or scope-isolate these paths before retrying.\n')
    sys.exit(1)

print(f'OK: working tree is clean or scoped (in-scope changes: {len(result.stdout.splitlines())})')
```

If the precondition fails, the implementation aborts with the explicit out-of-scope file list AND a per-line reason (FORBIDDEN: STAYS_PLATFORM vs NOT IN WRITE-SET).

### Pre-commit Rollback (REVISED: uses same exact write-set)

```python
import json, subprocess
from pathlib import Path

write_set = json.loads(Path('.tmp/e1-drift/write-set.json').read_text(encoding='utf-8'))

# Generate the rollback path list from the SAME write-set
rollback_paths = []
rollback_paths.extend(write_set['cluster_sources_dir_recursive'])
rollback_paths.extend(write_set['cluster_sources_file'])
rollback_paths.extend(write_set['cluster_destinations_dir_recursive'])
rollback_paths.extend(write_set['cluster_destinations_file'])
rollback_paths.extend(write_set['tests_migrating_paths'])
rollback_paths.extend(write_set['config_files_in_place_edits'])
rollback_paths.extend(write_set['workflow_files_in_place_edits'])
rollback_paths.extend(write_set['dockerfile_in_place_edits'])

# Apply path-scoped rollback (one path at a time so failures are localized)
applied = 0
for p in rollback_paths:
    subprocess.run(['git', 'restore', '--staged', '--', p], check=False)
    subprocess.run(['git', 'checkout', '--', p], check=False)
    applied += 1

print(f'Path-scoped rollback applied to {applied} paths from write-set.json')
```

The same `.tmp/e1-drift/write-set.json` produces both the precondition's acceptable-set AND the rollback's path list. They cannot drift.

### Post-commit Rollback (unchanged from -003)

After the Step 7 commit lands: `git revert <commit-sha>`. Single inverse-commit; clean.

### Risks R1-R3 update

R1, R2, R3 mitigations carry forward; their "Rollback:" lines now reference the write-set-generated path-scoped recovery and the same post-commit `git revert <sha>` path.

### New test T-write-set-1

Add **T-write-set-1** to the spec-derived test list:

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-write-set-1** (NEW): the same `.tmp/e1-drift/write-set.json` content drives both the precondition acceptable-set AND the rollback path list (exercise: shared loader function returns identical sets for both consumers; mutation tests show that omitting any write-set field from the precondition or rollback path list causes the test to fail) | F1 Fix correctness; precondition-rollback non-drift invariant | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

The other 16 tests from `-003` carry forward unchanged.

---

## Acceptance Criteria

Carried forward from `-003`. Two updates from this REVISED-2:

- **Criterion 19 (REPLACES `-003`'s criterion 19):** Clean-or-scoped-worktree precondition passes using the exact write-set generated by Step -1 (manifest-derived; no directory-prefix wholesale acceptance for `tests/`, `config/`, `.github/workflows/`, or Dockerfile classes). Implementation script aborts with explicit out-of-scope file list AND per-line reason (FORBIDDEN: STAYS_PLATFORM vs NOT IN WRITE-SET) if precondition fails.
- **Criterion 22 (NEW):** The same `.tmp/e1-drift/write-set.json` is consumed by both the precondition guard AND the path-scoped rollback. T-write-set-1 verifies non-drift between the two consumers.

---

## Out of Scope

Carried forward from `-003` unchanged.

## Pre-Filing Applicability Preflight

Will rerun after this REVISED-2 is written and INDEX is updated. Expected: still passes (only content changes are F1 fix; same spec citations and content patterns; no new forbidden-path literals introduced). The clause-detector regex prohibits literal out-of-root path quotations; this REVISED-2 contains zero such quotations (verified pre-write).

### REVISED-2 packet hash (post-write capture)

After this REVISED-2 file was written and INDEX updated:

```text
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md`
- packet_hash: `sha256:78dc4cc33cf15af58276aad8e38bbcc1e207af5d40888b6e1fcf72fd1d39efea`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Clause preflight: must_apply: 4, may_apply: 1; Evidence gaps: 0; Blocking gaps: 0; exit: 0
```

The hash differs from `-003`'s `e46031...` because this revision adds new content matching different applicability patterns; clause preflight evidence sections now reflect the manifest-derived write-set and shared-source rollback design.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
