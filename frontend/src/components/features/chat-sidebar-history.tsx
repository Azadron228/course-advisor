'use client';

import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { useChat } from '@/hooks/use-chat';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';

interface ChatSidebarHistoryProps {
  isCollapsed?: boolean;
}

export function ChatSidebarHistory({ isCollapsed }: ChatSidebarHistoryProps) {
  const tChat = useTranslations('Chat');
  const { 
    sessions, 
    currentSessionId, 
    clearHistory, 
    switchSession 
  } = useChat();

  if (isCollapsed) return null;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-3 mb-2">
        <button
          onClick={() => switchSession(null)}
          className="w-full py-2 px-4 bg-primary/10 border border-primary/20 rounded-xl text-xs font-bold text-primary shadow-sm hover:bg-primary/20 transition-all flex items-center justify-center gap-2"
        >
          <Plus size={14} />
          {tChat('newChat')}
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto px-3 space-y-1 custom-scrollbar">
        <p className="px-3 text-[10px] font-bold text-muted uppercase tracking-wider mb-2 mt-4">
          {tChat('recentChats')}
        </p>
        
        {sessions.map((session) => (
          <div key={session.id} className="relative group/session">
            <button
              onClick={() => switchSession(session.id)}
              className={cn(
                "w-full p-2.5 rounded-xl text-left text-xs transition-all flex items-start gap-3 group",
                currentSessionId === session.id
                  ? "bg-primary text-white font-semibold shadow-md shadow-primary/20"
                  : "text-muted hover:bg-muted/10 hover:text-foreground"
              )}
            >
              <MessageSquare size={14} className={cn(
                "mt-0.5 shrink-0",
                currentSessionId === session.id ? "text-white" : "text-muted group-hover:text-primary"
              )} />
              <div className="truncate pr-6">
                <div className="truncate font-medium">{session.title}</div>
                <div className={cn(
                  "text-[9px] font-normal mt-0.5",
                  currentSessionId === session.id ? "text-white/70" : "text-muted"
                )}>
                  {new Date(session.updated_at).toLocaleDateString()}
                </div>
              </div>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm(tChat('clearHistory') + '?')) {
                  clearHistory(session.id);
                }
              }}
              className={cn(
                "absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-md opacity-0 group-hover/session:opacity-100 transition-all z-10",
                currentSessionId === session.id 
                  ? "text-white/80 hover:text-white hover:bg-white/10" 
                  : "text-muted hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20"
              )}
              title={tChat('clearHistory')}
            >
              <Trash2 size={12} />
            </button>
          </div>
        ))}
        
        {sessions.length === 0 && (
          <div className="text-center py-8 px-4">
            <p className="text-[11px] text-muted font-medium">{tChat('noHistory')}</p>
          </div>
        )}
      </div>
    </div>
  );
}
