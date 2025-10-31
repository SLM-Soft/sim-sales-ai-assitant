import React from 'react';
import { Flex, HStack, Spinner, Text, Box } from '@chakra-ui/react';

interface Props {
  backendOk: boolean | null;
}

const ChatHeader: React.FC<Props> = ({ backendOk }) => {
  return (
    <Flex textAlign="center" p={4} bg="red.600" color="white" gap={2}>
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
      </HStack>{' '}
      Bedrock Chat
    </Flex>
  );
};

export default ChatHeader;
