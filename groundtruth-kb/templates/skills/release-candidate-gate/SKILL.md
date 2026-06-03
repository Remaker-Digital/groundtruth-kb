---
name: release-candidate-gate
description: Run a non-deploying release-candidate gate before treating an adopter build as production deployable. Covers security scans, dependency audit, targeted regression tests, frontend builds, and GroundTruth governance adoption checks.
argument-hint: [--python-only|--frontend-only|--full]
allowed-tools: Bash, Read, Grep
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  category: release-readiness
  governance: production-release, GroundTruth-KB, Deliberation-Archive, MemBase
---

# Release Candidate Gate

Use this skill before calling an adopter build production-ready. The gate is
non-deploying: it does not push images, update cloud resources, call live
services, or mutate external infrastructure.

## Template Parameters

- `{{adopter_python_scan_targets}}` - Python source/test paths for Ruff.
- `{{adopter_security_scan_target}}` - Python source path for Bandit.
- `{{adopter_targeted_tests}}` - pytest targets for release regressions.
- `{{adopter_frontend_projects}}` - semicolon-separated npm project paths.
- `{{adopter_governance_checks}}` - semicolon-separated governance commands.
- `{{adopter_requirements_file}}` - requirements file for dependency audit.

When a parameter is omitted by the adopter scaffold, the bundled script uses
safe local defaults.

## Commands

Run the complete local gate:

```powershell
python scripts/release_candidate_gate.py --include-frontend
```

Run the Python/security/governance side only:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

Run the frontend side only:

```powershell
python scripts/release_candidate_gate.py --skip-python --include-frontend
```

CI should prove the Python gate under the production target interpreter:

```powershell
python scripts/release_candidate_gate.py --require-python 3.12 --skip-frontend
```

## Readiness Checks

- Security scans: redacted GroundTruth secret scan and Bandit over the adopter security target.
- Dependency audit: pip-audit against the adopter requirements file.
- Targeted regression tests: pytest over the adopter release-regression targets.
- Frontend builds: npm test/build for configured frontend projects.
- GroundTruth governance adoption: configured governance commands such as project doctor or release-readiness checks.

## Required Evidence

Before reporting GO confidence, record:

- release gate command, result, and key counts;
- any skipped live/deploy checks and why they are out of scope;
- MemBase update path or KnowledgeDB document ID when relevant;
- Deliberation Archive source reference or DELIB ID when relevant;
- regression test files that would fail if the change regressed.

## Stop Conditions

Stop and report NO-GO if:

- the generated production manifest exists or is still tracked;
- secret scan, Ruff E/F, Bandit, or pip-audit gates fail;
- targeted release-regression tests fail;
- configured frontend tests or builds fail;
- GroundTruth governance adoption checks fail;
- required production Python-version proof is missing.
