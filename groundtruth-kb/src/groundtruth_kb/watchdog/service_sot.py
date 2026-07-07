# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Service and SoT availability watchdog with bounded safe restores."""

from __future__ import annotations

import inspect
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.dispatcher_disable_guard import disable_guard_status
from groundtruth_kb.operating_state import COMPONENTS, STATUS_ORDER, collect_operating_state
from groundtruth_kb.project.sot_registry import SoTArtifact, default_registry_path
from groundtruth_kb.project.sot_registry import load_toml as load_sot_toml
from groundtruth_kb.watchdog.resource_limits import execute_resource_bounded_restore
from groundtruth_kb.watchdog.restore_policy import AutoRestoreAction, decide_artifact_restoration

DEFAULT_TASK_NAME = "GTKB-ServiceSoTWatchdog"
DEFAULT_INTERVAL_MINUTES = 5
DEFAULT_STATUS_STALE_SECONDS = 900.0
RUNNER_SCRIPT = "scripts/gtkb_service_sot_watchdog.py"
INSTALL_SCRIPT = "scripts/install_service_sot_watchdog_task.ps1"
STATUS_RELATIVE_PATH = Path(".gtkb-state") / "watchdog" / "service-sot-status.json"
RESTORE_RETRY_RELATIVE_PATH = Path(".gtkb-state") / "watchdog" / "restore-retries.json"


class ServiceSoTWatchdogError(RuntimeError):
    """Raised when a watchdog control operation fails."""


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _worst_status(statuses: list[str]) -> str:
    if not statuses:
        return "UNKNOWN"
    return max(statuses, key=lambda status: STATUS_ORDER.get(status, STATUS_ORDER["FAIL"]))


def default_status_path(project_root: Path) -> Path:
    """Return the default runtime status path for the watchdog output."""
    return project_root.resolve() / STATUS_RELATIVE_PATH


def _load_config(project_root: Path) -> GTConfig:
    config_path = project_root.resolve() / "groundtruth.toml"
    if config_path.is_file():
        return GTConfig.load(config_path=config_path)
    return GTConfig.load(None, project_root=project_root.resolve())


def _component_to_dict(component: Any) -> dict[str, Any]:
    serializer = getattr(component, "to_json_dict", None)
    if callable(serializer):
        return serializer()
    return {
        "name": getattr(component, "name", "(unknown)"),
        "status": getattr(component, "status", "FAIL"),
        "detail": getattr(component, "detail", ""),
        "source": getattr(component, "source", ""),
        "duration_ms": getattr(component, "duration_ms", 0.0),
        "evidence": getattr(component, "evidence", {}),
    }


