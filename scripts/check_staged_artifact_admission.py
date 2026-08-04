#!/usr/bin/env python3
"""Staged-artifact admission gate (WI-5699).

Every verification gate in the sweep path validates a *property of* a file --
formatting, compilation, secret content, protected-path evidence. None
validates a file's *right to be present*. A pipeline composed entirely of
property checks cannot detect an unregistered artifact.

This check asks the missing question. For every staged ADDITION it requires
exactly one admission basis:

    authorized  the path matches a bridge thread's declared ``target_paths``
    registered  the path resolves to a SoT registry record
    excluded    the path matches a rule in config/governance/staging-admission.toml
    unresolved  none of the above

Phase 1 is ADVISORY: this script always exits 0. It reports; it never blocks.
Promotion to a blocking gate is a separate owner-approved proposal, so the
exclusion config can be tuned against real sweeps first.

Modifications and deletions are out of scope. "May this file exist" is a
question about additions; edits to existing files are already governed by the
protected-path and narrative-evidence gates.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_RELATIVE_PATH = "config/governance/staging-admission.toml"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))


@dataclass(frozen=True)
class ExclusionRule:
    """One owner-governed disposable-path rule."""

    id: str
    glob: str
    root_only: bool
    reason: str

    def matches(self, relative_path: str) -> bool:
        if self.root_only and "/" in relative_path:
            return False
        if fnmatch.fnmatch(relative_path, self.glob):
            return True
        # Support directory-prefix globs such as ".gtkb-state/**".
        if self.glob.endswith("/**"):
            prefix = self.glob[: -len("/**")]
            return relative_path == prefix or relative_path.startswith(f"{prefix}/")
        return False


@dataclass
class AdmissionReport:
    """Deterministic classification of every staged addition."""

    authorized: dict[str, str] = field(default_factory=dict)
    registered: dict[str, str] = field(default_factory=dict)
    excluded: dict[str, str] = field(default_factory=dict)
    unresolved: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "authorized": dict(sorted(self.authorized.items())),
            "errors": sorted(self.errors),
            "excluded": dict(sorted(self.excluded.items())),
            "registered": dict(sorted(self.registered.items())),
            "unresolved": sorted(self.unresolved),
        }


def normalize(relative_path: str) -> str:
    text = str(relative_path).strip().strip("'\"`").replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.rstrip("/")


def staged_additions(project_root: Path) -> list[str]:
    """Return staged additions only; modifications and deletions are out of scope."""
    completed = subprocess.run(
        ["git", "-C", str(project_root), "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        return []
    return sorted({normalize(line) for line in completed.stdout.splitlines() if line.strip()})


def load_exclusion_rules(project_root: Path) -> tuple[list[ExclusionRule], list[str]]:
    path = project_root / CONFIG_RELATIVE_PATH
    if not path.exists():
        return [], [f"exclusion config missing: {CONFIG_RELATIVE_PATH}"]
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [], [f"exclusion config unreadable: {exc}"]
    rules: list[ExclusionRule] = []
    errors: list[str] = []
    for entry in payload.get("rules", []):
        rule_id = entry.get("id")
        glob = entry.get("glob")
        reason = entry.get("reason")
        if not rule_id or not glob or not reason:
            errors.append(f"exclusion rule missing id, glob, or reason: {entry!r}")
            continue
        rules.append(
            ExclusionRule(
                id=str(rule_id),
                glob=str(glob),
                root_only=bool(entry.get("root_only", False)),
                reason=str(reason),
            )
        )
    return rules, errors


# Statuses that confer admission authority. Per NO-GO-008 and the approved
# WI-5699 plan, only a latest-`GO` thread carries an independently accepted
# authorization. Review-pending (`NEW`, `REVISED`), rejected (`NO-GO`),
# terminal (`VERIFIED`, `WITHDRAWN`, `DEFERRED`), and `NO-ACTION` threads confer
# none. An unresolvable status confers none and is reported as an error.
_AUTHORITY_CONFERRING_STATUS = frozenset({"GO"})

# Markdown / path structural characters that cannot be part of a real in-root
# relative path. A candidate containing any of these is rejected as
# authorization evidence (reported in errors[], never authorized).
_MARKDOWN_STRUCTURAL = frozenset("#`|")


def _is_path_shaped(target: str) -> str | None:
    """Return a normalized in-root relative path, or None when not path-shaped.

    A candidate is rejected (None) when it is empty/whitespace-only, contains
    Markdown structural characters, is absolute or drive-qualified, escapes the
    project root via ``..``, or normalizes to empty.
    """
    if not target or not target.strip():
        return None
    if any(ch in target for ch in _MARKDOWN_STRUCTURAL):
        return None
    normalized = normalize(target)
    if not normalized:
        return None
    if ":" in normalized:
        # drive-qualified (C:/x) or scheme-qualified
        return None
    if normalized.startswith("/") or normalized.startswith("\\"):
        return None
    if ".." in normalized.split("/"):
        return None
    return normalized


def bridge_authorized_paths(project_root: Path) -> tuple[dict[str, str], list[str]]:
    """Map each declared target path to the bridge thread that declares it.

    Only threads whose *latest* status confers admission authority (latest
    ``GO``) contribute target_paths as authorization evidence. Review-pending,
    rejected, terminal, and unresolvable threads contribute none (NO-GO-008).
    Reuses ``implementation_authorization.extract_target_paths`` and the
    canonical thread-lifecycle surface ``bridge_thread_files``; this module
    introduces no second parser.
    """
    try:
        from implementation_authorization import extract_target_paths
    except ImportError as exc:  # pragma: no cover - import wiring
        return {}, [f"target_paths parser unavailable: {exc}"]

    try:
        from bridge_thread_files import index_bridge_thread_files, latest_bridge_status_for_thread
    except ImportError as exc:  # pragma: no cover - import wiring
        return {}, [f"bridge thread lifecycle helper unavailable: {exc}"]

    declared: dict[str, str] = {}
    errors: list[str] = []
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return {}, ["bridge directory not found"]

    index = index_bridge_thread_files(project_root)
    for slug, files in sorted(index.items()):
        status = latest_bridge_status_for_thread(project_root, slug)
        if status is None:
            errors.append(f"bridge thread status unresolvable, excluded from authorization evidence: {slug}")
            continue
        if status not in _AUTHORITY_CONFERRING_STATUS:
            # Not a live authorization: no target_paths from this thread confer
            # admission, regardless of what its proposal declared.
            continue
        # Only a latest-GO thread confers authority; read the operative proposal
        # (latest NEW/REVISED) of that thread for its declared targets.
        operative = None
        for vfile in reversed(files):
            vstatus = _status_from_path(vfile.path)
            if vstatus in {"NEW", "REVISED"}:
                operative = vfile.path
                break
        if operative is None:
            # Latest-GO thread with no readable proposal; fail safe (report, no authority).
            errors.append(f"bridge thread latest GO has no operative proposal, excluded: {slug}")
            continue
        try:
            markdown = operative.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"bridge file unreadable, excluded from authorization evidence: {operative.name}: {exc}")
            continue
        try:
            targets = extract_target_paths(markdown)
        except Exception:  # noqa: BLE001
            continue
        for target in targets:
            shaped = _is_path_shaped(target)
            if shaped is None:
                errors.append(f"non-path target syntax rejected as authorization evidence: {target!r} (from {slug})")
                continue
            declared.setdefault(shaped, operative.name)
    return declared, errors


def _status_from_path(path: Path) -> str | None:
    try:
        from bridge_thread_files import status_from_bridge_file
    except ImportError:  # pragma: no cover - import wiring
        return None
    return status_from_bridge_file(path)


def registry_classification(relative_path: str, project_root: Path) -> str | None:
    """Return a registry classification label, or None when unregistered."""
    try:
        from controlled_artifact_paths import classify_controlled_artifact
    except ImportError:  # pragma: no cover - import wiring
        return None
    try:
        result = classify_controlled_artifact(relative_path, project_root=project_root)
    except Exception:  # noqa: BLE001 - registry unavailability must fail safe
        return None
    if result.reason_code == "registered_artifact":
        return result.classification
    return None


def matches_declared(relative_path: str, declared: dict[str, str]) -> str | None:
    if relative_path in declared:
        return declared[relative_path]
    for target, thread in sorted(declared.items()):
        if target.endswith("/**"):
            prefix = target[: -len("/**")]
            if relative_path == prefix or relative_path.startswith(f"{prefix}/"):
                return thread
        elif ("*" in target or "?" in target) and fnmatch.fnmatch(relative_path, target):
            return thread
    return None


def evaluate(project_root: Path, paths: list[str] | None = None) -> AdmissionReport:
    report = AdmissionReport()
    additions = paths if paths is not None else staged_additions(project_root)
    if not additions:
        return report

    declared, declared_errors = bridge_authorized_paths(project_root)
    rules, rule_errors = load_exclusion_rules(project_root)
    report.errors.extend(declared_errors)
    report.errors.extend(rule_errors)

    for relative_path in additions:
        thread = matches_declared(relative_path, declared)
        if thread is not None:
            report.authorized[relative_path] = thread
            continue
        classification = registry_classification(relative_path, project_root)
        if classification is not None:
            report.registered[relative_path] = classification
            continue
        matched_rule = next((rule for rule in rules if rule.matches(relative_path)), None)
        if matched_rule is not None:
            report.excluded[relative_path] = matched_rule.id
            continue
        report.unresolved.append(relative_path)
    return report


def render(report: AdmissionReport) -> str:
    payload = report.to_dict()
    lines: list[str] = ["## Staged Artifact Admission (WI-5699; Phase 1 advisory)"]
    lines.append(f"- authorized: {len(payload['authorized'])}")
    lines.append(f"- registered: {len(payload['registered'])}")
    lines.append(f"- excluded:   {len(payload['excluded'])}")
    lines.append(f"- unresolved: {len(payload['unresolved'])}")
    for path, thread in payload["authorized"].items():
        lines.append(f"  AUTHORIZED  {path}  <- {thread}")
    for path, classification in payload["registered"].items():
        lines.append(f"  REGISTERED  {path}  <- {classification}")
    for path, rule_id in payload["excluded"].items():
        lines.append(f"  EXCLUDED    {path}  <- rule {rule_id}")
    for path in payload["unresolved"]:
        lines.append(f"  UNRESOLVED  {path}")
    for error in payload["errors"]:
        lines.append(f"  ERROR       {error}")
    if payload["unresolved"]:
        lines.append("")
        lines.append(
            "Unresolved additions have no bridge target_paths coverage, no registry record, "
            "and no exclusion rule. Declare them in the authorizing proposal, register them, "
            "or add a reasoned exclusion rule. Phase 1 is advisory and does not block."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify staged additions by admission basis (advisory).")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--json", action="store_true", help="emit the machine-readable classification")
    parser.add_argument("--path", action="append", default=None, help="classify explicit paths instead of the index")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    explicit = [normalize(item) for item in args.path] if args.path else None
    report = evaluate(root, paths=explicit)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(render(report))
    # Phase 1 is advisory: always succeed.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
