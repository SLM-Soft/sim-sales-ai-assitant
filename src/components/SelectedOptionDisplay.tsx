import React from 'react';
import { Box, Text, Flex, Button } from '@chakra-ui/react';
import { firstOptions } from '../mock';
import { FaArrowLeft } from 'react-icons/fa';

interface Props {
  selected?: number | null;
  onBack?: () => void;
}

const SelectedOptionDisplay: React.FC<Props> = ({ selected, onBack }) => {
  if (selected === null || selected === undefined) return null;

  const opt = firstOptions[selected];
  if (!opt) return null;

  const { title, icon: Icon, bgColor } = firstOptions[selected];

  return (
    <Flex
      align="center"
      borderRadius="md"
      bg="gray.100"
      color="black"
      justifyContent="flex-start"
      mx={2}
    >
      {onBack && (
        <Button onClick={onBack} size="sm" variant="ghost">
          <FaArrowLeft />
        </Button>
      )}

      <Box
        w={10}
        h={10}
        borderRadius="none"
        bg={bgColor}
        display="flex"
        alignItems="center"
        justifyContent="center"
        color="white"
        mr={3}
      >
        <Icon size={24} />
      </Box>

      <Text fontWeight="bold">{title}</Text>
    </Flex>
  );
};

export default SelectedOptionDisplay;
