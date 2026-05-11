"""Validate a formal-artifact approval packet against the live gate's schema.

This script is the canonical helper that bridge proposals cite in IP-4
pre-insertion packet validation steps. It eliminates the previously
duplicated inline-Python patterns that embedded brittle PowerShell-
escaped `python -c "..."` invocations across multiple proposals.

Per WI-3266 (GTKB-FORMAL-ARTIFACT-PACKET-VALIDATOR-CLI), this helper:

- Loads `.claude/hooks/formal-artifact-approval-gate.py` via
  ``importlib.util.spec_from_file_location`` to access the canonical
  ``_load_packet`` and ``_validate_packet`` helpers PLUS the
  ``REQUIRED_PACKET_FIELDS`` / ``VALID_ARTIFACT_TYPES`` /
  ``VALID_APPROVAL_MODES`` constants. By construction the validation
  matches the live gate -- no duplication, no drift.

Exit codes:

- ``0`` -- packet validates against the live gate's schema. Prints
  ``packet_valid: <packet_path>`` to stdout for citation in bridge
  post-implementation reports.
- ``1`` -- packet fails validation. The gate's specific error message
  (the same string the gate would emit when it blocks a tool call) is
  printed to stderr.
- ``2`` -- invocation error (missing packet path argument, gate module
  not found, etc.).

Usage:

    python scripts/validate_formal_artifact_packet.py <packet_path>

Example:

    python scripts/validate_formal_artifact_packet.py \
        .groundtruth/formal-artifact-approvals/2026-05-11-adr-x.json

Authority: WI-3266 + bridge/gtkb-formal-artifact-packet-validator-cli-001.md.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_gate_module(project_root: Path) -> Any:
    """Load the live formal-artifact-approval-gate.py module by path.

    Returns the loaded module so the caller can access ``_load_packet``,
    ``_validate_packet``, and the canonical constants. Raises ``RuntimeError``
    with a precise message if the gate module cannot be loaded.
    """
    gate_path = project_root / ".claude" / "hooks" / "formal-artifact-approval-gate.py"
    if not gate_path.is_file():
        raise RuntimeError(f"formal-artifact-approval-gate.py not found at {gate_path}")
    spec = importlib.util.spec_from_file_location("formal_artifact_approval_gate", gate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not create import spec for {gate_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def validate(packet_path: str, project_root: Path | None = None) -> tuple[int, str]:
    """Validate the packet at ``packet_path`` against the live gate.

    Returns ``(exit_code, message)``. ``exit_code`` is ``0`` for a valid
    packet, ``1`` for a packet that fails the gate's validation, and ``2``
    for an invocation/import error.

    The ``message`` is either the success line (``packet_valid: <path>``) or
    the gate's verbatim error message.
    """
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    try:
        gate = _load_gate_module(project_root)
    except RuntimeError as exc:
        return 2, str(exc)

    packet, load_error = gate._load_packet(packet_path)
    if load_error is not None or packet is None:
        return 1, load_error or "packet could not be loaded"

    validation_error = gate._validate_packet(packet)
    if validation_error is not None:
        return 1, validation_error

    return 0, f"packet_valid: {packet_path}"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] in {"-h", "--help"}:
        print(
            "usage: python scripts/validate_formal_artifact_packet.py <packet_path>\n"
            "  validates a formal-artifact approval packet against the live gate.\n"
            "  exit 0 = packet_valid; exit 1 = validation failed; exit 2 = usage error.",
            file=sys.stderr,
        )
        return 2

    packet_path = args[0]
    exit_code, message = validate(packet_path)
    if exit_code == 0:
        print(message)
    else:
        print(message, file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
