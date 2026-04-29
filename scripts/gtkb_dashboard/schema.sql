PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS refresh_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    error TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS dashboard_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS health_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    label TEXT NOT NULL,
    value TEXT NOT NULL,
    status TEXT NOT NULL,
    tooltip TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS shortcuts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    label TEXT NOT NULL,
    target TEXT NOT NULL,
    kind TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS action_center (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    action TEXT NOT NULL,
    owner_lane TEXT NOT NULL,
    why TEXT NOT NULL,
    remediation TEXT NOT NULL,
    shortcut_label TEXT NOT NULL DEFAULT '',
    shortcut_target TEXT NOT NULL DEFAULT '',
    shortcut_kind TEXT NOT NULL DEFAULT 'file',
    source TEXT NOT NULL,
    severity TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_timeline_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    stage TEXT NOT NULL,
    label TEXT NOT NULL,
    event_count INTEGER NOT NULL,
    latest_result TEXT NOT NULL,
    latest_version TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    stage TEXT NOT NULL,
    stage_label TEXT NOT NULL,
    event TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    date_label TEXT NOT NULL,
    version TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    branch TEXT NOT NULL,
    result TEXT NOT NULL,
    result_color TEXT NOT NULL,
    test_results TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    environment TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    caused_by_deploy_id TEXT NOT NULL DEFAULT '',
    detected_at TEXT NOT NULL,
    mitigated_at TEXT NOT NULL DEFAULT '',
    closed_at TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS release_blockers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    blocker TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quality_rollup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    label TEXT NOT NULL,
    value INTEGER NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    risk TEXT NOT NULL,
    evidence TEXT NOT NULL,
    impact TEXT NOT NULL,
    remediation TEXT NOT NULL,
    owner TEXT NOT NULL,
    severity TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS integration_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    key TEXT NOT NULL,
    display_name TEXT NOT NULL,
    health TEXT NOT NULL,
    status TEXT NOT NULL,
    latest_run_summary TEXT NOT NULL,
    gate_role TEXT NOT NULL,
    remediation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kpi_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_at TEXT NOT NULL,
    metric_key TEXT NOT NULL,
    metric_label TEXT NOT NULL,
    value REAL,
    metric_group TEXT NOT NULL,
    lower_is_better INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS current_metrics (
    metric_key TEXT PRIMARY KEY,
    metric_label TEXT NOT NULL,
    value REAL,
    status TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS data_freshness (
    key TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS setup_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    section TEXT NOT NULL,
    title TEXT NOT NULL,
    instruction TEXT NOT NULL,
    command TEXT NOT NULL DEFAULT '',
    link_label TEXT NOT NULL DEFAULT '',
    link_url TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS required_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    purpose TEXT NOT NULL,
    check_command TEXT NOT NULL DEFAULT '',
    install_reference TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'documented'
);

CREATE TABLE IF NOT EXISTS third_party_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort_order INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    purpose TEXT NOT NULL,
    required_env_vars TEXT NOT NULL,
    setup_summary TEXT NOT NULL,
    console_url TEXT NOT NULL DEFAULT '',
    health_signal TEXT NOT NULL DEFAULT 'configuration required'
);
