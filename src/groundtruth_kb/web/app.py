"""
GroundTruth KB — Read-only web UI.

Strictly read-only: no forms, no POST endpoints for data mutation, no edit buttons.
All writes come from the AI assistant via the Python API during working sessions.
The project owner uses this UI to observe, filter, search, and verify.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB, get_depth, get_parent_id

_WEB_DIR = Path(__file__).parent
_HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")
_DEFAULT_BRAND_COLOR = "#2563eb"


def _validate_hex_color(value: str) -> str:
    """Return a normalised ``#rrggbb`` string, or the default if *value* is invalid."""
    if _HEX_RE.match(value):
        return value if value.startswith("#") else f"#{value}"
    return _DEFAULT_BRAND_COLOR


def _darken_hex(hex_color: str, factor: float = 0.8) -> str:
    """Darken a hex color by *factor* (0 = black, 1 = unchanged)."""
    safe = _validate_hex_color(hex_color)
    h = safe.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"


def _status_class(status: str) -> str:
    """Map spec status to a CSS class."""
    return {
        "verified": "status-verified",
        "implemented": "status-implemented",
        "specified": "status-specified",
        "retired": "status-retired",
    }.get(status, "status-unknown")


def _pass_fail_class(passed: bool | int) -> str:
    return "pass" if passed else "fail"


def create_app(config: GTConfig, db: KnowledgeDB) -> FastAPI:
    """Build a branded, read-only FastAPI application.

    All branding (title, colors, logo, footer) comes from *config*.
    Database access is via the provided *db* instance.
    """
    app = FastAPI(title=config.app_title, docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=_WEB_DIR / "templates")

    # Template helpers
    templates.env.globals["status_class"] = _status_class
    templates.env.globals["pass_fail_class"] = _pass_fail_class
    templates.env.globals["get_depth"] = get_depth
    templates.env.globals["get_parent_id"] = get_parent_id

    # Branding globals — available in every template
    safe_color = _validate_hex_color(config.brand_color)
    templates.env.globals["app_title"] = config.app_title
    templates.env.globals["brand_mark"] = config.brand_mark or "GT"
    templates.env.globals["brand_color"] = safe_color
    templates.env.globals["brand_color_dark"] = _darken_hex(safe_color)
    templates.env.globals["logo_url"] = config.logo_url
    templates.env.globals["legal_footer"] = config.legal_footer

    # -----------------------------------------------------------------
    # Routes (ALL GET — read-only)
    # -----------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        summary = db.get_summary()
        recent = db.get_history(limit=20)
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "summary": summary,
                "recent": recent,
            },
        )

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
            status=status,
            priority=priority,
            section=section,
            handle=handle,
            tag=tag,
            search=search,
        )
        all_specs = db.list_specs()
        statuses = sorted(set(s["status"] for s in all_specs))
        priorities = sorted(set(s["priority"] for s in all_specs if s["priority"]))
        sections = sorted(set(s["section"] for s in all_specs if s["section"]))
        handles = sorted(set(s["handle"] for s in all_specs if s.get("handle")))

        return templates.TemplateResponse(
            request=request,
            name="specs.html",
            context={
                "specs": specs,
                "statuses": statuses,
                "priorities": priorities,
                "sections": sections,
                "handles": handles,
                "filters": {
                    "status": status,
                    "priority": priority,
                    "section": section,
                    "handle": handle,
                    "tag": tag,
                    "search": search,
                },
            },
        )

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
        return templates.TemplateResponse(
            request=request,
            name="spec_detail.html",
            context={
                "spec": spec,
                "history": history,
                "children": children,
                "assertion_run": assertion_run,
                "parent": parent,
            },
        )

    @app.get("/tests", response_class=HTMLResponse)
    async def tests_list(request: Request, type: str = Query(None)):
        procedures = db.list_test_procedures(type=type)
        all_procs = db.list_test_procedures()
        types = sorted(set(p["type"] for p in all_procs if p["type"]))
        return templates.TemplateResponse(
            request=request,
            name="tests.html",
            context={
                "procedures": procedures,
                "types": types,
                "filters": {"type": type},
            },
        )

    @app.get("/tests/{proc_id}", response_class=HTMLResponse)
    async def test_detail(request: Request, proc_id: str):
        proc = db.get_test_procedure(proc_id)
        if not proc:
            return HTMLResponse("<h1>Test procedure not found</h1>", status_code=404)
        history = db.get_test_procedure_history(proc_id)
        return templates.TemplateResponse(
            request=request,
            name="test_detail.html",
            context={
                "proc": proc,
                "history": history,
            },
        )

    @app.get("/ops", response_class=HTMLResponse)
    async def ops_list(request: Request, type: str = Query(None)):
        procedures = db.list_op_procedures(type=type)
        all_procs = db.list_op_procedures()
        types = sorted(set(p["type"] for p in all_procs if p["type"]))
        return templates.TemplateResponse(
            request=request,
            name="ops.html",
            context={
                "procedures": procedures,
                "types": types,
                "filters": {"type": type},
            },
        )

    @app.get("/ops/{proc_id}", response_class=HTMLResponse)
    async def op_detail(request: Request, proc_id: str):
        proc = db.get_op_procedure(proc_id)
        if not proc:
            return HTMLResponse("<h1>Operational procedure not found</h1>", status_code=404)
        history = db.get_op_procedure_history(proc_id)
        return templates.TemplateResponse(
            request=request,
            name="op_detail.html",
            context={
                "proc": proc,
                "history": history,
            },
        )

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
        return templates.TemplateResponse(
            request=request,
            name="env.html",
            context={
                "configs": configs,
                "environments": environments,
                "categories": categories,
                "filters": {"environment": environment, "category": category},
            },
        )

    @app.get("/env/{config_id:path}", response_class=HTMLResponse)
    async def env_detail(request: Request, config_id: str):
        config_entry = db.get_env_config(config_id)
        if not config_entry:
            return HTMLResponse("<h1>Environment config not found</h1>", status_code=404)
        history = db.get_env_config_history(config_id)
        return templates.TemplateResponse(
            request=request,
            name="env_detail.html",
            context={
                "config": config_entry,
                "history": history,
            },
        )

    @app.get("/history", response_class=HTMLResponse)
    async def history_page(
        request: Request,
        changed_by: str = Query(None),
        table: str = Query(None),
    ):
        changes = db.get_history(limit=100, changed_by=changed_by, table=table)
        # Build dynamic author list from recent history
        all_changes = db.get_history(limit=500)
        authors = sorted(set(c["changed_by"] for c in all_changes if c.get("changed_by")))
        return templates.TemplateResponse(
            request=request,
            name="history.html",
            context={
                "changes": changes,
                "authors": authors,
                "filters": {"changed_by": changed_by, "table": table},
            },
        )

    @app.get("/pipeline", response_class=HTMLResponse)
    async def pipeline_dashboard(request: Request):
        metrics = db.get_lifecycle_metrics()
        summary = db.get_summary()
        return templates.TemplateResponse(
            request=request,
            name="pipeline.html",
            context={"metrics": metrics, "summary": summary},
        )

    @app.get("/assertions", response_class=HTMLResponse)
    async def assertions(request: Request):
        runs = db.get_all_latest_assertion_runs()
        for run in runs:
            spec = db.get_spec(run["spec_id"])
            run["spec_title"] = spec["title"] if spec else "Unknown"
        return templates.TemplateResponse(
            request=request,
            name="assertions.html",
            context={
                "runs": runs,
            },
        )

    return app
