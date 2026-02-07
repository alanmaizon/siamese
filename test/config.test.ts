import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const loadConfigModule = async () => {
  vi.resetModules();
  return import('../config');
};

const runtimeEnv = import.meta.env as Record<string, string | undefined>;
const originalGeminiKey = runtimeEnv.VITE_GEMINI_API_KEY;
const originalApiKey = runtimeEnv.VITE_API_KEY;

describe('getGeminiApiKey', () => {
  beforeEach(() => {
    window.__SIAMESE_CONFIG__ = undefined;
    runtimeEnv.VITE_GEMINI_API_KEY = '   ';
    runtimeEnv.VITE_API_KEY = '   ';
  });

  afterEach(() => {
    window.__SIAMESE_CONFIG__ = undefined;
    runtimeEnv.VITE_GEMINI_API_KEY = originalGeminiKey;
    runtimeEnv.VITE_API_KEY = originalApiKey;
  });

  it('prefers runtime config key when present', async () => {
    window.__SIAMESE_CONFIG__ = { geminiApiKey: '  runtime-key  ' };
    runtimeEnv.VITE_GEMINI_API_KEY = 'env-key';

    const { getGeminiApiKey } = await loadConfigModule();

    expect(getGeminiApiKey()).toBe('runtime-key');
  });

  it('falls back to VITE_GEMINI_API_KEY when runtime key is not set', async () => {
    runtimeEnv.VITE_GEMINI_API_KEY = '  env-key  ';

    const { getGeminiApiKey } = await loadConfigModule();

    expect(getGeminiApiKey()).toBe('env-key');
  });

  it('falls back to VITE_API_KEY when VITE_GEMINI_API_KEY is absent', async () => {
    runtimeEnv.VITE_GEMINI_API_KEY = '   ';
    runtimeEnv.VITE_API_KEY = 'legacy-env-key';

    const { getGeminiApiKey } = await loadConfigModule();

    expect(getGeminiApiKey()).toBe('legacy-env-key');
  });

  it('returns empty string when no configured keys are available', async () => {
    const { getGeminiApiKey } = await loadConfigModule();

    expect(getGeminiApiKey()).toBe('');
  });
});
