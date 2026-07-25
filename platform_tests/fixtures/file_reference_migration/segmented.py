from pathlib import Path
import os

pathlib_value = Path(".claude") / "hooks" / "old.py"
joinpath_value = Path(".claude").joinpath("hooks", "old.py")
os_join_value = os.path.join(".claude", "hooks", "old.py")
glob_value = Path(".claude").joinpath("hooks").glob("*.py")
