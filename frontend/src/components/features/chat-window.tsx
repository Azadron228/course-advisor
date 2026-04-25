'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { useChat } from '@/hooks/use-chat';
import { cn } from '@/lib/utils';

export function ChatWindow() {
  const { messages, isSending, sendMessage } = useChat();
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
    <div className="flex flex-col h-[calc(100vh-8rem)] w-full max-w-5xl mx-auto bg-white rounded-2xl shadow-xl shadow-indigo-500/5 border border-indigo-100 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-indigo-50 bg-gradient-to-r from-white to-indigo-50/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="p-2.5 rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-200">
              <Bot size={22} />
            </div>
            <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-green-500 border-2 border-white rounded-full"></div>
          </div>
          <div>
            <h2 className="font-bold text-gray-900 tracking-tight flex items-center gap-2">
              EduPath AI Advisor
              <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-100 text-indigo-700 font-bold uppercase tracking-wider">Beta</span>
            </h2>
            <p className="text-xs text-indigo-600/70 font-medium">Your personalized learning companion</p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-indigo-100 text-[11px] font-semibold text-indigo-600 shadow-sm">
          <Sparkles size={12} className="text-indigo-500" />
          AI Powered
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-12">
            <div className="p-4 rounded-full bg-indigo-50 text-indigo-600 animate-bounce">
              <Bot size={40} />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-gray-900">How can I help you today?</h3>
              <p className="text-sm text-gray-500 max-w-xs mx-auto">
                Ask me about course recommendations, skill development, or how to reach your career goals.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4 w-full max-w-md mx-auto">
              {[
                'Recommend Python courses', 
                'What skills for Web Dev?', 
                'Explain my learning plan', 
                'How to start in Data Science?'
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => sendMessage(suggestion)}
                  className="px-4 py-3 text-xs font-medium text-indigo-600 bg-white border border-indigo-100 rounded-xl hover:bg-indigo-50 hover:border-indigo-200 hover:shadow-sm transition-all text-left"
                >
                  "{suggestion}"
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
                : "bg-white border border-indigo-100 text-indigo-600"
            )}>
              {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
            </div>
            
            <div className={cn(
              "max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm relative",
              message.role === 'user' 
                ? "bg-indigo-600 text-white rounded-tr-none" 
                : "bg-white rounded-tl-none"
            )}>
              {message.role === 'assistant' && (
                <>
                  <div className="absolute inset-0 rounded-2xl rounded-tl-none p-[1.5px] bg-gradient-to-br from-indigo-300 via-purple-200 to-indigo-300 -z-10" />
                  <div className="absolute inset-[1.5px] rounded-[14px] rounded-tl-none bg-white -z-10" />
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-50/50 via-transparent to-purple-50/30 pointer-events-none" />
                </>
              )}
              <div className="relative z-10 whitespace-pre-wrap">{message.content}</div>
            </div>
          </div>
        ))}

        {isSending && (
          <div className="flex w-full gap-4 items-start">
            <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-white border border-indigo-100 flex items-center justify-center text-indigo-600">
              <Bot size={18} />
            </div>
            <div className="max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl bg-white rounded-tl-none shadow-sm relative overflow-hidden">
              <div className="absolute inset-0 rounded-2xl rounded-tl-none p-[1.5px] bg-gradient-to-br from-indigo-200 via-purple-100 to-indigo-200 -z-10 animate-pulse" />
              <div className="absolute inset-[1.5px] rounded-[14px] rounded-tl-none bg-white -z-10" />
              <div className="relative z-10 flex items-center gap-3 text-indigo-400">
                <div className="flex gap-1.5">
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></span>
                </div>
                <span className="text-xs font-medium animate-pulse">Advisor is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 sm:p-6 bg-white border-t border-indigo-50">
        <form onSubmit={handleSubmit} className="relative">
          <div className="relative flex items-center bg-white rounded-xl border border-indigo-100 shadow-sm focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 transition-all overflow-hidden">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your advisor anything..."
              className="flex-1 px-5 py-4 bg-transparent outline-none text-sm text-gray-800 placeholder:text-gray-400"
            />
            <div className="flex items-center gap-2 pr-3">
              <button
                type="submit"
                disabled={!input.trim() || isSending}
                className={cn(
                  "p-2.5 rounded-lg transition-all duration-300 flex items-center justify-center",
                  input.trim() && !isSending
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700"
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                )}
              >
                {isSending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
              </button>
            </div>
          </div>
        </form>
        <p className="mt-3 text-[10px] text-center text-gray-400 font-medium">
          AI-powered suggestions based on your profile and goals.
        </p>
      </div>
    </div>
  );
}
