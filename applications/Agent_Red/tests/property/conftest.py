"""Shared Hypothesis settings and strategies for property-based tests (SPEC-1843).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import hypothesis
from hypothesis import strategies as st

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.entitlement_service import TIER_ORDER, _GATE_ALIASES
from src.multi_tenant.schema.models import TierGate

# ---------------------------------------------------------------------------
# Hypothesis profile — keep CI fast, allow deeper local exploration
# ---------------------------------------------------------------------------

hypothesis.settings.register_profile(
    "ci",
    max_examples=50,
    deadline=5000,  # 5s per example
)
hypothesis.settings.register_profile(
    "dev",
    max_examples=200,
    deadline=10000,
)
hypothesis.settings.load_profile("ci")


# ---------------------------------------------------------------------------
# Reusable strategies
# ---------------------------------------------------------------------------

# Canonical tier names
CANONICAL_TIERS = list(TIER_ORDER.keys())  # trial, starter, professional, enterprise
tier_strategy = st.sampled_from(CANONICAL_TIERS)

# Tier names including aliases
ALL_TIER_NAMES = CANONICAL_TIERS + list(_GATE_ALIASES.keys())
tier_or_alias_strategy = st.sampled_from(ALL_TIER_NAMES)

# TenantTier enum values (used by schema validation)
tenant_tier_strategy = st.sampled_from(list(TenantTier))

# TierGate enum values
tier_gate_strategy = st.sampled_from(list(TierGate))

# Hex colors matching the HEX_COLOR_PATTERN
hex_color_strategy = st.from_regex(r"^#[0-9a-fA-F]{6}$", fullmatch=True)

# HTTP status codes
http_status_strategy = st.sampled_from([200, 201, 204, 400, 401, 403, 404, 429, 500, 502, 503])

# HTTP methods
http_method_strategy = st.sampled_from(["GET", "POST", "PUT", "PATCH", "DELETE"])

# Safe strings (no nulls, reasonable length)
safe_string_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"), blacklist_characters="\x00"),
    min_size=1,
    max_size=200,
)

# Tenant ID format
tenant_id_strategy = st.from_regex(r"^[a-z0-9\-]{5,40}$", fullmatch=True)

# API key suffix (last 8 chars)
key_suffix_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    min_size=8,
    max_size=8,
)

# API paths
api_path_strategy = st.sampled_from([
    "/api/chat", "/api/config", "/api/health", "/api/superadmin/tenants",
    "/api/widget/config", "/api/auth/login", "/api/integrations/shopify",
])
