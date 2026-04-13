# Desktop Setup for Same-Day Prototype Work

This guide is for a client team that wants to install `groundtruth-kb` from
GitHub and begin building a prototype service on the same day. The target is a
local-first setup that supports:

- specification-first project management with GroundTruth
- AI-assisted implementation on a desktop workstation
- an upgrade path toward an Agent Red-like architecture

## Choose your setup depth

| Setup path | Best for | Time to first useful session |
|------------|----------|------------------------------|
| Core local prototype | Solo or small-team proof of concept | Under 1 hour |
| AI-assisted desktop prototype | Same-day work with repo-local agent instructions | 1-2 hours |
| Agent Red-like prototype | Local prototype plus cloud/container tooling | Same day for setup, longer for cloud parity |

## Required downloads and accounts

### Required for any GroundTruth project

| Item | Why you need it | Required |
|------|------------------|----------|
| [Python 3.11+](https://www.python.org/downloads/) | Runs `groundtruth-kb` and the `gt` CLI | Yes |
| [Git](https://git-scm.com/downloads) | Clone, version control, template workflows | Yes |
| [GitHub account](https://github.com/) | Install from GitHub, collaborate, and push changes | Yes |

### Recommended for the AI-assisted desktop path

| Item | Why you need it | Required |
|------|------------------|----------|
| [Visual Studio Code](https://code.visualstudio.com/Download) or another editor | Practical day-to-day editing | Recommended |
| [GitHub CLI](https://cli.github.com/) | Easier auth, repo, and PR workflows | Recommended |
| [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/overview) | Shortest path if you want to use the included `CLAUDE.md` and `.claude/` control surfaces directly | Recommended |
| Anthropic account with access to Claude Code | Needed if you choose the Claude-first workflow | Conditional |

### Recommended for an Agent Red-like prototype

| Item | Why you need it | Required |
|------|------------------|----------|
| [Node.js LTS](https://nodejs.org/en/download) | Useful for frontend/admin UI or TypeScript tooling | Recommended |
| [Docker Desktop](https://docs.docker.com/desktop/) | Local container workflows and parity with service-oriented architectures | Recommended |
| [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) | Azure login and resource operations | Conditional |
| [Terraform CLI](https://developer.hashicorp.com/terraform/install) | Infrastructure-as-code workflows | Optional |
| [Azure subscription](https://azure.microsoft.com/free/) | Required only if you want cloud-hosted resources or Azure parity | Conditional |

## Subscription and access notes

- A GitHub account is required. If the repository is private, the client team
  must have access to the repository before installation.
- If the team wants the fastest path with the included `CLAUDE.md` and
  `.claude/` hooks/rules, they should use Claude Code or a compatible workflow
  and have the necessary Anthropic account access in place.
- If the team chooses another AI coding environment, the GroundTruth method
  still applies, but the `CLAUDE.md` and `.claude/` surfaces may need to be
  adapted to that tool.
- Docker Desktop licensing may require a paid subscription depending on the
  client's organization and usage terms. Confirm licensing before standardizing
  on Docker Desktop for commercial work.
- An Azure subscription is not required for the local-first same-day prototype.
  It becomes required only when the project expands into Azure-hosted services.

## Fastest path: install and bootstrap

### 1. Install GroundTruth from GitHub

```bash
pip install "groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0"
```

Optional extras:

```bash
pip install "groundtruth-kb[web] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0"
pip install "groundtruth-kb[dev] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0"
```

### 2. Bootstrap a desktop-ready project

```bash
gt bootstrap-desktop my-prototype \
  --owner "Acme Labs" \
  --project-type "AI Service Prototype" \
  --init-git
```

This creates:

- `groundtruth.toml`
- `groundtruth.db`
- `CLAUDE.md`
- `MEMORY.md`
- `BRIDGE-INVENTORY.md`
- `.claude/hooks/`
- `.claude/rules/`
- `.github/workflows/` from the reference CI templates

It also seeds the knowledge database with the standard governance specs plus
the example domain records.

### 3. Verify the environment

```bash
cd my-prototype
gt project doctor
gt --config groundtruth.toml summary
```

`gt project doctor` checks installed tools, verifies configuration, and
produces a readiness report highlighting any missing prerequisites.

### 4. Open the project in your editor and complete the first edits

Before the first real session:

- replace remaining `TBD` values in `BRIDGE-INVENTORY.md`
- update `CLAUDE.md` with project-specific rules
- update `MEMORY.md` with real environment notes
- decide whether the project will use a single-agent or dual-agent workflow

## What is automated vs manual

### Automated by `gt bootstrap-desktop`

- GroundTruth project initialization
- knowledge database creation
- template copy for rules, memory, hooks, and bridge inventory
- CI workflow copy
- governance/example seed data
- optional `git init`

### Still manual

- installing third-party tools
- authenticating GitHub, AI tools, and cloud accounts
- choosing the actual agent topology
- writing bridge entrypoints, automations, and runtime code
- provisioning Azure or other cloud infrastructure

## Recommended same-day checklist

Use this sequence for a client workshop or kickoff:

1. Install Python, Git, and GroundTruth.
2. Verify the client has GitHub access to the repo.
3. Run `gt bootstrap-desktop ...`.
4. Open the scaffolded project and review `CLAUDE.md`, `MEMORY.md`, and `BRIDGE-INVENTORY.md`.
5. Create the first spec and linked test.
6. Decide whether to stay local-first or add Docker/Azure on day one.

## When to add the Agent Red-like tooling

Do not force every client to install Azure CLI, Terraform, and Docker on day
one unless they are immediately validating cloud/container workflows. For many
prototype engagements, the better sequence is:

1. local GroundTruth + AI-assisted workflow
2. first useful prototype behavior
3. bridge/runtime inventory capture
4. cloud parity only after the prototype direction is validated
