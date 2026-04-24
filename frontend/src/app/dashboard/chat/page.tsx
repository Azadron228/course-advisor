'use client';
import React, { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface Msg {
  role: string;
  content: string;
}

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [msgs, setMsgs] = useState<Msg[]>([]);

  useEffect(() => {
    api.get('/api/v1/recommendations/chat/history').then(res => setMsgs(res.data)).catch(console.error);
  }, []);

  const send = async () => {
    if (!input) return;
    const userMsg = { role: 'user', content: input };
    setMsgs([...msgs, userMsg]);
    setInput('');
    try {
      const res = await api.post('/api/v1/recommendations/chat', { message: userMsg.content });
      setMsgs(res.data.history);
    } catch (e) {}
  };

  return (
    <div className="p-8 max-w-4xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      <h1 className="text-4xl font-bold mb-8">AI Advisor</h1>
      
      <Card className="flex-1 overflow-y-auto mb-4 flex flex-col gap-4 p-8 bg-gradient-to-b from-white to-[#fcfcff]">
        {msgs.map((m, i) => (
          <div key={i} className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-[var(--primary)] text-white self-end rounded-tr-sm' : 'bg-[var(--border-light)] text-[var(--text-main)] self-start rounded-tl-sm'}`}>
            {m.content}
          </div>
        ))}
      </Card>

      <div className="flex gap-4">
        <input 
          className="flex-1 rounded-lg border border-[var(--border-light)] p-4 focus:outline-none focus:border-[var(--primary)] bg-[var(--border-light)] focus:bg-white transition-colors"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about your learning journey..."
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <Button onClick={send} className="px-8 text-lg">Send</Button>
      </div>
    </div>
  );
}
