import React from 'react';
import { firstOptions } from '../mock';

interface Props {
  onSelect: (option: number) => void;
}

const gradient =
  'linear-gradient(135deg, var(--color-primary) 0%, rgba(255,255,255,0.08) 45%, var(--color-accent) 100%)';

const FirstOptionsGrid: React.FC<Props> = ({ onSelect }) => {
  return (
    <div
      className="flex h-full w-full flex-col items-center justify-center gap-14 px-4 py-6"
      style={{ color: 'var(--color-text)' }}
    >
      <div className="flex flex-col items-center justify-center text-center">
        <p className="text-2xl font-bold">What Can I Help You With?</p>
        <p className="mb-1" style={{ color: 'var(--color-text-muted)' }}>
          Choose one of the options below and we will assist you!
        </p>
        <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>
          Hover a card to feel the depth, click to jump in.
        </p>
      </div>

      <div className="option-grid grid w-full grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 lg:grid-cols-3">
        {firstOptions.map((opt, idx) => {
          const Icon = opt.icon;

          return (
            <div
              key={idx}
              role="button"
              tabIndex={0}
              onClick={() => onSelect(idx)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelect(idx);
                }
              }}
              className="option-card"
              aria-label={`Start with ${opt.title}`}
            >
              <div className="option-card__track">
                <span
                  aria-hidden
                  className="option-card__layer option-card__layer--glow"
                  style={{ background: gradient }}
                />
                <span
                  aria-hidden
                  className="option-card__layer option-card__layer--grid"
                />
                <span
                  aria-hidden
                  className="option-card__layer option-card__layer--edge"
                />

                <div className="option-card__surface">
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="flex flex-col gap-1 pr-2">
                      <p className="text-base font-bold leading-tight" style={{ color: 'var(--color-text)' }}>
                        {opt.title}
                      </p>
                      <p
                        className="text-sm"
                        style={{
                          color: 'var(--color-text-muted)',
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {opt.description}
                      </p>
                    </div>
                    <div
                      className="option-card__icon"
                      style={{ background: opt.bgColor }}
                    >
                      <Icon size={22} />
                    </div>
                  </div>

                  <p className="text-xs uppercase tracking-wide" style={{ color: 'var(--color-text-muted)' }}>
                    Hover for depth / Click to start
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FirstOptionsGrid;
