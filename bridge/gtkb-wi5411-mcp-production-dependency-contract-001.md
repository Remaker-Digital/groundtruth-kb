NEW

# WI-5411: Restore MCP as a production package dependency

bridge_kind: prime_proposal
Document: gtkb-wi5411-mcp-production-dependency-contract
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5411

target_paths: ["groundtruth-kb/pyproject.toml", "groundtruth-kb/uv.lock", "platform_tests/groundtruth_kb/test_mcp_dependency_contract.py"]

implementation_scope: configuration, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make `mcp>=1.0` a base `groundtruth-kb` production dependency, regenerate the
package lock, and add an executable dependency-contract test. The current
package metadata puts MCP only in the optional `bridge` extra even though
verified `SPEC-1526` says the SDK is a production dependency. Consequently, a
normal install and the full CI install shapes (`dev`, `web`, and `search`) may
omit MCP; the active environment does omit it, and four MCP surface tests fail
with `ModuleNotFoundError`.

The implementation keeps an empty `bridge` extra as a compatibility marker so
existing `groundtruth-kb[bridge]` install commands remain valid, moves the
unchanged `mcp>=1.0` requirement into `project.dependencies`, updates stale mypy
comments/overrides that describe MCP as optional, and regenerates only
`groundtruth-kb/uv.lock`. The new test proves pyproject, lock, and built-wheel
metadata all expose MCP without an extra marker. No root `pyproject.toml`, CI
workflow, MCP server source, dispatcher/TAFE/harness surface, or registration is
changed.

## Specification Links

- `SPEC-1526` - explicitly requires the MCP SDK to be listed as a production dependency.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the dependency correction to preserve current extras, source behavior, and install routes while closing the missing-runtime gap.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the package metadata and lock change to have deterministic, independently executable evidence.
- `GOV-WORK-TREE-HYGIENE-001` - keeps the unrelated dirty root `pyproject.toml` outside this clean three-path scope.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - requires exact three-path review and separate mechanical authority before any finalization commit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO/start and post-implementation VERIFIED before protected configuration/test adoption.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds package metadata, lock projection, and contract test to the production-dependency requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5411 to the active modernization-assurance project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires fresh production-install, full-test-install, wheel-metadata, and MCP surface evidence before VERIFIED.

## Prior Deliberations

- `DELIB-0026` - records the owner directive that MCP is mandatory except where it is not physically possible; packaging the MCP server without its SDK contradicts that direction.
- `DELIB-20264330` - independently verified the stable GT-KB MCP surface and its executable foundation tests; WI-5411 restores the installation contract needed for that verified surface to import in a normal environment.

This proposal does not expand the MCP surface or register it with any harness.
It repairs the package dependency needed by the already implemented surface.

## Owner Decisions / Input

No additional owner decision is required. The owner authorized the full
modernization assurance program at project scope and directed every discovered
omission to become hygiene work while implementation continues. Active
authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
covers configuration, test, metadata, documentation, runtime-state, governance
evidence, and governed bridge work while preserving independent GO/start,
VERIFIED, and mechanical Git gates.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-1526` is unambiguous that MCP is a
production dependency. The legacy assertion path naming `requirements.txt` is
stale after packaging migrated to PEP 621, but that does not make the normative
dependency requirement ambiguous. The executable contract test becomes the
current spec-derived proof without changing requirement meaning.

## Spec-Derived Verification Plan

`SPEC-1526` maps to the new package contract test. It must parse
`groundtruth-kb/pyproject.toml` and `groundtruth-kb/uv.lock`, build a wheel into
an in-root scratch directory, inspect wheel `METADATA`, and prove all of the
following:

- `mcp>=1.0` appears exactly once in base `project.dependencies`;
- no optional dependency group owns MCP;
- the `bridge` compatibility extra remains declared and empty;
- the lock binds MCP as a direct dependency of `groundtruth-kb` without an
  `extra == 'bridge'` marker; and
- built-wheel metadata contains an unconditional `Requires-Dist: mcp>=1.0`.

Expected result: all new contract tests pass.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mcp_dependency_contract.py -q --tb=short --timeout=600
```

The lock projection must be current and reproducible. Expected result: lock is
unchanged by `uv lock --check` after generation.

```text
cd groundtruth-kb
uv lock
uv lock --check
```

Production-install proof uses a fresh in-root virtual environment and the base
package only. Expected result: MCP and the GT-KB MCP server import successfully
without any extra.

