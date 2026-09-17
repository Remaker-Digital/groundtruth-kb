"""Imports preserve caller configuration; environment loading is explicit."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import groundtruth_kb
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(groundtruth_kb.__file__).resolve().parent.parent
MODULES = [
    "scripts._env",
    "groundtruth_kb",
    "groundtruth_kb.local_env",
    "groundtruth_kb.cursor_harness",
    "groundtruth_kb.cursor_readiness",
    "scripts.verify_claude_dispatch",
    "scripts.verify_cursor_dispatch",
    "scripts.verify_codex_dispatch",
    "scripts.verify_ollama_dispatch",
]


def _environment():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(map(str, (PACKAGE_ROOT, PROJECT_ROOT)))
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _child(code, args, env, cwd):
    result = subprocess.run(
        [sys.executable, "-c", code, *map(str, args)],
        env=env,
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize("configured", [False, True])
def test_fresh_import_preserves_all_environment_values(module, configured, tmp_path):
    env = _environment()
    for key in ("GIT_CONFIG_NOSYSTEM", "XDG_CONFIG_HOME"):
        env.pop(key, None)
    if configured:
        env.update(GIT_CONFIG_NOSYSTEM="0", XDG_CONFIG_HOME=str(tmp_path / "chosen-config"))
    report = _child(
        """
import importlib,json,os,sys
before=dict(os.environ)
module=importlib.import_module(sys.argv[1])
changed=sorted(k for k in set(before)|set(os.environ) if before.get(k)!=os.environ.get(k))
package=sys.modules.get('groundtruth_kb')
print(json.dumps({'changed_names':changed,'module_file':module.__file__,
                  'package_file':package.__file__ if package else None}))
""",
        [module],
        env,
        tmp_path,
    )
    # Report names only on failure; never expose the process environment's values.
    assert report["changed_names"] == []
    expected = PACKAGE_ROOT if module.startswith("groundtruth_kb") else PROJECT_ROOT
    assert Path(report["module_file"]).resolve().is_relative_to(expected)
    if report["package_file"]:
        assert Path(report["package_file"]).resolve().is_relative_to(PACKAGE_ROOT)


@pytest.mark.parametrize("module", ["scripts._env", "groundtruth_kb"])
@pytest.mark.parametrize("scope", ["system", "xdg"])
def test_import_preserves_selected_git_configuration(module, scope, tmp_path):
    git = shutil.which("git")
    assert git, "Git is required for this configuration-selection test"
    env = _environment()
    for key in list(env):
        if key.startswith("GIT_CONFIG_"):
            env.pop(key)
    # These paths belong to this disposable child. No host Git configuration is used.
    git_home = tmp_path / "home"
    git_home.mkdir()
    xdg = tmp_path / "chosen-xdg"
    (xdg / "git").mkdir(parents=True)
    system = tmp_path / "system.gitconfig"
    system.write_text("", encoding="utf-8")
    target = system if scope == "system" else xdg / "git/config"
    target.write_text('[gtkbimportfixture]\n selection = "chosen-fixture"\n', encoding="utf-8")
    env.update(HOME=str(git_home), XDG_CONFIG_HOME=str(xdg), GIT_CONFIG_SYSTEM=str(system))
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    report = _child(
        """
