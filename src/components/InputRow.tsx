import React, { useEffect, useRef } from 'react';
import { FiSettings, FiX, FiSend } from 'react-icons/fi';

interface Props {
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  loading: boolean;
  disabled?: boolean;
  showSettings: boolean;
  setShowSettings: (v: boolean) => void;
}

const InputRow: React.FC<Props> = ({
  input,
  setInput,
  onSend,
  loading,
  disabled = false,
  showSettings,
  setShowSettings,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const EXPANDED_HEIGHT_PX = 160;
  const MIN_HEIGHT_PX = 56;
  const COLLAPSED_MAX_HEIGHT_PX = 120;

  const adjustHeight = () => {
    const el = textareaRef.current;
    if (!el) return;
    if (el.value.includes('\n')) {
      el.style.height = `${EXPANDED_HEIGHT_PX}px`;
      return;
    }
    el.style.height = 'auto';
    el.style.height = `${Math.min(
      Math.max(el.scrollHeight, MIN_HEIGHT_PX),
      COLLAPSED_MAX_HEIGHT_PX
    )}px`;
  };

  useEffect(() => {
    adjustHeight();
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="flex w-full items-end gap-3">
      <div className="relative flex-1">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={adjustHeight}
          placeholder={disabled ? 'Please choose an option' : 'Write a message...'}
          disabled={disabled || loading}
          style={{ paddingRight: '120px' }}
          className="chat-textarea-scroll w-full min-h-[56px] resize-none rounded-md border border-[var(--color-border)] bg-[var(--color-surface-muted)] !p-4 text-[var(--color-text)] outline-none transition-colors placeholder:text-[var(--color-text-muted)] focus:border-[var(--color-primary)] focus:shadow-[0_0_0_1px_var(--color-primary)]"
        />
        <div className="absolute bottom-3 right-3 flex items-center gap-2 text-[var(--color-text)]">
          <button
            type="button"
            aria-label={showSettings ? 'Close generation settings' : 'Open generation settings'}
            onClick={() => setShowSettings(!showSettings)}
            disabled={disabled || loading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-[var(--color-border)] bg-[var(--color-surface-highlight)] transition hover:bg-white/10 disabled:opacity-60"
          >
            {showSettings ? <FiX size={18} /> : <FiSettings size={18} />}
          </button>
          <button
            type="button"
            aria-label="Send message"
            onClick={onSend}
            disabled={disabled || loading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-md bg-[var(--color-primary)] text-white transition hover:bg-[var(--color-primary-soft)] active:bg-[var(--color-primary-strong)] disabled:opacity-70"
          >
            <FiSend size={22} className={loading ? 'animate-pulse' : ''} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InputRow;
