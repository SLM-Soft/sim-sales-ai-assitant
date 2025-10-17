import React, { useEffect, useRef, useState } from 'react';
import { Box } from '@chakra-ui/react';
import ChatHeader from './ChatHeader';
import MessagesList from './MessagesList';
import FirstOptionsGrid from './FirstOptionsGrid';
import SecondOptionsGrid from './SecondOptionsGrid';
import InputRow from './InputRow';
import SelectedOptionDisplay from './SelectedOptionDisplay';
import { checkHealth, sendMessage } from '../api/bedrock';
import { firstOptions } from '../mock';

const ChatBox: React.FC = () => {
  const [firstOption, setFirstOption] = useState<number | null>(null);
  const [secondOption, setSecondOption] = useState<number | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<
    { role: 'User' | 'Assistant'; content: string }[]
  >([]);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [loading, setLoading] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages.length]);

  const handleFirstSelect = (opt: number) => setFirstOption(opt);
  const handleSecondSelect = (opt: number) => setSecondOption(opt);

  const handleSend = async () => {
    if (!firstOption || !secondOption || !input.trim()) return;

    const firstDesc = firstOptions[firstOption - 1].description;
    const secondTitle = ['Option 1', 'Option 2', 'Option 3', 'Option 4'][secondOption - 1];

    // const userMessage = `${firstDesc} | ${secondTitle} | ${input.trim()}`;
    const userMessage = input.trim();
    console.log('User message:', `${firstDesc} | ${secondTitle} | ${input.trim()}`);

    setMessages((m) => [...m, { role: 'User', content: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const { outputText } = await sendMessage([
        { role: 'User', content: userMessage },
      ]);

      if (outputText) {
        setMessages((m) => [...m, { role: 'Assistant', content: outputText }]);
      }
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        { role: 'Assistant', content: 'Error: failed to get a response' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchHealth = async () => {
      const ok = await checkHealth();
      setBackendOk(ok);
    };

    fetchHealth();
  }, []);

  return (
    <Box
      border="1px solid"
      borderColor="gray.200"
      display="flex"
      flexDirection="column"
      height="full"
      minH="520px"
      gap={4}
    >
      <ChatHeader backendOk={backendOk} />

      <SelectedOptionDisplay
        selected={firstOption}
        onBack={() => {
          setFirstOption(null);
          setSecondOption(null);
        }}
      />

      {firstOption && (
        <MessagesList messages={messages} scrollRef={scrollRef} />
      )}

      {!firstOption && <FirstOptionsGrid onSelect={handleFirstSelect} />}

      {firstOption && (
        <Box flex="0 0 auto">
          <SecondOptionsGrid
            selected={secondOption}
            onSelect={handleSecondSelect}
          />
          <Box mx={4} my={3}>
            <InputRow
              input={input}
              setInput={setInput}
              onSend={handleSend}
              loading={loading}
              disabled={!secondOption || loading}
            />
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ChatBox;
