"""Execute the authored read guard with explicit current declarations.

Fixtures qualify the parser and projected script behavior. They do not establish
that a native host invokes a hook, or that an allowed read proves currentness.
"""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import pytest

from platform_tests.scripts.sot_hook_fixtures import HOOK, REGISTRY, SUBSTITUTE, registry, run_hook

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def read_root(tmp_path: Path) -> Path:
    root = tmp_path / "selected"
    target = root / HOOK
    target.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / HOOK, target)
    registry(root)
    return root


def read_payload(path=SUBSTITUTE):
    return {"tool_name": "Read", "tool_input": {"file_path": path}}


def shell_payload(command, tool="Bash"):
    return {"tool_name": tool, "tool_input": {"command": command}}


def blocked(root, payload, **kwargs):
    value = run_hook(root, payload, **kwargs)
    assert value.get("decision") == "block", value
    assert "membase:work_items" in value["reason"] and "fixture-work" in value["reason"]
    return value


def test_read_against_forbidden_substitute_blocks(read_root):
    blocked(read_root, read_payload())


def test_grep_against_forbidden_substitute_blocks(read_root):
    blocked(read_root, {"tool_name": "Grep", "tool_input": {"path": SUBSTITUTE, "pattern": "state"}})


def test_glob_against_forbidden_substitute_blocks(read_root):
    blocked(read_root, {"tool_name": "Glob", "tool_input": {"pattern": SUBSTITUTE}})


def test_read_against_unregistered_path_no_block(read_root):
    assert run_hook(read_root, read_payload("README.md")) == {}


def test_read_against_canonical_sot_no_block(read_root):
    assert run_hook(read_root, read_payload("config/registry/sot-artifacts.toml")) == {}


def test_bash_get_content_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("Get-Content " + SUBSTITUTE))


def test_bash_gc_alias_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("gc " + SUBSTITUTE))


def test_bash_cat_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("cat " + SUBSTITUTE))


def test_bash_select_string_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("Select-String -Path " + SUBSTITUTE + " -Pattern state"))


def test_bash_get_childitem_recurse_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("Get-ChildItem -Path " + SUBSTITUTE + " -Recurse"))


def test_bash_rg_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("rg state " + SUBSTITUTE))


def test_bash_grep_forbidden_blocks(read_root):
    blocked(read_root, shell_payload("grep state " + SUBSTITUTE))


def test_bash_unrelated_command_no_block(read_root):
    assert run_hook(read_root, shell_payload("git status --short")) == {}


def test_bash_get_content_unregistered_no_block(read_root):
    assert run_hook(read_root, shell_payload("Get-Content README.md")) == {}


def test_bypass_env_disables_block(read_root):
    assert run_hook(read_root, read_payload(), bypass=True) == {}
    blocked(read_root, read_payload())


def test_unknown_tool_no_block(read_root):
    assert run_hook(read_root, {"tool_name": "Edit", "tool_input": {"file_path": SUBSTITUTE}}) == {}


def test_empty_payload_no_block(read_root):
    assert run_hook(read_root, {}) == {}


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content -LiteralPath derived/status.txt",
        "Get-Content -Path derived/status.txt -Raw",
        'Get-Content -literalpath "derived/status.txt"',
        "gc -Raw derived/status.txt",
        "rg --files derived/status.txt",
        "rg -e state derived/status.txt",
        "rg state README.md derived/status.txt",
        "grep -n state README.md derived/status.txt",
    ],
)
def test_explicit_read_and_search_arguments_cannot_disappear(read_root, command):
    blocked(read_root, shell_payload(command))


@pytest.mark.parametrize("tool", ["Bash", "PowerShell", "Shell", "bash", "powershell", "shell"])
def test_all_declared_normalized_shell_names_use_the_same_guard(read_root, tool):
    blocked(read_root, shell_payload("Get-Content -LiteralPath " + SUBSTITUTE, tool))


@pytest.mark.parametrize(
    "payload",
    [
        {"tool_name": "Read", "tool_input": {"path": SUBSTITUTE}},
        {"tool_name": "Grep", "tool_input": {"path": "derived", "pattern": "state"}},
        {"tool_name": "Glob", "tool_input": {"path": "derived", "pattern": "*.txt"}},
        {"tool_name": "Glob", "tool_input": {"path": "derived"}},
        {"tool_name": "Glob", "tool_input": {"pattern": "derived/*.txt"}},
    ],
)
def test_search_base_and_normalized_read_fields_are_respected(read_root, payload):
    blocked(read_root, payload)


