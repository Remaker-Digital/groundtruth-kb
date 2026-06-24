# Cursor harness skills

LO skill adapters for harness **Cursor (E)**.

Until `scripts/generate_cursor_skill_adapters.py` is added and run, Cursor sessions resolve skills in this order:

1. `.cursor/skills/<name>/SKILL.md`
2. `.codex/skills/<name>/SKILL.md`
3. `.claude/skills/<name>/SKILL.md`

Headless dispatch via `scripts/cursor_harness.py` uses the same resolution order.

To materialize the full adapter tree now, copy from Codex:

```powershell
robocopy E:\GT-KB\.codex\skills E:\GT-KB\.cursor\skills /E
```

Then sync MemBase registry authority:

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe E:\GT-KB\scripts\_bootstrap_cursor_harness.py
```
