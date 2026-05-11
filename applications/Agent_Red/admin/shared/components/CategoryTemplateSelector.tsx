// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * CategoryTemplateSelector — picks and applies an industry template.
 *
 * KA-7: Knowledge Automation Admin UI.
 *
 * Displays available category templates as a grid of selectable cards.
 * On selection, shows preview details and "Apply to KB" button.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState } from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  Badge,
  Button,
  SimpleGrid,
  Alert,
  Loader,
  Center,
} from '@mantine/core';
import type { CategoryTemplate, TemplateApplyResult } from '../hooks/useIngestion';
import { tokens } from '../theme/styles';

const ACTION_BLUE = tokens.action;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface CategoryTemplateSelectorProps {
  templates: CategoryTemplate[] | null;
  loading?: boolean;
  error?: string | null;
  onApply: (categoryId: string) => Promise<TemplateApplyResult | null>;
  applyLoading?: boolean;
  applyError?: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CategoryTemplateSelector({
  templates,
  loading = false,
  error = null,
  onApply,
  applyLoading = false,
  applyError = null,
}: CategoryTemplateSelectorProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [applyResult, setApplyResult] = useState<TemplateApplyResult | null>(null);

  if (loading) {
    return (
      <Center py="lg">
        <Loader size="sm" />
        <Text size="sm" c="dimmed" ml="sm">Loading templates...</Text>
      </Center>
    );
  }

  if (error) {
    return (
      <Alert color="red" variant="light" title="Failed to load templates">
        {error}
      </Alert>
    );
  }

  if (!templates || templates.length === 0) {
    return (
      <Text size="sm" c="dimmed" ta="center" py="md">
        No category templates available.
      </Text>
    );
  }

  const selectedTemplate = templates.find((t) => t.id === selected);

  const handleApply = async () => {
    if (!selected) return;
    const result = await onApply(selected);
    if (result) {
      setApplyResult(result);
    }
  };

  return (
    <Stack gap="md">
      {/* Template grid */}
      <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="sm">
        {templates.map((template) => (
          <Paper
            key={template.id}
            p="sm"
            radius="md"
            withBorder
            style={{
              cursor: 'pointer',
              borderColor: selected === template.id ? ACTION_BLUE : undefined,
              borderWidth: selected === template.id ? 2 : 1,
            }}
            onClick={() => {
              setSelected(selected === template.id ? null : template.id);
              setApplyResult(null);
            }}
          >
            <Stack gap="xs">
              <Group justify="space-between" wrap="nowrap">
                <Text fw={600} size="sm" truncate="end">{template.name}</Text>
                <Badge size="xs" variant="light" color="gray">
                  {template.articleCount} articles
                </Badge>
              </Group>
              <Text size="xs" c="dimmed" lineClamp={2}>
                {template.description}
              </Text>
            </Stack>
          </Paper>
        ))}
      </SimpleGrid>

      {/* Selected template detail */}
      {selectedTemplate && (
        <Paper p="md" radius="md" withBorder>
          <Stack gap="sm">
            <Group justify="space-between">
              <div>
                <Text fw={600}>{selectedTemplate.name}</Text>
                <Text size="sm" c="dimmed">{selectedTemplate.description}</Text>
              </div>
              <Button
                color={ACTION_BLUE}
                onClick={handleApply}
                loading={applyLoading}
              >
                Apply to knowledge base
              </Button>
            </Group>

            <Group gap="sm">
              <Badge variant="light">{selectedTemplate.articleCount} starter articles</Badge>
              {selectedTemplate.suggestedBrandVoice && (
                <Badge variant="light" color="violet">
                  Voice: {selectedTemplate.suggestedBrandVoice}
                </Badge>
              )}
            </Group>

            {applyError && (
              <Alert color="red" variant="light" title="Apply failed">
                {applyError}
              </Alert>
            )}

            {applyResult && (
              <Alert color="green" variant="light" title="Template applied">
                Created {applyResult.articlesCreated} articles
                ({applyResult.totalChars > 1000
                  ? `${(applyResult.totalChars / 1000).toFixed(1)}k`
                  : applyResult.totalChars} characters).
                {applyResult.configSuggestions && Object.keys(applyResult.configSuggestions).length > 0 && (
                  <Text size="xs" mt="xs" c="dimmed">
                    Configuration suggestions generated — check the Configuration page.
                  </Text>
                )}
              </Alert>
            )}
          </Stack>
        </Paper>
      )}
    </Stack>
  );
}
