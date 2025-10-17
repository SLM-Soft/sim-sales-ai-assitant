import React from 'react';
import { SimpleGrid, Box, Text } from '@chakra-ui/react';
import {
  FaApple,
  FaAndroid,
  FaReact,
  FaNode,
  FaPython,
  FaJava,
} from 'react-icons/fa';

interface Props {
  onSelect: (option: number) => void;
}

const icons = [FaApple, FaAndroid, FaReact, FaNode, FaPython, FaJava];

const FirstOptionsGrid: React.FC<Props> = ({ onSelect }) => {
  return (
    <SimpleGrid columns={2} row={3} gap={4} flex="1">
      {icons.map((Icon, idx) => (
        <Box
          key={idx}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          cursor="pointer"
          _hover={{ bg: 'red.600', color: 'white', transitionDuration: '0.5s' }}
          onClick={() => onSelect(idx + 1)}
        >
          <Icon size={32} />
          <Text mt={2}>Option {idx + 1}</Text>
        </Box>
      ))}
    </SimpleGrid>
  );
};

export default FirstOptionsGrid;
