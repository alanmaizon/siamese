import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import type { IncidentReport } from '../types';

const analyzeIncidentMock = vi.fn();

vi.mock('../services/geminiService', () => ({
  analyzeIncident: (...args: unknown[]) => analyzeIncidentMock(...args),
}));

vi.mock('../config', () => ({
  getGeminiApiKey: () => 'test-api-key',
}));

describe('App', () => {
  beforeEach(() => {
    analyzeIncidentMock.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it('shows a validation error when analysis starts without uploaded files', async () => {
    const user = userEvent.setup();

    render(<App />);

    await user.click(screen.getByRole('button', { name: /enter workspace/i }));
    await user.click(screen.getByRole('button', { name: /start analysis/i }));

    expect(screen.getByText('Analysis Failed')).toBeTruthy();
    expect(screen.getByText(/please upload at least one file/i)).toBeTruthy();
    expect(analyzeIncidentMock).not.toHaveBeenCalled();
  });

  it('runs analysis and renders parsed summary', async () => {
    const user = userEvent.setup();
    const json: IncidentReport = {
      summary: 'Database lock contention caused elevated latency.',
      timeline: ['14:00 alert fired'],
      root_causes: ['Database lock contention'],
      evidence: ['connection pool wait exceeded threshold'],
      mitigations: ['restarted the stuck worker'],
      follow_ups: ['add lock wait monitoring'],
      confidence: 0.91,
    };

    analyzeIncidentMock.mockResolvedValueOnce({
      text: JSON.stringify(json),
      json,
    });

    const { container } = render(<App />);

    await user.click(screen.getByRole('button', { name: /enter workspace/i }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement | null;
    expect(fileInput).toBeTruthy();

    await user.upload(
      fileInput as HTMLInputElement,
      new File(['2026-02-07T14:00:00Z ERROR lock wait timeout'], 'incident.log', { type: 'text/plain' }),
    );
    await screen.findByText('incident.log');

    await user.click(screen.getByRole('button', { name: /start analysis/i }));

    await waitFor(() => {
      expect(analyzeIncidentMock).toHaveBeenCalledTimes(1);
    });

    const [apiKey, modelName, question, files] = analyzeIncidentMock.mock.calls[0];
    expect(apiKey).toBe('test-api-key');
    expect(modelName).toBe('gemini-3-flash-preview');
    expect(String(question)).toContain('Analyze these logs');
    expect(Array.isArray(files)).toBe(true);
    expect(files[0]).toMatchObject({ name: 'incident.log' });

    const summaryText = await screen.findByText((content, element) => {
      return (
        element?.tagName.toLowerCase() === 'p' &&
        content.includes('Database lock contention caused elevated latency.')
      );
    });
    expect(summaryText).toBeTruthy();
  });

  it('shows API errors returned by the analysis service', async () => {
    const user = userEvent.setup();

    analyzeIncidentMock.mockRejectedValueOnce(new Error('Gemini request failed'));

    const { container } = render(<App />);

    await user.click(screen.getByRole('button', { name: /enter workspace/i }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement | null;
    expect(fileInput).toBeTruthy();

    await user.upload(
      fileInput as HTMLInputElement,
      new File(['log line'], 'incident.log', { type: 'text/plain' }),
    );
    await screen.findByText('incident.log');

    await user.click(screen.getByRole('button', { name: /start analysis/i }));

    expect(await screen.findByText('Analysis Failed')).toBeTruthy();
    expect(await screen.findByText(/gemini request failed/i)).toBeTruthy();
  });
});
