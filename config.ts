const ENV_KEYS = ['VITE_GEMINI_API_KEY', 'VITE_API_KEY'] as const;

const runtimeConfig = window.__SIAMESE_CONFIG__ || {};

export const getGeminiApiKey = (): string => {
  if (typeof runtimeConfig.geminiApiKey === 'string' && runtimeConfig.geminiApiKey.trim()) {
    return runtimeConfig.geminiApiKey.trim();
  }

  for (const key of ENV_KEYS) {
    const value = import.meta.env[key];
    if (typeof value === 'string' && value.trim()) {
      return value.trim();
    }
  }
  return '';
};
