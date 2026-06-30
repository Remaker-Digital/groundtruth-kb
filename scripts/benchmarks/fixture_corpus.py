"""Read-only GT-KB harness benchmark fixture corpus.

The corpus is inert benchmark ground truth. It loads fixture metadata and
answer keys from ``scripts/benchmarks/fixtures/`` without mutating live bridge,
backlog, specification, MemBase, harness-state, or application artifacts.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from scripts.benchmarks import harness_quality_manifest as manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
FIXTURE_INDEX = FIXTURE_ROOT / "fixture_index.json"

PROMOTION_STATUS_UNPROMOTED = "unpromoted"
PROMOTION_STATUS_PROMOTED = "promoted"
PROMOTION_APPROVAL_TOKEN = "explicit-benchmark-fixture-promotion"

DETERMINISTIC_ONLY_FAMILY_IDS: tuple[str, ...] = (
    "implementation_start_safety",
    "proposal_report_correctness",
    "direct_mutation_refusal",
    "cli_first_operation",
    "fixture_isolation",
)

FIXTURE_SCHEMA_FIELDS: tuple[str, ...] = (
    "fixture_id",
    "fixture_root",
    "source_artifact_refs",
    "promotion_status",
    "author_model_configuration",
)

MANIFEST_VISIBLE_FIXTURE_FIELDS: tuple[str, ...] = (
    "fixture_id",
    "author_model_configuration",
)


@dataclass(frozen=True)
class BenchmarkFixture:
    """A single isolated seeded-defect fixture with answer-key evidence."""

    fixture_id: str
    fixture_root: str
    source_artifact_refs: tuple[str, ...]
    challenge_family: str
    promotion_status: str
    author_model_configuration: str
    failure_classes: tuple[str, ...]
    deterministic_evidence: dict[str, bool | str]
    expected_evidence: dict[str, str]
    defect_summary: str


def _as_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list | tuple):
        return ()
    return tuple(str(item) for item in value)


def _fixture_from_mapping(payload: dict[str, Any]) -> BenchmarkFixture:
    return BenchmarkFixture(
        fixture_id=str(payload.get("fixture_id", "")),
        fixture_root=str(payload.get("fixture_root", "")),
        source_artifact_refs=_as_tuple(payload.get("source_artifact_refs", ())),
        challenge_family=str(payload.get("challenge_family", "")),
        promotion_status=str(payload.get("promotion_status", "")),
        author_model_configuration=str(payload.get("author_model_configuration", "")),
        failure_classes=_as_tuple(payload.get("failure_classes", ())),
        deterministic_evidence=dict(payload.get("deterministic_evidence", {})),
        expected_evidence=dict(payload.get("expected_evidence", {})),
        defect_summary=str(payload.get("defect_summary", "")),
    )


def load_fixture_corpus(index_file: Path | None = None) -> tuple[BenchmarkFixture, ...]:
    """Load fixture metadata without mutating live GT-KB state."""

    source = index_file or FIXTURE_INDEX
    payload = json.loads(source.read_text(encoding="utf-8"))
    fixtures = payload.get("fixtures", ())
    if not isinstance(fixtures, list):
        raise ValueError("fixture index must contain a fixtures list")
    return tuple(_fixture_from_mapping(item) for item in fixtures if isinstance(item, dict))


def _challenge_families() -> dict[str, manifest.ChallengeFamily]:
    return {family.id: family for family in manifest.HARNESS_QUALITY_MANIFEST.challenge_families}


def _resolve_fixture_root(fixture: BenchmarkFixture) -> Path:
    root = Path(fixture.fixture_root)
    if root.is_absolute():
        return root.resolve()
    return (PROJECT_ROOT / root).resolve()


def validate_fixture_corpus(fixtures: tuple[BenchmarkFixture, ...] | None = None) -> list[str]:
    """Return validation errors for the fixture corpus."""

    loaded = fixtures if fixtures is not None else load_fixture_corpus()
    errors: list[str] = []
    families = _challenge_families()
    failure_classes = set(manifest.FAILURE_CLASSES)
    evidence_fields = set(manifest.REQUIRED_EVIDENCE_FIELDS)

    missing_manifest_fields = set(MANIFEST_VISIBLE_FIXTURE_FIELDS) - evidence_fields
    if missing_manifest_fields:
        errors.append(f"manifest missing fixture evidence fields: {sorted(missing_manifest_fields)}")

    fixture_ids = [fixture.fixture_id for fixture in loaded]
    for fixture_id in sorted({item for item in fixture_ids if fixture_ids.count(item) > 1}):
        errors.append(f"duplicate fixture id: {fixture_id}")

    for fixture in loaded:
        if not fixture.fixture_id:
            errors.append("fixture missing fixture_id")
        if not fixture.defect_summary:
            errors.append(f"{fixture.fixture_id}: missing defect_summary")
        if fixture.challenge_family not in families:
            errors.append(f"{fixture.fixture_id}: unknown challenge family {fixture.challenge_family!r}")
            continue

        family = families[fixture.challenge_family]
        answer_keys = set(fixture.deterministic_evidence)
        unknown_answer_keys = answer_keys - set(family.deterministic_evidence)
        if unknown_answer_keys:
            errors.append(f"{fixture.fixture_id}: unknown deterministic evidence {sorted(unknown_answer_keys)}")
        if not answer_keys:
            errors.append(f"{fixture.fixture_id}: missing deterministic evidence answer key")

        fixture_root = _resolve_fixture_root(fixture)
        if not fixture_root.is_relative_to(FIXTURE_ROOT.resolve()):
            errors.append(f"{fixture.fixture_id}: fixture root escapes isolated corpus root")
        if not fixture_root.exists() or not fixture_root.is_dir():
            errors.append(f"{fixture.fixture_id}: fixture root does not exist")

        if fixture.promotion_status != PROMOTION_STATUS_UNPROMOTED:
            errors.append(f"{fixture.fixture_id}: seeded fixtures must default to unpromoted")
        if not fixture.author_model_configuration:
            errors.append(f"{fixture.fixture_id}: missing author_model_configuration")
        if not fixture.source_artifact_refs:
            errors.append(f"{fixture.fixture_id}: missing source artifact references")
        unknown_failure_classes = set(fixture.failure_classes) - failure_classes
        if unknown_failure_classes:
            errors.append(f"{fixture.fixture_id}: unknown failure classes {sorted(unknown_failure_classes)}")
        if not fixture.failure_classes:
            errors.append(f"{fixture.fixture_id}: missing failure class")

        for required_field in FIXTURE_SCHEMA_FIELDS:
            if not hasattr(fixture, required_field):
                errors.append(f"{fixture.fixture_id}: fixture schema missing {required_field}")

    family_ids = {fixture.challenge_family for fixture in loaded}
    missing_deterministic_families = set(DETERMINISTIC_ONLY_FAMILY_IDS) - family_ids
    if missing_deterministic_families:
        errors.append(f"missing deterministic-only fixture families: {sorted(missing_deterministic_families)}")

    observed_failure_classes = {failure_class for fixture in loaded for failure_class in fixture.failure_classes}
    for required_failure_class in ("root-boundary", "claim-accuracy"):
        if required_failure_class not in observed_failure_classes:
            errors.append(f"missing seeded fixture for failure class: {required_failure_class}")

    return errors


def require_valid_fixture_corpus(fixtures: tuple[BenchmarkFixture, ...] | None = None) -> tuple[BenchmarkFixture, ...]:
    """Return the loaded corpus or raise ``ValueError`` with validation details."""

    loaded = fixtures if fixtures is not None else load_fixture_corpus()
    errors = validate_fixture_corpus(loaded)
    if errors:
        raise ValueError("; ".join(errors))
    return loaded


def mark_fixture_promoted(fixture: BenchmarkFixture, *, approval_token: str) -> BenchmarkFixture:
    """Return a promoted fixture copy only when promotion is explicit."""

    if approval_token != PROMOTION_APPROVAL_TOKEN:
        raise ValueError("fixture promotion requires explicit approval token")
    return replace(fixture, promotion_status=PROMOTION_STATUS_PROMOTED)


def fixture_corpus_to_dict(fixtures: tuple[BenchmarkFixture, ...] | None = None) -> dict[str, Any]:
    """Serialize the validated fixture corpus for future runner slices."""

    loaded = require_valid_fixture_corpus(fixtures)
    return {
        "fixture_root": FIXTURE_ROOT.as_posix(),
        "fixtures": [asdict(fixture) for fixture in loaded],
    }


__all__ = [
    "DETERMINISTIC_ONLY_FAMILY_IDS",
    "FIXTURE_INDEX",
    "FIXTURE_ROOT",
    "FIXTURE_SCHEMA_FIELDS",
    "MANIFEST_VISIBLE_FIXTURE_FIELDS",
    "PROMOTION_APPROVAL_TOKEN",
    "PROMOTION_STATUS_PROMOTED",
    "PROMOTION_STATUS_UNPROMOTED",
    "BenchmarkFixture",
    "fixture_corpus_to_dict",
    "load_fixture_corpus",
    "mark_fixture_promoted",
    "require_valid_fixture_corpus",
    "validate_fixture_corpus",
]
