"""AST-based baseline test: no bare print() outside protocol modules.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from tests._print_guard import scan_bare_prints


def test_no_bare_print_outside_protocol_modules() -> None:
    """Verify no bare print() calls exist outside allowed protocol modules."""
    errors = scan_bare_prints()
    assert errors == [], "Bare print() in non-protocol library code:\n" + "\n".join(f"  {e}" for e in errors)
