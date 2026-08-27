#!/usr/bin/env python3
"""Read-only rule-projection policy/coupling diagnostic (WI-6329).

Canonical rule content lives under ``config/agent-control/gtkb-*``. This
script no longer writes ``.claude/rules`` compatibility projections.
``scripts/harness_projection/project_harness.py`` is the sole harness-neutral
projector. ``--check`` remains a read-only drift diagnostic.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY = Path("config/file-reference-migration/wi5640.toml")
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

_MARKDOWN_RELATIVE_LINK_RE = re.compile(r"(?P<head>\]\()(?P<target>[^)#?]+)(?P<tail>(?:[?#][^)]*)?\))")
RETIRED_WRITE_DIAGNOSTIC = (
    "Rule compatibility write/apply is retired. Use "
    "scripts/harness_projection/project_harness.py as the sole harness-neutral projector."
)
COMPARATOR_SUNSET_DIAGNOSTIC = (
    "comparator deprecated; mirrors are scheduled for terminal purge under "
    "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE / WI-6448 / WI-6386; "
    "this informational mode retires when those land"
)

# Policy-row source roots this loader accepts (WI-6329, Option A).
#
# The baseline root is the authoritative rule source; the legacy .claude/rules
# root is retained because the policy still carries one row there. Accepting the
# baseline root is only safe because the write/apply path above is retired: the
# hazard the original single-root restriction guarded against was overwriting a
# curated projection with stale baseline content, which is a property of writing.
# With no writer left in this module, the restriction protects nothing and only
# blocks the read-only --check diagnostic from seeing the real source of truth.
ALLOWED_SOURCE_ROOTS = (
    ".harness-baseline-configuration/rules/",
    ".claude/rules/",
)


class RuleProjectionError(ValueError):
    """Raised when the projection policy or a canonical input is unsafe."""


@dataclass(frozen=True, slots=True)
class RuleProjection:
    source: str
    canonical: str
    lifecycle_class: str
    load_policy: str


@dataclass(frozen=True, slots=True)
class ProjectionResult:
    source: str
    canonical: str
    canonical_sha256: str
    projected_sha256: str
    changed: bool


@dataclass(frozen=True, slots=True)
class LinkRewrite:
    canonical: str
    source_target: str
    projected_target: str
    expected_occurrences: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lf_normalize(data: bytes) -> bytes:
    """LF-normalize so line-ending-only differences are not treated as drift."""

    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def native_rule_projection_count(policy: dict[str, Any]) -> int:
    """Return the single policy-owned native rule-projection count."""

    retention = policy.get("retention")
    if not isinstance(retention, dict):
        raise RuleProjectionError("Policy is missing [retention]")
    raw = retention.get("native_rule_projection_count")
    if not isinstance(raw, int) or raw < 1:
        raise RuleProjectionError("retention.native_rule_projection_count must be a positive integer")
    return raw


def load_policy(project_root: Path, policy_path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    resolved = policy_path if policy_path.is_absolute() else project_root / policy_path
    try:
        payload = tomllib.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise RuleProjectionError(f"Cannot load rule projection policy {resolved}: {exc}") from exc
    if payload.get("schema_version") not in {1, 2}:
        raise RuleProjectionError("Rule projection policy must use schema_version = 1 or 2")
    return payload


def projection_rows(policy: dict[str, Any]) -> list[RuleProjection]:
    raw_rows = policy.get("rule_projections")
    if not isinstance(raw_rows, list):
        raise RuleProjectionError("Policy is missing [[rule_projections]] rows")
    rows: list[RuleProjection] = []
    seen_source: set[str] = set()
    seen_canonical: set[str] = set()
    for index, raw in enumerate(raw_rows, start=1):
        if not isinstance(raw, dict):
            raise RuleProjectionError(f"rule_projections row {index} is not a table")
        values = {key: str(raw.get(key) or "").strip().replace("\\", "/") for key in ("source", "canonical")}
        lifecycle_class = str(raw.get("class") or "").strip()
        load_policy = str(raw.get("load_policy") or "").strip()
        if not all((*values.values(), lifecycle_class, load_policy)):
            raise RuleProjectionError(f"rule_projections row {index} has an empty required field")
        source = values["source"]
        canonical = values["canonical"]
        if not source.startswith(ALLOWED_SOURCE_ROOTS):
            allowed = ", ".join(ALLOWED_SOURCE_ROOTS)
            raise RuleProjectionError(f"Projection source is outside the accepted rule roots ({allowed}): {source}")
        if not canonical.startswith("config/agent-control/gtkb-"):
            raise RuleProjectionError(f"Canonical rule is outside gtkb agent-control paths: {canonical}")
        source_key = unicodedata.normalize("NFC", source).casefold()
        canonical_key = unicodedata.normalize("NFC", canonical).casefold()
        if source_key in seen_source or canonical_key in seen_canonical:
            raise RuleProjectionError(f"Duplicate rule projection mapping: {source} -> {canonical}")
        seen_source.add(source_key)
        seen_canonical.add(canonical_key)
        rows.append(RuleProjection(source, canonical, lifecycle_class, load_policy))
    expected = native_rule_projection_count(policy)
    if len(rows) != expected:
        raise RuleProjectionError(f"Expected {expected} rule projections, found {len(rows)}")
    return rows


def _manifest_rule_sources(project_root: Path, policy: dict[str, Any]) -> set[str]:
    """Return the rule file names the migration manifest accounts for.

    Names, not paths (WI-6329, Option A). The manifest is a ledger of where each
    rule lived at migration time, so it still records the pre-migration
    ``.claude/rules`` home, while policy rows now point at the authoritative
    baseline root. Comparing whole paths would report that root difference as a
    ledger disagreement on every row, which is a false positive: the invariant
    this check exists to protect is that no rule is silently added to or dropped
    from the projection set, and that invariant is carried by the name set.
    """

    manifest_rel = str(policy.get("manifest_path") or "").strip()
    if not manifest_rel:
        raise RuleProjectionError("Policy is missing manifest_path")
    manifest_path = project_root / manifest_rel
    try:
        with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RuleProjectionError(f"Cannot read migration manifest {manifest_path}: {exc}") from exc
    names: set[str] = set()
    for row in rows:
        home = str(row.get("Current home directory:") or "").replace("\\", "/").rstrip("/")
        name = str(row.get("Current file name:") or "").strip()
        if home.casefold().endswith("/.claude/rules") and name:
            names.add(name)
    return names


def validate_policy_against_manifest(project_root: Path, policy: dict[str, Any], rows: list[RuleProjection]) -> None:
    declared = {PurePosixPath(row.source).name: row.source for row in rows}
    manifest = _manifest_rule_sources(project_root, policy)
    if set(declared) != manifest:
        missing = sorted(manifest - set(declared))
        extra = sorted(declared[name] for name in set(declared) - manifest)
        raise RuleProjectionError(f"Rule projection ledger disagrees with manifest; missing={missing}, extra={extra}")


def _decode_utf8(data: bytes, path: str) -> tuple[str, bytes]:
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    payload = data[len(bom) :]
    try:
        return payload.decode("utf-8"), bom
    except UnicodeDecodeError as exc:
        raise RuleProjectionError(f"Canonical rule is not UTF-8: {path}: {exc}") from exc


def link_rewrites(policy: dict[str, Any]) -> list[LinkRewrite]:
    rewrites: list[LinkRewrite] = []
    for index, raw in enumerate(policy.get("rule_link_rewrites", []), start=1):
        if not isinstance(raw, dict):
            raise RuleProjectionError(f"rule_link_rewrites row {index} is not a table")
        source = str(raw.get("source_target") or "")
        target = str(raw.get("projected_target") or "")
        canonical = str(raw.get("canonical") or "").replace("\\", "/")
        count = raw.get("expected_occurrences")
        if (
            not canonical.startswith("config/agent-control/gtkb-")
            or not source
            or not target
            or not isinstance(count, int)
            or count < 1
        ):
            raise RuleProjectionError(f"rule_link_rewrites row {index} is invalid")
        rewrites.append(LinkRewrite(canonical, source, target, count))
    return rewrites


def stabilize_relative_links(text: str, canonical_path: str, rewrites: list[LinkRewrite]) -> str:
    """Make canonical sibling Markdown links location-independent.

    Rewrites are explicit, file-scoped policy rows with exact occurrence counts.
    Prose, code blocks, URLs, and undeclared relative links remain untouched.
    """

    selected = [row for row in rewrites if row.canonical == canonical_path]
    by_source = {row.source_target: row for row in selected}
    observed = {row.source_target: 0 for row in selected}

    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        row = by_source.get(target)
        if row is None:
            return match.group(0)
        observed[target] += 1
        return f"{match.group('head')}{row.projected_target}{match.group('tail')}"

    rendered_lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = "```" if stripped.startswith("```") else "~~~" if stripped.startswith("~~~") else None
        if marker:
            fence = None if fence == marker else marker if fence is None else fence
            rendered_lines.append(line)
            continue
        if fence is not None:
            rendered_lines.append(line)
            continue
        parts = re.split(r"(`+[^`]*`+)", line)
        rendered_lines.append(
            "".join(
                part if index % 2 else _MARKDOWN_RELATIVE_LINK_RE.sub(replace, part) for index, part in enumerate(parts)
            )
        )
    rendered = "".join(rendered_lines)
    mismatches = {
        row.source_target: (observed[row.source_target], row.expected_occurrences)
        for row in selected
        if observed[row.source_target] != row.expected_occurrences
    }
    if mismatches:
        raise RuleProjectionError(f"Rule link rewrite occurrence mismatch: {mismatches}")
    return rendered


def render_projection(canonical_bytes: bytes, canonical_path: str, rewrites: list[LinkRewrite]) -> bytes:
    text, bom = _decode_utf8(canonical_bytes, canonical_path)
    rendered = stabilize_relative_links(text, canonical_path, rewrites)
    return bom + rendered.encode("utf-8")


def _assert_under(project_root: Path, relative: str) -> Path:
    candidate = (project_root / relative).resolve()
    try:
        candidate.relative_to(project_root.resolve())
    except ValueError as exc:
        raise RuleProjectionError(f"Projection path escapes project root: {relative}") from exc
    return candidate


def render_outputs(
    project_root: Path,
    *,
    policy_path: Path = DEFAULT_POLICY,
    canonical_overrides: dict[str, bytes] | None = None,
) -> tuple[list[RuleProjection], dict[str, bytes]]:
    """Render every owned projection without mutating the live tree."""

    root = project_root.resolve()
    policy = load_policy(root, policy_path)
    rows = projection_rows(policy)
    validate_policy_against_manifest(root, policy, rows)
    rewrites = link_rewrites(policy)
    outputs: dict[str, bytes] = {}
    overrides = canonical_overrides or {}
    for row in rows:
        canonical_path = _assert_under(root, row.canonical)
        _assert_under(root, row.source)
        if not canonical_path.is_file():
            raise RuleProjectionError(f"Canonical rule is missing: {row.canonical}")
        canonical_bytes = overrides[row.canonical] if row.canonical in overrides else canonical_path.read_bytes()
        outputs[row.source] = render_projection(canonical_bytes, row.canonical, rewrites)
    return rows, outputs


def generate(
    project_root: Path,
    *,
    policy_path: Path = DEFAULT_POLICY,
    check: bool = False,
) -> list[ProjectionResult]:
    if not check:
        raise RuleProjectionError(RETIRED_WRITE_DIAGNOSTIC)
    root = project_root.resolve()
    rows, outputs = render_outputs(root, policy_path=policy_path)
    results: list[ProjectionResult] = []
    for row in rows:
        canonical_path = _assert_under(root, row.canonical)
        source_path = _assert_under(root, row.source)
        canonical_bytes = canonical_path.read_bytes()
        projected = outputs[row.source]
        existing = source_path.read_bytes() if source_path.is_file() else None
        changed = existing is None or lf_normalize(existing) != lf_normalize(projected)
        results.append(
            ProjectionResult(
                source=row.source,
                canonical=row.canonical,
                canonical_sha256=sha256_bytes(canonical_bytes),
                projected_sha256=sha256_bytes(projected),
                changed=changed,
            )
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    args = parser.parse_args(argv)
    if not args.check:
        print(f"Rule compatibility projections: FAIL ({RETIRED_WRITE_DIAGNOSTIC})", file=sys.stderr)
        return 2
    try:
        results = generate(args.project_root, policy_path=args.policy, check=True)
    except RuleProjectionError as exc:
        print(f"Rule compatibility projections: FAIL ({exc})", file=sys.stderr)
        return 2
    changed = [result.source for result in results if result.changed]
    if changed:
        print(
            f"content drift detected: {len(changed)} file(s) would be regenerated by "
            "scripts/harness_projection/project_harness.py"
        )
        print(f"({COMPARATOR_SUNSET_DIAGNOSTIC})")
        for path in changed:
            print(f"- {path}")
        return 0
    print(f"Rule compatibility projections: PASS ({len(results)} projections current)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
