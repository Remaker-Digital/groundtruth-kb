"""Inventory all pytest-collectible tests by directory and file."""

import subprocess, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

r = subprocess.run(
    [sys.executable, "-m", "pytest", "--collect-only", "-qq"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
# Merge stdout and stderr (pytest may write to either)
all_output = r.stdout + "\n" + r.stderr
lines = [l for l in all_output.splitlines() if "::" in l and l.startswith("tests/")]

dirs = collections.Counter()
files = collections.Counter()
for l in lines:
    path = l.split("::")[0].replace("\\", "/")
    parts = path.split("/")
    if len(parts) >= 2:
        dirs[parts[0] + "/" + parts[1]] += 1
    else:
        dirs[path] += 1
    files[path] += 1

print(f"Total test items: {len(lines)}")
print(f"\n=== BY DIRECTORY ===")
for d, c in dirs.most_common():
    print(f"  {c:5d}  {d}")

# Identify what the thermal-safe harness covers vs doesn't
harness_dirs = {
    "tests/multi_tenant",
    "tests/unit",
    "tests/migrations",
    "tests/agents",
    "tests/chat",
    "tests/persistent_memory",
    "tests/evaluation",
    "tests/integrations",
}
harness_files = {
    "tests/test_conftest_smoke.py",
    "tests/test_cross_module.py",
    "tests/test_env_loader.py",
    "tests/test_error_handling.py",
    "tests/test_forgot_password.py",
    "tests/test_health.py",
    "tests/test_multi_tenant_isolation_e2e.py",
    "tests/security/test_adversarial.py",
}

in_harness = 0
not_in_harness = 0
not_in_harness_dirs = collections.Counter()
for l in lines:
    path = l.split("::")[0].replace("\\", "/")
    parts = path.split("/")
    dir2 = parts[0] + "/" + parts[1] if len(parts) >= 2 else path
    if dir2 in harness_dirs or path in harness_files:
        in_harness += 1
    else:
        not_in_harness += 1
        not_in_harness_dirs[dir2] += 1

print(f"\n=== HARNESS COVERAGE ===")
print(f"  In thermal-safe harness: {in_harness}")
print(f"  NOT in harness: {not_in_harness}")
print(f"\n  Uncovered directories:")
for d, c in not_in_harness_dirs.most_common():
    print(f"    {c:5d}  {d}")
