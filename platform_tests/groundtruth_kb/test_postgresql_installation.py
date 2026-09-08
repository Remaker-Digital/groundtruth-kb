"""Native installation integrity and WAL recovery behavior, without live config discovery."""

from __future__ import annotations

import hashlib
import importlib.util
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "infrastructure" / "postgresql" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = _module("install")
archiver = _module("archive_wal")


def _archive(tmp_path, extra=None):
    target = tmp_path / "package.zip"
    entries = {f"pgsql/bin/{binary}.exe": binary.encode() for binary in ("postgres", "pg_ctl", "initdb", "psql")}
    entries.update({"pgsql/pgAdmin 4/admin.exe": b"unneeded", "pgsql/server_license.txt": b"license"})
    entries.update(extra or {})
    with zipfile.ZipFile(target, "w") as package:
        for name, content in entries.items():
            entry = zipfile.ZipInfo()
            entry.filename = name
            package.writestr(entry, content)
    return target, hashlib.sha256(target.read_bytes()).hexdigest()


def test_server_extraction_excludes_unneeded_applications(tmp_path):
    archive, digest = _archive(tmp_path)
    target = tmp_path / "runtime"
    installer.extract_server(archive, target, digest)
    assert (target / "bin" / "postgres.exe").read_bytes() == b"postgres"
    assert (target / "server_license.txt").read_bytes() == b"license"
    assert not (target / "pgAdmin 4").exists()


def test_checksum_failure_has_no_installation_effect(tmp_path):
    archive, digest = _archive(tmp_path)
    target = tmp_path / "runtime"
    with pytest.raises(ValueError, match="checksum"):
        installer.extract_server(archive, target, "0" * 64)
    assert not target.exists()


@pytest.mark.parametrize(
    "name", ["pgsql/../escaped", "/absolute", "pgsql/bin/../../escaped", "pgsql/bin/file:stream", "pgsql/bin\\escaped"]
)
def test_archive_path_escape_is_rejected_before_extraction(tmp_path, name):
    archive, digest = _archive(tmp_path, {name: b"bad"})
    target = tmp_path / "runtime"
    with pytest.raises(ValueError, match="Unsafe path"):
        installer.extract_server(archive, target, digest)
    assert not target.exists()


def test_existing_runtime_is_preserved(tmp_path):
    archive, digest = _archive(tmp_path)
    target = tmp_path / "runtime"
    target.mkdir()
    (target / "foreign").write_bytes(b"keep")
    with pytest.raises(ValueError, match="already exists"):
        installer.extract_server(archive, target, digest)
    assert list(target.iterdir()) == [target / "foreign"]
    assert (target / "foreign").read_bytes() == b"keep"


def test_wal_archive_is_exact_and_idempotent(tmp_path):
    source, target = tmp_path / "source", tmp_path / "wal"
    source.write_bytes(b"complete WAL\x00" * 1000)
    archiver.archive(source, target)
    archiver.archive(source, target)
    assert target.read_bytes() == source.read_bytes()
    assert not list(tmp_path.glob("*.partial"))


def test_wal_archive_refuses_different_existing_bytes(tmp_path):
    source, target = tmp_path / "source", tmp_path / "wal"
    source.write_bytes(b"new")
    target.write_bytes(b"old")
    with pytest.raises(ValueError, match="different bytes"):
        archiver.archive(source, target)
    assert target.read_bytes() == b"old"


def test_concurrent_archive_retries_preserve_one_complete_file(tmp_path):
    source, target = tmp_path / "source", tmp_path / "wal"
    source.write_bytes(b"WAL" * 100_000)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: archiver.archive(source, target), range(8)))
    assert target.read_bytes() == source.read_bytes()
    assert not list(tmp_path.glob("*.partial"))


def test_failed_copy_leaves_no_partial_archive(tmp_path, monkeypatch):
    source, target = tmp_path / "source", tmp_path / "wal"
    source.write_bytes(b"WAL")

    def failed_copy(src, dst):
        dst.write(b"partial")
        raise OSError("disk full")

    monkeypatch.setattr(archiver.shutil, "copyfileobj", failed_copy)
    with pytest.raises(OSError, match="disk full"):
        archiver.archive(source, target)
    assert not target.exists()
    assert not list(tmp_path.glob("*.partial"))
