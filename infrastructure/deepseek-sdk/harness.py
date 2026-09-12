"""Run one GT-KB bridge action in the official DeepSeek Harness SDK runtime.

The launcher is the DeepSeek-specific adopter. It verifies the pinned installation,
binds the runtime's own session identifier as the immutable native context through
the GT-KB CLI, injects the neutral baseline instructions and the assigned task, runs
the model turn with the native effect guard loaded, and passes only when the native
service confirms this context's exact delivery. It never authors, rewrites or
publishes a bridge item and reads no other harness's configuration or state.

Exit codes: 0 delivered; 2 startup failed; 3 delivery incomplete; 4 binding failed;
5 interrupted; 6 installation invalid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import threading
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXIT_DELIVERED = 0
EXIT_STARTUP_FAILED = 2
EXIT_DELIVERY_INCOMPLETE = 3
EXIT_BIND_FAILED = 4
EXIT_INTERRUPTED = 5
EXIT_INSTALLATION_INVALID = 6

SOURCE = Path(__file__).resolve().parent
GUARD = SOURCE / "gtkb_guard.mjs"
CliRunner = Callable[[list[str]], dict[str, Any]]


class LauncherError(RuntimeError):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_installation(source: Path = SOURCE) -> dict[str, Any]:
    """Refuse to run unless the installed runtime matches the pinned release identity."""
    try:
        release = json.loads((source / "release.json").read_text(encoding="utf-8"))
        installed = json.loads((source / "installed.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LauncherError(EXIT_INSTALLATION_INVALID, f"Installation record unavailable: {error}") from error
    executable = source / "runtime-env" / release["runtime"]["executable"]
    if not executable.is_file():
        raise LauncherError(EXIT_INSTALLATION_INVALID, "The pinned runtime executable is missing")
    expected = release["runtime"]["executable_sha256"]
    if installed.get("executable_sha256") != expected or _digest(executable) != expected:
        raise LauncherError(EXIT_INSTALLATION_INVALID, "The runtime executable differs from the pinned identity")
    if installed.get("sdk_sha256") != release["sdk"]["sha256"]:
        raise LauncherError(EXIT_INSTALLATION_INVALID, "The installed SDK differs from the pinned identity")
    return {"executable": executable, "profile": release["profile"], "release": release}


def cli_runner(root: Path, config: Path | None, environment: dict[str, str]) -> CliRunner:
    python = root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    if not python.is_file():
        raise LauncherError(EXIT_STARTUP_FAILED, "GT-KB interpreter is unavailable")

    def call(arguments: list[str]) -> dict[str, Any]:
        command = [str(python), "-m", "groundtruth_kb"]
        if config is not None:
            command += ["--config", str(config)]
        command += [*arguments, "--json"]
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=root, env=environment
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"error": result.stderr.strip()[-1500:] or result.stdout.strip()[-1500:]}
        if result.returncode != 0:
            raise LauncherError(EXIT_STARTUP_FAILED, f"gt {' '.join(arguments[:2])} failed: {payload}")
        return payload

    return call


def bind_context(cli: CliRunner, native_context_id: str, init_line: str) -> dict[str, Any]:
    try:
        binding = cli(["session", "bind", "--native-context-id", native_context_id, "--init-keyword", init_line])
    except LauncherError as error:
        raise LauncherError(EXIT_BIND_FAILED, str(error)) from error
    if not binding.get("session_context_id") or not binding.get("role"):
        raise LauncherError(EXIT_BIND_FAILED, "The binding readback lacks a session context or role")
    return binding


def build_prompt(root: Path, binding: dict[str, Any], task: str, document: str, version: int) -> str:
    baseline = (root / ".harness-baseline-configuration" / "AGENTS.md").read_text(encoding="utf-8")
    facts = (
        f"Native context identifier: {binding['native_context_id']}. "
        f"Bound session context: {binding['session_context_id']}. Immutable role: {binding['role']}. "
        f"Assigned bridge document: {document}. The artifact you deliver must be version {version}.\n"
        "Claim it with `gt bridge claim` before authoring, deliver the complete authored item with "
        "`gt bridge deliver --content-file <your file>` using the fence returned by the claim, and read the "
        "result back. The harness verifies delivery through `gt bridge check-delivery`; final prose is not delivery. "
        "Use only this context's registered checkout and scratch directory."
    )
    return "\n\n".join((baseline.strip(), facts, "## Task", task.strip()))


def default_home(root: Path, session_context_id: str, native_context_id: str) -> Path:
    """The runtime home of one context (the SDK's dsh_home, the guard patch and the guard decision log): inside
    that context's own scratch directory, the one runtime location the native effect gate grants a context besides
    its registered checkout and one the commit gates never stage. Never a residue location such as `.gtkb-state`.
    """
    return root / "scratchpad" / session_context_id / "deepseek-sdk" / native_context_id


def write_patch(home: Path) -> Path:
    patch = home / "gtkb-guard.patch.yml"
    patch.write_text(
        f'- insert:\n    - id: gtkb-effect-guard\n      name: "{GUARD.resolve().as_uri()}"\n', encoding="utf-8"
    )
    return patch


def run_session(
    installation: dict[str, Any],
    *,
    root: Path,
    cwd: Path,
    home: Path,
    native_context_id: str,
    prompt: str | None,
    provider: str,
    model: str,
    timeout_seconds: float,
    environment: dict[str, str],
) -> dict[str, Any]:
    """Start the pinned runtime with the guard, run one turn, and always reap the process."""
    from deepseek_harness.api import DeepSeekHarness, DeepSeekHarnessConfig
    from deepseek_harness.errors import HarnessError

    home.mkdir(parents=True, exist_ok=True)
    guard_log = home / "guard-decisions.jsonl"
    env = {
        **environment,
        "GT_PROJECT_ROOT": str(root),
        "GTKB_NATIVE_CONTEXT_ID": native_context_id,
        "GTKB_GUARD_PYTHON": str(root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"),
        "GTKB_GUARD_GATE": str(root / "scripts" / "implementation_start_gate.py"),
        "GTKB_GUARD_CWD": str(cwd),
        "GTKB_GUARD_LOG": str(guard_log),
    }
    config = DeepSeekHarnessConfig(
        provider=provider,
        model=model,
        cwd=str(cwd),
        dsh_bin=str(installation["executable"]),
        profile=installation["profile"],
        patches=(str(write_patch(home)),),
        dsh_home=str(home),
        env=env,
        initialize_timeout_seconds=60,
        request_timeout_seconds=timeout_seconds,
        shutdown_timeout_seconds=10,
    )
    harness = DeepSeekHarness(config)
    interrupted = threading.Event()

    def interrupt() -> None:
        interrupted.set()
        harness.close()

    timer = threading.Timer(timeout_seconds, interrupt)
    try:
        try:
            harness.start()
        except (HarnessError, OSError, TimeoutError, ValueError) as error:
            raise LauncherError(EXIT_STARTUP_FAILED, f"Runtime startup failed: {error}") from error
        if prompt is None:
            return {"finish_reason": None, "events": 0, "guard_log": str(guard_log), "turn": "none"}
        timer.start()
        try:
            result = harness.start_session(native_context_id).run(prompt)
        except (HarnessError, OSError, TimeoutError) as error:
            if interrupted.is_set():
                raise LauncherError(EXIT_INTERRUPTED, "Runtime interrupted before delivery") from error
            raise LauncherError(EXIT_STARTUP_FAILED, f"Runtime turn failed: {error}") from error
        return {
            "finish_reason": result.finish_reason,
            "events": len(result.events),
            "guard_log": str(guard_log),
            "turn": "completed",
        }
    finally:
        timer.cancel()
        harness.close()


def check_delivery(cli: CliRunner, document: str, version: int, native_context_id: str) -> dict[str, Any]:
    try:
        return cli(
            ["bridge", "check-delivery", document, "--version", str(version), "--native-context-id", native_context_id]
        )
    except LauncherError as error:
        raise LauncherError(EXIT_DELIVERY_INCOMPLETE, str(error)) from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=SOURCE.parents[1], help="GT-KB installation root")
    parser.add_argument("--config", type=Path, default=None, help="GT-KB configuration file for the CLI")
    parser.add_argument("--cwd", type=Path, default=None, help="Registered checkout for this context (default: root)")
    parser.add_argument("--native-context-id", default=None, help="Defaults to a fresh deepseek-sdk identifier")
    parser.add_argument("--init", required=True, help="Exact init line supplied with the task, e.g. '::init gtkb lo'")
    parser.add_argument("--document", required=True, help="Assigned bridge document (attempt id)")
    parser.add_argument("--version", type=int, required=True, help="Version the context must deliver")
    parser.add_argument("--task-file", type=Path, required=True, help="UTF-8 task text supplied by the dispatcher")
    parser.add_argument("--provider", default="deepseek-official")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--timeout-seconds", type=float, default=3600.0)
    parser.add_argument(
        "--home",
        type=Path,
        default=None,
        help="Isolated runtime home (default: this context's own scratch directory, "
        "scratchpad/<session context>/deepseek-sdk/<native context id>)",
    )
    parser.add_argument("--report", type=Path, default=None, help="Write a JSON report without message content")
    parser.add_argument("--no-prompt", action="store_true", help="Start, bind and stop without a model turn")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    native_context_id = args.native_context_id or f"deepseek-sdk-{uuid.uuid4().hex}"
    report: dict[str, Any] = {"native_context_id": native_context_id, "started_at": datetime.now(UTC).isoformat()}
    environment = dict(os.environ)
    code = EXIT_STARTUP_FAILED
    try:
        installation = verify_installation()
        cli = cli_runner(root, args.config, environment)
        binding = bind_context(cli, native_context_id, args.init)
        report.update(session_context_id=binding["session_context_id"], role=binding["role"])
        task = args.task_file.read_text(encoding="utf-8")
        prompt = None if args.no_prompt else build_prompt(root, binding, task, args.document, args.version)
        home = args.home or default_home(root, binding["session_context_id"], native_context_id)
        report["session"] = run_session(
            installation,
            root=root,
            cwd=(args.cwd or root).resolve(),
            home=home,
            native_context_id=native_context_id,
            prompt=prompt,
            provider=args.provider,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
            environment=environment,
        )
        if args.no_prompt:
            code = EXIT_DELIVERED
            report["delivery"] = "not requested"
        else:
            report["delivery"] = check_delivery(cli, args.document, args.version, native_context_id)
            code = EXIT_DELIVERED
    except LauncherError as error:
        code = error.code
        report["error"] = str(error)
    except KeyboardInterrupt:
        code = EXIT_INTERRUPTED
        report["error"] = "Interrupted by the operator"
    report.update(exit_code=code, finished_at=datetime.now(UTC).isoformat())
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
