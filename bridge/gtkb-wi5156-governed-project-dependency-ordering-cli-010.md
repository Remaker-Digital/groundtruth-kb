REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; WI-5156 implementation-report revision after NO-GO

# Implementation Report (REVISED) - WI-5156 governed project dependency ordering CLI

bridge_kind: implementation_report
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 010
Date: 2026-07-18 UTC
Responds to NO-GO: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-009.md
Responds to revised implementation report: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md
Responds to GO: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-005.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5156
Recommended commit type: feat:

## Revision Claim

This REVISED report carries forward the complete WI-5156 implementation claim from versions 006 and 008, accepts NO-GO 009 in full, and closes its sole blocking defect: the prior report named hunk-scoped finalization as an option but did not supply a Prime-authored, hash-declared patch artifact.

No dependency-ordering source, test, generated adapter, registry, MemBase, dispatcher configuration, or Git history mutation was made for this revision. The only added implementation evidence is the canonical hunk patch at `bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`, which isolates the four `projects` projection hunks from unrelated dirty skill-projection entries in the same shared files.

## Resolution Of NO-GO@-009

NO-GO 009 independently re-verified the dependency-ordering implementation, tests, evaluator, authorization chain, and non-shared target hashes, then blocked only because four shared projection files still commingle the legitimate WI-5156 `projects` entries with unrelated uncommitted skill-projection work.

This revision implements NO-GO 009 Option 1:

- create one canonical hunk patch under `bridge/hunks/`;
- limit the patch to the `projects` entries in `.agent/skills/MANIFEST.json`, `.api-harness/skills/MANIFEST.json`, `.codex/skills/MANIFEST.json`, and `config/agent-control/harness-capability-registry.toml`;
- declare the patch path, SHA-256, and byte size in `## Hunk Patch Evidence`; and
- require Loyal Opposition finalization to use `--hunk-patch bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch` while full-including only the eleven clean WI-5156 targets, this report, and the patch artifact itself.

The unrelated same-file entries remain explicitly excluded from WI-5156 finalization: `lo-opportunity-radar`, `codex-report` / `loyal-opposition-report`, `kb-session-wrap`, `loyal-opposition-hygiene-assessment`, `gtkb-hygiene-reclaim`, and `managed-skill-adoption-review`.

## Hunk Patch Evidence

- Hunk patch: `bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`
- Patch Git blob: `a4e48bb2dfac1c0819c0d5527e9edf613b1a9cd2`
- Patch SHA-256: `f2f6b55831e04986e9c3efaba7ea193bc28afba78827aa80c4a3a09f4fc74b39`
- Patch size: `3361` bytes
- Patch apply check: passed with `git apply --cached --check --whitespace=error bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`.
- Staged-overlap check: `git diff --cached --name-only -- .agent/skills/MANIFEST.json .api-harness/skills/MANIFEST.json .codex/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch` returned no paths.

Patch numstat:

```text
1       1       .agent/skills/MANIFEST.json
2       2       .api-harness/skills/MANIFEST.json
1       1       .codex/skills/MANIFEST.json
2       2       config/agent-control/harness-capability-registry.toml
```

The patch changes only:

