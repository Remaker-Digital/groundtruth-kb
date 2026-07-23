#!/usr/bin/env python3
"""Pre-commit gate for protected-surface GO or VERIFIED evidence."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.bridge_author_metadata import (  # noqa: E402
    author_metadata_gaps,
    extract_author_metadata,
    is_synthetic_session_context_id,
)
from scripts.bridge_lifecycle_resolver import (  # noqa: E402
    BridgeLifecycleResolutionError,
    resolve_bridge_lifecycle,
)
from scripts.bridge_review_independence import verdict_self_review_reason  # noqa: E402
from scripts.controlled_artifact_paths import (  # noqa: E402
    classify_controlled_artifact,
    is_versioned_bridge_status_file,
)
from scripts.gtkb_bridge_writer import BridgeComplianceError  # noqa: E402
from scripts.implementation_authorization import (  # noqa: E402
    AuthorizationError,
    extract_target_paths,
    list_named_packets,
    now_utc,
    packet_hash,
    packet_path_for_bridge,
    parse_iso,
    path_authorized,
    validate_packet_project_authorization_operation,
)
from scripts.verdict_evidence_anchor_preflight import validate_verdict_evidence_anchors  # noqa: E402

BY_BRIDGE_PACKETS_REL = Path(".gtkb-state/implementation-authorizations/by-bridge")
VERSIONED_BRIDGE_RE = re.compile(r"^bridge/.+-\d{3}\.md$")
VERSIONED_BRIDGE_CAPTURE_RE = re.compile(r"^bridge/(?P<bridge_id>[A-Za-z0-9][A-Za-z0-9_.-]*)-(?P<version>\d{3})\.md$")
STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|DEFERRED|WITHDRAWN|ADVISORY)$")
IMPLEMENTATION_REPORT_RE = re.compile(r"(?mi)^bridge_kind:\s*implementation_report\s*$")
MANIFEST_PATH_RE = re.compile(r"^-\s+`([^`]+)`\s*$")
GLOB_META_RE = re.compile(r"[*?\[\]]")
AUTHOR_SESSION_RE = re.compile(r"(?mi)^author_session_context_id:\s*(\S+)\s*$")
GIT_OBJECT_FORMATS = {"sha1": 40, "sha256": 64}
MAX_BLOB_BYTES = 64 * 1024 * 1024
MAX_TREE_BYTES = 512 * 1024 * 1024
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}

EXTRA_PROTECTED_PREFIXES = (".githooks/",)


class GateError(RuntimeError):
    """Raised when the commit gate cannot evaluate safely."""


@dataclass(frozen=True, slots=True)
class _IndexSnapshot:
    env: dict[str, str]
    head_oid: str
    object_format: str
    selected_paths: tuple[str, ...]
    status_by_path: dict[str, str]
    index_file: Path
    index_file_identity: _PathIdentity
    index_root_identity: _PathIdentity

    @property
    def added_paths(self) -> set[str]:
        return {path for path, status in self.status_by_path.items() if status == "A"}


@dataclass(frozen=True, slots=True)
class _ApprovedChain:
    proposal_path: str
    go_path: str
    report_path: str
    target_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _IndexEntry:
    mode: str
    oid: str
    rel_path: str


@dataclass(frozen=True, slots=True)
class _LedgerEntry:
    mode: str
    sha256: str
    size: int
    device: int
    inode: int
    link_count: int


@dataclass(frozen=True, slots=True)
class _PathIdentity:
    resolved_path: str
    device: int
    inode: int
    link_count: int
    size: int
    mode: int
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class _BridgeSnapshot:
    root: Path
    ledger: dict[str, _LedgerEntry]


def _normalize_rel(path_text: str) -> str:
    rel = path_text.strip().replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def _is_narrative_artifact(rel_path: str) -> bool:
    name = Path(rel_path).name
    if rel_path == "AGENTS.md":
        return True
    if name.startswith("CLAUDE") and name.endswith(".md"):
        return rel_path == name or rel_path.startswith("applications/")
    return rel_path.startswith(".claude/rules/") and rel_path.endswith(".md")


def is_protected_path(rel_path: str) -> bool:
    rel = _normalize_rel(rel_path)
    if _is_narrative_artifact(rel):
        return False
    if rel.startswith(EXTRA_PROTECTED_PREFIXES):
        return True
    if is_versioned_bridge_status_file(rel):
        return False
    return classify_controlled_artifact(rel).is_controlled


def _windows_authority_git_candidates() -> tuple[Path, ...]:
    candidates: list[Path] = [
        Path(r"C:\Program Files\Git\cmd\git.exe"),
        Path(r"C:\Program Files\Git\bin\git.exe"),
    ]
    try:
        import winreg

        access_modes = (winreg.KEY_READ | winreg.KEY_WOW64_64KEY, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
        for access in access_modes:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GitForWindows", 0, access) as key:
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            except OSError:
                continue
            if isinstance(install_path, str) and Path(install_path).is_absolute():
                candidates.extend(
                    (
                        Path(install_path) / "cmd" / "git.exe",
                        Path(install_path) / "bin" / "git.exe",
                    )
                )
    except (ImportError, AttributeError):
        pass
    return tuple(dict.fromkeys(candidates))


def _authority_git_candidates() -> tuple[Path, ...]:
    if os.name == "nt":
        return _windows_authority_git_candidates()
    return (Path("/usr/bin/git"), Path("/usr/local/bin/git"))


def _authority_bound_executable(candidate: Path) -> str | None:
    try:
        resolved = candidate.resolve(strict=True)
        if not resolved.is_file() or _path_is_linklike(candidate) or _path_is_linklike(resolved):
            return None
        if os.name != "nt":
            for path in (resolved, *resolved.parents):
                info = path.stat()
                if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                    return None
                if path == Path("/"):
                    break
    except OSError:
        return None
    return str(resolved)


@functools.lru_cache(maxsize=1)
def _trusted_git_executable() -> str:
    for candidate in _authority_git_candidates():
        executable = _authority_bound_executable(candidate)
        if executable is not None:
            return executable
    raise GateError("authority-bound Git executable is unavailable")


def _sanitized_subprocess_env(
    *,
    index_file: Path | None = None,
    isolate_python: bool = False,
) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "TMPDIR"):
        value = os.environ.get(key)
        if value:
            env[key] = value
    path_entries = [str(Path(_trusted_git_executable()).parent)]
    system_root = env.get("SYSTEMROOT") or env.get("WINDIR")
    if system_root:
        path_entries.append(str(Path(system_root) / "System32"))
    env.update(
        {
            "PATH": os.pathsep.join(dict.fromkeys(path_entries)),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    if index_file is not None:
        env["GIT_INDEX_FILE"] = str(index_file.resolve())
    if isolate_python:
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONNOUSERSITE"] = "1"
    return env


def _git_command(*args: str) -> list[str]:
    return [
        _trusted_git_executable(),
        "--no-replace-objects",
        "-c",
        "core.fsmonitor=false",
        "-c",
        f"core.hooksPath={os.devnull}",
        *args,
    ]


# WI-5658: bound every checker git subprocess so a blocked/slow git call fails
# closed instead of grinding unbounded (honors the git-subprocess timeout-bound
# invariant relied on by the finalizer / pre-commit gate).
_GIT_SUBPROCESS_TIMEOUT_SECONDS = 120


def _run_git(
    root: Path,
    *args: str,
    env: dict[str, str] | None = None,
    text: bool = False,
    timeout: float | None = _GIT_SUBPROCESS_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[Any]:
    try:
        return subprocess.run(
            _git_command(*args),
            cwd=root,
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            errors="replace" if text else None,
            check=False,
            env=env or _sanitized_subprocess_env(),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        message = f"git subprocess timed out after {timeout}s: {' '.join(str(a) for a in args)}"
        return subprocess.CompletedProcess(
            exc.cmd,
            returncode=124,
            stdout=exc.stdout if exc.stdout is not None else ("" if text else b""),
            stderr=message if text else message.encode("utf-8"),
        )


def _git_object_text(root: Path, object_spec: str, *, env: dict[str, str] | None = None) -> str:
    result = _run_git(root, "show", object_spec, env=env, text=True)
    if result.returncode != 0:
        raise GateError(f"could not read Git object {object_spec}: {result.stderr.strip()}")
    return result.stdout


def _resolve_head_oid(root: Path) -> str | None:
    result = _run_git(root, "rev-parse", "--verify", "HEAD^{commit}", text=True)
    if result.returncode != 0:
        return None
    oid = result.stdout.strip()
    return oid or None


def _resolve_object_format(root: Path) -> str:
    result = _run_git(root, "rev-parse", "--show-object-format", text=True)
    value = result.stdout.strip().lower() if result.returncode == 0 else ""
    if value not in GIT_OBJECT_FORMATS:
        raise GateError(f"unsupported or unreadable Git object format {value!r}")
    return value


def _decode_git_path(raw: bytes) -> str:
    return _validated_index_path(raw)


def _parse_staged_name_status(raw: bytes) -> tuple[tuple[str, ...], dict[str, str]]:
    tokens = raw.split(b"\0")
    if tokens and tokens[-1] == b"":
        tokens.pop()
    selected: list[str] = []
    statuses: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        status_text = tokens[index].decode("ascii", errors="strict")
        index += 1
        code = status_text[:1]
        if code in {"R", "C"}:
            if index + 1 >= len(tokens):
                raise GateError(f"truncated staged {code} record")
            old_path = _decode_git_path(tokens[index])
            new_path = _decode_git_path(tokens[index + 1])
            index += 2
            records = ((old_path, f"{code}-source"), (new_path, f"{code}-destination"))
        elif code in {"A", "M", "D"}:
            if index >= len(tokens):
                raise GateError(f"truncated staged {code} record")
            records = ((_decode_git_path(tokens[index]), code),)
            index += 1
        else:
            raise GateError(f"unsupported staged Git status {status_text!r}")

        for rel_path, path_status in records:
            if not rel_path or Path(rel_path).is_absolute() or ".." in Path(rel_path).parts:
                raise GateError(f"invalid staged path {rel_path!r}")
            if rel_path in statuses:
                raise GateError(f"duplicate staged path record {rel_path!r}")
            statuses[rel_path] = path_status
            selected.append(rel_path)
    return tuple(selected), statuses


def _validated_index_path(raw_path: bytes) -> str:
    try:
        decoded = raw_path.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise GateError("index contains a path that is not valid UTF-8") from exc
    if decoded != decoded.strip() or "\\" in decoded or any(ord(character) < 32 for character in decoded):
        raise GateError(f"index contains non-canonical path bytes {decoded!r}")
    rel_path = decoded
    raw_parts = rel_path.split("/")
    parts = Path(rel_path).parts
    if (
        not rel_path
        or Path(rel_path).is_absolute()
        or any(part in {"", ".", ".."} for part in raw_parts)
        or ".." in parts
        or parts[0].lower() == ".git"
        or any(":" in part for part in parts)
        or any(part.endswith((".", " ")) for part in raw_parts)
    ):
        raise GateError(f"index contains unsafe path {rel_path!r}")
    for part in raw_parts:
        stem = part.split(".", 1)[0].rstrip(" .").upper()
        if stem in WINDOWS_RESERVED_NAMES:
            raise GateError(f"index contains platform-reserved path component {part!r}")
    return rel_path


def _parse_index_inventory(raw: bytes) -> tuple[_IndexEntry, ...]:
    records = raw.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    entries: list[_IndexEntry] = []
    seen: set[str] = set()
    collision_keys: dict[str, str] = {}
    for record in records:
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode_raw, oid_raw, stage_raw = metadata.split(b" ", 2)
            mode = mode_raw.decode("ascii", errors="strict")
            oid = oid_raw.decode("ascii", errors="strict")
            stage = stage_raw.decode("ascii", errors="strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise GateError("malformed stage-0 index inventory record") from exc
        if stage != "0":
            raise GateError(f"unmerged index entry is not eligible for authorization materialization: stage {stage}")
        if mode not in {"100644", "100755"}:
            raise GateError(f"unsupported index mode {mode}; only regular files are eligible")
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", oid):
            raise GateError(f"invalid index object id {oid!r}")
        rel_path = _validated_index_path(raw_path)
        if rel_path in seen:
            raise GateError(f"duplicate stage-0 index path {rel_path!r}")
        collision_key = unicodedata.normalize("NFC", rel_path).casefold()
        collision = collision_keys.get(collision_key)
        if collision is not None and collision != rel_path:
            raise GateError(f"casefold or Unicode-normalized index path collision: {collision!r}, {rel_path!r}")
        seen.add(rel_path)
        collision_keys[collision_key] = rel_path
        entries.append(_IndexEntry(mode=mode, oid=oid, rel_path=rel_path))
    return tuple(entries)


def _path_is_linklike(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(reparse_flag and file_attributes & reparse_flag)


def _path_identity(path: Path, *, hash_bytes: bool = False) -> _PathIdentity:
    if _path_is_linklike(path):
        raise GateError(f"guarded authority path is symlink, junction, or reparse point: {path}")
    try:
        info = path.stat()
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise GateError(f"could not bind guarded authority path {path}: {exc}") from exc
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if hash_bytes else None
    return _PathIdentity(
        resolved_path=str(resolved),
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
        size=info.st_size,
        mode=stat.S_IMODE(info.st_mode),
        sha256=digest,
    )


def _verify_path_identity(path: Path, expected: _PathIdentity) -> None:
    actual = _path_identity(path, hash_bytes=expected.sha256 is not None)
    if actual != expected:
        raise GateError(f"guarded authority path identity or bytes drifted during evaluation: {path}")


@contextmanager
def _hold_paths_no_replace(paths: tuple[Path, ...]) -> Iterator[None]:
    handles: list[Any] = []
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
            create_file.argtypes = (
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.LPVOID,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.HANDLE,
            )
            create_file.restype = wintypes.HANDLE
            invalid_handle = wintypes.HANDLE(-1).value
            for path in paths:
                desired_access = 0x0080 | (0x80000000 if path.is_file() else 0)
                flags = 0x02000000 if path.is_dir() else 0x00000080
                handle = create_file(
                    str(path),
                    desired_access,
                    0x00000001,
                    None,
                    3,
                    flags,
                    None,
                )
                if handle == invalid_handle:
                    error = ctypes.get_last_error()
                    raise GateError(f"could not lock guarded authority path {path}: Windows error {error}")
                handles.append(handle)
            yield
        else:
            for path in paths:
                flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
                if path.is_dir():
                    flags |= getattr(os, "O_DIRECTORY", 0)
                handles.append(os.open(path, flags))
            yield
    finally:
        if os.name == "nt":
            if handles:
                import ctypes

                close_handle = ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle
                close_handle.argtypes = (ctypes.c_void_p,)
                close_handle.restype = ctypes.c_int
                for handle in reversed(handles):
                    close_handle(handle)
        else:
            for handle in reversed(handles):
                os.close(handle)


def _verify_index_snapshot(snapshot: _IndexSnapshot) -> None:
    _verify_path_identity(snapshot.index_file.parent, snapshot.index_root_identity)
    _verify_path_identity(snapshot.index_file, snapshot.index_file_identity)


@contextmanager
def _immutable_index_snapshot(snapshot: _IndexSnapshot) -> Iterator[None]:
    snapshot.index_file.chmod(0o444)
    snapshot.index_file.parent.chmod(0o555)
    guarded = (snapshot.index_file.parent, snapshot.index_file)
    try:
        _verify_index_snapshot(snapshot)
        with _hold_paths_no_replace(guarded):
            _verify_index_snapshot(snapshot)
            try:
                yield
            finally:
                _verify_index_snapshot(snapshot)
    finally:
        snapshot.index_file.parent.chmod(0o755)
        snapshot.index_file.chmod(0o644)


def _run_index_git(
    root: Path,
    snapshot: _IndexSnapshot,
    *args: str,
    text: bool = False,
) -> subprocess.CompletedProcess[Any]:
    _verify_index_snapshot(snapshot)
    result = _run_git(root, *args, env=snapshot.env, text=text)
    _verify_index_snapshot(snapshot)
    return result


def _scratch_root(root: Path) -> Path:
    root_resolved = root.resolve()
    if _path_is_linklike(root):
        raise GateError(f"project root is a symlink, junction, or reparse point: {root}")
    scratch = root / ".gtkb-state"
    if scratch.exists() and _path_is_linklike(scratch):
        raise GateError(f"scratch root is a symlink, junction, or reparse point: {scratch}")
    scratch.mkdir(parents=True, exist_ok=True)
    scratch_resolved = scratch.resolve()
    try:
        scratch_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise GateError(f"scratch root resolves outside the project root: {scratch_resolved}") from exc
    for ancestor in (scratch, *scratch.parents):
        if ancestor == root.parent:
            break
        if _path_is_linklike(ancestor):
            raise GateError(f"scratch ancestor is a symlink, junction, or reparse point: {ancestor}")
        if ancestor == root:
            break
    return scratch


def _index_entries(root: Path, snapshot: _IndexSnapshot) -> tuple[_IndexEntry, ...]:
    result = _run_index_git(root, snapshot, "ls-files", "--stage", "-z")
    if result.returncode != 0:
        raise GateError(f"could not enumerate copied index entries: {result.stderr!r}")
    return _parse_index_inventory(result.stdout)


def _parse_tree_inventory(raw: bytes) -> tuple[_IndexEntry, ...]:
    records = raw.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    index_records: list[bytes] = []
    for record in records:
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, object_type, oid = metadata.split(b" ", 2)
        except ValueError as exc:
            raise GateError("malformed committed tree inventory record") from exc
        if object_type != b"blob":
            raise GateError(f"unsupported committed tree object type {object_type!r}")
        index_records.append(mode + b" " + oid + b" 0\t" + raw_path)
    return _parse_index_inventory(b"\0".join(index_records) + (b"\0" if index_records else b""))


def _blob_ledger_entry(
    root: Path,
    destination: Path,
    entry: _IndexEntry,
    *,
    env: dict[str, str],
    object_format: str,
) -> _LedgerEntry:
    expected_oid_length = GIT_OBJECT_FORMATS[object_format]
    if len(entry.oid) != expected_oid_length:
        raise GateError(f"index object id length does not match repository {object_format} format for {entry.rel_path}")
    size_result = _run_git(root, "cat-file", "-s", entry.oid, env=env, text=True)
    try:
        expected_size = int(size_result.stdout.strip())
    except ValueError as exc:
        raise GateError(f"could not read raw blob size for {entry.rel_path}") from exc
    if size_result.returncode != 0 or expected_size < 0:
        raise GateError(f"could not read raw blob size for {entry.rel_path}: {size_result.stderr!r}")
    if expected_size > MAX_BLOB_BYTES:
        raise GateError(f"raw blob exceeds {MAX_BLOB_BYTES}-byte materialization limit: {entry.rel_path}")

    object_hasher = hashlib.new(object_format)
    object_hasher.update(f"blob {expected_size}\0".encode("ascii"))
    content_hasher = hashlib.sha256()
    actual_size = 0
    process = subprocess.Popen(
        _git_command("cat-file", "blob", entry.oid),
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        with destination.open("xb") as output:
            assert process.stdout is not None
            while chunk := process.stdout.read(1024 * 1024):
                actual_size += len(chunk)
                if actual_size > expected_size or actual_size > MAX_BLOB_BYTES:
                    process.kill()
                    raise GateError(f"raw blob exceeded declared or configured size for {entry.rel_path}")
                object_hasher.update(chunk)
                content_hasher.update(chunk)
                output.write(chunk)
        stderr = process.communicate(timeout=30)[1]
    except BaseException:
        if process.poll() is None:
            process.kill()
            process.communicate()
        raise
    if process.returncode != 0:
        raise GateError(f"could not read raw index blob {entry.oid} for {entry.rel_path}: {stderr!r}")
    if actual_size != expected_size:
        raise GateError(f"raw blob size mismatch for {entry.rel_path}: expected {expected_size}, got {actual_size}")
    if object_hasher.hexdigest().lower() != entry.oid.lower():
        raise GateError(f"raw blob bytes do not hash to indexed object id for {entry.rel_path}")
    if os.name != "nt":
        destination.chmod(0o755 if entry.mode == "100755" else 0o644)
    info = destination.stat()
    return _LedgerEntry(
        mode=entry.mode,
        sha256=content_hasher.hexdigest(),
        size=actual_size,
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
    )


def _materialize_entries(
    root: Path,
    snapshot_root: Path,
    entries: tuple[_IndexEntry, ...],
    *,
    env: dict[str, str],
    object_format: str,
) -> dict[str, _LedgerEntry]:
    ledger: dict[str, _LedgerEntry] = {}
    total_size = 0
    for entry in entries:
        destination = snapshot_root / entry.rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if _path_is_linklike(destination.parent):
            raise GateError(f"snapshot destination parent is link-like: {destination.parent}")
        resolved_parent = destination.parent.resolve()
        try:
            resolved_parent.relative_to(snapshot_root.resolve())
        except ValueError as exc:
            raise GateError(f"snapshot destination escapes materialization root: {entry.rel_path}") from exc
        ledger_entry = _blob_ledger_entry(
            root,
            destination,
            entry,
            env=env,
            object_format=object_format,
        )
        total_size += ledger_entry.size
        if total_size > MAX_TREE_BYTES:
            raise GateError(f"prospective tree exceeds {MAX_TREE_BYTES}-byte materialization limit")
        ledger[entry.rel_path] = ledger_entry
    return ledger


def _materialize_index_tree(
    root: Path,
    snapshot_root: Path,
    snapshot: _IndexSnapshot,
) -> dict[str, _LedgerEntry]:
    _verify_index_snapshot(snapshot)
    try:
        return _materialize_entries(
            root,
            snapshot_root,
            _index_entries(root, snapshot),
            env=snapshot.env,
            object_format=snapshot.object_format,
        )
    finally:
        _verify_index_snapshot(snapshot)


@contextmanager
def _index_snapshot(root: Path, head_oid: str | None = None) -> Iterator[_IndexSnapshot]:
    pinned_head = head_oid or _resolve_head_oid(root)
    if pinned_head is None:
        raise GateError("could not resolve HEAD^{commit} for staged authorization evaluation")
    object_format = _resolve_object_format(root)
    source_text = os.environ.get("GIT_INDEX_FILE")
    if source_text:
        source_index = Path(source_text)
        if not source_index.is_absolute():
            source_index = root / source_index
    else:
        resolved = _run_git(root, "rev-parse", "--git-path", "index", text=True)
        if resolved.returncode != 0:
            raise GateError(f"could not resolve Git index path: {resolved.stderr.strip()}")
        source_index = Path(resolved.stdout.strip())
        if not source_index.is_absolute():
            source_index = root / source_index
    try:
        index_bytes = source_index.read_bytes()
    except OSError as exc:
        raise GateError(f"could not snapshot Git index {source_index}: {exc}") from exc

    with tempfile.TemporaryDirectory(prefix=".gtkb-index-", dir=root) as tmp:
        snapshot_index = Path(tmp) / "index"
        snapshot_index.write_bytes(index_bytes)
        snapshot_index.chmod(0o444)
        snapshot_index.parent.chmod(0o555)
        env = _sanitized_subprocess_env(index_file=snapshot_index)
        snapshot = _IndexSnapshot(
            env=env,
            head_oid=pinned_head,
            object_format=object_format,
            selected_paths=(),
            status_by_path={},
            index_file=snapshot_index,
            index_file_identity=_path_identity(snapshot_index, hash_bytes=True),
            index_root_identity=_path_identity(snapshot_index.parent),
        )
        with _immutable_index_snapshot(snapshot):
            result = _run_index_git(
                root,
                snapshot,
                "diff",
                "--cached",
                "--name-status",
                "-z",
                "--find-renames",
                pinned_head,
            )
            if result.returncode != 0:
                raise GateError(f"could not enumerate staged paths from index snapshot: {result.stderr!r}")
            selected_paths, status_by_path = _parse_staged_name_status(result.stdout)
            snapshot = replace(
                snapshot,
                selected_paths=selected_paths,
                status_by_path=status_by_path,
            )
            _index_entries(root, snapshot)
            yield snapshot


def _staged_text(root: Path, rel_path: str, snapshot: _IndexSnapshot) -> str:
    result = _run_index_git(root, snapshot, "show", f":{rel_path}", text=True)
    if result.returncode != 0:
        raise GateError(f"could not read copied index path {rel_path}: {result.stderr.strip()}")
    return result.stdout


def _staged_or_worktree_text(root: Path, rel_path: str) -> str:
    staged = _run_git(root, "show", f":{rel_path}", text=True)
    if staged.returncode == 0:
        return staged.stdout
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"could not read {rel_path}: {exc}") from exc


@contextmanager
def _bridge_snapshot(
    root: Path,
    bridge_id: str,
    index_snapshot: _IndexSnapshot | None = None,
    head_oid: str | None = None,
    precomputed_head_entries: tuple[_IndexEntry, ...] | None = None,
) -> Iterator[_BridgeSnapshot]:
    pinned_head = index_snapshot.head_oid if index_snapshot is not None else head_oid
    if pinned_head is None:
        raise GateError("could not resolve pinned HEAD commit for bridge lifecycle evidence")
    scratch_root = _scratch_root(root)
    with tempfile.TemporaryDirectory(prefix=".gtkb-lifecycle-", dir=scratch_root) as tmp:
        snapshot_root = Path(tmp)
        if index_snapshot is not None:
            ledger = _materialize_index_tree(root, snapshot_root, index_snapshot)
            yield _BridgeSnapshot(root=snapshot_root, ledger=ledger)
            return

    if precomputed_head_entries is not None:
        # WI-5658: reuse the once-enumerated committed bridge inventory instead of
        # re-running ls-tree + re-parsing the full ~13k-file tree for every caller.
        head_entries = precomputed_head_entries
    else:
        head_listing = _run_git(root, "ls-tree", "-r", "-z", pinned_head, "--", "bridge")
        if head_listing.returncode != 0:
            raise GateError(f"could not enumerate committed bridge history: {head_listing.stderr!r}")

        exact_re = re.compile(rf"^bridge/{re.escape(bridge_id)}-\d{{3}}\.md$")
        head_entries = tuple(
            entry for entry in _parse_tree_inventory(head_listing.stdout) if exact_re.fullmatch(entry.rel_path)
        )
    with tempfile.TemporaryDirectory(prefix=".gtkb-lifecycle-", dir=scratch_root) as tmp:
        snapshot_root = Path(tmp)
        ledger = _materialize_entries(
            root,
            snapshot_root,
            head_entries,
            env=_sanitized_subprocess_env(),
            object_format=_resolve_object_format(root),
        )
        yield _BridgeSnapshot(root=snapshot_root, ledger=ledger)


def _verify_snapshot_ledger(snapshot: _BridgeSnapshot) -> None:
    actual_paths: set[str] = set()
    for candidate in snapshot.root.rglob("*"):
        rel_path = candidate.relative_to(snapshot.root).as_posix()
        if rel_path == ".gtkb-state" or rel_path.startswith(".gtkb-state/"):
            continue
        if _path_is_linklike(candidate):
            raise GateError(f"prospective audit tree contains a link-like path after audit: {rel_path}")
        if candidate.is_file():
            actual_paths.add(rel_path)
    expected_paths = set(snapshot.ledger)
    if actual_paths != expected_paths:
        raise GateError(
            "prospective audit tree file set drifted during audit"
            f"; missing={sorted(expected_paths - actual_paths)}"
            f"; extra={sorted(actual_paths - expected_paths)}"
        )
    for rel_path, expected in snapshot.ledger.items():
        candidate = snapshot.root / rel_path
        if not candidate.is_file() or _path_is_linklike(candidate):
            raise GateError(f"prospective audit authority path is no longer a regular file: {rel_path}")
        info = candidate.stat()
        if (
            info.st_size != expected.size
            or info.st_dev != expected.device
            or info.st_ino != expected.inode
            or info.st_nlink != expected.link_count
        ):
            raise GateError(f"prospective audit authority file identity drifted during audit: {rel_path}")
        actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual_hash != expected.sha256:
            raise GateError(f"prospective audit authority bytes drifted during audit: {rel_path}")
        if os.name != "nt":
            actual_executable = bool(info.st_mode & stat.S_IXUSR)
            if actual_executable != (expected.mode == "100755"):
                raise GateError(f"prospective audit authority mode drifted during audit: {rel_path}")


def _set_snapshot_read_only(snapshot: _BridgeSnapshot, read_only: bool) -> None:
    paths = sorted(
        (
            candidate
            for candidate in (snapshot.root, *snapshot.root.rglob("*"))
            if ".gtkb-state" not in candidate.relative_to(snapshot.root).parts
        ),
        key=lambda candidate: len(candidate.parts),
        reverse=read_only,
    )
    for candidate in paths:
        if _path_is_linklike(candidate):
            raise GateError(f"prospective audit tree contains a link-like path: {candidate}")
        if candidate.is_file():
            rel_path = candidate.relative_to(snapshot.root).as_posix()
            expected = snapshot.ledger.get(rel_path)
            if expected is None:
                raise GateError(f"prospective audit tree contains an untracked file: {rel_path}")
            mode = 0o444 if read_only else (0o755 if expected.mode == "100755" else 0o644)
            candidate.chmod(mode)
        elif candidate.is_dir():
            candidate.chmod(0o555 if read_only else 0o755)


def _snapshot_guard_paths(snapshot: _BridgeSnapshot) -> tuple[Path, ...]:
    descendants = tuple(
        candidate
        for candidate in snapshot.root.rglob("*")
        if ".gtkb-state" not in candidate.relative_to(snapshot.root).parts
    )
    return (snapshot.root.parent, snapshot.root, *sorted(descendants))


def _snapshot_guard_identities(snapshot: _BridgeSnapshot) -> dict[Path, _PathIdentity]:
    return {path: _path_identity(path, hash_bytes=path.is_file()) for path in _snapshot_guard_paths(snapshot)}


def _verify_snapshot_guard_identities(identities: dict[Path, _PathIdentity]) -> None:
    for path, expected in identities.items():
        _verify_path_identity(path, expected)


@contextmanager
def _immutable_snapshot(snapshot: _BridgeSnapshot) -> Iterator[None]:
    _verify_snapshot_ledger(snapshot)
    _set_snapshot_read_only(snapshot, True)
    identities = _snapshot_guard_identities(snapshot)
    try:
        with _hold_paths_no_replace(tuple(identities)):
            _verify_snapshot_guard_identities(identities)
            try:
                yield
            finally:
                _verify_snapshot_ledger(snapshot)
                _verify_snapshot_guard_identities(identities)
    finally:
        _set_snapshot_read_only(snapshot, False)
        _verify_snapshot_ledger(snapshot)


def _isolated_compliance_audit(
    *,
    snapshot_root: Path,
    candidate: Path,
    content: str,
) -> dict[str, object]:
    gate_path = snapshot_root / ".claude" / "hooks" / "bridge-compliance-gate.py"
    if not gate_path.is_file() or _path_is_linklike(gate_path):
        raise BridgeComplianceError(f"bridge-compliance gate is unavailable in prospective tree: {gate_path}")
    try:
        candidate_rel = candidate.relative_to(snapshot_root).as_posix()
    except ValueError as exc:
        raise BridgeComplianceError("bridge-compliance candidate escapes prospective tree") from exc
    payload = {
        "cwd": str(snapshot_root.resolve()),
        "tool_input": {"file_path": candidate_rel, "content": content},
    }
    audit_dir = snapshot_root / ".gtkb-state" / "compliance-audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="audit-", dir=audit_dir) as tmp:
        audit_output = Path(tmp) / "audit.json"
        audit_env = _sanitized_subprocess_env(isolate_python=True)
        audit_env["HOME"] = str(snapshot_root)
        audit_env["USERPROFILE"] = str(snapshot_root)
        result = subprocess.run(
            [
                str(Path(sys.executable).resolve()),
                "-I",
                "-B",
                "-S",
                str(gate_path),
                "--audit-only",
                "--audit-output",
                str(audit_output),
            ],
            cwd=snapshot_root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            env=audit_env,
        )
        if result.returncode != 0:
            raise BridgeComplianceError(
                "bridge-compliance audit failed to execute: "
                f"returncode={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        try:
            audit = json.loads(audit_output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeComplianceError("bridge-compliance audit did not produce readable JSON") from exc
    if not isinstance(audit, dict):
        raise BridgeComplianceError("bridge-compliance audit JSON root must be an object")
    if audit.get("decision") != "pass":
        reason = audit.get("reason") or "bridge-compliance audit denied the candidate bridge file"
        raise BridgeComplianceError(str(reason))
    return audit


def run_bridge_compliance_audit(
    *,
    file_path: Path,
    content: str,
    project_root: Path,
) -> dict[str, object]:
    """Run the project gate directly under the checker's isolated subprocess contract."""
    return _isolated_compliance_audit(
        snapshot_root=project_root,
        candidate=file_path,
        content=content,
    )


