import React from 'react';
import { FaArrowLeft } from 'react-icons/fa';
import { FiMoon, FiSun, FiAperture } from 'react-icons/fi';
import { firstOptions } from '../mock';
import { useChatStore } from '../store/chatStore';

interface Props {
  backendOk: boolean | null;
  selected?: number | null;
  onBack?: () => void;
}

const ChatHeader: React.FC<Props> = ({ backendOk, selected, onBack }) => {
  const opt = selected !== null && selected !== undefined ? firstOptions[selected] : null;
  const { theme, setTheme } = useChatStore();
  const themeOptions: Array<{
    key: 'dark' | 'light' | 'neutral';
    label: string;
    icon: React.ReactNode;
  }> = [
    { key: 'dark', label: 'Dark', icon: <FiMoon size={16} /> },
    { key: 'light', label: 'Light', icon: <FiSun size={16} /> },
    { key: 'neutral', label: 'Neutral', icon: <FiAperture size={16} /> },
  ];

  return (
    <div
      className="flex flex-col gap-2 max-w-[1350px] w-full sticky top-0 !py-3"
      style={{ background: 'var(--color-bg)', color: 'var(--color-text)', zIndex: 10 }}
    >
      <div className="flex items-center gap-3 px-3 justify-between flex-wrap">
        <div className="flex items-center gap-3">
          {backendOk ? (
            <div className="w-4 h-4 rounded-full" style={{ background: 'var(--color-success)' }} />
          ) : (
            <div className="w-4 h-4 rounded-full" style={{ background: 'var(--color-primary)' }} />
          )}
          <span className="!text-lg !font-semibold" style={{ color: 'var(--color-text)' }}>
            SLM Business Assistant
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div
            style={{
              display: 'inline-flex',
              background: 'var(--color-surface-muted)',
              border: '1px solid var(--color-border)',
              borderRadius: 9999,
              padding: '4px',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }}
          >
            {themeOptions.map((opt) => {
              const active = theme === opt.key;
              return (
                <button
                  key={opt.key}
                  type="button"
                  onClick={() => setTheme(opt.key)}
                  className="flex items-center gap-1 px-3 py-1 text-sm font-medium transition-colors"
                  style={{
                    borderRadius: 9999,
                    padding: '6px 12px',
                    background: active ? 'var(--color-primary)' : 'transparent',
                    color: active ? '#fff' : 'var(--color-text)',
                    border: 'none',
                    boxShadow: active ? '0 0 0 1px rgba(255,255,255,0.16)' : 'none',
                    cursor: 'pointer',
                  }}
                >
                  {opt.icon}
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {opt && (
        <div className="flex items-center gap-3 px-1">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="w-5 h-5 flex items-center justify-center transition-colors rounded text-[var(--color-text)] hover:text-[var(--color-accent)]"
            >
              <FaArrowLeft size={20} />
            </button>
          )}

          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 flex items-center justify-center"
              style={{ color: opt.bgColor }}
            >
              <opt.icon size={24} />
            </div>
            <p className="font-semibold" style={{ color: 'var(--color-text)' }}>
              {opt.title}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHeader;
