import subprocess, sys

# Stage
r = subprocess.run(
    ["git", "add", ".claude/rules/canonical-terminology.md"], capture_output=True, text=True, cwd=r"E:\GT-KB"
)
if r.returncode != 0:
    print(f"STAGE FAILED: {r.stderr}")
    sys.exit(1)
print("Staged OK")

# Commit
msg = """docs(glossary): add handoff prompt entry and cross-reference Session Prompt

Add 'handoff prompt' glossary entry to canonical-terminology.md per owner
decision DELIB-20260883. Cross-reference existing Session Prompt
supporting-record row back to handoff prompt. Reject 'continuation
prompt' as redundant third term. WI-4363.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"""

r2 = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True, cwd=r"E:\GT-KB")
print(r2.stdout)
if r2.returncode != 0:
    print(f"COMMIT FAILED: {r2.stderr}")
    sys.exit(1)
print("Commit OK")
