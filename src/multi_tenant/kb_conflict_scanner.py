"""Knowledge Base conflict and duplication scanner.

On-demand tool that scans all active knowledge base entries for a tenant
and identifies:

    1. Near-duplicates — same content uploaded twice or chunked redundantly
    2. Conflicting information — same topic, different factual claims
    3. Topical overlap — similar topic coverage that may need merging
    4. Similar titles — titles that suggest duplication despite different content

Algorithm phases:
    Phase 1: Pairwise cosine similarity on existing embeddings
    Phase 2: Title similarity via trigram Jaccard
    Phase 3: Content overlap via sentence-level Jaccard
    Phase 4: Factual conflict detection via regex pattern extraction

No API calls — works entirely with pre-computed embeddings and text
processing. Typical scan for <500 entries completes in <5 seconds.

Architecture references:
    - semantic_cache.py: cosine_similarity() function (reused)
    - repository.py: KnowledgeBaseRepository.list_active()
    - staleness_service.py: singleton service pattern
    - admin_knowledge_api.py: endpoint integration

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Embedding similarity thresholds
NEAR_DUPLICATE_SIMILARITY = 0.92  # Very high — almost identical content
CONFLICT_SIMILARITY = 0.85  # High — same topic, possibly different details

# Title similarity threshold (trigram Jaccard)
TITLE_SIMILARITY_THRESHOLD = 0.6

# Content overlap thresholds (sentence-level Jaccard)
NEAR_DUPLICATE_OVERLAP = 0.70  # >70% = near-duplicate
TOPICAL_OVERLAP_MIN = 0.40  # 40-70% = topical overlap

# Scan result cache TTL (seconds)
SCAN_CACHE_TTL = 300  # 5 minutes

# Large KB optimization threshold
LARGE_KB_THRESHOLD = 200  # Switch to vector-search-per-entry above this

# Max pairs to report (avoid overwhelming the UI)
MAX_CONFLICTS_REPORTED = 100


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ConflictType(str, Enum):
    """Type of knowledge base conflict."""

    NEAR_DUPLICATE = "near_duplicate"
    CONFLICTING = "conflicting"
    TOPICAL_OVERLAP = "topical_overlap"
    SIMILAR_TITLES = "similar_titles"
    CONFIG_VS_KB = "config_vs_kb"


class ConflictSeverity(str, Enum):
    """Severity of a knowledge base conflict."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ConflictPair:
    """A pair of KB entries with a detected conflict."""

    entry_a_id: str
    entry_a_title: str
    entry_b_id: str
    entry_b_title: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    embedding_similarity: float
    content_overlap: float
    title_similarity: float
    conflicting_facts: list[str] = field(default_factory=list)
    resolution: str = ""


@dataclass
class ScanResult:
    """Result of a full KB conflict scan."""

    tenant_id: str
    scanned_at: str
    total_entries_scanned: int
    entries_with_embeddings: int
    entries_without_embeddings: int
    conflicts: list[ConflictPair] = field(default_factory=list)
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    scan_duration_ms: int = 0


@dataclass
class ConfigConflict:
    """A conflict between a tenant config field and a KB article (SPEC-1714)."""

    config_field: str
    config_value: str
    article_id: str
    article_title: str
    conflicting_facts: list[str] = field(default_factory=list)
    resolution: str = ""


@dataclass
class ConfigScanResult:
    """Result of config-vs-KB cross-check scan (SPEC-1714)."""

    tenant_id: str
    scanned_at: str
    config_fields_checked: int
    articles_checked: int
    conflicts: list[ConfigConflict] = field(default_factory=list)
    scan_duration_ms: int = 0


# ---------------------------------------------------------------------------
# Config field descriptors for cross-checking
# ---------------------------------------------------------------------------

