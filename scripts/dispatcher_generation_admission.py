#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Dispatcher runtime generation admission service (WI-5429).

Admit dispatcher runtime generations only after terminal focused provenance:
every runtime-path delta since the previously admitted generation must be
covered by an atomic focused commit containing the relevant implementation/
report paths and a terminal VERIFIED verdict.

Bytes are read from Git objects — never from the mutable working tree.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

# --- constants ---

GENERATIONS_STATE_SUBDIR = (".gtkb-state", "dispatcher-generations")
LAST_ADMITTED_FILENAME = "last-admitted.json"
GENERATION_MANIFEST_FILENAME = "manifest.json"

# Runtime paths that define a dispatcher generation. Mirrors
# RUNTIME_GENERATION_RELATIVE_PATHS in gtkb_dispatcher_daemon.py.
# WI-5451 will later provide a governed executable dependency manifest;
# until then this inline list is the authoritative set.
DEFAULT_RUNTIME_PATHS: tuple[str, ...] = (
    "scripts/gtkb_dispatcher_daemon.py",
    "scripts/ensure_dispatcher_daemon.py",
    "scripts/dispatcher_runtime.py",
    "groundtruth-kb/src/groundtruth_kb/session/envelope.py",
)


# --- path helpers ---


def generations_dir(project_root: Path) -> Path:
    root = project_root.resolve()
    d = root
    for part in GENERATIONS_STATE_SUBDIR:
        d = d / part
    return d


def last_admitted_path(project_root: Path) -> Path:
    return generations_dir(project_root) / LAST_ADMITTED_FILENAME


def materialization_dir(project_root: Path, generation_id: str) -> Path:
    # generation_id looks like sha256:hexdigest
    safe_id = generation_id.replace(":", "-").replace("/", "-")
    return generations_dir(project_root) / safe_id


# --- last-admitted pointer ---


