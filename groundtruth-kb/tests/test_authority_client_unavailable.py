"""An unavailable authority is refused with its cause and timing recorded (no retry, no widened timeout)."""

from __future__ import annotations

import os
import socket
import subprocess
import sys

import pytest

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError


def _closed_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def test_refused_socket_names_its_cause_elapsed_and_timeout() -> None:
    client = AuthorityClient(f"http://127.0.0.1:{_closed_port()}", timeout=2)
    with pytest.raises(AuthorityClientError) as refused:
        client.request("GET", "/v1/status")
    assert refused.value.code == "authority_unavailable"
    details = refused.value.details
    assert isinstance(details, dict)
    # This Windows host drops connections to closed loopback ports instead of refusing them, so the
    # observed cause is a timeout after the full budget; both are recorded truthfully.
    assert details["cause"] in {"ConnectionRefusedError", "TimeoutError", "OSError", "URLError"}
    assert details["timeout_seconds"] == 2 and 0 <= details["elapsed_seconds"] <= 3
    assert details["method"] == "GET" and details["path"] == "/v1/status"
    assert details["cause_message"]


def test_expired_timeout_is_distinguished_from_a_refused_socket() -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)  # accepts the connection and never answers
        client = AuthorityClient(f"http://127.0.0.1:{listener.getsockname()[1]}", timeout=0.5)
        with pytest.raises(AuthorityClientError) as refused:
            client.request("GET", "/v1/status")
    details = refused.value.details
    assert refused.value.code == "authority_unavailable" and isinstance(details, dict)
    assert details["cause"] in {"TimeoutError", "timeout", "socket.timeout"}
    assert details["timeout_seconds"] == 0.5 and details["elapsed_seconds"] >= 0.5


def test_commit_hook_relays_the_cause_into_its_refusal(tmp_path, monkeypatch) -> None:
    """The reference-transaction hook prints the details after the message; Git relays that line."""
    port = _closed_port()
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "develop", str(checkout)], check=True)
    environment = {
        **{key: value for key, value in os.environ.items() if not key.startswith(("PG", "GIT_", "GT_POSTGRES_"))},
        "GTKB_PROJECT_COMMIT_AUTHORITY": f"http://127.0.0.1:{port}",
        "GTKB_PROJECT_COMMIT_PROJECT": "PROJECT-1",
        "GTKB_PROJECT_COMMIT_CONTEXT": "pb1",
        "GTKB_PROJECT_COMMIT_VERSION": "1",
        "GTKB_PROJECT_COMMIT_PARENT": "0" * 40,
        "GTKB_PROJECT_COMMIT_BRANCH": "refs/heads/develop",
        "GTKB_PROJECT_COMMIT_CHECKOUT": str(checkout),
        "PYTHONIOENCODING": "utf-8",
    }
    result = subprocess.run(
        [sys.executable, "-P", "-m", "groundtruth_kb.project.native_commit", "prepared"],
        cwd=checkout,
        env=environment,
        input=f"{'0' * 40} {'1' * 40} HEAD\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert result.returncode == 1
    assert "The configured authority is unavailable" in result.stderr
    assert (
        '"cause"' in result.stderr and '"elapsed_seconds"' in result.stderr and '"timeout_seconds": 5' in result.stderr
    )
