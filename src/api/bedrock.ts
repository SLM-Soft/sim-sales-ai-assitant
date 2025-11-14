import axios from 'axios';
import { config } from '../config';

export type Role = 'User' | 'Assistant';

export interface ChatMessage {
  role: Role;
  content: string;
}

// ---------- Chat Completion ----------
export async function sendChat(params: {
  userQuestion: string;
  optionKey: string; // sales | project_analysis | general_llm
  sessionId?: string;
}): Promise<{ outputText: string }> {
  const resp = await axios.post(`${config.apiBaseUrl}/chat`, params);

  if (!resp.data || !resp.data.outputText) {
    throw new Error("No output from backend");
  }

  return {
    outputText: resp.data.outputText,
  };
}

// ---------- Health ----------
export const checkHealth = async (): Promise<boolean> => {
  try {
    const resp = await axios.get(`${config.apiBaseUrl}/health`);
    return resp.status === 200 && resp.data?.ok === true;
  } catch {
    return false;
  }
};
