
import React from 'react';

interface Option {
  label: string;
  value: string;
}

interface Props {
  options: Option[];
  onOptionClick: (value: string) => void;
}

const OptionsGrid: React.FC<Props> = ({ options, onOptionClick }) => {
  return (
    <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onOptionClick(opt.value)}
          className="rounded border border-[var(--color-border)] px-4 py-3 text-left text-[var(--color-text)] transition hover:border-[var(--color-primary)] hover:bg-[var(--color-primary)]/10"
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
};

export default OptionsGrid;
