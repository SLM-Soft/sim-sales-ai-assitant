import React from 'react';
import { Flex, Heading, HStack, Spinner, Text, Badge } from '@chakra-ui/react';

interface Props {
  backendOk: boolean | null;
}

const ChatHeader: React.FC<Props> = ({ backendOk }) => {
  return (
    <Flex justifyContent="space-between" alignItems="center" mb={4}>
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
          <Badge colorScheme="green" variant="subtle">
            Backend online
          </Badge>
        ) : (
          <Badge colorScheme="red" variant="subtle">
            Backend offline
          </Badge>
        )}
      </HStack>
    </Flex>
  );
};

export default ChatHeader;
