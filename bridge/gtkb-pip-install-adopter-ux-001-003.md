REVISED

# Implementation Proposal (REVISED-1) - GTKB-PIP-INSTALL-ADOPTER-UX-001

Author: Prime Builder (Codex, harness A)
Drafted: 2026-05-06
Type: CLI/product UX implementation proposal
Risk tier: Medium-high (changes `gt project init` host-root behavior and isolation tests)
Backlog item: `GTKB-PIP-INSTALL-ADOPTER-UX-001`
Supersedes: `bridge/gtkb-pip-install-adopter-ux-001-001.md`
Addresses: Codex NO-GO at `bridge/gtkb-pip-install-adopter-ux-001-002.md`
Requested verdict: `GO`

## Revision Summary

Codex `-002` found one blocking issue: the proposal depended on an owner
decision accepting the rc1 install-UX limitation but lacked the required
`Owner Decisions / Input` section. This revision adds that section and narrows
the optional CLI-shape question.

## Background

Slice 8 install smoke proved the installed wheel works only with an awkward
command shape: discover `_GT_KB_HOST_ROOT` from the installed package, create
`<host_root>/applications/<name>`, and pass both `--gt-kb-root` and `--dir`.
For a pip-installed wheel, `_GT_KB_HOST_ROOT` resolves to the virtual
environment root, which is not the adopter's intended project home.

Owner accepted this limitation for `v0.7.0-rc1` and added this row for
`v0.7.0 GA`. This proposal files the governed fix.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites required specs and release evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must map
  install-smoke and isolation tests to the cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 36 of
  `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the rc1 limitation and GA fix must
  remain traceable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - editable installs must preserve
  the strict in-root applications boundary, while installed wheels need a sane
  adopter host-root model.
- `.claude/rules/canonical-terminology.md` - GT-KB platform behavior must be
  separated from Agent Red application behavior.
- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` - owner accepted
  rc1 limitation and targeted this follow-on.
- `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-008.md` - Codex
  NO-GO that surfaced the install-UX defect.
- `bridge/gtkb-pip-install-adopter-ux-001-002.md` - current NO-GO being
  addressed.

## Owner Decisions / Input

Owner decision:

- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` records owner
  selection of Path A: "Narrow fix; acknowledge rc limitation."

Rc1 limitation accepted:

- `v0.7.0-rc1` may ship with the known awkward installed-wheel command shape.
- Slice 8 documentation and verifier use the working explicit
  `--gt-kb-root` + `--dir` setup instead of claiming a seamless pip-installed
  adopter UX.

GA follow-on scope:

- Fix `_GT_KB_HOST_ROOT` / host-root resolution for installed wheels so
  adopters do not need to discover virtual-environment internals.
- Preserve strict root-boundary behavior for editable/source checkouts.
- Keep project placement under `<host_root>/applications/<name>` unless a later
  reviewed proposal changes that contract.

Optional CLI shapes:

- `--here` and `--target` are deferred from this revision.
- This proposal requests `GO` for the minimal installed-wheel host-root fix
  only. The implementation report may recommend a later CLI-shape proposal if
  the minimal fix still leaves ambiguous UX.

What this proposal does not authorize:

- Weakening editable checkout root-boundary enforcement.
- Publishing `v0.7.0-rc1` or `v0.7.0 GA`.
- Moving Agent Red or changing application repository topology.
- Broad scaffold redesign beyond the installed-wheel host-root defect.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "pip install adopter UX gt project init installed wheel host root site-packages --here --target" --limit 8
python -m groundtruth_kb deliberations search "Slice 8 install UX limitation gt project init pip wheel v0.7.0 GA --gt-kb-root" --limit 8
```

Relevant result:

- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`

Adjacent context:

- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`
- `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-008.md`

## Proposed Scope

1. Modify `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` so host-root
   resolution distinguishes editable/source checkout from installed wheel.
2. Preserve current strict behavior for editable/source checkout:
   - `_GT_KB_HOST_ROOT` remains the checked-out GT-KB root.
   - `--gt-kb-root` must match it.
   - application targets must live directly under `<host_root>/applications/`.
3. Add installed-wheel behavior:
   - detect installed-wheel context using a robust heuristic such as
     `site-packages` in `Path(__file__).resolve().parts`;
   - allow `--gt-kb-root` to define the adopter host root;
   - default host root to current working directory when no explicit root is
     provided;
   - keep application placement under `<host_root>/applications/<name>`.

## Acceptance Criteria

- Editable/source checkout tests preserve the existing strict root-boundary
  behavior.
- Installed-wheel smoke can run `gt project init MyApp --gt-kb-root <tmp-host>`
  without discovering venv internals.
- A no-explicit-root installed-wheel smoke has a documented, deterministic
  default.
- Clean-adopter tests pass.
- Release notes/announcement can remove or narrow the rc1 limitation language.
- No `--here` or `--target` option is added unless the implementation files a
  revised proposal first.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Pass condition |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify `bridge/INDEX.md` latest entry points to post-implementation report | Latest entry is correct |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-pip-install-adopter-ux-001` | `missing_required_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect report for rc1 limitation, GA scope, and CLI-shape deferral | Required owner-decision fields present |
| T-editable-root-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing scaffold isolation tests | Editable/source checkout strict root behavior preserved |
| T-installed-wheel-1 | GA UX follow-on | Installed-wheel smoke with explicit `--gt-kb-root <tmp-host>` | Init succeeds without venv-root discovery |
| T-clean-adopter-1 | Clean-adopter release path | Run clean-adopter tests | Tests pass |

## Suggested Commands

```powershell
cd groundtruth-kb
python -m pytest tests/test_scaffold_isolation.py tests/test_scaffold_provider_templates.py tests/adopter/ -q --tb=short
python -m pytest tests/test_cli.py -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

The implementation report must include an installed-wheel smoke comparable to
`scripts/_verify_slice8_closeout.py`, but proving the simplified command shape.

## Out Of Scope

- Weakening editable checkout root-boundary enforcement.
- Publishing `v0.7.0-rc1`.
- Moving Agent Red.
- Broad scaffold redesign beyond the installed-wheel UX defect.
- Adding `--here` or `--target` in this slice.

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO` with the minimal installed-wheel host-root
fix first. Revisit `--here` or `--target` only if the implementation evidence
shows the minimal fix is not enough.

