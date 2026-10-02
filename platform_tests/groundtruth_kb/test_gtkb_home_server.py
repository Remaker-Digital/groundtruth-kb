"""GT-KB Home server: the pinned DeepSeek Harness Web UI installer, launcher and configuration (owner rulings D58, D59).

The Home is installed from the committed lockfile only (digest pinned in release.json, install scripts off by default),
started from GT-KB's one committed patch (preset route, effect guard, Home plugin, upstream brand off) with a minimal
environment, and proven composed before it starts. Nothing here starts a server or touches the network.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "infrastructure" / "deepseek-web"
PRESET = "@preset/gtkb-openrouter-deepseek-v4-flash"


def _module(name: str):
    spec = importlib.util.spec_from_file_location(f"gtkb_home_{name}", WEB / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _PatchLoader(yaml.SafeLoader):
    """The patch grammar's !!js scalars are JavaScript expressions; keep them as tagged text."""


_PatchLoader.add_constructor("tag:yaml.org,2002:js", lambda loader, node: ("js", loader.construct_scalar(node)))


def _patch() -> list:
    return yaml.load((WEB / "gtkb-home.patch.yml").read_text(encoding="utf-8"), Loader=_PatchLoader)  # noqa: S506


def test_the_patch_is_the_one_gtkb_layer_over_the_pinned_web_bundles():
    rows = _patch()
    by_id = {row["id"]: row for row in rows if "id" in row}
    assert by_id["agent-default-model"]["config"] == {"provider": "gtkb-openrouter", "model": PRESET}
    provider = by_id["llm-pi-ai"]["config"]["providers"]["gtkb-openrouter"]
    assert provider == {
        "displayName": "GTKB OpenRouter",
        "apiKeyEnv": "GTKB_OPENROUTER_API_KEY",
        "api": "openai-completions",
        "baseURL": "https://openrouter.ai/api/v1",
        "models": [{"id": PRESET}],
    }
    assert by_id["ui-brand-official"] == {"id": "ui-brand-official", "disabled": True}
    assert by_id["llm-deepseek"] == {"id": "llm-deepseek", "disabled": True}, "the DeepSeek-specific provider is off"
    inserted = [row for entry in rows if "insert" in entry for row in entry["insert"]]
    assert [row["id"] for row in inserted] == ["gtkb-home-effect-guard", "gtkb-home"]
    assert inserted[0]["name"] == "./gtkb_home_guard.mjs" and (WEB / "gtkb_home_guard.mjs").is_file()
    assert inserted[1]["name"] == "./plugins/gtkb-home/lib/index.js"
    assert (WEB / "plugins" / "gtkb-home" / "lib" / "index.js").is_file()
    assert inserted[1]["config"] == {
        "gtArgv": ("js", "[process.env.GTKB_GUARD_PYTHON, '-m', 'groundtruth_kb']"),
        "gtCwd": ("js", "process.env.GTKB_HOME_ROOT"),
    }
    assert "KEY" not in (WEB / "gtkb-home.patch.yml").read_text(encoding="utf-8").replace("GTKB_OPENROUTER_API_KEY", "")


