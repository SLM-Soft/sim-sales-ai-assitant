import React from 'react';
import { Flex, Heading, HStack, Spinner, Text, Box } from '@chakra-ui/react';

interface Props {
  backendOk: boolean | null;
}

const ChatHeader: React.FC<Props> = ({ backendOk }) => {
  return (
    <Flex
      justifyContent="space-between"
      alignItems="center"
      p={4}
      bg="red.600"
      color="white"
    >
      <Heading size="md" textAlign="center">
        💬 Bedrock Chat
      </Heading>

      <HStack gap={2}>
        {backendOk === null ? (
          <HStack gap={2}>
            <Spinner size="sm" />
            <Text fontSize="sm">Server check…</Text>
          </HStack>
        ) : backendOk ? (
          <Box bg="green.400" w={5} h={5} rounded="full" />
        ) : (
          <Box bg="red.400" w={5} h={5} rounded="full" />
        )}
      </HStack>
    </Flex>
  );
};

export default ChatHeader;
