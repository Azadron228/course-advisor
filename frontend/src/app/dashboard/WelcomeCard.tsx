'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui-base';
import { GraduationCap, Upload, Zap, Loader2, AlertCircle } from 'lucide-react';

interface WelcomeCardProps {
  file: File | null;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  generateRecommendations: () => void;
  isLoading: boolean;
  error: string;
}

export const WelcomeCard: React.FC<WelcomeCardProps> = ({
  file,
  handleFileChange,
  generateRecommendations,
  isLoading,
  error
}) => {
  return (
    <Card className="max-w-2xl w-full border-0 shadow-2xl shadow-blue-100 overflow-hidden">
      <div className="bg-blue-600 p-8 text-white text-center space-y-4">
        <div className="w-16 h-16 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
          <GraduationCap size={32} />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Ready to plan your semester?</h1>
          <p className="text-blue-100 text-sm">Upload your transcript and set your goals to get an AI-powered personalized academic roadmap.</p>
        </div>
      </div>
      <CardContent className="p-8 space-y-8">
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-slate-900 font-bold">
            <Upload size={18} className="text-blue-600" />
            <h2>Upload Transcript</h2>
          </div>
          <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-all group hover:border-blue-400">
            <div className="flex flex-col items-center justify-center pt-5 pb-6 text-slate-400 group-hover:text-blue-600 transition-colors">
              <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mb-3 group-hover:bg-blue-50">
                <Upload size={24} />
              </div>
              <p className="text-sm font-semibold">{file ? file.name : 'Select Platonus HTML file'}</p>
              <p className="text-xs mt-1 text-slate-400">Drag and drop or click to browse</p>
            </div>
            <input type="file" className="hidden" accept=".html" onChange={handleFileChange} />
          </label>
        </div>

        {error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-xl text-sm flex items-center gap-2 border border-red-100">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <button
          onClick={generateRecommendations}
          disabled={isLoading || !file}
          className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 disabled:opacity-50 flex items-center justify-center gap-2 text-lg"
        >
          {isLoading ? <Loader2 className="animate-spin" /> : <Zap size={20} />}
          {isLoading ? 'Processing...' : 'Generate My Roadmap'}
        </button>
      </CardContent>
    </Card>
  );
};
