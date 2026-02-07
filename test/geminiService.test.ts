import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { FileArtifact } from '../types';
import { SYSTEM_INSTRUCTION } from '../constants';

const { generateContentMock, GoogleGenAIMock } = vi.hoisted(() => {
  const generateContentMock = vi.fn();
  const GoogleGenAIMock = vi.fn(() => ({
    models: {
      generateContent: generateContentMock,
    },
  }));

  return { generateContentMock, GoogleGenAIMock };
});

vi.mock('@google/genai', async () => {
  const actual = await vi.importActual<typeof import('@google/genai')>('@google/genai');
  return {
    ...actual,
    GoogleGenAI: GoogleGenAIMock,
  };
});

import { analyzeIncident } from '../services/geminiService';

describe('analyzeIncident', () => {
  beforeEach(() => {
    generateContentMock.mockReset();
    GoogleGenAIMock.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('throws when API key is missing', async () => {
    await expect(analyzeIncident('', 'gemini-3-flash-preview', 'What happened?', [])).rejects.toThrow(
      'API Key is missing. Please check your environment configuration.',
    );

    expect(GoogleGenAIMock).not.toHaveBeenCalled();
  });

  it('sends prompt context and returns parsed JSON', async () => {
    const files: FileArtifact[] = [
      {
        name: 'incident.log',
        content: '2026-02-07T14:00:00Z ERROR lock wait timeout',
        size: 45,
      },
    ];
    const responseJson = {
      summary: 'Database lock contention caused elevated latency.',
      timeline: ['14:00 alert fired'],
      root_causes: ['Database lock contention'],
      evidence: ['connection pool wait exceeded threshold'],
      mitigations: ['restarted worker'],
      follow_ups: ['add lock wait monitoring'],
      confidence: 0.9,
    };

    generateContentMock.mockResolvedValueOnce({
      text: JSON.stringify(responseJson),
    });

    const result = await analyzeIncident('unit-test-key', 'gemini-3-flash-preview', 'What happened?', files);

    expect(GoogleGenAIMock).toHaveBeenCalledWith({ apiKey: 'unit-test-key' });
    expect(generateContentMock).toHaveBeenCalledTimes(1);

    const request = generateContentMock.mock.calls[0][0];
    expect(request.model).toBe('gemini-3-flash-preview');
    expect(request.contents).toContain('# file: incident.log');
    expect(request.contents).toContain('lock wait timeout');
    expect(request.contents).toContain('User Question:');
    expect(request.contents).toContain('What happened?');
    expect(request.config.systemInstruction).toBe(SYSTEM_INSTRUCTION);
    expect(request.config.responseMimeType).toBe('application/json');
    expect(request.config.responseSchema.required).toEqual(
      expect.arrayContaining([
        'summary',
        'timeline',
        'root_causes',
        'evidence',
        'mitigations',
        'follow_ups',
        'confidence',
      ]),
    );

    expect(result.text).toContain('Database lock contention');
    expect(result.json).toMatchObject(responseJson);
  });

  it('returns raw text and undefined json when response is not valid JSON', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    generateContentMock.mockResolvedValueOnce({ text: 'not-json' });

    const result = await analyzeIncident('unit-test-key', 'gemini-3-flash-preview', 'What happened?', []);

    expect(result.text).toBe('not-json');
    expect(result.json).toBeUndefined();
    expect(warnSpy).toHaveBeenCalledWith('Failed to parse JSON response', expect.any(SyntaxError));
  });

  it('rewraps SDK errors with a user-facing message', async () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    generateContentMock.mockRejectedValueOnce(new Error('Gemini request failed'));

    await expect(analyzeIncident('unit-test-key', 'gemini-3-flash-preview', 'What happened?', [])).rejects.toThrow(
      'Gemini request failed',
    );
    expect(errorSpy).toHaveBeenCalledWith('Gemini API Error:', expect.any(Error));
  });
});
