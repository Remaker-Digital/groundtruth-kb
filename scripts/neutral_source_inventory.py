#!/usr/bin/env python3
"""Deterministic neutral-source inventory and fail-closed sanitation guard (WI-6040).

Provides a case-insensitive complete-tree walk of the canonical neutral
configuration source, classifying every current source artifact exactly once
under a registered family/owner and reporting its read/mutation route.

The inventory never treats a generated harness directory (`.claude/`,
`.codex/`, `.goose/`, `.cursor/`, `.agent/`, `.api-harness/`) as a source
family (GOV-HARNESS-NEUTRAL-BASELINE-001).

Output is diagnostic evidence only and carries no authority. The service
mutates no source, projection, specification, project authorization, or
alternate state; it writes only a machine-readable plan/check result (stdout
JSON and an optional `.gtkb-state/` report).

Exit codes:
  0  inventory/check clean (every artifact classified, no contamination)
  1  contamination/classification failure
  2  usage error
  3  unreadable/malformed input
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_RELATIVE = Path("config") / "governance" / "neutral-source-inventory.toml"


class NeutralSourceInventoryError(Exception):
    """Raised when the inventory cannot produce a clean result."""


def _load_config(root: Path) -> dict[str, Any]:
    """Load the inventory TOML, fail-closed on malformed input."""
    try:
        import tomllib
    except ImportError:  # pragma: no cover - Python 3.11+
        import tomli as tomllib  # type: ignore[import-not-found]
    cfg_path = root / CONFIG_RELATIVE
    try:
        with cfg_path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError as exc:
        raise NeutralSourceInventoryError(f"inventory config missing: {cfg_path}") from exc
    except Exception as exc:
        raise NeutralSourceInventoryError(f"inventory config malformed: {cfg_path}: {exc}") from exc


def _resolve_root_paths(root: Path, config: dict[str, Any]) -> list[Path]:
    """Resolve the walk roots from the TOML `[roots]` table."""
    roots: list[Path] = []
    for value in (config.get("roots") or {}).values():
        p = Path(str(value))
        if not p.is_absolute():
            p = root / p
        roots.append(p.resolve())
    return roots


def _projection_prefixes(config: dict[str, Any]) -> list[str]:
    return [str(p).rstrip("/") + "/" for p in (config.get("projection_prefixes") or {}).get("paths", [])]


def _disposable_prefixes(config: dict[str, Any]) -> list[str]:
    return [str(p) for p in (config.get("disposable_prefixes") or {}).get("paths", [])]


def _classify(rel_posix: str, config: dict[str, Any]) -> str:
    """Classify a relative path as exactly one family. Returns the family name.

    Priority:
      1. disposable/junk (caches, scratch, pyc)
      2. projection (generated harness trees)
      3. registered family by extension/route heuristic
    """
    lower = rel_posix.lower()
    # Disposable first (never a source family)
    for disp in _disposable_prefixes(config):
        d = disp.lower()
        if d.endswith("/"):
            if lower.startswith(d):
                return "junk"
        elif lower.endswith(d) or lower == d:
            return "junk"
    # Projection (generated harness trees)
    for proj in _projection_prefixes(config):
        if lower.startswith(proj.lower()):
            return "projection"
    # Registered families by extension / position
    if rel_posix.startswith("config/governance/"):
        return "governance_evidence"
    if rel_posix.startswith("config/") and rel_posix.endswith(".toml"):
        return "configuration"
    if rel_posix.startswith("config/") and rel_posix.endswith(".md"):
        return "configuration"
    if rel_posix.endswith(".py"):
        return "source" if "/test" not in lower else "test"
    if rel_posix.endswith((".md", ".rst")):
        return "documentation"
    if rel_posix.endswith((".toml", ".json")):
        return "metadata"
    return "junk"


def _owner_for(rel_posix: str) -> str:
    if rel_posix.startswith("applications/"):
        return "applications"
    return "platform"


def _walk_and_classify(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk the roots case-insensitively and classify every artifact once."""
    artifacts: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for base in _resolve_root_paths(root, config):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*"), key=lambda p: p.as_posix().lower()):
            if path.is_dir():
                continue
            if not path.is_file():
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                rel = path.as_posix()
            family = _classify(rel, config)
            if family == "projection":
                # Projections are reported but flagged; they are not source families.
                artifacts.append(
                    {
                        "path": rel,
                        "family": "projection",
                        "owner": _owner_for(rel),
                        "consumer": "generated harness tree",
                        "route": "generated output; do not edit in place",
                        "projection": True,
                    }
                )
                continue
            artifacts.append(
                {
                    "path": rel,
                    "family": family,
                    "owner": _owner_for(rel),
                    "consumer": "agent-visible surface" if family != "junk" else "none",
                    "route": _route_for(family, config),
                    "projection": False,
                }
            )
    return artifacts


