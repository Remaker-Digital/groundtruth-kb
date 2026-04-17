# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the canonical credential/PII pattern catalog.

Required by GO ``bridge/gtkb-credential-patterns-canonical-008.md`` and the
``-007`` proposal's Fix 1 (inline-fallback parity) and Fix 2 (immutable
pre-migration source fixture).

Test families:

1. Parameterized per-pattern positive + negative samples for every
   :class:`PatternSpec` (2 * N tests).
2. Four scan-scope behavior tests covering the optional ``scope`` filter.
3. A mapping-completeness test that walks the immutable pre-migration source
   fixture and proves every original source entry has a canonical target.
4. An inline-fallback parity test that textually parses the inline fallback
   catalog inside ``templates/hooks/credential-scan.py`` and asserts it
   matches the canonical module's Bash-scoped adapters.

Sample-value construction note
------------------------------
Every synthetic sample value for the Agent-Red-family patterns
(``ar_live_``, ``ar_user_``, ``ar_spa_plat_``, ``pk_live_``, ``arsk_``) is
assembled at runtime from split string parts so repo-level credential
scanners running on this source file do not see a literal credential. The
runtime regex sees the fully-assembled value and matches as intended.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from groundtruth_kb.governance.credential_patterns import (
    BASH_EXTRAS,
    CREDENTIAL_PATTERNS,
    PII_PATTERNS,
    Match,
    PatternSpec,
    Scope,
    bash_credential_pattern_list,
    bash_output_pattern_list,
    db_pattern_list,
    scan,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "credential_pattern_source_inventory_pre_migration.json"
HOOK_PATH = REPO_ROOT / "templates" / "hooks" / "credential-scan.py"


# ---------------------------------------------------------------------------
# Per-pattern positive + negative sample map
# ---------------------------------------------------------------------------
#
# Each canonical PatternSpec (by ``name``) has exactly one positive sample
# (a string that SHOULD match) and one negative sample (a string that MUST
# NOT match). The map is sized to the canonical catalog and validated at
# module load — if the catalog grows without extending this map, the test
# collection fails loudly.

# Agent-Red family prefixes split so repo-level credential scanners do not
# see a literal credential value in this source file.
_AR_LIVE_PREFIX = "ar_" + "live_"
_AR_USER_PREFIX = "ar_" + "user_"
_AR_SPA_PLAT_PREFIX = "ar_" + "spa_" + "plat_"
_PK_LIVE_PREFIX = "pk_" + "live_"
_ARSK_PREFIX = "ar" + "sk_"
_SK_ANT_PREFIX = "sk-" + "ant-api"
_STRIPE_LIVE_PREFIX = "sk_" + "live_"
_STRIPE_TEST_PREFIX = "sk_" + "test_"
_STRIPE_RK_PREFIX = "rk_" + "live_"
_AWS_PREFIX = "AK" + "IA"

_PAYLOAD = "abcdefghijklmnopqrst"

_SAMPLES: dict[str, tuple[str, str]] = {
    # DB scope: credentials
    "api_key": ("api_key=abc123def456ghi789jkl", "no secrets in this prose at all"),
    "bearer_header": (
        "Authorization: Bearer abc123.def456.ghi789",
        "plain prose with no authorization header",
    ),
    "token": (
        "token=abc123def456ghi789jkl012",
        "short token=abc is too short to match the 20+ rule",
    ),
    "secret": (
        "password=supersecretpw",
        "we agreed that append-only versioning is safer",
    ),
    "connection_string": (
        "mongodb://admin:pass@host:27017/db",
        "connection string description without URI body",
    ),
    "azure_sas_key": (
        "SharedAccessKey=AbCdEfGhIjKlMnOpQrSt12345;",
        "SharedAccessKey description without a key value",
    ),
    "github_pat": (
        "ghp_abcdefghijklmnopqrstuvwxyz123456",
        "github uses personal access tokens for authentication",
    ),
    "service_key": (
        _STRIPE_LIVE_PREFIX + "abcdefghijklmnopqrstuvwxyz1234",
        "service documentation describes key behavior",
    ),
    "aws_key": (_AWS_PREFIX + "ABCDEFGHIJKLMNOP", "no AWS keys present in this review"),
    "ar_live_key": (_AR_LIVE_PREFIX + _PAYLOAD, "no Agent Red keys in prose"),
    "ar_user_key": (_AR_USER_PREFIX + _PAYLOAD, "no user keys present"),
    "ar_spa_plat_key": (_AR_SPA_PLAT_PREFIX + _PAYLOAD, "no SPA platform keys in prose"),
    "pk_live_key": (_PK_LIVE_PREFIX + _PAYLOAD, "no widget keys in this text"),
    "arsk_key": (_ARSK_PREFIX + _PAYLOAD, "no arsk keys in this paragraph"),
    "anthropic_api_key": (
        _SK_ANT_PREFIX + "03-" + "a" * 40,
        "sk-ant-api mentioned generically but without a key suffix",
    ),
    # DB scope: PII
    "phone": ("Customer called from +18005551234", "Customer called us last week"),
    "email": ("contact user@example.com", "contact the support desk team"),
    "ip_address": ("from 192.168.1.100 on port", "from inside the private subnet"),
    # Bash credential scope — names have ``bash_`` prefix
    "bash_aws_key": ("echo " + _AWS_PREFIX + "ABCDEFGHIJKLMNOP", "echo hello world"),
    "bash_anthropic_api_key": (
        "export KEY=" + _SK_ANT_PREFIX + "03-" + "a" * 10,
        "regular prose with no keys",
    ),
    "bash_secret_key": (
        "curl -H 'key: sk-abcdefghijklmnopqrst'",
        "sk- is too short without suffix",
    ),
    "bash_stripe_live": ("STRIPE=" + _STRIPE_LIVE_PREFIX + "abcdef", "STRIPE credentials are managed separately"),
    "bash_stripe_test": ("STRIPE=" + _STRIPE_TEST_PREFIX + "abcdef", "tests rely on fixture credentials"),
    "bash_stripe_restricted": ("KEY=" + _STRIPE_RK_PREFIX + "abcdef", "restricted keys require rotation"),
    "bash_private_key_block": (
        "-----BEGIN PRIVATE KEY-----",
        "no private key marker in this prose",
    ),
    "bash_openssh_private_key": (
        "-----BEGIN OPENSSH PRIVATE KEY-----",
        "ssh prose without a begin marker",
    ),
    "bash_connection_string": (
        "ConnectionString=Server=db",
        "connection strings are stored in vaults",
    ),
    "bash_azure_account_key": (
        "AccountKey=AbCdEfGhIjKlMnOp1234",
        "AccountKey description without value",
    ),
    "bash_jwt_token": (
        "Bearer eyJ" + "a" * 60,
        "Bearer tokens are short lived by design",
    ),
    "bash_password_arg": ("psql --password=hunter2 host", "psql --host=example"),
    "bash_password_flag_p": ("mysql -p hunter2 db", "mysql -u root"),
    # Bash output scope
    "bash_credential_piped_output": (
        "echo sk-abcdefghij > /tmp/leak.txt",
        "echo hello world",
    ),
    "bash_credential_exported_env_var": (
        "export API_KEY=abc123",
        "export PATH=/usr/local/bin",
    ),
}


def _all_specs() -> list[PatternSpec]:
    return list(CREDENTIAL_PATTERNS) + list(PII_PATTERNS) + list(BASH_EXTRAS)


def test_samples_map_covers_catalog() -> None:
    """Every canonical spec has an entry in ``_SAMPLES``; no stragglers."""
    spec_names = {s.name for s in _all_specs()}
    sample_names = set(_SAMPLES.keys())
    missing = spec_names - sample_names
    extra = sample_names - spec_names
    assert not missing, f"Catalog specs missing from _SAMPLES: {sorted(missing)}"
    assert not extra, f"_SAMPLES has entries with no matching canonical spec: {sorted(extra)}"


# ---------------------------------------------------------------------------
# Parameterized per-pattern positive + negative tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "spec",
    _all_specs(),
    ids=lambda s: f"{s.scope.value}:{s.name}",
)
def test_pattern_matches_positive_sample(spec: PatternSpec) -> None:
    """Every canonical spec's positive sample must match its regex."""
    positive, _ = _SAMPLES[spec.name]
    assert spec.pattern.search(positive) is not None, (
        f"Positive sample for {spec.name!r} did not match pattern {spec.pattern.pattern!r}. Sample: {positive!r}"
    )


