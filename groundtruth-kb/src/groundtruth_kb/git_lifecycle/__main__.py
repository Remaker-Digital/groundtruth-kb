"""Production CLI for the governed GT-KB Git lifecycle."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from groundtruth_kb.git_lifecycle.commands import CommandBoundary
from groundtruth_kb.git_lifecycle.models import OperationDenied, OperationResult, PromotionEvidence
from groundtruth_kb.git_lifecycle.service import GitLifecycleService


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit one machine-readable JSON result")
    parser.add_argument("--dry-run", action="store_true", help="validate CLI shape and emit the planned operation only")
    commands = parser.add_subparsers(dest="command", required=True)

    restore = commands.add_parser(
        "restore-deleted-path",
        help="restore one unstaged tracked-file deletion from an explicit commit",
    )
    restore.add_argument("--path", action="append", required=True)
    restore.add_argument("--source-ref", action="append", required=True)

    create = commands.add_parser("create", help="create and select a deterministic work-item branch")
    create.add_argument("--work-item-id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--project-branch", required=True)
    create.add_argument("--operation-id")
    _drain_bounds(create)

    attach = commands.add_parser("attach", help="attach the selected work-item branch to immutable scope")
    attach.add_argument("--work-item-id", required=True)
    attach.add_argument("--title", required=True)
    attach.add_argument("--project-branch", required=True)
    attach.add_argument("--scope", action="append", required=True)
    attach.add_argument("--required-check", action="append", required=True)

    show = commands.add_parser("show", help="show one immutable work-item binding")
    show.add_argument("--work-item-id", required=True)

    validate = commands.add_parser("validate", help="validate branch existence, ancestry, and binding hash")
    validate.add_argument("--work-item-id", required=True)

    preserve = commands.add_parser("preserve", help="commit only the bound work-item scope")
    preserve.add_argument("--work-item-id", required=True)
    preserve.add_argument("--message", required=True)
    preserve.add_argument("--operation-id")
    _drain_bounds(preserve)

    promote = commands.add_parser("promote", help="run work-item, project, or stage promotion")
    promote.add_argument("--level", choices=("work-item", "project", "stage"), required=True)
    promote.add_argument("--work-item-id")
    promote.add_argument("--project-id")
    promote.add_argument("--project-branch")
    promote.add_argument("--release-id")
    promote.add_argument("--evidence-path", required=True, help="service-issued promotion receipt path")
    promote.add_argument("--evidence-sha256", required=True, help="service-issued promotion receipt SHA-256")
    promote.add_argument("--operation-id")
    _drain_bounds(promote)

    close = commands.add_parser("close", help="close a promoted work-item binding")
    close.add_argument("--work-item-id", required=True)
    close.add_argument("--operation-id")

    resume = commands.add_parser("resume", help="resume one hash-bound lifecycle transaction")
    resume.add_argument("--operation-id", required=True)

    recover = commands.add_parser("recover", help="record explicit recovery for an operation or stale drain")
    recover.add_argument("--operation-id")
    recover.add_argument("--reason", required=True)

    drain = commands.add_parser("drain", help="acquire, verify, release, or recover a bounded dispatcher drain")
    drain.add_argument("action", choices=("acquire", "verify", "release", "recover"))
    drain.add_argument("--operation-id")
    drain.add_argument("--reason")
    _drain_bounds(drain)

    maintenance = commands.add_parser(
        "maintenance",
        help="governed git object-store maintenance (plan/run/recover)",
    )
    maintenance.add_argument("action", choices=("plan", "run", "recover"))
    maintenance.add_argument("--operation-id")
    maintenance.add_argument("--reason")
    maintenance.add_argument("--expire", default="now")
    maintenance.add_argument("--prune", default="now")
    maintenance.add_argument("--max-garbage-age-seconds", type=float, default=86400.0)
    return parser


def _drain_bounds(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ttl-seconds", type=float, default=120.0)
    parser.add_argument("--wait-seconds", type=float, default=30.0)


def _require(value: str | None, option: str) -> str:
    if value:
        return value
    raise OperationDenied("cli_argument_missing", f"{option} is required for this promotion level")


def _require_one(values: list[str], option: str) -> str:
    if len(values) == 1:
        return values[0]
    raise OperationDenied(
        "cli_argument_count_invalid",
        f"{option} must be supplied exactly once",
        count=len(values),
        option=option,
    )


def _validate_cli_arguments(args: argparse.Namespace) -> None:
    if args.command == "restore-deleted-path":
        _require_one(args.path, "--path")
        _require_one(args.source_ref, "--source-ref")


def _serializable_arguments(args: argparse.Namespace) -> dict[str, Any]:
    return {
        key: str(value) if isinstance(value, Path) else value
        for key, value in sorted(vars(args).items())
        if key not in {"json", "dry_run"}
    }


def _execute(
    service: GitLifecycleService,
    args: argparse.Namespace,
    command_boundary: CommandBoundary | None = None,
) -> dict[str, Any] | OperationResult:
    if args.command == "restore-deleted-path":
        return service.restore_deleted_path(
            path=_require_one(args.path, "--path"),
            source_ref=_require_one(args.source_ref, "--source-ref"),
        )
    if args.command == "create":
        return service.create_work_item_branch(
            work_item_id=args.work_item_id,
            title=args.title,
            project_branch=args.project_branch,
            operation_id=args.operation_id,
            ttl_seconds=args.ttl_seconds,
            wait_seconds=args.wait_seconds,
        )
    if args.command == "attach":
        return service.attach_work_item(
            work_item_id=args.work_item_id,
            title=args.title,
            project_branch=args.project_branch,
            scope_paths=tuple(args.scope),
            required_checks=tuple(args.required_check),
        )
    if args.command == "show":
        return {"status": "PASS", "operation": "show", "binding": service.show_binding(args.work_item_id)}
    if args.command == "validate":
        return service.validate_binding(args.work_item_id)
    if args.command == "preserve":
        return service.preserve_scoped_changes(
            work_item_id=args.work_item_id,
            message=args.message,
            operation_id=args.operation_id,
            ttl_seconds=args.ttl_seconds,
            wait_seconds=args.wait_seconds,
        )
    if args.command == "promote":
        evidence = PromotionEvidence(bundle_path=args.evidence_path, bundle_sha256=args.evidence_sha256)
        common = {
            "evidence": evidence,
            "operation_id": args.operation_id,
            "ttl_seconds": args.ttl_seconds,
            "wait_seconds": args.wait_seconds,
        }
        if args.level == "work-item":
            return service.promote_work_item(work_item_id=_require(args.work_item_id, "--work-item-id"), **common)
        if args.level == "project":
            return service.promote_project_to_develop(
                project_id=_require(args.project_id, "--project-id"),
                project_branch=_require(args.project_branch, "--project-branch"),
                **common,
            )
        return service.promote_develop_to_stage(
            release_id=_require(args.release_id, "--release-id"),
            **common,
        )
    if args.command == "close":
        return service.close_work_item(work_item_id=args.work_item_id, operation_id=args.operation_id)
    if args.command == "resume":
        return service.resume_operation(args.operation_id)
    if args.command == "recover":
        if args.operation_id:
            return service.recover_operation(operation_id=args.operation_id, reason=args.reason)
        return service.recover_quiescence(reason=args.reason)
    if args.command == "drain":
        if args.action == "recover":
            return service.recover_quiescence(reason=_require(args.reason, "--reason"))
        operation_id = _require(args.operation_id, "--operation-id")
        if args.action == "acquire":
            return service.acquire_quiescence(
                operation_id=operation_id,
                ttl_seconds=args.ttl_seconds,
                wait_seconds=args.wait_seconds,
            )
        if args.action == "verify":
            return service.verify_quiescence(operation_id=operation_id)
        return service.release_quiescence(operation_id=operation_id)
    if args.command == "maintenance":
        from groundtruth_kb.git_lifecycle.maintenance import MaintenanceActuator

        actuator = MaintenanceActuator(
            repo_root=service.repo.root,
            quiescence=service,
            command=command_boundary,
        )
        if args.action == "plan":
            return actuator.plan()
        if args.action == "run":
            return actuator.run(
                operation_id=_require(args.operation_id, "--operation-id"),
                expire_spec=args.expire,
                prune_spec=args.prune,
                max_garbage_age_seconds=args.max_garbage_age_seconds,
            )
        return actuator.recover(
            reason=_require(args.reason, "--reason"),
            operation_id=args.operation_id,
        )
    raise OperationDenied("cli_command_unknown", "unsupported lifecycle command")


def _emit(payload: dict[str, Any], *, as_json: bool, stream: Any | None = None) -> None:
    destination = sys.stdout if stream is None else stream
    if as_json:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True), file=destination)
        return
    status = payload.get("status", "UNKNOWN")
    operation = payload.get("operation", payload.get("code", "git-lifecycle"))
    print(f"{status}: {operation}", file=destination)
    if payload.get("code"):
        print(f"code: {payload['code']}", file=destination)
    if payload.get("commit_sha"):
        print(f"commit: {payload['commit_sha']}", file=destination)
    if payload.get("path"):
        print(f"path: {payload['path']}", file=destination)
    if payload.get("source_commit"):
        print(f"source commit: {payload['source_commit']}", file=destination)
    if payload.get("source_blob"):
        print(f"source blob: {payload['source_blob']}", file=destination)
    if payload.get("restored_blob"):
        print(f"restored blob: {payload['restored_blob']}", file=destination)


def main(
    argv: Sequence[str] | None = None,
    *,
    command_boundary: CommandBoundary | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        _validate_cli_arguments(args)
        service = GitLifecycleService.production(
            Path.cwd(),
            command_boundary=command_boundary,
        )
        if args.dry_run:
            _emit(
                {
                    "status": "DRY-RUN",
                    "operation": args.command,
                    "repository": str(service.repo.root),
                    "arguments": _serializable_arguments(args),
                },
                as_json=args.json,
            )
            return 0
        result = _execute(service, args, command_boundary)
    except OperationDenied as exc:
        _emit(exc.to_dict(), as_json=args.json, stream=sys.stderr)
        return 2
    payload = result.to_dict() if isinstance(result, OperationResult) else result
    _emit(payload, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