def test_release_pins_the_lockfile_the_package_and_the_startup_reload_manifest():
    release = json.loads((WEB / "release.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((WEB / "package-lock.json").read_bytes()).hexdigest() == release["lockfile_sha256"]
    package = json.loads((WEB / "package.json").read_text(encoding="utf-8"))
    assert package["dependencies"] == {release["package"]: release["version"]}
    lock = json.loads((WEB / "package-lock.json").read_text(encoding="utf-8"))
    assert lock["packages"][f"node_modules/{release['package']}"]["version"] == release["version"]
    assert release["profile_manifest"] == {
        "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-web-app"],
        "patchReload": "startup",
    }


def _source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "infrastructure" / "deepseek-web"
    source.mkdir(parents=True)
    for name in ("release.json", "package-lock.json", "package.json"):
        (source / name).write_bytes((WEB / name).read_bytes())
    return source


def test_install_refuses_a_changed_lockfile_an_existing_tree_and_an_old_node(tmp_path, monkeypatch):
    install = _module("install")
    source = _source_tree(tmp_path)
    calls = []
    monkeypatch.setattr(install, "run", lambda command, cwd=None: calls.append(command) or "v18.20.0\n")
    with pytest.raises(install.InstallError, match="Node.js 20 or newer"):
        install.install(tmp_path, node="node", npm="npm", cache=None, allow_scripts=False)
    (source / "node_modules").mkdir()
    with pytest.raises(install.InstallError, match="already exists"):
        install.install(tmp_path, node="node", npm="npm", cache=None, allow_scripts=False)
    (source / "package-lock.json").write_bytes((WEB / "package-lock.json").read_bytes() + b"\n")
    with pytest.raises(install.InstallError, match="differs from the pinned lockfile digest"):
        install.install(tmp_path, node="node", npm="npm", cache=None, allow_scripts=False)
    assert all(command[1:] == ["--version"] for command in calls), "npm never ran"


@pytest.mark.parametrize(("allow_scripts", "cache"), [(False, None), (True, "cache")])
def test_install_runs_npm_ci_from_the_lockfile_and_records_what_it_installed(
    tmp_path, monkeypatch, allow_scripts, cache
):
    install = _module("install")
    source = _source_tree(tmp_path)
    release = json.loads((source / "release.json").read_text(encoding="utf-8"))
    commands = []

    def fake_run(command, cwd=None):
        commands.append((command, cwd))
        if command[1:] == ["--version"]:
            return "v24.11.1\n"
        package = source / "node_modules" / "@deepseek-ai" / "dsh"
        package.mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({"version": release["version"]}), encoding="utf-8")
        return ""

    monkeypatch.setattr(install, "run", fake_run)
    cache_path = tmp_path / cache if cache else None
    record = install.install(tmp_path, node="node", npm="npm", cache=cache_path, allow_scripts=allow_scripts)
    npm, cwd = commands[-1]
    assert cwd == source and npm[:4] == ["npm", "ci", "--no-audit", "--no-fund"]
    assert ("--ignore-scripts" in npm) is (not allow_scripts)
    assert (npm[-3:] == ["--offline", "--cache", str(cache_path)]) is bool(cache)
    lock = json.loads((source / "package-lock.json").read_text(encoding="utf-8"))
    assert record["packages"] == len(lock["packages"]) - 1
    assert record["install_scripts"] == ("allowed" if allow_scripts else "skipped")
    assert json.loads((source / "installed.json").read_text(encoding="utf-8")) == record


def test_install_refuses_a_package_other_than_the_pinned_one(tmp_path, monkeypatch):
    install = _module("install")
    source = _source_tree(tmp_path)

    def fake_run(command, cwd=None):
        if command[1:] == ["--version"]:
            return "v24.11.1\n"
        package = source / "node_modules" / "@deepseek-ai" / "dsh"
        package.mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({"version": "9.9.9"}), encoding="utf-8")
        return ""

    monkeypatch.setattr(install, "run", fake_run)
    with pytest.raises(install.InstallError, match="differs from the pinned"):
        install.install(tmp_path, node="node", npm="npm", cache=None, allow_scripts=False)
    assert not (source / "installed.json").exists()


