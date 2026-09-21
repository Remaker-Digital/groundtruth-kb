#!/usr/bin/env python3
"""Prove the declared operational-control set is complete and report what stays unresolved.

GHRP-DCL-CONTROL-A1 (DCL-CENTRAL-DYNAMIC-OPERATIONAL-CONTROLS-001) names this evaluator. For the selected root it
proves, from local files only (no authority request):

1. one typed value authority: ``config/governance/operational-controls.toml`` loads through the canonical loader,
   which has no environment, source-literal or cached fallback and refuses an invalid artifact visibly;
2. complete wiring of the declared set: every active control names a wired consumer whose module exists in the tree
   and references the key, and every key a wired consumer reads (the consumer contracts of
   ``operational_control_config``) is declared active; no orphan control, no undeclared consumer key;
3. invariant validation: every declared cross-key invariant holds for the live values;
4. calibration evidence: every active control cites a dated calibration record (``calibration:YYYY-MM-DD[:locator]``);
5. dynamic replacement: the governed diff route accepts the current bytes as a replacement with no change (the setter
   itself is not exercised; its mutex lives in the checkout's Git metadata directory, outside the governed tree).

It then REPORTS the inventory's unresolved population (``scripts/timer_inventory.py``: unclassified or ambiguous
production numeric uses, semantic completeness ``unproven``) without adjudicating it: the declared set can be complete
while the migration of every production literal (PROJECT-GTKB-TIMER-GOVERNANCE) is not.

Exit codes: 0 the declared set is complete (the unresolved count is printed, not judged, unless
``--fail-on-unresolved``); 1 a finding (orphan control, undeclared consumer key, unwired consumer module, invariant
violation, missing calibration evidence, replacement-route refusal) or ``--fail-on-unresolved`` with a nonzero count;
2 the catalog or the inventory cannot be evaluated (unavailable or invalid artifact, invalid root).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from groundtruth_kb.project import operational_control_config as occ

ASSERTION_ID = "GHRP-DCL-CONTROL-A1"
CALIBRATION_REF = re.compile(r"^calibration:(\d{4})-(\d{2})-(\d{2})(?::\S+)?$")
INVENTORY_SOURCE = Path(__file__).resolve().parent / "timer_inventory.py"
# Wired consumers: the modules whose typed-key reads operational_control_config enforces as consumer contracts, the
# keys each reads, and the names bound to those keys that a consumer may reference instead of the key literal.
WIRED_CONSUMERS: dict[str, dict[str, Any]] = {
    occ._REGISTRY_CONSUMER: {"keys": frozenset(occ.REGISTRY_CONTROL_UNITS), "tokens": ("REGISTRY_CONTROL_UNITS",)},
    occ._INVENTORY_CONSUMER: {
        "keys": frozenset({occ.INVENTORY_GIT_PROBE_CONTROL}),
        "tokens": ("INVENTORY_GIT_PROBE_CONTROL",),
    },
}


def consumer_module_path(consumer: str) -> Path:
    """Repository-relative source path of a dotted consumer name (package sources live under groundtruth-kb/src)."""
    parts = consumer.split(".")
    relative = Path(*parts).with_suffix(".py")
    return Path("groundtruth-kb/src") / relative if parts[0] == "groundtruth_kb" else relative


def _calibration_reference(refs: tuple[str, ...]) -> str | None:
    for ref in refs:
        match = CALIBRATION_REF.match(ref)
        if match is None:
            continue
        try:
            _dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            continue
        return ref
    return None


def evaluate_declared_set(root: Path, catalog: occ.OperationalControlCatalog) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    active = {key: d for key, d in catalog.definitions.items() if d.migration_state == "active"}
    module_texts: dict[str, str | None] = {}
    for consumer in WIRED_CONSUMERS:
        path = root / consumer_module_path(consumer)
        module_texts[consumer] = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None
    controls: dict[str, dict[str, Any]] = {}
    for key, definition in sorted(active.items()):
        wired = [c for c in definition.consumers if c in WIRED_CONSUMERS and key in WIRED_CONSUMERS[c]["keys"]]
        unwired = [c for c in definition.consumers if c not in wired]
        referenced = []
        for consumer in wired:
            text = module_texts[consumer]
            tokens = (key, *WIRED_CONSUMERS[consumer]["tokens"])
            referenced.append(text is not None and any(token in text for token in tokens))
        calibration = _calibration_reference(definition.evidence_refs)
        module_present = {c: module_texts[c] is not None for c in wired}
        module_references_key = dict(zip(wired, referenced))
        entry: dict[str, Any] = {
            "consumers": list(definition.consumers),
            "wired_consumers": wired,
            "consumers_without_contract": unwired,
            "consumer_modules": {c: consumer_module_path(c).as_posix() for c in wired},
            "module_present": module_present,
            "module_references_key": module_references_key,
            "calibration_evidence": calibration,
            "evidence_refs": list(definition.evidence_refs),
            "value": str(definition.value),
            "unit": definition.unit,
        }
        controls[key] = entry
        if not wired:
            findings.append(
                {
                    "code": "orphan_control",
                    "detail": f"{key} names no wired consumer that reads it: {list(definition.consumers)}",
                }
            )
        for consumer, present in module_present.items():
            if not present:
                findings.append(
                    {
                        "code": "consumer_module_absent",
                        "detail": f"{key}: {consumer} ({consumer_module_path(consumer).as_posix()}) is not in the tree",
                    }
                )
        for consumer, ok in module_references_key.items():
            if module_present[consumer] and not ok:
                findings.append(
                    {"code": "consumer_module_unreferenced", "detail": f"{key}: {consumer} does not reference the key"}
                )
        if unwired:
            findings.append(
                {
                    "code": "consumer_without_contract",
                    "detail": f"{key} names consumers with no enforced contract: {unwired}",
                }
            )
        if calibration is None:
            findings.append(
                {
                    "code": "calibration_evidence_missing",
                    "detail": f"{key} cites no dated calibration record (calibration:YYYY-MM-DD[:locator]) in evidence_refs",
                }
            )
    contracts: dict[str, dict[str, Any]] = {}
    for consumer, contract in WIRED_CONSUMERS.items():
        undeclared = sorted(k for k in contract["keys"] if k not in active)
        contracts[consumer] = {
            "module": consumer_module_path(consumer).as_posix(),
            "module_present": module_texts[consumer] is not None,
            "keys": sorted(contract["keys"]),
            "undeclared_keys": undeclared,
        }
        for key in undeclared:
            findings.append(
                {
                    "code": "undeclared_consumer_key",
                    "detail": f"{consumer} reads {key}, which is not an active declared control",
                }
            )
    values = {key: d.value for key, d in catalog.definitions.items()}
    invariants = []
    for invariant in catalog.invariants:
        try:
            occ._invariants_hold([invariant], values)
            holds = True
        except occ.OperationalControlConfigError:
            holds = False
            findings.append({"code": "invariant_violation", "detail": invariant.invariant_id})
        invariants.append(
            {
                "id": invariant.invariant_id,
                "left": invariant.left_control_id,
                "operator": invariant.operator,
                "right": invariant.right_control_id,
                "margin": str(invariant.margin),
                "left_value": str(values[invariant.left_control_id]),
                "right_value": str(values[invariant.right_control_id]),
                "holds": holds,
            }
        )
    try:
        diff = occ.diff_operational_controls(root, (root / occ.CATALOG_RELATIVE_PATH).read_bytes())
        replacement = {
            "diff_route": "accepted",
            "changed_controls": sorted(diff["controls"]),
            "same_sha256": diff["before_sha256"] == diff["after_sha256"],
        }
        if diff["controls"] or diff["before_sha256"] != diff["after_sha256"]:
            findings.append(
                {
                    "code": "replacement_route_drift",
                    "detail": "diff of the current bytes against themselves reports a change",
                }
            )
    except occ.OperationalControlConfigError as exc:
        replacement = {"diff_route": "refused", "refusal": f"{exc.code}: {exc.detail}"}
        findings.append({"code": "replacement_route_refused", "detail": f"{exc.code}: {exc.detail}"})
    replacement["reload_behavior"] = sorted({d.reload_behavior for d in active.values()})
    replacement["failure_disposition"] = sorted({d.failure_disposition for d in active.values()})
    return {
        "controls": controls,
        "active_control_count": len(active),
        "inactive_control_count": len(catalog.definitions) - len(active),
        "consumer_contracts": contracts,
        "invariants": invariants,
        "dynamic_replacement": replacement,
        "findings": findings,
    }


def _load_inventory_module() -> Any:
    """Load the exact sibling extractor source; a cached module alias grants nothing."""
    if not INVENTORY_SOURCE.is_file():
        raise ValueError(f"inventory extractor is absent: {INVENTORY_SOURCE}")
    spec = importlib.util.spec_from_file_location("_gtkb_runtime_control_inventory", INVENTORY_SOURCE)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load inventory extractor: {INVENTORY_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def report_inventory(root: Path) -> dict[str, Any]:
    started = time.monotonic()
    inventory = _load_inventory_module().build_inventory(root)
    summary = inventory["summary"]
    coverage = inventory["coverage"]
    return {
        "built": True,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "generating_commit": inventory["generating_commit"],
        "unclassified_or_ambiguous_count": summary["unclassified_or_ambiguous_count"],
        "production_record_count": summary["production_record_count"],
        "production_class_counts": summary["production_class_counts"],
        "canonical_control_count": summary["canonical_control_count"],
        "diagnostic_count": summary["diagnostic_count"],
        "coverage_status": coverage["status"],
        "semantic_completeness": coverage["semantic_completeness"],
        "scanned_file_count": len(coverage["scanned_files"]),
        "statement": (
            "the declared set is evaluated above; the inventory's unclassified or ambiguous production uses are reported, "
            "not adjudicated: migration completeness (DCL clause 'Migration and completeness' 4) is not established here"
        ),
    }


def evaluate(root: Path, *, inventory: bool = True) -> dict[str, Any]:
    catalog = occ.load_operational_control_catalog(root)
    result: dict[str, Any] = {
        "assertion": ASSERTION_ID,
        "project_root": str(root),
        "catalog": {
            "source_reference": catalog.source_reference,
            "catalog_sha256": catalog.catalog_sha256,
            "schema_version": catalog.schema_version,
            "control_count": len(catalog.definitions),
            "invariant_count": len(catalog.invariants),
        },
    }
    result.update(evaluate_declared_set(root, catalog))
    result["inventory"] = (
        report_inventory(root) if inventory else {"built": False, "statement": "inventory skipped by request"}
    )
    result["declared_set_complete"] = not result["findings"]
    return result


def render(result: dict[str, Any]) -> str:
    verdict = "PASS" if result["declared_set_complete"] else "FAIL"
    inventory = result["inventory"]
    unresolved = (
        f"unresolved inventory: {inventory['unclassified_or_ambiguous_count']} unclassified or ambiguous production uses "
        f"(semantic completeness {inventory['semantic_completeness']}; migration completeness not established)"
        if inventory["built"]
        else "unresolved inventory: not built (skipped)"
    )
    lines = [
        f"{verdict} runtime-control centralization ({ASSERTION_ID}): {result['active_control_count']} active controls, "
        f"{len(result['consumer_contracts'])} wired consumers, "
        f"{sum(1 for i in result['invariants'] if i['holds'])}/{len(result['invariants'])} invariants hold, "
        f"{sum(1 for c in result['controls'].values() if c['calibration_evidence'])}/{result['active_control_count']} "
        f"controls with dated calibration evidence; catalog {result['catalog']['catalog_sha256']}",
        unresolved,
    ]
    lines.extend(f"  {finding['code']}: {finding['detail']}" for finding in result["findings"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prove the declared operational-control set and report the unresolved inventory."
    )
    parser.add_argument(
        "--project-root", type=Path, default=None, help="Selected project root (default: this checkout)."
    )
    parser.add_argument("--json", action="store_true", help="Emit the complete evaluation as JSON.")
    parser.add_argument(
        "--skip-inventory", action="store_true", help="Do not build the inventory; report only the declared set."
    )
    parser.add_argument(
        "--fail-on-unresolved", action="store_true", help="Exit 1 when the inventory reports unresolved uses."
    )
    args = parser.parse_args(argv)
    root = (args.project_root if args.project_root is not None else Path(__file__).resolve().parents[1]).resolve()
    try:
        result = evaluate(root, inventory=not args.skip_inventory)
    except occ.OperationalControlConfigError as exc:
        print(
            f"FAIL runtime-control centralization ({ASSERTION_ID}): catalog refused ({exc.code}: {exc.detail})",
            file=sys.stderr,
        )
        return 2
    except (OSError, ValueError) as exc:
        print(
            f"FAIL runtime-control centralization ({ASSERTION_ID}): cannot evaluate {root} ({type(exc).__name__}: {exc})",
            file=sys.stderr,
        )
        return 2
    code = 0 if result["declared_set_complete"] else 1
    if (
        args.fail_on_unresolved
        and result["inventory"]["built"]
        and result["inventory"]["unclassified_or_ambiguous_count"]
    ):
        code = 1
    result["exit_code"] = code
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else render(result))
    return code


if __name__ == "__main__":
    sys.exit(main())
