import React from 'react';
import ChatBoxNew from '../components/ChatBoxNew';

const HomePage: React.FC = () => {
  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-xl h-3/4">
        <ChatBoxNew />
      </div>
    </div>
  );
};

export default HomePage;