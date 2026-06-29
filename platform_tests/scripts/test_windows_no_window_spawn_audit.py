from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AUDIT_PATH = _REPO_ROOT / "scripts" / "windows_no_window_spawn_audit.py"


def _load_audit() -> ModuleType:
    spec = importlib.util.spec_from_file_location("windows_no_window_spawn_audit", _AUDIT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(root: Path, rel_path: str, text: str) -> Path:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_release_runtime_subprocess_without_no_window_is_violation(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(
        tmp_path,
        ".codex/gtkb-hooks/hook.py",
        "import subprocess\nsubprocess.run(['python', '-c', 'pass'])\n",
    )

    findings = audit.scan_file(path, root=tmp_path)

    assert [(finding.call, finding.state) for finding in findings] == [("subprocess.run", "violation")]


def test_direct_creationflags_is_compliant(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(
        tmp_path,
        ".codex/gtkb-hooks/hook.py",
        (
            "import subprocess\n"
            "subprocess.run(['python', '-c', 'pass'], "
            "creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))\n"
        ),
    )

    findings = audit.scan_file(path, root=tmp_path)

    assert findings[0].state == "compliant_no_window"
    assert findings[0].no_window is True


def test_kwargs_creationflags_is_compliant_even_through_cast(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(
        tmp_path,
        "groundtruth-kb/src/groundtruth_kb/bridge/poller.py",
        (
            "import subprocess\n"
            "from typing import Any, cast\n"
            "def launch():\n"
            "    popen_kwargs = {'stdout': subprocess.DEVNULL}\n"
            "    popen_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW\n"
            "    subprocess.Popen(['python', '-c', 'pass'], **cast(Any, popen_kwargs))\n"
        ),
    )

    findings = audit.scan_file(path, root=tmp_path)

    assert findings[0].state == "compliant_no_window"
    assert findings[0].no_window is True


def test_no_window_kwargs_helper_call_is_compliant(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(
        tmp_path,
        ".codex/gtkb-hooks/hook.py",
        (
            "import subprocess\n"
            "def _no_window_subprocess_kwargs():\n"
            "    return {'creationflags': subprocess.CREATE_NO_WINDOW}\n"
            "subprocess.run(['python', '-c', 'pass'], **_no_window_subprocess_kwargs())\n"
        ),
    )

    findings = audit.scan_file(path, root=tmp_path)

    assert findings[0].state == "compliant_no_window"
    assert findings[0].no_window is True


def test_test_paths_are_classified_non_release(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(
        tmp_path,
        "platform_tests/scripts/test_fixture.py",
        "import subprocess\nsubprocess.Popen(['python', '-c', 'pass'])\n",
    )

    findings = audit.scan_file(path, root=tmp_path)

    assert findings[0].state == "non_release_runtime"


def test_os_system_in_release_hook_is_violation(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(tmp_path, ".claude/hooks/hook.py", "import os\nos.system('pwsh -NoProfile -Command echo ok')\n")

    findings = audit.scan_file(path, root=tmp_path)

    assert [(finding.call, finding.state) for finding in findings] == [("os.system", "violation")]


def test_os_system_in_operator_script_is_interactive_allowlist(tmp_path: Path) -> None:
    audit = _load_audit()
    path = _write(tmp_path, "scripts/operator_tool.py", "import os\nos.system('pwsh -NoProfile')\n")

    findings = audit.scan_file(path, root=tmp_path)

    assert findings[0].state == "interactive_allowlist"
