import React from 'react';
import ChatBox from '../components/ChatBox';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen w-full bg-neutral-800 flex justify-center px-4 py-6">
      <ChatBox />
    </div>
  );
};

export default HomePage;
