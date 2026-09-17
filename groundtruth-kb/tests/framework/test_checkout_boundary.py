"""A supplied checkout boundary is independent of a retired local policy copy."""

import json
from pathlib import Path

import pytest

from groundtruth_kb.enforcement import check_bash_command, check_path_boundary


@pytest.mark.parametrize("location", ["first-host", "relocated/second-host"])
@pytest.mark.parametrize("content", ["stale", "malformed"])
def test_local_file_cannot_redirect_the_supplied_checkout(tmp_path, location, content):
    root = tmp_path / location
    legacy = root / ".gtkb/directive-registry.json"
    legacy.parent.mkdir(parents=True)
    text = (
        json.dumps(
            {"directives": [{"id": "DIR-ROOT-BOUNDARY-001", "patterns": {"allowed_root": str(tmp_path / "foreign")}}]}
        )
        if content == "stale"
        else "{invalid"
    )
    legacy.write_text(text, encoding="utf-8")
    assert check_path_boundary("docs/current.md", root) == (True, "")
    assert check_path_boundary(str(root / "docs/current.md"), root) == (True, "")
    assert check_bash_command('cat > "' + str(root / "docs/current.md") + '"', root) == (True, "")
    assert legacy.read_text(encoding="utf-8") == text


@pytest.mark.parametrize(
    "relative", ["ordinary.md", ".claude/settings.json", ".codex/hooks.json", ".api-harness/provider/settings.json"]
)
def test_foreign_harness_paths_receive_no_boundary_exemption(tmp_path, relative):
    root = tmp_path / "checkout"
    root.mkdir()
    foreign = tmp_path / "checkout-other" / Path(relative)
    allowed, reason = check_path_boundary(str(foreign), root)
    assert not allowed
    assert "outside allowed root" in reason
    allowed, reason = check_path_boundary("../checkout-other/" + relative, root)
    assert not allowed
    assert "outside allowed root" in reason
    assert not foreign.exists()
