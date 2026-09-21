"""Fresh native startup context must not read or write retired startup caches."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The artifact family the disclosure cache used. Split so this file does not
# itself match the census it runs.
_CACHE_STEM = "last-user-visible" + "-startup"

# These are the current CLI and native-service producers of session context.
_PRODUCER_PATHS = (
    "groundtruth-kb/src/groundtruth_kb/cli_authority.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/native.py",
)


def test_no_producer_names_the_disclosure_cache() -> None:
    """No producer surface reads, writes or names the disclosure cache."""
    offenders: list[str] = []
    for rel in _PRODUCER_PATHS:
        path = PROJECT_ROOT / rel
        assert path.is_file(), f"native context producer missing: {rel}"
        if _CACHE_STEM in path.read_text(encoding="utf-8"):
            offenders.append(rel)
    assert offenders == [], f"producers still reference the disclosure cache: {offenders}"


def test_the_deleted_cache_bootstrapper_stays_deleted() -> None:
    """The projection-to-projection cache seeder must not return.

    It copied a cached disclosure out of one harness projection into another,
    wrote a forbidden state path, hardcoded vendor names, and asserted role
    authority from cache metadata.
    """
    assert not (PROJECT_ROOT / "scripts" / "_bootstrap_cursor_startup_cache.py").exists()


def test_no_producer_writes_the_packet_cache() -> None:
    """The session-packet cache under the forbidden state directory is gone."""
    offenders: list[str] = []
    for rel in _PRODUCER_PATHS:
        path = PROJECT_ROOT / rel
        assert path.is_file(), f"native context producer missing: {rel}"
        if "session-envelope/packet-cache" in path.read_text(encoding="utf-8"):
            offenders.append(rel)
    assert offenders == [], f"producers still reference the packet cache: {offenders}"
