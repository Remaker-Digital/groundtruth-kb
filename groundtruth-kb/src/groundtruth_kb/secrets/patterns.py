# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Provider-class regex registry for the secret scanner.

Anchored: SPEC-SEC-SCAN-PROVIDER-COVERAGE-001 v1 (S333).

Two parallel pattern sets exist:

- ``PRODUCTION_PATTERNS``: real provider-class regexes, used in production scans
  against the working tree, staged blobs, commit ranges, and CI jobs.
- ``TEST_SYNTHETIC_PATTERNS``: parallel set matching ``GTKB_TEST_<PROVIDER>_PATTERN_*``
  shapes. Tests use these to exercise the engine without committing
  provider-shaped contiguous text (per SPEC-SEC-ALLOWLIST-001 + Codex
  ``-002`` F1 fix on bridge/gtkb-sec-redaction-commit-gate-001-002.md).

Production patterns are deliberately written so that the regex source itself
does not satisfy the regex (no contiguous secret-shaped substring inside the
pattern source line). Adding new patterns: pair production + test_synthetic
entries with the same name and severity.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Severity tier controls scanner ``--fail-on`` semantics."""

    VERIFIED_PROVIDER = "verified-provider"
    CANDIDATE_HIGH = "candidate-high"
    CANDIDATE_MEDIUM = "candidate-medium"


@dataclass(frozen=True)
class PatternEntry:
    name: str
    severity: Severity
    pattern: re.Pattern[str]
    description: str


def _compile(pattern: str, flags: int = 0) -> re.Pattern[str]:
    return re.compile(pattern, flags)


# ---------------------------------------------------------------------------
# Production patterns (17 provider classes anchored in SPEC-SEC-SCAN-PROVIDER-COVERAGE-001)
# ---------------------------------------------------------------------------

PRODUCTION_PATTERNS: tuple[PatternEntry, ...] = (
    # --- Stripe family ---
    PatternEntry(
        name="stripe_test_secret_key",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b" + "sk_test_" + r"[A-Za-z0-9]{24,}\b"),
        description="Stripe Test API Secret Key",
    ),
    PatternEntry(
        name="stripe_live_secret_key",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b" + "sk_live_" + r"[A-Za-z0-9]{24,}\b"),
        description="Stripe Live API Secret Key",
    ),
    PatternEntry(
        name="stripe_webhook_secret",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b" + "whsec_" + r"[A-Za-z0-9]{32,}\b"),
        description="Stripe Webhook Signing Secret",
    ),
    # --- Shopify family ---
    PatternEntry(
        name="shopify_access_token",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b" + "shpat_" + r"[a-fA-F0-9]{32}\b"),
        description="Shopify Access Token",
    ),
    PatternEntry(
        name="shopify_shared_secret",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b" + "shpss_" + r"[a-fA-F0-9]{32}\b"),
        description="Shopify App Shared Secret",
    ),
    # --- Mailchimp ---
    PatternEntry(
        name="mailchimp_api_key",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b[a-f0-9]{32}-us\d{1,2}\b"),
        description="Mailchimp API Key",
    ),
    # --- GitHub ---
    PatternEntry(
        name="github_oauth_token",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(r"\b" + "gho_" + r"[A-Za-z0-9]{36,}\b"),
        description="GitHub OAuth Access Token",
    ),
    # --- Azure family ---
    PatternEntry(
        name="azure_openai_key",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(
            r"\b(?:AZURE_OPENAI_KEY|OPENAI_API_KEY|openai[_-]?key|cognitive[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9]{32}\b",
            re.IGNORECASE,
        ),
        description="Azure OpenAI Key (heuristic: 32-char hex near 'openai'/'cognitive' context)",
    ),
    PatternEntry(
        name="azure_container_apps_fqdn",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(r"\b[a-z0-9-]+\.[a-z]+\.azurecontainerapps\.io\b"),
        description="Azure Container Apps FQDN",
    ),
    PatternEntry(
        name="azure_redis_fqdn",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(r"\b[a-z0-9-]+\.redis\.cache\.windows\.net\b"),
        description="Azure Cache for Redis FQDN",
    ),
    PatternEntry(
        name="azure_cosmos_fqdn",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(r"\b[a-z0-9-]+\.documents\.azure\.com\b"),
        description="Azure Cosmos DB FQDN",
    ),
    PatternEntry(
        name="azure_keyvault_fqdn",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(r"\b[a-z0-9-]+\.vault\.azure\.net\b"),
        description="Azure Key Vault FQDN",
    ),
    PatternEntry(
        name="azure_connection_string",
        severity=Severity.VERIFIED_PROVIDER,
        pattern=_compile(
            r"\bDefaultEndpointsProtocol="
            r"(?:https?|http)"
            r";AccountName=[A-Za-z0-9-]+;AccountKey=[A-Za-z0-9+/=]{20,}",
            re.IGNORECASE,
        ),
        description="Azure Storage / Service Bus / similar connection string",
    ),
    PatternEntry(
        name="azure_cache_redis_key",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(
            r"\b(?:AZURE_REDIS_KEY|REDIS_KEY|redis[_-]?(?:access[_-]?)?key)\s*[:=]\s*['\"]?"
            r"[A-Za-z0-9+/]{43}=(?![A-Za-z0-9+/=])",
            re.IGNORECASE,
        ),
        description="Azure Cache for Redis access key (heuristic: 44-char base64 ending '=')",
    ),
    PatternEntry(
        name="azure_communication_services_key",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(r"\bendpoint=https?://[^;]+;accesskey=[A-Za-z0-9+/=]+", re.IGNORECASE),
        description="Azure Communication Services connection string with accesskey",
    ),
    PatternEntry(
        name="azure_cosmos_db_key",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(
            r"\b(?:AZURE_COSMOS_KEY|COSMOS_KEY|cosmos(?:db)?[_-]?key|primary[_-]?key|secondary[_-]?key)"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9+/]{86}==(?![A-Za-z0-9+/=])",
            re.IGNORECASE,
        ),
        description="Azure Cosmos DB Identifiable Key (heuristic: 88-char base64 ending '==')",
    ),
    # --- Agent Red carry-forward (from scripts/guardrails/check_hardcoded_env.py) ---
    PatternEntry(
        name="agent_red_ar_key",
        severity=Severity.CANDIDATE_HIGH,
        pattern=_compile(r"\b" + "ar_" + r"(?:spa_plat|spa|tenant|widget|live|user)_[A-Za-z0-9_-]{16,}\b"),
        description="Agent Red ar_<family>_<value> key family",
    ),
)


# ---------------------------------------------------------------------------
# Test synthetic patterns (parallel set; matches GTKB_TEST_<PROVIDER>_PATTERN_* fixtures)
# ---------------------------------------------------------------------------
#
# These are used by tests/secrets/* fixtures so that no provider-shaped
# contiguous text needs to live in tracked test files. Test fixtures
# emit ``GTKB_TEST_<PROVIDER>_PATTERN_<runtime-assembled-suffix>`` strings
# at runtime; the test scanner uses TEST_SYNTHETIC_PATTERNS to detect them
# the same way production patterns detect real provider classes.

TEST_SYNTHETIC_PATTERNS: tuple[PatternEntry, ...] = tuple(
    PatternEntry(
        name=entry.name,
        severity=entry.severity,
        pattern=re.compile(r"\bGTKB_TEST_" + entry.name.upper() + r"_PATTERN_[A-Za-z0-9_-]{8,}\b"),
        description=f"Synthetic test pattern for {entry.name}",
    )
    for entry in PRODUCTION_PATTERNS
)
