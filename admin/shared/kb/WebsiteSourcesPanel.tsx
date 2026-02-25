/**
 * WebsiteSourcesPanel — manage automated website crawl sources for knowledge base.
 *
 * Displays a list of website sources with status, crawl stats, and actions.
 * Supports adding new sources, triggering manual re-crawls, pausing/resuming,
 * and deleting sources.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import type { ApiFetch } from '../hooks/useApi';
import {
  useWebsiteSources,
  useCreateWebsiteSource,
  useDeleteWebsiteSource,
  useTriggerCrawl,
  useUpdateWebsiteSource,
} from '../hooks/useWebsiteSources';
import type { WebsiteSource } from '../hooks/useWebsiteSources';
import { HelpTooltip } from '../HelpTooltip';
import {
  BRAND_PRIMARY,
  ACTION_PRIMARY,
  COLOR_SUCCESS,
  COLOR_DANGER,
  COLOR_GRAY,
  COLOR_LIGHT_GRAY,
  COLOR_BORDER,
  COLOR_WHITE,
  COLOR_TEXT,
  COLOR_TEXT_SECONDARY,
  COLOR_WARNING,
  FONT_FAMILY,
  BORDER_RADIUS,
  inputStyle,
  buttonStyle,
} from './styles';
import { LoadingSpinner } from './LoadingSpinner';
import { EmptyState } from './EmptyState';
import { ErrorBanner } from './ErrorBanner';

// ---------------------------------------------------------------------------
// Status badge styles
// ---------------------------------------------------------------------------

const STATUS_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  pending: { bg: '#fff8c5', color: COLOR_WARNING, label: 'Pending' },
  crawling: { bg: '#dbeafe', color: '#2563eb', label: 'Crawling' },
  active: { bg: '#dcffe4', color: COLOR_SUCCESS, label: 'Active' },
  failed: { bg: '#ffeef0', color: COLOR_DANGER, label: 'Failed' },
  paused: { bg: COLOR_LIGHT_GRAY, color: COLOR_GRAY, label: 'Paused' },
};

function SourceStatusBadge({ status }: { status: string }) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '10px',
        fontSize: '12px',
        fontWeight: 600,
        backgroundColor: s.bg,
        color: s.color,
      }}
    >
      {s.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatRelativeTime(isoStr: string | null): string {
  if (!isoStr) return '\u2014';
  try {
    const d = new Date(isoStr);
    const now = Date.now();
    const diffMs = now - d.getTime();
    if (diffMs < 0) {
      // future
      const mins = Math.round(-diffMs / 60_000);
      if (mins < 60) return `in ${mins}m`;
      const hrs = Math.round(mins / 60);
      if (hrs < 24) return `in ${hrs}h`;
      return `in ${Math.round(hrs / 24)}d`;
    }
    const mins = Math.round(diffMs / 60_000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.round(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.round(hrs / 24)}d ago`;
  } catch {
    return '\u2014';
  }
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface WebsiteSourcesPanelProps {
  apiFetch: ApiFetch;
  onNotify: (message: string, type: 'success' | 'error' | 'info') => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const WebsiteSourcesPanel: React.FC<WebsiteSourcesPanelProps> = ({
  apiFetch,
  onNotify,
}) => {
  const { data, loading, error, refetch } = useWebsiteSources(apiFetch);
  const { create, loading: creating, error: createError } = useCreateWebsiteSource(apiFetch);
  const { remove, loading: deleting } = useDeleteWebsiteSource(apiFetch);
  const { trigger, loading: triggering } = useTriggerCrawl(apiFetch);
  const { update, loading: updating } = useUpdateWebsiteSource(apiFetch);

  const [showAddForm, setShowAddForm] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newMaxPages, setNewMaxPages] = useState(25);
  const [newAutoRefresh, setNewAutoRefresh] = useState(true);
  const [newRefreshHours, setNewRefreshHours] = useState(24);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const sources = data?.sources ?? [];

  const handleCreate = useCallback(async () => {
    if (!newUrl.trim()) return;
    const result = await create({
      startUrl: newUrl.trim(),
      maxPages: newMaxPages,
      autoRefresh: newAutoRefresh,
      refreshIntervalHours: newRefreshHours,
    });
    if (result) {
      onNotify(`Website source added: ${result.domain}`, 'success');
      setNewUrl('');
      setNewMaxPages(25);
      setShowAddForm(false);
      refetch();
    } else {
      onNotify(createError || 'Failed to add website source', 'error');
    }
  }, [newUrl, newMaxPages, newAutoRefresh, newRefreshHours, create, createError, onNotify, refetch]);

  const handleDelete = useCallback(async (sourceId: string) => {
    const result = await remove(sourceId);
    if (result?.success) {
      onNotify(result.message, 'success');
      setConfirmDelete(null);
      refetch();
    } else {
      onNotify('Failed to delete website source', 'error');
    }
  }, [remove, onNotify, refetch]);

  const handleTriggerCrawl = useCallback(async (sourceId: string) => {
    const result = await trigger(sourceId);
    if (result?.success) {
      onNotify(result.message, 'success');
      refetch();
    } else {
      onNotify('Failed to trigger crawl', 'error');
    }
  }, [trigger, onNotify, refetch]);

  const handleTogglePause = useCallback(async (source: WebsiteSource) => {
    const newStatus = source.status === 'paused' ? 'active' : 'paused';
    const result = await update(source.id, { status: newStatus });
    if (result) {
      onNotify(`Source ${newStatus === 'paused' ? 'paused' : 'resumed'}: ${source.domain}`, 'success');
      refetch();
    } else {
      onNotify('Failed to update source', 'error');
    }
  }, [update, onNotify, refetch]);

  return (
    <div>
      {/* Header */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: `1px solid ${COLOR_BORDER}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }}>
            Website Sources
            <HelpTooltip
              text="Add your website URL and Agent Red will automatically crawl it to build your knowledge base. Pages are re-crawled on a schedule to keep content fresh."
              docLink="https://agentredcx.com/docs/admin-guide/website-sources"
            />
          </h2>
          <span style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>
            {sources.length} source{sources.length !== 1 ? 's' : ''}
          </span>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          style={buttonStyle('primary')}
        >
          + Add Website
        </button>
      </div>

      {/* Add form */}
      {showAddForm && (
        <div
          style={{
            padding: '16px 20px',
            borderBottom: `1px solid ${COLOR_BORDER}`,
            backgroundColor: COLOR_LIGHT_GRAY,
          }}
        >
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '300px' }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, display: 'block', marginBottom: '4px' }}>
                Website URL
              </label>
              <input
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://example.com"
                style={inputStyle()}
                onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              />
            </div>
            <div style={{ width: '100px' }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, display: 'block', marginBottom: '4px' }}>
                Max pages
              </label>
              <input
                type="number"
                value={newMaxPages}
                onChange={(e) => setNewMaxPages(Math.max(1, Math.min(100, parseInt(e.target.value) || 25)))}
                min={1}
                max={100}
                style={inputStyle()}
              />
            </div>
            <div style={{ width: '120px' }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, display: 'block', marginBottom: '4px' }}>
                Refresh interval
              </label>
              <select
                value={newRefreshHours}
                onChange={(e) => setNewRefreshHours(parseInt(e.target.value))}
                style={inputStyle()}
              >
                <option value={6}>Every 6h</option>
                <option value={12}>Every 12h</option>
                <option value={24}>Every 24h</option>
                <option value={48}>Every 2 days</option>
                <option value={168}>Weekly</option>
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', paddingBottom: '2px' }}>
              <input
                type="checkbox"
                checked={newAutoRefresh}
                onChange={(e) => setNewAutoRefresh(e.target.checked)}
                id="auto-refresh-toggle"
              />
              <label htmlFor="auto-refresh-toggle" style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY, cursor: 'pointer' }}>
                Auto-refresh
              </label>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleCreate}
                disabled={creating || !newUrl.trim()}
                style={buttonStyle('primary', creating || !newUrl.trim())}
              >
                {creating ? 'Adding...' : 'Add & Crawl'}
              </button>
              <button
                onClick={() => { setShowAddForm(false); setNewUrl(''); }}
                style={buttonStyle('secondary')}
              >
                Cancel
              </button>
            </div>
          </div>
          {createError && (
            <div style={{ fontSize: '13px', color: COLOR_DANGER, marginTop: '8px' }}>
              {createError}
            </div>
          )}
        </div>
      )}

      {/* Loading / Error / Empty states */}
      {loading && sources.length === 0 && (
        <LoadingSpinner text="Loading website sources..." />
      )}

      {error && sources.length === 0 && (
        <ErrorBanner message={error} onRetry={refetch} />
      )}

      {!loading && !error && sources.length === 0 && !showAddForm && (
        <EmptyState
          icon={String.fromCodePoint(0x1F310)}
          title="No website sources"
          subtitle="Add your website URL to automatically crawl and import content into your knowledge base."
        />
      )}

      {/* Source list */}
      {sources.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px',
            }}
          >
            <thead>
              <tr style={{ backgroundColor: COLOR_LIGHT_GRAY }}>
                {['Domain', 'Status', 'Pages', 'Articles', 'Last crawled', 'Next crawl', 'Actions'].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: '10px 16px',
                      textAlign: 'left',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: COLOR_TEXT_SECONDARY,
                      borderBottom: `1px solid ${COLOR_BORDER}`,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.5px',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sources.map((source) => (
                <tr
                  key={source.id}
                  style={{ borderBottom: `1px solid ${COLOR_BORDER}` }}
                >
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ fontWeight: 500, color: COLOR_TEXT }}>{source.domain}</div>
                    <div style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '2px' }}>
                      {source.startUrl.length > 60 ? source.startUrl.slice(0, 57) + '...' : source.startUrl}
                    </div>
                    {source.errorMessage && (
                      <div style={{ fontSize: '11px', color: COLOR_DANGER, marginTop: '4px' }}>
                        {source.errorMessage.length > 80 ? source.errorMessage.slice(0, 77) + '...' : source.errorMessage}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <SourceStatusBadge status={source.status} />
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT }}>
                    {source.pagesCrawled}/{source.maxPages}
                    <div style={{ fontSize: '11px', color: COLOR_TEXT_SECONDARY }}>
                      {formatNumber(source.totalChars)} chars
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT }}>
                    {source.articlesCreated}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>
                    {formatRelativeTime(source.lastCrawledAt)}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>
                    {source.autoRefresh ? formatRelativeTime(source.nextCrawlAt) : 'Manual'}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'nowrap' }}>
                      <button
                        onClick={() => handleTriggerCrawl(source.id)}
                        disabled={triggering || source.status === 'crawling'}
                        style={{
                          ...buttonStyle('secondary', triggering || source.status === 'crawling'),
                          padding: '4px 10px',
                          fontSize: '12px',
                        }}
                        title="Trigger re-crawl"
                      >
                        {source.status === 'crawling' ? 'Crawling...' : 'Re-crawl'}
                      </button>
                      <button
                        onClick={() => handleTogglePause(source)}
                        disabled={updating || source.status === 'crawling'}
                        style={{
                          ...buttonStyle('secondary', updating || source.status === 'crawling'),
                          padding: '4px 10px',
                          fontSize: '12px',
                        }}
                        title={source.status === 'paused' ? 'Resume auto-refresh' : 'Pause auto-refresh'}
                      >
                        {source.status === 'paused' ? 'Resume' : 'Pause'}
                      </button>
                      {confirmDelete === source.id ? (
                        <>
                          <button
                            onClick={() => handleDelete(source.id)}
                            disabled={deleting}
                            style={{
                              ...buttonStyle('danger', deleting),
                              padding: '4px 10px',
                              fontSize: '12px',
                            }}
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setConfirmDelete(null)}
                            style={{
                              ...buttonStyle('secondary'),
                              padding: '4px 10px',
                              fontSize: '12px',
                            }}
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => setConfirmDelete(source.id)}
                          style={{
                            ...buttonStyle('secondary'),
                            padding: '4px 10px',
                            fontSize: '12px',
                            color: COLOR_DANGER,
                          }}
                          title="Delete source and its KB entries"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default WebsiteSourcesPanel;
