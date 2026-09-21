#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Execute selected current specification tests without issuing a verification verdict.

Reads the configured native authority and current source. No bridge history,
waiver, local database or saved test result supplies requirements or a pass.
Discovery includes registered TEST selectors and module docstrings in tests/,
groundtruth-kb/tests/ and platform_tests/. Discovery is a floor for independent
review, never a complete applicability analysis.

Use --config PATH with --work-item WI-ID or repeatable --spec SPEC-ID. Reports
always leave independent verification UNASSESSED. Exit 1 means a partial report
(including successful selected execution); exit 2 means an observed failure.
--dry-run discovers tests but does not report them as executed or passed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError

TEST_ROOTS = ("tests", "groundtruth-kb/tests", "platform_tests")
DEFAULT_PYTEST_TIMEOUT_S = 120


class InputError(ValueError):
    """A selected input is missing, malformed, stale or outside the test roots."""


def _record(value: object, ident: str | None = None) -> dict:
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("id"), str)
        or type(value.get("version")) is not int
        or value["version"] < 1
        or (ident is not None and value["id"] != ident)
    ):
        raise InputError("invalid_canonical_record")
    return value


def _current_inputs(client, spec_ids: list[str], work_item: str | None) -> dict:
    """Read selected records through existing GET routes; retain no authority cache."""
    context = None
    selected = set(spec_ids)
    if work_item:
        context = client.request("GET", f"/v1/work-items/{quote(work_item, safe='')}/context")
        _record(context["work_item"], work_item)
        for spec in context["specifications"]:
            selected.add(_record(spec)["id"])
        if context.get("test"):
            selected.add(_record(context["test"])["spec_id"])
    if not selected:
        raise InputError("no_selected_canonical_requirements")
    specs, tests = {}, {}
    for ident in sorted(selected):
        spec = _record(client.request("GET", f"/v1/specifications/{quote(ident, safe='')}"), ident)
        if spec.get("status") != "active":
            raise InputError(f"inactive_requirement: {ident}")
        specs[ident] = spec
        after, cursors = None, set()
        while True:
            page = client.request("GET", "/v1/tests", query={"spec_id": ident, "limit": 1000, "after": after})
            for row in page["records"]:
                row = _record(row)
                if row.get("spec_id") != ident or row["id"] in tests:
                    raise InputError("invalid_test_registry_page")
                tests[row["id"]] = row
            after = page["next_after"]
            if not after:
                break
            if not isinstance(after, str) or after in cursors:
                raise InputError("invalid_test_registry_cursor")
            cursors.add(after)
    if context and context.get("test") and tests.get(context["test"]["id"]) != context["test"]:
        raise InputError("changed_context_test")
    if context:
        for spec in context["specifications"]:
            if specs[spec["id"]] != spec:
                raise InputError("changed_context_requirement")
    return {"context": context, "specifications": specs, "tests": tests}


