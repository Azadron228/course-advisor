'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { useChat } from '@/hooks/use-chat';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';

export function ChatWindow() {
  const tChat = useTranslations('Chat');
  const tCommon = useTranslations('Common');
  const { 
    messages, 
    sessions, 
    currentSessionId, 
    isSending, 
    isClearing, 
    sendMessage, 
    clearHistory, 
    switchSession 
  } = useChat();
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isSending) {
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] w-full bg-surface rounded-2xl shadow-xl shadow-primary/5 border border-border overflow-hidden">
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-background to-primary/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="p-2.5 rounded-xl bg-primary text-white shadow-lg shadow-primary/20">
                <Bot size={22} />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-green-500 border-2 border-background rounded-full"></div>
            </div>
            <div className="min-w-0">
              <h2 className="font-bold text-foreground tracking-tight flex items-center gap-2 truncate">
                <span className="truncate">{currentSessionId ? sessions.find(s => s.id === currentSessionId)?.title : tChat('title')}</span>
              </h2>
              <p className="text-xs text-primary/70 font-medium truncate">{tChat('companion')}</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-6 bg-background/50"
        >
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-12">
              <div className="p-4 rounded-full bg-primary/10 text-primary animate-bounce">
                <Bot size={40} />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-foreground">{tChat('howCanIHelp')}</h3>
                <p className="text-sm text-muted max-w-xs mx-auto">
                  {tChat('intro')}
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4 w-full max-w-md mx-auto">
                {[
                  tChat('suggestPython'),
                  tChat('suggestWebDev'),
                  tChat('suggestPlan'),
                  tChat('suggestDataScience')
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => sendMessage(suggestion)}
                    className="px-4 py-3 text-xs font-medium text-primary bg-surface border border-border rounded-xl hover:bg-primary/10 hover:border-primary/50 hover:shadow-sm transition-all text-left"
                  >
                    &quot;{suggestion}&quot;
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, index) => {
            // Skip rendering if it's an empty assistant message placeholder while sending
            const isLast = index === messages.length - 1;
            const isStreamingEmpty = isSending && isLast && message.role === 'assistant' && !message.content;
            
            if (isStreamingEmpty) return null;

            return (
              <div
                key={index}
                className={cn(
                  "flex w-full gap-4 items-start animate-in fade-in slide-in-from-bottom-2 duration-300",
                  message.role === 'user' ? "flex-row-reverse" : "flex-row"
                )}
              >
                <div className={cn(
                  "flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center shadow-sm",
                  message.role === 'user' 
                    ? "bg-primary text-white" 
                    : "bg-surface border border-border text-primary"
                )}>
                  {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                </div>
                
                <div className={cn(
                  "max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm relative",
                  message.role === 'user' 
                    ? "bg-primary text-white rounded-tr-none" 
                    : "bg-surface text-foreground rounded-tl-none"
                )}>
                  {message.role === 'assistant' && (
                    <>
                      <div className="absolute inset-0 rounded-2xl rounded-tl-none p-[1px] bg-gradient-to-br from-primary/30 via-secondary/20 to-primary/30 -z-10" />
                      <div className="absolute inset-[1px] rounded-[15px] rounded-tl-none bg-surface -z-10" />
                      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />
                    </>
                  )}
                  <div className="relative z-10 whitespace-pre-wrap">{message.content}</div>
                </div>
              </div>
            );
          })}

          {isSending && (
            messages.length === 0 || 
            messages[messages.length - 1].role !== 'assistant' || 
            !messages[messages.length - 1].content
          ) && (
            <div className="flex w-full gap-4 items-start">
              <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-surface border border-border flex items-center justify-center text-primary">
                <Bot size={18} />
              </div>
              <div className="max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl bg-surface rounded-tl-none shadow-sm relative overflow-hidden">
                <div className="absolute inset-0 rounded-2xl rounded-tl-none p-[1px] bg-gradient-to-br from-primary/20 via-secondary/10 to-primary/20 -z-10 animate-pulse" />
                <div className="absolute inset-[1px] rounded-[15px] rounded-tl-none bg-surface -z-10" />
                <div className="relative z-10 flex items-center gap-3 text-primary/70">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-xs font-medium animate-pulse">{tCommon('thinking')}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 sm:p-6 bg-surface border-t border-border">
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative flex items-center bg-input rounded-xl border border-border shadow-sm focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/10 transition-all overflow-hidden">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={tChat('placeholder')}
                className="flex-1 px-5 py-4 bg-transparent outline-none text-sm text-foreground placeholder:text-muted"
              />
              <div className="flex items-center gap-2 pr-3">
                <button
                  type="submit"
                  disabled={!input.trim() || isSending}
                  className={cn(
                    "p-2.5 rounded-lg transition-all duration-300 flex items-center justify-center",
                    input.trim() && !isSending
                      ? "bg-primary text-white shadow-md shadow-primary/20 hover:bg-primary/90"
                      : "bg-muted/20 text-muted/50 cursor-not-allowed"
                  )}
                >
                  {isSending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
