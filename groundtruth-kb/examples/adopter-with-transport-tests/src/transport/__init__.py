"""Minimal transport module showing the request/response contract shape.

This module demonstrates the structure an adopter would use, not production
behavior. The shapes are deliberately synthetic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransportRequest:
    """A request envelope for the transport contract."""

    operation: str
    payload: dict[str, str]


@dataclass(frozen=True)
class TransportResponse:
    """A response envelope for the transport contract."""

    status: str
    body: dict[str, str]


def echo(request: TransportRequest) -> TransportResponse:
    """Round-trip a request to a response with status='ok'.

    Demonstrates the simplest possible transport contract: any well-formed
    request returns a well-formed response with the same payload echoed
    into the body. Production transports replace this with real I/O.
    """
    return TransportResponse(status="ok", body=dict(request.payload))
