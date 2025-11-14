import { create } from 'zustand';

export type Role = 'User' | 'Assistant';
export type Level = 'brief' | 'detailed';

export interface ChatMessage {
  role: Role;
  content: string;
}

interface ChatState {
  // messages
  messages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  startAssistantStream: () => number;
  appendToMessage: (index: number, chunk: string) => void;
  clearMessages: () => void;

  // select first menu option
  firstOption: number | null;
  setFirstOption: (v: number | null) => void;

  // input field
  input: string;
  setInput: (v: string) => void;

  // statuses
  loading: boolean;
  setLoading: (v: boolean) => void;
  backendOk: boolean | null;
  setBackendOk: (v: boolean | null) => void;

  // generative settings
  showSettings: boolean;
  setShowSettings: (v: boolean) => void;

  temperature: number; // 0..1 (step 0.1)
  setTemperature: (v: number) => void;

  maxTokens: number; // 64..8192 (step 64)
  setMaxTokens: (v: number) => void;

  level: Level; // 'brief' | 'detailed'
  setLevel: (v: Level) => void;

  includeBenchmarks: boolean;
  setIncludeBenchmarks: (v: boolean) => void;

  // useful reset
  resetChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  // messages
  messages: [],
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),

  startAssistantStream: () => {
    let index = -1;
    set((s) => {
      index = s.messages.length;
      return { messages: [...s.messages, { role: 'Assistant', content: '' }] };
    });
    return index;
  },

  appendToMessage: (index, chunk) =>
    set((s) => {
      const arr = s.messages.slice();
      if (!arr[index]) return { messages: s.messages };
      arr[index] = {
        ...arr[index],
        content: (arr[index].content || '') + chunk,
      };
      return { messages: arr };
    }),

  clearMessages: () => set({ messages: [] }),

  // select and input
  firstOption: null,
  setFirstOption: (v) => set({ firstOption: v }),

  input: '',
  setInput: (v) => set({ input: v }),

  // statuses
  loading: false,
  setLoading: (v) => set({ loading: v }),
  backendOk: null,
  setBackendOk: (v) => set({ backendOk: v }),

  // generative settings
  showSettings: false,
  setShowSettings: (v) => set({ showSettings: v }),

  temperature: 0.7,
  setTemperature: (v) => set({ temperature: v }),

  maxTokens: 1024,
  setMaxTokens: (v) => set({ maxTokens: v }),

  level: 'brief',
  setLevel: (v) => set({ level: v }),

  includeBenchmarks: true,
  setIncludeBenchmarks: (v) => set({ includeBenchmarks: v }),

  resetChat: () =>
    set({
      messages: [],
      firstOption: null,
      input: '',
      loading: false,
      showSettings: false,
      temperature: 0.7,
      maxTokens: 1024,
      level: 'brief',
      includeBenchmarks: true,
    }),
}));
