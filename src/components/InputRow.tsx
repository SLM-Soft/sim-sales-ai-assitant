import React from 'react';
import { HStack, Input, Button } from '@chakra-ui/react';

interface Props {
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  loading: boolean;
  disabled?: boolean;
}

const InputRow: React.FC<Props> = ({
  input,
  setInput,
  onSend,
  loading,
  disabled = false,
}) => {
  return (
    <HStack gap={3}>
      <Input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && !disabled && onSend()}
        rounded="none"
        placeholder={
          disabled ? 'Please choose an option' : 'Write a message...'
        }
        disabled={disabled || loading}
        p={4}
      />
      <Button
        onClick={onSend}
        loading={loading}
        loadingText="Sending"
        bg="#dc2626"
        color="white"
        width="20%"
        _hover={{ opacity: 0.9 }}
        p={4}
        disabled={disabled || loading}
      >
        Send
      </Button>
    </HStack>
  );
};

export default InputRow;
