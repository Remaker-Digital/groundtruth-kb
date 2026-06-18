NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Pin the repo venv / gt CLI for headless-worker package imports (dispatch prompt + worker child env)

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4600

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_fab01_dispatch_substrate_revival.py"]

## Summary

WI-4600 (P2, defect, component `bridge-dispatch`). An auto-dispatched headless
bridge worker ran a `groundtruth_kb` package import under ambient
`C:\Python314\python.exe`, producing `ModuleNotFoundError: No module named
'groundtruth_kb'`, even though the package is reliably importable via the repo
venv (`groundtruth-kb/.venv/Scripts/python.exe`) and the venv `gt` console
script. This fix pins headless-worker package-importing commands to the in-root
repo venv / `gt` CLI, and adds a defense-in-depth `PYTHONPATH` backstop on the
worker child env, on BOTH dispatch substrates.

## Problem (root cause, verified)

The defect is NOT the dispatcher subprocess spawns:
`scripts/cross_harness_bridge_trigger.py:1545` and `:2735` already use
`sys.executable` to relaunch the trigger/wrapper under a valid interpreter. The
defect is the **worker-prompt prose** built by `_dispatch_prompt`
(`cross_harness_bridge_trigger.py`):

- `role_line` (L1721-1731) tells the worker to read its role "through the
  canonical `groundtruth_kb.harness_projection` or `gt harness roles` reader" —
  with no interpreter pin. A headless worker follows that prose under inherited
  PATH (ambient `python`/`gt`).
- `loyal_opposition_preflight_line` (L1738-1743) instructs the worker to run
  bare `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>`
  and bare `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>`
  — again no interpreter pin.

Compounding: the worker child env built in `_spawn_dispatch`
(`cross_harness_bridge_trigger.py:2677-2693`) and the independently-built child
env in `scripts/single_harness_bridge_dispatcher.py:648-670` never set
`PYTHONPATH`, so even a bare `python -m groundtruth_kb` the worker emits cannot
resolve the package from `groundtruth-kb/src`.

### Critical correctness note (must not regress into a worse bug)

`python -m groundtruth_kb.harness_projection` is NOT a role reader — it runs
`main()` (`groundtruth-kb/src/groundtruth_kb/harness_projection.py:399-417`),
which calls `generate_harness_projection(db, ...)` and **regenerates / rewrites
`harness-state/harness-registry.json` from the DB** (mutating, DB-dependent).
The canonical READER is the `gt harness roles` console subcommand
(`cli.py`) / the `read_roles()` function
(`harness_projection.py:305`) — as named by `CLAUDE.md`, `.claude/rules/operating-role.md`,
and `.claude/rules/codex-session-bootstrap.md`. Therefore this fix MUST pin the
role-resolution command to the venv `gt harness roles` console script and MUST
NOT introduce any `python -m groundtruth_kb.harness_projection` invocation
(which would direct headless workers to regenerate the registry instead of
reading their role).

## Proposed fix (two layers; in-root; reuses existing helpers)

**LAYER 1 — worker prompt (primary).** In `_dispatch_prompt`, replace every
bare-interpreter package-importing command with a venv-pinned form. The repo
venv interpreter rel-path is resolved from the established platform tuple
(`groundtruth-kb/.venv/Scripts/python.exe` on Windows, `groundtruth-kb/.venv/bin/python`
on POSIX) already used by `scripts/check_ruff_format.py::_venv_python` (L74) and
`groundtruth-kb/src/groundtruth_kb/project/doctor.py::_check_ruff` (L414); the
venv `gt` console path is resolved by `scripts/install_gt_path_shim.py::resolve_venv_gt_exe`
(L59). Because the prompt is generated prose, the resolved relative venv literal
is emitted directly (platform-selected at prompt-generation time; no
`shutil.which` needed):

- `role_line`: pin role resolution to the venv `gt` console script
  (e.g. `groundtruth-kb/.venv/Scripts/gt.exe harness roles`). Keep the literal
  reader-module substring `groundtruth_kb.harness_projection` in the prose
  (naming the underlying `read_roles` reader module), and add an explicit
  instruction: do NOT run `python -m groundtruth_kb.harness_projection` (it
  regenerates the registry) and do NOT use ambient bare `python` or bare `gt`.