def _run_snapshot_compliance_audit(
    *,
    snapshot: _BridgeSnapshot,
    candidate_path: str,
    content: str,
) -> dict[str, object]:
    snapshot_root = snapshot.root
    candidate = snapshot_root / candidate_path
    _verify_snapshot_ledger(snapshot)
    quarantine_dir = snapshot_root / ".gtkb-state" / "audit-candidate"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    hidden_candidate = quarantine_dir / candidate.name
    try:
        candidate.replace(hidden_candidate)
    except OSError as exc:
        raise GateError(f"could not isolate compliance candidate {candidate_path}: {exc}") from exc
    _verify_snapshot_ledger(
        _BridgeSnapshot(
            root=snapshot.root,
            ledger={path: entry for path, entry in snapshot.ledger.items() if path != candidate_path},
        )
    )
    _set_snapshot_read_only(
        _BridgeSnapshot(
            root=snapshot.root,
            ledger={path: entry for path, entry in snapshot.ledger.items() if path != candidate_path},
        ),
        True,
    )
    try:
        audit = run_bridge_compliance_audit(
            file_path=candidate,
            content=content,
            project_root=snapshot_root,
        )
    finally:
        _set_snapshot_read_only(
            _BridgeSnapshot(
                root=snapshot.root,
                ledger={path: entry for path, entry in snapshot.ledger.items() if path != candidate_path},
            ),
            False,
        )
        hidden_candidate.replace(candidate)
    _verify_snapshot_ledger(snapshot)
    return audit