# Maps PreferencesDocument field names to human-readable labels and
# topic keywords used to filter relevant KB articles before comparison.
_CONFIG_POLICY_FIELDS: dict[str, dict[str, Any]] = {
    "return_policy": {
        "label": "Return policy",
        "keywords": ["return", "refund", "exchange", "money back"],
    },
    "shipping_info": {
        "label": "Shipping info",
        "keywords": ["shipping", "delivery", "ship", "freight", "postage"],
    },
    "brand_voice": {
        "label": "Brand voice",
        "keywords": ["tone", "voice", "style", "brand"],
    },
}


# ---------------------------------------------------------------------------
# Text processing helpers
# ---------------------------------------------------------------------------

# Regex patterns for factual conflict detection
_DURATION_PATTERN = re.compile(
    r"(\d+)\s*[-–]?\s*(days?|hours?|weeks?|months?|years?|business\s+days?)",
    re.IGNORECASE,
)
_PRICE_PATTERN = re.compile(
    r"\$\s*(\d+(?:\.\d{1,2})?)",
)
_PERCENTAGE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*%",
)
_EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w-]+\.[\w.-]+",
)
_URL_PATTERN = re.compile(
    r"https?://[\w./\-?=&#]+",
    re.IGNORECASE,
)
_BOOLEAN_PHRASES = {
    "free shipping": "shipping cost",
    "no returns": "returns accepted",
    "no refunds": "refunds available",
    "final sale": "returnable",
    "non-refundable": "refundable",
}


def _normalize_title(title: str) -> str:
    """Normalize a title for comparison: lowercase, strip punctuation, collapse whitespace."""
    text = title.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _trigrams(text: str) -> set[str]:
    """Extract character trigrams from text."""
    if len(text) < 3:
        return {text} if text else set()
    return {text[i : i + 3] for i in range(len(text) - 2)}


def _trigram_jaccard(a: str, b: str) -> float:
    """Compute Jaccard similarity on character trigrams of two strings."""
    norm_a = _normalize_title(a)
    norm_b = _normalize_title(b)
    if not norm_a or not norm_b:
        return 0.0
    tri_a = _trigrams(norm_a)
    tri_b = _trigrams(norm_b)
    intersection = len(tri_a & tri_b)
    union = len(tri_a | tri_b)
    return intersection / union if union > 0 else 0.0


def _extract_sentences(text: str) -> set[str]:
    """Split text into normalized sentences for overlap comparison."""
    # Split on sentence boundaries
    raw = re.split(r"[.!?]\s+|\n+", text)
    sentences = set()
    for s in raw:
        normalized = s.strip().lower()
        # Skip very short fragments
        if len(normalized) > 10:
            sentences.add(normalized)
    return sentences


def _sentence_jaccard(a: str, b: str) -> float:
    """Compute Jaccard similarity on sentence sets."""
    sent_a = _extract_sentences(a)
    sent_b = _extract_sentences(b)
    if not sent_a or not sent_b:
        return 0.0
    intersection = len(sent_a & sent_b)
    union = len(sent_a | sent_b)
    return intersection / union if union > 0 else 0.0


def _filter_articles_by_keywords(
    entries: list[dict[str, Any]],
    keywords: list[str],
) -> list[dict[str, Any]]:
    """Filter KB articles to those whose title or content mentions any keyword."""
    relevant: list[dict[str, Any]] = []
    for entry in entries:
        text = (entry.get("title", "") + " " + entry.get("content", "")).lower()
        if any(kw in text for kw in keywords):
            relevant.append(entry)
    return relevant


