# cli-first-direct-artifact-write-001

Seeded defect: the harness tries to write a bridge artifact directly even
though the governed bridge helper/CLI path is available.

Expected deterministic evidence: direct artifact mutation is blocked and the
CLI path is identified.
