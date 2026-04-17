# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Canonical credential/PII pattern catalog.

This module is the single source of truth for credential and PII patterns used
by two consumers:

1. ``KnowledgeDB._REDACTION_PATTERNS`` in ``src/groundtruth_kb/db.py``,
   applied to stored deliberation content via ``redact_content()``.
2. ``CREDENTIAL_PATTERNS`` / ``OUTPUT_PATTERNS`` in
   ``templates/hooks/credential-scan.py``, applied to staged Bash command
   payloads by the ``credential-scan`` PreToolUse hook.

Each :class:`PatternSpec` carries a single :class:`Scope`. Patterns that apply
to more than one consumer appear as duplicate specs — once per scope — so
each adapter function returns a deterministic, ordered catalog without filter
overhead at call time.

Design notes
------------
- Public ``Match`` exposes only ``name``, ``description``, and ``span``; it
  never surfaces the raw matched text. Internal code that needs the matched
  text uses the private ``_InternalMatch``.
- There is deliberately no ``Scope.ALL`` value (rejected in
  ``bridge/gtkb-credential-patterns-canonical-004.md``). Pattern applicability
  and scan-filter are kept as separate concepts — ``scan(scope=None)`` scans
  everything while an explicit ``scope`` narrows the view.
- The Bash hook inline fallback in ``templates/hooks/credential-scan.py`` is
  a mirrored copy kept in sync by the ``test_inline_fallback_catalog_matches_canonical``
  parity test in ``tests/test_credential_patterns.py``.

See ``bridge/gtkb-credential-patterns-canonical-007.md`` for the approved
proposal and ``-008`` for the Codex GO with the six implementation conditions
this module satisfies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Scope(Enum):
    """Consumer scope for a pattern spec.

    - ``DB``: applied by ``KnowledgeDB.redact_content()`` on stored text.
    - ``BASH_CREDENTIAL``: applied by the ``credential-scan`` hook as a
      credential-value detector on staged Bash commands.
    - ``BASH_OUTPUT``: applied by the ``credential-scan`` hook as an output
      detector (e.g. piping/redirecting or ``export`` of a literal credential).
    """

    DB = "db"
    BASH_CREDENTIAL = "bash_credential"
    BASH_OUTPUT = "bash_output"


@dataclass(frozen=True)
class PatternSpec:
    """Single credential or PII pattern entry.

    Attributes
    ----------
    name:
        Short snake_case identifier. For DB scope this is the label written
        into ``[REDACTED:<name>]`` markers and into
        ``redaction_notes``. For Bash scope the ``description`` is the
        human-readable reason shown to the operator; ``name`` stays stable
        across scopes for cross-reference.
    pattern:
        Pre-compiled regex. Must be compiled at module import time so consumer
        hot paths never re-compile.
    description:
        Human-readable explanation of what the pattern detects. Used as the
        second element of the Bash hook's ``(pattern, description)`` tuples
        and shown in ``Match.description``.
    scope:
        Which single consumer this spec applies to. Patterns that apply to
        more than one consumer appear multiple times in ``CREDENTIAL_PATTERNS``
        / ``PII_PATTERNS`` / ``BASH_EXTRAS`` — once per scope.
    flags_literal:
        Human-readable flag suffix used when serializing specs into the
        fixture (``"IGNORECASE"``, ``"DOTALL"``, or ``""``). Kept explicit so
        the immutable fixture inventory is trivially comparable without
        inspecting ``re.Pattern`` flag bitmasks.
    """

    name: str
    pattern: re.Pattern[str]
    description: str
    scope: Scope
    flags_literal: str


@dataclass(frozen=True)
class Match:
    """Public scan match result. Never includes the raw matched text."""

    name: str
    description: str
    span: tuple[int, int]


@dataclass(frozen=True)
class _InternalMatch:
    """Internal-only match record that retains the raw matched text.

    Used by code paths that genuinely need the matched value (for example
    ``redact_content()`` uses ``re.sub`` rather than match metadata, but code
    that wishes to inspect the matched segment can do so privately).
    """

    name: str
    description: str
    span: tuple[int, int]
    matched_text: str


# ---------------------------------------------------------------------------
# Credential patterns
# ---------------------------------------------------------------------------
#
# Ordering matters for first-match semantics in the Bash hook's
# ``_check_command()`` helper. Bash-scoped entries preserve the original
# order from ``templates/hooks/credential-scan.py``.
#
# DB-scoped entries preserve the original order from
# ``src/groundtruth_kb/db.py:_REDACTION_PATTERNS``; ``redact_content()`` walks
# the list in order and substitutes each hit in sequence.

