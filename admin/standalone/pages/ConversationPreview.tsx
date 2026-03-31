// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Conversation Preview page — admin test-chat with decision trace (SPEC-1872).
 *
 * Displays:
 *   1. Chat input with send button
 *   2. Streaming response via POST-SSE (fetch + ReadableStream)
 *   3. Config overrides (tone preset, confidence threshold)
 *   4. Decision trace panel (collapsible JSON tree after response completes)
 *   5. Stage progress indicators during streaming
 *
 * Professional+ tier required. Admin role required via ProtectedRoute.
 * Daily limit of 50 previews/tenant enforced server-side (429 on exceed).
 */

import React, { useMemo, useState } from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  Title,
  TextInput,
  Button,
  Select,
  Slider,
  Badge,
  Loader,
  Alert,
  Code,
  Collapse,
  ActionIcon,
  ScrollArea,
  Tooltip,
  Box,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { usePreviewChat } from '../../shared/hooks/index';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TIER_ORDER: Record<string, number> = { free: 0, starter: 1, professional: 2, enterprise: 3 };
const PROFESSIONAL_TIER = 'professional';

const TONE_PRESETS = [
  { value: '', label: 'Default (tenant config)' },
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'casual', label: 'Casual' },
  { value: 'expert', label: 'Expert' },
];

// ---------------------------------------------------------------------------
// Chat message display
// ---------------------------------------------------------------------------

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  trace?: Record<string, unknown> | null;
  stages?: Array<{ stage: string; status: string }>;
  validated?: boolean;
  retracted?: boolean;
}

