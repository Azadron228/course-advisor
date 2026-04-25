'use client';

import { ChatWindow } from '@/components/features/chat-window';

export default function ChatPage() {
  return (
    <div className="flex flex-col h-full">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">AI Advisor</h1>
        <p className="text-gray-500 text-sm">Get personalized advice and course recommendations</p>
      </div>
      
      <div className="flex-1 min-h-[500px]">
        <ChatWindow />
      </div>
    </div>
  );
}