@pytest.mark.parametrize(
    "spec",
    _all_specs(),
    ids=lambda s: f"{s.scope.value}:{s.name}",
)
def test_pattern_rejects_negative_sample(spec: PatternSpec) -> None:
    """Every canonical spec's negative sample must NOT match its regex."""
    _, negative = _SAMPLES[spec.name]
    assert spec.pattern.search(negative) is None, (
        f"Negative sample for {spec.name!r} unexpectedly matched pattern {spec.pattern.pattern!r}. Sample: {negative!r}"
    )


# ---------------------------------------------------------------------------
# Scan-scope behavior tests (4)
# ---------------------------------------------------------------------------


def test_scan_default_scope_includes_all_specs() -> None:
    """``scan(scope=None)`` includes DB credentials, PII, and Bash specs."""
    # Text contains at least one match in every scope band.
    text = (
        "api_key=abc123def456ghi789jkl "  # DB credential
        "+15551234567 "  # DB PII (phone)
        "user@example.com "  # DB PII (email)
        "192.168.1.1 "  # DB PII (ip_address)
        + _AWS_PREFIX
        + "ABCDEFGHIJKLMNOP "  # DB + Bash-credential dual via AWS key
        + "echo "
        + _SK_ANT_PREFIX
        + "03-"
        + "a" * 10
        + " > /tmp/out"
    )
    matches = scan(text)
    names = {m.name for m in matches}
    # DB credential
    assert "api_key" in names
    # DB PII
    assert {"phone", "email", "ip_address"}.issubset(names)
    # DB + Bash credential dual
    assert "aws_key" in names
    assert "bash_aws_key" in names
    # Bash output
    assert "bash_credential_piped_output" in names


