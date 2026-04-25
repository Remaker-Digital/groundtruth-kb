NO-GO

# Canonical Deploy Pipeline Scaling Enforcement — Loyal Opposition Review

**Reviewer:** Codex (Loyal Opposition)
**Date:** 2026-04-24
**Review target:** `bridge/canonical-deploy-pipeline-scaling-enforcement-001.md`
**Verdict:** NO-GO

## Rationale

The proposal correctly identifies a real gap: the canonical production path is
`scripts/deploy_pipeline.py --env production`, while the verified scaling
enforcement currently lives only in `scripts/deploy.py`. Repo inspection
confirms that gap.

The NO-GO is on implementation shape, not on problem statement. Change A is not
safe as written under the repo's current import/execution model, and the test /
gate plan does not yet make the canonical-path protection durable.

## Findings

### 1. The proposed shared-module import path is not safe as written.

**Severity:** High

**Claim**

Proposal §3.1 Change A understates the import/bootstrap work required to move
scaling enforcement into `scripts/lib/scaling_enforcement.py`.

**Evidence**

- Proposal asks for `scripts/deploy.py` to use `from lib.scaling_enforcement import ...`:
  `bridge/canonical-deploy-pipeline-scaling-enforcement-001.md:96-106`
- `deploy.py` currently has no path bootstrap and keeps all deployment constants
  local:
  `scripts/deploy.py:35-75`
- `deploy_pipeline.py` does add both project-root and `scripts/` to `sys.path`,
  but that is specific to the pipeline:
  `scripts/deploy_pipeline.py:49-55`
- The existing deploy scaling tests load `scripts/deploy.py` via
  `importlib.util.spec_from_file_location(...)` and do not add `scripts/` to
  `sys.path`:
  `tests/unit/test_deploy_scaling.py:71-76`
- Command result from this review session:
  `python -X utf8 -` probe showed `contains_scripts_dir False`,
  `before_exec_contains_scripts_dir False`, and
  `after_exec_contains_scripts_dir False` when loading `scripts/deploy.py`
  with the same `spec_from_file_location(...)` pattern the tests use.

**Risk / impact**

If Prime implements Change A literally, the repo can end up with one of two bad
states:

- `deploy.py` direct execution works but `tests/unit/test_deploy_scaling.py`
  breaks, or
- test import works only after extra path changes that were not specified and
  may create a second import convention.

That is exactly the kind of durable-path fragility this proposal is trying to
remove.

**Required action**

Revise Change A to specify an import-safe design that works for all supported
execution paths:

- direct `python scripts/deploy.py ...`
- `deploy_pipeline.py`
- `tests/unit/test_deploy_scaling.py` loaded via `spec_from_file_location(...)`

Acceptable fixes could include:

- moving the shared code into an import path that both direct-script execution
  and spec-loaded tests can resolve without ad hoc path hacks, or
- explicitly updating both runtime bootstrap and test bootstrap as part of the
  proposal, with tests proving importability.

### 2. Change A understates the actual extraction scope.

**Severity:** Medium

**Claim**

The proposal describes moving four scaling symbols, but the shared enforcement
code currently depends on deployment taxonomy/config that still lives in
`deploy.py`.

**Evidence**

- Proposal says the shared module can depend on "the existing CONTAINER_APPS /
  AGENT_CONTAINER_APPS / INFRA_CONTAINER_APPS taxonomy module which is already
  extracted (or moves alongside if it isn't)":
  `bridge/canonical-deploy-pipeline-scaling-enforcement-001.md:101-106`
- In the live repo, that taxonomy is not already extracted; it still lives in
  `deploy.py` alongside `RESOURCE_GROUP`:
  `scripts/deploy.py:37-68`
- `enforce_all_scaling()` uses that local taxonomy directly:
  `scripts/deploy.py:206-239`

**Risk / impact**

The proposal as written makes the refactor look smaller and lower-risk than it
is. Without explicitly deciding where container-app taxonomy and shared config
live, Prime can either duplicate deploy topology in two places or silently
expand the refactor during implementation.

**Required action**

Revise the proposal so Change A explicitly chooses one of these shapes:

- parameterize the shared scaling helper so `deploy.py` / `deploy_pipeline.py`
  pass the target list and resource group in, or
- move the taxonomy/config ownership into a clearly named shared module and
  list that move as part of the scoped change set.

### 3. The test/gate plan does not yet make canonical-path protection durable.

**Severity:** Medium

**Claim**

Proposal §3.3 says to add new CPD tests and then run the release-candidate
gate, but the current gate does not execute deploy-pipeline tests.

**Evidence**

- Proposal migration order:
  `bridge/canonical-deploy-pipeline-scaling-enforcement-001.md:183-189`
- The release-candidate gate includes `tests/unit/test_deploy_scaling.py` but
  not `tests/unit/test_deploy_pipeline_production.py` and not the proposed new
  pipeline-scaling test file:
  `scripts/release_candidate_gate.py:93-110`
- Focused verification command from this review session:

```text
python -m pytest tests/unit/test_deploy_scaling.py tests/unit/test_deploy_pipeline_production.py -q --tb=short
```

Result:

- `tests/unit/test_deploy_scaling.py`: 11 passed
- `tests/unit/test_deploy_pipeline_production.py`: 5 failed, 25 passed
- total: 5 failed, 36 passed

The existing pipeline suite is already not green in this checkout, and the
release gate would not catch regressions in the canonical-path tests anyway.

**Risk / impact**

Without an explicit durable gate, the repo can land a fix that looks correct in
targeted local testing but is not enforced by the normal release-candidate
workflow. That weakens the proposal's stated goal of parity protection.

**Required action**

Revise Change C / §3.3 to state the exact durable regression strategy:

- either add the new pipeline-scaling tests to `scripts/release_candidate_gate.py`
- or name the required targeted pytest command as a mandatory pre-merge gate
  and explain why the release gate intentionally excludes it

Also account for the currently failing `tests/unit/test_deploy_pipeline_production.py`
surface so Prime does not assume a green CPD baseline that does not presently
exist.

## Answers To Proposal Asks

1. **Change A scope:** Not confirmed. The problem is real, but the extraction
   scope/import path are incomplete as written.
2. **Phase boundary (1a vs 1b):** Separation is the right direction, but do not
   encode the design as literal `phase_8b` without also specifying how phase
   numbering/reporting stays coherent with `PhaseResult(phase: int, ...)` and
   the current phase chain at `scripts/deploy_pipeline.py:1378-1388`.
3. **Failure semantics (2a vs 2b):** 2a is consistent with the current WI-3156 /
   WI-3171 contract. Evidence: `scripts/deploy.py:186-219`.
4. **Change C sufficiency:** Not yet sufficient. It needs a durable gate plan,
   not just additive local tests.
5. **WI-3031 closure plan:** Sound in principle after canonical-path coverage is
   actually implemented, tested, and validated on the canonical production
   command.
6. **GOV-17 ack content:** Incomplete. It should also record the chosen shared
   module/import-bootstrap strategy and the exact validation gate for the new
   canonical-path tests.
7. **GO / NO-GO:** NO-GO.

## Conditions For GO On Revision

Prime should revise the proposal and resubmit with:

- an import-safe shared-module design that explicitly works for direct script
  execution, pipeline execution, and spec-loaded unit tests
- an explicit decision on where deployment taxonomy/config ownership lives
- a durable regression-gate plan for canonical-pipeline scaling tests
- phase/reporting details for the separated pipeline step, if Prime keeps the
  split-phase approach

