NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 3 Init Defaults

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-009.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice3-init-defaults-2026-05-02`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-009.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001` through `-009`), the GO conditions in
`-008`, the post-implementation report, the implemented source/test/template
changes, the root-boundary rule, Phase 9 Section 1, and the Slice 2 registry
carry-forward gate.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `gt project init scaffold isolation`
- `GTKB-ISOLATION-017 Slice 3`
- `ADR-ISOLATION-APPLICATION-PLACEMENT gt project init`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. Active prior context is the bridge thread
itself, especially `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md`
and the Slice 3 proposal/review chain.

## Findings

### F1 - P1 - New template files are unregistered and fail the Slice 2 AST coverage gate

Claim: Slice 3 added two template source files but did not register them in the
managed artifact registry, so the registry AST coverage gate fails. This
violates the carried-forward Slice 2 condition and the approved Slice 3
proposal's registry acceptance criterion.

Evidence:

- The post-implementation report lists the new template files:
  `groundtruth-kb/templates/project/README-quickstart.md` and
  `groundtruth-kb/templates/project/release-readiness-banner.md`:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-009.md`.
- The implementation writes those templates into scaffold output from
  `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:415` and
  `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:422`.
- The approved proposal required registering new scaffold files in
  `groundtruth-kb/templates/managed-artifacts.toml` and included TP16 as
  managed-registry coverage:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-007.md`.
- Slice 2 verification carried a direct condition that Slice 3 register the
  deferred scaffolded template files, with the test comment stating "Slice 3
  NO-GO if it ships without registering all 22":
  `groundtruth-kb/tests/test_registry_ast_coverage.py:46` and
  `groundtruth-kb/tests/test_registry_ast_coverage.py:56`.
- Running the registry AST gate now fails:

```text
python -m pytest groundtruth-kb/tests/test_registry_ast_coverage.py -q --tb=short

FAILED groundtruth-kb\tests\test_registry_ast_coverage.py::test_every_template_source_file_has_registry_coverage
AssertionError: AST gate failure: 2 template-source files lack registry coverage
First 5: ['project/README-quickstart.md', 'project/release-readiness-banner.md'].
```

Risk / impact: Slice 3 can pass its reported targeted suite while leaving newly
added scaffold template sources outside the registry's reverse coverage gate.
That weakens upgrade/ownership visibility and preserves exactly the registry
coverage drift Slice 2 deferred to Slice 3.

Recommended action: Register
`project/README-quickstart.md` and
`project/release-readiness-banner.md` as FILE-class records in
`groundtruth-kb/templates/managed-artifacts.toml`, with lifecycle ownership
fields matching their intended scaffold/upgrade/doctor behavior. Then run the
registry AST coverage gate alongside the Slice 3 targeted suite.

Decision needed from owner: None.

## Gate Checks

The reported targeted test and lint evidence was reproduced:

```text
python -m pytest groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_managed_registry.py -q --tb=short
# 93 passed, 1 warning in 11.54s

python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli.py
# All checks passed.

python -m pytest groundtruth-kb/tests/test_cli.py -q --tb=short -k "bootstrap_desktop"
# 2 passed, 33 deselected, 1 warning in 0.31s
```

The IPR/CVR rows were present in the root project KB:

- `IPR-SLICE3-INIT-DEFAULTS-001`: category `implementation_proposal`, status
  `specified`, version `1`.
- `CVR-SLICE3-INIT-DEFAULTS-001`: category `constraint_verification`, status
  `verified`, version `1`.

Those passes do not close F1 because the spec-derived registry AST gate fails.

## Verdict

NO-GO until the new template source files are covered by the managed artifact
registry and `groundtruth-kb/tests/test_registry_ast_coverage.py` passes.

File bridge scan: selected entry 1 of 1 processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
