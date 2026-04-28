---
name: CI workflow patterns
description: Lessons from CI workflow fixes — inline Python in YAML, ruff flags, test triggers
type: feedback
---

Never inline complex Python scripts in GitHub Actions YAML `run:` blocks — bash will misparse parentheses, quotes, and f-strings. Extract to a standalone .py file and call `python scripts/foo.py` instead.

**Why:** S267 discovered that `print(f"  {' -> '.join(c)}")` in YAML caused `syntax error near unexpected token '('` — a bash parse error, not a Python error. The inline script had been silently failing since it was added.

**How to apply:** When adding CI steps that need more than 3-4 lines of Python, always create a script in `scripts/` and reference it from the workflow. This also makes the script testable locally.

Additional note: `ruff check --output-format=github --statistics` is invalid — the `--statistics` flag doesn't support `github` output format. Use them separately if both are needed.
