# Process Templates

Reference templates for GroundTruth projects. Copy these into your project
and customize for your needs.

These templates are **generic starting points** that become project-owned
after copying — GroundTruth does not manage or overwrite them after initial
setup.  Use `gt project init my-project --profile <profile>` for automated,
profile-based project setup.

Reference capture templates for bridges and automations are included here.
The `bridge-os-poller-setup-prompt.md` template is now a DEPRECATED
compatibility stub retained for two release cycles after the Slice 4
smart-poller retirement (2026-05-09). Bridge dispatch is automated by the
cross-harness event-driven trigger
(`scripts/cross_harness_bridge_trigger.py`) registered as PostToolUse + Stop
hooks in `.claude/settings.json` and `.codex/hooks.json`; see
`docs/tutorials/dual-agent-setup.md` for setup. Both the smart-poller and
the OS-poller predecessor are retired and archived under
`archive/smart-poller-2026-05-09/`.

See the [Adoption guide](../docs/method/09-adoption.md) for the managed vs
project-owned boundary.

The shipped CLAUDE.md / MEMORY.md / deliberation-protocol templates implement ADR-0001: Three-Tier Memory Architecture (MemBase, MEMORY.md, Deliberation Archive).

## Contents

| Template | Purpose | Copy to |
|----------|---------|---------|
| `CLAUDE.md` | Project rules and procedures for AI assistants | Project root |
| `MEMORY.md` | Session state and operational notepad (per ADR-0001) | Project root |
| `rules/canonical-terminology.md` | Canonical ADR-0001 glossary (MemBase, DA, Prime Builder, Loyal Opposition, etc.) | `.claude/rules/canonical-terminology.md` |
| `rules/canonical-terminology.toml` | Profile-aware doctor config for required canonical terms | `.claude/rules/canonical-terminology.toml` |
| `BRIDGE-INVENTORY.md` | Optional inventory of bridge directives, roles, schedules, prompts, and automations | Project root |
| `bridge-os-poller-setup-prompt.md` | DEPRECATED stub. Smart poller and OS poller both retired in Slice 4 (2026-05-09); retained as compatibility stub for two release cycles. Use the cross-harness event-driven trigger via `gt project init my-project --profile dual-agent`. | Project root or operations docs |
| `hooks/assertion-check.py` | SessionStart hook — run assertions on session start | `.claude/hooks/` |
| `hooks/spec-classifier.py` | UserPromptSubmit hook — detect spec language, enforce spec-first | `.claude/hooks/` |
| `rules/loyal-opposition.md` | Review agent behavior rules | `.claude/rules/` |
| `rules/prime-builder.md` | Build agent behavior rules | `.claude/rules/` |
| `ci/test.yml` | GitHub Actions — pytest + ruff + assertions | `.github/workflows/` |
| `ci/build.yml` | GitHub Actions — Docker build + registry push | `.github/workflows/` |
| `ci/deploy.yml` | GitHub Actions — deploy with environment selection | `.github/workflows/` |

## Usage

Templates are shipped inside the installed `groundtruth-kb` wheel. To find their
location on disk after installation:

```python
from groundtruth_kb import get_templates_dir
print(get_templates_dir())
```

Then copy them into your project:

```bash
# Find the installed templates path
TEMPLATES=$(python -c "from groundtruth_kb import get_templates_dir; print(get_templates_dir())")

# Copy templates to your project
cp "$TEMPLATES/CLAUDE.md" my-project/CLAUDE.md
cp "$TEMPLATES/MEMORY.md" my-project/MEMORY.md
cp "$TEMPLATES/BRIDGE-INVENTORY.md" my-project/BRIDGE-INVENTORY.md
cp "$TEMPLATES/bridge-os-poller-setup-prompt.md" my-project/bridge-os-poller-setup-prompt.md
mkdir -p my-project/.claude/hooks my-project/.claude/rules
cp "$TEMPLATES/hooks/"*.py my-project/.claude/hooks/
cp "$TEMPLATES/rules/"*.md my-project/.claude/rules/

# Then customize placeholders in each file
```

## Customization

Each template contains `{{PLACEHOLDER}}` markers. Replace them with your
project's values:

- `{{PROJECT_NAME}}` — your project name
- `{{PROJECT_TYPE}}` — e.g., "Web Application", "API Service"
- `{{OWNER}}` — project owner or organization
- `{{COPYRIGHT}}` — copyright notice
- `{{VERSION}}` — current version
- `{{ENVIRONMENT_DESCRIPTION}}` — deployment environment summary
- `{{TEST_STATUS}}` — current test pass/fail counts

If your project uses a bridge, multiple agents, or recurring automation, also
customize `BRIDGE-INVENTORY.md` so the runtime entrypoints, directives, role
descriptions, prompts, plugin/skill dependencies, and trigger registrations
are discoverable from the project. For file-based Prime Builder + Loyal
Opposition bridges, run `gt project init my-project --profile dual-agent` (which
scaffolds the cross-harness event-driven trigger,
`.claude/settings.json`, `.codex/hooks.json`, and the dispatch-state path)
and then record the resulting setup in `BRIDGE-INVENTORY.md`.

For automated profile-based customization, use `gt project init my-project --profile
dual-agent-webapp` instead of manual template copying.
