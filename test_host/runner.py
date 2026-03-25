# test_host/runner.py — Subprocess pytest orchestrator
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Orchestrates pytest execution as a subprocess with JSON reporting.
Parses results progressively and writes to Cosmos via CosmosWriter.
Supports individual suites (pytest invocations) and composite suites
(sequential execution of multiple individual suites).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import tempfile
import time
from pathlib import Path

from .cosmos_writer import CosmosWriter, TestResult
from .suites import PARALLELIZABLE_SUITES, SUITE_CONFIGS, SuiteConfig, get_suite

logger = logging.getLogger("test_host.runner")


class TestRunner:
    """Runs pytest suites as subprocesses and streams results to Cosmos."""

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
        """Execute the suite and return final state."""
        config = get_suite(self.suite)
        if not config:
            self.cosmos.finalize(status="error")
            return {"error": f"Unknown suite: {self.suite}"}

        try:
            if config.is_composite:
                return await self._run_composite(config)
            else:
                return await self._run_single(config)
        except Exception as exc:
            logger.exception("Test runner failed for suite %s", self.suite)
            self.cosmos.update_stdout(f"Runner exception: {exc}")
            self.cosmos.finalize(status="error")
            return {"error": str(exc)}

    async def cancel(self) -> None:
        """Cancel the running test process.

        Because subprocesses run in their own session (start_new_session=True),
        we send SIGTERM to the process group to ensure all child processes
        (e.g. Vite dev server, Chromium) are also terminated.

        IMPORTANT: finalize() is called FIRST, before subprocess cleanup.
        This ensures the Cosmos document gets a proper status and duration
        even if ACA sends SIGKILL during the cleanup sleep.
        """
        self._cancelled = True
        # Finalize BEFORE cleanup — survives container scale-down SIGKILL
        self.cosmos.finalize(status="error")
        if self._process and self._process.returncode is None:
            try:
                # Send SIGTERM to the entire process group
                pgid = os.getpgid(self._process.pid)
                os.killpg(pgid, signal.SIGTERM)
                await asyncio.sleep(5)
                if self._process.returncode is None:
                    os.killpg(pgid, signal.SIGKILL)
            except (ProcessLookupError, OSError):
                # Process already exited or group doesn't exist
                try:
                    self._process.kill()
                except ProcessLookupError:
                    pass

    async def _run_composite(self, config: SuiteConfig) -> dict:
        """Run multiple suites sequentially."""
        total_tests = sum(
            SUITE_CONFIGS[s].estimated_tests
            for s in config.composite_suites
            if s in SUITE_CONFIGS
        )
        self.cosmos.mark_running(
            total_tests=total_tests,
            phases_total=len(config.composite_suites),
        )

        for suite_name in config.composite_suites:
            if self._cancelled:
                break

            sub_config = get_suite(suite_name)
            if not sub_config:
                logger.warning("Unknown sub-suite %s in composite %s", suite_name, config.name)
                continue

            phase_idx = config.composite_suites.index(suite_name) + 1
            phase_total = len(config.composite_suites)
            logger.info(
                "Starting sub-suite %s (%d/%d) in composite %s",
                suite_name, phase_idx, phase_total, config.name,
            )
            self.cosmos.set_phase(suite_name)

            try:
                if sub_config.requires_locust:
                    await self._run_locust(sub_config)
                elif sub_config.pytest_args:
                    await self._run_pytest(sub_config)
                else:
                    logger.info("Skipping %s (no pytest args and not locust)", suite_name)
            except Exception as exc:
                # Isolate sub-suite failures so the composite loop continues.
                # Without this, a single exception (Cosmos write, JSON parse,
                # subprocess edge case) kills the entire remaining composite.
                logger.exception(
                    "Sub-suite %s (%d/%d) raised exception — continuing composite",
                    suite_name, phase_idx, phase_total,
                )
                self.cosmos.add_results([
                    TestResult(
                        name=f"{suite_name}_suite_error",
                        category=suite_name,
                        status="error",
                        detail=f"Suite exception: {exc!r}"[:500],
                    )
                ])

            self.cosmos.complete_phase(suite_name)
            logger.info("Completed sub-suite %s (%d/%d)", suite_name, phase_idx, phase_total)

        self.cosmos.finalize()
        return self._summary()

    async def _run_single(self, config: SuiteConfig) -> dict:
        """Run a single suite."""
        self.cosmos.mark_running(
            total_tests=config.estimated_tests,
            phases_total=1,
        )
        self.cosmos.set_phase(config.name)

        if config.requires_locust:
            await self._run_locust(config)
        elif config.pytest_args:
            await self._run_pytest(config)

        self.cosmos.complete_phase(config.name)
        self.cosmos.finalize()
        return self._summary()

    async def _run_pytest(self, config: SuiteConfig) -> None:
        """Execute pytest with JSON report output."""
        report_file = Path(tempfile.mktemp(suffix=".json", prefix="pytest_report_"))

        # Build argument list — no shell interpolation, all args are hardcoded
        # paths from SuiteConfig (not user input)
        cmd = [
            "python", "-m", "pytest",
            *config.pytest_args,
            "--json-report",
            f"--json-report-file={report_file}",
            "--json-report-indent=0",
            "--tb=short",
            "-v",
        ]

        # Parallelize safe suites via pytest-xdist.
        # worksteal distribution handles uneven test durations better than
        # the default 'load' mode. -x (fail-fast) is replaced with
        # --maxfail=10 since -x only stops one worker in parallel mode.
        if config.name in PARALLELIZABLE_SUITES:
            cmd.extend(["-n", "auto", "--dist", "worksteal"])
            # Replace -x with --maxfail for parallel-safe fail-fast behavior
            if "-x" in cmd:
                cmd.remove("-x")
                cmd.append("--maxfail=10")

        env = self._build_env(config)
        logger.info("Running pytest: %s", " ".join(cmd))

        try:
            # Using create_subprocess_exec (not shell=True) to prevent injection.
            # start_new_session=True isolates the subprocess from the parent
            # process group so that SIGTERM propagated by tini/uvicorn during
            # container scale-down does NOT kill the pytest process mid-run.
            # The runner manages the subprocess lifecycle explicitly via
            # cancel() and the per-suite timeout.
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
                cwd="/app",
                start_new_session=True,
            )

            stdout_chunks: list[str] = []

            async def _stream_output():
                assert self._process and self._process.stdout
                while True:
                    line = await self._process.stdout.readline()
                    if not line:
                        break
                    decoded = line.decode("utf-8", errors="replace")
                    stdout_chunks.append(decoded)
                    if len(stdout_chunks) > 200:
                        stdout_chunks.pop(0)

            stream_task = asyncio.create_task(_stream_output())

            try:
                await asyncio.wait_for(
                    self._process.wait(),
                    timeout=config.timeout_s,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "pytest timed out after %ds for suite %s",
                    config.timeout_s,
                    config.name,
                )
                if self._process.returncode is None:
                    self._process.kill()
                    await self._process.wait()
                self.cosmos.update_stdout(
                    "".join(stdout_chunks) + f"\n\nTIMEOUT after {config.timeout_s}s"
                )

            # Kill the entire process group to ensure xdist workers don't
            # keep stdout open.  start_new_session=True means the subprocess
            # has its own process group — we SIGKILL it here to guarantee
            # the pipe is fully closed before we await the stream task.
            if hasattr(os, "killpg"):  # Linux/macOS only (always true in container)
                try:
                    pgid = os.getpgid(self._process.pid)
                    os.killpg(pgid, signal.SIGKILL)
                    logger.info("Killed process group %d for suite %s", pgid, config.name)
                except (ProcessLookupError, OSError):
                    logger.debug("Process group already dead for suite %s (expected)", config.name)

            # Close the stdout transport to unblock readline().
            # asyncio.wait_for/cancel CANNOT interrupt a readline() blocked
            # on a pipe fd still held by zombie xdist workers — the task
            # won't yield until data arrives or the fd closes.  Closing
            # the transport forces readline() to return b'' immediately.
            if self._process.stdout:
                self._process.stdout.feed_eof()

            # Wait for stream_task with a safety timeout.
            try:
                await asyncio.wait_for(stream_task, timeout=5.0)
            except asyncio.TimeoutError:
                stream_task.cancel()
                try:
                    await stream_task
                except asyncio.CancelledError:
                    pass
                logger.warning(
                    "stdout stream for %s did not close within 5s after feed_eof — cancelled",
                    config.name,
                )
            self.cosmos.update_stdout("".join(stdout_chunks))

            # Parse JSON report
            if report_file.exists():
                self._parse_json_report(report_file, config.name)
            else:
                logger.warning("No JSON report file at %s", report_file)
                rc = self._process.returncode or 0
                # Provide actionable diagnostics for common failure modes
                if rc < 0:
                    sig_name = signal.Signals(-rc).name if -rc in signal.Signals._value2member_map_ else f"signal {-rc}"
                    detail = (
                        f"Process killed by {sig_name} (exit {rc}). "
                        "Likely cause: container scale-down sent SIGTERM, "
                        "or OOM killer intervened. Check ACA replica scaling "
                        "and container memory limits."
                    )
                elif rc == 5:
                    detail = (
                        "pytest exit code 5: no tests collected. "
                        "Check test paths, markers, and conftest imports."
                    )
                else:
                    tail = "".join(stdout_chunks[-20:]) if stdout_chunks else ""
                    detail = f"Exit code {rc}. Last output:\n{tail}" if tail else f"Exit code {rc}"
                self.cosmos.add_results([
                    TestResult(
                        name=f"{config.name}_suite",
                        category=config.name,
                        status="pass" if rc == 0 else "fail",
                        detail=detail,
                    )
                ])

        finally:
            if report_file.exists():
                report_file.unlink()

    def _parse_json_report(self, report_path: Path, category: str) -> None:
        """Parse pytest-json-report output into TestResult objects."""
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to parse JSON report: %s", exc)
            return

        tests = data.get("tests", [])
        batch: list[TestResult] = []

        for test in tests:
            node_id = test.get("nodeid", "unknown")
            # Shorten: tests/unit/test_foo.py::test_bar -> test_foo::test_bar
            short_name = node_id
            if "::" in node_id:
                parts = node_id.split("::")
                file_part = parts[0].rsplit("/", 1)[-1].replace(".py", "")
                short_name = f"{file_part}::{parts[-1]}"

            outcome = test.get("outcome", "unknown")
            duration = test.get("duration", 0.0)
            detail = ""

            # --- Skip classification (owner rule: no SKIPs in the real world) ---
            # A test that SHOULD be skipped and IS skipped = PASS.
            # A test that should RUN but skips = FAIL.
            #
            # Heuristic: pytest.mark.skipif triggers in the setup phase
            # (the test body never executes). An in-body pytest.skip() call
            # triggers in the call phase (the test started then bailed).
            #   - Setup-phase skip with a reason  → legitimate conditional → PASS
            #   - Call-phase skip or no reason     → evasive / unexplained → FAIL
            if outcome == "skipped":
                setup_info = test.get("setup", {})
                setup_longrepr = setup_info.get("longrepr")
                if setup_longrepr:
                    # Condition-based skip (e.g. skipif file not in container).
                    # The test correctly evaluated its environment → PASS.
                    status = "pass"
                    detail = f"CONDITIONAL_SKIP: {str(setup_longrepr)[:400]}"
                else:
                    # In-body skip or unexplained — treat as failure.
                    call_info = test.get("call", {})
                    longrepr = call_info.get("longrepr", "")
                    status = "fail"
                    detail = f"EVASIVE_SKIP: {str(longrepr)[:400]}" if longrepr else "EVASIVE_SKIP: no reason provided"
            else:
                status_map = {
                    "passed": "pass",
                    "failed": "fail",
                    "error": "error",
                    "xfailed": "fail",   # Expected failures are still failures
                    "xpassed": "pass",
                }
                status = status_map.get(outcome, "error")

            if status in ("fail", "error") and not detail:
                call_info = test.get("call", {})
                longrepr = call_info.get("longrepr", "")
                if isinstance(longrepr, str):
                    detail = longrepr[:500]
                elif isinstance(longrepr, dict):
                    detail = str(longrepr.get("reprcrash", {}).get("message", ""))[:500]

            batch.append(TestResult(
                name=short_name,
                category=category,
                status=status,
                latency_ms=round(duration * 1000, 1),
                detail=detail,
            ))

            if len(batch) >= 50:
                self.cosmos.add_results(batch)
                batch = []

        if batch:
            self.cosmos.add_results(batch)

        # Update total_tests with actual count
        state = self.cosmos.state
        if state.total_tests < state.completed:
            state.total_tests = state.completed

    async def _run_locust(self, config: SuiteConfig) -> None:
        """Run Locust load test in headless mode."""
        env = self._build_env(config)
        target = env.get("PROD_URL", self.target_url)

        # All arguments are hardcoded — no user-controlled input
        cmd = [
            "python", "-m", "locust",
            "--headless",
            "--host", target,
            "--users", "50",
            "--spawn-rate", "10",
            "--run-time", "120s",
            "--csv", "/tmp/locust_results",
            "--locustfile", "tests/performance/locustfile.py",
        ]

        logger.info("Running Locust load test against %s", target)

        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
                cwd="/app",
                start_new_session=True,
            )

            try:
                stdout_bytes, _ = await asyncio.wait_for(
                    self._process.communicate(),
                    timeout=config.timeout_s,
                )
                stdout_text = stdout_bytes.decode("utf-8", errors="replace")
            except asyncio.TimeoutError:
                if self._process.returncode is None:
                    self._process.kill()
                    await self._process.wait()
                stdout_text = f"TIMEOUT after {config.timeout_s}s"

            self.cosmos.update_stdout(stdout_text)

            stats_file = Path("/tmp/locust_results_stats.csv")
            if stats_file.exists():
                self._parse_locust_csv(stats_file)
            else:
                rc = self._process.returncode or 0
                if rc < 0:
                    sig_name = signal.Signals(-rc).name if -rc in signal.Signals._value2member_map_ else f"signal {-rc}"
                    detail = (
                        f"Locust killed by {sig_name} (exit {rc}). "
                        "Container may have been scaled down mid-run."
                    )
                elif not stdout_text.strip():
                    detail = f"Locust exited with code {rc} and no output. Check locustfile path and dependencies."
                else:
                    detail = stdout_text[-500:]
                self.cosmos.add_results([
                    TestResult(
                        name="load_test",
                        category="load",
                        status="pass" if rc == 0 else "fail",
                        detail=detail,
                    )
                ])

        finally:
            for suffix in ["_stats.csv", "_failures.csv", "_stats_history.csv",
                           "_exceptions.csv"]:
                p = Path(f"/tmp/locust_results{suffix}")
                if p.exists():
                    p.unlink()

    def _parse_locust_csv(self, stats_path: Path) -> None:
        """Parse Locust stats CSV into test results."""
        import csv

        results: list[TestResult] = []
        try:
            with open(stats_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("Name", "unknown")
                    if name == "Aggregated":
                        fail_count = int(row.get("Failure Count", "0"))
                        req_count = int(row.get("Request Count", "0"))
                        avg_ms = float(row.get("Average Response Time", "0"))
                        p99_ms = float(row.get("99%", "0"))
                        status = "pass" if fail_count == 0 else "fail"
                        results.append(TestResult(
                            name="load_aggregated",
                            category="load",
                            status=status,
                            latency_ms=avg_ms,
                            detail=(
                                f"{req_count} requests, {fail_count} failures, "
                                f"avg={avg_ms:.0f}ms, p99={p99_ms:.0f}ms"
                            ),
                        ))
                    else:
                        method = row.get("Type", "")
                        fail_count = int(row.get("Failure Count", "0"))
                        avg_ms = float(row.get("Average Response Time", "0"))
                        results.append(TestResult(
                            name=f"load_{method}_{name}".replace("/", "_").replace(" ", "_")[:80],
                            category="load",
                            status="pass" if fail_count == 0 else "fail",
                            latency_ms=avg_ms,
                            detail=f"{row.get('Request Count', 0)} reqs, {fail_count} fails",
                        ))
        except Exception as exc:
            logger.error("Failed to parse Locust CSV: %s", exc)
            results.append(TestResult(
                name="load_csv_parse",
                category="load",
                status="error",
                detail=str(exc)[:500],
            ))

        self.cosmos.add_results(results)

    def _build_env(self, config: SuiteConfig | None = None) -> dict[str, str]:
        """Build environment variables for subprocess execution.

        For E2E Playwright suites, clears LIVE_SPA_BASE_URL and sets
        API_PROXY_TARGET so the conftest starts a local Vite dev server
        that proxies /api/* to the staging API.  This makes E2E tests
        self-contained (no dependency on the deployed SPA serving correctly).
        """
        env = os.environ.copy()

        env["PROD_URL"] = self.target_url
        env["STAGING_URL"] = self.target_url

        if config and config.requires_playwright:
            # E2E mode: use the DEPLOYED SPA served by the staging container.
            # The conftest's deployed-SPA path navigates directly to the
            # staging admin SPA (same origin as API), avoiding the complexity
            # of starting a local Vite dev server inside the test container.
            env["LIVE_SPA_BASE_URL"] = f"{self.target_url}/admin/standalone"
            env["API_PROXY_TARGET"] = self.target_url
        else:
            # Non-E2E suites: set LIVE_SPA_BASE_URL for any incidental
            # SPA references (not used by unit/integration tests, but safe).
            if "LIVE_SPA_BASE_URL" not in env:
                env["LIVE_SPA_BASE_URL"] = f"{self.target_url}/admin/standalone"

        for key in [
            "STAGING_REMAKER_TENANT_KEY",
            "STAGING_REMAKER_WIDGET_KEY",
            "STAGING_SPA_KEY",
            "STAGING_001_TENANT_KEY",
            "STAGING_001_WIDGET_KEY",
            "STAGING_002_TENANT_KEY",
            "STAGING_002_WIDGET_KEY",
            "SUPERADMIN_PREVIEW_API_KEY",
            "PREVIEW_WIDGET_KEY",
            "SPA_CONSOLE_API_KEY",
            "COSMOS_DB_ENDPOINT",
            "COSMOS_DB_KEY",
            "COSMOS_DB_DATABASE",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
        ]:
            val = os.environ.get(key)
            if val:
                env[key] = val

        # Alias staging keys to load test expected names
        if "LOAD_TEST_API_KEY" not in env:
            val = env.get("STAGING_REMAKER_TENANT_KEY", "")
            if val:
                env["LOAD_TEST_API_KEY"] = val
        if "LOAD_TEST_WIDGET_KEY" not in env:
            val = env.get("STAGING_REMAKER_WIDGET_KEY", "") or env.get("PREVIEW_WIDGET_KEY", "")
            if val:
                env["LOAD_TEST_WIDGET_KEY"] = val

        # Alias for E2E Playwright tests.
        # The standalone SPA is a TENANT admin console — it needs a tenant
        # key (ar_live_*) that carries admin role, NOT an SPA platform key
        # (ar_spa_*) which has no tenant role and gets 401 on /api/admin/*.
        if "STAGING_REMAKER_USER_KEY" not in env:
            val = env.get("STAGING_REMAKER_TENANT_KEY", "")
            if val:
                env["STAGING_REMAKER_USER_KEY"] = val

        # Propagate DISABLE_RATE_LIMITING from env (set by test host config)
        if os.environ.get("DISABLE_RATE_LIMITING"):
            env["DISABLE_RATE_LIMITING"] = os.environ["DISABLE_RATE_LIMITING"]

        # Apply per-suite env_vars from SuiteConfig (e.g. FUZZ_TARGET_URL)
        if config and config.env_vars:
            env.update(config.env_vars)

        env.update(self.env_overrides)

        return env

    def _summary(self) -> dict:
        """Return a summary dict of the run state."""
        s = self.cosmos.state
        return {
            "run_id": s.run_id,
            "suite": s.suite,
            "status": s.status,
            "total_tests": s.completed,
            "passed": s.passed,
            "failed": s.failed,
            "skipped": s.skipped,
            "errored": s.errored,
            "duration_s": s.duration_s,
            "phases_completed": s.phases_completed,
        }
