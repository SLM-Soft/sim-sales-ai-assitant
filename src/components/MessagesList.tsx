import React from 'react';
import { Box, VStack, Text } from '@chakra-ui/react';

interface Msg {
  role: string;
  content: string;
}

interface Props {
  messages: Msg[];
  scrollRef: React.RefObject<HTMLDivElement | null>;
}

const MessagesList: React.FC<Props> = ({ messages, scrollRef }) => {
  return (
    <Box
      ref={scrollRef}
      flex="1 1 auto"
      overflowY="auto"
      px={2}
      py={2}
      borderWidth="1px"
      borderRadius="md"
      mb={4}
    >
      <VStack gap={3} align="stretch">
        {messages.length === 0 ? (
          <Text color="gray.500" textAlign="center">
            No messages. Please select an option to start.
          </Text>
        ) : (
          messages.map((m, i) => (
            <Box key={i}>
              <Text fontSize="sm" color={m.role === 'User' ? 'gray.800' : 'gray.600'}>
                <strong>{m.role}:</strong> {m.content}
              </Text>
            </Box>
          ))
        )}
      </VStack>
    </Box>
  );
};

export default MessagesList;