```text
uv venv .gtkb-state/wi5411/prod-venv --python 3.14
uv pip install --python .gtkb-state/wi5411/prod-venv/Scripts/python.exe ./groundtruth-kb
.gtkb-state/wi5411/prod-venv/Scripts/python.exe -c "import mcp; from groundtruth_kb.mcp_surface.server import SERVER; print(type(SERVER).__name__)"
```

Full-test-install proof uses the same extras as the root GT-KB workflow without
adding `bridge`. Expected result: the MCP foundation suite passes completely;
the current baseline is 11 passed and 4 failed solely because `mcp` is absent.

```text
uv venv .gtkb-state/wi5411/full-venv --python 3.14
uv pip install --python .gtkb-state/wi5411/full-venv/Scripts/python.exe "./groundtruth-kb[dev,search,web]"
.gtkb-state/wi5411/full-venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short --timeout=600
```

`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and exact-scope hygiene map to Ruff,
TOML/lock review, and whitespace checks. Expected result: clean checks and no
diff outside the exact three targets.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/groundtruth_kb/test_mcp_dependency_contract.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/groundtruth_kb/test_mcp_dependency_contract.py
git diff --check -- groundtruth-kb/pyproject.toml groundtruth-kb/uv.lock platform_tests/groundtruth_kb/test_mcp_dependency_contract.py
git diff -- groundtruth-kb/pyproject.toml groundtruth-kb/uv.lock platform_tests/groundtruth_kb/test_mcp_dependency_contract.py
```

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires independent LO to
rerun all commands against the exact implementation and verify that neither the
dirty root `pyproject.toml` nor any workflow/source file is absorbed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5411 modernization acceptance failure and verified SPEC-1526 production dependency requirement",
  "canonical_authority": "SPEC-1526 and PEP 621 project.dependencies",
  "primary_route": "pip or uv installation of the base groundtruth-kb package",
  "before_behavior": "MCP is available only when callers know to request the optional bridge extra, while normal and full-test installs can fail to import the shipped MCP surface",
  "after_behavior": "every base installation receives MCP; existing bridge-extra commands remain accepted through an empty compatibility extra",
  "self_descriptive_naming": "the package dependency table directly names mcp and the contract test names the production dependency invariant",
  "obsolete_guidance_disposition": "mypy comments and optional-import configuration that describe MCP as absent are removed or narrowed to genuinely optional dependencies",
  "history_preservation": "the bridge extra name is retained for installer compatibility and the existing mcp version floor is unchanged",
  "baseline": {
    "pyproject_location": "optional bridge extra",
    "active_environment": "mcp not installed",
    "mcp_foundation_tests": "11 passed, 4 failed with ModuleNotFoundError"
  },
  "expected_result": {
    "pyproject_location": "base project dependencies",
    "wheel_metadata": "unconditional Requires-Dist for mcp>=1.0",
    "mcp_foundation_tests": "15 passed"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the later exact three-path dependency-contract commit and regenerate the prior lock",
    "test": "rerun the package contract, fresh install, MCP foundation, Ruff, and lock checks"
  },
  "hard_invariants": [
    "no root pyproject.toml, CI workflow, MCP source, bridge, dispatcher, TAFE, harness, credential, deployment, release, or external-system mutation",
    "the mcp version floor remains >=1.0",
    "the bridge extra remains a valid compatibility install name",
    "all scratch environments and build artifacts remain under E:/GT-KB/.gtkb-state/wi5411"
  ],
  "fail_closed_conditions": [
    "wheel metadata marks MCP optional or omits it",
    "uv lock is stale or maps MCP only through an extra marker",
    "base-install import or any MCP foundation test fails",
    "the exact target scope or independent implementation authority differs"
  ],
  "essential_context_preservation": "existing package extras, CI install commands, MCP server behavior, project-root containment, and concurrent root configuration changes remain intact"
}
```

## Risk / Rollback

Making MCP unconditional increases base installation size and exposes its
transitive dependency constraints to every user, but that is the behavior
already required by `SPEC-1526` and by the shipped MCP surface. Keeping the
existing version floor avoids introducing a separate version-policy change;
fresh production and full-test installs detect conflicts. Under separate exact
mechanical authority, finalization should be one focused `fix` commit containing
only the three reviewed targets. Rollback is a separately governed revert of
that commit plus deterministic lock regeneration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5411-mcp-production-dependency-contract`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - restores the verified production dependency contract and makes normal
installed MCP functionality importable.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
