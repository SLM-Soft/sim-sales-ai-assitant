// components/SecondOptionsGrid.tsx
import React from 'react';
import { SimpleGrid, Box, Text } from '@chakra-ui/react';

interface Props {
  selected?: number | null; // <-- добавили ожидаемый проп
  onSelect: (option: number) => void;
}

const SecondOptionsGrid: React.FC<Props> = ({ selected = null, onSelect }) => {
  return (
    // Маленькая сетка 2x2 — компактная, чтобы под ней поместилось поле ввода
    <SimpleGrid columns={2} gap={3}>
      {[1, 2, 3, 4].map((num) => (
        <Box
          key={num}
          p={3}
          borderWidth="1px"
          borderRadius="md"
          display="flex"
          alignItems="center"
          justifyContent="center"
          cursor="pointer"
          bg={selected === num ? 'red.600' : 'transparent'}
          color={selected === num ? 'white' : 'black'}
          _hover={{ bg: 'red.600', color: 'white', transitionDuration: '0.5s' }}
          onClick={() => onSelect(num)}
        >
          <Text>Sub {num}</Text>
        </Box>
      ))}
    </SimpleGrid>
  );
};

export default SecondOptionsGrid;