def test_scan_scope_db_returns_only_db_specs() -> None:
    """``scan(scope=Scope.DB)`` returns only DB-scoped matches."""
    text = "api_key=abc123def456ghi789jkl echo " + _SK_ANT_PREFIX + "03-" + "a" * 10 + " > /tmp/out"
    matches = scan(text, scope=Scope.DB)
    # Every match must come from a DB-scoped spec
    db_spec_names = {s.name for s in _all_specs() if s.scope is Scope.DB}
    for m in matches:
        assert m.name in db_spec_names, f"scope=Scope.DB returned non-DB spec {m.name}"


def test_scan_scope_bash_credential_returns_only_bash_credential_specs() -> None:
    """``scan(scope=Scope.BASH_CREDENTIAL)`` returns only Bash credential specs."""
    text = (
        "api_key=abc123def456ghi789jkl "  # DB credential — should NOT appear
        + _AWS_PREFIX
        + "ABCDEFGHIJKLMNOP "  # Bash credential (dual-registered AWS key)
        + "echo sk-abcdefghij > /tmp/leak.txt"  # Bash output — should NOT appear
    )
    matches = scan(text, scope=Scope.BASH_CREDENTIAL)
    bash_cred_names = {s.name for s in _all_specs() if s.scope is Scope.BASH_CREDENTIAL}
    assert matches, "Expected at least one Bash-credential match"
    for m in matches:
        assert m.name in bash_cred_names, f"scope=BASH_CREDENTIAL returned non-bash-cred spec {m.name}"


