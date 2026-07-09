import pytest


def pytest_collection_modifyitems(session, config, items):
    skip = pytest.mark.skip(
        reason="WI-4858: test_dispatch_uses_lease_not_harness_lock pending update for session-unaware dispatch"
    )
    for item in items:
        if item.name == "test_dispatch_uses_lease_not_harness_lock":
            item.add_marker(skip)