def _first_nonblank_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def _section_body(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _has_commit_finalization_evidence(text: str) -> bool:
    section = _section_body(text, "Commit Finalization Evidence")
    if not section:
        return False
    return "Same-transaction path set" in section and bool(re.search(r"(?m)^\s*-\s+`[^`]+`\s*$", section))


def _superseded_versioned_bridge(
    rel_path: str,
    snapshot: _IndexSnapshot | None,
) -> bool:
    """Return True when ``rel_path`` is a superseded predecessor within its numbered
    bridge chain in THIS commit transaction: a higher-numbered version of the same
    slug is staged in the current transaction (``snapshot.selected_paths``).

    Supersession is scoped to the staged transaction, never the ambient worktree,
    so an untracked or parked higher-numbered draft cannot false-positively mark a
    genuine latest terminal VERIFIED as superseded (which would both break a
    legitimate commit and suppress the terminal-VERIFIED finalization-evidence
    finding). A superseded predecessor is non-authoritative history: excluded from
    the VERIFIED-candidate count and from the finalization-evidence finding.
    Excluding it grants no authority: with zero live VERIFIED candidates a protected
    commit is simply not authorized (fail-closed), so only the single latest
    VERIFIED candidate ever carries authorization, and that candidate still receives
    full validation (including the resolver latest-strict-state check).
    """
    if snapshot is None:
        return False
    match = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(rel_path)
    if match is None:
        return False
    slug = match.group("bridge_id")
    version = int(match.group("version"))

    def _is_higher_sibling(candidate: str) -> bool:
        sibling = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(candidate)
        return sibling is not None and sibling.group("bridge_id") == slug and int(sibling.group("version")) > version

    return any(_is_higher_sibling(p) for p in snapshot.selected_paths)


def _verified_bridge_finalization_finding(
    root: Path,
    rel_path: str,
    snapshot: _IndexSnapshot | None,
) -> dict[str, Any] | None:
    if not VERSIONED_BRIDGE_RE.fullmatch(rel_path):
        return None
    if snapshot is not None and rel_path in snapshot.status_by_path:
        path_status = snapshot.status_by_path[rel_path]
        if path_status == "D" or path_status.endswith("-source"):
            return {
                "path": rel_path,
                "reason": "versioned bridge status artifact deletion cannot supply finalization evidence",
            }
        content = _staged_text(root, rel_path, snapshot)
    else:
        if not (root / rel_path).exists():
            return None
        content = _staged_or_worktree_text(root, rel_path)
    status = _first_nonblank_line(content)
    if status and not STATUS_RE.fullmatch(status):
        return {
            "path": rel_path,
            "reason": f"versioned bridge file has invalid status token {status!r}",
        }
    if status != "VERIFIED":
        return None
    if _superseded_versioned_bridge(rel_path, snapshot):
        # A superseded predecessor VERIFIED is committed as inert history; it is
        # not the live terminal state and needs no Commit Finalization Evidence.
        return None
    if _has_commit_finalization_evidence(content):
        return None
    return {
        "path": rel_path,
        "reason": "terminal VERIFIED bridge file lacks Commit Finalization Evidence with a same-transaction path set",
    }


def _load_live_go_evidence(root: Path) -> tuple[list[dict[str, Any]], list[str], int]:
    errors: list[str] = []
    try:
        packets = list_named_packets(root)
    except Exception as exc:  # noqa: BLE001 - fail closed on authorization subsystem errors.
        return [], [f"could not list implementation authorization packets: {exc}"], 0

    valid_packets: list[dict[str, Any]] = []
    for packet in packets:
        if packet.get("error"):
            errors.append(f"{packet.get('path', '<unknown-packet>')}: {packet['error']}")
            continue
        if packet.get("valid") is True:
            valid_packets.append(packet)
    return valid_packets, errors, len(packets)


def _live_go_authorization(
    packets: list[dict[str, Any]], errors: list[str], rel_path: str
) -> tuple[bool, str | None, list[str]]:
    for packet in packets:
        if path_authorized(packet, rel_path):
            return True, str(packet.get("bridge_id") or packet.get("path") or "<unknown-packet>"), errors
    return False, None, errors


def _version_by_path(resolution: Any, rel_path: str | None) -> Any | None:
    if not rel_path:
        return None
    return next((version for version in resolution.audit_versions if version.path == rel_path), None)


def _approved_chain(snapshot_root: Path, resolution: Any) -> _ApprovedChain:
    latest = resolution.latest_strict_state
    if latest.status != "VERIFIED" or not latest.responds_to:
        raise GateError("latest lifecycle state is not a report-linked VERIFIED verdict")
    report = _version_by_path(resolution, latest.responds_to)
    if report is None or report.status not in {"NEW", "REVISED"} or report.author_role != "prime-builder":
        raise GateError("VERIFIED verdict is not linked to a Prime implementation report")
    try:
        report_text = (snapshot_root / report.path).read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"could not read linked implementation report {report.path}: {exc}") from exc
    if IMPLEMENTATION_REPORT_RE.search(report_text) is None:
        raise GateError("linked Prime artifact is not an implementation report")

    go = _version_by_path(resolution, report.responds_to)
    if go is None or go.status != "GO" or go.author_role != "loyal-opposition":
        raise GateError("implementation report is not linked to its approving GO")
    proposal = _version_by_path(resolution, go.responds_to)
    if proposal is None or proposal.status not in {"NEW", "REVISED"} or proposal.author_role != "prime-builder":
        raise GateError("approving GO is not linked to a Prime proposal")
    try:
        proposal_text = (snapshot_root / proposal.path).read_text(encoding="utf-8")
        target_paths = tuple(_normalize_rel(path) for path in extract_target_paths(proposal_text))
    except (OSError, AuthorizationError) as exc:
        raise GateError(f"could not resolve approved proposal target scope: {exc}") from exc
    if not target_paths or len(target_paths) != len(set(target_paths)):
        raise GateError("approved proposal target scope is empty or duplicated")
    return _ApprovedChain(
        proposal_path=proposal.path,
        go_path=go.path,
        report_path=report.path,
        target_paths=target_paths,
    )


