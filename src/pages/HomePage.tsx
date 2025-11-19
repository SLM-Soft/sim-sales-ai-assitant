import React from 'react';
import ChatBox from '../components/ChatBox';

const HomePage: React.FC = () => {
  return (
    <div
      className="min-h-screen w-full flex justify-center px-4 py-6"
      style={{ background: 'var(--color-bg)', color: 'var(--color-text)' }}
    >
      <ChatBox />
    </div>
  );
};

export default HomePage;
