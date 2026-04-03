/**
 * Quality hooks — knowledge score, gap review, and preview chat.
 *
 * Domain hooks for Track B Phase 2 (SPEC-1872, SPEC-1873).
 * Phase 1: useKnowledgeScore, useGapReview (GET endpoints).
 * Phase 2: usePreviewChat, usePreviewTrace (POST SSE + GET, deferred).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Types — Knowledge Score (SPEC-1873)
// ---------------------------------------------------------------------------

export interface ScoreFactors {
  coverage: number;
  relevance: number;
  escalationRate: number;
  freshness: number;
}

export interface KnowledgeScoreResponse {
  score: number;
  factors: ScoreFactors;
  totalConversations: number;
  unansweredCount: number;
  kbEntryCount: number;
  freshEntryCount: number;
  trend: {
    direction?: 'up' | 'down' | '=';
    delta?: number;
    previous?: number | null;
  };
}

export interface GapCluster {
  intent: string;
  sampleQuestion: string;
  frequency: number;
  lastOccurrence: string;
  suggestedAction: string;
  priorityScore: number;
  conversationIds: string[];
}

export interface GapReviewResponse {
  tenantId: string;
  since: string;
  until: string;
  totalGaps: number;
  clusters: GapCluster[];
}

// ---------------------------------------------------------------------------
// Hooks — Knowledge Score
// ---------------------------------------------------------------------------

/**
 * Fetch composite knowledge quality score with factor breakdown.
 * Professional+ tier required (backend returns 403 for lower tiers).
 * Pass `enabled = false` to skip the fetch (prevents 403-triggered logout).
 */
export function useKnowledgeScore(apiFetch: ApiFetch, since?: string, enabled = true) {
  const params = since ? `?since=${encodeURIComponent(since)}` : '';
  return useApi<KnowledgeScoreResponse>(apiFetch, `/api/admin/knowledge/score${params}`, enabled);
}

/**
 * Fetch clustered unanswered-question gap review.
 * Professional+ tier required (backend returns 403 for lower tiers).
 * Pass `enabled: false` in opts to skip the fetch.
 */
export function useGapReview(
  apiFetch: ApiFetch,
  opts?: { since?: string; until?: string; limit?: number; enabled?: boolean },
) {
  const params = new URLSearchParams();
  if (opts?.since) params.set('since', opts.since);
  if (opts?.until) params.set('until', opts.until);
  if (opts?.limit) params.set('limit', String(opts.limit));
  const qs = params.toString();
  return useApi<GapReviewResponse>(apiFetch, `/api/admin/knowledge/gaps/review${qs ? `?${qs}` : ''}`, opts?.enabled ?? true);
}

// ---------------------------------------------------------------------------
// Types — Preview Chat (SPEC-1872)
// ---------------------------------------------------------------------------

/** SSE event types emitted by the pipeline + preview trace. */
export type PreviewEventType = 'stage' | 'token' | 'validated' | 'retracted' | 'done' | 'error' | 'trace';

export interface PreviewSSEEvent {
  event: PreviewEventType;
  data: Record<string, unknown>;
}

export interface PreviewTraceResponse {
  conversationId: string;
  trace: Record<string, unknown>;
}

export interface PreviewChatState {
  /** Accumulated response text from token events. */
  responseText: string;
  /** Pipeline trace from the final trace event. */
  trace: Record<string, unknown> | null;
  /** Conversation ID from response headers or trace event. */
  conversationId: string | null;
  /** Whether the stream is currently active. */
  streaming: boolean;
  /** Error message if the stream failed. */
  error: string | null;
  /** Whether the critic validated the response. */
  validated: boolean;
  /** Whether the response was retracted by critic. */
  retracted: boolean;
  /** Retraction fallback text (replaces responseText). */
  retractionText: string | null;
  /** Stage progress events. */
  stages: Array<{ stage: string; status: string }>;
}

// ---------------------------------------------------------------------------
// POST-SSE parser — new code path (not reused from widget)
// ---------------------------------------------------------------------------

/**
 * Parse a raw SSE text chunk into structured events.
 * SSE format: "event: <type>\ndata: <json>\n\n"
 */
function parseSSEChunk(chunk: string): PreviewSSEEvent[] {
  const events: PreviewSSEEvent[] = [];
  const blocks = chunk.split('\n\n').filter(Boolean);
  for (const block of blocks) {
    const lines = block.split('\n');
    let eventType: PreviewEventType = 'token';
    let dataStr = '';
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.slice(7).trim() as PreviewEventType;
      } else if (line.startsWith('data: ')) {
        dataStr = line.slice(6);
      }
    }
    if (dataStr) {
      try {
        events.push({ event: eventType, data: JSON.parse(dataStr) });
      } catch {
        events.push({ event: eventType, data: { raw: dataStr } });
      }
    }
  }
  return events;
}

