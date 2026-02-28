"""
Source inspection tests -- WI-0771: Customer context pre-computation.

Verifies that:
1. ChatPipeline.warm_up() exists with correct signature
2. warm_up() populates _profile_cache for cache-hit in execute()
3. start_conversation endpoint calls warm_up() fire-and-forget
4. _load_customer_profile checks _profile_cache before Cosmos DB

Run with:
    pytest tests/widget/test_warm_up_call_site.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATOR = ROOT / "src" / "chat" / "pipeline" / "orchestrator.py"
ENDPOINTS = ROOT / "src" / "chat" / "endpoints.py"


def _read(path: Path) -> str:
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


# ===========================================================================
# TestWarmUpMethod — warm_up() exists on ChatPipeline
# ===========================================================================


class TestWarmUpMethod:
    """WI-0771: ChatPipeline.warm_up() pre-fetches customer profile."""

    def test_warm_up_defined(self) -> None:
        source = _read(ORCHESTRATOR)
        assert "async def warm_up(" in source

    def test_warm_up_accepts_tenant_id(self) -> None:
        source = _read(ORCHESTRATOR)
        # Extract the warm_up signature
        match = re.search(r"async def warm_up\([^)]+\)", source, re.DOTALL)
        assert match, "warm_up() method not found"
        sig = match.group(0)
        assert "tenant_id" in sig

    def test_warm_up_accepts_customer_id(self) -> None:
        source = _read(ORCHESTRATOR)
        match = re.search(r"async def warm_up\([^)]+\)", source, re.DOTALL)
        assert match
        sig = match.group(0)
        assert "customer_id" in sig

    def test_warm_up_accepts_tier(self) -> None:
        source = _read(ORCHESTRATOR)
        match = re.search(r"async def warm_up\([^)]+\)", source, re.DOTALL)
        assert match
        sig = match.group(0)
        assert "tier" in sig

    def test_warm_up_populates_profile_cache(self) -> None:
        """warm_up() stores fetched profile in _profile_cache."""
        source = _read(ORCHESTRATOR)
        # Find the warm_up method body
        start = source.index("async def warm_up(")
        # Find the profile cache population line
        cache_write = source.find("self._profile_cache[cache_key] = profile", start)
        # There should be a cache write INSIDE warm_up, before the next method
        next_method = source.find("\n    async def ", start + 1)
        if next_method == -1:
            next_method = source.find("\n    def ", start + 1)
        assert cache_write != -1, "warm_up() does not write to _profile_cache"
        assert cache_write < next_method, "profile_cache write is outside warm_up()"

    def test_warm_up_early_return_on_no_customer(self) -> None:
        """warm_up() returns early if customer_id is None."""
        source = _read(ORCHESTRATOR)
        start = source.index("async def warm_up(")
        body_end = source.find("\n    async def ", start + 1)
        if body_end == -1:
            body_end = source.find("\n    def ", start + 1)
        body = source[start:body_end]
        assert "if not customer_id" in body

    def test_warm_up_checks_cache_before_fetch(self) -> None:
        """warm_up() skips fetch if profile already cached."""
        source = _read(ORCHESTRATOR)
        start = source.index("async def warm_up(")
        body_end = source.find("\n    async def ", start + 1)
        if body_end == -1:
            body_end = source.find("\n    def ", start + 1)
        body = source[start:body_end]
        assert "if cache_key in self._profile_cache" in body

    def test_warm_up_is_fire_and_forget(self) -> None:
        """warm_up() catches all exceptions (fire-and-forget safe)."""
        source = _read(ORCHESTRATOR)
        start = source.index("async def warm_up(")
        body_end = source.find("\n    async def ", start + 1)
        if body_end == -1:
            body_end = source.find("\n    def ", start + 1)
        body = source[start:body_end]
        assert "except Exception" in body


# ===========================================================================
# TestWarmUpCallSite — start_conversation fires warm_up()
# ===========================================================================


class TestWarmUpCallSite:
    """WI-0771: start_conversation endpoint fires warm_up() as background task."""

    def test_start_conversation_calls_warm_up(self) -> None:
        """The start_conversation endpoint contains a warm_up() call."""
        source = _read(ENDPOINTS)
        assert "warm_up(" in source

    def test_warm_up_uses_asyncio_create_task(self) -> None:
        """warm_up() is invoked via asyncio.create_task (fire-and-forget)."""
        source = _read(ENDPOINTS)
        assert "asyncio.create_task" in source
        # The create_task should contain warm_up
        match = re.search(r"asyncio\.create_task\(\s*\n?\s*pipeline\.warm_up\(", source)
        assert match, "asyncio.create_task should wrap pipeline.warm_up()"

    def test_warm_up_passes_tenant_id(self) -> None:
        """The warm_up call passes ctx.tenant_id."""
        source = _read(ENDPOINTS)
        # Find the warm_up call and check it passes tenant_id
        match = re.search(r"pipeline\.warm_up\(ctx\.tenant_id", source)
        assert match, "warm_up() must receive ctx.tenant_id"

    def test_warm_up_passes_customer_id(self) -> None:
        """The warm_up call passes the resolved customer_id."""
        source = _read(ENDPOINTS)
        assert "customer_id_for_warmup" in source

    def test_warm_up_guarded_by_customer_id_check(self) -> None:
        """warm_up is only called when customer_id is available."""
        source = _read(ENDPOINTS)
        assert "if customer_id_for_warmup" in source

    def test_warm_up_in_try_except(self) -> None:
        """warm_up call is wrapped in try/except for fault tolerance."""
        source = _read(ENDPOINTS)
        # Find the WI-0771 section — use 800 chars to include the full block
        start = source.index("WI-0771")
        section = source[start:start + 800]
        assert "try:" in section
        assert "except" in section

    def test_wi_0771_comment_present(self) -> None:
        """The implementation is tagged with WI-0771 for traceability."""
        source = _read(ENDPOINTS)
        assert "WI-0771" in source


# ===========================================================================
# TestProfileCacheIntegration — _load_customer_profile uses cache
# ===========================================================================


class TestProfileCacheIntegration:
    """WI-0771: _load_customer_profile checks cache before Cosmos DB fetch."""

    def test_load_profile_checks_cache(self) -> None:
        """_load_customer_profile checks _profile_cache before fetching."""
        source = _read(ORCHESTRATOR)
        start = source.index("async def _load_customer_profile(")
        body_end = source.find("\n    async def ", start + 1)
        if body_end == -1:
            body_end = source.find("\n    def ", start + 1)
        body = source[start:body_end]
        assert "cache_key in self._profile_cache" in body

    def test_cache_key_format(self) -> None:
        """Cache key is tenant_id:customer_id (same in warm_up and _load)."""
        source = _read(ORCHESTRATOR)
        # Both warm_up and _load_customer_profile use the same cache key format
        keys = re.findall(r'cache_key\s*=\s*f"([^"]+)"', source)
        assert len(keys) >= 2, f"Expected ≥2 cache_key definitions, found {len(keys)}"
        # All cache keys should use the same format
        assert all(k == keys[0] for k in keys), (
            f"Cache key formats differ: {keys}"
        )

    def test_invalidate_profile_cache_exists(self) -> None:
        """invalidate_profile_cache() method exists for mid-conversation re-fetch."""
        source = _read(ORCHESTRATOR)
        assert "def invalidate_profile_cache(" in source
