'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function LessonSidebarChat({ lessonId, lessonContent }: { lessonId: string, lessonContent?: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
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

  const sendMessage = async (text: string) => {
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setIsSending(true);
    setInput('');

    try {
      // Mocked endpoint behavior since we haven't built the AI proxy route for it yet
      // In real implementation this would go to a `/api/chat` with lesson context
      setTimeout(() => {
        setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: `I'm your AI tutor anchored to this lesson. You asked: "${text}". Here is my helpful response based on the lesson text.` 
        }]);
        setIsSending(false);
      }, 1000);
    } catch (e) {
      console.error(e);
      setIsSending(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isSending) {
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden border-l border-border bg-surface/50">
      <div className="p-4 border-b border-border bg-background flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-primary" />
          <h3 className="font-bold text-sm">Lesson Tutor</h3>
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-3 opacity-50">
            <Bot className="w-10 h-10 text-muted" />
            <p className="text-sm">Ask me anything about this lesson.</p>
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              <button onClick={() => sendMessage("Summarize this section")} className="text-xs bg-surface border border-border px-3 py-1.5 rounded-full hover:bg-muted/10 transition-colors">Summarize</button>
              <button onClick={() => sendMessage("Explain the main concept")} className="text-xs bg-surface border border-border px-3 py-1.5 rounded-full hover:bg-muted/10 transition-colors">Explain Concepts</button>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={cn("flex gap-3 text-sm", m.role === 'user' ? "flex-row-reverse" : "")}>
            <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm", m.role === 'user' ? "bg-primary text-white" : "bg-surface border border-border text-primary")}>
              {m.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className={cn("p-3 rounded-xl max-w-[80%] shadow-sm", m.role === 'user' ? "bg-primary text-white rounded-tr-none" : "bg-surface border border-border rounded-tl-none")}>
              {m.content}
            </div>
          </div>
        ))}
        {isSending && (
           <div className="flex gap-3 text-sm">
             <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-surface border border-border text-primary shadow-sm">
                <Loader2 size={14} className="animate-spin" />
             </div>
           </div>
        )}
      </div>

      <div className="p-4 border-t border-border bg-background">
        <form onSubmit={handleSubmit} className="flex items-center gap-2 bg-input border border-border rounded-xl p-2 focus-within:border-primary/50 transition-colors shadow-sm">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the lesson..."
            className="flex-1 bg-transparent text-sm outline-none px-2"
          />
          <button type="submit" disabled={!input.trim() || isSending} className="p-2 bg-primary text-white rounded-lg disabled:opacity-50 transition-opacity shadow-md">
            {isSending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          </button>
        </form>
      </div>
    </div>
  );
}
