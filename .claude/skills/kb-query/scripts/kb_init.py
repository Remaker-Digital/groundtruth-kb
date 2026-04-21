#!/usr/bin/env python3
"""Initialize KnowledgeDB connection for skill scripts.

Usage:
    python scripts/kb_init.py summary
    python scripts/kb_init.py specs specified
    python scripts/kb_init.py wi open
    python scripts/kb_init.py next-ids
"""
import sys
sys.path.insert(0, "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement")
from tools.knowledge_db.db import KnowledgeDB

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
