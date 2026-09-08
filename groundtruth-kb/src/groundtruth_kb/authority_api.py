"""Loopback HTTP transport for the native GT-KB domain service.

Host/filesystem controls protect this single-owner installation. Database
credentials exist only in the server process's libpq configuration. This
listener is not a LAN endpoint; LAN exposure requires a configured TLS and
authentication boundary before it can be enabled.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute

from groundtruth_kb.bridge.native import (
    AbandonRequest,
    BindSession,
    ClaimRequest,
    DeliverRequest,
    FenceRequest,
    NativeBridgeService,
    SessionRequest,
)
from groundtruth_kb.native_authority import (
    AuthorityService,
    Identifier,
    MembershipMove,
    ProjectMutation,
    SpecMutation,
    TestMutation,
    TestPhaseMutation,
    TestPlanMutation,
    WorkItemMutation,
)
from groundtruth_kb.postgres_kernel import PostgresKernelError, canonical_json_bytes, parse_json_bytes

Domain = Literal["specifications", "tests", "projects", "work-items", "test-plans", "test-phases"]


class CanonicalJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: object) -> bytes:
        return canonical_json_bytes(content)


class CanonicalRequest(Request):
    async def json(self):
        return parse_json_bytes(await self.body())


class CanonicalRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def canonical_request(request: Request):
            return await handler(CanonicalRequest(request.scope, request.receive))

        return canonical_request


def _result(value: object) -> Response:
    # Avoid FastAPI's float conversion of arbitrary-precision canonical JSON.
    return CanonicalJSONResponse(value)


def create_authority_app(service: AuthorityService, *, project_root: Path | None = None) -> FastAPI:
    """Build the service without opening a database at import time."""
    app = FastAPI(title="GT-KB authority", version="1", docs_url=None, redoc_url=None)
    app.router.route_class = CanonicalRoute
    bridge = NativeBridgeService(service.kernel, project_root or Path.cwd())

    @app.middleware("http")
    async def local_cli_boundary(request: Request, call_next):
        if request.headers.get("origin") is not None:
            return JSONResponse({"code": "browser_origin_refused", "message": "Use the GT-KB CLI"}, status_code=403)
        if (
            request.method in {"POST", "PUT", "PATCH"}
            and request.headers.get("content-type", "").split(";", 1)[0].strip() != "application/json"
        ):
            return JSONResponse(
                {"code": "json_required", "message": "A JSON domain request is required"}, status_code=415
            )
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(PostgresKernelError)
    async def domain_error(_request: Request, error: PostgresKernelError):
        if error.code == "not_found":
            status = 404
        elif error.code in {"cas_conflict", "retryable_conflict"}:
            status = 409
        elif error.code in {"postgres_unavailable", "postgres_operation_failed"}:
            status = 503
        else:
            status = 422
        return JSONResponse(error.to_json_dict(), status_code=status)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request: Request, error: RequestValidationError):
        # Validation diagnostics identify fields but do not echo submitted bodies.
        return JSONResponse(
            {
                "code": "invalid_request",
                "message": "Request does not match the domain contract",
                "fields": [{"location": list(item["loc"]), "type": item["type"]} for item in error.errors()],
            },
            status_code=422,
        )

    @app.get("/v1/status")
    def status() -> Response:
        return _result(service.kernel.status())

    @app.post("/v1/sessions/bind")
    def bind_session(request: BindSession) -> Response:
        return _result(bridge.bind(request))

    @app.get("/v1/sessions/binding")
    def session_binding(native_context_id: str) -> Response:
        return _result(bridge.session(native_context_id))

    @app.post("/v1/sessions/retire")
    def retire_session(request: SessionRequest) -> Response:
        return _result(bridge.retire_session(request.native_context_id))

    @app.get("/v1/bridge/queue")
    def bridge_queue(role: Literal["pb", "lo"]) -> Response:
        return _result(bridge.queue(role))

    @app.get("/v1/bridge/{document}/show")
    def bridge_show(document: Identifier, include_content: bool = False) -> Response:
        return _result(bridge.show(document, include_content=include_content))

    @app.get("/v1/bridge/{document}/artifacts")
    def bridge_artifacts(document: Identifier) -> Response:
        return _result(bridge.artifacts(document))

    @app.post("/v1/bridge/{document}/claim")
    def bridge_claim(document: Identifier, request: ClaimRequest) -> Response:
        return _result(bridge.claim(document, request))

    @app.post("/v1/bridge/{document}/check")
    def bridge_check(document: Identifier, request: FenceRequest) -> Response:
        return _result(bridge.check(document, request))

    @app.post("/v1/bridge/{document}/release")
    def bridge_release(document: Identifier, request: FenceRequest) -> Response:
        return _result(bridge.release(document, request))

    @app.post("/v1/bridge/{document}/deliver")
    def bridge_deliver(document: Identifier, request: DeliverRequest) -> Response:
        return _result(bridge.deliver(document, request))

    @app.post("/v1/bridge/{document}/abandon")
    def bridge_abandon(document: Identifier, request: AbandonRequest) -> Response:
        return _result(bridge.abandon(document, request))

    @app.get("/v1/{domain}")
    def list_records(
        request: Request,
        domain: Domain,
        after: str | None = None,
        limit: Annotated[int, Query(ge=1, le=1000)] = 200,
        search: str | None = None,
        status: str | None = None,
        kind: str | None = None,
        priority: str | None = None,
        spec_id: str | None = None,
        plan_id: str | None = None,
        resolution_status: str | None = None,
        component: str | None = None,
        test_type: str | None = None,
        parent_project_id: str | None = None,
        application_scope: str | None = None,
    ) -> Response:
        accepted = {
            "after",
            "limit",
            "search",
            "status",
            "kind",
            "priority",
            "spec_id",
            "plan_id",
            "resolution_status",
            "component",
            "test_type",
            "parent_project_id",
            "application_scope",
        }
        if set(request.query_params) - accepted or len(request.query_params.multi_items()) != len(request.query_params):
            raise PostgresKernelError("invalid_query", "Unknown or repeated query fields are not accepted")
        filters = {
            key: value
            for key, value in {
                "status": status,
                "kind": kind,
                "priority": priority,
                "spec_id": spec_id,
                "plan_id": plan_id,
                "resolution_status": resolution_status,
                "component": component,
                "test_type": test_type,
                "parent_project_id": parent_project_id,
                "application_scope": application_scope,
            }.items()
            if value is not None
        }
        return _result(service.list_records(domain, filters=filters, after=after, limit=limit, search=search))

    @app.get("/v1/{domain}/{record_id}")
    def show(domain: Domain, record_id: Identifier) -> Response:
        return _result(service.show(domain, record_id))

    @app.put("/v1/specifications/{record_id}")
    def amend_specification(record_id: Identifier, request: SpecMutation) -> Response:
        return _result(service.amend_specification(record_id, request))

    @app.put("/v1/tests/{record_id}")
    def amend_test(record_id: Identifier, request: TestMutation) -> Response:
        return _result(service.amend_test(record_id, request))

    @app.put("/v1/test-plans/{record_id}")
    def amend_test_plan(record_id: Identifier, request: TestPlanMutation) -> Response:
        return _result(service.amend_test_plan(record_id, request))

    @app.put("/v1/test-phases/{record_id}")
    def amend_test_phase(record_id: Identifier, request: TestPhaseMutation) -> Response:
        return _result(service.amend_test_phase(record_id, request))

    @app.put("/v1/projects/{record_id}")
    def amend_project(record_id: Identifier, request: ProjectMutation) -> Response:
        return _result(service.amend_project(record_id, request))

    @app.put("/v1/work-items/{record_id}")
    def amend_work_item(record_id: Identifier, request: WorkItemMutation) -> Response:
        return _result(service.amend_work_item(record_id, request))

    @app.post("/v1/work-items/{record_id}/move")
    def move(record_id: Identifier, request: MembershipMove) -> Response:
        return _result(service.move_work_item(record_id, request))

    @app.get("/v1/work-items/{record_id}/context")
    def context(record_id: Identifier) -> Response:
        return _result(service.task_context(record_id))

    return app
