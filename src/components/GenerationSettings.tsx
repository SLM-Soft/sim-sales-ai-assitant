import React from 'react';
import { FiSettings } from 'react-icons/fi';
import { useChatStore } from '../store/chatStore';

const RED = '#dc2626';
const snap = (v: number, step: number) => Math.round(v / step) * step;
const round10 = (v: number) => Math.round(v * 10) / 10;

const RangeRow: React.FC<{
  id: string;
  label: string;
  value: number | string;
  min: number;
  max: number;
  step: number;
  onChange: (n: number) => void;
  showValue?: (n: number) => string | number;
}> = ({ id, label, value, min, max, step, onChange, showValue }) => {
  return (
    <div>
      <label htmlFor={id} style={{ fontSize: 12, fontWeight: 600 }}>
        {label}: {showValue ? showValue(Number(value)) : value}
      </label>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        onWheel={(e) => e.currentTarget.blur()}
        style={{ width: '100%', marginTop: 6, accentColor: RED }}
      />
    </div>
  );
};

const GenerationSettings: React.FC = () => {
  const {
    showSettings,
    temperature,
    setTemperature,
    maxTokens,
    setMaxTokens,
    level,
    setLevel,
    includeBenchmarks,
    setIncludeBenchmarks,
  } = useChatStore();

  const handleTemp = (n: number) => setTemperature(round10(n));

  if (!showSettings) return null;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
        marginBottom: 12,
        padding: 14,
        border: '1px solid rgba(0,0,0,0.15)',
      }}
      className='text-black bg-white'
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <FiSettings size={18} />
        <strong style={{ fontSize: 14 }}>Generation settings</strong>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', rowGap: 8 }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <label style={{ fontSize: 12, fontWeight: 600 }}>
            Level
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value as typeof level)}
              style={{
                marginLeft: 8,
                border: '1px solid rgba(0,0,0,0.15)',
                borderRadius: 6,
                padding: '6px 8px',
                fontSize: 13,
                background: 'white',
              }}
            >
              <option value="brief">brief</option>
              <option value="detailed">detailed</option>
            </select>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
            <input
              type="checkbox"
              checked={includeBenchmarks}
              onChange={(e) => setIncludeBenchmarks(e.target.checked)}
            />
            includeBenchmarks
          </label>
        </div>

        <div className="grid grid-cols-2 gap-x-10">
          <RangeRow
            id="temperature"
            label="Temperature"
            value={temperature}
            min={0}
            max={1}
            step={0.1}
            onChange={handleTemp}
            showValue={(n) => n.toFixed(1)}
          />

          <RangeRow
            id="maxTokensRange"
            label="Max tokens"
            value={maxTokens}
            min={64}
            max={8192}
            step={64}
            onChange={(n) => setMaxTokens(Math.round(n))}
            showValue={(n) => snap(n, 64)}
          />

        </div>
      </div>
    </div>
  );
};

export default GenerationSettings;
