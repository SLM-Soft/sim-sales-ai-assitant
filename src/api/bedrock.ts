import axios from 'axios';
import { config } from '../config';

export interface ChatMessage {
  role: 'User' | 'Assistant';
  content: string;
}

interface BedrockResponse {
  success: boolean;
  output: string;
}

export const sendMessage = async (
  messages: ChatMessage[]
): Promise<{ outputText: string; tokensUsed: number }> => {
  const resp = await axios.post<BedrockResponse>(`${config.apiBaseUrl}/bedrock`, { messages });
  if (!resp.data) throw new Error('No response from server');
  if (!resp.data.success)
    throw new Error(resp.data.output || 'Error from backend');

  const data = JSON.parse(resp.data.output);
  console.log(data);
  const outputText = data.results?.[0]?.outputText;
  const tokensUsed = data.results?.[0]?.tokenCount;

  return { outputText, tokensUsed };
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const resp = await axios.get(`${config.apiBaseUrl}/health`);
    return resp.status === 200 && resp.data?.ok === true;
  } catch {
    return false;
  }
};
