NEW

# GTKB Environment Boundary Baseline Implementation Proposal

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-003]
target_paths: [".dockerignore", "scripts/check_environment_isolation.py", "scripts/release_candidate_gate.py", "tests/scripts/test_check_environment_isolation.py", "tests/scripts/test_release_candidate_gate.py"]

## Requested Verdict

GO to implement the narrow Phase 3 environment-boundary baseline below, or
NO-GO with required revisions.

## Parent GO Inputs

This proposal is the first concrete implementation slice after the accepted
Phase 3 planning review:

- `bridge/gtkb-isolation-003-environment-plan-review-002.md`

The Phase 3 plan accepted environment-isolation planning and required later
concrete implementation proposals before behavior changes.

## Claim

The correct first Phase 3 implementation slice is static, app-local, and
release-gate visible:

1. add a deterministic environment-isolation checker that reports repository
   root identity, git remote/branch, and GT-KB dependency mode while enforcing
   the first static Docker/Compose/build-context policy checks,
2. close the immediate build-context leak surface identified in the Phase 3
   plan by expanding `.dockerignore` to cover missing GT-KB governance/runtime
   paths, and
3. wire this checker into the existing release-candidate gate so environment
   boundary regressions become visible before broader migration and packaging
   work.

This slice should not yet implement devcontainer generation, workflow rewrites,
service-boundary logic, overlay mechanics, or Phase 7 startup/hook guardrails.

## Current Evidence

### Existing Enforcement Gap

- `scripts/release_candidate_gate.py` currently runs lint, security, parity,
  and targeted pytest lanes, but it does not yet run a dedicated environment
  boundary checker.
- `tests/scripts/test_release_candidate_gate.py` currently covers secret
  manifest containment, frontend gate behavior, and parity ordering, but it has
  no assertion for Phase 3 environment checks.

### Existing Static Environment Surface

- `.github/workflows/release-candidate-gate.yml` already runs
  `scripts/release_candidate_gate.py`, so the release gate is the natural
  enforcement hook for this slice without needing a new workflow first.
- `docker-compose.yml` builds from context `.` and bind-mounts `./src:/app/src:ro`,
  which is compatible with an app-root-only static policy audit.
- `Dockerfile` copies allowlisted app runtime paths only, which makes it
  reasonable to add a static check that rejects future copies of GT-KB
  governance/runtime surfaces.
- `requirements-local.txt` and `requirements-test.txt` default to the released
  `groundtruth-kb` package, while `requirements-local.txt` still documents an
  editable sibling-checkout override for maintainer work.

### Immediate Build-Context Drift

- `.dockerignore` already excludes `.claude`, `groundtruth.db`,
  `.groundtruth-chroma/`, env files, and `memory/`.
- The Phase 3 plan identified missing or unsafe coverage for `.codex/`,
  `.groundtruth/`, `bridge/`, and the correctly spelled
  `independent-progress-assessments/` path. Those surfaces are GT-KB
  governance/runtime artifacts that should not enter ordinary app image build
  context.

### Deliberate Non-Overlap With The Current Phase 7 Proposal

- `bridge/gtkb-work-subject-root-enforcement-implementation-001.md` is already
  the live Phase 7 foundation proposal and targets `scripts/workstream_focus.py`,
  `.claude/hooks/workstream-focus.py`, and `scripts/session_self_initialization.py`.
- This Phase 3 slice stays off those files intentionally so backlog progress
  can continue without conflating environment-boundary work with the pending
  work-subject/root-enforcement review.

## Scope

Implement only:

1. A new `scripts/check_environment_isolation.py` checker with deterministic
   text and `--json` output.
2. Repository/root/dependency probing inside that checker:
   - current working directory
   - Git repository root
   - remote URL
   - branch/HEAD
   - default GT-KB dependency mode inferred from requirement files
3. Initial static policy checks for:
   - `.dockerignore` denylist coverage of GT-KB governance/runtime paths
   - forbidden Dockerfile `COPY` of GT-KB governance/runtime surfaces
   - Compose host-bind scope and read-only source-mount expectations
   - active editable GT-KB dependency lines in app-default requirement files
4. `.dockerignore` updates for the missing denylist entries identified above.
5. Release-gate wiring in `scripts/release_candidate_gate.py`.
6. Focused regression tests for the checker and the new release-gate call.

Do not implement in this slice:

- `.devcontainer` or Codespaces files,
- `.github/workflows/*` edits,
- startup or hook subject/root guardrails,
- service-side GOV or scoped GT-KB client behavior,
- overlay/promotion behavior,
- migration rehearsal or root moves,
- downstream GT-KB scaffold/init/upgrade packaging.

## Proposed Checker Contract

Command:

```powershell
python scripts/check_environment_isolation.py --json
```

Proposed output shape:

```json
{
  "cwd": "absolute cwd",
  "repo_root": "absolute git root",
  "git_remote": "origin url or null",
  "git_branch": "branch name or detached",
  "default_gtkb_dependency_mode": "released_package|editable_local|missing",
  "findings": [
    {
      "code": "DOCKERIGNORE_MISSING_RULE",
      "severity": "error|warning",
      "path": ".dockerignore",
      "message": "human-readable explanation"
    }
  ]
}
```

Exit behavior:

- exit `0` when no `error` findings are present,
- exit non-zero when any `error` finding is present.

## Proposed First-Slice Policy Rules

1. `.dockerignore` must exclude at least:
   - `.codex/`
   - `.groundtruth/`
   - `bridge/`
   - `independent-progress-assessments/`
   - `groundtruth.db`
   - `.groundtruth-chroma/`
   - env files already treated as sensitive
2. `Dockerfile` must not add `COPY` instructions for:
   - `.claude/`
   - `.codex/`
   - `.groundtruth/`
   - `bridge/`
   - `independent-progress-assessments/`
   - `groundtruth.db`
3. `docker-compose.yml` host bind mounts must stay within the app repo and
   source binds must remain read-only unless a later explicit app-local
   writable path is allowed.
4. App-default requirement files must not contain an active editable
   `groundtruth-kb` sibling-checkout install line.

## Proposed File Touchpoints

Primary code:

- `scripts/check_environment_isolation.py`
- `scripts/release_candidate_gate.py`
- `.dockerignore`

Tests:

- `tests/scripts/test_check_environment_isolation.py`
- `tests/scripts/test_release_candidate_gate.py`

## Implementation Sequence

1. Add the checker with root/dependency probe helpers and deterministic
   findings.
2. Expand `.dockerignore` to close the missing build-context denylist entries.
3. Wire the checker into `scripts/release_candidate_gate.py` before the pytest
   lane so failures surface early.
4. Add focused tests for probe output, policy findings, and release-gate call
   ordering.

## Verification Commands

Required focused checks:

```powershell
python scripts/check_environment_isolation.py --json
python -m pytest tests/scripts/test_check_environment_isolation.py tests/scripts/test_release_candidate_gate.py -q --tb=short
```

Recommended broader check after focused green:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

## Review Questions

1. Is the first Phase 3 slice narrow enough if it is limited to static policy
   checks, `.dockerignore` hardening, and release-gate visibility?
2. Is `scripts/release_candidate_gate.py` the correct first enforcement lane
   for Phase 3, or should this checker remain standalone until a later slice?
3. Is leaving `.devcontainer` and workflow-file mutation out of the first slice
   acceptable, given that the current repo has no `.devcontainer` directory and
   the workflow already calls the release gate?

## Non-Scope Reminder

This proposal does not request devcontainer generation, CI workflow edits,
service-boundary implementation, overlay behavior, migration rehearsal, or
startup/hook root enforcement. Those remain later slices.
