"""Receiving tests for branch identity and raw-index ambiguity; not applied yet."""

import subprocess

import pytest

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_commit_boundary import commit_environment as commit_environment
from platform_tests.groundtruth_kb.test_native_commit_boundary import invoke, real_index
from platform_tests.groundtruth_kb.test_native_project_finalization import base, git, integration

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def test_same_oid_branch_switch_cannot_redirect_project_commit(commit_environment):
    client, root, parent, checkout, hooks, config, message = commit_environment
    initial_branch = git(checkout, "symbolic-ref", "HEAD").stdout.strip()
    git(checkout, "branch", "foreign-branch", parent)
    before = real_index(checkout).read_bytes()
    hook = hooks / "pre-commit"
    hook.write_text("#!/bin/sh\ngit symbolic-ref HEAD refs/heads/foreign-branch\n", encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    result = invoke(config, message)
    assert result.exit_code != 0 and any(
        code in result.output for code in ("checkout_redirected", "checkout_base_changed")
    ), result.output
    assert git(checkout, "rev-parse", initial_branch).stdout.strip() == parent
    assert git(checkout, "rev-parse", "refs/heads/foreign-branch").stdout.strip() == parent
    assert base(integration(root)) == parent
    assert real_index(checkout).read_bytes() == before
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"


@pytest.mark.parametrize("alias", [b"CODE.PY", b"bad-\xff-name.py"])
def test_raw_index_ambiguity_is_typed_and_refuses_without_index_or_head_changes(commit_environment, alias):
    client, root, parent, checkout, _, config, message = commit_environment
    oid = git(checkout, "rev-parse", "HEAD:code.py").stdout.strip()
    result = subprocess.run(
        ["git", "-C", str(checkout), "update-index", "-z", "--index-info"],
        input=b"100644 " + oid.encode("ascii") + b"\t" + alias + b"\0",
        capture_output=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    before = real_index(checkout).read_bytes()
    product = (checkout / "code.py").read_bytes()
    result = invoke(config, message)
    assert result.exit_code != 0, result.output
    assert "index_ambiguous" in result.output, (result.output, result.exception)
    assert base(checkout) == base(integration(root)) == parent
    assert real_index(checkout).read_bytes() == before
    assert (checkout / "code.py").read_bytes() == product
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
