/**
 * ActivationDialog — Modal for validating and activating draft configuration.
 *
 * Triggered by the [Activate] button on ActivationBanner. Shows:
 *   1. Validation status — green checks / red X / yellow warnings
 *   2. Change summary grouped by category
 *   3. [Activate now] button (disabled if hard-block validation fails)
 *   4. [Cancel] button
 *
 * API endpoints consumed:
 *   GET  /api/config/draft          — Full draft state + diff
 *   POST /api/config/draft/activate — Execute activation
 *
 * Props:
 *   - apiFetch  — shell-provided fetch wrapper
 *   - onNotify  — shell toast callback
 *   - onClose   — close the dialog
 *   - onSuccess — called after successful activation (trigger banner refresh)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DraftState {
  has_pending_changes: boolean;
  active_version: number;
  active_activated_at: string | null;
  draft_version: number | null;
  changed_fields: string[];
  draft_config: Record<string, unknown>;
  active_config: Record<string, unknown>;
}

interface PreflightResult {
  can_activate: boolean;
  hard_errors: Array<{ field: string; message: string; page?: string }>;
  warnings: Array<{ field: string; message: string; page?: string }>;
}

interface ActivateResult {
  success: boolean;
  version: number;
  activated_at: string | null;
  errors: Array<{ field: string; message: string }>;
  warnings: Array<{ field: string; message: string }>;
}

interface ActivationDialogProps {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onClose: () => void;
  onSuccess: () => void;
}

// ---------------------------------------------------------------------------
// Field grouping
// ---------------------------------------------------------------------------

/** Map page slugs from preflight validation to human-readable labels. */
function pageLabel(page: string): string {
  const map: Record<string, string> = {
    'agent-configuration': 'Agent configuration',
    'knowledge-base': 'Knowledge base',
    'quick-actions': 'Quick actions',
    'widget-configuration': 'Widget configuration',
    'system': 'System',
  };
  return map[page] ?? page.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

/** Map config field prefixes to human-readable group names. */
function groupField(field: string): string {
  if (field.startsWith('widget_')) return 'Widget configuration';
  if (field.startsWith('retrieval_') || field.startsWith('intent_')) return 'Retrieval & intent';
  if (field.startsWith('escalation_')) return 'Escalation rules';
  if (['brand_name', 'brand_voice', 'brand_tagline', 'greeting_message',
       'greeting_follow_up'].includes(field)) return 'Brand & tone';
  if (['response_length', 'formality_level', 'use_emoji', 'cite_sources_in_response',
       'custom_instructions'].includes(field)) return 'Response style';
  if (field.startsWith('memory_') || field.startsWith('data_retention_')) return 'Memory & privacy';
  return 'Agent configuration';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ActivationDialog({
  apiFetch,
  onNotify,
  onClose,
  onSuccess,
}: ActivationDialogProps) {
  const [draft, setDraft] = useState<DraftState | null>(null);
  const [preflight, setPreflight] = useState<PreflightResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [activateErrors, setActivateErrors] = useState<Array<{ field: string; message: string }>>([]);
  const [activateWarnings, setActivateWarnings] = useState<Array<{ field: string; message: string }>>([]);

  // Fetch draft state + preflight validation on mount (D35: show errors immediately)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [draftRes, preflightRes] = await Promise.all([
          apiFetch('/api/config/draft'),
          apiFetch('/api/config/draft/preflight'),
        ]);
        if (!cancelled) {
          if (draftRes.ok) setDraft(await draftRes.json());
          if (preflightRes.ok) setPreflight(await preflightRes.json());
        }
      } catch {
        // handled
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch]);

  // Activate handler
  const handleActivate = useCallback(async () => {
    setActivating(true);
    setActivateErrors([]);
    setActivateWarnings([]);
    try {
      const res = await apiFetch('/api/config/draft/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      });
      if (res.ok) {
        const result: ActivateResult = await res.json();
        if (result.warnings?.length) {
          setActivateWarnings(result.warnings);
        }
        onNotify(
          `Configuration activated (v${result.version})`,
          'success',
        );
        onSuccess();
        onClose();
      } else {
        const body = await res.json().catch(() => ({ detail: 'Activation failed' }));
        const errors = body.detail?.errors ?? [{ field: '_system', message: body.detail ?? 'Activation failed' }];
        setActivateErrors(errors);
        onNotify('Activation blocked — see errors below', 'error');
      }
    } catch {
      onNotify('Network error during activation', 'error');
    } finally {
      setActivating(false);
    }
  }, [apiFetch, onNotify, onClose, onSuccess]);

  // Group changed fields
  const groups: Record<string, string[]> = {};
  if (draft?.changed_fields) {
    for (const field of draft.changed_fields) {
      const group = groupField(field);
      if (!groups[group]) groups[group] = [];
      groups[group].push(field);
    }
  }

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={dialogStyle} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={titleStyle}>Activate configuration</h2>
          <button onClick={onClose} style={closeButtonStyle}>✕</button>
        </div>

        {/* Content */}
        <div style={bodyStyle}>
          {loading && <div style={loadingStyle}>Loading…</div>}

          {/* D35: Preflight hard errors — shown immediately on dialog open */}
          {!loading && preflight && preflight.hard_errors.length > 0 && (
            <div style={errorSectionStyle}>
              <h3 style={{ ...sectionTitleStyle, color: '#ff4444' }}>
                Required before activation
              </h3>
              <div style={{ ...summaryStyle, marginBottom: '12px' }}>
                The following fields must be configured before your AI assistant can be activated:
              </div>
              {preflight.hard_errors.map((e, i) => (
                <div key={i} style={errorItemStyle}>
                  <strong>{e.page ? pageLabel(e.page) : e.field}:</strong> {e.message}
                </div>
              ))}
            </div>
          )}

          {/* Preflight warnings */}
          {!loading && preflight && preflight.warnings.length > 0 && (
            <div style={warningSectionStyle}>
              <h3 style={{ ...sectionTitleStyle, color: '#ffaa00' }}>
                Recommendations
              </h3>
              {preflight.warnings.map((w, i) => (
                <div key={i} style={warningItemStyle}>
                  <strong>{w.page ? pageLabel(w.page) : w.field}:</strong> {w.message}
                </div>
              ))}
            </div>
          )}

          {/* Change summary — only when there are pending changes AND no hard errors */}
          {!loading && draft?.has_pending_changes && preflight?.can_activate && (
            <div style={sectionStyle}>
              <h3 style={sectionTitleStyle}>Changes to activate</h3>
              <div style={summaryStyle}>
                {draft.changed_fields.length} field{draft.changed_fields.length !== 1 ? 's' : ''} changed
                {draft.draft_version != null && ` (draft v${draft.draft_version})`}
              </div>

              {Object.entries(groups).map(([group, fields]) => (
                <div key={group} style={groupStyle}>
                  <div style={groupLabelStyle}>{group}</div>
                  <div style={fieldListStyle}>
                    {fields.map(f => (
                      <span key={f} style={fieldChipStyle}>
                        {f.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Post-activate errors (from actual activation attempt) */}
          {activateErrors.length > 0 && (
            <div style={errorSectionStyle}>
              <h3 style={{ ...sectionTitleStyle, color: '#ff4444' }}>
                Activation blocked
              </h3>
              {activateErrors.map((e, i) => (
                <div key={i} style={errorItemStyle}>
                  <strong>{e.field}:</strong> {e.message}
                </div>
              ))}
            </div>
          )}

          {/* No changes and no errors */}
          {!loading && !draft?.has_pending_changes && preflight?.can_activate && (
            <div style={emptyStyle}>Draft configuration is ready to activate.</div>
          )}

          {/* Confirmation step */}
          {confirmed && preflight?.can_activate && activateErrors.length === 0 && (
            <div style={confirmSectionStyle}>
              Are you sure you want to activate these changes? This will make them live immediately.
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={footerStyle}>
          <button onClick={onClose} style={cancelButtonStyle}>
            {preflight && !preflight.can_activate ? 'Close' : 'Cancel'}
          </button>
          {preflight?.can_activate && !confirmed ? (
            <button
              onClick={() => setConfirmed(true)}
              disabled={loading}
              style={{
                ...activateButtonStyle,
                opacity: loading ? 0.5 : 1,
              }}
            >
              Activate now
            </button>
          ) : preflight?.can_activate && confirmed ? (
            <button
              onClick={handleActivate}
              disabled={activating}
              style={{
                ...confirmButtonStyle,
                opacity: activating ? 0.5 : 1,
              }}
            >
              {activating ? 'Activating…' : 'Yes, activate'}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles (inline, dark theme)
// ---------------------------------------------------------------------------

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  backgroundColor: 'rgba(0,0,0,0.6)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 9999,
};

const dialogStyle: React.CSSProperties = {
  backgroundColor: '#1f1f1f',
  borderRadius: '12px',
  border: '1px solid #272727',
  width: '90%',
  maxWidth: '560px',
  maxHeight: '80vh',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '20px 24px 16px',
  borderBottom: '1px solid #272727',
};

const titleStyle: React.CSSProperties = {
  color: '#e0e0e0',
  fontSize: '18px',
  fontWeight: 600,
  margin: 0,
};

const closeButtonStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: '#666',
  fontSize: '18px',
  cursor: 'pointer',
  padding: '4px',
};

const bodyStyle: React.CSSProperties = {
  padding: '16px 24px',
  overflowY: 'auto',
  flex: 1,
};

const loadingStyle: React.CSSProperties = { color: '#888', textAlign: 'center', padding: '24px' };
const emptyStyle: React.CSSProperties = { color: '#888', textAlign: 'center', padding: '24px' };

const sectionStyle: React.CSSProperties = { marginBottom: '16px' };
const sectionTitleStyle: React.CSSProperties = {
  color: '#c0c0c0',
  fontSize: '14px',
  fontWeight: 600,
  marginBottom: '8px',
};

const summaryStyle: React.CSSProperties = {
  color: '#888',
  fontSize: '13px',
  marginBottom: '12px',
};

const groupStyle: React.CSSProperties = {
  marginBottom: '10px',
};

const groupLabelStyle: React.CSSProperties = {
  color: '#aaa',
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  marginBottom: '6px',
};

const fieldListStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '4px',
};

const fieldChipStyle: React.CSSProperties = {
  backgroundColor: '#272727',
  color: '#c0c0c0',
  fontSize: '12px',
  padding: '2px 8px',
  borderRadius: '4px',
};

const errorSectionStyle: React.CSSProperties = {
  backgroundColor: 'rgba(255,68,68,0.08)',
  borderRadius: '8px',
  padding: '12px 16px',
  marginBottom: '12px',
};

const errorItemStyle: React.CSSProperties = {
  color: '#ff6666',
  fontSize: '13px',
  marginTop: '4px',
};

const warningSectionStyle: React.CSSProperties = {
  backgroundColor: 'rgba(255,170,0,0.08)',
  borderRadius: '8px',
  padding: '12px 16px',
  marginBottom: '12px',
};

const warningItemStyle: React.CSSProperties = {
  color: '#ffcc66',
  fontSize: '13px',
  marginTop: '4px',
};

const footerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'flex-end',
  gap: '8px',
  padding: '16px 24px',
  borderTop: '1px solid #272727',
};

const cancelButtonStyle: React.CSSProperties = {
  backgroundColor: 'transparent',
  color: '#888',
  border: '1px solid #333',
  borderRadius: '6px',
  padding: '8px 20px',
  fontSize: '13px',
  cursor: 'pointer',
};

const activateButtonStyle: React.CSSProperties = {
  backgroundColor: '#ff3621',
  color: '#fff',
  border: 'none',
  borderRadius: '6px',
  padding: '8px 20px',
  fontSize: '13px',
  fontWeight: 600,
  cursor: 'pointer',
};

const confirmButtonStyle: React.CSSProperties = {
  backgroundColor: '#2b8a3e',
  color: '#fff',
  border: 'none',
  borderRadius: '6px',
  padding: '8px 20px',
  fontSize: '13px',
  fontWeight: 600,
  cursor: 'pointer',
};

const confirmSectionStyle: React.CSSProperties = {
  backgroundColor: 'rgba(43, 138, 62, 0.1)',
  borderRadius: '8px',
  padding: '12px 16px',
  marginTop: '12px',
  color: '#a0d0b0',
  fontSize: '14px',
  lineHeight: '1.5',
};
