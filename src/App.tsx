import { ChakraProvider } from '@chakra-ui/react';
import { system } from './theme';
import HomePage from './pages/HomePage';

export default function App() {
  return (
    <ChakraProvider value={system}>
      <HomePage />
    </ChakraProvider>
  );
}
