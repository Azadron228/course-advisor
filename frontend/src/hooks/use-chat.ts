'use client';

import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export function useChat() {
  const queryClient = useQueryClient();
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { data: historyMessages = [], isLoading: isLoadingHistory } = useQuery<Message[]>({
    queryKey: ['chat-history'],
    queryFn: async () => {
      try {
        return await apiClient.get<Message[]>('/recommendations/chat/history');
      } catch (error) {
        console.error('Failed to fetch chat history:', error);
        return [];
      }
    },
  });

  // Local state for immediate UI updates (including streaming)
  const [localMessages, setLocalMessages] = useState<Message[]>([]);

  // Combined messages: history + new local messages
  const messages = [...historyMessages, ...localMessages];

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isSending) return;

    setIsSending(true);
    setError(null);

    // 1. Add user message to local state immediately
    const userMessage: Message = { role: 'user', content };
    setLocalMessages(prev => [...prev, userMessage]);

    try {
      // 2. Prepare assistant message placeholder
      let assistantContent = '';
      setLocalMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // 3. Start streaming
      await apiClient.stream(
        '/recommendations/chat',
        { message: content },
        (chunk) => {
          assistantContent += chunk;
          // Update the LAST message in localMessages (which is the assistant's)
          setLocalMessages(prev => {
            const next = [...prev];
            if (next.length > 0) {
              next[next.length - 1] = { 
                role: 'assistant', 
                content: assistantContent 
              };
            }
            return next;
          });
        }
      );

      // 4. On finish, clear local state and invalidate query to fetch official history
      queryClient.invalidateQueries({ queryKey: ['chat-history'] });
      setLocalMessages([]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError(err instanceof Error ? err : new Error(err.message || 'Failed to send message'));
    } finally {
      setIsSending(false);
    }
  }, [isSending, queryClient]);

  return {
    messages,
    isLoading: isLoadingHistory,
    isSending,
    sendMessage,
    error,
  };
}
