# GT-KB v0.7.0-rc1 Release Notes

**Release date:** 2026-05-03 (release candidate 1)
**PyPI:** *not yet published — gated on Slice 8.5 CI-green VERIFIED*
**Prior release:** v0.6.1 (2026-04-17)
**Tag:** *not yet authorized — gated on Slice 8.5 VERIFIED*

## Status

This is a **release candidate**. Final tag (`v0.7.0-rc1`) and PyPI publication
are gated on the GitHub Actions CI-green evidence captured in Slice 8.5 (a
separate post-VERIFIED bridge thread filed after the Slice 8 commit lands; see
`bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`). This file is the rc1
release-notes artifact ready for publication when Slice 8.5 records VERIFIED.

## Highlights

v0.7.0-rc1 ships the GTKB-ISOLATION-017 program: a strict separation between
GT-KB platform artifacts and the adopter application code that consumes them.
Eight slices VERIFIED across S326-S329 (Slices 1, 2, 2.5, 3, 4, 5, 6, 7) plus
this Slice 8 closeout — 12 doctor checks, registry-isolation enforcement,
managed-only init defaults, isolation-aware upgrade with rollback, a
45-function clean-adopter test suite, a 314-LOC architecture chapter, and 4
worked examples covering clean-adopter / transport-tests / release-gate /
existing-adopter-migration paths.

Together these surfaces let an adopter project boundary be enforced
mechanically: GT-KB platform code never reaches into adopter code, adopter
code never depends on private platform internals, and the boundary holds
across init, upgrade, and downstream test execution.

## Adopter-visible changes

### Application/platform isolation contract (12 doctor checks)

`gt project doctor` now enforces 12 isolation contracts via dedicated check
functions in `src/groundtruth_kb/project/doctor_isolation.py`:

- **isolation:root-boundary** — adopter project root is contained.
- **isolation:app-placement** — application files live under
  `applications/<app-name>/` (per ADR-ISOLATION-APPLICATION-PLACEMENT-001).
- **isolation:harness-placement** — harness state lives under
  `harness-state/<harness>/` only.
- **isolation:registry-strict** — managed registry rows do not overlap with
  application file globs.
- **isolation:no-cross-import** — adopter code does not import private GT-KB
  internals (only the public `groundtruth_kb` surface is allowed).
- **isolation:bridge-app-boundary** — bridge files do not embed application
  source.
- **isolation:db-app-boundary** — `groundtruth.db` does not contain
  application-private records mixed with platform records.
- **isolation:chroma-regeneratable** — `.groundtruth-chroma/` is fully
  regeneratable from `groundtruth.db` (overlay invariant).
- Plus 4 additional checks covering harness-tree boundaries, manifest
  boundaries, and rule-file boundaries.

ERROR on hard violations; WARN on potential drift. Fresh adopter projects
pass by construction; existing projects can run `gt project upgrade --apply`
to bring legacy layouts into compliance.

### Managed-only init defaults

`gt project init` now scaffolds in **managed-only mode** by default: the
target tree contains only registry-managed artifacts. Adopter application
code is added explicitly under `applications/<app-name>/`, never mixed
into the platform-owned tree. Profile-specific defaults (`local-only`,
`dual-agent`, `dual-agent-webapp`, `harness-memory`) determine which managed
artifacts ship.

Optional `--include-app-tree` flag preserves legacy mixed-tree behavior for
adopters not yet ready to migrate; the default remains managed-only.

### Isolation-aware upgrade + rollback

`gt project upgrade --apply` is now isolation-aware: it skips application
files (`upgrade_policy = preserve` or `transient`), flags cross-boundary
divergence, and emits a rollback journal. `gt project upgrade --rollback`
reverses the most recent apply using the journal — covered by 12+ tests
across `tests/test_upgrade_*.py`.

### Clean-adopter test suite (45 functions, 13 files)

New test suite at `tests/clean_adopter/` exercises the isolation contract
end-to-end against fresh-init adopter trees. 45 test functions across 13
files cover init, doctor, upgrade, rollback, registry-isolation, overlay
stale-detection, and cross-import enforcement. Two fixture trees
(`fixtures/clean-adopter-minimal/` and `fixtures/adopter-with-app-tree/`)
provide stable baselines.

CI wiring (`.github/workflows/ci.yml`) runs the clean-adopter suite on
every push.

### Architecture chapter + 4 worked examples

`docs/architecture/isolation.md` (314 LOC) documents the isolation
contract, its motivation, the 12 doctor checks, the registry contract, and
the upgrade behavior with rollback semantics.

`docs/examples/` contains 4 example trees:

- `clean-adopter-minimal/` — `gt project init` baseline.
- `adopter-with-transport-tests/` — adopter exercising the transport API
  surface plus its own product tests.
- `adopter-with-release-gate/` — adopter wiring `release-candidate-gate.yml`
  for its own release flow.
- `existing-adopter-migration/` — 2-phase migration verification using
  `run_doctor` (public surface) for legacy mixed-tree adopters.

## Technical changes

### Rationale schema extension (DELIB)

`deliberations` table gains a `rationale_summary` field so isolation
decisions can be cited succinctly in downstream artifacts without retrieving
the full deliberation body.

### Smart bridge poller