// ---------------------------------------------------------------------------
// Hooks — Preview Chat
// ---------------------------------------------------------------------------

/**
 * POST-SSE hook for preview chat.
 * Returns a `send` function and current stream state.
 * Each call to `send` aborts any previous stream.
 */
export function usePreviewChat(apiFetch: ApiFetch): {
  state: PreviewChatState;
  send: (message: string, configOverrides?: Record<string, unknown>) => void;
  reset: () => void;
} {
  const [state, setState] = React.useState<PreviewChatState>({
    responseText: '',
    trace: null,
    conversationId: null,
    streaming: false,
    error: null,
    validated: false,
    retracted: false,
    retractionText: null,
    stages: [],
  });

  const abortRef = React.useRef<AbortController | null>(null);

  const reset = React.useCallback(() => {
    abortRef.current?.abort();
    setState({
      responseText: '',
      trace: null,
      conversationId: null,
      streaming: false,
      error: null,
      validated: false,
      retracted: false,
      retractionText: null,
      stages: [],
    });
  }, []);

  const send = React.useCallback(
    (message: string, configOverrides?: Record<string, unknown>) => {
      // Abort previous stream
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setState({
        responseText: '',
        trace: null,
        conversationId: null,
        streaming: true,
        error: null,
        validated: false,
        retracted: false,
        retractionText: null,
        stages: [],
      });

      (async () => {
        try {
          const resp = await apiFetch('/api/admin/preview/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message,
              ...(configOverrides ? { config_overrides: configOverrides } : {}),
            }),
            signal: controller.signal,
          });

          if (!resp.ok) {
            const body = await resp.text().catch(() => '');
            setState((s) => ({ ...s, streaming: false, error: `${resp.status}: ${body}` }));
            return;
          }

          const convId = resp.headers.get('X-Conversation-Id');
          if (convId) {
            setState((s) => ({ ...s, conversationId: convId }));
          }

          const reader = resp.body?.getReader();
          if (!reader) {
            setState((s) => ({ ...s, streaming: false, error: 'No response stream' }));
            return;
          }

          const decoder = new TextDecoder();
          let buffer = '';

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE blocks (separated by \n\n)
            const lastDoubleNewline = buffer.lastIndexOf('\n\n');
            if (lastDoubleNewline === -1) continue;

            const complete = buffer.slice(0, lastDoubleNewline + 2);
            buffer = buffer.slice(lastDoubleNewline + 2);

            const events = parseSSEChunk(complete);
            for (const evt of events) {
              switch (evt.event) {
                case 'token':
                  setState((s) => ({
                    ...s,
                    responseText: s.responseText + ((evt.data.text as string) ?? ''),
                  }));
                  break;
                case 'stage':
                  setState((s) => ({
                    ...s,
                    stages: [
                      ...s.stages,
                      {
                        stage: (evt.data.stage as string) ?? '',
                        status: (evt.data.status as string) ?? '',
                      },
                    ],
                  }));
                  break;
                case 'validated':
                  setState((s) => ({ ...s, validated: true }));
                  break;
                case 'retracted':
                  setState((s) => ({
                    ...s,
                    retracted: true,
                    retractionText: (evt.data.fallback_text as string) ?? null,
                  }));
                  break;
                case 'done':
                  // Stream complete, trace event may follow
                  break;
                case 'error':
                  setState((s) => ({
                    ...s,
                    error: (evt.data.message as string) ?? 'Pipeline error',
                  }));
                  break;
                case 'trace':
                  setState((s) => ({
                    ...s,
                    trace: (evt.data.trace as Record<string, unknown>) ?? evt.data,
                    conversationId:
                      (evt.data.conversation_id as string) ?? s.conversationId,
                  }));
                  break;
              }
            }
          }

          setState((s) => ({ ...s, streaming: false }));
        } catch (err: unknown) {
          if ((err as Error).name === 'AbortError') return;
          setState((s) => ({
            ...s,
            streaming: false,
            error: (err as Error).message ?? 'Stream failed',
          }));
        }
      })();
    },
    [apiFetch],
  );

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  return { state, send, reset };
}

/**
 * Fetch the full decision trace for a preview conversation.
 * Professional+ tier required.
 */
export function usePreviewTrace(apiFetch: ApiFetch, conversationId: string | null) {
  return useApi<PreviewTraceResponse>(
    apiFetch,
    conversationId ? `/api/admin/preview/${conversationId}/trace` : '',
    !!conversationId,
  );
}
