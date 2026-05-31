from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.hooks.code_quality_baseline_proposal_check import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
