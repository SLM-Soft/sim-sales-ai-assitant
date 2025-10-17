import { createSystem, defaultConfig } from '@chakra-ui/react';

export const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        red: {
          600: { value: '#dc2626' },
        },
        gray: {
          600: { value: '#4b5563' },
        },
      },
    },
  },
});
