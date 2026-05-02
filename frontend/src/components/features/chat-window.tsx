'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Trash2, Plus, MessageSquare } from 'lucide-react';
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
    <div className="flex h-[calc(100vh-8rem)] w-full max-w-6xl mx-auto bg-surface rounded-2xl shadow-xl shadow-indigo-500/5 border border-indigo-100 dark:border-slate-800 overflow-hidden">
      {/* Sidebar - Chat History */}
      <div className="w-64 border-r border-indigo-50 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex flex-col hidden md:flex">
        <div className="p-4 border-b border-indigo-50 dark:border-slate-800">
          <button
            onClick={() => switchSession(null)}
            className="w-full py-2.5 px-4 bg-surface dark:bg-slate-800 border border-indigo-100 dark:border-slate-700 rounded-xl text-sm font-bold text-indigo-600 dark:text-indigo-400 shadow-sm hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-500 transition-all flex items-center justify-center gap-2"
          >
            <Plus size={18} />
            {tChat('newChat')}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => switchSession(session.id)}
              className={cn(
                "w-full p-3 rounded-xl text-left text-sm transition-all flex items-start gap-3 group",
                currentSessionId === session.id
                  ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 font-semibold border border-indigo-100 dark:border-indigo-800 shadow-sm"
                  : "text-gray-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 hover:shadow-sm hover:border-indigo-50 dark:hover:border-slate-700 border border-transparent"
              )}
            >
              <MessageSquare size={16} className={cn(
                "mt-0.5 shrink-0",
                currentSessionId === session.id ? "text-indigo-600 dark:text-indigo-400" : "text-gray-400 dark:text-slate-500 group-hover:text-indigo-400"
              )} />
              <div className="truncate">
                <div className="truncate">{session.title}</div>
                <div className="text-[10px] text-gray-400 dark:text-slate-500 font-normal mt-0.5">
                  {new Date(session.updated_at).toLocaleDateString()}
                </div>
              </div>
            </button>
          ))}
          {sessions.length === 0 && (
            <div className="text-center py-8 px-4">
              <p className="text-xs text-gray-400 dark:text-slate-500 font-medium">{tChat('noHistory')}</p>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="px-6 py-4 border-b border-indigo-50 dark:border-slate-800 bg-gradient-to-r from-white to-indigo-50/30 dark:from-slate-900 dark:to-indigo-950/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="p-2.5 rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-200 dark:shadow-indigo-900/50">
                <Bot size={22} />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-green-500 border-2 border-white dark:border-slate-900 rounded-full"></div>
            </div>
            <div className="min-w-0">
              <h2 className="font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2 truncate">
                <span className="truncate">{currentSessionId ? sessions.find(s => s.id === currentSessionId)?.title : tChat('title')}</span>
                <span className="shrink-0 px-1.5 py-0.5 rounded text-[10px] bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-400 font-bold uppercase tracking-wider">{tCommon('beta')}</span>
              </h2>
              <p className="text-xs text-indigo-600/70 dark:text-indigo-400/70 font-medium truncate">{tChat('companion')}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface dark:bg-slate-800 border border-indigo-100 dark:border-slate-700 text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 shadow-sm">
              <Sparkles size={12} className="text-indigo-500" />
              {tCommon('aiPowered')}
            </div>
            
            <button
              onClick={() => {
                if (confirm(tChat('clearHistory') + '?')) {
                  clearHistory();
                }
              }}
              disabled={(sessions.length === 0 && messages.length === 0) || isClearing}
              className={cn(
                "p-2 rounded-lg transition-all flex items-center gap-2 text-xs font-medium",
                (sessions.length === 0 && messages.length === 0) || isClearing
                  ? "text-gray-300 dark:text-slate-600 cursor-not-allowed"
                  : "text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400"
              )}
              title={tChat('clearHistory')}
            >
              {isClearing ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
              <span className="hidden lg:inline">{tChat('clearHistory')}</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30 dark:bg-slate-950/30"
        >
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-12">
              <div className="p-4 rounded-full bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 animate-bounce">
                <Bot size={40} />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">{tChat('howCanIHelp')}</h3>
                <p className="text-sm text-gray-500 dark:text-slate-400 max-w-xs mx-auto">
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
                    className="px-4 py-3 text-xs font-medium text-indigo-600 dark:text-indigo-400 bg-surface dark:bg-slate-800 border border-indigo-100 dark:border-slate-700 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:border-indigo-200 dark:hover:border-indigo-500 hover:shadow-sm transition-all text-left"
                  >
                    &quot;{suggestion}&quot;
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, index) => (
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
                  ? "bg-indigo-600 text-white" 
                  : "bg-surface dark:bg-slate-800 border border-indigo-100 dark:border-slate-700 text-indigo-600 dark:text-indigo-400"
              )}>
                {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              
              <div className={cn(
                "max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm relative",
                message.role === 'user' 
                  ? "bg-indigo-600 text-white rounded-tr-none" 
                  : "bg-surface dark:bg-slate-800 dark:text-slate-200 rounded-tl-none"
              )}>
                {message.role === 'assistant' && (
                  <>
                    <div className="absolute inset-0 rounded-2xl rounded-tl-none p-[1.5px] bg-gradient-to-br from-indigo-300 via-purple-200 to-indigo-300 dark:from-indigo-700 dark:via-purple-800 dark:to-indigo-700 -z-10" />
                    <div className="absolute inset-[1.5px] rounded-[14px] rounded-tl-none bg-surface dark:bg-slate-800 -z-10" />
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-50/50 via-transparent to-purple-50/30 dark:from-indigo-900/20 dark:to-purple-900/20 pointer-events-none" />
                  </>
                )}
                <div className="relative z-10 whitespace-pre-wrap">{message.content}</div>
              </div>
            </div>
          ))}

          {isSending && (
            <div className="flex w-full gap-4 items-start">
              <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-surface dark:bg-slate-800 border border-indigo-100 dark:border-slate-700 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                <Bot size={18} />
              </div>
              <div className="max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl bg-surface dark:bg-slate-800 rounded-tl-none shadow-sm relative overflow-hidden">
                <div className="absolute inset-0 rounded-2xl rounded-tl-none p-[1.5px] bg-gradient-to-br from-indigo-200 via-purple-100 to-indigo-200 dark:from-indigo-800 dark:via-purple-900 dark:to-indigo-800 -z-10 animate-pulse" />
                <div className="absolute inset-[1.5px] rounded-[14px] rounded-tl-none bg-surface dark:bg-slate-800 -z-10" />
                <div className="relative z-10 flex items-center gap-3 text-indigo-400 dark:text-indigo-300">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 bg-indigo-400 dark:bg-indigo-300 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-2 h-2 bg-indigo-400 dark:bg-indigo-300 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-2 h-2 bg-indigo-400 dark:bg-indigo-300 rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-xs font-medium animate-pulse">{tCommon('thinking')}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 sm:p-6 bg-surface dark:bg-slate-900 border-t border-indigo-50 dark:border-slate-800">
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative flex items-center bg-surface dark:bg-slate-800 rounded-xl border border-indigo-100 dark:border-slate-700 shadow-sm focus-within:border-indigo-500 dark:focus-within:border-indigo-400 focus-within:ring-4 focus-within:ring-indigo-500/10 dark:focus-within:ring-indigo-400/10 transition-all overflow-hidden">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={tChat('placeholder')}
                className="flex-1 px-5 py-4 bg-transparent outline-none text-sm text-gray-800 dark:text-slate-200 placeholder:text-gray-400 dark:placeholder:text-slate-500"
              />
              <div className="flex items-center gap-2 pr-3">
                <button
                  type="submit"
                  disabled={!input.trim() || isSending}
                  className={cn(
                    "p-2.5 rounded-lg transition-all duration-300 flex items-center justify-center",
                    input.trim() && !isSending
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-200 dark:shadow-indigo-900/50 hover:bg-indigo-700 dark:hover:bg-indigo-500"
                      : "bg-gray-100 dark:bg-slate-700 text-gray-400 dark:text-slate-500 cursor-not-allowed"
                  )}
                >
                  {isSending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                </button>
              </div>
            </div>
          </form>
          <p className="mt-3 text-[10px] text-center text-gray-400 dark:text-slate-500 font-medium">
            {tChat('aiPoweredNote')}
          </p>
        </div>
      </div>
    </div>
  );
}