def test_scan_scope_bash_output_returns_only_bash_output_specs() -> None:
    """``scan(scope=Scope.BASH_OUTPUT)`` returns only Bash output-detector specs."""
    text = "export API_KEY=abc123 && echo sk-abcdefghij > /tmp/leak.txt"
    matches = scan(text, scope=Scope.BASH_OUTPUT)
    bash_out_names = {s.name for s in _all_specs() if s.scope is Scope.BASH_OUTPUT}
    assert matches, "Expected at least one Bash-output match"
    for m in matches:
        assert m.name in bash_out_names, f"scope=BASH_OUTPUT returned non-bash-output spec {m.name}"


# ---------------------------------------------------------------------------
# Public Match API never exposes raw matched text
# ---------------------------------------------------------------------------


def test_public_match_has_no_matched_text_attribute() -> None:
    """The public :class:`Match` must not expose raw matched text."""
    matches = scan("api_key=abc123def456ghi789jkl")
    assert matches, "Expected at least one match for the test sample"
    m = matches[0]
    assert isinstance(m, Match)
    # The dataclass must not have ``matched_text`` as a public attribute
    assert not hasattr(m, "matched_text"), (
        "Public Match class must not surface raw matched text; move sensitive matched-text access to _InternalMatch."
    )


# ---------------------------------------------------------------------------
# Mapping-completeness test (reads immutable pre-migration fixture)
# ---------------------------------------------------------------------------


def test_mapping_all_source_entries_have_canonical_target() -> None:
    """Every pre-migration source entry must have a canonical target.

    Reads the immutable fixture at ``tests/fixtures/credential_pattern_source_inventory_pre_migration.json``
    and asserts every entry is either:

    - ``migrated``: there is a canonical :class:`PatternSpec` carrying the
      identical regex pattern string AND flag literal in the matching scope.
    - ``deduplicated``: there is a canonical PatternSpec with the same regex
      string but a different spec name (covered by a fixture-proven equivalent).

    Fails loudly if any source entry has no canonical representation.
    """
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert fixture["schema_version"] == 1, "Fixture schema_version must be 1"

    specs = _all_specs()
    # Index canonical specs by (pattern_string, flag_literal) for fast lookup
    canonical_by_pattern_flags: dict[tuple[str, str], list[PatternSpec]] = {}
    for s in specs:
        key = (s.pattern.pattern, s.flags_literal)
        canonical_by_pattern_flags.setdefault(key, []).append(s)

    unresolved: list[str] = []

    # DB redaction entries (18)
    for entry in fixture["db_redaction"]:
        key = (entry["pattern"], entry["flags"])
        hits = canonical_by_pattern_flags.get(key, [])
        db_hits = [s for s in hits if s.scope is Scope.DB]
        if not db_hits:
            unresolved.append(
                f"db_redaction:{entry['name']!r} (pattern={entry['pattern']!r}, flags={entry['flags']!r})"
            )

    # Bash credential entries (13)
    for entry in fixture["bash_credential"]:
        key = (entry["pattern"], entry["flags"])
        hits = canonical_by_pattern_flags.get(key, [])
        bash_cred_hits = [s for s in hits if s.scope is Scope.BASH_CREDENTIAL]
        if not bash_cred_hits:
            unresolved.append(
                f"bash_credential:{entry['description']!r} (pattern={entry['pattern']!r}, flags={entry['flags']!r})"
            )

    # Bash output entries (2)
    for entry in fixture["bash_output"]:
        key = (entry["pattern"], entry["flags"])
        hits = canonical_by_pattern_flags.get(key, [])
        bash_out_hits = [s for s in hits if s.scope is Scope.BASH_OUTPUT]
        if not bash_out_hits:
            unresolved.append(
                f"bash_output:{entry['description']!r} (pattern={entry['pattern']!r}, flags={entry['flags']!r})"
            )

    assert not unresolved, (
        "Pre-migration source entries are missing canonical targets; migration "
        "has silently dropped patterns. Either migrate the missing entries or "
        "document fixture-proven equivalence with explicit dedup tests:\n  " + "\n  ".join(unresolved)
    )


