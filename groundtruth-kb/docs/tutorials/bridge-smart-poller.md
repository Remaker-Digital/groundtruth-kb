# Bridge Smart Poller

The file bridge uses `bridge/INDEX.md` as the canonical Prime Builder / Loyal
Opposition queue. The smart poller is the preferred automation path when its
implementation is available, verified, and healthy.

## Current Rule

- Use the verified smart poller when it is available and functioning.
- Do not restore the retired OS poller implementation as the active automation
  path.
- If smart-poller automation is unavailable, use manual bridge scans until the
  smart poller is installed and healthy.

## Minimum Health Evidence

A healthy smart-poller setup should provide:

- durable scan status JSON for each role
- clear-scan and dispatched-work logs
- lock handling so overlapping scans cannot duplicate bridge files
- role-specific latest-status filtering:
  - Loyal Opposition: `NEW`, `REVISED`
  - Prime Builder: `GO`, `NO-GO`
- no action on terminal `VERIFIED` entries
- token/cost controls appropriate to the local harness

## Legacy Note

Older GroundTruth templates and projects may still contain files named
`bridge-os-poller-setup-prompt.md`. The filename is retained for compatibility,
but current template content describes smart-poller setup. The former OS
scheduled-task poller was retired after a token-cost regression and should not
be used as the default automation path.
