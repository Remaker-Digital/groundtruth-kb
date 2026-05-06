NEW

# Implementation Proposal - GTKB-PIP-INSTALL-ADOPTER-UX-001: Simplify Installed-Wheel Project Init

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** CLI/product UX implementation proposal
**Risk tier:** Medium-high (changes `gt project init` host-root behavior and isolation tests)
**Backlog item:** `GTKB-PIP-INSTALL-ADOPTER-UX-001`

---

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
  registered in `bridge/INDEX.md` with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  required specs and release evidence.
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
- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` - owner accepted
  rc1 limitation and targeted this follow-on.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "pip install adopter UX gt project init installed wheel host root site-packages --here --target" --limit 8
```

Relevant result: `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`.
Older packaging/installability records are context only.

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
   - keep application placement under `<host_root>/applications/<name>` unless
     a reviewed CLI option changes that contract.
4. Consider but do not necessarily ship:
   - `gt project init MyApp --here`
   - `gt project init MyApp --target <abs-path>`

Recommendation: first ship relaxed installed-wheel host-root behavior without
adding both new CLI shapes. Add `--here` or `--target` only if needed to make
the user-facing command unambiguous.

## Acceptance Criteria

- Editable/source checkout tests preserve the existing strict root-boundary
  behavior.
- Installed-wheel smoke can run `gt project init MyApp --gt-kb-root <tmp-host>`
  without discovering venv internals.
- A no-explicit-root installed-wheel smoke has a documented, deterministic
  default.
- Clean-adopter tests pass.
- Release notes/announcement can remove or narrow the rc1 limitation language.

## Test Plan

Suggested commands:

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

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO` with the minimal installed-wheel host-root
fix first, then revisit optional `--here` or `--target` CLI sugar if still
needed.

