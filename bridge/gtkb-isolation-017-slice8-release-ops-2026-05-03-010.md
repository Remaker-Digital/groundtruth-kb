NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 8 Release Ops Revision 1

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-009.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice8-release-ops-2026-05-03`
at latest status `REVISED` with
`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-009.md`.

I reviewed the full bridge thread (`-001` through `-009`) against
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`,
the accepted REVISED-2 proposal at `-005`, the prior NO-GO at `-008`, and the
post-implementation verification gate.

I ran:

```powershell
python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 Slice 8 install UX limitation release ops"
python scripts/_verify_slice8_closeout.py
python -c "import tempfile; print(tempfile.gettempdir())"
```

Observed results:

- deliberation search completed successfully and returned no rows in this
  environment;
- composite verifier exited 0 with `8 pass, 1 deferred (intentional), 0 fail`;
- B5 specifically passed: `build + pip install + gt --version (0.7.0rc1) + gt project init ... all succeeded`;
- full pytest inside the composite verifier reported `1945 passed, 1 skipped, 1 warning in 523.23s`;
- Python's default temp directory in this environment is
  `C:\Users\micha\AppData\Local\Temp`.

## Prior Deliberations

No prior deliberations were found for the search query above in this
environment. The relevant active authority remains the bridge thread, the
formal approval packets and DELIB IDs cited in `-009`, and the root-boundary
rule loaded from `.claude/rules/project-root-boundary.md`.

## Findings

### F1 - Blocking: B5 verification depends on an outside-root temp venv and scaffolded adopter

Claim: The implementation cannot receive VERIFIED because the revised B5
installed-wheel smoke depends on a runtime path outside `E:\GT-KB`, creating
the installed test environment and scaffolded adopter under Python's default
temp directory rather than under the mandatory GT-KB root boundary.

Evidence:

- `.claude/rules/file-bridge-protocol.md` requires every bridge proposal,
  review, implementation report, and verification to comply with
  `.claude/rules/project-root-boundary.md`; a bridge item that depends on a
  live path outside the allowed roots is `NO-GO`.
- `.claude/rules/project-root-boundary.md` says all active GT-KB files and
  artifacts must be within `E:\GT-KB`, GT-KB application files must be within
  `E:\GT-KB\applications\`, and no GT-KB artifact may be created, read as a
  live dependency, updated, verified, or required from outside `E:\GT-KB`.
- The revised verifier creates B5's temporary root with
  `tempfile.mkdtemp(prefix="gtkb-slice8-b5-smoke-")`
  (`scripts/_verify_slice8_closeout.py:142`).
- In this environment, `tempfile.gettempdir()` resolves to
  `C:\Users\micha\AppData\Local\Temp`, outside the permitted `E:\GT-KB` root.
- The same B5 check creates a venv under that temp root, installs the wheel
  there, derives `_GT_KB_HOST_ROOT` from that installed package, creates
  `<host_root>/applications/SmokeApp`, runs `gt project init`, and verifies
  the scaffolded `groundtruth.toml` (`scripts/_verify_slice8_closeout.py:142-206`).
- The `-009` report marks the root-boundary gate PASS only for modified/created
  repository paths and does not account for the outside-root verification
  dependency or scaffolded application path (`bridge/...-009.md`, root-boundary
  gate section).

Risk / impact: The B5 smoke now proves the installed-wheel command shape works,
but it proves it by creating and verifying a GT-KB-style scaffold outside the
mandatory project root. That weakens the release evidence because the verified
path violates the same root-boundary rule that the bridge protocol makes a
hard gate.

Recommended action:

Revise `scripts/_verify_slice8_closeout.py` so the installed-wheel smoke uses
an explicit in-root scratch path, for example under `E:\GT-KB\.tmp\...`, and
sets the venv and `SmokeApp` target inside that path. The revised report should
include the exact in-root paths used by B5 and a fresh composite verifier run.
If the team wants installed-wheel smoke output outside `E:\GT-KB`, add an
owner-approved root-boundary exception first; the current sandbox exception is
limited to rehearsal-class output and does not cover Slice 8 release
verification.

Decision needed from owner: no, unless Prime Builder wants to create a new
root-boundary exception instead of keeping B5 verification in-root.

## Passing / Non-Blocking Checks

- F1/F2 from `-008` are functionally addressed: the composite verifier now
  performs build + pip install + `gt --version` + `gt project init`, and the
  announcement/release-notes surfaces now document the explicit host-root
  limitation and working command shape.
- Composite verifier: PASS for the in-scope functional checks, with B6
  intentionally deferred to Slice 8.5.
- B1 version: PASS inside composite verifier; observed `0.7.0rc1`.
- B2 narrowed ruff: PASS inside composite verifier.
- B3 pytest: PASS inside composite verifier; observed `1945 passed, 1 skipped,
  1 warning in 523.23s`.
- B6 split disposition remains acceptable at the Slice 8 level; CI-green
  evidence is still deferred to Slice 8.5 and tag authorization remains gated.

## Gate Checks

- Root-boundary gate: FAIL. B5 verification creates and verifies the installed
  venv plus scaffolded adopter under Python's outside-root temp directory.
- Specification-linkage carry-forward: PASS.
- Mandatory specification-derived verification gate: FAIL until the B5 smoke is
  rerun with root-contained verification paths or an explicit owner-approved
  exception.
- Bridge audit trail: PASS.

## Verdict

NO-GO. The B5 install smoke is now real, but the verification path must be
root-contained before Slice 8 can receive VERIFIED.

File bridge scan: 1 entry processed.
