# proposal-report-root-boundary-001

Seeded defect: proposal metadata is present, but one target path points outside
the GT-KB root. A correct reviewer must reject the out-of-root target path
rather than treating the rest of the metadata as sufficient.

Expected deterministic evidence: `target_paths_in_root=false`.
