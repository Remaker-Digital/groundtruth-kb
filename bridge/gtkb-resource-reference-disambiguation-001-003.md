NEW

# Implementation Report - GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001

**Author:** Prime Builder (Codex, harness A)  
**Implemented:** 2026-05-06  
**Subject:** `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001 - External resource identity registry and confusion audit`  
**Prior review:** `bridge/gtkb-resource-reference-disambiguation-001-002.md` (`GO`)

## Claim

GT-KB now has a governed external resource alias registry, a deterministic
resolver/check script, exact CI-evidence validation helpers, release-gate
registry enforcement, and compact operating-state/dashboard visibility. The
implementation keeps Agent Red resources marked as separate-project context and
does not mutate GitHub, Azure, SonarCloud, PyPI, DNS, credentials, packages, or
Agent Red files.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed through the live bridge
  authority at `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries
  forward the proposal's governing spec citations and implementation evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification commands below
  map to the approved spec-derived test plan.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - resource identity decisions are now
  preserved as durable local artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - registry rows link resource identity,
  alias, lifecycle state, evidence, and consuming surfaces.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - registry entries carry explicit
  lifecycle/status values including `canonical`, `canonical_unverified_url`, and
  `separate_project_not_gtkb`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red resources are marked as
  separate-project context and are not default GT-KB targets.

## GO Condition Mapping

| GO condition | Result |
| --- | --- |
| Avoid two competing registries | `config/agent-control/project-resource-aliases.toml` is the governed registry; `.claude/rules/project-resource-aliases.toml` is a pointer only and tests reject `[[resources]]` there. |
| Warn/fail on ambiguous and separate-project resources unless scoped | `scripts/resolve_project_resource.py` returns `ambiguous` for duplicate aliases and `separate_project_warning` for Agent Red resources under default GT-KB scope; `--scope agent-red` resolves them. |
| Require exact release CI evidence binding | `validate_ci_evidence()` requires `resource_id`, repo, branch, event, full head SHA, workflow, job, and run URL, and verifies repo binding to `Remaker-Digital/groundtruth-kb`. |
| Historical bridge/doc artifacts warning-level initially | `scan_text_for_unqualified_terms()` emits warning findings and the CLI scan exits non-blocking for historical text. |
| No external mutation | Only local tracked GT-KB files were changed; external resources were referenced but not mutated. |

## Files Changed

- `config/agent-control/project-resource-aliases.toml` - governed resource registry with GT-KB canonical resources and Agent Red separate-project resources.
- `.claude/rules/project-resource-aliases.toml` - startup-readable pointer to the governed registry.
- `memory/project_external_resource_registry.md` - human companion updated to reference the governed registry.
- `scripts/resolve_project_resource.py` - deterministic resolver, registry validator, git-remote drift checker, CI evidence validator, and warning-level scanner.
- `scripts/release_candidate_gate.py` - release gate now validates the resource registry and origin remote binding.
- `groundtruth-kb/src/groundtruth_kb/operating_state.py` - compact `resource-registry` component for startup/dashboard status.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - `gt status --component resource-registry` support.
- `tests/scripts/test_project_resource_aliases.py` - registry, resolver, drift, CI evidence, scanner, and CLI tests.
- `tests/scripts/test_release_candidate_gate.py` - release-gate registry checks.
- `groundtruth-kb/tests/test_operating_state.py` - resource-registry operating-state tests.

## Verification

### Applicability preflight

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-resource-reference-disambiguation-001
```

Observed:

```text
packet_hash: sha256:2431bf9f1843016941a73df8f251fde78046f982f5612e5dcd019e553a21e932
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

### Tests

```powershell
python -m pytest tests/scripts/test_project_resource_aliases.py tests/scripts/test_release_candidate_gate.py -q --tb=short
```

Observed: `35 passed in 0.58s`.

```powershell
cd groundtruth-kb
python -m pytest tests/test_operating_state.py tests/test_dashboard.py -q --tb=short
```

Observed: `11 passed, 1 warning in 3.72s`. Warning was the existing ChromaDB
Python 3.14 deprecation warning.

### Lint and formatting

```powershell
python -m ruff check scripts/resolve_project_resource.py scripts/release_candidate_gate.py tests/scripts/test_project_resource_aliases.py tests/scripts/test_release_candidate_gate.py
python -m ruff format --check scripts/resolve_project_resource.py scripts/release_candidate_gate.py tests/scripts/test_project_resource_aliases.py tests/scripts/test_release_candidate_gate.py
cd groundtruth-kb
python -m ruff check src/groundtruth_kb/operating_state.py src/groundtruth_kb/cli.py tests/test_operating_state.py tests/test_dashboard.py
python -m ruff format --check src/groundtruth_kb/operating_state.py src/groundtruth_kb/cli.py tests/test_operating_state.py tests/test_dashboard.py
```

Observed: all checks passed; final format checks reported already formatted.

### Resolver and release-gate probes

```powershell
python scripts\resolve_project_resource.py repo --json
python scripts\resolve_project_resource.py "Agent Red repo" --scope agent-red --json
python scripts\resolve_project_resource.py --check-git-remotes --json
```

Observed:

- `repo` resolves to `gtkb.github.repo` with identity `Remaker-Digital/groundtruth-kb`.
- `Agent Red repo` resolves only under explicit Agent Red scope.
- Git remote drift check returned `status: pass`, `origin=https://github.com/Remaker-Digital/groundtruth-kb.git`, and separate `agent_red=https://github.com/mike-remakerdigital/agent-red.git`.

```powershell
python scripts\release_candidate_gate.py --skip-python --skip-frontend --skip-dev-inventory
```

Observed:

```text
PASS secret manifest containment
PASS local secret gate presence
PASS broad GT-KB secret-scan workflow presence
PASS project resource registry (config/agent-control/project-resource-aliases.toml, origin=https://github.com/Remaker-Digital/groundtruth-kb.git)
RELEASE GATE: PASS
```

### Compact status

```powershell
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'
python -m groundtruth_kb --config groundtruth.toml status --component resource-registry --json
```

Observed: `overall_status=WARN`, `resources=11`, `unverified_canonical=["gtkb.sonarcloud.project"]`,
`separate_project=4`, `pointer_status=delegated`.

### Diff hygiene

```powershell
git diff --check -- config/agent-control/project-resource-aliases.toml .claude/rules/project-resource-aliases.toml memory/project_external_resource_registry.md scripts/resolve_project_resource.py scripts/release_candidate_gate.py tests/scripts/test_project_resource_aliases.py tests/scripts/test_release_candidate_gate.py groundtruth-kb/src/groundtruth_kb/operating_state.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_operating_state.py groundtruth-kb/tests/test_dashboard.py
```

Observed: exit code `0`; Git reported the existing line-ending warning for
`memory/project_external_resource_registry.md`.

## Residual Risk

- `gtkb.sonarcloud.project` intentionally remains `canonical_unverified_url`;
  that keeps operating-state status at `WARN` until the exact SonarCloud project
  key is verified and pinned.
- The high-risk text scanner is warning-level only for historical bridge/doc
  surfaces. A later cleanup proposal can decide which new artifact classes
  should become blocking.
- This implementation does not mutate formal GOV/SPEC/PB/ADR/DCL records.

## Decision Needed From Owner

None for this implementation report.

## Recommended Next Action

Loyal Opposition should verify this implementation report. If verified, Prime
Builder can proceed to the next bridge-actionable backlog item.
