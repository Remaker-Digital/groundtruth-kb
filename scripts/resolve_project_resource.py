#!/usr/bin/env python3
"""Resolve GT-KB external resource aliases against the governed registry."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "config" / "agent-control" / "project-resource-aliases.toml"
POINTER_PATH = PROJECT_ROOT / ".claude" / "rules" / "project-resource-aliases.toml"

ALLOWED_STATUSES = {
    "canonical",
    "canonical_unverified_url",
    "separate_project_not_gtkb",
    "historical",
    "unknown",
    "retired",
}
REQUIRED_RESOURCE_FIELDS = (
    "id",
    "kind",
    "name",
    "url",
    "identity",
    "aliases",
    "status",
    "authority",
    "verification_method",
    "last_verified",
    "release_blocking",
    "owner_confirmation_required",
    "notes",
    "related_specs",
    "related_deliberations",
)
CI_EVIDENCE_REQUIRED_FIELDS = ("resource_id", "repo", "branch", "event", "head_sha", "workflow", "job", "run_url")
UNQUALIFIED_RESOURCE_TERMS = (
    "the GitHub",
    "the repo",
    "repo",
    "repository",
    "CI",
    "GitHub Actions",
    "SonarCloud",
    "quality gate",
    "PyPI",
    "package",
    "docs site",
    "wiki",
    "issues",
    "Azure",
    "subscription",
    "production",
)


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load the governed resource registry."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError("registry root must be a TOML table")
    return data


def resource_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return registry resource rows."""
    rows = registry.get("resources", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def validate_registry(registry: dict[str, Any]) -> list[str]:
    """Validate the resource registry schema and lifecycle values."""
    errors: list[str] = []
    if registry.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    project = registry.get("project")
    if not isinstance(project, dict) or not project.get("canonical_name"):
        errors.append("project.canonical_name is required")
    rows = resource_rows(registry)
    if not rows:
        errors.append("at least one [[resources]] row is required")

    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("id") or f"row-{index}")
        for field in REQUIRED_RESOURCE_FIELDS:
            if field not in row:
                errors.append(f"{row_id}: missing required field {field}")
        if row_id in seen_ids:
            errors.append(f"{row_id}: duplicate resource id")
        seen_ids.add(row_id)
        status = row.get("status")
        if status not in ALLOWED_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_STATUSES))
            errors.append(f"{row_id}: status {status!r} must be one of {allowed}")
        aliases = row.get("aliases")
        if not isinstance(aliases, list) or not aliases or not all(isinstance(alias, str) for alias in aliases):
            errors.append(f"{row_id}: aliases must be a non-empty string list")
        for bool_field in ("release_blocking", "owner_confirmation_required"):
            if bool_field in row and not isinstance(row[bool_field], bool):
                errors.append(f"{row_id}: {bool_field} must be boolean")
        for list_field in ("related_specs", "related_deliberations"):
            if list_field in row and not isinstance(row[list_field], list):
                errors.append(f"{row_id}: {list_field} must be a list")
    return errors


def validate_pointer(pointer_path: Path = POINTER_PATH) -> list[str]:
    """Validate the startup-readable pointer file does not define a second registry."""
    if not pointer_path.exists():
        return [f"pointer file missing: {pointer_path}"]
    with pointer_path.open("rb") as handle:
        pointer = tomllib.load(handle)
    errors = []
    if pointer.get("schema_version") != 1:
        errors.append("pointer schema_version must be 1")
    if pointer.get("registry_path") != "config/agent-control/project-resource-aliases.toml":
        errors.append("pointer registry_path must target the governed registry")
    if "resources" in pointer:
        errors.append("pointer file must not define [[resources]]")
    return errors