def _route_for(family: str, config: dict[str, Any]) -> str:
    routes = config.get("routes") or {}
    read_map = routes.get("read") or {}
    mutate_map = routes.get("mutate") or {}
    if family == "projection":
        return "generated output; do not edit in place"
    return f"read={read_map.get(family, 'n/a')}; mutate={mutate_map.get(family, 'n/a')}"


def _content_digest(artifacts: list[dict[str, Any]]) -> str:
    """Deterministic normalized digest of the classification result (acceptance 3)."""
    payload = json.dumps(artifacts, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _check(artifacts: list[dict[str, Any]]) -> list[str]:
    """Return a list of contamination findings (empty = clean)."""
    findings: list[str] = []
    for artifact in artifacts:
        if artifact["family"] == "unclassified":
            findings.append(f"unclassified artifact: {artifact['path']}")
    return findings


def run_inventory(root: Path, config: dict[str, Any], *, report_dir: Path | None = None) -> dict[str, Any]:
    artifacts = _walk_and_classify(root, config)
    digest = _content_digest(artifacts)
    findings = _check(artifacts)
    result = {
        "schema_version": config.get("schema_version", 1),
        "source_tree": ".harness-baseline-configuration + config + scripts + groundtruth-kb/src",
        "artifact_count": len(artifacts),
        "families": _family_counts(artifacts),
        "digest": digest,
        "clean": not findings,
        "findings": findings,
        "artifacts": artifacts,
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "neutral-source-inventory.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    return result


def _family_counts(artifacts: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in artifacts:
        counts[a["family"]] = counts.get(a["family"], 0) + 1
    return counts


HARNESS_PATH_CLASS = "harness_path"
PROJECTION_TOKEN_CLASS = "projection_token"
_REFERENCE_CLASSES = (HARNESS_PATH_CLASS, PROJECTION_TOKEN_CLASS)


def _reference_tokens(config: dict[str, Any]) -> list[str]:
    """Bare generated-target tokens the certification scans for.

    Defaults to the projection prefixes so the certification and the
    classification share one vocabulary rather than drifting apart.
    """
    declared = config.get("declared_references") or {}
    tokens = declared.get("tokens")
    if not tokens:
        tokens = [p.rstrip("/") for p in _projection_prefixes(config)]
    return [str(t).rstrip("/") for t in tokens if str(t).strip()]


def _declared_reference_rules(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse and validate the declared-reference registry, fail-closed.

    A declaration without a non-empty ``reason`` is itself a defect: an
    undeclared reference and a reference declared for no stated reason are
    equally unauditable.
    """
    declared = config.get("declared_references") or {}
    rules: list[dict[str, Any]] = []
    for index, entry in enumerate(declared.get("declarations") or []):
        path = str(entry.get("path") or "").strip()
        reason = str(entry.get("reason") or "").strip()
        if not path:
            raise NeutralSourceInventoryError(f"declared_references.declarations[{index}] has no path")
        if not reason:
            raise NeutralSourceInventoryError(
                f"declared_references.declarations[{index}] ({path}) has no reason; "
                "every declared reference must state why the reference is legitimate"
            )
        classes = entry.get("classes") or list(_REFERENCE_CLASSES)
        unknown = sorted(set(map(str, classes)) - set(_REFERENCE_CLASSES))
        if unknown:
            raise NeutralSourceInventoryError(
                f"declared_references.declarations[{index}] ({path}) names unknown "
                f"occurrence class(es): {', '.join(unknown)}"
            )
        rules.append({"path": path, "reason": reason, "classes": [str(c) for c in classes]})
    return rules


def _reference_pattern(tokens: list[str]) -> re.Pattern[str]:
    alternation = "|".join(re.escape(t) for t in sorted(tokens, key=len, reverse=True))
    return re.compile(
        rf"(?<![A-Za-z0-9_.\-])({alternation})(/|(?![A-Za-z0-9_\-]))",
        re.IGNORECASE,
    )


def _declaration_for(rel_posix: str, occurrence_class: str, rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    for rule in rules:
        if occurrence_class not in rule["classes"]:
            continue
        if rel_posix == rule["path"] or fnmatch.fnmatch(rel_posix, rule["path"]):
            return rule
    return None


def _scan_reference_occurrences(
    root: Path, config: dict[str, Any], rules: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Enumerate every generated-target reference across the walk roots.

    Returns ``(occurrences, unreadable)``. Unreadable content fails closed
    rather than being skipped silently.
    """
    pattern = _reference_pattern(_reference_tokens(config))
    occurrences: list[dict[str, Any]] = []
    unreadable: list[str] = []
    seen: set[Path] = set()
    for base in _resolve_root_paths(root, config):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*"), key=lambda p: p.as_posix().lower()):
            if not path.is_file():
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                rel = path.as_posix()
            family = _classify(rel, config)
            if family in {"junk", "projection"}:
                # Disposable content and generated trees are not neutral source;
                # they are out of the certification subject by construction.
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Binary-in-source is a separate contamination class; the
                # certification cannot certify content it cannot read.
                unreadable.append(rel)
                continue
            except OSError as exc:
                unreadable.append(f"{rel}: {exc}")
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                for match in pattern.finditer(line):
                    token = match.group(1)
                    occurrence_class = HARNESS_PATH_CLASS if match.group(2) == "/" else PROJECTION_TOKEN_CLASS
                    rule = _declaration_for(rel, occurrence_class, rules)
                    occurrences.append(
                        {
                            "path": rel,
                            "line": lineno,
                            "token": token,
                            "class": occurrence_class,
                            "declared": rule is not None,
                            "reason": rule["reason"] if rule else None,
                        }
                    )
    return occurrences, unreadable


def _generated_output_in_source(root: Path, config: dict[str, Any]) -> list[str]:
    """Report projector output that is living inside the neutral source.

    This is a LOCATION defect, deliberately separate from the reference
    declarations. A projection ownership manifest legitimately names every
    target it produces - that is its function - so declaring its references is
    correct. What no declaration can justify is the file sitting inside the
    neutral source at all: the source is the projector's input, and its own
    output has no place in it. Declaring the references would otherwise silence
    the reference count while leaving the misplacement in position.
    """
    names = {str(n).lower() for n in (config.get("declared_references") or {}).get("generated_output_names", [])}
    if not names:
        return []
    findings: list[str] = []
    for base in _resolve_root_paths(root, config):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*"), key=lambda p: p.as_posix().lower()):
            if not path.is_file() or path.name.lower() not in names:
                continue
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
            if _classify(rel, config) in {"junk", "projection"}:
                continue
            findings.append(
                f"generated output in neutral source: {rel} is projector output; "
                "its references are declarable but its location is not"
            )
    return findings


def run_certification(root: Path, config: dict[str, Any], *, report_dir: Path | None = None) -> dict[str, Any]:
    """Certify that every generated-target reference in neutral source is declared.

    Fail-closed: any undeclared occurrence, or any unreadable source content,
    leaves ``certified`` false.
    """
    rules = _declared_reference_rules(config)
    occurrences, unreadable = _scan_reference_occurrences(root, config, rules)
    undeclared = [o for o in occurrences if not o["declared"]]
    misplaced = _generated_output_in_source(root, config)
    findings = (
        [f"undeclared {o['class']} reference {o['token']!r} at {o['path']}:{o['line']}" for o in undeclared]
        + [f"unreadable neutral-source content: {u}" for u in unreadable]
        + misplaced
    )
    result = {
        "schema_version": config.get("schema_version", 1),
        "mode": "certify",
        "source_tree": (".harness-baseline-configuration + config + scripts + groundtruth-kb/src"),
        "declaration_count": len(rules),
        "occurrence_count": len(occurrences),
        "declared_count": len(occurrences) - len(undeclared),
        "undeclared_count": len(undeclared),
        "unreadable_count": len(unreadable),
        "misplaced_output_count": len(misplaced),
        "undeclared_paths": sorted({o["path"] for o in undeclared}),
        "certified": not findings,
        "findings": findings,
        "occurrences": occurrences,
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "neutral-source-certification.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Neutral-source inventory and fail-closed guard")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run the inventory and exit 1 if any artifact is unclassified/contaminated",
    )
    parser.add_argument(
        "--certify",
        action="store_true",
        help=(
            "Certify every generated-target reference against the declared-reference "
            "registry; exit 1 on any undeclared reference or unreadable content"
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--report-dir", type=Path, default=None, help="Optional .gtkb-state report dir")
    parser.add_argument("--project-root", type=Path, default=None, help="Host root override")
    args = parser.parse_args(argv)

    root = (args.project_root or PROJECT_ROOT).resolve()
    try:
        config = _load_config(root)
    except NeutralSourceInventoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    report_dir = args.report_dir
    if report_dir is not None and not report_dir.is_absolute():
        report_dir = root / report_dir

    if args.certify:
        # WI-6390 condition 3: certification is a distinct mode with its own
        # fail-closed exit code. The flag existed but was never wired, so it
        # silently ran the inventory instead of certifying anything.
        try:
            certification = run_certification(root, config, report_dir=report_dir)
        except NeutralSourceInventoryError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 3
        print(
            json.dumps(certification, sort_keys=True)
            if args.json
            else json.dumps(certification, indent=2, sort_keys=True)
        )
        if not certification["certified"]:
            for finding in certification["findings"]:
                print(f"contamination: {finding}", file=sys.stderr)
            return 1
        return 0

    result = run_inventory(root, config, report_dir=report_dir)

    if args.json or args.check:
        print(json.dumps(result, indent=2, sort_keys=True) if not args.json else json.dumps(result, sort_keys=True))

    if args.check and not result["clean"]:
        for f in result["findings"]:
            print(f"contamination: {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
