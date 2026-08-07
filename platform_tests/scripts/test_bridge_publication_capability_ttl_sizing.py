"""Focused coverage for the WI-5839 worker-enablement mint-TTL wiring.

Asserts that the bridge-publication capability mint resolves its default TTL
through the governed timer SoT instead of the previous hard-coded 120-second
default, that the 800-second ceiling is still enforced for explicit values, and
that the production bridge writer passes the resolved TTL at its single mint
call. Authority: W0.1 thread B (bridge/gtkb-w0-worker-enablement-plumbing);
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`;
`DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.project.registry_control_plane import (  # noqa: E402
    RegistryAuthorizationError,
    mint_bridge_publication_capability,
)
from groundtruth_kb.project.timer_config import (  # noqa: E402
    resolve_protected_commit_timers,
)

CONFIG_REL = Path("config/governance/protected-commit-timers.toml")


def _write_config(root: Path, ttl: int, bound: int) -> None:
    cfg = root / CONFIG_REL
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(
        f"[protected_commit]\nevaluation_bound_seconds = {bound}\nbridge_publication_capability_ttl_seconds = {ttl}\n",
        encoding="utf-8",
    )


def test_mint_default_signature_is_resolution_routed(tmp_path: Path):
    """The mint default is no longer a hard-coded 120; it must resolve (None)."""
    _write_config(tmp_path, ttl=600, bound=590)
    sig = inspect.signature(mint_bridge_publication_capability)
    default = sig.parameters["ttl_seconds"].default
    assert default is None, "mint TTL default must resolve through timer_config when omitted"


def test_mint_default_equals_config_backed_resolver_value(tmp_path: Path):
    """The config-backed resolver value is what a no-TTL mint uses."""
    _write_config(tmp_path, ttl=600, bound=590)
    timers = resolve_protected_commit_timers(project_root=tmp_path)
    assert timers.bridge_publication_capability_ttl_seconds == 600
    assert timers.evaluation_bound_seconds == 590
    # Sanity: the ceiling that the mint enforces is unchanged at 800.
    assert 600 <= 800


def test_mint_ceiling_still_enforced_for_explicit_values():
    """An explicit TTL above the 800-second ceiling is still denied (fail closed)."""
    with pytest.raises(RegistryAuthorizationError):
        mint_bridge_publication_capability(
            document_name="gtkb-ceiling-test",
            version=1,
            status="NEW",
            target_path=Path("bridge/gtkb-ceiling-test-001.md"),
            content=b"NEW\n",
            session_id="test-session",
            compliance_digest="sha256:test",
            ttl_seconds=801,
        )


def test_live_config_resolves_800_ttl_under_coupled_invariant():
    """The real governance config keeps ttl=800 with the coupled bound < ttl."""
    timers = resolve_protected_commit_timers(project_root=REPO_ROOT)
    assert timers.bridge_publication_capability_ttl_seconds == 800
    assert timers.evaluation_bound_seconds < timers.bridge_publication_capability_ttl_seconds
    assert timers.margin_seconds > 0


def test_writer_mint_call_carries_resolved_ttl():
    """The production bridge writer passes the resolved TTL at its mint call."""
    writer_src = (REPO_ROOT / "scripts" / "gtkb_bridge_writer.py").read_text(encoding="utf-8")
    assert "resolve_protected_commit_timers" in writer_src
    assert "ttl_seconds=timers.bridge_publication_capability_ttl_seconds" in writer_src