def resolve_alias(
    alias: str,
    *,
    scope: str = "gtkb",
    allow_separate_project: bool = False,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve an alias to a registry row or return a deterministic warning/error."""
    registry = registry or load_registry()
    normalized = _normalize(alias)
    matches = [row for row in resource_rows(registry) if normalized in _match_keys(row)]
    if not matches:
        return {
            "status": "not_found",
            "alias": alias,
            "scope": scope,
            "message": "No resource matched the alias.",
            "candidates": [],
        }
    if len(matches) > 1:
        return {
            "status": "ambiguous",
            "alias": alias,
            "scope": scope,
            "message": "Alias matched multiple resources; use an explicit resource id or scope.",
            "candidates": [_public_row(row) for row in matches],
        }

    row = matches[0]
    resource_scope = _resource_scope(row)
    if scope not in {"gtkb", "agent-red", "explicit"}:
        return {
            "status": "invalid_scope",
            "alias": alias,
            "scope": scope,
            "message": "Scope must be gtkb, agent-red, or explicit.",
            "resource": _public_row(row),
        }
    if scope == "agent-red" and resource_scope != "agent-red":
        return {
            "status": "scope_mismatch",
            "alias": alias,
            "scope": scope,
            "message": "Alias resolved to a GT-KB resource, not an Agent Red resource.",
            "resource": _public_row(row),
        }
    if resource_scope == "agent-red" and scope == "gtkb" and not allow_separate_project:
        return {
            "status": "separate_project_warning",
            "alias": alias,
            "scope": scope,
            "message": "Alias resolved to a separate Agent Red resource; use --scope agent-red or --allow-separate-project.",
            "resource": _public_row(row),
        }
    return {
        "status": "resolved",
        "alias": alias,
        "scope": scope,
        "message": "Alias resolved.",
        "resource": _public_row(row),
    }


def check_git_remote_drift(
    registry: dict[str, Any] | None = None,
    *,
    repo_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Check that local git remotes match governed resource identities."""
    registry = registry or load_registry()
    gtkb_repo = _resource_by_id(registry, "gtkb.github.repo")
    expected_identity = str((gtkb_repo or {}).get("identity") or "")
    origin = _git_remote_url(repo_root, "origin")
    agent_red = _git_remote_url(repo_root, "agent-red")
    if origin is None:
        return {
            "status": "unknown",
            "message": "origin remote is unavailable",
            "expected_identity": expected_identity,
            "origin": None,
            "agent_red": agent_red,
        }
    normalized_origin = _normalize_repo_identity(origin)
    normalized_expected = _normalize_repo_identity(expected_identity)
    status = "pass" if normalized_origin == normalized_expected else "fail"
    message = "origin remote matches governed GT-KB repo" if status == "pass" else "origin remote drift detected"
    return {
        "status": status,
        "message": message,
        "expected_identity": expected_identity,
        "origin": origin,
        "agent_red": agent_red,
    }


def validate_ci_evidence(evidence: dict[str, Any], registry: dict[str, Any] | None = None) -> list[str]:
    """Validate exact CI evidence binding for release or bridge evidence rows."""
    registry = registry or load_registry()
    errors = [f"missing CI evidence field {field}" for field in CI_EVIDENCE_REQUIRED_FIELDS if not evidence.get(field)]
    repo = str(evidence.get("repo") or "")
    head_sha = str(evidence.get("head_sha") or "")
    run_url = str(evidence.get("run_url") or "")
    gtkb_repo = _resource_by_id(registry, "gtkb.github.repo")
    expected_repo = str((gtkb_repo or {}).get("identity") or "")
    if expected_repo and repo and _normalize_repo_identity(repo) != _normalize_repo_identity(expected_repo):
        errors.append(f"repo {repo!r} does not match governed GT-KB repo {expected_repo!r}")
    if head_sha and not re.fullmatch(r"[0-9a-fA-F]{40}", head_sha):
        errors.append("head_sha must be the full 40-character commit SHA")
    if run_url and not run_url.startswith("https://github.com/"):
        errors.append("run_url must be an exact GitHub run URL")
    if run_url and repo and _normalize_repo_identity(repo) not in _normalize_repo_identity(run_url):
        errors.append("run_url must include the exact repo identity")
    if evidence.get("resource_id") not in {"gtkb.github.actions", "gtkb.github.repo"}:
        errors.append("resource_id must bind CI evidence to gtkb.github.actions or gtkb.github.repo")
    return errors


def scan_text_for_unqualified_terms(text: str, *, path: str | Path = "<memory>") -> list[dict[str, Any]]:
    """Return warning-level findings for high-risk unqualified resource terms."""
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if _line_has_explicit_resource_binding(line):
            continue
        for term in UNQUALIFIED_RESOURCE_TERMS:
            if _term_present(line, term):
                findings.append(
                    {
                        "status": "warning",
                        "path": str(path),
                        "line": line_number,
                        "term": term,
                        "message": "Unqualified external resource term; bind new release evidence to a resource_id.",
                    }
                )
                break
    return findings


def _resource_by_id(registry: dict[str, Any], resource_id: str) -> dict[str, Any] | None:
    for row in resource_rows(registry):
        if row.get("id") == resource_id:
            return row
    return None


def _public_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "kind": row.get("kind"),
        "name": row.get("name"),
        "url": row.get("url"),
        "identity": row.get("identity"),
        "status": row.get("status"),
        "release_blocking": row.get("release_blocking"),
        "owner_confirmation_required": row.get("owner_confirmation_required"),
    }


def _match_keys(row: dict[str, Any]) -> set[str]:
    keys = {_normalize(str(row.get(field) or "")) for field in ("id", "name", "identity")}
    keys.update(_normalize(alias) for alias in row.get("aliases", []) if isinstance(alias, str))
    keys.discard("")
    return keys


