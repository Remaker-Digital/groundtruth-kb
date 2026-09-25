"""Install, verify or remove the pinned DeepSeek Harness Web UI (the GT-KB Home server) beneath an explicit GT-KB root.

An operator bootstrap like the DeepSeek SDK and PostgreSQL installers: it installs the npm package tree from the committed
lockfile with `npm ci`, which verifies every package against its recorded integrity hash, and refuses an existing tree.
The lockfile's own digest is pinned in release.json. Package install scripts do not run unless --allow-scripts is given.
The installed tree's identity (one SHA-256 over every file's relative path and content digest) is recorded in
installed.json; --verify recomputes it and refuses a changed or damaged tree. --uninstall removes the tree and its record
(stop the Home first), after which the same pinned inputs, from the registry or an --cache folder, reinstall it.
It handles no credentials, registers no harness and starts no server. Node.js is a prerequisite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
from datetime import UTC, datetime
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
NODE_MODULES = "node_modules"


class InstallError(RuntimeError):
    pass


def load_release(source: Path = SOURCE) -> dict:
    return json.loads((source / "release.json").read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def is_link(path: Path) -> bool:
    """A symbolic link or a Windows junction (any reparse point), detected without following it."""
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def tree_identity(tree: Path) -> dict:
    """SHA-256 over every file's relative path and content digest, in path order; links are refused, not followed."""
    lines = []
    total = 0
    for path in sorted(tree.rglob("*"), key=lambda item: item.relative_to(tree).as_posix()):
        if is_link(path):
            raise InstallError(f"the installed tree contains a link, which GT-KB does not install: {path}")
        if path.is_file():
            total += path.stat().st_size
            lines.append(f"{path.relative_to(tree).as_posix()}\0{digest(path)}\n")
    combined = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
    return {"tree_sha256": combined, "tree_files": len(lines), "tree_bytes": total}


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise InstallError(f"{Path(command[0]).name} failed ({result.returncode}): {result.stderr.strip()[-2000:]}")
    return result.stdout


def node_version(node: str, minimum_major: int) -> str:
    version = run([node, "--version"]).strip()
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", version)
    if match is None or int(match.group(1)) < minimum_major:
        raise InstallError(f"Node.js {minimum_major} or newer is required; found {version or 'nothing'}")
    return version


def install(root: Path, *, node: str, npm: str, cache: Path | None, allow_scripts: bool) -> dict:
    source = root / "infrastructure" / "deepseek-web"
    release = load_release(source)
    lockfile = source / "package-lock.json"
    if digest(lockfile) != release["lockfile_sha256"]:
        raise InstallError("package-lock.json differs from the pinned lockfile digest in release.json")
    destination = source / NODE_MODULES
    if destination.exists():
        raise InstallError(f"{destination} already exists; remove it deliberately before reinstalling")
    version = node_version(node, int(release["node_minimum_major"]))
    command = [npm, "ci", "--no-audit", "--no-fund"]
    if not allow_scripts:
        command.append("--ignore-scripts")
    if cache is not None:
        command += ["--offline", "--cache", str(cache)]
    run(command, cwd=source)
    installed = json.loads((destination / "@deepseek-ai" / "dsh" / "package.json").read_text(encoding="utf-8"))
    if installed.get("version") != release["version"]:
        raise InstallError(
            f"Installed @deepseek-ai/dsh {installed.get('version')} differs from the pinned {release['version']}"
        )
    lock = json.loads(lockfile.read_text(encoding="utf-8"))
    record = {
        "installed_at": datetime.now(UTC).isoformat(),
        "node": version,
        "package": release["package"],
        "version": release["version"],
        "lockfile_sha256": release["lockfile_sha256"],
        "packages": len(lock["packages"]) - 1,
        "install_scripts": "allowed" if allow_scripts else "skipped",
        "offline_cache": str(cache) if cache is not None else None,
        **tree_identity(destination),
    }
    (source / "installed.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def verify(root: Path) -> dict:
    """Refuse unless the installed tree still has the identity recorded when it was installed."""
    source = root / "infrastructure" / "deepseek-web"
    record_path = source / "installed.json"
    destination = source / NODE_MODULES
    if not record_path.is_file() or not destination.is_dir():
        raise InstallError("the Home server is not installed here")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    current = tree_identity(destination)
    if current["tree_sha256"] != record.get("tree_sha256"):
        raise InstallError(
            f"the installed tree differs from its recorded identity ({current['tree_files']} files now, "
            f"{record.get('tree_files')} recorded); uninstall and reinstall from the pinned inputs"
        )
    return {"version": record["version"], **current}


def uninstall(root: Path) -> dict:
    """Remove the installed tree and its record; the committed pins stay. Stop the Home first."""
    source = root / "infrastructure" / "deepseek-web"
    destination = source / NODE_MODULES
    if is_link(destination):
        raise InstallError(f"{destination} is a link; remove it deliberately, not through the uninstaller")
    removed = destination.is_dir()
    if removed:
        try:
            shutil.rmtree(destination)
        except OSError as error:
            raise InstallError(f"could not remove {destination} (is the Home still running?): {error}") from error
    (source / "installed.json").unlink(missing_ok=True)
    return {"removed": removed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="GT-KB root that holds infrastructure/deepseek-web")
    parser.add_argument("--node", default=shutil.which("node") or "node", help="Node.js executable")
    parser.add_argument("--npm", default=shutil.which("npm") or "npm", help="npm executable")
    parser.add_argument(
        "--cache", type=Path, default=None, help="npm cache holding the pinned packages (offline install)"
    )
    parser.add_argument("--allow-scripts", action="store_true", help="Run package install scripts (off by default)")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--verify", action="store_true", help="Check the installed tree against its recorded identity")
    action.add_argument("--uninstall", action="store_true", help="Remove the installed tree and its record")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    key = "verified" if args.verify else "uninstalled" if args.uninstall else "installed"
    try:
        if args.verify:
            record = verify(root)
        elif args.uninstall:
            record = uninstall(root)
        else:
            record = install(root, node=args.node, npm=args.npm, cache=args.cache, allow_scripts=args.allow_scripts)
    except (InstallError, OSError, json.JSONDecodeError, KeyError) as error:
        print(json.dumps({key: False, "error": str(error)}))
        return 1
    print(json.dumps({key: True, **record}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
