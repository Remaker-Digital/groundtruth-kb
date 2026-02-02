/**
 * AnalyticsOverview - Analytics dashboard with summary cards, intent breakdown,
 * and knowledge gaps table.
 *
 * Summary cards: total conversations, avg response time, resolution rate,
 *   escalation rate, CSAT.
 * Intent breakdown: horizontal bar chart of top intents by count.
 * Knowledge gaps: table of unresolved queries with frequency and last-seen date.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 * Receives auth, API fetch, and notification callbacks from the shell.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useMemo } from 'react';
import type { BaseComponentProps, IntentBreakdown, KnowledgeGap } from './types';
import { useAnalyticsSummary, useIntentBreakdown, useKnowledgeGaps } from './hooks';

// ---------------------------------------------------------------------------
// Style constants
// ---------------------------------------------------------------------------

const BRAND_PRIMARY = '#C41E2A';
const COLOR_SUCCESS = '#22863a';
const COLOR_DANGER = '#d73a49';
const COLOR_GRAY = '#6a737d';
const COLOR_LIGHT_GRAY = '#f6f8fa';
const COLOR_BORDER = '#e1e4e8';
const COLOR_WHITE = '#ffffff';
const COLOR_TEXT = '#24292e';
const COLOR_TEXT_SECONDARY = '#586069';
const COLOR_WARNING = '#e36209';
const FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";
const FONT_MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace";
const BORDER_RADIUS = '6px';

// Bar chart color palette — 8 distinct hues for intent bars
const BAR_COLORS = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#84cc16',
];

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function formatMs(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  const sec = ms / 1000;
  if (sec < 60) return `${sec.toFixed(1)}s`;
  const min = Math.floor(sec / 60);
  const remSec = Math.round(sec % 60);
  return `${min}m ${remSec}s`;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString();
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatRelativeDate(iso: string): string {
  const d = new Date(iso);
  const now = Date.now();
  const diffMs = now - d.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return formatDate(iso);
}

// ---------------------------------------------------------------------------
// Sub-components: shared loading / error / empty
// ---------------------------------------------------------------------------

const LoadingSpinner: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 16px',
      color: COLOR_TEXT_SECONDARY,
    }}
  >
    <div
      style={{
        width: '32px',
        height: '32px',
        border: `3px solid ${COLOR_BORDER}`,
        borderTopColor: BRAND_PRIMARY,
        borderRadius: '50%',
        animation: 'analyticsSpin 0.8s linear infinite',
        marginBottom: '12px',
      }}
    />
    <span style={{ fontSize: '14px' }}>{text}</span>
    <style>{`@keyframes analyticsSpin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

const EmptyState: React.FC<{ icon: string; title: string; subtitle?: string }> = ({ icon, title, subtitle }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '32px 16px',
      color: COLOR_TEXT_SECONDARY,
    }}
  >
    <span style={{ fontSize: '36px', marginBottom: '10px' }}>{icon}</span>
    <span style={{ fontSize: '14px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }}>{title}</span>
    {subtitle && <span style={{ fontSize: '12px' }}>{subtitle}</span>}
  </div>
);

const ErrorBanner: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div
    style={{
      padding: '12px 16px',
      backgroundColor: '#ffeef0',
      border: `1px solid ${COLOR_DANGER}33`,
      borderRadius: BORDER_RADIUS,
      margin: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
    }}
  >
    <span style={{ fontSize: '13px', color: COLOR_DANGER }}>{message}</span>
    {onRetry && (
      <button
        onClick={onRetry}
        style={{
          padding: '4px 12px',
          border: `1px solid ${COLOR_DANGER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: 'transparent',
          color: COLOR_DANGER,
          fontSize: '12px',
          fontFamily: FONT_FAMILY,
          cursor: 'pointer',
          whiteSpace: 'nowrap',
        }}
      >
        Retry
      </button>
    )}
  </div>
);

// ---------------------------------------------------------------------------
// Section header
// ---------------------------------------------------------------------------

const SectionHeader: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => (
  <div style={{ marginBottom: '16px' }}>
    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: COLOR_TEXT }}>{title}</h3>
    {subtitle && (
      <span style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>{subtitle}</span>
    )}
  </div>
);

// ---------------------------------------------------------------------------
// Summary card
// ---------------------------------------------------------------------------

interface SummaryCardProps {
  label: string;
  value: string;
  subtext?: string;
  accentColor?: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ label, value, subtext, accentColor = BRAND_PRIMARY }) => (
  <div
    style={{
      flex: '1 1 180px',
      minWidth: '160px',
      backgroundColor: COLOR_WHITE,
      border: `1px solid ${COLOR_BORDER}`,
      borderRadius: BORDER_RADIUS,
      padding: '16px 20px',
      borderTop: `3px solid ${accentColor}`,
    }}
  >
    <div style={{ fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
      {label}
    </div>
    <div style={{ fontSize: '28px', fontWeight: 700, color: COLOR_TEXT, lineHeight: 1.1, fontFamily: FONT_MONO }}>
      {value}
    </div>
    {subtext && (
      <div style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '4px' }}>
        {subtext}
      </div>
    )}
  </div>
);

// ---------------------------------------------------------------------------
// Horizontal bar chart for intents
// ---------------------------------------------------------------------------

interface IntentBarChartProps {
  intents: IntentBreakdown[];
}

const IntentBarChart: React.FC<IntentBarChartProps> = ({ intents }) => {
  const maxCount = useMemo(() => {
    if (intents.length === 0) return 1;
    return Math.max(...intents.map((i) => i.count), 1);
  }, [intents]);

  if (intents.length === 0) {
    return (
      <EmptyState
        icon="\u{1F4CA}"
        title="No intent data"
        subtitle="Intent breakdown will appear once conversations are processed."
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {intents.map((intent, idx) => {
        const barWidth = Math.max((intent.count / maxCount) * 100, 2);
        const color = BAR_COLORS[idx % BAR_COLORS.length];

        return (
          <div key={intent.intent} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Label */}
            <div
              style={{
                width: '180px',
                minWidth: '120px',
                fontSize: '13px',
                color: COLOR_TEXT,
                fontWeight: 500,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              title={intent.intent}
            >
              {intent.intent}
            </div>

            {/* Bar */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  flex: 1,
                  height: '24px',
                  backgroundColor: COLOR_LIGHT_GRAY,
                  borderRadius: '4px',
                  overflow: 'hidden',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    width: `${barWidth}%`,
                    height: '100%',
                    backgroundColor: color,
                    borderRadius: '4px',
                    transition: 'width 0.4s ease-out',
                    minWidth: '4px',
                  }}
                />
              </div>
              <div
                style={{
                  width: '70px',
                  textAlign: 'right',
                  fontSize: '12px',
                  fontFamily: FONT_MONO,
                  color: COLOR_TEXT_SECONDARY,
                  flexShrink: 0,
                }}
              >
                {formatNumber(intent.count)}{' '}
                <span style={{ fontSize: '11px', color: COLOR_GRAY }}>
                  ({formatPercent(intent.percentage)})
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Knowledge gaps table
// ---------------------------------------------------------------------------

interface KnowledgeGapsTableProps {
  gaps: KnowledgeGap[];
}

const KnowledgeGapsTable: React.FC<KnowledgeGapsTableProps> = ({ gaps }) => {
  if (gaps.length === 0) {
    return (
      <EmptyState
        icon="\u{2705}"
        title="No knowledge gaps detected"
        subtitle="Your knowledge base is covering all customer queries."
      />
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
        <thead>
          <tr style={{ backgroundColor: COLOR_LIGHT_GRAY }}>
            <th
              style={{
                padding: '10px 16px',
                textAlign: 'left',
                fontSize: '12px',
                fontWeight: 600,
                color: COLOR_TEXT_SECONDARY,
                borderBottom: `1px solid ${COLOR_BORDER}`,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}
            >
              Unresolved Query
            </th>
            <th
              style={{
                padding: '10px 16px',
                textAlign: 'right',
                fontSize: '12px',
                fontWeight: 600,
                color: COLOR_TEXT_SECONDARY,
                borderBottom: `1px solid ${COLOR_BORDER}`,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                width: '100px',
              }}
            >
              Frequency
            </th>
            <th
              style={{
                padding: '10px 16px',
                textAlign: 'right',
                fontSize: '12px',
                fontWeight: 600,
                color: COLOR_TEXT_SECONDARY,
                borderBottom: `1px solid ${COLOR_BORDER}`,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                width: '120px',
              }}
            >
              Last Seen
            </th>
          </tr>
        </thead>
        <tbody>
          {gaps.map((gap, idx) => (
            <tr
              key={`${gap.query}-${idx}`}
              style={{ backgroundColor: idx % 2 === 0 ? COLOR_WHITE : COLOR_LIGHT_GRAY }}
            >
              <td
                style={{
                  padding: '10px 16px',
                  borderBottom: `1px solid ${COLOR_BORDER}`,
                  color: COLOR_TEXT,
                  fontSize: '13px',
                }}
              >
                {gap.query}
              </td>
              <td
                style={{
                  padding: '10px 16px',
                  borderBottom: `1px solid ${COLOR_BORDER}`,
                  textAlign: 'right',
                  fontFamily: FONT_MONO,
                  fontSize: '13px',
                  color: gap.frequency >= 10 ? COLOR_DANGER : gap.frequency >= 5 ? COLOR_WARNING : COLOR_TEXT,
                  fontWeight: gap.frequency >= 10 ? 600 : 400,
                }}
              >
                {gap.frequency}
              </td>
              <td
                style={{
                  padding: '10px 16px',
                  borderBottom: `1px solid ${COLOR_BORDER}`,
                  textAlign: 'right',
                  fontSize: '12px',
                  color: COLOR_TEXT_SECONDARY,
                }}
              >
                {formatRelativeDate(gap.lastSeen)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const AnalyticsOverview: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  // Data hooks
  const {
    data: summary,
    loading: summaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useAnalyticsSummary(apiFetch);

  const {
    data: intentData,
    loading: intentsLoading,
    error: intentsError,
    refetch: refetchIntents,
  } = useIntentBreakdown(apiFetch);
  const intents = intentData?.intents ?? [];

  const {
    data: gapsData,
    loading: gapsLoading,
    error: gapsError,
    refetch: refetchGaps,
  } = useKnowledgeGaps(apiFetch);
  const gaps = gapsData?.gaps ?? [];

  // Determine overall loading state for the initial load
  const isInitialLoad = summaryLoading && !summary;

  if (isInitialLoad) {
    return (
      <div
        style={{
          fontFamily: FONT_FAMILY,
          border: `1px solid ${COLOR_BORDER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: COLOR_WHITE,
          minHeight: '500px',
        }}
      >
        <LoadingSpinner text="Loading analytics..." />
      </div>
    );
  }

  // Determine rating color for CSAT
  function csatColor(score: number | null): string {
    if (score === null) return COLOR_GRAY;
    if (score >= 4.0) return COLOR_SUCCESS;
    if (score >= 3.0) return COLOR_WARNING;
    return COLOR_DANGER;
  }

  // Determine rating color for escalation rate
  function escalationColor(rate: number): string {
    if (rate <= 0.05) return COLOR_SUCCESS;
    if (rate <= 0.15) return COLOR_WARNING;
    return COLOR_DANGER;
  }

  return (
    <div
      style={{
        fontFamily: FONT_FAMILY,
        border: `1px solid ${COLOR_BORDER}`,
        borderRadius: BORDER_RADIUS,
        backgroundColor: COLOR_WHITE,
        minHeight: '500px',
      }}
    >
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
            Analytics Overview
          </h2>
          {summary?.period && (
            <span style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>
              Period: {summary.period}
            </span>
          )}
        </div>
        <button
          onClick={() => {
            refetchSummary();
            refetchIntents();
            refetchGaps();
          }}
          style={{
            padding: '6px 14px',
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            backgroundColor: COLOR_WHITE,
            color: COLOR_TEXT,
            fontSize: '12px',
            fontFamily: FONT_FAMILY,
            cursor: 'pointer',
            fontWeight: 500,
          }}
        >
          Refresh
        </button>
      </div>

      <div style={{ padding: '20px' }}>
        {/* Summary cards */}
        {summaryError && (
          <ErrorBanner message={summaryError} onRetry={refetchSummary} />
        )}

        {summary && (
          <div
            style={{
              display: 'flex',
              gap: '16px',
              flexWrap: 'wrap',
              marginBottom: '32px',
            }}
          >
            <SummaryCard
              label="Total Conversations"
              value={formatNumber(summary.totalConversations)}
              accentColor="#3b82f6"
            />
            <SummaryCard
              label="Avg Response Time"
              value={formatMs(summary.avgResponseTime)}
              subtext={summary.avgResponseTime <= 2000 ? 'Within SLA' : 'Above P95 target'}
              accentColor={summary.avgResponseTime <= 2000 ? COLOR_SUCCESS : COLOR_WARNING}
            />
            <SummaryCard
              label="Resolution Rate"
              value={formatPercent(summary.resolutionRate)}
              accentColor={summary.resolutionRate >= 0.8 ? COLOR_SUCCESS : COLOR_WARNING}
            />
            <SummaryCard
              label="Escalation Rate"
              value={formatPercent(summary.escalationRate)}
              accentColor={escalationColor(summary.escalationRate)}
            />
            <SummaryCard
              label="CSAT"
              value={summary.customerSatisfaction !== null ? summary.customerSatisfaction.toFixed(1) : '--'}
              subtext={summary.customerSatisfaction !== null ? 'out of 5.0' : 'No ratings yet'}
              accentColor={csatColor(summary.customerSatisfaction)}
            />
          </div>
        )}

        {/* Intent breakdown */}
        <div
          style={{
            marginBottom: '32px',
            padding: '20px',
            backgroundColor: COLOR_LIGHT_GRAY,
            borderRadius: BORDER_RADIUS,
            border: `1px solid ${COLOR_BORDER}`,
          }}
        >
          <SectionHeader
            title="Intent Breakdown"
            subtitle="Top customer intents by conversation count"
          />

          {intentsError && (
            <ErrorBanner message={intentsError} onRetry={refetchIntents} />
          )}

          {intentsLoading && intents.length === 0 && (
            <LoadingSpinner text="Loading intents..." />
          )}

          {!intentsLoading && !intentsError && (
            <IntentBarChart intents={intents} />
          )}
        </div>

        {/* Knowledge gaps */}
        <div
          style={{
            padding: '20px',
            backgroundColor: COLOR_LIGHT_GRAY,
            borderRadius: BORDER_RADIUS,
            border: `1px solid ${COLOR_BORDER}`,
          }}
        >
          <SectionHeader
            title="Knowledge Gaps"
            subtitle="Queries the AI could not resolve — consider adding KB articles for these topics"
          />

          {gapsError && (
            <ErrorBanner message={gapsError} onRetry={refetchGaps} />
          )}

          {gapsLoading && gaps.length === 0 && (
            <LoadingSpinner text="Loading knowledge gaps..." />
          )}

          {!gapsLoading && !gapsError && (
            <KnowledgeGapsTable gaps={gaps} />
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsOverview;
