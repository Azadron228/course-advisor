'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useTranslations } from 'next-intl';

const MarkdownComponents = {
  code({ node, inline, className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className || '');
    return !inline && match ? (
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={match[1]}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    ) : (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function LessonSidebarChat() {
  const t = useTranslations('Plan');
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
            content: t('tutorWelcomeMessage', { text }) 
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
          <h3 className="font-bold text-sm">{t('lessonTutor')}</h3>
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-3 opacity-50">
            <Bot className="w-10 h-10 text-muted" />
            <p className="text-sm">{t('askAnythingAboutLesson')}</p>
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              <button onClick={() => sendMessage(t('summarizeConcept'))} className="text-xs bg-surface border border-border px-3 py-1.5 rounded-full hover:bg-muted/10 transition-colors">{t('summarize')}</button>
              <button onClick={() => sendMessage(t('explainMainConcept'))} className="text-xs bg-surface border border-border px-3 py-1.5 rounded-full hover:bg-muted/10 transition-colors">{t('explainConcepts')}</button>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={cn("flex gap-3 text-sm", m.role === 'user' ? "flex-row-reverse" : "")}>
            <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm", m.role === 'user' ? "bg-primary text-white" : "bg-surface border border-border text-primary")}>
              {m.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className={cn("p-3 rounded-xl max-w-[80%] shadow-sm", m.role === 'user' ? "bg-primary text-white rounded-tr-none" : "bg-surface border border-border rounded-tl-none")}>
              <div className={cn(
                "prose prose-sm max-w-none prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent",
                m.role === 'user' ? "prose-invert text-white" : "dark:prose-invert text-foreground"
              )}>
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>
                  {m.content}
                </ReactMarkdown>
              </div>
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
            placeholder={t('askTutorPlaceholder')}
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
