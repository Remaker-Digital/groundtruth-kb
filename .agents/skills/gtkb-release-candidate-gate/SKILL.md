---
name: gtkb-release-candidate-gate
description: Run the non-deploying Agent Red release-candidate gate before treating a build as production deployable. Covers Python security checks, targeted regression tests, frontend builds, and GroundTruth governance adoption checks.
argument-hint: [--python-only|--frontend-only|--full]
allowed-tools: Bash, Read, Grep
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: groundtruth-kb
  category: release-readiness
  governance: production-release, GroundTruth-KB, native-authority
---
# Release Candidate Gate

Use this skill before calling a build production-ready. The gate is non-deploying:
it runs declared local checks and may read the configured native authority.
It does not authorize or perform a deployment, push images or update Azure resources.
Use the current immutable role/activity and report only the scope actually measured.

## Commands

Run the complete local gate:

```powershell
python scripts/release_candidate_gate.py --include-frontend
```

Run the Python/security side only:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

Run the frontend side only:

```powershell
python scripts/release_candidate_gate.py --skip-python --include-frontend
```

CI must prove the Python gate under the production target interpreter:

```powershell
python scripts/release_candidate_gate.py --require-python 3.12 --skip-frontend
```

## Required Evidence

Before reporting the candidate's readiness, record:

- release gate command, result, and key counts;
- any skipped live/deploy checks and why they are out of scope;
- relevant current canonical record IDs and versions, with fresh native readback;
- the selected source/commit, interpreter, application scope and actual result evidence;
- any unresolved duty, failed check or pending independent review; historical rationale is not current authority;
- regression test files that would fail if the change regressed.

## Stop Conditions

Stop the readiness claim and report the concrete failed check if:

- the generated production gateway manifest exists or is still tracked;
- Ruff E/F, import-cycle, Bandit, or pip-audit gates fail;
- targeted auth/config/deploy/release-gate tests fail;
- frontend tests or any admin/widget build fails;
- GroundTruth-KB governance adoption checks fail;
- Python 3.12 proof is missing for the build being considered for deployment.

A local gate result is not a bridge verdict. Only the eligible independent review
context may author the corresponding formal verdict; this skill does not switch
roles or grant release permission. Do not create a deliberation archive or
require a DELIB identifier to make the result durable.
