import { create } from 'zustand';

interface ChatState {
  currentSessionId: number | null;
  setCurrentSessionId: (id: number | null) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  currentSessionId: null,
  setCurrentSessionId: (id) => set({ currentSessionId: id }),
}));
