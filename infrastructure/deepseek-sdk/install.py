"""Install the pinned official DeepSeek Harness SDK beneath an explicit GT-KB root.

This is an operator bootstrap like the PostgreSQL installer: it creates a private
runtime environment from verified wheels and refuses an existing one. It handles no
credentials, registers no harness and starts no session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
RUNTIME_ENV = "runtime-env"


class InstallError(RuntimeError):
    pass


def load_release(source: Path = SOURCE) -> dict:
    return json.loads((source / "release.json").read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def obtain_wheel(entry: dict, wheel_dir: Path | None, download_dir: Path) -> Path:
    name = entry["url"].rsplit("/", 1)[-1]
    candidate = wheel_dir / name if wheel_dir else None
    if candidate is None or not candidate.is_file():
        candidate = download_dir / name
        with urllib.request.urlopen(entry["url"], timeout=120) as response, candidate.open("wb") as target:
            shutil.copyfileobj(response, target)
    actual = digest(candidate)
    if actual != entry["sha256"]:
        raise InstallError(f"{entry['name']} wheel digest {actual} differs from the pinned {entry['sha256']}")
    return candidate


def run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise InstallError(f"{command[0]} failed ({result.returncode}): {result.stderr.strip()[-2000:]}")
    return result.stdout


def install(root: Path, *, wheel_dir: Path | None, python: str, uv: str) -> dict:
    release = load_release()
    destination = root / "infrastructure" / "deepseek-sdk" / RUNTIME_ENV
    if destination.exists():
        raise InstallError(f"{destination} already exists; remove it deliberately before reinstalling")
    with tempfile.TemporaryDirectory(prefix="deepseek-sdk-wheels-") as temporary:
        download_dir = Path(temporary)
        wheels = [obtain_wheel(release[key], wheel_dir, download_dir) for key in ("sdk", "runtime")]
        run([uv, "venv", str(destination), "--python", python])
        interpreter = destination / "Scripts" / "python.exe"
        run([uv, "pip", "install", "--python", str(interpreter), "--no-deps", *map(str, wheels)])
        run([uv, "pip", "install", "--python", str(interpreter), *release["dependencies"]])
    executable = destination / release["runtime"]["executable"]
    if not executable.is_file():
        raise InstallError("The runtime executable is missing after installation")
    actual = digest(executable)
    if actual != release["runtime"]["executable_sha256"]:
        raise InstallError(f"Runtime executable digest {actual} differs from the pinned identity")
    frozen = [
        line.strip() for line in run([uv, "pip", "freeze", "--python", str(interpreter)]).splitlines() if line.strip()
    ]
    version = run([str(interpreter), "-c", "import sys;print(sys.version.split()[0])"]).strip()
    record = {
        "installed_at": datetime.now(UTC).isoformat(),
        "python": version,
        "sdk_sha256": release["sdk"]["sha256"],
        "runtime_sha256": release["runtime"]["sha256"],
        "executable": str(executable),
        "executable_sha256": actual,
        "packages": sorted(frozen),
    }
    (destination.parent / "installed.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="GT-KB root that receives infrastructure/deepseek-sdk")
    parser.add_argument("--wheel-dir", type=Path, default=None, help="Directory holding the pinned wheels (offline)")
    parser.add_argument("--python", default=sys.executable, help="Interpreter used to create the runtime environment")
    parser.add_argument("--uv", default="uv", help="uv executable")
    args = parser.parse_args()
    try:
        record = install(args.root.resolve(), wheel_dir=args.wheel_dir, python=args.python, uv=args.uv)
    except (InstallError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"installed": False, "error": str(error)}))
        return 1
    print(json.dumps({"installed": True, **record}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
