import React from 'react';
import { HStack, Input, Button } from '@chakra-ui/react';
import { FiSettings, FiX } from 'react-icons/fi';

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
  return (
    <HStack gap={3}>
      <Input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && !disabled && onSend()}
        rounded="none"
        placeholder={disabled ? 'Please choose an option' : 'Write a message...'}
        disabled={disabled || loading}
        p={4}
      />
      <div className="flex justify-end">
        <button
          type="button"
          onClick={() => setShowSettings(!showSettings)}
          title={showSettings ? 'Close generation settings' : 'Open generation settings'}
          className="w-10 h-10 !border border-gray-600 inline-flex items-center justify-center cursor-pointer"
        >
          {showSettings ? <FiX size={25} /> : <FiSettings size={25} />}
        </button>
      </div>

      <Button
        onClick={onSend}
        loading={loading}
        loadingText="Sending"
        bg="#000"
        color="white"
        w="20%"
        borderRadius={0}
        _hover={{ bg: '#dc2626' }}
        p={4}
        disabled={disabled || loading}
      >
        Send
      </Button>
    </HStack>
  );
};

export default InputRow;