import importlib,json,subprocess,sys
def read():
 r=subprocess.run([sys.argv[2],'config','--get','gtkbimportfixture.selection'],
                  capture_output=True,text=True,timeout=10,
                  creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return {'exit':r.returncode,'value':r.stdout.strip()}
before=read()
importlib.import_module(sys.argv[1])
print(json.dumps({'before':before,'after':read()}))
""",
        [module, git],
        env,
        tmp_path,
    )
    expected = {"exit": 0, "value": "chosen-fixture"}
    assert report["before"] == expected
    assert report["after"] == expected
    assert {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("mode", ["setdefault", "override", "check_only"])
def test_explicit_environment_loading_preserves_its_selected_mode(mode, tmp_path, monkeypatch):
    from scripts._env import load_env_local

    path = tmp_path / "selected.env"
    path.write_text("GTKB_IMPORT_NEW=new-value\nGTKB_IMPORT_EXISTING=file-value\n", encoding="utf-8")
    # Register cleanup even when this key was absent before the loader adds it.
    monkeypatch.setenv("GTKB_IMPORT_NEW", "cleanup-sentinel")
    monkeypatch.delenv("GTKB_IMPORT_NEW")
    monkeypatch.setenv("GTKB_IMPORT_EXISTING", "caller-value")
    before = dict(os.environ)
    values = load_env_local(env_file=path, check_only=mode == "check_only", override=mode == "override")
    assert values == {"GTKB_IMPORT_NEW": "new-value", "GTKB_IMPORT_EXISTING": "file-value"}
    changed = {k for k in set(before) | set(os.environ) if before.get(k) != os.environ.get(k)}
    if mode == "check_only":
        assert changed == set()
    else:
        assert os.environ["GTKB_IMPORT_NEW"] == "new-value"
        assert os.environ["GTKB_IMPORT_EXISTING"] == ("file-value" if mode == "override" else "caller-value")
        assert changed == ({"GTKB_IMPORT_NEW", "GTKB_IMPORT_EXISTING"} if mode == "override" else {"GTKB_IMPORT_NEW"})


@pytest.mark.parametrize("mode", ["setdefault", "override", "check_only"])
def test_packaged_loader_keeps_literal_values_and_selected_mode(mode, tmp_path, monkeypatch):
    from groundtruth_kb.local_env import load_env_local

    selected = tmp_path / "selected"
    selected.mkdir()
    path = selected / ".env.local"
    path.write_text(
        "# comment\n ignored\n =bad\n GTKB_ENV_NEW = first \n"
        'GTKB_ENV_NEW = "literal=quoted" \nGTKB_ENV_EXISTING = file-value\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("GTKB_ENV_NEW", "cleanup")
    monkeypatch.delenv("GTKB_ENV_NEW")
    monkeypatch.setenv("GTKB_ENV_EXISTING", "caller-value")
    before = dict(os.environ)
    values = load_env_local(project_root=selected, check_only=mode == "check_only", override=mode == "override")
    assert values == {"GTKB_ENV_NEW": '"literal=quoted"', "GTKB_ENV_EXISTING": "file-value"}
    changed = {key for key in before.keys() | os.environ.keys() if before.get(key) != os.environ.get(key)}
    if mode == "check_only":
        assert changed == set()
    else:
        assert os.environ["GTKB_ENV_NEW"] == '"literal=quoted"'
        assert os.environ["GTKB_ENV_EXISTING"] == ("file-value" if mode == "override" else "caller-value")
        assert changed == ({"GTKB_ENV_NEW", "GTKB_ENV_EXISTING"} if mode == "override" else {"GTKB_ENV_NEW"})


def test_packaged_loader_refuses_implicit_installation_or_cwd_selection(tmp_path, monkeypatch):
    from groundtruth_kb.local_env import load_env_local

    (tmp_path / ".env.local").write_text("GTKB_ENV_WRONG=wrong-root\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    before = dict(os.environ)
    with pytest.raises(ValueError, match="Select env_file or project_root explicitly"):
        load_env_local()
    assert dict(os.environ) == before


def test_packaged_loader_needs_no_repository_scripts(tmp_path):
    env = _environment()
    env["PYTHONPATH"] = str(PACKAGE_ROOT)
    path = tmp_path / "synthetic.env"
    path.write_text("GTKB_ENV_PORTABLE=synthetic-value\n", encoding="utf-8")
    report = _child(
        """
import json,os,sys
from pathlib import Path
from groundtruth_kb import local_env
before=dict(os.environ)
values=local_env.load_env_local(env_file=Path(sys.argv[1]),check_only=True)
print(json.dumps({'values':values,'file':local_env.__file__,
                  'unchanged':dict(os.environ)==before,
                  'scripts_loaded':any(k=='scripts' or k.startswith('scripts.') for k in sys.modules)}))
""",
        [path],
        env,
        tmp_path,
    )
    assert report["values"] == {"GTKB_ENV_PORTABLE": "synthetic-value"}
    assert report["unchanged"] and not report["scripts_loaded"]
    assert Path(report["file"]).resolve().is_relative_to(PACKAGE_ROOT)


@pytest.mark.parametrize("mode", ["setdefault", "override", "check_only"])
def test_standalone_loader_bootstraps_without_site_packages(mode, tmp_path):
    # Only these two authored stdlib files are present; no package initializer or dependencies.
    source = PROJECT_ROOT / "groundtruth-kb/src/groundtruth_kb/local_env.py"
    for original, relative in [
        (PROJECT_ROOT / "scripts/_env.py", "scripts/_env.py"),
        (source, "groundtruth-kb/src/groundtruth_kb/local_env.py"),
    ]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    (tmp_path / ".env.local").write_text("GTKB_ENV_BOOTSTRAP=file-value\n", encoding="utf-8")
    code = """
import json,os,runpy,sys
before=dict(os.environ); paths=list(sys.path)
loader=runpy.run_path(sys.argv[1])
assert dict(os.environ)==before and sys.path==paths
os.environ['GTKB_ENV_BOOTSTRAP']='caller-value'
values=loader['load_env_local'](override=sys.argv[2]=='override',check_only=sys.argv[2]=='check_only')
print(json.dumps({'values':values,'value':os.environ['GTKB_ENV_BOOTSTRAP'],
                  'package_imported':'groundtruth_kb' in sys.modules,'path_unchanged':sys.path==paths,
                  'loader_source':loader['_parse_env_file'].__code__.co_filename}))
"""
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(tmp_path / "scripts/_env.py"), mode],
        cwd=tmp_path,
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["values"] == {"GTKB_ENV_BOOTSTRAP": "file-value"}
    assert report["value"] == ("file-value" if mode == "override" else "caller-value")
    assert not report["package_imported"] and report["path_unchanged"]
    assert (
        Path(report["loader_source"]).resolve()
        == (tmp_path / "groundtruth-kb/src/groundtruth_kb/local_env.py").resolve()
    )