def _fake_tree(root: Path) -> Path:
    for rel, text in {
        "@deepseek-ai/dsh/package.json": '{"version": "0.1.2-rc.1"}',
        "@deepseek-ai/dsh/lib/bin.js": "export {};\n",
        ".bin/dsh.cmd": "@node %~dp0\\..\\@deepseek-ai\\dsh\\lib\\bin.js %*\n",
    }.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def test_the_installed_tree_identity_is_reproducible_and_changes_with_any_byte_name_or_file(tmp_path):
    install = _module("install")
    first = install.tree_identity(_fake_tree(tmp_path / "a"))
    assert first == install.tree_identity(_fake_tree(tmp_path / "b")), "same pinned inputs, same identity"
    assert (first["tree_files"], first["tree_bytes"]) == (
        3,
        sum(p.stat().st_size for p in (tmp_path / "a").rglob("*") if p.is_file()),
    )
    (tmp_path / "b" / "@deepseek-ai/dsh/lib/bin.js").write_text("export {}; \n", encoding="utf-8")
    assert install.tree_identity(tmp_path / "b")["tree_sha256"] != first["tree_sha256"]
    _fake_tree(tmp_path / "c")
    (tmp_path / "c" / ".bin/dsh.cmd").rename(tmp_path / "c" / ".bin/dsh2.cmd")
    assert install.tree_identity(tmp_path / "c")["tree_sha256"] != first["tree_sha256"]
    _fake_tree(tmp_path / "d")
    (tmp_path / "d" / "extra.js").write_text("", encoding="utf-8")
    assert install.tree_identity(tmp_path / "d")["tree_files"] == 4


def test_verify_refuses_a_changed_tree_and_uninstall_removes_tree_and_record(tmp_path, monkeypatch):
    install = _module("install")
    source = _source_tree(tmp_path)
    release = json.loads((source / "release.json").read_text(encoding="utf-8"))

    def fake_run(command, cwd=None):
        if command[1:] == ["--version"]:
            return "v24.11.1\n"
        _fake_tree(source / "node_modules")
        (source / "node_modules/@deepseek-ai/dsh/package.json").write_text(
            json.dumps({"version": release["version"]}), encoding="utf-8"
        )
        return ""

    monkeypatch.setattr(install, "run", fake_run)
    record = install.install(tmp_path, node="node", npm="npm", cache=None, allow_scripts=False)
    assert install.verify(tmp_path)["tree_sha256"] == record["tree_sha256"]
    (source / "node_modules/@deepseek-ai/dsh/lib/bin.js").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(install.InstallError, match="differs from its recorded identity"):
        install.verify(tmp_path)
    assert install.uninstall(tmp_path) == {"removed": True}
    assert not (source / "node_modules").exists() and not (source / "installed.json").exists()
    assert (source / "package-lock.json").is_file(), "the committed pins stay"
    with pytest.raises(install.InstallError, match="not installed"):
        install.verify(tmp_path)
    reinstalled = install.install(tmp_path, node="node", npm="npm", cache=None, allow_scripts=False)
    assert reinstalled["tree_sha256"] == record["tree_sha256"], "a reinstall from the same pins has the same identity"


def test_uninstall_refuses_a_linked_tree_and_leaves_its_target(tmp_path):
    install = _module("install")
    source = _source_tree(tmp_path)
    elsewhere = _fake_tree(tmp_path / "elsewhere")
    link = source / "node_modules"
    if sys.platform == "win32":
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(elsewhere)], capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
    else:
        link.symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(install.InstallError, match="is a link"):
        install.uninstall(tmp_path)
    assert (elsewhere / "@deepseek-ai/dsh/lib/bin.js").is_file()
    if sys.platform == "win32":
        os.rmdir(link)  # removes the junction itself, never its target
    else:
        link.unlink()


def test_the_installer_reports_each_action_as_json(tmp_path, capsys):
    install = _module("install")
    _source_tree(tmp_path)
    assert install.main(["--root", str(tmp_path), "--verify"]) == 1
    assert json.loads(capsys.readouterr().out) == {"verified": False, "error": "the Home server is not installed here"}
    assert install.main(["--root", str(tmp_path), "--uninstall"]) == 0
    assert json.loads(capsys.readouterr().out) == {"uninstalled": True, "removed": False}