def test_payload_cwd_controls_relative_read_without_changing_registry_root(read_root, tmp_path):
    nested = read_root / "derived"
    nested.mkdir()
    payload = read_payload("status.txt")
    payload["cwd"] = str(nested)
    blocked(read_root, payload, cwd=tmp_path)
    payload["tool_input"]["file_path"] = "../README.md"
    assert run_hook(read_root, payload, cwd=tmp_path) == {}


def test_same_named_path_outside_selected_project_is_not_a_substitute(read_root, tmp_path):
    outside = tmp_path / "other"
    outside.mkdir()
    assert run_hook(read_root, read_payload(str(outside / SUBSTITUTE))) == {}
    assert run_hook(read_root, read_payload(), cwd=outside) == {}


def test_absolute_in_root_path_blocks_even_from_foreign_cwd(read_root, tmp_path):
    blocked(read_root, read_payload(str(read_root / SUBSTITUTE)), cwd=tmp_path)


def test_empty_registry_is_no_policy_and_does_not_create_state(read_root):
    registry(read_root, "artifacts = []\n")
    assert run_hook(read_root, read_payload()) == {}


@pytest.mark.parametrize("failure", ["missing", "invalid"])
def test_registry_failure_is_explicit_and_never_an_empty_allow(read_root, failure):
    path = registry(read_root)
    if failure == "missing":
        path.unlink()
    else:
        path.write_text("invalid = [", encoding="utf-8")
    value = run_hook(read_root, read_payload())
    assert value.get("decision") == "block" and "registry" in value["reason"]


def test_archive_declaration_does_not_block_as_current_authority(read_root):
    registry(read_root, REGISTRY.replace('lifecycle = "active"', 'lifecycle = "archive"'))
    assert run_hook(read_root, read_payload()) == {}


@pytest.mark.parametrize(
    "target", ["derived/status.txt.copy", "x/derived/status.txt", "derived/children-sibling/a.txt"]
)
def test_path_boundaries_do_not_reject_unregistered_siblings(read_root, target):
    assert run_hook(read_root, read_payload(target)) == {}


@pytest.mark.parametrize("target", ["derived/children/a.txt", "derived/children/nested/a.txt", "DERIVED/STATUS.TXT"])
def test_declared_subtrees_and_windows_case_are_covered(read_root, target):
    blocked(read_root, read_payload(target))


def test_search_parent_uses_windows_case_rules(read_root):
    blocked(read_root, {"tool_name": "Grep", "tool_input": {"path": "DERIVED"}})


def test_nonrecursive_listing_does_not_read_nested_substitute_contents(read_root):
    assert run_hook(read_root, shell_payload("Get-ChildItem .")) == {}
    blocked(read_root, shell_payload("Get-ChildItem . -Recurse"))


def test_quoted_literal_path_preserves_spaces_and_unicode(read_root):
    registry(read_root, REGISTRY.replace("derived/status.txt", "derived/current état.txt"))
    blocked(read_root, shell_payload('Get-Content -LiteralPath "derived/current état.txt"'))


def test_invalid_substitute_locator_cannot_silently_disable_guard(read_root):
    registry(read_root, REGISTRY.replace("derived/status.txt", "../other.txt"))
    value = run_hook(read_root, read_payload())
    assert value.get("decision") == "block" and "registry" in value["reason"]


@pytest.mark.timeout(300)
def test_each_complete_projected_hook_reads_its_own_root_from_foreign_cwd(generated_harness_root, tmp_path):
    root = tmp_path / "projected-copy"
    shutil.copytree(generated_harness_root, root)
    registry(root)
    profiles = tomllib.loads((root / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))
    names = []
    for name, profile in profiles["harnesses"].items():
        if profile.get("status") == "profile_pending":
            continue
        names.append(name)
        # Every native registration now addresses this same authored script.
        hook = Path(profiles["baseline"]["hooks_root"]) / "sot-read-discipline.py"
        payload = read_payload(str(root / SUBSTITUTE))
        payload["cwd"] = str(root)
        blocked(root, payload, hook=hook, cwd=tmp_path)
        assert run_hook(root, read_payload(str(tmp_path / "unrelated.txt")), hook=hook, cwd=tmp_path) == {}
    assert len(names) == 8