def _packet_target_paths(packet: dict[str, Any]) -> list[str] | None:
    raw_targets = packet.get("target_path_globs")
    if not isinstance(raw_targets, list) or not raw_targets:
        return None
    if any(not isinstance(target, str) or not target.strip() for target in raw_targets):
        return None
    return [_normalize_rel(target) for target in raw_targets]


def _packet_binding_errors(
    packet_path: Path,
    packet: dict[str, Any],
    bridge_id: str,
    chain: _ApprovedChain,
    *,
    require_schema_v3: bool,
) -> list[str]:
    errors: list[str] = []
    if packet_path.stem != bridge_id:
        errors.append(f"{bridge_id}: named packet filename does not match bridge id")
    if packet.get("bridge_id") != bridge_id:
        errors.append(f"{bridge_id}: named packet object names another bridge")
    allowed_schemas = {3} if require_schema_v3 else {2, 3}
    if packet.get("schema_version") not in allowed_schemas:
        errors.append(f"{bridge_id}: named packet has an unsupported schema")
    if packet.get("packet_hash") != packet_hash(packet):
        errors.append(f"{bridge_id}: named packet hash mismatch")
    if packet.get("proposal_file") != chain.proposal_path:
        errors.append(f"{bridge_id}: named packet is not bound to the resolver-approved proposal")
    if packet.get("go_file") != chain.go_path:
        errors.append(f"{bridge_id}: named packet is not bound to the resolver-approved GO")
    packet_targets = _packet_target_paths(packet)
    if packet_targets is None or tuple(packet_targets) != chain.target_paths:
        errors.append(f"{bridge_id}: named packet target scope differs from the resolver-approved proposal")
    return errors


