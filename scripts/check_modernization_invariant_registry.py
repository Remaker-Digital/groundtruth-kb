#!/usr/bin/env python3
"""Read-only, deterministic checker for the modernization hard-invariant registry.

WI-5152 — validates the WI-5158 Gate 1.25 28-outer-assertion map against
current formal-carrier versions, project/work-item state, deferred successors,
and the terminal WI-5153 fail-closed evaluator baseline. This checker performs
no mutation of any kind.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "config" / "governance" / "modernization-hard-invariants.toml"

ALLOWED_APPLICABILITY = {"MUST_APPLY", "DEFERRED_TO", "CONDITIONAL"}

CARRIER_EXPECTED_VERSIONS = {
    "ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001": 1,
    "REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001": 2,
    "DCL-GIT-BRANCH-BINDING-PROMOTION-001": 3,
    "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001": 1,
}

DEFERRED_TO = {
    "GIT-ADR-A5": "WI-5159",
    "GIT-REQ-A5": "WI-5159",
    "GIT-REQ-A7": "WI-5160",
    "BRANCH-BIND-A6": "WI-5159",
}

WI5153_VERIFIED_PATH = "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md"

REASON_OK = "ok"
REASON_STALE_CARRIER = "stale-carrier-version"
REASON_MISSING_CARRIER = "missing-carrier"
REASON_UNSUPPORTED_APPLICABILITY = "unsupported-applicability"
REASON_MISSING_DEFERRED = "missing-deferred-target"
REASON_MISSING_EVALUATOR = "missing-wi5153-evaluator"
REASON_COUNT_MISMATCH = "registry-count-mismatch"
REASON_DUPLICATE = "duplicate-entry"
REASON_CONDITIONAL_UNPROVEN = "conditional-a4-unproven"


class CheckerError(RuntimeError):
    """Raised when the registry cannot be evaluated safely."""


def _load_registry(path: Path) -> dict[str, Any]:
    try:
        import tomllib
    except ImportError:  # pragma: no cover - py<3.11 fallback
        tomllib = __import__("tomli")  # type: ignore
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError as exc:
        raise CheckerError(f"registry not found: {path}") from exc


def _canonical_hash(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


class SpecVersionProvider:
    """Resolve carrier versions from MemBase. Overridable in tests."""

    def resolve(self, spec_id: str) -> tuple[int | None, str | None]:
        return _spec_version_cli(spec_id)


def _spec_version_cli(spec_id: str) -> tuple[int | None, str | None]:
    import re
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "-m", "groundtruth_kb.cli", "spec", "show", spec_id, "--json"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
    except Exception:
        return None, None
    out = (result.stdout or "").strip()
    version_match = re.search(r'"version":\s*(\d+)', out)
    status_match = re.search(r'"status":\s*"([^"]+)"', out)
    if version_match is None:
        return None, (status_match.group(1) if status_match else None)
    try:
        return int(version_match.group(1)), (status_match.group(1) if status_match else None)
    except (TypeError, ValueError):
        return None, (status_match.group(1) if status_match else None)


def _wi5153_terminal() -> bool:
    path = PROJECT_ROOT / WI5153_VERIFIED_PATH
    if not path.is_file():
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="replace").lstrip()
    except OSError:
        return False
    return head.startswith("VERIFIED")


def evaluate(
    registry_path: Path | None = None,
    registry: dict[str, Any] | None = None,
    provider: SpecVersionProvider | None = None,
    terminal_evaluator: bool | None = None,
) -> dict[str, Any]:
    if registry is None:
        registry = _load_registry(registry_path or DEFAULT_REGISTRY_PATH)
    if provider is None:
        provider = SpecVersionProvider()
    if terminal_evaluator is None:
        terminal_evaluator = _wi5153_terminal()
    entries = registry.get("entries")
    if not isinstance(entries, list):
        raise CheckerError("registry has no entries list")

    reasons: list[dict[str, str]] = []
    seen: set[str] = set()

    for entry in entries:
        if not isinstance(entry, dict):
            reasons.append({"id": "<non-dict>", "reason": REASON_UNSUPPORTED_APPLICABILITY})
            continue
        eid = str(entry.get("id") or "")
        if not eid:
            reasons.append({"id": "<missing-id>", "reason": REASON_UNSUPPORTED_APPLICABILITY})
            continue
        if eid in seen:
            reasons.append({"id": eid, "reason": REASON_DUPLICATE})
        seen.add(eid)

        carrier = str(entry.get("carrier") or "")
        applicability = str(entry.get("applicability") or "")
        if applicability not in ALLOWED_APPLICABILITY:
            reasons.append({"id": eid, "reason": REASON_UNSUPPORTED_APPLICABILITY})
            continue

        if applicability == "MUST_APPLY":
            if carrier not in CARRIER_EXPECTED_VERSIONS:
                reasons.append({"id": eid, "reason": REASON_MISSING_CARRIER})
                continue
            live_version, live_status = provider.resolve(carrier)
            expected = CARRIER_EXPECTED_VERSIONS[carrier]
            if live_version is None:
                reasons.append({"id": eid, "reason": REASON_MISSING_CARRIER})
            elif live_version != expected or (live_status and live_status not in {"specified", "published", "active"}):
                reasons.append({"id": eid, "reason": REASON_STALE_CARRIER})
        elif applicability == "DEFERRED_TO":
            deferred = str(entry.get("deferred_to") or "")
            expected_deferred = DEFERRED_TO.get(eid)
            if expected_deferred is None or deferred != expected_deferred:
                reasons.append({"id": eid, "reason": REASON_MISSING_DEFERRED})
        elif applicability == "CONDITIONAL":
            if eid != "A4":
                reasons.append({"id": eid, "reason": REASON_UNSUPPORTED_APPLICABILITY})
            else:
                reasons.append({"id": eid, "reason": REASON_CONDITIONAL_UNPROVEN})

    if not terminal_evaluator:
        reasons.append({"id": "WI-5153", "reason": REASON_MISSING_EVALUATOR})

    must_count = sum(1 for e in entries if isinstance(e, dict) and e.get("applicability") == "MUST_APPLY")
    deferred_count = sum(1 for e in entries if isinstance(e, dict) and e.get("applicability") == "DEFERRED_TO")
    conditional_count = sum(1 for e in entries if isinstance(e, dict) and e.get("applicability") == "CONDITIONAL")

    if len(entries) != 28 or must_count != 23 or deferred_count != 4 or conditional_count != 1:
        reasons.append({"id": "registry", "reason": REASON_COUNT_MISMATCH})

    findings = [
        {"id": item["id"], "reason": item["reason"]}
        for item in reasons
        if item["reason"] not in {REASON_CONDITIONAL_UNPROVEN}
    ]
    status = "PASS" if not findings else "FAIL"

    return {
        "schema_version": 1,
        "registry_id": registry.get("registry_id"),
        "status": status,
        "entry_count": len(entries),
        "must_apply": must_count,
        "deferred_to": deferred_count,
        "conditional": conditional_count,
        "fail_closed": not findings,
        "findings": findings,
        "all_reasons": [{"id": item["id"], "reason": item["reason"]} for item in reasons],
        "registry_digest_sha256": _canonical_hash({"entries": entries}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    args = parser.parse_args(argv)
    try:
        payload = evaluate(registry_path=args.registry)
    except CheckerError as exc:
        payload = {
            "schema_version": 1,
            "status": "FAIL",
            "fail_closed": False,
            "findings": [{"id": "registry", "reason": str(exc)}],
        }
        if args.as_json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
        else:
            print("MODERNIZATION HARD-INVARIANT REGISTRY: FAIL")
            print(f"- {exc}")
        return 1
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print(f"MODERNIZATION HARD-INVARIANT REGISTRY: {payload['status']}")
        print(
            f"- entries: {payload['entry_count']} (MUST_APPLY {payload['must_apply']}, DEFERRED_TO {payload['deferred_to']}, CONDITIONAL {payload['conditional']})"
        )
        for finding in payload["findings"]:
            print(f"- {finding['id']}: {finding['reason']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