def test_home_state_folder_precedence(tmp_path, monkeypatch):
    home = _module("home")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    monkeypatch.delenv("GTKB_HOME_STATE", raising=False)
    assert home.state_folder(None) == tmp_path / "local" / "GT-KB" / "home"
    monkeypatch.setenv("GTKB_HOME_STATE", str(tmp_path / "configured"))
    assert home.state_folder(None) == tmp_path / "configured"
    assert home.state_folder(tmp_path / "explicit") == tmp_path / "explicit"


def test_the_server_environment_is_minimal_and_carries_no_secret(tmp_path, monkeypatch):
    home = _module("home")
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-not-for-the-home")
    monkeypatch.setenv("GTKB_OPENROUTER_API_KEY", "fixture-credential")
    monkeypatch.setenv("UNRELATED_SETTING", "x")
    env = home.base_environment(tmp_path)
    assert not {name for name in env if any(word in name for word in ("KEY", "TOKEN", "SECRET", "PASSWORD"))}
    assert "UNRELATED_SETTING" not in env
    assert env["DSH_HOME"] == env["GTKB_HOME_STATE"] == str(tmp_path)
    assert env["DSH_TELEMETRY_DISABLED"] == "1" and env["DSH_PERMISSION_MODE"] == "workspace-write"
    assert env["GTKB_GUARD_GATE"].endswith(str(Path("scripts") / "implementation_start_gate.py"))
    # c123 (batch design WP3 3.2): the guard's decision log, in the state folder's logs under the SDK's file name.
    assert env["GTKB_GUARD_LOG"] == str(tmp_path / "logs" / "guard-decisions.jsonl")
    assert env["GT_PROJECT_ROOT"] == env["GTKB_HOME_ROOT"] == str(home.ROOT)


