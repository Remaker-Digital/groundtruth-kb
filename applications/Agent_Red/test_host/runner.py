"""Subprocess pytest orchestration for the Agent Red test host."""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import os
import signal
import tempfile
from pathlib import Path

from .cosmos_writer import CosmosWriter, TestResult
from .suites import PARALLELIZABLE_SUITES, SUITE_CONFIGS, SuiteConfig, get_suite

logger = logging.getLogger("test_host.runner")


class TestRunner:
    def __init__(
        self,
        run_id: str,
        suite: str,
        environment: str,
        target_url: str,
        cosmos_writer: CosmosWriter,
        env_overrides: dict[str, str] | None = None,
    ):
        self.run_id = run_id
        self.suite = suite
        self.environment = environment
        self.target_url = target_url
        self.cosmos = cosmos_writer
        self.env_overrides = env_overrides or {}
        self._process: asyncio.subprocess.Process | None = None
        self._cancelled = False

    async def run(self) -> dict:
        config = get_suite(self.suite)
        if config is None:
            self.cosmos.finalize(status="error")
            return {"error": f"Unknown suite: {self.suite}"}
        try:
            if config.is_composite:
                return await self._run_composite(config)
            return await self._run_single(config)
        except Exception as exc:
            logger.exception("Test runner failed for suite %s", self.suite)
            self.cosmos.update_stdout(f"Runner exception: {exc}")
            self.cosmos.finalize(status="error")
            return {"error": str(exc)}

    async def cancel(self) -> None:
        self._cancelled = True
        self.cosmos.finalize(status="error")
        if self._process and self._process.returncode is None:
            try:
                if hasattr(os, "killpg"):
                    os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                else:
                    self._process.terminate()
            except (OSError, ProcessLookupError):
                pass

    async def _run_composite(self, config: SuiteConfig) -> dict:
        total = sum(SUITE_CONFIGS[name].estimated_tests for name in config.composite_suites if name in SUITE_CONFIGS)
        self.cosmos.mark_running(total_tests=total, phases_total=len(config.composite_suites))
        for suite_name in config.composite_suites:
            if self._cancelled:
                break
            sub_config = get_suite(suite_name)
            if sub_config is None:
                continue
            self.cosmos.set_phase(suite_name)
            if sub_config.requires_locust:
                await self._run_locust(sub_config)
            elif sub_config.pytest_args:
                await self._run_pytest(sub_config)
            self.cosmos.complete_phase(suite_name)
        self.cosmos.finalize()
        return self._summary()

    async def _run_single(self, config: SuiteConfig) -> dict:
        self.cosmos.mark_running(total_tests=config.estimated_tests, phases_total=1)
        self.cosmos.set_phase(config.name)
        if config.requires_locust:
            await self._run_locust(config)
        elif config.pytest_args:
            await self._run_pytest(config)
        self.cosmos.complete_phase(config.name)
        self.cosmos.finalize()
        return self._summary()

    async def _run_pytest(self, config: SuiteConfig) -> None:
        report_file = Path(tempfile.mktemp(suffix=".json", prefix="pytest_report_"))
        cmd = [
            "python",
            "-m",
            "pytest",
            *config.pytest_args,
            "--json-report",
            f"--json-report-file={report_file}",
            "--json-report-indent=0",
            "--tb=short",
            "-v",
        ]
        if config.name in PARALLELIZABLE_SUITES:
            cmd.extend(["-n", "auto", "--dist", "worksteal"])
            if "-x" in cmd:
                cmd.remove("-x")
                cmd.append("--maxfail=10")
        env = self._build_env(config)
        stdout_text = ""
        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
                cwd="/app",
                start_new_session=True,
            )
            stdout_bytes, _ = await asyncio.wait_for(self._process.communicate(), timeout=config.timeout_s)
            stdout_text = stdout_bytes.decode("utf-8", errors="replace")
            self.cosmos.update_stdout(stdout_text)
            if report_file.exists():
                self._parse_json_report(report_file, config.name)
            else:
                rc = self._process.returncode or 0
                self.cosmos.add_results(
                    [
                        TestResult(
                            name=f"{config.name}_suite",
                            category=config.name,
                            status="pass" if rc == 0 else "fail",
                            detail=stdout_text[-500:] if stdout_text else f"Exit code {rc}",
                        )
                    ]
                )
        except TimeoutError:
            if self._process and self._process.returncode is None:
                self._process.kill()
                await self._process.wait()
            self.cosmos.update_stdout(stdout_text + f"\n\nTIMEOUT after {config.timeout_s}s")
            self.cosmos.add_results(
                [
                    TestResult(
                        name=f"{config.name}_timeout",
                        category=config.name,
                        status="error",
                        detail=f"Timeout after {config.timeout_s}s",
                    )
                ]
            )
        finally:
            if report_file.exists():
                report_file.unlink()

    def _parse_json_report(self, report_path: Path, category: str) -> None:
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to parse JSON report: %s", exc)
            return
        batch: list[TestResult] = []
        for test in data.get("tests", []):
            node_id = test.get("nodeid", "unknown")
            short_name = node_id
            if "::" in node_id:
                parts = node_id.split("::")
                short_name = f"{parts[0].rsplit('/', 1)[-1].replace('.py', '')}::{parts[-1]}"
            outcome = test.get("outcome", "unknown")
            status = {
                "passed": "pass",
                "failed": "fail",
                "error": "error",
                "skipped": "skip",
                "xfailed": "skip",
                "xpassed": "pass",
            }.get(outcome, "error")
            detail = ""
            if status in {"fail", "error", "skip"}:
                call_info = test.get("call") or test.get("setup") or {}
                longrepr = call_info.get("longrepr", "")
                if isinstance(longrepr, dict):
                    detail = str(longrepr.get("reprcrash", {}).get("message", ""))[:500]
                else:
                    detail = str(longrepr)[:500]
            batch.append(
                TestResult(
                    name=short_name,
                    category=category,
                    status=status,
                    latency_ms=round(float(test.get("duration", 0.0)) * 1000, 1),
                    detail=detail,
                )
            )
            if len(batch) >= 50:
                self.cosmos.add_results(batch)
                batch = []
        if batch:
            self.cosmos.add_results(batch)
        if self.cosmos.state.total_tests < self.cosmos.state.completed:
            self.cosmos.state.total_tests = self.cosmos.state.completed

    async def _run_locust(self, config: SuiteConfig) -> None:
        env = self._build_env(config)
        target = env.get("PROD_URL", self.target_url)
        cmd = [
            "python",
            "-m",
            "locust",
            "--headless",
            "--host",
            target,
            "--users",
            "50",
            "--spawn-rate",
            "10",
            "--run-time",
            "120s",
            "--csv",
            "/tmp/locust_results",
            "--locustfile",
            "tests/performance/locustfile.py",
        ]
        self._process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
            cwd="/app",
            start_new_session=True,
        )
        stdout_bytes, _ = await asyncio.wait_for(self._process.communicate(), timeout=config.timeout_s)
        self.cosmos.update_stdout(stdout_bytes.decode("utf-8", errors="replace"))
        stats_file = Path("/tmp/locust_results_stats.csv")
        if stats_file.exists():
            self._parse_locust_csv(stats_file)

    def _parse_locust_csv(self, stats_path: Path) -> None:
        results: list[TestResult] = []
        with stats_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                name = row.get("Name", "unknown")
                fail_count = int(row.get("Failure Count", "0"))
                avg_ms = float(row.get("Average Response Time", "0"))
                results.append(
                    TestResult(
                        name=f"load_{name}".replace("/", "_").replace(" ", "_")[:80],
                        category="load",
                        status="pass" if fail_count == 0 else "fail",
                        latency_ms=avg_ms,
                        detail=f"{row.get('Request Count', 0)} requests, {fail_count} failures",
                    )
                )
        self.cosmos.add_results(results)

    def _build_env(self, config: SuiteConfig | None = None) -> dict[str, str]:
        env = os.environ.copy()
        env["PROD_URL"] = self.target_url
        env["STAGING_URL"] = self.target_url
        if config and config.requires_playwright:
            env.pop("LIVE_SPA_BASE_URL", None)
            env["API_PROXY_TARGET"] = self.target_url
        else:
            env.setdefault("LIVE_SPA_BASE_URL", f"{self.target_url}/admin/standalone")
        for key in [
            "STAGING_REMAKER_TENANT_KEY",
            "STAGING_REMAKER_WIDGET_KEY",
            "STAGING_SPA_KEY",
            "SUPERADMIN_PREVIEW_API_KEY",
            "PREVIEW_WIDGET_KEY",
            "SPA_CONSOLE_API_KEY",
            "COSMOS_DB_ENDPOINT",
            "COSMOS_DB_KEY",
            "COSMOS_DB_DATABASE",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
        ]:
            if os.environ.get(key):
                env[key] = os.environ[key]
        if config and config.env_vars:
            env.update(config.env_vars)
        env.update(self.env_overrides)
        return env

    def _summary(self) -> dict:
        state = self.cosmos.state
        return {
            "run_id": state.run_id,
            "suite": state.suite,
            "status": state.status,
            "total_tests": state.completed,
            "passed": state.passed,
            "failed": state.failed,
            "skipped": state.skipped,
            "errored": state.errored,
            "duration_s": state.duration_s,
            "phases_completed": state.phases_completed,
        }
