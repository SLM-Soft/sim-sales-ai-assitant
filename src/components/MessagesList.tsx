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
  console.log('Rendering MessagesList with messages:', messages);
  return (
    <Box px={2} py={2} className="text-white">
      <VStack gap={3} align="stretch">
        {messages.length === 0 ? (
          <Text textAlign="center">
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

        {/* якорь для авто-скролла страницы */}
        <Box ref={scrollRef} h="1px" />
      </VStack>
    </Box>
  );
};

export default MessagesList;
