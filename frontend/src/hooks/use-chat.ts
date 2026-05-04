'use client';

import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  created_at?: string;
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export function useChat() {
  const queryClient = useQueryClient();
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch all sessions
  const { data: sessions = [], isLoading: isLoadingSessions } = useQuery<ChatSession[]>({
    queryKey: ['chat-sessions'],
    queryFn: async () => {
      try {
        return await apiClient.get<ChatSession[]>('/recommendations/chat/sessions');
      } catch (error) {
        console.error('Failed to fetch chat sessions:', error);
        return [];
      }
    },
  });

  // Fetch history for current session
  const { data: historyMessages = [], isLoading: isLoadingHistory } = useQuery<Message[]>({
    queryKey: ['chat-history', currentSessionId],
    queryFn: async () => {
      if (!currentSessionId) return [];
      try {
        const detail = await apiClient.get<{ messages: Message[] }>(`/recommendations/chat/sessions/${currentSessionId}`);
        return detail.messages;
      } catch (error) {
        console.error('Failed to fetch chat history:', error);
        return [];
      }
    },
    enabled: !!currentSessionId,
  });

  // Local state for immediate UI updates (including streaming)
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const [isClearing, setIsClearing] = useState(false);

  // Combined messages: history + new local messages
  const messages = [...historyMessages, ...localMessages];

  const clearHistory = useCallback(async (chatId: number) => {
    setIsClearing(true);
    try {
      const url = `/recommendations/chat/history?chat_id=${chatId}`;
      await apiClient.delete(url);
      
      // Invalidate the sessions list
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] });
      
      // If we cleared the current session, clean up local state
      if (currentSessionId === chatId) {
        queryClient.setQueryData(['chat-history', chatId], []);
        setLocalMessages([]);
        setCurrentSessionId(null);
      }
    } catch (err) {
      console.error('Failed to clear chat history:', err);
      throw err;
    } finally {
      setIsClearing(false);
    }
  }, [queryClient, currentSessionId]);

  const switchSession = useCallback((sessionId: number | null) => {
    setCurrentSessionId(sessionId);
    setLocalMessages([]);
  }, []);

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
        { message: content, session_id: currentSessionId },
        (chunk) => {
          // Check if chunk is a JSON object containing session_id (some backends might send it as first chunk)
          // But our backend sends it in the final JSON response for non-streaming, 
          // or we might need to handle it differently for streaming.
          // In our current backend, we don't send session_id in the stream.
          
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

      // 4. On finish, invalidate queries to fetch official history and update session list
      await queryClient.invalidateQueries({ queryKey: ['chat-sessions'] });
      
      // If it was a new session, we need to find it and set it as current
      if (!currentSessionId) {
        const updatedSessions = await apiClient.get<ChatSession[]>('/recommendations/chat/sessions');
        if (updatedSessions.length > 0) {
          setCurrentSessionId(updatedSessions[0].id);
        }
      } else {
        await queryClient.invalidateQueries({ queryKey: ['chat-history', currentSessionId] });
      }
      
      setLocalMessages([]);
    } catch (err: unknown) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : (err as { message?: string })?.message || 'Failed to send message';
      setError(err instanceof Error ? err : new Error(errorMessage));
    } finally {
      setIsSending(false);
    }
  }, [isSending, queryClient, currentSessionId]);

  return {
    messages,
    sessions,
    currentSessionId,
    isLoading: isLoadingHistory || isLoadingSessions,
    isSending,
    isClearing,
    sendMessage,
    clearHistory,
    switchSession,
    error,
  };
}
