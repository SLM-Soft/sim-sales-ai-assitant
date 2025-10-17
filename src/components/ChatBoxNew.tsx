import React, { useEffect, useRef, useState } from 'react';
import { Box } from '@chakra-ui/react';
import ChatHeader from './ChatHeader';
import MessagesList from './MessagesList';
import FirstOptionsGrid from './FirstOptionsGrid';
import SecondOptionsGrid from './SecondOptionsGrid';
import InputRow from './InputRow';

const ChatBox: React.FC = () => {
  const [firstOption, setFirstOption] = useState<number | null>(null);
  const [secondOption, setSecondOption] = useState<number | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<
    { role: 'User' | 'Assistant'; content: string }[]
  >([]);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // автоскролл при добавлении сообщений
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages.length]);

  const handleFirstSelect = (opt: number) => {
    setFirstOption(opt);
    // можно добавить запись в messages, например:
    setMessages((m) => [
      ...m,
      { role: 'User', content: `Selected first option ${opt}` },
    ]);
  };

  const handleSecondSelect = (opt: number) => {
    setSecondOption(opt);
    setMessages((m) => [
      ...m,
      { role: 'User', content: `Selected second option ${opt}` },
    ]);
  };

  const handleSend = () => {
    // закомментирована оригинальная логика отправки (сеть)
    // sendMessage([...])...

    console.log({
      user: 'User',
      message: {
        firstOption,
        secondOption,
        input,
      },
    });

    // локально добавим сообщение в список диалога для наглядности:
    if (input.trim()) {
      setMessages((m) => [...m, { role: 'User', content: input.trim() }]);
      // имитация ответа ассистента (опционально)
      setMessages((m) => [
        ...m,
        { role: 'Assistant', content: 'Ответ (заглушка)' },
      ]);
    }

    setInput('');
  };

  return (
    <Box
      borderRadius="md"
      boxShadow="md"
      p={4}
      display="flex"
      flexDirection="column"
      height="full"
      minH="520px"
    >
      {/* Header всегда виден */}
      <ChatHeader backendOk={null} />

      {/* Основная область: сверху диалог, снизу — либо большая сетка (шаг1), либо маленькие карточки + input (шаг2) */}
      {/* Диалог всегда видим (MessagesList) */}
      {firstOption && (
        <MessagesList messages={messages} scrollRef={scrollRef} />
      )}

      {/* Шаг 1: 6 больших карточек (занимают оставшееся место) */}
      {!firstOption && <FirstOptionsGrid onSelect={handleFirstSelect} />}

      {/* Шаг 2: 4 маленькие карточки + поле ввода (поле disabled пока не выбран secondOption) */}
      {firstOption && (
        <Box mt={4} flex="0 0 auto">
          <SecondOptionsGrid
            selected={secondOption}
            onSelect={handleSecondSelect}
          />
          <Box mt={3}>
            <InputRow
              input={input}
              setInput={setInput}
              onSend={handleSend}
              loading={false}
              disabled={!secondOption} // <--- disabled пока не выбран secondOption
            />
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ChatBox;