def _committed_bridge_entries_by_id(root: Path, head_oid: str) -> dict[str, tuple[_IndexEntry, ...]]:
    """Enumerate the committed ``bridge/`` tree ONCE and group versioned entries by
    bridge slug, so callers can look up a chain's committed entries without
    re-running ``git ls-tree`` (and re-parsing the full ~13k-file inventory) per
    packet. This turns ``_load_verified_evidence`` from
    O(packets x committed-bridge-files) into O(packets + committed-bridge-files).
    Grouping by ``VERSIONED_BRIDGE_CAPTURE_RE`` bridge_id is equivalent to the
    prior per-bridge exact-slug filter.
    """
    listing = _run_git(root, "ls-tree", "-r", "-z", head_oid, "--", "bridge")
    if listing.returncode != 0:
        raise GateError(f"could not enumerate committed bridge history: {listing.stderr!r}")
    by_id: dict[str, list[_IndexEntry]] = {}
    for entry in _parse_tree_inventory(listing.stdout):
        match = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(entry.rel_path)
        if match is not None:
            by_id.setdefault(match.group("bridge_id"), []).append(entry)
    return {bridge_id: tuple(entries) for bridge_id, entries in by_id.items()}


def _load_verified_evidence(
    root: Path,
    head_oid: str | None = None,
) -> tuple[list[tuple[str, list[str]]], list[str], int]:
    errors: list[str] = []
    evidence: list[tuple[str, list[str]]] = []
    by_bridge_dir = root / BY_BRIDGE_PACKETS_REL
    if not by_bridge_dir.is_dir():
        return evidence, errors, 0

    packet_paths = sorted(by_bridge_dir.glob("*.json"))
    if packet_paths and head_oid is None:
        return evidence, ["terminal VERIFIED evidence cannot be read without a pinned HEAD commit"], len(packet_paths)
    # WI-5658: enumerate committed bridge history ONCE and group by bridge-id, so the
    # per-packet loop below is O(packets + committed-bridge-files) instead of
    # re-running ls-tree over all committed bridge files for each packet.
    head_entries_by_bridge = (
        _committed_bridge_entries_by_id(root, head_oid) if (packet_paths and head_oid is not None) else {}
    )
    for packet_path in packet_paths:
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{packet_path.relative_to(root).as_posix()}: corrupt or unreadable: {exc}")
            continue
        if not isinstance(packet, dict):
            errors.append(f"{packet_path.relative_to(root).as_posix()}: decoded packet root is not an object")
            continue
        bridge_id = packet.get("bridge_id")
        if not isinstance(bridge_id, str) or not bridge_id.strip():
            continue
        try:
            with _bridge_snapshot(
                root,
                bridge_id,
                head_oid=head_oid,
                precomputed_head_entries=head_entries_by_bridge.get(bridge_id, ()),
            ) as bridge_snapshot:
                snapshot_root = bridge_snapshot.root
                with _immutable_snapshot(bridge_snapshot):
                    resolution = resolve_bridge_lifecycle(snapshot_root, bridge_id)
                    latest = resolution.latest_strict_state
                    if latest.status != "VERIFIED":
                        continue
                    if resolution.blocking_diagnostics:
                        errors.append(f"{bridge_id}: terminal VERIFIED thread has blocking lifecycle diagnostics")
                        continue
                    chain = _approved_chain(snapshot_root, resolution)
        except (BridgeLifecycleResolutionError, GateError, OSError, ValueError) as exc:
            errors.append(f"{bridge_id}: could not read bridge thread: {exc}")
            continue
        binding_errors = _packet_binding_errors(packet_path, packet, bridge_id, chain, require_schema_v3=False)
        if binding_errors:
            errors.extend(binding_errors)
            continue
        evidence.append((bridge_id, list(chain.target_paths)))
    return evidence, errors, len(packet_paths)