def test_the_credential_comes_from_the_environment_or_gtkbs_own_loader_by_name(tmp_path, monkeypatch):
    home = _module("home")
    monkeypatch.setenv("GTKB_OPENROUTER_API_KEY", "fixture-from-environment")
    assert home.credential() == {"GTKB_OPENROUTER_API_KEY": "fixture-from-environment"}
    monkeypatch.delenv("GTKB_OPENROUTER_API_KEY")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "_env.py").write_text(
        "def load_env_local(check_only=False):\n    assert check_only\n    return {'GTKB_OPENROUTER_API_KEY': 'fixture-from-loader', 'OTHER_KEY': 'x'}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(home, "ROOT", tmp_path)
    assert home.credential() == {"GTKB_OPENROUTER_API_KEY": "fixture-from-loader"}
    (tmp_path / "scripts" / "_env.py").write_text(
        "def load_env_local(check_only=False):\n    return {}\n", encoding="utf-8"
    )
    assert home.credential() == {}


def test_the_profile_manifest_is_always_the_pinned_one(tmp_path):
    home = _module("home")
    release = json.loads((WEB / "release.json").read_text(encoding="utf-8"))
    manifest = home.write_profile_manifest(tmp_path, release)
    assert manifest == tmp_path / "profiles" / "gtkb" / "package.json"
    assert json.loads(manifest.read_text(encoding="utf-8"))["dsh"]["profile"] == release["profile_manifest"]
    manifest.write_text("{}", encoding="utf-8")
    home.write_profile_manifest(tmp_path, release)
    assert json.loads(manifest.read_text(encoding="utf-8"))["dsh"]["profile"]["patchReload"] == "startup"


# c123 (owner decision C3): the acknowledgement a fresh Home state is seeded with, in the namespace and field the
# upstream onboarding copy reads.
ACKNOWLEDGEMENT = b'ui-onboarding:\n  welcomeNoticeVersion: "2026-08-13.1"\n'


def test_a_fresh_home_state_acknowledges_the_internal_testing_notice(tmp_path):
    """c123 (owner decision C3): a fresh state gets settings.yaml with only the acknowledgement of upstream's Internal
    Testing Notice, so the notice does not show; the version reads back as a string."""
    home = _module("home")
    settings = home.seed_onboarding_acknowledgement(tmp_path / "state")
    assert settings == tmp_path / "state" / "settings.yaml"
    assert settings.read_bytes() == ACKNOWLEDGEMENT
    assert yaml.safe_load(settings.read_text(encoding="utf-8")) == {
        "ui-onboarding": {"welcomeNoticeVersion": "2026-08-13.1"}
    }


@pytest.mark.parametrize(
    "existing",
    [
        b"# the owner's own settings\nllm-pi-ai:\n  providers: {}\n"
        b"ui-onboarding:\n  welcomeNoticeVersion: 2026-01-01.1\n",
        b"llm-pi-ai:\n  providers: {}\n",
    ],
    ids=["comment-and-another-section", "without-ui-onboarding"],
)
def test_an_existing_settings_file_is_never_changed(tmp_path, existing):
    """c123 (owner decision C3): the owner's settings document stays byte-identical, whatever it holds."""
    home = _module("home")
    settings = tmp_path / "settings.yaml"
    settings.write_bytes(existing)
    assert home.seed_onboarding_acknowledgement(tmp_path) == settings
    assert settings.read_bytes() == existing


def test_start_seeds_the_acknowledgement_before_it_launches(tmp_path, monkeypatch):
    """c123 (owner decision C3): start() seeds a fresh state before it launches the server. The installation, Node, the
    composition proof and the credential are stubs, and the launch itself fails."""
    home = _module("home")
    state = tmp_path / "state"
    monkeypatch.setattr(home, "verify_installation", lambda: {"profile_manifest": {}})
    monkeypatch.setattr(home, "node_executable", lambda: "node")
    monkeypatch.setattr(home, "prove_composition", lambda node, env: None)
    monkeypatch.setattr(home, "credential", lambda: {})
    seen_at_launch = []

    def popen(*args, **kwargs):
        seen_at_launch.append((state / "settings.yaml").read_bytes())
        raise OSError("fixture: the server is not launched")

    monkeypatch.setattr(home.subprocess, "Popen", popen)
    with pytest.raises(OSError, match="fixture: the server is not launched"):
        home.start(state)
    assert seen_at_launch == [ACKNOWLEDGEMENT]


# c123 (owner decision C3): WELCOME_NOTICE_VERSION was read from the pinned upstream onboarding copy,
# @deepseek-ai/dsh-client-ui-settings-models 0.1.2-rc.1, lib/client.js ("ui-onboarding", "welcomeNoticeVersion",
# "2026-08-13.1"). This pins that package, so a version or content change fails here, before release.
VERIFIED_NOTICE_PACKAGE = {
    "entry": "node_modules/@deepseek-ai/dsh-client-ui-settings-models",
    "version": "0.1.2-rc.1",
    "integrity": "sha512-r4ErsBy1NE9QWqZmFyxoBFQhCc+pymmc62PFN7PBxFAX85JRJ3asWwjZPpgXW+y7AkqNWy1JVJqlLdf7W5pCIA==",
}


def test_the_notice_acknowledgement_is_pinned_to_the_verified_upstream_onboarding_copy():
    home = _module("home")
    lock = json.loads((WEB / "package-lock.json").read_text(encoding="utf-8"))
    entry = lock["packages"][VERIFIED_NOTICE_PACKAGE["entry"]]
    assert (entry["version"], entry["integrity"]) == (
        VERIFIED_NOTICE_PACKAGE["version"],
        VERIFIED_NOTICE_PACKAGE["integrity"],
    ), "verify WELCOME_NOTICE_VERSION in the upstream onboarding copy, then update home.py"
    assert home.WELCOME_NOTICE_VERSION == "2026-08-13.1"


DUMP = """- id: agent-default-model
  config: {}
- id: llm-pi-ai
  config: {}
- id: llm-deepseek
  name: '@deepseek-ai/dsh-llm-deepseek'
  disabled: true
- id: ui-brand-official
  name: '@deepseek-ai/dsh-client-ui-brand-official'
  disabled: true
- id: gtkb-home-effect-guard
  name: ./gtkb_home_guard.mjs
- id: gtkb-home
  name: ./plugins/gtkb-home/lib/index.js
"""
ENABLED_BRAND = DUMP.replace("dsh-client-ui-brand-official'\n  disabled: true\n", "dsh-client-ui-brand-official'\n")
ENABLED_PROVIDER = DUMP.replace(
    "dsh-llm-deepseek'\n  disabled: true\n", "dsh-llm-deepseek'\n  config:\n    disabled: true\n"
)


@pytest.mark.parametrize(
    ("dump", "problem"),
    [
        (DUMP, None),
        (DUMP.replace("- id: gtkb-home-effect-guard\n  name: ./gtkb_home_guard.mjs\n", ""), "lacks required rows"),
        (ENABLED_BRAND, "row ui-brand-official is not disabled"),
        (ENABLED_PROVIDER, "row llm-deepseek is not disabled"),
    ],
)
def test_start_proves_the_composed_configuration_first(monkeypatch, dump, problem):
    home = _module("home")
    monkeypatch.setattr(
        home.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout=dump, stderr="")
    )
    if problem is None:
        home.prove_composition("node", {})
    else:
        with pytest.raises(home.HomeError, match=problem):
            home.prove_composition("node", {})