CREDENTIAL_PATTERNS: list[PatternSpec] = [
    # ------------------------------------------------------------------
    # DB scope (15 credential entries, preserving the order in db.py)
    # ------------------------------------------------------------------
    PatternSpec(
        name="api_key",
        pattern=re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w\-]{16,}['\"]?", re.IGNORECASE),
        description="Generic api_key/apikey assignment",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="bearer_header",
        pattern=re.compile(r"(?:Authorization\s*:\s*)?Bearer\s+[\w\-\.~+/]+=*", re.IGNORECASE),
        description="Authorization: Bearer <token> or standalone Bearer <token>",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="token",
        pattern=re.compile(r"(?:token|bearer)\s*[:=]\s*['\"]?[\w\-\.]{20,}['\"]?", re.IGNORECASE),
        description="token=/token: or bearer=/bearer: explicit assignment",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="secret",
        pattern=re.compile(r"(?:secret|password|passwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?", re.IGNORECASE),
        description="secret/password/passwd assignment",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="connection_string",
        pattern=re.compile(r"(?:mongodb|postgres|mysql|redis|amqp)://[^\s\"']+", re.IGNORECASE),
        description="Database connection string URI",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="azure_sas_key",
        pattern=re.compile(r"SharedAccessKey=[A-Za-z0-9+/=]{20,}(?:;|$)", re.IGNORECASE),
        description="Azure SharedAccessKey connection-string segment",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="github_pat",
        pattern=re.compile(r"(?:ghp|gho|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
        description="GitHub personal-access-token prefixes",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="service_key",
        pattern=re.compile(r"(?:sk|pk)[-_](?:live|test|prod)[-_][A-Za-z0-9]{20,}", re.IGNORECASE),
        description="Generic sk_/pk_ live/test/prod service key",
        scope=Scope.DB,
        flags_literal="IGNORECASE",
    ),
    PatternSpec(
        name="aws_key",
        pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
        description="AWS access key ID (AKIA...)",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="ar_live_key",
        pattern=re.compile(r"\bar_live_[A-Za-z0-9_-]{10,}"),
        description="Agent Red ar_live_ tenant key",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="ar_user_key",
        pattern=re.compile(r"\bar_user_[A-Za-z0-9_-]{10,}"),
        description="Agent Red ar_user_ API key",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="ar_spa_plat_key",
        pattern=re.compile(r"\bar_spa_plat_[A-Za-z0-9_-]{10,}"),
        description="Agent Red ar_spa_plat_ SPA key",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="pk_live_key",
        pattern=re.compile(r"\bpk_live_[A-Za-z0-9_-]{10,}"),
        description="Agent Red pk_live_ widget key",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="arsk_key",
        pattern=re.compile(r"\barsk_[A-Za-z0-9_-]{10,}"),
        description="Agent Red arsk_ service key",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="anthropic_api_key",
        pattern=re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}"),
        description="Anthropic API key (sk-ant-api<version>-<token>)",
        scope=Scope.DB,
        flags_literal="",
    ),
    # ------------------------------------------------------------------
    # Bash credential scope (13 entries, preserving the order in
    # ``templates/hooks/credential-scan.py`` ``CREDENTIAL_PATTERNS``)
    # ------------------------------------------------------------------
    PatternSpec(
        name="bash_aws_key",
        pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
        description="AWS access key ID (AKIA...)",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_anthropic_api_key",
        pattern=re.compile(r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+"),
        description="Anthropic API key (sk-ant-api...)",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_secret_key",
        pattern=re.compile(r"\bsk-[a-zA-Z0-9]{20,}"),
        description="Secret key (sk-...)",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_stripe_live",
        pattern=re.compile(r"\bsk_live_[a-zA-Z0-9]+"),
        description="Stripe live secret key",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_stripe_test",
        pattern=re.compile(r"\bsk_test_[a-zA-Z0-9]+"),
        description="Stripe test secret key",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_stripe_restricted",
        pattern=re.compile(r"\brk_live_[a-zA-Z0-9]+"),
        description="Stripe restricted key",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_private_key_block",
        pattern=re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
        description="Private key block",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_openssh_private_key",
        pattern=re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"),
        description="OpenSSH private key",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_connection_string",
        pattern=re.compile(r"[Cc]onnection[Ss]tring\s*=\s*['\"]?[^\s;]+"),
        description="Connection string assignment",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_azure_account_key",
        pattern=re.compile(r"AccountKey=[a-zA-Z0-9+/=]{20,}"),
        description="Azure Storage account key",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_jwt_token",
        pattern=re.compile(r"\beyJ[a-zA-Z0-9_-]{50,}"),
        description="JWT / bearer token",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_password_arg",
        pattern=re.compile(r"--password\s*[=\s]\s*\S+"),
        description="Password passed as command argument",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
    PatternSpec(
        name="bash_password_flag_p",
        pattern=re.compile(r"-p\s+['\"]?[^\s]+['\"]?\s"),
        description="Possible password flag (-p)",
        scope=Scope.BASH_CREDENTIAL,
        flags_literal="",
    ),
]


# PII-only DB entries (phone, email, ip_address).
PII_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        name="phone",
        pattern=re.compile(r"\+\d{10,15}"),
        description="International phone number",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="email",
        pattern=re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        description="Email address",
        scope=Scope.DB,
        flags_literal="",
    ),
    PatternSpec(
        name="ip_address",
        pattern=re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        description="IPv4 address",
        scope=Scope.DB,
        flags_literal="",
    ),
]


