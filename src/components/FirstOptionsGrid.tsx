import React from 'react';
import { SimpleGrid, Box, Text, Flex, VStack } from '@chakra-ui/react';
import { firstOptions } from '../mock';

interface Props {
  onSelect: (option: number) => void;
}

const FirstOptionsGrid: React.FC<Props> = ({ onSelect }) => {
  return (
    <VStack align="stretch" flex="1" p={4}>
      <Box textAlign="center" mb={4}>
        <Text fontSize="xl" fontWeight="bold" mb={2}>
          What Can I Help You With?
        </Text>
        <Text fontSize="sm" color="gray.500">
          Choose one of the options below and we will assist you!
        </Text>
      </Box>

      <SimpleGrid columns={2} row={3} gap={4} mt={2} flex="1">
        {firstOptions.map((opt, idx) => {
          const Icon = opt.icon;
          return (
            <Box
              key={idx}
              p={4}
              borderWidth="1px"
              cursor="pointer"
              _hover={{ bg: 'red.600', color: 'white', transitionDuration: '0.3s' }}
              onClick={() => onSelect(idx + 1)}
              display="flex"
              flexDirection="column"
              justifyContent="flex-start"
              position="relative"
            >
              <Flex justifyContent="space-between" alignItems="flex-start" mb={2}>
                <Text fontWeight="bold" flex="1" mr={4} fontSize="base">
                  {opt.title}
                </Text>
                <Box
                  w={10}
                  h={10}
                  borderRadius="none"
                  bg={opt.bgColor}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  color="white"
                >
                  <Icon size={24} />
                </Box>
              </Flex>

              <Text fontSize="sm" color="gray.500">
                {opt.description}
              </Text>
            </Box>
          );
        })}
      </SimpleGrid>
    </VStack>
  );
};

export default FirstOptionsGrid;