def test_the_home_refuses_to_start_uninstalled_or_changed(tmp_path, monkeypatch):
    home = _module("home")
    source = _source_tree(tmp_path)
    monkeypatch.setattr(home, "SOURCE", source)
    with pytest.raises(home.HomeError, match="not installed"):
        home.verify_installation()
    launcher = source / "node_modules" / "@deepseek-ai" / "dsh" / "lib"
    launcher.mkdir(parents=True)
    (launcher / "bin.js").write_text("", encoding="utf-8")
    (source / "installed.json").write_text(
        json.dumps({"lockfile_sha256": "0" * 64, "version": "0.1.2-rc.1"}), encoding="utf-8"
    )
    with pytest.raises(home.HomeError, match="differs from the pinned release"):
        home.verify_installation()


def test_start_and_stop_outcomes_are_logged_for_the_logon_task(tmp_path, monkeypatch, capsys):
    home = _module("home")

    def not_installed():
        raise home.HomeError("fixture: the Home server is not installed")

    monkeypatch.setattr(home, "verify_installation", not_installed)
    assert home.main(["stop", "--state", str(tmp_path)]) == 0
    assert home.main(["start", "--state", str(tmp_path)]) == 1
    assert home.main(["status", "--state", str(tmp_path)]) == 0
    assert home.main(["url", "--state", str(tmp_path)]) == 1
    capsys.readouterr()
    lines = (tmp_path / "logs" / "home-launcher.log").read_text(encoding="utf-8").splitlines()
    entries = [json.loads(line) for line in lines]
    assert [(entry["action"], entry["ok"]) for entry in entries] == [("stop", True), ("start", False)]
    assert entries[0]["reason"] == "no run record"
    assert entries[1]["error"] == "fixture: the Home server is not installed"
    assert all("at" in entry for entry in entries) and "token=" not in "".join(lines)


def test_without_a_run_record_nothing_is_stopped_and_no_url_is_given(tmp_path, capsys):
    home = _module("home")
    assert home.status(tmp_path) == {"running": False}
    assert home.stop(tmp_path) == {"stopped": False, "reason": "no run record"}
    assert home.main(["url", "--state", str(tmp_path)]) == 1
    assert json.loads(capsys.readouterr().out) == {
        "action": "url",
        "ok": False,
        "error": "The Home server is not running; start it with: gt home start",
    }