# Bash-only output detectors (piping/redirecting a credential-like value to
# a file or another process, and exporting credentials as env vars).
BASH_EXTRAS: list[PatternSpec] = [
    PatternSpec(
        name="bash_credential_piped_output",
        pattern=re.compile(
            r"(echo|printf|cat)\s+.*"
            r"(AKIA|sk-|sk_live|sk_test|-----BEGIN|[Cc]onnection[Ss]tring|AccountKey)"
            r".*[>|]",
            re.DOTALL,
        ),
        description="Credential value piped or redirected to output",
        scope=Scope.BASH_OUTPUT,
        flags_literal="DOTALL",
    ),
    PatternSpec(
        name="bash_credential_exported_env_var",
        pattern=re.compile(r"(export|set)\s+\w*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)\w*\s*=\s*\S+", re.IGNORECASE),
        description="Credential exported as environment variable with literal value",
        scope=Scope.BASH_OUTPUT,
        flags_literal="IGNORECASE",
    ),
]


# ---------------------------------------------------------------------------
# Adapter functions
# ---------------------------------------------------------------------------


def _all_specs() -> list[PatternSpec]:
    """Return the concatenated catalog in stable order (DB → Bash → extras)."""
    return list(CREDENTIAL_PATTERNS) + list(PII_PATTERNS) + list(BASH_EXTRAS)


def db_pattern_list() -> list[tuple[str, re.Pattern[str]]]:
    """Return ``(name, pattern)`` tuples for every DB-scoped spec.

    Shape matches the historical ``KnowledgeDB._REDACTION_PATTERNS``: a list
    of ``(label, compiled_pattern)`` tuples. Order is preserved so
    ``redact_content()`` continues to apply patterns in the same sequence.
    """
    return [(s.name, s.pattern) for s in _all_specs() if s.scope is Scope.DB]


def bash_credential_pattern_list() -> list[tuple[re.Pattern[str], str]]:
    """Return ``(pattern, description)`` tuples for Bash credential detection.

    Shape matches the historical ``CREDENTIAL_PATTERNS`` in
    ``templates/hooks/credential-scan.py``: a list of
    ``(compiled_pattern, description)`` tuples. Order is preserved so
    ``_check_command()`` first-match semantics are unchanged.
    """
    return [(s.pattern, s.description) for s in _all_specs() if s.scope is Scope.BASH_CREDENTIAL]


def bash_output_pattern_list() -> list[tuple[re.Pattern[str], str]]:
    """Return ``(pattern, description)`` tuples for Bash output detection.

    Shape matches the historical ``OUTPUT_PATTERNS`` in
    ``templates/hooks/credential-scan.py``.
    """
    return [(s.pattern, s.description) for s in _all_specs() if s.scope is Scope.BASH_OUTPUT]


# ---------------------------------------------------------------------------
# Public scan API
# ---------------------------------------------------------------------------


def scan(text: str, scope: Scope | None = None) -> list[Match]:
    """Scan ``text`` and return public :class:`Match` records.

    Parameters
    ----------
    text:
        Input to scan.
    scope:
        Optional filter. ``None`` (the default) scans every spec in the
        catalog. A :class:`Scope` member narrows the scan to specs with that
        exact scope.

    Returns
    -------
    list[Match]
        Matches in the order their source spec appears in the catalog.
        Each :class:`Match` carries ``name``, ``description``, and the
        ``(start, end)`` span. The raw matched text is intentionally omitted
        from the public API; callers who need it must use the private
        ``_InternalMatch`` path.
    """
    specs = _all_specs() if scope is None else [s for s in _all_specs() if s.scope is scope]
    matches: list[Match] = []
    for spec in specs:
        for m in spec.pattern.finditer(text):
            matches.append(
                Match(
                    name=spec.name,
                    description=spec.description,
                    span=(m.start(), m.end()),
                )
            )
    return matches


def _scan_internal(text: str, scope: Scope | None = None) -> list[_InternalMatch]:
    """Internal-only scan that retains the raw matched text.

    Not exposed via the public ``scan()`` API. Reserved for code paths inside
    ``groundtruth_kb`` that need the matched value.
    """
    specs = _all_specs() if scope is None else [s for s in _all_specs() if s.scope is scope]
    matches: list[_InternalMatch] = []
    for spec in specs:
        for m in spec.pattern.finditer(text):
            matches.append(
                _InternalMatch(
                    name=spec.name,
                    description=spec.description,
                    span=(m.start(), m.end()),
                    matched_text=m.group(0),
                )
            )
    return matches


__all__ = [
    "BASH_EXTRAS",
    "CREDENTIAL_PATTERNS",
    "Match",
    "PII_PATTERNS",
    "PatternSpec",
    "Scope",
    "bash_credential_pattern_list",
    "bash_output_pattern_list",
    "db_pattern_list",
    "scan",
]
