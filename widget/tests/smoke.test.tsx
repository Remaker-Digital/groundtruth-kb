/**
 * Smoke test — verify Vitest + Preact + @testing-library/preact work together.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h } from 'preact';
import { render, screen } from '@testing-library/preact';
import { describe, it, expect } from 'vitest';

function HelloWorld() {
  return <div>Hello from Preact</div>;
}

describe('Vitest smoke test', () => {
  it('renders a Preact component and finds text', () => {
    render(<HelloWorld />);
    expect(screen.getByText('Hello from Preact')).toBeTruthy();
  });

  it('happy-dom environment is active', () => {
    expect(typeof document).toBe('object');
    expect(typeof window).toBe('object');
  });
});