def test_the_run_record_names_its_root_and_its_guard_log(tmp_path, monkeypatch):
    """c123 (batch design WP3 3.2, 3.3): start records the installation's root and the guard log it gave the server,
    and status reports that log. The server is a stub that reports ready; nothing is installed or started."""
    home = _module("home")
    state = tmp_path / "state"
    guard_log = str(state / "logs" / "guard-decisions.jsonl")
    identity = {"exe": "C:\\nodejs\\node.exe", "cmd": "fixture", "created": "2026-10-01T00:00:00.0000000Z"}
    monkeypatch.setattr(home, "verify_installation", lambda: {"profile_manifest": {}})
    monkeypatch.setattr(home, "node_executable", lambda: "node")
    monkeypatch.setattr(home, "prove_composition", lambda node, env: None)
    monkeypatch.setattr(home, "credential", lambda: {})
    monkeypatch.setattr(home, "process_identity", lambda pid: identity)
    monkeypatch.setattr(home.time, "sleep", lambda seconds: None)
    launched = []

    class Server:
        pid = 4242

        def poll(self):
            return None

    def popen(command, *, env, stdout, stderr, **options):
        launched.append(env["GTKB_GUARD_LOG"])
        stdout.write(b"http://127.0.0.1:3080/?token=fixture-not-a-token\n")
        stderr.write(("\n".join(home.ACTIVATION_LINES) + "\n").encode("utf-8"))
        return Server()

    monkeypatch.setattr(home.subprocess, "Popen", popen)
    assert home.start(state)["started"] is True
    record = json.loads((state / "run" / "home-run.json").read_text(encoding="utf-8"))
    assert launched == [guard_log] and record["guard_log"] == guard_log
    assert record["root"] == str(home.ROOT)
    monkeypatch.setattr(home, "ours", lambda found: False)
    assert home.status(state)["guard_log"] == guard_log


def test_a_live_home_of_another_root_keeps_its_run_record_and_url_file(tmp_path, monkeypatch):
    """c123 (batch design WP3 3.3): every installation shares the default state folder, so stop and start refuse the
    run record of another root's live Home before anything else, and the record and the URL file stay. A record from
    before records named their root is another root's while its live process runs another tree's launcher."""
    home = _module("home")
    state = tmp_path / "state"
    other = tmp_path / "GT-KB"
    (state / "run").mkdir(parents=True)
    url_file = state / "run" / "home-url.txt"
    url_file.write_text("http://127.0.0.1:3080/?token=fixture-not-a-token\n", encoding="utf-8")
    record_path = state / "run" / "home-run.json"
    record = {
        "pid": 4242,
        "created": "2026-09-30T18:09:24.0000000Z",
        "root": str(other),
        "port": 3080,
        "control": "fixture-not-a-secret",
        "url_file": str(url_file),
        "log_file": str(state / "logs" / "home-20260930T180924.log"),
        "credential_supplied": True,
    }
    launcher = other / "infrastructure" / "deepseek-web" / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"
    live = {"exe": "C:\\nodejs\\node.exe", "cmd": f'node "{launcher}" --profile gtkb', "created": record["created"]}
    monkeypatch.setattr(home, "process_identity", lambda pid: live if pid == record["pid"] else None)

    def nothing_else():
        raise AssertionError("the refusal comes before anything is verified, written or started")

    monkeypatch.setattr(home, "verify_installation", nothing_else)
    legacy = {key: value for key, value in record.items() if key != "root"}
    for written, owner in ((record, str(other)), (legacy, "another installation")):
        record_path.write_text(json.dumps(written), encoding="utf-8")
        kept = (record_path.read_bytes(), url_file.read_bytes())
        for action in (home.stop, home.start):
            with pytest.raises(home.HomeError, match="belongs to the live Home of") as refused:
                action(state)
            assert owner in str(refused.value) and str(home.ROOT) in str(refused.value)
            assert (record_path.read_bytes(), url_file.read_bytes()) == kept
    monkeypatch.setattr(home, "process_identity", lambda pid: None)
    assert home.stop(state) == {"stopped": False, "reason": "the recorded process is not running"}
    assert not record_path.exists() and url_file.exists(), "once that Home has ended, stop clears its stale record"
