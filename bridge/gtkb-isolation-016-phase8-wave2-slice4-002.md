NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 Proposal

Status: NO-GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-slice4-001.md` is not approved as
written. `_path_rewrite.py` is the right next Stage B lane, but the proposed
subprocess entrypoint does not actually invoke `classify-tree` in this
checkout.

## Findings

### F1 - Blocking: proposed `python -m groundtruth_kb.cli` invocation is a no-op

The proposal makes `python -m groundtruth_kb.cli project classify-tree ...` the
authoritative subprocess command
(`bridge/gtkb-isolation-016-phase8-wave2-slice4-001.md:44` through `:45`).

Smoke test against a temp directory in this checkout:

`python -m groundtruth_kb.cli project classify-tree --dir <tmp> --max-depth 2 --format json --output <tmp>/classification.json`

Result: exit code `0`, but `<tmp>/classification.json` was not created.

The local package is importable from
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py`,
but historical project evidence already records that `python -m
groundtruth_kb.cli --help` exits successfully while printing no help because
the module does not call `main()` under a `__main__` guard. Current local
evidence confirms the same behavior for `project classify-tree`.

The working local entrypoint is:

`python -c "from groundtruth_kb.cli import main; main()" project classify-tree --dir <tmp> --max-depth 2 --format json --output <tmp>/classification.json`

That command wrote the classification file and produced the expected JSON
schema, including `rows[].path`, `ownership`, `owner_decision_pending`, and
`record_id`.

Impact: as proposed, the real lane would fail to produce
`classification.json` during operator-driven execution. A mocked
`subprocess.run` test could miss this entirely unless it verifies the callable
entrypoint shape.

Required revision: build the subprocess command with `sys.executable` and the
working callable form, or another locally verified callable entrypoint. Add a
test that asserts the exact subprocess command shape does not use
`python -m groundtruth_kb.cli`. Keep the current mock strategy for avoiding
live-root walks, but include a small temp-dir smoke test or command-builder test
that would catch this no-op entrypoint regression.

### F2 - Blocking: target namespace should be derived from the validated manifest

The proposal asks whether `target_namespace = "applications/Agent_Red"` may be
hard-coded (`bridge/gtkb-isolation-016-phase8-wave2-slice4-001.md:214`). It
should not be hard-coded in this lane. Slice 3 now loads a Wave 2 validated
manifest before dispatch, and the manifest already contains `legacy_root`,
`applications_namespace`, and `target_root`.

Impact: hard-coding `applications/Agent_Red` creates a second source of truth
for path rewrite targets. It works only for the current Agent Red default and
can drift from the manifest if this rehearsal machinery is reused for another
adopter or if the target root changes.

Required revision: derive the rewrite prefix from the validated manifest, for
example by computing `Path(manifest["target_root"]).resolve().relative_to(
Path(manifest["legacy_root"]).resolve())` and normalizing to forward slashes.
Add a fixture test using a different valid `applications/<name>` target to
prove the lane does not hard-code Agent Red.

## Recommended Action

Revise Slice 4 before implementation:

- Use a locally callable GT-KB CLI entrypoint for `classify-tree`.
- Assert the subprocess command shape in tests.
- Derive `target_namespace` from the validated manifest instead of hard-coding
  `applications/Agent_Red`.

The rest of the lane shape is directionally sound: mocked subprocess tests are
appropriate, `legacy-exception` and `owner_decision_pending` can remain
warnings with `status="ok"`, and generating git-filter-repo arguments without
running `git filter-repo` is the right Phase 8 boundary.

## Decision Needed From Owner

None.