def _verified_authorization(
    evidence: list[tuple[str, list[str]]], errors: list[str], rel_path: str
) -> tuple[bool, str | None, list[str]]:
    for bridge_id, target_paths in evidence:
        if path_authorized({"target_path_globs": target_paths}, rel_path):
            return True, bridge_id, errors
    return False, None, errors


def _manifest_path_error(root: Path, raw_path: str) -> str | None:
    if not raw_path:
        return "same-transaction manifest contains an empty path"
    if Path(raw_path).is_absolute() or re.match(r"^[A-Za-z]:", raw_path):
        return f"same-transaction manifest contains absolute path {raw_path!r}"
    if ".." in Path(raw_path).parts:
        return f"same-transaction manifest contains path escape {raw_path!r}"
    if raw_path == ".git" or raw_path.startswith(".git/"):
        return f"same-transaction manifest contains forbidden Git path {raw_path!r}"
    if GLOB_META_RE.search(raw_path):
        return f"same-transaction manifest contains glob path {raw_path!r}"
    if raw_path.endswith("/") or (root / raw_path).is_dir():
        return f"same-transaction manifest contains directory shorthand {raw_path!r}"
    try:
        _validated_index_path(raw_path.encode("utf-8"))
    except GateError:
        return f"same-transaction manifest contains non-canonical or unsafe path {raw_path!r}"
    return None


def _parse_transaction_manifest(root: Path, content: str) -> tuple[list[str], list[str]]:
    section = _section_body(content, "Commit Finalization Evidence")
    if not section:
        return [], ["VERIFIED candidate lacks Commit Finalization Evidence"]

    lines = [line.strip() for line in section.splitlines()]
    markers = [index for index, line in enumerate(lines) if line == "- Same-transaction path set:"]
    if len(markers) != 1:
        return [], ["VERIFIED candidate must contain exactly one Same-transaction path set marker"]

    paths: list[str] = []
    errors: list[str] = []
    for line in lines[markers[0] + 1 :]:
        if not line:
            if paths:
                break
            continue
        match = MANIFEST_PATH_RE.fullmatch(line)
        if match is None:
            break
        raw_path = match.group(1)
        path_error = _manifest_path_error(root, raw_path)
        if path_error:
            errors.append(path_error)
        paths.append(raw_path)

    if not paths:
        errors.append("VERIFIED candidate same-transaction path set is empty")
    duplicates = sorted({path for path in paths if paths.count(path) > 1})
    if duplicates:
        errors.append("same-transaction manifest contains duplicate path(s): " + ", ".join(duplicates))
    collision_keys: dict[str, str] = {}
    for path in paths:
        collision_key = unicodedata.normalize("NFC", path).casefold()
        prior = collision_keys.get(collision_key)
        if prior is not None and prior != path:
            errors.append(f"same-transaction manifest contains casefold or Unicode collision: {prior!r}, {path!r}")
        collision_keys[collision_key] = path
    return paths, errors


