# Process Templates

Reference templates for GroundTruth projects. Copy these into your project
and customize for your needs.

These templates are **generic starting points** that become project-owned
after copying — GroundTruth does not manage or overwrite them after initial
setup.  Project-specific customization (bridge runtimes, cloud deployment,
dual-agent configuration) is planned for
[groundtruth-project-kit](../docs/architecture/product-split.md).

See the [Adoption guide](../docs/method/09-adoption.md) for the managed vs
project-owned boundary.

## Contents

| Template | Purpose | Copy to |
|----------|---------|---------|
| `CLAUDE.md` | Project rules and procedures for AI assistants | Project root |
| `MEMORY.md` | Session state and operational memory | Project root |
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

The manual placeholder approach is intentional for groundtruth-kb.
Automated profile-based customization (e.g., `gt project init --profile
dual-agent-webapp`) is a planned [groundtruth-project-kit](../docs/architecture/product-split.md)
capability.
