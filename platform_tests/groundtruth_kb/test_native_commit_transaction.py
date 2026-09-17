"""Receiving regression: the reviewed formal roots remain locked through commit."""

import os
import shlex
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_commit_boundary import commit_environment as commit_environment
from platform_tests.groundtruth_kb.test_native_project_finalization import base, integration

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def test_current_formal_roots_cannot_change_between_reference_check_and_project_commit(commit_environment):
    client, root, parent, checkout, hooks, config, message = commit_environment
    pause = hooks.parent / "reference-pause"
    ready = Path(str(pause) + ".ready")
    release = Path(str(pause) + ".release")
    hook = hooks / "reference-transaction"
    hook.write_text(
        "#!/bin/sh\nPAUSE="
        + shlex.quote(str(pause).replace("\\", "/"))
        + "\n"
        + """
if [ -z "$GTKB_PROJECT_COMMIT_PROJECT" ]; then exit 0; fi
"$GTKB_PROJECT_COMMIT_PYTHON" -m groundtruth_kb.project.native_commit "$@" || exit $?
if [ "$1" = prepared ]; then
  printf ready > "${PAUSE}.ready"
  while [ ! -f "${PAUSE}.release" ]; do sleep 0.05; done
fi
""",
        encoding="utf-8",
        newline="\n",
    )
    hook.chmod(0o755)
    env = dict(os.environ, GTKB_TEST_REFERENCE_PAUSE=str(pause).replace("\\", "/"))
    args = [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "--config",
        str(config),
        "projects",
        "commit",
        "PROJECT-1",
        "--native-context-id",
        "lo3",
        "--expected-version",
        "1",
        "--message-file",
        str(message),
        "--json",
    ]
    process = subprocess.Popen(
        args,
        cwd=checkout,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    original_formal = client.get("/v1/specifications/SPEC-1").json()
    changed_fields = {
        "title": "Required effect",
        "description": "Materially changed formal intent",
        "status": "active",
    }
    try:
        deadline = time.monotonic() + 40
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        # String messages survive pytest's repr elision; a refusal's diagnostic details stay in the evidence.
        assert ready.exists(), "stdout: {}\nstderr: {}".format(*process.communicate(timeout=5))
        assert base(checkout) == parent
        with ThreadPoolExecutor(max_workers=1) as pool:
            mutation = pool.submit(
                put,
                client,
                "specifications",
                "SPEC-1",
                changed_fields,
                expected_version=1,
            )
            # The mutation must eventually succeed, but only after this commit's
            # reference/finalization boundary releases the actual formal row lock.
            try:
                time.sleep(1)
                assert not mutation.done(), mutation.result().text
            finally:
                release.touch()
            output, error = process.communicate(timeout=30)
            assert process.returncode == 0, f"stdout: {output}\nstderr: {error}"
            response = mutation.result(timeout=15)
            committed_head = base(checkout)
            assert committed_head != parent
            assert base(integration(root)) == committed_head
            committed_project = client.get("/v1/projects/PROJECT-1").json()
            assert committed_project["project"]["status"] == "verified"
            if response.status_code == 409:
                # Serializable arbitration may refuse the waiting mutation
                # after finalization. Reread canonical state before one retry;
                # a conflict must neither change formal state nor undo Git.
                assert response.json()["error"]["code"] == "retryable_conflict", response.text
                assert client.get("/v1/specifications/SPEC-1").json() == original_formal
                response = put(
                    client,
                    "specifications",
                    "SPEC-1",
                    changed_fields,
                    expected_version=original_formal["version"],
                )
            assert response.status_code == 200, response.text
        updated_formal = client.get("/v1/specifications/SPEC-1").json()
        assert updated_formal["version"] == original_formal["version"] + 1
        assert all(updated_formal[key] == value for key, value in changed_fields.items())
        assert client.get("/v1/projects/PROJECT-1").json() == committed_project
        assert base(integration(root)) == base(checkout) == committed_head
    finally:
        release.touch()
        if process.poll() is None:
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True,
                        timeout=10,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                else:
                    process.kill()
                process.communicate(timeout=10)
