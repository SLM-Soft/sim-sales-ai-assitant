import React from 'react';
import { FaArrowLeft } from 'react-icons/fa';
import { firstOptions } from '../mock';

interface Props {
  backendOk: boolean | null;
  selected?: number | null;
  onBack?: () => void;
}

const ChatHeader: React.FC<Props> = ({ backendOk, selected, onBack }) => {
  const opt = selected !== null && selected !== undefined ? firstOptions[selected] : null;

  return (
    <div className="flex flex-col gap-2 max-w-[1350px] bg-neutral-800 w-full sticky top-0 !py-3">
      <div className="flex items-center gap-3 text-white px-3">
        {backendOk ? (
          <div className="w-4 h-4 rounded-full bg-green-400" />
        ) : (
          <div className="w-4 h-4 rounded-full bg-red-500" />
        )}
        <span className="!text-lg !font-semibold">SLM Business Assistant</span>
      </div>

      {opt && (
        <div className="flex items-center gap-3 px-1">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="w-5 h-5 flex items-center justify-center text-white transition-colors rounded !hover:bg-red-600 cursor-pointer"
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
            <p className="font-semibold text-white">{opt.title}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHeader;
