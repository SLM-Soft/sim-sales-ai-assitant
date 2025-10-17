import React from 'react';
import { type ChatMessage } from '../store/chatStore';

interface Props {
  message: ChatMessage;
}

const Message: React.FC<Props> = ({ message }) => {
  return (
    <div
      className={`p-2 my-1 rounded ${
        message.role === 'User'
          ? 'bg-blue-100 self-end'
          : 'bg-gray-200 self-start'
      }`}
    >
      <span>{message.content}</span>
    </div>
  );
};

export default Message;
