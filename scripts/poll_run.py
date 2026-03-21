"""Quick poll script for test run status."""
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

with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())

fields = ["status", "completed", "passed", "failed", "errored", "currentPhase", "phasesRun", "durationS"]
print(json.dumps({k: data.get(k) for k in fields}, indent=2))
