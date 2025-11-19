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

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages.length]);

  useEffect(() => {
    (async () => {
      const ok = await checkHealth();
      setBackendOk(ok);
    })();
  }, [setBackendOk]);

  const handleFirstSelect = (opt: number) => setFirstOption(opt);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();

    addMessage({ role: 'User', content: userMessage });
    setInput('');
    setLoading(true);

    try {
      const optionKey =
        firstOption !== null && firstOptions[firstOption]
          ? firstOptions[firstOption].key
          : 'general_llm';

      const resp = await sendChat({
        userQuestion: userMessage,
        optionKey,
        sessionId: sessionIdRef.current,
      });

      addMessage({ role: 'Assistant', content: resp.outputText });
    } catch (err) {
      console.error(err);
      addMessage({ role: 'Assistant', content: 'Error: failed to get response' });
    } finally {
      setLoading(false);
    }
  };

  const hasMessages = messages.length > 0;
  const showChat = firstOption !== null || hasMessages;

  return (
    <div className="w-full max-w-[1350px] flex flex-col" style={{ color: 'var(--color-text)' }}>
      <ChatHeader
        backendOk={backendOk}
        selected={firstOption}
        onBack={() => {
          setFirstOption(null);
          clearMessages();
        }}
      />

      <div className="w-full flex-1">
        {showChat ? (
          <MessagesList messages={messages} scrollRef={scrollRef} />
        ) : (
          <FirstOptionsGrid onSelect={handleFirstSelect} />
        )}
      </div>
      <div className="sticky bottom-0 !pb-4" style={{ background: 'var(--color-bg)' }}>
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
    </div>
  );
};

export default ChatBox;
