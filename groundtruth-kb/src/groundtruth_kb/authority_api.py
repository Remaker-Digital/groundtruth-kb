"""Loopback HTTP transport for the native GT-KB domain service.

Host/filesystem controls protect this single-owner installation. Database
credentials exist only in the server process's libpq configuration. This
listener is not a LAN endpoint; LAN exposure requires a configured TLS and
authentication boundary before it can be enabled.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import RequestResponseEndpoint

from groundtruth_kb.bridge.native import (
    AbandonRequest,
    BindSession,
    ClaimRequest,
    DeliverRequest,
    EffectCheckRequest,
    FenceRequest,
    NativeBridgeService,
    PublishWorkRequest,
    ScratchTeardownRequest,
)
from groundtruth_kb.native_authority import (
    AuthorityService,
    DependencyMutation,
    FormalLinkIdentifier,
    HarnessMutation,
    Identifier,
    MembershipMove,
    ProjectAuthorizationChange,
    ProjectFormalLinkMutation,
    ProjectMutation,
    ProjectRetirement,
    SpecMutation,
    TermMutation,
    TestMutation,
    TestPhaseMutation,
    TestPlanMutation,
    WorkItemMutation,
    WorkItemRetirement,
)
from groundtruth_kb.postgres_kernel import PostgresKernelError, canonical_json_bytes, parse_json_bytes
from groundtruth_kb.project.native_finalization import (
    CommitCheck,
    CommitConfirmation,
    CommitFailure,
    FinalizationRequest,
    NativeProjectFinalization,
    ProjectCommit,
)

Domain = Literal[
    "specifications",
    "tests",
    "projects",
    "work-items",
    "test-plans",
    "test-phases",
    "project-dependencies",
    "project-formal-links",
    "terms",
    "harnesses",
    "deliberations",
]


class CanonicalJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: object) -> bytes:
        return canonical_json_bytes(content)


class CanonicalRequest(Request):
    async def json(self) -> Any:
        return parse_json_bytes(await self.body())


class CanonicalRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def canonical_request(request: Request) -> Response:
            return await handler(CanonicalRequest(request.scope, request.receive))

        return canonical_request


def _result(value: object) -> Response:
    # Avoid FastAPI's float conversion of arbitrary-precision canonical JSON.
    return CanonicalJSONResponse(value)


def _query_fields(request: Request, allowed: set[str]) -> None:
    if set(request.query_params) - allowed or len(request.query_params.multi_items()) != len(request.query_params):
        raise PostgresKernelError("invalid_query", "Unknown or repeated query fields are not accepted")


def create_authority_app(service: AuthorityService, *, project_root: Path | None = None) -> FastAPI:
    """Build the service without opening a database at import time."""
    app = FastAPI(title="GT-KB authority", version="1", docs_url=None, redoc_url=None)
    app.router.route_class = CanonicalRoute
    bridge = NativeBridgeService(service.kernel, project_root or Path.cwd())
    finalization = NativeProjectFinalization(bridge)

    @app.middleware("http")
    async def local_cli_boundary(request: Request, call_next: RequestResponseEndpoint) -> Response:
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
    async def domain_error(_request: Request, error: PostgresKernelError) -> JSONResponse:
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
    async def invalid_request(_request: Request, error: RequestValidationError) -> JSONResponse:
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

    @app.get("/v1/registry/path-observations")
    def registry_path_observations() -> Response:
        return _result(service.registry_path_observations())

    @app.get("/v1/specifications/snapshot")
    def specification_snapshot(request: Request) -> Response:
        _query_fields(request, set())
        return _result(service.specification_snapshot())

    @app.post("/v1/sessions/bind")
    def bind_session(request: BindSession) -> Response:
        return _result(bridge.bind(request))

    @app.get("/v1/sessions/binding")
    def session_binding(native_context_id: str) -> Response:
        return _result(bridge.session(native_context_id))

    @app.get("/v1/sessions/context")
    def session_context(request: Request, native_context_id: str) -> Response:
        _query_fields(request, {"native_context_id"})
        return _result(bridge.session_context(native_context_id))

    @app.post("/v1/sessions/scratch-teardown")
    def scratch_teardown(request: ScratchTeardownRequest) -> Response:
        return _result(bridge.scratch_teardown(request))

    @app.post("/v1/bridge/check-effects")
    def bridge_check_effects(request: EffectCheckRequest) -> Response:
        return _result(bridge.check_effects(request))

    @app.get("/v1/bridge/queue")
    def bridge_queue(role: Literal["pb", "lo"]) -> Response:
        return _result(bridge.queue(role))

    @app.get("/v1/bridge/state-report")
    def bridge_state_report() -> Response:
        return _result(bridge.state_report())

    @app.get("/v1/bridge/{document}/show")
    def bridge_show(document: Identifier, include_content: bool = False) -> Response:
        return _result(bridge.show(document, include_content=include_content))

    @app.get("/v1/bridge/{document}/artifacts")
    def bridge_artifacts(document: Identifier) -> Response:
        return _result(bridge.artifacts(document))

    @app.get("/v1/bridge/{document}/delivery")
    def bridge_delivery(document: Identifier, version: Annotated[int, Query(ge=1)], native_context_id: str) -> Response:
        return _result(bridge.check_delivery(document, version, native_context_id))

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

    @app.post("/v1/bridge/{document}/worktree")
    def bridge_worktree(document: Identifier, request: FenceRequest) -> Response:
        return _result(bridge.open_worktree(document, request))

    @app.post("/v1/bridge/{document}/publish-work")
    def bridge_publish_work(document: Identifier, request: PublishWorkRequest) -> Response:
        return _result(bridge.publish_work(document, request))

    @app.get("/v1/authority/resolve")
    def resolve_authority(
        request: Request, subject: Annotated[str, Query(min_length=1)], scope: str | None = None
    ) -> Response:
        _query_fields(request, {"subject", "scope"})
        return _result(service.resolve_authority(subject, scope=scope))

    @app.get("/v1/authority/status")
    def authority_status(request: Request, scope: str | None = None) -> Response:
        _query_fields(request, {"scope"})
        return _result(service.authority_status(scope=scope))

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
        repository_ref: str | None = None,
        project_id: str | None = None,
        application_scope: str | None = None,
        dependent_project_id: str | None = None,
        prerequisite_project_id: str | None = None,
        affected_gate: str | None = None,
        lifecycle_status: str | None = None,
        authority_level: str | None = None,
        scope: str | None = None,
        source_type: str | None = None,
        work_item_id: str | None = None,
        artifact_type: str | None = None,
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
            "repository_ref",
            "project_id",
            "application_scope",
            "dependent_project_id",
            "prerequisite_project_id",
            "affected_gate",
            "lifecycle_status",
            "authority_level",
            "scope",
            "source_type",
            "work_item_id",
            "artifact_type",
        }
        _query_fields(request, accepted)
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
                "repository_ref": repository_ref,
                "project_id": project_id,
                "application_scope": application_scope,
                "dependent_project_id": dependent_project_id,
                "prerequisite_project_id": prerequisite_project_id,
                "affected_gate": affected_gate,
                "lifecycle_status": lifecycle_status,
                "authority_level": authority_level,
                "scope": scope,
                "source_type": source_type,
                "work_item_id": work_item_id,
                "artifact_type": artifact_type,
            }.items()
            if value is not None
        }
        return _result(service.list_records(domain, filters=filters, after=after, limit=limit, search=search))

    @app.post("/v1/projects/{project_id}/commit")
    def commit_project(project_id: Identifier, body: ProjectCommit, request: Request) -> Response:
        # The native server binds loopback. Use its actual listening port, not
        # a caller's Host header or a second configured authority endpoint.
        server = request.scope.get("server")
        if not server or not isinstance(server[1], int):
            raise PostgresKernelError("authority_unavailable", "The commit callback endpoint is unavailable")
        return _result(finalization.commit(project_id, body, authority_url=f"http://127.0.0.1:{server[1]}"))

    @app.post("/v1/projects/{project_id}/prepare-commit")
    def prepare_commit(project_id: Identifier, request: FinalizationRequest) -> Response:
        return _result(finalization.prepare(project_id, request))

    @app.post("/v1/projects/{project_id}/check-commit")
    def check_commit(project_id: Identifier, request: CommitCheck) -> Response:
        return _result(finalization.check_commit(project_id, request))

    @app.post("/v1/projects/{project_id}/confirm-commit")
    def confirm_commit(project_id: Identifier, request: CommitConfirmation) -> Response:
        return _result(finalization.confirm(project_id, request))

    @app.post("/v1/projects/{project_id}/commit-failed")
    def commit_failed(project_id: Identifier, request: CommitFailure) -> Response:
        return _result(finalization.failure(project_id, request))

    # Formal-link addresses accept the long historical identities of imported
    # obsolete relationships; they are registered before the generic domain
    # reads so the specific address wins for this domain.
    @app.get("/v1/project-formal-links/{record_id}/history")
    def project_formal_link_history(record_id: FormalLinkIdentifier) -> Response:
        return _result(service.history("project-formal-links", record_id))

    @app.get("/v1/project-formal-links/{record_id}")
    def show_project_formal_link(record_id: FormalLinkIdentifier) -> Response:
        return _result(service.show("project-formal-links", record_id))

    @app.get("/v1/{domain}/{record_id}/history")
    def history(domain: Domain, record_id: Identifier) -> Response:
        return _result(service.history(domain, record_id))

    @app.get("/v1/{domain}/{record_id}")
    def show(domain: Domain, record_id: Identifier) -> Response:
        return _result(service.show(domain, record_id))

    @app.put("/v1/deliberations/{record_id}")
    async def refuse_deliberation_write(record_id: Identifier, request: Request) -> Response:
        # Historical reasoning records are read-only (SPEC-2098 v2). Read the body before refusing so the refusal
        # itself is delivered: a method-mismatch 405 that leaves the request body unread can surface to the client
        # as a connection reset on Windows.
        await request.body()
        raise PostgresKernelError(
            "read_only_domain",
            "Deliberations are historical reasoning records; the native service offers no write route",
            details={"domain": "deliberations", "id": record_id},
        )

    @app.put("/v1/harnesses/{record_id}")
    def amend_harness(record_id: Identifier, request: HarnessMutation) -> Response:
        return _result(service.amend_harness(record_id, request))

    @app.put("/v1/specifications/{record_id}")
    def amend_specification(record_id: Identifier, request: SpecMutation) -> Response:
        return _result(service.amend_specification(record_id, request, project_root=bridge.project_root))

    @app.put("/v1/terms/{record_id}")
    def amend_term(record_id: Identifier, request: TermMutation) -> Response:
        return _result(service.amend_term(record_id, request))

    @app.put("/v1/tests/{record_id}")
    def amend_test(record_id: Identifier, request: TestMutation) -> Response:
        return _result(service.amend_test(record_id, request, project_root=bridge.project_root))

    @app.put("/v1/test-plans/{record_id}")
    def amend_test_plan(record_id: Identifier, request: TestPlanMutation) -> Response:
        return _result(service.amend_test_plan(record_id, request))

    @app.put("/v1/test-phases/{record_id}")
    def amend_test_phase(record_id: Identifier, request: TestPhaseMutation) -> Response:
        return _result(service.amend_test_phase(record_id, request))

    @app.put("/v1/projects/{record_id}")
    def amend_project(record_id: Identifier, request: ProjectMutation) -> Response:
        return _result(service.amend_project(record_id, request, project_root=bridge.project_root))

    @app.put("/v1/projects/{record_id}/authorization")
    def set_project_authorization(record_id: Identifier, request: ProjectAuthorizationChange) -> Response:
        return _result(service.set_project_authorization(record_id, request))

    @app.post("/v1/projects/{record_id}/retire")
    def retire_project(record_id: Identifier, request: ProjectRetirement) -> Response:
        return _result(service.retire_project(record_id, request))

    @app.put("/v1/project-dependencies/{record_id}")
    def amend_dependency(record_id: Identifier, request: DependencyMutation) -> Response:
        return _result(service.amend_dependency(record_id, request))

    @app.put("/v1/project-formal-links/{record_id}")
    def amend_project_formal_link(record_id: FormalLinkIdentifier, request: ProjectFormalLinkMutation) -> Response:
        return _result(service.amend_project_formal_link(record_id, request))

    @app.get("/v1/projects/{record_id}/readiness")
    def project_readiness(record_id: Identifier, gate: Literal["readiness", "closure"] = "readiness") -> Response:
        return _result(service.project_readiness(record_id, gate))

    @app.put("/v1/work-items/{record_id}")
    def amend_work_item(record_id: Identifier, request: WorkItemMutation) -> Response:
        return _result(service.amend_work_item(record_id, request))

    @app.post("/v1/work-items/{record_id}/move")
    def move(record_id: Identifier, request: MembershipMove) -> Response:
        return _result(service.move_work_item(record_id, request))

    @app.post("/v1/work-items/{record_id}/retire")
    def retire_work_item(record_id: Identifier, request: WorkItemRetirement) -> Response:
        return _result(service.retire_work_item(record_id, request))

    @app.get("/v1/work-items/{record_id}/context")
    def context(record_id: Identifier) -> Response:
        return _result(service.task_context(record_id, predecessor_readiness=bridge._dependency_readiness))

    @app.get("/v1/work-items/{record_id}/readiness")
    def work_item_readiness(record_id: Identifier) -> Response:
        return _result(bridge.work_item_readiness(record_id))

    return app
