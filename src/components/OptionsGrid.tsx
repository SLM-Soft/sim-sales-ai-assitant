
import React from 'react';
import { SimpleGrid, Button } from '@chakra-ui/react';

interface Option {
  label: string;
  value: string;
}

interface Props {
  options: Option[];
  onOptionClick: (value: string) => void;
}

const OptionsGrid: React.FC<Props> = ({ options, onOptionClick }) => {
  return (
    <SimpleGrid columns={{ base: 1, md: 2 }} gap={3} mb={4}>
      {options.map((opt) => (
        <Button
          key={opt.value}
          onClick={() => onOptionClick(opt.value)}
          variant="outline"
          whiteSpace="normal"
        >
          {opt.label}
        </Button>
      ))}
    </SimpleGrid>
  );
};

export default OptionsGrid;