def _test_path(root: Path, value: str) -> tuple[Path, str]:
    if not isinstance(value, str) or not value or "::" in value or "\\" in value:
        raise InputError("invalid_test_path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise InputError("outside_test_roots")
    path = (root / relative).resolve()
    for test_root in TEST_ROOTS:
        allowed = root / test_root
        if path.is_relative_to(allowed) and path.is_file() and path.suffix == ".py":
            if not allowed.resolve().is_relative_to(root):
                break
            return path, test_root
    raise InputError(f"missing_or_outside_test_roots: {value}")


def _source_inputs(root: Path) -> tuple[dict, dict]:
    """Read discovery inputs once; unreadable or malformed modules stay visible."""
    hashes, docstrings = {}, {}
    for name in TEST_ROOTS:
        directory = root / name
        if not directory.exists():
            continue
        if not directory.is_dir() or not directory.resolve().is_relative_to(root):
            raise InputError(f"outside_test_roots: {name}")
        for candidate in sorted(directory.rglob("*.py")):
            # Imported fixtures and helpers can change the observed behavior too.
            # Test discovery still uses only test modules below; identity covers all Python inputs.
            relative = candidate.relative_to(root).as_posix()
            path, _ = _test_path(root, relative)
            data = path.read_bytes()
            hashes[relative] = hashlib.sha256(data).hexdigest()
            if candidate.name.startswith("test_"):
                try:
                    docstrings[relative] = ast.get_docstring(ast.parse(data, filename=relative)) or ""
                except (SyntaxError, UnicodeError) as error:
                    raise InputError(f"invalid_test_source: {relative}") from error
    for base in (root, root / "groundtruth-kb", *(root / name for name in TEST_ROOTS)):
        for name in ("conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.exists() and not path.resolve().is_relative_to(root):
                raise InputError(f"outside_source_root: {relative}")
            hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return hashes, docstrings


def _discover(root: Path, inputs: dict, docstrings: dict) -> tuple[dict, list[str]]:
    matrix, problems = {}, []
    for ident in inputs["specifications"]:
        pattern = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(ident)}(?![A-Za-z0-9_-])")
        selectors = {path for path, docstring in docstrings.items() if pattern.search(docstring)}
        registrations = []
        for test in inputs["tests"].values():
            if test["spec_id"] != ident:
                continue
            registrations.append(test["id"])
            try:
                path = test.get("test_file")
                _test_path(root, path)
                suffix = []
                for key in ("test_class", "test_function"):
                    value = test.get(key)
                    if value is not None:
                        if not isinstance(value, str) or not value.isidentifier():
                            raise InputError("invalid_test_selector")
                        suffix.append(value)
                selectors.add("::".join([path, *suffix]))
            except InputError as error:
                problems.append(f"{test['id']}: {error}")
        selectors = {s for s in selectors if "::" not in s or s.split("::")[0] not in selectors}
        matrix[ident] = {
            "version": inputs["specifications"][ident]["version"],
            "registered_tests": sorted(registrations),
            "selectors": sorted(selectors),
        }
        if not selectors:
            problems.append(f"{ident}: no_derived_tests")
    return matrix, sorted(problems)


def _execute(root: Path, selector: str, timeout_s: int) -> dict:
    """Use actual process status and testcase outcomes, never console pass counts."""
    _, test_root = _test_path(root, selector.split("::")[0])
    pytest_root = root / "groundtruth-kb" if test_root == "groundtruth-kb/tests" else root
    result = {
        "selector": selector,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "returncode": None,
        "result": "FAIL",
        "reason": "not_executed",
    }
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTEST_ADDOPTS", None)
    with tempfile.TemporaryDirectory(prefix="gtkb-selected-tests-") as temporary:
        report = Path(temporary) / "junit.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            f"--rootdir={pytest_root}",
            "--import-mode=importlib",
            "-o",
            "pythonpath=",
            "-p",
            "no:cacheprovider",
            f"--junitxml={report}",
            selector,
            "--tb=no",
            "-q",
            "--no-header",
        ]
        try:
            process = subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=timeout_s, check=False)
        except subprocess.TimeoutExpired:
            result["reason"] = "pytest_timeout"
            return result
        except OSError:
            result["reason"] = "pytest_launch_failed"
            return result
        result["returncode"] = process.returncode
        try:
            cases = list(ElementTree.parse(report).getroot().iter("testcase"))
        except (OSError, ElementTree.ParseError):
            result["reason"] = "missing_or_invalid_pytest_report"
            return result
        for case in cases:
            if case.find("error") is not None:
                result["errors"] += 1
            elif case.find("failure") is not None:
                result["failed"] += 1
            elif case.find("skipped") is not None:
                result["skipped"] += 1
            else:
                result["passed"] += 1
        if process.returncode != 0:
            result["reason"] = "pytest_nonzero_exit"
        elif result["errors"] or result["failed"]:
            result["reason"] = "test_failure"
        elif result["skipped"] or not result["passed"]:
            result["reason"] = "incomplete_execution"
        else:
            result.update(result="PASS", reason="selected_tests_passed")
    return result


