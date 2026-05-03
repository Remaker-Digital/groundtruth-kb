"""Transport contract tests — placeholder shapes, not production behavior.

The example demonstrates how an adopter wires contract assertions against
their transport module. Real adopters replace `echo` with their own
transport client and replace these placeholders with the actual
contract assertions.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transport import TransportRequest, TransportResponse, echo  # noqa: E402


def test_echo_round_trips_payload_to_body() -> None:
    request = TransportRequest(operation="ping", payload={"k": "v"})
    response = echo(request)
    assert isinstance(response, TransportResponse)
    assert response.status == "ok"
    assert response.body == {"k": "v"}


def test_echo_preserves_payload_immutability() -> None:
    payload = {"k": "v"}
    request = TransportRequest(operation="ping", payload=payload)
    response = echo(request)
    payload["k"] = "mutated"
    assert response.body == {"k": "v"}, "echo must copy payload, not alias it"


def test_request_is_frozen_dataclass() -> None:
    request = TransportRequest(operation="ping", payload={"k": "v"})
    try:
        request.operation = "other"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("TransportRequest should be frozen")
