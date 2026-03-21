"""Poll for test run failures only."""
import json
import os
import sys
import urllib.request

from _env import load_env_local
load_env_local()

run_id = sys.argv[1] if len(sys.argv) > 1 else "run-5fb396d9cc3e"
base = os.environ.get("STAGING_URL", "")  # SPEC-0058: No hardcoded FQDNs
if not base:
    print("Error: STAGING_URL env var not set", file=sys.stderr)
    sys.exit(1)
url = f"{base}/api/superadmin/tests/{run_id}/status"

# SPEC-0058: API key from env var, not hardcoded
spa = os.environ.get("STAGING_SPA_KEY", "")
if not spa:
    print("Error: STAGING_SPA_KEY env var not set", file=sys.stderr)
    sys.exit(1)
req = urllib.request.Request(url, headers={"X-API-Key": spa})

with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.loads(resp.read())

print(f"Status: {data.get('status')}")
print(f"Passed: {data.get('passed')}, Failed: {data.get('failed')}, Errored: {data.get('errored')}")
print(f"Phases: {data.get('phasesRun')}")
print(f"Duration: {data.get('durationS')}")
print(f"\nFailures ({len(data.get('failures', []))}):")
for f in data.get("failures", []):
    print(f"  [{f.get('category')}] {f.get('name')}: {f.get('detail', '')[:200]}")
