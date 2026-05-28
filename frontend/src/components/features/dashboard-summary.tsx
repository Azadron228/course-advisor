import React from 'react';
import { BookOpen, Trophy, ArrowRight } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';

interface DashboardSummaryProps {
  welcomeMessage: string;
  activePlanId: number | null;
  activePlanTitle: string | null;
  progressPercentage: number;
}

export function DashboardSummary({
  welcomeMessage,
  activePlanId,
  activePlanTitle,
  progressPercentage,
}: DashboardSummaryProps) {
  const t = useTranslations('Dashboard');

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">{welcomeMessage}</h1>
        <p className="text-muted">{t('subtitle')}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Progress Card */}
        <div className="flex flex-col justify-between rounded-xl border border-border bg-surface p-6 shadow-sm">
          <div>
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <BookOpen className="h-6 w-6" />
              </div>
              <div className="flex-1 space-y-1 min-w-0">
                <p className="text-sm font-medium text-muted">{t('activePlan')}</p>
                <h3 className="text-lg font-semibold text-foreground truncate">
                  {activePlanTitle || t('noActivePlan')}
                </h3>
              </div>
            </div>

            <div className="mt-6 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted font-medium">{t('progress')}</span>
                <span className="font-bold text-primary">{progressPercentage}%</span>
              </div>
              {/* Duolingo-style thick progress bar (8px height) */}
              <div className="h-2 w-full overflow-hidden rounded-full bg-input">
                <div
                  className="h-full bg-primary transition-all duration-500 ease-out"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
            </div>
          </div>

          {activePlanId && (
            <div className="mt-6">
              <Link
                href={`/plan/${activePlanId}`}
                className="inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 bg-primary text-white text-xs font-black uppercase tracking-wider rounded-xl hover:bg-primary/90 hover:shadow-lg hover:shadow-primary/20 transition-all active:scale-[0.98] shadow-md text-center"
              >
                {t('continue')}
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>

        {/* Quick Stats or Achievement Placeholder */}
        <div className="rounded-xl border border-border bg-surface p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-tertiary/10 text-tertiary">
              <Trophy className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium text-muted">{t('achievementLevel')}</p>
              <h3 className="text-lg font-semibold text-foreground">{t('risingStar')}</h3>
            </div>
          </div>
          <p className="mt-4 text-sm text-muted">
            {t('achievementDesc')}
          </p>
        </div>
      </div>
    </div>
  );
}
