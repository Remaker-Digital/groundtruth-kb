#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Classify harness-equivalence evidence freshness and archival boundaries."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from groundtruth_kb.project.registry_control_plane import RegistryControlPlaneError, load_registry_snapshot

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH: Final[Path] = PROJECT_ROOT / "config" / "governance" / "evidence-freshness-boundaries.toml"
DEFAULT_REPORT_PATH: Final[Path] = (
    PROJECT_ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-2026-07-06.md"
)
REQUIRED_CLASSES: Final[set[str]] = {
    "current",
    "stale",
    "archival-citation-only",
    "full-read-justified",
    "missing",
}
SUMMARY_SOURCE_KINDS: Final[set[str]] = {"compact_summary", "copied_excerpt", "paraphrase", "generated_summary"}
ARCHIVAL_CLAIM_KINDS: Final[set[str]] = {"historical", "audit_trail", "archive", "archival_citation"}


class EvidenceFreshnessError(ValueError):
    """Raised when config or evidence input is not usable."""


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config = _load_toml(path)
    validate_config(config, path=path)
    return config


def validate_config(config: dict[str, Any], *, path: Path | None = None) -> None:
    location = f" in {path}" if path else ""
    if config.get("schema_version") != 1:
        raise EvidenceFreshnessError(f"Unsupported schema_version{location}: {config.get('schema_version')!r}")
    relationship = config.get("relationship_to_sot_registry")
    if not isinstance(relationship, dict):
        raise EvidenceFreshnessError(f"Missing relationship_to_sot_registry{location}")
    if relationship.get("duplicate_sot_inventory") is not False:
        raise EvidenceFreshnessError("evidence freshness config must not duplicate the SoT registry")
    freshness = config.get("freshness")
    if not isinstance(freshness, dict):
        raise EvidenceFreshnessError(f"Missing freshness policy{location}")
    classes = {item.get("id") for item in config.get("evidence_classes", []) if isinstance(item, dict)}
    missing = sorted(REQUIRED_CLASSES - classes)
    if missing:
        raise EvidenceFreshnessError(f"Missing evidence classes{location}: {', '.join(missing)}")
    blockers = config.get("blocker_families", [])
    blocker_ids = {item.get("id") for item in blockers if isinstance(item, dict)}
    expected_blockers = {f"B{idx}" for idx in range(1, 8)}
    missing_blockers = sorted(expected_blockers - blocker_ids)
    if missing_blockers:
        raise EvidenceFreshnessError(f"Missing blocker families{location}: {', '.join(missing_blockers)}")


def _normal_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/").strip().lower()


def _matches_pattern(path: str, pattern: str) -> bool:
    return fnmatch.fnmatch(_normal_path(path), _normal_path(pattern))


