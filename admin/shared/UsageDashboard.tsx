/**
 * UsageDashboard — Real-time billing usage dashboard.
 *
 * Three-section layout providing full billing transparency (Decision #25):
 *
 *   1. **Top — Usage Summary:**  Meter gauge (used / total included allowance),
 *      pack balance, overage estimate, and active billing alerts.
 *
 *   2. **Middle — Daily Volume Chart:**  Simple CSS bar chart built from
 *      useDailyVolume data showing total vs billable conversations per day.
 *
 *   3. **Bottom — Conversation List:**  Paginated table of billable
 *      conversations with CSV export.
 *
 * API endpoints consumed:
 *   GET /api/dashboard/usage                — Usage summary (Layer 1)
 *   GET /api/dashboard/usage/daily          — Daily volume (Layer 1)
 *   GET /api/dashboard/conversations        — Paginated conversation list (Layer 2)
 *   GET /api/dashboard/conversations/export — CSV download (Layer 2)
 *
 * Props (from shell):
 *   - tenantContext — authenticated tenant information
 *   - apiFetch     — shell-provided fetch wrapper with auth
 *   - onNotify     — shell toast/banner callback
 *
 * Dependencies:
 *   - ../types  — BaseComponentProps, UsageDashboard, DailyVolume,
 *                  ConversationSummary, PaginatedList
 *   - ../hooks  — useUsageDashboard, useDailyVolume, useConversationList
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useMemo } from 'react';
import type {
  BaseComponentProps,
  UsageDashboard as UsageDashboardData,
  DailyVolume,
  ConversationSummary,
} from './types';
import { useUsageDashboard, useDailyVolume, useConversationList } from './hooks';
import { HelpTooltip } from './HelpTooltip';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PAGE_SIZE = 50;

// Generate billing period options for the dropdown (current + past 5 months)
function getBillingPeriodOptions(): Array<{ value: string; label: string }> {
  const options: Array<{ value: string; label: string }> = [];
  const now = new Date();
  for (let i = 0; i < 6; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    const label = d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
    options.push({ value, label });
  }
  return options;
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const st = {
  container: {
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    color: '#1a1a1a',
  } as React.CSSProperties,

  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 28,
    flexWrap: 'wrap' as const,
    gap: 12,
  } as React.CSSProperties,

  title: {
    fontSize: 24,
    fontWeight: 600,
    margin: 0,
  } as React.CSSProperties,

  subtitle: {
    fontSize: 13,
    color: '#888',
    margin: '4px 0 0 0',
  } as React.CSSProperties,

  periodSelect: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    backgroundColor: '#fff',
    color: '#1a1a1a',
    outline: 'none',
  } as React.CSSProperties,

  // -- Section wrappers --
  section: {
    marginBottom: 32,
  } as React.CSSProperties,

  sectionTitle: {
    fontSize: 16,
    fontWeight: 600,
    color: '#1a1a1a',
    margin: '0 0 16px 0',
  } as React.CSSProperties,

  // -- Summary cards --
  cardsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: 16,
    marginBottom: 20,
  } as React.CSSProperties,

  card: {
    padding: '16px 20px',
    backgroundColor: '#fafafa',
    border: '1px solid #e5e5e5',
    borderRadius: 8,
  } as React.CSSProperties,

  cardLabel: {
    fontSize: 12,
    fontWeight: 500,
    color: '#888',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    margin: '0 0 6px 0',
  } as React.CSSProperties,

  cardValue: {
    fontSize: 28,
    fontWeight: 700,
    color: '#1a1a1a',
    margin: 0,
    lineHeight: 1.1,
  } as React.CSSProperties,

  cardSub: {
    fontSize: 12,
    color: '#888',
    margin: '4px 0 0 0',
  } as React.CSSProperties,

  // -- Meter --
  meterContainer: {
    marginBottom: 20,
    padding: '16px 20px',
    backgroundColor: '#fafafa',
    border: '1px solid #e5e5e5',
    borderRadius: 8,
  } as React.CSSProperties,

  meterLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: 8,
  } as React.CSSProperties,

  meterTrack: {
    height: 12,
    backgroundColor: '#e5e5e5',
    borderRadius: 6,
    overflow: 'hidden',
    position: 'relative' as const,
  } as React.CSSProperties,

  meterFill: (percent: number, isOverage: boolean): React.CSSProperties => ({
    height: '100%',
    width: `${Math.min(percent, 100)}%`,
    backgroundColor: isOverage ? '#ff3621' : percent > 80 ? '#f59e0b' : '#16a34a',
    borderRadius: 6,
    transition: 'width 0.4s ease, background-color 0.3s ease',
  }),

  meterOverflow: (overflowPercent: number): React.CSSProperties => ({
    position: 'absolute',
    top: 0,
    right: 0,
    height: '100%',
    width: `${Math.min(overflowPercent, 20)}%`,
    backgroundColor: '#ff3621',
    opacity: 0.3,
    borderRadius: '0 6px 6px 0',
  }),

  // -- Alerts --
  alertsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 8,
  } as React.CSSProperties,

  alertItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '10px 14px',
    backgroundColor: '#fef3c7',
    border: '1px solid #fde68a',
    borderRadius: 6,
    fontSize: 13,
    color: '#92400e',
  } as React.CSSProperties,

  alertIcon: {
    fontSize: 16,
    flexShrink: 0,
  } as React.CSSProperties,

  // -- Bar chart --
  chartContainer: {
    overflowX: 'auto' as const,
  } as React.CSSProperties,

  chartInner: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: 4,
    minHeight: 160,
    padding: '8px 0 0 0',
  } as React.CSSProperties,

  chartColumn: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    flex: '1 0 28px',
    minWidth: 28,
    maxWidth: 48,
  } as React.CSSProperties,

  barGroup: {
    display: 'flex',
    gap: 2,
    alignItems: 'flex-end',
    width: '100%',
    justifyContent: 'center',
  } as React.CSSProperties,

  bar: (height: number, color: string): React.CSSProperties => ({
    width: 10,
    height: Math.max(height, 2),
    backgroundColor: color,
    borderRadius: '3px 3px 0 0',
    transition: 'height 0.3s ease',
  }),

  chartLabel: {
    fontSize: 10,
    color: '#888',
    marginTop: 6,
    textAlign: 'center' as const,
    whiteSpace: 'nowrap' as const,
  } as React.CSSProperties,

  chartLegend: {
    display: 'flex',
    gap: 16,
    marginTop: 12,
    fontSize: 12,
    color: '#666',
  } as React.CSSProperties,

  legendDot: (color: string): React.CSSProperties => ({
    display: 'inline-block',
    width: 10,
    height: 10,
    borderRadius: '50%',
    backgroundColor: color,
    marginRight: 6,
  }),

  // -- Conversation table --
  tableWrapper: {
    overflowX: 'auto' as const,
    border: '1px solid #e5e5e5',
    borderRadius: 8,
  } as React.CSSProperties,

  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
    fontSize: 13,
  } as React.CSSProperties,

  th: {
    textAlign: 'left' as const,
    padding: '10px 12px',
    backgroundColor: '#fafafa',
    borderBottom: '1px solid #e5e5e5',
    fontWeight: 600,
    color: '#555',
    fontSize: 12,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.3px',
    whiteSpace: 'nowrap' as const,
  } as React.CSSProperties,

  td: {
    padding: '10px 12px',
    borderBottom: '1px solid #f0f0f0',
    color: '#333',
    whiteSpace: 'nowrap' as const,
  } as React.CSSProperties,

  statusBadge: (isBillable: boolean): React.CSSProperties => ({
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
    backgroundColor: isBillable ? '#fef2f2' : '#f0fdf4',
    color: isBillable ? '#991b1b' : '#166534',
  }),

  criticBadge: (passed: boolean | null): React.CSSProperties => ({
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
    backgroundColor:
      passed === null ? '#f5f5f5' : passed ? '#f0fdf4' : '#fef2f2',
    color: passed === null ? '#888' : passed ? '#166534' : '#991b1b',
  }),

  // -- Pagination --
  pagination: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
    flexWrap: 'wrap' as const,
    gap: 12,
  } as React.CSSProperties,

  pageInfo: {
    fontSize: 13,
    color: '#888',
  } as React.CSSProperties,

  pageButtons: {
    display: 'flex',
    gap: 8,
  } as React.CSSProperties,

  pageBtn: (disabled: boolean): React.CSSProperties => ({
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 500,
    backgroundColor: 'transparent',
    color: disabled ? '#ccc' : '#555',
    border: `1px solid ${disabled ? '#eee' : '#d0d0d0'}`,
    borderRadius: 6,
    cursor: disabled ? 'not-allowed' : 'pointer',
  }),

  // -- Export button --
  exportBtn: {
    padding: '8px 16px',
    fontSize: 13,
    fontWeight: 500,
    backgroundColor: 'transparent',
    color: '#555',
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  // -- States --
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 64,
    fontSize: 14,
    color: '#888',
  } as React.CSSProperties,

  error: {
    padding: '16px 20px',
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 8,
    color: '#991b1b',
    fontSize: 14,
    lineHeight: 1.5,
  } as React.CSSProperties,

  empty: {
    padding: '32px 20px',
    textAlign: 'center' as const,
    color: '#888',
    fontSize: 14,
  } as React.CSSProperties,

  btnSecondary: {
    padding: '8px 20px',
    fontSize: 14,
    fontWeight: 500,
    backgroundColor: 'transparent',
    color: '#555',
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  tableHeaderRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  } as React.CSSProperties,
} as const;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatNumber(n: number | undefined | null): string {
  if (n == null) return '0';
  return n.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function formatCurrency(n: number | undefined | null): string {
  if (n == null) return '$0.00';
  return `$${n.toFixed(2)}`;
}

function formatShortDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch {
    return iso;
  }
}

function formatDateTime(iso: string | null): string {
  if (!iso) return '--';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

// Usage meter gauge
interface UsageMeterProps {
  usage: UsageDashboardData;
}

const UsageMeter: React.FC<UsageMeterProps> = ({ usage }) => {
  const percent = usage.includedAllowance > 0
    ? (usage.totalConversations / usage.includedAllowance) * 100
    : 0;
  const isOverage = usage.totalConversations > usage.includedAllowance;
  const overflowPercent = isOverage
    ? ((usage.totalConversations - usage.includedAllowance) / usage.includedAllowance) * 100
    : 0;

  return (
    <div style={st.meterContainer}>
      <div style={st.meterLabel}>
        <div>
          <span style={{ fontSize: 14, fontWeight: 600, color: '#1a1a1a' }}>
            Conversations Used
          </span>
          <span style={{ fontSize: 13, color: '#888', marginLeft: 8 }}>
            {formatNumber(usage.totalConversations)} of{' '}
            {formatNumber(usage.includedAllowance)} included
          </span>
        </div>
        <span
          style={{
            fontSize: 14,
            fontWeight: 600,
            color: isOverage ? '#ff3621' : percent > 80 ? '#f59e0b' : '#16a34a',
          }}
        >
          {(percent ?? 0).toFixed(0)}%
        </span>
      </div>

      <div style={st.meterTrack}>
        <div style={st.meterFill(percent, isOverage)} />
        {isOverage && <div style={st.meterOverflow(overflowPercent)} />}
      </div>

      {isOverage && (
        <div
          style={{
            fontSize: 12,
            color: '#ff3621',
            marginTop: 8,
            fontWeight: 500,
          }}
        >
          {formatNumber(usage.overageConversations)} overage conversation
          {usage.overageConversations === 1 ? '' : 's'} &middot; Estimated
          cost: {formatCurrency(usage.estimatedOverageCost)}<HelpTooltip text="Projected cost for overage conversations at your tier's per-conversation rate." docLink="https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" />
        </div>
      )}
    </div>
  );
};

// Summary cards
interface SummaryCardsProps {
  usage: UsageDashboardData;
}

const SummaryCards: React.FC<SummaryCardsProps> = ({ usage }) => (
  <div style={st.cardsRow}>
    <div style={st.card}>
      <p style={st.cardLabel}>Remaining included<HelpTooltip text="Conversations used from your plan's included monthly allowance." docLink="https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" /></p>
      <p style={st.cardValue}>{formatNumber(usage.remainingIncluded)}</p>
      <p style={st.cardSub}>of {formatNumber(usage.includedAllowance)}</p>
    </div>

    <div style={st.card}>
      <p style={st.cardLabel}>Pack balance<HelpTooltip text="Remaining pre-purchased conversation credits (FIFO, 90-day validity)." docLink="https://agentredcx.com/docs/billing/overview#conversation-packs" /></p>
      <p style={st.cardValue}>{formatNumber(usage.packBalance)}</p>
      <p style={st.cardSub}>pre-purchased conversations</p>
    </div>

    <div style={st.card}>
      <p style={st.cardLabel}>Overage<HelpTooltip text="Conversations beyond your included allowance and pack balance, billed at your tier's overage rate." docLink="https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" /></p>
      <p
        style={{
          ...st.cardValue,
          color: usage.overageConversations > 0 ? '#ff3621' : '#1a1a1a',
        }}
      >
        {formatNumber(usage.overageConversations)}
      </p>
      <p style={st.cardSub}>
        {usage.overageConversations > 0
          ? formatCurrency(usage.estimatedOverageCost)
          : 'no overage'}
      </p>
    </div>

    <div style={st.card}>
      <p style={st.cardLabel}>Overage reported</p>
      <p style={st.cardValue}>{formatNumber(usage.overageReported)}</p>
      <p style={st.cardSub}>reported to billing</p>
    </div>
  </div>
);

// Alerts panel
interface AlertsPanelProps {
  alerts: string[];
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts }) => {
  if (alerts.length === 0) return null;

  return (
    <div style={st.alertsContainer}>
      {alerts.map((alert, idx) => (
        <div key={idx} style={st.alertItem}>
          <span style={st.alertIcon} role="img" aria-label="Warning">
            !
          </span>
          {alert}
        </div>
      ))}
    </div>
  );
};

// Daily volume bar chart
interface DailyChartProps {
  days: DailyVolume[];
}

const DailyChart: React.FC<DailyChartProps> = ({ days }) => {
  const maxValue = useMemo(() => {
    let max = 1;
    for (const d of days) {
      if (d.total > max) max = d.total;
    }
    return max;
  }, [days]);

  const chartHeight = 140;

  if (days.length === 0) {
    return <div style={st.empty}>No daily volume data available.</div>;
  }

  return (
    <div>
      <div style={st.chartContainer}>
        <div style={st.chartInner}>
          {days.map((day) => {
            const totalH = (day.total / maxValue) * chartHeight;
            const billableH = (day.billable / maxValue) * chartHeight;
            return (
              <div key={day.date} style={st.chartColumn}>
                <div style={st.barGroup}>
                  <div
                    style={st.bar(totalH, '#d0d0d0')}
                    title={`Total: ${day.total}`}
                  />
                  <div
                    style={st.bar(billableH, '#ff3621')}
                    title={`Billable: ${day.billable}`}
                  />
                </div>
                <div style={st.chartLabel}>{formatShortDate(day.date)}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={st.chartLegend}>
        <span>
          <span style={st.legendDot('#d0d0d0')} />
          Total
        </span>
        <span>
          <span style={st.legendDot('#ff3621')} />
          Billable
        </span>
      </div>
    </div>
  );
};

// Conversation table
interface ConversationTableProps {
  conversations: ConversationSummary[];
  totalCount: number;
  offset: number;
  pageSize: number;
  onPageChange: (newOffset: number) => void;
  loading: boolean;
}

const ConversationTable: React.FC<ConversationTableProps> = ({
  conversations,
  totalCount,
  offset,
  pageSize,
  onPageChange,
  loading,
}) => {
  if (!loading && conversations.length === 0) {
    return <div style={st.empty}>No conversations found for this period.</div>;
  }

  const currentPage = Math.floor(offset / pageSize) + 1;
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
  const hasPrev = offset > 0;
  const hasNext = offset + pageSize < totalCount;

  return (
    <div>
      <div style={st.tableWrapper}>
        <table style={st.table}>
          <thead>
            <tr>
              <th style={st.th}>ID</th>
              <th style={st.th}>Status</th>
              <th style={st.th}>Customer</th>
              <th style={st.th}>Billable</th>
              <th style={st.th}>Messages</th>
              <th style={st.th}>Turns</th>
              <th style={st.th}>Started</th>
              <th style={st.th}>Ended</th>
              <th style={st.th}>Model</th>
              <th style={st.th}>Critic</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td style={st.td} colSpan={10}>
                  <div style={{ textAlign: 'center', padding: 16, color: '#888' }}>
                    Loading conversations...
                  </div>
                </td>
              </tr>
            ) : (
              conversations.map((conv) => (
                <tr key={conv.conversationId}>
                  <td
                    style={{
                      ...st.td,
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 12,
                      maxWidth: 120,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={conv.conversationId}
                  >
                    {conv.conversationId.slice(0, 12)}...
                  </td>
                  <td style={st.td}>{conv.status ?? '--'}</td>
                  <td
                    style={{
                      ...st.td,
                      maxWidth: 100,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={conv.customerId ?? undefined}
                  >
                    {conv.customerId ?? '--'}
                  </td>
                  <td style={st.td}>
                    <span style={st.statusBadge(conv.isBillable)}>
                      {conv.isBillable ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td style={st.td}>{conv.messageCount}</td>
                  <td style={st.td}>{conv.turnCount}</td>
                  <td style={st.td}>{formatDateTime(conv.startedAt)}</td>
                  <td style={st.td}>{formatDateTime(conv.endedAt)}</td>
                  <td style={{ ...st.td, fontSize: 12 }}>
                    {conv.modelUsed ?? '--'}
                  </td>
                  <td style={st.td}>
                    <span style={st.criticBadge(conv.criticPassed)}>
                      {conv.criticPassed === null
                        ? 'N/A'
                        : conv.criticPassed
                          ? 'Pass'
                          : 'Fail'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div style={st.pagination}>
        <span style={st.pageInfo}>
          Showing {offset + 1}--{Math.min(offset + pageSize, totalCount)} of{' '}
          {formatNumber(totalCount)} conversations
        </span>
        <div style={st.pageButtons}>
          <button
            style={st.pageBtn(!hasPrev)}
            disabled={!hasPrev}
            onClick={() => onPageChange(Math.max(0, offset - pageSize))}
          >
            Previous
          </button>
          <span
            style={{
              padding: '6px 10px',
              fontSize: 13,
              color: '#555',
              alignSelf: 'center',
            }}
          >
            Page {currentPage} of {totalPages}
          </span>
          <button
            style={st.pageBtn(!hasNext)}
            disabled={!hasNext}
            onClick={() => onPageChange(offset + pageSize)}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const UsageDashboard: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  // ---- state ----
  const [billingPeriod, setBillingPeriod] = useState<string | undefined>(undefined);
  const [convOffset, setConvOffset] = useState(0);
  const [exporting, setExporting] = useState(false);

  // ---- hooks ----
  const {
    data: usageData,
    loading: usageLoading,
    error: usageError,
    refetch: refetchUsage,
  } = useUsageDashboard(apiFetch, billingPeriod);

  const {
    data: dailyData,
    loading: dailyLoading,
    error: dailyError,
  } = useDailyVolume(apiFetch, billingPeriod);

  const {
    data: convData,
    loading: convLoading,
    error: convError,
  } = useConversationList(apiFetch, billingPeriod, convOffset, PAGE_SIZE);

  // ---- period options ----
  const periodOptions = useMemo(() => getBillingPeriodOptions(), []);

  // ---- handlers ----
  const handlePeriodChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const val = e.target.value;
      setBillingPeriod(val || undefined);
      setConvOffset(0);
    },
    [],
  );

  const handleExportCsv = useCallback(async () => {
    if (exporting) return;
    setExporting(true);

    try {
      const params = new URLSearchParams();
      if (billingPeriod) params.set('billing_period', billingPeriod);
      const path = `/api/dashboard/conversations/export?${params}`;
      const resp = await apiFetch(path);

      if (!resp.ok) {
        const body = await resp.text().catch(() => '');
        throw new Error(`${resp.status}: ${body}`);
      }

      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversations-${billingPeriod ?? 'current'}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      onNotify('CSV export downloaded.', 'success');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Export failed';
      onNotify(`Export failed: ${msg}`, 'error');
    } finally {
      setExporting(false);
    }
  }, [exporting, billingPeriod, apiFetch, onNotify]);

  const handlePageChange = useCallback((newOffset: number) => {
    setConvOffset(newOffset);
  }, []);

  // ---- loading state (initial) ----
  if (usageLoading && !usageData) {
    return (
      <div style={st.container}>
        <div style={st.loading}>Loading usage dashboard...</div>
      </div>
    );
  }

  // ---- error state ----
  if (usageError && !usageData) {
    return (
      <div style={st.container}>
        <div style={st.error}>
          <strong>Failed to load usage dashboard.</strong>
          <br />
          {usageError}
          <br />
          <button
            style={{ ...st.btnSecondary, marginTop: 12 }}
            onClick={refetchUsage}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Derive data
  const usage = usageData;
  const days: DailyVolume[] = dailyData?.days ?? [];
  const conversations: ConversationSummary[] = convData?.items ?? [];
  const convTotalCount = convData?.totalCount ?? 0;

  return (
    <div style={st.container}>
      {/* Header */}
      <div style={st.header}>
        <div>
          <h2 style={st.title}>Usage dashboard</h2>
          <p style={st.subtitle}>
            {tenantContext.tier} tier &middot;{' '}
            {usage?.billingPeriod ?? 'current period'}
          </p>
        </div>

        <select
          style={st.periodSelect}
          value={billingPeriod ?? ''}
          onChange={handlePeriodChange}
        >
          <option value="">Current period</option>
          {periodOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Section 1: Usage Summary */}
      <div style={st.section}>
        <h3 style={st.sectionTitle}>Usage summary</h3>

        {usage ? (
          <>
            <UsageMeter usage={usage} />
            <SummaryCards usage={usage} />
            {(usage.activeAlerts ?? []).length > 0 && (
              <AlertsPanel alerts={usage.activeAlerts ?? []} />
            )}
          </>
        ) : (
          <div style={st.empty}>No usage data available.</div>
        )}
      </div>

      {/* Section 2: Daily Volume Chart */}
      <div style={st.section}>
        <h3 style={st.sectionTitle}>Daily volume<HelpTooltip text="Total and billable conversations per day for the selected billing period." docLink="https://agentredcx.com/docs/billing/overview#usage-dashboard" /></h3>

        {dailyLoading && days.length === 0 ? (
          <div style={{ padding: 24, textAlign: 'center', color: '#888', fontSize: 14 }}>
            Loading chart data...
          </div>
        ) : dailyError ? (
          <div style={st.error}>
            Failed to load daily volume: {dailyError}
          </div>
        ) : (
          <DailyChart days={days} />
        )}
      </div>

      {/* Section 3: Conversation List */}
      <div style={st.section}>
        <div style={st.tableHeaderRow}>
          <h3 style={st.sectionTitle}>Conversations<HelpTooltip text="Conversations where the AI produced at least one response. Non-billable: test, admin, health-check, and system conversations." docLink="https://agentredcx.com/docs/billing/billable-conversation-spec" /></h3>
          <button
            style={{
              ...st.exportBtn,
              ...(exporting ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            onClick={handleExportCsv}
            disabled={exporting}
          >
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
        </div>

        {convError ? (
          <div style={st.error}>
            Failed to load conversations: {convError}
          </div>
        ) : (
          <ConversationTable
            conversations={conversations}
            totalCount={convTotalCount}
            offset={convOffset}
            pageSize={PAGE_SIZE}
            onPageChange={handlePageChange}
            loading={convLoading}
          />
        )}
      </div>
    </div>
  );
};

export default UsageDashboard;
