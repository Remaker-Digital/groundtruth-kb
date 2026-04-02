"""
Knowledge Database — Read-only web UI (migration shim).

Delegates to the extracted groundtruth-kb package with Agent Red branding
loaded from the adjacent groundtruth.toml. All routes, templates, and
static assets are served by groundtruth_kb.web.create_app().

Usage:
  python tools/knowledge-db/app.py             # start on port 8090
  python tools/knowledge-db/app.py --port 9000  # custom port

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.web import create_app

_CONFIG_PATH = Path(__file__).parent / "groundtruth.toml"

config = GTConfig.load(config_path=_CONFIG_PATH)
db = KnowledgeDB(db_path=config.db_path, check_same_thread=False)
app = create_app(config, db)

if __name__ == "__main__":
    import argparse
    import os

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    port = int(os.environ.get("PORT", 0)) or args.port or 8090

    print(f"\n  {config.app_title}: http://{args.host}:{port}")
    print(f"  Database: {config.db_path}\n")

    uvicorn.run(app, host=args.host, port=port, log_level="info")