def read_last_admitted(project_root: Path) -> dict[str, Any] | None:
    """Return the last-admitted generation record, or None."""
    path = last_admitted_path(project_root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def write_last_admitted(project_root: Path, record: dict[str, Any]) -> None:
    """Atomically record a newly admitted generation as the current pointer."""
    _write_json_atomic(last_admitted_path(project_root), record)


# --- git operations ---


def _git(
    project_root: Path,
    *args: str,
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=timeout,
    )


def git_show_bytes(project_root: Path, commit: str, path: str) -> bytes | None:
    """Return the blob at ``commit:path`` from Git object storage."""
    proc = _git(project_root, "show", f"{commit}:{path}", timeout=15)
    if proc.returncode != 0:
        return None
    return proc.stdout.encode("utf-8", errors="surrogateescape")


def git_commit_exists(project_root: Path, commit: str) -> bool:
    proc = _git(project_root, "cat-file", "-t", commit, timeout=10)
    return proc.returncode == 0 and proc.stdout.strip() == "commit"


def git_changed_paths(
    project_root: Path, commit: str
) -> list[str]:
    """Return the paths changed in *commit* (no rename detection).

    Uses ``--root`` so root commits (no parent) are handled correctly.
    """
    proc = _git(
        project_root,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "--root",
        commit,
        timeout=10,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def git_log_range(
    project_root: Path,
    from_commit: str,
    to_commit: str,
) -> list[str]:
    """Return commit SHAs reachable from *to_commit* but not *from_commit*."""
    proc = _git(
        project_root,
        "log",
        "--pretty=format:%H",
        f"{from_commit}..{to_commit}",
        timeout=10,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def git_commit_subject(project_root: Path, commit: str) -> str | None:
    proc = _git(project_root, "log", "-1", "--pretty=format:%s", commit, timeout=10)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def git_merge_base(project_root: Path, a: str, b: str) -> str | None:
    proc = _git(project_root, "merge-base", a, b, timeout=10)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


# --- provenance validation ---


def _compute_generation_hash(
    project_root: Path,
    commit: str,
    runtime_paths: tuple[str, ...],
) -> str | None:
    """Compute the deterministic generation hash from Git object bytes."""
    digest = hashlib.sha256()
    for rp in sorted(runtime_paths):
        body = git_show_bytes(project_root, commit, rp)
        if body is None:
            return None
        digest.update(rp.encode("utf-8"))
        digest.update(b"\0")
        digest.update(body)
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _commit_contains_verified_verdict(
    project_root: Path, commit: str, changed: list[str]
) -> dict[str, Any]:
    """Check whether *commit* is a focused VERIFIED finalization commit.

    A VERIFIED commit must:
    - Touch at least one path under bridge/
    - Have a commit subject that includes 'verify' or 'VERIFIED'
    - Touch implementation or report paths alongside the verdict

    Returns diagnostic dict with 'verified' boolean and evidence.
    """
    subject = git_commit_subject(project_root, commit)
    bridge_files = [p for p in changed if p.startswith("bridge/")]
    non_bridge_files = [p for p in changed if not p.startswith("bridge/")]

    subject_ok = subject is not None and (
        "verify" in subject.lower() or "VERIFIED" in subject
    )

    result: dict[str, Any] = {
        "commit": commit,
        "subject": subject,
        "bridge_files": bridge_files,
        "non_bridge_files": non_bridge_files,
        "verified": bool(bridge_files and subject_ok),
        "reason": None,
    }

    if not bridge_files:
        result["reason"] = "no_bridge_files_in_commit"
    elif not subject_ok:
        result["reason"] = "commit_subject_not_verified"
    elif not non_bridge_files:
        result["reason"] = "verdict_only_commit_no_implementation_paths"

    return result


def validate_runtime_provenance(
    project_root: Path,
    candidate_commit: str,
    runtime_paths: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Validate that every runtime-path delta since the last admitted
    generation is covered by terminal focused VERIFIED commits.

    Returns a dict with:
        valid: bool
        generation: str | None  (the computed generation hash)
        errors: list[str]
        covered_paths: list[str]
        uncovered_paths: list[str]
        commits: list[dict]
    """
    if runtime_paths is None:
        runtime_paths = DEFAULT_RUNTIME_PATHS

    errors: list[str] = []
    commit_evidence: list[dict[str, Any]] = []

    # 1. Candidate must exist
    if not git_commit_exists(project_root, candidate_commit):
        return {
            "valid": False,
            "generation": None,
            "errors": ["candidate_commit_not_found"],
            "covered_paths": [],
            "uncovered_paths": list(runtime_paths),
            "commits": [],
        }

    # 2. Determine predecessor
    prev = read_last_admitted(project_root)
    predecessor_commit = prev.get("commit") if prev else None

    # 3. Determine the commit range to validate
    if predecessor_commit:
        if not git_commit_exists(project_root, predecessor_commit):
            errors.append("predecessor_commit_not_found")
            return {
                "valid": False,
                "generation": None,
                "errors": errors,
                "covered_paths": [],
                "uncovered_paths": list(runtime_paths),
                "commits": [],
            }
        # Same commit: no new commits to validate, generation unchanged
        if candidate_commit == predecessor_commit:
            return {
                "valid": True,
                "generation": _compute_generation_hash(project_root, candidate_commit, runtime_paths),
                "errors": [],
                "covered_paths": [],
                "uncovered_paths": [],
                "changed_runtime_paths": [],
                "commits": [],
                "predecessor_commit": predecessor_commit,
                "candidate_commit": candidate_commit,
                "commits_between_count": 0,
            }
        # Check if candidate is descendant of predecessor
        merge_base = git_merge_base(project_root, predecessor_commit, candidate_commit)
        if merge_base != predecessor_commit:
            errors.append(
                f"candidate_not_descendant_of_predecessor "
                f"(merge_base={merge_base}, predecessor={predecessor_commit})"
            )
            return {
                "valid": False,
                "generation": None,
                "errors": errors,
                "covered_paths": [],
                "uncovered_paths": list(runtime_paths),
                "commits": [],
            }
        commits_between = git_log_range(project_root, predecessor_commit, candidate_commit)
    else:
        # First admission: validate the candidate commit itself
        commits_between = [candidate_commit]

    if not commits_between:
        errors.append("no_commits_between_predecessor_and_candidate")
        return {
            "valid": False,
            "generation": None,
            "errors": errors,
            "covered_paths": [],
            "uncovered_paths": list(runtime_paths),
            "commits": [],
        }

    # 4. For each commit in the range, check it's a VERIFIED terminal commit
    all_covered: set[str] = set()
    for commit_sha in commits_between:
        changed = git_changed_paths(project_root, commit_sha)
        verdict = _commit_contains_verified_verdict(project_root, commit_sha, changed)
        commit_evidence.append(verdict)

        if not verdict["verified"]:
            errors.append(
                f"commit_{commit_sha[:8]}_not_verified: {verdict.get('reason', 'unknown')}"
            )
            continue

        # This commit covers any runtime paths it changed
        runtime_changed = [
            p for p in changed if p in runtime_paths
        ]
        all_covered.update(runtime_changed)

    # 5. Check which runtime paths differ between predecessor and candidate
    changed_runtime_paths: set[str] = set()
    for rp in runtime_paths:
        old_bytes: bytes | None = None
        new_bytes = git_show_bytes(project_root, candidate_commit, rp)
        if predecessor_commit:
            old_bytes = git_show_bytes(project_root, predecessor_commit, rp)
        if old_bytes != new_bytes:
            changed_runtime_paths.add(rp)

    uncovered = changed_runtime_paths - all_covered

    if uncovered:
        errors.append(
            f"runtime_paths_changed_but_not_covered_by_verified_commits: "
            f"{sorted(uncovered)}"
        )

    # 6. All runtime paths must exist at candidate
    missing_paths = []
    for rp in runtime_paths:
        if git_show_bytes(project_root, candidate_commit, rp) is None:
            missing_paths.append(rp)
    if missing_paths:
        errors.append(f"runtime_paths_missing_at_candidate: {sorted(missing_paths)}")

    valid = len(errors) == 0

    # 7. Compute generation hash from the candidate bytes
    generation_id: str | None = None
    if valid:
        generation_id = _compute_generation_hash(project_root, candidate_commit, runtime_paths)
        if generation_id is None:
            valid = False
            errors.append("generation_hash_computation_failed")

    return {
        "valid": valid,
        "generation": generation_id,
        "errors": errors,
        "covered_paths": sorted(all_covered),
        "uncovered_paths": sorted(uncovered),
        "changed_runtime_paths": sorted(changed_runtime_paths),
        "commits": commit_evidence,
        "predecessor_commit": predecessor_commit,
        "candidate_commit": candidate_commit,
        "commits_between_count": len(commits_between),
    }


# --- materialization ---


def materialize_generation(
    project_root: Path,
    commit: str,
    runtime_paths: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Materialize runtime files from *commit* into the generations directory.

    Returns dict with path-to-hash manifest, materialization directory,
    and any errors.
    """
    if runtime_paths is None:
        runtime_paths = DEFAULT_RUNTIME_PATHS

    # Compute generation identity first
    generation_id = _compute_generation_hash(project_root, commit, runtime_paths)
    if generation_id is None:
        errors.append("generation_hash_computation_failed")

    manifest: list[dict[str, Any]] = []
    for rp in runtime_paths:
        body = git_show_bytes(project_root, commit, rp)
        if body is None:
            errors.append(f"missing_at_commit: {rp}")
            continue
        file_hash = hashlib.sha256(body).hexdigest()
        manifest.append(
            {
                "path": rp,
                "sha256": file_hash,
                "size": len(body),
            }
        )
        body = git_show_bytes(project_root, commit, rp)
        if body is None:
            errors.append(f"missing_at_commit: {rp}")
            continue
        file_hash = hashlib.sha256(body).hexdigest()
        manifest.append(
            {
                "path": rp,
                "sha256": file_hash,
                "size": len(body),
            }
        )
        digest.update(rp.encode("utf-8"))
        digest.update(b"\0")
        digest.update(body)
        digest.update(b"\0")

    if errors:
        return {
            "materialized": False,
            "generation": None,
            "materialization_dir": None,
            "manifest": manifest,
            "errors": errors,
        }

    generation_id = f"sha256:{digest.hexdigest()}"
    mat_dir = materialization_dir(project_root, generation_id)

    # Write each file preserving relative paths
    written_paths: list[str] = []
    for entry in manifest:
        rp = entry["path"]
        body = git_show_bytes(project_root, commit, rp)
        if body is None:
            errors.append(f"materialize_read_failed: {rp}")
            continue
        dest = mat_dir / rp
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
        # Verify written bytes
        written = dest.read_bytes()
        if hashlib.sha256(written).hexdigest() != entry["sha256"]:
            errors.append(f"materialize_hash_mismatch: {rp}")
            continue
        written_paths.append(rp)

    if errors:
        return {
            "materialized": False,
            "generation": generation_id,
            "materialization_dir": str(mat_dir),
            "manifest": manifest,
            "written_paths": written_paths,
            "errors": errors,
        }

    # Write manifest into the materialization dir
    manifest_payload = {
        "generation": generation_id,
        "commit": commit,
        "materialized_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_paths": list(runtime_paths),
        "manifest": manifest,
    }
    _write_json_atomic(mat_dir / GENERATION_MANIFEST_FILENAME, manifest_payload)

    return {
        "materialized": True,
        "generation": generation_id,
        "materialization_dir": str(mat_dir),
        "manifest": manifest,
        "written_paths": written_paths,
        "errors": [],
    }


# --- admission ---


def admit_generation(
    project_root: Path,
    candidate_commit: str,
    runtime_paths: tuple[str, ...] | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Full admission pipeline: validate provenance, materialize, and record.

    Returns a detailed result dict.
    """
    if runtime_paths is None:
        runtime_paths = DEFAULT_RUNTIME_PATHS

    prev = read_last_admitted(project_root)

    # Step 1: provenance validation
    provenance = validate_runtime_provenance(
        project_root, candidate_commit, runtime_paths
    )

    if not provenance["valid"]:
        # If there is a predecessor and candidate is the same commit, the
        # provenance check naturally finds no commits between. Detect that
        # as "already admitted" before treating it as a failure.
        if (
            prev
            and candidate_commit == prev.get("commit")
            and not provenance["errors"]
        ):
            return {
                "admitted": False,
                "generation": prev.get("generation"),
                "reason": "generation_already_admitted",
                "provenance": provenance,
                "materialization": None,
            }
        return {
            "admitted": False,
            "generation": None,
            "reason": "provenance_validation_failed",
            "provenance": provenance,
            "materialization": None,
        }

    generation_id = provenance["generation"]

    # If same generation as last admitted, no-op (already handled above)
    if prev and prev.get("generation") == generation_id:
        return {
            "admitted": False,
            "generation": generation_id,
            "reason": "generation_already_admitted",
            "provenance": provenance,
            "materialization": None,
        }

    # Step 2: materialize
    materialization = materialize_generation(project_root, candidate_commit, runtime_paths)

    if not materialization["materialized"]:
        return {
            "admitted": False,
            "generation": generation_id,
            "reason": "materialization_failed",
            "provenance": provenance,
            "materialization": materialization,
        }

    # Step 3: verify materialized hashes match provenance generation
    mat_gen = materialization["generation"]
    if mat_gen != generation_id:
        return {
            "admitted": False,
            "generation": generation_id,
            "reason": "materialized_generation_hash_mismatch",
            "provenance": provenance,
            "materialization": materialization,
        }

    # Step 4: record
    if not dry_run:
        record = {
            "generation": generation_id,
            "commit": candidate_commit,
            "admitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime_paths": list(runtime_paths),
            "manifest": materialization["manifest"],
            "materialization_dir": materialization["materialization_dir"],
            "predecessor_generation": prev.get("generation") if prev else None,
            "predecessor_commit": provenance["predecessor_commit"],
        }
        write_last_admitted(project_root, record)

    return {
        "admitted": True,
        "generation": generation_id,
        "reason": "admitted",
        "provenance": provenance,
        "materialization": materialization,
        "predecessor_generation": prev.get("generation") if prev else None,
    }


# --- validation-only entrypoint for supervisor use ---


def candidate_admission_status(
    project_root: Path,
    runtime_paths: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Lightweight check: is there a current on-disk generation that is
    not yet admitted, and is the last-admitted generation still valid?

    Used by the supervisor to decide whether to recover from the admitted
    generation vs. fall back to working-tree source.
    """
    if runtime_paths is None:
        runtime_paths = DEFAULT_RUNTIME_PATHS

    last = read_last_admitted(project_root)

    # Check last-admitted materialization integrity
    last_materialization_ok = False
    if last:
        mat_dir = last.get("materialization_dir")
        if mat_dir and Path(mat_dir).is_dir():
            manifest_path = Path(mat_dir) / GENERATION_MANIFEST_FILENAME
            try:
                stored = json.loads(manifest_path.read_text(encoding="utf-8"))
                all_ok = True
                for entry in stored.get("manifest", []):
                    fpath = Path(mat_dir) / entry["path"]
                    if not fpath.is_file():
                        all_ok = False
                        break
                    body = fpath.read_bytes()
                    if hashlib.sha256(body).hexdigest() != entry.get("sha256"):
                        all_ok = False
                        break
                last_materialization_ok = all_ok
            except (OSError, json.JSONDecodeError, KeyError):
                last_materialization_ok = False

    # Compute current on-disk generation (mirroring _compute_runtime_generation)
    digest = hashlib.sha256()
    errors: list[str] = []
    for rp in runtime_paths:
        path = project_root.resolve() / rp
        try:
            body = path.read_bytes()
        except OSError as exc:
            errors.append(f"{rp}: {exc}")
            continue
        digest.update(rp.encode("utf-8"))
        digest.update(b"\0")
        digest.update(body)
        digest.update(b"\0")

    current_generation = None if errors else f"sha256:{digest.hexdigest()}"

    already_admitted = (
        last is not None
        and current_generation is not None
        and last.get("generation") == current_generation
    )

    return {
        "last_admitted_generation": last.get("generation") if last else None,
        "last_admitted_commit": last.get("commit") if last else None,
        "last_admitted_materialization_ok": last_materialization_ok,
        "current_working_tree_generation": current_generation,
        "current_already_admitted": already_admitted,
        "current_unfinalized": (
            current_generation is not None
            and not already_admitted
            and last is not None
        ),
        "no_admitted_generation_exists": last is None,
        "working_tree_errors": errors,
    }


# --- CLI ---


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Dispatcher runtime generation admission (WI-5429)."
    )
    sub = parser.add_subparsers(dest="command")

    status_p = sub.add_parser("status", help="Show admission status for current working tree.")
    status_p.add_argument("--project-root", type=Path, default=Path.cwd())

    admit_p = sub.add_parser("admit", help="Admit a candidate commit as a trusted generation.")
    admit_p.add_argument("--project-root", type=Path, default=Path.cwd())
    admit_p.add_argument("--commit", required=True, help="Candidate commit SHA.")
    admit_p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "status":
        result = candidate_admission_status(args.project_root.resolve())
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.command == "admit":
        result = admit_generation(
            args.project_root.resolve(),
            args.commit,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())