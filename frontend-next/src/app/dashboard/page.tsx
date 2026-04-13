'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import { 
  RecommendationResponse, 
  RecommendationResult, 
  SkillGapAnalysis, 
  LearningPathStep 
} from '@/lib/types';
import { Card, CardContent, CardHeader } from '@/components/ui-base';
import { 
  GraduationCap, 
  Upload, 
  LogOut, 
  Target, 
  Zap, 
  Map, 
  Search, 
  CheckCircle2, 
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [difficulty, setDifficulty] = useState(0.5);
  const [workload, setWorkload] = useState(0.5);
  const [interests, setInterests] = useState('Machine Learning, Web Development');
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState('');

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
      const parseResp = await api.post('/parse-transcript', formData);
      const transcriptEntries = parseResp.data;

      // 2. Get recommendations
      const interestList = interests.split(',').map(s => s.trim()).filter(Boolean);
      const recResp = await api.post('/recommend', {
        student: {
          id: user?.username || 'user',
          name: user?.username || 'User',
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
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during generation.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-80 bg-white border-r border-slate-200 flex flex-col sticky top-0 h-screen">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-600 font-bold text-xl">
            <GraduationCap />
            <span>AI Advisor</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Goals Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <Target size={18} />
              <h2>Your Goals</h2>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-xs text-slate-500 uppercase font-bold tracking-wider">
                  <span>Difficulty</span>
                  <span>{difficulty.toFixed(1)}</span>
                </div>
                <input 
                  type="range" min="0" max="1" step="0.1" 
                  className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  value={difficulty}
                  onChange={(e) => setDifficulty(parseFloat(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs text-slate-500 uppercase font-bold tracking-wider">
                  <span>Workload</span>
                  <span>{workload.toFixed(1)}</span>
                </div>
                <input 
                  type="range" min="0" max="1" step="0.1" 
                  className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  value={workload}
                  onChange={(e) => setWorkload(parseFloat(e.target.value))}
                />
              </div>
            </div>
          </section>

          {/* Interests Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <Search size={18} />
              <h2>Interests</h2>
            </div>
            <textarea
              className="w-full p-3 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50"
              rows={3}
              placeholder="e.g. Machine Learning, Data Science..."
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
            />
          </section>

          {/* Upload Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <Upload size={18} />
              <h2>Transcript</h2>
            </div>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors group">
              <div className="flex flex-col items-center justify-center pt-5 pb-6 text-slate-400 group-hover:text-blue-500">
                <Upload size={24} className="mb-2" />
                <p className="text-xs">{file ? file.name : 'Upload Platonus HTML'}</p>
              </div>
              <input type="file" className="hidden" accept=".html" onChange={handleFileChange} />
            </label>
          </section>
        </div>

        <div className="p-6 border-t border-slate-100 bg-slate-50/50">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold uppercase">
                {user?.username?.[0] || 'U'}
              </div>
              <span className="text-sm font-medium text-slate-700">{user?.username}</span>
            </div>
            <button onClick={logout} className="text-slate-400 hover:text-red-500 transition-colors">
              <LogOut size={18} />
            </button>
          </div>
          <button
            onClick={generateRecommendations}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading ? <Loader2 className="animate-spin" /> : <Zap size={18} />}
            {isLoading ? 'Processing...' : 'Generate Plan'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-10 space-y-10">
        <AnimatePresence mode="wait">
          {!results && !isLoading ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="h-full flex flex-col items-center justify-center text-center space-y-6"
            >
              <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 mx-auto">
                <GraduationCap size={40} />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 mb-2">Ready to plan your semester?</h1>
                <p className="text-slate-500 max-w-md">Upload your transcript and set your goals to get an AI-powered personalized academic roadmap.</p>
              </div>
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
            <motion.div 
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-12 pb-20"
            >
              {/* Header */}
              <div className="flex items-end justify-between border-b border-slate-200 pb-6">
                <div>
                  <h1 className="text-4xl font-bold text-slate-900">Your Academic Roadmap</h1>
                  <p className="text-slate-500 mt-2">Personalized strategy based on your {results?.results.length} course recommendations.</p>
                </div>
                <div className="bg-green-50 text-green-700 px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 border border-green-100">
                  <CheckCircle2 size={16} />
                  Plan Ready
                </div>
              </div>

              {/* Analysis Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Skill Gap Analysis */}
                <Card className="lg:col-span-2">
                  <CardHeader className="flex flex-row items-center gap-2 font-bold text-slate-900 bg-slate-50/50">
                    <AlertCircle size={20} className="text-orange-500" />
                    Skill Gap Analysis
                  </CardHeader>
                  <CardContent className="space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <div className="p-4 bg-orange-50 rounded-2xl border border-orange-100">
                          <span className="text-xs text-orange-600 font-bold uppercase tracking-wider">Overall Gap Score</span>
                          <div className="text-4xl font-black text-orange-700 mt-1">{((results?.skill_gap_analysis?.overall_gap_score || 0) * 100).toFixed(0)}%</div>
                        </div>
                        <div>
                          <h3 className="text-sm font-bold text-slate-900 mb-3">Critical Skills to Acquire</h3>
                          <div className="flex flex-wrap gap-2">
                            {results?.skill_gap_analysis?.critical_skills.map((skill, i) => (
                              <span key={i} className="px-3 py-1 bg-red-50 text-red-600 rounded-full text-xs font-semibold border border-red-100">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <h3 className="text-sm font-bold text-slate-900">Gaps by Domain</h3>
                        <div className="space-y-4">
                          {results?.skill_gap_analysis?.domain_breakdown.map((domain, i) => (
                            <div key={i} className="space-y-1.5">
                              <div className="flex justify-between text-xs">
                                <span className="font-semibold text-slate-700">{domain.domain}</span>
                                <span className="text-slate-400">{(domain.gap_score * 100).toFixed(0)}%</span>
                              </div>
                              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-orange-500 rounded-full" 
                                  style={{ width: `${domain.gap_score * 100}%` }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Quick Stats */}
                <div className="space-y-6">
                  <Card className="bg-blue-600 text-white border-0">
                    <CardContent className="p-8 space-y-2">
                      <Zap size={32} className="text-blue-200 mb-4" />
                      <h2 className="text-2xl font-bold">Smart Recommendation</h2>
                      <p className="text-blue-100 text-sm opacity-80 leading-relaxed">
                        We prioritize courses that fill your critical skill gaps while maintaining your target {difficulty > 0.5 ? 'challenge' : 'workload'}.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Learning Path */}
              <section className="space-y-6">
                <div className="flex items-center gap-2 text-2xl font-bold text-slate-900">
                  <Map size={24} className="text-blue-600" />
                  <h2>Learning Path</h2>
                </div>
                <div className="relative space-y-8 before:absolute before:left-6 before:top-4 before:bottom-4 before:w-0.5 before:bg-blue-100">
                  {results?.learning_path.sort((a, b) => a.order - b.order).map((step, i) => (
                    <motion.div 
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      key={i} 
                      className="relative pl-16"
                    >
                      <div className="absolute left-0 w-12 h-12 rounded-full bg-white border-4 border-blue-50 flex items-center justify-center z-10 shadow-sm">
                        <span className="text-blue-600 font-black">{step.order}</span>
                      </div>
                      <Card>
                        <CardContent className="p-6 flex items-start justify-between">
                          <div className="space-y-1">
                            <h3 className="text-lg font-bold text-slate-900">{step.title}</h3>
                            <p className="text-slate-500 text-sm">{step.description}</p>
                            {step.resource_id && (
                              <div className="mt-4 pt-4 border-t border-slate-100 flex items-center gap-4">
                                {step.is_external ? (
                                  <a 
                                    href={step.resource_id} target="_blank" rel="noopener noreferrer"
                                    className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1 uppercase tracking-widest"
                                  >
                                    View Resource <ExternalLink size={12} />
                                  </a>
                                ) : (
                                  <span className="text-xs font-bold text-slate-400 flex items-center gap-1 uppercase tracking-widest">
                                    Internal Course ID: {step.resource_id}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                          <ChevronRight size={20} className="text-slate-300" />
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </section>

              {/* Course Catalog */}
              <section className="space-y-6">
                <div className="flex items-center gap-2 text-2xl font-bold text-slate-900">
                  <CheckCircle2 size={24} className="text-green-600" />
                  <h2>Recommended Courses</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {results?.results.map((rec, i) => (
                    <Card key={i} className="hover:shadow-md transition-shadow">
                      <CardHeader className="bg-slate-50/50">
                        <div className="flex justify-between items-start">
                          <h3 className="font-bold text-slate-900 leading-tight pr-4">{rec.subject_name}</h3>
                          <div className="bg-blue-50 text-blue-600 px-2 py-1 rounded text-xs font-black">
                            {(rec.score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <p className="text-sm text-slate-600 line-clamp-3">
                          {rec.reasoning}
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {rec.reason_tags.map((tag, j) => (
                            <span key={j} className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                              {tag}
                            </span>
                          ))}
                        </div>
                        <div className="pt-4 grid grid-cols-2 gap-4">
                          <div className="space-y-1">
                            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Alignment</span>
                            <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500" style={{ width: `${rec.breakdown.content_sim * 100}%` }} />
                            </div>
                          </div>
                          <div className="space-y-1">
                            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Skill Gap</span>
                            <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full bg-green-500" style={{ width: `${rec.breakdown.skill_gap * 100}%` }} />
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
