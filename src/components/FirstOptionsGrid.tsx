import React from 'react';
import { SimpleGrid, Box, Text, } from '@chakra-ui/react';
import { firstOptions } from '../mock';

interface Props {
  onSelect: (option: number) => void;
}

const FirstOptionsGrid: React.FC<Props> = ({ onSelect }) => {
  return (
    <div className='flex flex-col !h-full items-center justify-center text-white gap-20'>
      <div className='items-center justify-center flex flex-col'>
        <p className='!text-2xl !font-bold text-center'>
          What Can I Help You With?
        </p>
        <p className='mb-4 text-center text-gray-300'>
          Choose one of the options below and we will assist you!
        </p>
      </div>

      <SimpleGrid columns={3} gap={4} mt={2}>
        {firstOptions.map((opt, idx) => {
          const Icon = opt.icon;
          return (
            <Box
              key={idx}
              onClick={() => onSelect(idx)}
              className='flex relative justify-start flex-col hover:bg-red-600 hover:text-white duration-300 cursor-pointer !p-4 !border'
            >
              <div className='flex items-start justify-between mb-2'>
                <p className='text-base mr-4 flex-1 !font-bold'>
                  {opt.title}
                </p>
                <Box
                  className={`rounded-none w-10 h-10 flex items-center justify-center text-white`}
                  bg={opt.bgColor}
                >
                  <Icon size={24} />
                </Box>
              </div>

              <Text fontSize="sm">{opt.description}</Text>
            </Box>
          );
        })}
      </SimpleGrid>
    </div>
  );
};

export default FirstOptionsGrid;
