import React, { useEffect, useRef } from 'react';
import ChatHeader from './ChatHeader';
import MessagesList from './MessagesList';
import FirstOptionsGrid from './FirstOptionsGrid';
import InputRow from './InputRow';
import GenerationSettings from './GenerationSettings';
import { checkHealth, sendChat } from '../api/bedrock';
import { firstOptions, suggestionByOption } from '../mock';
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

  const resolveOptionKey = () => {
    if (firstOption !== null && firstOptions[firstOption]) {
      return firstOptions[firstOption].key;
    }
    return 'general_llm';
  };

  const handleSend = async (textOverride?: string) => {
    const messageToSend = typeof textOverride === 'string' ? textOverride : input;
    if (!messageToSend.trim() || loading) return;

    const userMessage = messageToSend.trim();

    addMessage({ role: 'User', content: userMessage });
    setInput('');
    setLoading(true);

    try {
      const optionKey = resolveOptionKey();

      const resp = await sendChat({
        userQuestion: userMessage,
        optionKey,
        sessionId: sessionIdRef.current,
      });

      addMessage({
        role: 'Assistant',
        content: resp.outputText,
      });
    } catch (err) {
      console.error(err);
      addMessage({ role: 'Assistant', content: 'Error: failed to get response' });
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAsk = async (question: string) => {
    if (loading) return;
    setInput(question);
    await handleSend(question);
  };

  const hasMessages = messages.length > 0;
  const showChat = firstOption !== null || hasMessages;
  const optionKey = resolveOptionKey();
  const suggestionList = suggestionByOption[optionKey] || suggestionByOption.general_llm;

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
        {!messages.length && (
          <div className="flex w-full justify-center">
            {suggestionList.length > 0 && (
              <div className="flex flex-wrap gap-2 !mb-3">
                {suggestionList.map((q) => (
                  <button
                    key={q}
                    type="button"
                    disabled={loading}
                    onClick={() => handleQuickAsk(q)}
                    className="rounded-full border border-[var(--color-border)] bg-[var(--color-surface-muted)] !px-3 !py-1.5 text-sm text-[var(--color-text)] transition hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] disabled:opacity-60"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
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
