'use client';

import { LearningPlan } from '@/components/features/plan-stepper';
import { ChevronRight, Calendar, BookOpen, Clock, Zap } from 'lucide-react';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';

export function PlanList({ plans }: { plans: LearningPlan[] }) {
  const t = useTranslations('Plan');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-foreground">{t('myPaths')}</h1>
        <Link 
          href="/plan?view=new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-white font-bold rounded-xl hover:bg-primary/90 transition-all shadow-lg shadow-primary/10 dark:shadow-none"
        >
          <Zap className="w-4 h-4" />
          {t('createNew')}
        </Link>
      </div>

      <div className="grid gap-4">
        {plans.length === 0 ? (
          <div className="bg-surface p-12 rounded-2xl border-2 border-dashed border-border text-center">
            <BookOpen className="w-16 h-16 text-muted/30 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-foreground">{t('noPaths')}</h3>
            <p className="text-muted mb-6 max-w-xs mx-auto">{t('startGenerating')}</p>
            <Link 
              href="/plan?view=new"
              className="inline-flex items-center text-primary font-bold hover:underline"
            >
              {t('getStarted')} <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        ) : (
          plans.map((plan) => (
            <Link 
              key={plan.id}
              href={`/plan?id=${plan.id}`}
              className="group flex items-center justify-between p-6 bg-surface rounded-2xl border border-border hover:border-primary hover:shadow-xl hover:shadow-primary/5 dark:hover:shadow-none transition-all"
            >
              <div className="flex-1 min-w-0">
                <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors truncate mb-2">
                  {plan.goal}
                </h3>
                <div className="flex flex-wrap gap-4 text-xs font-semibold text-muted">
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-muted  rounded-md">
                    {t('stepsCount', { count: plan.steps.length })}
                  </span>
                </div>
              </div>
              <div className="ml-6 flex items-center justify-center w-12 h-12 rounded-full bg-input group-hover:bg-primary/10 text-muted group-hover:text-primary transition-all">
                <ChevronRight className="w-6 h-6 group-hover:translate-x-0.5 transition-transform" />
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
