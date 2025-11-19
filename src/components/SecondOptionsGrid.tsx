import React from 'react';

interface Props {
  selected?: number | null;
  onSelect: (option: number) => void;
}

const SecondOptionsGrid: React.FC<Props> = ({ selected = null, onSelect }) => {
  return (
    <div className="grid grid-cols-2 gap-2 px-4">
      {[1, 2, 3, 4].map((num) => {
        const isActive = selected === num;
        return (
          <button
            key={num}
            type="button"
            onClick={() => onSelect(num)}
            className={`mx-4 flex items-center justify-center rounded border px-2 py-2 transition ${
              isActive
                ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white'
                : 'border-[var(--color-border)] bg-transparent text-[var(--color-text)] hover:bg-[var(--color-primary)]/10'
            }`}
          >
            Sub {num}
          </button>
        );
      })}
    </div>
  );
};

export default SecondOptionsGrid;