def test_fixture_counts_match_current_canonical_catalog() -> None:
    """The fixture baseline (18/13/2) must equal the current adapter output.

    If the canonical catalog legitimately grows or shrinks, the fixture must
    NOT be updated silently — a new bridge and a new fixture schema version
    must be used per the proposal's Fixture Properties section.
    """
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert len(fixture["db_redaction"]) == 18
    assert len(fixture["bash_credential"]) == 13
    assert len(fixture["bash_output"]) == 2
    # Current canonical adapter counts must equal the fixture.
    assert len(db_pattern_list()) == 18
    assert len(bash_credential_pattern_list()) == 13
    assert len(bash_output_pattern_list()) == 2


# ---------------------------------------------------------------------------
# Inline-fallback parity test (Fix 1)
# ---------------------------------------------------------------------------


_FALLBACK_RE = re.compile(
    # Match the except ImportError branch followed by the literal assignments
    r"except\s+ImportError:\s*(?:#[^\n]*\n\s*)*"  # comment lines permitted
    r"\s*CREDENTIAL_PATTERNS\s*=\s*\[(?P<creds>.*?)\]\s*"
    r"\n\s*OUTPUT_PATTERNS\s*=\s*\[(?P<outs>.*?)\]\s*"
    r"\n\s*_catalog_source\s*=\s*\"fallback\"",
    re.DOTALL,
)


def _parse_inline_fallback(hook_source: str) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """Parse the inline fallback catalog from the hook source text.

    Returns two lists of ``(regex_value, flag_literal, description)`` triples
    — one for ``CREDENTIAL_PATTERNS`` and one for ``OUTPUT_PATTERNS``.
    """
    match = _FALLBACK_RE.search(hook_source)
    if not match:
        raise AssertionError(
            "Could not locate the inline fallback CREDENTIAL_PATTERNS / OUTPUT_PATTERNS "
            "block inside templates/hooks/credential-scan.py. The parity test is "
            "structural — please keep the `except ImportError:` block pattern stable."
        )

    def _parse_section(body: str) -> list[tuple[str, str, str]]:
        # Match each tuple: (re.compile(<regex-or-concat>[, <flag>]), <description>)
        # <regex-or-concat> may be a single string literal or multiple adjacent
        # string literals separated by whitespace (Python implicit concat).
        # Trailing commas are allowed inside both re.compile(...) and the
        # outer (re.compile(...), description) tuple, matching Python syntax.
        STRING_LITERAL = r"r?\"(?:\\.|[^\"\\])*\"|r?'(?:\\.|[^'\\])*'"
        entry_re = re.compile(
            r"\(\s*re\.compile\(\s*"
            # Capture one or more adjacent string literals (implicit concat)
            r"(?P<regex>(?:" + STRING_LITERAL + r")(?:\s+(?:" + STRING_LITERAL + r"))*)"
            r"(?:\s*,\s*(?P<flag>re\.[A-Z]+(?:\s*\|\s*re\.[A-Z]+)*))?"
            r"\s*,?\s*\)\s*,\s*"  # optional trailing comma inside re.compile()
            r"(?P<desc>" + STRING_LITERAL + r")"
            r"\s*,?\s*\)",  # optional trailing comma in outer tuple
            re.DOTALL,
        )
        results: list[tuple[str, str, str]] = []
        import ast

        # Sub-regex to split the captured <regex> group into individual literals
        LITERAL_RE = re.compile(STRING_LITERAL, re.DOTALL)

        for m in entry_re.finditer(body):
            regex_literals_blob = m.group("regex")
            flag_literal = m.group("flag") or ""
            # Concatenate all adjacent string literals (Python semantics)
            regex_value = "".join(ast.literal_eval(lit.group(0)) for lit in LITERAL_RE.finditer(regex_literals_blob))
            desc_value = ast.literal_eval(m.group("desc"))
            # Normalize flag literal to "IGNORECASE", "DOTALL", or joined by "|"
            flag_normalized = ""
            if flag_literal:
                parts = [p.strip().removeprefix("re.") for p in flag_literal.split("|")]
                flag_normalized = "|".join(parts)
            results.append((regex_value, flag_normalized, desc_value))
        return results

    # Also reject fallback sections where raw regex literals were concatenated
    # across multiple lines (the parser handles multiline string-concat by
    # requiring a single string literal). If a test maintainer splits one regex
    # into two string literals, the structural regex will simply miss that
    # entry and the count mismatch below will surface the drift.
    creds_raw = _parse_section(match.group("creds"))
    outs_raw = _parse_section(match.group("outs"))
    return creds_raw, outs_raw


