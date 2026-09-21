# Desktop Setup for Same-Day Prototype Work

This guide is for a client team that wants to install `groundtruth-kb` from
GitHub and begin building a prototype service on the same day. The target is a
local-first setup that supports:

- specification-first project management with GroundTruth
- AI-assisted implementation on a desktop workstation
- an upgrade path toward a dual-agent, cloud-deployed architecture

## Choose your setup depth

| Setup path | Best for | Time to first useful session |
|------------|----------|------------------------------|
| Core local prototype | Solo or small-team proof of concept | Under 1 hour |
| AI-assisted desktop prototype | Same-day work with repo-local agent instructions | 1-2 hours |
| Cloud/container prototype | Local prototype plus cloud/container tooling | Same day for setup, longer for cloud parity |

## Required downloads and accounts

### Required for any GroundTruth project

| Item | Why you need it | Required |
|------|------------------|----------|
| [Python 3.11+](https://www.python.org/downloads/) | Runs `groundtruth-kb` and the `gt` CLI | Yes |
| [Git](https://git-scm.com/downloads) | Clone, version control, template workflows | Yes |
| [GitHub account](https://github.com/) | Install from GitHub, collaborate, and push changes | Yes |
| [Grafana OSS](https://grafana.com/grafana/download) | Local operations dashboard runtime; `gt dashboard install` can install it on Windows | Recommended |

### Recommended for the AI-assisted desktop path

| Item | Why you need it | Required |
|------|------------------|----------|
| [Visual Studio Code](https://code.visualstudio.com/Download) or another editor | Practical day-to-day editing | Recommended |
| [GitHub CLI](https://cli.github.com/) | Easier auth, repo, and PR workflows | Recommended |
| [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/overview) | Shortest path if you want to use the included `CLAUDE.md` and `.claude/` control surfaces directly | Recommended |
| Anthropic account with access to Claude Code | Needed if you choose the Claude-first workflow | Conditional |

### Recommended for a cloud/container prototype

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
- Select a supported harness profile and use its projector. For Claude Code,
  `.claude/` contains native registration and skill pointers; shared skills live
  in `.agents/skills`, while rules and hook implementations remain under
  `.harness-baseline-configuration`. Supply the account access required by the
  selected host.
- To use another supported coding environment, select its projector profile;
  do not manually adapt a generated `.claude/` tree.
- Docker Desktop licensing may require a paid subscription depending on the
  client's organization and usage terms. Confirm licensing before standardizing
  on Docker Desktop for commercial work.
- An Azure subscription is not required for the local-first same-day prototype.
  It becomes required only when the project expands into Azure-hosted services.

## Fastest path: install and bootstrap

### 1. Install GroundTruth from GitHub

```bash
pip install groundtruth-kb
```

Optional extras:

```bash
pip install "groundtruth-kb[dev]"
```

### 2. Initialize the application under its host

Register the application with the GT-KB host, then create its files with the
single native initializer:

```bash
gt --config <host>/groundtruth.toml application register my-prototype --host-root <host>
gt --config <host>/groundtruth.toml project init my-prototype \
  --project-id PROJECT-my-prototype \
  --host-root <host> \
  --owner "Acme Labs" \
  --profile local-only \
  --harness claude
```

This creates the profile's files inside the registered application root:
`groundtruth.toml` pointing at the host authority, the harness configuration
projected from the host baseline (`.claude/`), the profile-tiered
`.github/workflows/`, and the application's artifact-boundary registry. No
local database is created: specifications, tests and work items live in the
host's PostgreSQL authority, and `--spec-scaffold minimal|full` writes the
inferred starter specifications there. Nothing is committed.

### 3. Verify the environment

```bash
cd my-prototype
gt project doctor
gt --config groundtruth.toml summary
```

`gt project doctor` checks installed tools, verifies configuration, and
produces a readiness report highlighting any missing prerequisites.

### 4. Generate the operations dashboard

```bash
gt dashboard init
gt dashboard install
gt dashboard start
```

Open `http://127.0.0.1:3000/d/groundtruth-kb-dashboard/groundtruth-kb-dashboard`.
If enterprise policy requires a managed Grafana install, install Grafana and
the SQLite datasource plugin through the approved channel and pass
`--grafana-home` to `gt dashboard install` or `gt dashboard start`.

### 5. Open the project in your editor and complete the first edits

Before the first real session:

- replace remaining `TBD` values in `BRIDGE-INVENTORY.md`
- update `CLAUDE.md` with project-specific rules
- update `MEMORY.md` with real environment notes
- decide whether the project will use a single-agent or dual-agent workflow

## What is automated vs manual

### Automated by `gt project init`

- application file initialization for the selected profile
- harness configuration projected from the host baseline (`--harness`)
- CI workflow copy (profile-tiered; `--no-include-ci` to skip)
- inferred starter specifications in the host authority (`--spec-scaffold`)
- the current core-specification intake question, read after creation

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
3. Register the application and run `gt project init ...`.
4. Generate the dashboard with `gt dashboard init`.
5. Open the scaffolded project and review `CLAUDE.md`, `MEMORY.md`, and `BRIDGE-INVENTORY.md`.
6. Create the first spec and linked test.
7. Decide whether to stay local-first or add Docker/Azure on day one.

## When to add cloud/container tooling

Do not force every client to install Azure CLI, Terraform, and Docker on day
one unless they are immediately validating cloud/container workflows. For many
prototype engagements, the better sequence is:

1. local GroundTruth + AI-assisted workflow
2. first useful prototype behavior
3. bridge/runtime inventory capture
4. cloud parity only after the prototype direction is validated
