# Task Tracker Memory

## Current Status

- **Version:** 0.1.0
- **Knowledge DB:** 7 specs (5 domain + 2 GOV), 8 tests, 1 ADR, 1 DCL, 1 WI (resolved)
- **Tests:** 8/8 pass
- **Assertions:** All passing

## Recent Sessions

- S1: Initial implementation. 5 API endpoints, 7 specs, 7 tests. ADR-001 (in-memory store). WI-001 (title length validation) found during review, fixed, resolved. All assertions clean.

## Quick Reference

- **Run tests:** `pytest tests/ -v`
- **Run assertions:** `gt --config groundtruth.toml assert`
- **Start API:** `uvicorn task_tracker.app:app --reload`
- **Web UI:** `pip install groundtruth-kb[web] && gt --config groundtruth.toml serve`
