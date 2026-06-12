REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: .gtkb-state/bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 007
Responds-To: bridge/gtkb-fab-12-agent-red-residue-sweep-006.md
Revises: bridge/gtkb-fab-12-agent-red-residue-sweep-003.md

Project Authorization: PAUTH-FAB12-20260610
Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4424

target_paths: ["groundtruth.toml", "pyproject.toml", "memory/MEMORY.md", "CLAUDE.md", ".groundtruth/formal-artifact-approvals/*.json", ".github/workflows/groundtruth-kb-tests.yml", ".github/workflows/python-tests.yml", ".github/workflows/sonarcloud.yml", ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/**", "sonar-project.properties", ".github/dependabot.yml", "scripts/membase_ci_seed.py", "scripts/session_self_initialization.py", "scripts/seed_tenant.py", ".claude/skills/deploy/**", ".claude/skills/seed-tenant/**", ".claude/skills/run-tests/**", ".claude/agents/**", ".claude/commands/**", "applications/Agent_Red/**", "config/governance/hygiene-sweep-patterns.toml", "platform_tests/scripts/**"]

# FAB-12 Agent-Red Residue Sweep - Revised Verification Envelope

## Summary

This revision responds to the NO-GO in
`bridge/gtkb-fab-12-agent-red-residue-sweep-006.md`. It does not claim new
implementation work. It corrects the approved envelope so Prime Builder can
refile the implementation report against a scope and evidence contract that can
be verified from the local bridge work before commit/push.

The underlying FAB-12 implementation direction remains the same: remove stale
Agent Red identity/config/tooling residue from GT-KB platform surfaces, keep all
Agent Red application-owned artifacts under `applications/Agent_Red/`, preserve
GT-KB root identity, and keep out-of-root home-cache reconciliation deferred.

## Specification Links

- `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-0001`
- `GOV-08`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `DELIB-FAB12-REMEDIATION-20260610` - owner decisions for root identity,
  repo memory authority, config/CI repair, and in-root Agent Red tooling
  relocation.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` - Fable Investigation charter and
  remediation sequence.
- `DELIB-0834` and `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - reference-adopter
  framing and application placement boundaries.
- `bridge/gtkb-fab-12-agent-red-residue-sweep-004.md` - prior GO.
- `bridge/gtkb-fab-12-agent-red-residue-sweep-006.md` - NO-GO requiring target
  scope correction, CI evidence correction, durable artifact set evidence, and
  durable approval-packet evidence.

## NO-GO Response

### F1 - SonarCloud Workflow Target Path

`bridge/gtkb-fab-12-agent-red-residue-sweep-006.md` correctly found that the
implementation touched `.github/workflows/sonarcloud.yml` while the approved
`target_paths` omitted that workflow. This revision adds
`.github/workflows/sonarcloud.yml` to the approved target path list.

The SonarCloud workflow is in scope because FAB-12's config/CI repair area
explicitly covers stale Agent Red path residue in CI and quality-gate surfaces.
The follow-on implementation report must include this file in both file-change
evidence and local workflow/static verification evidence.

### F2 - Remote Workflow Dispatch Acceptance Evidence

The original acceptance wording was too broad for a local pre-commit bridge
implementation pass. This revision narrows FAB-12 verification as follows:

- Required before VERIFIED: local static workflow/config assertions proving the
  affected workflow files and quality-gate configuration no longer reference
  stale Agent Red/root test paths, plus focused pytest/ruff/compile/config
  checks.
- Not required before VERIFIED: remote GitHub Actions `workflow_dispatch` runs,
  because bridge implementation occurs on an unpushed local worktree and remote
  runs cannot exercise uncommitted local file content.
- Still required before release/deploy treatment: normal post-push CI or
  release-candidate evidence under the repository's release readiness process.

This preserves `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` without making a
local bridge verification depend on remote evidence for content that is not yet
on GitHub.

### F3 - Durable Artifact Set

The follow-on implementation report must prove that its claimed file set is a
coherent durable artifact candidate. Required evidence:

- `git status --short` scoped to all FAB-12 target paths.
- `git diff --name-only --cached` after staging the intended FAB-12 artifact
  set, or an equivalent explicit statement that no staging is being claimed.
- No same-file staged/unstaged ambiguity for files claimed as the FAB-12 durable
  artifact set.
- Relocated files under `applications/Agent_Red/` must be tracked/staged or the
  report must not claim them as durable.
- Old root files that were moved must be represented as deletions in the same
  artifact set.

### F4 - Protected Narrative Approval Packet

The follow-on implementation report must make the FAB-12 `CLAUDE.md` approval
packet durable. The expected evidence is either:

- `git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json` followed by staged readback; or
- a different tracked approval-evidence path explicitly covered by target
  scope.

Working-tree-only ignored approval evidence is not enough for a protected
narrative edit.

## Corrected Acceptance Criteria

A follow-on FAB-12 implementation report may be VERIFIED if it provides all of
this evidence:

1. Bridge applicability preflight passes with no missing required/advisory
   specs.
2. ADR/DCL clause preflight has zero blocking gaps.
3. Focused FAB12 regression pytest passes.
4. Adjacent startup/governance regression pytest passes.
5. Ruff check passes for changed Python/test files.
6. Ruff format check passes for changed Python/test files.
7. Python compile checks pass for changed Python scripts/tests.
8. TOML/JSON parse checks pass for changed config and approval packet files.
9. Static workflow/config assertions cover `groundtruth-kb-tests.yml`,
   `python-tests.yml`, `sonarcloud.yml`, `sonar-project.properties`,
   `dependabot.yml`, templates, and issue templates where changed.
10. Git/index evidence shows the final claimed FAB-12 artifact set is coherent
    and durable, including relocated Agent Red files and old root deletions.
11. The protected `CLAUDE.md` approval packet is tracked/staged or replaced by
    equivalent tracked approval evidence.
12. The report states remote `workflow_dispatch` was not required for local
    verification and identifies post-push CI/release readiness as downstream
    evidence.

## Specification-Derived Verification Plan

| Specification | Follow-on verification evidence |
|---|---|
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | FAB12 regression asserts root platform identity and Agent Red files under `applications/Agent_Red/`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Regression covers relocation of Agent Red skills, commands, agents, and `seed_tenant.py`. |
| `ADR-0001` / `GOV-08` | Regression covers root `memory/MEMORY.md`, `CLAUDE.md`, and approval packet hash. |
| `GOV-ARTIFACT-APPROVAL-001` | Approval packet parse/hash and durable tracked/staged evidence. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Static workflow/config assertions plus local pytest/ruff/compile/config checks; remote CI deferred to post-push release readiness. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Follow-on report records exact commands and observed results. |

## Review Request

Requesting Loyal Opposition review of this narrowed verification envelope. If
accepted, Prime Builder will use it to produce a new implementation report that
addresses the four NO-GO findings without expanding FAB-12 beyond the existing
PAUTH, root-boundary, and Agent Red isolation constraints.
