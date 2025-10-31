import type { BedrockRequest } from './bedrock';

// === Individual presets ===

// Balanced / default mode
const defaultPreset: Omit<BedrockRequest, 'messages'> = {
  maxTokens: 1024,
  temperature: 0.7,
  topP: 0.9,
  stopSequences: ['\nUser:'],
  systemPrompt: 'You are a helpful assistant. Respond clearly and concisely.',
};

// Creative mode — for brainstorming, writing, storytelling
const creativePreset: Omit<BedrockRequest, 'messages'> = {
  maxTokens: 1500,
  temperature: 1.0,
  topP: 0.95,
  systemPrompt:
    'You are a playful, imaginative storyteller. Use vivid metaphors, surprising comparisons, and a warm tone. Favor colorful language and playful phrasing.',
};

// Precise mode — for technical or factual tasks
const precisePreset: Omit<BedrockRequest, 'messages'> = {
  maxTokens: 800,
  temperature: 0.2,
  topP: 0.8,
  systemPrompt:
    'You are a technical assistant. Provide accurate, structured, and factual answers.',
};

// Short / concise replies
const shortPreset: Omit<BedrockRequest, 'messages'> = {
  maxTokens: 200,
  temperature: 0.5,
  topP: 0.9,
  systemPrompt:
    'Respond briefly and to the point, in one or two sentences maximum.',
};

// Claude-style — thoughtful and natural reasoning
const claudeStylePreset: Omit<BedrockRequest, 'messages'> = {
  maxTokens: 900,
  temperature: 0.6,
  topP: 0.9,
  systemPrompt:
    'You are a thoughtful, compassionate explainer. Use simple analogies, one clear example, and end with a single-sentence takeaway. Keep it friendly but concise.',
};

// === Export unified presets object ===
export const bedrockPresets = {
  default: defaultPreset,
  creative: creativePreset,
  precise: precisePreset,
  short: shortPreset,
  claude: claudeStylePreset,
} as const;

export type BedrockPresetName = keyof typeof bedrockPresets;
