# adopter-with-release-gate

Demonstrates **wiring a release gate to adopter CI**: a stripped-down
GitHub Actions workflow that invokes an adopter-side release-gate check
before declaring a build deployable. The platform's reference release-gate
script lives at `scripts/release_candidate_gate.py` (workspace-level, not
under the package); this example shows how an adopter wires their own
equivalent.

## Run the example

```bash
# Copy the example tree to a workspace location of your choosing
cp -r examples/adopter-with-release-gate/ ~/projects/release-gated-app/
cd ~/projects/release-gated-app/
git init && git add -A && git commit -m "initial"

# Verify the isolation contract
gt project doctor --profile dual-agent

# Inspect the release-gate stub (adopter would replace this with their gate)
bash scripts/release_gate_check.sh
```

Expected outcome: `gt project doctor` reports every `isolation:*` check as
`pass` or `info`; the release-gate stub prints an "OK (placeholder)" message
and exits zero.

## Dashboard rendering

The release-gate dashboard rendering walks through how an adopter sees
their build state alongside the service and overlay surfaces.

```bash
gt dashboard render --adopter-root ~/projects/release-gated-app/
```

The dashboard surfaces:

- **Service health** from `[service].endpoint` — placeholder until overridden.
- **Overlay state** from `.groundtruth-chroma/` — empty until the first
  index build.
- (Optional) **Release-gate state** wired in by the adopter via a
  dashboard panel that reads the gate workflow's last result.

Both the service and overlay surfaces appear in the same render so the
adopter sees the full readiness picture before the release gate runs.

## Reference: workspace-level release-gate

The platform's reference release-gate script is at
[scripts/release_candidate_gate.py](../../../scripts/release_candidate_gate.py)
(workspace-level path; resolves to `<gt-kb-root>/scripts/release_candidate_gate.py`).
Adopters do NOT consume this script directly; they implement their own
release-gate per their deployment pipeline. The script is referenced here
only as the canonical pattern.

## See also

- [Application/Platform Isolation](../../docs/architecture/isolation.md)
- [cli.md](../../docs/reference/cli.md)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