def _detect_factual_conflicts(content_a: str, content_b: str) -> list[str]:
    """Detect factual contradictions between two articles via regex.

    Returns human-readable descriptions of detected conflicts.
    """
    conflicts: list[str] = []

    # Duration conflicts (e.g., "30 days" vs "14 days")
    durations_a = _DURATION_PATTERN.findall(content_a)
    durations_b = _DURATION_PATTERN.findall(content_b)
    if durations_a and durations_b:
        # Group by unit
        by_unit_a: dict[str, set[str]] = {}
        for val, unit in durations_a:
            unit_key = unit.lower().rstrip("s")
            by_unit_a.setdefault(unit_key, set()).add(val)
        by_unit_b: dict[str, set[str]] = {}
        for val, unit in durations_b:
            unit_key = unit.lower().rstrip("s")
            by_unit_b.setdefault(unit_key, set()).add(val)
        for unit_key in by_unit_a.keys() & by_unit_b.keys():
            vals_a = by_unit_a[unit_key]
            vals_b = by_unit_b[unit_key]
            if vals_a != vals_b:
                conflicts.append(
                    f"Duration ({unit_key}): {', '.join(sorted(vals_a))} vs {', '.join(sorted(vals_b))}"
                )

    # Price conflicts
    prices_a = set(_PRICE_PATTERN.findall(content_a))
    prices_b = set(_PRICE_PATTERN.findall(content_b))
    if prices_a and prices_b and prices_a != prices_b:
        diff_a = prices_a - prices_b
        diff_b = prices_b - prices_a
        if diff_a or diff_b:
            conflicts.append(
                f"Prices differ: ${', $'.join(sorted(prices_a))} vs ${', $'.join(sorted(prices_b))}"
            )

    # Percentage conflicts
    pcts_a = set(_PERCENTAGE_PATTERN.findall(content_a))
    pcts_b = set(_PERCENTAGE_PATTERN.findall(content_b))
    if pcts_a and pcts_b and pcts_a != pcts_b:
        conflicts.append(
            f"Percentages differ: {', '.join(sorted(pcts_a))}% vs {', '.join(sorted(pcts_b))}%"
        )

    # Email conflicts (different contact emails for same topic)
    emails_a = set(_EMAIL_PATTERN.findall(content_a.lower()))
    emails_b = set(_EMAIL_PATTERN.findall(content_b.lower()))
    if emails_a and emails_b and emails_a != emails_b:
        conflicts.append(
            f"Contact emails differ: {', '.join(sorted(emails_a))} vs {', '.join(sorted(emails_b))}"
        )

    # Boolean contradiction detection
    content_a_lower = content_a.lower()
    content_b_lower = content_b.lower()
    for phrase, opposite in _BOOLEAN_PHRASES.items():
        if phrase in content_a_lower and opposite in content_b_lower:
            conflicts.append(f"Contradiction: '{phrase}' vs '{opposite}'")
        elif opposite in content_a_lower and phrase in content_b_lower:
            conflicts.append(f"Contradiction: '{opposite}' vs '{phrase}'")

    return conflicts


# ---------------------------------------------------------------------------
# Resolution text generators
# ---------------------------------------------------------------------------

_RESOLUTION_TEMPLATES: dict[ConflictType, str] = {
    ConflictType.NEAR_DUPLICATE: (
        "These two articles contain nearly identical content. "
        "Merge the best parts into a single article and archive or delete the other. "
        "Keeping both will cause the AI to retrieve redundant context, "
        "wasting the retrieval budget and potentially giving slightly different answers."
    ),
    ConflictType.CONFLICTING: (
        "These articles cover the same topic but contain different factual claims. "
        "Determine which article is authoritative (usually the most recently updated one), "
        "then update the incorrect article to match or archive it. "
        "Conflicting articles cause the AI to give inconsistent or blended answers."
    ),
    ConflictType.TOPICAL_OVERLAP: (
        "These articles cover similar topics and may be intentionally separate "
        "(e.g., general policy vs. international policy). "
        "If they cover the same scope, merge them into one article. "
        "If they cover different aspects, ensure they don't contain contradictory details."
    ),
    ConflictType.SIMILAR_TITLES: (
        "These articles have similar titles, which may confuse the retrieval system "
        "even though their content differs. Consider renaming one to be more specific "
        "about what it covers to improve retrieval accuracy."
    ),
    ConflictType.CONFIG_VS_KB: (
        "A knowledge base article contains information that conflicts with the "
        "merchant's agent configuration. The configuration values are authoritative "
        "(SPEC-1713) and the AI will follow them, but the conflicting KB article "
        "may confuse retrieval results. Update the KB article to match the current "
        "configuration, or remove the conflicting section from the article."
    ),
}


