'use client';

import React from 'react';
import { ChatMessage } from '@/lib/types';
import {
  GraduationCap,
  LogOut,
  Search,
  Settings,
  Send,
  MessageSquare,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';

interface ChatSidebarProps {
  user: any;
  logout: () => void;
  difficulty: number;
  setDifficulty: (v: number) => void;
  workload: number;
  setWorkload: (v: number) => void;
  interests: string;
  setInterests: (v: string) => void;
  chatMessages: ChatMessage[];
  chatInput: string;
  setChatInput: (v: string) => void;
  handleSendMessage: () => void;
  isSettingsOpen: boolean;
  setIsSettingsOpen: (v: boolean) => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  user,
  logout,
  difficulty,
  setDifficulty,
  workload,
  setWorkload,
  interests,
  setInterests,
  chatMessages,
  chatInput,
  setChatInput,
  handleSendMessage,
  isSettingsOpen,
  setIsSettingsOpen
}) => {
  return (
    <aside className="w-96 bg-white border-r border-slate-200 flex flex-col sticky top-0 h-screen">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-white z-10">
        <div className="flex items-center gap-2 text-blue-600 font-bold text-lg">
          <GraduationCap size={24} />
          <span>AI Advisor Hub</span>
        </div>
        <button onClick={logout} className="text-slate-400 hover:text-red-500 transition-colors">
          <LogOut size={18} />
        </button>
      </div>

      {/* Collapsible Settings */}
      <div className="border-b border-slate-100">
        <button 
          onClick={() => setIsSettingsOpen(!isSettingsOpen)}
          className="w-full p-4 flex items-center justify-between text-slate-700 font-semibold hover:bg-slate-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Settings size={18} className="text-slate-400" />
            <span>Plan Settings</span>
          </div>
          {isSettingsOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
        
        <AnimatePresence>
          {isSettingsOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden bg-slate-50/50"
            >
              <div className="p-4 space-y-6">
                {user?.is_admin && (
                  <Link 
                    href="/admin"
                    className="flex items-center gap-2 p-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors text-sm"
                  >
                    <Settings size={14} />
                    <span>Admin Panel</span>
                  </Link>
                )}

                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-[10px] text-slate-500 uppercase font-bold tracking-wider">
                      <span>Difficulty</span>
                      <span>{difficulty.toFixed(1)}</span>
                    </div>
                    <input
                      type="range" min="0" max="1" step="0.1"
                      className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      value={difficulty}
                      onChange={(e) => setDifficulty(parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-[10px] text-slate-500 uppercase font-bold tracking-wider">
                      <span>Workload</span>
                      <span>{workload.toFixed(1)}</span>
                    </div>
                    <input
                      type="range" min="0" max="1" step="0.1"
                      className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      value={workload}
                      onChange={(e) => setWorkload(parseFloat(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] text-slate-500 uppercase font-bold tracking-wider flex items-center gap-1">
                    <Search size={10} /> Interests
                  </label>
                  <textarea
                    className="w-full p-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                    rows={2}
                    placeholder="e.g. ML, Web Dev..."
                    value={interests}
                    onChange={(e) => setInterests(e.target.value)}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30">
        {chatMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3 opacity-40">
            <MessageSquare size={32} className="text-slate-300" />
            <p className="text-sm text-slate-500">Ask me anything about your academic plan or courses!</p>
          </div>
        ) : (
          chatMessages.map((msg, i) => (
            <div 
              key={i} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-white border border-slate-100 text-slate-700 shadow-sm rounded-tl-none'
              }`}>
                {msg.content}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Chat Input */}
      <div className="p-4 border-t border-slate-100 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Type a message..."
            className="flex-1 p-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button 
            onClick={handleSendMessage}
            disabled={!chatInput.trim()}
            className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all disabled:opacity-50 shadow-sm"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </aside>
  );
};
