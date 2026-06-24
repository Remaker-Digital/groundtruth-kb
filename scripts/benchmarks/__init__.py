"""GT-KB benchmark suite (Self-Diagnostic Leak Closure Slice 2).

Read-only measurement benchmarks. Each benchmark module exposes:

    run(window_start, window_end, project_root) -> BenchmarkResult

Outputs land under ``.gtkb-state/benchmarks/<run_id>/``. No MemBase writes.

Governing artifacts: SPEC-1662 (GOV-18), GOV-ARTIFACT-ORIENTED-GOVERNANCE-001,
GOV-STANDING-BACKLOG-001, ADR-DA-READ-SURFACE-PLACEMENT-001,
DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE,
INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from scripts.benchmarks.common import (
    BenchmarkResult,
    benchmark_output_dir,
    compute_idempotency_key,
    new_run_id,
    write_run_outputs,
)
from scripts.benchmarks.effectiveness_observatory import (
    build_effectiveness_payload,
    write_effectiveness_outputs,
)
from scripts.benchmarks.effectiveness_observatory import (
    render_markdown as render_effectiveness_markdown,
)
from scripts.benchmarks.metric_registry import metric_definitions, registry_payload

__all__ = [
    "BenchmarkResult",
    "build_effectiveness_payload",
    "benchmark_output_dir",
    "compute_idempotency_key",
    "metric_definitions",
    "new_run_id",
    "registry_payload",
    "render_effectiveness_markdown",
    "write_effectiveness_outputs",
    "write_run_outputs",
]
