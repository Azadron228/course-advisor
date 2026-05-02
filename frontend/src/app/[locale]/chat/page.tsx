'use client';

import { ChatWindow } from '@/components/features/chat-window';
import { useTranslations } from 'next-intl';

export default function ChatPage() {
  const t = useTranslations('Chat');

  return (
    <div className="flex flex-col h-full">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{t('title')}</h1>
        <p className="text-gray-500 dark:text-slate-400 text-sm">{t('subtitle')}</p>
      </div>
      
      <div className="flex-1 min-h-[500px]">
        <ChatWindow />
      </div>
    </div>
  );
}