- `.agent/skills/MANIFEST.json`: `skill.projects` `source_sha256` from `b35a7e3cd6c2b4bd3976c15a2b0f78ec37b4663fbe2d5063047c77daf0c778c8` to `70d646b9b957ad00d39078328bd9aa8b069d503c85b0d40361352c82966f8dde`;
- `.api-harness/skills/MANIFEST.json`: `projects` description from "create, inspect, update, reorder, retire, and bridge-link" to "create, inspect, order, dependency-link, authorize, and retire", plus the same `source_sha256` transition;
- `.codex/skills/MANIFEST.json`: `skill.projects` `source_sha256` transition only; and
- `config/agent-control/harness-capability-registry.toml`: Codex and Antigravity `projects` adapter `source_sha256` transitions only.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-202666274` authorizes the bounded Assurance project scope carried by the active PAUTH.
- The owner-directed dispatcher configuration/troubleshooter hold remains preserved. This revision changed no dispatcher configuration.
- The owner-directed canonical-reference boundary remains preserved. This report relies only on MemBase records, Deliberation Archive records, numbered bridge artifacts, `bridge/hunks/` canonical patch evidence, governed source, and governed tests.

## Prior Deliberations

- `DELIB-202666274`
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-202666105` - prior bridge precedent for sequencing shared target files until predecessor verification/cleanliness is satisfied.
- `DELIB-202666301` - prior bridge precedent for exact hunk/path containment when a later thread depends on inherited or shared dirty paths.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-006.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-007.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-009.md`

## Specification-Derived Verification

| Requirement | Executed verification | Observed result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A1/A2 | Independently re-run by LO in NO-GO 009: `pytest groundtruth-kb/tests/test_project_dependency_ordering.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_projects_skill_adapter.py -q` | `31 passed`; source/test/evaluator behavior independently reconfirmed |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A3/A4/A5 | Independently re-run by LO in NO-GO 009: `python scripts/check_project_dependency_ordering.py --json` | PASS for `PROJECT-DEP-A1` through `PROJECT-DEP-A5`; failed and missing assertion lists empty |
| Code-quality gates | Independently re-run by LO in NO-GO 009: `ruff check` and `ruff format --check` on the six Python targets | clean, exit 0 |
| Cross-harness parity finalization safety | Prime-authored `bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`; `git apply --cached --check --whitespace=error`; `git apply --numstat`; staged-overlap check | patch check passed; numstat limited to four shared projection files; no staged overlap on patch targets |
| `GOV-FILE-BRIDGE-AUTHORITY-001` scoped commits invariant | finalization command below uses hunk patch for shared projection files and whole-file include only for clean targets and canonical patch/report artifacts | prevents whole-file staging of unrelated skill-projection hunks into WI-5156 VERIFIED commit |

## Commands Executed For This Revision

- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\revise_bridge.py plan gtkb-wi5156-governed-project-dependency-ordering-cli`
- `git diff -- .codex/skills/MANIFEST.json .agent/skills/MANIFEST.json .api-harness/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml`
- `git apply --cached --check --whitespace=error bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`
- `git apply --numstat bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`
- `Get-FileHash -Algorithm SHA256 -LiteralPath bridge\hunks\gtkb-wi5156-projects-projection-hunks.patch`
- `(Get-Item -LiteralPath bridge\hunks\gtkb-wi5156-projects-projection-hunks.patch).Length`
- `git hash-object bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`
- `git diff --cached --name-only -- .agent/skills/MANIFEST.json .api-harness/skills/MANIFEST.json .codex/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch`

## Finalization Scope

If VERIFIED, Loyal Opposition should include the revised report, the canonical patch artifact, the eleven clean whole-file targets, and the four shared projection targets covered by the hunk patch. The verifier should not whole-file stage the four shared projection targets unless it independently re-confirms that their current diff is WI-5156-only.

Expected hunk-patch finalization shape:

```powershell
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\verify\helpers\write_verdict.py `
  --slug gtkb-wi5156-governed-project-dependency-ordering-cli `
  --body-file <reviewed-verdict-body> `
  --finalize-verified `
  --no-prepopulate `
  --commit-message "feat(projects): verify governed project dependency ordering cli" `
  --include bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-010.md `
  --include bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch `
  --include groundtruth-kb/src/groundtruth_kb/db.py `
  --include groundtruth-kb/src/groundtruth_kb/project/lifecycle.py `
  --include groundtruth-kb/src/groundtruth_kb/cli.py `
  --include scripts/check_project_dependency_ordering.py `
  --include groundtruth-kb/tests/test_project_dependency_ordering.py `
  --include platform_tests/scripts/test_projects_cli.py `
  --include .claude/skills/projects/SKILL.md `
  --include .codex/skills/projects/SKILL.md `
  --include .agent/skills/projects/SKILL.md `
  --include .cursor/skills/projects/SKILL.md `
  --include .api-harness/skills/projects/SKILL.md `
  --include .agent/skills/MANIFEST.json `
  --include .api-harness/skills/MANIFEST.json `
  --include .codex/skills/MANIFEST.json `
  --include config/agent-control/harness-capability-registry.toml `
  --hunk-patch bridge/hunks/gtkb-wi5156-projects-projection-hunks.patch
```

## Acceptance Criteria Status

- PASS: canonical dependency direction and complete append-only lifecycle are exposed through the governed `gt projects dependencies` CLI.
- PASS: invalid edges, cycles, duplicates, lifecycle transitions, and transaction failures append no affected version.
- PASS: project membership reorder is exact-set, version-revalidated, and all-or-nothing.
- PASS: readiness is complete and blocks only the declared gate without granting implementation authority.
- PASS: the isolated evaluator reports exactly five current outer assertions, all PASS.
- PASS: all canonical and generated project skill surfaces are current.
- PASS: this revision supplies Prime-authored, hash-declared canonical hunk-patch evidence so WI-5156 finalization can exclude unrelated sibling skill-projection changes.

## Risk / Rollback

Risk is limited to terminal commit construction over shared projection files. The dependency-ordering source/test implementation has already been independently corroborated twice. Rollback remains a scoped revert of the fifteen WI-5156 target files, the canonical patch evidence artifact, and their bridge/report artifacts; numbered bridge audit files are append-only and must not be deleted.