def _resource_scope(row: dict[str, Any]) -> str:
    status = str(row.get("status") or "")
    row_id = str(row.get("id") or "")
    if status.startswith("separate_project") or row_id.startswith("agentred."):
        return "agent-red"
    return "gtkb"


def _git_remote_url(repo_root: Path, remote: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote],
            cwd=repo_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def _normalize_repo_identity(value: str) -> str:
    cleaned = value.strip().removesuffix(".git")
    cleaned = cleaned.removeprefix("https://github.com/")
    cleaned = cleaned.removeprefix("http://github.com/")
    cleaned = cleaned.removeprefix("git@github.com:")
    return cleaned.strip("/").lower()


def _line_has_explicit_resource_binding(line: str) -> bool:
    lowered = line.lower()
    return (
        "resource_id" in lowered
        or "gtkb." in lowered
        or "remaker-digital/groundtruth-kb" in lowered
        or "https://github.com/remaker-digital/groundtruth-kb" in lowered
    )


def _term_present(line: str, term: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", line, flags=re.IGNORECASE) is not None


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _exit_code_for_result(result: dict[str, Any]) -> int:
    status = result.get("status")
    if status in {"resolved", "pass"}:
        return 0
    if status in {"separate_project_warning", "unknown"}:
        return 2
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve GT-KB external resource aliases.")
    parser.add_argument("alias", nargs="?", help="Alias or resource id to resolve.")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="Registry TOML path.")
    parser.add_argument("--scope", default="gtkb", choices=("gtkb", "agent-red", "explicit"), help="Resolution scope.")
    parser.add_argument(
        "--allow-separate-project", action="store_true", help="Allow separate-project resource results."
    )
    parser.add_argument(
        "--check-git-remotes", action="store_true", help="Check local git remotes against the registry."
    )
    parser.add_argument(
        "--scan-file", type=Path, default=None, help="Warning-level scan for unqualified resource terms."
    )
    parser.add_argument("--validate-ci-evidence", type=Path, default=None, help="JSON CI evidence row to validate.")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    try:
        registry = load_registry(args.registry)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        result: dict[str, Any] = {"status": "error", "message": str(exc), "registry": str(args.registry)}
        _emit(result, json_output=args.json_output)
        return 1

    validation_errors = validate_registry(registry)
    pointer_errors = validate_pointer() if args.registry == REGISTRY_PATH else []
    if validation_errors or pointer_errors:
        result = {"status": "invalid_registry", "errors": [*validation_errors, *pointer_errors]}
        _emit(result, json_output=args.json_output)
        return 1

    if args.check_git_remotes:
        result = check_git_remote_drift(registry, repo_root=PROJECT_ROOT)
        _emit(result, json_output=args.json_output)
        return _exit_code_for_result(result)

    if args.scan_file:
        try:
            findings = scan_text_for_unqualified_terms(args.scan_file.read_text(encoding="utf-8"), path=args.scan_file)
        except OSError as exc:
            result = {"status": "error", "message": str(exc), "path": str(args.scan_file)}
            _emit(result, json_output=args.json_output)
            return 1
        result = {"status": "warning" if findings else "pass", "findings": findings}
        _emit(result, json_output=args.json_output)
        return 0

    if args.validate_ci_evidence:
        try:
            evidence = json.loads(args.validate_ci_evidence.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result = {"status": "error", "message": str(exc), "path": str(args.validate_ci_evidence)}
            _emit(result, json_output=args.json_output)
            return 1
        errors = validate_ci_evidence(evidence, registry)
        result = {"status": "pass" if not errors else "fail", "errors": errors}
        _emit(result, json_output=args.json_output)
        return 0 if not errors else 1

    if not args.alias:
        parser.error("alias is required unless --check-git-remotes, --scan-file, or --validate-ci-evidence is used")

    result = resolve_alias(
        args.alias,
        scope=args.scope,
        allow_separate_project=args.allow_separate_project,
        registry=registry,
    )
    _emit(result, json_output=args.json_output)
    return _exit_code_for_result(result)


def _emit(result: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"{result.get('status')}: {result.get('message', '')}")
    if "resource" in result:
        resource = result["resource"]
        print(f"  {resource.get('id')} -> {resource.get('identity')} ({resource.get('status')})")
    for candidate in result.get("candidates", []):
        print(f"  candidate: {candidate.get('id')} -> {candidate.get('identity')} ({candidate.get('status')})")
    for error in result.get("errors", []):
        print(f"  error: {error}")
    for finding in result.get("findings", []):
        print(f"  warning: {finding['path']}:{finding['line']} {finding['term']}")


if __name__ == "__main__":
    raise SystemExit(main())
