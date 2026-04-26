import React from 'react';
import { BookOpen, Trophy } from 'lucide-react';

interface DashboardSummaryProps {
  welcomeMessage: string;
  activePlanTitle: string | null;
  progressPercentage: number;
}

export function DashboardSummary({
  welcomeMessage,
  activePlanTitle,
  progressPercentage,
}: DashboardSummaryProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">{welcomeMessage}</h1>
        <p className="text-slate-500">Track your progress and continue your learning journey.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Progress Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
              <BookOpen className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium text-slate-500">Active Learning Plan</p>
              <h3 className="text-lg font-semibold text-slate-900 truncate">
                {activePlanTitle || 'No active plan'}
              </h3>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500 font-medium">Progress</span>
              <span className="font-bold text-indigo-600">{progressPercentage}%</span>
            </div>
            {/* Duolingo-style thick progress bar (8px height) */}
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full bg-indigo-600 transition-all duration-500 ease-out"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Quick Stats or Achievement Placeholder */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
              <Trophy className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium text-slate-500">Achievement Level</p>
              <h3 className="text-lg font-semibold text-slate-900">Rising Star</h3>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-500">
            Keep completing tasks to unlock more badges and level up your skills!
          </p>
        </div>
      </div>
    </div>
  );
}