def probe_gt_status_components(
    project_root: Path,
    *,
    config: GTConfig | None = None,
    components: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Probe the same component inventory surfaced by ``gt status``."""
    root = project_root.resolve()
    selected = components or COMPONENTS
    try:
        state = collect_operating_state(
            root,
            config=config or _load_config(root),
            startup=True,
            components=tuple(selected),
        )
    except Exception as exc:  # noqa: BLE001 - watchdog must report, not crash
        return {
            "status": "FAIL",
            "components": [],
            "findings": [f"gt status component probe failed: {type(exc).__name__}: {exc}"],
        }

    items = [_component_to_dict(component) for component in getattr(state, "components", ())]
    return {
        "status": getattr(state, "overall_status", _worst_status([str(item.get("status")) for item in items])),
        "components": items,
        "findings": [
            f"{item.get('name')}: {item.get('status')} - {item.get('detail')}"
            for item in items
            if item.get("status") in {"WARN", "FAIL"}
        ],
    }


def _tool_check_to_dict(check: Any) -> dict[str, Any]:
    status = str(getattr(check, "status", "fail")).lower()
    mapped = {
        "pass": "PASS",
        "warning": "WARN",
        "fail": "FAIL",
        "info": "UNKNOWN",
    }.get(status, "FAIL")
    return {
        "name": getattr(check, "name", "(unknown)"),
        "status": mapped,
        "detail": getattr(check, "message", ""),
        "found": bool(getattr(check, "found", False)),
        "required": bool(getattr(check, "required", False)),
    }


def _doctor_profile_name(project_root: Path) -> str:
    try:
        with (project_root / "groundtruth.toml").open("rb") as handle:
            import tomllib

            payload = tomllib.load(handle)
        project = payload.get("project", {})
        if isinstance(project, dict) and isinstance(project.get("profile"), str):
            return project["profile"]
    except Exception:
        pass
    return "dual-agent"


def _invoke_health_check(function_name: str, project_root: Path) -> dict[str, Any]:
    from groundtruth_kb.project import doctor

    func = getattr(doctor, function_name, None)
    if not callable(func):
        return {
            "name": function_name,
            "status": "FAIL",
            "detail": f"doctor health check {function_name!r} is not available",
            "found": False,
            "required": False,
        }

    profile_name = _doctor_profile_name(project_root)
    try:
        signature = inspect.signature(func)
        parameters = list(signature.parameters.values())
        params = [param.name for param in parameters]
        if function_name == "_check_bridge_dispatch_liveness":
            # The SoT registry names one dispatch-state health function, while
            # the doctor probes per recipient. Cover both known bridge agents and
            # aggregate the result under the single SoT artifact row.
            checks = [func(project_root, "claude"), func(project_root, "codex")]
            payloads = [_tool_check_to_dict(check) for check in checks]
            return {
                "name": function_name,
                "status": _worst_status([str(item["status"]) for item in payloads]),
                "detail": "; ".join(str(item.get("detail") or item["name"]) for item in payloads),
                "subchecks": payloads,
                "found": all(bool(item.get("found")) for item in payloads),
                "required": any(bool(item.get("required")) for item in payloads),
            }
        if params == ["target"]:
            return _tool_check_to_dict(func(project_root))
        if params == ["target", "profile_name"]:
            return _tool_check_to_dict(func(project_root, profile_name))
        if params and params[0] == "target":
            supported_kinds = {
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }
            required_extra = [
                param.name
                for param in parameters[1:]
                if param.kind in supported_kinds and param.default is inspect.Signature.empty
            ]
            if not required_extra:
                return _tool_check_to_dict(func(project_root))
    except Exception as exc:  # noqa: BLE001 - watchdog must report, not crash
        return {
            "name": function_name,
            "status": "FAIL",
            "detail": f"doctor health check {function_name!r} failed: {type(exc).__name__}: {exc}",
            "found": False,
            "required": False,
        }

    return {
        "name": function_name,
        "status": "FAIL",
        "detail": f"doctor health check {function_name!r} has unsupported signature {inspect.signature(func)}",
        "found": False,
        "required": False,
    }


def _artifact_probe(artifact: SoTArtifact, project_root: Path) -> dict[str, Any]:
    function_name = (artifact.health_check_function or "").strip()
    if not function_name:
        return {
            "artifact_id": artifact.id,
            "storage_path": artifact.storage_path,
            "health_check_function": "",
            "status": "UNKNOWN",
            "detail": "no health_check_function registered",
        }
    probe = _invoke_health_check(function_name, project_root)
    return {
        "artifact_id": artifact.id,
        "storage_path": artifact.storage_path,
        "domain": artifact.domain,
        "lifecycle": artifact.lifecycle,
        "restore_action": artifact.restore_action,
        "health_check_function": function_name,
        **probe,
    }


def _retry_state_path(project_root: Path) -> Path:
    return project_root.resolve() / RESTORE_RETRY_RELATIVE_PATH


def _retry_key(artifact: SoTArtifact) -> str:
    return f"{artifact.id}:{artifact.restore_action}"


def _load_retry_state(project_root: Path) -> dict[str, Any]:
    path = _retry_state_path(project_root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {"schema_version": 1, "attempts": {}}
    if not isinstance(payload, dict):
        return {"schema_version": 1, "attempts": {}}
    attempts = payload.get("attempts")
    if not isinstance(attempts, dict):
        payload["attempts"] = {}
    payload.setdefault("schema_version", 1)
    return payload


def _retry_attempts(retry_state: dict[str, Any], artifact: SoTArtifact) -> int:
    attempts = retry_state.get("attempts")
    record = attempts.get(_retry_key(artifact)) if isinstance(attempts, dict) else None
    if not isinstance(record, dict):
        return 0
    try:
        value = int(record.get("attempts", 0))
    except (TypeError, ValueError):
        return 0
    return max(value, 0)


def _set_retry_attempts(
    retry_state: dict[str, Any],
    artifact: SoTArtifact,
    *,
    attempts: int,
    result: dict[str, Any],
) -> None:
    records = retry_state.setdefault("attempts", {})
    if not isinstance(records, dict):
        records = {}
        retry_state["attempts"] = records
    key = _retry_key(artifact)
    if attempts <= 0:
        records.pop(key, None)
    else:
        records[key] = {
            "artifact_id": artifact.id,
            "restore_action": artifact.restore_action,
            "attempts": attempts,
            "updated_at": _now_iso(),
            "last_result": result,
        }
    retry_state["updated_at"] = _now_iso()


def _write_retry_state(project_root: Path, retry_state: dict[str, Any]) -> None:
    path = _retry_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(retry_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _task_name_for_artifact(artifact: SoTArtifact) -> str | None:
    if artifact.id == "dispatcher-supervisor-task":
        return "GTKB-DispatcherDaemon"
    if artifact.id == "dispatcher-storm-watchdog-task":
        return "GTKB-HarnessStormWatchdog"
    storage_path = str(artifact.storage_path or "")
    prefix = "windows-scheduled-task:"
    if storage_path.startswith(prefix):
        return storage_path.removeprefix(prefix)
    return None


def _active_disable_guard(artifact: SoTArtifact, project_root: Path) -> dict[str, Any] | None:
    task_name = _task_name_for_artifact(artifact)
    if task_name is None:
        return None
    status = disable_guard_status(project_root, task_name=task_name)
    return status if status.get("active") else None


def _restore_callable_for_artifact(artifact: SoTArtifact, project_root: Path):
    if artifact.id == "dispatcher-supervisor-task":
        from groundtruth_kb.dispatcher_supervisor import install_supervisor

        return lambda: install_supervisor(project_root)
    if artifact.id == "dispatcher-storm-watchdog-task":
        from groundtruth_kb.dispatcher_watchdog import install_watchdog

        return lambda: install_watchdog(project_root)
    return None


def _deferred_restore_payload(
    artifact: SoTArtifact,
    *,
    decision: dict[str, Any],
    reason_code: str,
    detail: str,
    disable_guard: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_id": artifact.id,
        "restore_action": artifact.restore_action,
        "status": "deferred",
        "reason_code": reason_code,
        "detail": detail,
        "decision": decision,
    }
    if disable_guard is not None:
        payload["disable_guard"] = disable_guard
    return payload


def _evaluate_restore_for_artifact(
    artifact: SoTArtifact,
    probe: dict[str, Any],
    project_root: Path,
    retry_state: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    retry_attempts = _retry_attempts(retry_state, artifact)
    decision = decide_artifact_restoration(artifact, probe, retry_attempts=retry_attempts)
    decision_payload = decision.to_json_dict()
    probe["restore_decision"] = decision_payload
    if not isinstance(decision, AutoRestoreAction):
        if decision.kind == "escalate":
            return (
                probe,
                [],
                [
                    _deferred_restore_payload(
                        artifact,
                        decision=decision_payload,
                        reason_code=decision.reason_code,
                        detail=decision.detail,
                    )
                ],
            )
        return probe, [], []

    disable_guard = _active_disable_guard(artifact, project_root)
    if disable_guard is not None:
        return (
            probe,
            [],
            [
                _deferred_restore_payload(
                    artifact,
                    decision=decision_payload,
                    reason_code="disable_guard_active",
                    detail="active dispatcher disable guard suppresses automatic restore",
                    disable_guard=disable_guard,
                )
            ],
        )

    restore = _restore_callable_for_artifact(artifact, project_root)
    if restore is None:
        return (
            probe,
            [],
            [
                _deferred_restore_payload(
                    artifact,
                    decision=decision_payload,
                    reason_code="restore_recipe_unavailable",
                    detail=f"no restore recipe is registered for artifact {artifact.id!r}",
                )
            ],
        )

    result = execute_resource_bounded_restore(
        decision,
        restore=restore,
        fresh_probe=lambda: _artifact_probe(artifact, project_root),
        success_probe=lambda: _artifact_probe(artifact, project_root),
    )
    result_payload = {
        "artifact_id": artifact.id,
        "restore_action": artifact.restore_action,
        "decision": decision_payload,
        "result": result.to_json_dict(),
    }
    if result.status == "executed":
        _set_retry_attempts(retry_state, artifact, attempts=0, result=result_payload)
        if isinstance(result.success_probe, dict):
            probe["pre_restore_probe"] = dict(probe)
            probe.update(result.success_probe)
        probe["restore_result"] = result.to_json_dict()
        return probe, [result_payload], []
    if result.status == "failed":
        _set_retry_attempts(retry_state, artifact, attempts=retry_attempts + 1, result=result_payload)
        probe["restore_result"] = result.to_json_dict()
        return probe, [result_payload], []
    return probe, [], [result_payload]


def probe_sot_registry(project_root: Path) -> dict[str, Any]:
    """Probe every SoT registry row with a non-empty health-check function."""
    root = project_root.resolve()
    registry_path = default_registry_path(root)
    try:
        records = load_sot_toml(registry_path)
    except Exception as exc:  # noqa: BLE001 - watchdog must report, not crash
        return {
            "status": "FAIL",
            "registry_path": str(registry_path),
            "artifacts": [],
            "findings": [f"SoT registry load failed: {type(exc).__name__}: {exc}"],
        }

    retry_state = _load_retry_state(root)
    artifacts: list[dict[str, Any]] = []
    restore_actions_executed: list[dict[str, Any]] = []
    restore_actions_deferred: list[dict[str, Any]] = []
    for record in records:
        if record.lifecycle != "active" or not (record.health_check_function or "").strip():
            continue
        probe = _artifact_probe(record, root)
        evaluated, executed, deferred = _evaluate_restore_for_artifact(record, probe, root, retry_state)
        artifacts.append(evaluated)
        restore_actions_executed.extend(executed)
        restore_actions_deferred.extend(deferred)
    _write_retry_state(root, retry_state)
    findings = [
        f"{item['artifact_id']}: {item['status']} - {item.get('detail', '')}"
        for item in artifacts
        if item.get("status") in {"WARN", "FAIL"}
    ]
    return {
        "status": _worst_status([str(item.get("status")) for item in artifacts]),
        "registry_path": str(registry_path),
        "artifacts": artifacts,
        "findings": findings,
        "restore_actions_executed": restore_actions_executed,
        "restore_actions_deferred": restore_actions_deferred,
        "canonical_mutations_executed": [],
        "retry_state_path": str(_retry_state_path(root)),
    }


def build_service_sot_status(
    project_root: Path,
    *,
    components: tuple[str, ...] | None = None,
    config: GTConfig | None = None,
) -> dict[str, Any]:
    """Build a detection-only watchdog status payload without writing it."""
    root = project_root.resolve()
    gt_status = probe_gt_status_components(root, config=config, components=components)
    sot_status = probe_sot_registry(root)
    statuses = [str(gt_status.get("status", "FAIL")), str(sot_status.get("status", "FAIL"))]
    overall = _worst_status(statuses)
    return {
        "schema_version": 1,
        "captured_at": _now_iso(),
        "project_root": str(root),
        "overall_status": overall,
        "summary": {
            "gt_status_component_count": len(gt_status.get("components", [])),
            "sot_artifact_probe_count": len(sot_status.get("artifacts", [])),
            "restore_actions_executed": len(sot_status.get("restore_actions_executed", [])),
            "restore_actions_deferred": len(sot_status.get("restore_actions_deferred", [])),
            "canonical_mutations_executed": 0,
        },
        "gt_status": gt_status,
        "sot_registry": sot_status,
        "findings": list(gt_status.get("findings", [])) + list(sot_status.get("findings", [])),
        "restore_actions_executed": list(sot_status.get("restore_actions_executed", [])),
        "restore_actions_deferred": list(sot_status.get("restore_actions_deferred", [])),
        "canonical_mutations_executed": list(sot_status.get("canonical_mutations_executed", [])),
    }


def write_service_sot_status(payload: dict[str, Any], output_path: Path) -> Path:
    """Write the watchdog payload as deterministic JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def run_service_sot_watchdog(
    project_root: Path,
    *,
    output_path: Path | None = None,
    components: tuple[str, ...] | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Run the detection pass and optionally write the runtime status file."""
    root = project_root.resolve()
    payload = build_service_sot_status(root, components=components)
    target = output_path or default_status_path(root)
    if write:
        write_service_sot_status(payload, target)
        payload["output_path"] = str(target)
    return payload


def _run_powershell(command: str, *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    kwargs: dict[str, Any] = {
        "capture_output": True,
        "text": True,
        "timeout": timeout,
        "check": False,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        **kwargs,
    )


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _powershell_json(command: str) -> Any:
    proc = _run_powershell(command)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise ServiceSoTWatchdogError(detail or f"PowerShell failed (exit {proc.returncode})")
    raw = (proc.stdout or "").strip()
    if not raw:
        return None
    return json.loads(raw)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _script_path(project_root: Path, script_name: str) -> Path:
    script = Path(script_name.replace("/", os.sep))
    if script.is_absolute():
        return script
    return project_root.resolve() / script


def _read_last_status(project_root: Path, *, stale_seconds: float = DEFAULT_STATUS_STALE_SECONDS) -> dict[str, Any]:
    path = default_status_path(project_root)
    payload: dict[str, Any] = {
        "path": str(path),
        "present": False,
        "parseable": False,
        "fresh": False,
        "age_seconds": None,
        "overall_status": None,
        "finding": "watchdog status output is absent",
    }
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return payload
    except (OSError, json.JSONDecodeError) as exc:
        payload.update({"present": True, "finding": f"watchdog status output is unreadable: {exc}"})
        return payload
    if not isinstance(doc, dict):
        payload.update({"present": True, "finding": "watchdog status output is not a JSON object"})
        return payload
    payload["present"] = True
    payload["parseable"] = True
    payload["overall_status"] = doc.get("overall_status")
    captured_at = str(doc.get("captured_at") or "")
    try:
        captured = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    except ValueError:
        payload["finding"] = "watchdog status output has an unparsable captured_at"
        return payload
    if captured.tzinfo is None:
        captured = captured.replace(tzinfo=UTC)
    age = time.time() - captured.timestamp()
    payload["age_seconds"] = age
    payload["fresh"] = age <= stale_seconds
    if not payload["fresh"]:
        payload["finding"] = f"watchdog status output is stale ({age:.1f}s > {stale_seconds:.1f}s)"
    elif payload["overall_status"] == "FAIL":
        payload["finding"] = "last watchdog run reports FAIL"
    else:
        payload["finding"] = None
    return payload


def collect_task_status(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
) -> dict[str, Any]:
    """Return machine-readable scheduled-task and last-output health."""
    root = project_root.resolve()
    status_output = _read_last_status(root)
    payload: dict[str, Any] = {
        "platform": os.name,
        "task_name": task_name,
        "project_root": str(root),
        "supported": os.name == "nt",
        "registered": False,
        "state": None,
        "enabled": False,
        "hidden": None,
        "execute": None,
        "arguments": None,
        "uses_pythonw": False,
        "uses_runner_script": False,
        "runner_script_present": False,
        "triggers": [],
        "has_startup_trigger": False,
        "has_repetition_trigger": False,
        "status_output": status_output,
        "healthy": False,
        "findings": [],
    }
    runner_path = root / RUNNER_SCRIPT.replace("/", os.sep)
    payload["runner_script_present"] = runner_path.is_file()
    if not payload["runner_script_present"]:
        payload["findings"].append(f"missing service/SoT watchdog runner: {runner_path.as_posix()}")
    if os.name != "nt":
        payload["findings"].append("service/SoT watchdog scheduled task is Windows-only")
        return payload

    query = (
        f"$t = Get-ScheduledTask -TaskName {_ps_quote(task_name)} -ErrorAction SilentlyContinue; "
        "if ($null -eq $t) { @{ registered = $false } | ConvertTo-Json -Compress } "
        "else { "
        "$triggers = @($t.Triggers); "
        "$triggerDocs = @($triggers | ForEach-Object { "
        "@{ class = [string]$_.CimClass.CimClassName; "
        "start_boundary = [string]$_.StartBoundary; "
        "repetition_interval = [string]$_.Repetition.Interval; "
        "repetition_duration = [string]$_.Repetition.Duration; "
        "enabled = [bool]$_.Enabled } }); "
        "@{ registered = $true; state = [string]$t.State; "
        "hidden = [bool]$t.Settings.Hidden; "
        "execute = [string]$t.Actions[0].Execute; "
        "arguments = [string]$t.Actions[0].Arguments; "
        "triggers = $triggerDocs; "
        "has_startup_trigger = [bool]($triggers | Where-Object { "
        "$_.CimClass.CimClassName -eq 'MSFT_TaskBootTrigger' }); "
        "has_repetition_trigger = [bool]($triggers | Where-Object { $_.Repetition -and $_.Repetition.Interval }) } "
        "| ConvertTo-Json -Compress }"
    )
    try:
        doc = _powershell_json(query)
    except (ServiceSoTWatchdogError, json.JSONDecodeError) as exc:
        payload["findings"].append(f"scheduled-task probe failed: {exc}")
        return payload

    if not isinstance(doc, dict) or not doc.get("registered"):
        payload["findings"].append(f"scheduled task {task_name!r} is not registered")
        return payload

    payload["registered"] = True
    payload["state"] = doc.get("state")
    payload["hidden"] = doc.get("hidden")
    payload["execute"] = doc.get("execute")
    payload["arguments"] = doc.get("arguments")
    payload["triggers"] = [item for item in _as_list(doc.get("triggers")) if isinstance(item, dict)]
    payload["has_startup_trigger"] = bool(doc.get("has_startup_trigger"))
    payload["has_repetition_trigger"] = bool(doc.get("has_repetition_trigger"))
    state = str(payload["state"] or "").strip()
    payload["enabled"] = state.lower() in {"ready", "running"}
    execute = str(payload["execute"] or "").strip().strip('"')
    arguments = str(payload["arguments"] or "")
    payload["uses_pythonw"] = execute.lower().endswith("pythonw.exe")
    payload["uses_runner_script"] = RUNNER_SCRIPT.replace("/", "\\") in arguments or RUNNER_SCRIPT in arguments

    if not payload["enabled"]:
        payload["findings"].append(f"scheduled task state is {state!r}; expected Ready or Running")
    if not payload["uses_pythonw"]:
        payload["findings"].append("scheduled task does not launch via pythonw.exe")
    if not payload["uses_runner_script"]:
        payload["findings"].append(f"scheduled task does not invoke {RUNNER_SCRIPT}")
    if payload["hidden"] is False:
        payload["findings"].append("scheduled task is not hidden")
    if not payload["has_startup_trigger"]:
        payload["findings"].append("scheduled task lacks startup trigger coverage")
    if not payload["has_repetition_trigger"]:
        payload["findings"].append("scheduled task lacks repeating interval trigger coverage")
    if not status_output.get("fresh"):
        payload["findings"].append(str(status_output.get("finding") or "watchdog status output is not fresh"))
    elif status_output.get("overall_status") == "FAIL":
        payload["findings"].append(str(status_output.get("finding") or "last watchdog run reports FAIL"))

    payload["healthy"] = (
        payload["registered"]
        and payload["enabled"]
        and payload["hidden"] is True
        and payload["uses_pythonw"]
        and payload["uses_runner_script"]
        and payload["runner_script_present"]
        and payload["has_startup_trigger"]
        and payload["has_repetition_trigger"]
        and bool(status_output.get("fresh"))
        and status_output.get("overall_status") != "FAIL"
    )
    return payload


def _run_installer_script(
    project_root: Path,
    script_name: str,
    *,
    task_name: str,
    dry_run: bool,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    if os.name != "nt":
        raise ServiceSoTWatchdogError("service/SoT watchdog install is Windows-only")
    script = _script_path(project_root, script_name)
    if not script.is_file():
        raise ServiceSoTWatchdogError(f"missing script: {script.as_posix()}")
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-ProjectRoot",
        str(project_root.resolve()),
        "-TaskName",
        task_name,
    ]
    if dry_run:
        cmd.append("-DryRun")
    if extra_args:
        cmd.extend(extra_args)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise ServiceSoTWatchdogError(detail or f"{script_name} failed (exit {proc.returncode})")
    return {
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "dry_run": dry_run,
        "task_name": task_name,
    }


def install_task(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
    interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
    dry_run: bool = False,
) -> dict[str, Any]:
    result = _run_installer_script(
        project_root,
        INSTALL_SCRIPT,
        task_name=task_name,
        dry_run=dry_run,
        extra_args=["-IntervalMinutes", str(interval_minutes)],
    )
    if not dry_run:
        enable_task(task_name=task_name)
    result["action"] = "install"
    result["status"] = collect_task_status(project_root, task_name=task_name)
    return result


def enable_task(*, task_name: str = DEFAULT_TASK_NAME) -> dict[str, Any]:
    if os.name != "nt":
        raise ServiceSoTWatchdogError("service/SoT watchdog enable is Windows-only")
    proc = _run_powershell(f"Enable-ScheduledTask -TaskName {_ps_quote(task_name)} | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise ServiceSoTWatchdogError(detail or f"Enable-ScheduledTask failed (exit {proc.returncode})")
    return {"action": "enable", "task_name": task_name, "stdout": (proc.stdout or "").strip()}


def disable_task(*, task_name: str = DEFAULT_TASK_NAME) -> dict[str, Any]:
    if os.name != "nt":
        raise ServiceSoTWatchdogError("service/SoT watchdog disable is Windows-only")
    proc = _run_powershell(f"Disable-ScheduledTask -TaskName {_ps_quote(task_name)} | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise ServiceSoTWatchdogError(detail or f"Disable-ScheduledTask failed (exit {proc.returncode})")
    return {"action": "disable", "task_name": task_name, "stdout": (proc.stdout or "").strip()}


def uninstall_task(*, task_name: str = DEFAULT_TASK_NAME, dry_run: bool = False) -> dict[str, Any]:
    if os.name != "nt":
        raise ServiceSoTWatchdogError("service/SoT watchdog uninstall is Windows-only")
    if dry_run:
        return {
            "action": "uninstall",
            "task_name": task_name,
            "dry_run": True,
            "stdout": f"WOULD UNREGISTER TaskName={task_name}",
        }
    proc = _run_powershell(f"Unregister-ScheduledTask -TaskName {_ps_quote(task_name)} -Confirm:$false | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise ServiceSoTWatchdogError(detail or f"Unregister-ScheduledTask failed (exit {proc.returncode})")
    return {
        "action": "uninstall",
        "task_name": task_name,
        "dry_run": False,
        "stdout": (proc.stdout or "").strip(),
    }
