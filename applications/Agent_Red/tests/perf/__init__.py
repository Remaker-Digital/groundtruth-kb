"""Performance tests excluded from the release-candidate gate.

Per WRAPUP -011 §3 / -012 GO: live perf assertions live here under the
``perf`` pytest marker. Run via ``pytest -m perf``; not part of the
default release-candidate gate pytest bundle.
"""