def run(
    *,
    config_path: Path,
    spec_ids: list[str] | None = None,
    work_item: str | None = None,
    json_output: bool = False,
    pytest_timeout_s: int = DEFAULT_PYTEST_TIMEOUT_S,
    dry_run: bool = False,
) -> int:
    report = {
        "scope": "selected_current_requirements",
        "verification_result": "UNASSESSED",
        "verification_reason": "Complete applicability and independent semantic review remain required.",
        "result": "PARTIAL",
        "execution_result": "NOT_RUN",
        "dry_run": dry_run,
        "matrix": {},
        "executions": {},
        "problems": [],
        "inputs_unchanged": None,
    }
    try:
        if pytest_timeout_s <= 0:
            raise InputError("pytest_timeout_must_be_positive")
        config_path = config_path.resolve(strict=True)
        config_bytes = config_path.read_bytes()
        runner_bytes = Path(__file__).read_bytes()
        config = GTConfig.load(config_path=config_path)
        if not config.authority_url:
            raise InputError("native_authority_required")
        root = config.project_root.resolve(strict=True)
        client = AuthorityClient(config.authority_url)
        inputs = _current_inputs(client, spec_ids or [], work_item)
        hashes, docstrings = _source_inputs(root)
        matrix, problems = _discover(root, inputs, docstrings)
        report.update(matrix=matrix, problems=problems, source_files=len(hashes))
        for entry in matrix.values():
            for selector in entry["selectors"]:
                relative = selector.split("::")[0]
                hashes[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        selectors = sorted({s for e in matrix.values() for s in e["selectors"]})
        selectors = [s for s in selectors if "::" not in s or s.split("::")[0] not in selectors]
        if not dry_run and not problems:
            for selector in selectors:
                if any(
                    hashlib.sha256((root / p).read_bytes()).hexdigest() != h for p, h in hashes.items() if h is not None
                ):
                    raise InputError("source_changed_before_execution")
                report["executions"][selector] = _execute(root, selector, pytest_timeout_s)
        after, _ = _source_inputs(root)
        for relative in hashes.keys() - after.keys():
            path = root / relative
            after[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        unchanged = (
            inputs == _current_inputs(client, spec_ids or [], work_item)
            and hashes == after
            and config_bytes == config_path.read_bytes()
            and runner_bytes == Path(__file__).read_bytes()
        )
        report["inputs_unchanged"] = unchanged
        if not unchanged:
            report["problems"].append("selected_inputs_changed")
        if report["executions"]:
            report["execution_result"] = (
                "PASS" if all(e["result"] == "PASS" for e in report["executions"].values()) else "FAIL"
            )
        if report["problems"] or report["execution_result"] == "FAIL":
            report["result"] = "FAIL"
    except (InputError, AuthorityClientError, GTConfigError, OSError, KeyError, TypeError, ValueError) as error:
        report["result"] = "FAIL"
        report["problems"].append(error.code if isinstance(error, AuthorityClientError) else str(error))
    if report["executions"]:
        report["execution_result"] = (
            "PASS" if all(e["result"] == "PASS" for e in report["executions"].values()) else "FAIL"
        )
    if json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Report: {report['result']}; selected execution: {report['execution_result']}")
        print(f"Independent verification: {report['verification_result']}. {report['verification_reason']}")
        for ident, row in report["matrix"].items():
            print(f"{ident} v{row['version']}: {', '.join(row['selectors']) or 'no derived tests'}")
        for problem in report["problems"]:
            print(problem)
    return 2 if report["result"] == "FAIL" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--work-item")
    selection.add_argument("--spec", dest="spec_ids", action="append")
    parser.add_argument("--json", dest="json_output", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--pytest-timeout", dest="pytest_timeout_s", type=int, default=DEFAULT_PYTEST_TIMEOUT_S)
    args = vars(parser.parse_args(argv))
    args["config_path"] = args.pop("config")
    return run(**args)


if __name__ == "__main__":
    raise SystemExit(main())
