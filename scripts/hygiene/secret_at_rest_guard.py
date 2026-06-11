"""Secret-at-rest regression guard — FAB-02 / WI-4414 (HYG-019, HYG-020).

Read-only, value-safe assertion of the FAB-02 secret-at-rest invariants. The
guard NEVER reads or prints secret values: it inspects the replication-control
file (``.driveignore``), checks for the presence/absence of named files, and
does a textual scan of ``infrastructure/terraform/*.tf`` config for the partial
azurerm backend block. It never opens ``terraform.tfstate`` or ``.env.local``
*contents*.

Invariants asserted (derived from the FAB-02 specification links):

- ``GOV-ENV-LOCAL-AUTHORITY-001`` + HYG-020: ``.env.local`` is Drive-excluded.
- project-root-boundary Drive-sync exposure + HYG-019: ``*.tfstate`` /
  ``*.tfstate.*`` / ``*.tfvars`` / ``.terraform/`` are Drive-excluded, and no
  ``*.tfstate*.backup`` files remain on disk under ``infrastructure/terraform/``.
- Backend config secret-at-rest (FAB-02 verification follow-up, -004 NO-GO):
  the owner-filled ``infrastructure/terraform/backend.hcl`` (backend
  identifiers) is Drive-excluded, so the ``backend.hcl.example`` / runbook
  claim that it is "never Drive-synced" is mechanically true. The non-secret
  ``*.example`` template stays synced via the ``!*.example`` re-include.
- Backend migration scaffolding: a ``backend "azurerm"`` block exists in
  ``infrastructure/terraform/*.tf`` and the runbook + ``backend.hcl.example``
  are present.

Exit 0 when all invariants hold; exit 1 otherwise. The result dict is
JSON-serializable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Required .driveignore exclusion patterns. Each entry is
# (invariant_name, accepted_literal_patterns): the invariant holds when any one
# of the accepted literal patterns is an active (non-comment, non-blank) line in
# .driveignore. .driveignore is an independent cloud-replication surface from
# .gitignore; these patterns stop Google Drive for Desktop from uploading the
# secret-bearing files.
_REQUIRED_DRIVEIGNORE: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("env_local_excluded", (".env.local", ".env*")),
    ("tfstate_excluded", ("*.tfstate",)),
    ("tfstate_variants_excluded", ("*.tfstate.*",)),
    ("tfvars_excluded", ("*.tfvars",)),
    ("backend_hcl_excluded", ("infrastructure/terraform/backend.hcl",)),
)

_TERRAFORM_DIR = Path("infrastructure") / "terraform"


def _active_patterns(text: str) -> list[str]:
    """Return the active (non-comment, non-blank) lines of a gitignore-syntax file."""
    patterns: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def evaluate(project_root: Path | str) -> dict:
    """Evaluate the FAB-02 secret-at-rest invariants under ``project_root``.

    Returns a JSON-serializable dict: ``{"ok": bool, "project_root": str,
    "checks": [{"name", "passed", "detail"}], "failures": [name, ...]}``.
    """
    root = Path(project_root)
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    driveignore = root / ".driveignore"
    if driveignore.is_file():
        record("driveignore_present", True, ".driveignore present")
        patterns = _active_patterns(driveignore.read_text(encoding="utf-8", errors="replace"))
    else:
        record("driveignore_present", False, ".driveignore is missing")
        patterns = []

    pattern_set = set(patterns)
    for name, accepted in _REQUIRED_DRIVEIGNORE:
        matched = next((p for p in accepted if p in pattern_set), None)
        record(name, matched is not None, f"matched {matched!r}" if matched else f"missing one of {list(accepted)!r}")

    dot_terraform = any(p.endswith(".terraform/") for p in patterns)
    record(
        "dot_terraform_excluded",
        dot_terraform,
        ".terraform/ exclusion present" if dot_terraform else "no .terraform/ exclusion in .driveignore",
    )

    tf_dir = root / _TERRAFORM_DIR

    stale_backups = sorted(p.name for p in tf_dir.glob("*.tfstate*.backup")) if tf_dir.is_dir() else []
    record(
        "no_stale_tfstate_backups",
        not stale_backups,
        "no *.tfstate*.backup files present"
        if not stale_backups
        else f"stale tfstate backups present: {stale_backups}",
    )

    backend_found = False
    if tf_dir.is_dir():
        for tf_file in sorted(tf_dir.glob("*.tf")):
            try:
                content = tf_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if 'backend "azurerm"' in content:
                backend_found = True
                break
    record(
        "azurerm_backend_block_present",
        backend_found,
        'backend "azurerm" block found'
        if backend_found
        else 'no backend "azurerm" block in infrastructure/terraform/*.tf',
    )

    record(
        "backend_example_present",
        (tf_dir / "backend.hcl.example").is_file(),
        "backend.hcl.example present" if (tf_dir / "backend.hcl.example").is_file() else "backend.hcl.example missing",
    )
    record(
        "migration_runbook_present",
        (tf_dir / "STATE-MIGRATION-RUNBOOK.md").is_file(),
        "STATE-MIGRATION-RUNBOOK.md present"
        if (tf_dir / "STATE-MIGRATION-RUNBOOK.md").is_file()
        else "STATE-MIGRATION-RUNBOOK.md missing",
    )

    failures = [c["name"] for c in checks if not c["passed"]]
    return {"ok": not failures, "project_root": str(root), "checks": checks, "failures": failures}


def _default_root() -> Path:
    # scripts/hygiene/secret_at_rest_guard.py -> project root is two parents up.
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]) if args else _default_root()
    result = evaluate(root)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
