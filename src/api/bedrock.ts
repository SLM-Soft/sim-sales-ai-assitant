import axios from 'axios';
import { config } from '../config';

export type Role = 'User' | 'Assistant';

export interface ChatMessage {
  role: Role;
  content: string;
}

export interface BedrockRequest {
  modelId?: string;
  systemPrompt?: string;
  messages?: ChatMessage[];

  // universal options
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  stopSequences?: string[];
}

interface BedrockResponse {
  success: boolean;
  output: string;
}

export interface AgentRequest {
  inputText: string;
  sessionId?: string;
}

export async function sendMessage(
  messages: ChatMessage[],
  options?: Omit<BedrockRequest, 'messages'>
): Promise<{ outputText: string; tokensUsed: number }> {
  const body: BedrockRequest = { messages, ...options };

  const resp = await axios.post<BedrockResponse>('/api/bedrock', body);

  if (!resp.data) throw new Error('No response from server');
  if (!resp.data.success) throw new Error(resp.data.output || 'Error from backend');

  // Тело модели может возвращать JSON, поэтому пробуем его распарсить
  let outputText = resp.data.output;
  let tokensUsed = 0;

  try {
    const data = JSON.parse(resp.data.output);
    outputText = data.results?.[0]?.outputText ?? resp.data.output;
    tokensUsed = data.results?.[0]?.tokenCount ?? 0;
  } catch {
    // если не JSON — оставляем как есть
  }

  return { outputText, tokensUsed };
}

export async function sendAgentMessage(
  inputText: string,
  sessionId: string = 'default-session'
): Promise<{ outputText: string }> {
  const body: AgentRequest = { inputText, sessionId };

  const resp = await axios.post<BedrockResponse>(`${config.apiBaseUrl}/agent`, body);

  if (!resp.data) throw new Error('No response from server');
  if (!resp.data.success) throw new Error(resp.data.output || 'Error from backend');

  return { outputText: resp.data.output };
}

export async function sendAgentDispatch(params: {
  userQuestion: string;
  optionKey: string;
  sessionId?: string;
  clientContext?: any;
  level?: 'brief' | 'detailed';
  includeBenchmarks?: boolean;
}): Promise<{ outputText: string }> {
  const resp = await axios.post(`${config.apiBaseUrl}/agent/dispatch`, params);
  if (!resp.data || !resp.data.success) {
    throw new Error(resp.data?.output || 'Agent dispatch error');
  }
  return { outputText: resp.data.output };
}


export const checkHealth = async (): Promise<boolean> => {
  try {
    const resp = await axios.get(`${config.apiBaseUrl}/health`);
    return resp.status === 200 && resp.data?.ok === true;
  } catch {
    return false;
  }
};
