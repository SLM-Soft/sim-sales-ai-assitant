import React from 'react';
import { SimpleGrid, Box, Text } from '@chakra-ui/react';

interface Props {
  selected?: number | null;
  onSelect: (option: number) => void;
}

const SecondOptionsGrid: React.FC<Props> = ({ selected = null, onSelect }) => {
  return (
    <SimpleGrid columns={2} gap={2} px={4}>
      {[1, 2, 3, 4].map((num) => (
        <Box
          key={num}
          p={2}
          mx={4}
          borderWidth="1px"
          display="flex"
          alignItems="center"
          justifyContent="center"
          cursor="pointer"
          margin={0}
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