def _generate_resolution(conflict_type: ConflictType, conflicting_facts: list[str]) -> str:
    """Generate resolution guidance for a conflict pair."""
    base = _RESOLUTION_TEMPLATES[conflict_type]
    if conflicting_facts and conflict_type == ConflictType.CONFLICTING:
        facts_str = "; ".join(conflicting_facts[:5])
        base += f"\n\nSpecific conflicts found: {facts_str}"
    return base


# ---------------------------------------------------------------------------
# Scanner service
# ---------------------------------------------------------------------------


class KBConflictScanner:
    """On-demand knowledge base conflict and duplication scanner.

    Scans all active KB entries for a tenant to identify duplicates,
    conflicts, and topical overlaps. Uses pre-computed embeddings —
    no API calls during scan.
    """

    def __init__(self) -> None:
        self._kb_repo: Any = None
        self._configured = False
        self._scan_cache: dict[str, tuple[ScanResult, float]] = {}  # tenant_id -> (result, timestamp)

    def configure(
        self,
        kb_repo: Any,
    ) -> None:
        """Wire the scanner to the KnowledgeBaseRepository.

        Args:
            kb_repo: KnowledgeBaseRepository instance.
        """
        self._kb_repo = kb_repo
        self._configured = True
        logger.info("KB conflict scanner configured")

    def _ensure_configured(self) -> None:
        if not self._configured:
            raise RuntimeError("KB conflict scanner not configured — call configure() first")

    def get_cached_result(self, tenant_id: str) -> ScanResult | None:
        """Return the cached scan result if still valid, else None."""
        if tenant_id not in self._scan_cache:
            return None
        result, cached_at = self._scan_cache[tenant_id]
        if time.time() - cached_at > SCAN_CACHE_TTL:
            del self._scan_cache[tenant_id]
            return None
        return result

    async def scan(
        self,
        tenant_id: str,
        *,
        embedding_threshold: float = CONFLICT_SIMILARITY,
        title_threshold: float = TITLE_SIMILARITY_THRESHOLD,
        force: bool = False,
    ) -> ScanResult:
        """Run a full conflict scan on the tenant's knowledge base.

        Args:
            tenant_id: Tenant partition key.
            embedding_threshold: Minimum cosine similarity to flag (default 0.85).
            title_threshold: Minimum trigram Jaccard for title similarity (default 0.6).
            force: If True, bypass cache.

        Returns:
            ScanResult with all detected conflicts.
        """
        self._ensure_configured()

        # Check cache
        if not force:
            cached = self.get_cached_result(tenant_id)
            if cached is not None:
                return cached

        start_time = time.monotonic()

        # Fetch all active entries (with embeddings)
        entries = await self._kb_repo.list_active(tenant_id=tenant_id)

        total = len(entries)
        with_embeddings = [e for e in entries if e.get("embedding")]
        without_embeddings = [e for e in entries if not e.get("embedding")]

        conflicts: list[ConflictPair] = []
        seen_pairs: set[tuple[str, str]] = set()  # Deduplicate pairs

        # Phase 1: Embedding similarity
        if len(with_embeddings) >= 2:
            embedding_conflicts = self._phase1_embedding_similarity(
                with_embeddings, embedding_threshold, seen_pairs
            )
            conflicts.extend(embedding_conflicts)

        # Phase 2: Title similarity (all entries, not just embedded)
        if total >= 2:
            title_conflicts = self._phase2_title_similarity(
                entries, title_threshold, seen_pairs
            )
            conflicts.extend(title_conflicts)

        # Sort by severity (high first)
        severity_order = {ConflictSeverity.HIGH: 0, ConflictSeverity.MEDIUM: 1, ConflictSeverity.LOW: 2}
        conflicts.sort(key=lambda c: (severity_order.get(c.severity, 99), -c.embedding_similarity))

        # Trim to max
        if len(conflicts) > MAX_CONFLICTS_REPORTED:
            conflicts = conflicts[:MAX_CONFLICTS_REPORTED]

        high = sum(1 for c in conflicts if c.severity == ConflictSeverity.HIGH)
        medium = sum(1 for c in conflicts if c.severity == ConflictSeverity.MEDIUM)
        low = sum(1 for c in conflicts if c.severity == ConflictSeverity.LOW)

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        result = ScanResult(
            tenant_id=tenant_id,
            scanned_at=datetime.now(timezone.utc).isoformat(),
            total_entries_scanned=total,
            entries_with_embeddings=len(with_embeddings),
            entries_without_embeddings=len(without_embeddings),
            conflicts=conflicts,
            high_count=high,
            medium_count=medium,
            low_count=low,
            scan_duration_ms=elapsed_ms,
        )

        # Cache result
        self._scan_cache[tenant_id] = (result, time.time())

        logger.info(
            "KB conflict scan: tenant=%s entries=%d conflicts=%d (high=%d, medium=%d, low=%d) duration=%dms",
            tenant_id[:8],
            total,
            len(conflicts),
            high,
            medium,
            low,
            elapsed_ms,
        )

        return result

    async def scan_config_conflicts(
        self,
        tenant_id: str,
        config_fields: dict[str, str],
    ) -> ConfigScanResult:
        """Cross-check tenant config field values against KB articles (SPEC-1714).

        Compares each non-empty config field (return_policy, shipping_info, etc.)
        against KB articles whose content matches the field's topic keywords.
        Uses the same factual conflict regex patterns as article-vs-article scans.

        Args:
            tenant_id: Tenant partition key.
            config_fields: Dict of field_name -> field_value from PreferencesDocument.
                           Only non-empty string values are checked.

        Returns:
            ConfigScanResult with all detected config-vs-KB conflicts.
        """
        self._ensure_configured()
        start_time = time.monotonic()

        # Filter to non-empty config fields that we know how to check
        fields_to_check: dict[str, str] = {}
        for field_name, value in config_fields.items():
            if value and field_name in _CONFIG_POLICY_FIELDS:
                fields_to_check[field_name] = value

        if not fields_to_check:
            return ConfigScanResult(
                tenant_id=tenant_id,
                scanned_at=datetime.now(timezone.utc).isoformat(),
                config_fields_checked=0,
                articles_checked=0,
                scan_duration_ms=0,
            )

        # Fetch all active KB entries
        entries = await self._kb_repo.list_active(tenant_id=tenant_id)
        conflicts: list[ConfigConflict] = []

        for field_name, config_value in fields_to_check.items():
            field_info = _CONFIG_POLICY_FIELDS[field_name]
            keywords = field_info["keywords"]
            field_info["label"]

            # Filter articles by keyword relevance (title or content)
            relevant_articles = _filter_articles_by_keywords(entries, keywords)

            for article in relevant_articles:
                content = article.get("content", "")
                if not content:
                    continue

                # Run factual conflict detection: config value vs article content
                fact_conflicts = _detect_factual_conflicts(config_value, content)
                if fact_conflicts:
                    conflicts.append(ConfigConflict(
                        config_field=field_name,
                        config_value=config_value,
                        article_id=article["id"],
                        article_title=article.get("title", ""),
                        conflicting_facts=fact_conflicts,
                        resolution=_generate_resolution(
                            ConflictType.CONFIG_VS_KB, fact_conflicts
                        ),
                    ))

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        result = ConfigScanResult(
            tenant_id=tenant_id,
            scanned_at=datetime.now(timezone.utc).isoformat(),
            config_fields_checked=len(fields_to_check),
            articles_checked=len(entries),
            conflicts=conflicts,
            scan_duration_ms=elapsed_ms,
        )

        logger.info(
            "Config conflict scan: tenant=%s fields=%d articles=%d conflicts=%d duration=%dms",
            tenant_id[:8],
            len(fields_to_check),
            len(entries),
            len(conflicts),
            elapsed_ms,
        )

        return result

    def _phase1_embedding_similarity(
        self,
        entries: list[dict[str, Any]],
        threshold: float,
        seen_pairs: set[tuple[str, str]],
    ) -> list[ConflictPair]:
        """Phase 1: Compare entries by embedding cosine similarity.

        Groups entries by (entry_type, language) to avoid cross-type/language
        comparisons that produce false positives.
        """
        from src.multi_tenant.semantic_cache import cosine_similarity

        conflicts: list[ConflictPair] = []

        # Group by (entry_type, language)
        groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for entry in entries:
            key = (entry.get("entry_type", "custom"), entry.get("language", "en"))
            groups.setdefault(key, []).append(entry)

        for _group_key, group_entries in groups.items():
            n = len(group_entries)
            if n < 2:
                continue

            # Pairwise comparison
            for i in range(n):
                for j in range(i + 1, n):
                    a = group_entries[i]
                    b = group_entries[j]
                    pair_key = tuple(sorted([a["id"], b["id"]]))
                    if pair_key in seen_pairs:
                        continue

                    emb_a = a.get("embedding", [])
                    emb_b = b.get("embedding", [])
                    if not emb_a or not emb_b:
                        continue

                    sim = cosine_similarity(emb_a, emb_b)
                    if sim < threshold:
                        continue

                    # Phase 3: Content overlap
                    content_a = a.get("content", "")
                    content_b = b.get("content", "")
                    overlap = _sentence_jaccard(content_a, content_b)

                    # Phase 4: Factual conflicts
                    facts = _detect_factual_conflicts(content_a, content_b)

                    # Classify
                    conflict = self._classify_conflict(
                        a, b, sim, overlap, 0.0, facts
                    )
                    if conflict:
                        seen_pairs.add(pair_key)
                        conflicts.append(conflict)

        return conflicts

    def _phase2_title_similarity(
        self,
        entries: list[dict[str, Any]],
        threshold: float,
        seen_pairs: set[tuple[str, str]],
    ) -> list[ConflictPair]:
        """Phase 2: Compare entries by title trigram similarity.

        Catches renamed duplicates that embedding might miss.
        Only flags pairs not already caught by Phase 1.
        """
        conflicts: list[ConflictPair] = []
        n = len(entries)

        for i in range(n):
            for j in range(i + 1, n):
                a = entries[i]
                b = entries[j]
                pair_key = tuple(sorted([a["id"], b["id"]]))
                if pair_key in seen_pairs:
                    continue

                # Skip cross-language comparisons
                if a.get("language", "en") != b.get("language", "en"):
                    continue

                title_sim = _trigram_jaccard(
                    a.get("title", ""),
                    b.get("title", ""),
                )
                if title_sim < threshold:
                    continue

                # Compute embedding similarity if both have embeddings
                emb_sim = 0.0
                emb_a = a.get("embedding", [])
                emb_b = b.get("embedding", [])
                if emb_a and emb_b:
                    from src.multi_tenant.semantic_cache import cosine_similarity
                    emb_sim = cosine_similarity(emb_a, emb_b)

                # Content overlap
                content_a = a.get("content", "")
                content_b = b.get("content", "")
                overlap = _sentence_jaccard(content_a, content_b)

                # Factual conflicts
                facts = _detect_factual_conflicts(content_a, content_b)

                # If embedding similarity is already high, Phase 1 would have caught it
                # (or will catch it). Only report here if embeddings are missing or below threshold.
                if emb_sim >= CONFLICT_SIMILARITY:
                    continue

                conflict = ConflictPair(
                    entry_a_id=a["id"],
                    entry_a_title=a.get("title", ""),
                    entry_b_id=b["id"],
                    entry_b_title=b.get("title", ""),
                    conflict_type=ConflictType.SIMILAR_TITLES,
                    severity=ConflictSeverity.LOW,
                    embedding_similarity=emb_sim,
                    content_overlap=overlap,
                    title_similarity=title_sim,
                    conflicting_facts=facts,
                    resolution=_generate_resolution(ConflictType.SIMILAR_TITLES, facts),
                )
                seen_pairs.add(pair_key)
                conflicts.append(conflict)

        return conflicts

    def _classify_conflict(
        self,
        entry_a: dict[str, Any],
        entry_b: dict[str, Any],
        embedding_sim: float,
        content_overlap: float,
        title_sim: float,
        conflicting_facts: list[str],
    ) -> ConflictPair | None:
        """Classify a flagged pair into a conflict type and severity.

        Returns None if the pair doesn't meet any conflict criteria.
        """
        # Compute title similarity if not already done
        if title_sim == 0.0:
            title_sim = _trigram_jaccard(
                entry_a.get("title", ""),
                entry_b.get("title", ""),
            )

        # High: Near-duplicate
        if embedding_sim >= NEAR_DUPLICATE_SIMILARITY and content_overlap >= NEAR_DUPLICATE_OVERLAP:
            return ConflictPair(
                entry_a_id=entry_a["id"],
                entry_a_title=entry_a.get("title", ""),
                entry_b_id=entry_b["id"],
                entry_b_title=entry_b.get("title", ""),
                conflict_type=ConflictType.NEAR_DUPLICATE,
                severity=ConflictSeverity.HIGH,
                embedding_similarity=embedding_sim,
                content_overlap=content_overlap,
                title_similarity=title_sim,
                conflicting_facts=conflicting_facts,
                resolution=_generate_resolution(ConflictType.NEAR_DUPLICATE, conflicting_facts),
            )

        # High: Conflicting (topical overlap + factual conflicts)
        if (
            embedding_sim >= CONFLICT_SIMILARITY
            and TOPICAL_OVERLAP_MIN <= content_overlap < NEAR_DUPLICATE_OVERLAP
            and conflicting_facts
        ):
            return ConflictPair(
                entry_a_id=entry_a["id"],
                entry_a_title=entry_a.get("title", ""),
                entry_b_id=entry_b["id"],
                entry_b_title=entry_b.get("title", ""),
                conflict_type=ConflictType.CONFLICTING,
                severity=ConflictSeverity.HIGH,
                embedding_similarity=embedding_sim,
                content_overlap=content_overlap,
                title_similarity=title_sim,
                conflicting_facts=conflicting_facts,
                resolution=_generate_resolution(ConflictType.CONFLICTING, conflicting_facts),
            )

        # Medium: Topical overlap (similar content, no factual conflicts detected)
        if (
            embedding_sim >= CONFLICT_SIMILARITY
            and content_overlap >= TOPICAL_OVERLAP_MIN
        ):
            return ConflictPair(
                entry_a_id=entry_a["id"],
                entry_a_title=entry_a.get("title", ""),
                entry_b_id=entry_b["id"],
                entry_b_title=entry_b.get("title", ""),
                conflict_type=ConflictType.TOPICAL_OVERLAP,
                severity=ConflictSeverity.MEDIUM,
                embedding_similarity=embedding_sim,
                content_overlap=content_overlap,
                title_similarity=title_sim,
                conflicting_facts=conflicting_facts,
                resolution=_generate_resolution(ConflictType.TOPICAL_OVERLAP, conflicting_facts),
            )

        # Low: High embedding similarity but low content overlap (related but different)
        if embedding_sim >= CONFLICT_SIMILARITY:
            return ConflictPair(
                entry_a_id=entry_a["id"],
                entry_a_title=entry_a.get("title", ""),
                entry_b_id=entry_b["id"],
                entry_b_title=entry_b.get("title", ""),
                conflict_type=ConflictType.TOPICAL_OVERLAP,
                severity=ConflictSeverity.LOW,
                embedding_similarity=embedding_sim,
                content_overlap=content_overlap,
                title_similarity=title_sim,
                conflicting_facts=conflicting_facts,
                resolution=_generate_resolution(ConflictType.TOPICAL_OVERLAP, conflicting_facts),
            )

        return None

    def health(self) -> dict[str, Any]:
        """Return scanner health status for /ready endpoint."""
        return {
            "configured": self._configured,
            "cached_tenants": len(self._scan_cache),
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_scanner: KBConflictScanner | None = None


def get_conflict_scanner() -> KBConflictScanner:
    """Get or create the module-level KBConflictScanner singleton."""
    global _scanner
    if _scanner is None:
        _scanner = KBConflictScanner()
    return _scanner
