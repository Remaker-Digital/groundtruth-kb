# Evidence-Derived Trust State

GT-KB lifecycle status records historical promotion:

```text
specified -> implemented -> verified -> retired
```

Trust state is computed separately from current evidence:

| Trust state | Meaning | Runtime handling |
|---|---|---|
| `passing` | Current linked evidence supports authoritative use. | Use normally. |
| `failing` | Latest assertion or linked test evidence failed. | Do not treat as authoritative. |
| `stale` | Required evidence is missing or the verification lease expired. | Warn, rerun evidence, or route to review. |
| `disputed` | Evidence conflicts, such as passing assertions with failing linked tests. | Require review or alternate route. |
| `blocked` | Lifecycle is not authoritative or no executable evidence exists. | Do not use as trusted behavior. |

PBC integration uses `pbc_anchor` on a GT-KB spec or protected behavior to map
current evidence back to a stable PBC behavior/rule/config ID. GT-KB may export
evidence for `pbc:provenance` or `pbc:grounding`, but it should not rewrite the
core PBC behavior text automatically.

Verification leases are optional. When set, `verified_at` and
`verification_expires_after_days` define how long passing evidence remains fresh.
`required_evidence` can name evidence classes such as `assertions`, `tests`, or
`tau_task_replay`; missing required evidence produces `stale` trust.
