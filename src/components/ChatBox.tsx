import React, { useEffect, useRef } from 'react';
import ChatHeader from './ChatHeader';
import MessagesList from './MessagesList';
import FirstOptionsGrid from './FirstOptionsGrid';
import InputRow from './InputRow';
import GenerationSettings from './GenerationSettings';
import { checkHealth, sendChat } from '../api/bedrock';
import { firstOptions } from '../mock';
import { useChatStore } from '../store/chatStore';

const ChatBox: React.FC = () => {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const genSessionId = () =>
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `s_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

  const sessionIdRef = useRef<string>(genSessionId());

  const {
    messages,
    addMessage,
    clearMessages,
    startAssistantStream,
    appendToMessage,

    firstOption,
    setFirstOption,
    input,
    setInput,

    loading,
    setLoading,
    backendOk,
    setBackendOk,

    showSettings,
    setShowSettings,
  } = useChatStore();

  // автоскролл к последнему сообщению — теперь скроллится вся страница
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages.length]);

  // health-check бэкенда
  useEffect(() => {
    (async () => {
      const ok = await checkHealth();
      setBackendOk(ok);
    })();
  }, [setBackendOk]);

  const handleFirstSelect = (opt: number) => setFirstOption(opt);

  const handleSend = async () => {
    if (firstOption === null || !input.trim() || loading) return;

    const userMessage = input.trim();

    addMessage({ role: 'User', content: userMessage });
    setInput('');
    setLoading(true);

    try {
      const optionKey = firstOptions[firstOption].key || 'default';

      const assistantIndex = startAssistantStream();

      const resp = await sendChat({
        userQuestion: userMessage,
        optionKey,
        sessionId: sessionIdRef.current,
      });

      appendToMessage(assistantIndex, resp.outputText);
    } catch (err) {
      console.error(err);
      appendToMessage(messages.length - 1, 'Error: failed to get response');
    } finally {
      setLoading(false);
    }
  };

  const showChat = firstOption !== null;

  return (
    <div className="w-full max-w-[1350px] flex flex-col text-white">
      {/* Хедер сверху, как у ChatGPT */}
      <ChatHeader
        backendOk={backendOk}
        selected={firstOption}
        onBack={() => {
          setFirstOption(null);
          clearMessages();
        }}
      />

      {/* Контентная часть: просто растёт, без собственного скролла */}
      <div className="w-full flex-1">
        {showChat ? (
          <MessagesList messages={messages} scrollRef={scrollRef} />
        ) : (
          <FirstOptionsGrid onSelect={handleFirstSelect} />
        )}
      </div>

      {/* Sticky «футер» как у chatgpt.com */}
      {showChat && (
        <div className="sticky bottom-0 bg-neutral-800 !pb-4">
          <GenerationSettings />
          <InputRow
            input={input}
            setInput={setInput}
            onSend={handleSend}
            loading={loading}
            showSettings={showSettings}
            setShowSettings={setShowSettings}
          />
        </div>
      )}
    </div>
  );
};

export default ChatBox;