- `loyal_opposition_preflight_line`: prepend the venv python interpreter to both
  preflight commands, e.g.
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id <document-name>`
  (and likewise `adr_dcl_clause_preflight.py`). The required substrings
  `bridge_applicability_preflight.py --bridge-id <document-name>` and
  `adr_dcl_clause_preflight.py --bridge-id <document-name>` are preserved.

Because `single_harness_bridge_dispatcher.py` reuses
`trigger._dispatch_prompt` (L594-595), LAYER 1 fixes the single-harness
substrate transitively with no second edit.

**LAYER 2 — worker child env (defense-in-depth, both substrates).** Factor a
small pure helper `_worker_pythonpath(inherited: str | None) -> str` into
`cross_harness_bridge_trigger.py` that prepends the existing `_PACKAGE_SRC`
constant (L81 — the `groundtruth-kb/src` path already added to `sys.path` for
the trigger process itself under WI-3360) to any inherited `PYTHONPATH`
(`os.pathsep`-joined; never clobbering an existing value). Call this helper to
set `env["PYTHONPATH"]` in BOTH worker-child-env blocks:
`cross_harness_bridge_trigger.py:2677-2693` AND
`single_harness_bridge_dispatcher.py:648-670` (the single-harness dispatcher
already loads `trigger`, so it calls `trigger._worker_pythonpath`). This ensures
a worker-emitted bare `python -m groundtruth_kb` still resolves the package on
both substrates. LAYER 2 in BOTH dispatchers avoids silent partial coverage of
single-harness-topology workers.

Both layers keep interpreter/package resolution strictly in-root
(`groundtruth-kb/.venv`, `groundtruth-kb/src`); no out-of-root literal is
introduced, so the project-root-boundary core directive is satisfied without
invoking the S366 External Harness Executable Resolution Exception (which covers
out-of-root harness executables, not in-root interpreters). No config key, no
`.env.local` addition, and no owner policy choice is required: the in-root repo
venv is the unambiguous deterministic default.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the cross-harness dispatch trigger is bridge
  automation; this is a bridge-automation reliability repair.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the required
  regression test (a dispatched-worker role-resolution probe must not use
  ambient system Python) and spec-derived verification.
- `GOV-ENV-LOCAL-AUTHORITY-001` — env source-of-truth authority for path
  prefixes / CLI configuration; cited to show the in-root venv default needs no
  `.env.local` key and no out-of-root literal.
- `.claude/rules/project-root-boundary.md` § "External Harness Executable
  Resolution Exception" (+ `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`)
  — the controlling root-boundary envelope; cited to show this fix stays in-root
  (repo venv / repo src) and is MORE root-contained than the exception requires.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — GT-KB root / application-placement
  boundary; all interpreter and package resolution introduced by this fix stays
  in-root (`groundtruth-kb/.venv`, `groundtruth-kb/src`), with no out-of-root
  path literal, honoring the in-root placement decision.
- `GOV-RELIABILITY-FAST-LANE-001` — small P2 defect-fix appropriate to a
  trigger/dispatcher + one-test-module change.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance and
  lifecycle-trigger advisories applicable to this tracked defect-fix work item.

## Prior Deliberations

- Deliberation + bridge survey found NO existing thread proposing a
  headless-worker-interpreter / venv / package-import fix; the two topically
  nearest threads are distinct: `gtkb-wi4530-gt-cli-path-install-shim`
  (WI-4530, gt-console PATH discoverability for fresh installs) and
  `gtkb-harness-data-driven-dispatch` (WI-3344, data-driven harness argv
  construction). Neither addresses the worker's package-import interpreter
  selection.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (companion bridge
  `gtkb-root-boundary-external-harness-exec-exception` VERIFIED) bounds
  out-of-root harness-executable resolution; this WI-4600 fix operates inside
  that envelope and is more root-contained (in-root repo venv), so it does not
  exercise the exception.
- WI-3360 previously added `_PACKAGE_SRC` to the trigger process's own
  `sys.path` to fix this exact `ModuleNotFoundError` for the trigger; LAYER 2
  extends the same in-root remedy to the spawned worker children.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20263239` — seed=search; bridge_thread; Loyal Opposition Review - WI-4530 gt CLI PATH Shim Generator