function ChatBubble({ msg }: { msg: ChatMessage }) {
  const [traceOpen, setTraceOpen] = useState(false);
  const isUser = msg.role === 'user';

  return (
    <Box mb="md">
      <Group gap="xs" mb={4}>
        <Badge
          variant="light"
          color={isUser ? 'blue' : 'gray'}
          size="xs"
        >
          {isUser ? 'You' : 'Agent Red'}
        </Badge>
        {msg.validated && (
          <Badge variant="light" color="green" size="xs">Validated</Badge>
        )}
        {msg.retracted && (
          <Badge variant="light" color="red" size="xs">Retracted</Badge>
        )}
      </Group>
      <Paper
        p="sm"
        radius="md"
        withBorder
        style={{
          backgroundColor: isUser ? 'var(--mantine-color-blue-light)' : undefined,
          maxWidth: '85%',
          marginLeft: isUser ? 'auto' : undefined,
        }}
      >
        <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
          {msg.content}
        </Text>
      </Paper>

      {/* Stage progress */}
      {msg.stages && msg.stages.length > 0 && (
        <Group gap={4} mt={4} ml="sm">
          {msg.stages.map((s, i) => (
            <Badge key={i} variant="dot" color="gray" size="xs">
              {s.stage}: {s.status}
            </Badge>
          ))}
        </Group>
      )}

      {/* Trace panel */}
      {msg.trace && (
        <Box mt="xs">
          <ActionIcon
            variant="subtle"
            size="xs"
            onClick={() => setTraceOpen(!traceOpen)}
          >
            <Text size="xs">{traceOpen ? '▲ Hide trace' : '▼ Show trace'}</Text>
          </ActionIcon>
          <Collapse in={traceOpen}>
            <Paper p="sm" mt="xs" bg="var(--mantine-color-dark-8)" radius="md">
              <Text size="xs" fw={600} mb="xs">Decision Trace</Text>
              <ScrollArea h={300}>
                <Code block style={{ fontSize: '11px' }}>
                  {JSON.stringify(msg.trace, null, 2)}
                </Code>
              </ScrollArea>
            </Paper>
          </Collapse>
        </Box>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// ConversationPreviewPage
// ---------------------------------------------------------------------------

export const ConversationPreviewPage: React.FC = () => {
  const { apiFetch, tenantContext } = useAppContext();
  const [input, setInput] = useState('');
  const [tonePreset, setTonePreset] = useState('');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.6);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [showOverrides, setShowOverrides] = useState(false);

  const { state, send, reset } = usePreviewChat(apiFetch);

  // Tier gate BEFORE any API interaction
  const tier = tenantContext?.tier ?? 'free';
  const hasTier = TIER_ORDER[tier] >= TIER_ORDER[PROFESSIONAL_TIER];

  if (!hasTier) {
    return (
      <Stack gap="lg">
        <Title order={2}>Conversation Preview</Title>
        <Alert color="yellow" title="Professional tier required">
          Conversation Preview requires a Professional or Enterprise subscription.
          Upgrade your plan to test your AI configuration.
        </Alert>
      </Stack>
    );
  }

  const handleSend = () => {
    const message = input.trim();
    if (!message || state.streaming) return;

    // Add user message to history
    setHistory((h) => [...h, { role: 'user', content: message }]);
    setInput('');

    // Build config overrides
    const overrides: Record<string, unknown> = {};
    if (tonePreset) overrides.response_tone_preset = tonePreset;
    if (confidenceThreshold !== 0.6) overrides.intent_confidence_threshold = confidenceThreshold;

    send(message, Object.keys(overrides).length > 0 ? overrides : undefined);
  };

  // When streaming completes, capture the response into history
  const lastResponseCapturedRef = React.useRef(false);
  React.useEffect(() => {
    if (!state.streaming && state.responseText && !lastResponseCapturedRef.current) {
      lastResponseCapturedRef.current = true;
      const content = state.retracted && state.retractionText
        ? state.retractionText
        : state.responseText;
      setHistory((h) => [
        ...h,
        {
          role: 'assistant',
          content,
          trace: state.trace,
          stages: state.stages,
          validated: state.validated,
          retracted: state.retracted,
        },
      ]);
    }
    if (state.streaming) {
      lastResponseCapturedRef.current = false;
    }
  }, [state.streaming, state.responseText, state.retracted, state.retractionText, state.trace, state.stages, state.validated]);

  const handleReset = () => {
    reset();
    setHistory([]);
  };

  return (
    <Stack gap="lg">
      {/* Page header */}
      <Group justify="space-between" align="flex-end">
        <div>
          <Title order={2}>Conversation Preview</Title>
          <Text c="dimmed" size="sm">
            Test your AI configuration with a preview conversation
          </Text>
        </div>
        <Group gap="sm">
          <Tooltip label="Configure response overrides">
            <Button
              variant="subtle"
              size="xs"
              onClick={() => setShowOverrides(!showOverrides)}
            >
              {showOverrides ? 'Hide overrides' : 'Config overrides'}
            </Button>
          </Tooltip>
          <Button variant="subtle" size="xs" color="red" onClick={handleReset}>
            Clear
          </Button>
        </Group>
      </Group>

      {/* Config overrides panel */}
      <Collapse in={showOverrides}>
        <Paper p="md" radius="md" withBorder>
          <Text fw={600} size="sm" mb="sm">Response Overrides (temporary, not persisted)</Text>
          <Group align="flex-end" gap="lg">
            <Select
              label="Tone preset"
              data={TONE_PRESETS}
              value={tonePreset}
              onChange={(v) => setTonePreset(v ?? '')}
              size="sm"
              style={{ minWidth: 200 }}
              clearable
            />
            <Box style={{ flex: 1, minWidth: 200 }}>
              <Text size="sm" mb={4}>Confidence threshold: {confidenceThreshold.toFixed(2)}</Text>
              <Slider
                value={confidenceThreshold}
                onChange={setConfidenceThreshold}
                min={0}
                max={1}
                step={0.05}
                marks={[
                  { value: 0.3, label: '0.3' },
                  { value: 0.6, label: '0.6' },
                  { value: 0.9, label: '0.9' },
                ]}
                size="sm"
              />
            </Box>
          </Group>
        </Paper>
      </Collapse>

      {/* Chat area */}
      <Paper p="lg" radius="md" withBorder style={{ minHeight: 400 }}>
        <ScrollArea h={350} offsetScrollbars>
          {history.length === 0 && !state.streaming && (
            <Text c="dimmed" size="sm" ta="center" py="xl">
              Send a message to preview your AI agent's response.
              Preview conversations are excluded from analytics and billing.
            </Text>
          )}

          {history.map((msg, idx) => (
            <ChatBubble key={idx} msg={msg} />
          ))}

          {/* Live streaming response */}
          {state.streaming && (
            <Box mb="md">
              <Group gap="xs" mb={4}>
                <Badge variant="light" color="gray" size="xs">Agent Red</Badge>
                <Loader size={12} />
              </Group>
              {state.stages.length > 0 && (
                <Group gap={4} mb={4}>
                  {state.stages.map((s, i) => (
                    <Badge key={i} variant="dot" color="gray" size="xs">
                      {s.stage}: {s.status}
                    </Badge>
                  ))}
                </Group>
              )}
              {state.responseText && (
                <Paper p="sm" radius="md" withBorder style={{ maxWidth: '85%' }}>
                  <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                    {state.responseText}
                  </Text>
                </Paper>
              )}
            </Box>
          )}

          {/* Error */}
          {state.error && (
            <Alert color="red" title="Preview error" mb="md">
              {state.error}
            </Alert>
          )}
        </ScrollArea>
      </Paper>

      {/* Input area */}
      <Group gap="sm">
        <TextInput
          placeholder="Type a customer message to preview..."
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={state.streaming}
          style={{ flex: 1 }}
          size="md"
        />
        <Button
          onClick={handleSend}
          loading={state.streaming}
          disabled={!input.trim() || state.streaming}
          size="md"
          color={tokens.brand}
        >
          Send
        </Button>
      </Group>
    </Stack>
  );
};
