import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FiCopy, FiCheck, FiEdit2, FiSave, FiX } from 'react-icons/fi';
import { useChatStore } from '../store/chatStore';

interface Msg {
  role: string;
  content: string;
}

interface Props {
  messages: Msg[];
  scrollRef: React.RefObject<HTMLDivElement | null>;
}

const urlRegex = /(https?:\/\/[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)/g;

const renderWithLinks = (text: string): React.ReactNode[] => {
  if (!text) return [''];
  const matches = Array.from(text.matchAll(urlRegex));
  if (matches.length === 0) return [text];

  const nodes: React.ReactNode[] = [];
  let lastIndex = 0;

  matches.forEach((match, idx) => {
    const start = match.index ?? 0;
    if (start > lastIndex) {
      nodes.push(text.slice(lastIndex, start));
    }
    const url = match[0];
    const href = url.startsWith('http') ? url : `https://${url}`;
    nodes.push(
      <a
        key={`link-${start}-${idx}`}
        href={href}
        target="_blank"
        rel="noreferrer"
        className="text-[var(--color-accent)] underline underline-offset-2 hover:opacity-80"
      >
        {url}
      </a>,
    );
    lastIndex = start + url.length;
  });

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return nodes;
};

const MessagesList: React.FC<Props> = ({ messages, scrollRef }) => {
  const updateMessageContent = useChatStore((s) => s.updateMessageContent);
  const [copiedMsgIdx, setCopiedMsgIdx] = React.useState<number | null>(null);
  const [editingIdx, setEditingIdx] = React.useState<number | null>(null);
  const [draftContent, setDraftContent] = React.useState<string>('');
  const editTextareaRef = React.useRef<HTMLTextAreaElement | null>(null);

  const adjustEditHeight = React.useCallback((target?: HTMLTextAreaElement | null) => {
    const el = target ?? editTextareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.max(el.scrollHeight, 60)}px`;
  }, []);

  const handleCopy = async (text: string, idx: number) => {
    if (!navigator?.clipboard) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMsgIdx(idx);
      setTimeout(() => {
        setCopiedMsgIdx((prev) => (prev === idx ? null : prev));
      }, 2000);
    } catch (error) {
      console.error('Failed to copy assistant message', error);
    }
  };

  const beginEdit = (idx: number, currentText: string) => {
    setEditingIdx(idx);
    setDraftContent(currentText);
  };

  const cancelEdit = () => {
    setEditingIdx(null);
    setDraftContent('');
  };

  const saveEdit = (idx: number) => {
    updateMessageContent(idx, draftContent);
    setEditingIdx(null);
    setDraftContent('');
  };

  const handleEditorKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>, idx: number) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      saveEdit(idx);
    }
    if (e.key === 'Escape') {
      e.preventDefault();
      cancelEdit();
    }
  };

  React.useEffect(() => {
    if (editingIdx !== null) {
      adjustEditHeight();
    }
  }, [draftContent, editingIdx, adjustEditHeight]);

  return (
    <div className="px-4 py-4 text-[var(--color-text)]">
      <div className="flex flex-col gap-4">
        {messages.length === 0 ? (
          <p className="text-center text-sm text-[var(--color-text-muted)]">
            No messages yet. Start the conversation!
          </p>
        ) : (
          messages.map((m, i) => {
            const isUser = m.role === 'User';
            const isCopied = copiedMsgIdx === i;

            return (
              <div key={i} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                <div
                  className="flex w-full max-w-[80%] flex-col"
                  style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}
                >
                  <div
                    className="w-full rounded-[18px] border px-5 py-4 text-left"
                    style={{
                      background: isUser
                        ? 'linear-gradient(135deg, var(--color-primary-soft), var(--color-primary))'
                        : 'var(--color-surface-muted)',
                      color: isUser ? '#fffafa' : 'var(--color-text)',
                      borderColor: isUser ? 'var(--color-primary-soft)' : 'var(--color-border)',
                      boxShadow: isUser
                        ? '0 20px 40px rgba(0, 0, 0, 0.35)'
                        : '0 12px 30px rgba(15, 23, 42, 0.12)',
                      backdropFilter: isUser ? 'blur(1.5px)' : 'none',
                      paddingRight: isUser ? '20px' : editingIdx === i ? '20px' : '72px',
                    }}
                  >
                    {editingIdx === i ? (
                      <>
                        <textarea
                          value={draftContent}
                          onChange={(e) => setDraftContent(e.target.value)}
                          onKeyDown={(e) => handleEditorKeyDown(e, i)}
                          ref={(el) => {
                            editTextareaRef.current = el;
                            adjustEditHeight(el);
                          }}
                          onInput={(e) => adjustEditHeight(e.currentTarget)}
                          className="chat-textarea-scroll w-full resize-none rounded-xl border border-[var(--color-border)] bg-[rgba(15,23,42,0.2)] !p-3 text-[var(--color-text)] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)] transition focus:border-[var(--color-primary)] focus:shadow-[0_0_0_1px_var(--color-primary)]"
                          style={{ fontFamily: 'inherit', fontSize: '0.95rem', lineHeight: '1.55', overflow: 'hidden' }}
                        />
                        <div className="!my-3 flex justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => saveEdit(i)}
                            className="inline-flex items-center gap-2 rounded-full bg-[var(--color-primary)] !px-3 !py-1.5 text-sm text-white"
                          >
                            <FiSave size={16} />
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={cancelEdit}
                            className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] !px-3 !py-1.5 text-sm text-[var(--color-text)]"
                          >
                            <FiX size={16} />
                            Cancel
                          </button>
                        </div>
                      </>
                    ) : isUser ? (
                      <p className="whitespace-pre-wrap text-base leading-relaxed !py-2 !px-4">
                        {renderWithLinks(m.content)}
                      </p>
                    ) : (
                      <div className="markdown-body text-base leading-relaxed !py-2 !px-4">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            a: ({ ...props }) => (
                              <a
                                {...props}
                                className="text-[var(--color-accent)] underline underline-offset-2 hover:opacity-80"
                                target="_blank"
                                rel="noreferrer"
                              />
                            ),
                            table: ({ ...props }) => (
                              <div className="overflow-x-auto">
                                <table
                                  {...props}
                                  className="w-full border-collapse text-left"
                                  style={{ borderColor: 'var(--color-border)' }}
                                />
                              </div>
                            ),
                            th: ({ ...props }) => (
                              <th
                                {...props}
                                className="border !px-3 !py-2"
                                style={{ borderColor: 'var(--color-border)' }}
                              />
                            ),
                            td: ({ ...props }) => (
                              <td
                                {...props}
                                className="border !px-3 !py-2 align-top"
                                style={{ borderColor: 'var(--color-border)' }}
                              />
                            ),
                            p: ({ ...props }) => <p {...props} className="!mb-3 last:mb-0" />,
                            ul: ({ ...props }) => <ul {...props} className="list-disc !pl-5 !mb-3" />,
                            ol: ({ ...props }) => <ol {...props} className="list-decimal !pl-5 !mb-3" />,
                            li: ({ ...props }) => <li {...props} className="!mb-1 last:mb-0" />,
                          }}
                        >
                          {m.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>

                  {!isUser && editingIdx !== i && (
                    <div className="!mt-2 !ml-4 flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleCopy(m.content, i)}
                        className="inline-flex items-center gap-2 rounded-full text-sm text-[var(--color-text)] transition hover:opacity-100"
                        style={{ opacity: 0.9 }}
                      >
                        {isCopied ? <FiCheck size={16} /> : <FiCopy size={16} />}
                        Copy
                      </button>
                      <button
                        type="button"
                        onClick={() => beginEdit(i, m.content)}
                        className="inline-flex items-center gap-2 rounded-full text-sm text-[var(--color-text)] transition hover:opacity-100"
                        style={{ opacity: 0.9 }}
                      >
                        <FiEdit2 size={16} />
                        Edit
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}

        <div ref={scrollRef} className="h-[1px]" />
      </div>
    </div>
  );
};

export default MessagesList;
