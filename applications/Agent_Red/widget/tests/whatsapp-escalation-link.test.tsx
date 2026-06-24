/**
 * SPEC-1880: WhatsApp escalation markdown links render as clickable widget anchors.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h } from 'preact';
import { cleanup, render, screen } from '@testing-library/preact';
import { afterEach, describe, expect, it } from 'vitest';
import { MessageBubble } from '../src/components/MessageBubble';
import { en } from '../src/locale/en';
import type { Message } from '../src/state/store';
import { resolveTokens, type WidgetConfig } from '../src/theme/tokens';

const config = { widget_header_text: 'Agent Red Test' } as WidgetConfig;
const tokens = resolveTokens(config);

afterEach(() => {
  cleanup();
});

describe('SPEC-1880 WhatsApp escalation link rendering', () => {
  it('renders the escalation markdown link as a clickable anchor', () => {
    const href = 'https://wa.me/15551234567?text=Hi%2C%20I%20need%20help';
    const message: Message = {
      id: 'msg-whatsapp-escalation',
      role: 'agent',
      content: `You can also continue this conversation on WhatsApp: [Open WhatsApp](${href})`,
      timestamp: Date.now(),
    };

    render(
      <MessageBubble
        tokens={tokens}
        locale={en}
        message={message}
        agentAvatarUrl={null}
        agentName="AI Assistant"
        showAvatar={false}
      />,
    );

    const whatsappLink = screen.getByRole('link', { name: /Open WhatsApp/i });
    expect(whatsappLink.getAttribute('href')).toBe(href);
    expect(whatsappLink.getAttribute('target')).toBe('_top');
    expect(screen.getByText(/continue this conversation on WhatsApp/i)).toBeTruthy();
  });
});
