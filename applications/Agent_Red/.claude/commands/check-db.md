---
description: Quick Knowledge Database health check. Shows spec counts, assertion pass rates, open work items, and regression status.
---

# KB Health Check

Query the Knowledge Database and display a 6-metric dashboard.

## Behavior

Run the following queries against `groundtruth.db`:

Per S307 hardcoded-path directive: discover repo root from git rather than
a workstation-local literal.

```python
import os
import subprocess
import sys
from pathlib import Path

_repo_root = (
    subprocess.run(["git", "rev-parse", "--show-toplevel"],
                   capture_output=True, text=True, check=False).stdout.strip()
    or os.environ.get("GTKB_PROJECT_ROOT", "")
)
sys.path.insert(0, str(Path(_repo_root) / "tools" / "knowledge-db"))
from db import KnowledgeDB

db = KnowledgeDB()

# 1. Spec counts by status
specs = db.list_specs()
by_status = {}
for s in specs:
    st = s.get('status', 'unknown')
    by_status[st] = by_status.get(st, 0) + 1

# 2. Test count
tests = db.list_tests()

# 3. Open work items
wis = [w for w in db.list_work_items() if w.get('status') in ('open', 'in_progress')]

# 4. Assertion stats (from latest assertion check)
# Read from .guard-rails/assertion-baseline.json if available

# 5. Documents count
docs = db.list_documents()

# 6. Procedures count
procs = db.list_op_procedures()
```

## Output Format

```
## KB Health Dashboard

| Metric                | Value    |
|-----------------------|----------|
| Total Specs           | X,XXX    |
| - Implemented         | X,XXX    |
| - Verified            | XXX      |
| - Specified           | XX       |
| Total Tests           | XX,XXX   |
| Open Work Items       | XX       |
| Documents             | XXX      |
| Procedures            | XX       |

### Open Work Items (if any)
[List top 10 by priority]
```
