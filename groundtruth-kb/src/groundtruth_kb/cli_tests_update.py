"""CLI adapter for the governed ``gt tests update`` service."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.test_artifact_update import TestArtifactUpdateRequest, update_test_artifact

_NULLABLE_FIELDS = (
    "application_scope",
    "description",
    "last_executed_at",
    "last_result",
    "test_class",
    "test_file",
    "test_function",
)


class TestsUpdateCLIError(click.ClickException):
    """User-facing validation error for ``gt tests update``."""


def _read_inside_root(path: Path, project_root: Path, option_name: str) -> str:
    resolved = path.resolve()
    root = project_root.resolve()
    if not resolved.is_relative_to(root):
        raise TestsUpdateCLIError(f"{option_name} must resolve inside project root {root}")
    try:
        return resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise TestsUpdateCLIError(f"cannot read {option_name}: {exc}") from exc


def _set_update(updates: dict[str, Any], name: str, value: Any) -> None:
    if value is not None:
        updates[name] = value


def register_tests_update_command(tests_group: click.Group, resolve_config: Callable[[click.Context], Any]) -> None:
    """Register the command on the shared ``tests`` Click group."""

    @tests_group.command("update")
    @click.argument("test_id")
    @click.option("--expected-version", required=True, type=click.IntRange(min=1))
    @click.option("--idempotency-key", required=True)
    @click.option("--project", "project_id", required=True)
    @click.option("--work-item", "work_item_id", required=True)
    @click.option("--bridge-id", "bridge_slug", required=True)
    @click.option("--session-context-id", required=True)
    @click.option("--changed-by", required=True)
    @click.option("--change-reason")
    @click.option("--change-reason-file", type=click.Path(path_type=Path, dir_okay=False))
    @click.option("--title")
    @click.option("--spec-id")
    @click.option("--test-type", type=click.Choice(["assertion", "e2e", "integration", "manual", "unit"]))
    @click.option("--test-file")
    @click.option("--test-class")
    @click.option("--test-function")
    @click.option("--description")
    @click.option("--description-file", type=click.Path(path_type=Path, dir_okay=False))
    @click.option("--expected-outcome")
    @click.option("--expected-outcome-file", type=click.Path(path_type=Path, dir_okay=False))
    @click.option("--last-result", type=click.Choice(["blocked", "error", "fail", "pass", "skipped"]))
    @click.option("--last-executed-at")
    @click.option("--execution-evidence-sha256")
    @click.option("--execution-evidence-at")
    @click.option("--application-scope", type=click.Choice(["agent_red_application", "gtkb_platform"]))
    @click.option("--clear", "clear_fields", multiple=True, type=click.Choice(_NULLABLE_FIELDS))
    @click.option("--dry-run", is_flag=True, default=False)
    @click.option("--json", "json_output", is_flag=True, default=False)
    @click.pass_context
    def tests_update_cmd(
        ctx: click.Context,
        test_id: str,
        expected_version: int,
        idempotency_key: str,
        project_id: str,
        work_item_id: str,
        bridge_slug: str,
        session_context_id: str,
        changed_by: str,
        change_reason: str | None,
        change_reason_file: Path | None,
        title: str | None,
        spec_id: str | None,
        test_type: str | None,
        test_file: str | None,
        test_class: str | None,
        test_function: str | None,
        description: str | None,
        description_file: Path | None,
        expected_outcome: str | None,
        expected_outcome_file: Path | None,
        last_result: str | None,
        last_executed_at: str | None,
        execution_evidence_sha256: str | None,
        execution_evidence_at: str | None,
        application_scope: str | None,
        clear_fields: tuple[str, ...],
        dry_run: bool,
        json_output: bool,
    ) -> None:
        """Inspect or append one authority-checked canonical TEST version."""

        config = resolve_config(ctx)
        root = config.project_root.resolve()
        if change_reason is not None and change_reason_file is not None:
            raise TestsUpdateCLIError("use only one of --change-reason or --change-reason-file")
        if description is not None and description_file is not None:
            raise TestsUpdateCLIError("use only one of --description or --description-file")
        if expected_outcome is not None and expected_outcome_file is not None:
            raise TestsUpdateCLIError("use only one of --expected-outcome or --expected-outcome-file")
        if change_reason_file is not None:
            change_reason = _read_inside_root(change_reason_file, root, "--change-reason-file")
        if description_file is not None:
            description = _read_inside_root(description_file, root, "--description-file")
        if expected_outcome_file is not None:
            expected_outcome = _read_inside_root(expected_outcome_file, root, "--expected-outcome-file")
        if not change_reason or not change_reason.strip():
            raise TestsUpdateCLIError("one non-empty --change-reason or --change-reason-file is required")

        supplied = {
            "application_scope": application_scope,
            "description": description,
            "expected_outcome": expected_outcome,
            "last_executed_at": last_executed_at,
            "last_result": last_result,
            "spec_id": spec_id,
            "test_class": test_class,
            "test_file": test_file,
            "test_function": test_function,
            "test_type": test_type,
            "title": title,
        }
        overlap = sorted(set(clear_fields) & {name for name, value in supplied.items() if value is not None})
        if overlap:
            raise TestsUpdateCLIError("cannot both set and clear: " + ", ".join(overlap))
        updates: dict[str, Any] = {}
        for name, value in supplied.items():
            _set_update(updates, name, value)
        for name in clear_fields:
            updates[name] = None
        if not updates:
            raise TestsUpdateCLIError("supply at least one TEST field update or --clear operation")
        if (execution_evidence_sha256 is None) != (execution_evidence_at is None):
            raise TestsUpdateCLIError(
                "--execution-evidence-sha256 and --execution-evidence-at must be supplied together"
            )
        execution_evidence = None
        if execution_evidence_sha256 is not None:
            execution_evidence = {
                "sha256": execution_evidence_sha256,
                "executed_at": execution_evidence_at or "",
            }

        request = TestArtifactUpdateRequest(
            test_id=test_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            project_id=project_id,
            work_item_id=work_item_id,
            bridge_slug=bridge_slug,
            actor_session_context_id=session_context_id,
            changed_by=changed_by,
            change_reason=change_reason,
            updates=updates,
            execution_evidence=execution_evidence,
            dry_run=dry_run,
        )
        db = KnowledgeDB(db_path=config.db_path)
        try:
            result = update_test_artifact(db, request, project_root=root)
        finally:
            db.close()
        payload = result.to_dict()
        if json_output:
            click.echo(json.dumps(payload, indent=2, sort_keys=True, default=str))
        else:
            click.echo(
                f"[{result.status.upper()}] {test_id} expected v{expected_version}"
                + (f" -> v{result.row['version']}" if result.row else "")
            )
            if result.reason_code:
                click.echo(f"  reason: {result.reason_code}")
            if result.recovery:
                click.echo(f"  recovery: {result.recovery}")
            if result.request_digest:
                click.echo(f"  request sha256: {result.request_digest}")
            if result.postimage_digest:
                click.echo(f"  postimage sha256: {result.postimage_digest}")
        if result.status in {"denied", "recovery_required"}:
            raise SystemExit(1)


__all__ = ["TestsUpdateCLIError", "register_tests_update_command"]