The Smart Bridge Poller (`scripts/run_smart_bridge_poller.vbs` +
`groundtruth-kb/scripts/bridge_poller_runner.py`) is now the canonical
bridge-monitoring path on Windows; runs every 15 seconds, kind-aware
routing (Codex on NEW/REVISED; Prime on GO/NO-GO), single-instance lock,
audit log under `.gtkb-state/bridge-poller/`. Doctor check
`_check_smart_bridge_poller` verifies activation end-to-end.

### Pytest feasibility

Full `python -m pytest groundtruth-kb/tests/` runs to completion (no
infinite loops or hangs). Per-lane runtime breakdown is documented in
`memory/release-readiness.md` `ISOLATION-017-CLOSEOUT` block.

### Ruff resolution scope

Per S330 owner sub-decision archived as
`DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`, ruff resolution
for v0.7.0-rc1 is narrowed to the `groundtruth-kb/` package (the platform
being released). Application-side ruff cleanup
(`tests/`, `scripts/`, `src/`) is tracked as a separate Agent Red
release-hardening work item, not blocking this rc.

## Breaking changes

- `gt project init` default mode changed from mixed-tree to managed-only.
  Existing scripts that depended on the mixed-tree default must pass
  `--include-app-tree` explicitly.
- The 12 isolation doctor checks are ERROR-level by default. Existing
  adopter projects with non-isolated layouts will fail `gt project doctor`
  until `gt project upgrade --apply` is run, or until the relevant checks
  are explicitly downgraded in the project's doctor config.

## Upgrade path

From v0.6.1:

```bash
pip install --upgrade groundtruth-kb==0.7.0rc1
gt project upgrade --apply --dir <path-to-existing-adopter>
gt project doctor --dir <path-to-existing-adopter>   # confirm isolation contracts
```

**Note for rc1:** `gt project upgrade` requires `--dir` pointing to the
existing adopter project; the location must satisfy the new isolation
contract (`<host_root>/applications/<name>`) where `host_root` is the
install-derived `_GT_KB_HOST_ROOT`. For pip-installed wheels this is the
venv root. Existing adopters whose layout pre-dates the isolation contract
should run `gt project upgrade --apply --accept-migration` to opt in to
the one-shot Slice 4 isolation migration. The pip-install adopter UX will
be simplified in v0.7.0 GA per `memory/work_list.md` row 36
(`GTKB-PIP-INSTALL-ADOPTER-UX-001`).

If `gt project doctor` reports isolation violations after upgrade, see
`docs/architecture/isolation.md` for the migration playbook. Adopter
projects that legitimately need mixed-tree behavior can scope down
specific isolation checks in their doctor config.

From v0.5.x: follow the v0.6.0 → v0.6.1 → v0.7.0-rc1 path stepwise.

## Release provenance

- Authorizing disposition: `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`
  (split into Slice 8 + Slice 8.5 per Codex F1 path 1; archived 2026-05-03).
- Slice 8 implementation bridge: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md`
  REVISED-2 (Codex GO at `-006`).
- VERIFIED upstream slices:
  - Slice 1 doctor checks: `bridge/gtkb-isolation-017-slice1-doctor-checks-012.md` (S326).
  - Slice 2 registry isolation: `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` (S326).
  - Slice 2.5 rationale schema: `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-008.md` (S327).
  - Slice 3 init defaults: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-014.md` (S327).
  - Slice 4 upgrade: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md` (S328; commit `61e50453`).
  - Slice 5 clean-adopter tests: `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-006.md` (S329; commit `dc8e58f8`).
  - Slice 6 docs: `bridge/gtkb-isolation-017-slice6-docs-2026-05-03-004.md` (S329; commit `9efd29bf`).
  - Slice 7 examples: `bridge/gtkb-isolation-017-slice7-examples-2026-05-03-004.md` (S329; commit `05774d6a`).

## Out of scope for this release

Deferred to v0.7.0 GA or later tracks:

- **Slice 5.5 (overlay refresh + disposability):** deferred per
  `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE`
  v1. Slice 5 ships overlay stale-detection (1 of 3 originally scoped
  overlay tests); refresh + disposability + the chroma-regen API they
  require are tracked at `memory/work_list.md` row 31.
- **Slice 8.5 (CI-green evidence):** filed AFTER Slice 8 commit lands;
  gates `v0.7.0-rc1` tag authorization. See
  `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` (planned).
- **Application-side ruff cleanup:** 1,943 ruff issues in adopter
  application code (`tests/`, `scripts/`, `src/`) tracked as a separate
  Agent Red release-hardening work item per
  `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`.
- **Standing-Backlog DB / Term Primer / Term Disambiguation Slice 2-7:**
  three Slice 1s landed in S327; Slices 2-7 deferred under feature freeze
  until v0.7.0-rc1 ships, per `memory/work_list.md` line 14.

## Acknowledgements

GTKB-ISOLATION-017 was a 7-session program (S326-S330) requiring 60+
bridge artifacts across 8 slices, 5+ owner sub-decisions archived as
DELIBs, and end-to-end verification of the isolation contract against
both fresh-init and migrating-adopter trees. The clean-adopter test suite
+ doctor checks + worked examples form a regression surface that should
prevent isolation drift from re-emerging after this release.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
