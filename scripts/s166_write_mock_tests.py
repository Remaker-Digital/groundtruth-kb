# S166: Generate mock E2E test files
import pathlib
import os

BASE = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent / "tests" / "e2e_mock"


def wf(name, content):
    path = BASE / name
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path} ({len(content)} bytes)")