def _parse_timestamp(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if not isinstance(value, str):
        raise EvidenceFreshnessError(f"Timestamp must be ISO text, got {type(value).__name__}")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _age_minutes(observed_at: Any, *, now: datetime) -> float | None:
    observed = _parse_timestamp(observed_at)
    if observed is None:
        return None
    return (now - observed.astimezone(UTC)).total_seconds() / 60


def load_forbidden_substitutes(registry_path: Path) -> dict[str, dict[str, str]]:
    if not registry_path.is_file():
        return {}
    project_root = registry_path.resolve().parents[2]
    try:
        registry = load_registry_snapshot(project_root=project_root, registry_path=registry_path)
    except RegistryControlPlaneError as exc:
        raise EvidenceFreshnessError(f"cannot load coherent registry snapshot: {exc}") from exc
    substitutes: dict[str, dict[str, str]] = {}
    for artifact in registry.records:
        artifact_id = artifact.id
        canonical = artifact.storage_path
        for substitute in artifact.forbidden_substitutes:
            substitutes[_normal_path(substitute)] = {
                "artifact_id": artifact_id,
                "canonical_path": canonical,
            }
    return substitutes


def _registry_path(config: dict[str, Any], *, config_path: Path = DEFAULT_CONFIG_PATH) -> Path:
    raw = str(config.get("sot_registry_path") or "")
    if not raw:
        return PROJECT_ROOT / "config" / "registry" / "sot-artifacts.toml"
    path = Path(raw)
    return path if path.is_absolute() else config_path.parent.parent.parent / path


def _forbidden_substitute_hit(
    source_path: str,
    *,
    config: dict[str, Any],
    config_path: Path = DEFAULT_CONFIG_PATH,
    substitutes: dict[str, dict[str, str]] | None = None,
) -> dict[str, str] | None:
    if not source_path:
        return None
    lookup = (
        substitutes
        if substitutes is not None
        else load_forbidden_substitutes(_registry_path(config, config_path=config_path))
    )
    normalized = _normal_path(source_path)
    return lookup.get(normalized)


def _citation_only_match(source_path: str, config: dict[str, Any]) -> str | None:
    for pattern in config.get("citation_only_patterns", []):
        if not isinstance(pattern, dict):
            continue
        if _matches_pattern(source_path, str(pattern.get("pattern", ""))):
            return str(pattern.get("id", "citation-only-pattern"))
    return None


def classify_reference(
    reference: dict[str, Any],
    config: dict[str, Any],
    *,
    now: datetime | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    forbidden_substitutes: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Classify one evidence reference without reading the referenced payload."""

    now = now.astimezone(UTC) if now else datetime.now(UTC)
    source_path = str(reference.get("source_path") or "")
    claim_kind = str(reference.get("claim_kind") or "").strip().lower()
    source_kind = str(reference.get("source_kind") or "").strip().lower()
    reasons: list[str] = []

    if reference.get("missing") is True or reference.get("exists") is False or source_kind == "missing":
        return _classification(reference, "missing", "none", False, ["evidence reference is missing"])

    full_read_reason = str(reference.get("full_read_reason") or "").strip()
    stable_citation = bool(reference.get("stable_citation") or source_path)
    if full_read_reason:
        if stable_citation:
            return _classification(
                reference,
                "full-read-justified",
                "full",
                True,
                [f"full archival read justified: {full_read_reason}"],
            )
        return _classification(
            reference,
            "stale",
            "canonical_refresh_required",
            False,
            ["full-read request lacks a stable citation"],
        )

    if claim_kind in ARCHIVAL_CLAIM_KINDS or reference.get("citation_only") is True:
        pattern_id = _citation_only_match(source_path, config)
        if pattern_id or stable_citation:
            reason = f"stable archival citation matched {pattern_id}" if pattern_id else "stable archival citation"
            return _classification(reference, "archival-citation-only", "citation_only", True, [reason])
        return _classification(
            reference,
            "missing",
            "none",
            False,
            ["archival citation lacks a stable path or identifier"],
        )

    if claim_kind != "current_state":
        return _classification(
            reference,
            "stale",
            "canonical_refresh_required",
            False,
            ["claim_kind is not archival and not an explicit current_state claim"],
        )

    substitute_hit = _forbidden_substitute_hit(
        source_path,
        config=config,
        config_path=config_path,
        substitutes=forbidden_substitutes,
    )
    if substitute_hit:
        reasons.append(
            "source_path is a registered forbidden_substitute for "
            f"{substitute_hit['artifact_id']} (canonical: {substitute_hit['canonical_path']})"
        )

    canonical_reader_output = bool(reference.get("canonical_reader_output") or reference.get("canonical_reader"))
    declared_ttl = bool(reference.get("ttl_declared"))
    fallback_to_canonical = bool(reference.get("fallback_to_canonical"))
    source_is_summary = source_kind in SUMMARY_SOURCE_KINDS
    if source_is_summary and not canonical_reader_output and not declared_ttl:
        reasons.append("summary/paraphrase/copied excerpt cannot satisfy a current-state claim")

    max_age = int(
        reference.get("ttl_minutes")
        or reference.get("max_age_minutes")
        or config.get("freshness", {}).get("default_current_max_age_minutes", 60)
    )
    age = _age_minutes(reference.get("observed_at") or reference.get("generated_at"), now=now)
    if age is None:
        reasons.append("current-state claim lacks observed_at/generated_at freshness metadata")
    elif age > max_age:
        reasons.append(f"current-state evidence age {age:.1f}m exceeds {max_age}m freshness bound")

    if declared_ttl:
        if not fallback_to_canonical:
            reasons.append("declared-TTL exception lacks canonical fallback metadata")
        if not reference.get("ttl_source"):
            reasons.append("declared-TTL exception lacks inline ttl_source metadata")

    accepted_transport = canonical_reader_output or (
        declared_ttl and fallback_to_canonical and bool(reference.get("ttl_source"))
    )
    if not accepted_transport:
        reasons.append("current-state claim is not backed by canonical-reader output or a valid declared-TTL exception")

    if reasons:
        return _classification(reference, "stale", "canonical_refresh_required", False, reasons)
    return _classification(reference, "current", "compact", True, ["fresh canonical-reader evidence"])


def _classification(
    reference: dict[str, Any],
    classification: str,
    read_mode: str,
    sufficient: bool,
    reasons: list[str],
) -> dict[str, Any]:
    return {
        "id": reference.get("id"),
        "source_path": reference.get("source_path"),
        "claim_kind": reference.get("claim_kind"),
        "classification": classification,
        "read_mode": read_mode,
        "sufficient_for_claim": sufficient,
        "reasons": reasons,
    }


def classify_references(
    references: list[dict[str, Any]],
    config: dict[str, Any],
    *,
    now: datetime | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> list[dict[str, Any]]:
    substitutes = load_forbidden_substitutes(_registry_path(config, config_path=config_path))
    return [
        classify_reference(item, config, now=now, config_path=config_path, forbidden_substitutes=substitutes)
        for item in references
    ]


def blocker_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(config.get("blocker_families", []), key=lambda item: item.get("id", ""))


def build_report(
    config: dict[str, Any],
    *,
    generated_at: datetime | None = None,
    implementation_packet_hash: str = "",
) -> str:
    generated_at = generated_at.astimezone(UTC) if generated_at else datetime.now(UTC)
    relationship = config["relationship_to_sot_registry"]
    freshness = config["freshness"]
    lines = [
        "# Harness Equivalence Phase 3 Evidence Freshness Boundaries",
        "",
        "Status: IMPLEMENTED",
        f"Generated: {generated_at.isoformat().replace('+00:00', 'Z')}",
        f"Project: {config['project']}",
        f"Work Item: {config['work_item']}",
        f"Bridge: {config['authority_bridge']}",
    ]
    if implementation_packet_hash:
        lines.append(f"Implementation authorization packet: {implementation_packet_hash}")
    lines.extend(
        [
            "",
            "## Claim",
            "",
            "WI-4971 is satisfied by a config-backed classifier that separates current-state evidence, stale evidence, archival citation-only references, justified full archival reads, and missing evidence without loading full historical state by default.",
            "",
            "## Relationship To SoT Freshness And Read Discipline",
            "",
            f"- Relationship mode: `{relationship['mode']}`.",
            f"- SoT registry path: `{config['sot_registry_path']}`.",
            f"- Duplicate SoT inventory: `{str(relationship['duplicate_sot_inventory']).lower()}`.",
            f"- Current-state authority: `{relationship['freshness_authority']}`.",
            f"- Read-hook authority: `{relationship['read_hook_authority']}`.",
            f"- Forbidden substitutes policy: `{freshness['forbidden_substitutes_policy']}`.",
            "",
            "Current-state claims require fresh canonical-reader evidence. Compact output is acceptable only when it is produced by the canonical reader for the state being claimed, or when a declared-TTL exception includes inline TTL metadata and canonical fallback. Archival/audit-trail references may be cited by stable path or ID without loading the full archived payload unless the session must verify, dispute, reproduce, or repair the archived claim.",
            "",
            "## Evidence Classes",
            "",
            "| Class | Routine read mode | Sufficient for current state | Rule |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in config["evidence_classes"]:
        lines.append(
            "| "
            f"`{item['id']}` | "
            f"`{item['default_read_mode']}` | "
            f"{str(item.get('sufficient_for_current_state', False)).lower()} | "
            f"{item['description']} |"
        )
    lines.extend(
        [
            "",
            "## B1-B7 Boundary Mapping",
            "",
            "| ID | Blocker | Evidence class | Boundary rule | Evidence path |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in blocker_rows(config):
        lines.append(
            "| "
            f"`{item['id']}` | "
            f"{item['summary']} | "
            f"`{item['evidence_class']}` | "
            f"{item['boundary_rule']} | "
            f"`{item['evidence_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Verification Notes",
            "",
            "- The policy stores evidence-classification rules under `config/governance/`; it does not add `[[artifacts]]` rows or duplicate the SoT registry.",
            "- The helper checks `forbidden_substitutes` from `config/registry/sot-artifacts.toml` before accepting current-state evidence.",
            "- Full archive reads are opt-in and require a reason plus a stable citation; routine reports can cite append-only history without loading full archived payloads.",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify = subparsers.add_parser("classify", help="Classify evidence references from a JSON file.")
    classify.add_argument("--evidence-file", type=Path, required=True)
    classify.add_argument("--json", action="store_true", help="Emit JSON output.")

    report = subparsers.add_parser("report", help="Render the WI-4971 markdown report.")
    report.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    report.add_argument("--implementation-packet-hash", default="")
    report.add_argument("--generated-at", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    config = load_config(args.config)
    if args.command == "classify":
        payload = _read_json_file(args.evidence_file)
        if not isinstance(payload, list):
            raise EvidenceFreshnessError("evidence-file must contain a JSON list")
        classifications = classify_references(payload, config, config_path=args.config)
        print(json.dumps({"classifications": classifications}, indent=2, sort_keys=True))
        return 0
    if args.command == "report":
        generated_at = _parse_timestamp(args.generated_at) if args.generated_at else None
        markdown = build_report(
            config,
            generated_at=generated_at,
            implementation_packet_hash=args.implementation_packet_hash,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8", newline="\n")
        print(str(args.output))
        return 0
    raise EvidenceFreshnessError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
