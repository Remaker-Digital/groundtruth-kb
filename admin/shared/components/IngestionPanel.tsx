/**
 * IngestionPanel — displays ingestion job progress and status.
 *
 * KA-7: Knowledge Automation Admin UI.
 *
 * Shows the current/latest ingestion job status with progress bar,
 * article count, and cancel button for running jobs.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  Badge,
  Progress,
  Button,
  SimpleGrid,
  Alert,
  Loader,
} from '@mantine/core';
import type { IngestionJob } from '../hooks/useIngestion';
import { tokens } from '../theme/styles';

const ACTION_BLUE = tokens.action;

// ---------------------------------------------------------------------------
// Status helpers
// ---------------------------------------------------------------------------

const statusColorMap: Record<string, string> = {
  pending: 'yellow',
  running: 'blue',
  completed: 'green',
  failed: 'red',
  cancelled: 'gray',
};

const statusLabelMap: Record<string, string> = {
  pending: 'Pending',
  running: 'In Progress',
  completed: 'Completed',
  failed: 'Failed',
  cancelled: 'Cancelled',
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface IngestionPanelProps {
  job: IngestionJob | null;
  loading?: boolean;
  onCancel?: () => void;
  cancelLoading?: boolean;
  onRefresh?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function IngestionPanel({
  job,
  loading = false,
  onCancel,
  cancelLoading = false,
  onRefresh,
}: IngestionPanelProps) {
  if (loading) {
    return (
      <Paper p="md" radius="md" withBorder>
        <Group justify="center" py="md">
          <Loader size="sm" />
          <Text size="sm" c="dimmed">Loading ingestion status...</Text>
        </Group>
      </Paper>
    );
  }

  if (!job) {
    return (
      <Paper p="md" radius="md" withBorder>
        <Stack gap="sm" align="center" py="md">
          <Text size="sm" c="dimmed">
            No ingestion job found. Start one by importing from your storefront
            or selecting a category template below.
          </Text>
        </Stack>
      </Paper>
    );
  }

  const isActive = job.status === 'pending' || job.status === 'running';

  return (
    <Paper p="md" radius="md" withBorder>
      <Stack gap="md">
        {/* Header row */}
        <Group justify="space-between">
          <Group gap="sm">
            <Text fw={600} size="sm">Ingestion Job</Text>
            <Badge
              size="sm"
              color={statusColorMap[job.status] || 'gray'}
              variant="filled"
            >
              {statusLabelMap[job.status] || job.status}
            </Badge>
            <Badge size="xs" variant="light" color="gray">
              {job.jobType === 'category_template' ? 'Template' : job.jobType.toUpperCase()}
            </Badge>
          </Group>
          <Group gap="xs">
            {isActive && onCancel && (
              <Button
                size="xs"
                variant="default"
                color="red"
                onClick={onCancel}
                loading={cancelLoading}
              >
                Cancel
              </Button>
            )}
            {onRefresh && (
              <Button size="xs" variant="default" onClick={onRefresh}>
                Refresh
              </Button>
            )}
          </Group>
        </Group>

        {/* Progress bar for active jobs */}
        {isActive && (
          <Progress
            value={job.progressPercent}
            size="lg"
            radius="md"
            color={ACTION_BLUE}
            animated={job.status === 'running'}
          />
        )}

        {/* Stats grid */}
        <SimpleGrid cols={4} spacing="sm">
          <Paper p="xs" radius="sm" withBorder>
            <Text size="xs" c="dimmed">Articles created</Text>
            <Text fw={700} size="lg">{job.articlesCreated}</Text>
          </Paper>
          <Paper p="xs" radius="sm" withBorder>
            <Text size="xs" c="dimmed">Articles failed</Text>
            <Text fw={700} size="lg" c={job.articlesFailed > 0 ? 'red' : undefined}>
              {job.articlesFailed}
            </Text>
          </Paper>
          <Paper p="xs" radius="sm" withBorder>
            <Text size="xs" c="dimmed">Total characters</Text>
            <Text fw={700} size="lg">
              {job.totalChars > 1000 ? `${(job.totalChars / 1000).toFixed(1)}k` : job.totalChars}
            </Text>
          </Paper>
          <Paper p="xs" radius="sm" withBorder>
            <Text size="xs" c="dimmed">Pages crawled</Text>
            <Text fw={700} size="lg">{job.pagesCrawled}</Text>
          </Paper>
        </SimpleGrid>

        {/* Error message */}
        {job.errorMessage && (
          <Alert color="red" variant="light" title="Error">
            {job.errorMessage}
          </Alert>
        )}

        {/* Completion message */}
        {job.status === 'completed' && (
          <Alert color="green" variant="light" title="Import complete">
            Successfully imported {job.articlesCreated} articles into your knowledge base.
          </Alert>
        )}
      </Stack>
    </Paper>
  );
}
