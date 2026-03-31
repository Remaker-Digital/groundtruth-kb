# Process Templates

Reference templates for GroundTruth projects. Copy these into your project
and customize for your needs.

These templates are **project-owned after copying** — GroundTruth does not
manage or overwrite them after initial setup. See the
[Adoption guide](../docs/method/09-adoption.md) for the managed vs
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

## Usage

```bash
# Copy templates to your project
cp templates/CLAUDE.md my-project/CLAUDE.md
cp templates/MEMORY.md my-project/MEMORY.md
mkdir -p my-project/.claude/hooks my-project/.claude/rules
cp templates/hooks/*.py my-project/.claude/hooks/
cp templates/rules/*.md my-project/.claude/rules/

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
