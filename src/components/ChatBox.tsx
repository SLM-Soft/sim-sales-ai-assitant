import React, { useEffect, useRef } from 'react';
import ChatHeader from './ChatHeader';
import MessagesList from './MessagesList';
import FirstOptionsGrid from './FirstOptionsGrid';
import InputRow from './InputRow';
import GenerationSettings from './GenerationSettings';
import { checkHealth, sendChat } from '../api/bedrock';
import { firstOptions, suggestionByOption } from '../mock';
import { useChatStore } from '../store/chatStore';
import { exportElementToPdf } from '../utils/pdfExport';

const ChatBox: React.FC = () => {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const conversationRef = useRef<HTMLDivElement | null>(null);
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
    theme,
  } = useChatStore();
  const [exportingChat, setExportingChat] = React.useState(false);

  const sanitizeAssistantText = (text: string) => {
    if (!text) return text;
    const lines = text.split('\n').filter((line) => {
      const lower = line.toLowerCase();
      const hasPdf = lower.includes('pdf');
      const hasInstruction =
        lower.includes('download') || lower.includes('click') || lower.includes('button');
      return !(hasPdf && hasInstruction);
    });
    return lines.join('\n').trim();
  };

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

  const triggerPdfDownload = (pdfBase64: string, fileName: string) => {
    try {
      const byteCharacters = atob(pdfBase64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i += 1) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF', err);
    }
  };

  const handleSend = async (textOverride?: string) => {
    const messageToSend = typeof textOverride === 'string' ? textOverride : input;
    if (!messageToSend.trim() || loading) return;

    const userMessage = messageToSend.trim();
    const userChatMessage = { role: 'User', content: userMessage } as const;
    const conversationMessages = [...messages, userChatMessage].map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    addMessage(userChatMessage);
    setInput('');
    setLoading(true);

    try {
      const optionKey = resolveOptionKey();

      const resp = await sendChat({
        userQuestion: userMessage,
        optionKey,
        sessionId: sessionIdRef.current,
        messages: conversationMessages,
      });

      const cleanText = sanitizeAssistantText(resp.outputText);
      addMessage({
        role: 'Assistant',
        content: cleanText,
        followUps: resp.followUps?.slice(0, 3),
        pdfBase64: resp.pdfBase64,
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

  const handleExportChat = async () => {
    if (!messages.length || exportingChat) return;
    try {
      setExportingChat(true);
      if (conversationRef.current) {
        await exportElementToPdf(conversationRef.current, {
          fileName: 'chat-history.pdf',
          theme,
        });
      }
    } catch (error) {
      console.error('Failed to export chat PDF', error);
    } finally {
      setExportingChat(false);
    }
  };

  const hasMessages = messages.length > 0;
  const showChat = firstOption !== null || hasMessages;
  const optionKey = resolveOptionKey();
  const suggestionList = suggestionByOption[optionKey] || suggestionByOption.general_llm;

  const handleNewChat = () => {
    clearMessages();
    setFirstOption(null);
    setInput('');
    sessionIdRef.current = genSessionId();
  };

  return (
    <div className="w-full max-w-[1350px] flex flex-col px-4" style={{ color: 'var(--color-text)' }}>
      <ChatHeader
        backendOk={backendOk}
        selected={firstOption}
        hasMessages={hasMessages}
        loading={loading}
        onNewChat={handleNewChat}
        onExportChat={handleExportChat}
        exportingChat={exportingChat}
        canExportChat={messages.length > 0}
      />

      <div className="w-full flex-1">
        <div ref={conversationRef} className="w-full flex-1">
          {showChat ? (
            <MessagesList
              messages={messages}
              scrollRef={scrollRef}
              onSuggestionClick={handleQuickAsk}
              onPdfDownload={triggerPdfDownload}
            />
          ) : (
            <FirstOptionsGrid onSelect={handleFirstSelect} />
          )}
        </div>
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
