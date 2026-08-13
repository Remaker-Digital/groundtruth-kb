#!/usr/bin/env python3
"""Initialize KnowledgeDB connection for skill scripts.

This is a kb-query skill helper invoked by Claude during KB queries. It
imports the in-repo `tools.knowledge_db.db` module without requiring the
package to be installed.

Per S307 hardcoded-path directive (no machine-local literals in active code):
the project root is discovered from this file's location, not configured.
The script is at .claude/skills/kb-query/scripts/kb_init.py — four levels
deep from the repo root. `Path(__file__).resolve().parents[4]` resolves to
the repo root regardless of which workstation runs it. This makes the skill
portable across workstations and pip-install scenarios.

Long-term this should become `from groundtruth_kb import KnowledgeDB` once
the package install is the supported path.

Usage:
    python .claude/skills/kb-query/scripts/kb_init.py summary
    python .claude/skills/kb-query/scripts/kb_init.py specs specified
    python .claude/skills/kb-query/scripts/kb_init.py wi open
    python .claude/skills/kb-query/scripts/kb_init.py next-ids
"""
import sys
from pathlib import Path

# Discover repo root from this file's location: .claude/skills/kb-query/scripts/kb_init.py
# parents[0]=scripts, [1]=kb-query, [2]=skills, [3]=.claude, [4]=repo root
# Note: the tools dir is `tools/knowledge-db` (with a dash). Python module names
# cannot contain dashes, so we must add the knowledge-db directory itself to
# sys.path and import the bare module name `db`. Adding `_REPO_ROOT` alone
# does not work because `from tools.knowledge_db ...` (underscore) finds
# nothing, and `from tools.knowledge-db ...` (dash) is a syntax error.
_REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "knowledge-db"))

from db import KnowledgeDB  # type: ignore[import-not-found]

db = KnowledgeDB()

if __name__ == "__main__":
    import json
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"

    if cmd == "summary":
        s = db.get_summary()
        for k, v in s.items():
            print(f"  {k}: {v}")
    elif cmd == "specs":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        specs = db.list_specs(status=status) if status else db.list_specs()
        for s in specs:
            print(f"  {s['id']}: {s['title']} [{s['status']}]")
        print(f"\n  Total: {len(specs)}")
    elif cmd == "wi":
        status = sys.argv[2] if len(sys.argv) > 2 else "open"
        wis = db.list_work_items(resolution_status=status) if status != "all" else db.list_work_items()
        for w in wis:
            print(f"  {w['id']}: {w['title']} [{w.get('resolution_status', '?')}]")
        print(f"\n  Total: {len(wis)}")
    elif cmd == "next-ids":
        wis = db.list_work_items()
        tests = db.list_tests()
        specs = db.list_specs()
        next_wi = max((int(w['id'].split('-')[1]) for w in wis if w['id'].split('-')[1].isdigit()), default=0) + 1
        next_test = max((int(t['id'].split('-')[1]) for t in tests if t['id'].split('-')[1].isdigit()), default=0) + 1
        next_spec = max((int(s['id'].split('-')[1]) for s in specs if s['id'].startswith('SPEC-') and s['id'].split('-')[1].isdigit()), default=0) + 1
        print(f"  Next WI:   WI-{next_wi}")
        print(f"  Next TEST: TEST-{next_test}")
        print(f"  Next SPEC: SPEC-{next_spec}")
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: kb_init.py [summary|specs|wi|next-ids]")
