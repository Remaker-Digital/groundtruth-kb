import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_scripts_env_side_effect():
    code = f"""
import os
import sys
sys.path.insert(0, r"{str(PROJECT_ROOT)}")
import scripts._env
print("NOSYSTEM:", os.environ.get("GIT_CONFIG_NOSYSTEM"))
print("XDG:", os.environ.get("XDG_CONFIG_HOME"))
"""

    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert "NOSYSTEM: 1" in res.stdout
    if os.name == "nt":
        import tempfile

        expected_xdg = tempfile.gettempdir()
        assert f"XDG: {expected_xdg}" in res.stdout


def test_groundtruth_kb_side_effect():
    code = """
import os
import sys
sys.path.insert(0, r"{src}")
import groundtruth_kb
print("NOSYSTEM:", os.environ.get("GIT_CONFIG_NOSYSTEM"))
print("XDG:", os.environ.get("XDG_CONFIG_HOME"))
""".format(src=str(PROJECT_ROOT / "groundtruth-kb" / "src"))

    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert "NOSYSTEM: 1" in res.stdout
    if os.name == "nt":
        import tempfile

        expected_xdg = tempfile.gettempdir()
        assert f"XDG: {expected_xdg}" in res.stdout