def _load_finalized_packet(
    root: Path,
    bridge_id: str,
    chain: _ApprovedChain,
    protected_paths: list[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        named_path = packet_path_for_bridge(root, bridge_id)
        packet = json.loads(named_path.read_text(encoding="utf-8"))
    except AuthorizationError as exc:
        return None, [f"{bridge_id}: implementation-start packet path is invalid: {exc}"]
    except FileNotFoundError:
        return None, [f"{bridge_id}: implementation-start packet is absent"]
    except json.JSONDecodeError as exc:
        return None, [f"{bridge_id}: implementation-start packet is not valid JSON: {exc}"]
    except OSError as exc:
        return None, [f"{bridge_id}: implementation-start packet is unreadable: {exc}"]

    if not isinstance(packet, dict):
        return None, [f"{bridge_id}: implementation-start packet root is not an object"]
    errors.extend(_packet_binding_errors(named_path, packet, bridge_id, chain, require_schema_v3=True))
    target_paths = _packet_target_paths(packet)
    try:
        if parse_iso(str(packet["expires_at"])) < now_utc():
            errors.append(f"{bridge_id}: implementation-start packet has expired")
    except (KeyError, TypeError, ValueError):
        errors.append(f"{bridge_id}: implementation-start packet has invalid expiry")

    implementation_start = packet.get("implementation_start")
    if not isinstance(implementation_start, dict):
        errors.append(f"{bridge_id}: implementation-start packet is not finalized")
    else:
        if implementation_start.get("schema_version") != 1:
            errors.append(f"{bridge_id}: implementation-start evidence has an unsupported schema")
        if implementation_start.get("bridge_id") != bridge_id:
            errors.append(f"{bridge_id}: finalized implementation-start names another bridge")
        if (
            not isinstance(implementation_start.get("finalized_at"), str)
            or not implementation_start["finalized_at"].strip()
        ):
            errors.append(f"{bridge_id}: implementation-start packet is not finalized")
        start_targets = implementation_start.get("target_path_globs")
        normalized_start_targets = (
            [_normalize_rel(target) for target in start_targets]
            if isinstance(start_targets, list)
            and all(isinstance(target, str) and target.strip() for target in start_targets)
            else None
        )
        if normalized_start_targets is None or target_paths is None or normalized_start_targets != target_paths:
            errors.append(f"{bridge_id}: finalized implementation-start target scope does not match packet scope")
        claim = implementation_start.get("work_intent_claim")
        provenance = implementation_start.get("worker_role_provenance")
        start_session = str(implementation_start.get("session_id") or "")
        if not start_session:
            errors.append(f"{bridge_id}: finalized implementation-start lacks a session id")
        if not isinstance(claim, dict):
            errors.append(f"{bridge_id}: finalized implementation-start lacks a work-intent claim")
        elif claim.get("thread_slug") != bridge_id:
            errors.append(f"{bridge_id}: finalized implementation-start claim does not match the bridge")
        else:
            if claim.get("session_id") != start_session:
                errors.append(f"{bridge_id}: finalized implementation-start claim session differs from start session")
            if claim.get("claim_kind") != "go_implementation":
                errors.append(f"{bridge_id}: finalized implementation-start claim kind is not go_implementation")
            if claim.get("acting_role") != "prime-builder":
                errors.append(f"{bridge_id}: finalized implementation-start claim acting role is not prime-builder")
        if not isinstance(provenance, dict):
            errors.append(f"{bridge_id}: finalized implementation-start lacks worker role provenance")
        else:
            if provenance.get("schema_version") != 1:
                errors.append(f"{bridge_id}: finalized implementation-start worker provenance schema is unsupported")
            if provenance.get("session_id") != start_session:
                errors.append(f"{bridge_id}: finalized implementation-start worker session differs from start session")
            if provenance.get("role") != "prime-builder":
                errors.append(f"{bridge_id}: finalized implementation-start worker role is not prime-builder")
        decision = implementation_start.get("project_authorization_decision")
        if not isinstance(decision, dict) or decision.get("allowed") is not True:
            errors.append(f"{bridge_id}: finalized implementation-start lacks an allowed project decision")
        pre_start_hash = implementation_start.get("pre_start_packet_hash")
        if not isinstance(pre_start_hash, str) or not pre_start_hash:
            errors.append(f"{bridge_id}: finalized implementation-start lacks a pre-start packet hash")
        else:
            pre_start = dict(packet)
            pre_start.pop("implementation_start", None)
            pre_start["schema_version"] = 2
            pre_start["packet_hash"] = pre_start_hash
            if packet_hash(pre_start) != pre_start_hash:
                errors.append(f"{bridge_id}: finalized implementation-start pre-start packet hash mismatch")

    project_authorization = packet.get("project_authorization")
    if not isinstance(project_authorization, dict):
        errors.append(f"{bridge_id}: finalized implementation-start lacks project authorization")
    elif isinstance(implementation_start, dict):
        claim = implementation_start.get("work_intent_claim")
        if isinstance(claim, dict) and claim.get("project_id") != project_authorization.get("project_id"):
            errors.append(f"{bridge_id}: implementation-start claim project differs from packet PAUTH")
        try:
            validate_packet_project_authorization_operation(
                root,
                packet,
                requested_operations=["protected_mutation"],
                target_paths=list(chain.target_paths),
            )
        except AuthorizationError as exc:
            errors.append(f"{bridge_id}: protected-mutation PAUTH validation failed: {exc}")

    if target_paths is not None:
        unauthorized_paths = [path for path in protected_paths if not path_authorized(packet, path)]
        if unauthorized_paths:
            errors.append(
                f"{bridge_id}: finalized implementation-start packet does not authorize protected staged path(s): "
                + ", ".join(unauthorized_paths)
            )
    return (packet if not errors else None), errors


def _single_author_session(content: str, label: str, errors: list[str]) -> str | None:
    session_ids = AUTHOR_SESSION_RE.findall(content)
    if len(session_ids) != 1:
        errors.append(f"{label} must contain exactly one author_session_context_id header")
        return None
    return session_ids[0]


def _load_transaction_verified_evidence(
    root: Path,
    protected_paths: list[str],
    snapshot: _IndexSnapshot,
) -> tuple[tuple[str, dict[str, Any]] | None, list[str], str | None]:
    selected_paths = list(snapshot.selected_paths)
    candidates: list[tuple[str, str]] = []
    for rel_path in selected_paths:
        if not VERSIONED_BRIDGE_RE.fullmatch(rel_path):
            continue
        status = snapshot.status_by_path[rel_path]
        if status == "D" or status.endswith("-source"):
            continue
        try:
            content = _staged_text(root, rel_path, snapshot)
        except GateError as exc:
            return None, [str(exc)], rel_path
        if _first_nonblank_line(content) == "VERIFIED":
            if _superseded_versioned_bridge(rel_path, snapshot):
                # Superseded predecessor VERIFIED is non-authoritative history,
                # not a live terminal candidate; only the latest-per-chain
                # VERIFIED counts toward the exactly-one-candidate clearance.
                continue
            candidates.append((rel_path, content))

    if not candidates:
        return None, [], None
    if len(candidates) != 1:
        paths = ", ".join(path for path, _ in candidates)
        return (
            None,
            [f"same-transaction clearance requires exactly one VERIFIED candidate; found {len(candidates)}: {paths}"],
            candidates[0][0],
        )

    candidate_path, content = candidates[0]
    errors: list[str] = []
    identity_match = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(candidate_path)
    if identity_match is None:
        return None, [f"VERIFIED candidate has invalid numbered bridge path: {candidate_path}"], candidate_path
    bridge_id = identity_match.group("bridge_id")

    if snapshot.status_by_path.get(candidate_path) != "A":
        errors.append("transaction-local VERIFIED candidate is not a Git-added staged file")

    manifest_paths, manifest_errors = _parse_transaction_manifest(root, content)
    errors.extend(manifest_errors)
    if len(selected_paths) != len(set(selected_paths)):
        errors.append("staged path set contains duplicate normalized paths")
    if set(manifest_paths) != set(selected_paths):
        missing = sorted(set(selected_paths) - set(manifest_paths))
        extra = sorted(set(manifest_paths) - set(selected_paths))
        errors.append(
            "same-transaction manifest does not equal the staged path set"
            + (f"; missing={missing}" if missing else "")
            + (f"; extra={extra}" if extra else "")
        )

    chain: _ApprovedChain | None = None
    report_text: str | None = None
    try:
        with _bridge_snapshot(root, bridge_id, snapshot) as bridge_snapshot:
            snapshot_root = bridge_snapshot.root
            _verify_snapshot_ledger(bridge_snapshot)
            with _immutable_snapshot(bridge_snapshot):
                try:
                    resolution = resolve_bridge_lifecycle(snapshot_root, bridge_id)
                except (BridgeLifecycleResolutionError, OSError, ValueError) as exc:
                    resolution = None
                    errors.append(f"{bridge_id}: VERIFIED candidate lifecycle is invalid: {exc}")
            _verify_snapshot_ledger(bridge_snapshot)

            if resolution is not None:
                latest = resolution.latest_strict_state
                if resolution.blocking_diagnostics:
                    errors.append(f"{bridge_id}: VERIFIED candidate lifecycle has blocking diagnostics")
                if latest.path != candidate_path or latest.status != "VERIFIED":
                    errors.append(f"{bridge_id}: VERIFIED candidate is not the exact latest strict lifecycle state")
                with _immutable_snapshot(bridge_snapshot):
                    try:
                        chain = _approved_chain(snapshot_root, resolution)
                        report_text = (snapshot_root / chain.report_path).read_text(encoding="utf-8")
                    except (GateError, OSError) as exc:
                        errors.append(f"{bridge_id}: VERIFIED candidate approved-chain validation failed: {exc}")
            _verify_snapshot_ledger(bridge_snapshot)

            with _immutable_snapshot(bridge_snapshot):
                anchor_violations = validate_verdict_evidence_anchors(content, project_root=snapshot_root)
            if anchor_violations:
                errors.append(f"{bridge_id}: VERIFIED candidate has invalid evidence anchors: {anchor_violations}")
            _verify_snapshot_ledger(bridge_snapshot)
            try:
                _run_snapshot_compliance_audit(
                    snapshot=bridge_snapshot,
                    candidate_path=candidate_path,
                    content=content,
                )
            except (BridgeComplianceError, OSError, subprocess.SubprocessError) as exc:
                errors.append(f"{bridge_id}: VERIFIED candidate bridge-compliance audit failed: {exc}")
            _verify_snapshot_ledger(bridge_snapshot)

            candidate_session = _single_author_session(content, f"{bridge_id} VERIFIED candidate", errors)
            report_session = (
                _single_author_session(report_text, f"{bridge_id} implementation report", errors)
                if report_text is not None
                else None
            )
            if candidate_session is not None and report_session is not None and candidate_session == report_session:
                errors.append(f"{bridge_id}: VERIFIED candidate is a same-session self-review")

            if chain is not None:
                with _immutable_snapshot(bridge_snapshot):
                    self_review_reason = verdict_self_review_reason(
                        content,
                        bridge_id,
                        snapshot_root,
                        expected_artifact_path=chain.report_path,
                    )
                if self_review_reason is not None:
                    errors.append(f"{bridge_id}: VERIFIED candidate review independence failed: {self_review_reason}")
            _verify_snapshot_ledger(bridge_snapshot)
    except GateError as exc:
        errors.append(str(exc))

    metadata = extract_author_metadata(content)
    gaps = author_metadata_gaps(metadata)
    if gaps:
        errors.append(f"{bridge_id}: VERIFIED candidate author metadata is incomplete: {', '.join(gaps)}")
    elif is_synthetic_session_context_id(metadata.get("author_session_context_id")):
        errors.append(f"{bridge_id}: VERIFIED candidate author session context is synthetic")

    if chain is None:
        packet = None
        errors.append(f"{bridge_id}: no resolver-approved chain exists for packet validation")
    else:
        packet, packet_errors = _load_finalized_packet(root, bridge_id, chain, protected_paths)
        errors.extend(packet_errors)

    if errors or packet is None:
        return None, errors, candidate_path
    return (bridge_id, packet), [], candidate_path


def _evaluate_protected_path(
    rel_path: str,
    *,
    live_go_packets: list[dict[str, Any]],
    live_go_errors: list[str],
    verified_evidence: list[tuple[str, list[str]]],
    verified_errors: list[str],
    transaction_evidence: tuple[str, dict[str, Any]] | None,
    transaction_errors: list[str],
    transaction_available: bool,
) -> dict[str, Any]:
    go_allowed, go_source, go_errors = _live_go_authorization(live_go_packets, live_go_errors, rel_path)
    if go_allowed:
        return {"path": rel_path, "status": "cleared", "evidence": "live_go_packet", "source": go_source}

    terminal_allowed, verified_source, terminal_errors = _verified_authorization(
        verified_evidence, verified_errors, rel_path
    )
    if terminal_allowed:
        return {
            "path": rel_path,
            "status": "cleared",
            "evidence": "terminal_verified_bridge_thread",
            "source": verified_source,
        }

    if transaction_evidence is not None:
        transaction_source, transaction_packet = transaction_evidence
        if path_authorized(transaction_packet, rel_path):
            return {
                "path": rel_path,
                "status": "cleared",
                "evidence": "transaction_local_verified_manifest",
                "source": transaction_source,
            }

    errors = go_errors + terminal_errors + transaction_errors
    evidence_routes = "live GO authorization packet or committed terminal VERIFIED bridge evidence"
    if transaction_available:
        evidence_routes += " or valid transaction-local VERIFIED evidence"
    finding: dict[str, Any] = {
        "path": rel_path,
        "reason": f"protected path lacks {evidence_routes}",
    }
    if errors:
        finding["evidence_errors"] = errors
    return finding


def _evaluate_selected(
    root: Path,
    selected_paths: list[str],
    snapshot: _IndexSnapshot | None,
    head_oid: str | None,
) -> dict[str, Any]:
    protected_paths = [path for path in selected_paths if is_protected_path(path)]
    skipped_unprotected = [path for path in selected_paths if path not in protected_paths]
    bridge_findings = [
        finding
        for path in selected_paths
        if (finding := _verified_bridge_finalization_finding(root, path, snapshot)) is not None
    ]

    if not protected_paths and not bridge_findings:
        return {
            "status": "pass",
            "findings": [],
            "cleared": [],
            "skipped_unprotected": skipped_unprotected,
            "protected_paths": [],
            "evidence_summary": {
                "live_go_packets_scanned": 0,
                "live_go_packets_valid": 0,
                "terminal_verified_packets_scanned": 0,
                "terminal_verified_threads_loaded": 0,
            },
        }

    live_go_packets: list[dict[str, Any]] = []
    live_go_errors: list[str] = []
    live_go_count = 0
    verified_evidence: list[tuple[str, list[str]]] = []
    verified_errors: list[str] = []
    verified_packet_count = 0
    transaction_evidence: tuple[str, dict[str, Any]] | None = None
    transaction_errors: list[str] = []
    transaction_candidate_path: str | None = None
    if protected_paths:
        live_go_packets, live_go_errors, live_go_count = _load_live_go_evidence(root)
        verified_evidence, verified_errors, verified_packet_count = _load_verified_evidence(root, head_oid=head_oid)
        if snapshot is not None:
            transaction_evidence, transaction_errors, transaction_candidate_path = _load_transaction_verified_evidence(
                root,
                protected_paths,
                snapshot,
            )

    findings: list[dict[str, Any]] = list(bridge_findings)
    if transaction_errors and transaction_candidate_path is not None:
        findings.append(
            {
                "path": transaction_candidate_path,
                "reason": "transaction-local VERIFIED candidate validation failed",
                "evidence_errors": transaction_errors,
            }
        )
    cleared: list[dict[str, Any]] = []
    for rel_path in protected_paths:
        result = _evaluate_protected_path(
            rel_path,
            live_go_packets=live_go_packets,
            live_go_errors=live_go_errors,
            verified_evidence=verified_evidence,
            verified_errors=verified_errors,
            transaction_evidence=transaction_evidence,
            transaction_errors=transaction_errors,
            transaction_available=snapshot is not None,
        )
        if result.get("status") == "cleared":
            cleared.append(result)
        else:
            findings.append(result)

    return {
        "status": "fail" if findings else "pass",
        "findings": findings,
        "cleared": cleared,
        "skipped_unprotected": skipped_unprotected,
        "protected_paths": protected_paths,
        "evidence_summary": {
            "live_go_packets_scanned": live_go_count,
            "live_go_packets_valid": len(live_go_packets),
            "terminal_verified_packets_scanned": verified_packet_count,
            "terminal_verified_threads_loaded": len(verified_evidence),
        },
    }


def evaluate(root: Path, *, paths: list[str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    head_oid = _resolve_head_oid(root)
    if paths is not None:
        selected_paths = [_normalize_rel(path) for path in paths]
        return _evaluate_selected(root, selected_paths, None, head_oid)
    with _index_snapshot(root, head_oid) as snapshot:
        return _evaluate_selected(root, list(snapshot.selected_paths), snapshot, head_oid)


def _format_human(result: dict[str, Any], *, transaction_available: bool = False) -> str:
    if result["status"] == "pass":
        if result["cleared"]:
            return f"PASS protected-commit authorization ({len(result['cleared'])} protected path(s) cleared)"
        return "PASS protected-commit authorization (no protected paths in staged set)"

    lines = ["FAIL protected-commit authorization"]
    for finding in result["findings"]:
        lines.append(f"  - {finding['path']}: {finding['reason']}")
        for error in finding.get("evidence_errors", []):
            lines.append(f"    evidence error: {error}")
    lines.append("")
    if transaction_available:
        lines.append(
            "Protected staged files require a live GO implementation packet, committed terminal VERIFIED bridge "
            "evidence, or transaction-local VERIFIED manifest evidence."
        )
    else:
        lines.append(
            "Protected files require either a live GO implementation packet or committed terminal VERIFIED evidence."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--staged", action="store_true", help="Read staged paths from git diff --cached.")
    selection.add_argument("--paths", nargs="*", help="Explicit paths to check.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    try:
        result = evaluate(args.project_root, paths=list(args.paths) if args.paths is not None else None)
    except GateError as exc:
        sys.stderr.write(f"protected-commit authorization gate error: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_human(result, transaction_available=args.staged))
        sys.stdout.write("\n")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