- DA: `DELIB-20262447` — seed=search; bridge_thread; Bridge thread: gtkb-worker-packet-auth-envelope-slice-2-auto-packet (4 versions,
- DA: `DELIB-20261108` — seed=search; bridge_thread; Loyal Opposition Verdict - V1 Spec-Corpus Distillation Scoping
- DA: `DELIB-20261249` — seed=search; bridge_thread; Loyal Opposition Verdict - V1 Spec-Corpus Distillation Scoping
- DA: `DELIB-2757` — seed=search; bridge_thread; Loyal Opposition Review - Role Enhancement Isolation Dependency Reframe

## Requirement Sufficiency

Existing requirements are sufficient. WI-4600 prescribes the behavior (headless
workers must use the repo venv / `gt` CLI / a repo-local interpreter for package
imports, plus regression coverage), and `GOV-ENV-LOCAL-AUTHORITY-001` +
`.claude/rules/project-root-boundary.md` govern in-root interpreter resolution.
No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — tests in
`platform_tests/scripts/test_cross_harness_bridge_trigger.py` (LAYER 1 + LAYER 2
helper) and `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py`
(LAYER 2 single-harness):

- WI-4600 core (worker probe must not use ambient Python) +
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:
  `test_dispatch_prompt_pins_venv_interpreter_for_package_imports` builds a
  DispatchTarget and calls `_dispatch_prompt`; POSITIVE: asserts the venv-pinned
  python literal precedes each preflight command and the venv `gt harness roles`
  form is used for role resolution; NEGATIVE: asserts the prompt contains no
  bare `python scripts/`, no bare `python -m groundtruth_kb`, and specifically
  no `python -m groundtruth_kb.harness_projection` (locking in the
  non-mutating-reader correctness point).
- Regression preservation:
  `test_dispatch_prompt_preserves_required_substrings` asserts
  `groundtruth_kb.harness_projection`,
  `bridge_applicability_preflight.py --bridge-id <document-name>`, and
  `adr_dcl_clause_preflight.py --bridge-id <document-name>` remain present (the
  existing prompt tests continue to pass).
- LAYER 2 helper:
  `test_worker_pythonpath_prepends_package_src_no_clobber` asserts
  `_worker_pythonpath(None)` contains `_PACKAGE_SRC`, and
  `_worker_pythonpath("X")` prepends `_PACKAGE_SRC` + `os.pathsep` + `X`
  (inherited value preserved, not clobbered).
- LAYER 2 cross-harness env:
  `test_spawn_dispatch_env_sets_worker_pythonpath` asserts the trigger's
  worker child env `PYTHONPATH` contains `_PACKAGE_SRC`.
- LAYER 2 single-harness env (in `test_fab01_dispatch_substrate_revival.py`):
  `test_single_harness_worker_env_sets_pythonpath` asserts the single-harness
  dispatcher's worker child env `PYTHONPATH` contains `_PACKAGE_SRC` (parity
  with the cross-harness substrate).

All assertions are pure string/dict checks against in-process function output —
deterministic, no live spawn, no ambient-interpreter dependency.

Commands (resolved against the GT-KB venv interpreter):

    .venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py -q
    .venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py
    .venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py

Expected: all tests pass (new tests fail before the fix); ruff check and ruff
format --check clean on all changed files.

## Acceptance Criteria

1. The dispatch worker prompt pins package-importing commands to the in-root
   repo venv / `gt` CLI; role resolution uses `gt harness roles` (NOT
   `python -m groundtruth_kb.harness_projection`).
2. The prompt contains no bare `python scripts/` or bare `python -m
   groundtruth_kb` for package-importing commands.
3. Existing prompt-test substrings are preserved (no regression to
   `test_cross_harness_bridge_trigger.py`).
4. Both the cross-harness and single-harness worker child envs set `PYTHONPATH`
   to include `_PACKAGE_SRC` (no-clobber prepend), proven by tests on both
   substrates.
5. Resolution stays strictly in-root; no out-of-root literal is added.
6. `ruff check` and `ruff format --check` clean on all changed files.

## Risk and Rollback

- Risk: LOW–MEDIUM. LAYER 1 is prose-text + LAYER 2 is an additive env var via a
  small pure helper. The primary correctness risk (instructing workers to run
  the mutating `-m groundtruth_kb.harness_projection`) is explicitly excluded by
  design and asserted-against in tests.
- Blast radius: `_dispatch_prompt` text + one new pure helper + two env-block
  call sites + two test modules. No change to dispatch routing,
  signature/actionability logic, `implementation_authorization.py`, or
  `scan_bridge.py` (so no conflict with in-flight WI-4618).
- Rollback: revert the diff; the prompt returns to bare-interpreter prose and
  the env blocks omit `PYTHONPATH`. No state, schema, or routing change.
- Bridge process integrity: this proposal is filed as a versioned bridge file in
  the append-only numbered chain
  (`bridge/gtkb-headless-worker-venv-interpreter-pin-001.md`); the
  post-implementation report will follow as the next numbered bridge file with
  correct status, and no prior version is deleted or rewritten — preserving the
  canonical numbered-file audit chain.

## Owner Decisions / Input

None required. Implementation authority derives from the active,
owner-decision-backed project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`). WI-4600 is an
unimplemented work item in PROJECT-GTKB-MAY29-HYGIENE; the WI text prescribes
the behavior and the fix is owner-policy-free (the in-root repo venv is the
deterministic default). No AskUserQuestion decision is needed.

## Recommended Commit Type

`fix:` — repairs a dispatch-reliability defect (headless workers using ambient
Python for package imports) with no new user-facing capability surface.
