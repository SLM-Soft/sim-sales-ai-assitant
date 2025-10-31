import React from 'react';
import { Box, VStack, Text, Flex } from '@chakra-ui/react';

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
      mx={4}
      border="1px solid"
      borderColor="gray.200"
    >
      <VStack gap={3} align="stretch">
        {messages.length === 0 ? (
          <Text color="gray.500" textAlign="center">
            No messages yet. Start the conversation!
          </Text>
        ) : (
          messages.map((m, i) => {
            const isUser = m.role === 'User';
            return (
              <Flex key={i} justify={isUser ? 'flex-end' : 'flex-start'}>
                <Box
                  maxW="70%"
                  px={4}
                  py={2}
                  bg={isUser ? 'red.600' : 'black'}
                  color="white"
                  textAlign="left"
                  wordBreak="break-word"
                >
                  <Text
                    whiteSpace="pre-wrap"
                    wordBreak="break-word"
                    fontSize="sm"
                  >
                    {m.content}
                  </Text>
                </Box>
              </Flex>
            );
          })
        )}
      </VStack>
    </Box>
  );
};

export default MessagesList;