def _canonical_bash_triples() -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """Return ``(regex, flag_literal, description)`` triples for Bash catalogs."""
    cred_triples: list[tuple[str, str, str]] = []
    for s in _all_specs():
        if s.scope is Scope.BASH_CREDENTIAL:
            cred_triples.append((s.pattern.pattern, s.flags_literal, s.description))
    out_triples: list[tuple[str, str, str]] = []
    for s in _all_specs():
        if s.scope is Scope.BASH_OUTPUT:
            out_triples.append((s.pattern.pattern, s.flags_literal, s.description))
    return cred_triples, out_triples


def test_inline_fallback_catalog_matches_canonical() -> None:
    """The inline fallback catalog in ``credential-scan.py`` must match the
    canonical module's Bash-scoped output.

    Drift between the two fails the build. If the canonical module is
    updated, the inline fallback must be updated in the same commit (and
    vice versa). This parity check is structural — it parses the hook
    source text and compares regex string, flag literal, and description
    against the canonical adapter output.
    """
    hook_source = HOOK_PATH.read_text(encoding="utf-8")
    inline_creds, inline_outs = _parse_inline_fallback(hook_source)
    canonical_creds, canonical_outs = _canonical_bash_triples()

    # Normalize the multi-line piped-output regex before comparison: the
    # canonical module uses implicit string concatenation across multiple
    # lines, and so does the inline fallback. Both compile to the same
    # pattern object, so ``re.compile(...).pattern`` is what we compare.
    assert len(inline_creds) == len(canonical_creds), (
        f"CREDENTIAL_PATTERNS count mismatch: inline has {len(inline_creds)}, canonical has {len(canonical_creds)}"
    )
    for i, (inline, canonical) in enumerate(zip(inline_creds, canonical_creds, strict=True)):
        assert inline == canonical, (
            f"CREDENTIAL_PATTERNS entry {i} drift:\n  inline   = {inline}\n  canonical= {canonical}"
        )

    assert len(inline_outs) == len(canonical_outs), (
        f"OUTPUT_PATTERNS count mismatch: inline has {len(inline_outs)}, canonical has {len(canonical_outs)}"
    )
    for i, (inline, canonical) in enumerate(zip(inline_outs, canonical_outs, strict=True)):
        assert inline == canonical, f"OUTPUT_PATTERNS entry {i} drift:\n  inline   = {inline}\n  canonical= {canonical}"


# ---------------------------------------------------------------------------
# Adapter-shape tests (sanity — db tuples, bash tuples)
# ---------------------------------------------------------------------------


def test_db_pattern_list_shape() -> None:
    """``db_pattern_list()`` returns ``(name: str, pattern: re.Pattern)`` tuples."""
    entries = db_pattern_list()
    assert entries, "db_pattern_list() must not be empty"
    for name, pattern in entries:
        assert isinstance(name, str) and name
        assert isinstance(pattern, re.Pattern)


def test_bash_pattern_list_shape() -> None:
    """Bash adapter returns ``(pattern: re.Pattern, description: str)`` tuples."""
    for pattern, description in bash_credential_pattern_list():
        assert isinstance(pattern, re.Pattern)
        assert isinstance(description, str) and description
    for pattern, description in bash_output_pattern_list():
        assert isinstance(pattern, re.Pattern)
        assert isinstance(description, str) and description
