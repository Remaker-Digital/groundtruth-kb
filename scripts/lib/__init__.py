"""Shared library modules for scripts/.

This package is intentionally minimal. Modules here are pure helpers that
both `scripts/deploy.py` (smoke tool) and `scripts/deploy_pipeline.py`
(canonical production path) can import without circular dependencies.

Created 2026-04-25 (S308) per
`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md`
to close the WI-3031 canonical-path scaling-enforcement gap.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
