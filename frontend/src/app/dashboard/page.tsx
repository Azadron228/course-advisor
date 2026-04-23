'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import {
  RecommendationResponse,
  ChatMessage
} from '@/lib/types';
import {
  Zap,
  Loader2
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

// Sub-components
import { ChatSidebar } from './ChatSidebar';
import { WelcomeCard } from './WelcomeCard';
import { RoadmapView } from './RoadmapView';
import { formatError } from '@/lib/utils';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [difficulty, setDifficulty] = useState(0.5);
  const [workload, setWorkload] = useState(0.5);
  const [interests, setInterests] = useState('Machine Learning, Web Development');
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState('');
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const resp = await api.get('/api/v1/recommendations/chat/history');
        setChatMessages(resp.data);
      } catch (err) {
        console.error('History fetch error:', err);
      }
    };
    fetchHistory();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
  };

  const generateRecommendations = async () => {
    if (!file) {
      setError('Please upload your transcript HTML file.');
      return;
    }
    setIsLoading(true);
    setError('');

    try {
      // 1. Parse transcript
      const formData = new FormData();
      formData.append('file', file);
      const parseResp = await api.post('/api/v1/parser/parse-transcript', formData);
      const transcriptEntries = parseResp.data;

      // 2. Get recommendations
      const interestList = interests.split(',').map(s => s.trim()).filter(Boolean);
      const recResp = await api.post('/api/v1/recommendations/recommend', {
        student: {
          id: user?.email || 'user',
          name: user?.full_name || user?.email || 'User',
          transcript: transcriptEntries,
          current_skills: interestList
        },
        preference: {
          interest_tags: interestList,
          target_difficulty: difficulty,
          max_workload: workload
        }
      }, { timeout: 120000 });

      setResults(recResp.data);
    } catch (err: unknown) {
      setError(formatError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setChatInput('');
    // Optimistic update
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    
    try {
      const resp = await api.post('/api/v1/recommendations/chat', { message: userMsg });
      setChatMessages(resp.data.history);
    } catch (err) {
      console.error('Chat error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <ChatSidebar 
        user={user}
        logout={logout}
        difficulty={difficulty}
        setDifficulty={setDifficulty}
        workload={workload}
        setWorkload={setWorkload}
        interests={interests}
        setInterests={setInterests}
        chatMessages={chatMessages}
        chatInput={chatInput}
        setChatInput={setChatInput}
        handleSendMessage={handleSendMessage}
        isSettingsOpen={isSettingsOpen}
        setIsSettingsOpen={setIsSettingsOpen}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-10 space-y-10">
        <AnimatePresence mode="wait">
          {!results && !isLoading ? (
            <motion.div
              key="welcome"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="h-full flex flex-col items-center justify-center"
            >
              <WelcomeCard 
                file={file}
                handleFileChange={handleFileChange}
                generateRecommendations={generateRecommendations}
                isLoading={isLoading}
                error={error}
              />
            </motion.div>
          ) : isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="h-full flex flex-col items-center justify-center space-y-4"
            >
              <div className="relative">
                <Loader2 size={48} className="text-blue-600 animate-spin" />
                <Zap size={24} className="text-yellow-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
              </div>
              <p className="text-slate-500 font-medium animate-pulse">Our AI is analyzing your academic DNA...</p>
            </motion.div>
          ) : (
            results && <RoadmapView results={results} difficulty={difficulty} />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
