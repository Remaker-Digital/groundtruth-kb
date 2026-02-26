"""
Knowledge Database — Read-only web UI.

Strictly read-only: no forms, no POST endpoints for data mutation, no edit buttons.
All writes come from Claude via the Python API during working sessions.
The owner uses this UI to observe, filter, search, and verify.

Usage:
  python tools/knowledge-db/app.py             # start on port 8090
  python tools/knowledge-db/app.py --port 9000  # custom port

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import KnowledgeDB, spec_sort_key, get_depth, get_parent_id

BASE_DIR = Path(__file__).parent
app = FastAPI(title="Agent Red Knowledge DB", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Single DB instance
db = KnowledgeDB()


# ─────────────────────────────────────────────────────────────────────
# Template Helpers
# ─────────────────────────────────────────────────────────────────────

def _status_class(status: str) -> str:
    """Map status to CSS class for color coding."""
    return {
        "verified": "status-verified",
        "implemented": "status-implemented",
        "specified": "status-specified",
        "retired": "status-retired",
    }.get(status, "status-unknown")


def _pass_fail_class(passed: bool | int) -> str:
    return "pass" if passed else "fail"


# Register as Jinja2 globals
templates.env.globals["status_class"] = _status_class
templates.env.globals["pass_fail_class"] = _pass_fail_class
templates.env.globals["get_depth"] = get_depth
templates.env.globals["get_parent_id"] = get_parent_id


# ─────────────────────────────────────────────────────────────────────
# Routes (ALL GET — read-only)
# ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    summary = db.get_summary()
    recent = db.get_history(limit=20)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "summary": summary,
        "recent": recent,
    })


@app.get("/specs", response_class=HTMLResponse)
async def specs_list(
    request: Request,
    status: str = Query(None),
    priority: str = Query(None),
    section: str = Query(None),
    handle: str = Query(None),
    tag: str = Query(None),
    search: str = Query(None),
):
    specs = db.list_specs(
        status=status, priority=priority, section=section,
        handle=handle, tag=tag, search=search,
    )
    # Collect unique filter values for dropdowns
    all_specs = db.list_specs()
    statuses = sorted(set(s["status"] for s in all_specs))
    priorities = sorted(set(s["priority"] for s in all_specs if s["priority"]))
    sections = sorted(set(s["section"] for s in all_specs if s["section"]))
    handles = sorted(set(s["handle"] for s in all_specs if s.get("handle")))

    return templates.TemplateResponse("specs.html", {
        "request": request,
        "specs": specs,
        "statuses": statuses,
        "priorities": priorities,
        "sections": sections,
        "handles": handles,
        "filters": {"status": status, "priority": priority, "section": section,
                     "handle": handle, "tag": tag, "search": search},
    })


@app.get("/specs/{spec_id:path}", response_class=HTMLResponse)
async def spec_detail(request: Request, spec_id: str):
    spec = db.get_spec(spec_id)
    if not spec:
        return HTMLResponse("<h1>Spec not found</h1>", status_code=404)
    history = db.get_spec_history(spec_id)
    children = db.list_direct_children(spec_id)
    assertion_run = db.get_latest_assertion_run(spec_id)
    parent_id = get_parent_id(spec_id)
    parent = db.get_spec(parent_id) if parent_id else None
    return templates.TemplateResponse("spec_detail.html", {
        "request": request,
        "spec": spec,
        "history": history,
        "children": children,
        "assertion_run": assertion_run,
        "parent": parent,
    })


@app.get("/tests", response_class=HTMLResponse)
async def tests_list(request: Request, type: str = Query(None)):
    procedures = db.list_test_procedures(type=type)
    all_procs = db.list_test_procedures()
    types = sorted(set(p["type"] for p in all_procs if p["type"]))
    return templates.TemplateResponse("tests.html", {
        "request": request,
        "procedures": procedures,
        "types": types,
        "filters": {"type": type},
    })


@app.get("/tests/{proc_id}", response_class=HTMLResponse)
async def test_detail(request: Request, proc_id: str):
    proc = db.get_test_procedure(proc_id)
    if not proc:
        return HTMLResponse("<h1>Test procedure not found</h1>", status_code=404)
    history = db.get_test_procedure_history(proc_id)
    return templates.TemplateResponse("test_detail.html", {
        "request": request,
        "proc": proc,
        "history": history,
    })


@app.get("/ops", response_class=HTMLResponse)
async def ops_list(request: Request, type: str = Query(None)):
    procedures = db.list_op_procedures(type=type)
    all_procs = db.list_op_procedures()
    types = sorted(set(p["type"] for p in all_procs if p["type"]))
    return templates.TemplateResponse("ops.html", {
        "request": request,
        "procedures": procedures,
        "types": types,
        "filters": {"type": type},
    })


@app.get("/ops/{proc_id}", response_class=HTMLResponse)
async def op_detail(request: Request, proc_id: str):
    proc = db.get_op_procedure(proc_id)
    if not proc:
        return HTMLResponse("<h1>Operational procedure not found</h1>", status_code=404)
    history = db.get_op_procedure_history(proc_id)
    return templates.TemplateResponse("op_detail.html", {
        "request": request,
        "proc": proc,
        "history": history,
    })


@app.get("/env", response_class=HTMLResponse)
async def env_list(
    request: Request,
    environment: str = Query(None),
    category: str = Query(None),
):
    configs = db.list_env_config(environment=environment, category=category)
    all_configs = db.list_env_config()
    environments = sorted(set(c["environment"] for c in all_configs))
    categories = sorted(set(c["category"] for c in all_configs))
    return templates.TemplateResponse("env.html", {
        "request": request,
        "configs": configs,
        "environments": environments,
        "categories": categories,
        "filters": {"environment": environment, "category": category},
    })


@app.get("/env/{config_id:path}", response_class=HTMLResponse)
async def env_detail(request: Request, config_id: str):
    config = db.get_env_config(config_id)
    if not config:
        return HTMLResponse("<h1>Environment config not found</h1>", status_code=404)
    history = db.get_env_config_history(config_id)
    return templates.TemplateResponse("env_detail.html", {
        "request": request,
        "config": config,
        "history": history,
    })


@app.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    changed_by: str = Query(None),
    table: str = Query(None),
):
    changes = db.get_history(limit=100, changed_by=changed_by, table=table)
    return templates.TemplateResponse("history.html", {
        "request": request,
        "changes": changes,
        "filters": {"changed_by": changed_by, "table": table},
    })


@app.get("/assertions", response_class=HTMLResponse)
async def assertions(request: Request):
    runs = db.get_all_latest_assertion_runs()
    # Enrich with spec title
    for run in runs:
        spec = db.get_spec(run["spec_id"])
        run["spec_title"] = spec["title"] if spec else "Unknown"
    return templates.TemplateResponse("assertions.html", {
        "request": request,
        "runs": runs,
    })


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    # Respect PORT env var (for preview tools), then --port flag, then default 8090
    port = int(os.environ.get("PORT", 0)) or args.port or 8090

    print(f"\n  Knowledge Database UI: http://{args.host}:{port}")
    print(f"  Database: {db.db_path}\n")

    uvicorn.run(app, host=args.host, port=port, log_level="info")
