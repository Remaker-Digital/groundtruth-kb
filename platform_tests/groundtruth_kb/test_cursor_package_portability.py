"""Package-only Cursor checks with disposable HTTP records and subprocess agents."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import groundtruth_kb
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(groundtruth_kb.__file__).resolve().parent.parent


def _child(code, args, cwd):
    env = os.environ.copy()
    for key in list(env):
        if key in {"PYTHONPATH", "PYTEST_ADDOPTS", "CURSOR_API_KEY", "CURSOR_AGENT_BIN"} or key.startswith(
            ("GT_", "GTKB_", "PG", "GIT_")
        ):
            env.pop(key, None)
    env.update(PYTHONPATH=str(PACKAGE_ROOT), PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, "-P", "-c", code, *map(str, args)],
        cwd=cwd,
        env=env,
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def _installation(tmp_path):
    selected = tmp_path / "selected installation"
    selected.mkdir()
    scripts = selected / "scripts"
    scripts.mkdir()
    for name in ("cursor_harness.py", "verify_cursor_dispatch.py"):
        shutil.copyfile(REPO_ROOT / "scripts" / name, scripts / name)
    for name in ("bridge", "proposal-review", "verify"):
        path = selected / ".cursor" / "skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("Selected own instruction " + name, encoding="utf-8")
    (selected / ".env.local").write_text("CURSOR_API_KEY=synthetic-selected-value\n", encoding="utf-8")
    other = tmp_path / "other working directory"
    other.mkdir()
    (other / ".env.local").write_text("CURSOR_API_KEY=synthetic-wrong-value\n", encoding="utf-8")
    return selected, other


@pytest.mark.parametrize("module", ["groundtruth_kb.cursor_harness", "groundtruth_kb.cursor_readiness"])
def test_package_imports_without_repository_scripts_or_environment_mutation(module, tmp_path):
    result = _child(
        """
import importlib,json,os,sys
before=dict(os.environ);paths=list(sys.path)
module=importlib.import_module(sys.argv[1])
print(json.dumps({'file':module.__file__,'unchanged':dict(os.environ)==before and sys.path==paths,
                  'scripts_loaded':any(k=='scripts' or k.startswith('scripts.') for k in sys.modules)}))
""",
        [module],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["unchanged"] and not report["scripts_loaded"]
    assert Path(report["file"]).resolve().is_relative_to(PACKAGE_ROOT)


@pytest.mark.parametrize("exit_code", [0, 7])
@pytest.mark.parametrize("mode", ["plan", "ask"])
def test_repository_entry_uses_selected_root_with_installed_code(exit_code, mode, tmp_path):
    selected, other = _installation(tmp_path)
    agent = tmp_path / "fixture-agent.py"
    agent.write_text(
        "import json,os,sys\n"
        "args=sys.argv[1:]\n"
        "print(json.dumps({'cwd':os.getcwd(),'workspace':args[args.index('--workspace')+1],"
        "'mode':args[args.index('--mode')+1],'format':args[args.index('--output-format')+1],"
        "'prompt':args[-1],'key':os.environ.get('CURSOR_API_KEY')}))\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    result = _child(
        """
import runpy,sys
from groundtruth_kb import cursor_harness
agent=sys.argv[2]
cursor_harness._resolve_agent_command=lambda:[sys.executable,agent]
script=sys.argv[1];mode=sys.argv[3]
sys.argv=[script,'--prompt','portable owner task','--skill','bridge-review',
          '--mode',mode,'--output-format','json','--timeout','5']
runpy.run_path(script,run_name='__main__')
""",
        [selected / "scripts/cursor_harness.py", agent, mode],
        other,
    )
    assert result.returncode == exit_code, result.stderr
    report = json.loads(result.stdout)
    assert Path(report["cwd"]) == selected
    assert Path(report["workspace"]) == selected
    assert report["mode"] == mode and report["format"] == "json"
    assert report["prompt"].endswith("portable owner task")
    assert "Selected own instruction bridge" in report["prompt"]
    assert "Selected own instruction proposal-review" in report["prompt"]
    assert report["key"] == "synthetic-selected-value"
    assert not (selected / "scripts/_env.py").exists()


@pytest.mark.parametrize("authenticated", [True, False])
def test_doctor_uses_packaged_probe_selected_http_record_and_real_auth_child(authenticated, tmp_path):
    selected, other = _installation(tmp_path)
    requests = []
    record = {
        "id": "E",
        "harness_name": "cursor",
        "harness_type": "cursor",
        "status": "active",
        "invocation_surfaces": {
            "headless": {"argv": ["python", "scripts/cursor_harness.py", "--skill", "bridge-review"]}
        },
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            payload = json.dumps(record).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_args):
            pass

    agent = tmp_path / "auth-agent.py"
    agent.write_text(
        "import json,os,sys\n"
        "assert sys.argv[1:] == ['status','--format','json']\n"
        "assert os.environ['CURSOR_API_KEY']=='synthetic-selected-value'\n"
        f"print(json.dumps({{'isAuthenticated': {authenticated!r}, 'private_response':'synthetic-private-value'}}))\n",
        encoding="utf-8",
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        (selected / "groundtruth.toml").write_text(
            f'[groundtruth]\nauthority_url="http://127.0.0.1:{server.server_port}"\n', encoding="utf-8"
        )
        try:
            result = _child(
                """
import json,sys
from pathlib import Path
from groundtruth_kb import cursor_harness
from groundtruth_kb.project.doctor import _check_cursor_dispatch_readiness
cursor_harness._resolve_agent_command=lambda:[sys.executable,sys.argv[2]]
report=_check_cursor_dispatch_readiness(Path(sys.argv[1]))
print(json.dumps({'status':report.status,'found':report.found,'message':report.message,
                  'scripts_loaded':any(k=='scripts' or k.startswith('scripts.') for k in sys.modules)}))
""",
                [selected, agent],
                other,
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["found"] and not report["scripts_loaded"]
    assert report["status"] == ("pass" if authenticated else "warning")
    assert requests == ["/v1/harnesses/E"]
    assert "synthetic-private-value" not in result.stdout
    if authenticated:
        assert "harness qualification is unverified" in report["message"]
    else:
        assert "authentication" in report["message"]


def test_verifier_entry_refuses_missing_selected_config_without_using_cwd(tmp_path):
    selected, other = _installation(tmp_path)
    (other / "groundtruth.toml").write_text('[groundtruth]\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    result = _child(
        """
import runpy,sys
script=sys.argv[1];sys.argv=[script,'--json']
runpy.run_path(script,run_name='__main__')
""",
        [selected / "scripts/verify_cursor_dispatch.py"],
        other,
    )
    assert result.returncode == 2, result.stderr
    report = json.loads(result.stdout)
    assert report["error"] == "invalid_selected_configuration"
    assert report["probe_passed"] is False
