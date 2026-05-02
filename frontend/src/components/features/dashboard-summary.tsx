import React from 'react';
import { BookOpen, Trophy } from 'lucide-react';
import { useTranslations } from 'next-intl';

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
  const t = useTranslations('Dashboard');

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">{welcomeMessage}</h1>
        <p className="text-slate-500 dark:text-slate-400">{t('subtitle')}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Progress Card */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-surface p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400">
              <BookOpen className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t('activePlan')}</p>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white truncate">
                {activePlanTitle || t('noActivePlan')}
              </h3>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500 dark:text-slate-400 font-medium">{t('progress')}</span>
              <span className="font-bold text-indigo-600 dark:text-indigo-400">{progressPercentage}%</span>
            </div>
            {/* Duolingo-style thick progress bar (8px height) */}
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className="h-full bg-indigo-600 dark:bg-indigo-500 transition-all duration-500 ease-out"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Quick Stats or Achievement Placeholder */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-surface p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400">
              <Trophy className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t('achievementLevel')}</p>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{t('risingStar')}</h3>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
            {t('achievementDesc')}
          </p>
        </div>
      </div>
    </div>
  );
}
