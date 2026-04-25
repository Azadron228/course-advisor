'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatResponse {
  response: string;
  history: Message[];
}

export function useChat() {
  const queryClient = useQueryClient();

  const { data: messages = [], isLoading: isLoadingHistory } = useQuery<Message[]>({
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

  const mutation = useMutation<ChatResponse, Error, string>({
    mutationFn: (message: string) =>
      apiClient.post<ChatResponse>('/recommendations/chat', { message }),
    onMutate: async (newMessage) => {
      // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ queryKey: ['chat-history'] });

      // Snapshot the previous value
      const previousMessages = queryClient.getQueryData<Message[]>(['chat-history']);

      // Optimistically update to the new value
      queryClient.setQueryData(['chat-history'], (old: Message[] = []) => [
        ...old,
        { role: 'user', content: newMessage },
      ]);

      // Return a context object with the snapshotted value
      return { previousMessages };
    },
    onError: (err, newMessage, context) => {
      queryClient.setQueryData(['chat-history'], context?.previousMessages);
    },
    onSuccess: (data) => {
      // Update with the actual history from the server
      queryClient.setQueryData(['chat-history'], data.history);
    },
    onSettled: () => {
      // Always refetch after error or success to ensure we're in sync
      queryClient.invalidateQueries({ queryKey: ['chat-history'] });
    },
  });

  const sendMessage = (message: string) => {
    if (!message.trim() || mutation.isPending) return;
    mutation.mutate(message);
  };

  return {
    messages,
    isLoading: isLoadingHistory,
    isSending: mutation.isPending,
    sendMessage,
    error: mutation.error,
  };
}
