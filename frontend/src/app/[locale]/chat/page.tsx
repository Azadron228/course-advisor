'use client';

import { ChatWindow } from '@/components/features/chat-window';

export default function ChatPage() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1">
        <ChatWindow />
      </div>
    </div>
  );
}
