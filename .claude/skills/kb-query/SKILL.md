---
name: kb-query
description: Query the Knowledge Database for specs, tests, work items, procedures, and documents. Use when looking up project knowledge, checking spec status, finding open work items, or reviewing test coverage.
argument-hint: [query-type] [filter]
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: knowledge-management
  references:
    - references/api-reference.md
  scripts:
    - scripts/kb_init.py
---

# Knowledge Database Query

Query the Agent Red Knowledge Database (`groundtruth.db`) using the Python API.

**Arguments:** `$ARGUMENTS[0]` = query type, remaining args = filters.

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `/kb-query summary` | Aggregate stats (spec counts, test counts, assertion pass rate) |
| `/kb-query specs implemented` | List all implemented specs |
| `/kb-query specs specified` | List specs still in "specified" status |
| `/kb-query specs search "rate limit"` | Search specs by keyword |
| `/kb-query spec SPEC-1803` | Get a specific spec by ID |
| `/kb-query tests SPEC-1803` | List tests linked to a spec |
| `/kb-query wi open` | List all open work items |
| `/kb-query procedures` | List all operational procedures |
| `/kb-query docs` | List all documents |
| `/kb-query untested` | Find specs with no linked tests |
| `/kb-query history SPEC-1803` | Version history for an artifact |

## Initialization

Use `scripts/kb_init.py` for quick CLI queries, or initialize inline:

```python
import sys
sys.path.insert(0, "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement")
from tools.knowledge_db.db import KnowledgeDB
db = KnowledgeDB()
```

## API Methods

See `references/api-reference.md` for the complete Python API including: summary, specs (list/search/get/history/children), tests, work items, documents, procedures, assertions, test plans, testable elements, and write operations.

## Key Rules

- **GOV-08:** All project knowledge lives in the KB -- not in markdown files.
- **Never** use UPDATE/DELETE SQL directly -- always use `db.*` API methods.
- Claude is the **sole writer**; owner observes via read-only UI at `localhost:8090`.
