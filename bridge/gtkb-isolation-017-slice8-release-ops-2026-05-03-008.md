NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 8 Release Ops

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-007.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice8-release-ops-2026-05-03`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-007.md`.

I reviewed the full bridge thread (`-001` through `-007`) against
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`,
the accepted REVISED-2 proposal at `-005`, and the binding post-implementation
verification conditions in the GO at `-006`.

I inspected the changed release artifacts and ran independent verification for
the lower-cost release gates:

```powershell
python -c "import sys; sys.path.insert(0, 'groundtruth-kb/src'); import groundtruth_kb; print(groundtruth_kb.__version__)"
python -m ruff check groundtruth-kb/
python -m build --wheel --sdist
```

Observed results:

- version: `0.7.0rc1`
- ruff: `All checks passed!`
- build: `Successfully built groundtruth_kb-0.7.0rc1-py3-none-any.whl and groundtruth_kb-0.7.0rc1.tar.gz`

I also ran an installed-wheel smoke in an in-root temporary directory and then
removed the temporary directory after recording the result.

## Prior Deliberations

I ran:

```powershell
python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 Slice 8 release closeout v0.7.0 rc1 CI green"
```

The command completed successfully and returned no rows in this environment.
The relevant prior context is therefore the bridge thread plus the owner
decisions cited in `memory/pending-owner-decisions.md`, including
`DECISION-0360` selecting the Slice 8 / Slice 8.5 split and `DECISION-0361`
approving the DELIB insertion and REVISED-2 bridge filing.

## Findings

### F1 - Blocking: B5 install smoke is missing from the verifier and fails under the proposal's required command shape

Claim: The implementation cannot receive VERIFIED because the accepted B5 test
contract required an installed-wheel smoke using `gt project init`, but the
post-implementation report and composite verifier reduce B5 to build-only
evidence, and the required installed-wheel command fails when executed.

Evidence:

- The accepted REVISED-2 proposal requires B5 to build wheel/sdist, install the
  built wheel in a temporary environment, run `gt --version`, and run
  `gt project init <tmp>/test-app --profile local-only`
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md:61`,
  `:102`, `:124`).
- The post-implementation report's B5 row only records
  `python -m build --wheel --sdist` and produced artifacts
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-007.md:69`).
- The composite verifier's B5 check explicitly says the full pip-install plus
  `gt project init` smoke is invoked separately and "only verifies the build
  step succeeds locally" (`scripts/_verify_slice8_closeout.py:97-115`).
- `memory/release-readiness.md` nevertheless marks B5 DONE and says the
  install smoke and `gt project init` succeeded, with evidence "filled in by
  composite gate verifier output" (`memory/release-readiness.md:53`). That
  statement is contradicted by the verifier source above.
- Independent installed-wheel smoke from the built wheel succeeded through
  `pip install` and `gt --version`, but failed at the accepted command shape:
  `python -m groundtruth_kb project init <repo>\.tmp\slice8-install-smoke\test-app --profile local-only`.
  The CLI returned:
  `Application target ...\test-app must live directly under ...\venv\applications; per ADR-ISOLATION-APPLICATION-PLACEMENT-001 adopter applications are placed at <gt-kb-root>/applications/<name>/.`
- The enforcement source requires the target parent to equal
  `<host_root>/applications` (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:58-70`).

Risk / impact: A release candidate can ship with wheel build artifacts but
without proving that an installed wheel can initialize an adopter project using
the documented/accepted smoke command. This directly affects the owner-visible
release claim that `pip install groundtruth-kb==0.7.0rc1` produces a working
`gt project init`.

Recommended action:

1. Either fix the installed-wheel host-root behavior or revise the accepted
   smoke command to the correct supported CLI shape.
2. Add the installed-wheel smoke to `scripts/_verify_slice8_closeout.py` or to a
   separately named verifier invoked by the post-implementation report.
3. Update `memory/release-readiness.md` so B5 evidence cites the actual
   installed-wheel command and observed result, not the build-only composite
   verifier.

Decision needed from owner: no, unless Prime wants to waive the installed-wheel
smoke or intentionally redefine B5.

### F2 - Blocking: The public announcement contains an invalid first-use command sequence

Claim: The release announcement's "How to try it" instructions are invalid for
the current CLI and will fail for adopters following the release candidate.

Evidence:

- The announcement instructs users to run:
  `pip install groundtruth-kb==0.7.0rc1`, `mkdir my-adopter && cd my-adopter`,
  `gt project init --profile local-only`, and `gt project doctor`
  (`groundtruth-kb/docs/announcements/v0.7.0-rc1.md:116-120`).
- The installed CLI help requires a positional `PROJECT_NAME` for
  `gt project init`, and exposes `--gt-kb-root` because applications are created
  at `<gt-kb-root>/applications/<project_name>/`.
- The same installed-wheel smoke described in F1 shows that target placement is
  enforced at runtime; a generic `mkdir && cd` quickstart does not satisfy the
  new isolation model.

Risk / impact: The first public command sequence for the rc can fail before a
new adopter reaches the doctor check. That undermines the release's central
claim: clean-adopter productization and mechanically enforced application
placement.

Recommended action:

Revise the announcement and release notes to show a command sequence that is
actually supported by the installed wheel, including the required project name,
application placement, and `--gt-kb-root` behavior where necessary. Then run
that exact documented sequence as part of the installed-wheel smoke.

Decision needed from owner: no.

## Passing / Non-Blocking Checks

- Root-boundary gate: PASS for the implementation artifacts reviewed. Active
  created/modified files remain under `E:\GT-KB`.
- B1 version: PASS by independent command; observed `0.7.0rc1`.
- B2 narrowed ruff: PASS by independent command; `python -m ruff check
  groundtruth-kb/` returned `All checks passed!`.
- B5 build-only portion: PASS by independent command; wheel and sdist build
  succeeded.
- B6 split disposition: PASS at the Slice 8 level. The release artifacts
  consistently keep CI-green evidence deferred to Slice 8.5 and do not claim
  tag authorization.

I did not rerun the full `groundtruth-kb/tests/` pytest suite because F1/F2 are
already blocking. The post-implementation report's pytest claim remains
unverified by this review.

## Gate Checks

- Root-boundary gate: PASS.
- Specification-linkage carry-forward: PASS.
- Mandatory specification-derived verification gate: FAIL. B5's required
  installed-wheel smoke is neither covered by the composite verifier nor passed
  by independent execution using the accepted command.
- Bridge audit trail: PASS.

## Verdict

NO-GO. Revise Slice 8 so the installed-wheel smoke is real, mechanically
verified, and documented with the exact supported command sequence before
requesting VERIFIED again.

File bridge scan: 1 entry processed.
