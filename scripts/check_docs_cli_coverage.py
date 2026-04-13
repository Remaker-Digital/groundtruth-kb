#!/usr/bin/env python3
"""Check documentation coverage for CLI commands and prevent docs drift.

Verifies that:
1. Every gt CLI command appears in docs/reference/cli.md (Click introspection)
2. No gt project init snippets are missing PROJECT_NAME argument
3. MkDocs nav references existing files
4. Version consistency across docs, templates, README, CLI source
5. No bare PyPI-style install commands (must use GitHub @tag)
6. Python prerequisite matches pyproject.toml
7. gt --version expected output matches __version__
8. Install tag consistency (all @vX.Y.Z refs use the same tag)
9. ChromaDB install message shape in docs and CLI source

Exit code 0 = all checks pass, 1 = failures found.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
CLI_REF = DOCS_DIR / "reference" / "cli.md"
SRC_DIR = ROOT / "src" / "groundtruth_kb"
CLI_SOURCE = SRC_DIR / "cli.py"

# Expected minimum leaf commands — updated when commands are added/removed.
EXPECTED_MIN_COMMANDS = 14

# File extensions to scan for install references
_INSTALL_REF_EXTENSIONS = {".md", ".yml", ".yaml", ".py", ".toml", ".cfg", ".txt"}


def _collect_scannable_files() -> list[Path]:
    """Collect all user-facing files that may contain install references.

    Covers: docs/**/*.md, templates/**/* (md, yml, py, etc.),
    examples/**/* (docs-linked example content), README.md,
    src/groundtruth_kb/cli.py.
    """
    files: list[Path] = []
    # Docs
    for f in DOCS_DIR.rglob("*"):
        if f.is_file() and f.suffix in _INSTALL_REF_EXTENSIONS:
            files.append(f)
    # Templates (all user-facing extensions)
    templates_dir = ROOT / "templates"
    if templates_dir.exists():
        for f in templates_dir.rglob("*"):
            if f.is_file() and f.suffix in _INSTALL_REF_EXTENSIONS:
                files.append(f)
    # Examples (docs-linked example content)
    examples_dir = ROOT / "examples"
    if examples_dir.exists():
        for f in examples_dir.rglob("*"):
            if f.is_file() and f.suffix in _INSTALL_REF_EXTENSIONS:
                files.append(f)
    # Root README
    readme = ROOT / "README.md"
    if readme.exists():
        files.append(readme)
    # CLI source
    if CLI_SOURCE.exists():
        files.append(CLI_SOURCE)
    return files


def _is_changelog(filepath: Path) -> bool:
    """Return True for files that legitimately reference old versions."""
    name = filepath.name.lower()
    return "changelog" in name or "history" in name


def get_cli_commands() -> list[str]:
    """Extract leaf command names from Click group metadata.

    Recursively walks the Click command tree rooted at
    ``groundtruth_kb.cli.main`` and returns fully qualified command paths
    (e.g., ``project init``, ``deliberations rebuild-index``).
    """
    try:
        import click

        from groundtruth_kb.cli import main as cli_root
    except ImportError:
        return []

    commands: list[str] = []

    def _walk(group: click.BaseCommand, prefix: str = "") -> None:
        if isinstance(group, click.Group):
            for name in sorted(group.list_commands(click.Context(group))):
                cmd = group.get_command(click.Context(group), name)
                if cmd is None:
                    continue
                full = f"{prefix} {name}".strip() if prefix else name
                if isinstance(cmd, click.Group):
                    _walk(cmd, full)
                else:
                    commands.append(full)
        else:
            commands.append(prefix)

    _walk(cli_root)
    return commands


def check_cli_coverage() -> list[str]:
    """Check that CLI reference documents all commands."""
    failures: list[str] = []
    if not CLI_REF.exists():
        failures.append(f"CLI reference not found: {CLI_REF}")
        return failures

    cli_text = CLI_REF.read_text(encoding="utf-8").lower()
    commands = get_cli_commands()

    if not commands:
        failures.append(
            "CLI command enumeration returned 0 commands — cannot verify coverage (is groundtruth_kb installed?)"
        )
        return failures

    if len(commands) < EXPECTED_MIN_COMMANDS:
        failures.append(f"CLI enumeration found {len(commands)} commands, expected at least {EXPECTED_MIN_COMMANDS}")

    for cmd in commands:
        if f"gt {cmd}" not in cli_text:
            failures.append(f"CLI command 'gt {cmd}' not documented in {CLI_REF.name}")

    return failures


def check_project_init_snippets() -> list[str]:
    """Check that gt project init snippets include PROJECT_NAME."""
    failures: list[str] = []
    bad_pattern = re.compile(
        r"gt\s+project\s+init\s+--(?:profile|dir|owner)",
        re.IGNORECASE,
    )

    scan_paths: list[tuple[Path, Path]] = []
    for md_file in DOCS_DIR.rglob("*.md"):
        scan_paths.append((md_file, DOCS_DIR))
    for extra in [ROOT / "README.md", ROOT / "templates" / "README.md"]:
        if extra.exists():
            scan_paths.append((extra, ROOT))

    for filepath, base in scan_paths:
        text = filepath.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if bad_pattern.search(stripped):
                before_opts = re.search(
                    r"gt\s+project\s+init\s+(\S+)",
                    stripped,
                )
                if before_opts and before_opts.group(1).startswith("--"):
                    rel = filepath.relative_to(base)
                    failures.append(f"{rel}:{i}: gt project init missing PROJECT_NAME")

    return failures


def check_mkdocs_nav() -> list[str]:
    """Check that mkdocs.yml nav references point to existing files."""
    failures: list[str] = []
    mkdocs_yml = ROOT / "mkdocs.yml"
    if not mkdocs_yml.exists():
        return failures

    text = mkdocs_yml.read_text(encoding="utf-8")
    for match in re.finditer(r":\s+(\S+\.md)\s*$", text, re.MULTILINE):
        rel_path = match.group(1)
        full_path = DOCS_DIR / rel_path
        if not full_path.exists():
            failures.append(f"mkdocs.yml nav references missing file: docs/{rel_path}")

    return failures


def _get_package_version() -> str | None:
    """Read __version__ from groundtruth_kb.__init__."""
    init_file = SRC_DIR / "__init__.py"
    if not init_file.exists():
        return None
    text = init_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else None


def check_version_consistency() -> list[str]:
    """Check install refs use a consistent @vX.Y.Z tag across all scannable files."""
    failures: list[str] = []
    version = _get_package_version()
    if not version:
        failures.append("Could not read __version__ from src/groundtruth_kb/__init__.py")
        return failures

    expected_tag = f"v{version}"
    tag_pattern = re.compile(r"@v(\d+\.\d+\.\d+)")

    for filepath in _collect_scannable_files():
        if _is_changelog(filepath):
            continue
        text = filepath.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            for m in tag_pattern.finditer(line):
                found_tag = f"v{m.group(1)}"
                if found_tag != expected_tag:
                    rel = filepath.relative_to(ROOT)
                    failures.append(
                        f"{rel}:{i}: install tag @{found_tag} does not match current version @{expected_tag}"
                    )

    return failures


def check_no_bare_pypi_install() -> list[str]:
    """Check that all pip install groundtruth-kb lines use a GitHub direct reference.

    Every install command must contain '@' (the direct-reference marker),
    e.g. ``pip install "groundtruth-kb @ git+https://...@vX.Y.Z"``.
    Bare ``pip install groundtruth-kb`` and extras-only
    ``pip install "groundtruth-kb[search]"`` both fail because the package
    is not published to PyPI.
    """
    failures: list[str] = []
    # Match pip install with groundtruth-kb as the package argument (possibly
    # quoted, possibly with extras). Excludes comments containing the name.
    install_pattern = re.compile(r'pip\s+install\s+[^#]*["\']?groundtruth-kb(?:\[|\s|["\']|$)')

    for filepath in _collect_scannable_files():
        if _is_changelog(filepath):
            continue
        text = filepath.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            # Strip inline comments before matching
            code_part = line.split("#")[0] if "#" in line else line
            if install_pattern.search(code_part) and "@" not in code_part:
                rel = filepath.relative_to(ROOT)
                failures.append(
                    f"{rel}:{i}: pip install without GitHub direct reference "
                    f"(line must contain '@' for git+https install)"
                )

    return failures


def check_python_prerequisite() -> list[str]:
    """Check that documented Python version matches pyproject.toml."""
    failures: list[str] = []
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        return failures

    text = pyproject.read_text(encoding="utf-8")
    match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        return failures

    required = match.group(1)
    version_match = re.search(r"(\d+\.\d+)", required)
    if not version_match:
        return failures

    min_version = version_match.group(1)

    start_here = DOCS_DIR / "start-here.md"
    if start_here.exists():
        sh_text = start_here.read_text(encoding="utf-8")
        if f"Python {min_version}" not in sh_text:
            failures.append(
                f"docs/start-here.md: Python prerequisite should mention {min_version} "
                f"(pyproject.toml requires {required})"
            )

    return failures


def check_gt_version_output() -> list[str]:
    """Check that docs showing gt --version output match __version__."""
    failures: list[str] = []
    version = _get_package_version()
    if not version:
        return failures

    expected = f"gt, version {version}"

    start_here = DOCS_DIR / "start-here.md"
    if start_here.exists():
        text = start_here.read_text(encoding="utf-8")
        if expected not in text:
            failures.append(f"docs/start-here.md: expected gt --version output '{expected}' not found")

    return failures


def check_chromadb_install_message() -> list[str]:
    """Check ChromaDB install instructions use [search] extra in docs and CLI source."""
    failures: list[str] = []
    expected_fragment = "groundtruth-kb[search]"

    # Check reference docs
    for ref_file in [CLI_REF, DOCS_DIR / "reference" / "configuration.md"]:
        if not ref_file.exists():
            continue
        text = ref_file.read_text(encoding="utf-8")
        if ("chromadb" in text.lower() or "chroma" in text.lower()) and expected_fragment not in text:
            rel = ref_file.relative_to(DOCS_DIR)
            failures.append(f"docs/{rel}: mentions ChromaDB but does not use '{expected_fragment}' install syntax")

    # Check CLI source — the error message shown to users
    if CLI_SOURCE.exists():
        cli_text = CLI_SOURCE.read_text(encoding="utf-8")
        # Find the ChromaDB not-installed error message
        if "ChromaDB is not installed" in cli_text and expected_fragment not in cli_text:
            failures.append(
                f"src/groundtruth_kb/cli.py: ChromaDB install error message "
                f"does not use '{expected_fragment}' install syntax"
            )

    return failures


def main() -> int:
    """Run all documentation checks."""
    all_failures: list[str] = []
    checks = [
        ("CLI command coverage", check_cli_coverage),
        ("gt project init snippets", check_project_init_snippets),
        ("mkdocs.yml nav references", check_mkdocs_nav),
        ("version consistency", check_version_consistency),
        ("bare PyPI install detection", check_no_bare_pypi_install),
        ("Python prerequisite", check_python_prerequisite),
        ("gt --version output", check_gt_version_output),
        ("ChromaDB install message", check_chromadb_install_message),
    ]

    for name, check_fn in checks:
        print(f"Checking {name}...")
        all_failures.extend(check_fn())

    if all_failures:
        print(f"\n{len(all_failures)} documentation issue(s) found:\n")
        for f in all_failures:
            print(f"  FAIL: {f}")
        return 1

    print("\nAll documentation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
